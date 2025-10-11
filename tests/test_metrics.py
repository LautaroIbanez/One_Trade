"""Unit tests for metrics module."""
from datetime import datetime

import pandas as pd
import pytest
import pytz

from one_trade.broker_sim import Trade
from one_trade.metrics import MetricsCalculator


@pytest.fixture
def sample_trades():
    """Create sample trades."""
    trades = []
    for i in range(10):
        pnl = 100 if i % 2 == 0 else -50
        trade = Trade(symbol="BTC/USDT", side="long", entry_time_utc=datetime(2023, 1, i + 1, 10, 0, 0, tzinfo=pytz.UTC), entry_time_art=datetime(2023, 1, i + 1, 7, 0, 0, tzinfo=pytz.timezone("America/Argentina/Buenos_Aires")), entry_price=30000.0, exit_time_utc=datetime(2023, 1, i + 1, 12, 0, 0, tzinfo=pytz.UTC), exit_time_art=datetime(2023, 1, i + 1, 9, 0, 0, tzinfo=pytz.timezone("America/Argentina/Buenos_Aires")), exit_price=30000.0 + pnl, size=0.1, pnl=pnl * 0.1, pnl_pct=(pnl / 30000.0) * 100, fees=6.0, entry_reason="TEST", exit_reason="TEST", stop_loss=29000.0, take_profit=31000.0)
        trades.append(trade)
    return trades


def test_metrics_calculator_initialization():
    """Test metrics calculator initialization."""
    calc = MetricsCalculator(initial_capital=10000.0, risk_free_rate=0.02)
    assert calc.initial_capital == 10000.0
    assert calc.risk_free_rate == 0.02


def test_calculate_metrics(sample_trades):
    """Test metrics calculation."""
    calc = MetricsCalculator(initial_capital=10000.0)
    metrics = calc.calculate_metrics(sample_trades)
    assert metrics.total_trades == 10
    assert metrics.winning_trades == 5
    assert metrics.losing_trades == 5
    assert metrics.win_rate == 50.0


def test_win_rate_calculation(sample_trades):
    """Test win rate calculation."""
    calc = MetricsCalculator(initial_capital=10000.0)
    metrics = calc.calculate_metrics(sample_trades)
    expected_win_rate = (5 / 10) * 100
    assert metrics.win_rate == expected_win_rate


def test_profit_factor_calculation(sample_trades):
    """Test profit factor calculation."""
    calc = MetricsCalculator(initial_capital=10000.0)
    metrics = calc.calculate_metrics(sample_trades)
    gross_profit = sum(t.pnl for t in sample_trades if t.pnl > 0)
    gross_loss = abs(sum(t.pnl for t in sample_trades if t.pnl < 0))
    expected_pf = gross_profit / gross_loss if gross_loss > 0 else 0
    assert abs(metrics.profit_factor - expected_pf) < 0.01


def test_empty_trades():
    """Test metrics with empty trades list."""
    calc = MetricsCalculator(initial_capital=10000.0)
    metrics = calc.calculate_metrics([])
    assert metrics.total_trades == 0
    assert metrics.final_equity == 10000.0


def test_max_drawdown_calculation():
    """Test max drawdown calculation."""
    calc = MetricsCalculator(initial_capital=10000.0)
    equity_curve = pd.DataFrame({"timestamp": pd.date_range(start="2023-01-01", periods=5, freq="D"), "equity": [10000, 11000, 9500, 12000, 11500]})
    max_dd, max_dd_pct = calc._calculate_max_drawdown(equity_curve)
    assert max_dd > 0
    assert max_dd_pct > 0



