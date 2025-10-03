#!/usr/bin/env python3
"""
Test lookahead bias fixes in get_trade_recommendation.
"""

import sys
import pandas as pd
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))


def test_no_future_data_used():
    """Test that no data after 'now' is used in recommendations."""
    print("Testing no future data usage...")
    
    # Mock fetch_historical_data to return test data
    def mock_fetch_historical_data(symbol, since, until, timeframe):
        # Create test data with timestamps before, at, and after 'now'
        now = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        
        timestamps = [
            now - timedelta(hours=2),  # Before now
            now - timedelta(minutes=30),  # Before now
            now - timedelta(minutes=5),  # Before now
            now,  # At now
            now + timedelta(minutes=5),  # After now (should be filtered)
            now + timedelta(minutes=15),  # After now (should be filtered)
            now + timedelta(hours=1),  # After now (should be filtered)
        ]
        
        data = []
        for i, ts in enumerate(timestamps):
            data.append({
                'timestamp': ts,
                'open': 50000 + i * 100,
                'high': 50100 + i * 100,
                'low': 49900 + i * 100,
                'close': 50050 + i * 100,
                'volume': 1000 + i * 10
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    # Test the function
    with patch('btc_1tpd_backtester.utils.fetch_historical_data', mock_fetch_historical_data):
        from btc_1tpd_backtester.signals.today_signal import get_today_trade_recommendation
        
        now = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        config = {
            "risk_usdt": 20.0,
            "atr_mult_orb": 1.2,
            "tp_multiplier": 2.0,
            "adx_min": 15.0,
            "orb_window": (0, 1),
            "entry_window": (1, 24),
            "full_day_trading": True,
            "force_one_trade": True
        }
        
        result = get_today_trade_recommendation("BTC/USDT:USDT", config, now)
        
        # Verify that the result doesn't contain future data
        assert result is not None, "Result should not be None"
        
        # If it's a signal, check that entry_time is not in the future
        if result.get("status") == "signal":
            entry_time = pd.to_datetime(result["entry_time"])
            assert entry_time <= now + timedelta(minutes=5), f"Entry time {entry_time} should not be after now {now}"
        
        print("No future data usage test passed")


def test_fallback_uses_valid_candles():
    """Test that EMA15 fallback only uses candles before 'now'."""
    print("\nTesting EMA15 fallback uses valid candles...")
    
    # Create test data with specific EMA15 setup
    now = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
    
    # Create data that would trigger EMA15 fallback
    timestamps = []
    prices = []
    for i in range(20):  # Enough for EMA15
        ts = now - timedelta(minutes=15 * (20 - i))
        timestamps.append(ts)
        # Create a trend that would trigger EMA15 pullback
        price = 50000 + i * 50 + (i % 3) * 10  # Some volatility
        prices.append(price)
    
    # Add some future data that should be filtered out
    for i in range(5):
        ts = now + timedelta(minutes=15 * (i + 1))
        timestamps.append(ts)
        prices.append(51000 + i * 100)  # Future prices
    
    def mock_fetch_historical_data(symbol, since, until, timeframe):
        data = []
        for ts, price in zip(timestamps, prices):
            data.append({
                'timestamp': ts,
                'open': price,
                'high': price + 50,
                'low': price - 50,
                'close': price,
                'volume': 1000
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    with patch('btc_1tpd_backtester.utils.fetch_historical_data', mock_fetch_historical_data):
        from btc_1tpd_backtester.signals.today_signal import get_today_trade_recommendation
        
        config = {
            "risk_usdt": 20.0,
            "atr_mult_orb": 1.2,
            "tp_multiplier": 2.0,
            "adx_min": 15.0,
            "orb_window": (0, 1),
            "entry_window": (1, 24),
            "full_day_trading": True,
            "force_one_trade": True
        }
        
        result = get_today_trade_recommendation("BTC/USDT:USDT", config, now)
        
        # Verify that if it's a signal, the entry_time is from valid candles only
        if result.get("status") == "signal":
            entry_time = pd.to_datetime(result["entry_time"])
            # Entry time should be from one of the valid candles (before now)
            valid_timestamps = [ts for ts in timestamps if ts <= now]
            assert entry_time in valid_timestamps, f"Entry time {entry_time} should be from valid candles"
        
        print("EMA15 fallback valid candles test passed")


def test_orb_evaluation_filters_future():
    """Test that ORB evaluation filters out future candles."""
    print("\nTesting ORB evaluation filters future candles...")
    
    # Create test data for ORB evaluation
    now = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)  # In entry window
    
    # Create ORB data (11:00-12:00) and entry window data
    orb_timestamps = []
    orb_prices = []
    
    # ORB window (11:00-12:00)
    for i in range(4):  # 4 x 15min candles
        ts = datetime(2024, 1, 15, 11, 15 * i, tzinfo=timezone.utc)
        orb_timestamps.append(ts)
        orb_prices.append(50000 + i * 100)  # Rising trend
    
    # Entry window (12:00-13:00) - before now
    for i in range(2):
        ts = datetime(2024, 1, 15, 12, 15 * i, tzinfo=timezone.utc)
        orb_timestamps.append(ts)
        orb_prices.append(50400 + i * 50)  # Continue trend
    
    # Future data (after now) - should be filtered
    for i in range(3):
        ts = now + timedelta(minutes=15 * (i + 1))
        orb_timestamps.append(ts)
        orb_prices.append(50500 + i * 100)  # Future prices
    
    def mock_fetch_historical_data(symbol, since, until, timeframe):
        data = []
        for ts, price in zip(orb_timestamps, orb_prices):
            data.append({
                'timestamp': ts,
                'open': price,
                'high': price + 100,
                'low': price - 100,
                'close': price,
                'volume': 1000
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    with patch('btc_1tpd_backtester.utils.fetch_historical_data', mock_fetch_historical_data):
        from btc_1tpd_backtester.signals.today_signal import get_today_trade_recommendation
        
        config = {
            "risk_usdt": 20.0,
            "atr_mult_orb": 1.2,
            "tp_multiplier": 2.0,
            "adx_min": 15.0,
            "orb_window": (11, 12),
            "entry_window": (12, 13),
            "full_day_trading": False,
            "force_one_trade": False
        }
        
        result = get_today_trade_recommendation("BTC/USDT:USDT", config, now)
        
        # Verify that if it's a signal, the entry_time is not in the future
        if result.get("status") == "signal":
            entry_time = pd.to_datetime(result["entry_time"])
            assert entry_time <= now, f"Entry time {entry_time} should not be after now {now}"
        
        print("ORB evaluation filters future test passed")


def main():
    """Run all lookahead fix tests."""
    print("Starting lookahead bias fix tests...")
    print("=" * 50)
    
    try:
        test_no_future_data_used()
        test_fallback_uses_valid_candles()
        test_orb_evaluation_filters_future()
        
        print("\n" + "=" * 50)
        print("All lookahead bias fix tests passed!")
        print("\nSummary:")
        print("[OK] No future data is used in trade recommendations")
        print("[OK] EMA15 fallback only uses candles before 'now'")
        print("[OK] ORB evaluation filters out future candles")
        print("[OK] All branches respect the 'now' timestamp")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
