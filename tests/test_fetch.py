"""OHLCV 정규화·다운로드 단위 테스트 (네트워크 없음)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from config import MIN_BARS_SMA200, OHLCV_COLUMNS
from data.fetch import FetchError, fetch_ohlcv, load_ohlcv_csv, normalize_ohlcv, normalize_ticker

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_normalize_ticker_strips_and_uppercases() -> None:
    assert normalize_ticker(" 005930.ks ") == "005930.KS"


def test_normalize_ticker_rejects_blank() -> None:
    with pytest.raises(FetchError, match="비어"):
        normalize_ticker("   ")


def test_load_plain_csv_selects_ohlcv() -> None:
    frame = load_ohlcv_csv(FIXTURE_DIR / "ohlcv_plain.csv")
    assert list(frame.columns) == list(OHLCV_COLUMNS)
    assert len(frame) == 3
    assert frame.index.name == "date"
    assert float(frame["close"].iloc[-1]) == 103.0


def test_flatten_yfinance_ticker_first_multiindex() -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"], utc=True)
    columns = pd.MultiIndex.from_product(
        [["AAPL"], ["Open", "High", "Low", "Close", "Volume"]],
        names=["Ticker", "Price"],
    )
    raw = pd.DataFrame(
        [
            [100.0, 102.0, 99.0, 101.0, 1000.0],
            [101.0, 103.0, 100.0, 102.0, 1100.0],
        ],
        index=index,
        columns=columns,
    )
    frame = normalize_ohlcv(raw)
    assert frame.index.tz is None
    assert frame["close"].tolist() == [101.0, 102.0]


def test_flatten_yfinance_multiindex() -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    columns = pd.MultiIndex.from_product(
        [["Open", "High", "Low", "Close", "Volume"], ["AAPL"]],
        names=["Price", "Ticker"],
    )
    raw = pd.DataFrame(
        [
            [100.0, 102.0, 99.0, 101.0, 1000.0],
            [101.0, 103.0, 100.0, 102.0, 1100.0],
        ],
        index=index,
        columns=columns,
    )
    frame = normalize_ohlcv(raw)
    assert list(frame.columns) == list(OHLCV_COLUMNS)
    assert frame["close"].tolist() == [101.0, 102.0]


def test_missing_close_raises() -> None:
    raw = pd.DataFrame(
        {"open": [1], "high": [1], "low": [1], "volume": [1]},
        index=pd.to_datetime(["2024-01-02"]),
    )
    with pytest.raises(FetchError, match="필수 컬럼"):
        normalize_ohlcv(raw)


def test_empty_frame_raises() -> None:
    with pytest.raises(FetchError, match="비어"):
        normalize_ohlcv(pd.DataFrame())


def test_fetch_uses_downloader_and_warns_when_short() -> None:
    index = pd.date_range("2024-01-01", periods=5, freq="D")
    raw = pd.DataFrame(
        {
            "Open": range(5, 10),
            "High": range(6, 11),
            "Low": range(4, 9),
            "Close": range(5, 10),
            "Volume": [100] * 5,
        },
        index=index,
    )

    def fake_download(ticker: str, **kwargs: object) -> pd.DataFrame:
        assert ticker == "AAPL"
        assert kwargs["period"] == "2y"
        assert kwargs["auto_adjust"] is True
        return raw

    result = fetch_ohlcv("aapl", downloader=fake_download)
    assert result.ticker == "AAPL"
    assert result.bar_count == 5
    assert result.warning is not None
    assert str(MIN_BARS_SMA200) in result.warning
    assert list(result.data.columns) == list(OHLCV_COLUMNS)


def test_fetch_empty_download_raises() -> None:
    def fake_download(ticker: str, **kwargs: object) -> pd.DataFrame:
        return pd.DataFrame()

    with pytest.raises(FetchError, match="시세를 가져오지 못했습니다"):
        fetch_ohlcv("QQQ", downloader=fake_download)
