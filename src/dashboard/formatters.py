"""표·게이지에 쓰는 숫자 포맷."""

from __future__ import annotations


def format_value(value: float | None) -> str:
    """TradingView Technicals 표와 동일하게 소수점 둘째 자리까지 표시한다."""
    if value is None:
        return "—"
    return f"{value:,.2f}"


def format_price(value: float) -> str:
    if abs(value) >= 100:
        return f"{value:,.2f}"
    if abs(value) >= 1:
        return f"{value:.2f}"
    return f"{value:.4f}"
