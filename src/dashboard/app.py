"""기술적 분석 Streamlit 대시보드."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from config import ACTION_COLORS, DEFAULT_TIMEFRAME, TIMEFRAME_LABELS, TIMEFRAMES
from dashboard.formatters import format_price
from dashboard.gauges import gauge_figure
from dashboard.tables import counts_html, inject_styles, pivots_table_html, signals_table_html
from data.fetch import FetchError, demo_ohlcv, fetch_timeframe_ohlcv
from indicators.analyze import analyze_ohlcv

st.set_page_config(page_title="기술적 분석", layout="wide", initial_sidebar_state="expanded")

_TIMEFRAME_BY_LABEL = {timeframe.label: timeframe for timeframe in TIMEFRAMES}
_DAILY_LABEL = "1일"


@st.cache_data(ttl=3600)
def _load_ohlcv(ticker: str, timeframe_label: str, period_override: str | None) -> tuple:
    timeframe = _TIMEFRAME_BY_LABEL[timeframe_label]
    result = fetch_timeframe_ohlcv(ticker, timeframe, period=period_override)
    return result.ticker, result.data, result.bar_count, result.warning


def main() -> None:
    st.markdown(inject_styles(), unsafe_allow_html=True)
    st.title("기술적 분석")

    timeframe_label = st.segmented_control(
        "기간 단위",
        options=TIMEFRAME_LABELS,
        default=DEFAULT_TIMEFRAME,
        label_visibility="collapsed",
    ) or DEFAULT_TIMEFRAME
    timeframe = _TIMEFRAME_BY_LABEL[timeframe_label]

    with st.sidebar:
        st.subheader("종목")
        ticker = st.text_input("티커", value="AAPL", help="미국: AAPL, SPY / 한국: 005930.KS")
        if timeframe_label == _DAILY_LABEL:
            period_override = st.selectbox("기간", options=["1y", "2y", "5y"], index=1)
        else:
            period_override = None
            st.caption(
                f"{timeframe_label} 봉은 야후 파이낸스가 제공하는 범위(최근 {timeframe.period})만 조회합니다."
            )
        use_sample = st.checkbox("샘플 데이터 (네트워크 없음)", value=False)
        run = st.button("분석", type="primary")
        st.caption(
            "투자 자문이 아닙니다. 선택한 시간 단위의 기술적 지표 요약이며, 매매 결정에 사용하지 마세요."
        )

    if not run and "analysis_ready" not in st.session_state:
        st.info("왼쪽에서 티커를 입력한 뒤 분석을 누르세요. 화면 확인용으로는 샘플 데이터를 쓸 수 있습니다.")
        return

    try:
        if use_sample:
            packed = demo_ohlcv()
            ticker_name, frame, warning = packed.ticker, packed.data, packed.warning
        else:
            ticker_name, frame, _bar_count, warning = _load_ohlcv(
                ticker, timeframe_label, period_override
            )
        analysis = analyze_ohlcv(frame, ticker=ticker_name, pivot_anchor=timeframe.pivot_anchor)
    except FetchError as exc:
        st.error(str(exc))
        return
    except Exception as exc:  # noqa: BLE001 — 대시보드에서는 원인 메시지를 그대로 보여 준다
        st.error(f"분석에 실패했습니다: {exc}")
        return

    st.session_state["analysis_ready"] = True

    prev_close = float(frame["close"].iloc[-2]) if len(frame) > 1 else analysis.close
    change = analysis.close - prev_close
    change_pct = 0.0 if prev_close == 0 else change / prev_close * 100
    change_color = ACTION_COLORS["buy"] if change >= 0 else ACTION_COLORS["sell"]
    st.markdown(
        f"**{analysis.ticker}**  ·  종가 {format_price(analysis.close)}  "
        f"<span style='color:{change_color}'>{change:+.2f} ({change_pct:+.2f}%)</span>",
        unsafe_allow_html=True,
    )
    if warning:
        st.warning(warning)

    left, mid, right = st.columns(3)
    with left:
        st.plotly_chart(
            gauge_figure(analysis.oscillator_gauge, "오실레이터"),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.markdown(
            counts_html(
                sell=analysis.oscillator_gauge.sell,
                neutral=analysis.oscillator_gauge.neutral,
                buy=analysis.oscillator_gauge.buy,
            ),
            unsafe_allow_html=True,
        )
    with mid:
        st.plotly_chart(
            gauge_figure(analysis.overall_gauge, "요약"),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.markdown(
            counts_html(
                sell=analysis.overall_gauge.sell,
                neutral=analysis.overall_gauge.neutral,
                buy=analysis.overall_gauge.buy,
            ),
            unsafe_allow_html=True,
        )
    with right:
        st.plotly_chart(
            gauge_figure(analysis.ma_gauge, "무빙 애버리지"),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.markdown(
            counts_html(
                sell=analysis.ma_gauge.sell,
                neutral=analysis.ma_gauge.neutral,
                buy=analysis.ma_gauge.buy,
            ),
            unsafe_allow_html=True,
        )

    st.markdown(signals_table_html("오실레이터", analysis.oscillators), unsafe_allow_html=True)
    st.markdown(signals_table_html("무빙 애버리지", analysis.moving_averages), unsafe_allow_html=True)
    st.markdown(pivots_table_html(analysis.pivots), unsafe_allow_html=True)
    st.caption("면책: 투자 자문이 아닙니다. 과거 가격 기반 지표이며 미래 수익을 보장하지 않습니다.")


if __name__ == "__main__":
    main()
