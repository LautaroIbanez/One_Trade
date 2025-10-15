#!/usr/bin/env python3
"""Diagnostic script for backtest synchronization issues."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def check_logs_for_backtest():
    """Check logs for backtest execution patterns."""
    print("🔍 Analyzing backtest logs...")
    
    try:
        log_file = Path("logs/webapp.log")
        if not log_file.exists():
            print("  ❌ Log file not found")
            return False
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find recent backtest events
        backtest_events = []
        for i, line in enumerate(lines):
            if "Backtest button clicked" in line:
                timestamp = line.split(' - ')[0]
                backtest_events.append(('clicked', timestamp, line.strip()))
            elif "Backtest completed successfully" in line:
                timestamp = line.split(' - ')[0]
                backtest_events.append(('completed', timestamp, line.strip()))
            elif "Dashboard refreshed" in line:
                timestamp = line.split(' - ')[0]
                backtest_events.append(('dashboard', timestamp, line.strip()))
        
        print(f"  📊 Found {len(backtest_events)} backtest-related events")
        
        # Analyze patterns
        recent_events = backtest_events[-10:]  # Last 10 events
        print("\n  📋 Recent events:")
        for event_type, timestamp, line in recent_events:
            icon = "🖱️" if event_type == "clicked" else "✅" if event_type == "completed" else "🔄"
            print(f"    {icon} {timestamp} - {event_type}")
        
        # Check for completion without dashboard refresh
        clicked_events = [e for e in backtest_events if e[0] == 'clicked']
        completed_events = [e for e in backtest_events if e[0] == 'completed']
        dashboard_events = [e for e in backtest_events if e[0] == 'dashboard']
        
        print(f"\n  📈 Statistics:")
        print(f"    Backtests clicked: {len(clicked_events)}")
        print(f"    Backtests completed: {len(completed_events)}")
        print(f"    Dashboard refreshes: {len(dashboard_events)}")
        
        if len(completed_events) > len(dashboard_events):
            print("  ⚠️  More backtests completed than dashboard refreshes - sync issue detected!")
            return False
        else:
            print("  ✅ Backtest completion and dashboard refresh counts match")
            return True
            
    except Exception as e:
        print(f"  ❌ Error analyzing logs: {e}")
        return False

def check_threading_imports():
    """Check if threading imports are correct."""
    print("\n🔍 Checking threading imports...")
    
    try:
        import threading
        from concurrent.futures import ThreadPoolExecutor
        
        print("  ✅ Threading modules imported successfully")
        
        # Test thread-safe dict creation
        test_dict = {}
        lock = threading.Lock()
        
        with lock:
            test_dict['test'] = 'value'
        
        print("  ✅ Thread-safe operations work correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Threading import/operation error: {e}")
        return False

def check_webapp_state():
    """Check webapp state management."""
    print("\n🔍 Checking webapp state management...")
    
    try:
        from webapp_v2.interactive_app import _backtest_futures, _data_futures, _futures_lock
        
        print("  ✅ Global futures dictionaries exist")
        print(f"    Active backtest futures: {len(_backtest_futures)}")
        print(f"    Active data futures: {len(_data_futures)}")
        
        # Test lock
        with _futures_lock:
            print("  ✅ Futures lock works correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Webapp state error: {e}")
        return False

def suggest_fixes():
    """Suggest potential fixes."""
    print("\n💡 Suggested fixes:")
    
    print("  1. 🔄 Restart the webapp to apply threading fixes:")
    print("     - Stop current server (Ctrl+C)")
    print("     - python start_interactive_webapp.py")
    
    print("\n  2. 🧪 Test with a very short period:")
    print("     - Use 2025-10-09 to 2025-10-09 (same day)")
    print("     - Should complete in <5 seconds")
    
    print("\n  3. 📊 Monitor logs in real-time:")
    print("     - Get-Content logs/webapp.log -Tail 10 -Wait")
    print("     - Look for 'Backtest future completed' messages")
    
    print("\n  4. 🔍 Check browser console:")
    print("     - F12 -> Console tab")
    print("     - Look for JavaScript errors")
    
    print("\n  5. 🗑️ Clear browser cache:")
    print("     - Hard refresh (Ctrl+F5)")
    print("     - Or open in incognito mode")

def main():
    """Run all diagnostic checks."""
    print("="*60)
    print("🔧 Backtest Synchronization Diagnostic")
    print("="*60)
    
    checks = [
        ("Log Analysis", check_logs_for_backtest),
        ("Threading Imports", check_threading_imports),
        ("Webapp State", check_webapp_state)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Diagnostic Results")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("-"*60)
    print(f"Total: {passed}/{total} checks passed ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed < total:
        print("\n⚠️  Issues detected. See suggestions below.")
        suggest_fixes()
        return 1
    else:
        print("\n🎉 All checks passed! The issue might be resolved with a restart.")
        suggest_fixes()
        return 0

if __name__ == "__main__":
    sys.exit(main())







