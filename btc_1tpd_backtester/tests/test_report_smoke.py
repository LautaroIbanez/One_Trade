import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np

from btc_1tpd_backtester.plot_results import create_comprehensive_report


class TestReportSmoke(unittest.TestCase):
    def test_report_saves_when_price_data_missing(self):
        # Create minimal artificial trades without relying on price data
        times = pd.date_range("2024-06-01", periods=5, freq="D")
        trades = pd.DataFrame({
            "entry_time": times,
            "pnl_usdt": [10, -5, 7, -3, 12],
            "r_multiple": [0.5, -0.3, 0.4, -0.2, 0.6],
            "entry_price": [100, 101, 102, 103, 104],
            "exit_time": times,
            "exit_price": [101, 100, 103, 102, 106],
            "side": ["long", "short", "long", "short", "long"],
        })

        # Force price fetch to return empty so price chart becomes None
        with patch("btc_1tpd_backtester.utils.fetch_historical_data", return_value=pd.DataFrame()):
            plots = create_comprehensive_report(trades, save_plots=True)

        # Ensure we got a plots dict and no exception was raised
        self.assertIsInstance(plots, dict)
        # Equity curve should be present
        self.assertIn("equity_curve", plots)


if __name__ == "__main__":
    unittest.main()








