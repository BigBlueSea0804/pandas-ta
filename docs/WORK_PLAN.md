# 기술적 분석 대시보드 작업 계획

TradingView Technicals 위젯과 동일한 구성으로, 주식·ETF의 오실레이터, 이동평균, 피봇을 계산하고 게이지로 요약한다.

대상 스택: **Python + yfinance + pandas-ta + Streamlit(Plotly)**

---

## 1. 목표와 범위

### 목표
- 티커(주식/ETF) 입력 시 OHLCV를 받아 기술적 지표를 계산한다.
- 각 지표에 **값 + 액션(바이/셀/뉴트럴)** 을 부여한다.
- 오실레이터·이동평균 표를 그리고, 투표 집계로 **스트롱 셀 ~ 스트롱 바이** 게이지를 표시한다.
- 전일 고가·저가·종가 기준으로 5종 피봇(클래식, 피보나치, 카마릴라, 우디, DM)을 표로 보여준다.

### 이번 범위에 포함
- 일봉 기준 분석 (TradingView Technicals 기본과 동일)
- 단일 티커 대시보드
- 한국/미국 티커 (`005930.KS`, `AAPL`, `SPY` 등)

### 이번 범위에서 제외 (후속)
- 인트라데이(1h, 15m) 타임프레임 전환
- 포트폴리오 일괄 스캔, 알림, 백테스트
- 로그인·DB 저장

---

## 2. 화면 구성 (이미지 기준)

대시보드는 위에서 아래로 4개 블록이다.

| 블록 | 내용 |
|------|------|
| 요약 게이지 | 오실레이터 / 전체 요약 / 무빙 애버리지. 바늘 + 하단 셀·뉴트럴·바이 카운트 |
| 오실레이터 표 | 이름, 값, 액션 |
| 무빙 애버리지 표 | EMA/SMA 10·20·30·50·100·200, 값, 액션 |
| 피봇 표 | 행: R3~S3, 열: 클래식·피보나치·카마릴라·우디·DM |

UI는 다크 테마, 바이=파랑, 셀=빨강, 뉴트럴=회색.

---

## 3. 권장 디렉터리 구조

```
src/
  data/
    fetch.py          # yfinance OHLCV, 티커 정규화
  indicators/
    oscillators.py    # RSI, Stoch, CCI, ADX, AO, MOM, MACD, StochRSI, W%R, BBP, UO
    moving_averages.py
    pivots.py         # classic / fib / camarilla / woodie / dm
    signals.py        # 지표값 → buy/sell/neutral
    summary.py        # 투표 집계 + 게이지 등급
  dashboard/
    app.py            # Streamlit 엔트리
    gauges.py         # Plotly semicircle gauge
    tables.py
  config.py           # 기간, 컬럼명, 임계값
tests/
  test_fetch.py
  test_signals.py
  test_pivots.py
  test_summary.py
pyproject.toml
uv.lock
```

패키지 관리는 **uv**. 엔트리는 `uv run streamlit run src/dashboard/app.py`.

---

## 4. 데이터 수집 (yfinance)

### 4.1 다운로드
- `yf.download(ticker, period="2y", interval="1d", auto_adjust=True)`
- SMA 200과 안정적인 MACD/ADX를 위해 **최소 250거래일** 필요. `2y`면 충분하다.
- 컬럼을 `open, high, low, close, volume` 소문자로 통일한다. MultiIndex(`Adj Close` 등)는 flatten 한다.

### 4.2 티커 규칙
- 미국: `AAPL`, `QQQ`
- 한국 코스피/코스닥: `005930.KS`, `035420.KQ`
- 입력 검증: 빈 데이터, 상장 기간 부족(200봉 미만) 시 사용자에게 경고하고 계산 가능한 지표만 표시.

### 4.3 주의
- Yahoo는 rate limit이 있다. 동일 티커는 `@st.cache_data(ttl=3600)` 로 캐시한다.
- 한국 종목은 원화 단위라 오실레이터 절대값(AO, MOM, MACD, BBP)이 이미지처럼 수천 단위가 될 수 있다. 표시는 천 단위 콤마, 소수 자릿수는 가격 스케일에 따라 조절한다.

---

## 5. 지표 계산 (pandas-ta)

pandas-ta는 최근 유지보수가 불안정하다. **pandas-ta-classic** 또는 동일 API의 포크를 기본으로 두고, 실패 시 핵심 지표만 pandas로 직접 구현하는 fallback을 `indicators/` 안에 둔다.

