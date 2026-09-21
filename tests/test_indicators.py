"""이동평균·오실레이터 계산 테스트."""

import numpy as np
import pandas as pd
import pandas_ta_classic as ta
import pytest

from indicators.analyze import analyze_ohlcv
from indicators.moving_averages import compute_moving_averages
from indicators.oscillators import compute_oscillators


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
