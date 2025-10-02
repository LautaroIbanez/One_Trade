#!/usr/bin/env python3
"""
Test date parsing improvements in load_trades function.
"""

import sys
import pandas as pd
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

from webapp.app import load_trades


def test_iso8601_date_parsing():
    """Test that ISO8601 dates with microseconds and timezone are parsed correctly."""
    print("Testing ISO8601 date parsing with microseconds and timezone...")
    
    # Create test CSV with various date formats
    test_data = {
        "entry_time": [
            "2024-01-15T12:30:45.123456Z",  # ISO8601 with microseconds and Z
            "2024-01-15T12:30:45.123456+00:00",  # ISO8601 with microseconds and timezone
            "2024-01-15T12:30:45Z",  # ISO8601 without microseconds
            "2024-01-15T12:30:45+00:00",  # ISO8601 without microseconds but with timezone
            "2024-01-15T12:30:45",  # ISO8601 without timezone
            "invalid-date",  # Invalid date to test error handling
        ],
        "exit_time": [
            "2024-01-15T13:30:45.123456Z",
            "2024-01-15T13:30:45.123456+00:00",
            "2024-01-15T13:30:45Z",
            "2024-01-15T13:30:45+00:00",
            "2024-01-15T13:30:45",
            "invalid-date",
        ],
        "side": ["long", "short", "long", "short", "long", "long"],
        "entry_price": [50000.0, 50000.0, 50000.0, 50000.0, 50000.0, 50000.0],
        "exit_price": [51000.0, 49000.0, 51000.0, 49000.0, 51000.0, 51000.0],
        "pnl_usdt": [1000.0, -1000.0, 1000.0, -1000.0, 1000.0, 1000.0],
    }
    
    df = pd.DataFrame(test_data)
    
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_csv = Path(f.name)
    
    try:
        # Test loading the CSV
        result = load_trades(csv_path=temp_csv.name)
        
        # Verify that valid dates were parsed correctly
        assert len(result) == 5, f"Expected 5 valid rows, got {len(result)}"  # 5 valid, 1 invalid removed
        
        # Check that entry_time column exists and has datetime type
        assert "entry_time" in result.columns, "entry_time column should exist"
        assert pd.api.types.is_datetime64_any_dtype(result["entry_time"]), "entry_time should be datetime type"
        
        # Check that exit_time column exists and has datetime type
        assert "exit_time" in result.columns, "exit_time column should exist"
        assert pd.api.types.is_datetime64_any_dtype(result["exit_time"]), "exit_time should be datetime type"
        
        # Verify that all dates are timezone-aware (UTC)
        assert result["entry_time"].dt.tz is not None, "entry_time should be timezone-aware"
        assert result["exit_time"].dt.tz is not None, "exit_time should be timezone-aware"
        
        print("ISO8601 date parsing test passed")
        
    finally:
        # Clean up temporary file
        temp_csv.unlink(missing_ok=True)


def test_corrupted_csv_handling():
    """Test that corrupted CSV files with invalid dates don't break the loading process."""
    print("\nTesting corrupted CSV handling...")
    
    # Create CSV with corrupted dates
    test_data = {
        "entry_time": [
            "2024-01-15T12:30:45Z",  # Valid
            "not-a-date",  # Invalid
            "2024-01-15T12:30:45Z",  # Valid
            "",  # Empty
            "2024-01-15T12:30:45Z",  # Valid
        ],
        "exit_time": [
            "2024-01-15T13:30:45Z",
            "not-a-date",
            "2024-01-15T13:30:45Z",
            "",
            "2024-01-15T13:30:45Z",
        ],
        "side": ["long", "short", "long", "short", "long"],
        "entry_price": [50000.0, 50000.0, 50000.0, 50000.0, 50000.0],
        "exit_price": [51000.0, 49000.0, 51000.0, 49000.0, 51000.0],
        "pnl_usdt": [1000.0, -1000.0, 1000.0, -1000.0, 1000.0],
    }
    
    df = pd.DataFrame(test_data)
    
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_csv = Path(f.name)
    
    try:
        # Test loading the CSV - should not raise an exception
        result = load_trades(csv_path=temp_csv.name)
        
        # Should have 3 valid rows (invalid dates removed)
        assert len(result) == 3, f"Expected 3 valid rows, got {len(result)}"
        
        # All remaining rows should have valid datetime
        assert not result["entry_time"].isna().any(), "No NaN values should remain in entry_time"
        
        print("Corrupted CSV handling test passed")
        
    finally:
        # Clean up temporary file
        temp_csv.unlink(missing_ok=True)


def test_timezone_preservation():
    """Test that timezone information is preserved correctly."""
    print("\nTesting timezone preservation...")
    
    # Create test data with timezone-aware dates
    test_data = {
        "entry_time": [
            "2024-01-15T12:30:45Z",  # UTC
            "2024-01-15T12:30:45+00:00",  # UTC with offset
            "2024-01-15T12:30:45-05:00",  # EST
        ],
        "exit_time": [
            "2024-01-15T13:30:45Z",
            "2024-01-15T13:30:45+00:00",
            "2024-01-15T13:30:45-05:00",
        ],
        "side": ["long", "short", "long"],
        "entry_price": [50000.0, 50000.0, 50000.0],
        "exit_price": [51000.0, 49000.0, 51000.0],
        "pnl_usdt": [1000.0, -1000.0, 1000.0],
    }
    
    df = pd.DataFrame(test_data)
    
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_csv = Path(f.name)
    
    try:
        # Test loading the CSV
        result = load_trades(csv_path=temp_csv.name)
        
        # Verify timezone preservation
        assert len(result) == 3, f"Expected 3 rows, got {len(result)}"
        assert result["entry_time"].dt.tz is not None, "entry_time should be timezone-aware"
        assert result["exit_time"].dt.tz is not None, "exit_time should be timezone-aware"
        
        # Check that all times are in UTC
        assert all(tz.zone == 'UTC' or tz.utcoffset(None).total_seconds() == 0 
                  for tz in result["entry_time"].dt.tz.unique()), "All times should be in UTC"
        
        print("Timezone preservation test passed")
        
    finally:
        # Clean up temporary file
        temp_csv.unlink(missing_ok=True)


def main():
    """Run all date parsing tests."""
    print("Starting date parsing tests...")
    print("=" * 50)
    
    try:
        test_iso8601_date_parsing()
        test_corrupted_csv_handling()
        test_timezone_preservation()
        
        print("\n" + "=" * 50)
        print("All date parsing tests passed!")
        print("\nSummary:")
        print("[OK] ISO8601 dates with microseconds and timezone parsed correctly")
        print("[OK] Corrupted CSV files handled gracefully")
        print("[OK] Timezone information preserved correctly")
        print("[OK] Invalid dates removed without breaking the loading process")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
