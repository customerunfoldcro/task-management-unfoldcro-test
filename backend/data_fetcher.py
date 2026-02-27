"""Data fetching service using Yahoo Finance v8 API via httpx (no yfinance dependency)."""

import logging
import time
from datetime import datetime, timedelta
from io import StringIO

import httpx
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

YF_BASE = "https://query1.finance.yahoo.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def _period_to_timestamps(period: str) -> tuple[int, int]:
    """Convert period string to (start, end) unix timestamps."""
    now = int(time.time())
    deltas = {
        "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825,
    }
    days = deltas.get(period, 365)
    start = now - days * 86400
    return start, now


def fetch_historical_bars(yf_symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame | None:
    """
    Fetch historical OHLCV data from Yahoo Finance chart API.

    Note: Yahoo Finance data for NSE (.NS) stocks may be delayed.
    For production, use a licensed NSE/BSE data feed.
    """
    try:
        period1, period2 = _period_to_timestamps(period)
        url = f"{YF_BASE}/v8/finance/chart/{yf_symbol}"
        params = {
            "period1": period1,
            "period2": period2,
            "interval": interval,
            "includePrePost": "false",
        }
        headers = {"User-Agent": USER_AGENT}

        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            resp = client.get(url, params=params, headers=headers)

        if resp.status_code != 200:
            logger.warning(f"HTTP {resp.status_code} for {yf_symbol}")
            return None

        data = resp.json()
        result = data.get("chart", {}).get("result")
        if not result:
            logger.warning(f"No chart result for {yf_symbol}")
            return None

        result = result[0]
        timestamps = result.get("timestamp", [])
        quote = result.get("indicators", {}).get("quote", [{}])[0]

        if not timestamps or not quote:
            return None

        df = pd.DataFrame({
            "open": quote.get("open", []),
            "high": quote.get("high", []),
            "low": quote.get("low", []),
            "close": quote.get("close", []),
            "volume": quote.get("volume", []),
        }, index=pd.to_datetime(timestamps, unit="s"))

        # Drop NaN close rows
        df = df.dropna(subset=["close"])

        # Replace remaining NaN with forward fill
        df = df.ffill()

        if len(df) < 50:
            logger.warning(f"Insufficient data for {yf_symbol}: {len(df)} bars")
            return None

        return df

    except Exception as e:
        logger.error(f"Error fetching data for {yf_symbol}: {e}")
        return None


def fetch_events(yf_symbol: str) -> list[dict]:
    """Fetch upcoming events for a symbol from Yahoo Finance."""
    events = []
    try:
        url = f"{YF_BASE}/v8/finance/chart/{yf_symbol}"
        params = {"period1": int(time.time()) - 86400, "period2": int(time.time()), "interval": "1d", "events": "div,split,earn"}
        headers = {"User-Agent": USER_AGENT}

        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            resp = client.get(url, params=params, headers=headers)

        if resp.status_code == 200:
            data = resp.json()
            result = data.get("chart", {}).get("result", [{}])
            if result:
                ev = result[0].get("events", {})
                # Dividends
                for _ts, div_data in ev.get("dividends", {}).items():
                    events.append({
                        "event_type": "dividend",
                        "event_date": datetime.fromtimestamp(div_data.get("date", 0)),
                        "description": f"Dividend: ₹{div_data.get('amount', 0):.2f}",
                    })
                # Splits
                for _ts, split_data in ev.get("splits", {}).items():
                    events.append({
                        "event_type": "split",
                        "event_date": datetime.fromtimestamp(split_data.get("date", 0)),
                        "description": f"Split: {split_data.get('numerator', 0)}:{split_data.get('denominator', 0)}",
                    })

    except Exception as e:
        logger.debug(f"Error fetching events for {yf_symbol}: {e}")

    return events


def get_market_status() -> dict:
    """
    Determine current Indian market status.
    IST = UTC + 5:30
    Pre-open: 9:00 - 9:15 IST
    Open: 9:15 - 15:30 IST
    Closed: otherwise
    """
    now_utc = datetime.utcnow()
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = now_utc + ist_offset

    hour, minute = now_ist.hour, now_ist.minute
    day = now_ist.weekday()  # 0=Monday

    # Weekend
    if day >= 5:
        return {"status": "Closed", "reason": "Weekend", "ist_time": now_ist.strftime("%H:%M IST")}

    time_val = hour * 60 + minute

    if time_val < 540:  # Before 9:00
        return {"status": "Closed", "reason": "Before market hours", "ist_time": now_ist.strftime("%H:%M IST")}
    elif time_val < 555:  # 9:00 - 9:15
        return {"status": "Pre-Open", "reason": "Pre-open session", "ist_time": now_ist.strftime("%H:%M IST")}
    elif time_val < 930:  # 9:15 - 15:30
        return {"status": "Open", "reason": "Regular trading", "ist_time": now_ist.strftime("%H:%M IST")}
    else:
        return {"status": "Closed", "reason": "After market hours", "ist_time": now_ist.strftime("%H:%M IST")}
