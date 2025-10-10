"""Command-line interface for One Trade system."""
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from config import load_config
from config.models import StrategyType
from one_trade.backtest import BacktestEngine
from one_trade.logging_config import setup_logging


console = Console()


@click.group()
@click.option("--config", default="config/config.yaml", help="Path to configuration file")
@click.option("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
@click.pass_context
def cli(ctx, config, log_level):
    """One Trade - Modular Backtesting and Trading System"""
    try:
        cfg = load_config(config)
        ctx.ensure_object(dict)
        ctx.obj["config"] = cfg
        log_file = cfg.logging.output.file_path if cfg.logging.output.file else None
        setup_logging(level=log_level, log_file=log_file, structured=(cfg.logging.format == "structured"), console_output=cfg.logging.output.console)
    except FileNotFoundError as e:
        console.print(f"[red]Error: Configuration file not found: {config}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--symbols", multiple=True, help="Symbols to update (default: all from config)")
@click.option("--timeframes", multiple=True, help="Timeframes to update (default: all from config)")
@click.pass_context
def update_data(ctx, symbols, timeframes):
    """Update market data incrementally"""
    config = ctx.obj["config"]
    engine = BacktestEngine(config)
    symbols_list = list(symbols) if symbols else None
    timeframes_list = list(timeframes) if timeframes else None
    console.print("[bold blue]Updating market data...[/bold blue]")
    try:
        engine.update_data(symbols=symbols_list, timeframes=timeframes_list)
        console.print("[bold green]Data update completed successfully![/bold green]")
    except Exception as e:
        console.print(f"[red]Error updating data: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("symbol")
@click.option("--start-date", help="Start date (YYYY-MM-DD)")
@click.option("--end-date", help="End date (YYYY-MM-DD)")
@click.option("--strategy", type=click.Choice(["current", "baseline"]), help="Strategy to use (overrides config)")
@click.pass_context
def backtest(ctx, symbol, start_date, end_date, strategy):
    """Run backtest for a symbol"""
    config = ctx.obj["config"]
    if strategy:
        config.strategy.type = StrategyType(strategy)
    engine = BacktestEngine(config)
    console.print(f"[bold blue]Running backtest for {symbol}...[/bold blue]")
    try:
        results = engine.run_backtest(symbol, start_date, end_date)
        if "error" in results:
            console.print(f"[red]Backtest failed: {results['error']}[/red]")
            sys.exit(1)
        metrics = results["metrics"]
        console.print("\n[bold green]Backtest completed successfully![/bold green]\n")
        _print_metrics_table(metrics, config.broker.initial_capital)
        console.print(f"\n[bold]Trades saved to:[/bold] {config.backtest.trades_output.path}")
    except Exception as e:
        console.print(f"[red]Error running backtest: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.pass_context
def check_data(ctx):
    """Check available data for all symbols"""
    config = ctx.obj["config"]
    engine = BacktestEngine(config)
    console.print("[bold blue]Checking available data...[/bold blue]\n")
    table = Table(title="Available Data", show_header=True, header_style="bold magenta")
    table.add_column("Symbol", style="cyan")
    table.add_column("Timeframe", style="cyan")
    table.add_column("Start Date", style="green")
    table.add_column("End Date", style="green")
    table.add_column("Candles", justify="right", style="yellow")
    for symbol in config.data.symbols:
        for timeframe in config.data.timeframes:
            try:
                start, end = engine.data_store.get_date_range(symbol, timeframe)
                if start and end:
                    data, _ = engine.data_store.read_data(symbol, timeframe)
                    candle_count = len(data) if data is not None else 0
                    table.add_row(symbol, timeframe, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), str(candle_count))
                else:
                    table.add_row(symbol, timeframe, "No data", "No data", "0")
            except Exception as e:
                table.add_row(symbol, timeframe, f"Error: {e}", "", "")
    console.print(table)


@cli.command()
@click.pass_context
def validate(ctx):
    """Validate configuration and setup"""
    config = ctx.obj["config"]
    console.print("[bold blue]Validating configuration...[/bold blue]\n")
    issues = []
    if not Path(config.data.storage_path).exists():
        issues.append(f"Data storage path does not exist: {config.data.storage_path}")
    if not config.data.symbols:
        issues.append("No symbols configured")
    if not config.data.timeframes:
        issues.append("No timeframes configured")
    if config.broker.initial_capital <= 0:
        issues.append("Initial capital must be positive")
    if issues:
        console.print("[red]Validation failed with the following issues:[/red]")
        for issue in issues:
            console.print(f"  - {issue}")
        sys.exit(1)
    else:
        console.print("[bold green]Configuration is valid![/bold green]")
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Exchange: {config.exchange.name.value}")
        console.print(f"  Symbols: {', '.join(config.data.symbols)}")
        console.print(f"  Timeframes: {', '.join(config.data.timeframes)}")
        console.print(f"  Strategy: {config.strategy.type.value}")
        console.print(f"  Initial Capital: ${config.broker.initial_capital:,.2f}")


def _print_metrics_table(metrics, initial_capital):
    """Print metrics in a formatted table"""
    table = Table(title="Performance Metrics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="yellow")
    table.add_row("Period", f"{metrics.start_date} to {metrics.end_date}")
    table.add_row("Duration (days)", str(metrics.duration_days))
    table.add_row("", "")
    table.add_row("Initial Capital", f"${initial_capital:,.2f}")
    table.add_row("Final Equity", f"${metrics.final_equity:,.2f}")
    return_color = "green" if metrics.total_return >= 0 else "red"
    table.add_row("Total Return", f"[{return_color}]${metrics.total_return:,.2f} ({metrics.total_return_pct:.2f}%)[/{return_color}]")
    table.add_row("CAGR", f"{metrics.cagr:.2f}%")
    table.add_row("Max Drawdown", f"${metrics.max_drawdown:,.2f} ({metrics.max_drawdown_pct:.2f}%)")
    table.add_row("Sharpe Ratio", f"{metrics.sharpe_ratio:.2f}")
    table.add_row("", "")
    table.add_row("Total Trades", str(metrics.total_trades))
    table.add_row("Winning Trades", str(metrics.winning_trades))
    table.add_row("Losing Trades", str(metrics.losing_trades))
    win_rate_color = "green" if metrics.win_rate >= 50 else "yellow"
    table.add_row("Win Rate", f"[{win_rate_color}]{metrics.win_rate:.2f}%[/{win_rate_color}]")
    table.add_row("Profit Factor", f"{metrics.profit_factor:.2f}")
    table.add_row("Expectancy", f"${metrics.expectancy:.2f}")
    table.add_row("", "")
    table.add_row("Average Win", f"${metrics.average_win:,.2f} ({metrics.average_win_pct:.2f}%)")
    table.add_row("Average Loss", f"${metrics.average_loss:,.2f} ({metrics.average_loss_pct:.2f}%)")
    table.add_row("Largest Win", f"${metrics.largest_win:,.2f}")
    table.add_row("Largest Loss", f"${metrics.largest_loss:,.2f}")
    table.add_row("", "")
    table.add_row("Total Fees", f"${metrics.total_fees:,.2f}")
    table.add_row("Daily PnL (Mean)", f"${metrics.daily_pnl_mean:.2f}")
    table.add_row("Daily PnL (Std)", f"${metrics.daily_pnl_std:.2f}")
    console.print(table)


if __name__ == "__main__":
    cli(obj={})

