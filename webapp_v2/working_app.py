"""One Trade v2.0 - Working Web Interface."""
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
from dash import dcc, html

from config import load_config

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
app.title = "One Trade v2.0 - Backtesting System"

config = load_config("config/config.yaml")

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

def create_dashboard_content():
    """Create dashboard content with saved backtests."""
    saved_backtests = load_saved_backtests()
    
    if not saved_backtests:
        return dbc.Alert([
            html.H4("📊 No Backtests Found", className="alert-heading"),
            html.P("No se encontraron backtests guardados. Ejecuta un backtest primero:"),
            html.Code("python -m cli.main backtest BTC/USDT --strategy baseline")
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
    
    return html.Div([
        dbc.Alert([
            html.H4("🎉 Dashboard Funcionando!", className="alert-heading"),
            html.P(f"Se encontraron {len(saved_backtests)} backtests guardados."),
            html.Hr(),
            html.P("Estos son los backtests más recientes:")
        ], color="success", className="mb-4"),
        
        html.Div(backtest_cards)
    ])

def create_backtest_content():
    """Create backtest form content."""
    return html.Div([
        dbc.Alert([
            html.H4("⚙️ Ejecutar Backtest", className="alert-heading"),
            html.P("Para ejecutar un backtest, usa la línea de comandos:"),
            html.Hr(),
            html.Pre([
                "# Backtest con estrategia baseline\n",
                "python -m cli.main backtest BTC/USDT --strategy baseline\n\n",
                "# Backtest con estrategia current\n", 
                "python -m cli.main backtest BTC/USDT --strategy current\n\n",
                "# Backtest con fechas específicas\n",
                "python -m cli.main backtest BTC/USDT --strategy baseline --start-date 2024-01-01"
            ], className="bg-light p-3 rounded"),
            html.Hr(),
            html.P("Los resultados se guardarán automáticamente y aparecerán en el Dashboard.")
        ], color="info")
    ])

def create_data_content():
    """Create data management content."""
    try:
        from one_trade.backtest import BacktestEngine
        engine = BacktestEngine(config)
        
        data_info = []
        for symbol in config.data.symbols:
            for timeframe in config.data.timeframes:
                start, end = engine.data_store.get_date_range(symbol, timeframe)
                if start and end:
                    _, last_ts = engine.data_store.read_data(symbol, timeframe)
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
            dbc.Alert([
                html.H4("📊 Estado de Datos", className="alert-heading"),
                html.P("Datos disponibles en el sistema:")
            ], color="info", className="mb-3"),
            
            dbc.Table.from_dataframe(
                df, 
                striped=True, 
                bordered=True, 
                hover=True,
                className="mb-3"
            ),
            
            dbc.Alert([
                html.H5("🔄 Actualizar Datos"),
                html.P("Para actualizar datos, usa:"),
                html.Code("python -m cli.main update-data --symbols BTC/USDT --timeframes 15m"),
                html.Br(),
                html.Code("python -m cli.main check-data")
            ], color="secondary")
        ])
        
    except Exception as e:
        return dbc.Alert([
            html.H4("❌ Error", className="alert-heading"),
            html.P(f"Error al cargar datos: {str(e)}")
        ], color="danger")

# Create layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-chart-line me-3"), 
                "One Trade v2.0"
            ], className="text-primary mb-0"),
            html.P("Modern Backtesting System", className="text-muted")
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
            create_dashboard_content()
        ]),
        dbc.Tab(label="⚙️ Backtest", tab_id="backtest", children=[
            create_backtest_content()
        ]),
        dbc.Tab(label="📁 Data", tab_id="data", children=[
            create_data_content()
        ])
    ], id="tabs", active_tab="dashboard")
    
], fluid=True, className="py-4")

if __name__ == "__main__":
    print("🚀 Starting One Trade v2.0 Working Web Interface...")
    print("📊 Dashboard available at: http://127.0.0.1:8052")
    app.run(debug=False, host="127.0.0.1", port=8052)
