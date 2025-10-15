"""Verify One Trade v2.0 installation and setup."""
import sys
from pathlib import Path


def check_directory_structure():
    """Check if all required directories exist."""
    print("Checking directory structure...")
    required_dirs = ["config", "one_trade", "cli", "tests", "data_incremental", "logs", "data_incremental/backtest_results"]
    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)
            print(f"  ✗ {dir_path}")
        else:
            print(f"  ✓ {dir_path}")
    return len(missing) == 0


def check_config_files():
    """Check if configuration files exist."""
    print("\nChecking configuration files...")
    required_files = ["config/config.yaml", "config/models.py", "config/__init__.py"]
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"  ✗ {file_path}")
        else:
            print(f"  ✓ {file_path}")
    return len(missing) == 0


def check_core_modules():
    """Check if core modules exist."""
    print("\nChecking core modules...")
    required_modules = ["one_trade/__init__.py", "one_trade/data_store.py", "one_trade/data_fetch.py", "one_trade/strategy.py", "one_trade/scheduler.py", "one_trade/broker_sim.py", "one_trade/metrics.py", "one_trade/backtest.py", "one_trade/logging_config.py"]
    missing = []
    for file_path in required_modules:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"  ✗ {file_path}")
        else:
            print(f"  ✓ {file_path}")
    return len(missing) == 0


def check_cli():
    """Check if CLI exists."""
    print("\nChecking CLI...")
    required_files = ["cli/__init__.py", "cli/main.py"]
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"  ✗ {file_path}")
        else:
            print(f"  ✓ {file_path}")
    return len(missing) == 0


def check_tests():
    """Check if tests exist."""
    print("\nChecking tests...")
    test_files = ["tests/__init__.py", "tests/test_data_store.py", "tests/test_scheduler.py", "tests/test_broker.py", "tests/test_strategy.py", "tests/test_metrics.py", "tests/test_backtest_e2e.py"]
    missing = []
    for file_path in test_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"  ✗ {file_path}")
        else:
            print(f"  ✓ {file_path}")
    return len(missing) == 0


def check_docs():
    """Check if documentation exists."""
    print("\nChecking documentation...")
    doc_files = ["README_V2.md", "QUICKSTART.md", "IMPLEMENTATION_V2_SUMMARY.md", "requirements.txt", "pytest.ini", ".gitignore"]
    missing = []
    for file_path in doc_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f"  ✗ {file_path}")
        else:
            print(f"  ✓ {file_path}")
    return len(missing) == 0


def check_imports():
    """Try importing core modules."""
    print("\nChecking Python imports...")
    imports_to_test = [("yaml", "PyYAML"), ("pandas", "pandas"), ("ccxt", "ccxt"), ("pydantic", "pydantic"), ("click", "click"), ("rich", "rich"), ("pytest", "pytest")]
    missing = []
    for module_name, package_name in imports_to_test:
        try:
            __import__(module_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"  ✗ {package_name} (not installed)")
    return len(missing) == 0


def print_summary(all_checks_passed):
    """Print summary of verification."""
    print("\n" + "="*60)
    if all_checks_passed:
        print("✅ All checks passed! Installation is complete.")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Validate config: python -m cli.main validate")
        print("  3. Read QUICKSTART.md for your first backtest")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("  - Missing directories: Run the script again")
        print("  - Missing imports: Run 'pip install -r requirements.txt'")
        print("  - Missing files: Contact support or check repository")
    print("="*60)


def main():
    """Run all verification checks."""
    print("="*60)
    print("One Trade v2.0 - Installation Verification")
    print("="*60 + "\n")
    checks = [check_directory_structure(), check_config_files(), check_core_modules(), check_cli(), check_tests(), check_docs(), check_imports()]
    all_passed = all(checks)
    print_summary(all_passed)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())









