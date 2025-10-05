#!/usr/bin/env python3
"""
Tests for mode configurations and UI functionality.
"""

import unittest
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import (
    MODE_CONFIG, 
    MODE_ASSETS, 
    STRATEGY_DESCRIPTIONS,
    get_effective_config,
    get_symbols_for_mode
)


class TestModeConfigurations(unittest.TestCase):
    """Test mode configurations and related functionality."""
    
    def test_mode_config_structure(self):
        """Test that MODE_CONFIG has the correct structure."""
        expected_modes = ['conservative', 'moderate', 'aggressive']
        
        for mode in expected_modes:
            self.assertIn(mode, MODE_CONFIG)
            
            config = MODE_CONFIG[mode]
            
            # Check required fields
            required_fields = [
                'risk_usdt', 'strategy_type', 'target_r_multiple', 
                'risk_reward_ratio', 'allow_shorts', 'max_drawdown'
            ]
            
            for field in required_fields:
                self.assertIn(field, config, f"Mode {mode} missing field {field}")
    
    def test_strategy_types(self):
        """Test that each mode has a valid strategy type."""
        expected_strategy_types = ['mean_reversion', 'trend_following', 'breakout_fade']
        
        for mode, config in MODE_CONFIG.items():
            strategy_type = config['strategy_type']
            self.assertIn(strategy_type, expected_strategy_types, 
                         f"Mode {mode} has invalid strategy type: {strategy_type}")
    
    def test_risk_progression(self):
        """Test that risk increases from conservative to aggressive."""
        conservative_risk = MODE_CONFIG['conservative']['risk_usdt']
        moderate_risk = MODE_CONFIG['moderate']['risk_usdt']
        aggressive_risk = MODE_CONFIG['aggressive']['risk_usdt']
        
        self.assertLess(conservative_risk, moderate_risk)
        self.assertLess(moderate_risk, aggressive_risk)
    
    def test_r_multiple_progression(self):
        """Test that R-multiple targets increase from conservative to aggressive."""
        conservative_r = MODE_CONFIG['conservative']['target_r_multiple']
        moderate_r = MODE_CONFIG['moderate']['target_r_multiple']
        aggressive_r = MODE_CONFIG['aggressive']['target_r_multiple']
        
        self.assertLess(conservative_r, moderate_r)
        self.assertLess(moderate_r, aggressive_r)
    
    def test_drawdown_progression(self):
        """Test that max drawdown increases from conservative to aggressive."""
        conservative_dd = MODE_CONFIG['conservative']['max_drawdown']
        moderate_dd = MODE_CONFIG['moderate']['max_drawdown']
        aggressive_dd = MODE_CONFIG['aggressive']['max_drawdown']
        
        self.assertLess(conservative_dd, moderate_dd)
        self.assertLess(moderate_dd, aggressive_dd)
    
    def test_short_trading_permissions(self):
        """Test short trading permissions."""
        # Conservative should not allow shorts
        self.assertFalse(MODE_CONFIG['conservative']['allow_shorts'])
        
        # Moderate and aggressive should allow shorts
        self.assertTrue(MODE_CONFIG['moderate']['allow_shorts'])
        self.assertTrue(MODE_CONFIG['aggressive']['allow_shorts'])
    
    def test_mode_assets_structure(self):
        """Test that MODE_ASSETS has the correct structure."""
        expected_modes = ['conservative', 'moderate', 'aggressive']
        
        for mode in expected_modes:
            self.assertIn(mode, MODE_ASSETS)
            
            assets = MODE_ASSETS[mode]
            self.assertIsInstance(assets, list)
            self.assertGreater(len(assets), 0)
            
            # Check that all assets are valid symbol formats
            for asset in assets:
                self.assertIn('USDT', asset)
                self.assertIn('/', asset)
    
    def test_asset_progression(self):
        """Test that asset count increases from conservative to aggressive."""
        conservative_assets = len(MODE_ASSETS['conservative'])
        moderate_assets = len(MODE_ASSETS['moderate'])
        aggressive_assets = len(MODE_ASSETS['aggressive'])
        
        self.assertLessEqual(conservative_assets, moderate_assets)
        self.assertLessEqual(moderate_assets, aggressive_assets)
    
    def test_strategy_descriptions_structure(self):
        """Test that STRATEGY_DESCRIPTIONS has the correct structure."""
        expected_modes = ['conservative', 'moderate', 'aggressive']
        
        for mode in expected_modes:
            self.assertIn(mode, STRATEGY_DESCRIPTIONS)
            
            description = STRATEGY_DESCRIPTIONS[mode]
            
            # Check required fields
            required_fields = ['name', 'description', 'tools', 'rules', 'risk_profile']
            
            for field in required_fields:
                self.assertIn(field, description, f"Mode {mode} missing description field {field}")
            
            # Check that tools and rules are lists
            self.assertIsInstance(description['tools'], list)
            self.assertIsInstance(description['rules'], list)
            self.assertGreater(len(description['tools']), 0)
            self.assertGreater(len(description['rules']), 0)
    
    def test_get_effective_config(self):
        """Test get_effective_config function."""
        # Test with valid mode
        config = get_effective_config("BTC/USDT:USDT", "conservative")
        
        self.assertIsInstance(config, dict)
        self.assertEqual(config['risk_usdt'], MODE_CONFIG['conservative']['risk_usdt'])
        self.assertEqual(config['strategy_type'], MODE_CONFIG['conservative']['strategy_type'])
        
        # Test with invalid mode (should default to moderate)
        config = get_effective_config("BTC/USDT:USDT", "invalid")
        
        self.assertIsInstance(config, dict)
        self.assertEqual(config['risk_usdt'], MODE_CONFIG['moderate']['risk_usdt'])
        
        # Test with None mode (should default to moderate)
        config = get_effective_config("BTC/USDT:USDT", None)
        
        self.assertIsInstance(config, dict)
        self.assertEqual(config['risk_usdt'], MODE_CONFIG['moderate']['risk_usdt'])
    
    def test_get_symbols_for_mode(self):
        """Test get_symbols_for_mode function."""
        # Test with valid mode
        symbols = get_symbols_for_mode("conservative")
        
        self.assertIsInstance(symbols, list)
        self.assertEqual(symbols, MODE_ASSETS['conservative'])
        
        # Test with invalid mode (should default to moderate)
        symbols = get_symbols_for_mode("invalid")
        
        self.assertIsInstance(symbols, list)
        self.assertEqual(symbols, MODE_ASSETS['moderate'])
        
        # Test with None mode (should default to moderate)
        symbols = get_symbols_for_mode(None)
        
        self.assertIsInstance(symbols, list)
        self.assertEqual(symbols, MODE_ASSETS['moderate'])
    
    def test_conservative_configuration(self):
        """Test conservative mode specific configuration."""
        config = MODE_CONFIG['conservative']
        
        # Should be mean reversion strategy
        self.assertEqual(config['strategy_type'], 'mean_reversion')
        
        # Should have conservative risk parameters
        self.assertEqual(config['risk_usdt'], 15.0)
        self.assertEqual(config['target_r_multiple'], 1.0)
        self.assertEqual(config['max_drawdown'], 0.05)
        
        # Should not allow shorts
        self.assertFalse(config['allow_shorts'])
        
        # Should have mean reversion specific parameters
        self.assertIn('bollinger_period', config)
        self.assertIn('rsi_period', config)
        self.assertIn('rsi_oversold', config)
        self.assertIn('rsi_overbought', config)
    
    def test_moderate_configuration(self):
        """Test moderate mode specific configuration."""
        config = MODE_CONFIG['moderate']
        
        # Should be trend following strategy
        self.assertEqual(config['strategy_type'], 'trend_following')
        
        # Should have moderate risk parameters
        self.assertEqual(config['risk_usdt'], 25.0)
        self.assertEqual(config['target_r_multiple'], 1.5)
        self.assertEqual(config['max_drawdown'], 0.08)
        
        # Should allow shorts
        self.assertTrue(config['allow_shorts'])
        
        # Should have trend following specific parameters
        self.assertIn('heikin_ashi', config)
        self.assertIn('adx_period', config)
        self.assertIn('adx_threshold', config)
        self.assertIn('ema_fast', config)
        self.assertIn('ema_slow', config)
    
    def test_aggressive_configuration(self):
        """Test aggressive mode specific configuration."""
        config = MODE_CONFIG['aggressive']
        
        # Should be breakout fade strategy
        self.assertEqual(config['strategy_type'], 'breakout_fade')
        
        # Should have aggressive risk parameters
        self.assertEqual(config['risk_usdt'], 40.0)
        self.assertEqual(config['target_r_multiple'], 2.0)
        self.assertEqual(config['max_drawdown'], 0.12)
        
        # Should allow shorts
        self.assertTrue(config['allow_shorts'])
        
        # Should have breakout fade specific parameters
        self.assertIn('breakout_period', config)
        self.assertIn('breakout_threshold', config)
        self.assertIn('rsi_extreme_high', config)
        self.assertIn('rsi_extreme_low', config)
    
    def test_validation_parameters(self):
        """Test validation parameters for each mode."""
        for mode, config in MODE_CONFIG.items():
            # Check that validation parameters exist and are reasonable
            self.assertIn('min_win_rate', config)
            self.assertIn('min_avg_r', config)
            self.assertIn('min_trades', config)
            self.assertIn('min_profit_factor', config)
            
            # Check that min_win_rate is reasonable (between 50% and 100%)
            self.assertGreaterEqual(config['min_win_rate'], 50.0)
            self.assertLessEqual(config['min_win_rate'], 100.0)
            
            # Check that min_avg_r is positive
            self.assertGreater(config['min_avg_r'], 0.0)
            
            # Check that min_trades is positive
            self.assertGreater(config['min_trades'], 0)
            
            # Check that min_profit_factor is greater than 1.0
            self.assertGreater(config['min_profit_factor'], 1.0)


if __name__ == '__main__':
    unittest.main()
