"""Simple test script for annual candle analysis enhancements. Tests date-range helper and candle analysis tasks builder without requiring pytest."""
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
sys.path.insert(0, str(Path(__file__).parent))
from app import determine_price_date_range, build_candle_analysis_tasks


def test_determine_price_date_range():
    """Test the date range helper function."""
    print("\n=== Testing determine_price_date_range ===")
    symbol = "BTC/USDT:USDT"
    passed = 0
    total = 0
    total += 1
    print(f"\nTest 1: No since_date returns 365 days")
    start_date, end_date = determine_price_date_range(symbol, since_date=None, lookback_days=365)
    days_diff = (end_date.date() - start_date.date()).days
    if days_diff == 365 and start_date.tzinfo == timezone.utc and end_date.tzinfo == timezone.utc:
        print(f"  ✓ PASSED: Got {days_diff} days with UTC timezone")
        passed += 1
    else:
        print(f"  ✗ FAILED: Expected 365 days with UTC, got {days_diff} days")
    total += 1
    print(f"\nTest 2: Short since_date expanded to 365 days")
    recent_date = (datetime.now(timezone.utc) - timedelta(days=100)).date().isoformat()
    start_date, end_date = determine_price_date_range(symbol, since_date=recent_date, lookback_days=365)
    days_diff = (end_date.date() - start_date.date()).days
    if days_diff >= 365:
        print(f"  ✓ PASSED: Got {days_diff} days (expanded from 100)")
        passed += 1
    else:
        print(f"  ✗ FAILED: Expected >= 365 days, got {days_diff}")
    total += 1
    print(f"\nTest 3: Valid since_date preserved")
    old_date = (datetime.now(timezone.utc) - timedelta(days=500)).date().isoformat()
    start_date, end_date = determine_price_date_range(symbol, since_date=old_date, lookback_days=365)
    days_diff = (end_date.date() - start_date.date()).days
    if days_diff >= 365 and start_date.date().isoformat() == old_date:
        print(f"  ✓ PASSED: Preserved {old_date}, got {days_diff} days")
        passed += 1
    else:
        print(f"  ✗ FAILED: Expected to preserve {old_date}")
    total += 1
    print(f"\nTest 4: Invalid since_date falls back to lookback")
    start_date, end_date = determine_price_date_range(symbol, since_date="invalid-date", lookback_days=365)
    days_diff = (end_date.date() - start_date.date()).days
    if days_diff == 365:
        print(f"  ✓ PASSED: Fallback to 365 days on invalid date")
        passed += 1
    else:
        print(f"  ✗ FAILED: Expected 365 days fallback, got {days_diff}")
    total += 1
    print(f"\nTest 5: Custom lookback_days works")
    start_date, end_date = determine_price_date_range(symbol, since_date=None, lookback_days=730)
    days_diff = (end_date.date() - start_date.date()).days
    if days_diff == 730:
        print(f"  ✓ PASSED: Custom lookback of 730 days")
        passed += 1
    else:
        print(f"  ✗ FAILED: Expected 730 days, got {days_diff}")
    print(f"\nDate Range Tests: {passed}/{total} passed")
    return passed, total


