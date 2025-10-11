"""One Trade v2.0 - Interactive Web Interface (Improved Version)."""
import json
import glob
import sys
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webapp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
app.title = "One Trade v2.0 - Interactive Backtesting System"

# Global configuration
config = load_config("config/config.yaml")
engine = BacktestEngine(config)

# Thread pool for async operations
executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="webapp_worker")

# Cache invalidation timestamp
_cache_timestamp = datetime.now().timestamp()

# Global state for async operations (thread-safe approach)
import threading
_backtest_futures = {}
_data_futures = {}
_futures_lock = threading.Lock()


def invalidate_cache():
    """Invalidate the backtest cache to force reload."""
    global _cache_timestamp
    _cache_timestamp = datetime.now().timestamp()
    load_saved_backtests.cache_clear()


@lru_cache(maxsize=1)
def load_saved_backtests() -> List[Dict]:
    """Load all saved backtest results from CSV files with caching."""
    logger.info("Loading saved backtests from CSV files")
    backtests = []
    results_dir = Path("data_incremental/backtest_results")
    
    if not results_dir.exists():
        logger.warning(f"Results directory does not exist: {results_dir}")
        return backtests
    
    csv_files = glob.glob(str(results_dir / "trades_*.csv"))
    logger.info(f"Found {len(csv_files)} backtest CSV files")
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            if df.empty:
                logger.warning(f"Empty CSV file: {csv_file}")
                continue
            
            # Validate required columns
            required_columns = ['pnl', 'fees']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing columns {missing_columns} in {csv_file}")
                continue
            
            # Extract info from filename
            filename = Path(csv_file).stem
            parts = filename.split('_')
            
            if len(parts) < 5:
                logger.error(f"Invalid filename format: {filename}")
                continue
                
            symbol = f"{parts[1]}/{parts[2]}"
            date_str = parts[3]
            time_str = parts[4]
            
            # Calculate basic metrics with validation
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
            logger.debug(f"Loaded backtest: {symbol} - {date_str} {time_str}")
        except Exception as e:
            logger.error(f"Error loading {csv_file}: {e}", exc_info=True)
            continue
    
    # Sort by creation date (newest first)
    backtests.sort(key=lambda x: x['created_at'], reverse=True)
    logger.info(f"Successfully loaded {len(backtests)} backtests")
    return backtests


def run_backtest_async(symbol: str, strategy: str, start_date: str, end_date: str) -> Dict:
    """Run backtest in background thread."""
    logger.info(f"Starting backtest: symbol={symbol}, strategy={strategy}, start={start_date}, end={end_date}")
    try:
        config.strategy.type = StrategyType(strategy)
        engine_temp = BacktestEngine(config)
        results = engine_temp.run_backtest(symbol, start_date, end_date)
        logger.info(f"Backtest completed successfully: {results['metrics'].total_trades} trades")
        
        # Invalidate cache to force reload
        invalidate_cache()
        
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def update_data_async(symbols: List[str], timeframes: List[str]) -> Dict:
    """Update data in background thread."""
    logger.info(f"Starting data update: symbols={symbols}, timeframes={timeframes}")
    try:
        engine.update_data(symbols, timeframes)
        logger.info("Data update completed successfully")
        return {"success": True}
    except Exception as e:
        logger.error(f"Data update failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


# Create layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-chart-line me-3"), 
                "One Trade v2.0"
            ], className="text-primary mb-0"),
            html.P("Interactive Backtesting System", className="text-muted")
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
    
    # Reactive stores for state management (replacing app.server.config)
    dcc.Store(id="backtest-state", data={
        "running": False,
        "result": None,
        "timestamp": None
    }),
    dcc.Store(id="data-state", data={
        "running": False,
        "result": None
    }),
    dcc.Store(id="backtest-completion-event", data={
        "completed": False,
        "timestamp": None
    }),
    
    # Intervals for polling
    dcc.Interval(id="status-interval", interval=1000, n_intervals=0),
    dcc.Interval(id="dashboard-refresh-interval", interval=2000, n_intervals=0, disabled=True)
    
], fluid=True, className="py-4")


