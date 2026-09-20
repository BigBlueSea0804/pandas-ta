"""오실레이터 11종과 액션."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from config import BBP_EMA_LENGTH
from indicators._series import last_number, last_three, last_two
from indicators.signals import (
    Signal,
    action_adx,
    action_ao,
    action_bbp,
    action_cci,
    action_rsi,
    action_signed,
    action_stoch,
    action_stochrsi,
    action_uo,
    action_willr,
)


def commodity_channel_index(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 20) -> pd.Series:
    """Typical price 대비 동일 윈도우 MAD 기반 CCI."""
    typical = (high + low + close) / 3.0

    def _cci(window: pd.Series) -> float:
        mean = float(window.mean())
        mad = float((window - mean).abs().mean())
        if mad == 0:
            return float("nan")
        return (float(window.iloc[-1]) - mean) / (0.015 * mad)

    return typical.rolling(length).apply(_cci, raw=False)


def compute_oscillators(ohlcv: pd.DataFrame) -> list[Signal]:
    high = ohlcv["high"]
    low = ohlcv["low"]
    close = ohlcv["close"]

    rsi = last_number(ta.rsi(close, length=14))
    stoch_k = last_number(ta.stoch(high, low, close, k=14, d=3, smooth_k=3), prefix="STOCHk")
    cci = last_number(commodity_channel_index(high, low, close, length=20))

    adx_df = ta.adx(high, low, close, length=14, tvmode=True)
    adx, prev_adx = last_two(adx_df, prefix="ADX_14")
    plus_di = last_number(adx_df, prefix="DMP_14")
    minus_di = last_number(adx_df, prefix="DMN_14")

    ao_value, ao_prev, ao_prev2 = last_three(ta.ao(high, low))
    mom = last_number(ta.mom(close, length=10))
    macd = last_number(ta.macd(close, fast=12, slow=26, signal=9), prefix="MACD_12")
    stochrsi_k = last_number(
        ta.stochrsi(close, length=14, rsi_length=14, k=3, d=3),
        prefix="STOCHRSIk",
    )
    willr = last_number(ta.willr(high, low, close, length=14))

    ema13 = ta.ema(close, length=BBP_EMA_LENGTH)
    bull = high - ema13
    bear = low - ema13
    bbp = last_number(bull + bear)
    last_close = last_number(close)
    last_ema = last_number(ema13)
    bull_now, bull_prev = last_two(bull)
    bear_now, bear_prev = last_two(bear)

    uo = last_number(ta.uo(high, low, close, fast=7, medium=14, slow=28))

    return [
        Signal(id="rsi_14", name="상대 강도 지수 (14)", value=rsi, action=action_rsi(rsi)),
        Signal(
            id="stoch_k",
            name="스토캐스틱 %K (14, 3, 3)",
            value=stoch_k,
            action=action_stoch(stoch_k),
        ),
        Signal(id="cci_20", name="커모디티 채널 인덱스 (20)", value=cci, action=action_cci(cci)),
        Signal(
            id="adx_14",
            name="애버리지 디렉셔널 인덱스 (14)",
            value=adx,
            action=action_adx(adx, plus_di, minus_di, prev_adx),
        ),
        Signal(id="ao", name="오썸 오실레이터", value=ao_value, action=action_ao(ao_value, ao_prev, ao_prev2)),
        Signal(id="mom_10", name="모멘텀 (10)", value=mom, action=action_signed(mom)),
        Signal(id="macd_12_26", name="MACD 레벨 (12, 26)", value=macd, action=action_signed(macd)),
        Signal(
            id="stochrsi_k",
            name="스토캐스틱 RSI 패스트 (3, 3, 14, 14)",
            value=stochrsi_k,
            action=action_stochrsi(stochrsi_k),
        ),
        Signal(
            id="willr_14",
            name="윌리엄스 퍼센트 레인지 (14)",
            value=willr,
            action=action_willr(willr),
        ),
        Signal(
            id="bbp",
            name="불 베어 파워",
            value=bbp,
            action=action_bbp(last_close, last_ema, bull_now, bear_now, bull_prev, bear_prev),
        ),
        Signal(
            id="uo",
            name="얼티미트 오실레이터 (7, 14, 28)",
            value=uo,
            action=action_uo(uo),
        ),
    ]
