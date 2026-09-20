"""신호 임계값 단위 테스트."""

from indicators.signals import (
    action_adx,
    action_ao,
    action_bbp,
    action_cci,
    action_ma,
    action_rsi,
    action_signed,
    action_stoch,
    action_willr,
)


def test_rsi_bands() -> None:
    assert action_rsi(30) == "buy"
    assert action_rsi(29) == "buy"
    assert action_rsi(50) == "neutral"
    assert action_rsi(70) == "sell"


def test_stoch_and_cci_bands() -> None:
    assert action_stoch(20) == "buy"
    assert action_stoch(50) == "neutral"
    assert action_stoch(80) == "sell"
    assert action_cci(-100) == "buy"
    assert action_cci(0) == "neutral"
    assert action_cci(100) == "sell"


def test_willr_bands() -> None:
    assert action_willr(-80) == "buy"
    assert action_willr(-50) == "neutral"
    assert action_willr(-20) == "sell"


def test_signed_momentum() -> None:
    assert action_signed(1) == "buy"
    assert action_signed(-1) == "sell"
    assert action_signed(0) == "neutral"
    assert action_signed(None) == "neutral"


def test_ma_vs_close() -> None:
    assert action_ma(101, 100) == "buy"
    assert action_ma(99, 100) == "sell"
    assert action_ma(100, 100) == "neutral"
    assert action_ma(100, None) == "neutral"


def test_adx_needs_trend_di_and_slope() -> None:
    assert action_adx(19, 30, 10, 18) == "neutral"
    assert action_adx(25, 30, 10, 20) == "buy"
    assert action_adx(25, 30, 10, 26) == "neutral"
    assert action_adx(25, 10, 30, 28) == "sell"
    assert action_adx(25, 10, 30, 20) == "neutral"
    assert action_adx(25, 20, 20, 20) == "neutral"
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
    assert action_bbp(close=110, ema=100, bull_power=5, bear_power=-2, previous_bull=6, previous_bear=-4) == "buy"
    assert action_bbp(close=110, ema=100, bull_power=5, bear_power=1, previous_bull=6, previous_bear=0) == "neutral"
    assert action_bbp(close=90, ema=100, bull_power=2, bear_power=-5, previous_bull=4, previous_bear=-6) == "sell"
    assert action_bbp(close=90, ema=100, bull_power=-1, bear_power=-5, previous_bull=0, previous_bear=-6) == "neutral"
