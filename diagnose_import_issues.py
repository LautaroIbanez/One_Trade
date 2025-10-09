"""Diagnose import issues preventing backtest module from loading. Tests each import independently to isolate the failing component."""
import sys
from pathlib import Path

print("=" * 60)
print("IMPORT DIAGNOSTICS")
print("=" * 60)
print()

sys.path.insert(0, str(Path(__file__).parent))

results = {}

print("1. Testing basic imports...")
try:
    import pandas as pd
    print("  ✓ pandas OK")
    results['pandas'] = True
except Exception as e:
    print(f"  ✗ pandas FAILED: {e}")
    results['pandas'] = False

try:
    import numpy as np
    print(f"  ✓ numpy OK (version: {np.__version__})")
    results['numpy'] = True
except Exception as e:
    print(f"  ✗ numpy FAILED: {e}")
    results['numpy'] = False

print("\n2. Testing btc_1tpd_backtester imports...")

try:
    from btc_1tpd_backtester import utils
    print("  ✓ btc_1tpd_backtester.utils OK")
    results['utils'] = True
except Exception as e:
    print(f"  ✗ btc_1tpd_backtester.utils FAILED: {e}")
    results['utils'] = False

try:
    from btc_1tpd_backtester.utils import fetch_historical_data
    print("  ✓ fetch_historical_data OK")
    results['fetch_historical_data'] = True
except Exception as e:
    print(f"  ✗ fetch_historical_data FAILED: {e}")
    results['fetch_historical_data'] = False

try:
    from btc_1tpd_backtester.signals.today_signal import get_today_trade_recommendation
    print("  ✓ get_today_trade_recommendation OK")
    results['today_signal'] = True
except Exception as e:
    print(f"  ✗ get_today_trade_recommendation FAILED: {e}")
    results['today_signal'] = False

print("\n3. Testing problematic import (btc_1tpd_backtest_final)...")
try:
    from btc_1tpd_backtester.btc_1tpd_backtest_final import run_backtest
    print("  ✓ run_backtest OK")
    results['run_backtest'] = True
except Exception as e:
    print(f"  ✗ run_backtest FAILED: {e}")
    print(f"     Error type: {type(e).__name__}")
    print(f"     This is likely the matplotlib/NumPy 2.x incompatibility")
    results['run_backtest'] = False

print("\n4. Testing matplotlib directly...")
try:
    import matplotlib
    print(f"  ✓ matplotlib OK (version: {matplotlib.__version__})")
    results['matplotlib'] = True
except Exception as e:
    print(f"  ✗ matplotlib FAILED: {e}")
    results['matplotlib'] = False

try:
    import matplotlib.pyplot as plt
    print("  ✓ matplotlib.pyplot OK")
    results['matplotlib_pyplot'] = True
except Exception as e:
    print(f"  ✗ matplotlib.pyplot FAILED: {e}")
    print(f"     Error type: {type(e).__name__}")
    results['matplotlib_pyplot'] = False

print("\n5. Testing alternative backtest import...")
try:
    from btc_1tpd_backtester import backtester
    print("  ✓ backtester module OK")
    results['backtester'] = True
except Exception as e:
    print(f"  ✗ backtester FAILED: {e}")
    results['backtester'] = False

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

total = len(results)
passed = sum(1 for v in results.values() if v)
failed = total - passed

print(f"Tests passed: {passed}/{total}")
print(f"Tests failed: {failed}/{total}")

if not results.get('run_backtest', False):
    print("\n⚠️ CRITICAL: run_backtest cannot be imported")
    print("\nSOLUTION OPTIONS:")
    print("  1. Downgrade NumPy: pip install 'numpy<2'")
    print("  2. Upgrade matplotlib: pip install --upgrade matplotlib")
    print("  3. Use alternative backtest module (if available)")
    print("\nRECOMMENDED:")
    print("  pip install 'numpy<2'")

if failed == 0:
    print("\n✓ All imports working! Backtest should be functional.")
    sys.exit(0)
else:
    print(f"\n✗ {failed} import(s) failed. See details above.")
    sys.exit(1)


