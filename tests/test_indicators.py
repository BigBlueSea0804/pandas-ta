"""이동평균·오실레이터 계산 테스트."""

from pathlib import Path

import numpy as np
import pandas as pd
import pandas_ta_classic as ta
import pytest

from data.fetch import load_ohlcv_csv
from indicators.analyze import analyze_ohlcv
from indicators.moving_averages import compute_moving_averages
from indicators.oscillators import compute_oscillators

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _trending_ohlcv(n: int = 250) -> pd.DataFrame:
    index = pd.date_range("2020-01-01", periods=n, freq="B")
    close = 100.0 + np.arange(n) * 0.5
    return pd.DataFrame(
        {
            "open": close - 0.2,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.full(n, 1000.0),
        },
        index=index,
    )


def _accelerating_ohlcv(n: int = 250) -> pd.DataFrame:
    """모멘텀/MACD가 직전 봉보다 계속 커지는(가속 상승) 픽스처.

    mom_10/MACD는 값의 부호가 아니라 직전 봉 대비 기울기(모멘텀) 또는
    시그널선 대비 위치(MACD)로 액션이 정해지므로, 등속 상승(선형)에서는
    모멘텀이 평평해져 뉴트럴이 된다. buy를 재현하려면 상승 속도 자체가
    커지는 픽스처가 필요하다.
    """
    index = pd.date_range("2020-01-01", periods=n, freq="B")
    i = np.arange(n, dtype="float64")
    close = 100.0 + i * 0.3 + 0.003 * i**2
    return pd.DataFrame(
        {
            "open": close - 0.2,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.full(n, 1000.0),
        },
        index=index,
    )


def test_moving_averages_order_and_buy_on_uptrend() -> None:
    frame = _trending_ohlcv()
    signals = compute_moving_averages(frame)
    assert [item.id for item in signals] == [
        "ema_10",
        "sma_10",
        "ema_20",
        "sma_20",
        "ema_30",
        "sma_30",
        "ema_50",
        "sma_50",
        "ema_100",
        "sma_100",
        "ema_200",
        "sma_200",
        "ichimoku_base_line",
        "vwma_20",
        "hma_9",
    ]
    close = frame["close"]
    last_close = float(close.iloc[-1])
    sma10 = signals[1]
    expected = float(ta.sma(close, length=10).iloc[-1])
    assert sma10.value == pytest.approx(expected)
    assert last_close > expected
    assert all(item.value is not None for item in signals)
    # 완벽한 등속 상승 픽스처에서는 반응이 빠른 HMA가 종가와 정확히
    # 같은 값으로 수렴할 수 있어(뉴트럴) 12개 기본 MA만 엄격히 검사한다.
    assert all(item.action == "buy" for item in signals[:12])


def test_sma200_missing_when_too_short() -> None:
    frame = _trending_ohlcv(n=50)
    signals = {item.id: item for item in compute_moving_averages(frame)}
    assert signals["sma_200"].value is None
    assert signals["sma_200"].action == "neutral"
    assert signals["sma_10"].value is not None
    assert signals["sma_10"].action == "buy"


def test_oscillators_return_eleven_named_rows() -> None:
    frame = _trending_ohlcv()
    signals = compute_oscillators(frame)
    assert len(signals) == 11
    assert [item.id for item in signals] == [
        "rsi_14",
        "stoch_k",
        "cci_20",
        "adx_14",
        "ao",
        "mom_10",
        "macd_12_26",
        "stochrsi_k",
        "willr_14",
        "bbp",
        "uo",
    ]
    assert all(item.value is not None for item in signals)
    by_id = {item.id: item for item in signals}
    assert by_id["mom_10"].name == "모멘텀 (10)"
    last = frame.iloc[-1]
    ema13 = float(ta.ema(frame["close"], length=13).iloc[-1])
    assert by_id["bbp"].value == pytest.approx(float(last["high"] + last["low"] - 2 * ema13))


def test_mom_and_macd_use_slope_not_sign() -> None:
    frame = _accelerating_ohlcv()
    signals = {item.id: item for item in compute_oscillators(frame)}
    assert signals["mom_10"].action == "buy"
    assert signals["macd_12_26"].action == "buy"


def test_analyze_ohlcv_builds_gauges() -> None:
    frame = _trending_ohlcv()
    result = analyze_ohlcv(frame, ticker="TEST")
    assert result.ticker == "TEST"
    assert result.close == float(frame["close"].iloc[-1])
    assert len(result.oscillators) == 11
    assert len(result.moving_averages) == 15
    assert result.ma_gauge.rating == "strong_buy"
    assert result.overall_gauge.buy == result.oscillator_gauge.buy + result.ma_gauge.buy
    assert result.pivots["classic"]["P"] is not None


def test_analyze_uses_separate_series_for_pivots() -> None:
    """인트라데이 탭은 지표는 인트라데이 봉, 피봇은 EOD 일봉으로 계산한다."""
    intraday_index = pd.date_range("2024-03-01 09:30", periods=260, freq="30min")
    intraday_close = 100.0 + np.arange(260) * 0.05
    intraday = pd.DataFrame(
        {
            "open": intraday_close - 0.05,
            "high": intraday_close + 0.2,
            "low": intraday_close - 0.2,
            "close": intraday_close,
            "volume": np.full(260, 1000.0),
        },
        index=intraday_index,
    )
    daily = pd.DataFrame(
        {
            "open": [95.0, 105.0],
            "high": [110.0, 112.0],
            "low": [90.0, 104.0],
            "close": [100.0, 108.0],
            "volume": [1000.0, 1000.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    result = analyze_ohlcv(intraday, ticker="TEST", pivot_ohlcv=daily, pivot_anchor="D")
    # 지표는 인트라데이 봉 기준
    assert result.close == pytest.approx(float(intraday["close"].iloc[-1]))
    # 피봇은 넘겨준 일봉 기준 (직전 일봉 H=110 L=90 C=100 -> P=100)
    assert result.pivots["classic"]["P"] == pytest.approx(100.0)


def _short_ohlcv(n: int = 60) -> pd.DataFrame:
    """선행스팬 B(52봉) + 26봉 시프트에 못 미치는 짧은 픽스처."""
    index = pd.date_range("2020-01-01", periods=n, freq="B")
    close = np.linspace(100.0, 50.0, n)
    return pd.DataFrame(
        {
            "open": close,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.full(n, 1000.0),
        },
        index=index,
    )


def test_ichimoku_neutral_without_enough_bars() -> None:
    """구름대는 52+26봉이 필요해서, 60봉에서는 기준선 값만 있고 액션은 뉴트럴이다."""
    signals = {item.id: item for item in compute_moving_averages(_short_ohlcv())}
    ichimoku = signals["ichimoku_base_line"]
    assert ichimoku.value is not None
    assert ichimoku.action == "neutral"
    # 종가가 기준선 아래라 다른 이동평균은 셀이다 (일목만 규칙이 다르다).
    assert signals["sma_20"].action == "sell"


def test_ibm_daily_ma_gauge_matches_tradingview() -> None:
    """골든 회귀: NYSE:IBM 일봉(TradingView 봉 300개)의 MA 게이지.

    TradingView Technicals 실측값
        close          229.55
        Recommend.MA   -0.9333333333333333  (= -14/15)
    일목만 뉴트럴이고 나머지 14개가 셀이라야 -14/15가 나온다. 일목을 다른
    이동평균처럼 종가 vs 기준선으로 판정하면 15개 전부 셀이 되어 -1.0이 된다.
    """
    frame = load_ohlcv_csv(FIXTURE_DIR / "ibm_1d_tv.csv")
    result = analyze_ohlcv(frame, ticker="IBM")
    assert result.close == pytest.approx(229.55)

    signals = {item.id: item for item in result.moving_averages}
    ichimoku = signals["ichimoku_base_line"]
    assert ichimoku.value == pytest.approx(239.6075)
    assert ichimoku.action == "neutral"
    assert ichimoku.value > result.close  # 종가가 기준선 아래인데도 셀이 아니다

    assert (result.ma_gauge.sell, result.ma_gauge.neutral, result.ma_gauge.buy) == (14, 1, 0)
    assert result.ma_gauge.score == pytest.approx(-14 / 15)
    assert result.ma_gauge.rating == "strong_sell"


def test_ibm_daily_moving_average_values_match_tradingview() -> None:
    """같은 픽스처에서 TradingView가 주는 이동평균 값 자체도 맞는지 확인한다."""
    frame = load_ohlcv_csv(FIXTURE_DIR / "ibm_1d_tv.csv")
    signals = {item.id: item for item in compute_moving_averages(frame)}
    # SMA는 윈도가 픽스처 안에 다 들어와 있어 완전히 같다. EMA는 봉 300개로만
    # 시딩해서 TradingView(전체 기간 시딩)와 아주 뒤 자리에서 갈린다 — 기간이
    # 길수록(=시딩이 더 필요할수록) 오차가 커진다.
    assert signals["sma_200"].value == pytest.approx(259.61924999999985)
    assert signals["ema_20"].value == pytest.approx(236.87820996008602, rel=1e-12)
    assert signals["ema_50"].value == pytest.approx(239.01114095287392, rel=1e-7)


def test_ibm_daily_all_gauges_match_tradingview() -> None:
    """골든 회귀: 세 게이지 모두 TradingView 실측값과 일치해야 한다.

    NYSE:IBM 일봉 TradingView Technicals 실측값
        Recommend.Other  -0.2727272727272727  (= -3/11)
        Recommend.MA     -0.9333333333333333  (= -14/15)
        Recommend.All    -0.6030303030303030  (= 두 값의 평균)
    오실레이터 11종·이동평균 15종의 액션 규칙과 요약 평균 공식이 모두 맞아야
    이 세 값이 동시에 나온다.
    """
    frame = load_ohlcv_csv(FIXTURE_DIR / "ibm_1d_tv.csv")
    result = analyze_ohlcv(frame, ticker="IBM")
    assert result.oscillator_gauge.score == pytest.approx(-0.2727272727272727)
    assert result.ma_gauge.score == pytest.approx(-0.9333333333333333)
    assert result.overall_gauge.score == pytest.approx(-0.603030303030303)
    # 오실레이터에서 셀인 3종 (나머지 8종은 뉴트럴)
    osc = {item.id: item.action for item in result.oscillators}
    assert [k for k, v in osc.items() if v == "sell"] == ["mom_10", "macd_12_26", "bbp"]
    assert not [k for k, v in osc.items() if v == "buy"]