계산은 시계열 전체에 한 뒤 **마지막 유효값(iloc[-1])** 만 표에 쓴다.

### 5.1 오실레이터 (이미지 11종)

| UI 이름 | 파라미터 | pandas-ta | 사용할 값 |
|---------|----------|-----------|-----------|
| 상대 강도 지수 (14) | length=14 | `ta.rsi(close, 14)` | RSI |
| 스토캐스틱 %K (14, 3, 3) | k=14, d=3, smooth=3 | `ta.stoch(high, low, close, 14, 3, 3)` | STOCHk |
| 커모디티 채널 인덱스 (20) | 20 | `ta.cci(high, low, close, 20)` | CCI |
| 애버리지 디렉셔널 인덱스 (14) | 14 | `ta.adx(high, low, close, 14)` | ADX_14 (DI+/DI-는 신호용) |
| 오썸 오실레이터 | 5, 34 | `ta.ao(high, low)` | AO |
| 모멘텀 (10) | 10 | `ta.mom(close, 10)` | MOM |
| MACD 레벨 (12, 26) | 12, 26, signal=9 | `ta.macd(close, 12, 26, 9)` | MACD 라인 (히스토그램 아님) |
| 스토캐스틱 RSI 패스트 (3, 3, 14, 14) | rsi=14, stoch=14, k=3, d=3 | `ta.stochrsi(close, 14, 14, 3, 3)` | %K |
| 윌리엄스 퍼센트 레인지 (14) | 14 | `ta.willr(high, low, close, 14)` | WILLR |
| 불 베어 파워 | 13 | `close - ta.ema(close, 13)` (Elder Bears/Bulls의 합성에 가깝게 close−EMA13) | BBP |
| 얼티미트 오실레이터 (7, 14, 28) | 7, 14, 28 | `ta.uo(high, low, close)` | UO |

Bull Bear Power는 라이브러리마다 정의가 다르다. TradingView는 보통 **Elder Bulls Power + Bears Power** 조합을 쓴다. 1차 구현은 `close - EMA(13)` 로 두고, 값·신호가 TV와 어긋나면 `high-EMA13`, `low-EMA13` 을 각각 계산해 합치는 방식으로 맞춘다.

### 5.2 이동평균 (이미지 12종)

기간: **10, 20, 30, 50, 100, 200**  
종류: `ta.ema(close, n)`, `ta.sma(close, n)`  
값: 해당 기간 MA의 최신 값.

### 5.3 피봇 (전일 H/L/C 기준)

전일: `high.iloc[-2]`, `low.iloc[-2]`, `close.iloc[-2]`  
우디만 당일 시가(`open.iloc[-1]`)를 사용한다.

`range = high - low`

**클래식**
- P = (H+L+C)/3
- R1 = 2P − L, S1 = 2P − H
- R2 = P + range, S2 = P − range
- R3 = H + 2(P − L), S3 = L − 2(H − P)

**피보나치**
- P = (H+L+C)/3
- R1 = P + 0.382×range, S1 = P − 0.382×range
- R2 = P + 0.618×range, S2 = P − 0.618×range
- R3 = P + 1.000×range, S3 = P − 1.000×range

**카마릴라**
- P = (H+L+C)/3 (표시용, TV는 P를 동일하게 보여 주는 경우가 많음)
- R1 = C + range×1.1/12, S1 = C − range×1.1/12
- R2 = C + range×1.1/6,  S2 = C − range×1.1/6
- R3 = C + range×1.1/4,  S3 = C − range×1.1/4

**우디**
- P = (H+L+2×Open)/4
- R1 = 2P − L, S1 = 2P − H
- R2 = P + range, S2 = P − range
- R3 = H + 2(P − L), S3 = L − 2(H − P)

**DM (DeMark)**
- X = C < O 이면 H+2L+C, C > O 이면 2H+L+C, 같으면 H+L+2C
- P = X/4, R1 = X/2 − L, S1 = X/2 − H
- R2/R3/S2/S3는 TV처럼 `—` 처리

피봇은 신호(바이/셀)를 내지 않고 가격 레벨만 표시한다.

---

## 6. 액션(바이/셀/뉴트럴) 규칙

TradingView Technicals와 맞추는 것이 1차 기준이다. 구현 후 동일 종목·동일 일봉으로 TV 위젯과 샘플 대조한다.

### 6.1 오실레이터

