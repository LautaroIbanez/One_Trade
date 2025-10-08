"""Tests for windowed daily quota backtest strategy. Covers daily quota enforcement, entry window filtering, trade reporting, and timezone conversion."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from strategy import WindowedSignalStrategy
from backtest_runner import BacktestRunner, TradeRecord

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


@pytest.fixture
def art_tz():
    """Argentina timezone fixture."""
    return ZoneInfo('America/Argentina/Buenos_Aires')


@pytest.fixture
def basic_config():
    """Basic configuration for strategy tests."""
    return {'entry_windows': [(5, 8), (11, 14)], 'timezone': 'America/Argentina/Buenos_Aires', 'risk_usdt': 20.0, 'leverage': 1.0, 'initial_capital': 1000.0, 'atr_multiplier': 2.0, 'risk_reward_ratio': 1.5, 'ema_fast': 9, 'ema_slow': 21, 'rsi_period': 14, 'atr_period': 14}


@pytest.fixture
def multi_day_data():
    """Generate synthetic multi-day OHLCV dataset for testing."""
    start_date = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    dates = [start_date + timedelta(hours=i) for i in range(24 * 5)]
    data = pd.DataFrame({'open': [100 + i * 0.1 for i in range(len(dates))], 'high': [101 + i * 0.1 for i in range(len(dates))], 'low': [99 + i * 0.1 for i in range(len(dates))], 'close': [100 + i * 0.1 for i in range(len(dates))], 'volume': [1000000] * len(dates)}, index=pd.DatetimeIndex(dates, tz=timezone.utc))
    return data


@pytest.fixture
def abundant_signals_data():
    """Generate dataset with price movements that should trigger multiple signals."""
    start_date = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    dates = [start_date + timedelta(hours=i) for i in range(24 * 3)]
    base_price = 50000
    prices = []
    for i in range(len(dates)):
        trend = i * 50
        noise = np.sin(i / 6) * 200
        prices.append(base_price + trend + noise)
    data = pd.DataFrame({'open': prices, 'high': [p * 1.01 for p in prices], 'low': [p * 0.99 for p in prices], 'close': prices, 'volume': [1000000] * len(dates)}, index=pd.DatetimeIndex(dates, tz=timezone.utc))
    return data


def test_daily_quota_enforcement(basic_config, abundant_signals_data):
    """Test that exactly one trade occurs per day even with abundant signals."""
    runner = BacktestRunner(abundant_signals_data, basic_config)
    result = runner.run()
    trades_df = result['_trades']
    assert not trades_df.empty, "Should have executed trades"
    trades_df['entry_date'] = pd.to_datetime(trades_df['entry_time']).dt.date
    trades_per_day = trades_df.groupby('entry_date').size()
    assert (trades_per_day <= 1).all(), f"Should have max 1 trade per day, got: {trades_per_day.to_dict()}"
    print(f"✓ Daily quota enforced: {len(trades_per_day)} days with trades, all ≤ 1 trade/day")


def test_entry_window_filtering_morning(basic_config, multi_day_data):
    """Test that trades only occur during morning window (05-08 ART)."""
    config = basic_config.copy()
    config['entry_windows'] = [(5, 8)]
    runner = BacktestRunner(multi_day_data, config)
    result = runner.run()
    trades_df = result['_trades']
    if not trades_df.empty:
        art_tz = ZoneInfo('America/Argentina/Buenos_Aires')
        trades_df['entry_time_art'] = pd.to_datetime(trades_df['entry_time']).dt.tz_convert(art_tz)
        trades_df['entry_hour_art'] = trades_df['entry_time_art'].dt.hour
        assert (trades_df['entry_hour_art'] >= 5).all() and (trades_df['entry_hour_art'] < 8).all(), f"Trades should be in 05-08 ART window, got hours: {trades_df['entry_hour_art'].unique()}"
        print(f"✓ Morning window (05-08 ART) enforced: {len(trades_df)} trades")
    else:
        print("✓ No trades executed (expected if no signals in morning window)")


def test_entry_window_filtering_midday(basic_config, multi_day_data):
    """Test that trades only occur during midday window (11-14 ART)."""
    config = basic_config.copy()
    config['entry_windows'] = [(11, 14)]
    runner = BacktestRunner(multi_day_data, config)
    result = runner.run()
    trades_df = result['_trades']
    if not trades_df.empty:
        art_tz = ZoneInfo('America/Argentina/Buenos_Aires')
        trades_df['entry_time_art'] = pd.to_datetime(trades_df['entry_time']).dt.tz_convert(art_tz)
        trades_df['entry_hour_art'] = trades_df['entry_time_art'].dt.hour
        assert (trades_df['entry_hour_art'] >= 11).all() and (trades_df['entry_hour_art'] < 14).all(), f"Trades should be in 11-14 ART window, got hours: {trades_df['entry_hour_art'].unique()}"
        print(f"✓ Midday window (11-14 ART) enforced: {len(trades_df)} trades")
    else:
        print("✓ No trades executed (expected if no signals in midday window)")


def test_trade_reporting_preserves_all_rows(basic_config, abundant_signals_data):
    """Test that trade reporting preserves all trade rows."""
    runner = BacktestRunner(abundant_signals_data, basic_config)
    result = runner.run()
    trades_df = result['_trades']
    metrics = result['_metrics']
    assert isinstance(trades_df, pd.DataFrame), "Should return DataFrame"
    assert isinstance(metrics, dict), "Should return metrics dict"
    if not trades_df.empty:
        assert 'entry_time' in trades_df.columns, "Should have entry_time column"
        assert 'exit_time' in trades_df.columns, "Should have exit_time column"
        assert 'pnl' in trades_df.columns, "Should have pnl column"
        assert 'side' in trades_df.columns, "Should have side column"
        assert len(trades_df) == metrics['total_trades'], f"Trade count mismatch: df has {len(trades_df)}, metrics has {metrics['total_trades']}"
        print(f"✓ Trade reporting intact: {len(trades_df)} rows preserved")
    else:
        print("✓ No trades to report")


def test_timezone_conversion_art(basic_config, multi_day_data):
    """Test that UTC timestamps are correctly converted to ART for daily reset."""
    strategy = WindowedSignalStrategy(basic_config)
    utc_midnight = datetime(2024, 1, 2, 3, 0, tzinfo=timezone.utc)
    art_time = strategy._to_local(utc_midnight)
    art_tz = ZoneInfo('America/Argentina/Buenos_Aires')
    expected_art_time = utc_midnight.astimezone(art_tz)
    assert art_time.hour == expected_art_time.hour, f"ART conversion failed: expected hour {expected_art_time.hour}, got {art_time.hour}"
    assert art_time.tzinfo == art_tz or str(art_time.tzinfo) == str(art_tz), f"Timezone should be ART, got {art_time.tzinfo}"
    print(f"✓ Timezone conversion: UTC {utc_midnight.hour}:00 → ART {art_time.hour}:00")


def test_daily_reset_logic(basic_config):
    """Test that daily trade counter resets correctly at midnight ART."""
    strategy = WindowedSignalStrategy(basic_config)
    day1_morning = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
    strategy.record_trade(day1_morning)
    assert not strategy.can_trade_today(day1_morning), "Should not allow second trade same day"
    day2_morning = datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc)
    assert strategy.can_trade_today(day2_morning), "Should allow trade on new day"
    print(f"✓ Daily reset logic: quota resets correctly at day boundary")


def test_position_sizing_within_capital_limits(basic_config):
    """Test that position sizing respects capital and leverage constraints."""
    strategy = WindowedSignalStrategy(basic_config)
    entry_price = 50000
    sl = 49000
    position_size = strategy.compute_position_size(entry_price, sl)
    risk_distance = abs(entry_price - sl)
    position_value = position_size * entry_price
    max_position_value = basic_config['initial_capital'] * basic_config['leverage']
    assert position_size > 0, "Position size should be positive"
    assert position_value <= max_position_value, f"Position value {position_value} exceeds max {max_position_value}"
    expected_size_by_risk = basic_config['risk_usdt'] / risk_distance
    assert position_size <= expected_size_by_risk, f"Position size {position_size} should not exceed risk-based {expected_size_by_risk}"
    print(f"✓ Position sizing: {position_size:.4f} @ ${entry_price} = ${position_value:.2f} (max: ${max_position_value:.2f})")


def test_signal_generation_with_indicators(basic_config, multi_day_data):
    """Test signal generation with EMA/RSI/MACD alignment."""
    strategy = WindowedSignalStrategy(basic_config)
    strategy.set_market_data(multi_day_data)
    for i in range(30, len(multi_day_data)):
        signal = strategy.generate_signal(i)
        if signal['valid']:
            assert signal['side'] in ['long', 'short'], f"Signal side should be long/short, got {signal['side']}"
            assert signal['entry_price'] > 0, "Entry price should be positive"
            assert signal['sl'] > 0, "Stop loss should be positive"
            assert signal['tp'] > 0, "Take profit should be positive"
            assert 'reason' in signal, "Signal should have reason"
            print(f"✓ Valid signal at index {i}: {signal['side']} @ {signal['entry_price']:.2f}, reason={signal['reason']}")
            break


def test_metrics_calculation_accuracy(basic_config, abundant_signals_data):
    """Test that calculated metrics are accurate."""
    runner = BacktestRunner(abundant_signals_data, basic_config)
    result = runner.run()
    trades_df = result['_trades']
    metrics = result['_metrics']
    if not trades_df.empty:
        assert metrics['total_trades'] == len(trades_df), "Total trades mismatch"
        calculated_pnl = trades_df['pnl'].sum()
        assert abs(metrics['total_pnl'] - calculated_pnl) < 0.01, f"PnL mismatch: metrics={metrics['total_pnl']}, calculated={calculated_pnl}"
        wins = len(trades_df[trades_df['pnl'] > 0])
        calculated_win_rate = (wins / len(trades_df)) * 100
        assert abs(metrics['win_rate'] - calculated_win_rate) < 0.1, f"Win rate mismatch: metrics={metrics['win_rate']}, calculated={calculated_win_rate}"
        print(f"✓ Metrics accurate: {metrics['total_trades']} trades, {metrics['total_pnl']:.2f} PnL, {metrics['win_rate']:.1f}% WR")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

