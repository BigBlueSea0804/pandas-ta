"""신호 임계값 단위 테스트."""

from indicators.signals import (
    action_adx,
    action_ao,
    action_bbp,
    action_cci,
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


def test_willr_bands() -> None:
    assert action_willr(-80) == "buy"
    assert action_willr(-50) == "neutral"
    assert action_willr(-20) == "sell"


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
