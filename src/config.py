"""데이터 수집·지표 계산에 쓰는 공통 상수."""

from typing import Literal

OHLCV_COLUMNS = ("open", "high", "low", "close", "volume")
DEFAULT_PERIOD = "2y"
DEFAULT_INTERVAL = "1d"
MIN_BARS_SMA200 = 200

MA_PERIODS = (10, 20, 30, 50, 100, 200)
BBP_EMA_LENGTH = 13

Action = Literal["buy", "sell", "neutral"]
ACTION_LABELS = {"buy": "바이", "sell": "셀", "neutral": "뉴트럴"}

Rating = Literal["strong_sell", "sell", "neutral", "buy", "strong_buy"]
RATING_LABELS = {
    "strong_sell": "스트롱 셀",
    "sell": "셀",
    "neutral": "뉴트럴",
    "buy": "바이",
    "strong_buy": "스트롱 바이",
}
SCORE_STRONG = 0.5
SCORE_LEAN = 0.1

PIVOT_METHODS = ("classic", "fibonacci", "camarilla", "woodie", "dm")
PIVOT_LEVELS = ("R3", "R2", "R1", "P", "S1", "S2", "S3")
FIB_R1 = 0.382
FIB_R2 = 0.618
FIB_R3 = 1.0

# TradingView Technicals 스타일 1차 임계값
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
STOCH_OVERSOLD = 20
STOCH_OVERBOUGHT = 80
CCI_OVERSOLD = -100
CCI_OVERBOUGHT = 100
ADX_TREND_MIN = 20
STOCHRSI_OVERSOLD = 20
STOCHRSI_OVERBOUGHT = 80
WILLR_OVERSOLD = -80
WILLR_OVERBOUGHT = -20
UO_OVERSOLD = 30
UO_OVERBOUGHT = 70
