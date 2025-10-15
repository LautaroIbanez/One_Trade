"""
Backtesting engine for One Trade Decision App.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.strategies.base_strategy import BaseStrategy, Signal, SignalType
from app.services.strategy_service import strategy_service
from app.services.binance_service import BinanceService
from app.core.logging import get_logger

logger = get_logger(__name__)


class TradeSide(str, Enum):
    """Trade side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Trade:
    """Trade data class."""
    symbol: str
    side: TradeSide
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float = 1.0
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    entry_signal: Optional[str] = None
    exit_signal: Optional[str] = None
    confidence: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percentage: Optional[float] = None
    duration_hours: Optional[float] = None
    is_open: bool = True


@dataclass
class BacktestEngineResult:
    """Backtest result data class."""
    initial_capital: float
    final_capital: float
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    avg_trade_duration: float
    best_trade: float
    worst_trade: float
    profit_factor: float
    recovery_factor: float
    calmar_ratio: float
    sortino_ratio: float
    trades: List[Trade]
    equity_curve: pd.DataFrame


class BacktestingEngine:
    """Backtesting engine for trading strategies."""
    
    def __init__(self):
        """Initialize the backtesting engine."""
        self.commission_rate = 0.001  # 0.1% commission
        self.slippage_rate = 0.0005   # 0.05% slippage
    
    async def run_backtest(
        self,
        symbol: str,
        strategy_name: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 10000.0,
        strategy_params: Optional[Dict[str, Any]] = None,
        timeframe: str = "1d"
    ) -> BacktestEngineResult:
        """
        Run a backtest for a given strategy.
        
        Args:
            symbol: Trading symbol
            strategy_name: Name of the strategy
            start_date: Start date for backtest
            end_date: End date for backtest
            initial_capital: Initial capital
            strategy_params: Strategy parameters
            timeframe: Data timeframe
            
        Returns:
            BacktestResult with performance metrics
        """
        try:
            logger.info(f"Starting backtest for {symbol} with {strategy_name}")
            
            # Get strategy
            strategy = strategy_service.get_strategy(strategy_name)
            if not strategy:
                raise ValueError(f"Strategy {strategy_name} not found")
            
            # Update strategy parameters if provided
            if strategy_params:
                strategy.update_parameters(strategy_params)
            
            # Get market data
            market_data = await self._get_historical_data(
                symbol, start_date, end_date, timeframe
            )
            
            if market_data.empty:
                raise ValueError(f"No market data available for {symbol}")
            
            # Run backtest simulation
            trades = self._simulate_trading(
                market_data, strategy, symbol, initial_capital
            )
            
            # Calculate performance metrics
            result = self._calculate_performance_metrics(
                trades, initial_capital, start_date, end_date
            )
            
            logger.info(f"Backtest completed: {result.total_return:.2%} return")
            return result
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise
    
    async def _get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str
    ) -> pd.DataFrame:
        """Get historical market data."""
        try:
            async with BinanceService() as binance:
                # Calculate days needed
                days = (end_date - start_date).days + 1
                
                # Get data
                data = await binance.get_market_data(
                    symbol=symbol,
                    interval=timeframe,
                    days=days
                )
                
                # Filter by date range
                data = data[
                    (data.index >= start_date) & 
                    (data.index <= end_date)
                ]
                
                return data
                
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            raise
    
    def _simulate_trading(
        self,
        market_data: pd.DataFrame,
        strategy: BaseStrategy,
        symbol: str,
        initial_capital: float
    ) -> List[Trade]:
        """Simulate trading based on strategy signals."""
        trades = []
        current_capital = initial_capital
        position = None  # Current position
        
        logger.info(f"Simulating trading for {len(market_data)} data points")
        
        for i, (timestamp, row) in enumerate(market_data.iterrows()):
            # Get data up to current point
            current_data = market_data.iloc[:i+1]
            
            if len(current_data) < strategy.min_data_points:
                continue
            
            try:
                # Get strategy signals
                signals = strategy.analyze(current_data)
                
                if not signals:
                    continue
                
                # Use the latest signal
                signal = signals[-1]
                current_price = row['close']
                
                # Apply commission and slippage
                effective_price = self._apply_costs(current_price, signal.signal)
                
                # Handle position management
                if position is None:
                    # No position - look for entry signals
                    if signal.signal in [SignalType.BUY, SignalType.SELL]:
                        position = self._open_position(
                            symbol, signal, effective_price, current_capital
                        )
                        if position:
                            trades.append(position)
                            current_capital -= position.quantity * position.entry_price
                
                else:
                    # Have position - look for exit signals
                    if self._should_exit_position(position, signal):
                        self._close_position(
                            position, signal, effective_price, timestamp
                        )
                        current_capital += position.quantity * position.exit_price
                        position = None
                
            except Exception as e:
                logger.warning(f"Error processing signal at {timestamp}: {e}")
                continue
        
        # Close any remaining open position
        if position and position.is_open:
            last_price = market_data['close'].iloc[-1]
            self._close_position(position, None, last_price, market_data.index[-1])
            current_capital += position.quantity * position.exit_price
        
        logger.info(f"Simulation completed: {len(trades)} trades generated")
        return trades
    
    def _apply_costs(self, price: float, signal_type: SignalType) -> float:
        """Apply commission and slippage to price."""
        if signal_type == SignalType.BUY:
            return price * (1 + self.commission_rate + self.slippage_rate)
        else:
            return price * (1 - self.commission_rate - self.slippage_rate)
    
    def _open_position(
        self,
        symbol: str,
        signal: Signal,
        price: float,
        available_capital: float
    ) -> Optional[Trade]:
        """Open a new position."""
        # Calculate position size (use 95% of available capital)
        position_size = available_capital * 0.95
        quantity = position_size / price
        
        if quantity <= 0:
            return None
        
        trade_side = TradeSide.BUY if signal.signal == SignalType.BUY else TradeSide.SELL
        
        return Trade(
            symbol=symbol,
            side=trade_side,
            entry_price=price,
            quantity=quantity,
            entry_time=signal.timestamp,
            entry_signal=signal.reasoning,
            confidence=signal.confidence,
            is_open=True
        )
    
    def _should_exit_position(self, position: Trade, signal: Signal) -> bool:
        """Determine if position should be closed."""
        if not position.is_open:
            return False
        
        # Exit on opposite signal
        if position.side == TradeSide.BUY and signal.signal == SignalType.SELL:
            return True
        elif position.side == TradeSide.SELL and signal.signal == SignalType.BUY:
            return True
        
        # Exit on HOLD signal with high confidence
        if signal.signal == SignalType.HOLD and signal.confidence > 0.8:
            return True
        
        return False
    
    def _close_position(
        self,
        position: Trade,
        signal: Optional[Signal],
        price: float,
        timestamp: datetime
    ):
        """Close an open position."""
        position.exit_price = price
        position.exit_time = timestamp
        position.is_open = False
        
        if signal:
            position.exit_signal = signal.reasoning
        
        # Calculate P&L
        if position.side == TradeSide.BUY:
            position.pnl = (position.exit_price - position.entry_price) * position.quantity
        else:
            position.pnl = (position.entry_price - position.exit_price) * position.quantity
        
        position.pnl_percentage = (position.pnl / (position.entry_price * position.quantity)) * 100
        
        # Calculate duration
        if position.entry_time and position.exit_time:
            duration = position.exit_time - position.entry_time
            position.duration_hours = duration.total_seconds() / 3600
    
    def _calculate_performance_metrics(
        self,
        trades: List[Trade],
        initial_capital: float,
        start_date: datetime,
        end_date: datetime
    ) -> BacktestEngineResult:
        """Calculate performance metrics from trades."""
        if not trades:
            return self._empty_result(initial_capital)
        
        # Calculate final capital
        final_capital = initial_capital + sum(trade.pnl for trade in trades if trade.pnl)
        
        # Basic metrics
        total_return = (final_capital - initial_capital) / initial_capital
        
        # Annualized return
        years = (end_date - start_date).days / 365.25
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Trade statistics
        closed_trades = [t for t in trades if not t.is_open and t.pnl is not None]
        total_trades = len(closed_trades)
        
        if total_trades == 0:
            return self._empty_result(initial_capital)
        
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        # Trade returns
        trade_returns = [t.pnl_percentage / 100 for t in closed_trades if t.pnl_percentage is not None]
        
        if not trade_returns:
            return self._empty_result(initial_capital)
        
        # Risk metrics
        returns_series = pd.Series(trade_returns)
        sharpe_ratio = self._calculate_sharpe_ratio(returns_series, annualized_return)
        max_drawdown = self._calculate_max_drawdown(returns_series)
        
        # Trade duration
        durations = [t.duration_hours for t in closed_trades if t.duration_hours is not None]
        avg_trade_duration = np.mean(durations) if durations else 0
        
        # Best and worst trades
        best_trade = max(trade_returns) if trade_returns else 0
        worst_trade = min(trade_returns) if trade_returns else 0
        
        # Additional metrics
        profit_factor = self._calculate_profit_factor(closed_trades)
        recovery_factor = abs(total_return / max_drawdown) if max_drawdown != 0 else 0
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        sortino_ratio = self._calculate_sortino_ratio(returns_series, annualized_return)
        
        # Create equity curve
        equity_curve = self._create_equity_curve(trades, initial_capital)
        
        return BacktestEngineResult(
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=total_trades,
            avg_trade_duration=avg_trade_duration,
            best_trade=best_trade,
            worst_trade=worst_trade,
            profit_factor=profit_factor,
            recovery_factor=recovery_factor,
            calmar_ratio=calmar_ratio,
            sortino_ratio=sortino_ratio,
            trades=trades,
            equity_curve=equity_curve
        )
    
    def _empty_result(self, initial_capital: float) -> BacktestEngineResult:
        """Return empty result for no trades."""
        return BacktestEngineResult(
            initial_capital=initial_capital,
            final_capital=initial_capital,
            total_return=0.0,
            annualized_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            total_trades=0,
            avg_trade_duration=0.0,
            best_trade=0.0,
            worst_trade=0.0,
            profit_factor=0.0,
            recovery_factor=0.0,
            calmar_ratio=0.0,
            sortino_ratio=0.0,
            trades=[],
            equity_curve=pd.DataFrame()
        )
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, annualized_return: float) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns - 0.02 / 252  # Assume 2% risk-free rate
        return (excess_returns.mean() * 252) / (excess_returns.std() * np.sqrt(252)) if excess_returns.std() != 0 else 0.0
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown."""
        if len(returns) < 2:
            return 0.0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _calculate_profit_factor(self, trades: List[Trade]) -> float:
        """Calculate profit factor."""
        gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
        return gross_profit / gross_loss if gross_loss != 0 else 0.0
    
    def _calculate_sortino_ratio(self, returns: pd.Series, annualized_return: float) -> float:
        """Calculate Sortino ratio."""
        if len(returns) < 2:
            return 0.0
        
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        
        if downside_std == 0:
            return 0.0
        
        excess_return = annualized_return - 0.02  # Assume 2% risk-free rate
        return excess_return / (downside_std * np.sqrt(252))
    
    def _create_equity_curve(self, trades: List[Trade], initial_capital: float) -> pd.DataFrame:
        """Create equity curve from trades."""
        if not trades:
            return pd.DataFrame()
        
        equity_data = []
        current_capital = initial_capital
        
        for trade in trades:
            if not trade.is_open and trade.pnl is not None:
                current_capital += trade.pnl
                equity_data.append({
                    'timestamp': trade.exit_time,
                    'equity': current_capital,
                    'trade_pnl': trade.pnl
                })
        
        return pd.DataFrame(equity_data)


# Global backtesting engine instance
backtesting_engine = BacktestingEngine()
