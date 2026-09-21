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
    pivot_ohlcv: pd.DataFrame | None = None,
    pivot_anchor: str = DEFAULT_PIVOT_ANCHOR,
) -> AnalysisResult:
    """지표는 ohlcv로, 피봇은 pivot_ohlcv(없으면 ohlcv)로 계산한다.

    TradingView가 인트라데이 차트에서도 피봇만 EOD 일봉으로 계산하기 때문에
    지표용 봉과 피봇용 봉을 따로 받을 수 있어야 한다.
    """
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
        pivots=compute_pivots(ohlcv if pivot_ohlcv is None else pivot_ohlcv, anchor=pivot_anchor),
    )
