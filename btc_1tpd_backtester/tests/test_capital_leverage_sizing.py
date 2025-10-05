#!/usr/bin/env python3
"""
Pruebas para verificar que el sizing respeta capital/leverage y mantiene take-profit rentable.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from btc_1tpd_backtest_final import SimpleTradingStrategy


class TestCapitalLeverageSizing(unittest.TestCase):
    """Test cases for capital/leverage position sizing."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data with clear signals
        self.test_data = self._create_test_data()
        
        # Base configuration for moderate mode
        self.base_config = {
            'risk_usdt': 25.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 1.5,
            'target_r_multiple': 1.5,
            'risk_reward_ratio': 1.5,
            'adx_min': 15.0,
            'force_one_trade': True,
            'fallback_mode': 'EMA15_pullback',
            'orb_window': (8, 9),
            'entry_window': (11, 14),
            'exit_window': (20, 22),
            'session_trading': True,
            'session_timezone': 'America/Argentina/Buenos_Aires',
            'commission_rate': 0.001,
            'slippage_rate': 0.0005,
            'use_multifactor_strategy': False,
            # Capital and leverage parameters
            'initial_capital': 1000.0,
            'leverage': 1.0,
            'equity_risk_cap': 0.01,  # 1% max equity risk per trade
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
    
    def test_position_sizing_respects_capital(self):
        """Test that position sizing respects capital constraints."""
        config = self.base_config.copy()
        config.update({
            'initial_capital': 1000.0,
            'leverage': 1.0,
            'risk_usdt': 25.0
        })
        
        strategy = SimpleTradingStrategy(config)
        
        # Test with high entry price that would require large position
        entry_price = 1000.0
        stop_loss = 980.0  # 2% risk
        
        position_size = strategy.compute_position_size(entry_price, stop_loss)
        
        # Calculate expected position size based on risk
        risk_amount = config['risk_usdt']
        price_diff = abs(entry_price - stop_loss)
        expected_risk_based_size = risk_amount / price_diff
        
        # Calculate max position size based on capital
        max_capital_based_size = (config['initial_capital'] * config['leverage']) / entry_price
        
        # Position size should be limited by capital constraint
        self.assertLessEqual(position_size, max_capital_based_size)
        self.assertLessEqual(position_size, expected_risk_based_size)
        
        # Verify actual risk doesn't exceed intended risk
        actual_risk = abs(entry_price - stop_loss) * position_size
        self.assertLessEqual(actual_risk, risk_amount)
    
    def test_position_sizing_respects_leverage(self):
        """Test that position sizing respects leverage constraints."""
        config = self.base_config.copy()
        config.update({
            'initial_capital': 1000.0,
            'leverage': 2.0,  # 2x leverage
            'risk_usdt': 25.0
        })
        
        strategy = SimpleTradingStrategy(config)
        
        entry_price = 100.0
        stop_loss = 98.0  # 2% risk
        
        position_size = strategy.compute_position_size(entry_price, stop_loss)
        
        # Calculate max position size with 2x leverage
        max_leveraged_size = (config['initial_capital'] * config['leverage']) / entry_price
        expected_max_size = (1000.0 * 2.0) / 100.0  # 20.0
        
        # Position size should be limited by leveraged capital
        self.assertLessEqual(position_size, max_leveraged_size)
        self.assertLessEqual(position_size, expected_max_size)
    
    def test_position_sizing_respects_equity_risk_cap(self):
        """Test that position sizing respects equity risk cap."""
        config = self.base_config.copy()
        config.update({
            'initial_capital': 1000.0,
            'leverage': 1.0,
            'equity_risk_cap': 0.01,  # 1% max equity risk
            'risk_usdt': 25.0
        })
        
        strategy = SimpleTradingStrategy(config)
        
        entry_price = 100.0
        stop_loss = 98.0  # 2% risk
        
        position_size = strategy.compute_position_size(entry_price, stop_loss)
        
        # Calculate max position size based on equity risk cap
        max_equity_risk_size = (config['initial_capital'] * config['equity_risk_cap']) / entry_price
        expected_equity_risk_size = (1000.0 * 0.01) / 100.0  # 0.1
        
        # Position size should be limited by equity risk cap
        self.assertLessEqual(position_size, max_equity_risk_size)
        self.assertLessEqual(position_size, expected_equity_risk_size)
    
    def test_take_profit_remains_profitable(self):
        """Test that take-profit exits yield positive PnL under capital constraints."""
        config = self.base_config.copy()
        config.update({
            'initial_capital': 1000.0,
            'leverage': 1.0,
            'risk_usdt': 25.0,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        })
        
        strategy = SimpleTradingStrategy(config)
        
        # Process a day to get a trade
        trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
        
        if trades:
            trade = trades[0]
            entry_price = trade['entry_price']
            stop_loss = trade['sl']
            take_profit = trade['tp']
            position_size = trade['position_size']
            side = trade['side']
            
            # Verify position size respects constraints
            max_capital_size = (config['initial_capital'] * config['leverage']) / entry_price
            max_equity_risk_size = (config['initial_capital'] * config['equity_risk_cap']) / entry_price
            expected_risk_size = config['risk_usdt'] / abs(entry_price - stop_loss)
            
            self.assertLessEqual(position_size, max_capital_size)
            self.assertLessEqual(position_size, max_equity_risk_size)
            self.assertLessEqual(position_size, expected_risk_size)
            
            # Simulate take-profit exit
            exit_info = strategy.simulate_trade_exit({
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size
            }, side, self.test_data)
            
            # Verify take-profit exit is profitable
            self.assertGreater(exit_info['pnl_usdt'], 0, 
                             f"Take-profit exit should be profitable, got {exit_info['pnl_usdt']}")
            
            # Verify R-multiple is positive
            self.assertGreater(exit_info['r_multiple'], 0,
                             f"R-multiple should be positive, got {exit_info['r_multiple']}")
            
            # Verify actual risk doesn't exceed intended risk
            actual_risk = abs(entry_price - stop_loss) * position_size
            self.assertLessEqual(actual_risk, config['risk_usdt'] * 1.1,  # Allow 10% tolerance
                               f"Actual risk {actual_risk} exceeds intended risk {config['risk_usdt']}")
    
    def test_synthetic_trade_take_profit_profitable(self):
        """Test synthetic trade with take-profit exit yields positive PnL."""
        config = self.base_config.copy()
        config.update({
            'initial_capital': 1000.0,
            'leverage': 1.0,
            'risk_usdt': 25.0,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        })
        
        strategy = SimpleTradingStrategy(config)
        
        # Create synthetic trade parameters
        entry_price = 100.0
        stop_loss = 98.0  # 2% risk
        take_profit = 103.0  # 3% reward (1.5R)
        side = 'long'
        
        # Calculate position size using the helper
        position_size = strategy.compute_position_size(entry_price, stop_loss)
        
        # Verify position size is reasonable
        self.assertGreater(position_size, 0)
        self.assertLessEqual(position_size, 10.0)  # Should be capped by capital
        
        # Simulate take-profit exit
        exit_info = strategy.simulate_trade_exit({
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_size
        }, side, self.test_data)
        
        # Verify take-profit exit is profitable
        self.assertGreater(exit_info['pnl_usdt'], 0, 
                         f"Take-profit exit should be profitable, got {exit_info['pnl_usdt']}")
        
        # Verify R-multiple is approximately 1.5
        expected_r_multiple = 1.5
        actual_r_multiple = exit_info['r_multiple']
        self.assertAlmostEqual(actual_r_multiple, expected_r_multiple, places=1,
                             msg=f"R-multiple should be ~{expected_r_multiple}, got {actual_r_multiple}")
        
        # Verify costs are reasonable
        total_costs = exit_info['commission_usdt'] + exit_info['slippage_usdt']
        self.assertGreater(total_costs, 0)
        self.assertLess(total_costs, exit_info['gross_pnl_usdt'])  # Costs should be less than gross profit
    
    def test_position_sizing_with_different_capital_levels(self):
        """Test position sizing with different capital levels."""
        base_config = self.base_config.copy()
        
        capital_levels = [500.0, 1000.0, 2000.0, 5000.0]
        
        for capital in capital_levels:
            with self.subTest(capital=capital):
                config = base_config.copy()
                config.update({
                    'initial_capital': capital,
                    'leverage': 1.0,
                    'risk_usdt': 25.0
                })
                
                strategy = SimpleTradingStrategy(config)
                
                entry_price = 100.0
                stop_loss = 98.0
                
                position_size = strategy.compute_position_size(entry_price, stop_loss)
                
                # Position size should scale with capital
                max_capital_size = (capital * 1.0) / entry_price
                self.assertLessEqual(position_size, max_capital_size)
                
                # For higher capital, position size should be limited by risk, not capital
                if capital >= 2500.0:  # 25.0 / 0.02 = 1250, so 2500+ should not be capital-limited
                    expected_risk_size = 25.0 / 2.0  # 12.5
                    self.assertAlmostEqual(position_size, expected_risk_size, places=1)
    
    def test_position_sizing_with_different_leverage_levels(self):
        """Test position sizing with different leverage levels."""
        base_config = self.base_config.copy()
        
        leverage_levels = [1.0, 2.0, 5.0, 10.0]
        
        for leverage in leverage_levels:
            with self.subTest(leverage=leverage):
                config = base_config.copy()
                config.update({
                    'initial_capital': 1000.0,
                    'leverage': leverage,
                    'risk_usdt': 25.0
                })
                
                strategy = SimpleTradingStrategy(config)
                
                entry_price = 100.0
                stop_loss = 98.0
                
                position_size = strategy.compute_position_size(entry_price, stop_loss)
                
                # Position size should scale with leverage
                max_leveraged_size = (1000.0 * leverage) / entry_price
                self.assertLessEqual(position_size, max_leveraged_size)
                
                # For low leverage, position size should be limited by capital
                if leverage <= 2.0:
                    expected_capital_size = (1000.0 * leverage) / 100.0
                    self.assertAlmostEqual(position_size, expected_capital_size, places=1)
    
    def test_edge_cases(self):
        """Test edge cases for position sizing."""
        config = self.base_config.copy()
        strategy = SimpleTradingStrategy(config)
        
        # Test with zero price difference
        position_size = strategy.compute_position_size(100.0, 100.0)
        self.assertEqual(position_size, 0)
        
        # Test with very small capital
        config_small = config.copy()
        config_small.update({
            'initial_capital': 10.0,
            'leverage': 1.0,
            'risk_usdt': 25.0
        })
        strategy_small = SimpleTradingStrategy(config_small)
        
        position_size = strategy_small.compute_position_size(100.0, 98.0)
        max_capital_size = (10.0 * 1.0) / 100.0  # 0.1
        self.assertLessEqual(position_size, max_capital_size)
        
        # Test with very high leverage
        config_high_leverage = config.copy()
        config_high_leverage.update({
            'initial_capital': 1000.0,
            'leverage': 100.0,
            'risk_usdt': 25.0
        })
        strategy_high_leverage = SimpleTradingStrategy(config_high_leverage)
        
        position_size = strategy_high_leverage.compute_position_size(100.0, 98.0)
        max_leveraged_size = (1000.0 * 100.0) / 100.0  # 1000.0
        self.assertLessEqual(position_size, max_leveraged_size)
        
        # Should still be limited by risk
        expected_risk_size = 25.0 / 2.0  # 12.5
        self.assertLessEqual(position_size, expected_risk_size)


if __name__ == '__main__':
    unittest.main()

