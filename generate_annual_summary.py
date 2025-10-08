"""Generate annual consolidated summary by combining CSV files per mode and calculating Year-to-Date metrics. Saves results to data/annual_summary_{mode}.json for dashboard consumption."""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

try:
    from webapp.app import MODE_ASSETS, repo_root
except Exception as e:
    print(f"Error importing webapp modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = repo_root / "data"
OUTPUT_DIR = DATA_DIR


class AnnualSummaryGenerator:
    """Generates consolidated annual summaries with Year-to-Date metrics for each trading mode."""
    def __init__(self, ytd_only: bool = False):
        """Initialize summary generator. Args: ytd_only: If True, only include trades from current year"""
        self.ytd_only = ytd_only
        self.current_year = datetime.now(timezone.utc).year
        self.summaries = {}
        logger.info(f"AnnualSummaryGenerator initialized: ytd_only={ytd_only}, current_year={self.current_year}")
    def _calculate_metrics(self, df: pd.DataFrame, mode: str, initial_capital: float = 1000.0) -> Dict:
        """Calculate comprehensive metrics from trades DataFrame. Args: df: Trades DataFrame, mode: Trading mode, initial_capital: Initial capital for ROI. Returns: Dictionary with calculated metrics"""
        if df.empty:
            return {'total_trades': 0, 'total_pnl': 0.0, 'win_rate': 0.0, 'avg_pnl': 0.0, 'max_drawdown': 0.0, 'profit_factor': 0.0, 'roi': 0.0, 'best_trade': 0.0, 'worst_trade': 0.0, 'avg_win': 0.0, 'avg_loss': 0.0, 'win_count': 0, 'loss_count': 0, 'gross_profit': 0.0, 'gross_loss': 0.0}
        total_trades = len(df)
        total_pnl = df['pnl_usdt'].sum()
        wins = df[df['pnl_usdt'] > 0]
        losses = df[df['pnl_usdt'] < 0]
        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
        avg_pnl = df['pnl_usdt'].mean()
        best_trade = df['pnl_usdt'].max()
        worst_trade = df['pnl_usdt'].min()
        avg_win = wins['pnl_usdt'].mean() if win_count > 0 else 0.0
        avg_loss = losses['pnl_usdt'].mean() if loss_count > 0 else 0.0
        gross_profit = wins['pnl_usdt'].sum() if win_count > 0 else 0.0
        gross_loss = abs(losses['pnl_usdt'].sum()) if loss_count > 0 else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0.0)
        df_sorted = df.sort_values('entry_time')
        df_sorted['cumulative_pnl'] = df_sorted['pnl_usdt'].cumsum()
        df_sorted['running_max'] = df_sorted['cumulative_pnl'].cummax()
        df_sorted['drawdown'] = df_sorted['cumulative_pnl'] - df_sorted['running_max']
        max_drawdown = df_sorted['drawdown'].min() if not df_sorted['drawdown'].empty else 0.0
        roi = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0.0
        return {'total_trades': total_trades, 'total_pnl': float(total_pnl), 'win_rate': float(win_rate), 'avg_pnl': float(avg_pnl), 'max_drawdown': float(max_drawdown), 'profit_factor': float(profit_factor) if not np.isinf(profit_factor) else 999.99, 'roi': float(roi), 'best_trade': float(best_trade), 'worst_trade': float(worst_trade), 'avg_win': float(avg_win), 'avg_loss': float(avg_loss), 'win_count': int(win_count), 'loss_count': int(loss_count), 'gross_profit': float(gross_profit), 'gross_loss': float(gross_loss)}
    def _load_mode_trades(self, mode: str) -> pd.DataFrame:
        """Load and combine all CSV files for a given mode. Args: mode: Trading mode. Returns: Combined DataFrame with all trades for the mode"""
        mode_suffix = mode.lower()
        pattern = f"trades_final_*_{mode_suffix}.csv"
        csv_files = list(DATA_DIR.glob(pattern))
        if not csv_files:
            logger.warning(f"No CSV files found for mode: {mode} (pattern: {pattern})")
            return pd.DataFrame()
        logger.info(f"Found {len(csv_files)} CSV files for mode {mode}")
        dfs = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                if not df.empty:
                    if 'entry_time' in df.columns:
                        df['entry_time'] = pd.to_datetime(df['entry_time'], errors='coerce')
                    if 'exit_time' in df.columns:
                        df['exit_time'] = pd.to_datetime(df['exit_time'], errors='coerce')
                    symbol_slug = csv_file.stem.replace(f'trades_final_', '').replace(f'_{mode_suffix}', '')
                    df['symbol_slug'] = symbol_slug
                    df['source_file'] = csv_file.name
                    dfs.append(df)
            except Exception as e:
                logger.error(f"Error loading {csv_file.name}: {e}")
                continue
        if not dfs:
            logger.warning(f"No valid trades found for mode: {mode}")
            return pd.DataFrame()
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df = combined_df.sort_values('entry_time')
        if self.ytd_only and 'entry_time' in combined_df.columns:
            combined_df = combined_df[combined_df['entry_time'].dt.year == self.current_year]
            logger.info(f"Filtered to YTD: {len(combined_df)} trades in {self.current_year}")
        logger.info(f"Combined {len(combined_df)} trades for mode {mode}")
        return combined_df
    def _generate_mode_summary(self, mode: str) -> Dict:
        """Generate summary for a single mode. Args: mode: Trading mode. Returns: Summary dictionary"""
        logger.info(f"Generating summary for mode: {mode}")
        trades_df = self._load_mode_trades(mode)
        if trades_df.empty:
            logger.warning(f"No trades available for mode {mode}, skipping summary")
            return None
        metrics = self._calculate_metrics(trades_df, mode)
        symbols = MODE_ASSETS.get(mode, [])
        symbol_metrics = {}
        for symbol in symbols:
            slug = symbol.replace('/', '_').replace(':', '_')
            symbol_df = trades_df[trades_df['symbol_slug'].str.contains(slug, na=False)]
            if not symbol_df.empty:
                symbol_metrics[symbol] = self._calculate_metrics(symbol_df, mode)
        date_range = {}
        if not trades_df.empty and 'entry_time' in trades_df.columns:
            first_trade = trades_df['entry_time'].min()
            last_trade = trades_df['entry_time'].max()
            if pd.notna(first_trade) and pd.notna(last_trade):
                date_range = {'first_trade_date': first_trade.date().isoformat(), 'last_trade_date': last_trade.date().isoformat(), 'coverage_days': (last_trade.date() - first_trade.date()).days}
        summary = {'mode': mode, 'timestamp': datetime.now(timezone.utc).isoformat(), 'ytd_only': self.ytd_only, 'current_year': self.current_year if self.ytd_only else None, 'date_range': date_range, 'overall_metrics': metrics, 'symbol_metrics': symbol_metrics, 'total_symbols': len(symbol_metrics)}
        logger.info(f"Summary for {mode}: {metrics['total_trades']} trades, PnL: ${metrics['total_pnl']:.2f}, Win Rate: {metrics['win_rate']:.1f}%")
        return summary
    def generate_all_summaries(self) -> Dict:
        """Generate summaries for all modes. Returns: Dictionary with summaries for all modes"""
        logger.info("Generating summaries for all modes...")
        modes = list(MODE_ASSETS.keys())
        for mode in modes:
            summary = self._generate_mode_summary(mode)
            if summary:
                self.summaries[mode] = summary
                self._save_summary(mode, summary)
        self._generate_cross_mode_comparison()
        logger.info(f"Generated {len(self.summaries)} mode summaries")
        return self.summaries
    def _save_summary(self, mode: str, summary: Dict):
        """Save summary to JSON file. Args: mode: Trading mode, summary: Summary dictionary"""
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_file = OUTPUT_DIR / f"annual_summary_{mode.lower()}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved summary to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save summary for {mode}: {e}")
    def _generate_cross_mode_comparison(self):
        """Generate cross-mode comparison report."""
        if not self.summaries:
            logger.warning("No summaries available for cross-mode comparison")
            return
        comparison = {'timestamp': datetime.now(timezone.utc).isoformat(), 'ytd_only': self.ytd_only, 'modes': {}}
        for mode, summary in self.summaries.items():
            comparison['modes'][mode] = {'total_trades': summary['overall_metrics']['total_trades'], 'total_pnl': summary['overall_metrics']['total_pnl'], 'win_rate': summary['overall_metrics']['win_rate'], 'profit_factor': summary['overall_metrics']['profit_factor'], 'roi': summary['overall_metrics']['roi'], 'max_drawdown': summary['overall_metrics']['max_drawdown']}
        comparison_file = OUTPUT_DIR / "annual_summary_comparison.json"
        try:
            with open(comparison_file, 'w', encoding='utf-8') as f:
                json.dump(comparison, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved cross-mode comparison to {comparison_file}")
        except Exception as e:
            logger.error(f"Failed to save cross-mode comparison: {e}")
    def print_summary(self):
        """Print summary to console."""
        if not self.summaries:
            logger.warning("No summaries to print")
            return
        logger.info(f"\n{'='*60}")
        logger.info(f"ANNUAL SUMMARY REPORT")
        logger.info(f"{'='*60}")
        logger.info(f"Period: {'Year-to-Date ' + str(self.current_year) if self.ytd_only else 'All available data'}")
        logger.info(f"Modes processed: {len(self.summaries)}")
        logger.info(f"{'='*60}\n")
        for mode, summary in self.summaries.items():
            metrics = summary['overall_metrics']
            logger.info(f"Mode: {mode.upper()}")
            logger.info(f"  Total Trades: {metrics['total_trades']}")
            logger.info(f"  Total PnL: ${metrics['total_pnl']:,.2f}")
            logger.info(f"  Win Rate: {metrics['win_rate']:.1f}% ({metrics['win_count']}W / {metrics['loss_count']}L)")
            logger.info(f"  Profit Factor: {metrics['profit_factor']:.2f}")
            logger.info(f"  ROI: {metrics['roi']:+.1f}%")
            logger.info(f"  Max Drawdown: ${metrics['max_drawdown']:,.2f}")
            logger.info(f"  Best Trade: ${metrics['best_trade']:,.2f}")
            logger.info(f"  Worst Trade: ${metrics['worst_trade']:,.2f}")
            logger.info(f"  Date Range: {summary['date_range'].get('first_trade_date', 'N/A')} to {summary['date_range'].get('last_trade_date', 'N/A')} ({summary['date_range'].get('coverage_days', 0)} days)")
            logger.info("")


def main():
    """Main entry point for annual summary generation."""
    import argparse
    parser = argparse.ArgumentParser(description='Generate Annual Consolidated Summary')
    parser.add_argument('--ytd-only', action='store_true', help='Only include Year-to-Date trades')
    parser.add_argument('--mode', help='Generate summary for specific mode only')
    args = parser.parse_args()
    generator = AnnualSummaryGenerator(ytd_only=args.ytd_only)
    if args.mode:
        logger.info(f"Generating summary for mode: {args.mode}")
        summary = generator._generate_mode_summary(args.mode)
        if summary:
            generator.summaries[args.mode] = summary
            generator._save_summary(args.mode, summary)
            generator.print_summary()
        else:
            logger.error(f"Failed to generate summary for mode: {args.mode}")
            sys.exit(1)
    else:
        generator.generate_all_summaries()
        generator.print_summary()
    logger.info("Annual summary generation completed")


if __name__ == '__main__':
    main()

