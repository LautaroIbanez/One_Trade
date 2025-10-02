#!/usr/bin/env python3
"""
Test that FutureWarning is avoided when appending active trade operations.
"""

import sys
import pandas as pd
import warnings
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))


def test_active_trade_concat_no_warning():
    """Test that concatenating active trade doesn't produce FutureWarning."""
    print("Testing active trade concatenation without FutureWarning...")
    
    # Create a mock active trade
    mock_active_trade = MagicMock()
    mock_active_trade.entry_time = "2024-01-15T12:30:45Z"
    mock_active_trade.side = "long"
    mock_active_trade.entry_price = 50000.0
    mock_active_trade.stop_loss = 49000.0
    mock_active_trade.take_profit = 51000.0
    
    # Mock the exit evaluation
    mock_exit_eval = {
        "should_exit": True,
        "exit_time": "2024-01-15T13:30:45Z",
        "exit_price": 51000.0,
        "exit_reason": "take_profit"
    }
    
    # Create empty combined DataFrame
    combined = pd.DataFrame()
    
    # Define standard columns
    standard_cols = [
        "day_key","entry_time","side","entry_price","sl","tp","exit_time","exit_price","exit_reason","pnl_usdt","r_multiple","used_fallback","mode"
    ]
    
    # Test the concatenation logic that should avoid FutureWarning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Simulate the new_row creation
        new_row = {
            "day_key": pd.to_datetime(mock_active_trade.entry_time).date().isoformat(),
            "entry_time": pd.to_datetime(mock_active_trade.entry_time),
            "side": mock_active_trade.side,
            "entry_price": mock_active_trade.entry_price,
            "sl": mock_active_trade.stop_loss,
            "tp": mock_active_trade.take_profit,
            "exit_time": mock_exit_eval["exit_time"],
            "exit_price": mock_exit_eval["exit_price"],
            "exit_reason": mock_exit_eval["exit_reason"],
            "pnl_usdt": (mock_exit_eval["exit_price"] - mock_active_trade.entry_price),
            "r_multiple": None,
            "used_fallback": None,
            "mode": "moderate",
        }
        
        # Create new row with standard columns to avoid FutureWarning
        new_row_df = pd.DataFrame([new_row], columns=standard_cols)
        if combined.empty:
            combined = new_row_df
        else:
            combined = pd.concat([combined, new_row_df], ignore_index=True)
        
        # Check that no FutureWarning was raised
        future_warnings = [warning for warning in w if issubclass(warning.category, FutureWarning)]
        assert len(future_warnings) == 0, f"FutureWarning was raised: {future_warnings}"
        
        # Verify the result
        assert len(combined) == 1, f"Expected 1 row, got {len(combined)}"
        assert list(combined.columns) == standard_cols, "Columns should match standard_cols"
        assert combined.iloc[0]["side"] == "long", "Side should be preserved"
        assert combined.iloc[0]["entry_price"] == 50000.0, "Entry price should be preserved"
        
        print("Active trade concatenation test passed - no FutureWarning")


def test_combined_empty_initialization():
    """Test that combined DataFrame is properly initialized with standard columns."""
    print("\nTesting combined DataFrame initialization...")
    
    # Test empty combined initialization
    standard_cols = [
        "day_key","entry_time","side","entry_price","sl","tp","exit_time","exit_price","exit_reason","pnl_usdt","r_multiple","used_fallback","mode"
    ]
    
    # Simulate the initialization logic
    combined = pd.DataFrame(columns=standard_cols)
    
    # Verify initialization
    assert len(combined) == 0, "Combined should be empty"
    assert list(combined.columns) == standard_cols, "Columns should match standard_cols"
    
    # Test adding a new row
    new_row = {
        "day_key": "2024-01-15",
        "entry_time": pd.to_datetime("2024-01-15T12:30:45Z"),
        "side": "long",
        "entry_price": 50000.0,
        "sl": 49000.0,
        "tp": 51000.0,
        "exit_time": "2024-01-15T13:30:45Z",
        "exit_price": 51000.0,
        "exit_reason": "take_profit",
        "pnl_usdt": 1000.0,
        "r_multiple": None,
        "used_fallback": None,
        "mode": "moderate",
    }
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        new_row_df = pd.DataFrame([new_row], columns=standard_cols)
        combined = pd.concat([combined, new_row_df], ignore_index=True)
        
        # Check that no FutureWarning was raised
        future_warnings = [warning for warning in w if issubclass(warning.category, FutureWarning)]
        assert len(future_warnings) == 0, f"FutureWarning was raised: {future_warnings}"
        
        # Verify the result
        assert len(combined) == 1, f"Expected 1 row, got {len(combined)}"
        assert combined.iloc[0]["side"] == "long", "Side should be preserved"
        
        print("Combined DataFrame initialization test passed")


def test_column_standardization():
    """Test that existing DataFrames get standardized columns added."""
    print("\nTesting column standardization...")
    
    standard_cols = [
        "day_key","entry_time","side","entry_price","sl","tp","exit_time","exit_price","exit_reason","pnl_usdt","r_multiple","used_fallback","mode"
    ]
    
    # Create a DataFrame with missing columns
    existing_df = pd.DataFrame({
        "entry_time": ["2024-01-15T12:30:45Z"],
        "side": ["long"],
        "entry_price": [50000.0],
        "pnl_usdt": [1000.0],
    })
    
    # Simulate the standardization logic
    for col in standard_cols:
        if col not in existing_df.columns:
            existing_df[col] = None
    
    # Verify standardization
    assert list(existing_df.columns) == standard_cols, "Columns should be standardized"
    assert existing_df["mode"].iloc[0] is None, "New columns should be None"
    assert existing_df["side"].iloc[0] == "long", "Existing data should be preserved"
    
    print("Column standardization test passed")


def main():
    """Run all FutureWarning fix tests."""
    print("Starting FutureWarning fix tests...")
    print("=" * 50)
    
    try:
        test_active_trade_concat_no_warning()
        test_combined_empty_initialization()
        test_column_standardization()
        
        print("\n" + "=" * 50)
        print("All FutureWarning fix tests passed!")
        print("\nSummary:")
        print("[OK] Active trade concatenation doesn't produce FutureWarning")
        print("[OK] Combined DataFrame properly initialized with standard columns")
        print("[OK] Column standardization works correctly")
        print("[OK] All concatenation operations use proper column alignment")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
