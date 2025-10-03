#!/usr/bin/env python3
"""
Pruebas para validaciones de win rate, PnL y R del backtester.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backtester import BacktestResults


class TestBacktestValidation(unittest.TestCase):
    """Test cases for backtest validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data with known performance characteristics
        self.test_data = self._create_test_data()
        
        # Base configuration
        self.base_config = {
            'min_win_rate': 80.0,
            'min_pnl': 0.0,
            'min_avg_r': 1.0,
            'min_trades': 10,
            'min_profit_factor': 1.2
        }
    
    def _create_test_data(self):
        """Create synthetic test data with known performance."""
        # Create 20 trades with known characteristics
        trades = []
        
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
        
        return pd.DataFrame(trades)
    
    def test_validation_passes_with_good_performance(self):
        """Test that validation passes with good performance."""
        config = self.base_config.copy()
        results = BacktestResults(self.test_data, config)
        
        # Should pass validation
        self.assertTrue(results.is_strategy_suitable())
        self.assertTrue(results.validation_results['is_valid'])
        self.assertEqual(len(results.validation_results['failed_validations']), 0)
        
        # Check metrics
        self.assertEqual(results.metrics['total_trades'], 20)
        self.assertEqual(results.metrics['win_rate'], 80.0)
        self.assertEqual(results.metrics['total_pnl'], 240.0)  # 16*20 - 4*20
        self.assertEqual(results.metrics['avg_r_multiple'], 0.6)  # (16*1.0 - 4*1.0) / 20
        self.assertEqual(results.metrics['profit_factor'], 4.0)  # 320 / 80
    
    def test_validation_fails_with_low_win_rate(self):
        """Test that validation fails with low win rate."""
        # Create data with low win rate
        trades = []
        
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
        
        data = pd.DataFrame(trades)
        config = self.base_config.copy()
        results = BacktestResults(data, config)
        
        # Should fail validation
        self.assertFalse(results.is_strategy_suitable())
        self.assertFalse(results.validation_results['is_valid'])
        self.assertGreater(len(results.validation_results['failed_validations']), 0)
        
        # Check that win rate failure is reported
        failures = results.validation_results['failed_validations']
        win_rate_failure = any('Win rate' in failure for failure in failures)
        self.assertTrue(win_rate_failure)
        
        # Check metrics
        self.assertEqual(results.metrics['total_trades'], 20)
        self.assertEqual(results.metrics['win_rate'], 25.0)
        self.assertEqual(results.metrics['total_pnl'], -200.0)  # 5*20 - 15*20
        self.assertEqual(results.metrics['avg_r_multiple'], -0.5)  # (5*1.0 - 15*1.0) / 20
    
    def test_validation_fails_with_negative_pnl(self):
        """Test that validation fails with negative PnL."""
        # Create data with negative PnL
        trades = []
        
        # 8 winning trades
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
        
        data = pd.DataFrame(trades)
        config = self.base_config.copy()
        results = BacktestResults(data, config)
        
        # Should fail validation
        self.assertFalse(results.is_strategy_suitable())
        self.assertFalse(results.validation_results['is_valid'])
        
        # Check that PnL failure is reported
        failures = results.validation_results['failed_validations']
        pnl_failure = any('Total PnL' in failure for failure in failures)
        self.assertTrue(pnl_failure)
        
        # Check metrics
        self.assertEqual(results.metrics['total_trades'], 20)
        self.assertEqual(results.metrics['win_rate'], 40.0)
        self.assertEqual(results.metrics['total_pnl'], -120.0)  # 8*15 - 12*20
        self.assertEqual(results.metrics['avg_r_multiple'], -0.3)  # (8*0.75 - 12*1.0) / 20
    
    def test_validation_fails_with_low_avg_r(self):
        """Test that validation fails with low average R-multiple."""
        # Create data with low average R-multiple
        trades = []
        
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
        
        data = pd.DataFrame(trades)
        config = self.base_config.copy()
        results = BacktestResults(data, config)
        
        # Should fail validation
        self.assertFalse(results.is_strategy_suitable())
        self.assertFalse(results.validation_results['is_valid'])
        
        # Check that R-multiple failure is reported
        failures = results.validation_results['failed_validations']
        r_failure = any('Average R-multiple' in failure for failure in failures)
        self.assertTrue(r_failure)
        
        # Check metrics
        self.assertEqual(results.metrics['total_trades'], 20)
        self.assertEqual(results.metrics['win_rate'], 50.0)
        self.assertEqual(results.metrics['total_pnl'], -150.0)  # 10*5 - 10*20
        self.assertEqual(results.metrics['avg_r_multiple'], -0.375)  # (10*0.25 - 10*1.0) / 20
    
    def test_validation_warnings(self):
        """Test that validation generates appropriate warnings."""
        # Create data with few trades
        trades = []
        
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
        
        data = pd.DataFrame(trades)
        config = self.base_config.copy()
        results = BacktestResults(data, config)
        
        # Should pass validation but have warnings
        self.assertTrue(results.is_strategy_suitable())
        self.assertTrue(results.validation_results['is_valid'])
        self.assertGreater(len(results.validation_results['warnings']), 0)
        
        # Check that trade count warning is reported
        warnings = results.validation_results['warnings']
        trade_warning = any('Only 5 trades' in warning for warning in warnings)
        self.assertTrue(trade_warning)
    
    def test_validation_with_empty_data(self):
        """Test validation with empty data."""
        empty_data = pd.DataFrame()
        config = self.base_config.copy()
        results = BacktestResults(empty_data, config)
        
        # Should fail validation
        self.assertFalse(results.is_strategy_suitable())
        self.assertFalse(results.validation_results['is_valid'])
        
        # Check metrics
        self.assertEqual(results.metrics['total_trades'], 0)
        self.assertEqual(results.metrics['win_rate'], 0.0)
        self.assertEqual(results.metrics['total_pnl'], 0.0)
        self.assertEqual(results.metrics['avg_r_multiple'], 0.0)
    
    def test_validation_summary_format(self):
        """Test that validation summary is properly formatted."""
        config = self.base_config.copy()
        results = BacktestResults(self.test_data, config)
        
        summary = results.get_validation_summary()
        
        # Should contain key elements
        self.assertIn('Strategy PASSED validation', summary)
        self.assertIn('Warnings:', summary)
        
        # Test with failing validation
        failing_data = self.test_data.copy()
        failing_data['pnl_usdt'] = -failing_data['pnl_usdt']  # Make all trades losing
        
        failing_results = BacktestResults(failing_data, config)
        failing_summary = failing_results.get_validation_summary()
        
        self.assertIn('Strategy FAILED validation', failing_summary)
        self.assertIn('Failed validations:', failing_summary)
    
    def test_metrics_calculation_accuracy(self):
        """Test that metrics are calculated accurately."""
        config = self.base_config.copy()
        results = BacktestResults(self.test_data, config)
        
        # Verify all metrics
        self.assertEqual(results.metrics['total_trades'], 20)
        self.assertEqual(results.metrics['winning_trades'], 16)
        self.assertEqual(results.metrics['losing_trades'], 4)
        self.assertEqual(results.metrics['win_rate'], 80.0)
        self.assertEqual(results.metrics['total_pnl'], 240.0)
        self.assertEqual(results.metrics['avg_r_multiple'], 0.6)
        self.assertEqual(results.metrics['profit_factor'], 4.0)
        self.assertEqual(results.metrics['expectancy'], 12.0)  # 240 / 20
        self.assertEqual(results.metrics['max_consecutive_losses'], 0)  # No consecutive losses in test data
        self.assertEqual(results.metrics['green_days_pct'], 100.0)  # All days are green
    
    def test_consecutive_losses_calculation(self):
        """Test consecutive losses calculation."""
        # Create data with consecutive losses
        trades = []
        
        # 3 consecutive losing trades
        for i in range(3):
            trades.append({
                'day_key': f'2024-01-{i+1:02d}',
                'entry_time': datetime(2024, 1, i+1, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+1, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 98.0,
                'exit_reason': 'stop_loss',
                'pnl_usdt': -20.0,
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': -1.0
            })
        
        # 1 winning trade
        trades.append({
            'day_key': '2024-01-04',
            'entry_time': datetime(2024, 1, 4, 12, 0, 0, tzinfo=timezone.utc),
            'side': 'long',
            'entry_price': 100.0,
            'sl': 98.0,
            'tp': 102.0,
            'exit_time': datetime(2024, 1, 4, 18, 0, 0, tzinfo=timezone.utc),
            'exit_price': 102.0,
            'exit_reason': 'take_profit',
            'pnl_usdt': 20.0,
            'position_size': 10.0,
            'strategy_used': 'orb',
            'used_fallback': False,
            'r_multiple': 1.0
        })
        
        # 2 more consecutive losing trades
        for i in range(2):
            trades.append({
                'day_key': f'2024-01-{i+5:02d}',
                'entry_time': datetime(2024, 1, i+5, 12, 0, 0, tzinfo=timezone.utc),
                'side': 'long',
                'entry_price': 100.0,
                'sl': 98.0,
                'tp': 102.0,
                'exit_time': datetime(2024, 1, i+5, 18, 0, 0, tzinfo=timezone.utc),
                'exit_price': 98.0,
                'exit_reason': 'stop_loss',
                'pnl_usdt': -20.0,
                'position_size': 10.0,
                'strategy_used': 'orb',
                'used_fallback': False,
                'r_multiple': -1.0
            })
        
        data = pd.DataFrame(trades)
        config = self.base_config.copy()
        results = BacktestResults(data, config)
        
        # Should have 3 consecutive losses (the first sequence)
        self.assertEqual(results.metrics['max_consecutive_losses'], 3)


if __name__ == '__main__':
    unittest.main()
