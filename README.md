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

- 게이지: 오실레이터 11표, 이동평균 15표, 둘을 합친 요약. 피봇은 투표에 넣지 않는다.
- 오실레이터: RSI, Stoch %K, CCI, ADX, AO, 모멘텀, MACD 레벨, StochRSI, Williams %R, Bull Bear Power, UO
- 이동평균: EMA/SMA 10, 20, 30, 50, 100, 200, 일목 기준선 (9, 26, 52, 26), VWMA (20), Hull MA (9)
- 피봇: 클래식, 피보나치, 카마릴라, 우디, DM

등급은 오실레이터·이동평균 각각 `(바이 − 셀) / 전체`이고, 요약은 **두 등급의 평균**이다
(TV도 카운트만 합산해 보여 주고 계산은 평균으로 한다). `|score| > 0.1` 이면 바이/셀,
`> 0.5` 면 스트롱 바이/셀, 그 외는 뉴트럴이다.

액션 규칙은 TradingView가 공개한 [TechnicalRating 라이브러리](https://www.tradingview.com/pine-script-reference/)
원문(`calcRatingAll()`)을 그대로 옮겼다. 값이 밴드를 넘겼다는 것만으로 신호를 내는
지표는 하나도 없고, 대부분 방향·교차·추세 필터가 함께 걸린다. 예를 들어

- RSI·CCI·윌리엄스 %R: 밴드 밖에서 **되돌아설 때만** 신호
- 스토캐스틱·스토캐스틱 RSI: %K·%D가 **모두** 밴드를 넘고 서로 교차해야 하며,
  스토캐스틱 RSI는 추세(EMA50)가 **반대** 방향일 때만
- ADX: ADX > 20 이고 **ADX가 직전 봉보다 올랐을 때** DI 방향을 따른다
- UO: 70 위가 **바이**, 30 아래가 **셀** (역추세로 읽지 않는다)
- 불 베어 파워: 추세 판정에 EMA13이 아니라 **EMA50**을 쓴다

일목만은 이동평균 중 유일하게 값 비교가 아니다. 표에 보이는 값은 기준선(26봉
도너치안)이지만, 액션은 구름·기준선·전환선·종가가 한 방향으로 줄을 설 때만 나온다.

```
바이: lead1[26] > lead2[26] and 기준선 > lead1[26] and 전환선 > 기준선 and 종가 > 전환선
셀 : 부호를 모두 뒤집은 조건
그 외: 뉴트럴
```

그래서 종가가 기준선 아래여도 셀이 아닌 경우가 흔하다. NYSE:IBM 일봉(종가 229.55,
기준선 239.6075)이 그런 경우로, 종가가 전환선(240.5975) 아래가 아니라 위라 뉴트럴이다.
이 규칙을 쓰면 세 게이지가 TV 실측값(`Recommend.Other` -3/11, `Recommend.MA` -14/15,
`Recommend.All` -0.6030)과 정확히 맞는다(`tests/fixtures/ibm_1d_tv.csv` 골든 회귀 테스트).
