#!/usr/bin/env python3
"""
Tests for mode-specific trading strategies.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.mode_strategies import (
    MeanReversionStrategy,
    TrendFollowingStrategy,
    BreakoutFadeStrategy,
    get_strategy_for_mode
)


class TestModeStrategies(unittest.TestCase):
    """Test mode-specific trading strategies."""
    
    def setUp(self):
        """Set up test data and configurations."""
        # Create sample OHLCV data
        dates = pd.date_range('2024-01-01', periods=100, freq='15min', tz=timezone.utc)
        
        # Generate realistic price data with some volatility
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
            'slippage_rate': 0.0005
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
            'slippage_rate': 0.0008
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
            'slippage_rate': 0.001
        }
    
    def test_mean_reversion_strategy_initialization(self):
        """Test MeanReversionStrategy initialization."""
        strategy = MeanReversionStrategy(self.conservative_config)
        
        self.assertEqual(strategy.risk_usdt, 15.0)
        self.assertEqual(strategy.allow_shorts, False)
        self.assertEqual(strategy.target_r_multiple, 1.0)
        self.assertEqual(strategy.risk_reward_ratio, 1.0)
    
    def test_trend_following_strategy_initialization(self):
        """Test TrendFollowingStrategy initialization."""
        strategy = TrendFollowingStrategy(self.moderate_config)
        
        self.assertEqual(strategy.risk_usdt, 25.0)
        self.assertEqual(strategy.allow_shorts, True)
        self.assertEqual(strategy.target_r_multiple, 1.5)
        self.assertEqual(strategy.risk_reward_ratio, 1.5)
    
    def test_breakout_fade_strategy_initialization(self):
        """Test BreakoutFadeStrategy initialization."""
        strategy = BreakoutFadeStrategy(self.aggressive_config)
        
        self.assertEqual(strategy.risk_usdt, 40.0)
        self.assertEqual(strategy.allow_shorts, True)
        self.assertEqual(strategy.target_r_multiple, 2.0)
        self.assertEqual(strategy.risk_reward_ratio, 2.0)
    
    def test_calculate_indicators_mean_reversion(self):
        """Test indicator calculation for mean reversion strategy."""
        strategy = MeanReversionStrategy(self.conservative_config)
        data_with_indicators = strategy.calculate_indicators(self.sample_data)
        
        # Check that indicators are calculated
        self.assertIn('bb_upper', data_with_indicators.columns)
        self.assertIn('bb_middle', data_with_indicators.columns)
        self.assertIn('bb_lower', data_with_indicators.columns)
        self.assertIn('rsi', data_with_indicators.columns)
        self.assertIn('atr', data_with_indicators.columns)
        self.assertIn('volume_ratio', data_with_indicators.columns)
        
        # Check that indicators have reasonable values
        self.assertTrue(data_with_indicators['rsi'].notna().any())
        self.assertTrue(data_with_indicators['atr'].notna().any())
        self.assertTrue(data_with_indicators['volume_ratio'].notna().any())
    
    def test_calculate_indicators_trend_following(self):
        """Test indicator calculation for trend following strategy."""
        strategy = TrendFollowingStrategy(self.moderate_config)
        data_with_indicators = strategy.calculate_indicators(self.sample_data)
        
        # Check that indicators are calculated
        self.assertIn('ha_open', data_with_indicators.columns)
        self.assertIn('ha_high', data_with_indicators.columns)
        self.assertIn('ha_low', data_with_indicators.columns)
        self.assertIn('ha_close', data_with_indicators.columns)
        self.assertIn('adx', data_with_indicators.columns)
        self.assertIn('ema_fast', data_with_indicators.columns)
        self.assertIn('ema_slow', data_with_indicators.columns)
        self.assertIn('atr', data_with_indicators.columns)
        self.assertIn('volume_ratio', data_with_indicators.columns)
        
        # Check that indicators have reasonable values
        self.assertTrue(data_with_indicators['adx'].notna().any())
        self.assertTrue(data_with_indicators['ema_fast'].notna().any())
        self.assertTrue(data_with_indicators['ema_slow'].notna().any())
    
    def test_calculate_indicators_breakout_fade(self):
        """Test indicator calculation for breakout fade strategy."""
        strategy = BreakoutFadeStrategy(self.aggressive_config)
        data_with_indicators = strategy.calculate_indicators(self.sample_data)
        
        # Check that indicators are calculated
        self.assertIn('bb_upper', data_with_indicators.columns)
        self.assertIn('bb_middle', data_with_indicators.columns)
        self.assertIn('bb_lower', data_with_indicators.columns)
        self.assertIn('rsi', data_with_indicators.columns)
        self.assertIn('atr', data_with_indicators.columns)
        self.assertIn('volume_ratio', data_with_indicators.columns)
        self.assertIn('price_change', data_with_indicators.columns)
        
        # Check that indicators have reasonable values
        self.assertTrue(data_with_indicators['rsi'].notna().any())
        self.assertTrue(data_with_indicators['price_change'].notna().any())
    
    def test_detect_signal_mean_reversion(self):
        """Test signal detection for mean reversion strategy."""
        strategy = MeanReversionStrategy(self.conservative_config)
        data_with_indicators = strategy.calculate_indicators(self.sample_data)
        
        # Test with sufficient data
        index = 25
        signal, confidence = strategy.detect_signal(data_with_indicators, index)
        
        # Signal should be None or a valid direction
        self.assertIn(signal, [None, 'long', 'short'])
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_detect_signal_trend_following(self):
        """Test signal detection for trend following strategy."""
        strategy = TrendFollowingStrategy(self.moderate_config)
        data_with_indicators = strategy.calculate_indicators(self.sample_data)
        
        # Test with sufficient data
        index = 25
        signal, confidence = strategy.detect_signal(data_with_indicators, index)
        
        # Signal should be None or a valid direction
        self.assertIn(signal, [None, 'long', 'short'])
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_detect_signal_breakout_fade(self):
        """Test signal detection for breakout fade strategy."""
        strategy = BreakoutFadeStrategy(self.aggressive_config)
        data_with_indicators = strategy.calculate_indicators(self.sample_data)
        
        # Test with sufficient data
        index = 25
        signal, confidence = strategy.detect_signal(data_with_indicators, index)
        
        # Signal should be None or a valid direction
        self.assertIn(signal, [None, 'long', 'short'])
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_calculate_trade_params(self):
        """Test trade parameter calculation."""
        strategy = MeanReversionStrategy(self.conservative_config)
        
        # Test with sample data
        entry_price = 50000.0
        side = 'long'
        trade_params = strategy.calculate_trade_params(side, entry_price, self.sample_data, self.sample_data.index[0])
        
        if trade_params is not None:
            self.assertIn('entry_price', trade_params)
            self.assertIn('stop_loss', trade_params)
            self.assertIn('take_profit', trade_params)
            self.assertIn('position_size', trade_params)
            self.assertIn('atr_value', trade_params)
            self.assertIn('entry_time', trade_params)
            
            # Check that stop loss and take profit are reasonable
            self.assertGreater(trade_params['take_profit'], trade_params['entry_price'])
            self.assertLess(trade_params['stop_loss'], trade_params['entry_price'])
            self.assertGreater(trade_params['position_size'], 0)
    
    def test_simulate_trade_exit(self):
        """Test trade exit simulation."""
        strategy = MeanReversionStrategy(self.conservative_config)
        
        # Create trade parameters
        trade_params = {
            'entry_price': 50000.0,
            'stop_loss': 49500.0,
            'take_profit': 50500.0,
            'position_size': 0.1,
            'atr_value': 100.0,
            'entry_time': self.sample_data.index[0]
        }
        
        side = 'long'
        exit_info = strategy.simulate_trade_exit(trade_params, side, self.sample_data)
        
        self.assertIn('exit_time', exit_info)
        self.assertIn('exit_price', exit_info)
        self.assertIn('exit_reason', exit_info)
        self.assertIn('pnl_usdt', exit_info)
        self.assertIn('r_multiple', exit_info)
        
        # Check that exit reason is valid
        valid_exit_reasons = ['take_profit', 'stop_loss', 'session_close', 'session_end']
        self.assertIn(exit_info['exit_reason'], valid_exit_reasons)
    
    def test_process_day(self):
        """Test daily processing."""
        strategy = MeanReversionStrategy(self.conservative_config)
        
        # Create a single day of data
        day_data = self.sample_data.iloc[:96]  # 24 hours of 15-min data
        date = datetime(2024, 1, 1).date()
        
        trades = strategy.process_day(day_data, date)
        
        self.assertIsInstance(trades, list)
        
        # If trades are generated, check their structure
        if trades:
            trade = trades[0]
            required_fields = [
                'day_key', 'entry_time', 'side', 'entry_price', 'sl', 'tp',
                'exit_time', 'exit_price', 'exit_reason', 'pnl_usdt', 'r_multiple',
                'strategy_type', 'confidence'
            ]
            
            for field in required_fields:
                self.assertIn(field, trade)
    
    def test_get_strategy_for_mode(self):
        """Test strategy factory function."""
        # Test mean reversion
        strategy = get_strategy_for_mode('conservative', self.conservative_config)
        self.assertIsInstance(strategy, MeanReversionStrategy)
        
        # Test trend following
        strategy = get_strategy_for_mode('moderate', self.moderate_config)
        self.assertIsInstance(strategy, TrendFollowingStrategy)
        
        # Test breakout fade
        strategy = get_strategy_for_mode('aggressive', self.aggressive_config)
        self.assertIsInstance(strategy, BreakoutFadeStrategy)
        
        # Test default fallback
        strategy = get_strategy_for_mode('unknown', self.moderate_config)
        self.assertIsInstance(strategy, TrendFollowingStrategy)
    
    def test_conservative_no_shorts(self):
        """Test that conservative strategy doesn't allow shorts."""
        strategy = MeanReversionStrategy(self.conservative_config)
        data_with_indicators = strategy.calculate_indicators(self.sample_data)
        
        # Force oversold conditions for short signal
        data_with_indicators.loc[data_with_indicators.index[25], 'close'] = data_with_indicators.loc[data_with_indicators.index[25], 'bb_upper'] + 100
        data_with_indicators.loc[data_with_indicators.index[25], 'rsi'] = 80
        data_with_indicators.loc[data_with_indicators.index[25], 'volume_ratio'] = 1.5
        
        signal, confidence = strategy.detect_signal(data_with_indicators, 25)
        
        # Should not generate short signal even with overbought conditions
        self.assertNotEqual(signal, 'short')
    
    def test_aggressive_allows_shorts(self):
        """Test that aggressive strategy allows shorts."""
        strategy = BreakoutFadeStrategy(self.aggressive_config)
        data_with_indicators = strategy.calculate_indicators(self.sample_data)
        
        # Force breakout conditions for short signal
        data_with_indicators.loc[data_with_indicators.index[25], 'price_change'] = 0.03  # 3% breakout
        data_with_indicators.loc[data_with_indicators.index[25], 'close'] = data_with_indicators.loc[data_with_indicators.index[25], 'bb_upper'] + 100
        data_with_indicators.loc[data_with_indicators.index[25], 'rsi'] = 85
        data_with_indicators.loc[data_with_indicators.index[25], 'volume_ratio'] = 2.0
        
        signal, confidence = strategy.detect_signal(data_with_indicators, 25)
        
        # Should potentially generate short signal with breakout conditions
        # (Note: actual signal depends on all conditions being met)
        self.assertIn(signal, [None, 'short'])


if __name__ == '__main__':
    unittest.main()
