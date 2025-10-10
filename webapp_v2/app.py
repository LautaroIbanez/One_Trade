"""One Trade v2.0 - Modern Web Interface with Dash."""
import json
import os
import glob
from datetime import datetime, timedelta
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State, dcc, html, dash_table
from dash.exceptions import PreventUpdate

from config import load_config
from one_trade.backtest import BacktestEngine

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME], suppress_callback_exceptions=True)
app.title = "One Trade v2.0 - Backtesting System"

config = load_config("config/config.yaml")
engine = BacktestEngine(config)

def load_saved_backtests():
    """Load all saved backtest results from CSV files."""
    backtests = []
    results_dir = Path("data_incremental/backtest_results")
    
    if not results_dir.exists():
        return backtests
    
    csv_files = glob.glob(str(results_dir / "trades_*.csv"))
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            if df.empty:
                continue
                
            # Extract info from filename
            filename = Path(csv_file).stem
            parts = filename.split('_')
            symbol = f"{parts[1]}/{parts[2]}"
            date_str = parts[3]
            time_str = parts[4]
            
            # Calculate basic metrics
            total_trades = len(df)
            winning_trades = len(df[df['pnl'] > 0])
            losing_trades = len(df[df['pnl'] <= 0])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            total_return = df['pnl'].sum()
            total_fees = df['fees'].sum()
            final_equity = config.broker.initial_capital + total_return
            total_return_pct = (total_return / config.broker.initial_capital) * 100
            
            backtests.append({
                'filename': filename,
                'filepath': csv_file,
                'symbol': symbol,
                'date': date_str,
                'time': time_str,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'final_equity': final_equity,
                'total_fees': total_fees,
                'created_at': datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S").isoformat()
            })
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")
            continue
    
    # Sort by creation date (newest first)
    backtests.sort(key=lambda x: x['created_at'], reverse=True)
    return backtests

def load_backtest_details(filepath):
    """Load detailed backtest data from CSV file."""
    try:
        df = pd.read_csv(filepath)
        return df.to_dict('records')
    except Exception as e:
        print(f"Error loading backtest details from {filepath}: {e}")
        return []

def create_layout():
    """Create the main layout."""
    return dbc.Container([
        dbc.Row([dbc.Col([html.H1([html.I(className="fas fa-chart-line me-3"), "One Trade v2.0"], className="text-primary mb-0"), html.P("Modern Backtesting System", className="text-muted")], width=8), dbc.Col([html.Div([html.Span("Exchange: ", className="fw-bold"), html.Span(config.exchange.name.value.upper(), className="badge bg-info me-2"), html.Span("Capital: ", className="fw-bold"), html.Span(f"${config.broker.initial_capital:,.0f}", className="badge bg-success")], className="text-end mt-2")], width=4)], className="mb-4"), 
        dbc.Tabs([
            dbc.Tab(label="Dashboard", tab_id="dashboard", children=[
                html.Div(id="dashboard-content", className="mt-4")
            ]),
            dbc.Tab(label="Backtest", tab_id="backtest", children=[
                html.Div(id="backtest-content", className="mt-4")
            ]),
            dbc.Tab(label="Data", tab_id="data", children=[
                html.Div(id="data-content", className="mt-4")
            ])
        ], id="tabs", active_tab="dashboard"),
        dcc.Store(id="backtest-results-store"),
        dcc.Interval(id="interval-component", interval=60000, n_intervals=0)
    ], fluid=True, className="py-4")

