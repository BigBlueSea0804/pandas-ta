"""TradingView Technical Ratings에 맞춘 AO/ADX/BBP/CCI."""

import pandas as pd
import pytest

from indicators.oscillators import commodity_channel_index


def test_cci_uses_typical_price_mad() -> None:
    index = pd.date_range("2024-01-01", periods=25, freq="D")
    close = pd.Series(range(100, 125), index=index, dtype="float64")
    high = close + 2
    low = close - 2
    cci = commodity_channel_index(high, low, close, length=20)
    last = float(cci.iloc[-1])
    assert last > 100
