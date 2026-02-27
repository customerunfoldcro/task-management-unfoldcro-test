"""Technical indicator engine - incremental computation."""

import numpy as np
import pandas as pd


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    """Compute Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Compute Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Compute MACD, Signal line, and Histogram."""
    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Compute Average True Range."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(span=period, adjust=False).mean()
    return atr


def compute_bollinger(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Compute Bollinger Bands."""
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    width = (upper - lower) / middle * 100  # as percentage
    return upper, middle, lower, width


def compute_all_indicators(df: pd.DataFrame) -> dict:
    """
    Compute all indicators for a symbol's OHLCV DataFrame.

    Args:
        df: DataFrame with columns [open, high, low, close, volume] indexed by date.

    Returns:
        Dict of indicator values for the latest bar.
    """
    if df is None or len(df) < 200:
        return None

    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    # EMAs
    ema20 = compute_ema(close, 20)
    ema50 = compute_ema(close, 50)
    ema200 = compute_ema(close, 200)

    # RSI
    rsi14 = compute_rsi(close, 14)

    # MACD
    macd_line, macd_signal, macd_hist = compute_macd(close)

    # ATR
    atr14 = compute_atr(high, low, close, 14)
    atr_pct = (atr14 / close * 100)

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower, bb_width = compute_bollinger(close)

    # Volume average
    vol_avg_20d = volume.rolling(window=20).mean()
    vol_ratio = volume / vol_avg_20d.replace(0, np.nan)

    # 20-day high/low
    high_20d = high.rolling(window=20).max()
    low_20d = low.rolling(window=20).min()

    # Get the latest values
    idx = -1
    latest = {
        "ema20": _safe(ema20.iloc[idx]),
        "ema50": _safe(ema50.iloc[idx]),
        "ema200": _safe(ema200.iloc[idx]),
        "rsi14": _safe(rsi14.iloc[idx]),
        "macd": _safe(macd_line.iloc[idx]),
        "macd_signal": _safe(macd_signal.iloc[idx]),
        "macd_hist": _safe(macd_hist.iloc[idx]),
        "atr14": _safe(atr14.iloc[idx]),
        "atr_pct": _safe(atr_pct.iloc[idx]),
        "bb_upper": _safe(bb_upper.iloc[idx]),
        "bb_middle": _safe(bb_middle.iloc[idx]),
        "bb_lower": _safe(bb_lower.iloc[idx]),
        "bb_width": _safe(bb_width.iloc[idx]),
        "vol_avg_20d": _safe(vol_avg_20d.iloc[idx]),
        "vol_ratio": _safe(vol_ratio.iloc[idx]),
        "high_20d": _safe(high_20d.iloc[idx]),
        "low_20d": _safe(low_20d.iloc[idx]),
    }

    # Previous values for trend detection
    if len(df) > 1:
        latest["prev_macd_hist"] = _safe(macd_hist.iloc[-2])
        latest["prev_close"] = _safe(close.iloc[-2])
    else:
        latest["prev_macd_hist"] = latest["macd_hist"]
        latest["prev_close"] = latest["ema20"]

    return latest


def compute_price_changes(df: pd.DataFrame) -> dict:
    """Compute price changes over various periods."""
    if df is None or len(df) < 20:
        return {"pct_1d": 0, "pct_5d": 0, "pct_20d": 0, "gap_pct": 0}

    close = df["close"]
    open_price = df["open"]
    latest_close = close.iloc[-1]

    pct_1d = ((latest_close / close.iloc[-2]) - 1) * 100 if len(df) > 1 else 0
    pct_5d = ((latest_close / close.iloc[-5]) - 1) * 100 if len(df) > 5 else 0
    pct_20d = ((latest_close / close.iloc[-20]) - 1) * 100 if len(df) > 20 else 0

    # Gap: today's open vs yesterday's close
    gap_pct = 0
    if len(df) > 1:
        gap_pct = ((open_price.iloc[-1] / close.iloc[-2]) - 1) * 100

    return {
        "pct_1d": round(_safe(pct_1d), 2),
        "pct_5d": round(_safe(pct_5d), 2),
        "pct_20d": round(_safe(pct_20d), 2),
        "gap_pct": round(_safe(gap_pct), 2),
    }


def detect_higher_highs_lows(df: pd.DataFrame, lookback: int = 10) -> bool:
    """Detect if recent price action shows higher highs and higher lows."""
    if len(df) < lookback + 5:
        return False

    recent = df.tail(lookback)
    highs = recent["high"].values
    lows = recent["low"].values

    # Check if highs are trending up and lows are trending up
    mid = len(highs) // 2
    first_half_high = np.max(highs[:mid])
    second_half_high = np.max(highs[mid:])
    first_half_low = np.min(lows[:mid])
    second_half_low = np.min(lows[mid:])

    return second_half_high > first_half_high and second_half_low > first_half_low


def detect_lower_highs_lows(df: pd.DataFrame, lookback: int = 10) -> bool:
    """Detect lower highs and lower lows (downtrend)."""
    if len(df) < lookback + 5:
        return False

    recent = df.tail(lookback)
    highs = recent["high"].values
    lows = recent["low"].values

    mid = len(highs) // 2
    first_half_high = np.max(highs[:mid])
    second_half_high = np.max(highs[mid:])
    first_half_low = np.min(lows[:mid])
    second_half_low = np.min(lows[mid:])

    return second_half_high < first_half_high and second_half_low < first_half_low


def _safe(val):
    """Convert numpy/pandas values to Python float, handling NaN."""
    if val is None:
        return 0.0
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return 0.0
        return round(f, 4)
    except (TypeError, ValueError):
        return 0.0
