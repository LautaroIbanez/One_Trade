"""Batch runner for annual backtesting across all modes and symbols. Iterates through MODE_ASSETS, executes refresh_trades forcing since=today-365, and generates structured logs with coverage validation."""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

try:
    from webapp.app import MODE_ASSETS, refresh_trades, get_effective_config, repo_root
except Exception as e:
    print(f"Error importing webapp modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MINIMUM_COVERAGE_DAYS = 365
OUTPUT_DIR = Path(__file__).parent / "data"
BACKTEST_LOG_FILE = OUTPUT_DIR / "backtest_execution_log.json"


class AnnualBacktestRunner:
    """Manages annual backtesting execution across all modes and symbols with coverage validation."""
    def __init__(self, since_mode: str = "auto", force_rebuild: bool = False):
        """Initialize annual backtest runner. Args: since_mode: 'auto' for today-365, 'full' for maximum history, or ISO date string, force_rebuild: Force complete rebuild regardless of existing data"""
        self.since_mode = since_mode
        self.force_rebuild = force_rebuild
        self.execution_log = []
        self.summary = {'total_symbols': 0, 'total_modes': 0, 'total_executions': 0, 'successful': 0, 'failed': 0, 'insufficient_coverage': 0, 'total_trades_generated': 0}
        self.since_date = self._calculate_since_date()
        logger.info(f"AnnualBacktestRunner initialized: since_mode={since_mode}, since_date={self.since_date}, force_rebuild={force_rebuild}")
    def _calculate_since_date(self) -> str:
        """Calculate the since date based on mode."""
        if self.since_mode == "auto":
            return (datetime.now(timezone.utc).date() - timedelta(days=MINIMUM_COVERAGE_DAYS)).isoformat()
        elif self.since_mode == "full":
            return (datetime.now(timezone.utc).date() - timedelta(days=730)).isoformat()
        else:
            try:
                datetime.fromisoformat(self.since_mode)
                return self.since_mode
            except Exception:
                logger.warning(f"Invalid since_mode '{self.since_mode}', falling back to auto")
                return (datetime.now(timezone.utc).date() - timedelta(days=MINIMUM_COVERAGE_DAYS)).isoformat()
    def _validate_coverage(self, symbol: str, mode: str) -> Tuple[bool, Dict]:
        """Validate that backtest coverage meets minimum requirements. Args: symbol: Trading symbol, mode: Trading mode. Returns: (is_valid, metadata_dict) tuple"""
        slug = symbol.replace('/', '_').replace(':', '_')
        mode_suffix = mode.lower()
        meta_path = OUTPUT_DIR / f"trades_final_{slug}_{mode_suffix}_meta.json"
        if not meta_path.exists():
            logger.warning(f"Coverage validation: meta file missing for {symbol} {mode}")
            return False, {}
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            actual_lookback = meta.get('actual_lookback_days')
            first_trade_date = meta.get('first_trade_date')
            last_trade_date = meta.get('last_trade_date')
            total_trades = meta.get('total_trades', 0)
            if actual_lookback is None or actual_lookback < MINIMUM_COVERAGE_DAYS:
                logger.error(f"Coverage validation FAILED: {symbol} {mode} has only {actual_lookback} days (need {MINIMUM_COVERAGE_DAYS})")
                return False, meta
            logger.info(f"Coverage validation PASSED: {symbol} {mode} has {actual_lookback} days ({first_trade_date} to {last_trade_date}, {total_trades} trades)")
            return True, meta
        except Exception as e:
            logger.error(f"Coverage validation ERROR: {symbol} {mode}: {e}")
            return False, {}
    def _execute_single_backtest(self, symbol: str, mode: str) -> Dict:
        """Execute backtest for a single symbol/mode combination. Args: symbol: Trading symbol, mode: Trading mode. Returns: Execution result dictionary"""
        start_time = datetime.now(timezone.utc)
        logger.info(f"{'='*60}")
        logger.info(f"Starting backtest: {symbol} - {mode}")
        logger.info(f"{'='*60}")
        result = {'symbol': symbol, 'mode': mode, 'start_time': start_time.isoformat(), 'end_time': None, 'status': 'pending', 'message': '', 'trades_generated': 0, 'coverage_days': 0, 'errors': []}
        try:
            config = get_effective_config(symbol, mode)
            logger.info(f"Effective config: lookback_days={config.get('lookback_days')}, since={self.since_date}")
            if self.force_rebuild:
                logger.info(f"Force rebuild enabled, clearing existing data")
            refresh_result = refresh_trades(symbol, mode)
            logger.info(f"refresh_trades result: {refresh_result}")
            if "ERROR" in refresh_result or "error" in refresh_result.lower():
                result['status'] = 'failed'
                result['message'] = refresh_result
                result['errors'].append(refresh_result)
                self.summary['failed'] += 1
                logger.error(f"Backtest FAILED: {symbol} {mode}: {refresh_result}")
            else:
                is_valid, meta = self._validate_coverage(symbol, mode)
                result['coverage_days'] = meta.get('actual_lookback_days', 0)
                result['trades_generated'] = meta.get('total_trades', 0)
                result['first_trade_date'] = meta.get('first_trade_date')
                result['last_trade_date'] = meta.get('last_trade_date')
                if is_valid:
                    result['status'] = 'success'
                    result['message'] = f"Backtest completed successfully: {result['trades_generated']} trades, {result['coverage_days']} days coverage"
                    self.summary['successful'] += 1
                    self.summary['total_trades_generated'] += result['trades_generated']
                    logger.info(f"Backtest SUCCESS: {symbol} {mode}: {result['message']}")
                else:
                    result['status'] = 'insufficient_coverage'
                    result['message'] = f"Insufficient coverage: {result['coverage_days']} days (need {MINIMUM_COVERAGE_DAYS})"
                    result['errors'].append(result['message'])
                    self.summary['insufficient_coverage'] += 1
                    logger.warning(f"Backtest INSUFFICIENT COVERAGE: {symbol} {mode}: {result['message']}")
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f"Exception during backtest: {str(e)}"
            result['errors'].append(str(e))
            self.summary['failed'] += 1
            logger.exception(f"Backtest ERROR: {symbol} {mode}: {e}")
        end_time = datetime.now(timezone.utc)
        result['end_time'] = end_time.isoformat()
        result['duration_seconds'] = (end_time - start_time).total_seconds()
        self.execution_log.append(result)
        self.summary['total_executions'] += 1
        return result
    def run_all_modes(self, modes: List[str] = None) -> Dict:
        """Execute backtests for all symbols across specified modes. Args: modes: List of modes to run (default: all modes). Returns: Summary dictionary with execution results"""
        if modes is None:
            modes = list(MODE_ASSETS.keys())
        logger.info(f"Starting batch backtest execution for modes: {modes}")
        logger.info(f"Since date: {self.since_date}, Minimum coverage: {MINIMUM_COVERAGE_DAYS} days")
        all_symbols = set()
        for mode in modes:
            symbols = MODE_ASSETS.get(mode, [])
            all_symbols.update(symbols)
            self.summary['total_modes'] += 1
        self.summary['total_symbols'] = len(all_symbols)
        logger.info(f"Total symbols to process: {self.summary['total_symbols']}")
        logger.info(f"Total modes to process: {self.summary['total_modes']}")
        for mode in modes:
            symbols = MODE_ASSETS.get(mode, [])
            logger.info(f"\n{'#'*60}")
            logger.info(f"Processing mode: {mode.upper()} ({len(symbols)} symbols)")
            logger.info(f"{'#'*60}\n")
            for symbol in symbols:
                self._execute_single_backtest(symbol, mode)
        self._save_execution_log()
        self._print_summary()
        return {'summary': self.summary, 'execution_log': self.execution_log, 'since_date': self.since_date}
    def _save_execution_log(self):
        """Save execution log to JSON file."""
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            log_data = {'timestamp': datetime.now(timezone.utc).isoformat(), 'since_date': self.since_date, 'force_rebuild': self.force_rebuild, 'summary': self.summary, 'executions': self.execution_log}
            with open(BACKTEST_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Execution log saved to {BACKTEST_LOG_FILE}")
        except Exception as e:
            logger.error(f"Failed to save execution log: {e}")
    def _print_summary(self):
        """Print execution summary to console."""
        logger.info(f"\n{'='*60}")
        logger.info(f"BATCH BACKTEST EXECUTION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total symbols processed: {self.summary['total_symbols']}")
        logger.info(f"Total modes processed: {self.summary['total_modes']}")
        logger.info(f"Total executions: {self.summary['total_executions']}")
        logger.info(f"Successful: {self.summary['successful']} ({self.summary['successful']/self.summary['total_executions']*100:.1f}%)" if self.summary['total_executions'] > 0 else "Successful: 0")
        logger.info(f"Failed: {self.summary['failed']}")
        logger.info(f"Insufficient coverage: {self.summary['insufficient_coverage']}")
        logger.info(f"Total trades generated: {self.summary['total_trades_generated']}")
        logger.info(f"Since date: {self.since_date}")
        logger.info(f"{'='*60}\n")
        if self.summary['failed'] > 0 or self.summary['insufficient_coverage'] > 0:
            logger.warning(f"⚠️  {self.summary['failed'] + self.summary['insufficient_coverage']} executions require attention!")
            for exec_result in self.execution_log:
                if exec_result['status'] in ['failed', 'insufficient_coverage', 'error']:
                    logger.warning(f"  - {exec_result['symbol']} {exec_result['mode']}: {exec_result['message']}")


def main():
    """Main entry point for batch backtest execution."""
    import argparse
    parser = argparse.ArgumentParser(description='Annual Backtest Batch Runner')
    parser.add_argument('--since', default='auto', help="Since mode: 'auto' (today-365), 'full' (today-730), or ISO date (e.g., '2023-01-01')")
    parser.add_argument('--modes', nargs='*', help='Specific modes to run (default: all modes)')
    parser.add_argument('--force-rebuild', action='store_true', help='Force complete rebuild of all data')
    parser.add_argument('--report-only', action='store_true', help='Generate report from existing log without running backtests')
    args = parser.parse_args()
    if args.report_only:
        logger.info("Report-only mode: generating summary from existing log")
        if BACKTEST_LOG_FILE.exists():
            with open(BACKTEST_LOG_FILE, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            logger.info(f"Last execution: {log_data['timestamp']}")
            logger.info(f"Since date: {log_data['since_date']}")
            logger.info(f"Summary: {json.dumps(log_data['summary'], indent=2)}")
            failed_count = log_data['summary']['failed'] + log_data['summary']['insufficient_coverage']
            if failed_count > 0:
                logger.warning(f"⚠️  {failed_count} executions require attention:")
                for exec_result in log_data['executions']:
                    if exec_result['status'] in ['failed', 'insufficient_coverage', 'error']:
                        logger.warning(f"  - {exec_result['symbol']} {exec_result['mode']}: {exec_result['message']}")
        else:
            logger.error(f"Log file not found: {BACKTEST_LOG_FILE}")
        return
    runner = AnnualBacktestRunner(since_mode=args.since, force_rebuild=args.force_rebuild)
    result = runner.run_all_modes(modes=args.modes)
    exit_code = 0
    if result['summary']['failed'] > 0 or result['summary']['insufficient_coverage'] > 0:
        exit_code = 1
        logger.error(f"Batch execution completed with errors (exit code {exit_code})")
    else:
        logger.info(f"Batch execution completed successfully (exit code {exit_code})")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

