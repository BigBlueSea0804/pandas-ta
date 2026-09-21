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
    """TV: 추세가 있고(ADX>20) 강해지는 중일 때(ADX 상승) DI 방향을 따른다.

    교차 시점은 보지 않는다. 양쪽 모두 ADX가 직전 봉보다 올라야 신호가 난다.
    """
    if None in (adx, plus_di, minus_di, previous_adx):
        return "neutral"
    if adx <= trend_min or adx <= previous_adx:
        return "neutral"
    if plus_di > minus_di:
        return "buy"
    if plus_di < minus_di:
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


def action_band_reversal(
    value: float | None,
    previous: float | None,
    *,
    oversold: float,
    overbought: float,
) -> Action:
    """TV: 밴드 밖으로 나간 값이 되돌아오기 시작할 때만 신호.

    밴드를 넘겼다는 사실만으로는 신호를 내지 않는다. 과매도 구간에서 계속
    흘러내리는 중이면(직전 봉보다 낮으면) 아직 뉴트럴이다.
    """
    if value is None or previous is None:
        return "neutral"
    if value < oversold and value > previous:
        return "buy"
    if value > overbought and value < previous:
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
    trend_ema: float | None,
    bull_power: float | None,
    bear_power: float | None,
    previous_bull: float | None,
    previous_bear: float | None,
) -> Action:
    """TV Elder-Ray: 상승장(종가>EMA50)에서 BearPower가 음수인 채 반등하면 바이,
    하락장에서 BullPower가 양수인 채 약해지면 셀. 추세 판정은 EMA13이 아니라 EMA50이다."""
    if None in (close, trend_ema, bull_power, bear_power):
        return "neutral"
    if close > trend_ema and bear_power < 0 and previous_bear is not None and bear_power > previous_bear:
        return "buy"
    if close < trend_ema and bull_power > 0 and previous_bull is not None and bull_power < previous_bull:
        return "sell"
    return "neutral"


def action_ichimoku(
    close: float | None,
    conversion: float | None,
    base: float | None,
    lead1_back: float | None,
    lead2_back: float | None,
) -> Action:
    """TV: 구름(26봉 전에 계산된 선행스팬)·기준선·전환선·종가가 한 방향으로 줄을 서야 신호.

    lead1_back/lead2_back은 pinescript의 lead1[26]/lead2[26], 즉 26봉 전에 계산된
    선행스팬 A/B다(현재 봉에 그려진 구름).
    """
    if None in (close, conversion, base, lead1_back, lead2_back):
        return "neutral"
    if lead1_back > lead2_back and base > lead1_back and conversion > base and close > conversion:
        return "buy"
    if lead1_back < lead2_back and base < lead1_back and conversion < base and close < conversion:
        return "sell"
    return "neutral"


def action_rsi(value: float | None, previous: float | None) -> Action:
    return action_band_reversal(value, previous, oversold=RSI_OVERSOLD, overbought=RSI_OVERBOUGHT)


def action_stoch(k: float | None, d: float | None) -> Action:
    return action_cross_band(k, d, oversold=STOCH_OVERSOLD, overbought=STOCH_OVERBOUGHT)


def action_stochrsi(
    k: float | None,
    d: float | None,
    close: float | None,
    trend_ema: float | None,
) -> Action:
    """TV: 스토캐스틱 RSI는 추세와 반대 방향으로만 신호를 낸다.

    하락장(종가<EMA50)에서 과매도 교차면 바이, 상승장에서 과매수 교차면 셀이다.
    """
    if close is None or trend_ema is None:
        return "neutral"
    crossed = action_cross_band(k, d, oversold=STOCHRSI_OVERSOLD, overbought=STOCHRSI_OVERBOUGHT)
    if crossed == "buy" and close < trend_ema:
        return "buy"
    if crossed == "sell" and close > trend_ema:
        return "sell"
    return "neutral"


def action_cci(value: float | None, previous: float | None) -> Action:
    return action_band_reversal(value, previous, oversold=CCI_OVERSOLD, overbought=CCI_OVERBOUGHT)


def action_willr(value: float | None, previous: float | None) -> Action:
    return action_band_reversal(value, previous, oversold=WILLR_OVERSOLD, overbought=WILLR_OVERBOUGHT)


def action_uo(value: float | None) -> Action:
    """TV: UO는 역추세가 아니라 순추세로 읽는다. 70 위면 바이, 30 아래면 셀."""
    if value is None:
        return "neutral"
    if value > UO_OVERBOUGHT:
        return "buy"
    if value < UO_OVERSOLD:
        return "sell"
    return "neutral"