def create_dashboard_content(results=None, selected_backtest=None):
    """Create dashboard content."""
    # Load saved backtests
    saved_backtests = load_saved_backtests()
    
    if results is None and not saved_backtests:
        return dbc.Alert([html.I(className="fas fa-info-circle me-2"), "No backtest results yet. Go to the Backtest tab to run your first backtest."], color="info")
    
    # If no specific results provided, use the most recent saved backtest
    if results is None and saved_backtests:
        if selected_backtest:
            # Load selected backtest details
            selected_bt = next((bt for bt in saved_backtests if bt['filename'] == selected_backtest), None)
            if selected_bt:
                trades_data = load_backtest_details(selected_bt['filepath'])
                # Create mock results structure
                results = {
                    'symbol': selected_bt['symbol'],
                    'metrics': type('Metrics', (), {
                        'total_trades': selected_bt['total_trades'],
                        'winning_trades': selected_bt['winning_trades'],
                        'losing_trades': selected_bt['losing_trades'],
                        'win_rate': selected_bt['win_rate'],
                        'total_return': selected_bt['total_return'],
                        'total_return_pct': selected_bt['total_return_pct'],
                        'final_equity': selected_bt['final_equity'],
                        'total_fees': selected_bt['total_fees'],
                        'max_drawdown': 0,  # Would need to calculate from equity curve
                        'max_drawdown_pct': 0,
                        'cagr': 0,  # Would need to calculate from period
                        'sharpe_ratio': 0,  # Would need to calculate from daily returns
                        'profit_factor': 0,  # Would need to calculate
                        'expectancy': 0,  # Would need to calculate
                        'average_win': 0,  # Would need to calculate
                        'average_loss': 0,  # Would need to calculate
                        'average_win_pct': 0,
                        'average_loss_pct': 0,
                        'largest_win': 0,  # Would need to calculate
                        'largest_loss': 0,  # Would need to calculate
                        'daily_pnl_mean': 0,
                        'daily_pnl_std': 0,
                        'daily_pnl_min': 0,
                        'daily_pnl_max': 0
                    })(),
                    'trades': trades_data,
                    'equity_curve': None  # Would need to reconstruct from trades
                }
        else:
            # Use most recent backtest
            latest_bt = saved_backtests[0]
            trades_data = load_backtest_details(latest_bt['filepath'])
            results = {
                'symbol': latest_bt['symbol'],
                'metrics': type('Metrics', (), {
                    'total_trades': latest_bt['total_trades'],
                    'winning_trades': latest_bt['winning_trades'],
                    'losing_trades': latest_bt['losing_trades'],
                    'win_rate': latest_bt['win_rate'],
                    'total_return': latest_bt['total_return'],
                    'total_return_pct': latest_bt['total_return_pct'],
                    'final_equity': latest_bt['final_equity'],
                    'total_fees': latest_bt['total_fees'],
                    'max_drawdown': 0,
                    'max_drawdown_pct': 0,
                    'cagr': 0,
                    'sharpe_ratio': 0,
                    'profit_factor': 0,
                    'expectancy': 0,
                    'average_win': 0,
                    'average_loss': 0,
                    'average_win_pct': 0,
                    'average_loss_pct': 0,
                    'largest_win': 0,
                    'largest_loss': 0,
                    'daily_pnl_mean': 0,
                    'daily_pnl_std': 0,
                    'daily_pnl_min': 0,
                    'daily_pnl_max': 0
                })(),
                'trades': trades_data,
                'equity_curve': None
            }
    
    metrics = results["metrics"]
    
    # Create simple backtest info display
    backtest_info = html.Div([
        dbc.Alert([
            html.H5("📊 Backtests Guardados", className="alert-heading"),
            html.P(f"Se encontraron {len(saved_backtests)} backtests guardados."),
            html.Hr(),
            html.P("Para ejecutar un nuevo backtest, ve a la pestaña 'Backtest'."),
            html.P("Para ver datos disponibles, ve a la pestaña 'Data'.")
        ], color="info", className="mb-4")
    ])
    
    kpi_cards = dbc.Row([
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Total Return", className="text-muted mb-2"), html.H3([f"${metrics.total_return:,.2f}", html.Small(f" ({metrics.total_return_pct:+.2f}%)", className="text-muted fs-6")], className=f"mb-0 {'text-success' if metrics.total_return >= 0 else 'text-danger'}")])], className="shadow-sm")], width=3),
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Win Rate", className="text-muted mb-2"), html.H3(f"{metrics.win_rate:.1f}%", className="mb-0 text-info"), html.Small(f"{metrics.winning_trades}/{metrics.total_trades} trades", className="text-muted")])], className="shadow-sm")], width=3),
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Profit Factor", className="text-muted mb-2"), html.H3(f"{metrics.profit_factor:.2f}", className="mb-0 text-primary")])], className="shadow-sm")], width=3),
        dbc.Col([dbc.Card([dbc.CardBody([html.H6("Max Drawdown", className="text-muted mb-2"), html.H3(f"{metrics.max_drawdown_pct:.2f}%", className="mb-0 text-warning")])], className="shadow-sm")], width=3)
    ], className="mb-4")
    
    equity_data = results.get("equity_curve")
    if equity_data is not None and not equity_data.empty:
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(x=equity_data["timestamp"], y=equity_data["equity"], mode="lines", name="Equity", line=dict(color="#0d6efd", width=2)))
        fig_equity.add_hline(y=config.broker.initial_capital, line_dash="dash", line_color="gray", annotation_text="Initial Capital")
        fig_equity.update_layout(title="Equity Curve", xaxis_title="Time", yaxis_title="Equity ($)", hovermode="x unified", template="plotly_white", height=400)
        equity_chart = dcc.Graph(figure=fig_equity, config={"displayModeBar": False})
    else:
        equity_chart = dbc.Alert("No equity curve data available", color="warning")
    
    trades_table = create_trades_table(results["trades"]) if results["trades"] else dbc.Alert("No trades executed", color="info")
    
    return html.Div([
        backtest_info,
        kpi_cards,
        dbc.Row([dbc.Col([dbc.Card([dbc.CardBody([html.H5("Equity Curve", className="card-title"), equity_chart])], className="shadow-sm")], width=12)], className="mb-4"),
        dbc.Row([dbc.Col([dbc.Card([dbc.CardBody([html.H5("Recent Trades", className="card-title"), trades_table])], className="shadow-sm")], width=12)])
    ])

