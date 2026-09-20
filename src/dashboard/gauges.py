"""Plotly 반원 게이지."""

from __future__ import annotations

import plotly.graph_objects as go

from config import BUY_COLOR, NEUTRAL_COLOR, SELL_COLOR
from indicators.summary import GaugeSummary


def score_to_gauge(score: float) -> float:
    return (score + 1) / 2 * 100


def gauge_figure(summary: GaugeSummary, title: str) -> go.Figure:
    value = score_to_gauge(summary.score)
    fig = go.Figure(
        go.Indicator(
            mode="gauge",
            value=value,
            title={
                "text": f"{title}<br><span style='font-size:1.15em;color:#e5e5e5'>{summary.rating_label}</span>",
                "font": {"size": 16, "color": "#d4d4d4"},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickvals": [10, 30, 50, 70, 90],
                    "ticktext": ["스트롱 셀", "셀", "뉴트럴", "바이", "스트롱 바이"],
                    "tickfont": {"size": 11, "color": "#a3a3a3"},
                },
                "bar": {"color": "rgba(0,0,0,0)", "thickness": 0},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 20], "color": "#7f1d1d"},
                    {"range": [20, 40], "color": SELL_COLOR},
                    {"range": [40, 60], "color": "#525252"},
                    {"range": [60, 80], "color": BUY_COLOR},
                    {"range": [80, 100], "color": "#1d4ed8"},
                ],
                "threshold": {
                    "line": {"color": "#f5f5f5", "width": 4},
                    "thickness": 0.85,
                    "value": value,
                },
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24, r=24, t=56, b=8),
        height=240,
        font={"color": NEUTRAL_COLOR},
    )
    return fig
