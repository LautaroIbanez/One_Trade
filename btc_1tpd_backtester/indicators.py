"""
Technical Indicators Module
Contains implementations of EMA, ATR, ADX, VWAP and other technical indicators.
"""

import pandas as pd
import numpy as np


def ema(data, period, price_col='close'):
    """Calculate Exponential Moving Average."""
    return data[price_col].ewm(span=period, adjust=False).mean()


def sma(data, period, price_col='close'):
    """Calculate Simple Moving Average."""
    return data[price_col].rolling(window=period, min_periods=period).mean()


def atr(data, period=14):
    """Calculate Average True Range."""
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift())
    low_close = np.abs(data['low'] - data['close'].shift())
    
    true_range = np.maximum(high_low, np.maximum(high_close, low_close))
    return true_range.rolling(window=period, min_periods=period).mean()


def true_range(data):
    """Calculate True Range for a single bar."""
    if len(data) < 2:
        return data['high'] - data['low']
    
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift())
    low_close = np.abs(data['low'] - data['close'].shift())
    
    return np.maximum(high_low, np.maximum(high_close, low_close))


def adx(data, period=14):
    """Calculate Average Directional Index."""
    # Calculate True Range
    tr = true_range(data)
    
    # Calculate Directional Movement
    dm_plus = np.where((data['high'].diff() > data['low'].diff().abs()) & 
                      (data['high'].diff() > 0), data['high'].diff(), 0)
    dm_minus = np.where((data['low'].diff().abs() > data['high'].diff()) & 
                       (data['low'].diff() < 0), data['low'].diff().abs(), 0)
    
    # Smooth the values
    atr_smooth = tr.rolling(window=period).mean()
    dm_plus_smooth = pd.Series(dm_plus, index=data.index).rolling(window=period).mean()
    dm_minus_smooth = pd.Series(dm_minus, index=data.index).rolling(window=period).mean()
    
    # Calculate Directional Indicators
    di_plus = 100 * (dm_plus_smooth / atr_smooth)
    di_minus = 100 * (dm_minus_smooth / atr_smooth)
    
    # Calculate ADX
    dx = 100 * np.abs(di_plus - di_minus) / (di_plus + di_minus)
    adx = dx.rolling(window=period).mean()
    
    return adx


def vwap(data, volume_col='volume'):
    """Calculate Volume Weighted Average Price."""
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    cumulative_tp_volume = (typical_price * data[volume_col]).cumsum()
    cumulative_volume = data[volume_col].cumsum()
    
    return cumulative_tp_volume / cumulative_volume


def opening_range_high(data, start_time, end_time):
    """Calculate Opening Range High between specified times."""
    # Convert datetime to time for comparison
    if hasattr(start_time, 'time'):
        start_time_obj = start_time.time()
    else:
        start_time_obj = start_time
        
    if hasattr(end_time, 'time'):
        end_time_obj = end_time.time()
    else:
        end_time_obj = end_time
    
    mask = (data.index.time >= start_time_obj) & (data.index.time <= end_time_obj)
    return data[mask]['high'].max() if mask.any() else np.nan


def opening_range_low(data, start_time, end_time):
    """Calculate Opening Range Low between specified times."""
    # Convert datetime to time for comparison
    if hasattr(start_time, 'time'):
        start_time_obj = start_time.time()
    else:
        start_time_obj = start_time
        
    if hasattr(end_time, 'time'):
        end_time_obj = end_time.time()
    else:
        end_time_obj = end_time
    
    mask = (data.index.time >= start_time_obj) & (data.index.time <= end_time_obj)
    return data[mask]['low'].min() if mask.any() else np.nan


def opening_range_breakout(data, orb_high, orb_low, side):
    """Check if price has broken the opening range."""
    current_price = data['close'].iloc[-1]
    
    if side == 'long':
        return current_price > orb_high
    elif side == 'short':
        return current_price < orb_low
    
    return False


def engulfing_pattern(data):
    """Check for bullish/bearish engulfing pattern."""
    if len(data) < 2:
        return False, 'none'
    
    current = data.iloc[-1]
    previous = data.iloc[-2]
    
    # Bullish engulfing
    if (current['close'] > current['open'] and 
        previous['close'] < previous['open'] and
        current['open'] < previous['close'] and 
        current['close'] > previous['open']):
        return True, 'bullish'
    
    # Bearish engulfing
    if (current['close'] < current['open'] and 
        previous['close'] > previous['open'] and
        current['open'] > previous['close'] and 
        current['close'] < previous['open']):
        return True, 'bearish'
    
    return False, 'none'


