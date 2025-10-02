#!/usr/bin/env python3
"""
Test timezone localization to Argentina time.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

# Import the timezone functions
from app import to_argentina_time, format_argentina_time, ARGENTINA_TZ


def test_timezone_conversion():
    """Test timezone conversion to Argentina time."""
    print("Testing timezone conversion to Argentina time...")
    
    # Test UTC to Argentina conversion
    utc_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    arg_time = to_argentina_time(utc_time)
    
    print(f"UTC time: {utc_time}")
    print(f"Argentina time: {arg_time}")
    
    # Argentina is UTC-3, so 12:00 UTC should be 09:00 Argentina
    assert arg_time.hour == 9, f"Expected 9 AM Argentina time, got {arg_time.hour}"
    assert arg_time.day == 15, f"Expected same day, got {arg_time.day}"
    
    # Test string input
    str_time = "2024-01-15 12:00:00"
    arg_time_from_str = to_argentina_time(str_time)
    assert arg_time_from_str.hour == 9, f"Expected 9 AM from string, got {arg_time_from_str.hour}"
    
    print("Timezone conversion test passed")


def test_timezone_formatting():
    """Test timezone formatting."""
    print("\nTesting timezone formatting...")
    
    utc_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    
    # Test different format strings
    formatted = format_argentina_time(utc_time, "%H:%M:%S %Z")
    print(f"Formatted time: {formatted}")
    assert "09:00:00" in formatted, f"Expected 09:00:00 in formatted time, got {formatted}"
    
    formatted_full = format_argentina_time(utc_time, "%Y-%m-%d %H:%M:%S %Z")
    print(f"Formatted full: {formatted_full}")
    assert "2024-01-15 09:00:00" in formatted_full, f"Expected 2024-01-15 09:00:00 in formatted time, got {formatted_full}"
    
    # Test None input
    formatted_none = format_argentina_time(None)
    assert formatted_none == "", f"Expected empty string for None, got {formatted_none}"
    
    print("Timezone formatting test passed")


def test_edge_cases():
    """Test edge cases for timezone conversion."""
    print("\nTesting edge cases...")
    
    # Test naive datetime (should assume UTC)
    naive_time = datetime(2024, 1, 15, 12, 0, 0)
    arg_time = to_argentina_time(naive_time)
    assert arg_time.hour == 9, f"Expected 9 AM for naive datetime, got {arg_time.hour}"
    
    # Test None input
    arg_time_none = to_argentina_time(None)
    assert arg_time_none is None, f"Expected None for None input, got {arg_time_none}"
    
    print("Edge cases test passed")


def main():
    """Run all timezone tests."""
    print("Starting timezone localization tests...")
    print("=" * 50)
    
    try:
        test_timezone_conversion()
        test_timezone_formatting()
        test_edge_cases()
        
        print("\n" + "=" * 50)
        print("All timezone localization tests passed!")
        print("\nSummary:")
        print("- UTC to Argentina timezone conversion works correctly")
        print("- Timezone formatting produces expected output")
        print("- Edge cases (None, naive datetime) are handled properly")
        print("- Argentina timezone is UTC-3 as expected")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
