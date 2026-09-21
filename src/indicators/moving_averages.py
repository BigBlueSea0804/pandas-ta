"""심플·지수 이동평균과 가격 대비 신호."""

from __future__ import annotations

import pandas as pd
import pandas_ta_classic as ta

from config import MA_PERIODS
from indicators._series import last_number, last_two
from indicators.signals import Signal, action_ichimoku, action_ma


def _ma_signal(
    *,
    kind: str,
    period: int,
    close: float | None,
    mean: float | None,
) -> Signal:
    label = "익스포넨셜" if kind == "ema" else "심플"
    return Signal(
        id=f"{kind}_{period}",
        name=f"{label} 무빙 애버리지 ({period})",
        value=mean,
        action=action_ma(close, mean),
    )


def compute_moving_averages(ohlcv: pd.DataFrame) -> list[Signal]:
    high = ohlcv["high"]
    low = ohlcv["low"]
    close = ohlcv["close"]
    volume = ohlcv["volume"]
    last_close = last_number(close)
    signals: list[Signal] = []
    for period in MA_PERIODS:
        signals.append(
            _ma_signal(
                kind="ema",
                period=period,
                close=last_close,
                mean=last_number(ta.ema(close, length=period)),
            )
        )
        signals.append(
            _ma_signal(
                kind="sma",
                period=period,
                close=last_close,
                mean=last_number(ta.sma(close, length=period)),
            )
        )

    # as_dataframe=False: pandas-ta-classic 다음 버전부터 기본 반환값이 튜플에서
    # 단일 DataFrame으로 바뀔 예정이라, 지금 쓰는 튜플 형태를 명시해 경고를 끈다.
    ichimoku_result = ta.ichimoku(high, low, close, tenkan=9, kijun=26, senkou=52, as_dataframe=False)
    ichimoku_df = ichimoku_result[0] if ichimoku_result is not None else None
    # 두 번째 DataFrame은 시프트 전 선행스팬(= 앞으로 26봉에 그려질 값)이라,
    # 마지막 행이 이번 봉에서 계산한 선행스팬 A/B다.
    ichimoku_span = ichimoku_result[1] if ichimoku_result is not None else None
    ichimoku_base, prev_ichimoku_base = last_two(ichimoku_df, prefix="IKS_26")
    conversion, prev_conversion = last_two(ichimoku_df, prefix="ITS_9")
    signals.append(
        Signal(
            id="ichimoku_base_line",
            name="일목 기준선 (9, 26, 52, 26)",
            # 표에 보여주는 값은 TradingView와 같이 기준선(IKS_26)이고,
            # 액션만 구름대 전체를 보는 TV 규칙을 쓴다.
            value=ichimoku_base,
            action=action_ichimoku(
                close=last_close,
                conversion=conversion,
                base=ichimoku_base,
                previous_conversion=prev_conversion,
                previous_base=prev_ichimoku_base,
                lead1=last_number(ichimoku_span, prefix="ISA_9"),
                lead2=last_number(ichimoku_span, prefix="ISB_26"),
                # ISA_9/ISB_26은 이미 26봉 뒤로 밀려 있어서, 마지막 값이
                # 현재 위치에 그려진 구름대 그대로다.
                cloud_lead1=last_number(ichimoku_df, prefix="ISA_9"),
                cloud_lead2=last_number(ichimoku_df, prefix="ISB_26"),
            ),
        )
    )

    vwma = last_number(ta.vwma(close, volume, length=20))
    signals.append(
        Signal(
            id="vwma_20",
            name="볼륨 웨이티드 무빙 애버리지 (20)",
            value=vwma,
            action=action_ma(last_close, vwma),
        )
    )

    hma = last_number(ta.hma(close, length=9))
    signals.append(
        Signal(id="hma_9", name="헐 이동 평균 (9)", value=hma, action=action_ma(last_close, hma))
    )

    return signals