def test_build_candle_analysis_tasks():
    """Test the candle analysis tasks builder."""
    print("\n\n=== Testing build_candle_analysis_tasks ===")
    passed = 0
    total = 0
    modes = ["conservative", "moderate", "aggressive"]
    total += len(modes)
    print(f"\nTest 1: All modes return tasks")
    for mode in modes:
        tasks = build_candle_analysis_tasks(mode, inverted=False)
        if isinstance(tasks, list) and len(tasks) > 0:
            print(f"  ✓ PASSED: {mode} returned {len(tasks)} tasks")
            passed += 1
        else:
            print(f"  ✗ FAILED: {mode} did not return valid tasks")
    total += 1
    print(f"\nTest 2: Task structure validation")
    tasks = build_candle_analysis_tasks("moderate", inverted=False)
    valid_structure = True
    for task in tasks:
        if not all(key in task for key in ["title", "description", "priority"]):
            valid_structure = False
            break
        if not isinstance(task["title"], str) or not isinstance(task["description"], str) or not isinstance(task["priority"], int):
            valid_structure = False
            break
    if valid_structure:
        print(f"  ✓ PASSED: All tasks have valid structure (title, description, priority)")
        passed += 1
    else:
        print(f"  ✗ FAILED: Some tasks have invalid structure")
    total += 1
    print(f"\nTest 3: Priority scale validation (1-3)")
    valid_priorities = True
    for mode in modes:
        tasks = build_candle_analysis_tasks(mode, inverted=False)
        for task in tasks:
            if not (1 <= task["priority"] <= 3):
                valid_priorities = False
                print(f"  ✗ Priority {task['priority']} out of range in {mode}")
                break
    if valid_priorities:
        print(f"  ✓ PASSED: All priorities within range 1-3")
        passed += 1
    else:
        print(f"  ✗ FAILED: Some priorities out of range")
    total += 1
    print(f"\nTest 4: Inversion flag changes descriptions")
    tasks_normal = build_candle_analysis_tasks("moderate", inverted=False)
    tasks_inverted = build_candle_analysis_tasks("moderate", inverted=True)
    inversion_detected = False
    for normal, inverted in zip(tasks_normal, tasks_inverted):
        if "invertida" in inverted["description"] and "invertida" not in normal["description"]:
            inversion_detected = True
            break
    if inversion_detected and len(tasks_normal) == len(tasks_inverted):
        print(f"  ✓ PASSED: Inversion flag adds inversion notes")
        passed += 1
    else:
        print(f"  ✗ FAILED: Inversion flag did not work as expected")
    total += 1
    print(f"\nTest 5: Base tasks present in all modes")
    base_tasks_present = True
    for mode in modes:
        tasks = build_candle_analysis_tasks(mode, inverted=False)
        titles = [task["title"] for task in tasks]
        if not any("Validar cobertura" in title for title in titles):
            base_tasks_present = False
            print(f"  ✗ Missing coverage validation in {mode}")
        if not any("patrones de largo plazo" in title for title in titles):
            base_tasks_present = False
            print(f"  ✗ Missing long-term patterns in {mode}")
    if base_tasks_present:
        print(f"  ✓ PASSED: Base tasks present in all modes")
        passed += 1
    else:
        print(f"  ✗ FAILED: Some base tasks missing")
    total += 1
    print(f"\nTest 6: Mode-specific tasks")
    conservative_tasks = build_candle_analysis_tasks("conservative", inverted=False)
    moderate_tasks = build_candle_analysis_tasks("moderate", inverted=False)
    aggressive_tasks = build_candle_analysis_tasks("aggressive", inverted=False)
    conservative_ok = any("Bollinger" in str(task) or "RSI" in str(task) or "reversión" in str(task) for task in conservative_tasks)
    moderate_ok = any("EMA" in str(task) or "ADX" in str(task) or "tendencia" in str(task) for task in moderate_tasks)
    aggressive_ok = any("breakout" in str(task) or "volatilidad" in str(task) for task in aggressive_tasks)
    if conservative_ok and moderate_ok and aggressive_ok:
        print(f"  ✓ PASSED: Mode-specific tasks present")
        passed += 1
    else:
        print(f"  ✗ FAILED: Some mode-specific tasks missing")
    print(f"\nCandle Analysis Tasks Tests: {passed}/{total} passed")
    return passed, total


def main():
    """Run all tests and report results."""
    print("=" * 60)
    print("Annual Candle Analysis Enhancements - Test Suite")
    print("=" * 60)
    passed1, total1 = test_determine_price_date_range()
    passed2, total2 = test_build_candle_analysis_tasks()
    total_passed = passed1 + passed2
    total_tests = total1 + total2
    print("\n" + "=" * 60)
    print(f"OVERALL RESULTS: {total_passed}/{total_tests} tests passed")
    print("=" * 60)
    if total_passed == total_tests:
        print("✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"✗ {total_tests - total_passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

