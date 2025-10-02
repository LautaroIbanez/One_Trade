#!/usr/bin/env python3
"""
Test timezone preservation in monthly performance grouping.
"""

import sys
import pandas as pd
import warnings
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

from webapp.app import figure_monthly_performance, to_argentina_time


def test_monthly_grouping_timezone():
    """Test that monthly grouping works correctly with timezone-aware dates."""
    print("Testing monthly grouping with timezone-aware dates...")
    
    # Create test data with timezone-aware timestamps
    test_data = {
        "entry_time": [
            "2024-01-15T12:30:45Z",  # January
            "2024-01-20T14:30:45Z",  # January
            "2024-02-10T10:30:45Z",  # February
            "2024-02-25T16:30:45Z",  # February
            "2024-03-05T09:30:45Z",  # March
        ],
        "pnl_usdt": [1000.0, -500.0, 1500.0, -200.0, 800.0],
        "side": ["long", "short", "long", "short", "long"],
        "entry_price": [50000.0, 50000.0, 50000.0, 50000.0, 50000.0],
        "exit_price": [51000.0, 49500.0, 51500.0, 49800.0, 50800.0],
    }
    
    df = pd.DataFrame(test_data)
    
    # Test the monthly performance function
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        fig = figure_monthly_performance(df)
        
        # Check that no timezone-related warnings were raised
        timezone_warnings = [warning for warning in w 
                           if "timezone" in str(warning.message).lower() or 
                              "ambiguous" in str(warning.message).lower()]
        assert len(timezone_warnings) == 0, f"Timezone warnings were raised: {timezone_warnings}"
        
        # Verify the figure was created successfully
        assert fig is not None, "Figure should be created"
        assert len(fig.data) == 1, "Should have one bar trace"
        
        # Get the data from the figure
        bar_data = fig.data[0]
        x_values = bar_data.x
        y_values = bar_data.y
        
        # Verify monthly grouping
        expected_months = ["2024-01", "2024-02", "2024-03"]
        assert list(x_values) == expected_months, f"Expected months {expected_months}, got {list(x_values)}"
        
        # Verify PnL values (January: 500, February: 1300, March: 800)
        expected_pnl = [500.0, 1300.0, 800.0]
        assert list(y_values) == expected_pnl, f"Expected PnL {expected_pnl}, got {list(y_values)}"
        
        print("Monthly grouping timezone test passed")


def test_timezone_conversion_preservation():
    """Test that timezone conversion preserves the correct grouping."""
    print("\nTesting timezone conversion preservation...")
    
    # Create data with different timezones
    test_data = {
        "entry_time": [
            "2024-01-15T12:30:45Z",  # UTC
            "2024-01-15T12:30:45+00:00",  # UTC with offset
            "2024-01-15T09:30:45-03:00",  # Argentina time (same as UTC)
            "2024-02-10T18:30:45Z",  # UTC
            "2024-02-10T15:30:45-03:00",  # Argentina time (same as UTC)
        ],
        "pnl_usdt": [1000.0, 500.0, 300.0, 800.0, 200.0],
        "side": ["long", "short", "long", "long", "short"],
        "entry_price": [50000.0, 50000.0, 50000.0, 50000.0, 50000.0],
        "exit_price": [51000.0, 49500.0, 50300.0, 50800.0, 49800.0],
    }
    
    df = pd.DataFrame(test_data)
    
    # Test timezone conversion
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Convert to Argentina timezone
        df["entry_time"] = df["entry_time"].apply(lambda x: to_argentina_time(x))
        
        # Convert to naive for monthly grouping
        df["entry_time"] = df["entry_time"].dt.tz_localize(None)
        
        # Group by month
        df["month"] = df["entry_time"].dt.to_period("M").astype(str)
        monthly = df.groupby("month")["pnl_usdt"].sum()
        
        # Verify grouping
        expected_months = ["2024-01", "2024-02"]
        assert list(monthly.index) == expected_months, f"Expected months {expected_months}, got {list(monthly.index)}"
        
        # January: 1000 + 500 + 300 = 1800, February: 800 + 200 = 1000
        expected_totals = [1800.0, 1000.0]
        assert list(monthly.values) == expected_totals, f"Expected totals {expected_totals}, got {list(monthly.values)}"
        
        # Check that no warnings were raised
        timezone_warnings = [warning for warning in w 
                           if "timezone" in str(warning.message).lower()]
        assert len(timezone_warnings) == 0, f"Timezone warnings were raised: {timezone_warnings}"
        
        print("Timezone conversion preservation test passed")


def test_edge_case_timezone_handling():
    """Test edge cases in timezone handling."""
    print("\nTesting edge case timezone handling...")
    
    # Create data with edge cases
    test_data = {
        "entry_time": [
            "2024-01-01T00:00:00Z",  # New Year UTC
            "2024-01-01T00:00:00-03:00",  # New Year Argentina
            "2024-12-31T23:59:59Z",  # End of year UTC
            "2024-12-31T23:59:59-03:00",  # End of year Argentina
        ],
        "pnl_usdt": [100.0, 200.0, 300.0, 400.0],
        "side": ["long", "short", "long", "short"],
        "entry_price": [50000.0, 50000.0, 50000.0, 50000.0],
        "exit_price": [50100.0, 49800.0, 50300.0, 49600.0],
    }
    
    df = pd.DataFrame(test_data)
    
    # Test the function
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        fig = figure_monthly_performance(df)
        
        # Should not raise any warnings
        assert len(w) == 0, f"Warnings were raised: {[str(warning.message) for warning in w]}"
        
        # Verify the figure
        assert fig is not None, "Figure should be created"
        
        # Get the data
        bar_data = fig.data[0]
        x_values = bar_data.x
        y_values = bar_data.y
        
        # Should have January and December
        expected_months = ["2024-01", "2024-12"]
        assert list(x_values) == expected_months, f"Expected months {expected_months}, got {list(x_values)}"
        
        # January: 100 + 200 = 300, December: 300 + 400 = 700
        expected_pnl = [300.0, 700.0]
        assert list(y_values) == expected_pnl, f"Expected PnL {expected_pnl}, got {list(y_values)}"
        
        print("Edge case timezone handling test passed")


def main():
    """Run all monthly timezone tests."""
    print("Starting monthly timezone tests...")
    print("=" * 50)
    
    try:
        test_monthly_grouping_timezone()
        test_timezone_conversion_preservation()
        test_edge_case_timezone_handling()
        
        print("\n" + "=" * 50)
        print("All monthly timezone tests passed!")
        print("\nSummary:")
        print("[OK] Monthly grouping works correctly with timezone-aware dates")
        print("[OK] Timezone conversion preserves correct grouping")
        print("[OK] Edge cases handled without warnings")
        print("[OK] No FutureWarning or timezone warnings raised")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
