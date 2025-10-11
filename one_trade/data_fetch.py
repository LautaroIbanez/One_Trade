"""Data fetching module with exchange integration and retry logic."""
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import ccxt
import pandas as pd
from ccxt.base.errors import NetworkError, RateLimitExceeded

from config.models import ExchangeConfig, RateLimitConfig


class DataFetcher:
    """Handles data fetching from exchanges with rate limiting and retries."""
    
    def __init__(self, exchange_config: ExchangeConfig):
        """Initialize DataFetcher. Args: exchange_config: Exchange configuration."""
        self.config = exchange_config
        self.rate_limit_config = exchange_config.rate_limit
        self.exchange = self._initialize_exchange()
    
    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize CCXT exchange instance. Returns: CCXT exchange object."""
        exchange_class = getattr(ccxt, self.config.name.value)
        exchange_params = {"enableRateLimit": True}
        if self.config.api_key and self.config.api_secret:
            exchange_params["apiKey"] = self.config.api_key
            exchange_params["secret"] = self.config.api_secret
        if self.config.testnet:
            exchange_params["options"] = {"defaultType": "future", "testnet": True}
        exchange = exchange_class(exchange_params)
        if not exchange.has["fetchOHLCV"]:
            raise ValueError(f"Exchange {self.config.name} does not support OHLCV fetching")
        return exchange
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay. Args: attempt: Current attempt number (0-indexed). Returns: Delay in seconds."""
        delay = min(self.rate_limit_config.backoff_base ** attempt, self.rate_limit_config.backoff_max)
        return delay
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, since: Optional[datetime] = None, limit: int = 1000) -> pd.DataFrame:
        """Fetch OHLCV data with retry logic. Args: symbol: Trading symbol (e.g., 'BTC/USDT'). timeframe: Timeframe (e.g., '15m', '1d'). since: Start timestamp (UTC). If None, fetches recent data. limit: Maximum number of candles to fetch. Returns: DataFrame with columns [timestamp_utc, open, high, low, close, volume]. Raises: RuntimeError: If fetching fails after all retries."""
        since_ms = int(since.timestamp() * 1000) if since else None
        for attempt in range(self.rate_limit_config.retry_attempts):
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=limit)
                if not ohlcv:
                    return pd.DataFrame(columns=["timestamp_utc", "open", "high", "low", "close", "volume"])
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["timestamp_utc"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
                df = df.drop(columns=["timestamp"])
                df = df[["timestamp_utc", "open", "high", "low", "close", "volume"]]
                return df
            except RateLimitExceeded as e:
                delay = self._exponential_backoff(attempt)
                time.sleep(delay)
            except NetworkError as e:
                delay = self._exponential_backoff(attempt)
                time.sleep(delay)
            except Exception as e:
                if attempt == self.rate_limit_config.retry_attempts - 1:
                    raise RuntimeError(f"Failed to fetch OHLCV for {symbol} {timeframe} after {self.rate_limit_config.retry_attempts} attempts: {e}") from e
                delay = self._exponential_backoff(attempt)
                time.sleep(delay)
        raise RuntimeError(f"Failed to fetch OHLCV for {symbol} {timeframe} after all retries")
    
    def fetch_ohlcv_range(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> pd.DataFrame:
        """Fetch OHLCV data for a date range, handling pagination. Args: symbol: Trading symbol. timeframe: Timeframe. start: Start timestamp (UTC). end: End timestamp (UTC). Returns: DataFrame with all OHLCV data in range."""
        timeframe_to_ms = {"1m": 60000, "5m": 300000, "15m": 900000, "30m": 1800000, "1h": 3600000, "4h": 14400000, "1d": 86400000, "1w": 604800000}
        timeframe_ms = timeframe_to_ms.get(timeframe, 900000)
        all_data = []
        current_start = start
        while current_start < end:
            df = self.fetch_ohlcv(symbol, timeframe, since=current_start, limit=1000)
            if df.empty:
                break
            all_data.append(df)
            last_timestamp = df["timestamp_utc"].max()
            if pd.isna(last_timestamp):
                break
            current_start = last_timestamp + timedelta(milliseconds=timeframe_ms)
            if current_start >= end:
                break
            time.sleep(0.1)
        if not all_data:
            return pd.DataFrame(columns=["timestamp_utc", "open", "high", "low", "close", "volume"])
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined[combined["timestamp_utc"] <= end]
        combined = combined.drop_duplicates(subset=["timestamp_utc"]).reset_index(drop=True)
        return combined
    
    def fetch_incremental(self, symbol: str, timeframe: str, last_timestamp: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch incremental data since last timestamp. Args: symbol: Trading symbol. timeframe: Timeframe. last_timestamp: Last known timestamp (UTC). If None, fetches recent data. Returns: DataFrame with new OHLCV data."""
        if last_timestamp is None:
            return self.fetch_ohlcv(symbol, timeframe, limit=1000)
        since = last_timestamp + timedelta(minutes=1)
        now = datetime.now(timezone.utc)
        if since >= now:
            return pd.DataFrame(columns=["timestamp_utc", "open", "high", "low", "close", "volume"])
        return self.fetch_ohlcv_range(symbol, timeframe, since, now)
    
    def reconcile_gaps(self, symbol: str, timeframe: str, gaps: List[dict]) -> pd.DataFrame:
        """Fetch data to fill detected gaps. Args: symbol: Trading symbol. timeframe: Timeframe. gaps: List of gap dictionaries from DataStore.check_gaps(). Returns: DataFrame with data to fill gaps."""
        if not gaps:
            return pd.DataFrame(columns=["timestamp_utc", "open", "high", "low", "close", "volume"])
        gap_data = []
        for gap in gaps:
            start = gap["start"] + timedelta(minutes=1)
            end = gap["end"]
            df = self.fetch_ohlcv_range(symbol, timeframe, start, end)
            if not df.empty:
                gap_data.append(df)
            time.sleep(0.2)
        if not gap_data:
            return pd.DataFrame(columns=["timestamp_utc", "open", "high", "low", "close", "volume"])
        return pd.concat(gap_data, ignore_index=True).drop_duplicates(subset=["timestamp_utc"]).reset_index(drop=True)



