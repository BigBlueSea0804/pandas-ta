"""게이지 투표 집계·등급 테스트."""

import pytest

from indicators.signals import Signal
from indicators.summary import rating_from_score, summarize_groups, summarize_signals


def _votes(*actions: str, missing: int = 0) -> list[Signal]:
    rows = [
        Signal(id=f"s{index}", name=f"s{index}", value=1.0, action=action)  # type: ignore[arg-type]
        for index, action in enumerate(actions)
    ]
    rows.extend(
        Signal(id=f"m{index}", name=f"m{index}", value=None, action="neutral")
        for index in range(missing)
    )
    return rows


def test_oscillator_1_9_1_is_neutral() -> None:
    summary = summarize_signals(_votes("sell", *["neutral"] * 9, "buy"))
    assert (summary.sell, summary.neutral, summary.buy) == (1, 9, 1)
    assert summary.total == 11
    assert summary.score == 0.0
    assert summary.rating == "neutral"
    assert summary.rating_label == "뉴트럴"


def test_ma_majority_buy_is_strong_buy() -> None:
    summary = summarize_signals(_votes(*["buy"] * 10, *["sell"] * 2))
    assert (summary.sell, summary.neutral, summary.buy) == (2, 0, 10)
    assert summary.score == (10 - 2) / 12
    assert summary.rating == "strong_buy"
    assert summary.rating_label == "스트롱 바이"


def test_overall_combines_oscillator_and_ma() -> None:
    """TV 요약: 카운트는 합산, 등급은 두 그룹 등급의 평균."""
    oscillators = _votes("sell", *["neutral"] * 9, "buy")
    moving_averages = _votes(*["buy"] * 10, *["sell"] * 2)
    osc, ma, overall = summarize_groups(oscillators, moving_averages)
    assert (osc.sell, osc.neutral, osc.buy) == (1, 9, 1)
    assert (ma.sell, ma.neutral, ma.buy) == (2, 0, 10)
    assert (overall.sell, overall.neutral, overall.buy) == (3, 9, 11)
    assert overall.score == (osc.score + ma.score) / 2
    # 26표를 한 번에 세는 방식((11-3)/23)과는 다른 값이다.
    assert overall.score != (11 - 3) / 23
    assert overall.rating == "buy"


def test_overall_matches_tradingview_ibm_snapshot() -> None:
    """TradingView IBM 일봉 스냅샷(Recommend.MA=-14/15, Other=-3/11) 회귀."""
    oscillators = _votes(*["sell"] * 3, *["neutral"] * 8)
    moving_averages = _votes(*["sell"] * 14, "neutral")
    osc, ma, overall = summarize_groups(oscillators, moving_averages)
    assert osc.score == pytest.approx(-0.2727272727272727)
    assert ma.score == pytest.approx(-0.9333333333333333)
    assert overall.score == pytest.approx(-0.603030303030303)


def test_missing_values_are_excluded_from_denominator() -> None:
    summary = summarize_signals(_votes("buy", "buy", missing=3))
    assert summary.total == 2
    assert summary.score == 1.0
    assert summary.rating == "strong_buy"


def test_empty_signals_are_neutral() -> None:
    summary = summarize_signals([])
    assert (summary.sell, summary.neutral, summary.buy) == (0, 0, 0)
    assert summary.score == 0.0
    assert summary.rating == "neutral"


def test_rating_boundaries() -> None:
    assert rating_from_score(-0.5) == "strong_sell"
    assert rating_from_score(-0.1) == "sell"
    assert rating_from_score(-0.09) == "neutral"
    assert rating_from_score(0.09) == "neutral"
    assert rating_from_score(0.1) == "buy"
    assert rating_from_score(0.49) == "buy"
    assert rating_from_score(0.5) == "strong_buy"
