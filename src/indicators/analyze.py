"""OHLCV 한 장에서 지표·피봇·게이지를 묶는다."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config import DEFAULT_PIVOT_ANCHOR
from indicators.moving_averages import compute_moving_averages
from indicators.oscillators import compute_oscillators
from indicators.pivots import PivotTable, compute_pivots
from indicators.signals import Signal
from indicators.summary import GaugeSummary, summarize_groups


@dataclass(frozen=True)
class AnalysisResult:
    ticker: str
    close: float
    oscillators: list[Signal]
    moving_averages: list[Signal]
    oscillator_gauge: GaugeSummary
    ma_gauge: GaugeSummary
    overall_gauge: GaugeSummary
    pivots: PivotTable


def analyze_ohlcv(
    ohlcv: pd.DataFrame,
    *,
    ticker: str = "",
    pivot_anchor: str = DEFAULT_PIVOT_ANCHOR,
) -> AnalysisResult:
    oscillators = compute_oscillators(ohlcv)
    moving_averages = compute_moving_averages(ohlcv)
    oscillator_gauge, ma_gauge, overall_gauge = summarize_groups(oscillators, moving_averages)
    return AnalysisResult(
        ticker=ticker,
        close=float(ohlcv["close"].iloc[-1]),
        oscillators=oscillators,
        moving_averages=moving_averages,
        oscillator_gauge=oscillator_gauge,
        ma_gauge=ma_gauge,
        overall_gauge=overall_gauge,
        pivots=compute_pivots(ohlcv, anchor=pivot_anchor),
    )
