"""Backtest engine integrating all components."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable

import pandas as pd
import pytz

from config.models import Config
from one_trade.broker_sim import BrokerSimulator, Trade
from one_trade.data_fetch import DataFetcher
from one_trade.data_store import DataStore
from one_trade.metrics import MetricsCalculator, PerformanceMetrics
from one_trade.scheduler import TradingScheduler
from one_trade.strategy import BaseStrategy, StrategyFactory


class BacktestEngine:
    """Main backtest engine that orchestrates all components."""
    
    def __init__(self, config: Config):
        """Initialize BacktestEngine. Args: config: Configuration object."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.data_store = DataStore(storage_path=config.data.storage_path, data_format=config.data.format, local_tz=config.timezone.local)
        self.data_fetcher = DataFetcher(exchange_config=config.exchange)
        self.scheduler = TradingScheduler(scheduling_config=config.scheduling.model_dump(), validation_config=config.validation.model_dump(), local_tz=config.timezone.local)
        self.broker = BrokerSimulator(broker_config=config.broker.model_dump(), risk_config=config.risk.model_dump(), local_tz=config.timezone.local)
        from config.models import StrategyType
        strategy_config = config.strategy.current.model_dump() if config.strategy.type == StrategyType.CURRENT else config.strategy.baseline.model_dump()
        strategy_type_value = config.strategy.type.value if hasattr(config.strategy.type, 'value') else config.strategy.type
        self.strategy: BaseStrategy = StrategyFactory.create_strategy(strategy_type_value, strategy_config)
        self.metrics_calculator = MetricsCalculator(initial_capital=config.broker.initial_capital, risk_free_rate=config.metrics.risk_free_rate)
        self.local_tz = pytz.timezone(config.timezone.local)
    
    def update_data(self, symbols: Optional[List[str]] = None, timeframes: Optional[List[str]] = None) -> None:
        """Update data incrementally for symbols and timeframes. Args: symbols: List of symbols to update. If None, uses config symbols. timeframes: List of timeframes to update. If None, uses config timeframes."""
        symbols = symbols or self.config.data.symbols
        timeframes = timeframes or self.config.data.timeframes
        self.logger.info(f"Updating data for {len(symbols)} symbols and {len(timeframes)} timeframes")
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    self.logger.info(f"Fetching {symbol} {timeframe}...")
                    existing_data, last_timestamp = self.data_store.read_data(symbol, timeframe)
                    new_data = self.data_fetcher.fetch_incremental(symbol, timeframe, last_timestamp)
                    if not new_data.empty:
                        source = f"{self.config.exchange.name.value}_{timeframe}"
                        self.data_store.write_data(symbol, timeframe, new_data, source)
                        self.logger.info(f"Saved {len(new_data)} new candles for {symbol} {timeframe}")
                    else:
                        self.logger.info(f"No new data for {symbol} {timeframe}")
                    if self.config.data.reconciliation.check_gaps:
                        gaps = self.data_store.check_gaps(symbol, timeframe, self.config.data.reconciliation.max_gap_minutes)
                        if gaps:
                            self.logger.warning(f"Found {len(gaps)} gaps in {symbol} {timeframe}")
                            if self.config.data.reconciliation.allow_corrections:
                                self.logger.info(f"Filling gaps for {symbol} {timeframe}...")
                                gap_data = self.data_fetcher.reconcile_gaps(symbol, timeframe, gaps)
                                if not gap_data.empty:
                                    source = f"{self.config.exchange.name.value}_{timeframe}_gap_fill"
                                    self.data_store.write_data(symbol, timeframe, gap_data, source)
                                    self.logger.info(f"Filled {len(gap_data)} candles for gaps")
                except Exception as e:
                    self.logger.error(f"Error updating {symbol} {timeframe}: {e}")
    
    def run_backtest(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, progress_callback: Optional[Callable[[Dict], None]] = None) -> Dict:
        """Run backtest for a single symbol. Returns: Dictionary with results including 'metrics' and 'elapsed_time', or error dict with 'error', 'error_code', and 'elapsed_time'."""
        start_time = datetime.now()
        try:
            start_date = start_date or self.config.backtest.start_date
            end_date = end_date or self.config.backtest.end_date or datetime.now().strftime("%Y-%m-%d")
            self.logger.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")
            if progress_callback:
                progress_callback({"stage": "loading_data", "message": f"Cargando datos para {symbol}...", "progress": 0})
            primary_timeframe = "15m"
            data_15m, _ = self.data_store.read_data_filtered(symbol, primary_timeframe, start_date, end_date)
            if data_15m is None or data_15m.empty:
                error_msg = f"No data available for {symbol} {primary_timeframe} in range {start_date} to {end_date}"
                self.logger.error(error_msg)
                return {"error": error_msg, "error_code": "NO_DATA", "symbol": symbol, "start_date": start_date, "end_date": end_date, "elapsed_time": (datetime.now() - start_time).total_seconds()}
            data_15m = data_15m.sort_values("timestamp_utc").set_index("timestamp_utc")
            self.logger.info(f"Loaded {len(data_15m)} candles for backtest")
            if progress_callback:
                progress_callback({"stage": "data_loaded", "message": f"Datos cargados: {len(data_15m)} velas", "progress": 10, "total_candles": len(data_15m)})
            self.broker.reset()
            equity_curve = []
            warmup_periods = self.config.backtest.warmup_periods
            total_iterations = len(data_15m) - warmup_periods
            if progress_callback:
                progress_callback({"stage": "processing", "message": "Iniciando procesamiento de velas...", "progress": 15, "candles_processed": 0, "total_candles": total_iterations})
            for idx in range(warmup_periods, len(data_15m)):
                current_timestamp = data_15m.index[idx]
                current_bar = data_15m.iloc[idx]
                current_equity = self.broker.get_equity()
                equity_curve.append({"timestamp": current_timestamp, "equity": current_equity})
                if progress_callback and (idx - warmup_periods) % max(1, total_iterations // 20) == 0:
                    candles_processed = idx - warmup_periods + 1
                    progress_pct = 15 + int((candles_processed / total_iterations) * 70)
                    trades_count = len(self.broker.get_trades())
                    progress_callback({"stage": "processing", "message": f"Procesando vela {candles_processed}/{total_iterations}", "progress": progress_pct, "candles_processed": candles_processed, "total_candles": total_iterations, "trades_count": trades_count})
                if self.broker.has_position():
                    position = self.broker.get_current_position()
                    hit, exit_price, reason = self.broker.check_stops(current_bar)
                    if hit:
                        trade = self.broker.close_position(current_timestamp, exit_price, reason)
                        if trade:
                            self.logger.info(f"Position closed: {trade.side.upper()} at {exit_price:.2f}, PnL: ${trade.pnl:.2f} ({trade.pnl_pct:.2f}%), Reason: {reason}")
                        continue
                    should_close, close_reason = self.scheduler.should_force_close(current_timestamp)
                    if should_close:
                        exit_price = current_bar["close"]
                        trade = self.broker.close_position(current_timestamp, exit_price, close_reason)
                        if trade:
                            self.logger.info(f"Position force closed: {trade.side.upper()} at {exit_price:.2f}, PnL: ${trade.pnl:.2f}, Reason: {close_reason}")
                        continue
                    should_exit, exit_reason = self.strategy.should_close(data_15m.reset_index(drop=True), idx, position.side, position.entry_price, position.entry_time_utc)
                    if should_exit:
                        exit_price = current_bar["close"]
                        trade = self.broker.close_position(current_timestamp, exit_price, exit_reason)
                        if trade:
                            self.logger.info(f"Position closed by strategy: {trade.side.upper()} at {exit_price:.2f}, PnL: ${trade.pnl:.2f}, Reason: {exit_reason}")
                else:
                    can_enter, entry_reason = self.scheduler.can_enter_trade(current_timestamp, symbol)
                    if not can_enter:
                        continue
                    signal = self.strategy.generate_signal(data_15m.reset_index(drop=True), idx)
                    if signal is None:
                        continue
                    success = self.broker.open_position(symbol=symbol, side=signal.side, timestamp_utc=current_timestamp, entry_price=signal.entry_price, stop_loss=signal.stop_loss, take_profit=signal.take_profit, reason=signal.reason)
                    if success:
                        self.scheduler.register_trade(current_timestamp, symbol)
                        position = self.broker.get_current_position()
                        self.logger.info(f"Position opened: {signal.side.upper()} at {signal.entry_price:.2f}, SL: {signal.stop_loss:.2f}, TP: {signal.take_profit:.2f}, Size: {position.size:.6f}, Reason: {signal.reason}")
            if self.broker.has_position():
                last_timestamp = data_15m.index[-1]
                last_bar = data_15m.iloc[-1]
                exit_price = last_bar["close"]
                trade = self.broker.close_position(last_timestamp, exit_price, "BACKTEST_END")
                if trade:
                    self.logger.info(f"Position closed at backtest end: PnL: ${trade.pnl:.2f}")
            if progress_callback:
                progress_callback({"stage": "calculating_metrics", "message": "Calculando métricas...", "progress": 90})
            trades = self.broker.get_trades()
            equity_df = pd.DataFrame(equity_curve)
            metrics = self.metrics_calculator.calculate_metrics(trades, equity_df)
            elapsed_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Backtest completed: {metrics.total_trades} trades, Final equity: ${metrics.final_equity:.2f}, Duration: {elapsed_time:.2f}s")
            if progress_callback:
                progress_callback({"stage": "completed", "message": f"Backtest completado: {metrics.total_trades} trades", "progress": 100, "elapsed_time": elapsed_time})
            if self.config.validation.check_trade_limit_daily:
                try:
                    self.scheduler.validate_daily_limit(symbol)
                    self.logger.info("Daily trade limit validation: PASSED")
                except AssertionError as e:
                    self.logger.error(f"Daily trade limit validation: FAILED - {e}")
                    if self.config.validation.strict_mode:
                        raise
            if self.config.backtest.save_trades and trades:
                self._save_trades(trades, symbol)
            if metrics is None:
                error_msg = "Metrics calculation returned None"
                self.logger.error(error_msg)
                return {"error": error_msg, "error_code": "METRICS_NONE", "symbol": symbol, "start_date": start_date, "end_date": end_date, "elapsed_time": elapsed_time}
            if not hasattr(metrics, 'total_trades'):
                error_msg = "Metrics object missing total_trades attribute"
                self.logger.error(error_msg)
                return {"error": error_msg, "error_code": "INVALID_METRICS", "symbol": symbol, "start_date": start_date, "end_date": end_date, "elapsed_time": elapsed_time}
            return {"symbol": symbol, "trades": trades, "metrics": metrics, "equity_curve": equity_df, "start_date": start_date, "end_date": end_date, "elapsed_time": elapsed_time}
        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Backtest failed: {type(e).__name__}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {"error": error_msg, "error_code": "EXCEPTION", "symbol": symbol if 'symbol' in locals() else "UNKNOWN", "start_date": start_date if 'start_date' in locals() else None, "end_date": end_date if 'end_date' in locals() else None, "elapsed_time": elapsed_time}
    
    def _save_trades(self, trades: List[Trade], symbol: str) -> None:
        """Save trades to CSV/Parquet. Args: trades: List of Trade objects. symbol: Trading symbol."""
        output_config = self.config.backtest.trades_output
        output_path = Path(output_config.path)
        output_path.mkdir(parents=True, exist_ok=True)
        trades_data = []
        for trade in trades:
            trades_data.append({"date": trade.exit_time_utc.date(), "symbol": trade.symbol, "side": trade.side, "entry_time_utc": trade.entry_time_utc, "entry_time_art": trade.entry_time_art, "entry_price": trade.entry_price, "exit_time_utc": trade.exit_time_utc, "exit_time_art": trade.exit_time_art, "exit_price": trade.exit_price, "pnl": trade.pnl, "pnl_pct": trade.pnl_pct, "fees": trade.fees, "entry_reason": trade.entry_reason, "exit_reason": trade.exit_reason, "stop_loss": trade.stop_loss, "take_profit": trade.take_profit, "size": trade.size})
        trades_df = pd.DataFrame(trades_data)
        safe_symbol = symbol.replace("/", "_")
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_config.format in ["csv", "both"]:
            csv_file = output_path / f"trades_{safe_symbol}_{timestamp_str}.csv"
            trades_df.to_csv(csv_file, index=False)
            self.logger.info(f"Saved trades to {csv_file}")
        if output_config.format in ["parquet", "both"]:
            parquet_file = output_path / f"trades_{safe_symbol}_{timestamp_str}.parquet"
            trades_df.to_parquet(parquet_file, index=False)
            self.logger.info(f"Saved trades to {parquet_file}")

