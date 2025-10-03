#!/usr/bin/env python3
"""
Pruebas para verificar que SL/TP y sizing están alineados con objetivos R por modo.
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
from strategy import TradingStrategy
from signals.today_signal import get_today_trade_recommendation


class TestRMultipleAlignment(unittest.TestCase):
    """Test cases for R-multiple alignment across different modes."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data with clear signals
        self.test_data = self._create_test_data()
        
        # Base configuration
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
    
    def test_conservative_mode_1r_target(self):
        """Test that conservative mode targets exactly 1R."""
        config = self.base_config.copy()
        config.update({
            'risk_usdt': 15.0,
            'tp_multiplier': 1.0,
            'target_r_multiple': 1.0,
            'risk_reward_ratio': 1.0,
            'use_multifactor_strategy': False  # Use ORB
        })
        
        # Test SimpleTradingStrategy
        strategy = SimpleTradingStrategy(config)
        trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        if trades:
            trade = trades[0]
            entry_price = trade['entry_price']
            stop_loss = trade['sl']
            take_profit = trade['tp']
            
            # Calculate risk and reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            # Calculate R-multiple
            r_multiple = reward / risk if risk > 0 else 0
            
            # Verify 1R target
            self.assertAlmostEqual(r_multiple, 1.0, places=2, 
                                 msg=f"Conservative mode should target 1R, got {r_multiple:.3f}")
            
            # Verify risk amount
            expected_risk = config['risk_usdt']
            actual_risk = risk * trade.get('position_size', 1.0)
            self.assertAlmostEqual(actual_risk, expected_risk, places=2,
                                 msg=f"Risk should be {expected_risk}, got {actual_risk:.2f}")
    
    def test_moderate_mode_1_5r_target(self):
        """Test that moderate mode targets exactly 1.5R."""
        config = self.base_config.copy()
        config.update({
            'risk_usdt': 25.0,
            'tp_multiplier': 1.5,
            'target_r_multiple': 1.5,
            'risk_reward_ratio': 1.5,
            'use_multifactor_strategy': True  # Use multifactor
        })
        
        # Test SimpleTradingStrategy
        strategy = SimpleTradingStrategy(config)
        trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        if trades:
            trade = trades[0]
            entry_price = trade['entry_price']
            stop_loss = trade['sl']
            take_profit = trade['tp']
            
            # Calculate risk and reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            # Calculate R-multiple
            r_multiple = reward / risk if risk > 0 else 0
            
            # Verify 1.5R target
            self.assertAlmostEqual(r_multiple, 1.5, places=2,
                                 msg=f"Moderate mode should target 1.5R, got {r_multiple:.3f}")
            
            # Verify risk amount
            expected_risk = config['risk_usdt']
            actual_risk = risk * trade.get('position_size', 1.0)
            self.assertAlmostEqual(actual_risk, expected_risk, places=2,
                                 msg=f"Risk should be {expected_risk}, got {actual_risk:.2f}")
    
    def test_aggressive_mode_2r_target(self):
        """Test that aggressive mode targets exactly 2R."""
        config = self.base_config.copy()
        config.update({
            'risk_usdt': 40.0,
            'tp_multiplier': 2.0,
            'target_r_multiple': 2.0,
            'risk_reward_ratio': 2.0,
            'use_multifactor_strategy': True  # Use multifactor
        })
        
        # Test SimpleTradingStrategy
        strategy = SimpleTradingStrategy(config)
        trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        if trades:
            trade = trades[0]
            entry_price = trade['entry_price']
            stop_loss = trade['sl']
            take_profit = trade['tp']
            
            # Calculate risk and reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            # Calculate R-multiple
            r_multiple = reward / risk if risk > 0 else 0
            
            # Verify 2R target
            self.assertAlmostEqual(r_multiple, 2.0, places=2,
                                 msg=f"Aggressive mode should target 2R, got {r_multiple:.3f}")
            
            # Verify risk amount
            expected_risk = config['risk_usdt']
            actual_risk = risk * trade.get('position_size', 1.0)
            self.assertAlmostEqual(actual_risk, expected_risk, places=2,
                                 msg=f"Risk should be {expected_risk}, got {actual_risk:.2f}")
    
    def test_multifactor_strategy_r_alignment(self):
        """Test R-multiple alignment in MultifactorStrategy."""
        modes = [
            ('conservative', 1.0),
            ('moderate', 1.5),
            ('aggressive', 2.0)
        ]
        
        for mode, target_r in modes:
            with self.subTest(mode=mode, target_r=target_r):
                config = self.base_config.copy()
                config.update({
                    'risk_usdt': 20.0,
                    'tp_multiplier': target_r,
                    'target_r_multiple': target_r,
                    'risk_reward_ratio': target_r,
                    'use_multifactor_strategy': True
                })
                
                strategy = MultifactorStrategy(config)
                trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
                
                if trades:
                    trade = trades[0]
                    entry_price = trade['entry_price']
                    stop_loss = trade['sl']
                    take_profit = trade['tp']
                    
                    # Calculate risk and reward
                    risk = abs(entry_price - stop_loss)
                    reward = abs(take_profit - entry_price)
                    
                    # Calculate R-multiple
                    r_multiple = reward / risk if risk > 0 else 0
                    
                    # Verify target R-multiple
                    self.assertAlmostEqual(r_multiple, target_r, places=2,
                                         msg=f"{mode} mode should target {target_r}R, got {r_multiple:.3f}")
    
    def test_trading_strategy_r_alignment(self):
        """Test R-multiple alignment in TradingStrategy (ORB)."""
        modes = [
            ('conservative', 1.0),
            ('moderate', 1.5),
            ('aggressive', 2.0)
        ]
        
        for mode, target_r in modes:
            with self.subTest(mode=mode, target_r=target_r):
                config = self.base_config.copy()
                config.update({
                    'signal_tf': '15m',
                    'daily_target': 50.0,
                    'daily_max_loss': -30.0,
                    'min_rr_ok': 1.0,
                    'atr_mult_orb': 1.5,
                    'atr_mult_fallback': 1.2,
                    'tp_multiplier': target_r,
                    'target_r_multiple': target_r,
                    'risk_reward_ratio': target_r,
                    'use_multifactor_strategy': False
                })
                
                strategy = TradingStrategy(config)
                
                # Test get_take_profit_price method
                entry_price = 100.0
                stop_loss = 98.0
                side = 'long'
                
                take_profit = strategy.get_take_profit_price(entry_price, stop_loss, side)
                
                # Calculate risk and reward
                risk = abs(entry_price - stop_loss)
                reward = abs(take_profit - entry_price)
                
                # Calculate R-multiple
                r_multiple = reward / risk if risk > 0 else 0
                
                # Verify target R-multiple
                self.assertAlmostEqual(r_multiple, target_r, places=2,
                                     msg=f"{mode} mode should target {target_r}R, got {r_multiple:.3f}")
    
    def test_signal_generation_r_alignment(self):
        """Test R-multiple alignment in signal generation."""
        modes = [
            ('conservative', 1.0),
            ('moderate', 1.5),
            ('aggressive', 2.0)
        ]
        
        for mode, target_r in modes:
            with self.subTest(mode=mode, target_r=target_r):
                config = self.base_config.copy()
                config.update({
                    'risk_usdt': 20.0,
                    'tp_multiplier': target_r,
                    'target_r_multiple': target_r,
                    'risk_reward_ratio': target_r,
                    'use_multifactor_strategy': False  # Use ORB for signal test
                })
                
                # Test signal generation
                now = self.test_data.index[50]
                signal = get_today_trade_recommendation('BTC/USDT:USDT', config, now)
                
                if signal.get('status') == 'signal':
                    entry_price = signal['entry_price']
                    stop_loss = signal['stop_loss']
                    take_profit = signal['take_profit']
                    
                    # Calculate risk and reward
                    risk = abs(entry_price - stop_loss)
                    reward = abs(take_profit - entry_price)
                    
                    # Calculate R-multiple
                    r_multiple = reward / risk if risk > 0 else 0
                    
                    # Verify target R-multiple
                    self.assertAlmostEqual(r_multiple, target_r, places=2,
                                         msg=f"{mode} mode signal should target {target_r}R, got {r_multiple:.3f}")
    
    def test_position_sizing_consistency(self):
        """Test that position sizing is consistent with risk management."""
        config = self.base_config.copy()
        config.update({
            'risk_usdt': 20.0,
            'tp_multiplier': 2.0,
            'target_r_multiple': 2.0,
            'use_multifactor_strategy': True
        })
        
        strategy = MultifactorStrategy(config)
        trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        if trades:
            trade = trades[0]
            entry_price = trade['entry_price']
            stop_loss = trade['sl']
            position_size = trade.get('position_size', 1.0)
            
            # Calculate actual risk
            risk_per_unit = abs(entry_price - stop_loss)
            actual_risk = risk_per_unit * position_size
            
            # Verify risk matches configured amount
            expected_risk = config['risk_usdt']
            self.assertAlmostEqual(actual_risk, expected_risk, places=2,
                                 msg=f"Position sizing should result in {expected_risk} risk, got {actual_risk:.2f}")
    
    def test_r_multiple_calculation_accuracy(self):
        """Test that R-multiple calculations are accurate."""
        # Test with known values
        entry_price = 100.0
        stop_loss = 98.0
        take_profit = 104.0
        
        # Calculate risk and reward
        risk = abs(entry_price - stop_loss)  # 2.0
        reward = abs(take_profit - entry_price)  # 4.0
        
        # Calculate R-multiple
        r_multiple = reward / risk  # 2.0
        
        # Verify calculation
        self.assertEqual(r_multiple, 2.0, "R-multiple calculation should be accurate")
        
        # Test with different values
        entry_price = 50.0
        stop_loss = 49.0
        take_profit = 51.5
        
        risk = abs(entry_price - stop_loss)  # 1.0
        reward = abs(take_profit - entry_price)  # 1.5
        r_multiple = reward / risk  # 1.5
        
        self.assertEqual(r_multiple, 1.5, "R-multiple calculation should be accurate")
    
    def test_mode_config_consistency(self):
        """Test that mode configurations are consistent."""
        # Import the actual mode config from webapp
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'webapp'))
            from app import MODE_CONFIG
            
            # Test each mode
            for mode, config in MODE_CONFIG.items():
                with self.subTest(mode=mode):
                    tp_multiplier = config.get('tp_multiplier')
                    target_r_multiple = config.get('target_r_multiple')
                    risk_reward_ratio = config.get('risk_reward_ratio')
                    
                    # All should be equal
                    self.assertEqual(tp_multiplier, target_r_multiple,
                                   f"{mode} mode: tp_multiplier should equal target_r_multiple")
                    self.assertEqual(tp_multiplier, risk_reward_ratio,
                                   f"{mode} mode: tp_multiplier should equal risk_reward_ratio")
                    
                    # Verify expected values
                    if mode == 'conservative':
                        self.assertEqual(tp_multiplier, 1.0, "Conservative mode should target 1R")
                    elif mode == 'moderate':
                        self.assertEqual(tp_multiplier, 1.5, "Moderate mode should target 1.5R")
                    elif mode == 'aggressive':
                        self.assertEqual(tp_multiplier, 2.0, "Aggressive mode should target 2R")
        
        except ImportError:
            self.skipTest("Could not import MODE_CONFIG from webapp")


if __name__ == '__main__':
    unittest.main()
