"""
Pydantic schemas for enhanced recommendations.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class StrategySignalDetail(BaseModel):
    """Individual strategy signal detail."""
    strategy: str = Field(..., description="Strategy name")
    signal: str = Field(..., description="Signal type (BUY/SELL/HOLD)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Signal confidence")
    weight: float = Field(..., ge=0.0, le=1.0, description="Strategy weight")
    reasoning: str = Field(..., description="Signal reasoning")
    timestamp: str = Field(..., description="Signal timestamp")


class SignalScores(BaseModel):
    """Weighted signal scores."""
    buy_score: float = Field(..., ge=0.0, le=1.0, description="Weighted buy score")
    sell_score: float = Field(..., ge=0.0, le=1.0, description="Weighted sell score")
    hold_score: float = Field(..., ge=0.0, le=1.0, description="Weighted hold score")


class RiskAssessment(BaseModel):
    """Risk assessment details."""
    level: str = Field(..., description="Risk level (LOW/MEDIUM/HIGH)")
    consistency: float = Field(..., ge=0.0, le=1.0, description="Signal consistency")
    signal_distribution: Dict[str, int] = Field(..., description="Distribution of signal types")
    factors: List[str] = Field(..., description="Risk factors identified")


class PriceRange(BaseModel):
    """Price range information."""
    min: float = Field(..., gt=0, description="Minimum price")
    max: float = Field(..., gt=0, description="Maximum price")
    current: float = Field(..., gt=0, description="Current price")


class DataSummary(BaseModel):
    """Data summary information."""
    symbol: str = Field(..., description="Trading symbol")
    timeframe: str = Field(..., description="Data timeframe")
    data_points: int = Field(..., ge=0, description="Number of data points")
    price_range: PriceRange = Field(..., description="Price range information")
    volatility: float = Field(..., ge=0, description="Price volatility percentage")


class RecentPerformance(BaseModel):
    """Recent performance metrics."""
    day_1: float = Field(..., description="1-day price change percentage")
    day_7: float = Field(..., description="7-day price change percentage")
    volatility: float = Field(..., description="Volatility percentage")


class MarketActivity(BaseModel):
    """Market activity metrics."""
    volume_24h: float = Field(..., ge=0, description="24-hour volume")
    trades_24h: int = Field(..., ge=0, description="24-hour trade count")


class MarketContext(BaseModel):
    """Market context analysis."""
    trend: str = Field(..., description="Market trend (UPTREND/DOWNTREND/SIDEWAYS)")
    volatility: str = Field(..., description="Volatility level (LOW/MEDIUM/HIGH)")
    recent_performance: RecentPerformance = Field(..., description="Recent performance")
    market_activity: MarketActivity = Field(..., description="Market activity")


class EntryRange(BaseModel):
    """Entry range for opening positions."""
    min: float = Field(..., gt=0, description="Minimum entry price")
    max: float = Field(..., gt=0, description="Maximum entry price")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this range")
    methodology: str = Field(default="ATR + Support/Resistance", description="Calculation methodology")


class TradingLevels(BaseModel):
    """Trading levels for entries, take profit and stop loss."""
    entry_long: Optional[EntryRange] = Field(None, description="LONG entry range with specific confidence")
    entry_short: Optional[EntryRange] = Field(None, description="SHORT entry range with specific confidence")
    take_profit_long: Optional[float] = Field(None, gt=0, description="Take profit level for LONG")
    stop_loss_long: Optional[float] = Field(None, gt=0, description="Stop loss level for LONG")
    take_profit_short: Optional[float] = Field(None, gt=0, description="Take profit level for SHORT")
    stop_loss_short: Optional[float] = Field(None, gt=0, description="Stop loss level for SHORT")
    atr: Optional[float] = Field(None, ge=0, description="Average True Range used for calculations")
    support_level: Optional[float] = Field(None, description="Detected support level")
    resistance_level: Optional[float] = Field(None, description="Detected resistance level")
    calculation_note: str = Field(default="Levels calculated using ATR (1.5x for SL, 2.5x for TP) bounded by support/resistance", description="Methodology note")


class EnhancedRecommendationResponse(BaseModel):
    """Enhanced recommendation response."""
    symbol: str = Field(..., description="Trading symbol")
    current_price: float = Field(..., gt=0, description="Current market price")
    recommendation: str = Field(..., description="Final recommendation (STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    reasoning: str = Field(..., description="Detailed reasoning")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment")
    strategy_signals: List[StrategySignalDetail] = Field(..., description="Individual strategy signals")
    scores: SignalScores = Field(..., description="Weighted signal scores")
    market_context: MarketContext = Field(..., description="Market context analysis")
    data_summary: DataSummary = Field(..., description="Data summary")
    trading_levels: Optional[TradingLevels] = Field(None, description="Entry, TP and SL levels")
    timestamp: str = Field(..., description="Recommendation timestamp")
    generated_at: str = Field(..., description="Generation timestamp")


class RecommendationRequest(BaseModel):
    """Request for generating recommendations."""
    symbol: str = Field("BTCUSDT", description="Trading symbol")
    timeframe: str = Field("1d", description="Data timeframe")
    days: int = Field(30, ge=1, le=365, description="Number of days of historical data")


class StrategyWeightsUpdate(BaseModel):
    """Request for updating strategy weights."""
    weights: Dict[str, float] = Field(..., description="Strategy weights (must sum to 1.0)")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Validate that weights sum to approximately 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Strategy weights must sum to 1.0, got {total_weight}")


class RecommendationSummary(BaseModel):
    """Summary of recommendation for quick overview."""
    symbol: str = Field(..., description="Trading symbol")
    recommendation: str = Field(..., description="Final recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    risk_level: str = Field(..., description="Risk level")
    trend: str = Field(..., description="Market trend")
    current_price: float = Field(..., gt=0, description="Current price")
    timestamp: str = Field(..., description="Recommendation timestamp")
