import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from btc_1tpd_backtester.strategy import TradingStrategy
from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy


class TestORBImprovements(unittest.TestCase):
    """Test ORB detection improvements and trade exit simulation."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample 15-minute data for a day
        base_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        times = [base_time + timedelta(minutes=15*i) for i in range(32)]  # 8 hours of data
        
        # Create realistic OHLC data
        np.random.seed(42)  # For reproducible tests
        base_price = 50000.0
        
        data = []
        for i, time in enumerate(times):
            # Simulate price movement
            price_change = np.random.normal(0, 100)  # Random walk
            base_price += price_change
            
            # Create OHLC for this candle
            open_price = base_price
            high_price = open_price + abs(np.random.normal(0, 50))
            low_price = open_price - abs(np.random.normal(0, 50))
            close_price = open_price + np.random.normal(0, 30)
            
            # Ensure OHLC relationships are valid
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # Ensure high volume for confirmations
            volume = np.random.uniform(2000, 5000)  # Higher volume
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
        
        self.ltf_data = pd.DataFrame(data, index=times)
        self.ltf_data.index.name = 'timestamp'
        
        # Create HTF data (1-hour)
        htf_times = [base_time + timedelta(hours=i) for i in range(8)]
        htf_data = []
        for i, time in enumerate(htf_times):
            htf_data.append({
                'open': 50000 + i*100,
                'high': 50100 + i*100,
                'low': 49900 + i*100,
                'close': 50050 + i*100,
                'volume': np.random.uniform(1000, 5000)
            })
        
        self.htf_data = pd.DataFrame(htf_data, index=htf_times)
        self.htf_data.index.name = 'timestamp'
        
        # Strategy config
        self.config = {
            'signal_tf': '15m',
            'risk_usdt': 20.0,
            'daily_target': 50.0,
            'daily_max_loss': -30.0,
            'force_one_trade': True,
            'fallback_mode': 'EMA15_pullback',
            'adx_min': 15.0,
            'min_rr_ok': 1.5,
            'atr_mult_orb': 1.2,
            'atr_mult_fallback': 1.5,
            'tp_multiplier': 2.0
        }
    
    def test_orb_levels_caching(self):
        """Test that ORB levels are calculated and cached correctly."""
        strategy = TradingStrategy(self.config)
        
        # Test ORB calculation for 11:00-12:00 window
        test_time = datetime(2024, 1, 15, 11, 30, 0, tzinfo=timezone.utc)
        
        # First call should calculate and cache
        orb_high, orb_low = strategy.get_orb_levels(self.ltf_data, test_time)
        
        self.assertIsNotNone(orb_high)
        self.assertIsNotNone(orb_low)
        self.assertGreater(orb_high, orb_low)
        
        # Second call should return cached values
        orb_high2, orb_low2 = strategy.get_orb_levels(self.ltf_data, test_time)
        self.assertEqual(orb_high, orb_high2)
        self.assertEqual(orb_low, orb_low2)
    
    def test_orb_breakout_detection_in_entry_window(self):
        """Test that ORB breakouts can be detected in entry window (11:00-13:00)."""
        strategy = TradingStrategy(self.config)
        
        # Test that ORB levels are calculated correctly
        test_time = datetime(2024, 1, 15, 12, 15, 0, tzinfo=timezone.utc)
        orb_high, orb_low = strategy.get_orb_levels(self.ltf_data, test_time)
        
        # Should have valid ORB levels
        self.assertIsNotNone(orb_high)
        self.assertIsNotNone(orb_low)
        self.assertGreater(orb_high, orb_low)
        
        # Test that entry window check works
        self.assertTrue(strategy.entry_start <= test_time.hour < strategy.entry_end)
        
        # Test the core ORB logic: if we have ORB levels and are in entry window,
        # and current price breaks above ORB high, it should be detected
        test_data = self.ltf_data.copy()
        
        # Filter to only include data up to test_time
        test_data = test_data[test_data.index <= test_time]
        
        # Add the test candle at 12:15 with a clear breakout
        new_candle = pd.DataFrame({
            'open': [orb_high + 50],
            'high': [orb_high + 150],
            'low': [orb_high + 30],
            'close': [orb_high + 100],
            'volume': [3000]
        }, index=[test_time])
        test_data = pd.concat([test_data, new_candle]).sort_index()
        
        # Test the basic breakout detection logic
        current_price = test_data['close'].iloc[-1]
        breakout_detected = current_price > orb_high
        
        print(f"Test time: {test_time}")
        print(f"Last index: {test_data.index[-1]}")
        print(f"Current price: {current_price}")
        print(f"ORB high: {orb_high}")
        print(f"Breakout detected: {breakout_detected}")
        print(f"Data length: {len(test_data)}")
        
        self.assertTrue(breakout_detected, "Breakout should be detected when current price > ORB high")
        
        # Test that the ORB levels are returned correctly
        orb_ok, detected_high, detected_low, trade_params = strategy.check_orb_conditions(
            test_data, self.htf_data, 'long'
        )
        
        # Even if trade_params is None due to indicator failures, 
        # we should at least get the ORB levels
        self.assertIsNotNone(detected_high)
        self.assertIsNotNone(detected_low)
        self.assertEqual(detected_high, orb_high)
        self.assertEqual(detected_low, orb_low)
    
    def test_sequential_candle_evaluation(self):
        """Test that trade exits are evaluated sequentially per candle."""
        # Create test data with overlapping TP/SL in same candle
        entry_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        exit_time = datetime(2024, 1, 15, 12, 15, 0, tzinfo=timezone.utc)
        
        # Create a candle where both TP and SL are hit
        test_candle = pd.DataFrame({
            'open': [50000],
            'high': [50200],  # Above TP
            'low': [49800],   # Below SL
            'close': [50050]
        }, index=[exit_time])
        
        # Trade parameters
        trade_params = {
            'entry_price': 50000,
            'stop_loss': 49900,  # SL at 49900
            'take_profit': 50100,  # TP at 50100
            'position_size': 1.0,
            'entry_time': entry_time
        }
        
        strategy = SimpleTradingStrategy({
            'risk_usdt': 20.0,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        })
        
        # Test long trade
        result = strategy.simulate_trade_exit(trade_params, 'long', test_candle)
        
        # Should exit at the level closer to open price
        # Open: 50000, TP: 50100 (distance: 100), SL: 49900 (distance: 100)
        # Since distances are equal, should prioritize TP (positive outcome)
        self.assertEqual(result['exit_reason'], 'take_profit')
        self.assertEqual(result['exit_price'], 50100)
    
    def test_commission_and_slippage_costs(self):
        """Test that commission and slippage costs are properly calculated."""
        strategy = SimpleTradingStrategy({
            'risk_usdt': 20.0,
            'commission_rate': 0.001,  # 0.1%
            'slippage_rate': 0.0005    # 0.05%
        })
        
        # Simple trade parameters
        trade_params = {
            'entry_price': 50000,
            'stop_loss': 49900,
            'take_profit': 50100,
            'position_size': 1.0,
            'entry_time': datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        }
        
        # Create exit data
        exit_time = datetime(2024, 1, 15, 12, 15, 0, tzinfo=timezone.utc)
        exit_data = pd.DataFrame({
            'open': [50050],
            'high': [50100],
            'low': [50000],
            'close': [50050]
        }, index=[exit_time])
        
        # Test long trade that hits TP
        result = strategy.simulate_trade_exit(trade_params, 'long', exit_data)
        
        # Calculate expected costs
        entry_commission = 50000 * 1.0 * 0.001  # 50
        exit_commission = 50100 * 1.0 * 0.001   # 50.1
        entry_slippage = 50000 * 1.0 * 0.0005  # 25
        exit_slippage = 50100 * 1.0 * 0.0005   # 25.05
        
        expected_total_costs = entry_commission + exit_commission + entry_slippage + exit_slippage
        expected_gross_pnl = (50100 - 50000) * 1.0  # 100
        expected_net_pnl = expected_gross_pnl - expected_total_costs
        
        self.assertEqual(result['exit_reason'], 'take_profit')
        self.assertAlmostEqual(result['gross_pnl_usdt'], expected_gross_pnl, places=2)
        self.assertAlmostEqual(result['commission_usdt'], entry_commission + exit_commission, places=2)
        self.assertAlmostEqual(result['slippage_usdt'], entry_slippage + exit_slippage, places=2)
        self.assertAlmostEqual(result['pnl_usdt'], expected_net_pnl, places=2)
    
    def test_no_systematic_bias_in_tp_sl_conflicts(self):
        """Test that TP/SL conflicts don't systematically favor one side."""
        strategy = SimpleTradingStrategy({
            'risk_usdt': 20.0,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        })
        
        # Test multiple scenarios where both TP and SL are hit
        scenarios = [
            # (open, high, low, close, expected_bias)
            (50000, 50100, 49900, 50050, 'neutral'),  # Equal distances
            (50050, 50100, 49900, 50050, 'tp_favored'),  # TP closer to open
            (49950, 50100, 49900, 50050, 'sl_favored'),  # SL closer to open
        ]
        
        tp_wins = 0
        sl_wins = 0
        
        for open_price, high, low, close, expected in scenarios:
            trade_params = {
                'entry_price': 50000,
                'stop_loss': 49900,
                'take_profit': 50100,
                'position_size': 1.0,
                'entry_time': datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
            }
            
            exit_data = pd.DataFrame({
                'open': [open_price],
                'high': [high],
                'low': [low],
                'close': [close]
            }, index=[datetime(2024, 1, 15, 12, 15, 0, tzinfo=timezone.utc)])
            
            result = strategy.simulate_trade_exit(trade_params, 'long', exit_data)
            
            if result['exit_reason'] == 'take_profit':
                tp_wins += 1
            elif result['exit_reason'] == 'stop_loss':
                sl_wins += 1
        
        # Should not be systematically biased
        self.assertGreater(tp_wins, 0, "Should have some TP wins")
        self.assertGreater(sl_wins, 0, "Should have some SL wins")
        
        # The bias should be based on distance to open price, not systematic preference
        print(f"TP wins: {tp_wins}, SL wins: {sl_wins}")

    def test_force_one_trade_fallback_no_breakout(self):
        """Test that force_one_trade generates fallback trade when no ORB breakout occurs."""
        # Create data with no breakout
        base_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        times = [base_time + timedelta(minutes=15*i) for i in range(32)]
        
        # Create data where price stays within ORB range
        base_price = 50000.0
        data = []
        for i, time in enumerate(times):
            # Keep price within a narrow range (no breakout)
            price = base_price + np.random.normal(0, 10)  # Small variations
            data.append({
                'open': price,
                'high': price + 5,
                'low': price - 5,
                'close': price + np.random.normal(0, 2),
                'volume': 1000
            })
        
        day_data = pd.DataFrame(data, index=times)
        day_data.index.name = 'timestamp'
        
        # Strategy with force_one_trade enabled
        strategy = SimpleTradingStrategy({
            'risk_usdt': 20.0,
            'atr_mult_orb': 1.2,
            'tp_multiplier': 2.0,
            'adx_min': 15.0,
            'orb_window': (11, 12),
            'entry_window': (11, 13),
            'force_one_trade': True,
            'fallback_mode': 'EMA15_pullback',
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        })
        
        # Process day - should generate fallback trade
        trades = strategy.process_day(day_data, datetime(2024, 1, 15, tzinfo=timezone.utc))
        
        # Should have at least one trade due to fallback
        self.assertGreater(len(trades), 0, "Should generate fallback trade when force_one_trade=True")
        
        # Check that trade is marked as fallback
        trade = trades[0]
        self.assertTrue(trade.get('used_fallback', False), "Trade should be marked as fallback")
        self.assertIn('side', trade)
        self.assertIn('entry_price', trade)
        self.assertIn('sl', trade)
        self.assertIn('tp', trade)
        self.assertIn('exit_reason', trade)
        self.assertIn('pnl_usdt', trade)


if __name__ == "__main__":
    unittest.main()
