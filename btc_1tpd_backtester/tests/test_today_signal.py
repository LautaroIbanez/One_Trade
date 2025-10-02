import unittest
from datetime import datetime, timezone
import pandas as pd
import numpy as np

from btc_1tpd_backtester.signals.today_signal import get_today_trade_recommendation, _find_breakout_in_entry_window
from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy


class TestTodaySignal(unittest.TestCase):
    def test_output_structure(self):
        # Use a fixed time outside trading window to avoid live data dependency
        now = datetime(2024, 9, 20, 18, 0, 0, tzinfo=timezone.utc)
        config = {"risk_usdt": 10.0, "atr_mult_orb": 1.2, "tp_multiplier": 2.0, "adx_min": 15.0}

        # We cannot fetch real data in unit tests; just ensure the function runs and returns required keys.
        # If data fetch fails, function should return status=no_data and still include keys.
        result = get_today_trade_recommendation("BTC/USDT:USDT", config, now=now)

        required_keys = {
            "status", "symbol", "date", "macro_bias",
            "orb_high", "orb_low", "notes"
        }

        self.assertTrue(required_keys.issubset(result.keys()))

    def test_exit_time_defined_on_last_candle(self):
        idx = pd.date_range("2024-06-01 11:00:00+00:00", periods=8, freq="15min")
        day = pd.DataFrame({
            "open": np.linspace(100, 108, len(idx)),
            "high": np.linspace(101, 109, len(idx)),
            "low": np.linspace(99, 107, len(idx)),
            "close": np.linspace(100, 108, len(idx)),
            "volume": np.ones(len(idx)),
        }, index=idx)

        strategy = SimpleTradingStrategy({
            "risk_usdt": 20.0,
            "daily_target": 50.0,
            "daily_max_loss": -30.0,
            "adx_min": 10.0,
            "atr_mult_orb": 1.2,
            "tp_multiplier": 2.0,
        })

        trade_params = {
            "entry_price": float(day["close"].iloc[-1]),
            "stop_loss": float(day["close"].iloc[-1] - 1.0),
            "take_profit": float(day["close"].iloc[-1] + 2.0),
            "position_size": 1.0,
            "entry_time": day.index[-1],
        }

        exit_info = strategy.simulate_trade_exit(trade_params, "long", day)
        self.assertIn("exit_time", exit_info)
        self.assertIsNotNone(exit_info["exit_time"])
        self.assertEqual(exit_info["exit_reason"], "session_end")

    def test_after_session_preserves_trade_details_when_breakout_occurred(self):
        # This test only checks function keys/logic path; actual data fetch may fail.
        # Use a time after entry window and expect function to either return details or no_data gracefully.
        now = datetime(2024, 9, 20, 18, 0, 0, tzinfo=timezone.utc)
        config = {"risk_usdt": 10.0, "atr_mult_orb": 1.2, "tp_multiplier": 2.0, "adx_min": 15.0,
                  "orb_window": (11, 12), "entry_window": (11, 13)}
        result = get_today_trade_recommendation("BTC/USDT:USDT", config, now=now)
        self.assertIn("status", result)
        # If data is available, and a breakout happened, new statuses should be possible
        allowed = {"no_data", "session_closed", "session_closed_triggered", "session_closed_params_unavailable"}
        self.assertIn(result["status"], allowed)

    def test_full_day_trading_entry_window(self):
        """Test that entry_window=(0, 24) works correctly without exceptions."""
        # Use a fixed time to avoid live data dependency
        now = datetime(2024, 9, 20, 12, 0, 0, tzinfo=timezone.utc)
        config = {
            "risk_usdt": 10.0, 
            "atr_mult_orb": 1.2, 
            "tp_multiplier": 2.0, 
            "adx_min": 15.0,
            "orb_window": (11, 12),
            "entry_window": (0, 24),  # Full day trading
            "full_day_trading": True
        }

        # Test that the function runs without exceptions
        try:
            result = get_today_trade_recommendation("BTC/USDT:USDT", config, now=now)
            
            # Verify the result has the expected structure
            required_keys = {
                "status", "symbol", "date", "macro_bias",
                "orb_high", "orb_low", "notes"
            }
            self.assertTrue(required_keys.issubset(result.keys()))
            
            # Verify the result is a valid state (not an error)
            valid_statuses = [
                "awaiting_orb", "no_orb_levels", "awaiting_breakout", 
                "long", "short", "no_data", "no_breakout",
                "trigger_detected_params_unavailable", "session_closed",
                "session_closed_triggered", "session_closed_params_unavailable"
            ]
            self.assertIn(result["status"], valid_statuses)
            
        except Exception as e:
            self.fail(f"get_today_trade_recommendation raised an exception with entry_window=(0, 24): {e}")

    def test_breakout_strict_comparison_high_equals_orb(self):
        """Test that when high only equals ORB high, no breakout is detected (strict comparison)."""
        # Create test data where high equals ORB high but doesn't exceed it
        idx = pd.date_range("2024-06-01 12:00:00+00:00", periods=4, freq="15min")
        entry_data = pd.DataFrame({
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [105.0, 105.0, 105.0, 105.0],  # High equals ORB high
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [101.0, 102.0, 103.0, 104.0],
            "volume": [1000, 1000, 1000, 1000],
        }, index=idx)
        
        orb_high = 105.0  # Same as high values
        orb_low = 95.0
        
        # Test the breakout detection
        side, timestamp, entry_price = _find_breakout_in_entry_window(entry_data, orb_high, orb_low)
        
        # Should return None values since high only equals ORB (strict comparison)
        self.assertIsNone(side)
        self.assertIsNone(timestamp)
        self.assertIsNone(entry_price)

    def test_breakout_strict_comparison_low_equals_orb(self):
        """Test that when low only equals ORB low, no breakout is detected (strict comparison)."""
        # Create test data where low equals ORB low but doesn't go below it
        idx = pd.date_range("2024-06-01 12:00:00+00:00", periods=4, freq="15min")
        entry_data = pd.DataFrame({
            "open": [100.0, 99.0, 98.0, 97.0],
            "high": [101.0, 100.0, 99.0, 98.0],
            "low": [95.0, 95.0, 95.0, 95.0],  # Low equals ORB low
            "close": [99.0, 98.0, 97.0, 96.0],
            "volume": [1000, 1000, 1000, 1000],
        }, index=idx)
        
        orb_high = 105.0
        orb_low = 95.0  # Same as low values
        
        # Test the breakout detection
        side, timestamp, entry_price = _find_breakout_in_entry_window(entry_data, orb_high, orb_low)
        
        # Should return None values since low only equals ORB (strict comparison)
        self.assertIsNone(side)
        self.assertIsNone(timestamp)
        self.assertIsNone(entry_price)

    def test_breakout_strict_comparison_high_exceeds_orb(self):
        """Test that when high exceeds ORB high, long breakout is detected."""
        # Create test data where high exceeds ORB high
        idx = pd.date_range("2024-06-01 12:00:00+00:00", periods=4, freq="15min")
        entry_data = pd.DataFrame({
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [105.0, 105.0, 106.0, 105.0],  # One candle exceeds ORB high
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [101.0, 102.0, 103.0, 104.0],
            "volume": [1000, 1000, 1000, 1000],
        }, index=idx)
        
        orb_high = 105.0
        orb_low = 95.0
        
        # Test the breakout detection
        side, timestamp, entry_price = _find_breakout_in_entry_window(entry_data, orb_high, orb_low)
        
        # Should detect long breakout
        self.assertEqual(side, 'long')
        self.assertIsNotNone(timestamp)
        self.assertIsNotNone(entry_price)
        # Entry price should be max of open and orb_high
        expected_entry_price = max(102.0, orb_high)  # open=102.0, orb_high=105.0
        self.assertEqual(entry_price, expected_entry_price)

    def test_breakout_strict_comparison_low_below_orb(self):
        """Test that when low goes below ORB low, short breakout is detected."""
        # Create test data where low goes below ORB low
        idx = pd.date_range("2024-06-01 12:00:00+00:00", periods=4, freq="15min")
        entry_data = pd.DataFrame({
            "open": [100.0, 99.0, 98.0, 97.0],
            "high": [101.0, 100.0, 99.0, 98.0],
            "low": [95.0, 95.0, 94.0, 95.0],  # One candle goes below ORB low
            "close": [99.0, 98.0, 97.0, 96.0],
            "volume": [1000, 1000, 1000, 1000],
        }, index=idx)
        
        orb_high = 105.0
        orb_low = 95.0
        
        # Test the breakout detection
        side, timestamp, entry_price = _find_breakout_in_entry_window(entry_data, orb_high, orb_low)
        
        # Should detect short breakout
        self.assertEqual(side, 'short')
        self.assertIsNotNone(timestamp)
        self.assertIsNotNone(entry_price)
        # Entry price should be min of open and orb_low
        expected_entry_price = min(98.0, orb_low)  # open=98.0, orb_low=95.0
        self.assertEqual(entry_price, expected_entry_price)


if __name__ == "__main__":
    unittest.main()


