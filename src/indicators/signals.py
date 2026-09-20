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
    previous_plus_di: float | None = None,
    previous_minus_di: float | None = None,
    *,
    trend_min: float = ADX_TREND_MIN,
) -> Action:
    """TV Technical Ratings: ADX>20이고 +DI/-DI가 이번 봉에 실제로 교차했을 때만 신호."""
    if None in (adx, plus_di, minus_di, previous_plus_di, previous_minus_di):
        return "neutral"
    if adx <= trend_min:
        return "neutral"
    if previous_plus_di < previous_minus_di and plus_di > minus_di:
        return "buy"
    if previous_plus_di > previous_minus_di and plus_di < minus_di:
        return "sell"
    return "neutral"


def action_cross_band(
    k: float | None,
    d: float | None,
    *,
    oversold: float,
    overbought: float,
) -> Action:
    """TV Stochastic/StochRSI: %K·%D가 모두 밴드를 넘고 서로 교차할 때만 신호.
    단순히 %K가 밴드를 넘겼다고 신호를 내지 않는다(예: %K만 80 위여도 %D보다
    높으면 상승이 이어지는 중이라 뉴트럴)."""
    if k is None or d is None:
        return "neutral"
    if k < oversold and d < oversold and k > d:
        return "buy"
    if k > overbought and d > overbought and k < d:
        return "sell"
    return "neutral"


def action_cci(value: float | None, previous: float | None) -> Action:
    """TV: CCI가 밴드 밖에서 0 쪽으로 되돌아올 때만 신호 (직전 봉 대비 방향 필요)."""
    if value is None or previous is None:
        return "neutral"
    if value < CCI_OVERSOLD and value > previous:
        return "buy"
    if value > CCI_OVERBOUGHT and value < previous:
        return "sell"
    return "neutral"


def action_mom(value: float | None, previous: float | None) -> Action:
    """TV: 모멘텀 값의 부호가 아니라 직전 봉 대비 기울기로 판단한다."""
    if value is None or previous is None:
        return "neutral"
    if value > previous:
        return "buy"
    if value < previous:
        return "sell"
    return "neutral"


def action_macd(macd: float | None, signal: float | None) -> Action:
    """TV: MACD 라인을 0이 아니라 시그널선과 비교한다."""
    if macd is None or signal is None:
        return "neutral"
    if macd > signal:
        return "buy"
    if macd < signal:
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


def action_stoch(k: float | None, d: float | None) -> Action:
    return action_cross_band(k, d, oversold=STOCH_OVERSOLD, overbought=STOCH_OVERBOUGHT)


def action_stochrsi(k: float | None, d: float | None) -> Action:
    return action_cross_band(k, d, oversold=STOCHRSI_OVERSOLD, overbought=STOCHRSI_OVERBOUGHT)


def action_willr(value: float | None) -> Action:
    return action_banded(value, oversold=WILLR_OVERSOLD, overbought=WILLR_OVERBOUGHT)


def action_uo(value: float | None) -> Action:
    return action_banded(value, oversold=UO_OVERSOLD, overbought=UO_OVERBOUGHT)
