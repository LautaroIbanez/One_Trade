import unittest
from datetime import datetime, timezone, timedelta
import pandas as pd

from btc_1tpd_backtester.utils import fetch_historical_data


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


if __name__ == "__main__":
    unittest.main()
