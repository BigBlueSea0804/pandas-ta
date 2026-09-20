# 주식·ETF 기술적 분석 대시보드

yfinance와 pandas-ta로 오실레이터, 이동평균, 피봇을 계산하고 TradingView Technicals 스타일로 시각화한다.

- 계획 문서: [docs/WORK_PLAN.md](docs/WORK_PLAN.md)

## 환경

Python 3.12, 패키지 관리는 [uv](https://docs.astral.sh/uv/).

```bash
uv sync --group dev
uv run python -c "import yfinance, pandas_ta, pandas, streamlit, plotly, pytest; print('ok')"
uv run pytest
```

## 데이터 레이어 (Phase 1)

`src/data/fetch.py`가 yfinance OHLCV를 `open/high/low/close/volume`으로 정규화한다.

## 지표·신호 (Phase 2)

`src/indicators/`에서 오실레이터 11개, 이동평균 12개, 피봇 5방법을 계산하고 바이/셀/뉴트럴을 붙인다.

## 요약 게이지 (Phase 3)

값이 있는 신호만 투표한다. `score = (바이 − 셀) / 전체` 로 스트롱 셀~스트롱 바이 등급을 정한다. 피봇은 투표에 넣지 않는다.

## 대시보드 (Phase 4)

```bash
uv run streamlit run src/dashboard/app.py
```

사이드바에서 티커·기간을 고르거나, 네트워크 없이 보려면 샘플 데이터를 선택한다.
