#!/usr/bin/env python3
"""
Test manual para verificar la alineación de SL/TP y sizing con objetivos R por modo.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

# Add the btc_1tpd_backtester directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'btc_1tpd_backtester'))

# Import the strategy classes directly
from strategy_multifactor import MultifactorStrategy
from btc_1tpd_backtest_final import SimpleTradingStrategy
from strategy import TradingStrategy
from signals.today_signal import get_today_trade_recommendation


def create_test_data():
    """Create synthetic test data with clear signals."""
    # Create 24 hours of 15-minute data
    start = datetime(2024, 1, 3, 0, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    idx = pd.date_range(start, end - timedelta(minutes=15), freq='15min', tz=timezone.utc)
    
    # Create data with clear bullish trend and breakout
    base_price = 100.0
    data = []
    
    for i, timestamp in enumerate(idx):
        # Create clear trend
        trend = i * 0.2  # Strong upward trend
        
        # Add volatility around trend
        if i < 20:  # First 5 hours - consolidation
            volatility = np.sin(i * 0.2) * 1.0
        elif i < 40:  # Next 5 hours - breakout
            volatility = np.sin(i * 0.2) * 2.0 + 1.0  # Higher volatility
        else:  # Rest of day - follow-through
            volatility = np.sin(i * 0.1) * 1.5
        
        open_price = base_price + trend + volatility
        high_price = open_price + abs(np.random.normal(0, 1.5))
        low_price = open_price - abs(np.random.normal(0, 1.5))
        close_price = open_price + np.random.normal(0, 1.0)
        
        # Ensure OHLC consistency
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': 1000.0 + np.random.normal(0, 200)
        })
    
    return pd.DataFrame(data, index=idx)


def test_r_multiple_alignment():
    """Test R-multiple alignment across different modes."""
    print("🧪 Testing R-Multiple Alignment")
    print("=" * 60)
    
    # Create test data
    test_data = create_test_data()
    print(f"📊 Created test data: {len(test_data)} candles")
    
    # Test modes with their target R-multiples
    modes = [
        ('conservative', 1.0, 15.0),
        ('moderate', 1.5, 25.0),
        ('aggressive', 2.0, 40.0)
    ]
    
    for mode_name, target_r, risk_usdt in modes:
        print(f"\n🎯 Testing {mode_name.upper()} mode (target: {target_r}R, risk: {risk_usdt} USDT)")
        print("-" * 50)
        
        # Base configuration
        config = {
            'risk_usdt': risk_usdt,
            'tp_multiplier': target_r,
            'target_r_multiple': target_r,
            'risk_reward_ratio': target_r,
            'atr_multiplier': 2.0,
            'min_reliability_score': 0.6,
            'ema_fast': 12,
            'ema_slow': 26,
            'adx_period': 14,
            'adx_min': 25.0,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'volume_confirmation': True,
            'volume_threshold': 1.2,
            'session_trading': True,
            'entry_window': (11, 14),
            'exit_window': (20, 22),
            'session_timezone': 'America/Argentina/Buenos_Aires',
            'force_one_trade': True,
            'max_daily_trades': 1,
            'commission_rate': 0.001,
            'slippage_rate': 0.0005
        }
        
        # Test 1: MultifactorStrategy
        print(f"\n1. Testing MultifactorStrategy...")
        config['use_multifactor_strategy'] = True
        strategy = MultifactorStrategy(config)
        trades = strategy.process_day(test_data, test_data.index[0].date())
        
        if trades:
            trade = trades[0]
            entry_price = trade['entry_price']
            stop_loss = trade['sl']
            take_profit = trade['tp']
            position_size = trade.get('position_size', 1.0)
            
            # Calculate risk and reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            r_multiple = reward / risk if risk > 0 else 0
            actual_risk = risk * position_size
            
            print(f"   📊 Trade details:")
            print(f"      Entry: {entry_price:.2f}")
            print(f"      SL: {stop_loss:.2f}")
            print(f"      TP: {take_profit:.2f}")
            print(f"      Risk: {risk:.2f} per unit")
            print(f"      Reward: {reward:.2f} per unit")
            print(f"      R-multiple: {r_multiple:.3f}")
            print(f"      Position size: {position_size:.2f}")
            print(f"      Actual risk: {actual_risk:.2f} USDT")
            
            # Verify R-multiple
            if abs(r_multiple - target_r) < 0.01:
                print(f"   ✅ R-multiple correct: {r_multiple:.3f} ≈ {target_r}")
            else:
                print(f"   ❌ R-multiple incorrect: {r_multiple:.3f} ≠ {target_r}")
            
            # Verify risk amount
            if abs(actual_risk - risk_usdt) < 0.01:
                print(f"   ✅ Risk amount correct: {actual_risk:.2f} ≈ {risk_usdt}")
            else:
                print(f"   ❌ Risk amount incorrect: {actual_risk:.2f} ≠ {risk_usdt}")
        else:
            print(f"   ⚠️ No trades generated")
        
        # Test 2: SimpleTradingStrategy with multifactor
        print(f"\n2. Testing SimpleTradingStrategy with multifactor...")
        simple_strategy = SimpleTradingStrategy(config)
        simple_trades = simple_strategy.process_day(test_data, test_data.index[0].date())
        
        if simple_trades:
            trade = simple_trades[0]
            entry_price = trade['entry_price']
            stop_loss = trade['sl']
            take_profit = trade['tp']
            position_size = trade.get('position_size', 1.0)
            
            # Calculate risk and reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            r_multiple = reward / risk if risk > 0 else 0
            actual_risk = risk * position_size
            
            print(f"   📊 Trade details:")
            print(f"      Entry: {entry_price:.2f}")
            print(f"      SL: {stop_loss:.2f}")
            print(f"      TP: {take_profit:.2f}")
            print(f"      R-multiple: {r_multiple:.3f}")
            print(f"      Actual risk: {actual_risk:.2f} USDT")
            
            # Verify R-multiple
            if abs(r_multiple - target_r) < 0.01:
                print(f"   ✅ R-multiple correct: {r_multiple:.3f} ≈ {target_r}")
            else:
                print(f"   ❌ R-multiple incorrect: {r_multiple:.3f} ≠ {target_r}")
        else:
            print(f"   ⚠️ No trades generated")
        
        # Test 3: SimpleTradingStrategy with ORB
        print(f"\n3. Testing SimpleTradingStrategy with ORB...")
        orb_config = config.copy()
        orb_config['use_multifactor_strategy'] = False
        orb_strategy = SimpleTradingStrategy(orb_config)
        orb_trades = orb_strategy.process_day(test_data, test_data.index[0].date())
        
        if orb_trades:
            trade = orb_trades[0]
            entry_price = trade['entry_price']
            stop_loss = trade['sl']
            take_profit = trade['tp']
            position_size = trade.get('position_size', 1.0)
            
            # Calculate risk and reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            r_multiple = reward / risk if risk > 0 else 0
            actual_risk = risk * position_size
            
            print(f"   📊 Trade details:")
            print(f"      Entry: {entry_price:.2f}")
            print(f"      SL: {stop_loss:.2f}")
            print(f"      TP: {take_profit:.2f}")
            print(f"      R-multiple: {r_multiple:.3f}")
            print(f"      Actual risk: {actual_risk:.2f} USDT")
            
            # Verify R-multiple
            if abs(r_multiple - target_r) < 0.01:
                print(f"   ✅ R-multiple correct: {r_multiple:.3f} ≈ {target_r}")
            else:
                print(f"   ❌ R-multiple incorrect: {r_multiple:.3f} ≠ {target_r}")
        else:
            print(f"   ⚠️ No trades generated")
        
        # Test 4: Signal generation
        print(f"\n4. Testing signal generation...")
        now = test_data.index[50]
        signal = get_today_trade_recommendation('BTC/USDT:USDT', config, now)
        
        if signal.get('status') == 'signal':
            entry_price = signal['entry_price']
            stop_loss = signal['stop_loss']
            take_profit = signal['take_profit']
            
            # Calculate risk and reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            r_multiple = reward / risk if risk > 0 else 0
            
            print(f"   📊 Signal details:")
            print(f"      Entry: {entry_price:.2f}")
            print(f"      SL: {stop_loss:.2f}")
            print(f"      TP: {take_profit:.2f}")
            print(f"      R-multiple: {r_multiple:.3f}")
            print(f"      Strategy: {signal.get('strategy', 'N/A')}")
            
            # Verify R-multiple
            if abs(r_multiple - target_r) < 0.01:
                print(f"   ✅ R-multiple correct: {r_multiple:.3f} ≈ {target_r}")
            else:
                print(f"   ❌ R-multiple incorrect: {r_multiple:.3f} ≠ {target_r}")
        else:
            print(f"   ⚠️ No signal generated: {signal.get('status', 'unknown')}")
    
    print("\n" + "=" * 60)
    print("🎉 R-Multiple Alignment testing completed!")
    print("=" * 60)


def test_mode_config_consistency():
    """Test that mode configurations are consistent."""
    print("\n🔧 Testing Mode Configuration Consistency")
    print("=" * 60)
    
    try:
        # Import the actual mode config from webapp
        sys.path.append(os.path.join(os.path.dirname(__file__), 'webapp'))
        from app import MODE_CONFIG
        
        print("📋 Mode Configuration Analysis:")
        
        for mode, config in MODE_CONFIG.items():
            print(f"\n{mode.upper()} mode:")
            tp_multiplier = config.get('tp_multiplier')
            target_r_multiple = config.get('target_r_multiple')
            risk_reward_ratio = config.get('risk_reward_ratio')
            risk_usdt = config.get('risk_usdt')
            
            print(f"   tp_multiplier: {tp_multiplier}")
            print(f"   target_r_multiple: {target_r_multiple}")
            print(f"   risk_reward_ratio: {risk_reward_ratio}")
            print(f"   risk_usdt: {risk_usdt}")
            
            # Check consistency
            if tp_multiplier == target_r_multiple == risk_reward_ratio:
                print(f"   ✅ All R-multiple values consistent: {tp_multiplier}")
            else:
                print(f"   ❌ R-multiple values inconsistent:")
                print(f"      tp_multiplier: {tp_multiplier}")
                print(f"      target_r_multiple: {target_r_multiple}")
                print(f"      risk_reward_ratio: {risk_reward_ratio}")
            
            # Check expected values
            expected_r = {'conservative': 1.0, 'moderate': 1.5, 'aggressive': 2.0}
            if tp_multiplier == expected_r.get(mode):
                print(f"   ✅ Target R-multiple correct: {tp_multiplier}")
            else:
                print(f"   ❌ Target R-multiple incorrect: {tp_multiplier} ≠ {expected_r.get(mode)}")
    
    except ImportError as e:
        print(f"⚠️ Could not import MODE_CONFIG: {e}")
        print("   Skipping mode configuration test")


if __name__ == '__main__':
    test_r_multiple_alignment()
    test_mode_config_consistency()
