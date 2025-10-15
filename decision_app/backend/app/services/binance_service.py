"""
Binance API service for fetching real market data.
"""

import asyncio
import aiohttp
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import structlog

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class BinanceService:
    """Service for fetching market data from Binance API."""
    
    def __init__(self):
        """Initialize Binance service."""
        self.base_url = "https://api.binance.com/api/v3"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_server_time(self) -> Dict[str, Any]:
        """Get Binance server time."""
        try:
            async with self.session.get(f"{self.base_url}/time") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Binance API error: {response.status}")
        except Exception as e:
            logger.error(f"Error getting server time: {e}")
            raise
    
    async def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information."""
        try:
            async with self.session.get(f"{self.base_url}/exchangeInfo") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Binance API error: {response.status}")
        except Exception as e:
            logger.error(f"Error getting exchange info: {e}")
            raise
    
    async def get_klines(
        self,
        symbol: str,
        interval: str = "1d",
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[List[Any]]:
        """
        Get kline/candlestick data from Binance.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of klines to retrieve (max 1000)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of kline data
        """
        try:
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": min(limit, 1000)
            }
            
            if start_time:
                params["startTime"] = start_time
            if end_time:
                params["endTime"] = end_time
            
            async with self.session.get(
                f"{self.base_url}/klines",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Retrieved {len(data)} klines for {symbol} {interval}")
                    return data
                else:
                    error_text = await response.text()
                    raise Exception(f"Binance API error: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error getting klines for {symbol}: {e}")
            raise
    
    async def get_24hr_ticker(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get 24hr ticker price change statistics.
        
        Args:
            symbol: Optional symbol to get ticker for specific pair
            
        Returns:
            List of ticker data
        """
        try:
            url = f"{self.base_url}/ticker/24hr"
            if symbol:
                url += f"?symbol={symbol.upper()}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if symbol:
                        return [data]  # Single ticker
                    else:
                        return data  # All tickers
                else:
                    error_text = await response.text()
                    raise Exception(f"Binance API error: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Error getting 24hr ticker: {e}")
            raise
    
    def klines_to_dataframe(self, klines: List[List[Any]]) -> pd.DataFrame:
        """
        Convert Binance klines data to pandas DataFrame.
        
        Args:
            klines: Raw klines data from Binance API
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Binance klines format:
            # [open_time, open, high, low, close, volume, close_time, quote_volume, 
            #  trades, taker_buy_base_volume, taker_buy_quote_volume, ignore]
            
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base_volume',
                'taker_buy_quote_volume', 'ignore'
            ])
            
            # Convert to appropriate data types
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # Convert price and volume columns to float
            price_columns = ['open', 'high', 'low', 'close']
            volume_columns = ['volume', 'quote_volume', 'taker_buy_base_volume', 'taker_buy_quote_volume']
            
            for col in price_columns + volume_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Convert trades to int
            df['trades'] = pd.to_numeric(df['trades'], errors='coerce').astype('Int64')
            
            # Set timestamp as index
            df.set_index('open_time', inplace=True)
            
            # Select only OHLCV columns for trading strategies
            ohlcv_df = df[['open', 'high', 'low', 'close', 'volume']].copy()
            
            # Add timestamp column for API compatibility
            ohlcv_df['timestamp'] = ohlcv_df.index
            
            logger.info(f"Converted {len(ohlcv_df)} klines to DataFrame")
            return ohlcv_df
            
        except Exception as e:
            logger.error(f"Error converting klines to DataFrame: {e}")
            raise
    
    async def get_market_data(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1d",
        days: int = 30
    ) -> pd.DataFrame:
        """
        Get market data for a symbol.
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval
            days: Number of days to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Calculate start time
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Convert to milliseconds
            start_time_ms = int(start_time.timestamp() * 1000)
            end_time_ms = int(end_time.timestamp() * 1000)
            
            # Get klines data
            klines = await self.get_klines(
                symbol=symbol,
                interval=interval,
                start_time=start_time_ms,
                end_time=end_time_ms
            )
            
            # Convert to DataFrame
            df = self.klines_to_dataframe(klines)
            
            logger.info(f"Retrieved {len(df)} data points for {symbol} {interval}")
            return df
            
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            raise


# Global Binance service instance
binance_service = BinanceService()
