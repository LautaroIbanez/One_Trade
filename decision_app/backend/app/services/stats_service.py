"""
Service for calculating real-time statistics from backtest data.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from pathlib import Path
from datetime import datetime
import glob

from app.core.logging import get_logger

logger = get_logger(__name__)


class StatsService:
    """Service for calculating statistics from backtest results."""
    
    def __init__(self):
        """Initialize stats service."""
        self.repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.trades_dir = self.repo_root
        
    def get_latest_backtest_results(self) -> List[Dict[str, Any]]:
        """
        Load latest backtest results from CSV files.
        
        Returns:
            List of backtest result dictionaries
        """
        results = []
        
        try:
            # Look for trades_final_*.csv files
            pattern = str(self.trades_dir / "trades_final_*.csv")
            trade_files = glob.glob(pattern)
            
            logger.info(f"Found {len(trade_files)} backtest result files")
            
            for file_path in trade_files:
                try:
                    df = pd.read_csv(file_path)
                    
                    if df.empty:
                        logger.warning(f"Empty backtest file: {file_path}")
                        continue
                    
                    # Extract symbol from filename
                    filename = Path(file_path).stem
                    parts = filename.split('_')
                    symbol = parts[2] if len(parts) > 2 else 'UNKNOWN'
                    
                    # Calculate metrics
                    total_trades = len(df)
                    
                    if 'pnl_pct' in df.columns:
                        winning_trades = len(df[df['pnl_pct'] > 0])
                        losing_trades = len(df[df['pnl_pct'] <= 0])
                        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                        total_pnl = df['pnl_pct'].sum()
                        max_drawdown = self._calculate_max_drawdown(df)
                        profit_factor = self._calculate_profit_factor(df)
                        avg_r_multiple = df.get('r_multiple', pd.Series([0])).mean()
                    else:
                        # Fallback for older format
                        winning_trades = 0
                        losing_trades = 0
                        win_rate = 0
                        total_pnl = 0
                        max_drawdown = 0
                        profit_factor = 0
                        avg_r_multiple = 0
                    
                    # Get last backtest date
                    if 'exit_time' in df.columns:
                        last_date = pd.to_datetime(df['exit_time']).max()
                        last_backtest_date = last_date.strftime('%Y-%m-%d')
                    else:
                        last_backtest_date = datetime.now().strftime('%Y-%m-%d')
                    
                    results.append({
                        'symbol': symbol,
                        'total_trades': total_trades,
                        'winning_trades': winning_trades,
                        'losing_trades': losing_trades,
                        'win_rate': win_rate,
                        'total_pnl': total_pnl,
                        'max_drawdown': max_drawdown,
                        'profit_factor': profit_factor,
                        'avg_r_multiple': avg_r_multiple,
                        'last_backtest_date': last_backtest_date,
                        'file_path': file_path
                    })
                    
                    logger.info(f"Loaded backtest for {symbol}: {total_trades} trades, {win_rate:.1f}% win rate")
                    
                except Exception as e:
                    logger.error(f"Error loading backtest file {file_path}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error loading backtest results: {e}")
            return []
    
    def _calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        """Calculate maximum drawdown from trades."""
        if 'pnl_pct' not in df.columns or df.empty:
            return 0.0
        
        try:
            # Calculate cumulative returns
            cumulative = (1 + df['pnl_pct'] / 100).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max * 100
            max_dd = drawdown.min()
            
            return float(max_dd) if not pd.isna(max_dd) else 0.0
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    def _calculate_profit_factor(self, df: pd.DataFrame) -> float:
        """Calculate profit factor from trades."""
        if 'pnl_pct' not in df.columns or df.empty:
            return 0.0
        
        try:
            gross_profit = df[df['pnl_pct'] > 0]['pnl_pct'].sum()
            gross_loss = abs(df[df['pnl_pct'] < 0]['pnl_pct'].sum())
            
            if gross_loss == 0:
                return float(gross_profit) if gross_profit > 0 else 0.0
            
            return float(gross_profit / gross_loss)
        except Exception as e:
            logger.error(f"Error calculating profit factor: {e}")
            return 0.0
    
    def get_aggregated_stats(self) -> Dict[str, Any]:
        """
        Get aggregated statistics from all backtest results.
        
        Returns:
            Dictionary with aggregated statistics
        """
        results = self.get_latest_backtest_results()
        
        if not results:
            logger.warning("No backtest results available")
            return {
                'active_recommendations': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'max_drawdown': 0.0,
                'total_trades': 0,
                'profit_factor': 0.0,
                'avg_r_multiple': 0.0,
                'data_source': 'none',
                'last_update': datetime.now().isoformat()
            }
        
        # Aggregate across all symbols
        total_trades = sum(r['total_trades'] for r in results)
        total_winning = sum(r['winning_trades'] for r in results)
        
        # Weighted average win rate
        win_rate = (total_winning / total_trades * 100) if total_trades > 0 else 0
        
        # Average P&L
        avg_pnl = sum(r['total_pnl'] for r in results) / len(results) if results else 0
        
        # Worst drawdown across all symbols
        max_drawdown = min(r['max_drawdown'] for r in results) if results else 0
        
        # Average profit factor
        avg_profit_factor = sum(r['profit_factor'] for r in results) / len(results) if results else 0
        
        # Average R-multiple
        avg_r_multiple = sum(r['avg_r_multiple'] for r in results) / len(results) if results else 0
        
        return {
            'active_recommendations': len(results),
            'total_pnl': float(avg_pnl),
            'win_rate': float(win_rate),
            'max_drawdown': float(max_drawdown),
            'total_trades': total_trades,
            'profit_factor': float(avg_profit_factor),
            'avg_r_multiple': float(avg_r_multiple),
            'data_source': 'backtests',
            'last_update': datetime.now().isoformat()
        }
    
    def get_symbol_performance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for a specific symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with symbol-specific metrics or None
        """
        results = self.get_latest_backtest_results()
        
        for result in results:
            if result['symbol'] == symbol:
                return result
        
        return None


# Global stats service instance
stats_service = StatsService()

