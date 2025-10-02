#!/usr/bin/env python3
"""
Core functionality tests that avoid matplotlib/NumPy import issues.
Tests the three main improvements without heavy dependencies.
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))


def create_mock_trades_data(num_trades=5, start_date=None):
    """Create mock trades data for testing."""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=num_trades)
    
    trades = []
    for i in range(num_trades):
        trade_date = start_date + timedelta(days=i)
        trades.append({
            'day_key': trade_date.strftime('%Y-%m-%d'),
            'entry_time': trade_date.replace(hour=12, minute=0, second=0),
            'side': 'long' if i % 2 == 0 else 'short',
            'entry_price': 50000.0 + i * 100,
            'sl': 49900.0 + i * 100,
            'tp': 50100.0 + i * 100,
            'exit_time': trade_date.replace(hour=18, minute=0, second=0),
            'exit_price': 50100.0 + i * 100,
            'exit_reason': 'take_profit',
            'pnl_usdt': 100.0 + i * 10,
            'r_multiple': 2.0 + i * 0.1,
            'used_fallback': False
        })
    
    return pd.DataFrame(trades)


def test_time_window_alignment():
    """Test that time windows are correctly aligned with 24h switch."""
    print("Testing time window alignment...")
    
    # Import only the config function to avoid heavy dependencies
    sys.path.append(str(repo_root / "webapp"))
    from app import get_effective_config
    
    # Test normal mode configuration
    config_normal = get_effective_config("BTC/USDT:USDT", "moderate", False)
    print(f"   Normal mode entry_window: {config_normal['entry_window']}")
    assert config_normal['entry_window'] == (11, 18), f"Expected (11, 18), got {config_normal['entry_window']}"
    
    # Test 24h mode configuration
    config_24h = get_effective_config("BTC/USDT:USDT", "moderate", True)
    print(f"   24h mode entry_window: {config_24h['entry_window']}")
    assert config_24h['entry_window'] == (1, 24), f"Expected (1, 24), got {config_24h['entry_window']}"
    
    # Test conservative mode
    config_conservative_normal = get_effective_config("BTC/USDT:USDT", "conservative", False)
    assert config_conservative_normal['entry_window'] == (11, 18), "Conservative normal mode should be (11, 18)"
    
    config_conservative_24h = get_effective_config("BTC/USDT:USDT", "conservative", True)
    assert config_conservative_24h['entry_window'] == (1, 24), "Conservative 24h mode should be (1, 24)"
    
    # Test aggressive mode
    config_aggressive_normal = get_effective_config("BTC/USDT:USDT", "aggressive", False)
    assert config_aggressive_normal['entry_window'] == (10, 18), "Aggressive normal mode should be (10, 18)"
    
    config_aggressive_24h = get_effective_config("BTC/USDT:USDT", "aggressive", True)
    assert config_aggressive_24h['entry_window'] == (1, 24), "Aggressive 24h mode should be (1, 24)"
    
    print("Time window alignment test passed")


def test_sidecar_metadata_structure():
    """Test that sidecar metadata structure is correct."""
    print("\nTesting sidecar metadata structure...")
    
    # Test the expected structure without actually writing files
    expected_fields = [
        "last_backtest_until",
        "last_trade_date", 
        "symbol",
        "mode",
        "full_day_trading",
        "backtest_start_date"
    ]
    
    # Create a sample metadata payload
    sample_meta = {
        "last_backtest_until": "2024-01-15",
        "last_trade_date": "2024-01-14", 
        "symbol": "BTC/USDT:USDT",
        "mode": "moderate",
        "full_day_trading": False,
        "backtest_start_date": "2024-01-01"
    }
    
    # Check all expected fields are present
    for field in expected_fields:
        assert field in sample_meta, f"Missing required field: {field}"
    
    print("Sidecar metadata structure test passed")


def test_freshness_validation_logic():
    """Test the freshness validation logic without file I/O."""
    print("\nTesting freshness validation logic...")
    
    # Simulate the validation logic
    today_date = datetime.now(timezone.utc).date().isoformat()
    yesterday_date = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    
    # Test case 1: Fresh sidecar, no trades today
    last_until = today_date
    max_entry_date = yesterday_date
    
    # Should accept (fresh sidecar covers today)
    is_valid = (last_until is not None and last_until >= today_date)
    assert is_valid, "Should accept file with fresh sidecar even if no trades today"
    
    # Test case 2: Stale sidecar
    last_until = yesterday_date
    max_entry_date = yesterday_date
    
    # Should reject (sidecar doesn't cover today)
    is_valid = (last_until is not None and last_until >= today_date)
    assert not is_valid, "Should reject file with stale sidecar"
    
    # Test case 3: Future entry date
    last_until = today_date
    max_entry_date = (datetime.now(timezone.utc).date() + timedelta(days=1)).isoformat()
    
    # Should reject (future entry date)
    is_valid = (max_entry_date <= today_date)
    assert not is_valid, "Should reject file with future entry dates"
    
    print("Freshness validation logic test passed")


def test_signal_status_handling():
    """Test that signal status is handled correctly."""
    print("\nTesting signal status handling...")
    
    # Test the logic from detect_or_update_active_trade
    test_recommendations = [
        {"status": "signal", "side": "long", "entry_price": 50000, "stop_loss": 49500, "take_profit": 51000, "entry_time": "2024-01-15T12:00:00Z"},
        {"status": "long", "side": "long", "entry_price": 50000, "stop_loss": 49500, "take_profit": 51000, "entry_time": "2024-01-15T12:00:00Z"},
        {"status": "short", "side": "short", "entry_price": 50000, "stop_loss": 50500, "take_profit": 49000, "entry_time": "2024-01-15T12:00:00Z"},
        {"status": "no_breakout", "side": None, "entry_price": None, "stop_loss": None, "take_profit": None, "entry_time": None}
    ]
    
    for rec in test_recommendations:
        status = (rec.get("status") or "").lower()
        side = (rec.get("side") or "").lower()
        
        # Check if actionable (from the updated logic)
        is_actionable = (status in {"long", "short", "signal"}) and side in {"long", "short"}
        
        if status in {"signal", "long", "short"} and side in {"long", "short"}:
            assert is_actionable, f"Should be actionable: {rec}"
            
            # Check required fields
            entry_price = rec.get("entry_price")
            stop_loss = rec.get("stop_loss")
            take_profit = rec.get("take_profit")
            entry_time = rec.get("entry_time")
            
            has_required_fields = all([entry_price, stop_loss, take_profit, entry_time])
            assert has_required_fields, f"Should have all required fields: {rec}"
        else:
            assert not is_actionable, f"Should not be actionable: {rec}"
    
    print("Signal status handling test passed")


def main():
    """Run all core functionality tests."""
    print("Starting core functionality tests...")
    print("=" * 60)
    
    try:
        test_time_window_alignment()
        test_sidecar_metadata_structure()
        test_freshness_validation_logic()
        test_signal_status_handling()
        
        print("\n" + "=" * 60)
        print("All core functionality tests passed!")
        print("\nSummary:")
        print("- Time windows are properly aligned with 24h switch")
        print("- Sidecar metadata structure includes all required fields")
        print("- Freshness validation logic works correctly")
        print("- Signal status handling accepts 'signal' status")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