| 지표 | 셀 | 뉴트럴 | 바이 |
|------|----|--------|------|
| RSI | ≥ 70 | 30~70 | ≤ 30 |
| Stoch %K | ≥ 80 | 20~80 | ≤ 20 |
| CCI | ≥ 100 | −100~100 | ≤ −100 |
| ADX | 방향만 사용. ADX < 20 이면 뉴트럴. ADX≥20 이고 −DI > +DI 이면 셀, +DI > −DI 이면 바이 | | |
| AO | 값 < 0 이고 직전 대비 하락 → 셀. 값 > 0 이고 직전 대비 상승 → 바이. 그 외 뉴트럴 (TV는 saucer/cross 규칙 사용, 1차는 부호+기울기) | | |
| MOM | < 0 셀, > 0 바이, = 0 뉴트럴 | | |
| MACD 레벨 | < 0 셀, > 0 바이 | | |
| Stoch RSI %K | ≥ 80 셀, ≤ 20 바이, 그 외 뉴트럴 | | |
| Williams %R | ≥ −20 셀, ≤ −80 바이, 그 외 뉴트럴 | | |
| BBP | < 0 셀, > 0 바이 | | |
| UO | ≥ 70 셀, ≤ 30 바이, 그 외 뉴트럴 | | |

과매수 구간을 **셀**, 과매도 구간을 **바이**로 두는 점은 역추세 오실레이터의 TV 관례와 같다. 추세 지표(MACD, MOM, BBP, ADX)는 부호·방향 그대로 따른다.

### 6.2 이동평균

- `close > MA` → **바이**
- `close < MA` → **셀**
- 같으면 뉴트럴 (실무상 거의 없음)

이미지에서 EMA(50)만 셀, 나머지 다수가 바이인 패턴이 이 규칙과 일치한다.

### 6.3 표시 형식
- 값은 정수에 가깝게 반올림하되, 가격이 작은 종목은 소수점 2~4자리.
- 액션 텍스트: `바이` / `셀` / `뉴트럴`
- 색: 바이 `#3b82f6`, 셀 `#ef4444`, 뉴트럴 `#9ca3af`

---

## 7. 요약 게이지

### 7.1 투표
- 오실레이터 11표, 이동평균 12표, 전체 23표.
- 피봇은 투표에 넣지 않는다.
- 하단 숫자 = 각 그룹의 셀 / 뉴트럴 / 바이 개수. 이미지 예: 오실레이터 1/9/1, MA 2/1/12, 요약 3/10/13.

### 7.2 등급 (TV와 동일한 5구간)

`score = (n_buy − n_sell) / n_total` 을 −1~+1로 두고 바늘 위치에 쓴다.

텍스트 등급은 비율 기준(초기값, 샘플 대조 후 미세 조정):

| 조건 | 라벨 |
|------|------|
| buy 비율 ≥ 0.7 이고 sell보다 많음 | 스트롱 바이 |
| buy > sell | 바이 |
| buy == sell (뉴트럴 포함 동률에 가깝면) | 뉴트럴 |
| sell > buy | 셀 |
| sell 비율 ≥ 0.7 | 스트롱 셀 |

더 안정적인 방식: `score` 임계값  
`-1.0, -0.5, -0.1, 0.1, 0.5, 1.0` → 스트롱 셀 / 셀 / 뉴트럴 / 바이 / 스트롱 바이.

이미지처럼 MA가 12바이·2셀이면 스트롱 바이, 오실레이터 1/9/1이면 뉴트럴, 합치면 바이.

### 7.3 시각화
- Plotly `go.Indicator` 또는 반원 `Scatterpolar`/`pie` 변형.
- 색 그라데이션: 빨강(셀) → 회색(뉴트럴) → 파랑(바이).
- 바늘은 `score`를 −90°~+90°로 매핑.
- 중앙 라벨은 등급 텍스트.

---

## 8. 대시보드 UX

1. 사이드바: 티커 입력, 기간(`1y`/`2y`/`5y`), 새로고침.
2. 헤더: 종목명, 최근 종가, 전일 대비.
3. 게이지 3개 (한 행).
4. 탭 또는 expander: 오실레이터 / 무빙 애버리지 / 피봇.
5. (선택) 하단에 종가 + SMA20/50/200 캔들 차트. 1차 범위에는 필수는 아님.

Streamlit 컬럼으로 표를 HTML/dataframe 스타일링하거나 `st.dataframe` + 조건부 색을 사용한다.

---

## 9. 구현 단계

