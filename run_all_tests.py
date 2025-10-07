#!/usr/bin/env python3
"""
Script para ejecutar todos los tests de One Trade en secuencia.

Ejecuta:
1. Tests de validación OHLC
2. Tests de backtest de 1 año
3. Tests de métricas parametrizadas
4. Tests de integración de inversión de estrategia

Uso:
    python run_all_tests.py
"""

import subprocess
import sys
from pathlib import Path

# Test files to run
TEST_FILES = [
    "btc_1tpd_backtester/tests/test_ohlc_validation.py",
    "btc_1tpd_backtester/tests/test_one_year_backtest.py",
    "webapp/test_metrics_parametrized.py",
    "webapp/test_strategy_inversion_integration.py",
]

def run_test_file(test_file: str) -> bool:
    """
    Run a single test file and return True if successful.
    
    Args:
        test_file: Path to test file
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    print(f"\n{'=' * 80}")
    print(f"Running: {test_file}")
    print('=' * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ {test_file} PASSED")
            return True
        else:
            print(f"❌ {test_file} FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {test_file} ERROR: {e}")
        return False


def main():
    """Run all tests and report results."""
    print("\n" + "=" * 80)
    print("ONE TRADE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    results = {}
    total_tests = len(TEST_FILES)
    passed_tests = 0
    
    # Run each test file
    for test_file in TEST_FILES:
        if not Path(test_file).exists():
            print(f"\n⚠️  Warning: {test_file} not found, skipping...")
            results[test_file] = "SKIPPED"
            continue
        
        success = run_test_file(test_file)
        results[test_file] = "PASSED" if success else "FAILED"
        
        if success:
            passed_tests += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_file, status in results.items():
        icon = "✅" if status == "PASSED" else "⚠️" if status == "SKIPPED" else "❌"
        print(f"{icon} {test_file}: {status}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {passed_tests}/{total_tests} test files passed")
    print("=" * 80)
    
    # Exit with appropriate code
    if passed_tests == total_tests:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Some tests failed: {total_tests - passed_tests} failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

