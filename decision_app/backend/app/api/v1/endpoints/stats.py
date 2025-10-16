"""
API endpoints for real-time statistics.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.stats_service import stats_service
from app.schemas.stats import RealTimeStatsResponse, HistoricalPerformance

router = APIRouter()


@router.get("/stats", response_model=RealTimeStatsResponse)
async def get_real_time_stats():
    """
    Get real-time statistics aggregated from backtest results.
    
    Returns:
        Real-time statistics with P&L, win rate, drawdown, etc.
    """
    try:
        stats = stats_service.get_aggregated_stats()
        
        return RealTimeStatsResponse(
            activeRecommendations=stats['active_recommendations'],
            totalPnL=stats['total_pnl'],
            winRate=stats['win_rate'],
            maxDrawdown=stats['max_drawdown'],
            lastUpdate=stats['last_update'],
            dataSource=stats['data_source'],
            totalTrades=stats.get('total_trades'),
            profitFactor=stats.get('profit_factor'),
            avgRMultiple=stats.get('avg_r_multiple')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@router.get("/stats/history", response_model=List[HistoricalPerformance])
async def get_historical_performance():
    """
    Get historical performance metrics for all symbols.
    
    Returns:
        List of historical performance metrics per symbol
    """
    try:
        results = stats_service.get_latest_backtest_results()
        
        performance_list = []
        for result in results:
            performance_list.append(HistoricalPerformance(
                symbol=result['symbol'],
                totalTrades=result['total_trades'],
                winningTrades=result['winning_trades'],
                losingTrades=result['losing_trades'],
                winRate=result['win_rate'],
                totalPnL=result['total_pnl'],
                maxDrawdown=result['max_drawdown'],
                profitFactor=result['profit_factor'],
                avgRMultiple=result['avg_r_multiple'],
                lastBacktestDate=result['last_backtest_date']
            ))
        
        return performance_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting historical performance: {str(e)}")


@router.get("/stats/{symbol}", response_model=HistoricalPerformance)
async def get_symbol_stats(symbol: str):
    """
    Get statistics for a specific symbol.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        Historical performance metrics for the symbol
    """
    try:
        result = stats_service.get_symbol_performance(symbol.upper())
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No backtest data found for {symbol}")
        
        return HistoricalPerformance(
            symbol=result['symbol'],
            totalTrades=result['total_trades'],
            winningTrades=result['winning_trades'],
            losingTrades=result['losing_trades'],
            winRate=result['win_rate'],
            totalPnL=result['total_pnl'],
            maxDrawdown=result['max_drawdown'],
            profitFactor=result['profit_factor'],
            avgRMultiple=result['avg_r_multiple'],
            lastBacktestDate=result['last_backtest_date']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting symbol statistics: {str(e)}")

