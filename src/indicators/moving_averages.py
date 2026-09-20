"""심플·지수 이동평균과 가격 대비 신호."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from config import MA_PERIODS
from indicators._series import last_number
from indicators.signals import Signal, action_ma


def _ma_signal(
    *,
    kind: str,
    period: int,
    close: float | None,
    mean: float | None,
) -> Signal:
    label = "익스포넨셜" if kind == "ema" else "심플"
    return Signal(
        id=f"{kind}_{period}",
        name=f"{label} 무빙 애버리지 ({period})",
        value=mean,
        action=action_ma(close, mean),
    )


def compute_moving_averages(ohlcv: pd.DataFrame) -> list[Signal]:
    close = ohlcv["close"]
    last_close = last_number(close)
    signals: list[Signal] = []
    for period in MA_PERIODS:
        signals.append(
            _ma_signal(
                kind="ema",
                period=period,
                close=last_close,
                mean=last_number(ta.ema(close, length=period)),
            )
        )
        signals.append(
            _ma_signal(
                kind="sma",
                period=period,
                close=last_close,
                mean=last_number(ta.sma(close, length=period)),
            )
        )
    return signals
