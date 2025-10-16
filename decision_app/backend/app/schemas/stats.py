"""
Pydantic schemas for real-time statistics.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RealTimeStatsResponse(BaseModel):
    """Real-time statistics response."""
    activeRecommendations: int = Field(..., description="Number of active trading recommendations")
    totalPnL: float = Field(..., description="Total P&L percentage from backtests")
    winRate: float = Field(..., description="Win rate percentage from backtests")
    maxDrawdown: float = Field(..., description="Maximum drawdown percentage")
    lastUpdate: str = Field(..., description="Last update timestamp")
    dataSource: str = Field(..., description="Source of data (backtests/estimated)")
    totalTrades: Optional[int] = Field(None, description="Total number of trades")
    profitFactor: Optional[float] = Field(None, description="Profit factor")
    avgRMultiple: Optional[float] = Field(None, description="Average R-multiple")


class HistoricalPerformance(BaseModel):
    """Historical performance metrics."""
    symbol: str = Field(..., description="Trading symbol")
    totalTrades: int = Field(..., description="Total trades")
    winningTrades: int = Field(..., description="Winning trades")
    losingTrades: int = Field(..., description="Losing trades")
    winRate: float = Field(..., description="Win rate percentage")
    totalPnL: float = Field(..., description="Total P&L percentage")
    maxDrawdown: float = Field(..., description="Maximum drawdown")
    profitFactor: float = Field(..., description="Profit factor")
    avgRMultiple: float = Field(..., description="Average R-multiple")
    lastBacktestDate: str = Field(..., description="Last backtest date")

