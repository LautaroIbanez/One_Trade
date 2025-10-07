#!/usr/bin/env python3
"""
Unit tests for OHLC data normalization and validation.

Tests:
- standardize_ohlc_columns with various column naming conventions
- validate_data_integrity with edge cases
- Handling of missing columns, NaN values, invalid OHLC relationships
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent.parent
repo_root = base_dir.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

from btc_1tpd_backtester.utils import standardize_ohlc_columns, validate_data_integrity


def test_standardize_ohlc_columns_standard_names():
    """Test standardization with already standard column names."""
    print("Testing standardize_ohlc_columns with standard names...")
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='1h', tz='UTC'),
        'open': [100.0] * 10,
        'high': [105.0] * 10,
        'low': [95.0] * 10,
        'close': [102.0] * 10,
        'volume': [1000.0] * 10
    })
    df.set_index('timestamp', inplace=True)
    
    result = standardize_ohlc_columns(df)
    
    assert 'open' in result.columns, "open column should exist"
    assert 'high' in result.columns, "high column should exist"
    assert 'low' in result.columns, "low column should exist"
    assert 'close' in result.columns, "close column should exist"
    assert 'volume' in result.columns, "volume column should exist"
    assert len(result) == 10, "Should have same number of rows"
    
    print("✅ Standard names test passed")


def test_standardize_ohlc_columns_capitalized():
    """Test standardization with capitalized column names."""
    print("Testing standardize_ohlc_columns with capitalized names...")
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='1h', tz='UTC'),
        'Open': [100.0] * 10,
        'High': [105.0] * 10,
        'Low': [95.0] * 10,
        'Close': [102.0] * 10,
        'Volume': [1000.0] * 10
    })
    df.set_index('timestamp', inplace=True)
    
    result = standardize_ohlc_columns(df)
    
    assert 'open' in result.columns, "Should have lowercase 'open'"
    assert 'high' in result.columns, "Should have lowercase 'high'"
    assert 'low' in result.columns, "Should have lowercase 'low'"
    assert 'close' in result.columns, "Should have lowercase 'close'"
    assert 'volume' in result.columns, "Should have lowercase 'volume'"
    
    print("✅ Capitalized names test passed")


def test_standardize_ohlc_columns_abbreviated():
    """Test standardization with abbreviated column names (O, H, L, C, V)."""
    print("Testing standardize_ohlc_columns with abbreviated names...")
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='1h', tz='UTC'),
        'O': [100.0] * 10,
        'H': [105.0] * 10,
        'L': [95.0] * 10,
        'C': [102.0] * 10,
        'V': [1000.0] * 10
    })
    df.set_index('timestamp', inplace=True)
    
    result = standardize_ohlc_columns(df)
    
    assert 'open' in result.columns, "Should rename 'O' to 'open'"
    assert 'high' in result.columns, "Should rename 'H' to 'high'"
    assert 'low' in result.columns, "Should rename 'L' to 'low'"
    assert 'close' in result.columns, "Should rename 'C' to 'close'"
    assert 'volume' in result.columns, "Should rename 'V' to 'volume'"
    
    print("✅ Abbreviated names test passed")


def test_standardize_ohlc_columns_missing_columns():
    """Test that missing columns raise an error."""
    print("Testing standardize_ohlc_columns with missing columns...")
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='1h', tz='UTC'),
        'open': [100.0] * 10,
        'high': [105.0] * 10,
        'low': [95.0] * 10,
        # Missing 'close' column
        'volume': [1000.0] * 10
    })
    df.set_index('timestamp', inplace=True)
    
    try:
        result = standardize_ohlc_columns(df)
        assert False, "Should have raised ValueError for missing column"
    except ValueError as e:
        assert "Missing required OHLC columns" in str(e), f"Wrong error message: {e}"
        print(f"✅ Correctly raised error: {e}")
    
    print("✅ Missing columns test passed")


def test_standardize_ohlc_columns_non_numeric():
    """Test handling of non-numeric data."""
    print("Testing standardize_ohlc_columns with non-numeric data...")
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='1h', tz='UTC'),
        'open': ['100.0', '101.0', '102.0', '103.0', '104.0', '105.0', '106.0', '107.0', '108.0', '109.0'],  # Strings
        'high': [105.0] * 10,
        'low': [95.0] * 10,
        'close': [102.0] * 10,
        'volume': [1000.0] * 10
    })
    df.set_index('timestamp', inplace=True)
    
    result = standardize_ohlc_columns(df)
    
    # Should convert strings to numeric
    assert pd.api.types.is_numeric_dtype(result['open']), "Should convert string to numeric"
    assert result['open'].iloc[0] == 100.0, "Should parse string '100.0' as float 100.0"
    
    print("✅ Non-numeric data test passed")


def test_validate_data_integrity_valid_data():
    """Test validation with valid data."""
    print("Testing validate_data_integrity with valid data...")
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='1h', tz='UTC'),
        'open': np.random.uniform(100, 110, 100),
        'high': np.random.uniform(110, 120, 100),
        'low': np.random.uniform(90, 100, 100),
        'close': np.random.uniform(100, 110, 100),
        'volume': np.random.uniform(1000, 5000, 100)
    })
    df.set_index('timestamp', inplace=True)
    
    is_valid, message = validate_data_integrity(df)
    
    assert is_valid, f"Should be valid: {message}"
    assert message == "Data validation passed", f"Wrong message: {message}"
    
    print("✅ Valid data test passed")


def test_validate_data_integrity_empty():
    """Test validation with empty DataFrame."""
    print("Testing validate_data_integrity with empty DataFrame...")
    
    df = pd.DataFrame()
    
    is_valid, message = validate_data_integrity(df)
    
    assert not is_valid, "Empty DataFrame should be invalid"
    assert "empty" in message.lower(), f"Wrong message: {message}"
    
    print("✅ Empty DataFrame test passed")


def test_validate_data_integrity_insufficient_data():
    """Test validation with insufficient data points."""
    print("Testing validate_data_integrity with insufficient data...")
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='1h', tz='UTC'),  # Only 10 candles
        'open': [100.0] * 10,
        'high': [105.0] * 10,
        'low': [95.0] * 10,
        'close': [102.0] * 10,
        'volume': [1000.0] * 10
    })
    df.set_index('timestamp', inplace=True)
    
    is_valid, message = validate_data_integrity(df)
    
    assert not is_valid, "Should be invalid with only 10 candles"
    assert "Insufficient data" in message, f"Wrong message: {message}"
    
    print("✅ Insufficient data test passed")


def test_validate_data_integrity_nan_values():
    """Test validation with NaN values."""
    print("Testing validate_data_integrity with NaN values...")
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=50, freq='1h', tz='UTC'),
        'open': [100.0] * 50,
        'high': [105.0] * 50,
        'low': [95.0] * 50,
        'close': [np.nan] * 50,  # All NaN
        'volume': [1000.0] * 50
    })
    df.set_index('timestamp', inplace=True)
    
    is_valid, message = validate_data_integrity(df)
    
    assert not is_valid, "Should be invalid with NaN values"
    assert "NaN values" in message, f"Wrong message: {message}"
    
    print("✅ NaN values test passed")


def test_validate_data_integrity_invalid_ohlc():
    """Test validation with invalid OHLC relationships."""
    print("Testing validate_data_integrity with invalid OHLC...")
    
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=50, freq='1h', tz='UTC'),
        'open': [100.0] * 50,
        'high': [90.0] * 50,  # High < Low (invalid!)
        'low': [95.0] * 50,
        'close': [102.0] * 50,
        'volume': [1000.0] * 50
    })
    df.set_index('timestamp', inplace=True)
    
    is_valid, message = validate_data_integrity(df)
    
    assert not is_valid, "Should be invalid with high < low"
    assert "Invalid OHLC" in message, f"Wrong message: {message}"
    
    print("✅ Invalid OHLC test passed")


def test_validate_data_integrity_unsorted_index():
    """Test validation with unsorted index."""
    print("Testing validate_data_integrity with unsorted index...")
    
    timestamps = pd.date_range('2024-01-01', periods=50, freq='1h', tz='UTC')
    # Shuffle timestamps to make them unsorted
    shuffled_idx = timestamps.to_series().sample(frac=1).values
    
    df = pd.DataFrame({
        'open': [100.0] * 50,
        'high': [105.0] * 50,
        'low': [95.0] * 50,
        'close': [102.0] * 50,
        'volume': [1000.0] * 50
    }, index=shuffled_idx)
    
    is_valid, message = validate_data_integrity(df)
    
    assert not is_valid, "Should be invalid with unsorted index"
    assert "chronological order" in message, f"Wrong message: {message}"
    
    print("✅ Unsorted index test passed")


def main():
    """Run all OHLC validation tests."""
    print("Starting OHLC validation tests...")
    print("=" * 70)
    
    try:
        # Standardization tests
        test_standardize_ohlc_columns_standard_names()
        test_standardize_ohlc_columns_capitalized()
        test_standardize_ohlc_columns_abbreviated()
        test_standardize_ohlc_columns_missing_columns()
        test_standardize_ohlc_columns_non_numeric()
        
        # Validation tests
        test_validate_data_integrity_valid_data()
        test_validate_data_integrity_empty()
        test_validate_data_integrity_insufficient_data()
        test_validate_data_integrity_nan_values()
        test_validate_data_integrity_invalid_ohlc()
        test_validate_data_integrity_unsorted_index()
        
        print("\n" + "=" * 70)
        print("All OHLC validation tests passed!")
        print("\nSummary:")
        print("- Column standardization works correctly")
        print("- Data validation catches all error conditions")
        print("- Edge cases handled properly")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

