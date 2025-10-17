"""
Pydantic schemas for recommendation-related API models.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class RecommendationBase(BaseModel):
    """Base schema for recommendation data."""
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    timeframe: str = Field(..., description="Timeframe (e.g., 1h, 4h, 1d)")
    action: str = Field(..., description="Recommended action: BUY, SELL, or HOLD")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0.0 to 1.0)")
    entry_price: Optional[float] = Field(None, description="Entry price for the trade")
    price_target: Optional[float] = Field(None, description="Primary target price (deprecated: use take_profit_targets)")
    take_profit_targets: Optional[List[float]] = Field(None, description="Take profit target prices (multiple levels)")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    reasoning: Optional[str] = Field(None, description="Human-readable explanation")
    strategy_weights: Optional[Dict[str, float]] = Field(None, description="Strategy contribution weights")
    market_conditions: Optional[Dict[str, Any]] = Field(None, description="Market regime analysis")


class RecommendationCreate(RecommendationBase):
    """Schema for creating a new recommendation."""
    valid_until: Optional[datetime] = Field(None, description="Recommendation validity period")


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation."""
    action: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    entry_price: Optional[float] = None
    price_target: Optional[float] = None
    take_profit_targets: Optional[List[float]] = None
    stop_loss: Optional[float] = None
    reasoning: Optional[str] = None
    strategy_weights: Optional[Dict[str, float]] = None
    market_conditions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation API responses."""
    id: int
    created_at: datetime
    valid_until: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class RecommendationHistoryResponse(BaseModel):
    """Schema for recommendation history API responses."""
    id: int
    recommendation_id: int
    action: str
    confidence: float
    price_at_recommendation: float
    price_target: Optional[float]
    stop_loss: Optional[float]
    reasoning: Optional[str]
    strategy_weights: Optional[Dict[str, float]]
    market_conditions: Optional[Dict[str, Any]]
    created_at: datetime
    price_at_execution: Optional[float]
    execution_timestamp: Optional[datetime]
    pnl_percentage: Optional[float]
    pnl_absolute: Optional[float]
    was_profitable: Optional[bool]
    
    class Config:
        from_attributes = True


class RecommendationSummary(BaseModel):
    """Schema for recommendation summary statistics."""
    total_recommendations: int
    buy_recommendations: int
    sell_recommendations: int
    hold_recommendations: int
    average_confidence: float
    profitable_recommendations: int
    total_pnl_percentage: float
    win_rate: float

