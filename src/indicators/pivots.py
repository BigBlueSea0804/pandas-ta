"""클래식·피보나치·카마릴라·우디·DM 피봇."""

from __future__ import annotations

from typing import Mapping

import pandas as pd

from config import FIB_R1, FIB_R2, FIB_R3, PIVOT_LEVELS, PIVOT_METHODS

PivotTable = dict[str, dict[str, float | None]]


def _levels(
    *,
    r3: float | None = None,
    r2: float | None = None,
    r1: float | None = None,
    pivot: float | None = None,
    s1: float | None = None,
    s2: float | None = None,
    s3: float | None = None,
) -> dict[str, float | None]:
    return {
        "R3": r3,
        "R2": r2,
        "R1": r1,
        "P": pivot,
        "S1": s1,
        "S2": s2,
        "S3": s3,
    }


def _empty_table() -> PivotTable:
    blank = {level: None for level in PIVOT_LEVELS}
    return {method: dict(blank) for method in PIVOT_METHODS}


def _classic(high: float, low: float, close: float) -> dict[str, float | None]:
    rng = high - low
    pivot = (high + low + close) / 3
    return _levels(
        pivot=pivot,
        r1=2 * pivot - low,
        s1=2 * pivot - high,
        r2=pivot + rng,
        s2=pivot - rng,
        r3=high + 2 * (pivot - low),
        s3=low - 2 * (high - pivot),
    )


def _fibonacci(high: float, low: float, close: float) -> dict[str, float | None]:
    rng = high - low
    pivot = (high + low + close) / 3
    return _levels(
        pivot=pivot,
        r1=pivot + FIB_R1 * rng,
        s1=pivot - FIB_R1 * rng,
        r2=pivot + FIB_R2 * rng,
        s2=pivot - FIB_R2 * rng,
        r3=pivot + FIB_R3 * rng,
        s3=pivot - FIB_R3 * rng,
    )


def _camarilla(high: float, low: float, close: float) -> dict[str, float | None]:
    rng = high - low
    pivot = (high + low + close) / 3
    return _levels(
        pivot=pivot,
        r1=close + rng * 1.1 / 12,
        s1=close - rng * 1.1 / 12,
        r2=close + rng * 1.1 / 6,
        s2=close - rng * 1.1 / 6,
        r3=close + rng * 1.1 / 4,
        s3=close - rng * 1.1 / 4,
    )


def _woodie(high: float, low: float, today_open: float) -> dict[str, float | None]:
    rng = high - low
    pivot = (high + low + 2 * today_open) / 4
    return _levels(
        pivot=pivot,
        r1=2 * pivot - low,
        s1=2 * pivot - high,
        r2=pivot + rng,
        s2=pivot - rng,
        r3=high + 2 * (pivot - low),
        s3=low - 2 * (high - pivot),
    )


def _demark(open_: float, high: float, low: float, close: float) -> dict[str, float | None]:
    if close < open_:
        x = high + 2 * low + close
    elif close > open_:
        x = 2 * high + low + close
    else:
        x = high + low + 2 * close
    return _levels(
        pivot=x / 4,
        r1=x / 2 - low,
        s1=x / 2 - high,
    )


def compute_pivots(ohlcv: pd.DataFrame) -> PivotTable:
    if len(ohlcv) < 2:
        return _empty_table()

    prev = ohlcv.iloc[-2]
    today = ohlcv.iloc[-1]
    high = float(prev["high"])
    low = float(prev["low"])
    close = float(prev["close"])
    prev_open = float(prev["open"])
    today_open = float(today["open"])

    table: PivotTable = {
        "classic": _classic(high, low, close),
        "fibonacci": _fibonacci(high, low, close),
        "camarilla": _camarilla(high, low, close),
        "woodie": _woodie(high, low, today_open),
        "dm": _demark(prev_open, high, low, close),
    }
    return table


def pivot_value(table: Mapping[str, Mapping[str, float | None]], method: str, level: str) -> float | None:
    return table[method][level]
