#!/usr/bin/env python3
"""
Regression tests for history preservation and time window alignment.
Tests the three main improvements:
1. Avoid history deletion when no trades occurred
2. Show daily recommendations in dashboard
3. Align time windows with 24h switch
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

from webapp.app import refresh_trades, load_trades, get_effective_config


def create_mock_trades_data(num_trades=5, start_date=None, last_trade_date=None):
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


def test_history_preservation_no_trades():
    """Test that history is preserved when no trades occurred but sidecar is fresh."""
    print("Testing history preservation when no trades occurred...")
    
    symbol = "BTC/USDT:USDT"
    mode = "moderate"
    full_day_trading = False
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Override the data directory for testing
        import webapp.app
        original_repo_root = webapp.app.repo_root
        webapp.app.repo_root = Path(temp_dir)
        
        try:
            # Create test data directory
            test_data_dir = Path(temp_dir) / "data"
            test_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create mock trades data (trades until yesterday)
            yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
            mock_trades = create_mock_trades_data(num_trades=3, start_date=yesterday - timedelta(days=2))
            
            # Save trades file
            slug = symbol.replace('/', '_').replace(':', '_')
            mode_suffix = mode.lower()
            trading_suffix = "_24h" if full_day_trading else ""
            filename = test_data_dir / f"trades_final_{slug}_{mode_suffix}{trading_suffix}.csv"
            mock_trades.to_csv(filename, index=False)
            
            # Create sidecar with today's date but no trades today
            today_iso = datetime.now(timezone.utc).date().isoformat()
            yesterday_iso = yesterday.isoformat()
            
            meta_path = filename.with_suffix("").with_suffix(".json")
            meta_path = Path(str(filename.with_suffix("")) + "_meta.json")
            
            meta_payload = {
                "last_backtest_until": today_iso,  # Fresh sidecar
                "last_trade_date": yesterday_iso,  # Last actual trade was yesterday
                "symbol": symbol,
                "mode": mode,
                "full_day_trading": full_day_trading,
                "backtest_start_date": (yesterday - timedelta(days=10)).isoformat()
            }
            meta_path.write_text(json.dumps(meta_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            
            # Test that load_trades returns the history instead of empty DataFrame
            loaded_trades = load_trades(symbol, mode, full_day_trading)
            
            print(f"   Loaded {len(loaded_trades)} trades")
            print(f"   Last trade date: {loaded_trades['entry_time'].max().date() if not loaded_trades.empty else 'None'}")
            
            # Should return the historical trades, not empty
            assert not loaded_trades.empty, "Should preserve historical trades when sidecar is fresh"
            assert len(loaded_trades) == 3, f"Expected 3 trades, got {len(loaded_trades)}"
            
            print("History preservation test passed")
            
        finally:
            # Restore original repo_root
            webapp.app.repo_root = original_repo_root


def test_time_window_alignment():
    """Test that time windows are correctly aligned with 24h switch."""
    print("\nTesting time window alignment...")
    
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


def test_daily_recommendation_display():
    """Test that daily recommendations are shown in dashboard."""
    print("\nTesting daily recommendation display...")
    
    # Mock the live_monitor module
    with patch('btc_1tpd_backtester.live_monitor.get_today_trade_recommendation') as mock_recommendation:
        # Mock a signal recommendation
        mock_recommendation.return_value = {
            "status": "signal",
            "side": "long",
            "entry_price": 50000.0,
            "stop_loss": 49500.0,
            "take_profit": 51000.0,
            "entry_time": "2024-01-15T12:30:00Z",
            "symbol": "BTC/USDT:USDT"
        }
        
        # Import and test detect_or_update_active_trade
        from btc_1tpd_backtester.live_monitor import detect_or_update_active_trade
        
        config = get_effective_config("BTC/USDT:USDT", "moderate", False)
        active_trade = detect_or_update_active_trade("BTC/USDT:USDT", "moderate", False, config)
        
        # Should create an active trade from the signal
        assert active_trade is not None, "Should create active trade from signal status"
        assert active_trade.side == "long", f"Expected 'long', got {active_trade.side}"
        assert active_trade.entry_price == 50000.0, f"Expected 50000.0, got {active_trade.entry_price}"
        assert active_trade.stop_loss == 49500.0, f"Expected 49500.0, got {active_trade.stop_loss}"
        assert active_trade.take_profit == 51000.0, f"Expected 51000.0, got {active_trade.take_profit}"
        
        print("Daily recommendation display test passed")


def test_sidecar_metadata_fields():
    """Test that sidecar includes last_trade_date field."""
    print("\nTesting sidecar metadata fields...")
    
    symbol = "BTC/USDT:USDT"
    mode = "moderate"
    full_day_trading = False
    
    with tempfile.TemporaryDirectory() as temp_dir:
        import webapp.app
        original_repo_root = webapp.app.repo_root
        webapp.app.repo_root = Path(temp_dir)
        
        try:
            # Create test data directory
            test_data_dir = Path(temp_dir) / "data"
            test_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create mock trades with specific dates
            yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
            mock_trades = create_mock_trades_data(num_trades=2, start_date=yesterday - timedelta(days=1))
            
            # Save trades file
            slug = symbol.replace('/', '_').replace(':', '_')
            mode_suffix = mode.lower()
            trading_suffix = "_24h" if full_day_trading else ""
            filename = test_data_dir / f"trades_final_{slug}_{mode_suffix}{trading_suffix}.csv"
            mock_trades.to_csv(filename, index=False)
            
            # Mock run_backtest to return empty (simulating no new trades)
            with patch('webapp.app.run_backtest') as mock_run_backtest:
                mock_run_backtest.return_value = pd.DataFrame()
                
                # Call refresh_trades
                result = refresh_trades(symbol, mode, full_day_trading)
                
                # Check that sidecar was written with last_trade_date
                meta_path = Path(str(filename.with_suffix("")) + "_meta.json")
                assert meta_path.exists(), "Sidecar should be created"
                
                meta_content = json.loads(meta_path.read_text(encoding="utf-8"))
                
                # Check required fields
                assert "last_backtest_until" in meta_content, "Sidecar should have last_backtest_until"
                assert "last_trade_date" in meta_content, "Sidecar should have last_trade_date"
                assert "symbol" in meta_content, "Sidecar should have symbol"
                assert "mode" in meta_content, "Sidecar should have mode"
                assert "full_day_trading" in meta_content, "Sidecar should have full_day_trading"
                
                # Check that last_trade_date is set correctly
                assert meta_content["last_trade_date"] == yesterday.isoformat(), f"Expected {yesterday.isoformat()}, got {meta_content['last_trade_date']}"
                
                print("Sidecar metadata fields test passed")
                
        finally:
            webapp.app.repo_root = original_repo_root


def test_entry_window_logic_in_strategy():
    """Test that SimpleTradingStrategy uses correct entry windows."""
    print("\nTesting entry window logic in strategy...")
    
    # Test normal mode
    config_normal = {
        'risk_usdt': 20.0,
        'orb_window': (11, 12),
        'entry_window': (11, 18),
        'full_day_trading': False
    }
    
    # Test 24h mode
    config_24h = {
        'risk_usdt': 20.0,
        'orb_window': (0, 1),
        'entry_window': (1, 24),
        'full_day_trading': True
    }
    
    # Import SimpleTradingStrategy
    from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy
    
    # Test normal mode strategy
    strategy_normal = SimpleTradingStrategy(config_normal)
    assert strategy_normal.entry_window == (11, 18), f"Normal mode should be (11, 18), got {strategy_normal.entry_window}"
    assert not strategy_normal.full_day_trading, "Normal mode should have full_day_trading=False"
    
    # Test 24h mode strategy
    strategy_24h = SimpleTradingStrategy(config_24h)
    assert strategy_24h.entry_window == (1, 24), f"24h mode should be (1, 24), got {strategy_24h.entry_window}"
    assert strategy_24h.full_day_trading, "24h mode should have full_day_trading=True"
    
    print("Entry window logic test passed")


def main():
    """Run all regression tests."""
    print("Starting regression tests for history preservation and time window alignment...")
    print("=" * 80)
    
    try:
        test_history_preservation_no_trades()
        test_time_window_alignment()
        test_daily_recommendation_display()
        test_sidecar_metadata_fields()
        test_entry_window_logic_in_strategy()
        
        print("\n" + "=" * 80)
        print("All regression tests passed!")
        print("\nSummary:")
        print("- History preservation works correctly when no trades occurred")
        print("- Time windows are properly aligned with 24h switch")
        print("- Daily recommendations are displayed in dashboard")
        print("- Sidecar metadata includes last_trade_date field")
        print("- Strategy logic uses correct entry windows")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
