"""오실레이터·이동평균·피봇 HTML 표."""

from __future__ import annotations

from config import ACTION_COLORS, PIVOT_LEVELS, PIVOT_METHOD_LABELS, PIVOT_METHODS
from dashboard.formatters import format_value
from indicators.pivots import PivotTable
from indicators.signals import Signal

_TABLE_STYLE = """
<style>
.ta-table {width:100%;border-collapse:collapse;font-size:0.95rem;color:#e5e5e5;}
.ta-table th,.ta-table td {border-bottom:1px solid #2a2a2a;padding:0.7rem 0.4rem;text-align:left;}
.ta-table th {color:#a3a3a3;font-weight:500;}
.ta-table td.num,.ta-table th.num {text-align:right;}
.ta-table td.act,.ta-table th.act {text-align:right;width:5.5rem;}
.ta-caption {font-size:1.15rem;margin:1.25rem 0 0.4rem;color:#f5f5f5;}
.ta-counts {display:flex;justify-content:center;gap:1.75rem;color:#a3a3a3;font-size:0.9rem;margin-top:-0.4rem;}
.ta-counts strong {display:block;text-align:center;color:#e5e5e5;font-size:1.05rem;}
</style>
"""


def inject_styles() -> str:
    return _TABLE_STYLE


def counts_html(*, sell: int, neutral: int, buy: int) -> str:
    return (
        "<div class='ta-counts'>"
        f"<div>셀<strong>{sell}</strong></div>"
        f"<div>뉴트럴<strong>{neutral}</strong></div>"
        f"<div>바이<strong>{buy}</strong></div>"
        "</div>"
    )


def signals_table_html(title: str, signals: list[Signal]) -> str:
    rows = []
    for item in signals:
        color = ACTION_COLORS[item.action]
        rows.append(
            "<tr>"
            f"<td>{item.name}</td>"
            f"<td class='num'>{format_value(item.value)}</td>"
            f"<td class='act' style='color:{color}'>{item.action_label}</td>"
            "</tr>"
        )
    body = "".join(rows)
    return (
        f"<div class='ta-caption'>{title}</div>"
        "<table class='ta-table'>"
        "<thead><tr><th>이름</th><th class='num'>값</th><th class='act'>액션</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def pivots_table_html(pivots: PivotTable) -> str:
    header = "".join(f"<th class='num'>{PIVOT_METHOD_LABELS[method]}</th>" for method in PIVOT_METHODS)
    rows = []
    for level in PIVOT_LEVELS:
        cells = "".join(
            f"<td class='num'>{format_value(pivots[method][level])}</td>" for method in PIVOT_METHODS
        )
        rows.append(f"<tr><td>{level}</td>{cells}</tr>")
    return (
        "<div class='ta-caption'>피봇</div>"
        "<table class='ta-table'>"
        f"<thead><tr><th>피봇</th>{header}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )
