#!/usr/bin/env python3
"""
Integration tests for mode-based strategies with the backtester.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from btc_1tpd_backtest_final import SimpleTradingStrategy, run_backtest
from strategies.mode_strategies import get_strategy_for_mode


class TestModeIntegration(unittest.TestCase):
    """Integration tests for mode-based strategies."""
    
    def setUp(self):
        """Set up test data and configurations."""
        # Create sample OHLCV data for testing
        dates = pd.date_range('2024-01-01', periods=200, freq='15min', tz=timezone.utc)
        
        # Generate realistic price data
        np.random.seed(42)
        base_price = 50000
        returns = np.random.normal(0, 0.001, len(dates))
        prices = base_price * np.exp(np.cumsum(returns))
        
        self.sample_data = pd.DataFrame({
            'open': prices * (1 + np.random.normal(0, 0.0005, len(dates))),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.001, len(dates)))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.001, len(dates)))),
            'close': prices,
            'volume': np.random.uniform(1000, 5000, len(dates))
        }, index=dates)
        
        # Ensure high >= max(open, close) and low <= min(open, close)
        self.sample_data['high'] = np.maximum(
            self.sample_data['high'],
            np.maximum(self.sample_data['open'], self.sample_data['close'])
        )
        self.sample_data['low'] = np.minimum(
            self.sample_data['low'],
            np.minimum(self.sample_data['open'], self.sample_data['close'])
        )
        
        # Conservative config
        self.conservative_config = {
            'risk_usdt': 15.0,
            'strategy_type': 'mean_reversion',
            'bollinger_period': 20,
            'bollinger_std': 2.0,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'atr_period': 14,
            'atr_multiplier': 1.5,
            'volume_threshold': 1.2,
            'target_r_multiple': 1.0,
            'risk_reward_ratio': 1.0,
            'allow_shorts': False,
            'entry_window': (11, 14),
            'exit_window': (20, 22),
            'session_timezone': 'America/Argentina/Buenos_Aires',
            'initial_capital': 1000.0,
            'leverage': 1.0,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005,
            'force_one_trade': True,
            'session_trading': True,
            'full_day_trading': False
        }
        
        # Moderate config
        self.moderate_config = {
            'risk_usdt': 25.0,
            'strategy_type': 'trend_following',
            'heikin_ashi': True,
            'adx_period': 14,
            'adx_threshold': 25,
            'ema_fast': 9,
            'ema_slow': 21,
            'atr_period': 14,
            'atr_multiplier': 2.0,
            'volume_threshold': 1.1,
            'target_r_multiple': 1.5,
            'risk_reward_ratio': 1.5,
            'allow_shorts': True,
            'entry_window': (11, 14),
            'exit_window': (20, 22),
            'session_timezone': 'America/Argentina/Buenos_Aires',
            'initial_capital': 1000.0,
            'leverage': 1.0,
            'commission_rate': 0.0012,
            'slippage_rate': 0.0008,
            'force_one_trade': True,
            'session_trading': True,
            'full_day_trading': False
        }
        
        # Aggressive config
        self.aggressive_config = {
            'risk_usdt': 40.0,
            'strategy_type': 'breakout_fade',
            'breakout_period': 20,
            'breakout_threshold': 0.02,
            'rsi_period': 14,
            'rsi_extreme_high': 80,
            'rsi_extreme_low': 20,
            'bollinger_period': 20,
            'bollinger_std': 2.5,
            'atr_period': 14,
            'atr_multiplier': 2.5,
            'volume_threshold': 1.5,
            'target_r_multiple': 2.0,
            'risk_reward_ratio': 2.0,
            'allow_shorts': True,
            'entry_window': (11, 14),
            'exit_window': (20, 22),
            'session_timezone': 'America/Argentina/Buenos_Aires',
            'initial_capital': 1000.0,
            'leverage': 1.0,
            'commission_rate': 0.0015,
            'slippage_rate': 0.001,
            'force_one_trade': True,
            'session_trading': True,
            'full_day_trading': False
        }
    
    def test_conservative_strategy_integration(self):
        """Test conservative strategy integration with SimpleTradingStrategy."""
        strategy = SimpleTradingStrategy(self.conservative_config)
        
        # Check that mode strategy is created
        self.assertTrue(hasattr(strategy, 'mode_strategy'))
        
        # Test daily processing
        day_data = self.sample_data.iloc[:96]  # 24 hours of 15-min data
        date = datetime(2024, 1, 1).date()
        
        trades = strategy.process_day(day_data, date)
        
        self.assertIsInstance(trades, list)
        
        # If trades are generated, check their structure
        if trades:
            trade = trades[0]
            self.assertEqual(trade['strategy_type'], 'mean_reversion')
            self.assertIn(trade['side'], ['long'])  # Conservative should only do longs
    
    def test_moderate_strategy_integration(self):
        """Test moderate strategy integration with SimpleTradingStrategy."""
        strategy = SimpleTradingStrategy(self.moderate_config)
        
        # Check that mode strategy is created
        self.assertTrue(hasattr(strategy, 'mode_strategy'))
        
        # Test daily processing
        day_data = self.sample_data.iloc[:96]  # 24 hours of 15-min data
        date = datetime(2024, 1, 1).date()
        
        trades = strategy.process_day(day_data, date)
        
        self.assertIsInstance(trades, list)
        
        # If trades are generated, check their structure
        if trades:
            trade = trades[0]
            self.assertEqual(trade['strategy_type'], 'trend_following')
            self.assertIn(trade['side'], ['long', 'short'])  # Moderate allows both
    
    def test_aggressive_strategy_integration(self):
        """Test aggressive strategy integration with SimpleTradingStrategy."""
        strategy = SimpleTradingStrategy(self.aggressive_config)
        
        # Check that mode strategy is created
        self.assertTrue(hasattr(strategy, 'mode_strategy'))
        
        # Test daily processing
        day_data = self.sample_data.iloc[:96]  # 24 hours of 15-min data
        date = datetime(2024, 1, 1).date()
        
        trades = strategy.process_day(day_data, date)
        
        self.assertIsInstance(trades, list)
        
        # If trades are generated, check their structure
        if trades:
            trade = trades[0]
            self.assertEqual(trade['strategy_type'], 'breakout_fade')
            self.assertIn(trade['side'], ['long', 'short'])  # Aggressive allows both
    
    def test_strategy_dispatch(self):
        """Test that correct strategy is dispatched based on config."""
        # Test mean reversion dispatch
        strategy = get_strategy_for_mode('conservative', self.conservative_config)
        self.assertEqual(strategy.config['strategy_type'], 'mean_reversion')
        
        # Test trend following dispatch
        strategy = get_strategy_for_mode('moderate', self.moderate_config)
        self.assertEqual(strategy.config['strategy_type'], 'trend_following')
        
        # Test breakout fade dispatch
        strategy = get_strategy_for_mode('aggressive', self.aggressive_config)
        self.assertEqual(strategy.config['strategy_type'], 'breakout_fade')
    
    def test_risk_management_consistency(self):
        """Test that risk management parameters are consistent across strategies."""
        strategies = [
            SimpleTradingStrategy(self.conservative_config),
            SimpleTradingStrategy(self.moderate_config),
            SimpleTradingStrategy(self.aggressive_config)
        ]
        
        for strategy in strategies:
            if hasattr(strategy, 'mode_strategy'):
                mode_strategy = strategy.mode_strategy
                
                # Check that risk parameters are set correctly
                self.assertGreater(mode_strategy.risk_usdt, 0)
                self.assertGreater(mode_strategy.target_r_multiple, 0)
                self.assertGreater(mode_strategy.risk_reward_ratio, 0)
                self.assertGreater(mode_strategy.max_drawdown, 0)
                self.assertLess(mode_strategy.max_drawdown, 1.0)
    
    def test_session_trading_consistency(self):
        """Test that session trading parameters are consistent."""
        strategies = [
            SimpleTradingStrategy(self.conservative_config),
            SimpleTradingStrategy(self.moderate_config),
            SimpleTradingStrategy(self.aggressive_config)
        ]
        
        for strategy in strategies:
            if hasattr(strategy, 'mode_strategy'):
                mode_strategy = strategy.mode_strategy
                
                # Check session trading parameters
                self.assertIsInstance(mode_strategy.entry_window, tuple)
                self.assertIsInstance(mode_strategy.exit_window, tuple)
                self.assertEqual(len(mode_strategy.entry_window), 2)
                self.assertEqual(len(mode_strategy.exit_window), 2)
                
                # Check that entry window is before exit window
                entry_start, entry_end = mode_strategy.entry_window
                exit_start, exit_end = mode_strategy.exit_window
                
                self.assertLess(entry_start, entry_end)
                self.assertLess(exit_start, exit_end)
                self.assertLessEqual(entry_end, exit_start)
    
    def test_commission_and_slippage_consistency(self):
        """Test that commission and slippage rates are consistent."""
        strategies = [
            SimpleTradingStrategy(self.conservative_config),
            SimpleTradingStrategy(self.moderate_config),
            SimpleTradingStrategy(self.aggressive_config)
        ]
        
        for strategy in strategies:
            if hasattr(strategy, 'mode_strategy'):
                mode_strategy = strategy.mode_strategy
                
                # Check that commission and slippage rates are reasonable
                self.assertGreaterEqual(mode_strategy.commission_rate, 0)
                self.assertLessEqual(mode_strategy.commission_rate, 0.01)  # Max 1%
                self.assertGreaterEqual(mode_strategy.slippage_rate, 0)
                self.assertLessEqual(mode_strategy.slippage_rate, 0.01)  # Max 1%
    
    def test_validation_parameters_consistency(self):
        """Test that validation parameters are consistent."""
        configs = [self.conservative_config, self.moderate_config, self.aggressive_config]
        
        for config in configs:
            # Check that validation parameters exist and are reasonable
            validation_params = [
                'min_win_rate', 'min_avg_r', 'min_trades', 'min_profit_factor'
            ]
            
            for param in validation_params:
                if param in config:
                    value = config[param]
                    if param == 'min_win_rate':
                        self.assertGreaterEqual(value, 50.0)
                        self.assertLessEqual(value, 100.0)
                    elif param == 'min_avg_r':
                        self.assertGreater(value, 0.0)
                    elif param == 'min_trades':
                        self.assertGreater(value, 0)
                    elif param == 'min_profit_factor':
                        self.assertGreater(value, 1.0)


if __name__ == '__main__':
    unittest.main()