def create_trades_table(trades):
    """Create trades table."""
    if not trades:
        return html.P("No trades to display", className="text-muted")
    
    trades_data = []
    for trade in trades[:20]:
        trades_data.append({"Date": trade.exit_time_art.strftime("%Y-%m-%d"), "Time": trade.exit_time_art.strftime("%H:%M"), "Side": trade.side.upper(), "Entry": f"${trade.entry_price:,.2f}", "Exit": f"${trade.exit_price:,.2f}", "PnL": f"${trade.pnl:,.2f}", "PnL %": f"{trade.pnl_pct:+.2f}%", "Reason": trade.exit_reason})
    
    df = pd.DataFrame(trades_data)
    
    return dash_table.DataTable(data=df.to_dict("records"), columns=[{"name": i, "id": i} for i in df.columns], style_cell={"textAlign": "left", "padding": "10px", "fontSize": "14px"}, style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"}, style_data_conditional=[{"if": {"filter_query": "{PnL %} contains '+'", "column_id": "PnL %"}, "color": "#198754"}, {"if": {"filter_query": "{PnL %} contains '-'", "column_id": "PnL %"}, "color": "#dc3545"}], page_size=10, style_table={"overflowX": "auto"})

def create_backtest_content():
    """Create backtest form content."""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Run Backtest", className="card-title mb-4"),
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([dbc.Label("Symbol", className="fw-bold"), dcc.Dropdown(id="symbol-dropdown", options=[{"label": s, "value": s} for s in config.data.symbols], value=config.data.symbols[0], clearable=False)], width=6),
                            dbc.Col([dbc.Label("Strategy", className="fw-bold"), dcc.Dropdown(id="strategy-dropdown", options=[{"label": "Current (EMA/RSI/MACD)", "value": "current"}, {"label": "Baseline (Simple)", "value": "baseline"}], value="current", clearable=False)], width=6)
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col([dbc.Label("Start Date", className="fw-bold"), dbc.Input(id="start-date-input", type="date", value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))], width=6),
                            dbc.Col([dbc.Label("End Date", className="fw-bold"), dbc.Input(id="end-date-input", type="date", value=datetime.now().strftime("%Y-%m-%d"))], width=6)
                        ], className="mb-4"),
                        dbc.Button([html.I(className="fas fa-play me-2"), "Run Backtest"], id="run-backtest-btn", color="primary", size="lg", className="w-100")
                    ])
                ])
            ], className="shadow-sm mb-4"),
            html.Div(id="backtest-status")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Backtest Results", className="card-title"),
                    html.Div(id="backtest-results-display")
                ])
            ], className="shadow-sm")
        ], width=8)
    ])

