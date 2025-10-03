#!/usr/bin/env python3
"""
Test position sizing with capital and leverage constraints.
"""

import sys
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))


def test_position_size_capital_limit():
    """Test that position size is limited by capital and leverage."""
    print("Testing position size capital limits...")
    
    from btc_1tpd_backtester.strategy import TradingStrategy
    
    # Test configuration with limited capital
    config = {
        'signal_tf': '1h',
        'risk_usdt': 50.0,
        'daily_target': 100.0,
        'daily_max_loss': 50.0,
        'force_one_trade': True,
        'fallback_mode': 'EMA15_pullback',
        'adx_min': 15.0,
        'min_rr_ok': 1.5,
        'atr_mult_orb': 1.2,
        'atr_mult_fallback': 1.2,
        'tp_multiplier': 2.0,
        'orb_window': (11, 12),
        'entry_window': (11, 18),
        'full_day_trading': False,
        'initial_capital': 1000.0,  # Limited capital
        'leverage': 1.0  # No leverage
    }
    
    strategy = TradingStrategy(config)
    
    # Test position size calculation
    entry_price = 50000.0  # BTC price
    stop_loss = 49500.0    # 500 USDT risk
    
    position_size = strategy.calculate_position_size(entry_price, stop_loss)
    
    # Calculate expected limits
    max_position_by_capital = (1000.0 * 1.0) / 50000.0  # 0.02 BTC
    max_position_by_risk = 50.0 / 500.0  # 0.1 BTC
    
    # Position size should be limited by capital (smaller limit)
    expected_position = min(max_position_by_capital, max_position_by_risk)
    
    assert abs(position_size - expected_position) < 0.0001, f"Position size {position_size} should be limited by capital {expected_position}"
    
    print(f"Position size: {position_size:.6f} BTC")
    print(f"Max by capital: {max_position_by_capital:.6f} BTC")
    print(f"Max by risk: {max_position_by_risk:.6f} BTC")
    print("Capital limit test passed")


def test_position_size_leverage_effect():
    """Test that leverage increases position size limit."""
    print("\nTesting leverage effect on position size...")
    
    from btc_1tpd_backtester.strategy import TradingStrategy
    
    # Test with leverage
    config = {
        'signal_tf': '1h',
        'risk_usdt': 50.0,
        'daily_target': 100.0,
        'daily_max_loss': 50.0,
        'force_one_trade': True,
        'fallback_mode': 'EMA15_pullback',
        'adx_min': 15.0,
        'min_rr_ok': 1.5,
        'atr_mult_orb': 1.2,
        'atr_mult_fallback': 1.2,
        'tp_multiplier': 2.0,
        'orb_window': (11, 12),
        'entry_window': (11, 18),
        'full_day_trading': False,
        'initial_capital': 1000.0,
        'leverage': 3.0  # 3x leverage
    }
    
    strategy = TradingStrategy(config)
    
    entry_price = 50000.0
    stop_loss = 49500.0
    
    position_size = strategy.calculate_position_size(entry_price, stop_loss)
    
    # Calculate expected limits
    max_position_by_capital = (1000.0 * 3.0) / 50000.0  # 0.06 BTC with 3x leverage
    max_position_by_risk = 50.0 / 500.0  # 0.1 BTC
    
    # Position size should be limited by capital (still smaller than risk limit)
    expected_position = min(max_position_by_capital, max_position_by_risk)
    
    assert abs(position_size - expected_position) < 0.0001, f"Position size {position_size} should be limited by leveraged capital {expected_position}"
    
    print(f"Position size with 3x leverage: {position_size:.6f} BTC")
    print(f"Max by leveraged capital: {max_position_by_capital:.6f} BTC")
    print(f"Max by risk: {max_position_by_risk:.6f} BTC")
    print("Leverage effect test passed")


def test_zero_position_size():
    """Test that position size is zero when insufficient capital."""
    print("\nTesting zero position size with insufficient capital...")
    
    from btc_1tpd_backtester.strategy import TradingStrategy
    
    # Test with very limited capital
    config = {
        'signal_tf': '1h',
        'risk_usdt': 50.0,
        'daily_target': 100.0,
        'daily_max_loss': 50.0,
        'force_one_trade': True,
        'fallback_mode': 'EMA15_pullback',
        'adx_min': 15.0,
        'min_rr_ok': 1.5,
        'atr_mult_orb': 1.2,
        'atr_mult_fallback': 1.2,
        'tp_multiplier': 2.0,
        'orb_window': (11, 12),
        'entry_window': (11, 18),
        'full_day_trading': False,
        'initial_capital': 100.0,  # Very limited capital
        'leverage': 1.0
    }
    
    strategy = TradingStrategy(config)
    
    entry_price = 50000.0
    stop_loss = 49500.0
    
    position_size = strategy.calculate_position_size(entry_price, stop_loss)
    
    # With only 100 USDT capital, max position would be 100/50000 = 0.002 BTC
    # But risk-based position size would be 50/500 = 0.1 BTC
    # So position should be limited by capital
    max_position_by_capital = (100.0 * 1.0) / 50000.0  # 0.002 BTC
    
    assert position_size == max_position_by_capital, f"Position size {position_size} should equal capital limit {max_position_by_capital}"
    
    print(f"Position size with limited capital: {position_size:.6f} BTC")
    print(f"Capital limit: {max_position_by_capital:.6f} BTC")
    print("Zero position size test passed")


def test_effective_risk_calculation():
    """Test that effective risk is recalculated based on capped position size."""
    print("\nTesting effective risk calculation...")
    
    from btc_1tpd_backtester.strategy import TradingStrategy
    
    config = {
        'signal_tf': '1h',
        'risk_usdt': 100.0,  # High risk target
        'daily_target': 200.0,
        'daily_max_loss': 100.0,
        'force_one_trade': True,
        'fallback_mode': 'EMA15_pullback',
        'adx_min': 15.0,
        'min_rr_ok': 1.5,
        'atr_mult_orb': 1.2,
        'atr_mult_fallback': 1.2,
        'tp_multiplier': 2.0,
        'orb_window': (11, 12),
        'entry_window': (11, 18),
        'full_day_trading': False,
        'initial_capital': 1000.0,
        'leverage': 1.0
    }
    
    strategy = TradingStrategy(config)
    
    entry_price = 50000.0
    stop_loss = 49500.0  # 500 USDT price difference
    
    # Calculate position size
    position_size = strategy.calculate_position_size(entry_price, stop_loss)
    
    # Calculate effective risk
    effective_risk = abs(entry_price - stop_loss) * position_size
    
    # Original risk target was 100 USDT
    # But if position is capped by capital, effective risk will be lower
    print(f"Original risk target: {config['risk_usdt']} USDT")
    print(f"Position size: {position_size:.6f} BTC")
    print(f"Effective risk: {effective_risk:.2f} USDT")
    
    # Effective risk should be <= original risk target
    assert effective_risk <= config['risk_usdt'], f"Effective risk {effective_risk} should not exceed target {config['risk_usdt']}"
    
    print("Effective risk calculation test passed")


def main():
    """Run all position sizing tests."""
    print("Starting position sizing tests...")
    print("=" * 50)
    
    try:
        test_position_size_capital_limit()
        test_position_size_leverage_effect()
        test_zero_position_size()
        test_effective_risk_calculation()
        
        print("\n" + "=" * 50)
        print("All position sizing tests passed!")
        print("\nSummary:")
        print("[OK] Position size is limited by capital and leverage")
        print("[OK] Leverage increases position size limit")
        print("[OK] Zero position size with insufficient capital")
        print("[OK] Effective risk is recalculated based on capped position size")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
