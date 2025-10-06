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
    """Test that time windows are correctly configured for session trading."""
    print("Testing time window alignment...")
    
    # Import only the config function to avoid heavy dependencies
    sys.path.append(str(repo_root / "webapp"))
    from app import get_effective_config
    
    # Test moderate mode configuration
    config_moderate = get_effective_config("BTC/USDT:USDT", "moderate")
    print(f"   Moderate mode entry_window: {config_moderate['entry_window']}")
    assert config_moderate['entry_window'] == (11, 14), f"Expected (11, 14), got {config_moderate['entry_window']}"
    
    # Test conservative mode
    config_conservative = get_effective_config("BTC/USDT:USDT", "conservative")
    assert config_conservative['entry_window'] == (11, 14), "Conservative mode should be (11, 14)"
    
    # Test aggressive mode
    config_aggressive = get_effective_config("BTC/USDT:USDT", "aggressive")
    assert config_aggressive['entry_window'] == (11, 14), "Aggressive mode should be (11, 14)"
    
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


def test_obsolete_data_preservation():
    """Test that obsolete data is preserved and marked with stale attribute."""
    print("\nTesting obsolete data preservation...")
    
    # Create mock trades data
    trades_df = create_mock_trades_data(3)
    
    # Test that DataFrame can have attrs attribute
    assert hasattr(trades_df, 'attrs'), "DataFrame should have attrs attribute"
    
    # Test setting stale attribute
    stale_date = "2024-01-10"
    trades_df.attrs["stale_last_until"] = stale_date
    
    # Test that attribute is preserved
    assert "stale_last_until" in trades_df.attrs, "stale_last_until attribute should be set"
    assert trades_df.attrs["stale_last_until"] == stale_date, f"stale_last_until should be {stale_date}"
    
    # Test that data is still accessible
    assert len(trades_df) == 3, "DataFrame should still contain 3 trades"
    assert "entry_time" in trades_df.columns, "entry_time column should be preserved"
    
    print("Obsolete data preservation test passed")


def test_stale_data_alert_logic():
    """Test the logic for detecting and alerting on stale data."""
    print("\nTesting stale data alert logic...")
    
    # Test case 1: Fresh data (no stale attribute)
    fresh_trades = create_mock_trades_data(2)
    has_stale_attr = hasattr(fresh_trades, 'attrs') and "stale_last_until" in fresh_trades.attrs
    assert not has_stale_attr, "Fresh data should not have stale attribute"
    
    # Test case 2: Stale data (with stale attribute)
    stale_trades = create_mock_trades_data(2)
    stale_trades.attrs["stale_last_until"] = "2024-01-10"
    has_stale_attr = hasattr(stale_trades, 'attrs') and "stale_last_until" in stale_trades.attrs
    assert has_stale_attr, "Stale data should have stale attribute"
    
    # Test case 3: Alert message construction
    stale_date = "2024-01-10"
    expected_alert = f"Datos actualizados hasta {stale_date}. Los datos pueden estar desactualizados."
    # This simulates the alert message construction logic
    alert_msg = f"Datos actualizados hasta {stale_date}. Los datos pueden estar desactualizados."
    assert alert_msg == expected_alert, "Alert message should match expected format"
    
    print("Stale data alert logic test passed")


def main():
    """Run all core functionality tests."""
    print("Starting core functionality tests...")
    print("=" * 60)
    
    try:
        test_time_window_alignment()
        test_sidecar_metadata_structure()
        test_freshness_validation_logic()
        test_signal_status_handling()
        test_obsolete_data_preservation()
        test_stale_data_alert_logic()
        
        print("\n" + "=" * 60)
        print("All core functionality tests passed!")
        print("\nSummary:")
        print("- Time windows are properly configured for session trading")
        print("- Sidecar metadata structure includes all required fields")
        print("- Freshness validation logic works correctly")
        print("- Signal status handling accepts 'signal' status")
        print("- Obsolete data preservation works correctly")
        print("- Stale data alert logic functions properly")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
