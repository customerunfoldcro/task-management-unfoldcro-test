"""Signal scoring engine: Strong Buy / Buy / Neutral / Sell / Strong Sell."""

import json
from datetime import datetime, timedelta

from .config import (
    ATR_PCT_MAX,
    ATR_PCT_MIN,
    BUY_THRESHOLD,
    NEUTRAL_LOW,
    SELL_THRESHOLD,
    STRONG_BUY_THRESHOLD,
)
from .indicators import detect_higher_highs_lows, detect_lower_highs_lows


def compute_signal(indicators: dict, price_changes: dict, df, events: list = None, news_sentiment: float = None):
    """
    Compute the composite signal score and classification.

    Args:
        indicators: Latest indicator values from compute_all_indicators().
        price_changes: From compute_price_changes().
        df: Full OHLCV DataFrame for pattern detection.
        events: List of upcoming events (earnings, etc.).
        news_sentiment: Average recent news sentiment (-1 to 1).

    Returns:
        dict with score, label, component scores, reasons, and risks.
    """
    if indicators is None:
        return _neutral_signal()

    close = df["close"].iloc[-1] if df is not None and len(df) > 0 else 0
    reasons = []
    risks = []

    # --- Determine market direction (bullish or bearish bias) ---
    bullish_points = 0
    bearish_points = 0

    # Count directional signals
    if indicators["ema20"] > indicators["ema50"]:
        bullish_points += 1
    else:
        bearish_points += 1

    if indicators["ema50"] > indicators["ema200"]:
        bullish_points += 1
    else:
        bearish_points += 1

    if close > indicators["ema20"]:
        bullish_points += 1
    else:
        bearish_points += 1

    if indicators["rsi14"] > 50:
        bullish_points += 1
    else:
        bearish_points += 1

    is_bearish = bearish_points > bullish_points

    if is_bearish:
        return _compute_bearish_signal(indicators, price_changes, df, events, news_sentiment, close)
    else:
        return _compute_bullish_signal(indicators, price_changes, df, events, news_sentiment, close)


