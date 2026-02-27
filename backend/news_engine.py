"""News ingestion engine with entity tagging and sentiment analysis."""

import hashlib
import re
from datetime import datetime, timedelta

import xml.etree.ElementTree as ET

import httpx

# Company name to symbol mapping for entity tagging
COMPANY_ALIASES = {
    "reliance": "RELIANCE",
    "reliance industries": "RELIANCE",
    "ril": "RELIANCE",
    "tcs": "TCS",
    "tata consultancy": "TCS",
    "hdfc bank": "HDFCBANK",
    "hdfcbank": "HDFCBANK",
    "infosys": "INFY",
    "icici bank": "ICICIBANK",
    "hindustan unilever": "HINDUNILVR",
    "hul": "HINDUNILVR",
    "itc": "ITC",
    "sbi": "SBIN",
    "state bank": "SBIN",
    "bharti airtel": "BHARTIARTL",
    "airtel": "BHARTIARTL",
    "kotak": "KOTAKBANK",
    "kotak mahindra": "KOTAKBANK",
    "larsen": "LT",
    "l&t": "LT",
    "axis bank": "AXISBANK",
    "bajaj finance": "BAJFINANCE",
    "asian paints": "ASIANPAINT",
    "maruti": "MARUTI",
    "maruti suzuki": "MARUTI",
    "titan": "TITAN",
    "sun pharma": "SUNPHARMA",
    "tata motors": "TATAMOTORS",
    "ultratech": "ULTRACEMCO",
    "wipro": "WIPRO",
    "ongc": "ONGC",
    "ntpc": "NTPC",
    "power grid": "POWERGRID",
    "mahindra": "M&M",
    "m&m": "M&M",
    "tata steel": "TATASTEEL",
    "hcl tech": "HCLTECH",
    "hcl technologies": "HCLTECH",
    "adani enterprises": "ADANIENT",
    "adani ports": "ADANIPORTS",
    "coal india": "COALINDIA",
    "jsw steel": "JSWSTEEL",
    "tech mahindra": "TECHM",
    "britannia": "BRITANNIA",
    "nestle india": "NESTLEIND",
    "cipla": "CIPLA",
    "dr reddy": "DRREDDY",
    "eicher motors": "EICHERMOT",
    "apollo hospitals": "APOLLOHOSP",
    "hero motocorp": "HEROMOTOCO",
    "bpcl": "BPCL",
    "bajaj auto": "BAJAJ-AUTO",
    "hindalco": "HINDALCO",
    "zomato": "ZOMATO",
    "tata power": "TATAPOWER",
    "adani green": "ADANIGREEN",
    "hal": "HAL",
    "hindustan aeronautics": "HAL",
    "vedanta": "VEDL",
    "dlf": "DLF",
    "irctc": "IRCTC",
    "lic": "LICI",
    "paytm": "PAYTM",
    "nifty": None,  # Market-wide
    "sensex": None,
    "rbi": None,
}

# Sentiment keywords
POSITIVE_KEYWORDS = [
    "surge", "rally", "jump", "gain", "profit", "beat", "upgrade",
    "outperform", "bullish", "strong", "growth", "record", "high",
    "buy", "overweight", "positive", "boost", "expand", "order win",
    "dividend", "bonus", "acquisition", "partnership",
]

NEGATIVE_KEYWORDS = [
    "fall", "drop", "crash", "loss", "miss", "downgrade", "underperform",
    "bearish", "weak", "decline", "low", "sell", "underweight", "negative",
    "fraud", "scam", "ban", "penalty", "fine", "probe", "investigation",
    "debt", "default", "layoff", "cut", "slash", "warning",
]

# Urgency patterns
HIGH_URGENCY_PATTERNS = [
    r"earning[s]?\s+(beat|miss|surprise|result)",
    r"guidance\s+(raise|cut|lower|update)",
    r"fraud|scam|investigation|probe",
    r"ban|restrict|suspend|delist",
    r"downgrade|upgrade|target\s+(raise|cut)",
    r"large\s+order|mega\s+deal|billion\s+deal",
    r"merger|acquisition|takeover|buyout",
    r"rbi.*(rate|policy|repo)",
    r"dividend.*(special|interim|final)",
    r"split|bonus\s+issue",
]

MEDIUM_URGENCY_PATTERNS = [
    r"interview|management\s+speak|analyst\s+call",
    r"quarter|quarterly|q[1-4]",
    r"market\s+(open|close|wrap|update)",
    r"sector\s+(update|outlook|report)",
]

# RSS Feed sources for Indian market news
NEWS_FEEDS = [
    {
        "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "source": "Economic Times",
    },
    {
        "url": "https://www.moneycontrol.com/rss/marketreports.xml",
        "source": "Moneycontrol",
    },
    {
        "url": "https://www.livemint.com/rss/markets",
        "source": "Livemint",
    },
]


