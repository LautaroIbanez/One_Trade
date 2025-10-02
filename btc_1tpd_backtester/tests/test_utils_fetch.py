import unittest
from datetime import datetime, timezone, timedelta
import pandas as pd
from unittest.mock import patch, MagicMock

from btc_1tpd_backtester.utils import fetch_historical_data, fetch_latest_price


class TestUtilsFetch(unittest.TestCase):
    def test_fetch_historical_data_date_only_strings(self):
        """Test that date-only strings (YYYY-MM-DD) are handled correctly."""
        # Use a recent date range to ensure data availability
        today = datetime.now(timezone.utc).date()
        since = (today - timedelta(days=7)).isoformat()  # 7 days ago
        until = (today - timedelta(days=1)).isoformat()  # yesterday
        
        # Test with date-only strings
        result = fetch_historical_data("BTC/USDT:USDT", since, until, "1h")
        
        # Should return non-empty DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Should return non-empty DataFrame for valid date range")
        
        # Check that data is within expected range
        if not result.empty:
            self.assertTrue(result.index.min() >= pd.to_datetime(since + "T00:00:00+00:00"))
            self.assertTrue(result.index.max() < pd.to_datetime(until + "T00:00:00+00:00") + timedelta(days=1))
    
    def test_fetch_historical_data_same_day(self):
        """Test that same-day refresh works without returning empty data."""
        # Use yesterday to avoid issues with incomplete current day data
        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        
        result = fetch_historical_data("BTC/USDT:USDT", yesterday, yesterday, "1h")
        
        # Should return non-empty DataFrame even for same-day range
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty, "Should return non-empty DataFrame for same-day range")
    
    def test_fetch_historical_data_until_after_since(self):
        """Test that until is properly adjusted when it's not after since."""
        today = datetime.now(timezone.utc).date()
        since = today.isoformat()
        until = since  # Same day
        
        result = fetch_historical_data("BTC/USDT:USDT", since, until, "1h")
        
        # Should still work and return data
        self.assertIsInstance(result, pd.DataFrame)
        # Note: May be empty if no data available for today, but should not crash

    @patch('btc_1tpd_backtester.utils.ccxt')
    def test_fetch_latest_price_formats_output(self, mock_ccxt):
        mock_exchange = MagicMock()
        mock_exchange.fetch_ticker.return_value = {
            'last': 50000.5,
            'bid': 49990.0,
            'ask': 50010.0,
            'baseVolume': 1234.5,
            'timestamp': int(datetime(2024,1,1,12,0,tzinfo=timezone.utc).timestamp()*1000)
        }
        mock_ccxt.binance.return_value = mock_exchange
        result = fetch_latest_price('BTC/USDT:USDT')
        self.assertIsNotNone(result)
        self.assertEqual(result['price'], 50000.5)
        self.assertEqual(result['bid'], 49990.0)
        self.assertEqual(result['ask'], 50010.0)
        self.assertEqual(result['volume'], 1234.5)
        self.assertEqual(result['timestamp'].year, 2024)

    @patch('btc_1tpd_backtester.utils.ccxt')
    def test_fetch_latest_price_returns_none_on_error(self, mock_ccxt):
        mock_ccxt.binance.side_effect = Exception('network error')
        result = fetch_latest_price('BTC/USDT:USDT')
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()






