"""Quick recovery script for historical trades data. Executes complete rebuild for symbols with insufficient coverage and validates results."""
import sys
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
MINIMUM_COVERAGE_DAYS = 365


def check_coverage_status():
    """Check current coverage status for all meta files."""
    logger.info("Checking coverage status for all symbols/modes...")
    meta_files = list(DATA_DIR.glob("*_meta.json"))
    issues = []
    for meta_file in meta_files:
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            symbol = meta.get('symbol', 'unknown')
            mode = meta.get('mode', 'unknown')
            actual_days = meta.get('actual_lookback_days', 0)
            total_trades = meta.get('total_trades', 0)
            if actual_days < MINIMUM_COVERAGE_DAYS:
                issues.append({'file': meta_file.name, 'symbol': symbol, 'mode': mode, 'actual_days': actual_days, 'total_trades': total_trades, 'severity': 'critical'})
            elif total_trades < 10:
                issues.append({'file': meta_file.name, 'symbol': symbol, 'mode': mode, 'actual_days': actual_days, 'total_trades': total_trades, 'severity': 'warning'})
        except Exception as e:
            logger.error(f"Error reading {meta_file.name}: {e}")
    return issues


def print_issues(issues):
    """Print coverage issues in a formatted way."""
    if not issues:
        logger.info("✓ No coverage issues found!")
        return
    critical = [i for i in issues if i['severity'] == 'critical']
    warnings = [i for i in issues if i['severity'] == 'warning']
    if critical:
        logger.error(f"\n{'='*60}")
        logger.error(f"CRITICAL: {len(critical)} symbol/mode combinations have insufficient coverage:")
        logger.error(f"{'='*60}")
        for issue in critical:
            logger.error(f"  {issue['symbol']} - {issue['mode']}: {issue['actual_days']} days, {issue['total_trades']} trades")
    if warnings:
        logger.warning(f"\n{'='*60}")
        logger.warning(f"WARNING: {len(warnings)} symbol/mode combinations have low trade counts:")
        logger.warning(f"{'='*60}")
        for issue in warnings:
            logger.warning(f"  {issue['symbol']} - {issue['mode']}: {issue['actual_days']} days, {issue['total_trades']} trades")


def backup_corrupted_files():
    """Backup files with insufficient coverage."""
    logger.info("\nBacking up corrupted files...")
    backup_dir = DATA_DIR / "backup" / datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    meta_files = list(DATA_DIR.glob("*_meta.json"))
    backed_up = 0
    for meta_file in meta_files:
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            actual_days = meta.get('actual_lookback_days', 0)
            if actual_days < MINIMUM_COVERAGE_DAYS:
                csv_file = meta_file.with_suffix('.csv')
                if csv_file.exists():
                    import shutil
                    shutil.copy(csv_file, backup_dir / csv_file.name)
                    shutil.copy(meta_file, backup_dir / meta_file.name)
                    logger.info(f"  Backed up: {csv_file.name}")
                    backed_up += 1
        except Exception as e:
            logger.error(f"Error backing up {meta_file.name}: {e}")
    logger.info(f"✓ Backed up {backed_up} file pairs to {backup_dir}")
    return backup_dir


def run_rebuild(mode=None, force=True):
    """Execute manage_backtests.py to rebuild data."""
    logger.info(f"\n{'='*60}")
    logger.info("Starting complete rebuild...")
    logger.info(f"{'='*60}\n")
    cmd = ["python", "manage_backtests.py", "--since=full"]
    if mode:
        cmd.extend(["--modes", mode])
    if force:
        cmd.append("--force-rebuild")
    logger.info(f"Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode == 0:
            logger.info("✓ Rebuild completed successfully")
            return True
        else:
            logger.error(f"✗ Rebuild failed with exit code {result.returncode}")
            return False
    except Exception as e:
        logger.error(f"✗ Error executing rebuild: {e}")
        return False


def run_tests():
    """Run coverage tests to validate rebuild."""
    logger.info(f"\n{'='*60}")
    logger.info("Running coverage tests...")
    logger.info(f"{'='*60}\n")
    cmd = ["pytest", "btc_1tpd_backtester/tests/test_annual_coverage.py::test_csv_coverage_meets_minimum", "-v", "-s"]
    logger.info(f"Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode == 0:
            logger.info("✓ All coverage tests PASSED")
            return True
        else:
            logger.error(f"✗ Some tests failed (exit code {result.returncode})")
            return False
    except Exception as e:
        logger.error(f"✗ Error running tests: {e}")
        return False


def generate_summary():
    """Generate post-recovery summary."""
    logger.info(f"\n{'='*60}")
    logger.info("POST-RECOVERY SUMMARY")
    logger.info(f"{'='*60}\n")
    cmd = ["python", "generate_annual_summary.py"]
    try:
        subprocess.run(cmd, capture_output=False, text=True)
        logger.info("✓ Annual summary generated")
    except Exception as e:
        logger.error(f"✗ Error generating summary: {e}")


def main():
    """Main recovery workflow."""
    import argparse
    parser = argparse.ArgumentParser(description='Historical Trades Data Recovery')
    parser.add_argument('--check-only', action='store_true', help='Only check coverage status without rebuilding')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup of corrupted files')
    parser.add_argument('--mode', help='Rebuild only specific mode (conservative/moderate/aggressive)')
    parser.add_argument('--skip-tests', action='store_true', help='Skip test execution after rebuild')
    args = parser.parse_args()
    logger.info(f"\n{'='*60}")
    logger.info("HISTORICAL TRADES DATA RECOVERY")
    logger.info(f"{'='*60}\n")
    logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info("")
    issues = check_coverage_status()
    print_issues(issues)
    if args.check_only:
        logger.info("\n--check-only mode: exiting without rebuild")
        sys.exit(0 if not issues else 1)
    if not issues:
        logger.info("\nNo recovery needed. All data has sufficient coverage.")
        sys.exit(0)
    if not args.no_backup:
        backup_dir = backup_corrupted_files()
    else:
        logger.info("\n--no-backup mode: skipping backup step")
    success = run_rebuild(mode=args.mode, force=True)
    if not success:
        logger.error("\n✗ Rebuild failed. Check logs above for details.")
        logger.error("You may need to manually execute: python manage_backtests.py --since=full --force-rebuild")
        sys.exit(1)
    if not args.skip_tests:
        tests_passed = run_tests()
        if not tests_passed:
            logger.warning("\n⚠️ Some tests failed. Review output above.")
    else:
        logger.info("\n--skip-tests mode: skipping test execution")
    generate_summary()
    issues_post = check_coverage_status()
    logger.info(f"\n{'='*60}")
    logger.info("RECOVERY COMPLETE")
    logger.info(f"{'='*60}\n")
    logger.info(f"Issues before: {len(issues)}")
    logger.info(f"Issues after: {len(issues_post)}")
    if issues_post:
        logger.warning(f"\n⚠️ {len(issues_post)} issues remain. Review details above.")
        print_issues(issues_post)
        sys.exit(1)
    else:
        logger.info("\n✓ All issues resolved!")
        logger.info("\nNext steps:")
        logger.info("  1. Start dashboard: python -m webapp.app")
        logger.info("  2. Open http://localhost:8050")
        logger.info("  3. Verify charts show historical data")
        sys.exit(0)


if __name__ == '__main__':
    main()


