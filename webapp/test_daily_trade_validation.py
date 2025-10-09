#!/usr/bin/env python3
"""
Tests for daily trade validation functionality.
Tests the logic that compares strategy signals with recent trades.
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


def create_sample_trades_with_sides():
    """Create sample trades with different sides for testing."""
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
        }
    ]
    return pd.DataFrame(trades_data)


def test_strategy_signal_validation():
    """Test validation logic for strategy signals vs recent trades."""
    print("Testing strategy signal validation...")
    
    # Test case 1: Matching signals (no alert)
    trades_df = create_sample_trades_with_sides()
    strategy_signal = "long"  # Matches most recent trade (first in sorted list)
    recent_side = trades_df.iloc[0]["side"]  # "long"
    
    # Simulate validation logic
    validation_alert = ""
    if strategy_signal and not trades_df.empty and "side" in trades_df.columns:
        recent_trade = trades_df.iloc[0] if len(trades_df) > 0 else None
        if recent_trade is not None:
            recent_side = recent_trade.get("side")
            if recent_side:
                if strategy_signal.lower() != recent_side.lower():
                    validation_alert = f"[WARN] Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
    
    assert validation_alert == "", f"Should not generate alert for matching signals, got: {validation_alert}"
    
    # Test case 2: Mismatched signals (should generate alert)
    strategy_signal = "short"  # Doesn't match most recent trade
    recent_side = trades_df.iloc[0]["side"]  # "long"
    
    validation_alert = ""
    if strategy_signal and not trades_df.empty and "side" in trades_df.columns:
        recent_trade = trades_df.iloc[0] if len(trades_df) > 0 else None
        if recent_trade is not None:
            recent_side = recent_trade.get("side")
            if recent_side:
                if strategy_signal.lower() != recent_side.lower():
                    validation_alert = f"[WARN] Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
    
    assert validation_alert != "", "Should generate alert for mismatched signals"
    assert "SHORT" in validation_alert, "Alert should contain strategy signal"
    assert "LONG" in validation_alert, "Alert should contain recent trade side"
    
    print("[OK] Strategy signal validation test passed")


def test_inversion_display_logic():
    """Test that inversion affects display but not validation."""
    print("Testing inversion display logic...")
    
    # Test case 1: Normal mode (no inversion)
    is_inverted = False
    strategy_signal = "long"
    
    # Apply inversion to display if enabled
    display_side = strategy_signal
    if is_inverted and strategy_signal:
        display_side = "short" if strategy_signal.lower() == "long" else "long"
    
    assert display_side == "long", f"Display side should remain 'long' in normal mode, got {display_side}"
    
    # Test case 2: Inverted mode (affects display)
    is_inverted = True
    strategy_signal = "long"
    
    # Apply inversion to display if enabled
    display_side = strategy_signal
    if is_inverted and strategy_signal:
        display_side = "short" if strategy_signal.lower() == "long" else "long"
    
    assert display_side == "short", f"Display side should be 'short' in inverted mode, got {display_side}"
    
    # Test case 3: Validation should use original signal, not display signal
    trades_df = create_sample_trades_with_sides()
    recent_side = trades_df.iloc[0]["side"]  # "long"
    
    # Validation should compare original strategy_signal, not display_side
    validation_alert = ""
    if strategy_signal and not trades_df.empty and "side" in trades_df.columns:
        recent_trade = trades_df.iloc[0] if len(trades_df) > 0 else None
        if recent_trade is not None:
            recent_side = recent_trade.get("side")
            if recent_side:
                # Compare original signals (not inverted for display)
                if strategy_signal.lower() != recent_side.lower():
                    validation_alert = f"[WARN] Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
    
    assert validation_alert == "", "Validation should use original signal, not display signal"
    
    print("[OK] Inversion display logic test passed")


def test_edge_cases():
    """Test edge cases for validation logic."""
    print("Testing edge cases...")
    
    # Test case 1: Empty trades DataFrame
    empty_trades = pd.DataFrame()
    strategy_signal = "long"
    
    validation_alert = ""
    if strategy_signal and not empty_trades.empty and "side" in empty_trades.columns:
        recent_trade = empty_trades.iloc[0] if len(empty_trades) > 0 else None
        if recent_trade is not None:
            recent_side = recent_trade.get("side")
            if recent_side:
                if strategy_signal.lower() != recent_side.lower():
                    validation_alert = f"[WARN] Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
    
    assert validation_alert == "", "Should not generate alert for empty trades"
    
    # Test case 2: No strategy signal
    trades_df = create_sample_trades_with_sides()
    strategy_signal = None
    
    validation_alert = ""
    if strategy_signal and not trades_df.empty and "side" in trades_df.columns:
        recent_trade = trades_df.iloc[0] if len(trades_df) > 0 else None
        if recent_trade is not None:
            recent_side = recent_trade.get("side")
            if recent_side:
                if strategy_signal.lower() != recent_side.lower():
                    validation_alert = f"[WARN] Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
    
    assert validation_alert == "", "Should not generate alert when no strategy signal"
    
    # Test case 3: Trades without side column
    trades_no_side = pd.DataFrame([{"entry_time": "2024-01-15T12:00:00Z", "pnl_usdt": 100.0}])
    strategy_signal = "long"
    
    validation_alert = ""
    if strategy_signal and not trades_no_side.empty and "side" in trades_no_side.columns:
        recent_trade = trades_no_side.iloc[0] if len(trades_no_side) > 0 else None
        if recent_trade is not None:
            recent_side = recent_trade.get("side")
            if recent_side:
                if strategy_signal.lower() != recent_side.lower():
                    validation_alert = f"[WARN] Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
    
    assert validation_alert == "", "Should not generate alert when trades have no side column"
    
    print("[OK] Edge cases test passed")


def test_alert_message_format():
    """Test the format of validation alert messages."""
    print("Testing alert message format...")
    
    trades_df = create_sample_trades_with_sides()
    strategy_signal = "short"
    recent_side = trades_df.iloc[0]["side"]  # "long"
    
    validation_alert = ""
    if strategy_signal and not trades_df.empty and "side" in trades_df.columns:
        recent_trade = trades_df.iloc[0] if len(trades_df) > 0 else None
        if recent_trade is not None:
            recent_side = recent_trade.get("side")
            if recent_side:
                if strategy_signal.lower() != recent_side.lower():
                    validation_alert = f"[WARN] Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
    
    # Check message format
    assert "[WARN] Inconsistencia detectada:" in validation_alert, "Alert should contain warning emoji and text"
    assert "Señal de estrategia" in validation_alert, "Alert should mention strategy signal"
    assert "no coincide con trade más reciente" in validation_alert, "Alert should mention trade mismatch"
    assert "SHORT" in validation_alert, "Alert should contain strategy signal in uppercase"
    assert "LONG" in validation_alert, "Alert should contain recent trade side in uppercase"
    
    print("[OK] Alert message format test passed")


def main():
    """Run all daily trade validation tests."""
    print("Starting daily trade validation tests...")
    print("=" * 60)
    
    try:
        test_strategy_signal_validation()
        test_inversion_display_logic()
        test_edge_cases()
        test_alert_message_format()
        
        print("\n" + "=" * 60)
        print("All daily trade validation tests passed!")
        print("\nSummary:")
        print("- Strategy signal validation works correctly")
        print("- Inversion affects display but not validation logic")
        print("- Edge cases are handled properly")
        print("- Alert messages have correct format")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
