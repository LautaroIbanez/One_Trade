#!/usr/bin/env python3
"""
Pruebas de integración para verificar la coherencia entre backtesting y señal diaria.
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
from btc_1tpd_backtest_final import SimpleTradingStrategy
from signals.today_signal import get_today_trade_recommendation


class TestStrategyIntegration(unittest.TestCase):
    """Test cases for strategy integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_config = {
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
            'max_daily_trades': 1,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        }
        
        # Create test data
        self.test_data = self._create_test_data()
    
    def _create_test_data(self):
        """Create synthetic test data with clear signals."""
        # Create 24 hours of 15-minute data
        start = datetime(2024, 1, 3, 0, 0, 0, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=timezone.utc)
        
        # Create data with clear bullish trend and breakout
        base_price = 100.0
        data = []
        
        for i, timestamp in enumerate(idx):
            # Create clear trend
            trend = i * 0.2  # Strong upward trend
            
            # Add volatility around trend
            if i < 20:  # First 5 hours - consolidation
                volatility = np.sin(i * 0.2) * 1.0
            elif i < 40:  # Next 5 hours - breakout
                volatility = np.sin(i * 0.2) * 2.0 + 1.0  # Higher volatility
            else:  # Rest of day - follow-through
                volatility = np.sin(i * 0.1) * 1.5
            
            open_price = base_price + trend + volatility
            high_price = open_price + abs(np.random.normal(0, 1.5))
            low_price = open_price - abs(np.random.normal(0, 1.5))
            close_price = open_price + np.random.normal(0, 1.0)
            
            # Ensure OHLC consistency
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000.0 + np.random.normal(0, 200)
            })
        
        return pd.DataFrame(data, index=idx)
    
    def test_multifactor_vs_orb_consistency(self):
        """Test consistency between multifactor and ORB strategies."""
        # Test multifactor strategy
        multifactor_config = self.base_config.copy()
        multifactor_config['use_multifactor_strategy'] = True
        
        multifactor_strategy = SimpleTradingStrategy(multifactor_config)
        multifactor_trades = multifactor_strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        # Test ORB strategy
        orb_config = self.base_config.copy()
        orb_config['use_multifactor_strategy'] = False
        
        orb_strategy = SimpleTradingStrategy(orb_config)
        orb_trades = orb_strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        # Both strategies should return valid trade structures
        self.assertIsInstance(multifactor_trades, list)
        self.assertIsInstance(orb_trades, list)
        
        # If trades are generated, they should have consistent structure
        if multifactor_trades:
            trade = multifactor_trades[0]
            required_fields = [
                'day_key', 'entry_time', 'side', 'entry_price', 'sl', 'tp',
                'exit_time', 'exit_price', 'exit_reason', 'pnl_usdt', 'r_multiple'
            ]
            
            for field in required_fields:
                self.assertIn(field, trade)
            
            # Multifactor trades should have reliability score
            self.assertIn('reliability_score', trade)
            self.assertIn('used_multifactor', trade)
            self.assertTrue(trade['used_multifactor'])
        
        if orb_trades:
            trade = orb_trades[0]
            required_fields = [
                'day_key', 'entry_time', 'side', 'entry_price', 'sl', 'tp',
                'exit_time', 'exit_price', 'exit_reason', 'pnl_usdt', 'r_multiple'
            ]
            
            for field in required_fields:
                self.assertIn(field, trade)
    
    def test_signal_consistency(self):
        """Test consistency between backtesting and signal generation."""
        # Test with multifactor strategy
        multifactor_config = self.base_config.copy()
        multifactor_config['use_multifactor_strategy'] = True
        
        # Get signal using today_signal
        now = self.test_data.index[50]  # Middle of the day
        signal = get_today_trade_recommendation('BTC/USDT:USDT', multifactor_config, now)
        
        # Signal should have valid structure
        self.assertIsInstance(signal, dict)
        self.assertIn('status', signal)
        self.assertIn('symbol', signal)
        self.assertIn('date', signal)
        
        # If signal is generated, it should have required fields
        if signal['status'] == 'signal':
            required_fields = ['side', 'entry_price', 'stop_loss', 'take_profit']
            for field in required_fields:
                self.assertIn(field, signal)
            
            # Multifactor signals should have reliability score
            if signal.get('strategy') == 'multifactor':
                self.assertIn('reliability_score', signal)
                self.assertGreaterEqual(signal['reliability_score'], 0.0)
                self.assertLessEqual(signal['reliability_score'], 1.0)
    
    def test_different_modes_consistency(self):
        """Test consistency across different trading modes."""
        modes = ['conservative', 'moderate', 'aggressive']
        
        for mode in modes:
            with self.subTest(mode=mode):
                # Create mode-specific config
                mode_config = self.base_config.copy()
                
                if mode == 'conservative':
                    mode_config.update({
                        'min_reliability_score': 0.8,
                        'atr_multiplier': 1.5,
                        'volume_threshold': 1.5,
                        'use_multifactor_strategy': False  # Use ORB
                    })
                elif mode == 'moderate':
                    mode_config.update({
                        'min_reliability_score': 0.6,
                        'atr_multiplier': 2.0,
                        'volume_threshold': 1.2,
                        'use_multifactor_strategy': True  # Use multifactor
                    })
                elif mode == 'aggressive':
                    mode_config.update({
                        'min_reliability_score': 0.4,
                        'atr_multiplier': 2.5,
                        'volume_threshold': 1.0,
                        'trailing_stop': True,
                        'use_multifactor_strategy': True  # Use multifactor
                    })
                
                # Test backtesting
                strategy = SimpleTradingStrategy(mode_config)
                trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
                
                # Test signal generation
                now = self.test_data.index[50]
                signal = get_today_trade_recommendation('BTC/USDT:USDT', mode_config, now)
                
                # Both should work without errors
                self.assertIsInstance(trades, list)
                self.assertIsInstance(signal, dict)
                
                # If trades are generated, they should be valid
                if trades:
                    trade = trades[0]
                    self.assertIn(trade['side'], ['long', 'short'])
                    self.assertGreater(trade['entry_price'], 0)
                    self.assertGreater(trade['sl'], 0)
                    self.assertGreater(trade['tp'], 0)
                
                # If signal is generated, it should be valid
                if signal['status'] == 'signal':
                    self.assertIn(signal['side'], ['long', 'short'])
                    self.assertGreater(signal['entry_price'], 0)
                    self.assertGreater(signal['stop_loss'], 0)
                    self.assertGreater(signal['take_profit'], 0)
    
    def test_reliability_score_consistency(self):
        """Test that reliability scores are consistent and meaningful."""
        # Test with different reliability thresholds
        thresholds = [0.3, 0.5, 0.7, 0.9]
        
        for threshold in thresholds:
            with self.subTest(threshold=threshold):
                config = self.base_config.copy()
                config['min_reliability_score'] = threshold
                config['use_multifactor_strategy'] = True
                
                strategy = SimpleTradingStrategy(config)
                trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
                
                # If trades are generated, reliability should meet threshold
                if trades:
                    trade = trades[0]
                    self.assertIn('reliability_score', trade)
                    self.assertGreaterEqual(trade['reliability_score'], threshold)
    
    def test_session_vs_24h_consistency(self):
        """Test consistency between session and 24h trading modes."""
        # Test session trading
        session_config = self.base_config.copy()
        session_config.update({
            'session_trading': True,
            'full_day_trading': False,
            'entry_window': (11, 14),
            'exit_window': (20, 22)
        })
        
        session_strategy = SimpleTradingStrategy(session_config)
        session_trades = session_strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        # Test 24h trading
        full_day_config = self.base_config.copy()
        full_day_config.update({
            'session_trading': False,
            'full_day_trading': True,
            'entry_window': (1, 24),
            'exit_window': None
        })
        
        full_day_strategy = SimpleTradingStrategy(full_day_config)
        full_day_trades = full_day_strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        # Both should work without errors
        self.assertIsInstance(session_trades, list)
        self.assertIsInstance(full_day_trades, list)
        
        # If trades are generated, they should have valid structure
        for trades in [session_trades, full_day_trades]:
            if trades:
                trade = trades[0]
                self.assertIn(trade['side'], ['long', 'short'])
                self.assertGreater(trade['entry_price'], 0)
                self.assertGreater(trade['sl'], 0)
                self.assertGreater(trade['tp'], 0)
    
    def test_error_handling(self):
        """Test error handling in strategy integration."""
        # Test with invalid config
        invalid_config = self.base_config.copy()
        invalid_config['min_reliability_score'] = -1.0  # Invalid value
        
        strategy = SimpleTradingStrategy(invalid_config)
        trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        # Should handle gracefully
        self.assertIsInstance(trades, list)
        
        # Test with empty data
        empty_data = pd.DataFrame()
        trades_empty = strategy.process_day(empty_data, datetime.now().date())
        
        # Should return empty list
        self.assertEqual(trades_empty, [])
        
        # Test with insufficient data
        insufficient_data = self.test_data.head(10)  # Only 10 candles
        trades_insufficient = strategy.process_day(insufficient_data, datetime.now().date())
        
        # Should handle gracefully
        self.assertIsInstance(trades_insufficient, list)


if __name__ == '__main__':
    unittest.main()
