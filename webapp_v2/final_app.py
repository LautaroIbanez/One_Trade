"""One Trade v2.0 - Final Working Web Interface."""
import json
import glob
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State, dcc, html, callback_context
from dash.exceptions import PreventUpdate

from config import load_config
from one_trade.backtest import BacktestEngine
from config.models import StrategyType

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
app.title = "One Trade v2.0 - Final Backtesting System"

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

# Create layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-chart-line me-3"), 
                "One Trade v2.0"
            ], className="text-primary mb-0"),
            html.P("Final Backtesting System", className="text-muted")
        ], width=8),
        dbc.Col([
            html.Div([
                html.Span("Exchange: ", className="fw-bold"),
                html.Span(config.exchange.name.value.upper(), className="badge bg-info me-2"),
                html.Span("Capital: ", className="fw-bold"),
                html.Span(f"${config.broker.initial_capital:,.0f}", className="badge bg-success")
            ], className="text-end mt-2")
        ], width=4)
    ], className="mb-4"),
    
    # Navigation
    dbc.Tabs([
        dbc.Tab(label="📊 Dashboard", tab_id="dashboard", children=[
            html.Div(id="dashboard-content")
        ]),
        dbc.Tab(label="⚙️ Backtest", tab_id="backtest", children=[
            html.Div(id="backtest-content")
        ]),
        dbc.Tab(label="📁 Data", tab_id="data", children=[
            html.Div(id="data-content")
        ])
    ], id="tabs", active_tab="dashboard"),
    
    # Hidden stores and interval for auto-refresh
    dcc.Store(id="backtest-status"),
    dcc.Store(id="data-status"),
    dcc.Interval(id="auto-refresh", interval=2000, n_intervals=0)
    
], fluid=True, className="py-4")

def create_dashboard_content():
    """Create dashboard content with saved backtests."""
    saved_backtests = load_saved_backtests()
    
    if not saved_backtests:
        return dbc.Alert([
            html.H4("📊 No Backtests Found", className="alert-heading"),
            html.P("No se encontraron backtests guardados. Ejecuta un backtest primero desde la pestaña 'Backtest'.")
        ], color="warning")
    
    # Create backtest cards
    backtest_cards = []
    for bt in saved_backtests[:10]:  # Show latest 10
        color = "success" if bt['total_return'] > 0 else "danger"
        icon = "📈" if bt['total_return'] > 0 else "📉"
        
        backtest_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6([
                        html.I(className=f"fas fa-{'arrow-up' if bt['total_return'] > 0 else 'arrow-down'} me-2"),
                        f"{icon} {bt['symbol']} - {bt['date']} {bt['time']}"
                    ], className="card-title"),
                    html.P([
                        html.Strong(f"Trades: {bt['total_trades']}"),
                        " | ",
                        html.Strong(f"Win Rate: {bt['win_rate']:.1f}%"),
                        " | ",
                        html.Strong(f"Return: {bt['total_return_pct']:+.2f}%")
                    ]),
                    html.Small([
                        f"Final Equity: ${bt['final_equity']:,.2f} | ",
                        f"Fees: ${bt['total_fees']:.2f}"
                    ], className="text-muted")
                ])
            ], color=color, outline=True, className="mb-3")
        )
    
    # Create summary metrics
    total_backtests = len(saved_backtests)
    profitable_backtests = len([bt for bt in saved_backtests if bt['total_return'] > 0])
    total_return = sum([bt['total_return'] for bt in saved_backtests])
    avg_win_rate = sum([bt['win_rate'] for bt in saved_backtests]) / total_backtests if total_backtests > 0 else 0
    
    summary_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Backtests", className="text-muted mb-2"),
                    html.H3(f"{total_backtests}", className="mb-0 text-primary")
                ])
            ], className="shadow-sm")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Profitable", className="text-muted mb-2"),
                    html.H3(f"{profitable_backtests}", className="mb-0 text-success")
                ])
            ], className="shadow-sm")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Return", className="text-muted mb-2"),
                    html.H3(f"${total_return:.2f}", className=f"mb-0 {'text-success' if total_return >= 0 else 'text-danger'}")
                ])
            ], className="shadow-sm")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Avg Win Rate", className="text-muted mb-2"),
                    html.H3(f"{avg_win_rate:.1f}%", className="mb-0 text-info")
                ])
            ], className="shadow-sm")
        ], width=3)
    ], className="mb-4")
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-sync-alt me-2"),
                    "Refresh Backtests"
                ], id="refresh-backtests-btn", color="primary", className="mb-3")
            ], width=12)
        ]),
        
        summary_cards,
        
        dbc.Row([
            dbc.Col([
                html.H5("📊 Backtests Detallados", className="mb-3")
            ], width=12)
        ]),
        
        html.Div(backtest_cards)
    ])

