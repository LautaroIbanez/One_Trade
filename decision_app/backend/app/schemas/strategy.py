"""
Pydantic schemas for trading strategies.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class StrategyInfo(BaseModel):
    """Strategy information schema."""
    name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    parameters: Dict[str, Any] = Field(..., description="Strategy parameters")
    signal_types: List[str] = Field(..., description="Available signal types")


class SignalData(BaseModel):
    """Trading signal data schema."""
    signal: str = Field(..., description="Signal type (BUY/SELL/HOLD)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Signal confidence (0.0-1.0)")
    price: float = Field(..., gt=0, description="Price at signal time")
    timestamp: str = Field(..., description="Signal timestamp (ISO format)")
    reasoning: str = Field(..., description="Signal reasoning")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class StrategyAnalysis(BaseModel):
    """Strategy analysis result schema."""
    strategy: str = Field(..., description="Strategy name")
    total_signals: int = Field(..., ge=0, description="Total number of signals generated")
    signals: List[SignalData] = Field(..., description="List of generated signals")


class StrategyPerformance(BaseModel):
    """Strategy performance metrics schema."""
    strategy: str = Field(..., description="Strategy name")
    total_signals: int = Field(..., ge=0, description="Total number of signals")
    buy_signals: int = Field(..., ge=0, description="Number of BUY signals")
    sell_signals: int = Field(..., ge=0, description="Number of SELL signals")
    hold_signals: int = Field(..., ge=0, description="Number of HOLD signals")
    avg_confidence: float = Field(..., ge=0.0, le=1.0, description="Average signal confidence")


class MarketDataRequest(BaseModel):
    """Market data request schema."""
    data: List[Dict[str, Any]] = Field(..., description="OHLCV market data")
    symbol: Optional[str] = Field(None, description="Trading symbol")
    timeframe: Optional[str] = Field(None, description="Data timeframe")


class StrategyConfig(BaseModel):
    """Strategy configuration schema."""
    name: str = Field(..., description="Strategy name")
    parameters: Dict[str, Any] = Field(..., description="Strategy parameters")
    enabled: bool = Field(True, description="Whether strategy is enabled")
