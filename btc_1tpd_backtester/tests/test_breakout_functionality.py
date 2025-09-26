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
            'slippage_rate': 0.0005
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


if __name__ == "__main__":
    unittest.main()
