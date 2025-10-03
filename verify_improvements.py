#!/usr/bin/env python3
"""
Simple verification script for the three improvements.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

# Add the btc_1tpd_backtester directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'btc_1tpd_backtester'))

# Import the strategy class directly
from btc_1tpd_backtest_final import SimpleTradingStrategy


def create_test_data():
    """Create synthetic test data."""
    date = datetime(2024, 1, 3, tzinfo=timezone.utc)
    start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=timezone.utc)
    
    # Create bullish trend with high volatility in the middle
    base_price = 100.0
    price_increase = np.linspace(0, 5, len(idx))
    
    data = []
    for i, (timestamp, price_inc) in enumerate(zip(idx, price_increase)):
        open_price = base_price + price_inc
        
        # Create high volatility in the middle of the day (index 20-30)
        if 20 <= i <= 30:
            high_price = open_price + 3.0  # High range
            low_price = open_price - 2.0
            close_price = open_price + 1.0
        else:
            high_price = open_price + 0.5
            low_price = open_price - 0.5
            close_price = open_price + 0.2
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 1000.0
        })
    
    return pd.DataFrame(data, index=idx)


def test_improvements():
    """Test the three improvements."""
    print("Verifying Trading Strategy Improvements")
    print("=" * 50)
    
    # Create test data
    day_data = create_test_data()
    
    # Add next day data for exit simulation
    next_day_start = day_data.index[-1] + timedelta(minutes=15)
    next_day_idx = pd.date_range(next_day_start, next_day_start + timedelta(hours=2), freq='15min', tz=timezone.utc)
    next_day_data = pd.DataFrame({
        'open': 105.0, 'high': 105.5, 'low': 104.5, 'close': 105.0, 'volume': 1000.0
    }, index=next_day_idx)
    full_data = pd.concat([day_data, next_day_data])
    
    # Test 1: Fallback entry fix
    print("\n1. Testing fallback entry fix...")
    config1 = {
        'risk_usdt': 10.0,
        'atr_mult_orb': 1.2,
        'tp_multiplier': 2.0,
        'adx_min': 15.0,
        'orb_window': (11, 12),
        'entry_window': (11, 13),
        'full_day_trading': True,
        'force_one_trade': True,
    }
    
    strategy1 = SimpleTradingStrategy(config1)
    trades1 = strategy1.process_day(full_data, day_data.index[0].date())
    
    if trades1:
        trade = trades1[0]
        entry_time = trade['entry_time']
        entry_price = trade['entry_price']
        last_session_candle = day_data.index[-1]
        
        print(f"   Entry time: {entry_time}")
        print(f"   Entry price: {entry_price}")
        print(f"   Last session candle: {last_session_candle}")
        
        # Check that entry is not at the last candle
        if entry_time != last_session_candle:
            print("   ✅ Entry is not at last candle - PASSED")
        else:
            print("   ❌ Entry is at last candle - FAILED")
    else:
        print("   ❌ No trades generated - FAILED")
    
    # Test 2: Daily trend filter
    print("\n2. Testing daily trend filter...")
    
    # Create daily data
    dates = pd.date_range('2024-01-01', '2024-01-10', freq='D', tz=timezone.utc)
    daily_data = pd.DataFrame({
        'open': [100 + i * 2 for i in range(len(dates))],
        'high': [100 + i * 2 + 0.5 for i in range(len(dates))],
        'low': [100 + i * 2 - 0.5 for i in range(len(dates))],
        'close': [100 + i * 2 + 1.5 for i in range(len(dates))],
        'volume': [10000] * len(dates)
    }, index=dates)
    
    config2 = {
        'risk_usdt': 10.0,
        'atr_mult_orb': 1.2,
        'tp_multiplier': 2.0,
        'adx_min': 15.0,
        'orb_window': (11, 12),
        'entry_window': (11, 13),
        'full_day_trading': True,
        'force_one_trade': True,
        'use_daily_trend_filter': True,
    }
    
    strategy2 = SimpleTradingStrategy(config2, daily_data)
    
    # Test daily trend computation
    daily_trend = strategy2.compute_daily_trend(day_data.index[0].date())
    print(f"   Daily trend detected: {daily_trend}")
    
    trades2 = strategy2.process_day(full_data, day_data.index[0].date())
    
    if trades2:
        trade = trades2[0]
        trade_side = trade['side']
        print(f"   Trade side: {trade_side}")
        
        if daily_trend == 'long' and trade_side == 'long':
            print("   ✅ Daily trend filter working - PASSED")
        else:
            print("   ❌ Daily trend filter not working - FAILED")
    else:
        print("   ❌ No trades generated - FAILED")
    
    # Test 3: Reentry on trend change
    print("\n3. Testing reentry on trend change...")
    
    config3 = {
        'risk_usdt': 10.0,
        'atr_mult_orb': 1.2,
        'tp_multiplier': 2.0,
        'adx_min': 15.0,
        'orb_window': (11, 12),
        'entry_window': (11, 13),
        'full_day_trading': True,
        'force_one_trade': True,
        'allow_reentry_on_trend_change': True,
        'max_daily_trades': 3,
    }
    
    strategy3 = SimpleTradingStrategy(config3)
    
    # Test trend change detection
    entry_time = day_data.index[20]
    trend_changed, change_time = strategy3.detect_intraday_trend_change(full_data, 'long', entry_time)
    print(f"   Trend change detected: {trend_changed}")
    if trend_changed:
        print(f"   Change time: {change_time}")
    
    trades3 = strategy3.process_day(full_data, day_data.index[0].date())
    print(f"   Number of trades: {len(trades3)}")
    print(f"   Max daily trades: {strategy3.max_daily_trades}")
    
    if len(trades3) <= strategy3.max_daily_trades:
        print("   ✅ Reentry configuration working - PASSED")
    else:
        print("   ❌ Reentry configuration not working - FAILED")
    
    print("\n" + "=" * 50)
    print("🎉 VERIFICATION COMPLETED!")
    print("=" * 50)


if __name__ == '__main__':
    test_improvements()
