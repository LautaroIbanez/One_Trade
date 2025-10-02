import unittest
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy


class TestShortTPWithRoundTripCosts(unittest.TestCase):
    def _build_short_tp_scenario(self):
        tz = timezone.utc
        date = datetime(2024, 1, 5, tzinfo=tz)
        start = datetime(2024, 1, 5, 0, 0, 0, tzinfo=tz)
        # Create 24h + next 2h
        idx = pd.date_range(start, start + timedelta(days=1, hours=2) - timedelta(minutes=15), freq='15min', tz=tz)
        # Prices engineered: after noon breakout window, simulate a drop to hit TP for short
        open_prices = np.full(len(idx), 100.0)
        high_prices = np.full(len(idx), 101.0)
        low_prices = np.full(len(idx), 99.0)
        close_prices = np.full(len(idx), 100.0)
        # Make ORB window (11-12) define orb_low slightly above 99
        # Then in entry window (>=12), ensure lows pierce below to trigger short, and after entry drift further to TP
        df = pd.DataFrame({
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': np.full(len(idx), 1000.0)
        }, index=idx)
        # Force a clear short breakout by setting low below orb_low after 12:00
        df.loc[df.index.hour >= 12, 'low'] = 98.5
        df.loc[df.index.hour >= 12, 'close'] = 99.0
        return date, df

    def test_short_tp_positive_after_costs(self):
        date, day = self._build_short_tp_scenario()
        config = {
            'risk_usdt': 10.0,
            'atr_mult_orb': 0.5,
            'tp_multiplier': 1.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),
            'entry_window': (11, 13),
            'full_day_trading': True,
            'force_one_trade': True,
            'commission_rate': 0.001,  # round-trip 0.1%
            'slippage_rate': 0.0005,   # round-trip 0.05%
        }
        strat = SimpleTradingStrategy(config)
        trades = strat.process_day(day, date.date())
        self.assertTrue(len(trades) >= 1)
        t = trades[0]
        # Ensure positive pnl_usdt even after costs
        self.assertGreaterEqual(t['pnl_usdt'], 0.0, f"PnL should be non-negative after round-trip costs, got {t['pnl_usdt']}")


if __name__ == '__main__':
    unittest.main()




