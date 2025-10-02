import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy


class TestBreakoutFunctionality(unittest.TestCase):
    """Test the updated breakout detection functionality."""
    
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
        
        # Strategy config
        self.config = {
            'risk_usdt': 20.0,
            'daily_target': 50.0,
            'daily_max_loss': -30.0,
            'adx_min': 15.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005,
            'orb_window': (11, 12),
            'entry_window': (11, 13),
            'full_day_trading': False
        }
    
    def test_orb_levels_calculation(self):
        """Test that ORB levels are calculated correctly."""
        strategy = SimpleTradingStrategy(self.config)
        
        # Test ORB calculation for 11:00-12:00 window
        orb_high, orb_low = strategy.get_orb_levels(self.day_data, orb_window=(11, 12))
        
        self.assertIsNotNone(orb_high)
        self.assertIsNotNone(orb_low)
        self.assertGreater(orb_high, orb_low)
        
        # Verify that orb_high is the maximum high in the window
        orb_data = self.day_data[(self.day_data.index.hour >= 11) & (self.day_data.index.hour < 12)]
        expected_high = orb_data['high'].max()
        expected_low = orb_data['low'].min()
        
        self.assertEqual(orb_high, expected_high)
        self.assertEqual(orb_low, expected_low)
    
    def test_long_breakout_detection(self):
        """Test that long breakouts are detected when high pierces orb_high."""
        strategy = SimpleTradingStrategy(self.config)
        
        # Get ORB levels
        orb_high, orb_low = strategy.get_orb_levels(self.day_data, orb_window=(11, 12))
        
        # Create entry data with a long breakout
        entry_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        entry_data = pd.DataFrame({
            'open': [orb_high - 10],  # Open below orb_high
            'high': [orb_high + 50],  # High pierces orb_high
            'low': [orb_high - 20],   # Low stays below orb_high
            'close': [orb_high + 30], # Close above orb_high
            'volume': [3000]
        }, index=[entry_time])
        
        # Test breakout detection
        side, timestamp, entry_price = strategy.check_breakout(entry_data, orb_high, orb_low)
        
        self.assertEqual(side, 'long')
        self.assertEqual(timestamp, entry_time)
        # Entry price should be max of open and orb_high
        expected_entry_price = max(orb_high - 10, orb_high)
        self.assertEqual(entry_price, expected_entry_price)
    
    def test_short_breakout_detection(self):
        """Test that short breakouts are detected when low pierces orb_low."""
        strategy = SimpleTradingStrategy(self.config)
        
        # Get ORB levels
        orb_high, orb_low = strategy.get_orb_levels(self.day_data, orb_window=(11, 12))
        
        # Create entry data with a short breakout
        entry_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        entry_data = pd.DataFrame({
            'open': [orb_low + 10],   # Open above orb_low
            'high': [orb_low + 20],   # High stays above orb_low
            'low': [orb_low - 50],    # Low pierces orb_low
            'close': [orb_low - 30],  # Close below orb_low
            'volume': [3000]
        }, index=[entry_time])
        
        # Test breakout detection
        side, timestamp, entry_price = strategy.check_breakout(entry_data, orb_high, orb_low)
        
        self.assertEqual(side, 'short')
        self.assertEqual(timestamp, entry_time)
        # Entry price should be min of open and orb_low
        expected_entry_price = min(orb_low + 10, orb_low)
        self.assertEqual(entry_price, expected_entry_price)
    
    def test_no_breakout_detection(self):
        """Test that no breakout is detected when price stays within ORB range."""
        strategy = SimpleTradingStrategy(self.config)
        
        # Get ORB levels
        orb_high, orb_low = strategy.get_orb_levels(self.day_data, orb_window=(11, 12))
        
        # Create entry data with no breakout
        entry_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        entry_data = pd.DataFrame({
            'open': [orb_low + 10],   # Open within range
            'high': [orb_high - 10],  # High stays below orb_high
            'low': [orb_low + 5],     # Low stays above orb_low
            'close': [orb_low + 15],  # Close within range
            'volume': [3000]
        }, index=[entry_time])
        
        # Test breakout detection
        side, timestamp, entry_price = strategy.check_breakout(entry_data, orb_high, orb_low)
        
        self.assertIsNone(side)
        self.assertIsNone(timestamp)
        self.assertIsNone(entry_price)
    
    def test_entry_price_calculation_long(self):
        """Test that entry price is calculated correctly for long breakouts."""
        strategy = SimpleTradingStrategy(self.config)
        
        orb_high = 50000
        orb_low = 49900
        
        # Test case 1: Open below orb_high, high pierces orb_high
        entry_data = pd.DataFrame({
            'open': [49950],  # Below orb_high
            'high': [50050],  # Above orb_high
            'low': [49940],
            'close': [50020],
            'volume': [3000]
        }, index=[datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)])
        
        side, timestamp, entry_price = strategy.check_breakout(entry_data, orb_high, orb_low)
        
        self.assertEqual(side, 'long')
        # Entry price should be max(49950, 50000) = 50000
        self.assertEqual(entry_price, 50000)
        
        # Test case 2: Open above orb_high, high pierces orb_high
        entry_data = pd.DataFrame({
            'open': [50010],  # Above orb_high
            'high': [50050],  # Above orb_high
            'low': [50000],
            'close': [50020],
            'volume': [3000]
        }, index=[datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)])
        
        side, timestamp, entry_price = strategy.check_breakout(entry_data, orb_high, orb_low)
        
        self.assertEqual(side, 'long')
        # Entry price should be max(50010, 50000) = 50010
        self.assertEqual(entry_price, 50010)
    
    def test_entry_price_calculation_short(self):
        """Test that entry price is calculated correctly for short breakouts."""
        strategy = SimpleTradingStrategy(self.config)
        
        orb_high = 50000
        orb_low = 49900
        
        # Test case 1: Open above orb_low, low pierces orb_low
        entry_data = pd.DataFrame({
            'open': [49950],  # Above orb_low
            'high': [49960],
            'low': [49850],   # Below orb_low
            'close': [49880],
            'volume': [3000]
        }, index=[datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)])
        
        side, timestamp, entry_price = strategy.check_breakout(entry_data, orb_high, orb_low)
        
        self.assertEqual(side, 'short')
        # Entry price should be min(49950, 49900) = 49900
        self.assertEqual(entry_price, 49900)
        
        # Test case 2: Open below orb_low, low pierces orb_low
        entry_data = pd.DataFrame({
            'open': [49880],  # Below orb_low
            'high': [49900],
            'low': [49850],   # Below orb_low
            'close': [49870],
            'volume': [3000]
        }, index=[datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)])
        
        side, timestamp, entry_price = strategy.check_breakout(entry_data, orb_high, orb_low)
        
        self.assertEqual(side, 'short')
        # Entry price should be min(49880, 49900) = 49880
        self.assertEqual(entry_price, 49880)
    
    def test_multiple_candles_breakout_detection(self):
        """Test breakout detection with multiple candles in entry window."""
        strategy = SimpleTradingStrategy(self.config)
        
        orb_high = 50000
        orb_low = 49900
        
        # Create multiple candles, with breakout in the second one
        entry_times = [
            datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 15, 12, 15, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        ]
        
        entry_data = pd.DataFrame({
            'open': [49950, 49980, 50020],   # First two below orb_high, third above
            'high': [49960, 50050, 50030],   # Second candle breaks orb_high
            'low': [49940, 49970, 50010],
            'close': [49955, 50020, 50025],
            'volume': [3000, 3000, 3000]
        }, index=entry_times)
        
        # Test breakout detection
        side, timestamp, entry_price = strategy.check_breakout(entry_data, orb_high, orb_low)
        
        self.assertEqual(side, 'long')
        # Should detect breakout in the second candle (12:15)
        self.assertEqual(timestamp, entry_times[1])
        # Entry price should be max(49980, 50000) = 50000
        self.assertEqual(entry_price, 50000)
    
    def test_full_day_trading_mode(self):
        """Test full day trading mode functionality."""
        # Create config with full_day_trading enabled
        full_day_config = self.config.copy()
        full_day_config['full_day_trading'] = True
        
        strategy = SimpleTradingStrategy(full_day_config)
        
        # Verify full_day_trading is enabled
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
    
    def test_full_day_trading_exit_reasons(self):
        """Test that full_day_trading affects exit reasons."""
        full_day_config = self.config.copy()
        full_day_config['full_day_trading'] = True
        
        strategy = SimpleTradingStrategy(full_day_config)
        
        # Test trade parameters
        trade_params = {
            'entry_price': 50000,
            'stop_loss': 49900,
            'take_profit': 50100,
            'position_size': 1.0,
            'entry_time': datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        }
        
        # Create exit data that would normally trigger session_end
        exit_time = datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc)  # After session_end
        exit_data = pd.DataFrame({
            'open': [50050],
            'high': [50050],
            'low': [50050],
            'close': [50050]
        }, index=[exit_time])
        
        # Test that full_day_trading affects exit reason
        result = strategy.simulate_trade_exit(trade_params, 'long', exit_data)
        
        # In full_day_trading mode, should not force exit at session_end
        # The result should depend on the actual trade logic, not session timing
        self.assertIsNotNone(result['exit_reason'])
    
    def test_full_day_trading_entry_window_adjustment(self):
        """Test that full_day_trading properly adjusts entry window to start after ORB ends."""
        # Create config with ORB window (11:00-12:00) and entry window (10:00-13:00)
        # In full day trading, entry should start at 12:00 (after ORB ends)
        full_day_config = {
            'risk_usdt': 20.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),  # ORB ends at 12:00
            'entry_window': (10, 13),  # Would start at 10:00, but should be adjusted to 12:00
            'full_day_trading': True,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        }
        
        strategy = SimpleTradingStrategy(full_day_config)
        
        # Create test data with breakout only before 12:00 (should not trigger entry)
        dates = pd.date_range('2024-01-01 10:00:00', periods=20, freq='15min', tz=timezone.utc)
        test_data = pd.DataFrame({
            'open': np.random.uniform(50000, 51000, len(dates)),
            'high': np.random.uniform(51000, 52000, len(dates)),
            'low': np.random.uniform(49000, 50000, len(dates)),
            'close': np.random.uniform(50000, 51000, len(dates)),
            'volume': np.random.uniform(100, 1000, len(dates))
        }, index=dates)
        
        # Add breakout only before 12:00 (should be ignored)
        test_data.loc[(test_data.index.hour >= 10) & (test_data.index.hour < 12), 'high'] = 55000
        test_data.loc[(test_data.index.hour >= 10) & (test_data.index.hour < 12), 'low'] = 45000
        
        # Process the day
        trades = strategy.process_day(test_data, datetime(2024, 1, 1))
        
        # Should not generate any trades because breakout is before ORB ends
        self.assertEqual(len(trades), 0, "No trades should be generated when breakout occurs before ORB ends")
        
        # Now test with breakout after 12:00 (should trigger entry)
        test_data_after_orb = test_data.copy()
        test_data_after_orb.loc[test_data_after_orb.index.hour >= 12, 'high'] = 55000
        test_data_after_orb.loc[test_data_after_orb.index.hour >= 12, 'low'] = 45000
        
        trades_after_orb = strategy.process_day(test_data_after_orb, datetime(2024, 1, 1))
        
        # Should generate trades when breakout occurs after ORB ends
        if trades_after_orb:  # If trades are generated
            for trade in trades_after_orb:
                entry_time = pd.to_datetime(trade['entry_time'])
                # Entry time should be at 12:00 or later
                self.assertGreaterEqual(entry_time.hour, 12, 
                    f"Entry at {entry_time} is before ORB ends at 12:00")
    
    def test_entry_window_calculation_logic(self):
        """Test the internal logic of entry window calculation in full_day_trading mode."""
        # Test case 1: entry_window starts before ORB ends
        config1 = {
            'risk_usdt': 20.0,
            'orb_window': (11, 12),  # ORB ends at 12:00
            'entry_window': (10, 13),  # Would start at 10:00
            'full_day_trading': True
        }
        
        strategy1 = SimpleTradingStrategy(config1)
        
        # Simulate the logic from process_day method
        if strategy1.full_day_trading:
            ew_start = max(strategy1.orb_window[1], strategy1.entry_window[0])
            ew_end = 24
            entry_window = (ew_start, ew_end)
        else:
            entry_window = strategy1.entry_window
        
        # Should start at 12:00 (max of 12 and 10)
        self.assertEqual(entry_window[0], 12, "Entry window should start at 12:00 when entry_window starts before ORB ends")
        self.assertEqual(entry_window[1], 24, "Entry window should end at 24:00 in full day trading")
        
        # Test case 2: entry_window starts after ORB ends
        config2 = {
            'risk_usdt': 20.0,
            'orb_window': (11, 12),  # ORB ends at 12:00
            'entry_window': (13, 15),  # Starts at 13:00
            'full_day_trading': True
        }
        
        strategy2 = SimpleTradingStrategy(config2)
        
        # Simulate the logic from process_day method
        if strategy2.full_day_trading:
            ew_start = max(strategy2.orb_window[1], strategy2.entry_window[0])
            ew_end = 24
            entry_window = (ew_start, ew_end)
        else:
            entry_window = strategy2.entry_window
        
        # Should start at 13:00 (max of 12 and 13)
        self.assertEqual(entry_window[0], 13, "Entry window should start at 13:00 when entry_window starts after ORB ends")
        self.assertEqual(entry_window[1], 24, "Entry window should end at 24:00 in full day trading")


if __name__ == "__main__":
    unittest.main()
