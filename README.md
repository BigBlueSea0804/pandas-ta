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
