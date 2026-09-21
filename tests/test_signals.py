"""신호 임계값 단위 테스트."""

from indicators.signals import (
    action_adx,
    action_ao,
    action_bbp,
    action_cci,
    action_ichimoku,
    action_ma,
    action_macd,
    action_mom,
    action_rsi,
    action_stoch,
    action_stochrsi,
    action_willr,
)


def test_rsi_bands() -> None:
    assert action_rsi(30) == "buy"
    assert action_rsi(29) == "buy"
    assert action_rsi(50) == "neutral"
    assert action_rsi(70) == "sell"


def test_stoch_needs_band_and_kd_cross() -> None:
    # %K·%D 둘 다 밴드를 넘고 서로 교차해야 신호. %K만 밴드를 넘긴 경우는 뉴트럴.
    assert action_stoch(15, 10) == "buy"
    assert action_stoch(85, 90) == "sell"
    assert action_stoch(50, 50) == "neutral"
    assert action_stoch(90, 70) == "neutral"
    assert action_stoch(None, 90) == "neutral"


def test_stochrsi_needs_band_and_kd_cross() -> None:
    assert action_stochrsi(15, 10) == "buy"
    assert action_stochrsi(94.6, 96) == "sell"
    assert action_stochrsi(94.6, 80) == "neutral"


def test_cci_needs_reversal_from_band() -> None:
    assert action_cci(-105, -110) == "buy"
    assert action_cci(-105, -95) == "neutral"
    assert action_cci(105, 110) == "sell"
    assert action_cci(105, 95) == "neutral"
    assert action_cci(50, 40) == "neutral"
    assert action_cci(None, None) == "neutral"


def test_willr_needs_reversal_from_band() -> None:
    # 과매도에서 되돌아설 때만 바이, 과매수에서 꺾일 때만 셀.
    assert action_willr(-85, -90) == "buy"
    assert action_willr(-15, -10) == "sell"
    assert action_willr(-50, -55) == "neutral"
    assert action_willr(None, -90) == "neutral"
    # 과매도 구간이어도 계속 흘러내리는 중이면 뉴트럴 (TradingView 실제 규칙).
    assert action_willr(-98.02, -61.92) == "neutral"


def test_mom_uses_slope_not_sign() -> None:
    assert action_mom(5, 3) == "buy"
    assert action_mom(3, 5) == "sell"
    assert action_mom(5, 5) == "neutral"
    assert action_mom(None, None) == "neutral"
    # 값 자체는 양수여도 직전 봉보다 줄었으면 셀(TradingView 실제 규칙).
    assert action_mom(7.92, 8.5) == "sell"


def test_macd_compares_to_signal_line() -> None:
    assert action_macd(1.2, 0.8) == "buy"
    assert action_macd(0.5, 0.9) == "sell"
    assert action_macd(0.5, 0.5) == "neutral"
    assert action_macd(None, None) == "neutral"


def test_ma_vs_close() -> None:
    assert action_ma(101, 100) == "buy"
    assert action_ma(99, 100) == "sell"
    assert action_ma(100, 100) == "neutral"
    assert action_ma(100, None) == "neutral"


def test_adx_needs_trend_and_di_cross() -> None:
    assert action_adx(19, 30, 10, 20, 25) == "neutral"
    assert action_adx(25, 30, 10, 20, 25) == "buy"
    assert action_adx(25, 30, 10, 30, 10) == "neutral"
    assert action_adx(25, 10, 30, 25, 20) == "sell"
    assert action_adx(25, 20, 20, 20, 20) == "neutral"
    assert action_adx(25, 30, 10, None, 25) == "neutral"


def test_ao_zero_cross_and_saucer() -> None:
    assert action_ao(0.2, -0.1, -0.3) == "buy"
    assert action_ao(-0.2, 0.1, 0.3) == "sell"
    assert action_ao(2, 1, 1.5) == "buy"
    assert action_ao(-2, -1, -1.5) == "sell"
    assert action_ao(2, 1, 0.5) == "neutral"
    assert action_ao(1, 2, 3) == "neutral"
    assert action_ao(1, None) == "neutral"


def test_bbp_elder_rules() -> None:
    assert action_bbp(close=110, ema=100, bull_power=5, bear_power=-2, previous_bull=6, previous_bear=-4) == "buy"
    assert action_bbp(close=110, ema=100, bull_power=5, bear_power=1, previous_bull=6, previous_bear=0) == "neutral"
    assert action_bbp(close=90, ema=100, bull_power=2, bear_power=-5, previous_bull=4, previous_bear=-6) == "sell"
    assert action_bbp(close=90, ema=100, bull_power=-1, bear_power=-5, previous_bull=0, previous_bear=-6) == "neutral"


