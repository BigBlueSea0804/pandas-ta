"""pandas-ta 결과에서 마지막 유효값을 꺼낸다."""

from __future__ import annotations

import pandas as pd


def as_series(result: pd.Series | pd.DataFrame | None, prefix: str | None = None) -> pd.Series:
    if result is None:
        return pd.Series(dtype="float64")
    if isinstance(result, pd.Series):
        return result.astype("float64")
    columns = [column for column in result.columns if prefix is None or str(column).startswith(prefix)]
    if not columns:
        return pd.Series(dtype="float64")
    return result[columns[0]].astype("float64")


def last_number(series: pd.Series | pd.DataFrame | None, prefix: str | None = None) -> float | None:
    values = as_series(series, prefix=prefix).dropna()
    if values.empty:
        return None
    return float(values.iloc[-1])


def last_two(series: pd.Series | pd.DataFrame | None, prefix: str | None = None) -> tuple[float | None, float | None]:
    values = as_series(series, prefix=prefix).dropna()
    if values.empty:
        return None, None
    current = float(values.iloc[-1])
    previous = float(values.iloc[-2]) if len(values) > 1 else None
    return current, previous


def last_three(
    series: pd.Series | pd.DataFrame | None, prefix: str | None = None
) -> tuple[float | None, float | None, float | None]:
    values = as_series(series, prefix=prefix).dropna()
    if values.empty:
        return None, None, None
    current = float(values.iloc[-1])
    previous = float(values.iloc[-2]) if len(values) > 1 else None
    previous2 = float(values.iloc[-3]) if len(values) > 2 else None
    return current, previous, previous2
