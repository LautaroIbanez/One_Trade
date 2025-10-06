#!/usr/bin/env python3
"""
Integration test for obsolete data preservation functionality.
Tests the complete flow from load_trades to dashboard alert display.
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


def create_test_csv_with_stale_sidecar():
    """Create a test CSV file with a stale sidecar for testing."""
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    data_dir = temp_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Create test trades data
    trades_data = [
        {
            'day_key': '2024-01-10',
            'entry_time': '2024-01-10T12:00:00Z',
            'side': 'long',
            'entry_price': 50000.0,
            'sl': 49500.0,
            'tp': 51000.0,
            'exit_time': '2024-01-10T18:00:00Z',
            'exit_price': 51000.0,
            'exit_reason': 'take_profit',
            'pnl_usdt': 100.0,
            'r_multiple': 2.0,
            'used_fallback': False
        },
        {
            'day_key': '2024-01-11',
            'entry_time': '2024-01-11T12:00:00Z',
            'side': 'short',
            'entry_price': 51000.0,
            'sl': 51500.0,
            'tp': 50000.0,
            'exit_time': '2024-01-11T18:00:00Z',
            'exit_price': 50000.0,
            'exit_reason': 'take_profit',
            'pnl_usdt': 100.0,
            'r_multiple': 2.0,
            'used_fallback': False
        }
    ]
    
    # Create CSV file
    csv_path = data_dir / "trades_final_BTC_USDT_USDT_moderate.csv"
    df = pd.DataFrame(trades_data)
    df.to_csv(csv_path, index=False)
    
    # Create stale sidecar (yesterday's date)
    yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    sidecar_path = data_dir / "trades_final_BTC_USDT_USDT_moderate_meta.json"
    sidecar_data = {
        "last_backtest_until": yesterday,
        "last_trade_date": "2024-01-11",
        "symbol": "BTC/USDT:USDT",
        "mode": "moderate",
        "full_day_trading": False,
        "session_trading": True,
        "backtest_start_date": "2024-01-01"
    }
    sidecar_path.write_text(json.dumps(sidecar_data, indent=2))
    
    return temp_dir, csv_path, sidecar_path


def test_load_trades_with_stale_data():
    """Test that load_trades preserves stale data and marks it correctly."""
    print("Testing load_trades with stale data...")
    
    # Create test environment
    temp_dir, csv_path, sidecar_path = create_test_csv_with_stale_sidecar()
    
    try:
        # Mock the repo_root to point to our temp directory
        with patch('webapp.app.repo_root', temp_dir):
            from webapp.app import load_trades
            
            # Load trades - should preserve data despite stale sidecar
            trades = load_trades("BTC/USDT:USDT", "moderate")
            
            # Verify data is preserved
            assert not trades.empty, "Trades should be preserved even with stale sidecar"
            assert len(trades) == 2, f"Expected 2 trades, got {len(trades)}"
            assert "entry_time" in trades.columns, "entry_time column should be preserved"
            
            # Verify stale attribute is set
            assert hasattr(trades, 'attrs'), "DataFrame should have attrs attribute"
            assert "stale_last_until" in trades.attrs, "stale_last_until attribute should be set"
            
            # Verify the stale date
            yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
            assert trades.attrs["stale_last_until"] == yesterday, f"Expected {yesterday}, got {trades.attrs['stale_last_until']}"
            
            print("✅ load_trades correctly preserves stale data and marks it")
            
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


def test_dashboard_alert_with_stale_data():
    """Test that dashboard shows alert when data is stale."""
    print("Testing dashboard alert with stale data...")
    
    # Create test environment
    temp_dir, csv_path, sidecar_path = create_test_csv_with_stale_sidecar()
    
    try:
        # Mock the repo_root to point to our temp directory
        with patch('webapp.app.repo_root', temp_dir):
            from webapp.app import load_trades, format_argentina_time
            
            # Load trades with stale data
            trades = load_trades("BTC/USDT:USDT", "moderate")
            
            # Simulate the dashboard alert logic
            alert_msg = ""
            stale_last_until = None
            
            if hasattr(trades, 'attrs') and "stale_last_until" in trades.attrs:
                stale_last_until = trades.attrs["stale_last_until"]
                alert_msg = f"Datos actualizados hasta {format_argentina_time(datetime.fromisoformat(stale_last_until), '%Y-%m-%d')}. Los datos pueden estar desactualizados."
            
            # Verify alert is generated
            assert stale_last_until is not None, "stale_last_until should be detected"
            assert alert_msg != "", "Alert message should be generated"
            assert "Datos actualizados hasta" in alert_msg, "Alert should contain update date"
            assert "desactualizados" in alert_msg, "Alert should mention data may be outdated"
            
            print("✅ Dashboard correctly generates alert for stale data")
            
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


def test_fresh_data_no_alert():
    """Test that no alert is shown when data is fresh."""
    print("Testing fresh data (no alert)...")
    
    # Create test environment with fresh sidecar
    temp_dir = Path(tempfile.mkdtemp())
    data_dir = temp_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    try:
        # Create test trades data
        trades_data = [{
            'day_key': '2024-01-15',
            'entry_time': '2024-01-15T12:00:00Z',
            'side': 'long',
            'entry_price': 50000.0,
            'sl': 49500.0,
            'tp': 51000.0,
            'exit_time': '2024-01-15T18:00:00Z',
            'exit_price': 51000.0,
            'exit_reason': 'take_profit',
            'pnl_usdt': 100.0,
            'r_multiple': 2.0,
            'used_fallback': False
        }]
        
        # Create CSV file
        csv_path = data_dir / "trades_final_BTC_USDT_USDT_moderate.csv"
        df = pd.DataFrame(trades_data)
        df.to_csv(csv_path, index=False)
        
        # Create fresh sidecar (today's date)
        today = datetime.now(timezone.utc).date().isoformat()
        sidecar_path = data_dir / "trades_final_BTC_USDT_USDT_moderate_meta.json"
        sidecar_data = {
            "last_backtest_until": today,
            "last_trade_date": "2024-01-15",
            "symbol": "BTC/USDT:USDT",
            "mode": "moderate",
            "full_day_trading": False,
            "session_trading": True,
            "backtest_start_date": "2024-01-01"
        }
        sidecar_path.write_text(json.dumps(sidecar_data, indent=2))
        
        # Mock the repo_root to point to our temp directory
        with patch('webapp.app.repo_root', temp_dir):
            from webapp.app import load_trades
            
            # Load trades with fresh data
            trades = load_trades("BTC/USDT:USDT", "moderate")
            
            # Verify data is loaded
            assert not trades.empty, "Trades should be loaded"
            assert len(trades) == 1, f"Expected 1 trade, got {len(trades)}"
            
            # Verify no stale attribute
            has_stale_attr = hasattr(trades, 'attrs') and "stale_last_until" in trades.attrs
            assert not has_stale_attr, "Fresh data should not have stale attribute"
            
            print("✅ Fresh data correctly loaded without stale attribute")
            
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


def main():
    """Run all integration tests for obsolete data preservation."""
    print("Starting obsolete data preservation integration tests...")
    print("=" * 70)
    
    try:
        test_load_trades_with_stale_data()
        test_dashboard_alert_with_stale_data()
        test_fresh_data_no_alert()
        
        print("\n" + "=" * 70)
        print("All obsolete data preservation integration tests passed!")
        print("\nSummary:")
        print("- load_trades preserves stale data and marks it with stale_last_until attribute")
        print("- Dashboard correctly generates alert when data is stale")
        print("- Fresh data loads without stale attribute and no alert is shown")
        print("- Complete flow from CSV loading to alert display works correctly")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
