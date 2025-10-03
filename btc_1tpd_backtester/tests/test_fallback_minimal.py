import unittest
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only the strategy class without the plotting dependencies
from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy


class TestFallbackMinimal(unittest.TestCase):
    def _make_bullish_session(self, date: datetime) -> pd.DataFrame:
        """Create a synthetic bullish session with clear uptrend."""
        tz = timezone.utc
        start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
        end = start + timedelta(days=1)
        idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=tz)
        
        # Create bullish trend: price starts at 100 and ends at 110
        base_price = 100.0
        price_increase = np.linspace(0, 10, len(idx))
        
        # Add some volatility with higher range in middle of day
        volatility = np.sin(np.linspace(0, 4*np.pi, len(idx))) * 2
        
        data = []
        for i, (timestamp, price_inc, vol) in enumerate(zip(idx, price_increase, volatility)):
            open_price = base_price + price_inc
            high_price = open_price + abs(vol) + 1  # Higher volatility in middle
            low_price = open_price - abs(vol) - 0.5
            close_price = open_price + vol * 0.3  # Slight upward bias
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000.0
            })
        
        return pd.DataFrame(data, index=idx)
    
    def _make_bearish_session(self, date: datetime) -> pd.DataFrame:
        """Create a synthetic bearish session with clear downtrend."""
        tz = timezone.utc
        start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
        end = start + timedelta(days=1)
        idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=tz)
        
        # Create bearish trend: price starts at 110 and ends at 100
        base_price = 110.0
        price_decrease = np.linspace(0, -10, len(idx))
        
        # Add some volatility with higher range in middle of day
        volatility = np.sin(np.linspace(0, 4*np.pi, len(idx))) * 2
        
        data = []
        for i, (timestamp, price_dec, vol) in enumerate(zip(idx, price_decrease, volatility)):
            open_price = base_price + price_dec
            high_price = open_price + abs(vol) + 0.5
            low_price = open_price - abs(vol) - 1  # Higher volatility in middle
            close_price = open_price - abs(vol) * 0.3  # Slight downward bias
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000.0
            })
        
        return pd.DataFrame(data, index=idx)
    
    def _make_high_range_session(self, date: datetime) -> pd.DataFrame:
        """Create a session with one candle having significantly higher range."""
        tz = timezone.utc
        start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
        end = start + timedelta(days=1)
        idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=tz)
        
        data = []
        for i, timestamp in enumerate(idx):
            if i == 20:  # Middle of day - create high range candle
                open_price = 100.0
                high_price = 105.0  # 5% range
                low_price = 95.0
                close_price = 102.0
            else:
                open_price = 100.0
                high_price = 100.5  # Small range
                low_price = 99.5
                close_price = 100.0
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000.0
            })
        
        return pd.DataFrame(data, index=idx)
    
    def test_fallback_direction_detection_bullish(self):
        """Test that fallback direction detection correctly identifies bullish trend."""
        date = datetime(2024, 1, 3, tzinfo=timezone.utc)
        session_data = self._make_bullish_session(date)
        
        config = {
            'risk_usdt': 10.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),
            'entry_window': (11, 13),
            'full_day_trading': True,
            'force_one_trade': True,
        }
        
        strategy = SimpleTradingStrategy(config)
        detected_direction = strategy.detect_fallback_direction(session_data)
        
        self.assertEqual(detected_direction, 'long', "Should detect bullish trend as long direction")
    
    def test_fallback_direction_detection_bearish(self):
        """Test that fallback direction detection correctly identifies bearish trend."""
        date = datetime(2024, 1, 3, tzinfo=timezone.utc)
        session_data = self._make_bearish_session(date)
        
        config = {
            'risk_usdt': 10.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),
            'entry_window': (11, 13),
            'full_day_trading': True,
            'force_one_trade': True,
        }
        
        strategy = SimpleTradingStrategy(config)
        detected_direction = strategy.detect_fallback_direction(session_data)
        
        self.assertEqual(detected_direction, 'short', "Should detect bearish trend as short direction")
    
    def test_fallback_entry_time_selection(self):
        """Test that fallback entry time selection finds candle with highest range."""
        date = datetime(2024, 1, 3, tzinfo=timezone.utc)
        session_data = self._make_high_range_session(date)
        
        config = {
            'risk_usdt': 10.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),
            'entry_window': (11, 13),
            'full_day_trading': True,
            'force_one_trade': True,
        }
        
        strategy = SimpleTradingStrategy(config)
        selected_time = strategy.find_best_fallback_entry_time(session_data)
        
        # Should select the candle at index 20 (middle of day) which has the highest range
        expected_time = session_data.index[20]
        self.assertEqual(selected_time, expected_time, "Should select candle with highest range")


if __name__ == '__main__':
    unittest.main()
