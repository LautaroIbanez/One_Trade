"""Unit tests for strategy module."""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from one_trade.strategy import BaselineStrategy, CurrentStrategy, StrategyFactory


@pytest.fixture
def sample_data():
    """Create sample OHLCV data."""
    dates = pd.date_range(start="2023-01-01", periods=100, freq="15min")
    np.random.seed(42)
    close = 30000 + np.cumsum(np.random.randn(100) * 100)
    data = pd.DataFrame({"timestamp_utc": dates, "open": close + np.random.randn(100) * 50, "high": close + np.abs(np.random.randn(100) * 100), "low": close - np.abs(np.random.randn(100) * 100), "close": close, "volume": np.random.randint(100, 1000, 100)})
    data = data.set_index("timestamp_utc")
    return data


def test_strategy_factory_current():
    """Test strategy factory creates current strategy."""
    config = {"indicators": {"ema_fast": 12, "ema_slow": 26}, "entry_conditions": {"require_ema_cross": True}}
    strategy = StrategyFactory.create_strategy("current", config)
    assert isinstance(strategy, CurrentStrategy)


def test_strategy_factory_baseline():
    """Test strategy factory creates baseline strategy."""
    config = {"indicators": {"ema_period": 50}, "entry_conditions": {"price_above_ema": True}}
    strategy = StrategyFactory.create_strategy("baseline", config)
    assert isinstance(strategy, BaselineStrategy)


def test_current_strategy_signal_generation(sample_data):
    """Test current strategy signal generation."""
    config = {"indicators": {"ema_fast": 12, "ema_slow": 26, "rsi_period": 14}, "entry_conditions": {"require_ema_cross": True, "require_rsi_confirmation": True, "require_macd_confirmation": True}}
    strategy = CurrentStrategy(config)
    signal = strategy.generate_signal(sample_data, 50)
    assert signal is None or signal.side in ["long", "short"]


def test_baseline_strategy_signal_generation(sample_data):
    """Test baseline strategy signal generation."""
    config = {"indicators": {"ema_period": 20, "rsi_period": 14}, "entry_conditions": {"price_above_ema": True, "rsi_range": True}}
    strategy = BaselineStrategy(config)
    signal = strategy.generate_signal(sample_data, 50)
    assert signal is None or signal.side in ["long", "short"]


def test_current_strategy_should_close(sample_data):
    """Test current strategy close conditions."""
    config = {"indicators": {"ema_fast": 12, "ema_slow": 26}, "entry_conditions": {}}
    strategy = CurrentStrategy(config)
    entry_time = sample_data.index[30]
    entry_price = sample_data.iloc[30]["close"]
    should_close, reason = strategy.should_close(sample_data, 50, "long", entry_price, entry_time)
    assert isinstance(should_close, bool)


def test_baseline_strategy_should_close(sample_data):
    """Test baseline strategy close conditions."""
    config = {"indicators": {"ema_period": 20}, "entry_conditions": {}}
    strategy = BaselineStrategy(config)
    entry_time = sample_data.index[30]
    entry_price = sample_data.iloc[30]["close"]
    should_close, reason = strategy.should_close(sample_data, 50, "long", entry_price, entry_time)
    assert isinstance(should_close, bool)



