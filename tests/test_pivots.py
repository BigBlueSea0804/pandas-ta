"""피봇 공식 골든 픽스처."""

import pandas as pd
import pytest

from config import PIVOT_ANCHOR_DAILY, PIVOT_ANCHOR_MONTHLY
from indicators.pivots import compute_pivots


def _two_day_ohlcv() -> pd.DataFrame:
    # 직전 기간 H=110, L=90, C=100, O=95 / 현재 기간 O=105
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
    table = compute_pivots(_two_day_ohlcv(), anchor=PIVOT_ANCHOR_DAILY)
    classic = table["classic"]
    assert classic["P"] == pytest.approx(100.0)
    assert classic["R1"] == pytest.approx(110.0)
    assert classic["S1"] == pytest.approx(90.0)
    assert classic["R2"] == pytest.approx(120.0)
    assert classic["S2"] == pytest.approx(80.0)
    # TV Classic의 R3/S3는 P ± 2*range (Traditional의 H+2*(P-L)가 아니다).
    assert classic["R3"] == pytest.approx(140.0)
    assert classic["S3"] == pytest.approx(60.0)

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
    table = compute_pivots(frame, anchor=PIVOT_ANCHOR_DAILY)
    assert table["classic"]["P"] is None


def test_monthly_anchor_uses_previous_month_not_previous_bar() -> None:
    index = pd.to_datetime(["2024-01-30", "2024-01-31", "2024-02-01"])
    frame = pd.DataFrame(
        {
            "open": [95.0, 98.0, 105.0],
            "high": [110.0, 104.0, 112.0],
            "low": [90.0, 97.0, 104.0],
            "close": [98.0, 100.0, 108.0],
            "volume": [1000.0, 1000.0, 1100.0],
        },
        index=index,
    )
    monthly = compute_pivots(frame, anchor=PIVOT_ANCHOR_MONTHLY)
    # 1월 전체를 하나의 봉으로 합치면 H=110, L=90, C=100 -> P=100
    assert monthly["classic"]["P"] == pytest.approx(100.0)
    # 같은 데이터라도 일봉 앵커면 직전 "봉"(1/31)만 보므로 P가 달라진다.
    daily = compute_pivots(frame, anchor=PIVOT_ANCHOR_DAILY)
    assert daily["classic"]["P"] == pytest.approx((104.0 + 97.0 + 100.0) / 3)


def _aapl_daily_ohlcv() -> pd.DataFrame:
    """월봉으로 합치면 AAPL 실제 값이 되는 일봉 픽스처.

    2026-08(직전 완료 월) O=309.58 H=322.37 L=300.57 C=316.85,
    2026-09(현재 월) 시가 316.98. TradingView 월봉 시세에서 가져왔다.
    """
    index = pd.to_datetime(["2026-08-03", "2026-08-31", "2026-09-01"])
    return pd.DataFrame(
        {
            "open": [309.58, 310.00, 316.98],
            "high": [317.40, 322.37, 338.49],
            "low": [300.57, 305.00, 309.90],
            "close": [310.00, 316.85, 336.13],
            "volume": [1e6, 1e6, 1e6],
        },
        index=index,
    )


def test_matches_tradingview_pivot_points_standard() -> None:
    """TradingView "Pivot Points Standard"(AAPL 일봉, Auto=월봉 앵커) 화면값 회귀.

    일봉 차트의 피봇은 전일이 아니라 전월 OHLC 기준이라, 앵커가 틀리면 여기서 깨진다.
    허용 오차 0.005는 TV 화면이 소수점 둘째 자리까지만 보여 주기 때문이다.
    """
    table = compute_pivots(_aapl_daily_ohlcv(), anchor=PIVOT_ANCHOR_MONTHLY)
    expected = {
        "classic": {"R3": 356.86, "R2": 335.06, "R1": 325.96, "P": 313.26, "S1": 304.16, "S2": 291.46, "S3": 269.66},
        "fibonacci": {"R3": 335.06, "R2": 326.74, "R1": 321.59, "P": 313.26, "S1": 304.94, "S2": 299.79, "S3": 291.46},
        "camarilla": {"R3": 322.85, "R2": 320.85, "R1": 318.85, "P": 313.26, "S1": 314.85, "S2": 312.85, "S3": 310.86},
        "woodie": {"R3": 349.68, "R2": 336.03, "R1": 327.88, "P": 314.23, "S1": 306.08, "S2": 292.43, "S3": 284.28},
        "dm": {"R1": 330.51, "P": 315.54, "S1": 308.71},
    }
    for method, levels in expected.items():
        for level, value in levels.items():
            assert table[method][level] == pytest.approx(value, abs=0.005), f"{method} {level}"
