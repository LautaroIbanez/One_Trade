#!/usr/bin/env python3
"""
Pruebas unitarias para la estrategia multifactor.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from strategy_multifactor import MultifactorStrategy


class TestMultifactorStrategy(unittest.TestCase):
    """Test cases for MultifactorStrategy."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'risk_usdt': 20.0,
            'atr_multiplier': 2.0,
            'tp_multiplier': 2.0,
            'min_reliability_score': 0.6,
            'ema_fast': 12,
            'ema_slow': 26,
            'adx_period': 14,
            'adx_min': 25.0,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'volume_confirmation': True,
            'volume_threshold': 1.2,
            'session_trading': True,
            'entry_window': (11, 14),
            'exit_window': (20, 22),
            'session_timezone': 'America/Argentina/Buenos_Aires',
            'force_one_trade': True,
            'max_daily_trades': 1
        }
        
        self.strategy = MultifactorStrategy(self.config)
        
        # Create test data
        self.test_data = self._create_test_data()
    
    def _create_test_data(self):
        """Create synthetic test data."""
        # Create 24 hours of 15-minute data
        start = datetime(2024, 1, 3, 0, 0, 0, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=timezone.utc)
        
        # Create bullish trend with volatility
        base_price = 100.0
        data = []
        
        for i, timestamp in enumerate(idx):
            # Create trend with some volatility
            trend = i * 0.1  # Upward trend
            volatility = np.sin(i * 0.1) * 2.0  # Some volatility
            
            open_price = base_price + trend + volatility
            high_price = open_price + abs(np.random.normal(0, 1))
            low_price = open_price - abs(np.random.normal(0, 1))
            close_price = open_price + np.random.normal(0, 0.5)
            
            # Ensure OHLC consistency
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000.0 + np.random.normal(0, 100)
            })
        
        return pd.DataFrame(data, index=idx)
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.risk_usdt, 20.0)
        self.assertEqual(self.strategy.min_reliability_score, 0.6)
        self.assertEqual(self.strategy.ema_fast, 12)
        self.assertEqual(self.strategy.ema_slow, 26)
        self.assertTrue(self.strategy.volume_confirmation)
        self.assertEqual(self.strategy.entry_window, (11, 14))
        self.assertEqual(self.strategy.exit_window, (20, 22))
    
    def test_calculate_indicators(self):
        """Test indicator calculations."""
        data_with_indicators = self.strategy.calculate_indicators(self.test_data)
        
        # Check that indicators are calculated
        self.assertIn('ema_fast', data_with_indicators.columns)
        self.assertIn('ema_slow', data_with_indicators.columns)
        self.assertIn('adx', data_with_indicators.columns)
        self.assertIn('rsi', data_with_indicators.columns)
        self.assertIn('macd', data_with_indicators.columns)
        self.assertIn('atr', data_with_indicators.columns)
        self.assertIn('vwap', data_with_indicators.columns)
        self.assertIn('volume_confirmation', data_with_indicators.columns)
        
        # Check that indicators have reasonable values
        self.assertFalse(data_with_indicators['ema_fast'].isna().all())
        self.assertFalse(data_with_indicators['ema_slow'].isna().all())
        self.assertFalse(data_with_indicators['atr'].isna().all())
    
    def test_calculate_reliability_score(self):
        """Test reliability score calculation."""
        data_with_indicators = self.strategy.calculate_indicators(self.test_data)
        
        # Test with sufficient data
        test_index = 50  # Should have enough data for all indicators
        reliability = self.strategy.calculate_reliability_score(data_with_indicators, test_index)
        
        # Reliability should be between 0 and 1
        self.assertGreaterEqual(reliability, 0.0)
        self.assertLessEqual(reliability, 1.0)
        
        # Test with insufficient data
        reliability_early = self.strategy.calculate_reliability_score(data_with_indicators, 5)
        self.assertEqual(reliability_early, 0.0)
    
    def test_detect_signal(self):
        """Test signal detection."""
        data_with_indicators = self.strategy.calculate_indicators(self.test_data)
        
        # Test with sufficient data
        test_index = 50
        signal_direction, reliability = self.strategy.detect_signal(data_with_indicators, test_index)
        
        # Signal should be None, 'long', or 'short'
        self.assertIn(signal_direction, [None, 'long', 'short'])
        
        # Reliability should be between 0 and 1
        self.assertGreaterEqual(reliability, 0.0)
        self.assertLessEqual(reliability, 1.0)
        
        # Test with insufficient data
        signal_early, reliability_early = self.strategy.detect_signal(data_with_indicators, 5)
        self.assertIsNone(signal_early)
        self.assertEqual(reliability_early, 0.0)
    
    def test_calculate_trade_params(self):
        """Test trade parameters calculation."""
        data_with_indicators = self.strategy.calculate_indicators(self.test_data)
        
        # Test long trade
        entry_price = 100.0
        entry_time = self.test_data.index[50]
        
        trade_params = self.strategy.calculate_trade_params(
            'long', entry_price, data_with_indicators, entry_time
        )
        
        self.assertIsNotNone(trade_params)
        self.assertEqual(trade_params['entry_price'], entry_price)
        self.assertLess(trade_params['stop_loss'], entry_price)  # SL below entry for long
        self.assertGreater(trade_params['take_profit'], entry_price)  # TP above entry for long
        self.assertGreater(trade_params['position_size'], 0)
        
        # Test short trade
        trade_params_short = self.strategy.calculate_trade_params(
            'short', entry_price, data_with_indicators, entry_time
        )
        
        self.assertIsNotNone(trade_params_short)
        self.assertEqual(trade_params_short['entry_price'], entry_price)
        self.assertGreater(trade_params_short['stop_loss'], entry_price)  # SL above entry for short
        self.assertLess(trade_params_short['take_profit'], entry_price)  # TP below entry for short
        self.assertGreater(trade_params_short['position_size'], 0)
    
    def test_simulate_trade_exit(self):
        """Test trade exit simulation."""
        data_with_indicators = self.strategy.calculate_indicators(self.test_data)
        
        # Create trade parameters
        trade_params = {
            'entry_price': 100.0,
            'stop_loss': 98.0,
            'take_profit': 104.0,
            'position_size': 1.0,
            'entry_time': self.test_data.index[50]
        }
        
        # Test long trade exit
        exit_info = self.strategy.simulate_trade_exit(trade_params, 'long', self.test_data)
        
        self.assertIsNotNone(exit_info)
        self.assertIn('exit_time', exit_info)
        self.assertIn('exit_price', exit_info)
        self.assertIn('exit_reason', exit_info)
        self.assertIn('pnl_usdt', exit_info)
        self.assertIn('r_multiple', exit_info)
        
        # Exit time should be after entry time
        self.assertGreater(exit_info['exit_time'], trade_params['entry_time'])
        
        # Exit reason should be valid
        valid_reasons = ['take_profit', 'stop_loss', 'session_close', 'session_end', 'time_limit_24h']
        self.assertIn(exit_info['exit_reason'], valid_reasons)
    
    def test_process_day(self):
        """Test daily processing."""
        date = self.test_data.index[0].date()
        trades = self.strategy.process_day(self.test_data, date)
        
        # Should return a list
        self.assertIsInstance(trades, list)
        
        # If trades are generated, they should have the correct structure
        if trades:
            trade = trades[0]
            required_fields = [
                'day_key', 'entry_time', 'side', 'entry_price', 'sl', 'tp',
                'exit_time', 'exit_price', 'exit_reason', 'pnl_usdt', 'r_multiple'
            ]
            
            for field in required_fields:
                self.assertIn(field, trade)
            
            # Side should be 'long' or 'short'
            self.assertIn(trade['side'], ['long', 'short'])
            
            # Reliability score should be present
            self.assertIn('reliability_score', trade)
            self.assertGreaterEqual(trade['reliability_score'], 0.0)
            self.assertLessEqual(trade['reliability_score'], 1.0)
    
    def test_can_trade_today(self):
        """Test daily trading limits."""
        # Initially should be able to trade
        self.assertTrue(self.strategy.can_trade_today())
        
        # After reaching max trades, should not be able to trade
        self.strategy.daily_trades = self.strategy.max_daily_trades
        self.assertFalse(self.strategy.can_trade_today())
        
        # Reset and test daily target
        self.strategy.reset_daily_state()
        self.strategy.daily_pnl = self.strategy.daily_target
        self.assertFalse(self.strategy.can_trade_today())
        
        # Reset and test daily loss limit
        self.strategy.reset_daily_state()
        self.strategy.daily_pnl = self.strategy.daily_max_loss
        self.assertFalse(self.strategy.can_trade_today())
    
    def test_reset_daily_state(self):
        """Test daily state reset."""
        # Set some state
        self.strategy.daily_pnl = 50.0
        self.strategy.daily_trades = 2
        
        # Reset
        self.strategy.reset_daily_state()
        
        # Check reset
        self.assertEqual(self.strategy.daily_pnl, 0.0)
        self.assertEqual(self.strategy.daily_trades, 0)
    
    def test_get_strategy_info(self):
        """Test strategy information."""
        info = self.strategy.get_strategy_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['name'], 'MultifactorStrategy')
        self.assertEqual(info['version'], '1.0.0')
        self.assertIn('indicators', info)
        self.assertIn('reliability_control', info)
        self.assertTrue(info['reliability_control'])
    
    def test_different_modes(self):
        """Test different trading modes."""
        # Test conservative mode
        conservative_config = self.config.copy()
        conservative_config.update({
            'min_reliability_score': 0.8,
            'atr_multiplier': 1.5,
            'volume_threshold': 1.5
        })
        
        conservative_strategy = MultifactorStrategy(conservative_config)
        self.assertEqual(conservative_strategy.min_reliability_score, 0.8)
        self.assertEqual(conservative_strategy.atr_multiplier, 1.5)
        self.assertEqual(conservative_strategy.volume_threshold, 1.5)
        
        # Test aggressive mode
        aggressive_config = self.config.copy()
        aggressive_config.update({
            'min_reliability_score': 0.4,
            'atr_multiplier': 2.5,
            'volume_threshold': 1.0,
            'trailing_stop': True
        })
        
        aggressive_strategy = MultifactorStrategy(aggressive_config)
        self.assertEqual(aggressive_strategy.min_reliability_score, 0.4)
        self.assertEqual(aggressive_strategy.atr_multiplier, 2.5)
        self.assertEqual(aggressive_strategy.volume_threshold, 1.0)
        self.assertTrue(aggressive_strategy.trailing_stop)
    
    def test_volume_confirmation(self):
        """Test volume confirmation logic."""
        # Create data with high volume
        high_volume_data = self.test_data.copy()
        high_volume_data['volume'] = high_volume_data['volume'] * 2.0  # Double the volume
        
        data_with_indicators = self.strategy.calculate_indicators(high_volume_data)
        
        # Volume confirmation should be 1 for high volume
        self.assertTrue((data_with_indicators['volume_confirmation'] == 1).any())
        
        # Create data with low volume
        low_volume_data = self.test_data.copy()
        low_volume_data['volume'] = low_volume_data['volume'] * 0.5  # Half the volume
        
        data_with_indicators_low = self.strategy.calculate_indicators(low_volume_data)
        
        # Volume confirmation should be 0 for low volume
        self.assertTrue((data_with_indicators_low['volume_confirmation'] == 0).any())


if __name__ == '__main__':
    unittest.main()
