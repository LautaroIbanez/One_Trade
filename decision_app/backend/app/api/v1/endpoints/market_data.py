"""
API endpoints for market data from Binance.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.binance_service import BinanceService
from app.schemas.market_data import MarketDataResponse, TickerResponse

router = APIRouter()


@router.get("/binance/time", response_model=Dict[str, Any])
async def get_binance_server_time():
    """
    Get Binance server time.
    
    Returns:
        Binance server time information
    """
    try:
        async with BinanceService() as binance:
            server_time = await binance.get_server_time()
            return server_time
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting server time: {str(e)}")


@router.get("/binance/exchange-info", response_model=Dict[str, Any])
async def get_binance_exchange_info():
    """
    Get Binance exchange information.
    
    Returns:
        Exchange information including symbols and trading rules
    """
    try:
        async with BinanceService() as binance:
            exchange_info = await binance.get_exchange_info()
            return exchange_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting exchange info: {str(e)}")


@router.get("/binance/klines", response_model=MarketDataResponse)
async def get_binance_klines(
    symbol: str = Query("BTCUSDT", description="Trading pair symbol"),
    interval: str = Query("1d", description="Kline interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)"),
    limit: int = Query(100, description="Number of klines to retrieve (max 1000)"),
    days: int = Query(30, description="Number of days to fetch")
):
    """
    Get kline/candlestick data from Binance.
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
        interval: Kline interval
        limit: Number of klines to retrieve
        days: Number of days to fetch
        
    Returns:
        Market data in OHLCV format
    """
    try:
        async with BinanceService() as binance:
            # Get market data
            df = await binance.get_market_data(
                symbol=symbol,
                interval=interval,
                days=days
            )
            
            # Convert to API format
            data_records = []
            for idx, row in df.iterrows():
                data_records.append({
                    "timestamp": row['timestamp'].isoformat(),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": float(row['volume'])
                })
            
            return MarketDataResponse(
                symbol=symbol,
                interval=interval,
                data_points=len(data_records),
                data=data_records
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting klines: {str(e)}")


@router.get("/binance/ticker", response_model=List[TickerResponse])
async def get_binance_ticker(
    symbol: Optional[str] = Query(None, description="Optional symbol to get ticker for specific pair")
):
    """
    Get 24hr ticker price change statistics.
    
    Args:
        symbol: Optional symbol to get ticker for specific pair
        
    Returns:
        List of ticker data
    """
    try:
        async with BinanceService() as binance:
            tickers = await binance.get_24hr_ticker(symbol=symbol)
            
            # Convert to response format
            ticker_responses = []
            for ticker in tickers:
                ticker_responses.append(TickerResponse(
                    symbol=ticker['symbol'],
                    price_change=float(ticker['priceChange']),
                    price_change_percent=float(ticker['priceChangePercent']),
                    weighted_avg_price=float(ticker['weightedAvgPrice']),
                    prev_close_price=float(ticker['prevClosePrice']),
                    last_price=float(ticker['lastPrice']),
                    last_qty=float(ticker['lastQty']),
                    bid_price=float(ticker['bidPrice']),
                    ask_price=float(ticker['askPrice']),
                    open_price=float(ticker['openPrice']),
                    high_price=float(ticker['highPrice']),
                    low_price=float(ticker['lowPrice']),
                    volume=float(ticker['volume']),
                    quote_volume=float(ticker['quoteVolume']),
                    open_time=ticker['openTime'],
                    close_time=ticker['closeTime'],
                    count=ticker['count']
                ))
            
            return ticker_responses
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ticker: {str(e)}")


@router.get("/binance/symbols", response_model=List[str])
async def get_binance_symbols():
    """
    Get list of available trading symbols from Binance.
    
    Returns:
        List of available trading symbols
    """
    try:
        async with BinanceService() as binance:
            exchange_info = await binance.get_exchange_info()
            
            symbols = []
            for symbol_info in exchange_info.get('symbols', []):
                if symbol_info.get('status') == 'TRADING':
                    symbols.append(symbol_info['symbol'])
            
            return sorted(symbols)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting symbols: {str(e)}")