def create_dashboard_content(show_alert: bool = False):
    """Create dashboard content with saved backtests."""
    saved_backtests = load_saved_backtests()
    
    # Alert for new backtest completion
    new_backtest_alert = None
    if show_alert:
        new_backtest_alert = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "¡Nuevo backtest completado! Los resultados se han actualizado automáticamente."
        ], color="success", className="mb-3", dismissable=True, duration=5000)
    
    if not saved_backtests:
        return html.Div([
            new_backtest_alert,
            dbc.Alert([
                html.H4("📊 No Backtests Found", className="alert-heading"),
                html.P("No se encontraron backtests guardados. Ejecuta un backtest primero desde la pestaña 'Backtest'.")
            ], color="warning")
        ])
    
    return html.Div([
        new_backtest_alert,
        dbc.Row([
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-sync-alt me-2"),
                    "Refresh Backtests"
                ], id="refresh-backtests-btn", color="primary", className="mb-3")
            ], width=12)
        ]),
        
        html.Div(id="backtest-cards")
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
                        html.Div(id="backtest-progress")
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
                            html.Div(id="data-progress")
                        ])
                    ], className="shadow")
                ], width=4)
            ])
        ])
        
    except Exception as e:
        logger.error(f"Error creating data content: {e}", exc_info=True)
        return dbc.Alert([
            html.H4("❌ Error", className="alert-heading"),
            html.P(f"Error al cargar datos: {str(e)}")
        ], color="danger")


# Callbacks
@app.callback(
    Output("dashboard-content", "children"),
    [Input("tabs", "active_tab"),
     Input("refresh-backtests-btn", "n_clicks"),
     Input("backtest-completion-event", "data")]
)
def render_dashboard_content(active_tab, refresh_clicks, completion_event):
    """Render dashboard content with automatic updates."""
    if active_tab != "dashboard":
        return ""
    
    ctx = callback_context
    show_alert = False
    
    if ctx.triggered:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Show alert if triggered by backtest completion
        if trigger_id == "backtest-completion-event" and completion_event.get("completed"):
            show_alert = True
            logger.info("Dashboard refreshed due to backtest completion")
        elif trigger_id == "refresh-backtests-btn":
            invalidate_cache()
            logger.info("Dashboard manually refreshed")
    
    return create_dashboard_content(show_alert=show_alert)


@app.callback(
    Output("backtest-content", "children"),
    Input("tabs", "active_tab")
)
def render_backtest_content(active_tab):
    """Render backtest tab content."""
    if active_tab == "backtest":
        return create_backtest_content()
    return ""


@app.callback(
    Output("data-content", "children"),
    Input("tabs", "active_tab")
)
def render_data_content(active_tab):
    """Render data tab content."""
    if active_tab == "data":
        return create_data_content()
    return ""


@app.callback(
    [Output("backtest-state", "data"),
     Output("backtest-progress", "children"),
     Output("backtest-results", "children"),
     Output("backtest-completion-event", "data")],
    [Input("run-backtest-btn", "n_clicks"),
     Input("status-interval", "n_intervals")],
    [State("symbol-select", "value"),
     State("strategy-select", "value"),
     State("start-date", "date"),
     State("end-date", "date"),
     State("backtest-state", "data")]
)
def run_backtest(n_clicks, n_intervals, symbol, strategy, start_date, end_date, state):
    """Execute backtest with reactive state management."""
    ctx = callback_context
    
    if not ctx.triggered:
        initial_state = {"running": False, "result": None, "timestamp": None}
        return initial_state, dbc.Alert("Listo para ejecutar backtest", color="info"), "", {"completed": False, "timestamp": None}
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger_id == "run-backtest-btn" and n_clicks:
        logger.info(f"Backtest button clicked: {symbol}, {strategy}, {start_date} to {end_date}")
        
        # Start backtest
        progress = dbc.Alert([
            dbc.Spinner(size="sm"),
            f" Ejecutando backtest para {symbol} con estrategia {strategy}..."
        ], color="info")
        
        # Submit to thread pool
        future = executor.submit(run_backtest_async, symbol, strategy, start_date, end_date)
        timestamp = datetime.now().timestamp()
        
        new_state = {
            "running": True,
            "result": None,
            "timestamp": timestamp,
            "future": str(timestamp)  # Use timestamp as future identifier
        }
        
        # Store future in a global dict (thread-safe approach)
        with _futures_lock:
            _backtest_futures[str(timestamp)] = future
        
        return new_state, progress, "", {"completed": False, "timestamp": None}
    
    elif trigger_id == "status-interval" and state.get("running"):
        # Check if backtest completed
        timestamp = state.get("future")
        logger.debug(f"Checking backtest status - timestamp: {timestamp}, running: {state.get('running')}")
        
        if timestamp:
            with _futures_lock:
                future = _backtest_futures.get(timestamp)
            
            if future and future.done():
                logger.info(f"Backtest future completed for timestamp: {timestamp}")
                result = future.result()
                with _futures_lock:
                    if timestamp in _backtest_futures:
                        del _backtest_futures[timestamp]
                
                logger.info(f"Backtest completed: success={result.get('success')}")
                
                if result['success']:
                    metrics = result['results']['metrics']
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
                            ])
                        ])
                    ])
                    
                    # Signal completion event
                    completion_event = {
                        "completed": True,
                        "timestamp": datetime.now().timestamp()
                    }
                    
                    completed_state = {"running": False, "result": result, "timestamp": None}
                    return completed_state, success_alert, results_content, completion_event
                else:
                    error_alert = dbc.Alert([
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"Error: {result['error']}"
                    ], color="danger")
                    
                    completed_state = {"running": False, "result": result, "timestamp": None}
                    return completed_state, error_alert, "", {"completed": False, "timestamp": None}
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(
    Output("backtest-cards", "children"),
    [Input("status-interval", "n_intervals"),
     Input("refresh-backtests-btn", "n_clicks"),
     Input("backtest-completion-event", "data")]
)
def update_backtest_cards(n_intervals, refresh_clicks, completion_event):
    """Update backtest cards automatically."""
    saved_backtests = load_saved_backtests()
    
    if not saved_backtests:
        return dbc.Alert([
            html.H5("📊 No Backtests Found", className="alert-heading"),
            html.P("No se encontraron backtests guardados. Ejecuta un backtest primero desde la pestaña 'Backtest'.")
        ], color="warning")
    
    # Create backtest cards with loading spinner
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
    
    return backtest_cards