def create_data_content():
    """Create data management content."""
    data_info = []
    for symbol in config.data.symbols:
        for timeframe in config.data.timeframes:
            start, end = engine.data_store.get_date_range(symbol, timeframe)
            if start and end:
                _, last_ts = engine.data_store.read_data(symbol, timeframe)
                candle_count = len(engine.data_store.read_data(symbol, timeframe)[0])
                data_info.append({"Symbol": symbol, "Timeframe": timeframe, "Start": start.strftime("%Y-%m-%d"), "End": end.strftime("%Y-%m-%d"), "Candles": candle_count, "Status": "✓"})
            else:
                data_info.append({"Symbol": symbol, "Timeframe": timeframe, "Start": "No data", "End": "No data", "Candles": 0, "Status": "✗"})
    
    df = pd.DataFrame(data_info)
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Data Status", className="card-title mb-4"),
                        dash_table.DataTable(data=df.to_dict("records"), columns=[{"name": i, "id": i} for i in df.columns], style_cell={"textAlign": "left", "padding": "10px"}, style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"}, style_data_conditional=[{"if": {"filter_query": "{Status} = ✓"}, "backgroundColor": "#d1e7dd"}, {"if": {"filter_query": "{Status} = ✗"}, "backgroundColor": "#f8d7da"}])
                    ])
                ], className="shadow-sm mb-4")
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Update Data", className="card-title mb-3"),
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([dbc.Label("Symbols"), dcc.Dropdown(id="update-symbols-dropdown", options=[{"label": s, "value": s} for s in config.data.symbols], value=config.data.symbols, multi=True)], width=6),
                                dbc.Col([dbc.Label("Timeframes"), dcc.Dropdown(id="update-timeframes-dropdown", options=[{"label": t, "value": t} for t in config.data.timeframes], value=config.data.timeframes, multi=True)], width=6)
                            ], className="mb-3"),
                            dbc.Button([html.I(className="fas fa-download me-2"), "Update Data"], id="update-data-btn", color="success", className="w-100")
                        ]),
                        html.Div(id="update-status", className="mt-3")
                    ])
                ], className="shadow-sm")
            ])
        ])
    ])

@app.callback(Output("dashboard-content", "children"), Output("backtest-content", "children"), Output("data-content", "children"), Input("tabs", "active_tab"), Input("backtest-results-store", "data"))
def render_tab_content(active_tab, stored_results):
    """Render content based on active tab."""
    results = json.loads(stored_results) if stored_results else None
    if results and "metrics" in results:
        metrics_dict = results["metrics"]
        from one_trade.metrics import PerformanceMetrics
        metrics = PerformanceMetrics(**metrics_dict)
        results["metrics"] = metrics
        if "trades" in results and results["trades"]:
            from one_trade.broker_sim import Trade
            trades = []
            for t_dict in results["trades"]:
                t_dict["entry_time_utc"] = pd.to_datetime(t_dict["entry_time_utc"])
                t_dict["entry_time_art"] = pd.to_datetime(t_dict["entry_time_art"])
                t_dict["exit_time_utc"] = pd.to_datetime(t_dict["exit_time_utc"])
                t_dict["exit_time_art"] = pd.to_datetime(t_dict["exit_time_art"])
                trades.append(Trade(**t_dict))
            results["trades"] = trades
        if "equity_curve" in results and results["equity_curve"]:
            results["equity_curve"] = pd.DataFrame(results["equity_curve"])
            results["equity_curve"]["timestamp"] = pd.to_datetime(results["equity_curve"]["timestamp"])
    
    if active_tab == "dashboard":
        # If no stored results, load from saved backtests
        if results is None:
            saved_backtests = load_saved_backtests()
            if saved_backtests:
                # Use the most recent backtest
                return create_dashboard_content(results=None), dash.no_update, dash.no_update
        return create_dashboard_content(results), dash.no_update, dash.no_update
    elif active_tab == "backtest":
        return dash.no_update, create_backtest_content(), dash.no_update
    elif active_tab == "data":
        return dash.no_update, dash.no_update, create_data_content()
    return dash.no_update, dash.no_update, dash.no_update