def _compute_bullish_signal(indicators, price_changes, df, events, news_sentiment, close):
    """Compute score from bullish perspective (higher = stronger buy)."""
    reasons = []
    risks = []

    # === TREND (40 points) ===
    trend_score = 0

    if indicators["ema20"] > indicators["ema50"]:
        trend_score += 10
        reasons.append("EMA20 above EMA50 (short-term uptrend)")

    if indicators["ema50"] > indicators["ema200"]:
        trend_score += 10
        reasons.append("EMA50 above EMA200 (long-term uptrend)")

    if close > indicators["ema20"]:
        trend_score += 10
        reasons.append("Price above EMA20")

    if detect_higher_highs_lows(df):
        trend_score += 10
        reasons.append("Higher highs and higher lows pattern")

    # === MOMENTUM (25 points) ===
    momentum_score = 0

    if indicators["rsi14"] > 55:
        momentum_score += 10
        reasons.append(f"RSI({indicators['rsi14']:.1f}) shows bullish momentum")
    elif indicators["rsi14"] > 50:
        momentum_score += 5

    macd_hist = indicators.get("macd_hist", 0)
    prev_macd_hist = indicators.get("prev_macd_hist", 0)
    if macd_hist > 0 and macd_hist > prev_macd_hist:
        momentum_score += 10
        reasons.append("MACD histogram positive and rising")
    elif macd_hist > 0:
        momentum_score += 5
        reasons.append("MACD histogram positive")

    if close > indicators["high_20d"] * 0.99 and indicators.get("vol_ratio", 0) > 1.2:
        momentum_score += 5
        reasons.append("Breakout near 20-day high with volume")

    # === VOLUME & PARTICIPATION (20 points) ===
    volume_score = 0

    vol_ratio = indicators.get("vol_ratio", 0)
    if vol_ratio > 1.5:
        volume_score += 10
        reasons.append(f"Volume {vol_ratio:.1f}x above 20-day average")
    elif vol_ratio > 1.2:
        volume_score += 5

    atr14 = indicators.get("atr14", 0)
    if atr14 > 0:
        open_price = df["open"].iloc[-1] if df is not None and len(df) > 0 else close
        true_range = max(
            df["high"].iloc[-1] - df["low"].iloc[-1],
            abs(df["high"].iloc[-1] - indicators.get("prev_close", close)),
            abs(df["low"].iloc[-1] - indicators.get("prev_close", close)),
        ) if df is not None and len(df) > 0 else 0

        if true_range > 1.3 * atr14 and price_changes.get("pct_1d", 0) > 0:
            volume_score += 10
            reasons.append("Range expansion day aligned with uptrend")
        elif true_range > 1.1 * atr14 and price_changes.get("pct_1d", 0) > 0:
            volume_score += 5

    # === RISK ADJUSTMENT (up to -15 points) ===
    risk_penalty = 0

    # Earnings proximity
    if events:
        now = datetime.utcnow()
        for evt in events:
            if evt.get("event_type") == "earnings":
                evt_date = evt.get("event_date")
                if evt_date and (evt_date - now).days <= 5:
                    risk_penalty += 10
                    risks.append("Earnings within 5 trading days")
                    break

    # Gap risk
    gap_pct = abs(price_changes.get("gap_pct", 0))
    if atr14 > 0:
        atr_pct_val = indicators.get("atr_pct", 0)
        if gap_pct > 2 * atr_pct_val and atr_pct_val > 0:
            risk_penalty += 5
            risks.append(f"Large gap ({gap_pct:.1f}%) exceeds 2x ATR%")

    # News negative sentiment
    if news_sentiment is not None and news_sentiment < -0.3:
        risk_penalty += 5
        risks.append("Negative news sentiment spike")

    # === COMPOSITE SCORE ===
    raw_score = trend_score + momentum_score + volume_score - risk_penalty
    score = max(0, min(100, raw_score))

    label = _classify(score)

    # Swing suitability check
    atr_pct_val = indicators.get("atr_pct", 0)
    swing_suitable = ATR_PCT_MIN <= atr_pct_val <= ATR_PCT_MAX

    if not swing_suitable and label in ("Strong Buy", "Strong Sell"):
        if atr_pct_val < ATR_PCT_MIN:
            risks.append(f"ATR% too low ({atr_pct_val:.1f}%) for swing trading")
        elif atr_pct_val > ATR_PCT_MAX:
            risks.append(f"ATR% too high ({atr_pct_val:.1f}%) - excessive volatility")

    return {
        "score": round(score, 1),
        "label": label,
        "trend_score": trend_score,
        "momentum_score": momentum_score,
        "volume_score": volume_score,
        "risk_penalty": risk_penalty,
        "reasons_json": json.dumps(reasons),
        "risks_json": json.dumps(risks),
        "swing_suitable": swing_suitable,
    }


