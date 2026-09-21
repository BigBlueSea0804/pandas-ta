"""클래식·피보나치·카마릴라·우디·DM 피봇.

TradingView "Pivot Points Standard"와 값을 맞춘다. 두 가지가 중요하다.

1. 앵커 기간: TV는 차트 주기보다 한 단계 긴 기간으로 피봇을 잡는다(일봉 차트면
   전월 OHLC). 그래서 봉을 앵커 기간으로 합친 뒤 "직전 완료 기간"의 H/L/C와
   "현재 기간"의 시가를 쓴다. 자세한 매핑은 config.PIVOT_ANCHOR_* 참고.
2. 공식 출처: 피보나치/카마릴라는 pandas-ta-classic의 CPR(Central Pivot Range)이
   TV와 정확히 일치해 그대로 위임한다. 나머지 셋은 CPR과 공식이 달라 직접 구현한다.
   - 클래식: TV Classic은 R3=P+2*range인데 CPR은 Traditional식(R3=H+2*(P-L))을 쓴다.
   - 우디: TV는 현재 기간 시가로 P=(H+L+2*Open)/4, CPR은 직전 종가를 쓴다.
   - DM: CPR에 아예 없는 방식이다.
"""

from __future__ import annotations

from typing import Mapping

import pandas as pd
import pandas_ta_classic as ta

from config import DEFAULT_PIVOT_ANCHOR, PIVOT_LEVELS, PIVOT_METHODS

PivotTable = dict[str, dict[str, float | None]]

_ANCHOR_AGG = {"open": "first", "high": "max", "low": "min", "close": "last"}


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


def _cpr_levels(periods: pd.DataFrame, *, method: str) -> dict[str, float | None]:
    """앵커 기간으로 합쳐 둔 봉에 pandas-ta-classic의 CPR을 적용한다.

    timeframe="daily"는 실제로는 "봉 하나 shift"만 하는 모드라(라이브러리
    내부에서 캘린더 리샘플을 하지 않는다), 이미 앵커 기간으로 합쳐 둔 봉을
    넘기면 직전 완료 기간 기준으로 계산된다.
    """
    result = ta.cpr(
        periods["open"],
        periods["high"],
        periods["low"],
        periods["close"],
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


def _classic(high: float, low: float, close: float) -> dict[str, float | None]:
    """TV의 Classic 타입. R3/S3가 Traditional(=CPR)과 달리 P 기준 2*range다."""
    rng = high - low
    pivot = (high + low + close) / 3
    return _levels(
        pivot=pivot,
        r1=2 * pivot - low,
        s1=2 * pivot - high,
        r2=pivot + rng,
        s2=pivot - rng,
        r3=pivot + 2 * rng,
        s3=pivot - 2 * rng,
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


def _anchor_periods(ohlcv: pd.DataFrame, anchor: str) -> pd.DataFrame:
    """봉을 피봇 앵커 기간(일/주/월/년)으로 합친다."""
    periods = ohlcv.loc[:, list(_ANCHOR_AGG)].resample(anchor).agg(_ANCHOR_AGG)
    return periods.dropna(subset=list(_ANCHOR_AGG))


def compute_pivots(ohlcv: pd.DataFrame, *, anchor: str = DEFAULT_PIVOT_ANCHOR) -> PivotTable:
    periods = _anchor_periods(ohlcv, anchor)
    if len(periods) < 2:
        return _empty_table()

    prev = periods.iloc[-2]
    current = periods.iloc[-1]
    high = float(prev["high"])
    low = float(prev["low"])
    close = float(prev["close"])
    prev_open = float(prev["open"])
    current_open = float(current["open"])

    return {
        "classic": _classic(high, low, close),
        "fibonacci": _cpr_levels(periods, method="fibonacci"),
        "camarilla": _cpr_levels(periods, method="camarilla"),
        "woodie": _woodie(high, low, current_open),
        "dm": _demark(prev_open, high, low, close),
    }


def pivot_value(table: Mapping[str, Mapping[str, float | None]], method: str, level: str) -> float | None:
    return table[method][level]
