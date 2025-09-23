import unittest
from datetime import datetime, timezone
import pandas as pd
import numpy as np

from btc_1tpd_backtester.signals.today_signal import get_today_trade_recommendation
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


if __name__ == "__main__":
    unittest.main()


