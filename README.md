# 주식·ETF 기술적 분석 대시보드

yfinance와 pandas-ta로 오실레이터, 이동평균, 피봇을 계산하고 TradingView Technicals 스타일로 시각화한다.

- 계획 문서: [docs/WORK_PLAN.md](docs/WORK_PLAN.md)

## 환경 (Phase 0)

Python 3.12에서 아래 의존성을 설치·임포트까지 확인했다.

```bash
pip install -r requirements.txt
python -c "import yfinance, pandas_ta, pandas, streamlit, plotly, pytest; print('ok')"
```

구현은 Phase 1(데이터 레이어)부터 이어진다.
