#!/usr/bin/env python3
"""
Manual test for fallback improvements without matplotlib dependencies.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

# Add the btc_1tpd_backtester directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'btc_1tpd_backtester'))

# Import the strategy class directly
import btc_1tpd_backtest_final
from btc_1tpd_backtest_final import SimpleTradingStrategy


def make_bullish_session(date: datetime) -> pd.DataFrame:
    """Create a synthetic bullish session with clear uptrend."""
    tz = timezone.utc
    start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
    end = start + timedelta(days=1)
    idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=tz)
    
    # Create bullish trend: price starts at 100 and ends at 110
    base_price = 100.0
    price_increase = np.linspace(0, 10, len(idx))
    
    # Add some volatility with higher range in middle of day
    volatility = np.sin(np.linspace(0, 4*np.pi, len(idx))) * 2
    
    data = []
    for i, (timestamp, price_inc, vol) in enumerate(zip(idx, price_increase, volatility)):
        open_price = base_price + price_inc
        high_price = open_price + abs(vol) + 1  # Higher volatility in middle
        low_price = open_price - abs(vol) - 0.5
        close_price = open_price + vol * 0.3  # Slight upward bias
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 1000.0
        })
    
    return pd.DataFrame(data, index=idx)


def make_bearish_session(date: datetime) -> pd.DataFrame:
    """Create a synthetic bearish session with clear downtrend."""
    tz = timezone.utc
    start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
    end = start + timedelta(days=1)
    idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=tz)
    
    # Create bearish trend: price starts at 110 and ends at 100
    base_price = 110.0
    price_decrease = np.linspace(0, -10, len(idx))
    
    # Add some volatility with higher range in middle of day
    volatility = np.sin(np.linspace(0, 4*np.pi, len(idx))) * 2
    
    data = []
    for i, (timestamp, price_dec, vol) in enumerate(zip(idx, price_decrease, volatility)):
        open_price = base_price + price_dec
        high_price = open_price + abs(vol) + 0.5
        low_price = open_price - abs(vol) - 1  # Higher volatility in middle
        close_price = open_price - abs(vol) * 0.3  # Slight downward bias
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 1000.0
        })
    
    return pd.DataFrame(data, index=idx)


def make_high_range_session(date: datetime) -> pd.DataFrame:
    """Create a session with one candle having significantly higher range."""
    tz = timezone.utc
    start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
    end = start + timedelta(days=1)
    idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=tz)
    
    data = []
    for i, timestamp in enumerate(idx):
        if i == 20:  # Middle of day - create high range candle
            open_price = 100.0
            high_price = 105.0  # 5% range
            low_price = 95.0
            close_price = 102.0
        else:
            open_price = 100.0
            high_price = 100.5  # Small range
            low_price = 99.5
            close_price = 100.0
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 1000.0
        })
    
    return pd.DataFrame(data, index=idx)


def test_fallback_improvements():
    """Test the fallback improvements."""
    print("Testing Fallback Improvements")
    print("=" * 50)
    
    config = {
        'risk_usdt': 10.0,
        'atr_mult_orb': 1.2,
        'tp_multiplier': 2.0,
        'adx_min': 15.0,
        'orb_window': (11, 12),
        'entry_window': (11, 13),
        'full_day_trading': True,
        'force_one_trade': True,
    }
    
    strategy = SimpleTradingStrategy(config)
    date = datetime(2024, 1, 3, tzinfo=timezone.utc)
    
    # Test 1: Direction detection for bullish session
    print("\n1. Testing direction detection for bullish session...")
    bullish_session = make_bullish_session(date)
    detected_direction = strategy.detect_fallback_direction(bullish_session)
    print(f"   Bullish session detected direction: {detected_direction}")
    assert detected_direction == 'long', f"Expected 'long', got '{detected_direction}'"
    print("   ✅ PASSED")
    
    # Test 2: Direction detection for bearish session
    print("\n2. Testing direction detection for bearish session...")
    bearish_session = make_bearish_session(date)
    detected_direction = strategy.detect_fallback_direction(bearish_session)
    print(f"   Bearish session detected direction: {detected_direction}")
    assert detected_direction == 'short', f"Expected 'short', got '{detected_direction}'"
    print("   ✅ PASSED")
    
    # Test 3: Entry time selection for high range session
    print("\n3. Testing entry time selection for high range session...")
    high_range_session = make_high_range_session(date)
    selected_time = strategy.find_best_fallback_entry_time(high_range_session)
    expected_time = high_range_session.index[20]  # Index 20 has the highest range
    print(f"   Selected time: {selected_time}")
    print(f"   Expected time: {expected_time}")
    assert selected_time == expected_time, f"Expected {expected_time}, got {selected_time}"
    print("   ✅ PASSED")
    
    # Test 4: Full fallback trade with bullish session
    print("\n4. Testing full fallback trade with bullish session...")
    # Add next day data for exit simulation
    next_day_start = date + timedelta(days=1)
    next_day_idx = pd.date_range(next_day_start, next_day_start + timedelta(hours=2), freq='15min', tz=timezone.utc)
    next_day_data = pd.DataFrame({
        'open': 100.0, 'high': 100.5, 'low': 99.5, 'close': 100.0, 'volume': 1000.0
    }, index=next_day_idx)
    day_data = pd.concat([bullish_session, next_day_data])
    
    trades = strategy.process_day(day_data, date.date())
    print(f"   Number of trades created: {len(trades)}")
    assert len(trades) == 1, f"Expected 1 trade, got {len(trades)}"
    
    trade = trades[0]
    print(f"   Trade side: {trade['side']}")
    print(f"   Used fallback: {trade['used_fallback']}")
    print(f"   Entry time: {trade['entry_time']}")
    print(f"   Entry price: {trade['entry_price']}")
    
    assert trade['used_fallback'] == True, "Trade should be marked as fallback"
    assert trade['side'] == 'long', f"Expected 'long' side, got '{trade['side']}'"
    print("   ✅ PASSED")
    
    # Test 5: Full fallback trade with bearish session
    print("\n5. Testing full fallback trade with bearish session...")
    day_data_bearish = pd.concat([bearish_session, next_day_data])
    
    trades_bearish = strategy.process_day(day_data_bearish, date.date())
    print(f"   Number of trades created: {len(trades_bearish)}")
    assert len(trades_bearish) == 1, f"Expected 1 trade, got {len(trades_bearish)}"
    
    trade_bearish = trades_bearish[0]
    print(f"   Trade side: {trade_bearish['side']}")
    print(f"   Used fallback: {trade_bearish['used_fallback']}")
    print(f"   Entry time: {trade_bearish['entry_time']}")
    print(f"   Entry price: {trade_bearish['entry_price']}")
    
    assert trade_bearish['used_fallback'] == True, "Trade should be marked as fallback"
    assert trade_bearish['side'] == 'short', f"Expected 'short' side, got '{trade_bearish['side']}'"
    print("   ✅ PASSED")
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! Fallback improvements are working correctly.")
    print("=" * 50)


if __name__ == '__main__':
    test_fallback_improvements()
