"""데이터 수집·지표 계산에 쓰는 공통 상수."""

from dataclasses import dataclass
from typing import Literal

OHLCV_COLUMNS = ("open", "high", "low", "close", "volume")
DEFAULT_PERIOD = "2y"
DEFAULT_INTERVAL = "1d"
MIN_BARS_SMA200 = 200


@dataclass(frozen=True)
class Timeframe:
    """TradingView 스타일 시간 단위 하나. yfinance가 직접 지원하지 않는
    2시간/4시간은 resample_rule로 1시간봉을 다운받아 합성한다."""

    label: str
    yf_interval: str
    period: str
    pivot_anchor: str
    resample_rule: str | None = None


# 피봇 앵커는 TradingView "Pivot Points Standard"의 Pivots timeframe=Auto 규칙을 따른다.
#   15분 이하 인트라데이 -> 1D, 15분 초과 인트라데이 -> 1W, 일봉 -> 1M, 주봉 이상 -> 12M
# 즉 일봉 차트의 피봇은 "전일"이 아니라 "전월" OHLC로 계산된다.
PIVOT_ANCHOR_DAILY = "D"
PIVOT_ANCHOR_WEEKLY = "W"
PIVOT_ANCHOR_MONTHLY = "ME"
PIVOT_ANCHOR_YEARLY = "YE"
DEFAULT_PIVOT_ANCHOR = PIVOT_ANCHOR_MONTHLY

# TradingView Technicals 상단 탭과 동일한 순서.
TIMEFRAMES: tuple[Timeframe, ...] = (
    Timeframe("1분", "1m", "5d", PIVOT_ANCHOR_DAILY),
    Timeframe("5분", "5m", "1mo", PIVOT_ANCHOR_DAILY),
    Timeframe("15분", "15m", "1mo", PIVOT_ANCHOR_DAILY),
    Timeframe("30분", "30m", "1mo", PIVOT_ANCHOR_WEEKLY),
    Timeframe("1시간", "60m", "2y", PIVOT_ANCHOR_WEEKLY),
    Timeframe("2시간", "60m", "2y", PIVOT_ANCHOR_WEEKLY, resample_rule="2h"),
    Timeframe("4시간", "60m", "2y", PIVOT_ANCHOR_WEEKLY, resample_rule="4h"),
    Timeframe("1일", "1d", DEFAULT_PERIOD, PIVOT_ANCHOR_MONTHLY),
    Timeframe("1주", "1wk", "5y", PIVOT_ANCHOR_YEARLY),
    Timeframe("1달", "1mo", "10y", PIVOT_ANCHOR_YEARLY),
)
TIMEFRAME_LABELS = tuple(timeframe.label for timeframe in TIMEFRAMES)
DEFAULT_TIMEFRAME = "1일"

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

BUY_COLOR = "#3b82f6"
SELL_COLOR = "#ef4444"
NEUTRAL_COLOR = "#9ca3af"
ACTION_COLORS = {"buy": BUY_COLOR, "sell": SELL_COLOR, "neutral": NEUTRAL_COLOR}

PIVOT_METHOD_LABELS = {
    "classic": "클래식",
    "fibonacci": "피보나치",
    "camarilla": "카마릴라",
    "woodie": "우디",
    "dm": "DM",
}
