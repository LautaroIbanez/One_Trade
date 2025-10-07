"""
Utility Functions Module
Contains helper functions for data fetching, resampling, and session management.
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import pytz
import time
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_symbol_type(symbol: str) -> tuple[str, str]:
    """
    Detect symbol type and return appropriate exchange name and market type.
    
    Args:
        symbol: Trading symbol (e.g., 'BTC/USDT:USDT', 'BTC/USDT', 'BTCUSD_PERP')
    
    Returns:
        tuple: (exchange_name, market_type)
    """
    symbol_upper = symbol.upper()
    
    # Futures symbols
    if ':USDT' in symbol_upper:
        return 'binanceusdm', 'future'
    elif ':USD' in symbol_upper:
        return 'binancecoinm', 'future'
    elif '_PERP' in symbol_upper:
        return 'binanceusdm', 'future'
    else:
        # Spot symbols
        return 'binance', 'spot'


def create_exchange_client(exchange_name: str, market_type: str = 'future') -> ccxt.Exchange:
    """
    Create and configure exchange client with proper settings.
    
    Args:
        exchange_name: Exchange name (e.g., 'binance', 'binanceusdm')
        market_type: Market type ('spot', 'future')
    
    Returns:
        ccxt.Exchange: Configured exchange client
    """
    config = {
        'apiKey': '',  # No API key needed for public data
        'secret': '',
        'sandbox': False,
        'enableRateLimit': True,
    }
    
    if market_type == 'future':
        config['options'] = {'defaultType': 'future'}
    
    exchange = getattr(ccxt, exchange_name)(config)
    
    # Load markets to ensure proper symbol mapping
    try:
        exchange.load_markets()
        logger.info(f"Loaded markets for {exchange_name} ({market_type})")
    except Exception as e:
        logger.warning(f"Could not load markets for {exchange_name}: {e}")
    
    return exchange


def fetch_with_retry(exchange: ccxt.Exchange, method: str, symbol: str, *args, max_retries: int = 3, **kwargs) -> Optional[Any]:
    """
    Fetch data with retry logic and exponential backoff.
    
    Args:
        exchange: Exchange client
        method: Method name to call ('fetch_ohlcv', 'fetch_ticker', etc.)
        symbol: Trading symbol
        *args: Positional arguments for the method
        max_retries: Maximum number of retry attempts
        **kwargs: Keyword arguments for the method
    
    Returns:
        Fetched data or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} - {method} for {symbol}")
            result = getattr(exchange, method)(symbol, *args, **kwargs)
            logger.info(f"Successfully fetched {method} for {symbol}")
            return result
            
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {e}")
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} attempts failed for {symbol}")
                
        except Exception as e:
            logger.error(f"Unexpected error in {method} for {symbol}: {e}")
            break
    
    return None


