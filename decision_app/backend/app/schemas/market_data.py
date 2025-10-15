"""
Pydantic schemas for market data.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MarketDataPoint(BaseModel):
    """Single market data point schema."""
    timestamp: str = Field(..., description="Timestamp in ISO format")
    open: float = Field(..., gt=0, description="Opening price")
    high: float = Field(..., gt=0, description="Highest price")
    low: float = Field(..., gt=0, description="Lowest price")
    close: float = Field(..., gt=0, description="Closing price")
    volume: float = Field(..., ge=0, description="Trading volume")


class MarketDataResponse(BaseModel):
    """Market data response schema."""
    symbol: str = Field(..., description="Trading pair symbol")
    interval: str = Field(..., description="Data interval")
    data_points: int = Field(..., ge=0, description="Number of data points")
    data: List[MarketDataPoint] = Field(..., description="Market data points")


class TickerResponse(BaseModel):
    """24hr ticker response schema."""
    symbol: str = Field(..., description="Trading pair symbol")
    price_change: float = Field(..., description="Price change in last 24hr")
    price_change_percent: float = Field(..., description="Price change percentage in last 24hr")
    weighted_avg_price: float = Field(..., gt=0, description="Weighted average price")
    prev_close_price: float = Field(..., gt=0, description="Previous close price")
    last_price: float = Field(..., gt=0, description="Last price")
    last_qty: float = Field(..., ge=0, description="Last quantity")
    bid_price: float = Field(..., gt=0, description="Bid price")
    ask_price: float = Field(..., gt=0, description="Ask price")
    open_price: float = Field(..., gt=0, description="Open price")
    high_price: float = Field(..., gt=0, description="High price")
    low_price: float = Field(..., gt=0, description="Low price")
    volume: float = Field(..., ge=0, description="Volume")
    quote_volume: float = Field(..., ge=0, description="Quote volume")
    open_time: int = Field(..., description="Open time in milliseconds")
    close_time: int = Field(..., description="Close time in milliseconds")
    count: int = Field(..., ge=0, description="Number of trades")