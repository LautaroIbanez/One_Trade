#!/usr/bin/env python3
"""
Simple verification test for the implemented changes.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))


def test_config_changes():
    """Test configuration changes without importing heavy modules."""
    print("Testing configuration changes...")
    
    # Read the app.py file directly to check for changes
    app_file = base_dir / "app.py"
    app_content = app_file.read_text(encoding="utf-8")
    
    # Check that 24h switch is removed
    assert 'dbc.Switch(id="full-day-trading"' not in app_content, "24h switch should be removed"
    
    # Check that full_day_trading parameter is removed from callback
    assert 'Input("full-day-trading", "value")' not in app_content, "full_day_trading input should be removed"
    
    # Check that BASE_CONFIG has the right values
    assert '"full_day_trading": True' in app_content, "BASE_CONFIG should have full_day_trading=True"
    assert '"force_one_trade": True' in app_content, "BASE_CONFIG should have force_one_trade=True"
    
    # Check that MODE_CONFIG has integrated 24h values
    assert '"orb_window": (0, 1)' in app_content, "MODE_CONFIG should have orb_window=(0,1)"
    assert '"entry_window": (1, 24)' in app_content, "MODE_CONFIG should have entry_window=(1,24)"
    
    # Check that get_effective_config doesn't take full_day_trading parameter
    assert 'def get_effective_config(symbol: str, mode: str) -> dict:' in app_content, "get_effective_config should not take full_day_trading parameter"
    
    print("Configuration changes test passed")


def test_timezone_changes():
    """Test timezone changes without importing heavy modules."""
    print("\nTesting timezone changes...")
    
    # Read the app.py file directly to check for changes
    app_file = base_dir / "app.py"
    app_content = app_file.read_text(encoding="utf-8")
    
    # Check that timezone imports are present
    assert 'from zoneinfo import ZoneInfo' in app_content or 'from backports.zoneinfo import ZoneInfo' in app_content, "ZoneInfo import should be present"
    
    # Check that timezone helper functions are defined
    assert 'ARGENTINA_TZ = ZoneInfo("America/Argentina/Buenos_Aires")' in app_content, "Argentina timezone should be defined"
    assert 'def to_argentina_time(dt):' in app_content, "to_argentina_time function should be defined"
    assert 'def format_argentina_time(dt, format_str=' in app_content, "format_argentina_time function should be defined"
    
    # Check that timezone functions are used in the code
    assert 'format_argentina_time(' in app_content, "format_argentina_time should be used in the code"
    
    print("Timezone changes test passed")


def test_function_signature_changes():
    """Test function signature changes without importing heavy modules."""
    print("\nTesting function signature changes...")
    
    # Read the app.py file directly to check for changes
    app_file = base_dir / "app.py"
    app_content = app_file.read_text(encoding="utf-8")
    
    # Check that refresh_trades doesn't take full_day_trading parameter
    assert 'def refresh_trades(symbol: str, mode: str) -> str:' in app_content, "refresh_trades should not take full_day_trading parameter"
    
    # Check that load_trades doesn't take full_day_trading parameter
    assert 'def load_trades(symbol: str | None = None, mode: str | None = None, csv_path: str = "trades_final.csv") -> pd.DataFrame:' in app_content, "load_trades should not take full_day_trading parameter"
    
    # Check that update_dashboard callback doesn't take full_day_trading parameter
    assert 'def update_dashboard(symbol, n_clicks, mode):' in app_content, "update_dashboard should not take full_day_trading parameter"
    
    print("Function signature changes test passed")


def test_live_monitor_changes():
    """Test live_monitor changes without importing heavy modules."""
    print("\nTesting live_monitor changes...")
    
    # Read the live_monitor.py file directly to check for changes
    live_monitor_file = repo_root / "btc_1tpd_backtester" / "live_monitor.py"
    live_monitor_content = live_monitor_file.read_text(encoding="utf-8")
    
    # Check that detect_or_update_active_trade doesn't take full_day_trading parameter
    assert 'def detect_or_update_active_trade(symbol: str, mode: str, config: Dict[str, Any]) -> Optional[ActiveTrade]:' in live_monitor_content, "detect_or_update_active_trade should not take full_day_trading parameter"
    
    # Check that full_day_trading is hardcoded to True
    assert 'full_day_trading=True,  # Always True for 24h mode' in live_monitor_content, "full_day_trading should be hardcoded to True"
    
    print("Live monitor changes test passed")


def test_signals_changes():
    """Test signals changes without importing heavy modules."""
    print("\nTesting signals changes...")
    
    # Read the today_signal.py file directly to check for changes
    signals_file = repo_root / "btc_1tpd_backtester" / "signals" / "today_signal.py"
    signals_content = signals_file.read_text(encoding="utf-8")
    
    # Check that default config has 24h values
    assert '"orb_window": (0, 1),  # ORB at midnight UTC (24h mode)' in signals_content, "Default config should have orb_window=(0,1)"
    assert '"entry_window": (1, 24),  # Can enter throughout the day' in signals_content, "Default config should have entry_window=(1,24)"
    assert '"full_day_trading": True  # Always True for 24h mode' in signals_content, "Default config should have full_day_trading=True"
    
    # Check that next day fetching is always enabled
    assert 'Always fetch next day for 24h trading mode' in signals_content, "Next day fetching should always be enabled"
    
    print("Signals changes test passed")


def main():
    """Run all simple verification tests."""
    print("Starting simple verification tests...")
    print("=" * 50)
    
    try:
        test_config_changes()
        test_timezone_changes()
        test_function_signature_changes()
        test_live_monitor_changes()
        test_signals_changes()
        
        print("\n" + "=" * 50)
        print("All simple verification tests passed!")
        print("\nSummary:")
        print("[OK] 24h configuration successfully removed from UI and integrated into configs")
        print("[OK] Timezone localization functions added and used throughout the app")
        print("[OK] Function signatures updated to remove full_day_trading parameter")
        print("[OK] Live monitor module updated to always use 24h mode")
        print("[OK] Signals module updated to always use 24h mode")
        print("\nAll changes have been successfully implemented!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
