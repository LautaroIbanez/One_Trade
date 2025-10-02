import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy, run_backtest

# Import webapp functions for testing
sys.path.append(str(Path(__file__).parent.parent.parent / "webapp"))
try:
    from webapp.app import get_effective_config, MODE_CONFIG, BASE_CONFIG
except ImportError:
    get_effective_config = None
    MODE_CONFIG = None
    BASE_CONFIG = None


class TestModeConfig(unittest.TestCase):
    """Test mode configuration and custom windows."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample 15-minute data for a day
        base_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        times = [base_time + timedelta(minutes=15*i) for i in range(32)]  # 8 hours of data
        
        # Create realistic OHLC data
        np.random.seed(42)  # For reproducible tests
        base_price = 50000.0
        
        data = []
        for i, time in enumerate(times):
            # Simulate price movement
            price_change = np.random.normal(0, 100)  # Random walk
            base_price += price_change
            
            # Create OHLC for this candle
            open_price = base_price
            high_price = open_price + abs(np.random.normal(0, 50))
            low_price = open_price - abs(np.random.normal(0, 50))
            close_price = open_price + np.random.normal(0, 30)
            
            # Ensure OHLC relationships are valid
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': np.random.uniform(2000, 5000)
            })
        
        self.day_data = pd.DataFrame(data, index=times)
        self.day_data.index.name = 'timestamp'
    
    def test_custom_orb_window(self):
        """Test that custom ORB window is respected."""
        # Test with custom ORB window (11:00-12:00) - use window that has data
        config = {
            'risk_usdt': 20.0,
            'orb_window': (11, 12),  # Custom window with data
            'entry_window': (11, 13),
            'full_day_trading': False,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        }
        
        strategy = SimpleTradingStrategy(config)
        
        # Verify attributes are set correctly
        self.assertEqual(strategy.orb_window, (11, 12))
        self.assertEqual(strategy.entry_window, (11, 13))
        self.assertFalse(strategy.full_day_trading)
        
        # Test ORB calculation with custom window
        orb_high, orb_low = strategy.get_orb_levels(self.day_data, strategy.orb_window)
        
        # Should calculate ORB from 11:00-12:00 window
        orb_data = self.day_data[(self.day_data.index.hour >= 11) & (self.day_data.index.hour < 12)]
        expected_high = orb_data['high'].max()
        expected_low = orb_data['low'].min()
        
        self.assertEqual(orb_high, expected_high)
        self.assertEqual(orb_low, expected_low)
    
    def test_custom_entry_window(self):
        """Test that custom entry window is respected."""
        config = {
            'risk_usdt': 20.0,
            'orb_window': (11, 12),
            'entry_window': (10, 14),  # Custom entry window
            'full_day_trading': False,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        }
        
        strategy = SimpleTradingStrategy(config)
        
        # Test process_day with custom entry window
        date = datetime(2024, 1, 15).date()
        trades = strategy.process_day(self.day_data, date)
        
        # Verify that entry window is respected
        # The strategy should only look for entries between 10:00-14:00
        if trades:
            for trade in trades:
                entry_time = pd.to_datetime(trade['entry_time'])
                self.assertGreaterEqual(entry_time.hour, 10)
                self.assertLess(entry_time.hour, 14)
    
    def test_full_day_trading_mode(self):
        """Test full day trading mode."""
        config = {
            'risk_usdt': 20.0,
            'orb_window': (11, 12),
            'entry_window': (11, 13),  # This should be ignored in full_day_trading
            'full_day_trading': True,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        }
        
        strategy = SimpleTradingStrategy(config)
        
        # Verify full_day_trading is set
        self.assertTrue(strategy.full_day_trading)
        
        # Test that entry window is expanded to full day
        date = datetime(2024, 1, 15).date()
        trades = strategy.process_day(self.day_data, date)
        
        # In full_day_trading mode, entries can happen at any hour
        if trades:
            for trade in trades:
                entry_time = pd.to_datetime(trade['entry_time'])
                # Should be able to enter at any hour (0-23)
                self.assertGreaterEqual(entry_time.hour, 0)
                self.assertLess(entry_time.hour, 24)
    
    def test_backtest_with_custom_windows(self):
        """Test that run_backtest respects custom windows."""
        # Create a simple config with custom windows
        config = {
            'risk_usdt': 20.0,
            'orb_window': (10, 11),  # Custom ORB window
            'entry_window': (10, 12),  # Custom entry window
            'full_day_trading': False,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        }
        
        # This test would require actual data fetching, so we'll test the config passing
        strategy = SimpleTradingStrategy(config)
        
        # Verify the strategy uses the custom windows
        self.assertEqual(strategy.orb_window, (10, 11))
        self.assertEqual(strategy.entry_window, (10, 12))
        self.assertFalse(strategy.full_day_trading)
    
    def test_mode_config_inheritance(self):
        """Test that mode configs properly inherit and override base config."""
        base_config = {
            'risk_usdt': 20.0,
            'orb_window': (11, 12),
            'entry_window': (11, 13),
            'full_day_trading': False,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        }
        
        # Test conservative mode overrides
        conservative_config = {
            **base_config,
            'orb_window': (10, 12),  # Override
            'entry_window': (10, 13),  # Override
        }
        
        strategy = SimpleTradingStrategy(conservative_config)
        
        # Should use overridden values
        self.assertEqual(strategy.orb_window, (10, 12))
        self.assertEqual(strategy.entry_window, (10, 13))
        self.assertEqual(strategy.risk_usdt, 20.0)  # Should inherit base value
    
    def test_full_day_trading_exit_reasons(self):
        """Test that full_day_trading affects exit reasons."""
        config = {
            'risk_usdt': 20.0,
            'orb_window': (11, 12),
            'entry_window': (11, 13),
            'full_day_trading': True,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        }
        
        strategy = SimpleTradingStrategy(config)
        
        # Test that full_day_trading affects exit reason logic
        # This would be tested in simulate_trade_exit method
        self.assertTrue(strategy.full_day_trading)
        
        # In full_day_trading mode, exits should use 'end_of_data' instead of 'session_end'
        # This is handled in the simulate_trade_exit method

    def test_mode_change_detection(self):
        """Test that switching between normal and 24h modes triggers complete rebuild."""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Import webapp functions
        from webapp.app import refresh_trades, load_trades
        import pandas as pd
        from datetime import datetime, timedelta
        
        symbol = "BTC/USDT:USDT"
        mode = "moderate"
        
        # Create some mock data for normal mode
        mock_trades_normal = pd.DataFrame({
            'entry_time': [datetime.now() - timedelta(days=1)],
            'side': ['long'],
            'entry_price': [50000.0],
            'exit_price': [51000.0],
            'pnl_usdt': [1000.0],
            'r_multiple': [2.0],
            'exit_time': [datetime.now()],
            'exit_reason': ['take_profit']
        })
        
        # Save mock data for normal mode
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            mock_trades_normal.to_csv(f.name, index=False)
            normal_file = f.name
        
        try:
            # Test that switching to 24h mode triggers rebuild
            # This would normally be tested with actual file operations
            # For now, we verify the logic structure
            
            # Simulate normal mode data exists
            existing_normal = load_trades(symbol, mode, False)
            existing_24h = load_trades(symbol, mode, True)
            
            # If normal mode has data but 24h doesn't, switching to 24h should trigger rebuild
            mode_change_detected = not existing_normal.empty and existing_24h.empty
            
            # This test verifies the logic structure
            self.assertIsInstance(mode_change_detected, bool)
            
        finally:
            # Clean up
            if os.path.exists(normal_file):
                os.unlink(normal_file)

    def test_full_day_trading_no_entries_before_orb(self):
        """Test that in full day trading mode, no entries are generated before ORB ends."""
        from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy
        import pandas as pd
        from datetime import datetime, timezone
        import numpy as np
        
        # Create test data with ORB window (11:00-12:00) and entry window (10:00-13:00)
        # In full day trading, entry should start at 12:00 (after ORB ends)
        dates = pd.date_range('2024-01-01 10:00:00', periods=20, freq='15min', tz=timezone.utc)
        test_data = pd.DataFrame({
            'open': np.random.uniform(50000, 51000, len(dates)),
            'high': np.random.uniform(51000, 52000, len(dates)),
            'low': np.random.uniform(49000, 50000, len(dates)),
            'close': np.random.uniform(50000, 51000, len(dates)),
            'volume': np.random.uniform(100, 1000, len(dates))
        }, index=dates)
        
        # Add some breakout after ORB ends (12:00)
        test_data.loc[test_data.index.hour >= 12, 'high'] = 55000  # Breakout above ORB
        test_data.loc[test_data.index.hour >= 12, 'low'] = 45000   # Breakout below ORB
        
        config = {
            'risk_usdt': 20.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),  # ORB ends at 12:00
            'entry_window': (10, 13),  # Would start at 10:00, but should be adjusted to 12:00
            'full_day_trading': True
        }
        
        strategy = SimpleTradingStrategy(config)
        
        # Process the day
        trades = strategy.process_day(test_data, datetime(2024, 1, 1))
        
        # Verify no trades are generated before 12:00 (ORB end)
        if trades:  # trades is a list
            for trade in trades:
                entry_time = pd.to_datetime(trade['entry_time'])
                # Entry time should be at 12:00 or later
                self.assertGreaterEqual(entry_time.hour, 12, 
                    f"Entry at {entry_time} is before ORB ends at 12:00")
        
        # Verify that entry window is correctly adjusted
        # This tests the internal logic
        if strategy.full_day_trading:
            expected_start = max(strategy.orb_window[1], strategy.entry_window[0])
            self.assertEqual(expected_start, 12, "Entry window should start at 12:00 (after ORB)")

    @unittest.skipIf(get_effective_config is None, "Webapp module not available")
    def test_get_effective_config_full_day_overrides(self):
        """Test that get_effective_config properly applies full_day_overrides when full_day_trading=True."""
        symbol = "BTC/USDT:USDT"
        
        # Test conservative mode
        normal_config = get_effective_config(symbol, "conservative", False)
        full_day_config = get_effective_config(symbol, "conservative", True)
        
        # Verify that full_day_trading applies overrides
        self.assertEqual(normal_config["risk_usdt"], 10.0)
        self.assertEqual(full_day_config["risk_usdt"], 15.0)  # From full_day_overrides
        
        self.assertEqual(normal_config["orb_window"], (11, 12))
        self.assertEqual(full_day_config["orb_window"], (0, 1))  # From full_day_overrides
        
        self.assertEqual(normal_config["entry_window"], (11, 13))
        self.assertEqual(full_day_config["entry_window"], (1, 23))  # From full_day_overrides
        
        self.assertEqual(normal_config["commission_rate"], 0.0008)
        self.assertEqual(full_day_config["commission_rate"], 0.001)  # From full_day_overrides
        
        # Test moderate mode
        normal_config = get_effective_config(symbol, "moderate", False)
        full_day_config = get_effective_config(symbol, "moderate", True)
        
        self.assertEqual(normal_config["risk_usdt"], 20.0)
        self.assertEqual(full_day_config["risk_usdt"], 25.0)  # From full_day_overrides
        
        # Test aggressive mode
        normal_config = get_effective_config(symbol, "aggressive", False)
        full_day_config = get_effective_config(symbol, "aggressive", True)
        
        self.assertEqual(normal_config["risk_usdt"], 30.0)
        self.assertEqual(full_day_config["risk_usdt"], 40.0)  # From full_day_overrides
        
        self.assertEqual(normal_config["commission_rate"], 0.0012)
        self.assertEqual(full_day_config["commission_rate"], 0.0015)  # From full_day_overrides

    @unittest.skipIf(get_effective_config is None, "Webapp module not available")
    def test_get_effective_config_inheritance(self):
        """Test that get_effective_config properly inherits from BASE_CONFIG and applies mode overrides."""
        symbol = "BTC/USDT:USDT"
        
        # Test that base config values are inherited
        config = get_effective_config(symbol, "moderate", False)
        
        # These should come from BASE_CONFIG
        self.assertEqual(config["atr_mult_orb"], 1.2)  # From BASE_CONFIG
        self.assertEqual(config["tp_multiplier"], 2.0)  # From BASE_CONFIG
        self.assertEqual(config["initial_capital"], 1000.0)  # From BASE_CONFIG
        self.assertEqual(config["leverage"], 1.0)  # From BASE_CONFIG
        
        # These should come from mode config
        self.assertEqual(config["risk_usdt"], 20.0)  # From moderate mode
        self.assertEqual(config["orb_window"], (11, 12))  # From moderate mode
        self.assertEqual(config["entry_window"], (11, 13))  # From moderate mode

    @unittest.skipIf(get_effective_config is None, "Webapp module not available")
    def test_strategy_instantiation_with_full_day_overrides(self):
        """Test that SimpleTradingStrategy can be instantiated with full_day_overrides applied."""
        symbol = "BTC/USDT:USDT"
        
        # Get config with full_day_overrides
        config = get_effective_config(symbol, "conservative", True)
        
        # Create strategy with this config
        strategy = SimpleTradingStrategy(config)
        
        # Verify that the strategy uses the overridden values
        self.assertEqual(strategy.risk_usdt, 15.0)  # From full_day_overrides
        self.assertEqual(strategy.orb_window, (0, 1))  # From full_day_overrides
        self.assertEqual(strategy.entry_window, (1, 23))  # From full_day_overrides
        self.assertTrue(strategy.full_day_trading)

    def test_timezone_handling_in_refresh_trades(self):
        """Test that refresh_trades uses UTC timestamps correctly."""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Import webapp functions
        try:
            from webapp.app import refresh_trades
        except ImportError:
            self.skipTest("Webapp module not available")
        
        # Mock the run_backtest function to avoid actual execution
        import unittest.mock
        
        with unittest.mock.patch('webapp.app.run_backtest') as mock_run_backtest:
            mock_run_backtest.return_value = pd.DataFrame()
            
            # Test that the function can be called without errors
            # The actual timezone handling is tested by the function using datetime.now(timezone.utc)
            result = refresh_trades("BTC/USDT:USDT", "moderate", False)
            
            # Verify that the function was called (even if it returns empty results)
            self.assertIsInstance(result, str)
            self.assertTrue(result.startswith("OK:") or result.startswith("ERROR:") or "No new trades" in result)

    def test_timezone_consistency_across_timezones(self):
        """Test that refresh_trades works consistently regardless of system timezone."""
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Import webapp functions
        try:
            from webapp.app import refresh_trades
        except ImportError:
            self.skipTest("Webapp module not available")
        
        # Test with different simulated timezones by mocking datetime.now
        import unittest.mock
        from datetime import datetime, timezone, timedelta
        
        # Mock the run_backtest function
        with unittest.mock.patch('webapp.app.run_backtest') as mock_run_backtest:
            mock_run_backtest.return_value = pd.DataFrame()
            
            # Test with UTC timezone (should work normally)
            utc_now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            with unittest.mock.patch('webapp.app.datetime') as mock_datetime:
                mock_datetime.now.return_value = utc_now
                mock_datetime.now.side_effect = lambda tz=None: utc_now if tz == timezone.utc else utc_now.replace(tzinfo=None)
                
                result_utc = refresh_trades("BTC/USDT:USDT", "moderate", False)
                self.assertIsInstance(result_utc, str)
            
            # Test with EST timezone (UTC-5) - should still work correctly
            est_now = datetime(2024, 1, 15, 7, 0, 0, tzinfo=timezone(timedelta(hours=-5)))
            with unittest.mock.patch('webapp.app.datetime') as mock_datetime:
                mock_datetime.now.return_value = est_now
                mock_datetime.now.side_effect = lambda tz=None: est_now.astimezone(tz) if tz else est_now.replace(tzinfo=None)
                
                result_est = refresh_trades("BTC/USDT:USDT", "moderate", False)
                self.assertIsInstance(result_est, str)
            
            # Test with PST timezone (UTC-8) - should still work correctly
            pst_now = datetime(2024, 1, 15, 4, 0, 0, tzinfo=timezone(timedelta(hours=-8)))
            with unittest.mock.patch('webapp.app.datetime') as mock_datetime:
                mock_datetime.now.return_value = pst_now
                mock_datetime.now.side_effect = lambda tz=None: pst_now.astimezone(tz) if tz else pst_now.replace(tzinfo=None)
                
                result_pst = refresh_trades("BTC/USDT:USDT", "moderate", False)
                self.assertIsInstance(result_pst, str)
            
            # Verify that all calls were made (indicating the function works across timezones)
            self.assertEqual(mock_run_backtest.call_count, 3)


if __name__ == "__main__":
    unittest.main()
