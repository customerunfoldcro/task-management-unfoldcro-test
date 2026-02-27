"""FastAPI application: India Swing Tracker API."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from .config import CORS_ORIGINS, NEWS_LOOKBACK_HOURS
from .data_fetcher import get_market_status
from .database import AsyncSessionLocal, Symbol, Signal, News, SignalAudit, Event, init_db
from .scheduler import (
    initial_load,
    latest_data,
    refresh_news,
    refresh_prices,
    refresh_signals,
    sse_subscribers,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: start background tasks."""
    logger.info("Starting India Swing Tracker...")

    # Initialize DB
    await init_db()

    # Run initial load in background
    task = asyncio.create_task(initial_load())

    yield

    task.cancel()
    logger.info("Shutting down India Swing Tracker")


app = FastAPI(
    title="India Swing Tracker",
    description="Top 100 Indian Stock Swing Universe - Strong Buy / Strong Sell with Real Time News",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === API Endpoints ===


@app.get("/api/market-status")
async def market_status():
    """Get current market status."""
    return get_market_status()


@app.get("/api/universe/top100")
async def get_universe():
    """Get the full top 100 universe with latest data."""
    symbols_data = latest_data.get("symbols", {})

    # Compute breadth
    advancers = sum(1 for s in symbols_data.values() if s.get("pct_1d", 0) > 0)
    decliners = sum(1 for s in symbols_data.values() if s.get("pct_1d", 0) < 0)
    unchanged = len(symbols_data) - advancers - decliners

    return {
        "market_status": latest_data.get("market_status", get_market_status()),
        "breadth": {
            "advancers": advancers,
            "decliners": decliners,
            "unchanged": unchanged,
            "total": len(symbols_data),
        },
        "last_price_update": latest_data.get("last_price_update"),
        "last_news_update": latest_data.get("last_news_update"),
        "last_signal_update": latest_data.get("last_signal_update"),
        "symbols": list(symbols_data.values()),
    }


@app.get("/api/signals")
async def get_signals(
    label: str | None = Query(None, description="Filter by signal label"),
    symbol: str | None = Query(None, description="Filter by symbol"),
    sort: str = Query("score_desc", description="Sort: score_desc, score_asc, change"),
    limit: int = Query(100, ge=1, le=100),
):
    """Get signals with optional filtering and sorting."""
    symbols_data = latest_data.get("symbols", {})

    results = []
    for sym_key, sym_val in symbols_data.items():
        signal = sym_val.get("signal")
        if not signal:
            continue

        if label and signal.get("label", "").lower().replace(" ", "_") != label.lower().replace(" ", "_"):
            continue

        if symbol and sym_key.upper() != symbol.upper():
            continue

        results.append({
            "symbol": sym_key,
            "name": sym_val.get("name"),
            "sector": sym_val.get("sector"),
            "price": sym_val.get("price"),
            "pct_1d": sym_val.get("pct_1d"),
            **signal,
        })

    # Sort
    if sort == "score_desc":
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
    elif sort == "score_asc":
        results.sort(key=lambda x: x.get("score", 0))
    elif sort == "change":
        results.sort(key=lambda x: abs(x.get("pct_1d", 0)), reverse=True)

    return {"signals": results[:limit], "total": len(results)}


@app.get("/api/signals/{symbol}")
async def get_signal_detail(symbol: str):
    """Get detailed signal info for a specific symbol."""
    sym_data = latest_data["symbols"].get(symbol.upper())
    if not sym_data:
        return {"error": "Symbol not found"}

    # Get signal audit trail
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SignalAudit)
            .where(SignalAudit.symbol == symbol.upper())
            .order_by(SignalAudit.ts.desc())
            .limit(20)
        )
        audits = result.scalars().all()

    # Get events
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Event).where(Event.symbol == symbol.upper())
        )
        events = result.scalars().all()

    signal = sym_data.get("signal", {})

    # Compute swing levels
    price = sym_data.get("price", 0)
    atr = sym_data.get("atr14", 0)

    levels = None
    if price > 0 and atr > 0:
        if signal.get("label") in ("Strong Buy", "Buy"):
            levels = {
                "entry": round(price, 2),
                "stop_loss": round(price - 2 * atr, 2),
                "target_1": round(price + 2 * atr, 2),
                "target_2": round(price + 3 * atr, 2),
                "risk_reward": "1:1 to 1:1.5",
            }
        elif signal.get("label") in ("Strong Sell", "Sell"):
            levels = {
                "entry": round(price, 2),
                "stop_loss": round(price + 2 * atr, 2),
                "target_1": round(price - 2 * atr, 2),
                "target_2": round(price - 3 * atr, 2),
                "risk_reward": "1:1 to 1:1.5",
            }

    return {
        "symbol_data": sym_data,
        "signal": signal,
        "reasons": json.loads(signal.get("reasons_json", "[]")),
        "risks": json.loads(signal.get("risks_json", "[]")),
        "levels": levels,
        "audit_trail": [
            {
                "ts": a.ts.isoformat() if a.ts else None,
                "old_label": a.old_label,
                "new_label": a.new_label,
                "old_score": a.old_score,
                "new_score": a.new_score,
                "trigger": a.trigger,
            }
            for a in audits
        ],
        "events": [
            {
                "type": e.event_type,
                "date": e.event_date.isoformat() if e.event_date else None,
                "description": e.description,
            }
            for e in events
        ],
    }


@app.get("/api/news")
async def get_news(
    symbol: str | None = Query(None),
    range_hours: int = Query(NEWS_LOOKBACK_HOURS, alias="range"),
    urgency: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """Get news feed with optional filtering."""
    news_items = latest_data.get("news", [])
    cutoff = datetime.utcnow() - timedelta(hours=range_hours)

    filtered = []
    for item in news_items:
        if item["ts"] < cutoff:
            continue
        if symbol and item.get("symbol") != symbol.upper():
            continue
        if urgency and item.get("urgency") != urgency:
            continue
        filtered.append({
            **item,
            "ts": item["ts"].isoformat() if isinstance(item["ts"], datetime) else item["ts"],
        })

    return {"news": filtered[:limit], "total": len(filtered)}


@app.get("/api/alerts/stream")
async def alerts_stream():
    """SSE endpoint for real-time alerts."""
    queue = asyncio.Queue(maxsize=100)
    sse_subscribers.append(queue)

    async def event_generator():
        try:
            # Send initial heartbeat
            yield f"data: {json.dumps({'type': 'connected', 'ts': datetime.utcnow().isoformat()})}\n\n"

            while True:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {message}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat', 'ts': datetime.utcnow().isoformat()})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in sse_subscribers:
                sse_subscribers.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/refresh/prices")
async def trigger_price_refresh():
    """Manually trigger a price refresh."""
    asyncio.create_task(refresh_prices())
    return {"status": "Price refresh started"}


@app.post("/api/refresh/news")
async def trigger_news_refresh():
    """Manually trigger a news refresh."""
    asyncio.create_task(refresh_news())
    return {"status": "News refresh started"}


@app.post("/api/refresh/signals")
async def trigger_signal_refresh():
    """Manually trigger a signal refresh."""
    asyncio.create_task(refresh_signals())
    return {"status": "Signal refresh started"}


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "symbols_loaded": len(latest_data.get("symbols", {})),
        "last_price_update": latest_data.get("last_price_update"),
        "last_news_update": latest_data.get("last_news_update"),
        "market_status": latest_data.get("market_status", {}).get("status"),
    }
