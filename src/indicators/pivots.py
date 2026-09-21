"""클래식·피보나치·카마릴라·우디·DM 피봇.

클래식/피보나치/카마릴라는 pandas-ta-classic의 CPR(Central Pivot Range)이
우리 기존 공식과 소수점 오차 수준까지 정확히 일치해 그대로 위임한다. 우디는
pandas-ta-classic의 CPR이 "직전 종가" 기반 표준 공식을 쓰는 반면 TradingView는
"당일 시가" 기반 공식을 쓰므로(값이 달라짐, 예: (H+L+2*Open)/4 vs (H+L+2*Close)/4)
TV와 맞춘 직접 구현을 유지한다. DM(데마크)은 CPR에 아예 없는 방식이라 역시 직접
구현을 유지한다.
"""

from __future__ import annotations

from typing import Mapping

import pandas as pd
import pandas_ta_classic as ta

from config import PIVOT_LEVELS, PIVOT_METHODS

PivotTable = dict[str, dict[str, float | None]]

_CPR_METHODS = ("classic", "fibonacci", "camarilla")


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


def _last_value(series: pd.Series | None) -> float | None:
    if series is None or series.empty:
        return None
    value = series.iloc[-1]
    return None if pd.isna(value) else float(value)


def _cpr_levels(
    open_: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    *,
    method: str,
) -> dict[str, float | None]:
    """pandas-ta-classic의 CPR로 클래식/피보나치/카마릴라를 계산한다.

    timeframe="daily"는 실제로는 "봉 하나 shift"만 하는 모드라(라이브러리
    내부에서 캘린더 리샘플을 하지 않는다), 우리가 이미 원하는 시간 단위로
    받아둔 봉이라면 인트라데이 탭에서도 그대로 안전하게 쓸 수 있다.
    """
    result = ta.cpr(
        open_,
        high,
        low,
        close,
        method=method,
        timeframe="daily",
        levels="extended",
        width_analysis=False,
        price_position=False,
    )
    if result is None:
        return _levels()
    return _levels(
        pivot=_last_value(result.get("CPR_PIVOT")),
        r1=_last_value(result.get("CPR_R1")),
        s1=_last_value(result.get("CPR_S1")),
        r2=_last_value(result.get("CPR_R2")),
        s2=_last_value(result.get("CPR_S2")),
        r3=_last_value(result.get("CPR_R3")),
        s3=_last_value(result.get("CPR_S3")),
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
        method: _cpr_levels(ohlcv["open"], ohlcv["high"], ohlcv["low"], ohlcv["close"], method=method)
        for method in _CPR_METHODS
    }
    table["woodie"] = _woodie(high, low, today_open)
    table["dm"] = _demark(prev_open, high, low, close)
    return table


def pivot_value(table: Mapping[str, Mapping[str, float | None]], method: str, level: str) -> float | None:
    return table[method][level]
