"""
Market data models for storing OHLCV data and metadata.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger, Boolean, Index
from sqlalchemy.sql import func

from app.core.database import Base


class Symbol(Base):
    """Model for trading symbols and their metadata."""
    
    __tablename__ = "symbols"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    base_asset = Column(String(10), nullable=False)  # BTC, ETH, etc.
    quote_asset = Column(String(10), nullable=False)  # USDT, USD, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    min_qty = Column(Float, nullable=True)
    max_qty = Column(Float, nullable=True)
    step_size = Column(Float, nullable=True)
    tick_size = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Timeframe(Base):
    """Model for supported timeframes."""
    
    __tablename__ = "timeframes"
    
    id = Column(Integer, primary_key=True, index=True)
    timeframe = Column(String(10), unique=True, nullable=False, index=True)
    description = Column(String(50), nullable=True)
    seconds = Column(Integer, nullable=False)  # Duration in seconds
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class MarketData(Base):
    """Model for storing OHLCV market data."""
    
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    quote_volume = Column(Float, nullable=True)
    trades_count = Column(Integer, nullable=True)
    taker_buy_volume = Column(Float, nullable=True)
    taker_buy_quote_volume = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Composite indexes for efficient querying
    __table_args__ = (
        Index('ix_market_data_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
        Index('ix_market_data_timestamp_symbol', 'timestamp', 'symbol'),
    )