def fetch_historical_data(symbol, since, until=None, timeframe='1h', exchange_name=None):
    """
    Fetch historical data from Binance with automatic symbol type detection.
    
    Args:
        symbol: Trading symbol (e.g., 'BTC/USDT:USDT')
        since: Start date in ISO format or datetime
        until: End date in ISO format or datetime (optional)
        timeframe: Data timeframe ('1h', '15m', '5m', etc.)
        exchange_name: Exchange name (optional, auto-detected if None)
    
    Returns:
        pandas.DataFrame: OHLCV data with UTC timezone
    """
    try:
        # Auto-detect exchange and market type if not provided
        if exchange_name is None:
            exchange_name, market_type = detect_symbol_type(symbol)
            logger.info(f"Auto-detected {exchange_name} ({market_type}) for {symbol}")
        else:
            market_type = 'future'  # Default to future for backward compatibility
        
        # Initialize exchange with proper configuration
        exchange = create_exchange_client(exchange_name, market_type)
        
        # Parse dates
        if isinstance(since, str):
            # Handle date-only strings (YYYY-MM-DD) by adding timezone
            if len(since) == 10 and since.count('-') == 2:
                since_dt = datetime.fromisoformat(since + 'T00:00:00+00:00')
            else:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        else:
            since_dt = since
            
        if until:
            if isinstance(until, str):
                # Handle date-only strings (YYYY-MM-DD) by adding timezone and bumping to next day
                if len(until) == 10 and until.count('-') == 2:
                    until_dt = datetime.fromisoformat(until + 'T00:00:00+00:00') + timedelta(days=1)
                else:
                    until_dt = datetime.fromisoformat(until.replace('Z', '+00:00'))
            else:
                until_dt = until
        else:
            until_dt = datetime.now(timezone.utc)
        
        # Ensure timezone awareness
        if since_dt.tzinfo is None:
            since_dt = since_dt.replace(tzinfo=timezone.utc)
        if until_dt.tzinfo is None:
            until_dt = until_dt.replace(tzinfo=timezone.utc)
        
        # Ensure until_dt > since_dt
        if until_dt <= since_dt:
            until_dt = since_dt + timedelta(days=1)
        
        # Convert to milliseconds
        since_ms = int(since_dt.timestamp() * 1000)
        until_ms = int(until_dt.timestamp() * 1000)
        
        print(f"Fetching {symbol} data from {since_dt} to {until_dt} ({timeframe})...")
        
        # Fetch data in chunks to avoid rate limits
        all_data = []
        current_since = since_ms
        chunk_size = 1000  # Number of candles per request
        
        while current_since < until_ms:
            # Calculate chunk end time
            chunk_until = min(current_since + (chunk_size * _get_timeframe_ms(timeframe)), until_ms)
            
            # Fetch chunk with retry logic
            ohlcv = fetch_with_retry(exchange, 'fetch_ohlcv', symbol, timeframe, current_since, chunk_size)
            
            if not ohlcv:
                logger.warning(f"No data returned for chunk starting at {current_since}")
                break
            
            all_data.extend(ohlcv)
            
            # Update current_since to last timestamp + 1
            current_since = ohlcv[-1][0] + 1
            
            # Rate limiting
            time.sleep(0.1)
        
        if not all_data:
            print(f"No data retrieved for {symbol}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df.set_index('timestamp', inplace=True)
        
        # Ensure UTC timezone
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        else:
            df.index = df.index.tz_convert('UTC')
        
        # Remove duplicates and sort
        df = df[~df.index.duplicated(keep='first')]
        df = df.sort_index()
        
        # Filter by date range (until_dt is exclusive upper bound)
        df = df[(df.index >= since_dt) & (df.index < until_dt)]
        
        # Standardize and validate OHLC columns
        df = standardize_ohlc_columns(df)
        is_valid, validation_msg = validate_data_integrity(df)
        if not is_valid:
            logger.warning(f"Data validation warning for {symbol}: {validation_msg}")
        
        logger.info(f"Retrieved {len(df)} candles for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return pd.DataFrame()


def standardize_ohlc_columns(df):
    """
    Standardize OHLC column names and ensure all required columns exist.
    
    This function handles cases where:
    - CCXT returns abbreviated column names (O, H, L, C, V)
    - Columns might be in different cases (Open vs open)
    - Some columns might be missing or None
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with standardized column names ['open', 'high', 'low', 'close', 'volume']
    """
    if df.empty:
        return df
    
    # Mapping of possible column name variations to standard names
    column_mappings = {
        'open': ['open', 'Open', 'OPEN', 'O', 'o'],
        'high': ['high', 'High', 'HIGH', 'H', 'h'],
        'low': ['low', 'Low', 'LOW', 'L', 'l'],
        'close': ['close', 'Close', 'CLOSE', 'C', 'c'],
        'volume': ['volume', 'Volume', 'VOLUME', 'V', 'v', 'vol', 'Vol']
    }
    
    # Rename columns to standard names
    rename_dict = {}
    for standard_name, variations in column_mappings.items():
        for col in df.columns:
            if col in variations and col != standard_name:
                rename_dict[col] = standard_name
                break
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
        logger.debug(f"Renamed columns: {rename_dict}")
    
    # Ensure all required columns exist
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        logger.error(f"Missing required OHLC columns after standardization: {missing_columns}")
        raise ValueError(f"Missing required OHLC columns: {missing_columns}. Available columns: {list(df.columns)}")
    
    # Ensure numeric dtypes
    for col in required_columns:
        if df[col].dtype == object or df[col].dtype == 'O':
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                logger.warning(f"Column '{col}' was not numeric, converted with coercion")
            except Exception as e:
                logger.error(f"Failed to convert column '{col}' to numeric: {e}")
                raise ValueError(f"Column '{col}' contains non-numeric data")
    
    # Fill any NaN values that resulted from coercion
    if df[required_columns].isnull().any().any():
        nan_counts = df[required_columns].isnull().sum()
        logger.warning(f"Found NaN values after numeric conversion: {nan_counts.to_dict()}")
        # Forward fill then backward fill to handle NaNs
        df[required_columns] = df[required_columns].fillna(method='ffill').fillna(method='bfill')
        remaining_nans = df[required_columns].isnull().sum().sum()
        if remaining_nans > 0:
            logger.error(f"Could not fill all NaN values: {remaining_nans} remaining")
            raise ValueError(f"Data contains unfillable NaN values: {remaining_nans}")
    
    return df


def _get_timeframe_ms(timeframe):
    """Convert timeframe string to milliseconds."""
    timeframe_map = {
        '1m': 60 * 1000,
        '3m': 3 * 60 * 1000,
        '5m': 5 * 60 * 1000,
        '15m': 15 * 60 * 1000,
        '30m': 30 * 60 * 1000,
        '1h': 60 * 60 * 1000,
        '2h': 2 * 60 * 60 * 1000,
        '4h': 4 * 60 * 60 * 1000,
        '6h': 6 * 60 * 60 * 1000,
        '8h': 8 * 60 * 60 * 1000,
        '12h': 12 * 60 * 60 * 1000,
        '1d': 24 * 60 * 60 * 1000,
    }
    
    return timeframe_map.get(timeframe, 60 * 60 * 1000)  # Default to 1 hour


def resample_data(df, timeframe, agg_method='ohlc'):
    """
    Resample data to different timeframe.
    
    Args:
        df: DataFrame with OHLCV data
        timeframe: Target timeframe string
        agg_method: Aggregation method ('ohlc' or 'last')
    
    Returns:
        pandas.DataFrame: Resampled data
    """
    try:
        if df.empty:
            return df
        
        # Define aggregation rules
        if agg_method == 'ohlc':
            agg_rules = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }
        else:  # last
            agg_rules = {
                'open': 'last',
                'high': 'last',
                'low': 'last',
                'close': 'last',
                'volume': 'last'
            }
        
        # Resample
        resampled = df.resample(timeframe).agg(agg_rules)
        
        # Remove rows with NaN values
        resampled = resampled.dropna()
        
        return resampled
        
    except Exception as e:
        print(f"Error resampling data: {e}")
        return df


def get_trading_sessions():
    """Get trading session times in UTC."""
    return {
        'orb_start': 11,    # 11:00 UTC
        'orb_end': 12,      # 12:00 UTC
        'entry_start': 11,  # 11:00 UTC
        'entry_end': 13,    # 13:00 UTC
        'session_end': 17   # 17:00 UTC
    }


def is_market_open(dt_utc):
    """Check if market is open at given UTC time."""
    hour = dt_utc.hour
    return 0 <= hour < 24  # Crypto markets are 24/7


def get_previous_close(data, current_time):
    """Get previous close price at given time."""
    try:
        previous_data = data[data.index < current_time]
        if not previous_data.empty:
            return previous_data['close'].iloc[-1]
        return None
    except:
        return None


def validate_data_integrity(df, required_columns=['open', 'high', 'low', 'close', 'volume']):
    """
    Comprehensive validation of OHLCV data integrity.
    
    Checks:
    - Required columns presence
    - Data types (numeric)
    - NaN/Inf values
    - Negative or zero prices
    - OHLC relationships
    - Index ordering
    - Minimum data points
    
    Args:
        df: DataFrame with OHLCV data
        required_columns: List of required column names
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if df.empty:
        return False, "Data is empty"
    
    # Check minimum data points (at least 24 hours for 1h timeframe)
    if len(df) < 24:
        return False, f"Insufficient data: {len(df)} candles (minimum 24 required)"
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing columns: {missing_columns}"
    
    # Check data types (must be numeric)
    for col in required_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False, f"Column '{col}' is not numeric (dtype: {df[col].dtype})"
    
    # Check for NaN values
    nan_counts = df[required_columns].isnull().sum()
    if nan_counts.any():
        return False, f"NaN values found: {nan_counts[nan_counts > 0].to_dict()}"
    
    # Check for infinite values
    inf_mask = df[required_columns].isin([np.inf, -np.inf])
    if inf_mask.any().any():
        inf_counts = inf_mask.sum()
        return False, f"Infinite values found: {inf_counts[inf_counts > 0].to_dict()}"
    
    # Check for negative or zero prices
    price_columns = ['open', 'high', 'low', 'close']
    negative_or_zero_prices = (df[price_columns] <= 0).any()
    if negative_or_zero_prices.any():
        problematic_cols = [col for col in price_columns if (df[col] <= 0).any()]
        return False, f"Negative or zero prices found in columns: {problematic_cols}"
    
    # Check for negative volume (allow zero volume for low-liquidity periods)
    if (df['volume'] < 0).any():
        return False, "Negative volume found"
    
    # Check OHLC logic (high must be >= all others, low must be <= all others)
    invalid_high = (df['high'] < df['low']) | (df['high'] < df['open']) | (df['high'] < df['close'])
    invalid_low = (df['low'] > df['open']) | (df['low'] > df['close']) | (df['low'] > df['high'])
    
    if invalid_high.any():
        num_invalid = invalid_high.sum()
        return False, f"Invalid OHLC: {num_invalid} candles where high < other prices"
    
    if invalid_low.any():
        num_invalid = invalid_low.sum()
        return False, f"Invalid OHLC: {num_invalid} candles where low > other prices"
    
    # Check index ordering (must be sorted chronologically)
    if not df.index.is_monotonic_increasing:
        return False, "Index is not sorted in chronological order"
    
    # Check for duplicate timestamps
    if df.index.duplicated().any():
        num_dupes = df.index.duplicated().sum()
        return False, f"Duplicate timestamps found: {num_dupes} duplicates"
    
    return True, "Data validation passed"


def calculate_returns(prices):
    """Calculate simple returns from price series."""
    return prices.pct_change().dropna()


def calculate_log_returns(prices):
    """Calculate logarithmic returns from price series."""
    return np.log(prices / prices.shift(1)).dropna()


def get_volatility(returns, window=20):
    """Calculate rolling volatility."""
    return returns.rolling(window=window).std() * np.sqrt(252)  # Annualized


def format_currency(amount, currency='USDT', decimals=2):
    """Format currency amount for display."""
    return f"{amount:,.{decimals}f} {currency}"


def format_percentage(value, decimals=1):
    """Format percentage value for display."""
    return f"{value:.{decimals}f}%"


def get_timeframe_description(timeframe):
    """Get human-readable description of timeframe."""
    descriptions = {
        '1m': '1 minute',
        '3m': '3 minutes',
        '5m': '5 minutes',
        '15m': '15 minutes',
        '30m': '30 minutes',
        '1h': '1 hour',
        '2h': '2 hours',
        '4h': '4 hours',
        '6h': '6 hours',
        '8h': '8 hours',
        '12h': '12 hours',
        '1d': '1 day',
    }
    return descriptions.get(timeframe, timeframe)


def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is zero."""
    return numerator / denominator if denominator != 0 else default


def clamp(value, min_value, max_value):
    """Clamp value between min and max."""
    return max(min_value, min(value, max_value))


def round_to_precision(value, precision):
    """Round value to specified decimal precision."""
    return round(value, precision)


def get_current_utc_time():
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def is_weekend(dt):
    """Check if given datetime is weekend."""
    return dt.weekday() >= 5  # Saturday = 5, Sunday = 6


def get_next_trading_day(dt):
    """Get next trading day (skip weekends for traditional markets)."""
    next_day = dt + timedelta(days=1)
    while is_weekend(next_day):
        next_day += timedelta(days=1)
    return next_day


def fetch_latest_price(symbol, exchange_name=None):
    """
    Fetch the latest price via ccxt with automatic symbol type detection and retry logic.
    Returns dict with keys: price, bid, ask, volume, timestamp, symbol, exchange.
    Returns None on failure.
    """
    try:
        # Auto-detect exchange and market type if not provided
        if exchange_name is None:
            exchange_name, market_type = detect_symbol_type(symbol)
            logger.info(f"Auto-detected {exchange_name} ({market_type}) for {symbol} price fetch")
        else:
            market_type = 'future'  # Default to future for backward compatibility
        
        # Initialize exchange with proper configuration
        exchange = create_exchange_client(exchange_name, market_type)
        
        # Fetch ticker with retry logic
        ticker = fetch_with_retry(exchange, 'fetch_ticker', symbol)
        
        if not ticker:
            logger.error(f"Failed to fetch ticker for {symbol} after all retries")
            return None
        
        # Parse timestamp
        ts = ticker.get('timestamp') or ticker.get('datetime')
        if isinstance(ts, (int, float)):
            ts_dt = datetime.fromtimestamp(ts/1000.0, tz=timezone.utc)
        else:
            try:
                ts_dt = datetime.now(timezone.utc) if ts is None else datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
            except Exception:
                ts_dt = datetime.now(timezone.utc)
        
        result = {
            'price': ticker.get('last', ticker.get('close')),
            'bid': ticker.get('bid'),
            'ask': ticker.get('ask'),
            'volume': ticker.get('baseVolume', ticker.get('quoteVolume', 0)),
            'timestamp': ts_dt,
            'symbol': symbol,
            'exchange': exchange_name
        }
        
        logger.info(f"Successfully fetched price for {symbol}: ${result['price']}")
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error fetching latest price for {symbol}: {e}")
        return None


def get_fetch_error_message(symbol: str, operation: str = "data") -> str:
    """
    Generate a clear error message for frontend display when fetch operations fail.
    
    Args:
        symbol: Trading symbol that failed
        operation: Type of operation that failed ('data', 'price')
    
    Returns:
        str: User-friendly error message
    """
    if operation == "price":
        return f"Error al obtener el precio actual de {symbol}. Verifique la conexión a internet y que el símbolo sea válido."
    else:
        return f"Error al obtener datos históricos de {symbol}. Verifique la conexión a internet y que el símbolo sea válido."
