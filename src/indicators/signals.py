"""지표값을 바이/셀/뉴트럴로 변환한다."""

from __future__ import annotations

from dataclasses import dataclass

from config import (
    ACTION_LABELS,
    ADX_TREND_MIN,
    CCI_OVERBOUGHT,
    CCI_OVERSOLD,
    RSI_OVERBOUGHT,
    RSI_OVERSOLD,
    STOCH_OVERBOUGHT,
    STOCH_OVERSOLD,
    STOCHRSI_OVERBOUGHT,
    STOCHRSI_OVERSOLD,
    UO_OVERBOUGHT,
    UO_OVERSOLD,
    WILLR_OVERBOUGHT,
    WILLR_OVERSOLD,
    Action,
)


@dataclass(frozen=True)
class Signal:
    id: str
    name: str
    value: float | None
    action: Action

    @property
    def action_label(self) -> str:
        return ACTION_LABELS[self.action]


def action_banded(
    value: float | None,
    *,
    oversold: float,
    overbought: float,
) -> Action:
    if value is None:
        return "neutral"
    if value <= oversold:
        return "buy"
    if value >= overbought:
        return "sell"
    return "neutral"


def action_signed(value: float | None) -> Action:
    if value is None or value == 0:
        return "neutral"
    return "buy" if value > 0 else "sell"


def action_ma(close: float | None, mean: float | None) -> Action:
    if close is None or mean is None:
        return "neutral"
    if close > mean:
        return "buy"
    if close < mean:
        return "sell"
    return "neutral"


def action_adx(
    adx: float | None,
    plus_di: float | None,
    minus_di: float | None,
    previous_adx: float | None = None,
    *,
    trend_min: float = ADX_TREND_MIN,
) -> Action:
    """TV Technical Ratings: ADX>20이고 DI 방향과 ADX 기울기가 같을 때만 신호."""
    if adx is None or plus_di is None or minus_di is None or previous_adx is None:
        return "neutral"
    if adx < trend_min:
        return "neutral"
    if plus_di > minus_di and adx > previous_adx:
        return "buy"
    if minus_di > plus_di and adx < previous_adx:
        return "sell"
    return "neutral"


def action_ao(
    value: float | None,
    previous: float | None,
    previous2: float | None = None,
) -> Action:
    """TV: 제로라인 돌파 또는 같은 부호에서 접시(saucer) 반전."""
    if value is None or previous is None:
        return "neutral"
    if previous <= 0 < value:
        return "buy"
    if previous >= 0 > value:
        return "sell"
    if previous2 is None:
        return "neutral"
    if value > 0 and previous > 0 and value > previous and previous < previous2:
        return "buy"
    if value < 0 and previous < 0 and value < previous and previous > previous2:
        return "sell"
    return "neutral"


def action_bbp(
    close: float | None,
    ema: float | None,
    bull_power: float | None,
    bear_power: float | None,
    previous_bull: float | None,
    previous_bear: float | None,
) -> Action:
    """TV Elder-Ray: 상승장+BearPower 음수 반등 / 하락장+BullPower 양수 약화."""
    if None in (close, ema, bull_power, bear_power):
        return "neutral"
    if close > ema and bear_power < 0 and previous_bear is not None and bear_power > previous_bear:
        return "buy"
    if close < ema and bull_power > 0 and previous_bull is not None and bull_power < previous_bull:
        return "sell"
    return "neutral"


def action_rsi(value: float | None) -> Action:
    return action_banded(value, oversold=RSI_OVERSOLD, overbought=RSI_OVERBOUGHT)


def action_stoch(value: float | None) -> Action:
    return action_banded(value, oversold=STOCH_OVERSOLD, overbought=STOCH_OVERBOUGHT)


def action_cci(value: float | None) -> Action:
    return action_banded(value, oversold=CCI_OVERSOLD, overbought=CCI_OVERBOUGHT)


def action_stochrsi(value: float | None) -> Action:
    return action_banded(value, oversold=STOCHRSI_OVERSOLD, overbought=STOCHRSI_OVERBOUGHT)


def action_willr(value: float | None) -> Action:
    return action_banded(value, oversold=WILLR_OVERSOLD, overbought=WILLR_OVERBOUGHT)


def action_uo(value: float | None) -> Action:
    return action_banded(value, oversold=UO_OVERSOLD, overbought=UO_OVERBOUGHT)
