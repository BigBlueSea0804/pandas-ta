"""피봇 공식 골든 픽스처."""

import pandas as pd
import pytest

from indicators.pivots import compute_pivots


def _two_day_ohlcv() -> pd.DataFrame:
    # 전일 H=110, L=90, C=100, O=95 / 당일 O=105
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    return pd.DataFrame(
        {
            "open": [95.0, 105.0],
            "high": [110.0, 112.0],
            "low": [90.0, 104.0],
            "close": [100.0, 108.0],
            "volume": [1000.0, 1100.0],
        },
        index=index,
    )


def test_classic_fib_camarilla_woodie_dm() -> None:
    table = compute_pivots(_two_day_ohlcv())
    classic = table["classic"]
    assert classic["P"] == pytest.approx(100.0)
    assert classic["R1"] == pytest.approx(110.0)
    assert classic["S1"] == pytest.approx(90.0)
    assert classic["R2"] == pytest.approx(120.0)
    assert classic["S2"] == pytest.approx(80.0)
    assert classic["R3"] == pytest.approx(130.0)
    assert classic["S3"] == pytest.approx(70.0)

    fib = table["fibonacci"]
    assert fib["P"] == pytest.approx(100.0)
    assert fib["R1"] == pytest.approx(107.64)
    assert fib["S1"] == pytest.approx(92.36)
    assert fib["R2"] == pytest.approx(112.36)
    assert fib["S2"] == pytest.approx(87.64)
    assert fib["R3"] == pytest.approx(120.0)
    assert fib["S3"] == pytest.approx(80.0)

    cam = table["camarilla"]
    assert cam["P"] == pytest.approx(100.0)
    assert cam["R1"] == pytest.approx(100 + 20 * 1.1 / 12)
    assert cam["S1"] == pytest.approx(100 - 20 * 1.1 / 12)
    assert cam["R3"] == pytest.approx(100 + 20 * 1.1 / 4)
    assert cam["S3"] == pytest.approx(100 - 20 * 1.1 / 4)

    woodie = table["woodie"]
    assert woodie["P"] == pytest.approx(102.5)
    assert woodie["R1"] == pytest.approx(115.0)
    assert woodie["S1"] == pytest.approx(95.0)
    assert woodie["R2"] == pytest.approx(122.5)
    assert woodie["S2"] == pytest.approx(82.5)
    assert woodie["R3"] == pytest.approx(135.0)
    assert woodie["S3"] == pytest.approx(75.0)

    dm = table["dm"]
    assert dm["P"] == pytest.approx(102.5)
    assert dm["R1"] == pytest.approx(115.0)
    assert dm["S1"] == pytest.approx(95.0)
    assert dm["R2"] is None
    assert dm["R3"] is None
    assert dm["S2"] is None
    assert dm["S3"] is None


def test_pivots_need_two_bars() -> None:
    index = pd.to_datetime(["2024-01-02"])
    frame = pd.DataFrame(
        {"open": [1], "high": [1], "low": [1], "close": [1], "volume": [1]},
        index=index,
    )
    table = compute_pivots(frame)
    assert table["classic"]["P"] is None
