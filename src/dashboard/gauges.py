"""Plotly 반원 게이지."""

from __future__ import annotations

import plotly.graph_objects as go

from config import BUY_COLOR, NEUTRAL_COLOR, SELL_COLOR
from indicators.summary import GaugeSummary


_RATING_COLORS = {
    "strong_sell": SELL_COLOR,
    "sell": SELL_COLOR,
    "neutral": NEUTRAL_COLOR,
    "buy": BUY_COLOR,
    "strong_buy": BUY_COLOR,
}


def score_to_gauge(score: float) -> float:
    return (score + 1) / 2 * 100


def gauge_figure(summary: GaugeSummary, title: str) -> go.Figure:
    value = score_to_gauge(summary.score)
    fig = go.Figure(
        go.Indicator(
            mode="gauge",
            value=value,
            title={"text": title, "font": {"size": 16, "color": "#d4d4d4"}},
            domain={"x": [0, 1], "y": [0, 0.72]},
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
    # 등급 텍스트(바이/셀/...)는 title에 넣지 않고 별도 annotation으로 그린다.
    # title에 <br>로 두 줄을 합쳐 넣으면 Plotly가 title 높이를 한 줄 기준으로만
    # 예약해서 게이지 축 눈금(뉴트럴 등)과 겹치는 문제가 있었다.
    fig.add_annotation(
        x=0.5,
        y=0.08,
        xref="paper",
        yref="paper",
        xanchor="center",
        yanchor="bottom",
        text=summary.rating_label,
        showarrow=False,
        font={"size": 19, "color": _RATING_COLORS[summary.rating]},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24, r=24, t=48, b=24),
        height=240,
        font={"color": NEUTRAL_COLOR},
    )
    return fig
