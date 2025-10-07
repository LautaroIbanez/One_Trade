#!/usr/bin/env python3
"""
Parametrized unit tests for metrics calculation with inversion support.
Tests the pure metrics helper with both normal and inverted datasets.
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


def create_test_dataset_normal():
    """Create a test dataset with known metrics for normal mode."""
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


def create_test_dataset_mixed():
    """Create a test dataset with mixed wins and losses."""
    trades_data = [
        {'day_key': '2024-01-15', 'entry_time': '2024-01-15T12:00:00Z', 'side': 'long', 'entry_price': 50000.0, 'sl': 49500.0, 'tp': 51000.0, 'exit_time': '2024-01-15T18:00:00Z', 'exit_price': 51000.0, 'exit_reason': 'take_profit', 'pnl_usdt': 200.0, 'r_multiple': 2.0, 'used_fallback': False},
        {'day_key': '2024-01-16', 'entry_time': '2024-01-16T12:00:00Z', 'side': 'short', 'entry_price': 51000.0, 'sl': 51500.0, 'tp': 50000.0, 'exit_time': '2024-01-16T18:00:00Z', 'exit_price': 50000.0, 'exit_reason': 'take_profit', 'pnl_usdt': 100.0, 'r_multiple': 1.0, 'used_fallback': False},
        {'day_key': '2024-01-17', 'entry_time': '2024-01-17T12:00:00Z', 'side': 'long', 'entry_price': 50000.0, 'sl': 49500.0, 'tp': 51000.0, 'exit_time': '2024-01-17T18:00:00Z', 'exit_price': 49500.0, 'exit_reason': 'stop_loss', 'pnl_usdt': -100.0, 'r_multiple': -1.0, 'used_fallback': False},
        {'day_key': '2024-01-18', 'entry_time': '2024-01-18T12:00:00Z', 'side': 'short', 'entry_price': 50000.0, 'sl': 50500.0, 'tp': 49000.0, 'exit_time': '2024-01-18T18:00:00Z', 'exit_price': 50500.0, 'exit_reason': 'stop_loss', 'pnl_usdt': -50.0, 'r_multiple': -0.5, 'used_fallback': False},
        {'day_key': '2024-01-19', 'entry_time': '2024-01-19T12:00:00Z', 'side': 'long', 'entry_price': 50000.0, 'sl': 49500.0, 'tp': 51000.0, 'exit_time': '2024-01-19T18:00:00Z', 'exit_price': 51000.0, 'exit_reason': 'take_profit', 'pnl_usdt': 150.0, 'r_multiple': 1.5, 'used_fallback': False}
    ]
    return pd.DataFrame(trades_data)


def create_test_dataset_all_wins():
    """Create a test dataset with all winning trades."""
    trades_data = [
        {'day_key': '2024-01-15', 'entry_time': '2024-01-15T12:00:00Z', 'side': 'long', 'entry_price': 50000.0, 'sl': 49500.0, 'tp': 51000.0, 'exit_time': '2024-01-15T18:00:00Z', 'exit_price': 51000.0, 'exit_reason': 'take_profit', 'pnl_usdt': 100.0, 'r_multiple': 2.0, 'used_fallback': False},
        {'day_key': '2024-01-16', 'entry_time': '2024-01-16T12:00:00Z', 'side': 'short', 'entry_price': 51000.0, 'sl': 51500.0, 'tp': 50000.0, 'exit_time': '2024-01-16T18:00:00Z', 'exit_price': 50000.0, 'exit_reason': 'take_profit', 'pnl_usdt': 100.0, 'r_multiple': 2.0, 'used_fallback': False},
        {'day_key': '2024-01-17', 'entry_time': '2024-01-17T12:00:00Z', 'side': 'long', 'entry_price': 50000.0, 'sl': 49500.0, 'tp': 51000.0, 'exit_time': '2024-01-17T18:00:00Z', 'exit_price': 51000.0, 'exit_reason': 'take_profit', 'pnl_usdt': 100.0, 'r_multiple': 2.0, 'used_fallback': False}
    ]
    return pd.DataFrame(trades_data)


def create_test_dataset_all_losses():
    """Create a test dataset with all losing trades."""
    trades_data = [
        {'day_key': '2024-01-15', 'entry_time': '2024-01-15T12:00:00Z', 'side': 'long', 'entry_price': 50000.0, 'sl': 49500.0, 'tp': 51000.0, 'exit_time': '2024-01-15T18:00:00Z', 'exit_price': 49500.0, 'exit_reason': 'stop_loss', 'pnl_usdt': -100.0, 'r_multiple': -2.0, 'used_fallback': False},
        {'day_key': '2024-01-16', 'entry_time': '2024-01-16T12:00:00Z', 'side': 'short', 'entry_price': 51000.0, 'sl': 51500.0, 'tp': 50000.0, 'exit_time': '2024-01-16T18:00:00Z', 'exit_price': 51500.0, 'exit_reason': 'stop_loss', 'pnl_usdt': -100.0, 'r_multiple': -2.0, 'used_fallback': False},
        {'day_key': '2024-01-17', 'entry_time': '2024-01-17T12:00:00Z', 'side': 'long', 'entry_price': 50000.0, 'sl': 49500.0, 'tp': 51000.0, 'exit_time': '2024-01-17T18:00:00Z', 'exit_price': 49500.0, 'exit_reason': 'stop_loss', 'pnl_usdt': -100.0, 'r_multiple': -2.0, 'used_fallback': False}
    ]
    return pd.DataFrame(trades_data)


# Test cases for parametrized testing
TEST_CASES = [
    {
        "name": "normal_dataset",
        "dataset": create_test_dataset_normal(),
        "expected_normal": {
            "total_trades": 3,
            "win_rate": 66.67,  # 2 wins out of 3 trades
            "total_pnl": 150.0,  # 100 + 100 - 50
            "avg_pnl": 50.0,  # 150 / 3
            "best_trade": 100.0,
            "worst_trade": -50.0,
            "profit_factor": 4.0,  # 200 / 50 (gross_profit / gross_loss)
            "expectancy": 50.0
        },
        "expected_inverted": {
            "total_trades": 3,
            "win_rate": 33.33,  # 1 win out of 3 trades (inverted)
            "total_pnl": -150.0,  # -100 - 100 + 50
            "avg_pnl": -50.0,  # -150 / 3
            "best_trade": 50.0,
            "worst_trade": -100.0,
            "profit_factor": 0.25,  # 50 / 200 (inverted: gross_profit / gross_loss)
            "expectancy": -50.0
        }
    },
    {
        "name": "mixed_dataset",
        "dataset": create_test_dataset_mixed(),
        "expected_normal": {
            "total_trades": 5,
            "win_rate": 60.0,  # 3 wins out of 5 trades
            "total_pnl": 300.0,  # 200 + 100 - 100 - 50 + 150
            "avg_pnl": 60.0,  # 300 / 5
            "best_trade": 200.0,
            "worst_trade": -100.0,
            "profit_factor": 3.0,  # 450 / 150
            "expectancy": 60.0
        },
        "expected_inverted": {
            "total_trades": 5,
            "win_rate": 40.0,  # 2 wins out of 5 trades (inverted)
            "total_pnl": -300.0,  # -200 - 100 + 100 + 50 - 150
            "avg_pnl": -60.0,  # -300 / 5
            "best_trade": 100.0,
            "worst_trade": -200.0,
            "profit_factor": 0.33,  # 150 / 450
            "expectancy": -60.0
        }
    },
    {
        "name": "all_wins_dataset",
        "dataset": create_test_dataset_all_wins(),
        "expected_normal": {
            "total_trades": 3,
            "win_rate": 100.0,  # 3 wins out of 3 trades
            "total_pnl": 300.0,  # 100 + 100 + 100
            "avg_pnl": 100.0,  # 300 / 3
            "best_trade": 100.0,
            "worst_trade": 100.0,
            "profit_factor": float('inf'),  # No losses
            "expectancy": 100.0
        },
        "expected_inverted": {
            "total_trades": 3,
            "win_rate": 0.0,  # 0 wins out of 3 trades (inverted)
            "total_pnl": -300.0,  # -100 - 100 - 100
            "avg_pnl": -100.0,  # -300 / 3
            "best_trade": -100.0,
            "worst_trade": -100.0,
            "profit_factor": 0.0,  # No profits
            "expectancy": -100.0
        }
    },
    {
        "name": "all_losses_dataset",
        "dataset": create_test_dataset_all_losses(),
        "expected_normal": {
            "total_trades": 3,
            "win_rate": 0.0,  # 0 wins out of 3 trades
            "total_pnl": -300.0,  # -100 - 100 - 100
            "avg_pnl": -100.0,  # -300 / 3
            "best_trade": -100.0,
            "worst_trade": -100.0,
            "profit_factor": 0.0,  # No profits
            "expectancy": -100.0
        },
        "expected_inverted": {
            "total_trades": 3,
            "win_rate": 100.0,  # 3 wins out of 3 trades (inverted)
            "total_pnl": 300.0,  # 100 + 100 + 100
            "avg_pnl": 100.0,  # 300 / 3
            "best_trade": 100.0,
            "worst_trade": 100.0,
            "profit_factor": float('inf'),  # No losses
            "expectancy": 100.0
        }
    }
]


def test_metrics_calculation_normal_mode():
    """Test metrics calculation in normal mode."""
    print("Testing metrics calculation in normal mode...")
    
    from webapp.app import compute_metrics_pure
    
    for test_case in TEST_CASES:
        print(f"  Testing {test_case['name']}...")
        
        # Calculate metrics in normal mode
        metrics = compute_metrics_pure(test_case['dataset'], 1000.0, 1.0, invertido=False)
        expected = test_case['expected_normal']
        
        # Check key metrics
        assert metrics['total_trades'] == expected['total_trades'], f"Total trades mismatch for {test_case['name']}"
        assert abs(metrics['win_rate'] - expected['win_rate']) < 0.1, f"Win rate mismatch for {test_case['name']}: {metrics['win_rate']} vs {expected['win_rate']}"
        assert abs(metrics['total_pnl'] - expected['total_pnl']) < 0.01, f"Total PnL mismatch for {test_case['name']}: {metrics['total_pnl']} vs {expected['total_pnl']}"
        assert abs(metrics['avg_pnl'] - expected['avg_pnl']) < 0.01, f"Avg PnL mismatch for {test_case['name']}: {metrics['avg_pnl']} vs {expected['avg_pnl']}"
        assert abs(metrics['best_trade'] - expected['best_trade']) < 0.01, f"Best trade mismatch for {test_case['name']}: {metrics['best_trade']} vs {expected['best_trade']}"
        assert abs(metrics['worst_trade'] - expected['worst_trade']) < 0.01, f"Worst trade mismatch for {test_case['name']}: {metrics['worst_trade']} vs {expected['worst_trade']}"
        assert abs(metrics['expectancy'] - expected['expectancy']) < 0.01, f"Expectancy mismatch for {test_case['name']}: {metrics['expectancy']} vs {expected['expectancy']}"
        
        # Handle special cases for profit factor
        if expected['profit_factor'] == float('inf'):
            assert metrics['profit_factor'] == float('inf'), f"Profit factor should be inf for {test_case['name']}"
        else:
            assert abs(metrics['profit_factor'] - expected['profit_factor']) < 0.01, f"Profit factor mismatch for {test_case['name']}: {metrics['profit_factor']} vs {expected['profit_factor']}"
    
    print("✅ Normal mode metrics calculation test passed")


def test_metrics_calculation_inverted_mode():
    """Test metrics calculation in inverted mode."""
    print("Testing metrics calculation in inverted mode...")
    
    from webapp.app import compute_metrics_pure
    
    for test_case in TEST_CASES:
        print(f"  Testing {test_case['name']}...")
        
        # Calculate metrics in inverted mode
        metrics = compute_metrics_pure(test_case['dataset'], 1000.0, 1.0, invertido=True)
        expected = test_case['expected_inverted']
        
        # Check key metrics
        assert metrics['total_trades'] == expected['total_trades'], f"Total trades mismatch for {test_case['name']}"
        assert abs(metrics['win_rate'] - expected['win_rate']) < 0.1, f"Win rate mismatch for {test_case['name']}: {metrics['win_rate']} vs {expected['win_rate']}"
        assert abs(metrics['total_pnl'] - expected['total_pnl']) < 0.01, f"Total PnL mismatch for {test_case['name']}: {metrics['total_pnl']} vs {expected['total_pnl']}"
        assert abs(metrics['avg_pnl'] - expected['avg_pnl']) < 0.01, f"Avg PnL mismatch for {test_case['name']}: {metrics['avg_pnl']} vs {expected['avg_pnl']}"
        assert abs(metrics['best_trade'] - expected['best_trade']) < 0.01, f"Best trade mismatch for {test_case['name']}: {metrics['best_trade']} vs {expected['best_trade']}"
        assert abs(metrics['worst_trade'] - expected['worst_trade']) < 0.01, f"Worst trade mismatch for {test_case['name']}: {metrics['worst_trade']} vs {expected['worst_trade']}"
        assert abs(metrics['expectancy'] - expected['expectancy']) < 0.01, f"Expectancy mismatch for {test_case['name']}: {metrics['expectancy']} vs {expected['expectancy']}"
        
        # Handle special cases for profit factor
        if expected['profit_factor'] == float('inf'):
            assert metrics['profit_factor'] == float('inf'), f"Profit factor should be inf for {test_case['name']}"
        elif expected['profit_factor'] == 0.0:
            assert metrics['profit_factor'] == 0.0, f"Profit factor should be 0 for {test_case['name']}"
        else:
            assert abs(metrics['profit_factor'] - expected['profit_factor']) < 0.01, f"Profit factor mismatch for {test_case['name']}: {metrics['profit_factor']} vs {expected['profit_factor']}"
    
    print("✅ Inverted mode metrics calculation test passed")


def test_metrics_consistency():
    """Test that metrics are consistent between normal and inverted modes.
    
    NOTE: This test validates the NEW behavior where:
    - Win rate reflects the actual win percentage of inverted trades (not 100 - win_rate)
    - All metrics maintain standard interpretation
    - Max drawdown always remains negative (magnitude-sensitive)
    """
    print("Testing metrics consistency...")
    
    from webapp.app import compute_metrics_pure
    
    for test_case in TEST_CASES:
        print(f"  Testing {test_case['name']}...")
        
        # Calculate metrics in normal mode
        normal_metrics = compute_metrics_pure(test_case['dataset'], 1000.0, 1.0, invertido=False)
        
        # Calculate metrics in inverted mode
        inverted_metrics = compute_metrics_pure(test_case['dataset'], 1000.0, 1.0, invertido=True)
        
        # Test consistency: total_trades should be the same
        assert normal_metrics['total_trades'] == inverted_metrics['total_trades'], "Total trades should be the same"
        
        # NEW BEHAVIOR: win_rate reflects actual win percentage of inverted trades
        # This should match the expected_inverted win_rate from test cases
        expected_inverted = test_case['expected_inverted']
        assert abs(inverted_metrics['win_rate'] - expected_inverted['win_rate']) < 0.1, f"Win rate should reflect inverted trades actual win rate: {inverted_metrics['win_rate']} vs {expected_inverted['win_rate']}"
        
        # Test consistency: total_pnl should be inverted (directional metric)
        expected_inverted_pnl = -normal_metrics['total_pnl']
        assert abs(inverted_metrics['total_pnl'] - expected_inverted_pnl) < 0.01, "Total PnL should be inverted"
        
        # Test consistency: avg_pnl should be inverted (directional metric)
        expected_inverted_avg_pnl = -normal_metrics['avg_pnl']
        assert abs(inverted_metrics['avg_pnl'] - expected_inverted_avg_pnl) < 0.01, "Avg PnL should be inverted"
        
        # Test consistency: expectancy should be inverted (directional metric)
        expected_inverted_expectancy = -normal_metrics['expectancy']
        assert abs(inverted_metrics['expectancy'] - expected_inverted_expectancy) < 0.01, "Expectancy should be inverted"
        
        # Test consistency: max_drawdown should always be negative (magnitude-sensitive)
        assert inverted_metrics['max_drawdown'] <= 0, "Max drawdown should always be negative or zero"
    
    print("✅ Metrics consistency test passed")


def test_empty_dataset():
    """Test metrics calculation with empty dataset."""
    print("Testing empty dataset...")
    
    from webapp.app import compute_metrics_pure
    
    empty_df = pd.DataFrame()
    
    # Test normal mode
    normal_metrics = compute_metrics_pure(empty_df, 1000.0, 1.0, invertido=False)
    assert normal_metrics['total_trades'] == 0, "Total trades should be 0 for empty dataset"
    assert normal_metrics['win_rate'] == 0.0, "Win rate should be 0 for empty dataset"
    assert normal_metrics['total_pnl'] == 0.0, "Total PnL should be 0 for empty dataset"
    assert normal_metrics['current_capital'] == 1000.0, "Current capital should equal initial capital for empty dataset"
    
    # Test inverted mode
    inverted_metrics = compute_metrics_pure(empty_df, 1000.0, 1.0, invertido=True)
    assert inverted_metrics['total_trades'] == 0, "Total trades should be 0 for empty dataset"
    assert inverted_metrics['win_rate'] == 0.0, "Win rate should be 0 for empty dataset"
    assert inverted_metrics['total_pnl'] == 0.0, "Total PnL should be 0 for empty dataset"
    assert inverted_metrics['current_capital'] == 1000.0, "Current capital should equal initial capital for empty dataset"
    
    print("✅ Empty dataset test passed")


def main():
    """Run all parametrized metrics tests."""
    print("Starting parametrized metrics tests...")
    print("=" * 70)
    
    try:
        test_metrics_calculation_normal_mode()
        test_metrics_calculation_inverted_mode()
        test_metrics_consistency()
        test_empty_dataset()
        
        print("\n" + "=" * 70)
        print("All parametrized metrics tests passed!")
        print("\nSummary:")
        print("- Normal mode metrics calculation works correctly")
        print("- Inverted mode metrics calculation works correctly")
        print("- Metrics consistency between modes is maintained")
        print("- Empty dataset handling works correctly")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
