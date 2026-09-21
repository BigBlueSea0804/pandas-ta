# 주식·ETF 기술적 분석 대시보드

일봉 OHLCV로 오실레이터, 이동평균, 피봇을 계산하고 TradingView Technicals 스타일 게이지로 요약한다.

시세는 [yfinance](https://github.com/ranaroussi/yfinance)에서 받고, 지표는 [pandas-ta-classic](https://github.com/xgboosted/pandas-ta-classic)과 TradingView 정합을 위해 직접 구현한 우디 피봇·DM 피봇을 쓴다.

구현 단계는 [docs/WORK_PLAN.md](docs/WORK_PLAN.md)에 있다.

## 면책

이 도구는 **투자 자문이나 매매 신호가 아니다.** 교육·연구용 기술적 지표 요약이며, 손실에 대한 책임은 사용자에게 있다. 시세는 Yahoo Finance 기준이라 거래소·차트 서비스와 다를 수 있다.

## 요구 사항

- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## 설치

```bash
uv sync --group dev
```

## 실행

```bash
uv run streamlit run src/dashboard/app.py
```

브라우저에서 대시보드가 열린다. 네트워크 없이 화면만 보려면 사이드바에서 **샘플 데이터**를 선택한다.

### 티커 예시

| 시장 | 입력 | 설명 |
|------|------|------|
| 미국 주식 | `AAPL` | 애플 |
| 미국 ETF | `SPY`, `QQQ` | S&P 500, 나스닥 100 |
| 한국 코스피 | `005930.KS` | 삼성전자 |
| 한국 코스닥 | `035420.KQ` | NAVER 등 `.KQ` 접미사 |

기간은 `1y` / `2y` / `5y` (기본 `2y`). SMA 200을 쓰려면 거래일이 약 200봉 이상 필요하다.

## 테스트

네트워크 없이 파서·지표·게이지·표 HTML을 검증한다.

```bash
uv run pytest
```

## 화면에 나오는 것

- 게이지: 오실레이터 11표, 이동평균 12표, 둘을 합친 요약. 피봇은 투표에 넣지 않는다.
- 오실레이터: RSI, Stoch %K, CCI, ADX, AO, 모멘텀, MACD 레벨, StochRSI, Williams %R, Bull Bear Power, UO
- 이동평균: EMA/SMA 10, 20, 30, 50, 100, 200
- 피봇: 클래식, 피보나치, 카마릴라, 우디, DM

등급은 `score = (바이 − 셀) / 전체` 이다. `|score| < 0.1` 뉴트럴, `0.1` 이상 바이/셀, `0.5` 이상 스트롱 바이/셀.

AO·ADX·BBP 신호와 CCI 값은 TradingView Technicals(일봉)에 맞춰 두었다. TV 요약 게이지는 Hull MA, VWMA, 이치모쿠를 더 넣으므로 전체 점수까지 항상 같지는 않다.
