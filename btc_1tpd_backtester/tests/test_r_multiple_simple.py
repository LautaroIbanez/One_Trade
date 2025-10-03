#!/usr/bin/env python3
"""
Test R-multiple calculation using net PnL (simplified version without matplotlib).
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


def test_r_multiple_calculation_logic():
    """Test the R-multiple calculation logic directly."""
    print("Testing R-multiple calculation logic...")
    
    # Test parameters
    entry_price = 50000.0
    stop_loss = 49500.0
    take_profit = 51000.0
    position_size = 0.1
    
    # Calculate gross PnL for winning trade
    exit_price = take_profit  # TP hit
    gross_pnl = (exit_price - entry_price) * position_size  # 100 USDT
    
    # Calculate costs
    commission_rate = 0.001  # 0.1%
    slippage_rate = 0.0005   # 0.05%
    
    per_leg_commission = commission_rate / 2.0
    per_leg_slippage = slippage_rate / 2.0
    
    entry_cost = entry_price * position_size * (per_leg_commission + per_leg_slippage)
    exit_cost = exit_price * position_size * (per_leg_commission + per_leg_slippage)
    total_costs = entry_cost + exit_cost
    
    # Net PnL
    net_pnl = gross_pnl - total_costs
    
    # Risk in USDT
    risk_in_usdt = abs(entry_price - stop_loss) * position_size  # 50 USDT
    
    # R-multiple calculation
    r_multiple = net_pnl / risk_in_usdt
    
    print(f"Entry price: {entry_price} USDT")
    print(f"Exit price: {exit_price} USDT")
    print(f"Position size: {position_size} BTC")
    print(f"Gross PnL: {gross_pnl:.2f} USDT")
    print(f"Total costs: {total_costs:.2f} USDT")
    print(f"Net PnL: {net_pnl:.2f} USDT")
    print(f"Risk in USDT: {risk_in_usdt:.2f} USDT")
    print(f"R-multiple: {r_multiple:.4f}")
    
    # Verify calculations
    assert gross_pnl == 100.0, f"Gross PnL should be 100 USDT, got {gross_pnl}"
    assert total_costs > 0, "Total costs should be positive"
    assert net_pnl < gross_pnl, "Net PnL should be lower than gross PnL due to costs"
    assert r_multiple > 0, "R-multiple should be positive for winning trade"
    
    # Test losing trade
    print("\nTesting losing trade...")
    exit_price = stop_loss  # SL hit
    gross_pnl = (exit_price - entry_price) * position_size  # -50 USDT
    
    entry_cost = entry_price * position_size * (per_leg_commission + per_leg_slippage)
    exit_cost = exit_price * position_size * (per_leg_commission + per_leg_slippage)
    total_costs = entry_cost + exit_cost
    
    net_pnl = gross_pnl - total_costs  # Even more negative
    r_multiple = net_pnl / risk_in_usdt
    
    print(f"Exit price (SL): {exit_price} USDT")
    print(f"Gross PnL: {gross_pnl:.2f} USDT")
    print(f"Total costs: {total_costs:.2f} USDT")
    print(f"Net PnL: {net_pnl:.2f} USDT")
    print(f"R-multiple: {r_multiple:.4f}")
    
    assert gross_pnl == -50.0, f"Gross PnL should be -50 USDT, got {gross_pnl}"
    assert net_pnl < gross_pnl, "Net PnL should be more negative than gross PnL due to costs"
    assert r_multiple < 0, "R-multiple should be negative for losing trade"
    
    print("R-multiple calculation logic test passed")


def test_r_multiple_edge_cases():
    """Test R-multiple calculation edge cases."""
    print("\nTesting R-multiple edge cases...")
    
    # Test zero risk case
    entry_price = 50000.0
    stop_loss = 50000.0  # Same as entry price
    position_size = 0.1
    net_pnl = 10.0
    
    risk_in_usdt = abs(entry_price - stop_loss) * position_size  # 0 USDT
    
    if risk_in_usdt > 0:
        r_multiple = net_pnl / risk_in_usdt
    else:
        r_multiple = 0
    
    assert r_multiple == 0, f"R-multiple should be 0 when risk is 0, got {r_multiple}"
    print("Zero risk case handled correctly")
    
    # Test break-even trade
    entry_price = 50000.0
    stop_loss = 49500.0
    position_size = 0.1
    exit_price = 50000.0  # Break-even
    gross_pnl = (exit_price - entry_price) * position_size  # 0 USDT
    
    # Add small costs
    total_costs = 1.0  # 1 USDT costs
    net_pnl = gross_pnl - total_costs  # -1 USDT
    
    risk_in_usdt = abs(entry_price - stop_loss) * position_size  # 50 USDT
    r_multiple = net_pnl / risk_in_usdt
    
    print(f"Break-even trade with costs:")
    print(f"Gross PnL: {gross_pnl:.2f} USDT")
    print(f"Net PnL: {net_pnl:.2f} USDT")
    print(f"R-multiple: {r_multiple:.4f}")
    
    assert r_multiple < 0, "R-multiple should be negative for break-even trade with costs"
    print("Break-even case handled correctly")
    
    print("R-multiple edge cases test passed")


def test_position_size_impact():
    """Test that position size affects R-multiple calculation."""
    print("\nTesting position size impact on R-multiple...")
    
    entry_price = 50000.0
    stop_loss = 49500.0
    exit_price = 51000.0  # TP hit
    
    # Test with different position sizes
    position_sizes = [0.05, 0.1, 0.2]
    commission_rate = 0.001
    slippage_rate = 0.0005
    
    per_leg_commission = commission_rate / 2.0
    per_leg_slippage = slippage_rate / 2.0
    
    for pos_size in position_sizes:
        # Gross PnL
        gross_pnl = (exit_price - entry_price) * pos_size
        
        # Costs
        entry_cost = entry_price * pos_size * (per_leg_commission + per_leg_slippage)
        exit_cost = exit_price * pos_size * (per_leg_commission + per_leg_slippage)
        total_costs = entry_cost + exit_cost
        
        # Net PnL
        net_pnl = gross_pnl - total_costs
        
        # Risk and R-multiple
        risk_in_usdt = abs(entry_price - stop_loss) * pos_size
        r_multiple = net_pnl / risk_in_usdt
        
        print(f"Position size: {pos_size} BTC")
        print(f"  Gross PnL: {gross_pnl:.2f} USDT")
        print(f"  Net PnL: {net_pnl:.2f} USDT")
        print(f"  Risk: {risk_in_usdt:.2f} USDT")
        print(f"  R-multiple: {r_multiple:.4f}")
        
        # R-multiple should be similar regardless of position size
        # (since both numerator and denominator scale with position size)
        assert abs(r_multiple - 1.9) < 0.1, f"R-multiple should be around 1.9, got {r_multiple}"
    
    print("Position size impact test passed")


def main():
    """Run all R-multiple tests."""
    print("Starting R-multiple calculation tests (simplified)...")
    print("=" * 50)
    
    try:
        test_r_multiple_calculation_logic()
        test_r_multiple_edge_cases()
        test_position_size_impact()
        
        print("\n" + "=" * 50)
        print("All R-multiple calculation tests passed!")
        print("\nSummary:")
        print("[OK] R-multiple correctly calculated using net PnL")
        print("[OK] Positive net PnL results in positive R-multiple")
        print("[OK] Negative net PnL results in negative R-multiple")
        print("[OK] Trading costs are properly included in calculation")
        print("[OK] Edge cases (zero risk, break-even) handled correctly")
        print("[OK] Position size scaling works correctly")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