def compute_sentiment(text: str) -> tuple[float, str]:
    """
    Simple keyword-based sentiment analysis.

    Returns:
        (score, label) where score is -1 to 1 and label is positive/negative/neutral.
    """
    text_lower = text.lower()
    pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)

    total = pos_count + neg_count
    if total == 0:
        return 0.0, "neutral"

    score = (pos_count - neg_count) / total
    if score > 0.2:
        return round(score, 2), "positive"
    elif score < -0.2:
        return round(score, 2), "negative"
    else:
        return round(score, 2), "neutral"


def classify_urgency(text: str) -> str:
    """Classify news urgency as high, medium, or low."""
    text_lower = text.lower()

    for pattern in HIGH_URGENCY_PATTERNS:
        if re.search(pattern, text_lower):
            return "high"

    for pattern in MEDIUM_URGENCY_PATTERNS:
        if re.search(pattern, text_lower):
            return "medium"

    return "low"


def tag_entity(text: str) -> str | None:
    """Extract stock symbol from news text using entity mapping."""
    text_lower = text.lower()

    for alias, symbol in COMPANY_ALIASES.items():
        if alias in text_lower:
            return symbol

    return None


def deduplicate_key(title: str, url: str) -> str:
    """Create a deduplication key from title and URL."""
    # Normalize title
    normalized = re.sub(r"[^a-z0-9\s]", "", title.lower().strip())
    normalized = re.sub(r"\s+", " ", normalized)
    return hashlib.md5(f"{normalized}:{url}".encode()).hexdigest()


def _parse_rss_xml(xml_text: str) -> list[dict]:
    """Parse RSS XML without feedparser using stdlib xml.etree."""
    items = []
    try:
        root = ET.fromstring(xml_text)
        # Handle RSS 2.0
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_el = item.find("pubDate")
            items.append({
                "title": title_el.text.strip() if title_el is not None and title_el.text else "",
                "link": link_el.text.strip() if link_el is not None and link_el.text else "",
                "description": desc_el.text.strip()[:500] if desc_el is not None and desc_el.text else "",
                "pubDate": pub_el.text.strip() if pub_el is not None and pub_el.text else "",
            })
    except ET.ParseError:
        pass
    return items


def _parse_pub_date(date_str: str) -> datetime:
    """Parse RSS pubDate string to datetime."""
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.replace(tzinfo=None)
    except Exception:
        return datetime.utcnow()


async def fetch_rss_feeds() -> list[dict]:
    """Fetch and parse news from RSS feeds."""
    all_items = []
    seen_keys = set()

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        for feed_info in NEWS_FEEDS:
            try:
                resp = await client.get(feed_info["url"])
                if resp.status_code != 200:
                    continue

                entries = _parse_rss_xml(resp.text)

                for entry in entries[:20]:
                    title = entry.get("title", "").strip()
                    if not title:
                        continue

                    url = entry.get("link", "")
                    dedup = deduplicate_key(title, url)
                    if dedup in seen_keys:
                        continue
                    seen_keys.add(dedup)

                    # Parse published date
                    pub_str = entry.get("pubDate", "")
                    ts = _parse_pub_date(pub_str) if pub_str else datetime.utcnow()

                    # Skip old news
                    if (datetime.utcnow() - ts).total_seconds() > 72 * 3600:
                        continue

                    summary = entry.get("description", "")[:500]
                    full_text = f"{title} {summary}"

                    sentiment_score, sentiment_label = compute_sentiment(full_text)
                    urgency = classify_urgency(full_text)
                    symbol = tag_entity(full_text)

                    is_macro = symbol is None and any(
                        kw in full_text.lower()
                        for kw in ["rbi", "inflation", "crude", "usdinr", "nifty", "sensex", "gdp", "fiscal"]
                    )

                    all_items.append({
                        "symbol": symbol,
                        "ts": ts,
                        "source": feed_info["source"],
                        "title": title,
                        "url": url,
                        "summary": summary,
                        "sentiment": sentiment_score,
                        "sentiment_label": sentiment_label,
                        "urgency": urgency,
                        "is_macro": is_macro,
                    })

            except Exception:
                continue

    # Sort by timestamp descending
    all_items.sort(key=lambda x: x["ts"], reverse=True)
    return all_items


def get_symbol_news_sentiment(news_items: list[dict], symbol: str) -> float | None:
    """Get average sentiment for a symbol from recent news."""
    symbol_news = [n for n in news_items if n.get("symbol") == symbol]
    if not symbol_news:
        return None
    sentiments = [n["sentiment"] for n in symbol_news]
    return sum(sentiments) / len(sentiments)
