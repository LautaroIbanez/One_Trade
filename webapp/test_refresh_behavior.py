#!/usr/bin/env python3
"""
Pruebas para el comportamiento de refresh_trades.
"""

import unittest
import pandas as pd
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta
import sys

# Add the webapp directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import refresh_trades, load_trades


class TestRefreshBehavior(unittest.TestCase):
    """Test cases for refresh_trades behavior."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.original_data_dir = None
        
        # Mock the data directory
        import app
        if hasattr(app, 'repo_root'):
            self.original_data_dir = app.repo_root
            app.repo_root = Path(self.test_dir)
        
        # Create data directory
        data_dir = Path(self.test_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original data directory
        if self.original_data_dir is not None:
            import app
            app.repo_root = self.original_data_dir
        
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_refresh_trades_with_deleted_csv(self):
        """Test that refresh_trades completes successfully when CSV is deleted."""
        symbol = "BTC/USDT:USDT"
        mode = "moderate"
        
        # Ensure CSV doesn't exist
        slug = symbol.replace('/', '_').replace(':', '_')
        mode_suffix = mode.lower()
        data_dir = Path(self.test_dir) / "data"
        csv_file = data_dir / f"trades_final_{slug}_{mode_suffix}.csv"
        meta_file = data_dir / f"trades_final_{slug}_{mode_suffix}_meta.json"
        
        # Remove files if they exist
        if csv_file.exists():
            csv_file.unlink()
        if meta_file.exists():
            meta_file.unlink()
        
        # Call refresh_trades
        try:
            result = refresh_trades(symbol, mode)
            
            # Verify function completed without raising
            self.assertIsInstance(result, str)
            self.assertIn("OK", result)
            
            # Verify CSV file was created
            self.assertTrue(csv_file.exists(), "CSV file should be created after refresh_trades")
            
            # Verify CSV file is not empty (should contain at least headers)
            if csv_file.exists():
                df = pd.read_csv(csv_file)
                # Should have standard columns even if empty
                expected_columns = [
                    "day_key", "entry_time", "side", "entry_price", "sl", "tp", 
                    "exit_time", "exit_price", "exit_reason", "pnl_usdt", 
                    "r_multiple", "used_fallback", "mode"
                ]
                for col in expected_columns:
                    self.assertIn(col, df.columns, f"Column {col} should be present in CSV")
            
            # Verify meta file was created
            self.assertTrue(meta_file.exists(), "Meta file should be created after refresh_trades")
            
            # Verify meta file contains expected data
            if meta_file.exists():
                import json
                with open(meta_file, 'r') as f:
                    meta = json.load(f)
                
                self.assertIn('symbol', meta)
                self.assertIn('mode', meta)
                self.assertEqual(meta['symbol'], symbol)
                self.assertEqual(meta['mode'], mode)
            
        except Exception as e:
            self.fail(f"refresh_trades raised an exception: {e}")
    
    def test_refresh_trades_with_existing_csv(self):
        """Test that refresh_trades works with existing CSV."""
        symbol = "BTC/USDT:USDT"
        mode = "moderate"
        
        # Create a dummy CSV file
        slug = symbol.replace('/', '_').replace(':', '_')
        mode_suffix = mode.lower()
        data_dir = Path(self.test_dir) / "data"
        csv_file = data_dir / f"trades_final_{slug}_{mode_suffix}.csv"
        
        # Create dummy trades data
        dummy_trades = pd.DataFrame({
            'day_key': ['2024-01-01'],
            'entry_time': [datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)],
            'side': ['long'],
            'entry_price': [100.0],
            'sl': [98.0],
            'tp': [102.0],
            'exit_time': [datetime(2024, 1, 1, 18, 0, 0, tzinfo=timezone.utc)],
            'exit_price': [102.0],
            'exit_reason': ['take_profit'],
            'pnl_usdt': [20.0],
            'r_multiple': [1.0],
            'used_fallback': [False],
            'mode': [mode]
        })
        
        dummy_trades.to_csv(csv_file, index=False)
        
        # Call refresh_trades
        try:
            result = refresh_trades(symbol, mode)
            
            # Verify function completed without raising
            self.assertIsInstance(result, str)
            self.assertIn("OK", result)
            
            # Verify CSV file still exists
            self.assertTrue(csv_file.exists(), "CSV file should still exist after refresh_trades")
            
        except Exception as e:
            self.fail(f"refresh_trades raised an exception: {e}")
    
    def test_refresh_trades_different_modes(self):
        """Test refresh_trades with different modes."""
        symbol = "BTC/USDT:USDT"
        
        modes = ["conservative", "moderate", "aggressive"]
        
        for mode in modes:
            with self.subTest(mode=mode):
                # Ensure CSV doesn't exist for this mode
                slug = symbol.replace('/', '_').replace(':', '_')
                mode_suffix = mode.lower()
                data_dir = Path(self.test_dir) / "data"
                csv_file = data_dir / f"trades_final_{slug}_{mode_suffix}.csv"
                meta_file = data_dir / f"trades_final_{slug}_{mode_suffix}_meta.json"
                
                # Remove files if they exist
                if csv_file.exists():
                    csv_file.unlink()
                if meta_file.exists():
                    meta_file.unlink()
                
                # Call refresh_trades
                try:
                    result = refresh_trades(symbol, mode)
                    
                    # Verify function completed without raising
                    self.assertIsInstance(result, str)
                    self.assertIn("OK", result)
                    
                    # Verify CSV file was created
                    self.assertTrue(csv_file.exists(), f"CSV file should be created for mode {mode}")
                    
                    # Verify meta file was created
                    self.assertTrue(meta_file.exists(), f"Meta file should be created for mode {mode}")
                    
                except Exception as e:
                    self.fail(f"refresh_trades raised an exception for mode {mode}: {e}")
    
    def test_load_trades_with_missing_file(self):
        """Test load_trades with missing file."""
        symbol = "BTC/USDT:USDT"
        mode = "moderate"
        
        # Ensure CSV doesn't exist
        slug = symbol.replace('/', '_').replace(':', '_')
        mode_suffix = mode.lower()
        data_dir = Path(self.test_dir) / "data"
        csv_file = data_dir / f"trades_final_{slug}_{mode_suffix}.csv"
        
        if csv_file.exists():
            csv_file.unlink()
        
        # Call load_trades
        try:
            result = load_trades(symbol, mode)
            
            # Should return empty DataFrame
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty, "load_trades should return empty DataFrame when file doesn't exist")
            
        except Exception as e:
            self.fail(f"load_trades raised an exception: {e}")
    
    def test_load_trades_with_existing_file(self):
        """Test load_trades with existing file."""
        symbol = "BTC/USDT:USDT"
        mode = "moderate"
        
        # Create a dummy CSV file
        slug = symbol.replace('/', '_').replace(':', '_')
        mode_suffix = mode.lower()
        data_dir = Path(self.test_dir) / "data"
        csv_file = data_dir / f"trades_final_{slug}_{mode_suffix}.csv"
        
        # Create dummy trades data
        dummy_trades = pd.DataFrame({
            'day_key': ['2024-01-01'],
            'entry_time': [datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)],
            'side': ['long'],
            'entry_price': [100.0],
            'sl': [98.0],
            'tp': [102.0],
            'exit_time': [datetime(2024, 1, 1, 18, 0, 0, tzinfo=timezone.utc)],
            'exit_price': [102.0],
            'exit_reason': ['take_profit'],
            'pnl_usdt': [20.0],
            'r_multiple': [1.0],
            'used_fallback': [False],
            'mode': [mode]
        })
        
        dummy_trades.to_csv(csv_file, index=False)
        
        # Call load_trades
        try:
            result = load_trades(symbol, mode)
            
            # Should return DataFrame with data
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty, "load_trades should return non-empty DataFrame when file exists")
            self.assertEqual(len(result), 1, "Should have 1 trade")
            self.assertEqual(result.iloc[0]['side'], 'long')
            self.assertEqual(result.iloc[0]['entry_price'], 100.0)
            
        except Exception as e:
            self.fail(f"load_trades raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()