"""Unit tests for data_store module."""
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from one_trade.data_store import DataStore


@pytest.fixture
def temp_storage():
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_data_store_initialization(temp_storage):
    """Test DataStore initialization."""
    store = DataStore(storage_path=temp_storage, data_format="csv")
    assert store.storage_path == Path(temp_storage)
    assert store.data_format == "csv"


def test_write_and_read_data(temp_storage):
    """Test writing and reading data."""
    store = DataStore(storage_path=temp_storage, data_format="csv")
    timestamps = pd.date_range(start="2023-01-01", periods=10, freq="15min", tz=timezone.utc)
    test_data = pd.DataFrame({"timestamp_utc": timestamps, "open": [100.0] * 10, "high": [101.0] * 10, "low": [99.0] * 10, "close": [100.5] * 10, "volume": [1000.0] * 10})
    store.write_data("BTC/USDT", "15m", test_data, "binance_15m")
    read_data, last_timestamp = store.read_data("BTC/USDT", "15m")
    assert read_data is not None
    assert len(read_data) == 10
    assert last_timestamp == timestamps[-1]


def test_duplicate_handling(temp_storage):
    """Test that duplicates are handled correctly."""
    store = DataStore(storage_path=temp_storage, data_format="csv")
    timestamps = pd.date_range(start="2023-01-01", periods=5, freq="15min", tz=timezone.utc)
    test_data1 = pd.DataFrame({"timestamp_utc": timestamps, "open": [100.0] * 5, "high": [101.0] * 5, "low": [99.0] * 5, "close": [100.5] * 5, "volume": [1000.0] * 5})
    store.write_data("BTC/USDT", "15m", test_data1, "binance_15m")
    timestamps2 = pd.date_range(start="2023-01-01 00:30:00", periods=5, freq="15min", tz=timezone.utc)
    test_data2 = pd.DataFrame({"timestamp_utc": timestamps2, "open": [102.0] * 5, "high": [103.0] * 5, "low": [101.0] * 5, "close": [102.5] * 5, "volume": [2000.0] * 5})
    store.write_data("BTC/USDT", "15m", test_data2, "binance_15m")
    read_data, _ = store.read_data("BTC/USDT", "15m")
    assert len(read_data) == 7
    overlapping_rows = read_data[read_data["timestamp_utc"].isin(timestamps2[:3])]
    assert all(overlapping_rows["open"] == 102.0)


def test_check_gaps(temp_storage):
    """Test gap detection."""
    store = DataStore(storage_path=temp_storage, data_format="csv")
    timestamps = list(pd.date_range(start="2023-01-01", periods=5, freq="15min", tz=timezone.utc))
    timestamps.extend(pd.date_range(start="2023-01-01 02:00:00", periods=5, freq="15min", tz=timezone.utc))
    test_data = pd.DataFrame({"timestamp_utc": timestamps, "open": [100.0] * 10, "high": [101.0] * 10, "low": [99.0] * 10, "close": [100.5] * 10, "volume": [1000.0] * 10})
    store.write_data("BTC/USDT", "15m", test_data, "binance_15m")
    gaps = store.check_gaps("BTC/USDT", "15m", max_gap_minutes=20)
    assert len(gaps) == 1
    assert gaps[0]["duration_minutes"] > 20


def test_get_date_range(temp_storage):
    """Test getting date range."""
    store = DataStore(storage_path=temp_storage, data_format="csv")
    start = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end = datetime(2023, 1, 2, tzinfo=timezone.utc)
    timestamps = pd.date_range(start=start, end=end, freq="1h", tz=timezone.utc)
    test_data = pd.DataFrame({"timestamp_utc": timestamps, "open": [100.0] * len(timestamps), "high": [101.0] * len(timestamps), "low": [99.0] * len(timestamps), "close": [100.5] * len(timestamps), "volume": [1000.0] * len(timestamps)})
    store.write_data("BTC/USDT", "1h", test_data, "binance_1h")
    first, last = store.get_date_range("BTC/USDT", "1h")
    assert first == start
    assert last == end









