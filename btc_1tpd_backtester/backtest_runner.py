"""Lightweight backtest execution loop for windowed daily quota strategy. Implements bar-by-bar execution, daily logging, trade lifecycle management, and metrics calculation."""
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from .strategy import WindowedSignalStrategy

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    """Dataclass representing a single executed trade."""
    entry_time: datetime
    exit_time: Optional[datetime]
    side: str
    entry_price: float
    exit_price: Optional[float]
    sl: float
    tp: float
    pnl: Optional[float]
    reason: str
    exit_reason: Optional[str]
    position_size: float
    day_key: str


class BacktestRunner:
    """Lightweight backtest execution loop. Sorts data, instantiates WindowedSignalStrategy, and iterates bar-by-bar with daily quota management."""
    def __init__(self, data: pd.DataFrame, config: dict):
        """Initialize backtest runner. Args: data: DataFrame with OHLCV data and datetime index, config: Configuration dictionary for strategy"""
        self.data = data.sort_index()
        self.config = config
        self.strategy = WindowedSignalStrategy(config)
        self.strategy.set_market_data(self.data)
        self._trades = []
        self._metrics = {}
        self._open_trade = None
        self._current_day = None
        self._daily_log = {}
        try:
            self.local_tz = ZoneInfo(config.get('timezone', 'America/Argentina/Buenos_Aires'))
        except Exception:
            self.local_tz = timezone.utc
        logger.info(f"BacktestRunner initialized with {len(self.data)} bars from {self.data.index[0]} to {self.data.index[-1]}")
    def _to_local(self, dt: datetime) -> datetime:
        """Convert UTC datetime to local timezone."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(self.local_tz)
    def _log_daily_summary(self, local_date):
        """Log summary when a new local day begins. Args: local_date: Date object for the new day"""
        if self._current_day is not None and self._current_day != local_date:
            prev_day_trades = [t for t in self._trades if t.day_key == str(self._current_day)]
            prev_day_pnl = sum(t.pnl for t in prev_day_trades if t.pnl is not None)
            logger.info(f"daily_summary: date={self._current_day}, trades={len(prev_day_trades)}, pnl={prev_day_pnl:.2f}")
            self._daily_log[str(self._current_day)] = {'trades': len(prev_day_trades), 'pnl': prev_day_pnl}
        self._current_day = local_date
    def _check_exit_conditions(self, bar_index: int) -> Optional[tuple]:
        """Check if open trade should be closed. Args: bar_index: Current bar index. Returns: (exit_price, exit_reason) tuple if exit triggered, None otherwise"""
        if self._open_trade is None:
            return None
        row = self.data.iloc[bar_index]
        high = row['high']
        low = row['low']
        close = row['close']
        current_time = self.data.index[bar_index]
        local_time = self._to_local(current_time)
        trade_local_time = self._to_local(self._open_trade['entry_time'])
        if local_time.date() > trade_local_time.date():
            logger.debug(f"session_rollover: closing trade at {close:.2f} (next day)")
            return (close, 'session_rollover')
        if self._open_trade['side'] == 'long':
            if low <= self._open_trade['sl']:
                logger.debug(f"stop_loss_hit: long at {self._open_trade['sl']:.2f}")
                return (self._open_trade['sl'], 'stop_loss')
            if high >= self._open_trade['tp']:
                logger.debug(f"take_profit_hit: long at {self._open_trade['tp']:.2f}")
                return (self._open_trade['tp'], 'take_profit')
        else:
            if high >= self._open_trade['sl']:
                logger.debug(f"stop_loss_hit: short at {self._open_trade['sl']:.2f}")
                return (self._open_trade['sl'], 'stop_loss')
            if low <= self._open_trade['tp']:
                logger.debug(f"take_profit_hit: short at {self._open_trade['tp']:.2f}")
                return (self._open_trade['tp'], 'take_profit')
        return None
    def _open_trade_at_bar(self, bar_index: int, signal: dict):
        """Open a new trade at the current bar. Args: bar_index: Current bar index, signal: Signal dictionary from strategy"""
        current_time = self.data.index[bar_index]
        position_size = self.strategy.compute_position_size(signal['entry_price'], signal['sl'])
        local_time = self._to_local(current_time)
        day_key = str(local_time.date())
        self._open_trade = {'entry_time': current_time, 'side': signal['side'], 'entry_price': signal['entry_price'], 'sl': signal['sl'], 'tp': signal['tp'], 'reason': signal['reason'], 'position_size': position_size, 'day_key': day_key}
        self.strategy.record_trade(current_time)
        logger.debug(f"trade_opened: time={current_time}, side={signal['side']}, entry={signal['entry_price']:.2f}, sl={signal['sl']:.2f}, tp={signal['tp']:.2f}, size={position_size:.4f}, reason={signal['reason']}")
    def _close_trade_at_bar(self, bar_index: int, exit_price: float, exit_reason: str):
        """Close the open trade at the current bar. Args: bar_index: Current bar index, exit_price: Exit price, exit_reason: Reason for exit"""
        if self._open_trade is None:
            return
        current_time = self.data.index[bar_index]
        entry_price = self._open_trade['entry_price']
        position_size = self._open_trade['position_size']
        if self._open_trade['side'] == 'long':
            pnl = (exit_price - entry_price) * position_size
        else:
            pnl = (entry_price - exit_price) * position_size
        trade_record = TradeRecord(entry_time=self._open_trade['entry_time'], exit_time=current_time, side=self._open_trade['side'], entry_price=entry_price, exit_price=exit_price, sl=self._open_trade['sl'], tp=self._open_trade['tp'], pnl=pnl, reason=self._open_trade['reason'], exit_reason=exit_reason, position_size=position_size, day_key=self._open_trade['day_key'])
        self._trades.append(trade_record)
        logger.debug(f"trade_closed: time={current_time}, side={self._open_trade['side']}, exit={exit_price:.2f}, pnl={pnl:.2f}, reason={exit_reason}")
        self._open_trade = None
    def run(self) -> dict:
        """Execute backtest bar-by-bar. Returns: dict with '_trades' DataFrame and '_metrics' dict"""
        logger.info("Starting backtest execution...")
        for i in range(len(self.data)):
            current_time = self.data.index[i]
            local_time = self._to_local(current_time)
            local_date = local_time.date()
            self._log_daily_summary(local_date)
            if self._open_trade is not None:
                exit_result = self._check_exit_conditions(i)
                if exit_result is not None:
                    exit_price, exit_reason = exit_result
                    self._close_trade_at_bar(i, exit_price, exit_reason)
            if self._open_trade is None:
                if not self.strategy.is_time_in_entry_window(current_time):
                    continue
                if not self.strategy.can_trade_today(current_time):
                    continue
                signal = self.strategy.generate_signal(i)
                if signal['valid']:
                    self._open_trade_at_bar(i, signal)
        if self._open_trade is not None:
            last_close = self.data.iloc[-1]['close']
            self._close_trade_at_bar(len(self.data) - 1, last_close, 'end_of_data')
        if self._current_day is not None:
            self._log_daily_summary(self._current_day)
        self._calculate_metrics()
        logger.info(f"Backtest complete: {len(self._trades)} trades executed")
        trades_df = pd.DataFrame([asdict(t) for t in self._trades])
        return {'_trades': trades_df, '_metrics': self._metrics, '_daily_log': self._daily_log}
    def _calculate_metrics(self):
        """Calculate aggregate backtest metrics."""
        if not self._trades:
            self._metrics = {'total_trades': 0, 'total_pnl': 0.0, 'win_rate': 0.0, 'avg_trade': 0.0, 'profit_factor': 0.0, 'max_drawdown': 0.0, 'roi': 0.0}
            return
        total_trades = len(self._trades)
        total_pnl = sum(t.pnl for t in self._trades if t.pnl is not None)
        wins = [t for t in self._trades if t.pnl is not None and t.pnl > 0]
        losses = [t for t in self._trades if t.pnl is not None and t.pnl < 0]
        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0.0
        avg_trade = total_pnl / total_trades if total_trades > 0 else 0.0
        gross_profit = sum(t.pnl for t in wins) if wins else 0.0
        gross_loss = abs(sum(t.pnl for t in losses)) if losses else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0.0)
        cumulative_pnl = [0]
        for t in self._trades:
            if t.pnl is not None:
                cumulative_pnl.append(cumulative_pnl[-1] + t.pnl)
        max_cumulative = cumulative_pnl[0]
        max_drawdown = 0.0
        for pnl in cumulative_pnl:
            if pnl > max_cumulative:
                max_cumulative = pnl
            drawdown = max_cumulative - pnl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        initial_capital = self.config.get('initial_capital', 1000.0)
        roi = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0.0
        self._metrics = {'total_trades': total_trades, 'total_pnl': total_pnl, 'win_rate': win_rate, 'avg_trade': avg_trade, 'profit_factor': profit_factor, 'max_drawdown': max_drawdown, 'roi': roi, 'gross_profit': gross_profit, 'gross_loss': gross_loss}
        logger.info(f"metrics_calculated: trades={total_trades}, pnl={total_pnl:.2f}, win_rate={win_rate:.1f}%, profit_factor={profit_factor:.2f}, max_dd={max_drawdown:.2f}, roi={roi:.1f}%")

