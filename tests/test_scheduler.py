"""Unit tests for scheduler module."""
from datetime import datetime

import pytest
import pytz

from one_trade.scheduler import TradingScheduler


@pytest.fixture
def scheduler_config():
    """Create scheduler configuration."""
    scheduling = {"entry_window": {"start": "06:00", "end": "12:00"}, "forced_close_window": {"start": "19:00", "end": "20:00"}, "max_trades_per_day": 1, "enforce_daily_limit": True}
    validation = {"strict_mode": True, "check_trade_limit_daily": True, "check_entry_windows": True, "check_forced_close": True}
    return scheduling, validation


def test_scheduler_initialization(scheduler_config):
    """Test scheduler initialization."""
    scheduling, validation = scheduler_config
    scheduler = TradingScheduler(scheduling, validation)
    assert scheduler.max_trades_per_day == 1
    assert scheduler.enforce_daily_limit is True


def test_entry_window_validation(scheduler_config):
    """Test entry window validation."""
    scheduling, validation = scheduler_config
    scheduler = TradingScheduler(scheduling, validation)
    art_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    inside_window = art_tz.localize(datetime(2023, 1, 1, 10, 0, 0))
    outside_window = art_tz.localize(datetime(2023, 1, 1, 14, 0, 0))
    can_enter, reason = scheduler.can_enter_trade(inside_window.astimezone(pytz.UTC), "BTC/USDT")
    assert can_enter is True
    can_enter, reason = scheduler.can_enter_trade(outside_window.astimezone(pytz.UTC), "BTC/USDT")
    assert can_enter is False
    assert "Outside entry window" in reason


def test_daily_trade_limit(scheduler_config):
    """Test daily trade limit enforcement."""
    scheduling, validation = scheduler_config
    scheduler = TradingScheduler(scheduling, validation)
    art_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    timestamp1 = art_tz.localize(datetime(2023, 1, 1, 10, 0, 0)).astimezone(pytz.UTC)
    timestamp2 = art_tz.localize(datetime(2023, 1, 1, 11, 0, 0)).astimezone(pytz.UTC)
    can_enter, _ = scheduler.can_enter_trade(timestamp1, "BTC/USDT")
    assert can_enter is True
    scheduler.register_trade(timestamp1, "BTC/USDT")
    can_enter, reason = scheduler.can_enter_trade(timestamp2, "BTC/USDT")
    assert can_enter is False
    assert "Daily trade limit" in reason


def test_forced_close_window(scheduler_config):
    """Test forced close window detection."""
    scheduling, validation = scheduler_config
    scheduler = TradingScheduler(scheduling, validation)
    art_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    inside_close = art_tz.localize(datetime(2023, 1, 1, 19, 30, 0)).astimezone(pytz.UTC)
    outside_close = art_tz.localize(datetime(2023, 1, 1, 15, 0, 0)).astimezone(pytz.UTC)
    should_close, reason = scheduler.should_force_close(inside_close)
    assert should_close is True
    assert "FORCED_CLOSE" in reason
    should_close, _ = scheduler.should_force_close(outside_close)
    assert should_close is False


def test_daily_counter_reset(scheduler_config):
    """Test that daily counters reset on new day."""
    scheduling, validation = scheduler_config
    scheduler = TradingScheduler(scheduling, validation)
    art_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    day1 = art_tz.localize(datetime(2023, 1, 1, 10, 0, 0)).astimezone(pytz.UTC)
    day2 = art_tz.localize(datetime(2023, 1, 2, 10, 0, 0)).astimezone(pytz.UTC)
    scheduler.register_trade(day1, "BTC/USDT")
    can_enter, _ = scheduler.can_enter_trade(day1, "BTC/USDT")
    assert can_enter is False
    can_enter, _ = scheduler.can_enter_trade(day2, "BTC/USDT")
    assert can_enter is True


def test_strict_mode_violation(scheduler_config):
    """Test strict mode raises exception when registering excessive trades."""
    scheduling, validation = scheduler_config
    scheduler = TradingScheduler(scheduling, validation)
    art_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    timestamp = art_tz.localize(datetime(2023, 1, 1, 10, 0, 0)).astimezone(pytz.UTC)
    scheduler.register_trade(timestamp, "BTC/USDT")
    with pytest.raises(RuntimeError, match="STRICT MODE VIOLATION"):
        scheduler.register_trade(timestamp, "BTC/USDT")

