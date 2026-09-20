"""대시보드 포맷·게이지·표 HTML 테스트."""

from config import PIVOT_LEVELS
from dashboard.formatters import format_value
from dashboard.gauges import score_to_gauge
from dashboard.tables import counts_html, pivots_table_html, signals_table_html
from indicators.pivots import compute_pivots
from indicators.signals import Signal
from data.fetch import demo_ohlcv
from indicators.analyze import analyze_ohlcv


def test_format_value_shows_two_decimals_like_tradingview() -> None:
    assert format_value(None) == "—"
    assert format_value(2618) == "2,618.00"
    assert format_value(-2618) == "-2,618.00"
    assert format_value(51.2) == "51.20"
    assert format_value(0.37) == "0.37"
    assert format_value(118.91) == "118.91"


def test_score_to_gauge_maps_minus_one_to_one() -> None:
    assert score_to_gauge(-1) == 0
    assert score_to_gauge(0) == 50
    assert score_to_gauge(1) == 100


def test_signals_table_colors_actions() -> None:
    html = signals_table_html(
        "오실레이터",
        [
            Signal(id="rsi", name="상대 강도 지수 (14)", value=51, action="neutral"),
            Signal(id="mom", name="모멘텀 (10)", value=5500, action="buy"),
        ],
    )
    assert "상대 강도 지수 (14)" in html
    assert "뉴트럴" in html
    assert "바이" in html
    assert "#3b82f6" in html


def test_pivots_table_uses_korean_headers() -> None:
    result = analyze_ohlcv(demo_ohlcv().data, ticker="SAMPLE")
    html = pivots_table_html(result.pivots)
    assert "클래식" in html
    assert "피보나치" in html
    for level in PIVOT_LEVELS:
        assert f">{level}<" in html
    assert compute_pivots(demo_ohlcv().data)["classic"]["P"] is not None


def test_counts_html() -> None:
    html = counts_html(sell=1, neutral=9, buy=1)
    assert "<strong>1</strong>" in html
    assert "뉴트럴" in html


def test_demo_analysis_has_full_dashboard_payload() -> None:
    packed = demo_ohlcv()
    result = analyze_ohlcv(packed.data, ticker=packed.ticker)
    assert packed.ticker == "SAMPLE"
    assert len(result.oscillators) == 11
    assert len(result.moving_averages) == 15
    assert result.ma_gauge.buy >= 10
