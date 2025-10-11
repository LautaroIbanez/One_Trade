"""Data storage module for incremental OHLCV data."""
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import pytz


class DataStore:
    """Manages incremental storage of OHLCV data in CSV/Parquet format."""
    
    REQUIRED_COLUMNS = ["timestamp_utc", "timestamp_art", "open", "high", "low", "close", "volume", "source", "last_updated_utc"]
    
    def __init__(self, storage_path: str, data_format: str = "csv", local_tz: str = "America/Argentina/Buenos_Aires"):
        """Initialize DataStore. Args: storage_path: Directory to store data files. data_format: 'csv' or 'parquet'. local_tz: Local timezone for timestamp_art."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.data_format = data_format.lower()
        self.local_tz = pytz.timezone(local_tz)
        if self.data_format not in ["csv", "parquet"]:
            raise ValueError(f"Invalid data format: {self.data_format}. Must be 'csv' or 'parquet'.")
    
    def _get_file_path(self, symbol: str, timeframe: str) -> Path:
        """Get file path for symbol and timeframe. Args: symbol: Trading symbol (e.g., 'BTC/USDT'). timeframe: Timeframe (e.g., '15m', '1d'). Returns: Path to data file."""
        safe_symbol = symbol.replace("/", "_")
        filename = f"{safe_symbol}_{timeframe}.{self.data_format}"
        return self.storage_path / filename
    
    def read_data(self, symbol: str, timeframe: str) -> Tuple[Optional[pd.DataFrame], Optional[datetime]]:
        """Read existing data and return last timestamp. Args: symbol: Trading symbol. timeframe: Timeframe. Returns: Tuple of (DataFrame or None, last_timestamp_utc or None)."""
        file_path = self._get_file_path(symbol, timeframe)
        if not file_path.exists():
            return None, None
        try:
            if self.data_format == "csv":
                df = pd.read_csv(file_path, parse_dates=["timestamp_utc", "timestamp_art", "last_updated_utc"])
            else:
                df = pd.read_parquet(file_path)
            if df.empty:
                return df, None
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
            df = df.sort_values("timestamp_utc").reset_index(drop=True)
            last_timestamp = df["timestamp_utc"].max()
            if pd.isna(last_timestamp):
                return df, None
            if not isinstance(last_timestamp, datetime):
                last_timestamp = pd.to_datetime(last_timestamp)
            if last_timestamp.tzinfo is None:
                last_timestamp = last_timestamp.replace(tzinfo=timezone.utc)
            return df, last_timestamp
        except Exception as e:
            raise RuntimeError(f"Failed to read data for {symbol} {timeframe}: {e}") from e
    
    def write_data(self, symbol: str, timeframe: str, new_data: pd.DataFrame, source: str) -> None:
        """Write new data, merging with existing data and handling duplicates. Args: symbol: Trading symbol. timeframe: Timeframe. new_data: DataFrame with columns [timestamp_utc, open, high, low, close, volume]. source: Data source identifier (e.g., 'binance_15m')."""
        if new_data.empty:
            return
        required_input_cols = ["timestamp_utc", "open", "high", "low", "close", "volume"]
        for col in required_input_cols:
            if col not in new_data.columns:
                raise ValueError(f"new_data missing required column: {col}")
        prepared_data = new_data.copy()
        if not pd.api.types.is_datetime64_any_dtype(prepared_data["timestamp_utc"]):
            prepared_data["timestamp_utc"] = pd.to_datetime(prepared_data["timestamp_utc"], unit="ms")
        if prepared_data["timestamp_utc"].dt.tz is None:
            prepared_data["timestamp_utc"] = prepared_data["timestamp_utc"].dt.tz_localize(timezone.utc)
        else:
            prepared_data["timestamp_utc"] = prepared_data["timestamp_utc"].dt.tz_convert(timezone.utc)
        prepared_data["timestamp_art"] = prepared_data["timestamp_utc"].dt.tz_convert(self.local_tz)
        prepared_data["source"] = source
        prepared_data["last_updated_utc"] = datetime.now(timezone.utc)
        existing_data, _ = self.read_data(symbol, timeframe)
        if existing_data is not None and not existing_data.empty:
            combined = pd.concat([existing_data, prepared_data], ignore_index=True)
            combined = combined.sort_values("timestamp_utc")
            duplicates = combined.duplicated(subset=["timestamp_utc"], keep="last")
            combined = combined[~duplicates].reset_index(drop=True)
        else:
            combined = prepared_data
        combined = combined[self.REQUIRED_COLUMNS]
        file_path = self._get_file_path(symbol, timeframe)
        try:
            if self.data_format == "csv":
                combined.to_csv(file_path, index=False, date_format="%Y-%m-%d %H:%M:%S%z")
            else:
                combined.to_parquet(file_path, index=False, engine="pyarrow")
        except Exception as e:
            raise RuntimeError(f"Failed to write data for {symbol} {timeframe}: {e}") from e
    
    def check_gaps(self, symbol: str, timeframe: str, max_gap_minutes: int = 30) -> list[dict]:
        """Check for gaps in data. Args: symbol: Trading symbol. timeframe: Timeframe. max_gap_minutes: Maximum allowed gap in minutes. Returns: List of gap dictionaries with start, end, and duration."""
        existing_data, _ = self.read_data(symbol, timeframe)
        if existing_data is None or existing_data.empty or len(existing_data) < 2:
            return []
        timeframe_to_minutes = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "4h": 240, "1d": 1440, "1w": 10080}
        expected_interval_minutes = timeframe_to_minutes.get(timeframe, 15)
        existing_data = existing_data.sort_values("timestamp_utc").reset_index(drop=True)
        timestamps = existing_data["timestamp_utc"]
        gaps = []
        for i in range(len(timestamps) - 1):
            current = timestamps.iloc[i]
            next_ts = timestamps.iloc[i + 1]
            diff_minutes = (next_ts - current).total_seconds() / 60
            expected_diff = expected_interval_minutes
            if diff_minutes > expected_diff + max_gap_minutes:
                gaps.append({"start": current, "end": next_ts, "duration_minutes": diff_minutes, "expected_minutes": expected_diff})
        return gaps
    
    def get_date_range(self, symbol: str, timeframe: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get the date range of stored data. Args: symbol: Trading symbol. timeframe: Timeframe. Returns: Tuple of (first_timestamp, last_timestamp) or (None, None)."""
        existing_data, _ = self.read_data(symbol, timeframe)
        if existing_data is None or existing_data.empty:
            return None, None
        return existing_data["timestamp_utc"].min(), existing_data["timestamp_utc"].max()
    
    def delete_data(self, symbol: str, timeframe: str) -> None:
        """Delete data file for symbol and timeframe. Args: symbol: Trading symbol. timeframe: Timeframe."""
        file_path = self._get_file_path(symbol, timeframe)
        if file_path.exists():
            file_path.unlink()



