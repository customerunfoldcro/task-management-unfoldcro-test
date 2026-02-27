"""Background scheduler for data refresh tasks."""

import asyncio
import json
import logging
from datetime import datetime

from sqlalchemy import select, delete

from .config import NEWS_REFRESH_INTERVAL, PRICE_REFRESH_INTERVAL, SIGNAL_REFRESH_INTERVAL
from .data_fetcher import fetch_historical_bars, fetch_events, get_market_status
from .database import AsyncSessionLocal, Symbol, Bar, Indicator, Signal, SignalAudit, News, Event
from .indicators import compute_all_indicators, compute_price_changes
from .news_engine import fetch_rss_feeds, get_symbol_news_sentiment
from .signals import compute_signal

logger = logging.getLogger(__name__)

# Global state for SSE broadcasting
latest_data = {
    "market_status": {},
    "symbols": {},
    "news": [],
    "last_price_update": None,
    "last_news_update": None,
    "last_signal_update": None,
}

sse_subscribers = []


async def broadcast_sse(event_type: str, data: dict):
    """Broadcast an event to all SSE subscribers."""
    message = json.dumps({"type": event_type, "data": data, "ts": datetime.utcnow().isoformat()})
    dead = []
    for queue in sse_subscribers:
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            dead.append(queue)
    for q in dead:
        sse_subscribers.remove(q)


async def refresh_prices():
    """Fetch latest price data and compute indicators for all symbols."""
    logger.info("Starting price refresh...")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Symbol).where(Symbol.is_active == True))
        symbols = result.scalars().all()

    updated_count = 0
    for sym in symbols:
        try:
            df = fetch_historical_bars(sym.yf_symbol, period="1y", interval="1d")
            if df is None:
                continue

            # Compute indicators
            indicators = compute_all_indicators(df)
            if indicators is None:
                continue

            price_changes = compute_price_changes(df)

            # Store latest data in memory
            latest_close = float(df["close"].iloc[-1])
            latest_data["symbols"][sym.symbol] = {
                "symbol": sym.symbol,
                "name": sym.name,
                "sector": sym.sector,
                "industry": sym.industry,
                "universe": sym.universe,
                "price": latest_close,
                "open": float(df["open"].iloc[-1]),
                "high": float(df["high"].iloc[-1]),
                "low": float(df["low"].iloc[-1]),
                "volume": float(df["volume"].iloc[-1]),
                **price_changes,
                **{k: v for k, v in indicators.items() if k not in ("prev_macd_hist", "prev_close")},
            }

            # Save indicator to DB
            async with AsyncSessionLocal() as session:
                ind = Indicator(
                    symbol=sym.symbol,
                    ts=datetime.utcnow(),
                    **{k: v for k, v in indicators.items() if k not in ("prev_macd_hist", "prev_close")},
                )
                session.add(ind)
                await session.commit()

            updated_count += 1

        except Exception as e:
            logger.error(f"Error refreshing {sym.symbol}: {e}")
            continue

    latest_data["last_price_update"] = datetime.utcnow().isoformat()
    logger.info(f"Price refresh complete: {updated_count}/{len(symbols)} symbols updated")

    await broadcast_sse("price_update", {
        "updated": updated_count,
        "total": len(symbols),
        "ts": latest_data["last_price_update"],
    })


async def refresh_signals():
    """Recompute signals for all symbols."""
    logger.info("Starting signal refresh...")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Symbol).where(Symbol.is_active == True))
        symbols = result.scalars().all()

    news_items = latest_data.get("news", [])
    updated_count = 0

    for sym in symbols:
        try:
            sym_data = latest_data["symbols"].get(sym.symbol)
            if not sym_data:
                continue

            # Get historical data for pattern detection
            df = fetch_historical_bars(sym.yf_symbol, period="6mo", interval="1d")
            if df is None:
                continue

            indicators = compute_all_indicators(df)
            price_changes = compute_price_changes(df)

            # Get events
            events_list = []
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Event).where(Event.symbol == sym.symbol)
                )
                db_events = result.scalars().all()
                events_list = [{"event_type": e.event_type, "event_date": e.event_date} for e in db_events]

            # Get news sentiment
            news_sentiment = get_symbol_news_sentiment(news_items, sym.symbol)

            # Compute signal
            signal = compute_signal(indicators, price_changes, df, events_list, news_sentiment)

            # Check for signal change (audit trail)
            old_signal = sym_data.get("signal")
            if old_signal and old_signal.get("label") != signal["label"]:
                async with AsyncSessionLocal() as session:
                    audit = SignalAudit(
                        symbol=sym.symbol,
                        ts=datetime.utcnow(),
                        old_label=old_signal.get("label"),
                        new_label=signal["label"],
                        old_score=old_signal.get("score"),
                        new_score=signal["score"],
                        trigger="scheduled_refresh",
                    )
                    session.add(audit)
                    await session.commit()

                await broadcast_sse("signal_change", {
                    "symbol": sym.symbol,
                    "old_label": old_signal.get("label"),
                    "new_label": signal["label"],
                    "score": signal["score"],
                })

            # Update in-memory data
            latest_data["symbols"][sym.symbol]["signal"] = signal

            # Save to DB
            async with AsyncSessionLocal() as session:
                sig = Signal(
                    symbol=sym.symbol,
                    ts=datetime.utcnow(),
                    **signal,
                )
                session.add(sig)
                await session.commit()

            updated_count += 1

        except Exception as e:
            logger.error(f"Error computing signal for {sym.symbol}: {e}")
            continue

    latest_data["last_signal_update"] = datetime.utcnow().isoformat()
    logger.info(f"Signal refresh complete: {updated_count}/{len(symbols)} signals updated")


