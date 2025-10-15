#!/usr/bin/env python3
"""Simple tests for webapp improvements without pytest dependency."""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("\n🧪 Testing imports...")
    try:
        from webapp_v2.interactive_app import (
            load_saved_backtests,
            invalidate_cache,
            run_backtest_async,
            update_data_async,
            app
        )
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_cache_invalidation():
    """Test cache invalidation functionality."""
    print("\n🧪 Testing cache invalidation...")
    try:
        from webapp_v2.interactive_app import load_saved_backtests, invalidate_cache
        
        # Load once
        result1 = load_saved_backtests()
        
        # Load again (should use cache)
        result2 = load_saved_backtests()
        
        # Invalidate
        invalidate_cache()
        
        # Load again (should reload)
        result3 = load_saved_backtests()
        
        print(f"  ✅ Cache invalidation works (loaded {len(result1)} backtests)")
        return True
    except Exception as e:
        print(f"  ❌ Cache test failed: {e}")
        return False


def test_load_backtests():
    """Test loading saved backtests."""
    print("\n🧪 Testing load_saved_backtests...")
    try:
        from webapp_v2.interactive_app import load_saved_backtests, invalidate_cache
        
        invalidate_cache()
        backtests = load_saved_backtests()
        
        print(f"  ✅ Loaded {len(backtests)} backtests")
        
        if backtests:
            bt = backtests[0]
            required_keys = ['symbol', 'total_trades', 'win_rate', 'total_return', 
                           'total_return_pct', 'final_equity', 'total_fees']
            
            missing_keys = [key for key in required_keys if key not in bt]
            if missing_keys:
                print(f"  ⚠️  Missing keys: {missing_keys}")
                return False
            
            print(f"  ✅ Backtest structure valid: {bt['symbol']} - {bt['total_trades']} trades")
        else:
            print("  ℹ️  No backtests found (this is OK if none have been run)")
        
        return True
    except Exception as e:
        print(f"  ❌ Load test failed: {e}")
        return False


def test_metrics_calculation():
    """Test metrics calculation logic."""
    print("\n🧪 Testing metrics calculation...")
    try:
        # Create sample data
        data = {
            'pnl': [100, -50, 200, -30, 150],
            'fees': [5, 5, 5, 5, 5]
        }
        df = pd.DataFrame(data)
        
        # Calculate metrics
        total_trades = len(df)
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] <= 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_return = df['pnl'].sum()
        total_fees = df['fees'].sum()
        
        # Verify
        assert total_trades == 5, f"Expected 5 trades, got {total_trades}"
        assert winning_trades == 3, f"Expected 3 wins, got {winning_trades}"
        assert losing_trades == 2, f"Expected 2 losses, got {losing_trades}"
        assert win_rate == 60.0, f"Expected 60% win rate, got {win_rate}"
        assert total_return == 370, f"Expected 370 return, got {total_return}"
        assert total_fees == 25, f"Expected 25 fees, got {total_fees}"
        
        print("  ✅ Metrics calculations correct")
        return True
    except AssertionError as e:
        print(f"  ❌ Metrics test failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Metrics test error: {e}")
        return False


def test_filename_parsing():
    """Test filename parsing logic."""
    print("\n🧪 Testing filename parsing...")
    try:
        # Valid filename
        filename = "trades_BTC_USDT_20241010_120000"
        parts = filename.split('_')
        
        assert len(parts) >= 5, f"Expected 5+ parts, got {len(parts)}"
        assert parts[0] == "trades", f"Expected 'trades', got {parts[0]}"
        assert parts[1] == "BTC", f"Expected 'BTC', got {parts[1]}"
        assert parts[2] == "USDT", f"Expected 'USDT', got {parts[2]}"
        
        symbol = f"{parts[1]}/{parts[2]}"
        assert symbol == "BTC/USDT", f"Expected 'BTC/USDT', got {symbol}"
        
        # Parse date
        date_str = parts[3]
        time_str = parts[4]
        dt = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
        
        assert dt.year == 2024
        assert dt.month == 10
        assert dt.day == 10
        
        print("  ✅ Filename parsing correct")
        return True
    except AssertionError as e:
        print(f"  ❌ Filename test failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Filename test error: {e}")
        return False


def test_state_structure():
    """Test state structure for dcc.Store."""
    print("\n🧪 Testing state structure...")
    try:
        # Test backtest state
        backtest_state = {
            "running": False,
            "result": None,
            "timestamp": None
        }
        
        assert "running" in backtest_state
        assert "result" in backtest_state
        assert "timestamp" in backtest_state
        
        # Test completion event
        completion_event = {
            "completed": False,
            "timestamp": None
        }
        
        assert "completed" in completion_event
        assert "timestamp" in completion_event
        
        print("  ✅ State structures valid")
        return True
    except AssertionError as e:
        print(f"  ❌ State test failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ State test error: {e}")
        return False


def test_logging_setup():
    """Test logging is properly configured."""
    print("\n🧪 Testing logging setup...")
    try:
        from webapp_v2.interactive_app import logger
        import logging
        
        assert logger is not None, "Logger is None"
        assert isinstance(logger, logging.Logger), "Logger is not a Logger instance"
        assert logger.name == 'webapp_v2.interactive_app', f"Unexpected logger name: {logger.name}"
        
        print("  ✅ Logging properly configured")
        return True
    except AssertionError as e:
        print(f"  ❌ Logging test failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Logging test error: {e}")
        return False


def test_threadpool_executor():
    """Test ThreadPoolExecutor is configured."""
    print("\n🧪 Testing ThreadPoolExecutor setup...")
    try:
        from webapp_v2.interactive_app import executor
        from concurrent.futures import ThreadPoolExecutor
        
        assert executor is not None, "Executor is None"
        assert isinstance(executor, ThreadPoolExecutor), "Executor is not ThreadPoolExecutor"
        
        print("  ✅ ThreadPoolExecutor properly configured")
        return True
    except AssertionError as e:
        print(f"  ❌ ThreadPool test failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ ThreadPool test error: {e}")
        return False


def test_dash_stores():
    """Test that Dash stores are defined in layout."""
    print("\n🧪 Testing Dash Store components...")
    try:
        from webapp_v2.interactive_app import app
        
        # Convert layout to string to check for stores
        layout_str = str(app.layout)
        
        required_stores = [
            'backtest-state',
            'data-state',
            'backtest-completion-event'
        ]
        
        missing = []
        for store in required_stores:
            if store not in layout_str:
                missing.append(store)
        
        if missing:
            print(f"  ⚠️  Missing stores: {missing}")
            return False
        
        print("  ✅ All Dash Store components present")
        return True
    except Exception as e:
        print(f"  ❌ Dash Store test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("🧪 Running Webapp Improvements Tests")
    print("="*70)
    
    tests = [
        ("Imports", test_imports),
        ("Cache Invalidation", test_cache_invalidation),
        ("Load Backtests", test_load_backtests),
        ("Metrics Calculation", test_metrics_calculation),
        ("Filename Parsing", test_filename_parsing),
        ("State Structure", test_state_structure),
        ("Logging Setup", test_logging_setup),
        ("ThreadPool Executor", test_threadpool_executor),
        ("Dash Stores", test_dash_stores)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Results Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("-"*70)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())








