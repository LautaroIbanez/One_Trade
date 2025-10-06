#!/usr/bin/env python3
"""
Unit tests for strategy inversion functionality.
Tests the helpers that invert trades, metrics, and dataframes.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))


def create_sample_trade():
    """Create a sample trade for testing."""
    return {
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
    }


def create_sample_trades_dataframe():
    """Create a sample trades DataFrame for testing."""
    trades_data = [
        {
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
        },
        {
            'day_key': '2024-01-16',
            'entry_time': '2024-01-16T12:00:00Z',
            'side': 'short',
            'entry_price': 51000.0,
            'sl': 51500.0,
            'tp': 50000.0,
            'exit_time': '2024-01-16T18:00:00Z',
            'exit_price': 50000.0,
            'exit_reason': 'take_profit',
            'pnl_usdt': 100.0,
            'r_multiple': 2.0,
            'used_fallback': False
        },
        {
            'day_key': '2024-01-17',
            'entry_time': '2024-01-17T12:00:00Z',
            'side': 'long',
            'entry_price': 50000.0,
            'sl': 49500.0,
            'tp': 51000.0,
            'exit_time': '2024-01-17T18:00:00Z',
            'exit_price': 49500.0,
            'exit_reason': 'stop_loss',
            'pnl_usdt': -50.0,
            'r_multiple': -1.0,
            'used_fallback': False
        }
    ]
    return pd.DataFrame(trades_data)


def create_sample_metrics():
    """Create sample metrics for testing."""
    return {
        "total_trades": 3,
        "win_rate": 66.67,
        "total_pnl": 150.0,
        "max_drawdown": -50.0,
        "avg_risk_per_trade": 50.0,
        "dd_in_r": 1.0,
        "initial_capital": 1000.0,
        "current_capital": 1150.0,
        "roi": 15.0,
        "leverage": 1.0
    }


def test_invert_trade():
    """Test single trade inversion."""
    print("Testing single trade inversion...")
    
    from webapp.app import invert_trade
    
    # Test long trade
    long_trade = create_sample_trade()
    inverted_long = invert_trade(long_trade)
    
    assert inverted_long["side"] == "short", f"Expected 'short', got {inverted_long['side']}"
    assert inverted_long["pnl_usdt"] == -100.0, f"Expected -100.0, got {inverted_long['pnl_usdt']}"
    assert inverted_long["r_multiple"] == -2.0, f"Expected -2.0, got {inverted_long['r_multiple']}"
    assert inverted_long["exit_reason"] == "stop_loss", f"Expected 'stop_loss', got {inverted_long['exit_reason']}"
    
    # Test short trade
    short_trade = create_sample_trade()
    short_trade["side"] = "short"
    short_trade["pnl_usdt"] = -50.0
    short_trade["r_multiple"] = -1.0
    short_trade["exit_reason"] = "stop_loss"
    
    inverted_short = invert_trade(short_trade)
    
    assert inverted_short["side"] == "long", f"Expected 'long', got {inverted_short['side']}"
    assert inverted_short["pnl_usdt"] == 50.0, f"Expected 50.0, got {inverted_short['pnl_usdt']}"
    assert inverted_short["r_multiple"] == 1.0, f"Expected 1.0, got {inverted_short['r_multiple']}"
    assert inverted_short["exit_reason"] == "take_profit", f"Expected 'take_profit', got {inverted_short['exit_reason']}"
    
    print("✅ Single trade inversion test passed")


def test_invert_trades_dataframe():
    """Test DataFrame trades inversion."""
    print("Testing DataFrame trades inversion...")
    
    from webapp.app import invert_trades_dataframe
    
    # Test with sample data
    df = create_sample_trades_dataframe()
    inverted_df = invert_trades_dataframe(df)
    
    # Check side inversion
    assert inverted_df.iloc[0]["side"] == "short", f"Expected 'short', got {inverted_df.iloc[0]['side']}"
    assert inverted_df.iloc[1]["side"] == "long", f"Expected 'long', got {inverted_df.iloc[1]['side']}"
    assert inverted_df.iloc[2]["side"] == "short", f"Expected 'short', got {inverted_df.iloc[2]['side']}"
    
    # Check PnL inversion
    assert inverted_df.iloc[0]["pnl_usdt"] == -100.0, f"Expected -100.0, got {inverted_df.iloc[0]['pnl_usdt']}"
    assert inverted_df.iloc[1]["pnl_usdt"] == -100.0, f"Expected -100.0, got {inverted_df.iloc[1]['pnl_usdt']}"
    assert inverted_df.iloc[2]["pnl_usdt"] == 50.0, f"Expected 50.0, got {inverted_df.iloc[2]['pnl_usdt']}"
    
    # Check R-multiple inversion
    assert inverted_df.iloc[0]["r_multiple"] == -2.0, f"Expected -2.0, got {inverted_df.iloc[0]['r_multiple']}"
    assert inverted_df.iloc[1]["r_multiple"] == -2.0, f"Expected -2.0, got {inverted_df.iloc[1]['r_multiple']}"
    assert inverted_df.iloc[2]["r_multiple"] == 1.0, f"Expected 1.0, got {inverted_df.iloc[2]['r_multiple']}"
    
    # Check exit reason inversion
    assert inverted_df.iloc[0]["exit_reason"] == "stop_loss", f"Expected 'stop_loss', got {inverted_df.iloc[0]['exit_reason']}"
    assert inverted_df.iloc[1]["exit_reason"] == "stop_loss", f"Expected 'stop_loss', got {inverted_df.iloc[1]['exit_reason']}"
    assert inverted_df.iloc[2]["exit_reason"] == "take_profit", f"Expected 'take_profit', got {inverted_df.iloc[2]['exit_reason']}"
    
    # Test empty DataFrame
    empty_df = pd.DataFrame()
    inverted_empty = invert_trades_dataframe(empty_df)
    assert inverted_empty.empty, "Empty DataFrame should remain empty after inversion"
    
    print("✅ DataFrame trades inversion test passed")


def test_invert_metrics():
    """Test metrics inversion."""
    print("Testing metrics inversion...")
    
    from webapp.app import invert_metrics
    
    # Test with sample metrics
    metrics = create_sample_metrics()
    inverted_metrics = invert_metrics(metrics)
    
    # Check PnL inversion
    assert inverted_metrics["total_pnl"] == -150.0, f"Expected -150.0, got {inverted_metrics['total_pnl']}"
    
    # Check current capital recalculation
    assert inverted_metrics["current_capital"] == 850.0, f"Expected 850.0, got {inverted_metrics['current_capital']}"
    
    # Check ROI inversion
    assert inverted_metrics["roi"] == -15.0, f"Expected -15.0, got {inverted_metrics['roi']}"
    
    # Check drawdown inversion (becomes max gain)
    assert inverted_metrics["max_drawdown"] == 50.0, f"Expected 50.0, got {inverted_metrics['max_drawdown']}"
    
    # Check win rate inversion (becomes loss rate)
    assert inverted_metrics["win_rate"] == 33.33, f"Expected 33.33, got {inverted_metrics['win_rate']}"
    
    # Check that non-invertible metrics remain the same
    assert inverted_metrics["total_trades"] == 3, f"Expected 3, got {inverted_metrics['total_trades']}"
    assert inverted_metrics["initial_capital"] == 1000.0, f"Expected 1000.0, got {inverted_metrics['initial_capital']}"
    assert inverted_metrics["leverage"] == 1.0, f"Expected 1.0, got {inverted_metrics['leverage']}"
    
    print("✅ Metrics inversion test passed")


def test_double_inversion():
    """Test that double inversion returns to original values."""
    print("Testing double inversion...")
    
    from webapp.app import invert_trade, invert_trades_dataframe, invert_metrics
    
    # Test single trade double inversion
    original_trade = create_sample_trade()
    inverted_once = invert_trade(original_trade)
    inverted_twice = invert_trade(inverted_once)
    
    assert inverted_twice["side"] == original_trade["side"], "Double inversion should restore original side"
    assert inverted_twice["pnl_usdt"] == original_trade["pnl_usdt"], "Double inversion should restore original PnL"
    assert inverted_twice["r_multiple"] == original_trade["r_multiple"], "Double inversion should restore original R-multiple"
    assert inverted_twice["exit_reason"] == original_trade["exit_reason"], "Double inversion should restore original exit reason"
    
    # Test DataFrame double inversion
    original_df = create_sample_trades_dataframe()
    inverted_once_df = invert_trades_dataframe(original_df)
    inverted_twice_df = invert_trades_dataframe(inverted_once_df)
    
    pd.testing.assert_frame_equal(original_df, inverted_twice_df, check_dtype=False)
    
    # Test metrics double inversion
    original_metrics = create_sample_metrics()
    inverted_once_metrics = invert_metrics(original_metrics)
    inverted_twice_metrics = invert_metrics(inverted_once_metrics)
    
    assert inverted_twice_metrics["total_pnl"] == original_metrics["total_pnl"], "Double inversion should restore original total_pnl"
    assert inverted_twice_metrics["roi"] == original_metrics["roi"], "Double inversion should restore original ROI"
    assert inverted_twice_metrics["win_rate"] == original_metrics["win_rate"], "Double inversion should restore original win_rate"
    
    print("✅ Double inversion test passed")


def main():
    """Run all strategy inversion tests."""
    print("Starting strategy inversion tests...")
    print("=" * 60)
    
    try:
        test_invert_trade()
        test_invert_trades_dataframe()
        test_invert_metrics()
        test_double_inversion()
        
        print("\n" + "=" * 60)
        print("All strategy inversion tests passed!")
        print("\nSummary:")
        print("- Single trade inversion works correctly")
        print("- DataFrame trades inversion works correctly")
        print("- Metrics inversion works correctly")
        print("- Double inversion restores original values")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
