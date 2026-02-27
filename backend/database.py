"""Database setup and models."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL, SYNC_DATABASE_URL


class Base(DeclarativeBase):
    pass


# --- ORM Models ---


class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    yf_symbol = Column(String(30), nullable=False)
    isin = Column(String(12))
    name = Column(String(200), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    universe = Column(String(20), nullable=False)  # NIFTY50 or NEXT50
    universe_rank = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Bar(Base):
    __tablename__ = "bars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, default="1d")
    ts = Column(DateTime, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    adj_close = Column(Float)


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    ts = Column(DateTime, nullable=False, index=True)
    ema20 = Column(Float)
    ema50 = Column(Float)
    ema200 = Column(Float)
    rsi14 = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    atr14 = Column(Float)
    atr_pct = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    bb_width = Column(Float)
    vol_avg_20d = Column(Float)
    vol_ratio = Column(Float)
    high_20d = Column(Float)
    low_20d = Column(Float)


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    ts = Column(DateTime, nullable=False, index=True)
    score = Column(Float, nullable=False)
    label = Column(String(20), nullable=False)
    trend_score = Column(Float)
    momentum_score = Column(Float)
    volume_score = Column(Float)
    risk_penalty = Column(Float)
    reasons_json = Column(Text)
    risks_json = Column(Text)
    swing_suitable = Column(Boolean, default=True)


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True)
    ts = Column(DateTime, nullable=False, index=True)
    source = Column(String(100))
    title = Column(String(500), nullable=False)
    url = Column(String(1000))
    summary = Column(Text)
    sentiment = Column(Float)  # -1 to 1
    sentiment_label = Column(String(20))  # positive, negative, neutral
    urgency = Column(String(10))  # high, medium, low
    is_macro = Column(Boolean, default=False)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    event_date = Column(DateTime)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SignalAudit(Base):
    __tablename__ = "signal_audit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    ts = Column(DateTime, nullable=False)
    old_label = Column(String(20))
    new_label = Column(String(20))
    old_score = Column(Float)
    new_score = Column(Float)
    trigger = Column(String(200))


# --- Engine setup ---

async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