def _ichimoku(**overrides: float | None) -> str:
    """바이가 성립하는 기본값에서 한 조건만 바꿔 보기 위한 헬퍼."""
    args: dict[str, float | None] = {
        "close": 110.0,
        "conversion": 105.0,
        "base": 100.0,
        "previous_conversion": 99.0,
        "previous_base": 100.0,
        "lead1": 104.0,
        "lead2": 103.0,
        "cloud_lead1": 95.0,
        "cloud_lead2": 90.0,
    }
    args.update(overrides)
    return action_ichimoku(**args)  # type: ignore[arg-type]


def test_ichimoku_buy_needs_every_condition() -> None:
    assert _ichimoku() == "buy"
    # 1) 종가가 구름대 안이거나 아래면 뉴트럴
    assert _ichimoku(cloud_lead1=115.0) == "neutral"
    # 2) 종가가 기준선 위여야 한다 (구름대는 넘었지만 기준선 아래)
    assert _ichimoku(close=98.0, cloud_lead1=95.0, cloud_lead2=90.0) == "neutral"
    # 3) 전환선이 기준선 위여야 한다
    assert _ichimoku(conversion=99.0) == "neutral"
    assert _ichimoku(conversion=100.0) == "neutral"
    # 4) 그 교차가 이번 봉에 막 일어났어야 한다 (이미 위에 있던 상태면 뉴트럴)
    assert _ichimoku(previous_conversion=101.0) == "neutral"
    # 5) 앞으로 그려질 선행스팬 A가 B보다 위여야 한다
    assert _ichimoku(lead1=103.0, lead2=104.0) == "neutral"


def test_ichimoku_sell_is_mirrored() -> None:
    sell = {
        "close": 90.0,
        "conversion": 95.0,
        "base": 100.0,
        "previous_conversion": 101.0,
        "previous_base": 100.0,
        "lead1": 96.0,
        "lead2": 97.0,
        "cloud_lead1": 105.0,
        "cloud_lead2": 110.0,
    }
    assert action_ichimoku(**sell) == "sell"  # type: ignore[arg-type]
    assert action_ichimoku(**{**sell, "cloud_lead1": 85.0}) == "neutral"  # type: ignore[arg-type]
    assert action_ichimoku(**{**sell, "conversion": 100.0}) == "neutral"  # type: ignore[arg-type]
    assert action_ichimoku(**{**sell, "previous_conversion": 99.0}) == "neutral"  # type: ignore[arg-type]
    assert action_ichimoku(**{**sell, "lead1": 98.0, "lead2": 97.0}) == "neutral"  # type: ignore[arg-type]


def test_ichimoku_uses_shifted_cloud_not_the_future_one() -> None:
    """현재 위치의 구름대는 26봉 전에 계산된 값이라, 앞으로 그려질 값과 구분해야 한다."""
    # 앞으로 그려질 구름대(lead1/lead2)는 종가 위에 있어도 무방하다.
    assert _ichimoku(lead1=1_000.0, lead2=999.0) == "buy"
    # 반대로 현재 위치의 구름대가 종가 위면 신호가 나오지 않는다.
    assert _ichimoku(cloud_lead1=1_000.0, cloud_lead2=999.0) == "neutral"


def test_ichimoku_missing_inputs_are_neutral() -> None:
    assert _ichimoku(cloud_lead2=None) == "neutral"
    assert _ichimoku(previous_conversion=None) == "neutral"


def test_ichimoku_ibm_daily_is_neutral_not_sell() -> None:
    """NYSE:IBM 일봉 실측값. 종가가 기준선 아래라 종전 규칙은 셀이었지만,
    전환선(240.5975)이 기준선(239.6075) 위라 TradingView는 뉴트럴로 본다."""
    assert (
        action_ichimoku(
            close=229.55,
            conversion=240.5975,
            base=239.6075,
            previous_conversion=241.0075,
            previous_base=239.6075,
            lead1=240.1025,
            lead2=251.505,
            cloud_lead1=240.34875,
            cloud_lead2=265.825,
        )
        == "neutral"
    )
    # 같은 값으로 옛 규칙(종가 vs 기준선)을 돌리면 셀이 나온다.
    assert action_ma(229.55, 239.6075) == "sell"