### Phase 0 — 환경
- `pyproject.toml` + `uv.lock`: `yfinance`, `pandas`, `numpy`, `pandas-ta`, `streamlit`, `plotly`, `pytest`(dev group)
- Python 3.12 (`requires-python = ">=3.12,<3.13"`). `pandas-ta`가 구버전 pandas에 묶여 있으면 포크 또는 직접 구현으로 우회.

### Phase 1 — 데이터 레이어
- `fetch.py`: 다운로드, 컬럼 정규화, 최소 봉 수 검증.
- 단위 테스트: 픽스처 CSV로 파서만 검증 (네트워크 없이).

### Phase 2 — 지표 + 신호
- 오실레이터·MA·피봇 순으로 함수 작성. 입력은 DataFrame, 출력은 `list[IndicatorRow]` / `dict` 같은 타입.
- `signals.py`에 임계값 상수화 (`config.py`).
- 골든 픽스처: 알려진 OHLCV 한 세트로 피봇 숫자와 MA 교차 신호를 고정.

### Phase 3 — 요약
- 카운트와 `score`, 5단계 라벨.
- 이미지와 같은 카운트 합산이 나오는지 테스트.

### Phase 4 — UI
- Streamlit 레이아웃, 다크 CSS, 게이지, 세 표.
- 티커 캐시, 에러 메시지(없는 티커, 데이터 부족).

### Phase 5 — TV 대조
- 동일 종목(예: `AAPL`, `005930.KS`) 일봉으로 TradingView Technicals와 액션·값이 크게 어긋나지 않는지 확인.
- 어긋남이 큰 지표(AO, BBP, ADX)만 규칙 수정.

### Phase 6 — 품질
- `pytest` CI 수준 로컬 실행.
- README: 설치, 실행, 티커 예시, 면책(투자 조언 아님).

---

## 10. 핵심 데이터 계약

```python
@dataclass
class Signal:
    name: str
    value: float
    action: Literal["buy", "sell", "neutral"]

@dataclass
class GaugeSummary:
    sell: int
    neutral: int
    buy: int
    score: float          # -1 ~ 1
    rating: Literal["strong_sell", "sell", "neutral", "buy", "strong_buy"]

@dataclass
class AnalysisResult:
    ticker: str
    close: float
    oscillators: list[Signal]
    moving_averages: list[Signal]
    oscillator_gauge: GaugeSummary
    ma_gauge: GaugeSummary
    overall_gauge: GaugeSummary
    pivots: dict[str, dict[str, float | None]]  # method -> {R3..S3}
```

대시보드는 `AnalysisResult`만 렌더링하고, 계산은 UI와 분리한다. 나중에 FastAPI로 바꿔도 같은 객체를 JSON으로 내보내면 된다.

---

## 11. 테스트 전략

| 종류 | 대상 |
|------|------|
| 순수 함수 | 피봇 공식, 신호 임계값, 게이지 등급 |
| 픽스처 OHLCV | SMA/EMA 마지막 값, RSI 범위 0~100 |
| 스모크 | `analyze("AAPL")` 가 23개 신호 + 피봇을 반환 (네트워크 허용 시 수동) |
| UI | 로컬에서 티커 변경, 빈 입력, 잘못된 티커 |

네트워크가 없는 CI에서는 yfinance 호출을 모킹한다.

---

## 12. 리스크와 대응

| 리스크 | 대응 |
|--------|------|
| pandas-ta 설치/버전 충돌 | pandas-ta-classic 또는 RSI/MACD/MA만 pandas 재구현 |
| yfinance 컬럼/타임존 변경 | flatten + tz-naive 인덱스로 정규화 |
| TV와 신호 불일치 | 임계값을 config로 분리하고 Phase 5에서 조정. AO/BBP가 가장 흔히 다름 |
| 한국 종목 가격 스케일 | 값 포맷만 가격 자릿수에 맞추고, 신호 규칙은 동일 |
| 상장 짧은 ETF | 200 MA는 `None` + 표에서 `—`, 게이지 분모에서 제외 |

---

## 13. 작업 순서 요약

1. 의존성 고정 및 OHLCV 정규화.
2. MA 12개 + 가격 대비 바이/셀 (가장 단순, 게이지 검증용).
3. 오실레이터 11개와 임계값.
4. 피봇 5방법.
5. 투표·게이지.
6. Streamlit 다크 대시보드.
7. TradingView 샘플 대조 후 임계값 튜닝.
8. 테스트·README.

이 순서면 중간에 이미 “표 + 게이지”가 동작하므로, 지표를 하나씩 붙여 가며 화면을 확인할 수 있다.