def volume_confirmation(data, period=20):
    """Check if current volume is above SMA volume."""
    if len(data) < period:
        return False
    
    volume_sma = data['volume'].rolling(window=period).mean().iloc[-1]
    current_volume = data['volume'].iloc[-1]
    
    return current_volume > volume_sma


def calculate_r_multiple(entry_price, exit_price, stop_loss, side):
    """Calculate R-multiple for a trade."""
    if side == 'long':
        if exit_price > entry_price:
            # Winning trade
            return (exit_price - entry_price) / (entry_price - stop_loss)
        else:
            # Losing trade
            return (exit_price - entry_price) / (entry_price - stop_loss)
    else:  # short
        if exit_price < entry_price:
            # Winning trade
            return (entry_price - exit_price) / (stop_loss - entry_price)
        else:
            # Losing trade
            return (entry_price - exit_price) / (stop_loss - entry_price)


def get_macro_bias(htf_data):
    """Determine macro bias based on EMA200 and EMA50."""
    if len(htf_data) < 200:
        return 'neutral'
    
    ema_200 = ema(htf_data, 200).iloc[-1]
    ema_50 = ema(htf_data, 50).iloc[-1]
    current_price = htf_data['close'].iloc[-1]
    
    # Long bias: close > EMA200 and EMA50 > EMA200
    if current_price > ema_200 and ema_50 > ema_200:
        return 'long'
    
    # Short bias: close < EMA200 and EMA50 < EMA200
    elif current_price < ema_200 and ema_50 < ema_200:
        return 'short'
    
    return 'neutral'


def is_trading_session(time_utc, start_hour=11, end_hour=17):
    """Check if current time is within trading session."""
    # Handle both datetime and pandas Timestamp
    if hasattr(time_utc, 'hour'):
        hour = time_utc.hour
    else:
        hour = time_utc.time().hour
    return start_hour <= hour < end_hour


def is_entry_window(time_utc, start_hour=11, end_hour=13):
    """Check if current time is within entry window."""
    # Handle both datetime and pandas Timestamp
    if hasattr(time_utc, 'hour'):
        hour = time_utc.hour
    else:
        hour = time_utc.time().hour
    return start_hour <= hour < end_hour


def is_orb_window(time_utc, start_hour=11, end_hour=12):
    """Check if current time is within ORB calculation window."""
    # Handle both datetime and pandas Timestamp
    if hasattr(time_utc, 'hour'):
        hour = time_utc.hour
    else:
        hour = time_utc.time().hour
    return start_hour <= hour < end_hour


def rsi(data, period=14, price_col='close'):
    """Calculate Relative Strength Index."""
    delta = data[price_col].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def bollinger_bands(data, period=20, std_dev=2, price_col='close'):
    """Calculate Bollinger Bands."""
    sma = data[price_col].rolling(window=period).mean()
    std = data[price_col].rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return upper_band, sma, lower_band


def heikin_ashi(data):
    """Calculate Heikin Ashi candlesticks."""
    ha_close = (data['open'] + data['high'] + data['low'] + data['close']) / 4
    ha_open = pd.Series(index=data.index, dtype=float)
    ha_open.iloc[0] = (data['open'].iloc[0] + data['close'].iloc[0]) / 2
    
    for i in range(1, len(data)):
        ha_open.iloc[i] = (ha_open.iloc[i-1] + ha_close.iloc[i-1]) / 2
    
    ha_high = np.maximum(data['high'], np.maximum(ha_open, ha_close))
    ha_low = np.minimum(data['low'], np.minimum(ha_open, ha_close))
    
    return pd.DataFrame({
        'ha_open': ha_open,
        'ha_high': ha_high,
        'ha_low': ha_low,
        'ha_close': ha_close
    }, index=data.index)


def macd(data, fast=12, slow=26, signal=9, price_col='close'):
    """Calculate MACD (Moving Average Convergence Divergence)."""
    ema_fast = ema(data, fast, price_col)
    ema_slow = ema(data, slow, price_col)
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram
