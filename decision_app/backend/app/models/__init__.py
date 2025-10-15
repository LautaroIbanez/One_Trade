"""
Database models for the One Trade application.
"""

from app.core.database import Base

# Import all models to ensure they are registered with SQLAlchemy
from .recommendation import Recommendation, RecommendationHistory
from .market_data import MarketData, Symbol, Timeframe
from .backtest import Backtest, Trade, PerformanceMetric

__all__ = [
    "Base",
    "Recommendation",
    "RecommendationHistory", 
    "MarketData",
    "Symbol",
    "Timeframe",
    "Backtest",
    "Trade",
    "PerformanceMetric",
]

