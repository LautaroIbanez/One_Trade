"""Example usage of One Trade system programmatically."""
from datetime import datetime
from config import load_config
from one_trade.backtest import BacktestEngine
from one_trade.logging_config import setup_logging


def main():
    """Example: Run a backtest programmatically."""
    print("="*60)
    print("One Trade v2.0 - Example Usage")
    print("="*60 + "\n")
    
    # 1. Load and validate configuration
    print("1. Loading configuration...")
    config = load_config("config/config.yaml")
    print(f"   ✓ Loaded config: {len(config.data.symbols)} symbols, {len(config.data.timeframes)} timeframes\n")
    
    # 2. Setup logging
    print("2. Setting up logging...")
    setup_logging(level=config.logging.level, log_file=config.logging.output.file_path if config.logging.output.file else None, structured=(config.logging.format == "structured"), console_output=config.logging.output.console)
    print("   ✓ Logging configured\n")
    
    # 3. Initialize backtest engine
    print("3. Initializing backtest engine...")
    engine = BacktestEngine(config)
    print("   ✓ Engine initialized with:")
    print(f"      - Exchange: {config.exchange.name.value}")
    print(f"      - Strategy: {config.strategy.type.value}")
    print(f"      - Initial capital: ${config.broker.initial_capital:,.2f}\n")
    
    # 4. Optional: Update data
    print("4. Checking data availability...")
    symbol = "BTC/USDT"
    timeframe = "15m"
    
    start, end = engine.data_store.get_date_range(symbol, timeframe)
    if start and end:
        print(f"   ✓ Data available: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    else:
        print(f"   ⚠ No data found for {symbol} {timeframe}")
        print(f"   Run: python -m cli.main update-data --symbols {symbol} --timeframes {timeframe}\n")
        return
    print()
    
    # 5. Run backtest
    print("5. Running backtest...")
    print(f"   Symbol: {symbol}")
    print(f"   Period: {config.backtest.start_date} to {config.backtest.end_date or 'today'}")
    print(f"   Strategy: {config.strategy.type.value}")
    print()
    
    results = engine.run_backtest(symbol=symbol, start_date=config.backtest.start_date, end_date=config.backtest.end_date)
    
    if "error" in results:
        print(f"   ✗ Backtest failed: {results['error']}\n")
        return
    
    # 6. Display results
    print("="*60)
    print("BACKTEST RESULTS")
    print("="*60 + "\n")
    
    metrics = results["metrics"]
    
    print(f"Period: {metrics.start_date} to {metrics.end_date}")
    print(f"Duration: {metrics.duration_days} days\n")
    
    print("Performance:")
    print(f"  Initial Capital:  ${config.broker.initial_capital:>12,.2f}")
    print(f"  Final Equity:     ${metrics.final_equity:>12,.2f}")
    print(f"  Total Return:     ${metrics.total_return:>12,.2f} ({metrics.total_return_pct:>6.2f}%)")
    print(f"  CAGR:             {metrics.cagr:>13.2f}%")
    print(f"  Max Drawdown:     ${metrics.max_drawdown:>12,.2f} ({metrics.max_drawdown_pct:>6.2f}%)")
    print(f"  Sharpe Ratio:     {metrics.sharpe_ratio:>13.2f}\n")
    
    print("Trade Statistics:")
    print(f"  Total Trades:     {metrics.total_trades:>13}")
    print(f"  Winning Trades:   {metrics.winning_trades:>13}")
    print(f"  Losing Trades:    {metrics.losing_trades:>13}")
    print(f"  Win Rate:         {metrics.win_rate:>12.2f}%")
    print(f"  Profit Factor:    {metrics.profit_factor:>13.2f}")
    print(f"  Expectancy:       ${metrics.expectancy:>12.2f}\n")
    
    print("Risk Metrics:")
    print(f"  Average Win:      ${metrics.average_win:>12,.2f} ({metrics.average_win_pct:>6.2f}%)")
    print(f"  Average Loss:     ${metrics.average_loss:>12,.2f} ({metrics.average_loss_pct:>6.2f}%)")
    print(f"  Largest Win:      ${metrics.largest_win:>12,.2f}")
    print(f"  Largest Loss:     ${metrics.largest_loss:>12,.2f}")
    print(f"  Total Fees:       ${metrics.total_fees:>12,.2f}\n")
    
    print("="*60)
    
    # 7. Show sample trades
    if results["trades"]:
        print("\nSample Trades (first 5):")
        print("-"*60)
        for i, trade in enumerate(results["trades"][:5], 1):
            print(f"{i}. {trade.side.upper()} @ {trade.entry_price:.2f} → {trade.exit_price:.2f}")
            print(f"   Entry: {trade.entry_time_art.strftime('%Y-%m-%d %H:%M')} ART")
            print(f"   Exit:  {trade.exit_time_art.strftime('%Y-%m-%d %H:%M')} ART")
            print(f"   PnL:   ${trade.pnl:>8.2f} ({trade.pnl_pct:>6.2f}%)")
            print(f"   Reason: {trade.entry_reason} → {trade.exit_reason}")
            print()
    
    print("✓ Backtest completed successfully!")
    print(f"\nTrades saved to: {config.backtest.trades_output.path}\n")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("Make sure config/config.yaml exists and data is available.\n")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()









