"""One Trade v2.0 - Simple Web Interface."""
import json
import os
import glob
from datetime import datetime
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, State, dcc, html, dash_table
from dash.exceptions import PreventUpdate

from config import load_config
from one_trade.backtest import BacktestEngine

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
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

def create_simple_layout():
    """Create a simple layout that definitely works."""
    saved_backtests = load_saved_backtests()
    
    # Create backtest info cards
    backtest_cards = []
    for bt in saved_backtests[:5]:  # Show only latest 5
        color = "success" if bt['total_return'] > 0 else "danger"
        backtest_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6(f"{bt['symbol']} - {bt['date']} {bt['time']}", className="card-title"),
                    html.P([
                        f"Trades: {bt['total_trades']} | ",
                        f"Win Rate: {bt['win_rate']:.1f}% | ",
                        f"Return: {bt['total_return_pct']:+.2f}%"
                    ]),
                    html.Small(f"File: {bt['filename']}", className="text-muted")
                ])
            ], color=color, outline=True, className="mb-2")
        )
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([html.I(className="fas fa-chart-line me-3"), "One Trade v2.0"], 
                       className="text-primary mb-0"),
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
        
        dbc.Alert([
            html.H4("🎉 ¡Webapp Funcionando!", className="alert-heading"),
            html.P("La webapp está cargando correctamente. Se encontraron los siguientes backtests:"),
            html.Hr(),
            html.P(f"Total de backtests guardados: {len(saved_backtests)}")
        ], color="success", className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.H5("📊 Backtests Recientes"),
                html.Div(backtest_cards)
            ], width=6),
            dbc.Col([
                html.H5("🚀 Acciones Rápidas"),
                dbc.Card([
                    dbc.CardBody([
                        html.P("Para ejecutar un nuevo backtest:"),
                        html.Code("python -m cli.main backtest BTC/USDT --strategy baseline"),
                        html.Br(),
                        html.Br(),
                        html.P("Para actualizar datos:"),
                        html.Code("python -m cli.main update-data --symbols BTC/USDT"),
                        html.Br(),
                        html.Br(),
                        html.P("Para ver datos disponibles:"),
                        html.Code("python -m cli.main check-data")
                    ])
                ])
            ], width=6)
        ])
    ], fluid=True, className="py-4")

app.layout = create_simple_layout()

if __name__ == "__main__":
    print("🚀 Starting One Trade v2.0 Simple Web Interface...")
    print("📊 Dashboard available at: http://127.0.0.1:8051")
    app.run(debug=True, host="127.0.0.1", port=8051)








