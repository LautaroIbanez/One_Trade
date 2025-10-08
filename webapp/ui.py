"""UI utilities for windowed daily quota backtest results. Provides functions for computing trade metrics and preparing trade reports without mutating DataFrames."""
import pandas as pd
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def compute_trade_metrics(trades_df: pd.DataFrame, initial_capital: float = 1000.0) -> Dict:
    """Derive aggregated metrics from trades DataFrame without mutating it. Args: trades_df: DataFrame with trade data (columns: entry_time, exit_time, side, entry_price, exit_price, pnl, etc.), initial_capital: Initial capital for ROI calculation. Returns: Dictionary with computed metrics"""
    if trades_df is None or trades_df.empty:
        logger.warning("compute_trade_metrics: empty or None DataFrame provided")
        return {'total_trades': 0, 'total_pnl': 0.0, 'win_rate': 0.0, 'avg_trade': 0.0, 'profit_factor': 0.0, 'max_drawdown': 0.0, 'roi': 0.0, 'best_trade': 0.0, 'worst_trade': 0.0}
    df = trades_df.copy()
    total_trades = len(df)
    if 'pnl' not in df.columns:
        logger.error("compute_trade_metrics: 'pnl' column missing from DataFrame")
        return {'total_trades': total_trades, 'total_pnl': 0.0, 'win_rate': 0.0, 'avg_trade': 0.0, 'profit_factor': 0.0, 'max_drawdown': 0.0, 'roi': 0.0, 'best_trade': 0.0, 'worst_trade': 0.0}
    total_pnl = df['pnl'].sum()
    wins = df[df['pnl'] > 0]
    losses = df[df['pnl'] < 0]
    win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0.0
    avg_trade = total_pnl / total_trades if total_trades > 0 else 0.0
    gross_profit = wins['pnl'].sum() if not wins.empty else 0.0
    gross_loss = abs(losses['pnl'].sum()) if not losses.empty else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0.0)
    df['cumulative_pnl'] = df['pnl'].cumsum()
    df['running_max'] = df['cumulative_pnl'].cummax()
    df['drawdown'] = df['cumulative_pnl'] - df['running_max']
    max_drawdown = abs(df['drawdown'].min()) if not df['drawdown'].empty else 0.0
    roi = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0.0
    best_trade = df['pnl'].max() if not df.empty else 0.0
    worst_trade = df['pnl'].min() if not df.empty else 0.0
    logger.info(f"compute_trade_metrics: total_trades={total_trades}, total_pnl={total_pnl:.2f}, win_rate={win_rate:.1f}%, max_dd={max_drawdown:.2f}")
    return {'total_trades': total_trades, 'total_pnl': total_pnl, 'win_rate': win_rate, 'avg_trade': avg_trade, 'profit_factor': profit_factor, 'max_drawdown': max_drawdown, 'roi': roi, 'gross_profit': gross_profit, 'gross_loss': gross_loss, 'best_trade': best_trade, 'worst_trade': worst_trade}


def prepare_trade_report(backtest_result: Dict) -> Dict:
    """Return the untouched trades DataFrame alongside metrics. Logs the number of rows rendered. Args: backtest_result: Dictionary from BacktestRunner.run() with '_trades' DataFrame and '_metrics' dict. Returns: Dictionary with 'trades' DataFrame, 'metrics' dict, and 'daily_log' dict"""
    if backtest_result is None or not isinstance(backtest_result, dict):
        logger.error("prepare_trade_report: invalid backtest_result provided")
        return {'trades': pd.DataFrame(), 'metrics': {}, 'daily_log': {}}
    trades_df = backtest_result.get('_trades', pd.DataFrame())
    metrics = backtest_result.get('_metrics', {})
    daily_log = backtest_result.get('_daily_log', {})
    if trades_df is None or not isinstance(trades_df, pd.DataFrame):
        logger.warning("prepare_trade_report: '_trades' is not a DataFrame")
        trades_df = pd.DataFrame()
    row_count = len(trades_df)
    logger.info(f"prepare_trade_report: rendering {row_count} trade rows")
    return {'trades': trades_df, 'metrics': metrics, 'daily_log': daily_log, 'row_count': row_count}


def determine_signal_banner(today_signal: Optional[Dict], open_position_side: Optional[str], last_closed_trade_side: Optional[str] = None) -> Dict:
    """Determine banner level and message based on signal and position state. Validates signal integrity and returns appropriate banner info. Args: today_signal: Signal dict from strategy (keys: side, entry_price, sl, tp, valid), open_position_side: Current open position side ('long', 'short', 'flat', or None), last_closed_trade_side: Side of last closed trade (for context). Returns: dict with 'level' (str: 'ok', 'warning', 'error') and 'message' (str)"""
    if today_signal is None or not isinstance(today_signal, dict):
        logger.debug("signal_banner: no signal provided, level=ok")
        return {'level': 'ok', 'message': 'No signal generated for today'}
    if not today_signal.get('valid', False):
        reason = today_signal.get('reason', 'unknown')
        logger.debug(f"signal_banner: invalid signal, reason={reason}, level=ok")
        return {'level': 'ok', 'message': f'No valid signal (reason: {reason})'}
    signal_side = today_signal.get('side')
    entry_price = today_signal.get('entry_price')
    sl = today_signal.get('sl')
    tp = today_signal.get('tp')
    if signal_side not in ['long', 'short']:
        logger.error(f"signal_banner: invalid signal side={signal_side}, level=error")
        return {'level': 'error', 'message': f'Invalid signal side: {signal_side}'}
    if entry_price is None or entry_price <= 0:
        logger.error(f"signal_banner: invalid entry_price={entry_price}, level=error")
        return {'level': 'error', 'message': f'Invalid entry price: {entry_price}'}
    if sl is None or sl <= 0 or tp is None or tp <= 0:
        logger.error(f"signal_banner: invalid stop/target sl={sl}, tp={tp}, level=error")
        return {'level': 'error', 'message': f'Invalid stop loss or take profit levels'}
    if open_position_side is None or open_position_side == 'flat':
        logger.debug(f"signal_ok_no_position: signal_side={signal_side}, level=ok")
        return {'level': 'ok', 'message': f'Signal: {signal_side.upper()} @ {entry_price:.2f} (SL: {sl:.2f}, TP: {tp:.2f})'}
    if open_position_side.lower() == signal_side.lower():
        logger.debug(f"signal_aligned: signal_side={signal_side}, position_side={open_position_side}, level=ok")
        return {'level': 'ok', 'message': f'Signal {signal_side.upper()} aligns with open {open_position_side.upper()} position'}
    logger.warning(f"signal_reversal: signal_side={signal_side}, position_side={open_position_side}, level=warning")
    return {'level': 'warning', 'message': f'⚠️ Reversal signal: {signal_side.upper()} suggested but {open_position_side.upper()} position open'}

