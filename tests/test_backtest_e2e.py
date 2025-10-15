"""End-to-end backtest tests."""
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest
import pytz

from config.models import Config, load_config
from one_trade.backtest import BacktestEngine


@pytest.fixture
def temp_config_dir():
    """Create temporary directory for config and data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_config(temp_config_dir):
    """Create mock configuration."""
    config_dict = {"exchange": {"name": "binance", "api_key": "", "api_secret": "", "testnet": False, "rate_limit": {"max_requests_per_minute": 1200, "retry_attempts": 3, "backoff_base": 2.0, "backoff_max": 60.0}}, "data": {"symbols": ["BTC/USDT"], "timeframes": ["15m"], "storage_path": f"{temp_config_dir}/data", "format": "csv", "incremental_update": True, "reconciliation": {"check_gaps": False, "max_gap_minutes": 30, "allow_corrections": False}}, "timezone": {"local": "America/Argentina/Buenos_Aires", "exchange": "UTC"}, "strategy": {"type": "baseline", "current": {"indicators": {"ema_fast": 12, "ema_slow": 26, "rsi_period": 14}, "entry_conditions": {"require_ema_cross": True}}, "baseline": {"indicators": {"ema_period": 20, "rsi_period": 14}, "entry_conditions": {"price_above_ema": True, "rsi_range": True}}}, "scheduling": {"entry_window": {"start": "06:00", "end": "12:00"}, "forced_close_window": {"start": "19:00", "end": "20:00"}, "max_trades_per_day": 1, "enforce_daily_limit": True}, "risk": {"stop_loss": {"type": "atr", "atr_multiplier": 2.0}, "take_profit": {"type": "atr", "atr_multiplier": 3.0}, "position_sizing": {"method": "fixed_risk", "risk_per_trade_pct": 1.0, "max_position_pct": 10.0}, "atr": {"period": 14, "timeframe": "1d"}}, "broker": {"initial_capital": 10000.0, "quote_currency": "USDT", "fees": {"maker": 0.001, "taker": 0.001}, "slippage": {"enabled": False, "percentage": 0.05}}, "backtest": {"start_date": "2023-01-01", "end_date": "2023-01-10", "warmup_periods": 30, "save_trades": False, "trades_output": {"path": f"{temp_config_dir}/results", "format": "csv"}, "save_equity_curve": True}, "metrics": {"risk_free_rate": 0.02, "benchmark_symbol": "BTC/USDT", "calculate": ["total_return", "cagr", "sharpe_ratio"]}, "logging": {"level": "INFO", "format": "simple", "output": {"console": False, "file": False, "file_path": f"{temp_config_dir}/logs/test.log"}, "log_trades": False, "log_signals": False, "log_scheduler_events": False}, "reproducibility": {"seed": 42, "deterministic": True}, "validation": {"strict_mode": False, "check_trade_limit_daily": True, "check_entry_windows": True, "check_forced_close": True}}
    config = Config(**config_dict)
    return config


@pytest.fixture
def mock_data(temp_config_dir):
    """Create mock OHLCV data."""
    Path(f"{temp_config_dir}/data").mkdir(parents=True, exist_ok=True)
    art_tz = pytz.timezone("America/Argentina/Buenos_Aires")
    dates_utc = pd.date_range(start="2023-01-01", end="2023-01-10", freq="15min", tz=timezone.utc)
    import numpy as np
    np.random.seed(42)
    close = 30000 + np.cumsum(np.random.randn(len(dates_utc)) * 50)
    data = pd.DataFrame({"timestamp_utc": dates_utc, "timestamp_art": dates_utc.tz_convert(art_tz), "open": close + np.random.randn(len(dates_utc)) * 20, "high": close + np.abs(np.random.randn(len(dates_utc)) * 50), "low": close - np.abs(np.random.randn(len(dates_utc)) * 50), "close": close, "volume": np.random.randint(100, 1000, len(dates_utc)), "source": "binance_15m", "last_updated_utc": datetime.now(timezone.utc)})
    csv_path = Path(f"{temp_config_dir}/data/BTC_USDT_15m.csv")
    data.to_csv(csv_path, index=False)
    return csv_path


def test_backtest_engine_initialization(mock_config):
    """Test backtest engine initialization."""
    engine = BacktestEngine(mock_config)
    assert engine.config == mock_config
    assert engine.broker is not None
    assert engine.strategy is not None


def test_run_backtest_e2e(mock_config, mock_data):
    """Test end-to-end backtest execution."""
    engine = BacktestEngine(mock_config)
    results = engine.run_backtest("BTC/USDT")
    assert "error" not in results
    assert "metrics" in results
    assert "trades" in results
    metrics = results["metrics"]
    assert metrics.final_equity > 0


def test_backtest_respects_daily_limit(mock_config, mock_data):
    """Test that backtest respects daily trade limit."""
    engine = BacktestEngine(mock_config)
    results = engine.run_backtest("BTC/USDT")
    if results["trades"]:
        trades_df = pd.DataFrame([{"date": t.exit_time_art.date(), "symbol": t.symbol} for t in results["trades"]])
        daily_counts = trades_df.groupby("date").size()
        assert all(daily_counts <= 1), "Daily trade limit violated"


def test_backtest_validates_entry_window(mock_config, mock_data):
    """Test that trades only happen within entry window."""
    engine = BacktestEngine(mock_config)
    results = engine.run_backtest("BTC/USDT")
    if results["trades"]:
        for trade in results["trades"]:
            entry_hour = trade.entry_time_art.hour
            assert 6 <= entry_hour <= 12, f"Entry outside window: {entry_hour}:00 ART"









