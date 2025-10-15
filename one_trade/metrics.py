"""Performance metrics calculation for backtest results."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np
import pandas as pd


@dataclass
class PerformanceMetrics:
    """Container for backtest performance metrics."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    total_return_pct: float
    cagr: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    profit_factor: float
    expectancy: float
    average_win: float
    average_loss: float
    average_win_pct: float
    average_loss_pct: float
    largest_win: float
    largest_loss: float
    total_fees: float
    final_equity: float
    daily_pnl_mean: float
    daily_pnl_std: float
    daily_pnl_min: float
    daily_pnl_max: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = None


class MetricsCalculator:
    """Calculates performance metrics from trades and equity curve."""
    
    def __init__(self, initial_capital: float, risk_free_rate: float = 0.02):
        """Initialize MetricsCalculator. Args: initial_capital: Starting capital. risk_free_rate: Annual risk-free rate for Sharpe (default 2%)."""
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
    
    def calculate_metrics(self, trades: List, equity_curve: Optional[pd.DataFrame] = None) -> PerformanceMetrics:
        """Calculate all performance metrics. Args: trades: List of Trade objects. equity_curve: Optional DataFrame with columns [timestamp, equity]. Returns: PerformanceMetrics object."""
        if not trades:
            return self._empty_metrics()
        trades_df = self._trades_to_dataframe(trades)
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df["pnl"] > 0])
        losing_trades = len(trades_df[trades_df["pnl"] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        total_pnl = trades_df["pnl"].sum()
        total_fees = trades_df["fees"].sum()
        final_equity = self.initial_capital + total_pnl
        total_return = total_pnl
        total_return_pct = (total_return / self.initial_capital) * 100
        start_date = trades_df["entry_time_utc"].min()
        end_date = trades_df["exit_time_utc"].max()
        duration_days = (end_date - start_date).days if start_date and end_date else 0
        cagr = self._calculate_cagr(final_equity, self.initial_capital, duration_days)
        if equity_curve is not None and not equity_curve.empty:
            max_dd, max_dd_pct = self._calculate_max_drawdown(equity_curve)
        else:
            equity_curve = self._build_equity_curve_from_trades(trades_df)
            max_dd, max_dd_pct = self._calculate_max_drawdown(equity_curve)
        sharpe = self._calculate_sharpe_ratio(trades_df, duration_days)
        profit_factor = self._calculate_profit_factor(trades_df)
        expectancy = self._calculate_expectancy(trades_df)
        wins = trades_df[trades_df["pnl"] > 0]["pnl"]
        losses = trades_df[trades_df["pnl"] < 0]["pnl"]
        wins_pct = trades_df[trades_df["pnl_pct"] > 0]["pnl_pct"]
        losses_pct = trades_df[trades_df["pnl_pct"] < 0]["pnl_pct"]
        average_win = wins.mean() if len(wins) > 0 else 0.0
        average_loss = losses.mean() if len(losses) > 0 else 0.0
        average_win_pct = wins_pct.mean() if len(wins_pct) > 0 else 0.0
        average_loss_pct = losses_pct.mean() if len(losses_pct) > 0 else 0.0
        largest_win = wins.max() if len(wins) > 0 else 0.0
        largest_loss = losses.min() if len(losses) > 0 else 0.0
        daily_pnl = self._aggregate_daily_pnl(trades_df)
        daily_pnl_mean = daily_pnl.mean() if len(daily_pnl) > 0 else 0.0
        daily_pnl_std = daily_pnl.std() if len(daily_pnl) > 0 else 0.0
        daily_pnl_min = daily_pnl.min() if len(daily_pnl) > 0 else 0.0
        daily_pnl_max = daily_pnl.max() if len(daily_pnl) > 0 else 0.0
        return PerformanceMetrics(total_trades=total_trades, winning_trades=winning_trades, losing_trades=losing_trades, win_rate=win_rate, total_return=total_return, total_return_pct=total_return_pct, cagr=cagr, max_drawdown=max_dd, max_drawdown_pct=max_dd_pct, sharpe_ratio=sharpe, profit_factor=profit_factor, expectancy=expectancy, average_win=average_win, average_loss=average_loss, average_win_pct=average_win_pct, average_loss_pct=average_loss_pct, largest_win=largest_win, largest_loss=largest_loss, total_fees=total_fees, final_equity=final_equity, daily_pnl_mean=daily_pnl_mean, daily_pnl_std=daily_pnl_std, daily_pnl_min=daily_pnl_min, daily_pnl_max=daily_pnl_max, start_date=start_date, end_date=end_date, duration_days=duration_days)
    
    def _trades_to_dataframe(self, trades: List) -> pd.DataFrame:
        """Convert list of Trade objects to DataFrame."""
        trade_dicts = []
        for trade in trades:
            trade_dicts.append({"symbol": trade.symbol, "side": trade.side, "entry_time_utc": trade.entry_time_utc, "entry_time_art": trade.entry_time_art, "entry_price": trade.entry_price, "exit_time_utc": trade.exit_time_utc, "exit_time_art": trade.exit_time_art, "exit_price": trade.exit_price, "size": trade.size, "pnl": trade.pnl, "pnl_pct": trade.pnl_pct, "fees": trade.fees, "entry_reason": trade.entry_reason, "exit_reason": trade.exit_reason, "stop_loss": trade.stop_loss, "take_profit": trade.take_profit})
        return pd.DataFrame(trade_dicts)
    
    def _calculate_cagr(self, final_value: float, initial_value: float, days: int) -> float:
        """Calculate Compound Annual Growth Rate."""
        if days <= 0 or initial_value <= 0:
            return 0.0
        years = days / 365.25
        if years <= 0:
            return 0.0
        cagr = ((final_value / initial_value) ** (1 / years) - 1) * 100
        return cagr
    
    def _calculate_max_drawdown(self, equity_curve: pd.DataFrame) -> tuple[float, float]:
        """Calculate maximum drawdown. Args: equity_curve: DataFrame with 'equity' column. Returns: (max_drawdown_absolute, max_drawdown_percentage)."""
        if equity_curve.empty or "equity" not in equity_curve.columns:
            return 0.0, 0.0
        equity = equity_curve["equity"]
        cummax = equity.expanding().max()
        drawdown = equity - cummax
        max_dd = drawdown.min()
        max_dd_at_idx = drawdown.idxmin()
        peak_equity = cummax.loc[max_dd_at_idx]
        max_dd_pct = (max_dd / peak_equity * 100) if peak_equity > 0 else 0.0
        return abs(max_dd), abs(max_dd_pct)
    
    def _calculate_sharpe_ratio(self, trades_df: pd.DataFrame, duration_days: int) -> float:
        """Calculate Sharpe Ratio (simple version using trade returns)."""
        if trades_df.empty or duration_days <= 0:
            return 0.0
        returns = trades_df["pnl"] / self.initial_capital
        if len(returns) < 2:
            return 0.0
        mean_return = returns.mean()
        std_return = returns.std()
        if std_return == 0:
            return 0.0
        years = duration_days / 365.25
        risk_free_rate_per_trade = self.risk_free_rate / len(returns)
        sharpe = (mean_return - risk_free_rate_per_trade) / std_return
        sharpe_annualized = sharpe * np.sqrt(len(returns) / years) if years > 0 else sharpe
        return sharpe_annualized
    
    def _calculate_profit_factor(self, trades_df: pd.DataFrame) -> float:
        """Calculate Profit Factor (gross profit / gross loss)."""
        if trades_df.empty:
            return 0.0
        gross_profit = trades_df[trades_df["pnl"] > 0]["pnl"].sum()
        gross_loss = abs(trades_df[trades_df["pnl"] < 0]["pnl"].sum())
        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0
        return gross_profit / gross_loss
    
    def _calculate_expectancy(self, trades_df: pd.DataFrame) -> float:
        """Calculate expectancy (average PnL per trade)."""
        if trades_df.empty:
            return 0.0
        return trades_df["pnl"].mean()
    
    def _aggregate_daily_pnl(self, trades_df: pd.DataFrame) -> pd.Series:
        """Aggregate PnL by day."""
        if trades_df.empty:
            return pd.Series(dtype=float)
        trades_df = trades_df.copy()
        trades_df["exit_date"] = pd.to_datetime(trades_df["exit_time_utc"]).dt.date
        daily_pnl = trades_df.groupby("exit_date")["pnl"].sum()
        return daily_pnl
    
    def _build_equity_curve_from_trades(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """Build equity curve from trades."""
        if trades_df.empty:
            return pd.DataFrame(columns=["timestamp", "equity"])
        trades_df = trades_df.sort_values("exit_time_utc")
        equity_curve = []
        current_equity = self.initial_capital
        for _, trade in trades_df.iterrows():
            current_equity += trade["pnl"]
            equity_curve.append({"timestamp": trade["exit_time_utc"], "equity": current_equity})
        return pd.DataFrame(equity_curve)
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty metrics object."""
        return PerformanceMetrics(total_trades=0, winning_trades=0, losing_trades=0, win_rate=0.0, total_return=0.0, total_return_pct=0.0, cagr=0.0, max_drawdown=0.0, max_drawdown_pct=0.0, sharpe_ratio=0.0, profit_factor=0.0, expectancy=0.0, average_win=0.0, average_loss=0.0, average_win_pct=0.0, average_loss_pct=0.0, largest_win=0.0, largest_loss=0.0, total_fees=0.0, final_equity=self.initial_capital, daily_pnl_mean=0.0, daily_pnl_std=0.0, daily_pnl_min=0.0, daily_pnl_max=0.0)
    
    def print_metrics(self, metrics: PerformanceMetrics) -> None:
        """Print metrics in formatted output."""
        print("\n" + "="*60)
        print("BACKTEST PERFORMANCE METRICS")
        print("="*60)
        print(f"\nPeriod: {metrics.start_date} to {metrics.end_date}")
        print(f"Duration: {metrics.duration_days} days\n")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Equity: ${metrics.final_equity:,.2f}")
        print(f"Total Return: ${metrics.total_return:,.2f} ({metrics.total_return_pct:.2f}%)")
        print(f"CAGR: {metrics.cagr:.2f}%")
        print(f"Max Drawdown: ${metrics.max_drawdown:,.2f} ({metrics.max_drawdown_pct:.2f}%)")
        print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"\nTotal Trades: {metrics.total_trades}")
        print(f"Winning Trades: {metrics.winning_trades}")
        print(f"Losing Trades: {metrics.losing_trades}")
        print(f"Win Rate: {metrics.win_rate:.2f}%")
        print(f"Profit Factor: {metrics.profit_factor:.2f}")
        print(f"Expectancy: ${metrics.expectancy:.2f}")
        print(f"\nAverage Win: ${metrics.average_win:.2f} ({metrics.average_win_pct:.2f}%)")
        print(f"Average Loss: ${metrics.average_loss:.2f} ({metrics.average_loss_pct:.2f}%)")
        print(f"Largest Win: ${metrics.largest_win:.2f}")
        print(f"Largest Loss: ${metrics.largest_loss:.2f}")
        print(f"\nTotal Fees: ${metrics.total_fees:.2f}")
        print(f"\nDaily PnL - Mean: ${metrics.daily_pnl_mean:.2f}")
        print(f"Daily PnL - Std: ${metrics.daily_pnl_std:.2f}")
        print(f"Daily PnL - Min: ${metrics.daily_pnl_min:.2f}")
        print(f"Daily PnL - Max: ${metrics.daily_pnl_max:.2f}")
        print("="*60 + "\n")









