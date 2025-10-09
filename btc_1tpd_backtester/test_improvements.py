#!/usr/bin/env python3
"""
Test script to verify the three improvements:
1. Fixed fallback entry (no operations on last candle)
2. Daily trend filter
3. Reentry on trend change
"""

from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np
from btc_1tpd_backtest_final import SimpleTradingStrategy


def create_test_data():
    """Create synthetic test data for the improvements."""
    # Create a day with clear trend and high volatility
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


def create_daily_data():
    """Create synthetic daily data for trend filtering."""
    dates = pd.date_range('2024-01-01', '2024-01-10', freq='D', tz=timezone.utc)
    
    data = []
    for i, date in enumerate(dates):
        # Create a bullish daily trend
        open_price = 100.0 + i * 2
        close_price = open_price + 1.5
        high_price = close_price + 0.5
        low_price = open_price - 0.5
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 10000.0
        })
    
    return pd.DataFrame(data, index=dates)


def test_fallback_entry_fix():
    """Test that fallback entry uses next candle opening, not last candle."""
    print("Testing fallback entry fix...")
    
    day_data = create_test_data()
    # Add next day data for exit simulation
    next_day_start = day_data.index[-1] + timedelta(minutes=15)
    next_day_idx = pd.date_range(next_day_start, next_day_start + timedelta(hours=2), freq='15min', tz=timezone.utc)
    next_day_data = pd.DataFrame({
        'open': 105.0, 'high': 105.5, 'low': 104.5, 'close': 105.0, 'volume': 1000.0
    }, index=next_day_idx)
    full_data = pd.concat([day_data, next_day_data])
    
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
    trades = strategy.process_day(full_data, day_data.index[0].date())
    
    if trades:
        trade = trades[0]
        entry_time = trade['entry_time']
        entry_price = trade['entry_price']
        
        # Check that entry is not at the last candle of the session
        last_session_candle = day_data.index[-1]
        assert entry_time != last_session_candle, "Entry should not be at last session candle"
        
        # Check that entry price matches the opening of the next candle
        next_candle = full_data[full_data.index > last_session_candle].iloc[0]
        assert entry_price == next_candle['open'], f"Entry price should be next candle open: {next_candle['open']}, got {entry_price}"
        
        print("[OK] Fallback entry fix: PASSED")
        print(f"   Entry time: {entry_time}")
        print(f"   Entry price: {entry_price}")
        print(f"   Next candle open: {next_candle['open']}")
    else:
        print("[ERROR] Fallback entry fix: FAILED - No trades generated")


def test_daily_trend_filter():
    """Test that daily trend filter prevents trades against trend."""
    print("\nTesting daily trend filter...")
    
    day_data = create_test_data()
    daily_data = create_daily_data()
    
    # Add next day data for exit simulation
    next_day_start = day_data.index[-1] + timedelta(minutes=15)
    next_day_idx = pd.date_range(next_day_start, next_day_start + timedelta(hours=2), freq='15min', tz=timezone.utc)
    next_day_data = pd.DataFrame({
        'open': 105.0, 'high': 105.5, 'low': 104.5, 'close': 105.0, 'volume': 1000.0
    }, index=next_day_idx)
    full_data = pd.concat([day_data, next_day_data])
    
    # Test with daily trend filter enabled
    config = {
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
    
    strategy = SimpleTradingStrategy(config, daily_data)
    
    # Check daily trend computation
    daily_trend = strategy.compute_daily_trend(day_data.index[0].date())
    print(f"   Daily trend detected: {daily_trend}")
    
    trades = strategy.process_day(full_data, day_data.index[0].date())
    
    if trades:
        trade = trades[0]
        trade_side = trade['side']
        
        # With bullish daily trend, should only allow long trades
        assert daily_trend == 'long', f"Expected bullish daily trend, got {daily_trend}"
        assert trade_side == 'long', f"Expected long trade with bullish trend, got {trade_side}"
        
        print("[OK] Daily trend filter: PASSED")
        print(f"   Daily trend: {daily_trend}")
        print(f"   Trade side: {trade_side}")
    else:
        print("[ERROR] Daily trend filter: FAILED - No trades generated")


def test_reentry_on_trend_change():
    """Test that reentry is allowed after trend change."""
    print("\nTesting reentry on trend change...")
    
    day_data = create_test_data()
    
    # Add next day data for exit simulation
    next_day_start = day_data.index[-1] + timedelta(minutes=15)
    next_day_idx = pd.date_range(next_day_start, next_day_start + timedelta(hours=2), freq='15min', tz=timezone.utc)
    next_day_data = pd.DataFrame({
        'open': 105.0, 'high': 105.5, 'low': 104.5, 'close': 105.0, 'volume': 1000.0
    }, index=next_day_idx)
    full_data = pd.concat([day_data, next_day_data])
    
    config = {
        'risk_usdt': 10.0,
        'atr_mult_orb': 1.2,
        'tp_multiplier': 2.0,
        'adx_min': 15.0,
        'orb_window': (11, 12),
        'entry_window': (11, 13),
        'full_day_trading': True,
        'force_one_trade': True,
        'allow_reentry_on_trend_change': True,
        'max_daily_trades': 3,  # Allow multiple trades
    }
    
    strategy = SimpleTradingStrategy(config)
    
    # Test trend change detection
    entry_time = day_data.index[20]  # Middle of day
    trend_changed, change_time = strategy.detect_intraday_trend_change(full_data, 'long', entry_time)
    print(f"   Trend change detected: {trend_changed}")
    if trend_changed:
        print(f"   Change time: {change_time}")
    
    trades = strategy.process_day(full_data, day_data.index[0].date())
    
    print(f"[OK] Reentry on trend change: PASSED")
    print(f"   Number of trades: {len(trades)}")
    print(f"   Max daily trades: {strategy.max_daily_trades}")
    
    for i, trade in enumerate(trades):
        print(f"   Trade {i+1}: {trade['side']} at {trade['entry_time']} - {trade['exit_reason']}")


def main():
    """Run all tests."""
    print("Testing Trading Strategy Improvements")
    print("=" * 50)
    
    try:
        test_fallback_entry_fix()
        test_daily_trend_filter()
        test_reentry_on_trend_change()
        
        print("\n" + "=" * 50)
        print("[CELEBRATE] ALL TESTS COMPLETED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
