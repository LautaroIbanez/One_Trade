#!/usr/bin/env python3
"""
Test manual para verificar que el sizing respeta capital/leverage y mantiene take-profit rentable.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np

# Add the btc_1tpd_backtester directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'btc_1tpd_backtester'))

# Import the strategy class directly
from btc_1tpd_backtest_final import SimpleTradingStrategy


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


def test_position_sizing_constraints():
    """Test that position sizing respects capital and leverage constraints."""
    print("🧪 Testing Position Sizing Constraints")
    print("=" * 60)
    
    # Base configuration
    base_config = {
        'risk_usdt': 25.0,
        'atr_mult_orb': 1.2,
        'tp_multiplier': 1.5,
        'target_r_multiple': 1.5,
        'risk_reward_ratio': 1.5,
        'adx_min': 15.0,
        'force_one_trade': True,
        'fallback_mode': 'EMA15_pullback',
        'orb_window': (8, 9),
        'entry_window': (11, 14),
        'exit_window': (20, 22),
        'session_trading': True,
        'session_timezone': 'America/Argentina/Buenos_Aires',
        'commission_rate': 0.001,
        'slippage_rate': 0.0005,
        'use_multifactor_strategy': False,
    }
    
    # Test different capital levels
    capital_levels = [500.0, 1000.0, 2000.0, 5000.0]
    
    for capital in capital_levels:
        print(f"\n💰 Testing with capital: {capital} USDT")
        print("-" * 40)
        
        config = base_config.copy()
        config.update({
            'initial_capital': capital,
            'leverage': 1.0,
            'equity_risk_cap': 0.01
        })
        
        strategy = SimpleTradingStrategy(config)
        
        # Test position sizing
        entry_price = 100.0
        stop_loss = 98.0  # 2% risk
        
        position_size = strategy.compute_position_size(entry_price, stop_loss)
        
        # Calculate constraints
        risk_amount = config['risk_usdt']
        price_diff = abs(entry_price - stop_loss)
        expected_risk_size = risk_amount / price_diff
        
        max_capital_size = (capital * 1.0) / entry_price
        max_equity_risk_size = (capital * 0.01) / entry_price
        
        print(f"Entry Price: {entry_price}")
        print(f"Stop Loss: {stop_loss}")
        print(f"Price Diff: {price_diff:.2f}")
        print(f"Risk Amount: {risk_amount}")
        print(f"Position Size: {position_size:.4f}")
        print(f"Expected Risk Size: {expected_risk_size:.4f}")
        print(f"Max Capital Size: {max_capital_size:.4f}")
        print(f"Max Equity Risk Size: {max_equity_risk_size:.4f}")
        
        # Verify constraints
        assert position_size <= max_capital_size, f"Position size {position_size} exceeds capital limit {max_capital_size}"
        assert position_size <= max_equity_risk_size, f"Position size {position_size} exceeds equity risk limit {max_equity_risk_size}"
        assert position_size <= expected_risk_size, f"Position size {position_size} exceeds risk-based size {expected_risk_size}"
        
        # Calculate actual risk
        actual_risk = price_diff * position_size
        print(f"Actual Risk: {actual_risk:.2f} USDT")
        assert actual_risk <= risk_amount, f"Actual risk {actual_risk} exceeds intended risk {risk_amount}"
        
        print("✅ All constraints respected")


def test_leverage_impact():
    """Test the impact of different leverage levels."""
    print("\n🎯 Testing Leverage Impact")
    print("=" * 60)
    
    base_config = {
        'risk_usdt': 25.0,
        'initial_capital': 1000.0,
        'equity_risk_cap': 0.01,
        'atr_mult_orb': 1.2,
        'tp_multiplier': 1.5,
        'adx_min': 15.0,
        'force_one_trade': True,
        'fallback_mode': 'EMA15_pullback',
        'orb_window': (8, 9),
        'entry_window': (11, 14),
        'exit_window': (20, 22),
        'session_trading': True,
        'session_timezone': 'America/Argentina/Buenos_Aires',
        'commission_rate': 0.001,
        'slippage_rate': 0.0005,
        'use_multifactor_strategy': False,
    }
    
    leverage_levels = [1.0, 2.0, 5.0, 10.0]
    
    for leverage in leverage_levels:
        print(f"\n⚡ Testing with leverage: {leverage}x")
        print("-" * 30)
        
        config = base_config.copy()
        config['leverage'] = leverage
        
        strategy = SimpleTradingStrategy(config)
        
        entry_price = 100.0
        stop_loss = 98.0
        
        position_size = strategy.compute_position_size(entry_price, stop_loss)
        
        # Calculate constraints
        max_leveraged_size = (1000.0 * leverage) / entry_price
        max_equity_risk_size = (1000.0 * 0.01) / entry_price
        expected_risk_size = 25.0 / 2.0
        
        print(f"Position Size: {position_size:.4f}")
        print(f"Max Leveraged Size: {max_leveraged_size:.4f}")
        print(f"Max Equity Risk Size: {max_equity_risk_size:.4f}")
        print(f"Expected Risk Size: {expected_risk_size:.4f}")
        
        # Verify constraints
        assert position_size <= max_leveraged_size, f"Position size exceeds leveraged limit"
        assert position_size <= max_equity_risk_size, f"Position size exceeds equity risk limit"
        
        # For low leverage, should be capital-limited
        if leverage <= 2.0:
            assert position_size <= expected_risk_size, f"Position size should be risk-limited for low leverage"
        
        print("✅ Leverage constraints respected")


def test_take_profit_profitable():
    """Test that take-profit exits remain profitable under capital constraints."""
    print("\n🎯 Testing Take-Profit Profitability")
    print("=" * 60)
    
    # Create test data
    test_data = create_test_data()
    
    config = {
        'risk_usdt': 25.0,
        'initial_capital': 1000.0,
        'leverage': 1.0,
        'equity_risk_cap': 0.01,
        'atr_mult_orb': 1.2,
        'tp_multiplier': 1.5,
        'target_r_multiple': 1.5,
        'risk_reward_ratio': 1.5,
        'adx_min': 15.0,
        'force_one_trade': True,
        'fallback_mode': 'EMA15_pullback',
        'orb_window': (8, 9),
        'entry_window': (11, 14),
        'exit_window': (20, 22),
        'session_trading': True,
        'session_timezone': 'America/Argentina/Buenos_Aires',
        'commission_rate': 0.001,
        'slippage_rate': 0.0005,
        'use_multifactor_strategy': False,
    }
    
    strategy = SimpleTradingStrategy(config)
    
    # Process a day to get a trade
    print("🔄 Processing day to generate trade...")
    trades = strategy.process_day(test_data, test_data.index[0].date())
    
    if trades:
        trade = trades[0]
        print(f"\n📊 Trade Details:")
        print(f"Entry Price: {trade['entry_price']:.2f}")
        print(f"Stop Loss: {trade['sl']:.2f}")
        print(f"Take Profit: {trade['tp']:.2f}")
        print(f"Position Size: {trade['position_size']:.4f}")
        print(f"Side: {trade['side']}")
        
        # Verify position size constraints
        entry_price = trade['entry_price']
        stop_loss = trade['sl']
        position_size = trade['position_size']
        
        max_capital_size = (config['initial_capital'] * config['leverage']) / entry_price
        max_equity_risk_size = (config['initial_capital'] * config['equity_risk_cap']) / entry_price
        expected_risk_size = config['risk_usdt'] / abs(entry_price - stop_loss)
        
        print(f"\n🔍 Position Size Analysis:")
        print(f"Actual Position Size: {position_size:.4f}")
        print(f"Max Capital Size: {max_capital_size:.4f}")
        print(f"Max Equity Risk Size: {max_equity_risk_size:.4f}")
        print(f"Expected Risk Size: {expected_risk_size:.4f}")
        
        assert position_size <= max_capital_size, "Position size exceeds capital limit"
        assert position_size <= max_equity_risk_size, "Position size exceeds equity risk limit"
        assert position_size <= expected_risk_size, "Position size exceeds risk-based size"
        
        # Simulate take-profit exit
        print(f"\n🎯 Simulating Take-Profit Exit...")
        exit_info = strategy.simulate_trade_exit({
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': trade['tp'],
            'position_size': position_size
        }, trade['side'], test_data)
        
        print(f"Exit Price: {exit_info['exit_price']:.2f}")
        print(f"Exit Reason: {exit_info['exit_reason']}")
        print(f"Gross PnL: {exit_info['gross_pnl_usdt']:.2f} USDT")
        print(f"Net PnL: {exit_info['pnl_usdt']:.2f} USDT")
        print(f"Commission: {exit_info['commission_usdt']:.2f} USDT")
        print(f"Slippage: {exit_info['slippage_usdt']:.2f} USDT")
        print(f"R-Multiple: {exit_info['r_multiple']:.2f}")
        
        # Verify take-profit is profitable
        assert exit_info['pnl_usdt'] > 0, f"Take-profit exit should be profitable, got {exit_info['pnl_usdt']}"
        assert exit_info['r_multiple'] > 0, f"R-multiple should be positive, got {exit_info['r_multiple']}"
        
        # Verify actual risk doesn't exceed intended risk
        actual_risk = abs(entry_price - stop_loss) * position_size
        assert actual_risk <= config['risk_usdt'] * 1.1, f"Actual risk {actual_risk} exceeds intended risk {config['risk_usdt']}"
        
        print("✅ Take-profit exit is profitable and respects risk constraints")
        
    else:
        print("⚠️ No trades generated")


def test_synthetic_trade():
    """Test synthetic trade with take-profit exit."""
    print("\n🧪 Testing Synthetic Trade")
    print("=" * 60)
    
    # Create test data
    test_data = create_test_data()
    
    config = {
        'risk_usdt': 25.0,
        'initial_capital': 1000.0,
        'leverage': 1.0,
        'equity_risk_cap': 0.01,
        'atr_mult_orb': 1.2,
        'tp_multiplier': 1.5,
        'target_r_multiple': 1.5,
        'risk_reward_ratio': 1.5,
        'adx_min': 15.0,
        'force_one_trade': True,
        'fallback_mode': 'EMA15_pullback',
        'orb_window': (8, 9),
        'entry_window': (11, 14),
        'exit_window': (20, 22),
        'session_trading': True,
        'session_timezone': 'America/Argentina/Buenos_Aires',
        'commission_rate': 0.001,
        'slippage_rate': 0.0005,
        'use_multifactor_strategy': False,
    }
    
    strategy = SimpleTradingStrategy(config)
    
    # Create synthetic trade parameters
    entry_price = 100.0
    stop_loss = 98.0  # 2% risk
    take_profit = 103.0  # 3% reward (1.5R)
    side = 'long'
    
    print(f"📊 Synthetic Trade Parameters:")
    print(f"Entry Price: {entry_price}")
    print(f"Stop Loss: {stop_loss}")
    print(f"Take Profit: {take_profit}")
    print(f"Side: {side}")
    
    # Calculate position size using the helper
    position_size = strategy.compute_position_size(entry_price, stop_loss)
    
    print(f"\n🔍 Position Size Analysis:")
    print(f"Position Size: {position_size:.4f}")
    
    # Verify position size is reasonable
    assert position_size > 0, "Position size should be positive"
    assert position_size <= 10.0, "Position size should be capped by capital"
    
    # Simulate take-profit exit
    print(f"\n🎯 Simulating Take-Profit Exit...")
    exit_info = strategy.simulate_trade_exit({
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'position_size': position_size
    }, side, test_data)
    
    print(f"Exit Price: {exit_info['exit_price']:.2f}")
    print(f"Exit Reason: {exit_info['exit_reason']}")
    print(f"Gross PnL: {exit_info['gross_pnl_usdt']:.2f} USDT")
    print(f"Net PnL: {exit_info['pnl_usdt']:.2f} USDT")
    print(f"Commission: {exit_info['commission_usdt']:.2f} USDT")
    print(f"Slippage: {exit_info['slippage_usdt']:.2f} USDT")
    print(f"R-Multiple: {exit_info['r_multiple']:.2f}")
    
    # Verify take-profit exit is profitable
    assert exit_info['pnl_usdt'] > 0, f"Take-profit exit should be profitable, got {exit_info['pnl_usdt']}"
    
    # Verify R-multiple is approximately 1.5
    expected_r_multiple = 1.5
    actual_r_multiple = exit_info['r_multiple']
    assert abs(actual_r_multiple - expected_r_multiple) < 0.2, f"R-multiple should be ~{expected_r_multiple}, got {actual_r_multiple}"
    
    # Verify costs are reasonable
    total_costs = exit_info['commission_usdt'] + exit_info['slippage_usdt']
    assert total_costs > 0, "Total costs should be positive"
    assert total_costs < exit_info['gross_pnl_usdt'], "Costs should be less than gross profit"
    
    print("✅ Synthetic trade take-profit exit is profitable and respects constraints")


if __name__ == '__main__':
    test_position_sizing_constraints()
    test_leverage_impact()
    test_take_profit_profitable()
    test_synthetic_trade()
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Capital/leverage sizing is working correctly.")
    print("=" * 60)