async def refresh_news():
    """Fetch latest news and update sentiment/urgency tags."""
    logger.info("Starting news refresh...")

    try:
        news_items = await fetch_rss_feeds()
        latest_data["news"] = news_items
        latest_data["last_news_update"] = datetime.utcnow().isoformat()

        # Save to DB
        async with AsyncSessionLocal() as session:
            for item in news_items[:100]:  # Limit to 100 most recent
                news = News(
                    symbol=item.get("symbol"),
                    ts=item["ts"],
                    source=item["source"],
                    title=item["title"],
                    url=item.get("url"),
                    summary=item.get("summary"),
                    sentiment=item.get("sentiment", 0),
                    sentiment_label=item.get("sentiment_label", "neutral"),
                    urgency=item.get("urgency", "low"),
                    is_macro=item.get("is_macro", False),
                )
                session.add(news)
            await session.commit()

        # Broadcast high urgency news
        high_urgency = [n for n in news_items if n.get("urgency") == "high"]
        if high_urgency:
            await broadcast_sse("urgent_news", {
                "count": len(high_urgency),
                "items": [{"title": n["title"], "symbol": n.get("symbol"), "source": n["source"]}
                          for n in high_urgency[:5]],
            })

        logger.info(f"News refresh complete: {len(news_items)} items fetched")

    except Exception as e:
        logger.error(f"News refresh error: {e}")


async def refresh_events():
    """Fetch upcoming events for all symbols."""
    logger.info("Starting events refresh...")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Symbol).where(Symbol.is_active == True))
        symbols = result.scalars().all()

    for sym in symbols:
        try:
            events = fetch_events(sym.yf_symbol)
            if events:
                async with AsyncSessionLocal() as session:
                    # Clear old events for this symbol
                    await session.execute(
                        delete(Event).where(Event.symbol == sym.symbol)
                    )
                    for evt in events:
                        event = Event(
                            symbol=sym.symbol,
                            event_type=evt["event_type"],
                            event_date=evt.get("event_date"),
                            description=evt.get("description"),
                        )
                        session.add(event)
                    await session.commit()

                # Update in-memory
                if sym.symbol in latest_data["symbols"]:
                    latest_data["symbols"][sym.symbol]["events"] = events

        except Exception as e:
            logger.debug(f"Error fetching events for {sym.symbol}: {e}")

    logger.info("Events refresh complete")


async def initial_load():
    """Run initial data load on startup."""
    from .database import AsyncSessionLocal, Symbol, init_db
    from .universe import get_full_universe

    await init_db()

    # Load universe into DB
    universe = get_full_universe()
    async with AsyncSessionLocal() as session:
        for stock in universe:
            existing = await session.execute(
                select(Symbol).where(Symbol.symbol == stock["symbol"])
            )
            if existing.scalar_one_or_none() is None:
                sym = Symbol(
                    symbol=stock["symbol"],
                    yf_symbol=stock["yf_symbol"],
                    name=stock["name"],
                    sector=stock["sector"],
                    industry=stock.get("industry"),
                    universe=stock["universe"],
                    universe_rank=stock["universe_rank"],
                )
                session.add(sym)
        await session.commit()

    logger.info(f"Universe loaded: {len(universe)} symbols")

    # Update market status
    latest_data["market_status"] = get_market_status()

    # Run initial data fetch
    await refresh_prices()
    await refresh_news()
    await refresh_signals()
