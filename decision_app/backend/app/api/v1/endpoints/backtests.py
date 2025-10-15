"""
API endpoints for backtesting.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.backtesting_engine import backtesting_engine
from app.schemas.backtest import (
    BacktestCreate,
    BacktestResponse,
    BacktestResultResponse,
    BacktestMetricResponse,
    TradeResponse
)

router = APIRouter()


@router.post("/run", response_model=BacktestResultResponse)
async def run_backtest(
    backtest_request: BacktestCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Run a new backtest.
    
    Args:
        backtest_request: Backtest configuration
        background_tasks: Background tasks for async processing
        db: Database session
        
    Returns:
        Backtest results with performance metrics
    """
    try:
        # Validate date range
        if backtest_request.end_date <= backtest_request.start_date:
            raise HTTPException(
                status_code=400,
                detail="End date must be after start date"
            )
        
        # Check if date range is too large (max 1 year)
        date_diff = backtest_request.end_date - backtest_request.start_date
        if date_diff.days > 365:
            raise HTTPException(
                status_code=400,
                detail="Date range cannot exceed 1 year"
            )
        
        # Run backtest
        result = await backtesting_engine.run_backtest(
            symbol=backtest_request.symbol,
            strategy_name=backtest_request.strategy_name,
            start_date=backtest_request.start_date,
            end_date=backtest_request.end_date,
            initial_capital=backtest_request.initial_capital,
            strategy_params=backtest_request.strategy_params,
            timeframe=backtest_request.timeframe
        )
        
        # Convert trades to response format
        trades_response = []
        for trade in result.trades:
            trades_response.append(TradeResponse(
                id=0,  # Will be set by database
                symbol=trade.symbol,
                side=trade.side.value,
                entry_price=trade.entry_price,
                exit_price=trade.exit_price,
                quantity=trade.quantity,
                entry_time=trade.entry_time or datetime.now(),
                exit_time=trade.exit_time,
                pnl=trade.pnl,
                pnl_percentage=trade.pnl_percentage,
                duration_hours=trade.duration_hours,
                entry_signal=trade.entry_signal,
                exit_signal=trade.exit_signal,
                confidence=trade.confidence,
                is_open=trade.is_open
            ))
        
        # Create backtest response
        backtest_response = BacktestResponse(
            id=0,  # Will be set by database
            name=backtest_request.name,
            symbol=backtest_request.symbol,
            strategy_name=backtest_request.strategy_name,
            start_date=backtest_request.start_date,
            end_date=backtest_request.end_date,
            initial_capital=backtest_request.initial_capital,
            final_capital=result.final_capital,
            total_return=result.total_return,
            annualized_return=result.annualized_return,
            sharpe_ratio=result.sharpe_ratio,
            max_drawdown=result.max_drawdown,
            win_rate=result.win_rate,
            total_trades=result.total_trades,
            avg_trade_duration=result.avg_trade_duration,
            best_trade=result.best_trade,
            worst_trade=result.worst_trade,
            strategy_params=backtest_request.strategy_params,
            timeframe=backtest_request.timeframe,
            status="completed",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create performance metrics response
        performance_metrics = [
            {
                "id": 0,
                "metric_name": "Total Return",
                "metric_value": result.total_return,
                "metric_type": "return",
                "period": "total",
                "calculated_at": datetime.now()
            },
            {
                "id": 0,
                "metric_name": "Sharpe Ratio",
                "metric_value": result.sharpe_ratio,
                "metric_type": "risk",
                "period": "total",
                "calculated_at": datetime.now()
            },
            {
                "id": 0,
                "metric_name": "Max Drawdown",
                "metric_value": result.max_drawdown,
                "metric_type": "risk",
                "period": "total",
                "calculated_at": datetime.now()
            },
            {
                "id": 0,
                "metric_name": "Win Rate",
                "metric_value": result.win_rate,
                "metric_type": "trade",
                "period": "total",
                "calculated_at": datetime.now()
            }
        ]
        
        return BacktestResultResponse(
            backtest=backtest_response,
            trades=trades_response,
            performance_metrics=performance_metrics,
            summary={
                "total_return_pct": f"{result.total_return:.2%}",
                "annualized_return_pct": f"{result.annualized_return:.2%}",
                "sharpe_ratio": f"{result.sharpe_ratio:.2f}",
                "max_drawdown_pct": f"{result.max_drawdown:.2%}",
                "win_rate_pct": f"{result.win_rate:.2%}",
                "total_trades": result.total_trades,
                "profit_factor": f"{result.profit_factor:.2f}",
                "calmar_ratio": f"{result.calmar_ratio:.2f}",
                "sortino_ratio": f"{result.sortino_ratio:.2f}"
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running backtest: {str(e)}")


@router.get("/strategies", response_model=List[str])
async def get_available_strategies():
    """
    Get list of available strategies for backtesting.
    
    Returns:
        List of strategy names
    """
    try:
        from app.services.strategy_service import strategy_service
        return list(strategy_service._strategies.keys())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting strategies: {str(e)}")


@router.get("/symbols", response_model=List[str])
async def get_available_symbols():
    """
    Get list of available symbols for backtesting.
    
    Returns:
        List of trading symbols
    """
    try:
        from app.services.recommendation_engine import recommendation_engine
        return recommendation_engine.get_supported_symbols()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting symbols: {str(e)}")


@router.get("/quick-test/{symbol}")
async def run_quick_backtest(
    symbol: str,
    strategy: str = Query("RSI Strategy", description="Strategy name"),
    days: int = Query(30, ge=7, le=90, description="Number of days to backtest"),
    initial_capital: float = Query(10000.0, gt=0, description="Initial capital"),
    db: AsyncSession = Depends(get_db)
):
    """
    Run a quick backtest for testing purposes.
    
    Args:
        symbol: Trading symbol
        strategy: Strategy name
        days: Number of days to backtest
        initial_capital: Initial capital
        
    Returns:
        Quick backtest results
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Run backtest
        result = await backtesting_engine.run_backtest(
            symbol=symbol,
            strategy_name=strategy,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        
        return {
            "symbol": symbol,
            "strategy": strategy,
            "period": f"{days} days",
            "initial_capital": initial_capital,
            "final_capital": result.final_capital,
            "total_return": f"{result.total_return:.2%}",
            "annualized_return": f"{result.annualized_return:.2%}",
            "sharpe_ratio": f"{result.sharpe_ratio:.2f}",
            "max_drawdown": f"{result.max_drawdown:.2%}",
            "win_rate": f"{result.win_rate:.2%}",
            "total_trades": result.total_trades,
            "avg_trade_duration": f"{result.avg_trade_duration:.1f} hours",
            "best_trade": f"{result.best_trade:.2%}",
            "worst_trade": f"{result.worst_trade:.2%}",
            "profit_factor": f"{result.profit_factor:.2f}",
            "calmar_ratio": f"{result.calmar_ratio:.2f}",
            "sortino_ratio": f"{result.sortino_ratio:.2f}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running quick backtest: {str(e)}")


@router.get("/compare/{symbol}")
async def compare_strategies(
    symbol: str,
    days: int = Query(30, ge=7, le=90, description="Number of days to backtest"),
    initial_capital: float = Query(10000.0, gt=0, description="Initial capital"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple strategies on the same symbol.
    
    Args:
        symbol: Trading symbol
        days: Number of days to backtest
        initial_capital: Initial capital
        
    Returns:
        Comparison results for all strategies
    """
    try:
        from app.services.strategy_service import strategy_service
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all available strategies
        strategies = list(strategy_service._strategies.keys())
        
        # Run backtests for all strategies
        results = {}
        for strategy_name in strategies:
            try:
                result = await backtesting_engine.run_backtest(
                    symbol=symbol,
                    strategy_name=strategy_name,
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=initial_capital
                )
                
                results[strategy_name] = {
                    "total_return": f"{result.total_return:.2%}",
                    "annualized_return": f"{result.annualized_return:.2%}",
                    "sharpe_ratio": f"{result.sharpe_ratio:.2f}",
                    "max_drawdown": f"{result.max_drawdown:.2%}",
                    "win_rate": f"{result.win_rate:.2%}",
                    "total_trades": result.total_trades,
                    "profit_factor": f"{result.profit_factor:.2f}",
                    "calmar_ratio": f"{result.calmar_ratio:.2f}",
                    "sortino_ratio": f"{result.sortino_ratio:.2f}"
                }
            except Exception as e:
                results[strategy_name] = {"error": str(e)}
        
        return {
            "symbol": symbol,
            "period": f"{days} days",
            "initial_capital": initial_capital,
            "strategies": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing strategies: {str(e)}")