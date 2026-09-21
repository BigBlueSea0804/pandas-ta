"""TradingView Technical Ratings에 맞춘 AO/ADX/BBP/CCI."""

import pandas as pd
import pandas_ta_classic as ta
import pytest

from indicators.oscillators import compute_oscillators


def test_cci_uses_typical_price_mad() -> None:
    index = pd.date_range("2024-01-01", periods=25, freq="D")
    close = pd.Series(range(100, 125), index=index, dtype="float64")
    high = close + 2
    low = close - 2
    cci = ta.cci(high, low, close, length=20)
    last = float(cci.iloc[-1])
    assert last > 100


def test_compute_oscillators_uses_pandas_ta_classic_cci() -> None:
    index = pd.date_range("2024-01-01", periods=25, freq="D")
    close = pd.Series(range(100, 125), index=index, dtype="float64")
    frame = pd.DataFrame(
        {"open": close - 1, "high": close + 2, "low": close - 2, "close": close, "volume": 1000.0},
        index=index,
    )
    signals = {item.id: item for item in compute_oscillators(frame)}
    expected = float(ta.cci(frame["high"], frame["low"], frame["close"], length=20).iloc[-1])
    assert signals["cci_20"].value == pytest.approx(expected)
