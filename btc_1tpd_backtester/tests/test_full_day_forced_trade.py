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

    def test_ema15_fallback_handles_invalid_atr(self):
        """Test that EMA15 fallback handles invalid ATR gracefully and returns consistent tuple."""
        # Build data with flat prices to create invalid ATR
        date = datetime(2024, 1, 3, tzinfo=timezone.utc)
        day_slice = self._build_day_with_next_day(date, next_day_minutes=60)
        
        config = {
            'risk_usdt': 20.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),
            'entry_window': (11, 18),  # Use updated entry window
            'full_day_trading': False,
            'force_one_trade': True,
        }
        
        strategy = SimpleTradingStrategy(config)
        
        # Test that check_ema15_pullback_conditions returns consistent tuple format
        # With flat prices, ATR should be 0 or invalid
        ok, fb, fb_ts = strategy.check_ema15_pullback_conditions(day_slice, 'long')
        
        # Should always return 3 elements
        self.assertEqual(len((ok, fb, fb_ts)), 3, "Should always return 3 elements")
        
        # With invalid ATR, should return False, None, None
        self.assertFalse(ok, "Should return False for invalid ATR")
        self.assertIsNone(fb, "Should return None for fb when invalid ATR")
        self.assertIsNone(fb_ts, "Should return None for fb_ts when invalid ATR")

    def test_deterministic_final_fallback_creates_trade(self):
        """Test that deterministic final fallback creates a trade when all else fails."""
        # Build data with completely flat prices to ensure all fallbacks fail
        date = datetime(2024, 1, 4, tzinfo=timezone.utc)
        day_slice = self._build_day_with_next_day(date, next_day_minutes=60)
        
        config = {
            'risk_usdt': 20.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),
            'entry_window': (11, 18),
            'full_day_trading': False,
            'force_one_trade': True,
        }
        
        strategy = SimpleTradingStrategy(config)
        trades = strategy.process_day(day_slice, date.date())
        
        # Should produce one trade even with flat prices
        self.assertEqual(len(trades), 1, "Should produce one trade with deterministic fallback")
        
        trade = trades[0]
        self.assertTrue(trade['used_fallback'], "Trade should be marked as fallback")
        
        # Verify trade has valid parameters
        self.assertIsNotNone(trade['entry_price'], "Should have entry price")
        self.assertIsNotNone(trade['sl'], "Should have stop loss")
        self.assertIsNotNone(trade['tp'], "Should have take profit")
        self.assertIsNotNone(trade['exit_time'], "Should have exit time")
        self.assertIsNotNone(trade['exit_reason'], "Should have exit reason")
        
        # Verify entry and exit times are different
        entry_time = pd.to_datetime(trade['entry_time'])
        exit_time = pd.to_datetime(trade['exit_time'])
        self.assertGreater(exit_time, entry_time, "Exit should be after entry")

    def test_deterministic_fallback_uses_orb_range(self):
        """Test that deterministic fallback uses ORB range when available."""
        date = datetime(2024, 1, 5, tzinfo=timezone.utc)
        tz = timezone.utc
        
        # Create data with ORB range but flat prices after ORB
        session_start = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
        session_end = session_start + timedelta(days=1)
        session_index = pd.date_range(session_start, session_end - timedelta(minutes=15), freq='15min', tz=tz)
        
        # Create ORB with some range (11:00-12:00)
        orb_start = session_start.replace(hour=11, minute=0)
        orb_end = session_start.replace(hour=12, minute=0)
        orb_mask = (session_index >= orb_start) & (session_index < orb_end)
        
        # Create data with ORB range but flat prices elsewhere
        data = []
        for i, ts in enumerate(session_index):
            if orb_mask[i]:
                # ORB period: create range
                base_price = 100.0
                range_size = 5.0
                data.append({
                    'open': base_price,
                    'high': base_price + range_size,
                    'low': base_price - range_size,
                    'close': base_price,
                    'volume': 1000.0
                })
            else:
                # Non-ORB: flat prices
                data.append({
                    'open': 100.0,
                    'high': 100.0,
                    'low': 100.0,
                    'close': 100.0,
                    'volume': 1000.0
                })
        
        day_slice = pd.DataFrame(data, index=session_index)
        
        config = {
            'risk_usdt': 20.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),
            'entry_window': (11, 18),
            'full_day_trading': False,
            'force_one_trade': True,
        }
        
        strategy = SimpleTradingStrategy(config)
        trades = strategy.process_day(day_slice, date.date())
        
        # Should produce one trade using ORB range for stop/take profit
        self.assertEqual(len(trades), 1, "Should produce one trade using ORB range")
        
        trade = trades[0]
        self.assertTrue(trade['used_fallback'], "Trade should be marked as fallback")
        
        # Verify that stop loss and take profit are reasonable based on ORB range
        entry_price = trade['entry_price']
        stop_loss = trade['sl']
        take_profit = trade['tp']
        
        # Stop loss should be below entry (long trade)
        self.assertLess(stop_loss, entry_price, "Stop loss should be below entry for long")
        
        # Take profit should be above entry (long trade)
        self.assertGreater(take_profit, entry_price, "Take profit should be above entry for long")
        
        # Risk/reward should be reasonable (not too extreme)
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        self.assertGreater(risk, 0, "Risk should be positive")
        self.assertGreater(reward, 0, "Reward should be positive")
        self.assertLess(reward / risk, 10, "Reward/risk ratio should not be too extreme")


if __name__ == "__main__":
    unittest.main()




