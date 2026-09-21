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
    action_uo,
    action_willr,
)


def test_rsi_needs_reversal_from_band() -> None:
    # TV: 과매도에서 반등할 때만 바이, 과매수에서 꺾일 때만 셀.
    assert action_rsi(28, 25) == "buy"
    assert action_rsi(28, 32) == "neutral"
    assert action_rsi(72, 75) == "sell"
    assert action_rsi(72, 68) == "neutral"
    assert action_rsi(50, 48) == "neutral"


def test_stoch_needs_band_and_kd_cross() -> None:
    # %K·%D 둘 다 밴드를 넘고 서로 교차해야 신호. %K만 밴드를 넘긴 경우는 뉴트럴.
    assert action_stoch(15, 10) == "buy"
    assert action_stoch(85, 90) == "sell"
    assert action_stoch(50, 50) == "neutral"
    assert action_stoch(90, 70) == "neutral"
    assert action_stoch(None, 90) == "neutral"


def test_stochrsi_needs_band_cross_and_counter_trend() -> None:
    # TV: 교차에 더해 추세 필터(EMA50)가 반대 방향이어야 신호가 난다.
    assert action_stochrsi(15, 10, close=90, trend_ema=100) == "buy"
    assert action_stochrsi(15, 10, close=110, trend_ema=100) == "neutral"
    assert action_stochrsi(94.6, 96, close=110, trend_ema=100) == "sell"
    assert action_stochrsi(94.6, 96, close=90, trend_ema=100) == "neutral"
    assert action_stochrsi(94.6, 80, close=110, trend_ema=100) == "neutral"


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


def test_adx_needs_trend_strengthening_and_di_direction() -> None:
    """TV: ADX>20 이고 ADX가 직전 봉보다 올랐을 때만 DI 방향을 따른다."""
    assert action_adx(25, 30, 10, 24) == "buy"
    assert action_adx(25, 10, 30, 24) == "sell"
    # ADX가 20 이하이거나 약해지는 중이면 DI 방향과 무관하게 뉴트럴
    assert action_adx(19, 30, 10, 18) == "neutral"
    assert action_adx(25, 30, 10, 26) == "neutral"
    assert action_adx(25, 10, 30, 26) == "neutral"
    assert action_adx(25, 20, 20, 24) == "neutral"
    assert action_adx(25, 30, 10, None) == "neutral"


def test_ao_zero_cross_and_saucer() -> None:
    assert action_ao(0.2, -0.1, -0.3) == "buy"
    assert action_ao(-0.2, 0.1, 0.3) == "sell"
    assert action_ao(2, 1, 1.5) == "buy"
    assert action_ao(-2, -1, -1.5) == "sell"
    assert action_ao(2, 1, 0.5) == "neutral"
    assert action_ao(1, 2, 3) == "neutral"
    assert action_ao(1, None) == "neutral"


def test_bbp_elder_rules() -> None:
    # 추세 필터는 EMA13이 아니라 EMA50(trend_ema)이다.
    assert action_bbp(close=110, trend_ema=100, bull_power=5, bear_power=-2, previous_bull=6, previous_bear=-4) == "buy"
    assert action_bbp(close=110, trend_ema=100, bull_power=5, bear_power=1, previous_bull=6, previous_bear=0) == "neutral"
    assert action_bbp(close=90, trend_ema=100, bull_power=2, bear_power=-5, previous_bull=4, previous_bear=-6) == "sell"
    assert action_bbp(close=90, trend_ema=100, bull_power=-1, bear_power=-5, previous_bull=0, previous_bear=-6) == "neutral"


def test_uo_follows_trend_not_counter_trend() -> None:
    # TV: UO는 70 위면 바이, 30 아래면 셀 (역추세로 읽지 않는다).
    assert action_uo(75) == "buy"
    assert action_uo(25) == "sell"
    assert action_uo(50) == "neutral"
    assert action_uo(70) == "neutral"
    assert action_uo(30) == "neutral"
    assert action_uo(None) == "neutral"


def test_ichimoku_needs_full_cloud_alignment() -> None:
    """TV: lead1[26]>lead2[26] > 기준선 > 전환선 > 종가가 한 방향으로 줄을 서야 신호."""
    # 바이: 구름 양전환 + 기준선 > 구름 상단 + 전환선 > 기준선 + 종가 > 전환선
    assert action_ichimoku(close=120, conversion=115, base=110, lead1_back=105, lead2_back=100) == "buy"
    # 종가가 전환선 아래면 바이 불성립
    assert action_ichimoku(close=112, conversion=115, base=110, lead1_back=105, lead2_back=100) == "neutral"
    # 셀: 전부 반대 방향
    assert action_ichimoku(close=100, conversion=105, base=110, lead1_back=115, lead2_back=120) == "sell"
    # 종가가 전환선 위면 셀 불성립 (IBM 주봉이 이 경우였다)
    assert action_ichimoku(close=229.55, conversion=225.50, base=265.82, lead1_back=245.66, lead2_back=265.82) == "neutral"
    assert action_ichimoku(None, 115, 110, 105, 100) == "neutral"


def test_ichimoku_ibm_daily_is_neutral_not_sell() -> None:
    """NYSE:IBM 일봉 실측값. 종가가 기준선 아래라 종전 규칙은 셀이었지만,
    종가(229.55)가 전환선(240.5975) 위여서 TradingView는 뉴트럴로 본다."""
    assert (
        action_ichimoku(
            close=229.55,
            conversion=240.5975,
            base=239.6075,
            lead1_back=240.34875,
            lead2_back=265.825,
        )
        == "neutral"
    )
    # 같은 값으로 옛 규칙(종가 vs 기준선)을 돌리면 셀이 나온다.
    assert action_ma(229.55, 239.6075) == "sell"
