import unittest
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy


class TestForcedTradeNoBreakout(unittest.TestCase):
    def _make_flat_session(self, date: datetime) -> pd.DataFrame:
        tz = timezone.utc
        start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
        end = start + timedelta(days=1)
        idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=tz)
        # Flat prices: no breakout relative to any ORB range
        return pd.DataFrame({
            'open': np.full(len(idx), 100.0),
            'high': np.full(len(idx), 100.0),
            'low': np.full(len(idx), 100.0),
            'close': np.full(len(idx), 100.0),
            'volume': np.full(len(idx), 1000.0),
        }, index=idx)

    def test_forced_trade_created_when_no_breakout(self):
        date = datetime(2024, 1, 3, tzinfo=timezone.utc)
        day = self._make_flat_session(date)
        # Add a few next-day candles so exit has future data in 24h mode too
        extra_idx = pd.date_range(date + timedelta(days=1), date + timedelta(days=1, hours=1) - timedelta(minutes=15), freq='15min', tz=timezone.utc)
        extra_df = pd.DataFrame({
            'open': 100.0, 'high': 100.0, 'low': 100.0, 'close': 100.0, 'volume': 1000.0
        }, index=extra_idx)
        day_ext = pd.concat([day, extra_df])

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

        strat = SimpleTradingStrategy(config)
        trades = strat.process_day(day_ext, date.date())
        self.assertEqual(len(trades), 1, "Exactly one trade should be created with force_one_trade=True and no breakout")
        trade = trades[0]
        self.assertIn('used_fallback', trade)
        self.assertTrue(trade['used_fallback'], "Trade should be marked as used_fallback")
        self.assertIsNotNone(trade.get('entry_time'))
        self.assertIsNotNone(trade.get('exit_time'))
        self.assertGreater(pd.to_datetime(trade['exit_time']), pd.to_datetime(trade['entry_time']))


if __name__ == '__main__':
    unittest.main()




