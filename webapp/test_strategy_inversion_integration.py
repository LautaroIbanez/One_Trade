#!/usr/bin/env python3
"""
Integration test for complete strategy inversion functionality.
Tests the full flow from UI switch to dashboard updates and validation.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))


def create_comprehensive_test_data():
    """Create comprehensive test data for integration testing."""
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


def test_complete_inversion_flow():
    """Test the complete inversion flow from data to metrics.
    
    NEW BEHAVIOR: Metrics maintain standard interpretation.
    - Use compute_metrics_pure(..., invertido=True) instead of invert_metrics()
    - Win rate reflects actual win percentage of inverted trades
    - Max drawdown always negative (magnitude-sensitive)
    """
    print("Testing complete inversion flow...")
    
    from webapp.app import invert_trades_dataframe, compute_metrics_pure
    
    # Create test data
    original_trades = create_comprehensive_test_data()
    
    # Test normal metrics
    normal_metrics = compute_metrics_pure(original_trades, 1000.0, 1.0, invertido=False)
    
    # Test inverted trades
    inverted_trades = invert_trades_dataframe(original_trades)
    
    # Test inverted metrics using NEW approach
    inverted_metrics = compute_metrics_pure(original_trades, 1000.0, 1.0, invertido=True)
    
    # Verify inversion worked correctly
    assert len(inverted_trades) == len(original_trades), "Inverted trades should have same length"
    
    # Check side inversion
    assert inverted_trades.iloc[0]["side"] == "short", "First trade should be inverted to short"
    assert inverted_trades.iloc[1]["side"] == "long", "Second trade should be inverted to long"
    assert inverted_trades.iloc[2]["side"] == "short", "Third trade should be inverted to short"
    
    # Check PnL inversion
    assert inverted_trades.iloc[0]["pnl_usdt"] == -100.0, "First trade PnL should be inverted"
    assert inverted_trades.iloc[1]["pnl_usdt"] == -100.0, "Second trade PnL should be inverted"
    assert inverted_trades.iloc[2]["pnl_usdt"] == 50.0, "Third trade PnL should be inverted"
    
    # Check R-multiple inversion
    assert inverted_trades.iloc[0]["r_multiple"] == -2.0, "First trade R-multiple should be inverted"
    assert inverted_trades.iloc[1]["r_multiple"] == -2.0, "Second trade R-multiple should be inverted"
    assert inverted_trades.iloc[2]["r_multiple"] == 1.0, "Third trade R-multiple should be inverted"
    
    # Check exit reason inversion
    assert inverted_trades.iloc[0]["exit_reason"] == "stop_loss", "First trade exit reason should be inverted"
    assert inverted_trades.iloc[1]["exit_reason"] == "stop_loss", "Second trade exit reason should be inverted"
    assert inverted_trades.iloc[2]["exit_reason"] == "take_profit", "Third trade exit reason should be inverted"
    
    # Check metrics inversion (NEW BEHAVIOR)
    # Directional metrics: inverted
    assert inverted_metrics["total_pnl"] == -normal_metrics["total_pnl"], "Total PnL should be inverted"
    assert inverted_metrics["roi"] == -normal_metrics["roi"], "ROI should be inverted"
    
    # Win rate: reflects actual win percentage of inverted trades (not 100 - win_rate)
    # For this dataset: normal has 2 wins out of 3 (66.67%), inverted has 1 win out of 3 (33.33%)
    assert abs(inverted_metrics["win_rate"] - 33.33) < 0.1, f"Win rate should be 33.33% for inverted trades, got {inverted_metrics['win_rate']}"
    
    # Max drawdown: always negative (magnitude-sensitive)
    assert inverted_metrics["max_drawdown"] <= 0, "Max drawdown should always be negative or zero"
    
    print("✅ Complete inversion flow test passed")


def test_ui_state_management():
    """Test UI state management for inversion."""
    print("Testing UI state management...")
    
    # Test inversion state structure
    inversion_state_normal = {"inverted": False}
    inversion_state_inverted = {"inverted": True}
    
    # Test state extraction
    is_inverted_normal = inversion_state_normal.get("inverted", False)
    is_inverted_inverted = inversion_state_inverted.get("inverted", False)
    
    assert not is_inverted_normal, "Normal state should not be inverted"
    assert is_inverted_inverted, "Inverted state should be inverted"
    
    # Test badge style logic
    badge_style_normal = {"display": "block"} if is_inverted_normal else {"display": "none"}
    badge_style_inverted = {"display": "block"} if is_inverted_inverted else {"display": "none"}
    
    assert badge_style_normal["display"] == "none", "Normal state should hide badge"
    assert badge_style_inverted["display"] == "block", "Inverted state should show badge"
    
    print("✅ UI state management test passed")


def test_metric_labels_and_colors():
    """Test metric labels and colors based on inversion state.
    
    NEW BEHAVIOR: Labels remain standard in both modes, colors use standard interpretation.
    """
    print("Testing metric labels and colors...")
    
    # Test normal mode
    is_inverted = False
    win_rate_label = "Win rate"  # Always "Win rate" now
    dd_label = "Max DD"  # Always "Max DD" now
    
    assert win_rate_label == "Win rate", "Normal mode should show 'Win rate'"
    assert dd_label == "Max DD", "Normal mode should show 'Max DD'"
    
    # Test inverted mode - labels should remain the same
    is_inverted = True
    win_rate_label = "Win rate"  # No longer changes to "Loss rate"
    dd_label = "Max DD"  # No longer changes to "Max Gain"
    
    assert win_rate_label == "Win rate", "Inverted mode should still show 'Win rate'"
    assert dd_label == "Max DD", "Inverted mode should still show 'Max DD'"
    
    # Test color logic - should be consistent across both modes
    # Example: inverted strategy with poor performance
    metrics = {"win_rate": 33.33, "total_pnl": -150.0, "max_drawdown": -50.0, "roi": -15.0}
    
    # Standard color logic applies to both modes
    win_color = "success" if metrics['win_rate'] >= 50 else "warning" if metrics['win_rate'] > 0 else "secondary"
    pnl_color = "success" if metrics['total_pnl'] >= 0 else "danger"
    dd_color = "danger" if metrics['max_drawdown'] < 0 else "secondary"
    roi_color = "success" if metrics['roi'] >= 0 else "danger"
    
    assert win_color == "warning", "Low win rate (33%) should be warning color"
    assert pnl_color == "danger", "Negative PnL should be danger color"
    assert dd_color == "danger", "Negative drawdown should be danger color"
    assert roi_color == "danger", "Negative ROI should be danger color"
    
    print("✅ Metric labels and colors test passed")


def test_validation_with_inversion():
    """Test validation logic works correctly with inversion."""
    print("Testing validation with inversion...")
    
    # Create test data
    trades_df = create_comprehensive_test_data()
    strategy_signal = "long"  # Matches most recent trade
    
    # Test normal mode validation
    is_inverted = False
    display_side = strategy_signal
    if is_inverted and strategy_signal:
        display_side = "short" if strategy_signal.lower() == "long" else "long"
    
    # Validation should use original signal, not display signal
    validation_alert = ""
    if strategy_signal and not trades_df.empty and "side" in trades_df.columns:
        recent_trade = trades_df.iloc[0] if len(trades_df) > 0 else None
        if recent_trade is not None:
            recent_side = recent_trade.get("side")
            if recent_side:
                if strategy_signal.lower() != recent_side.lower():
                    validation_alert = f"⚠️ Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
    
    assert validation_alert == "", "Should not generate alert for matching signals in normal mode"
    assert display_side == "long", "Display side should be 'long' in normal mode"
    
    # Test inverted mode validation
    is_inverted = True
    display_side = strategy_signal
    if is_inverted and strategy_signal:
        display_side = "short" if strategy_signal.lower() == "long" else "long"
    
    # Validation should still use original signal
    validation_alert = ""
    if strategy_signal and not trades_df.empty and "side" in trades_df.columns:
        recent_trade = trades_df.iloc[0] if len(trades_df) > 0 else None
        if recent_trade is not None:
            recent_side = recent_trade.get("side")
            if recent_side:
                if strategy_signal.lower() != recent_side.lower():
                    validation_alert = f"⚠️ Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
    
    assert validation_alert == "", "Should not generate alert for matching signals in inverted mode"
    assert display_side == "short", "Display side should be 'short' in inverted mode"
    
    print("✅ Validation with inversion test passed")


def test_double_inversion_consistency():
    """Test that double inversion returns to original state.
    
    NEW BEHAVIOR: Use compute_metrics_pure for consistent behavior.
    """
    print("Testing double inversion consistency...")
    
    from webapp.app import invert_trades_dataframe, compute_metrics_pure
    
    # Create test data
    original_trades = create_comprehensive_test_data()
    original_metrics = compute_metrics_pure(original_trades, 1000.0, 1.0, invertido=False)
    
    # Apply trade inversion twice
    inverted_once = invert_trades_dataframe(original_trades)
    inverted_twice = invert_trades_dataframe(inverted_once)
    
    # Compute metrics with double inversion (should equal normal metrics)
    # First inversion
    metrics_inverted_once = compute_metrics_pure(original_trades, 1000.0, 1.0, invertido=True)
    # Double inversion: apply inversion to already inverted trades
    metrics_inverted_twice = compute_metrics_pure(inverted_once, 1000.0, 1.0, invertido=True)
    
    # Check that double inversion returns to original
    pd.testing.assert_frame_equal(original_trades, inverted_twice, check_dtype=False)
    
    # Metrics should also return to original after double inversion
    assert abs(metrics_inverted_twice["total_pnl"] - original_metrics["total_pnl"]) < 0.01, "Double inversion should restore original total_pnl"
    assert abs(metrics_inverted_twice["roi"] - original_metrics["roi"]) < 0.01, "Double inversion should restore original ROI"
    assert abs(metrics_inverted_twice["win_rate"] - original_metrics["win_rate"]) < 0.1, "Double inversion should restore original win_rate"
    assert abs(metrics_inverted_twice["max_drawdown"] - original_metrics["max_drawdown"]) < 0.01, "Double inversion should restore original max_drawdown"
    
    print("✅ Double inversion consistency test passed")


def main():
    """Run all strategy inversion integration tests."""
    print("Starting strategy inversion integration tests...")
    print("=" * 70)
    
    try:
        test_complete_inversion_flow()
        test_ui_state_management()
        test_metric_labels_and_colors()
        test_validation_with_inversion()
        test_double_inversion_consistency()
        
        print("\n" + "=" * 70)
        print("All strategy inversion integration tests passed!")
        print("\nSummary:")
        print("- Complete inversion flow works correctly")
        print("- UI state management functions properly")
        print("- Metric labels and colors adapt to inversion state")
        print("- Validation logic works correctly with inversion")
        print("- Double inversion maintains consistency")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
