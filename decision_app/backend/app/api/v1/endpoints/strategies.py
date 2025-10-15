"""
API endpoints for trading strategies.
"""

from typing import List, Dict, Any
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.strategy_service import strategy_service
from app.strategies.base_strategy import Signal
from app.schemas.strategy import StrategyInfo, StrategyAnalysis, StrategyPerformance

router = APIRouter()


@router.get("/", response_model=List[StrategyInfo])
async def list_strategies():
    """
    List all available trading strategies.
    
    Returns:
        List of strategy information
    """
    try:
        strategies = strategy_service.list_strategies()
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing strategies: {str(e)}")


@router.get("/{strategy_name}", response_model=StrategyInfo)
async def get_strategy(strategy_name: str):
    """
    Get information about a specific strategy.
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        Strategy information
    """
    strategy = strategy_service.get_strategy(strategy_name)
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy '{strategy_name}' not found")
    
    return strategy.get_info()


@router.post("/{strategy_name}/analyze", response_model=StrategyAnalysis)
async def analyze_with_strategy(
    strategy_name: str,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze market data with a specific strategy.
    
    Args:
        strategy_name: Name of the strategy to use
        data: Market data in OHLCV format
        db: Database session
        
    Returns:
        Analysis results with signals
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data.get('data', []))
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Validate required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"Data must contain columns: {required_columns}"
            )
        
        # Analyze with strategy
        signals = strategy_service.analyze_with_strategy(strategy_name, df)
        
        # Convert signals to dict format
        signals_data = []
        for signal in signals:
            signals_data.append({
                "signal": signal.signal.value,
                "confidence": signal.confidence,
                "price": signal.price,
                "timestamp": signal.timestamp.isoformat(),
                "reasoning": signal.reasoning,
                "metadata": signal.metadata
            })
        
        return StrategyAnalysis(
            strategy=strategy_name,
            total_signals=len(signals),
            signals=signals_data
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")


@router.post("/analyze-all", response_model=Dict[str, StrategyAnalysis])
async def analyze_with_all_strategies(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze market data with all available strategies.
    
    Args:
        data: Market data in OHLCV format
        db: Database session
        
    Returns:
        Analysis results for all strategies
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data.get('data', []))
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Validate required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"Data must contain columns: {required_columns}"
            )
        
        # Analyze with all strategies
        results = strategy_service.analyze_with_all_strategies(df)
        
        # Convert to response format
        response = {}
        for strategy_name, signals in results.items():
            signals_data = []
            for signal in signals:
                signals_data.append({
                    "signal": signal.signal.value,
                    "confidence": signal.confidence,
                    "price": signal.price,
                    "timestamp": signal.timestamp.isoformat(),
                    "reasoning": signal.reasoning,
                    "metadata": signal.metadata
                })
            
            response[strategy_name] = StrategyAnalysis(
                strategy=strategy_name,
                total_signals=len(signals),
                signals=signals_data
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")


@router.post("/{strategy_name}/performance", response_model=StrategyPerformance)
async def get_strategy_performance(
    strategy_name: str,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Get performance metrics for a strategy.
    
    Args:
        strategy_name: Name of the strategy
        data: Market data in OHLCV format
        db: Database session
        
    Returns:
        Strategy performance metrics
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data.get('data', []))
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Get performance metrics
        performance = strategy_service.get_strategy_performance(strategy_name, df)
        
        return StrategyPerformance(**performance)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance: {str(e)}")
