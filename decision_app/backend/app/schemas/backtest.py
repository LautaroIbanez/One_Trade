"""
Pydantic schemas for backtesting.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TradeCreate(BaseModel):
    """Schema for creating a trade."""
    symbol: str = Field(..., description="Trading symbol")
    side: str = Field(..., description="Trade side (BUY/SELL)")
    entry_price: float = Field(..., gt=0, description="Entry price")
    quantity: float = Field(..., gt=0, description="Trade quantity")
    entry_time: datetime = Field(..., description="Entry timestamp")
    entry_signal: Optional[str] = Field(None, description="Entry signal")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Signal confidence")


class TradeUpdate(BaseModel):
    """Schema for updating a trade."""
    exit_price: Optional[float] = Field(None, gt=0, description="Exit price")
    exit_time: Optional[datetime] = Field(None, description="Exit timestamp")
    exit_signal: Optional[str] = Field(None, description="Exit signal")
    is_open: Optional[bool] = Field(None, description="Trade status")


class TradeResponse(BaseModel):
    """Schema for trade response."""
    id: int
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    entry_time: datetime
    exit_time: Optional[datetime]
    pnl: Optional[float]
    pnl_percentage: Optional[float]
    duration_hours: Optional[float]
    entry_signal: Optional[str]
    exit_signal: Optional[str]
    confidence: Optional[float]
    is_open: bool
    
    class Config:
        from_attributes = True


class BacktestCreate(BaseModel):
    """Schema for creating a backtest."""
    name: str = Field(..., description="Backtest name")
    symbol: str = Field(..., description="Trading symbol")
    strategy_name: str = Field(..., description="Strategy name")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    initial_capital: float = Field(..., gt=0, description="Initial capital")
    strategy_params: Optional[Dict[str, Any]] = Field(None, description="Strategy parameters")
    timeframe: str = Field("1d", description="Data timeframe")


class BacktestUpdate(BaseModel):
    """Schema for updating a backtest."""
    name: Optional[str] = Field(None, description="Backtest name")
    status: Optional[str] = Field(None, description="Backtest status")
    final_capital: Optional[float] = Field(None, description="Final capital")


class BacktestResponse(BaseModel):
    """Schema for backtest response."""
    id: int
    name: str
    symbol: str
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: Optional[float]
    total_return: Optional[float]
    annualized_return: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    win_rate: Optional[float]
    total_trades: Optional[int]
    avg_trade_duration: Optional[float]
    best_trade: Optional[float]
    worst_trade: Optional[float]
    strategy_params: Optional[Dict[str, Any]]
    timeframe: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PerformanceMetricResponse(BaseModel):
    """Schema for performance metric response."""
    id: int
    metric_name: str
    metric_value: float
    metric_type: str
    period: Optional[str]
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class BacktestResultResponse(BaseModel):
    """Schema for complete backtest results."""
    backtest: BacktestResponse
    trades: List[TradeResponse]
    performance_metrics: List[PerformanceMetricResponse]
    summary: Dict[str, Any]


class BacktestMetricResponse(BaseModel):
    """Schema for backtest performance metrics."""
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    avg_trade_duration: float
    best_trade: float
    worst_trade: float
    profit_factor: float
    recovery_factor: float
    calmar_ratio: float
    sortino_ratio: float