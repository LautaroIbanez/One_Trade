"""
Backtesting models for One Trade Decision App.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Backtest(Base):
    """Backtest execution model."""
    
    __tablename__ = "backtests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    symbol = Column(String(20), nullable=False)
    strategy_name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=True)
    
    # Performance metrics
    total_return = Column(Float, nullable=True)
    annualized_return = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    total_trades = Column(Integer, nullable=True)
    avg_trade_duration = Column(Float, nullable=True)
    best_trade = Column(Float, nullable=True)
    worst_trade = Column(Float, nullable=True)
    
    # Configuration
    strategy_params = Column(Text, nullable=True)  # JSON string
    timeframe = Column(String(10), nullable=False, default="1d")
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    
    # Relationships
    trades = relationship("Trade", back_populates="backtest", cascade="all, delete-orphan")
    performance_metrics = relationship("PerformanceMetric", back_populates="backtest", cascade="all, delete-orphan")


class Trade(Base):
    """Individual trade model."""
    
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), nullable=False)
    
    # Trade details
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # BUY, SELL
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    
    # Timestamps
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    
    # Performance
    pnl = Column(Float, nullable=True)
    pnl_percentage = Column(Float, nullable=True)
    duration_hours = Column(Float, nullable=True)
    
    # Strategy context
    entry_signal = Column(String(50), nullable=True)
    exit_signal = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Status
    is_open = Column(Boolean, default=True)
    
    # Relationships
    backtest = relationship("Backtest", back_populates="trades")


class PerformanceMetric(Base):
    """Performance metrics for backtests."""
    
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), nullable=False)
    
    # Metric details
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)  # return, risk, trade, etc.
    period = Column(String(20), nullable=True)  # daily, weekly, monthly, total
    
    # Timestamp
    calculated_at = Column(DateTime, default=func.now())
    
    # Relationships
    backtest = relationship("Backtest", back_populates="performance_metrics")