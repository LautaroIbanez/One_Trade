"""Unit tests for broker_sim module."""
from datetime import datetime

import pandas as pd
import pytest
import pytz

from one_trade.broker_sim import BrokerSimulator


@pytest.fixture
def broker_config():
    """Create broker configuration."""
    broker = {"initial_capital": 10000.0, "quote_currency": "USDT", "fees": {"maker": 0.001, "taker": 0.001}, "slippage": {"enabled": True, "percentage": 0.05}}
    risk = {"stop_loss": {"type": "atr", "atr_multiplier": 2.0}, "take_profit": {"type": "atr", "atr_multiplier": 3.0}, "position_sizing": {"method": "fixed_risk", "risk_per_trade_pct": 1.0, "max_position_pct": 10.0}, "atr": {"period": 14, "timeframe": "1d"}}
    return broker, risk


def test_broker_initialization(broker_config):
    """Test broker initialization."""
    broker, risk = broker_config
    sim = BrokerSimulator(broker, risk)
    assert sim.initial_capital == 10000.0
    assert sim.state.equity == 10000.0


def test_open_position(broker_config):
    """Test opening a position."""
    broker, risk = broker_config
    sim = BrokerSimulator(broker, risk)
    timestamp = datetime(2023, 1, 1, 10, 0, 0, tzinfo=pytz.UTC)
    success = sim.open_position(symbol="BTC/USDT", side="long", timestamp_utc=timestamp, entry_price=30000.0, stop_loss=29000.0, take_profit=32000.0, reason="TEST_ENTRY")
    assert success is True
    assert sim.has_position() is True
    position = sim.get_current_position()
    assert position.side == "long"
    assert position.symbol == "BTC/USDT"


def test_position_size_calculation(broker_config):
    """Test position size calculation with max position limit."""
    broker, risk = broker_config
    sim = BrokerSimulator(broker, risk)
    entry_price = 30000.0
    stop_loss = 29000.0
    equity = 10000.0
    position_size = sim.calculate_position_size(entry_price, stop_loss, equity)
    assert position_size > 0
    risk_amount = equity * 0.01
    risk_based_size = risk_amount / (entry_price - stop_loss)
    max_position_size = equity * 0.10 / entry_price
    expected_size = min(risk_based_size, max_position_size)
    assert abs(position_size - expected_size) < 0.001


def test_stop_loss_hit(broker_config):
    """Test stop loss detection."""
    broker, risk = broker_config
    sim = BrokerSimulator(broker, risk)
    timestamp = datetime(2023, 1, 1, 10, 0, 0, tzinfo=pytz.UTC)
    sim.open_position(symbol="BTC/USDT", side="long", timestamp_utc=timestamp, entry_price=30000.0, stop_loss=29000.0, take_profit=32000.0, reason="TEST_ENTRY")
    bar = pd.Series({"high": 30500.0, "low": 28800.0, "close": 29500.0})
    hit, exit_price, reason = sim.check_stops(bar)
    assert hit is True
    assert reason == "STOP_LOSS"
    assert exit_price == 29000.0


def test_take_profit_hit(broker_config):
    """Test take profit detection."""
    broker, risk = broker_config
    sim = BrokerSimulator(broker, risk)
    timestamp = datetime(2023, 1, 1, 10, 0, 0, tzinfo=pytz.UTC)
    sim.open_position(symbol="BTC/USDT", side="long", timestamp_utc=timestamp, entry_price=30000.0, stop_loss=29000.0, take_profit=32000.0, reason="TEST_ENTRY")
    bar = pd.Series({"high": 32500.0, "low": 30200.0, "close": 32100.0})
    hit, exit_price, reason = sim.check_stops(bar)
    assert hit is True
    assert reason == "TAKE_PROFIT"
    assert exit_price == 32000.0


def test_close_position_pnl(broker_config):
    """Test closing position and PnL calculation."""
    broker, risk = broker_config
    sim = BrokerSimulator(broker, risk)
    timestamp_entry = datetime(2023, 1, 1, 10, 0, 0, tzinfo=pytz.UTC)
    timestamp_exit = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
    sim.open_position(symbol="BTC/USDT", side="long", timestamp_utc=timestamp_entry, entry_price=30000.0, stop_loss=29000.0, take_profit=32000.0, reason="TEST_ENTRY")
    trade = sim.close_position(timestamp_exit, 31000.0, "MANUAL_EXIT")
    assert trade is not None
    assert trade.pnl > 0
    assert sim.has_position() is False


def test_multiple_trades(broker_config):
    """Test multiple trades tracking."""
    broker, risk = broker_config
    sim = BrokerSimulator(broker, risk)
    for i in range(3):
        timestamp_entry = datetime(2023, 1, i + 1, 10, 0, 0, tzinfo=pytz.UTC)
        timestamp_exit = datetime(2023, 1, i + 1, 12, 0, 0, tzinfo=pytz.UTC)
        sim.open_position(symbol="BTC/USDT", side="long", timestamp_utc=timestamp_entry, entry_price=30000.0, stop_loss=29000.0, take_profit=32000.0, reason="TEST_ENTRY")
        sim.close_position(timestamp_exit, 31000.0, "TEST_EXIT")
    assert sim.get_trade_count() == 3

