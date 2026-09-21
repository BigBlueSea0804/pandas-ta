"""오실레이터·이동평균 투표를 게이지 요약으로 집계한다."""

from __future__ import annotations

from dataclasses import dataclass

from config import RATING_LABELS, SCORE_LEAN, SCORE_STRONG, Rating
from indicators.signals import Signal


@dataclass(frozen=True)
class GaugeSummary:
    sell: int
    neutral: int
    buy: int
    score: float
    rating: Rating

    @property
    def total(self) -> int:
        return self.sell + self.neutral + self.buy

    @property
    def rating_label(self) -> str:
        return RATING_LABELS[self.rating]


def rating_from_score(score: float) -> Rating:
    """TV ratingStatus와 같은 경계. 임계값과 정확히 같은 값은 약한 쪽으로 간다."""
    if score < -SCORE_STRONG:
        return "strong_sell"
    if score < -SCORE_LEAN:
        return "sell"
    if score > SCORE_STRONG:
        return "strong_buy"
    if score > SCORE_LEAN:
        return "buy"
    return "neutral"


def summarize_signals(signals: list[Signal]) -> GaugeSummary:
    counted = [item for item in signals if item.value is not None]
    sell = sum(item.action == "sell" for item in counted)
    buy = sum(item.action == "buy" for item in counted)
    neutral = sum(item.action == "neutral" for item in counted)
    total = sell + buy + neutral
    score = 0.0 if total == 0 else (buy - sell) / total
    return GaugeSummary(
        sell=sell,
        neutral=neutral,
        buy=buy,
        score=score,
        rating=rating_from_score(score),
    )


def combine_gauges(oscillator: GaugeSummary, moving_average: GaugeSummary) -> GaugeSummary:
    """TV 요약 게이지: 카운트는 두 그룹의 합, 등급은 두 그룹 등급의 평균이다.

    두 그룹 크기가 11 대 15로 다르기 때문에, 26표를 한 번에 세는 것과 값이 다르다.
    """
    score = (oscillator.score + moving_average.score) / 2
    return GaugeSummary(
        sell=oscillator.sell + moving_average.sell,
        neutral=oscillator.neutral + moving_average.neutral,
        buy=oscillator.buy + moving_average.buy,
        score=score,
        rating=rating_from_score(score),
    )


def summarize_groups(
    oscillators: list[Signal],
    moving_averages: list[Signal],
) -> tuple[GaugeSummary, GaugeSummary, GaugeSummary]:
    oscillator_gauge = summarize_signals(oscillators)
    ma_gauge = summarize_signals(moving_averages)
    return oscillator_gauge, ma_gauge, combine_gauges(oscillator_gauge, ma_gauge)
