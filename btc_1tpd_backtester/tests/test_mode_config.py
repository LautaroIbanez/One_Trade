import unittest
import pandas as pd
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from webapp.app import (
    BASE_CONFIG, MODE_CONFIG, get_effective_config, 
    refresh_trades, load_trades, compute_metrics
)


class TestModeConfig(unittest.TestCase):
    """Test mode-specific configuration and file handling."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_repo_root = None
        
        # Mock the repo_root for testing
        import webapp.app as app_module
        self.original_repo_root = app_module.repo_root
        app_module.repo_root = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import webapp.app as app_module
        app_module.repo_root = self.original_repo_root
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_base_config_structure(self):
        """Test that BASE_CONFIG has required keys."""
        required_keys = ['risk_usdt', 'atr_mult_orb', 'tp_multiplier', 'adx_min']
        for key in required_keys:
            self.assertIn(key, BASE_CONFIG, f"BASE_CONFIG missing key: {key}")
    
    def test_mode_config_structure(self):
        """Test that MODE_CONFIG has all required modes."""
        expected_modes = ['conservative', 'moderate', 'aggressive']
        for mode in expected_modes:
            self.assertIn(mode, MODE_CONFIG, f"MODE_CONFIG missing mode: {mode}")
            
        # Test that each mode has required keys
        required_keys = ['risk_usdt', 'atr_mult_orb', 'tp_multiplier', 'orb_window', 'entry_window']
        for mode in expected_modes:
            for key in required_keys:
                self.assertIn(key, MODE_CONFIG[mode], f"MODE_CONFIG[{mode}] missing key: {key}")
    
    def test_get_effective_config(self):
        """Test that get_effective_config properly merges base and mode configs."""
        # Test conservative mode
        config = get_effective_config("BTC/USDT:USDT", "conservative")
        self.assertEqual(config['risk_usdt'], 10.0)  # From conservative mode
        self.assertEqual(config['atr_mult_orb'], 1.5)  # From conservative mode
        self.assertEqual(config['adx_min'], 15.0)  # From base config
        
        # Test moderate mode
        config = get_effective_config("BTC/USDT:USDT", "moderate")
        self.assertEqual(config['risk_usdt'], 20.0)  # From moderate mode
        self.assertEqual(config['atr_mult_orb'], 1.2)  # From moderate mode
        
        # Test aggressive mode
        config = get_effective_config("BTC/USDT:USDT", "aggressive")
        self.assertEqual(config['risk_usdt'], 30.0)  # From aggressive mode
        self.assertEqual(config['atr_mult_orb'], 1.0)  # From aggressive mode
        
        # Test default mode
        config = get_effective_config("BTC/USDT:USDT", None)
        self.assertEqual(config['risk_usdt'], 20.0)  # Should default to moderate
    
    def test_load_trades_prioritizes_mode_specific_files(self):
        """Test that load_trades prioritizes symbol+mode specific files."""
        # Create test data
        test_data = pd.DataFrame({
            'entry_time': [datetime.now() - timedelta(days=i) for i in range(3)],
            'side': ['long', 'short', 'long'],
            'entry_price': [100.0, 101.0, 102.0],
            'exit_price': [105.0, 99.0, 103.0],
            'pnl_usdt': [5.0, -2.0, 1.0],
            'mode': ['conservative', 'conservative', 'conservative']
        })
        
        # Create data directory
        data_dir = Path(self.temp_dir) / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Create mode-specific file
        mode_file = data_dir / "trades_final_BTC_USDT_USDT_conservative.csv"
        test_data.to_csv(mode_file, index=False)
        
        # Create generic file with different data
        generic_data = test_data.copy()
        generic_data['pnl_usdt'] = [10.0, -5.0, 8.0]  # Different PnL values
        generic_data['mode'] = ['moderate', 'moderate', 'moderate']
        generic_file = data_dir / "trades_final_BTC_USDT_USDT.csv"
        generic_data.to_csv(generic_file, index=False)
        
        # Test that load_trades loads the mode-specific file
        result = load_trades("BTC/USDT:USDT", "conservative")
        
        self.assertFalse(result.empty, "Should load trades for conservative mode")
        self.assertEqual(len(result), 3, "Should load 3 trades")
        # Check that it loaded the conservative data (PnL: 5.0, -2.0, 1.0)
        self.assertEqual(result['pnl_usdt'].tolist(), [5.0, -2.0, 1.0])
    
    def test_load_trades_fallback_to_generic(self):
        """Test that load_trades falls back to generic files when mode-specific doesn't exist."""
        # Create test data
        test_data = pd.DataFrame({
            'entry_time': [datetime.now() - timedelta(days=i) for i in range(2)],
            'side': ['long', 'short'],
            'entry_price': [100.0, 101.0],
            'exit_price': [105.0, 99.0],
            'pnl_usdt': [5.0, -2.0]
        })
        
        # Create data directory
        data_dir = Path(self.temp_dir) / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Create only generic file (no mode-specific file)
        generic_file = data_dir / "trades_final_BTC_USDT_USDT.csv"
        test_data.to_csv(generic_file, index=False)
        
        # Test that load_trades falls back to generic file
        result = load_trades("BTC/USDT:USDT", "conservative")
        
        self.assertFalse(result.empty, "Should fallback to generic file")
        self.assertEqual(len(result), 2, "Should load 2 trades from generic file")
    
    def test_load_trades_returns_empty_when_no_files(self):
        """Test that load_trades returns empty DataFrame when no files exist."""
        result = load_trades("BTC/USDT:USDT", "conservative")
        
        self.assertTrue(result.empty, "Should return empty DataFrame when no files exist")
    
    def test_metrics_change_with_different_risk_levels(self):
        """Test that metrics change when using different risk levels."""
        # Create test data with different risk levels
        conservative_data = pd.DataFrame({
            'entry_time': [datetime.now() - timedelta(days=i) for i in range(3)],
            'side': ['long', 'short', 'long'],
            'entry_price': [100.0, 101.0, 102.0],
            'exit_price': [105.0, 99.0, 103.0],
            'pnl_usdt': [2.0, -1.0, 1.5],  # Smaller PnL (conservative risk)
            'r_multiple': [0.2, -0.1, 0.15]
        })
        
        aggressive_data = pd.DataFrame({
            'entry_time': [datetime.now() - timedelta(days=i) for i in range(3)],
            'side': ['long', 'short', 'long'],
            'entry_price': [100.0, 101.0, 102.0],
            'exit_price': [105.0, 99.0, 103.0],
            'pnl_usdt': [10.0, -5.0, 7.5],  # Larger PnL (aggressive risk)
            'r_multiple': [1.0, -0.5, 0.75]
        })
        
        # Calculate metrics for both
        conservative_metrics = compute_metrics(conservative_data)
        aggressive_metrics = compute_metrics(aggressive_data)
        
        # Metrics should be different
        self.assertNotEqual(conservative_metrics['total_pnl'], aggressive_metrics['total_pnl'])
        
        # Conservative should have smaller total PnL
        self.assertLess(conservative_metrics['total_pnl'], aggressive_metrics['total_pnl'])
        
        # Test that win rates are calculated correctly
        self.assertGreater(conservative_metrics['win_rate'], 0)
        self.assertGreater(aggressive_metrics['win_rate'], 0)
    
    def test_mode_column_preserved_in_dataframe(self):
        """Test that mode column is preserved when loading trades."""
        # Create test data with mode column
        test_data = pd.DataFrame({
            'entry_time': [datetime.now() - timedelta(days=i) for i in range(2)],
            'side': ['long', 'short'],
            'entry_price': [100.0, 101.0],
            'exit_price': [105.0, 99.0],
            'pnl_usdt': [5.0, -2.0],
            'mode': ['conservative', 'conservative']
        })
        
        # Create data directory and file
        data_dir = Path(self.temp_dir) / "data"
        data_dir.mkdir(exist_ok=True)
        mode_file = data_dir / "trades_final_BTC_USDT_USDT_conservative.csv"
        test_data.to_csv(mode_file, index=False)
        
        # Load trades
        result = load_trades("BTC/USDT:USDT", "conservative")
        
        # Check that mode column is preserved
        self.assertIn('mode', result.columns, "Mode column should be preserved")
        self.assertEqual(result['mode'].tolist(), ['conservative', 'conservative'])


if __name__ == "__main__":
    unittest.main()
