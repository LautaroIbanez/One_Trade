"""
Recommendation service for generating trading recommendations.
"""

import pandas as pd
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.market_data import MarketData
from app.models.recommendation import Recommendation as RecommendationModel
from app.schemas.recommendation import RecommendationCreate
from app.core.exceptions import RecommendationError, DataProcessingError
import structlog

logger = structlog.get_logger(__name__)


class RecommendationService:
    """Service for generating and managing trading recommendations."""
    
    def __init__(self):
        """Initialize the recommendation service."""
        self.strategies = self._load_strategies()
        self.engine = self._initialize_engine()
    
    def _load_strategies(self) -> List:
        """Load available trading strategies."""
        # TODO: Implement strategy loading from configuration
        # For now, return empty list - will be implemented in future iterations
        return []
    
    def _initialize_engine(self):
        """Initialize the recommendation engine."""
        # TODO: Initialize the actual recommendation engine
        # For now, return None - will be implemented when strategies are available
        return None
    
    async def get_market_data(
        self, 
        db: AsyncSession, 
        symbol: str, 
        timeframe: str, 
        limit: int = 1000
    ) -> pd.DataFrame:
        """Get market data for a symbol and timeframe."""
        try:
            query = (
                select(MarketData)
                .where(
                    and_(
                        MarketData.symbol == symbol,
                        MarketData.timeframe == timeframe
                    )
                )
                .order_by(desc(MarketData.timestamp))
                .limit(limit)
            )
            
            result = await db.execute(query)
            market_data = result.scalars().all()
            
            if not market_data:
                raise DataProcessingError(f"No market data found for {symbol} {timeframe}")
            
            # Convert to DataFrame
            data = []
            for record in market_data:
                data.append({
                    'timestamp_utc': record.timestamp,
                    'open': record.open_price,
                    'high': record.high_price,
                    'low': record.low_price,
                    'close': record.close_price,
                    'volume': record.volume,
                    'quote_volume': record.quote_volume,
                    'trades_count': record.trades_count,
                    'taker_buy_volume': record.taker_buy_volume,
                    'taker_buy_quote_volume': record.taker_buy_quote_volume,
                })
            
            df = pd.DataFrame(data)
            df = df.sort_values('timestamp_utc').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error("Failed to get market data", error=str(e), symbol=symbol, timeframe=timeframe)
            raise DataProcessingError(f"Failed to get market data: {str(e)}")
    
    async def generate_recommendation(
        self,
        db: AsyncSession,
        symbol: str,
        timeframe: str = "1h"
    ) -> RecommendationModel:
        """Generate a trading recommendation for a symbol."""
        try:
            # Get market data
            market_data = await self.get_market_data(db, symbol, timeframe)
            
            if len(market_data) < 50:  # Need minimum data for analysis
                raise DataProcessingError(f"Insufficient data for {symbol} {timeframe}")
            
            # For now, generate a mock recommendation
            # TODO: Replace with actual recommendation engine when strategies are implemented
            recommendation = await self._generate_mock_recommendation(
                symbol, timeframe, market_data
            )
            
            # Save to database
            db_recommendation = RecommendationModel(**recommendation.dict())
            db.add(db_recommendation)
            await db.commit()
            await db.refresh(db_recommendation)
            
            logger.info(
                "Generated recommendation",
                symbol=symbol,
                timeframe=timeframe,
                action=recommendation.action,
                confidence=recommendation.confidence
            )
            
            return db_recommendation
            
        except Exception as e:
            logger.error("Failed to generate recommendation", error=str(e), symbol=symbol, timeframe=timeframe)
            raise RecommendationError(f"Failed to generate recommendation: {str(e)}")
    
    async def _generate_mock_recommendation(
        self,
        symbol: str,
        timeframe: str,
        market_data: pd.DataFrame
    ) -> RecommendationCreate:
        """Generate a mock recommendation for testing purposes."""
        # Get latest price
        latest_price = market_data.iloc[-1]['close']
        
        # Simple mock logic based on price movement
        price_change = (latest_price - market_data.iloc[-2]['close']) / market_data.iloc[-2]['close']
        
        if price_change > 0.02:  # 2% increase
            action = "BUY"
            confidence = 0.75
            price_target = latest_price * 1.05
            stop_loss = latest_price * 0.95
            reasoning = f"Strong bullish momentum detected. Price increased by {price_change:.2%} in the last period."
        elif price_change < -0.02:  # 2% decrease
            action = "SELL"
            confidence = 0.70
            price_target = latest_price * 0.95
            stop_loss = latest_price * 1.05
            reasoning = f"Bearish momentum detected. Price decreased by {abs(price_change):.2%} in the last period."
        else:
            action = "HOLD"
            confidence = 0.60
            price_target = None
            stop_loss = None
            reasoning = f"Sideways movement detected. Price change of {price_change:.2%} is within normal range."
        
        return RecommendationCreate(
            symbol=symbol,
            timeframe=timeframe,
            action=action,
            confidence=confidence,
            price_target=price_target,
            stop_loss=stop_loss,
            reasoning=reasoning,
            strategy_weights={
                "rsi_strategy": 0.25,
                "macd_strategy": 0.20,
                "bollinger_bands": 0.30,
                "volume_profile": 0.25
            },
            market_conditions={
                "trend": "bullish" if price_change > 0 else "bearish" if price_change < 0 else "sideways",
                "volatility": "high" if abs(price_change) > 0.03 else "medium" if abs(price_change) > 0.01 else "low",
                "volume": "high" if market_data.iloc[-1]['volume'] > market_data['volume'].mean() else "low"
            }
        )
    
    async def get_latest_recommendations(
        self,
        db: AsyncSession,
        symbol: Optional[str] = None,
        limit: int = 10
    ) -> List[RecommendationModel]:
        """Get the latest recommendations."""
        try:
            query = select(RecommendationModel).where(RecommendationModel.is_active == True)
            
            if symbol:
                query = query.where(RecommendationModel.symbol == symbol)
            
            query = query.order_by(desc(RecommendationModel.created_at)).limit(limit)
            
            result = await db.execute(query)
            recommendations = result.scalars().all()
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to get latest recommendations", error=str(e))
            raise RecommendationError(f"Failed to get latest recommendations: {str(e)}")
    
    async def update_recommendation_performance(
        self,
        db: AsyncSession,
        recommendation_id: int,
        execution_price: float,
        pnl_percentage: float
    ) -> RecommendationModel:
        """Update recommendation with execution results."""
        try:
            # Get the recommendation
            query = select(RecommendationModel).where(RecommendationModel.id == recommendation_id)
            result = await db.execute(query)
            recommendation = result.scalar_one_or_none()
            
            if not recommendation:
                raise RecommendationError(f"Recommendation {recommendation_id} not found")
            
            # Create history record
            from app.models.recommendation import RecommendationHistory
            history = RecommendationHistory(
                recommendation_id=recommendation_id,
                action=recommendation.action,
                confidence=recommendation.confidence,
                price_at_recommendation=recommendation.price_target or 0.0,
                price_target=recommendation.price_target,
                stop_loss=recommendation.stop_loss,
                reasoning=recommendation.reasoning,
                strategy_weights=recommendation.strategy_weights,
                market_conditions=recommendation.market_conditions,
                price_at_execution=execution_price,
                execution_timestamp=datetime.now(timezone.utc),
                pnl_percentage=pnl_percentage,
                pnl_absolute=pnl_percentage * (execution_price * 0.1),  # Assuming 0.1 position size
                was_profitable=pnl_percentage > 0
            )
            
            db.add(history)
            await db.commit()
            
            logger.info(
                "Updated recommendation performance",
                recommendation_id=recommendation_id,
                pnl_percentage=pnl_percentage,
                was_profitable=pnl_percentage > 0
            )
            
            return recommendation
            
        except Exception as e:
            logger.error("Failed to update recommendation performance", error=str(e))
            raise RecommendationError(f"Failed to update recommendation performance: {str(e)}")


# Global service instance
recommendation_service = RecommendationService()

