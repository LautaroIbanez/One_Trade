"""
API endpoints for enhanced recommendations with multi-strategy support.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.recommendation_engine import recommendation_engine
from app.services.signal_consolidator import signal_consolidator
from app.schemas.enhanced_recommendation import (
    EnhancedRecommendationResponse,
    RecommendationRequest,
    StrategyWeightsUpdate,
    RecommendationSummary
)

router = APIRouter()


@router.post("/generate", response_model=EnhancedRecommendationResponse)
async def generate_enhanced_recommendation(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate an enhanced trading recommendation using multiple strategies.
    
    Args:
        request: Recommendation request parameters
        db: Database session
        
    Returns:
        Enhanced recommendation with multi-strategy analysis
    """
    try:
        recommendation = await recommendation_engine.generate_recommendation(
            symbol=request.symbol,
            timeframe=request.timeframe,
            days=request.days
        )
        
        return EnhancedRecommendationResponse(**recommendation)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")


@router.get("/generate/{symbol}", response_model=EnhancedRecommendationResponse)
async def generate_recommendation_for_symbol(
    symbol: str,
    timeframe: str = Query("1d", description="Data timeframe"),
    days: int = Query(30, description="Number of days of historical data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate an enhanced trading recommendation for a specific symbol.
    
    Args:
        symbol: Trading symbol
        timeframe: Data timeframe
        days: Number of days of historical data
        db: Database session
        
    Returns:
        Enhanced recommendation with multi-strategy analysis
    """
    try:
        recommendation = await recommendation_engine.generate_recommendation(
            symbol=symbol.upper(),
            timeframe=timeframe,
            days=days
        )
        
        return EnhancedRecommendationResponse(**recommendation)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")


@router.get("/summary/{symbol}", response_model=RecommendationSummary)
async def get_recommendation_summary(
    symbol: str,
    timeframe: str = Query("1d", description="Data timeframe"),
    days: int = Query(30, description="Number of days of historical data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a quick summary of the trading recommendation.
    
    Args:
        symbol: Trading symbol
        timeframe: Data timeframe
        days: Number of days of historical data
        db: Database session
        
    Returns:
        Recommendation summary for quick overview
    """
    try:
        recommendation = await recommendation_engine.generate_recommendation(
            symbol=symbol.upper(),
            timeframe=timeframe,
            days=days
        )
        
        return RecommendationSummary(
            symbol=recommendation["symbol"],
            recommendation=recommendation["recommendation"],
            confidence=recommendation["confidence"],
            risk_level=recommendation["risk_assessment"]["level"],
            trend=recommendation["market_context"]["trend"],
            current_price=recommendation["current_price"],
            timestamp=recommendation["timestamp"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.get("/supported-symbols", response_model=List[str])
def get_supported_symbols():
    """
    Get list of supported trading symbols.
    
    Returns:
        List of supported trading symbols
    """
    try:
        return recommendation_engine.get_supported_symbols()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting supported symbols: {str(e)}")


@router.post("/supported-symbols/{symbol}")
async def add_supported_symbol(symbol: str):
    """
    Add a new supported trading symbol.
    
    Args:
        symbol: Trading symbol to add
        
    Returns:
        Success message
    """
    try:
        recommendation_engine.add_supported_symbol(symbol.upper())
        return {"message": f"Added {symbol.upper()} to supported symbols"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding symbol: {str(e)}")


@router.delete("/supported-symbols/{symbol}")
async def remove_supported_symbol(symbol: str):
    """
    Remove a supported trading symbol.
    
    Args:
        symbol: Trading symbol to remove
        
    Returns:
        Success message
    """
    try:
        recommendation_engine.remove_supported_symbol(symbol.upper())
        return {"message": f"Removed {symbol.upper()} from supported symbols"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing symbol: {str(e)}")


@router.get("/strategy-weights", response_model=Dict[str, float])
async def get_strategy_weights():
    """
    Get current strategy weights.
    
    Returns:
        Current strategy weights
    """
    try:
        return signal_consolidator.get_strategy_weights()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting strategy weights: {str(e)}")


@router.put("/strategy-weights")
async def update_strategy_weights(request: StrategyWeightsUpdate):
    """
    Update strategy weights for signal consolidation.
    
    Args:
        request: New strategy weights
        
    Returns:
        Success message with updated weights
    """
    try:
        signal_consolidator.update_strategy_weights(request.weights)
        return {
            "message": "Strategy weights updated successfully",
            "weights": signal_consolidator.get_strategy_weights()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating strategy weights: {str(e)}")


@router.get("/batch/{symbols}")
async def generate_batch_recommendations(
    symbols: str,
    timeframe: str = Query("1d", description="Data timeframe"),
    days: int = Query(30, description="Number of days of historical data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate recommendations for multiple symbols.
    
    Args:
        symbols: Comma-separated list of trading symbols
        timeframe: Data timeframe
        days: Number of days of historical data
        db: Database session
        
    Returns:
        Dictionary mapping symbols to their recommendations
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        results = {}
        
        for symbol in symbol_list:
            try:
                recommendation = await recommendation_engine.generate_recommendation(
                    symbol=symbol,
                    timeframe=timeframe,
                    days=days
                )
                results[symbol] = recommendation
            except Exception as e:
                results[symbol] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating batch recommendations: {str(e)}")
