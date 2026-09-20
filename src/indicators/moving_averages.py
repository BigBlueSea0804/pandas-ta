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
    high = ohlcv["high"]
    low = ohlcv["low"]
    close = ohlcv["close"]
    volume = ohlcv["volume"]
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

    ichimoku_result = ta.ichimoku(high, low, close, tenkan=9, kijun=26, senkou=52)
    ichimoku_df = ichimoku_result[0] if ichimoku_result is not None else None
    ichimoku_base = last_number(ichimoku_df, prefix="IKS_26")
    signals.append(
        Signal(
            id="ichimoku_base_line",
            name="일목 기준선 (9, 26, 52, 26)",
            value=ichimoku_base,
            action=action_ma(last_close, ichimoku_base),
        )
    )

    vwma = last_number(ta.vwma(close, volume, length=20))
    signals.append(
        Signal(
            id="vwma_20",
            name="볼륨 웨이티드 무빙 애버리지 (20)",
            value=vwma,
            action=action_ma(last_close, vwma),
        )
    )

    hma = last_number(ta.hma(close, length=9))
    signals.append(
        Signal(id="hma_9", name="헐 이동 평균 (9)", value=hma, action=action_ma(last_close, hma))
    )

    return signals