def create_backtest_content():
    """Create interactive backtest form."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("⚙️ Ejecutar Backtest", className="card-title mb-4"),
                        
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Símbolo", html_for="symbol-select"),
                                    dcc.Dropdown(
                                        id="symbol-select",
                                        options=[
                                            {"label": "BTC/USDT", "value": "BTC/USDT"},
                                            {"label": "ETH/USDT", "value": "ETH/USDT"}
                                        ],
                                        value="BTC/USDT"
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Estrategia", html_for="strategy-select"),
                                    dcc.Dropdown(
                                        id="strategy-select",
                                        options=[
                                            {"label": "Baseline (EMA/RSI)", "value": "baseline"},
                                            {"label": "Current (EMA/RSI/MACD)", "value": "current"}
                                        ],
                                        value="baseline"
                                    )
                                ], width=6)
                            ], className="mb-3"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Fecha Inicio", html_for="start-date"),
                                    dcc.DatePickerSingle(
                                        id="start-date",
                                        date="2024-01-01",
                                        display_format="YYYY-MM-DD"
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Fecha Fin", html_for="end-date"),
                                    dcc.DatePickerSingle(
                                        id="end-date",
                                        date="2025-10-09",
                                        display_format="YYYY-MM-DD"
                                    )
                                ], width=6)
                            ], className="mb-4"),
                            
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button([
                                        html.I(className="fas fa-play me-2"),
                                        "Ejecutar Backtest"
                                    ], id="run-backtest-btn", color="success", size="lg", className="w-100")
                                ], width=12)
                            ])
                        ])
                    ])
                ], className="shadow")
            ], width=8),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📊 Estado del Backtest", className="card-title"),
                        html.Div(id="backtest-progress", children=[
                            dbc.Alert("Listo para ejecutar backtest", color="info")
                        ])
                    ])
                ], className="shadow")
            ], width=4)
        ], className="mb-4"),
        
        html.Div(id="backtest-results")
    ])

def create_data_content():
    """Create interactive data management."""
    try:
        data_info = []
        for symbol in config.data.symbols:
            for timeframe in config.data.timeframes:
                start, end = engine.data_store.get_date_range(symbol, timeframe)
                if start and end:
                    candle_count = len(engine.data_store.read_data(symbol, timeframe)[0])
                    data_info.append({
                        "Symbol": symbol, 
                        "Timeframe": timeframe, 
                        "Start": start.strftime("%Y-%m-%d"), 
                        "End": end.strftime("%Y-%m-%d"), 
                        "Candles": candle_count, 
                        "Status": "✓"
                    })
                else:
                    data_info.append({
                        "Symbol": symbol, 
                        "Timeframe": timeframe, 
                        "Start": "No data", 
                        "End": "No data", 
                        "Candles": 0, 
                        "Status": "✗"
                    })
        
        df = pd.DataFrame(data_info)
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Estado de Datos", className="card-title mb-4"),
                            dbc.Table.from_dataframe(
                                df, 
                                striped=True, 
                                bordered=True, 
                                hover=True
                            )
                        ])
                    ], className="shadow mb-4")
                ], width=8),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("🔄 Actualizar Datos", className="card-title mb-3"),
                            
                            dbc.Form([
                                dbc.Label("Símbolos", html_for="update-symbols"),
                                dcc.Dropdown(
                                    id="update-symbols",
                                    options=[
                                        {"label": "BTC/USDT", "value": "BTC/USDT"},
                                        {"label": "ETH/USDT", "value": "ETH/USDT"}
                                    ],
                                    value=["BTC/USDT"],
                                    multi=True
                                ),
                                
                                dbc.Label("Timeframes", html_for="update-timeframes", className="mt-3"),
                                dcc.Dropdown(
                                    id="update-timeframes",
                                    options=[
                                        {"label": "15m", "value": "15m"},
                                        {"label": "1d", "value": "1d"}
                                    ],
                                    value=["15m"],
                                    multi=True
                                ),
                                
                                dbc.Button([
                                    html.I(className="fas fa-download me-2"),
                                    "Actualizar Datos"
                                ], id="update-data-btn", color="primary", className="w-100 mt-3")
                            ])
                        ])
                    ], className="shadow mb-4"),
                    
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("📈 Estado de Actualización", className="card-title"),
                            html.Div(id="data-progress", children=[
                                dbc.Alert("Listo para actualizar datos", color="info")
                            ])
                        ])
                    ], className="shadow")
                ], width=4)
            ])
        ])
        
    except Exception as e:
        return dbc.Alert([
            html.H4("❌ Error", className="alert-heading"),
            html.P(f"Error al cargar datos: {str(e)}")
        ], color="danger")

# Callbacks
@app.callback(
    Output("dashboard-content", "children"),
    [Input("tabs", "active_tab"),
     Input("auto-refresh", "n_intervals"),
     Input("refresh-backtests-btn", "n_clicks")]
)
def render_dashboard_content(active_tab, n_intervals, refresh_clicks):
    if active_tab == "dashboard":
        return create_dashboard_content()
    return ""

@app.callback(
    Output("backtest-content", "children"),
    Input("tabs", "active_tab")
)
def render_backtest_content(active_tab):
    if active_tab == "backtest":
        return create_backtest_content()
    return ""

@app.callback(
    Output("data-content", "children"),
    Input("tabs", "active_tab")
)
def render_data_content(active_tab):
    if active_tab == "data":
        return create_data_content()
    return ""

@app.callback(
    [Output("backtest-progress", "children"),
     Output("backtest-results", "children")],
    Input("run-backtest-btn", "n_clicks"),
    [State("symbol-select", "value"),
     State("strategy-select", "value"),
     State("start-date", "date"),
     State("end-date", "date")]
)
def run_backtest(n_clicks, symbol, strategy, start_date, end_date):
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    try:
        config.strategy.type = StrategyType(strategy)
        engine_temp = BacktestEngine(config)
        
        progress = dbc.Alert([
            html.I(className="fas fa-spinner fa-spin me-2"),
            f"Ejecutando backtest para {symbol} con estrategia {strategy}..."
        ], color="info")
        
        results = engine_temp.run_backtest(symbol, start_date, end_date)
        
        if "error" in results:
            error_alert = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Error: {results['error']}"
            ], color="danger")
            return error_alert, ""
        
        metrics = results["metrics"]
        success_alert = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            f"Backtest completado! {metrics.total_trades} trades, Return: {metrics.total_return_pct:+.2f}%"
        ], color="success")
        
        results_content = dbc.Card([
            dbc.CardBody([
                html.H5("📊 Resultados del Backtest", className="card-title"),
                dbc.Row([
                    dbc.Col([
                        html.H6("Total Return"),
                        html.H4(f"${metrics.total_return:.2f}", 
                               className="text-success" if metrics.total_return >= 0 else "text-danger")
                    ], width=3),
                    dbc.Col([
                        html.H6("Win Rate"),
                        html.H4(f"{metrics.win_rate:.1f}%", className="text-info")
                    ], width=3),
                    dbc.Col([
                        html.H6("Total Trades"),
                        html.H4(f"{metrics.total_trades}", className="text-primary")
                    ], width=3),
                    dbc.Col([
                        html.H6("Profit Factor"),
                        html.H4(f"{metrics.profit_factor:.2f}", className="text-warning")
                    ], width=3)
                ]),
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "Los resultados se han guardado automáticamente. Ve al Dashboard para ver todos tus backtests."
                ], color="info", className="mt-3")
            ])
        ])
        
        return success_alert, results_content
    
    except Exception as e:
        error_alert = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error: {str(e)}"
        ], color="danger")
        return error_alert, ""

@app.callback(
    [Output("data-progress", "children"),
     Output("update-data-btn", "disabled")],
    Input("update-data-btn", "n_clicks"),
    [State("update-symbols", "value"),
     State("update-timeframes", "value")]
)
def update_data(n_clicks, symbols, timeframes):
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    try:
        progress = dbc.Alert([
            html.I(className="fas fa-spinner fa-spin me-2"),
            f"Actualizando datos para {len(symbols)} símbolos y {len(timeframes)} timeframes..."
        ], color="info")
        
        engine.update_data(symbols, timeframes)
        
        success_alert = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "Datos actualizados exitosamente!"
        ], color="success")
        
        return success_alert, False
        
    except Exception as e:
        error_alert = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error: {str(e)}"
        ], color="danger")
        return error_alert, False

if __name__ == "__main__":
    print("🚀 Starting One Trade v2.0 Final Web Interface...")
    print("📊 Dashboard available at: http://127.0.0.1:8054")
    app.run(debug=False, host="127.0.0.1", port=8054)
