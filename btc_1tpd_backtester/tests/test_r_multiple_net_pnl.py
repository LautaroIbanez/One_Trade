#!/usr/bin/env python3
"""
Test R-multiple calculation using net PnL.
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


def test_r_multiple_positive_pnl():
    """Test R-multiple calculation with positive net PnL."""
    print("Testing R-multiple with positive net PnL...")
    
    from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleBacktester
    
    # Test configuration
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
        'commission_rate': 0.001,  # 0.1% commission
        'slippage_rate': 0.0005,   # 0.05% slippage
        'initial_capital': 1000.0,
        'leverage': 1.0
    }
    
    backtester = SimpleBacktester(config)
    
    # Test trade parameters
    trade_params = {
        'entry_price': 50000.0,
        'stop_loss': 49500.0,  # 500 USDT risk
        'take_profit': 51000.0,  # 1000 USDT reward (2:1 R/R)
        'position_size': 0.1,  # 0.1 BTC position
        'entry_time': datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    }
    
    # Create test data for a winning trade (TP hit)
    timestamps = [
        datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        datetime(2024, 1, 15, 12, 15, 0, tzinfo=timezone.utc),
        datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc),
    ]
    
    data = {
        'open': [50000, 50200, 50800],
        'high': [50100, 50500, 51050],  # TP hit in last candle
        'low': [49900, 50100, 50700],
        'close': [50200, 50400, 51000],
        'volume': [1000, 1200, 1500]
    }
    
    day_data = pd.DataFrame(data, index=timestamps)
    
    # Simulate trade exit
    result = backtester.simulate_trade_exit(trade_params, 'long', day_data)
    
    # Calculate expected values
    entry_price = 50000.0
    exit_price = 51000.0  # TP hit
    position_size = 0.1
    
    # Gross PnL
    gross_pnl = (exit_price - entry_price) * position_size  # 100 USDT
    
    # Costs (commission + slippage)
    per_leg_commission = (0.001 / 2)  # 0.0005 per leg
    per_leg_slippage = (0.0005 / 2)   # 0.00025 per leg
    
    entry_cost = entry_price * position_size * (per_leg_commission + per_leg_slippage)
    exit_cost = exit_price * position_size * (per_leg_commission + per_leg_slippage)
    total_costs = entry_cost + exit_cost
    
    net_pnl = gross_pnl - total_costs
    
    # Risk in USDT
    risk_in_usdt = abs(entry_price - trade_params['stop_loss']) * position_size  # 50 USDT
    
    # Expected R-multiple
    expected_r_multiple = net_pnl / risk_in_usdt
    
    print(f"Gross PnL: {gross_pnl:.2f} USDT")
    print(f"Total costs: {total_costs:.2f} USDT")
    print(f"Net PnL: {net_pnl:.2f} USDT")
    print(f"Risk in USDT: {risk_in_usdt:.2f} USDT")
    print(f"Expected R-multiple: {expected_r_multiple:.4f}")
    print(f"Actual R-multiple: {result['r_multiple']:.4f}")
    
    # Verify R-multiple calculation
    assert abs(result['r_multiple'] - expected_r_multiple) < 0.001, f"R-multiple {result['r_multiple']} should equal {expected_r_multiple}"
    assert result['r_multiple'] > 0, "R-multiple should be positive for winning trade"
    
    print("Positive PnL R-multiple test passed")


def test_r_multiple_negative_pnl():
    """Test R-multiple calculation with negative net PnL."""
    print("\nTesting R-multiple with negative net PnL...")
    
    from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleBacktester
    
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
        'commission_rate': 0.001,
        'slippage_rate': 0.0005,
        'initial_capital': 1000.0,
        'leverage': 1.0
    }
    
    backtester = SimpleBacktester(config)
    
    # Test trade parameters
    trade_params = {
        'entry_price': 50000.0,
        'stop_loss': 49500.0,  # 500 USDT risk
        'take_profit': 51000.0,
        'position_size': 0.1,
        'entry_time': datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    }
    
    # Create test data for a losing trade (SL hit)
    timestamps = [
        datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        datetime(2024, 1, 15, 12, 15, 0, tzinfo=timezone.utc),
        datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc),
    ]
    
    data = {
        'open': [50000, 49800, 49600],
        'high': [50100, 49900, 49700],
        'low': [49900, 49600, 49450],  # SL hit in last candle
        'close': [49800, 49650, 49500],
        'volume': [1000, 1200, 1500]
    }
    
    day_data = pd.DataFrame(data, index=timestamps)
    
    # Simulate trade exit
    result = backtester.simulate_trade_exit(trade_params, 'long', day_data)
    
    # Calculate expected values
    entry_price = 50000.0
    exit_price = 49500.0  # SL hit
    position_size = 0.1
    
    # Gross PnL (negative)
    gross_pnl = (exit_price - entry_price) * position_size  # -50 USDT
    
    # Costs
    per_leg_commission = (0.001 / 2)
    per_leg_slippage = (0.0005 / 2)
    
    entry_cost = entry_price * position_size * (per_leg_commission + per_leg_slippage)
    exit_cost = exit_price * position_size * (per_leg_commission + per_leg_slippage)
    total_costs = entry_cost + exit_cost
    
    net_pnl = gross_pnl - total_costs  # Even more negative due to costs
    
    # Risk in USDT
    risk_in_usdt = abs(entry_price - trade_params['stop_loss']) * position_size  # 50 USDT
    
    # Expected R-multiple (negative)
    expected_r_multiple = net_pnl / risk_in_usdt
    
    print(f"Gross PnL: {gross_pnl:.2f} USDT")
    print(f"Total costs: {total_costs:.2f} USDT")
    print(f"Net PnL: {net_pnl:.2f} USDT")
    print(f"Risk in USDT: {risk_in_usdt:.2f} USDT")
    print(f"Expected R-multiple: {expected_r_multiple:.4f}")
    print(f"Actual R-multiple: {result['r_multiple']:.4f}")
    
    # Verify R-multiple calculation
    assert abs(result['r_multiple'] - expected_r_multiple) < 0.001, f"R-multiple {result['r_multiple']} should equal {expected_r_multiple}"
    assert result['r_multiple'] < 0, "R-multiple should be negative for losing trade"
    
    print("Negative PnL R-multiple test passed")


def test_r_multiple_with_costs():
    """Test R-multiple calculation includes trading costs."""
    print("\nTesting R-multiple includes trading costs...")
    
    from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleBacktester
    
    # Test with high costs to make the effect obvious
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
        'commission_rate': 0.01,  # 1% commission (high)
        'slippage_rate': 0.005,   # 0.5% slippage (high)
        'initial_capital': 1000.0,
        'leverage': 1.0
    }
    
    backtester = SimpleBacktester(config)
    
    trade_params = {
        'entry_price': 50000.0,
        'stop_loss': 49500.0,
        'take_profit': 51000.0,
        'position_size': 0.1,
        'entry_time': datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    }
    
    # Create test data for a winning trade
    timestamps = [
        datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        datetime(2024, 1, 15, 12, 15, 0, tzinfo=timezone.utc),
    ]
    
    data = {
        'open': [50000, 50800],
        'high': [50100, 51050],  # TP hit
        'low': [49900, 50700],
        'close': [50200, 51000],
        'volume': [1000, 1500]
    }
    
    day_data = pd.DataFrame(data, index=timestamps)
    
    result = backtester.simulate_trade_exit(trade_params, 'long', day_data)
    
    # Calculate costs
    entry_price = 50000.0
    exit_price = 51000.0
    position_size = 0.1
    
    gross_pnl = (exit_price - entry_price) * position_size  # 100 USDT
    
    # High costs
    per_leg_commission = (0.01 / 2)  # 0.005 per leg
    per_leg_slippage = (0.005 / 2)   # 0.0025 per leg
    
    entry_cost = entry_price * position_size * (per_leg_commission + per_leg_slippage)
    exit_cost = exit_price * position_size * (per_leg_commission + per_leg_slippage)
    total_costs = entry_cost + exit_cost
    
    net_pnl = gross_pnl - total_costs
    risk_in_usdt = abs(entry_price - trade_params['stop_loss']) * position_size
    expected_r_multiple = net_pnl / risk_in_usdt
    
    print(f"Gross PnL: {gross_pnl:.2f} USDT")
    print(f"Total costs: {total_costs:.2f} USDT")
    print(f"Net PnL: {net_pnl:.2f} USDT")
    print(f"Expected R-multiple: {expected_r_multiple:.4f}")
    print(f"Actual R-multiple: {result['r_multiple']:.4f}")
    
    # With high costs, net PnL should be significantly lower than gross PnL
    assert total_costs > 0, "Costs should be positive"
    assert net_pnl < gross_pnl, "Net PnL should be lower than gross PnL due to costs"
    assert abs(result['r_multiple'] - expected_r_multiple) < 0.001, f"R-multiple should account for costs"
    
    print("R-multiple with costs test passed")


def main():
    """Run all R-multiple tests."""
    print("Starting R-multiple calculation tests...")
    print("=" * 50)
    
    try:
        test_r_multiple_positive_pnl()
        test_r_multiple_negative_pnl()
        test_r_multiple_with_costs()
        
        print("\n" + "=" * 50)
        print("All R-multiple calculation tests passed!")
        print("\nSummary:")
        print("[OK] R-multiple correctly calculated using net PnL")
        print("[OK] Positive net PnL results in positive R-multiple")
        print("[OK] Negative net PnL results in negative R-multiple")
        print("[OK] Trading costs are properly included in calculation")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

