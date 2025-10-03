#!/usr/bin/env python3
"""
Test manual para verificar la estrategia multifactor.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

# Add the btc_1tpd_backtester directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'btc_1tpd_backtester'))

# Import the strategy class directly
from strategy_multifactor import MultifactorStrategy
from btc_1tpd_backtest_final import SimpleTradingStrategy
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


def test_multifactor_strategy():
    """Test the multifactor strategy."""
    print("🧪 Testing MultifactorStrategy")
    print("=" * 50)
    
    # Create test data
    test_data = create_test_data()
    print(f"📊 Created test data: {len(test_data)} candles")
    
    # Test configuration
    config = {
        'risk_usdt': 20.0,
        'atr_multiplier': 2.0,
        'tp_multiplier': 2.0,
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
    
    # Test 1: Direct MultifactorStrategy
    print("\n1. Testing direct MultifactorStrategy...")
    strategy = MultifactorStrategy(config)
    
    # Calculate indicators
    data_with_indicators = strategy.calculate_indicators(test_data)
    print(f"   ✅ Indicators calculated: {len(data_with_indicators.columns)} columns")
    
    # Test reliability score
    test_index = 50
    reliability = strategy.calculate_reliability_score(data_with_indicators, test_index)
    print(f"   📈 Reliability score: {reliability:.3f}")
    
    # Test signal detection
    signal_direction, signal_reliability = strategy.detect_signal(data_with_indicators, test_index)
    print(f"   🎯 Signal: {signal_direction}, Reliability: {signal_reliability:.3f}")
    
    # Test trade parameters
    if signal_direction:
        entry_price = test_data['open'].iloc[test_index]
        entry_time = test_data.index[test_index]
        trade_params = strategy.calculate_trade_params(
            signal_direction, entry_price, data_with_indicators, entry_time
        )
        if trade_params:
            print(f"   💰 Trade params: Entry={trade_params['entry_price']:.2f}, SL={trade_params['stop_loss']:.2f}, TP={trade_params['take_profit']:.2f}")
    
    # Test daily processing
    date = test_data.index[0].date()
    trades = strategy.process_day(test_data, date)
    print(f"   📋 Daily trades: {len(trades)}")
    
    if trades:
        trade = trades[0]
        print(f"   📊 Trade details:")
        print(f"      Side: {trade['side']}")
        print(f"      Entry: {trade['entry_price']:.2f}")
        print(f"      SL: {trade['sl']:.2f}")
        print(f"      TP: {trade['tp']:.2f}")
        print(f"      PnL: {trade['pnl_usdt']:.2f} USDT")
        print(f"      R-multiple: {trade['r_multiple']:.2f}")
        print(f"      Reliability: {trade['reliability_score']:.3f}")
    
    # Test 2: SimpleTradingStrategy with multifactor
    print("\n2. Testing SimpleTradingStrategy with multifactor...")
    config['use_multifactor_strategy'] = True
    simple_strategy = SimpleTradingStrategy(config)
    
    simple_trades = simple_strategy.process_day(test_data, date)
    print(f"   📋 SimpleTradingStrategy trades: {len(simple_trades)}")
    
    if simple_trades:
        trade = simple_trades[0]
        print(f"   📊 Trade details:")
        print(f"      Side: {trade['side']}")
        print(f"      Entry: {trade['entry_price']:.2f}")
        print(f"      SL: {trade['sl']:.2f}")
        print(f"      TP: {trade['tp']:.2f}")
        print(f"      PnL: {trade['pnl_usdt']:.2f} USDT")
        print(f"      R-multiple: {trade['r_multiple']:.2f}")
        print(f"      Reliability: {trade.get('reliability_score', 'N/A')}")
        print(f"      Used multifactor: {trade.get('used_multifactor', False)}")
    
    # Test 3: Signal generation
    print("\n3. Testing signal generation...")
    now = test_data.index[50]
    signal = get_today_trade_recommendation('BTC/USDT:USDT', config, now)
    
    print(f"   📡 Signal status: {signal['status']}")
    if signal['status'] == 'signal':
        print(f"   📊 Signal details:")
        print(f"      Side: {signal['side']}")
        print(f"      Entry: {signal['entry_price']:.2f}")
        print(f"      SL: {signal['stop_loss']:.2f}")
        print(f"      TP: {signal['take_profit']:.2f}")
        print(f"      Strategy: {signal.get('strategy', 'N/A')}")
        print(f"      Reliability: {signal.get('reliability_score', 'N/A')}")
    
    # Test 4: Different modes
    print("\n4. Testing different modes...")
    modes = ['conservative', 'moderate', 'aggressive']
    
    for mode in modes:
        print(f"\n   🎯 Testing {mode} mode...")
        mode_config = config.copy()
        
        if mode == 'conservative':
            mode_config.update({
                'min_reliability_score': 0.8,
                'atr_multiplier': 1.5,
                'volume_threshold': 1.5,
                'use_multifactor_strategy': False  # Use ORB
            })
        elif mode == 'moderate':
            mode_config.update({
                'min_reliability_score': 0.6,
                'atr_multiplier': 2.0,
                'volume_threshold': 1.2,
                'use_multifactor_strategy': True  # Use multifactor
            })
        elif mode == 'aggressive':
            mode_config.update({
                'min_reliability_score': 0.4,
                'atr_multiplier': 2.5,
                'volume_threshold': 1.0,
                'trailing_stop': True,
                'use_multifactor_strategy': True  # Use multifactor
            })
        
        # Test backtesting
        mode_strategy = SimpleTradingStrategy(mode_config)
        mode_trades = mode_strategy.process_day(test_data, date)
        
        # Test signal generation
        mode_signal = get_today_trade_recommendation('BTC/USDT:USDT', mode_config, now)
        
        print(f"      Backtesting trades: {len(mode_trades)}")
        print(f"      Signal status: {mode_signal['status']}")
        
        if mode_trades:
            trade = mode_trades[0]
            print(f"      Trade PnL: {trade['pnl_usdt']:.2f} USDT")
            print(f"      R-multiple: {trade['r_multiple']:.2f}")
    
    print("\n" + "=" * 50)
    print("🎉 MultifactorStrategy testing completed!")
    print("=" * 50)


if __name__ == '__main__':
    test_multifactor_strategy()
