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

`src/indicators/`에서 오실레이터 11개, 이동평균 12개, 피봇 5방법을 계산하고 바이/셀/뉴트럴을 붙인다. 네트워크 없는 테스트:

```bash
uv run pytest
```
