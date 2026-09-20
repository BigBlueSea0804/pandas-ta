"""표·게이지에 쓰는 숫자 포맷."""

from __future__ import annotations


def format_value(value: float | None) -> str:
    if value is None:
        return "—"
    abs_value = abs(value)
    if abs_value >= 100:
        return f"{value:,.0f}"
    if abs_value >= 10:
        return f"{value:.0f}"
    if abs_value >= 1:
        return f"{value:.1f}"
    return f"{value:.2f}"


def format_price(value: float) -> str:
    if abs(value) >= 100:
        return f"{value:,.2f}"
    if abs(value) >= 1:
        return f"{value:.2f}"
    return f"{value:.4f}"
