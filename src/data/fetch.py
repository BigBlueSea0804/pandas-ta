"""OHLCV 다운로드와 컬럼 정규화."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd
import yfinance as yf

from config import DEFAULT_INTERVAL, DEFAULT_PERIOD, MIN_BARS_SMA200, OHLCV_COLUMNS

Downloader = Callable[..., pd.DataFrame | None]

_FIELD_ALIASES = {
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "adj_close": "close",
    "adjclose": "close",
    "volume": "volume",
}

_OHLC_TOKENS = {"open", "high", "low", "close", "adj close", "adj_close", "volume"}


class FetchError(ValueError):
    """시세 다운로드 또는 정규화 실패."""


@dataclass(frozen=True)
class OhlcvResult:
    ticker: str
    data: pd.DataFrame
    bar_count: int
    warning: str | None = None


def normalize_ticker(ticker: str) -> str:
    cleaned = ticker.strip()
    if not cleaned:
        raise FetchError("티커가 비어 있습니다.")
    return cleaned.upper()


def _normalize_field_name(name: object) -> str:
    return str(name).strip().lower().replace(" ", "_")


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if isinstance(out.columns, pd.MultiIndex):
        chosen_level: int | None = None
        for level in range(out.columns.nlevels):
            values = {
                str(value).strip().lower().replace("_", " ")
                for value in out.columns.get_level_values(level)
            }
            if values & _OHLC_TOKENS:
                chosen_level = level
                break
        if chosen_level is None:
            out.columns = ["_".join(str(part) for part in col).strip() for col in out.columns]
        else:
            out.columns = list(out.columns.get_level_values(chosen_level))
    out.columns = [_normalize_field_name(column) for column in out.columns]
    return out


def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """yfinance 등에서 받은 DataFrame을 open/high/low/close/volume으로 맞춘다."""
    if df is None or df.empty:
        raise FetchError("시세 데이터가 비어 있습니다.")

    out = _flatten_columns(df)
    renamed: dict[str, str] = {}
    for column in out.columns:
        alias = _FIELD_ALIASES.get(column)
        if alias is not None and alias not in renamed.values():
            renamed[column] = alias
    out = out.rename(columns=renamed)

    missing = [column for column in OHLCV_COLUMNS if column not in out.columns]
    if missing:
        raise FetchError(f"필수 컬럼이 없습니다: {', '.join(missing)}")

    out = out.loc[:, list(OHLCV_COLUMNS)]
    for column in OHLCV_COLUMNS:
        out[column] = pd.to_numeric(out[column], errors="coerce")

    if not isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index, errors="coerce")
    out = out[~out.index.isna()]
    if isinstance(out.index, pd.DatetimeIndex) and out.index.tz is not None:
        out.index = out.index.tz_localize(None)

    out = out.sort_index()
    out = out.dropna(subset=["open", "high", "low", "close"])
    if out.empty:
        raise FetchError("유효한 OHLC 행이 없습니다.")

    out.index.name = "date"
    return out


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, index_col=0)
    return normalize_ohlcv(frame)


def fetch_ohlcv(
    ticker: str,
    *,
    period: str = DEFAULT_PERIOD,
    interval: str = DEFAULT_INTERVAL,
    downloader: Downloader = yf.download,
) -> OhlcvResult:
    symbol = normalize_ticker(ticker)
    raw = downloader(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if raw is None or raw.empty:
        raise FetchError(f"{symbol}: 시세를 가져오지 못했습니다.")

    data = normalize_ohlcv(raw)
    warning = None
    if len(data) < MIN_BARS_SMA200:
        warning = (
            f"{symbol}: 봉 수가 {len(data)}개로 SMA 200 계산에 부족합니다"
            f"(최소 {MIN_BARS_SMA200})."
        )
    return OhlcvResult(ticker=symbol, data=data, bar_count=len(data), warning=warning)


def demo_ohlcv(n: int = 260) -> OhlcvResult:
    """네트워크 없이 대시보드를 확인할 수 있는 상승 추세 샘플."""
    index = pd.date_range("2024-01-02", periods=n, freq="B")
    close = 100.0 + pd.Series(range(n), index=index, dtype="float64") * 0.35
    data = pd.DataFrame(
        {
            "open": close - 0.25,
            "high": close + 0.8,
            "low": close - 0.8,
            "close": close,
            "volume": 1_000_000,
        },
        index=index,
    )
    data.index.name = "date"
    return OhlcvResult(ticker="SAMPLE", data=data, bar_count=len(data))