def _compute_bearish_signal(indicators, price_changes, df, events, news_sentiment, close):
    """Compute score from bearish perspective (lower score = stronger sell)."""
    reasons = []
    risks = []

    # Invert: compute how bearish (0=fully bearish, 100=not bearish at all)
    # We want: Strong Sell = 0-29, Sell = 30-44

    # === TREND (40 points - bearish gives 0) ===
    trend_score = 40  # Start at max, subtract for bearish signals

    if indicators["ema20"] < indicators["ema50"]:
        trend_score -= 10
        reasons.append("EMA20 below EMA50 (short-term downtrend)")

    if indicators["ema50"] < indicators["ema200"]:
        trend_score -= 10
        reasons.append("EMA50 below EMA200 (long-term downtrend)")

    if close < indicators["ema20"]:
        trend_score -= 10
        reasons.append("Price below EMA20")

    if detect_lower_highs_lows(df):
        trend_score -= 10
        reasons.append("Lower highs and lower lows pattern")

    # === MOMENTUM (25 points) ===
    momentum_score = 25

    if indicators["rsi14"] < 45:
        momentum_score -= 10
        reasons.append(f"RSI({indicators['rsi14']:.1f}) shows bearish momentum")
    elif indicators["rsi14"] < 50:
        momentum_score -= 5

    macd_hist = indicators.get("macd_hist", 0)
    prev_macd_hist = indicators.get("prev_macd_hist", 0)
    if macd_hist < 0 and macd_hist < prev_macd_hist:
        momentum_score -= 10
        reasons.append("MACD histogram negative and falling")
    elif macd_hist < 0:
        momentum_score -= 5
        reasons.append("MACD histogram negative")

    if close < indicators["low_20d"] * 1.01 and indicators.get("vol_ratio", 0) > 1.2:
        momentum_score -= 5
        reasons.append("Breakdown near 20-day low with volume")

    # === VOLUME (20 points) ===
    volume_score = 20

    vol_ratio = indicators.get("vol_ratio", 0)
    if vol_ratio > 1.5 and price_changes.get("pct_1d", 0) < 0:
        volume_score -= 10
        reasons.append(f"Selling volume {vol_ratio:.1f}x above average")
    elif vol_ratio > 1.2 and price_changes.get("pct_1d", 0) < 0:
        volume_score -= 5

    atr14 = indicators.get("atr14", 0)
    if atr14 > 0 and df is not None and len(df) > 0:
        true_range = max(
            df["high"].iloc[-1] - df["low"].iloc[-1],
            abs(df["high"].iloc[-1] - indicators.get("prev_close", close)),
            abs(df["low"].iloc[-1] - indicators.get("prev_close", close)),
        )
        if true_range > 1.3 * atr14 and price_changes.get("pct_1d", 0) < 0:
            volume_score -= 10
            reasons.append("Range expansion day aligned with downtrend")

    # === RISK (additional sell pressure) ===
    risk_penalty = 0
    if events:
        now = datetime.utcnow()
        for evt in events:
            if evt.get("event_type") == "earnings":
                evt_date = evt.get("event_date")
                if evt_date and (evt_date - now).days <= 5:
                    risk_penalty += 5
                    risks.append("Earnings within 5 trading days")
                    break

    if news_sentiment is not None and news_sentiment < -0.3:
        risk_penalty += 5
        risks.append("Negative news sentiment accelerating sell-off")

    gap_pct = price_changes.get("gap_pct", 0)
    if gap_pct < -1:
        risk_penalty += 5
        risks.append(f"Gap down ({gap_pct:.1f}%)")

    # === COMPOSITE ===
    raw_score = trend_score + momentum_score + volume_score - risk_penalty
    score = max(0, min(100, raw_score))

    label = _classify(score)

    atr_pct_val = indicators.get("atr_pct", 0)
    swing_suitable = ATR_PCT_MIN <= atr_pct_val <= ATR_PCT_MAX

    return {
        "score": round(score, 1),
        "label": label,
        "trend_score": 40 - trend_score,  # Report as bearish trend strength
        "momentum_score": 25 - momentum_score,
        "volume_score": 20 - volume_score,
        "risk_penalty": risk_penalty,
        "reasons_json": json.dumps(reasons),
        "risks_json": json.dumps(risks),
        "swing_suitable": swing_suitable,
    }


def _classify(score: float) -> str:
    """Classify score into signal label."""
    if score >= STRONG_BUY_THRESHOLD:
        return "Strong Buy"
    elif score >= BUY_THRESHOLD:
        return "Buy"
    elif score >= NEUTRAL_LOW:
        return "Neutral"
    elif score >= SELL_THRESHOLD:
        return "Sell"
    else:
        return "Strong Sell"


def _neutral_signal():
    """Return a neutral signal when data is insufficient."""
    return {
        "score": 50,
        "label": "Neutral",
        "trend_score": 0,
        "momentum_score": 0,
        "volume_score": 0,
        "risk_penalty": 0,
        "reasons_json": json.dumps(["Insufficient data for signal computation"]),
        "risks_json": json.dumps([]),
        "swing_suitable": False,
    }
