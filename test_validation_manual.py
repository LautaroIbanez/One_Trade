#!/usr/bin/env python3
"""
Test manual para validaciones de win rate, PnL y R del backtester.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

# Add the btc_1tpd_backtester directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'btc_1tpd_backtester'))

# Import the backtester classes directly
from backtester import BacktestResults


def create_test_data(scenario='good'):
    """Create synthetic test data for different scenarios."""
    trades = []
    
    if scenario == 'good':
        # 16 winning trades (80% win rate)
        for i in range(16):
            trades.append({
                'day_key': f'2024-01-{i+1:02d}',
                'entry_time': datetime(2024, 1, i+1, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+1, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 102.0,
                'exit_reason': 'take_profit',
                'pnl_usdt': 20.0,  # 1R profit
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': 1.0
            })
        
        # 4 losing trades (20% loss rate)
        for i in range(4):
            trades.append({
                'day_key': f'2024-01-{i+17:02d}',
                'entry_time': datetime(2024, 1, i+17, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+17, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 98.0,
                'exit_reason': 'stop_loss',
                'pnl_usdt': -20.0,  # 1R loss
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': -1.0
            })
    
    elif scenario == 'low_win_rate':
        # 5 winning trades (25% win rate)
        for i in range(5):
            trades.append({
                'day_key': f'2024-01-{i+1:02d}',
                'entry_time': datetime(2024, 1, i+1, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+1, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 102.0,
                'exit_reason': 'take_profit',
                'pnl_usdt': 20.0,
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': 1.0
            })
        
        # 15 losing trades (75% loss rate)
        for i in range(15):
            trades.append({
                'day_key': f'2024-01-{i+6:02d}',
                'entry_time': datetime(2024, 1, i+6, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+6, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 98.0,
                'exit_reason': 'stop_loss',
                'pnl_usdt': -20.0,
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': -1.0
            })
    
    elif scenario == 'negative_pnl':
        # 8 winning trades with small profits
        for i in range(8):
            trades.append({
                'day_key': f'2024-01-{i+1:02d}',
                'entry_time': datetime(2024, 1, i+1, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+1, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 102.0,
                'exit_reason': 'take_profit',
                'pnl_usdt': 15.0,  # Smaller profit
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': 0.75
            })
        
        # 12 losing trades
        for i in range(12):
            trades.append({
                'day_key': f'2024-01-{i+9:02d}',
                'entry_time': datetime(2024, 1, i+9, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+9, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 98.0,
                'exit_reason': 'stop_loss',
                'pnl_usdt': -20.0,
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': -1.0
            })
    
    elif scenario == 'low_avg_r':
        # 10 winning trades with low R-multiple
        for i in range(10):
            trades.append({
                'day_key': f'2024-01-{i+1:02d}',
                'entry_time': datetime(2024, 1, i+1, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 100.5,  # Very small profit
                'exit_time': datetime(2024, 1, i+1, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 100.5,
                'exit_reason': 'take_profit',
                'pnl_usdt': 5.0,  # Small profit
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': 0.25  # Low R-multiple
            })
        
        # 10 losing trades
        for i in range(10):
            trades.append({
                'day_key': f'2024-01-{i+11:02d}',
                'entry_time': datetime(2024, 1, i+11, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+11, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 98.0,
                'exit_reason': 'stop_loss',
                'pnl_usdt': -20.0,
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': -1.0
            })
    
    elif scenario == 'few_trades':
        # Only 5 trades (below minimum)
        for i in range(5):
            trades.append({
                'day_key': f'2024-01-{i+1:02d}',
                'entry_time': datetime(2024, 1, i+1, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+1, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 102.0,
                'exit_reason': 'take_profit',
                'pnl_usdt': 20.0,
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': 1.0
            })
    
    elif scenario == 'empty':
        # No trades
        pass
    
    return pd.DataFrame(trades)


def test_validation_scenarios():
    """Test different validation scenarios."""
    print("🧪 Testing Backtest Validation Scenarios")
    print("=" * 60)
    
    # Base configuration
    base_config = {
        'min_win_rate': 80.0,
        'min_pnl': 0.0,
        'min_avg_r': 1.0,
        'min_trades': 10,
        'min_profit_factor': 1.2
    }
    
    scenarios = [
        ('good', 'Good Performance (80% win rate, positive PnL)'),
        ('low_win_rate', 'Low Win Rate (25% win rate)'),
        ('negative_pnl', 'Negative PnL (losing strategy)'),
        ('low_avg_r', 'Low Average R-multiple (0.25R)'),
        ('few_trades', 'Few Trades (5 trades, below minimum)'),
        ('empty', 'Empty Data (no trades)')
    ]
    
    for scenario, description in scenarios:
        print(f"\n📊 Testing: {description}")
        print("-" * 50)
        
        # Create test data
        test_data = create_test_data(scenario)
        
        # Create results
        results = BacktestResults(test_data, base_config)
        
        # Display results
        results.display_summary()
        
        # Check validation
        if results.is_strategy_suitable():
            print("\n✅ Strategy PASSED validation")
        else:
            print("\n❌ Strategy FAILED validation")
        
        print(f"\nValidation Summary:")
        print(results.get_validation_summary())


def test_mode_specific_validation():
    """Test validation with mode-specific thresholds."""
    print("\n🎯 Testing Mode-Specific Validation")
    print("=" * 60)
    
    # Create good test data
    test_data = create_test_data('good')
    
    # Test different mode configurations
    modes = [
        ('conservative', {
            'min_win_rate': 85.0,
            'min_pnl': 0.0,
            'min_avg_r': 1.0,
            'min_trades': 15,
            'min_profit_factor': 1.5
        }),
        ('moderate', {
            'min_win_rate': 80.0,
            'min_pnl': 0.0,
            'min_avg_r': 1.5,
            'min_trades': 12,
            'min_profit_factor': 1.3
        }),
        ('aggressive', {
            'min_win_rate': 75.0,
            'min_pnl': 0.0,
            'min_avg_r': 2.0,
            'min_trades': 10,
            'min_profit_factor': 1.2
        })
    ]
    
    for mode, config in modes:
        print(f"\n🔍 Testing {mode.upper()} mode:")
        print("-" * 30)
        
        results = BacktestResults(test_data, config)
        
        print(f"Win Rate: {results.metrics['win_rate']:.1f}% (min: {config['min_win_rate']}%)")
        print(f"Total PnL: {results.metrics['total_pnl']:.2f} USDT (min: {config['min_pnl']} USDT)")
        print(f"Avg R-Multiple: {results.metrics['avg_r_multiple']:.2f} (min: {config['min_avg_r']})")
        print(f"Total Trades: {results.metrics['total_trades']} (min: {config['min_trades']})")
        print(f"Profit Factor: {results.metrics['profit_factor']:.2f} (min: {config['min_profit_factor']})")
        
        if results.is_strategy_suitable():
            print("✅ PASSED validation")
        else:
            print("❌ FAILED validation")
            print("Failed validations:")
            for failure in results.validation_results['failed_validations']:
                print(f"  - {failure}")
        
        if results.validation_results['warnings']:
            print("Warnings:")
            for warning in results.validation_results['warnings']:
                print(f"  - {warning}")


def test_metrics_calculation():
    """Test metrics calculation accuracy."""
    print("\n📈 Testing Metrics Calculation")
    print("=" * 60)
    
    # Create test data with known values
    test_data = create_test_data('good')
    
    config = {
        'min_win_rate': 80.0,
        'min_pnl': 0.0,
        'min_avg_r': 1.0,
        'min_trades': 10,
        'min_profit_factor': 1.2
    }
    
    results = BacktestResults(test_data, config)
    
    print("Expected vs Actual Metrics:")
    print(f"Total Trades: Expected 20, Actual {results.metrics['total_trades']}")
    print(f"Winning Trades: Expected 16, Actual {results.metrics['winning_trades']}")
    print(f"Losing Trades: Expected 4, Actual {results.metrics['losing_trades']}")
    print(f"Win Rate: Expected 80.0%, Actual {results.metrics['win_rate']:.1f}%")
    print(f"Total PnL: Expected 240.0, Actual {results.metrics['total_pnl']:.1f}")
    print(f"Avg R-Multiple: Expected 0.6, Actual {results.metrics['avg_r_multiple']:.2f}")
    print(f"Profit Factor: Expected 4.0, Actual {results.metrics['profit_factor']:.2f}")
    print(f"Expectancy: Expected 12.0, Actual {results.metrics['expectancy']:.1f}")
    print(f"Max Consecutive Losses: Expected 0, Actual {results.metrics['max_consecutive_losses']}")
    print(f"Green Days %: Expected 100.0%, Actual {results.metrics['green_days_pct']:.1f}%")
    
    # Verify calculations
    assert results.metrics['total_trades'] == 20, "Total trades incorrect"
    assert results.metrics['winning_trades'] == 16, "Winning trades incorrect"
    assert results.metrics['losing_trades'] == 4, "Losing trades incorrect"
    assert results.metrics['win_rate'] == 80.0, "Win rate incorrect"
    assert results.metrics['total_pnl'] == 240.0, "Total PnL incorrect"
    assert results.metrics['avg_r_multiple'] == 0.6, "Avg R-multiple incorrect"
    assert results.metrics['profit_factor'] == 4.0, "Profit factor incorrect"
    assert results.metrics['expectancy'] == 12.0, "Expectancy incorrect"
    assert results.metrics['max_consecutive_losses'] == 4, "Max consecutive losses incorrect"
    assert results.metrics['green_days_pct'] == 80.0, "Green days % incorrect"
    
    print("\n✅ All metrics calculated correctly!")


if __name__ == '__main__':
    test_validation_scenarios()
    test_mode_specific_validation()
    test_metrics_calculation()
