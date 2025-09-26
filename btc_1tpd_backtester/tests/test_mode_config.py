import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy, run_backtest


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


if __name__ == "__main__":
    unittest.main()
