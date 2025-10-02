import unittest
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy


class TestFullDayForcedTrade(unittest.TestCase):
    def _build_day_with_next_day(self, start_date: datetime, next_day_minutes: int = 120):
        tz = timezone.utc
        session_start = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=tz)
        session_end = session_start + timedelta(days=1)
        # 24h session @ 15m
        session_index = pd.date_range(session_start, session_end - timedelta(minutes=15), freq='15min', tz=tz)
        # Next-day candles
        extra_index = pd.date_range(session_end, session_end + timedelta(minutes=next_day_minutes) - timedelta(minutes=15), freq='15min', tz=tz)

        # Constant prices to avoid breakout and keep fallback conditions simple
        def df_for(index):
            return pd.DataFrame({
                'open': np.full(len(index), 100.0),
                'high': np.full(len(index), 100.0),
                'low': np.full(len(index), 100.0),
                'close': np.full(len(index), 100.0),
                'volume': np.full(len(index), 1000.0),
            }, index=index)

        session_df = df_for(session_index)
        extra_df = df_for(extra_index)
        return pd.concat([session_df, extra_df])

    def test_forced_trade_24h_uses_next_day_candles(self):
        # Build data with 24h session + 2h next day
        date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        day_slice = self._build_day_with_next_day(date, next_day_minutes=120)

        config = {
            'risk_usdt': 20.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),
            'entry_window': (11, 13),
            'full_day_trading': True,
            'force_one_trade': True,
        }

        strategy = SimpleTradingStrategy(config)
        trades = strategy.process_day(day_slice, date.date())

        # Should produce one forced trade
        self.assertTrue(len(trades) == 1, "Expected one forced trade in 24h mode")
        trade = trades[0]
        entry_time = pd.to_datetime(trade['entry_time'])
        exit_time = pd.to_datetime(trade['exit_time'])

        # Verify exit evaluated using next-day candles and not immediate end_of_data
        self.assertGreater(exit_time, entry_time, "exit_time should be after entry_time")
        self.assertNotEqual(trade['exit_reason'], 'end_of_data', "Should not exit due to immediate end of data")

    def test_forced_trade_not_immediate_close_first_bar(self):
        # Build data with 24h session + 1h next day to ensure at least one bar exists after entry
        date = datetime(2024, 1, 2, tzinfo=timezone.utc)
        day_slice = self._build_day_with_next_day(date, next_day_minutes=60)

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
        trades = strategy.process_day(day_slice, date.date())
        self.assertTrue(len(trades) == 1)
        trade = trades[0]
        entry_time = pd.to_datetime(trade['entry_time'])
        exit_time = pd.to_datetime(trade['exit_time'])

        # It must not close on the same candle as entry due to lack of data
        self.assertGreater(exit_time, entry_time)
        # And exit_reason should be either time_limit_24h or session_end depending on data, but not end_of_data
        self.assertNotEqual(trade['exit_reason'], 'end_of_data')


if __name__ == "__main__":
    unittest.main()




