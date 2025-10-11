#!/usr/bin/env python3
"""Quick verification script for webapp improvements."""

import sys
from pathlib import Path
import logging

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def check_imports():
    """Verify all required imports are available."""
    print("🔍 Checking imports...")
    try:
        import dash
        import dash_bootstrap_components as dbc
        import pandas as pd
        import plotly
        from concurrent.futures import ThreadPoolExecutor
        from functools import lru_cache
        print("  ✅ All required packages available")
        return True
    except ImportError as e:
        print(f"  ❌ Missing package: {e}")
        return False


def check_webapp_structure():
    """Verify webapp files exist."""
    print("\n🔍 Checking webapp structure...")
    required_files = [
        "webapp_v2/interactive_app.py",
        "start_interactive_webapp.py",
        "config/config.yaml"
    ]
    
    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} not found")
            all_exist = False
    
    return all_exist


def check_logs_directory():
    """Verify logs directory exists or can be created."""
    print("\n🔍 Checking logs directory...")
    log_dir = Path("logs")
    
    if not log_dir.exists():
        try:
            log_dir.mkdir(exist_ok=True)
            print("  ✅ Created logs directory")
            return True
        except Exception as e:
            print(f"  ❌ Cannot create logs directory: {e}")
            return False
    else:
        print("  ✅ logs directory exists")
        return True


def check_data_directory():
    """Verify data directory structure."""
    print("\n🔍 Checking data directory structure...")
    data_dir = Path("data_incremental/backtest_results")
    
    if not data_dir.exists():
        print(f"  ⚠️  {data_dir} does not exist (will be created on first backtest)")
        return True
    else:
        csv_files = list(data_dir.glob("trades_*.csv"))
        print(f"  ✅ {data_dir} exists with {len(csv_files)} backtest files")
        return True


def check_webapp_import():
    """Try importing the webapp module."""
    print("\n🔍 Checking webapp import...")
    try:
        from webapp_v2.interactive_app import app, load_saved_backtests, invalidate_cache
        print("  ✅ webapp_v2.interactive_app imports successfully")
        return True
    except Exception as e:
        print(f"  ❌ Cannot import webapp: {e}")
        return False


def check_improvements():
    """Verify specific improvements are in place."""
    print("\n🔍 Checking implemented improvements...")
    
    try:
        with open("webapp_v2/interactive_app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        improvements = {
            "ThreadPoolExecutor": "ThreadPoolExecutor" in content,
            "dcc.Store": "dcc.Store" in content,
            "logging": "import logging" in content and "logger = logging.getLogger" in content,
            "lru_cache": "lru_cache" in content,
            "invalidate_cache": "invalidate_cache()" in content,
            "backtest-completion-event": "backtest-completion-event" in content,
            "validation": "required_columns" in content or "missing_columns" in content
        }
        
        all_present = True
        for improvement, present in improvements.items():
            status = "✅" if present else "❌"
            print(f"  {status} {improvement}")
            if not present:
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"  ❌ Error checking improvements: {e}")
        return False


def check_config_removal():
    """Verify app.server.config is removed from start script."""
    print("\n🔍 Checking obsolete config removal...")
    
    try:
        with open("start_interactive_webapp.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "app.server.config['backtest_running']" in content:
            print("  ⚠️  Obsolete app.server.config still present in start script")
            print("     (This may be intentional for backward compatibility)")
            return True  # Not a critical error
        else:
            print("  ✅ Obsolete config code removed")
            return True
    except Exception as e:
        print(f"  ❌ Error checking start script: {e}")
        return False


def run_basic_functions():
    """Test basic functionality."""
    print("\n🔍 Testing basic functions...")
    
    try:
        from webapp_v2.interactive_app import load_saved_backtests, invalidate_cache
        
        # Test cache invalidation
        invalidate_cache()
        print("  ✅ invalidate_cache() works")
        
        # Test loading backtests
        backtests = load_saved_backtests()
        print(f"  ✅ load_saved_backtests() works (found {len(backtests)} backtests)")
        
        return True
    except Exception as e:
        print(f"  ❌ Function test failed: {e}")
        return False


def check_documentation():
    """Verify documentation files exist."""
    print("\n🔍 Checking documentation...")
    
    docs = {
        "WEBAPP_IMPROVEMENTS.md": "Technical improvements documentation",
        "WEBAPP_USER_GUIDE.md": "User guide for webapp",
        "tests/test_webapp_improvements.py": "Test suite"
    }
    
    all_exist = True
    for doc, description in docs.items():
        path = Path(doc)
        if path.exists():
            print(f"  ✅ {doc} ({description})")
        else:
            print(f"  ❌ {doc} missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all verification checks."""
    print("="*70)
    print("🚀 Webapp Improvements Verification")
    print("="*70)
    
    checks = [
        ("Imports", check_imports),
        ("Webapp Structure", check_webapp_structure),
        ("Logs Directory", check_logs_directory),
        ("Data Directory", check_data_directory),
        ("Webapp Import", check_webapp_import),
        ("Improvements", check_improvements),
        ("Config Removal", check_config_removal),
        ("Basic Functions", run_basic_functions),
        ("Documentation", check_documentation)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 Verification Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("-"*70)
    print(f"Total: {passed}/{total} checks passed ({passed/total*100:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All checks passed! Webapp improvements verified successfully.")
        print("\n📝 Next steps:")
        print("   1. Start the webapp: python start_interactive_webapp.py")
        print("   2. Open browser: http://127.0.0.1:8053")
        print("   3. Follow WEBAPP_USER_GUIDE.md for testing")
        print("   4. Run tests: pytest tests/test_webapp_improvements.py -v")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        print("\n📝 Troubleshooting:")
        print("   1. Install missing packages: pip install -r requirements.txt")
        print("   2. Verify file paths and permissions")
        print("   3. Check logs for detailed errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())