@app.callback(
    [Output("data-state", "data"),
     Output("data-progress", "children"),
     Output("update-data-btn", "disabled")],
    [Input("update-data-btn", "n_clicks"),
     Input("status-interval", "n_intervals")],
    [State("update-symbols", "value"),
     State("update-timeframes", "value"),
     State("data-state", "data")]
)
def update_data(n_clicks, n_intervals, symbols, timeframes, state):
    """Update market data with reactive state management."""
    ctx = callback_context
    
    if not ctx.triggered:
        initial_state = {"running": False, "result": None}
        return initial_state, "Listo para actualizar datos", False
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger_id == "update-data-btn" and n_clicks:
        logger.info(f"Data update button clicked: symbols={symbols}, timeframes={timeframes}")
        
        progress = dbc.Alert([
            dbc.Spinner(size="sm"),
            f" Actualizando datos para {len(symbols)} símbolos y {len(timeframes)} timeframes..."
        ], color="info")
        
        # Submit to thread pool
        future = executor.submit(update_data_async, symbols, timeframes)
        timestamp = datetime.now().timestamp()
        
        new_state = {
            "running": True,
            "result": None,
            "future": str(timestamp)
        }
        
        # Store future (thread-safe approach)
        with _futures_lock:
            _data_futures[str(timestamp)] = future
        
        return new_state, progress, True
    
    elif trigger_id == "status-interval" and state.get("running"):
        # Check if update completed
        timestamp = state.get("future")
        if timestamp:
            with _futures_lock:
                future = _data_futures.get(timestamp)
            
            if future and future.done():
                result = future.result()
                with _futures_lock:
                    if timestamp in _data_futures:
                        del _data_futures[timestamp]
                
                logger.info(f"Data update completed: success={result.get('success')}")
                
                if result['success']:
                    success_alert = dbc.Alert([
                        html.I(className="fas fa-check-circle me-2"),
                        "Datos actualizados exitosamente!"
                    ], color="success")
                    
                    completed_state = {"running": False, "result": result}
                    return completed_state, success_alert, False
                else:
                    error_alert = dbc.Alert([
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"Error: {result['error']}"
                    ], color="danger")
                    
                    completed_state = {"running": False, "result": result}
                    return completed_state, error_alert, False
    
    return dash.no_update, dash.no_update, dash.no_update


if __name__ == "__main__":
    print("🚀 Starting One Trade v2.0 Interactive Web Interface...")
    print("📊 Dashboard available at: http://127.0.0.1:8053")
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    app.run(debug=False, host="127.0.0.1", port=8053)