@app.callback(Output("backtest-results-store", "data"), Output("backtest-status", "children"), Input("run-backtest-btn", "n_clicks"), State("symbol-dropdown", "value"), State("strategy-dropdown", "value"), State("start-date-input", "value"), State("end-date-input", "value"), prevent_initial_call=True)
def run_backtest(n_clicks, symbol, strategy, start_date, end_date):
    """Run backtest and store results."""
    if not n_clicks:
        raise PreventUpdate
    
    try:
        from config.models import StrategyType
        config.strategy.type = StrategyType(strategy)
        engine_temp = BacktestEngine(config)
        
        status = dbc.Alert([html.I(className="fas fa-spinner fa-spin me-2"), f"Running backtest for {symbol}..."], color="info")
        
        results = engine_temp.run_backtest(symbol, start_date, end_date)
        
        if "error" in results:
            return None, dbc.Alert([html.I(className="fas fa-exclamation-triangle me-2"), f"Error: {results['error']}"], color="danger")
        
        results_serializable = {"symbol": results["symbol"], "start_date": results["start_date"], "end_date": results["end_date"]}
        
        metrics = results["metrics"]
        results_serializable["metrics"] = {
            "total_trades": metrics.total_trades, "winning_trades": metrics.winning_trades, "losing_trades": metrics.losing_trades, "win_rate": metrics.win_rate, "total_return": metrics.total_return, "total_return_pct": metrics.total_return_pct, "cagr": metrics.cagr, "max_drawdown": metrics.max_drawdown, "max_drawdown_pct": metrics.max_drawdown_pct, "sharpe_ratio": metrics.sharpe_ratio, "profit_factor": metrics.profit_factor, "expectancy": metrics.expectancy, "average_win": metrics.average_win, "average_loss": metrics.average_loss, "average_win_pct": metrics.average_win_pct, "average_loss_pct": metrics.average_loss_pct, "largest_win": metrics.largest_win, "largest_loss": metrics.largest_loss, "total_fees": metrics.total_fees, "final_equity": metrics.final_equity, "daily_pnl_mean": metrics.daily_pnl_mean, "daily_pnl_std": metrics.daily_pnl_std, "daily_pnl_min": metrics.daily_pnl_min, "daily_pnl_max": metrics.daily_pnl_max
        }
        
        if results["trades"]:
            results_serializable["trades"] = [{"symbol": t.symbol, "side": t.side, "entry_time_utc": t.entry_time_utc.isoformat(), "entry_time_art": t.entry_time_art.isoformat(), "entry_price": t.entry_price, "exit_time_utc": t.exit_time_utc.isoformat(), "exit_time_art": t.exit_time_art.isoformat(), "exit_price": t.exit_price, "size": t.size, "pnl": t.pnl, "pnl_pct": t.pnl_pct, "fees": t.fees, "entry_reason": t.entry_reason, "exit_reason": t.exit_reason, "stop_loss": t.stop_loss, "take_profit": t.take_profit} for t in results["trades"]]
        else:
            results_serializable["trades"] = []
        
        if results["equity_curve"] is not None and not results["equity_curve"].empty:
            results_serializable["equity_curve"] = results["equity_curve"].to_dict("records")
            for row in results_serializable["equity_curve"]:
                row["timestamp"] = row["timestamp"].isoformat()
        else:
            results_serializable["equity_curve"] = []
        
        success_message = dbc.Alert([html.I(className="fas fa-check-circle me-2"), f"Backtest completed! {metrics.total_trades} trades, Return: {metrics.total_return_pct:+.2f}%"], color="success")
        
        return json.dumps(results_serializable), success_message
    
    except Exception as e:
        return None, dbc.Alert([html.I(className="fas fa-exclamation-triangle me-2"), f"Error: {str(e)}"], color="danger")

@app.callback(Output("update-status", "children"), Input("update-data-btn", "n_clicks"), State("update-symbols-dropdown", "value"), State("update-timeframes-dropdown", "value"), prevent_initial_call=True)
def update_data(n_clicks, symbols, timeframes):
    """Update market data."""
    if not n_clicks:
        raise PreventUpdate
    
    try:
        engine.update_data(symbols, timeframes)
        return dbc.Alert([html.I(className="fas fa-check-circle me-2"), f"Data updated successfully for {len(symbols)} symbols and {len(timeframes)} timeframes"], color="success")
    except Exception as e:
        return dbc.Alert([html.I(className="fas fa-exclamation-triangle me-2"), f"Error: {str(e)}"], color="danger")

# Callbacks for backtest selector (will be added dynamically)

app.layout = create_layout()

if __name__ == "__main__":
    print("🚀 Starting One Trade v2.0 Web Interface...")
    print("📊 Dashboard available at: http://127.0.0.1:8050")
    print("⚡ Press Ctrl+C to stop")
    app.run(debug=True, host="127.0.0.1", port=8050)

