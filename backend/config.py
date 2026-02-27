"""Application configuration."""

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./swing_tracker.db")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", "sqlite:///./swing_tracker.db")

# Data refresh intervals (seconds)
PRICE_REFRESH_INTERVAL = int(os.getenv("PRICE_REFRESH_INTERVAL", "60"))
NEWS_REFRESH_INTERVAL = int(os.getenv("NEWS_REFRESH_INTERVAL", "90"))
SIGNAL_REFRESH_INTERVAL = int(os.getenv("SIGNAL_REFRESH_INTERVAL", "120"))

# Market hours (IST)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30
PRE_OPEN_HOUR = 9
PRE_OPEN_MINUTE = 0

# Signal thresholds
STRONG_BUY_THRESHOLD = 80
BUY_THRESHOLD = 65
NEUTRAL_LOW = 45
SELL_THRESHOLD = 30

# Universe filters
MIN_ADV_CRORES = 25  # ₹25 Cr minimum average daily value

# ATR band for swing suitability
ATR_PCT_MIN = 1.0
ATR_PCT_MAX = 4.0

# News settings
NEWS_LOOKBACK_HOURS = 72
MAX_NEWS_PER_SYMBOL = 50

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
