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
    *,
    trend_min: float = ADX_TREND_MIN,
) -> Action:
    if adx is None or plus_di is None or minus_di is None or adx < trend_min:
        return "neutral"
    if plus_di > minus_di:
        return "buy"
    if minus_di > plus_di:
        return "sell"
    return "neutral"


def action_ao(value: float | None, previous: float | None) -> Action:
    if value is None or previous is None:
        return "neutral"
    if value > 0 and value > previous:
        return "buy"
    if value < 0 and value < previous:
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
