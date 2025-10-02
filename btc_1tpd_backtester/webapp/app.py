import os
import json
from datetime import datetime, timezone

import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

from ..signals.today_signal import get_today_trade_recommendation
from .plots import (
    figure_equity_curve,
    figure_pnl_distribution,
    figure_drawdown,
    figure_trade_timeline,
)


def load_trades(csv_path: str = "trades_final.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
        if "entry_time" in df.columns:
            df["entry_time"] = pd.to_datetime(df["entry_time"])
        return df
    except Exception:
        return pd.DataFrame()


def create_app():
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = "1TPD Web Dashboard"

    app.layout = dbc.Container([
        html.H2("BTC 1 Trade Per Day - Web Dashboard"),
        dbc.Row([
            dbc.Col([
                dbc.Input(id="symbol", value="BTC/USDT:USDT", placeholder="Symbol"),
            ], md=4),
            dbc.Col([
                dbc.Button("Refrescar", id="refresh", color="primary"),
            ], md=2),
        ], className="mb-3"),

        dbc.Alert(id="alert", is_open=False, color="warning"),

        dbc.Card([
            dbc.CardHeader("Recomendación de hoy"),
            dbc.CardBody(id="today-reco"),
        ], className="mb-4"),

        dcc.Tabs([
            dcc.Tab(label="Equity Curve", children=[dcc.Graph(id="equity-fig")]),
            dcc.Tab(label="PnL Distribution", children=[dcc.Graph(id="pnl-fig")]),
            dcc.Tab(label="Drawdown", children=[dcc.Graph(id="dd-fig")]),
            dcc.Tab(label="Trade Timeline", children=[dcc.Graph(id="timeline-fig")]),
        ]),
    ], fluid=True)

    @app.callback(
        Output("today-reco", "children"),
        Output("equity-fig", "figure"),
        Output("pnl-fig", "figure"),
        Output("dd-fig", "figure"),
        Output("timeline-fig", "figure"),
        Output("alert", "is_open"),
        Output("alert", "children"),
        Input("refresh", "n_clicks"),
        State("symbol", "value"),
        prevent_initial_call=False,
    )
    def update_dashboard(n_clicks, symbol):
        trades = load_trades()
        if trades.empty:
            alert_msg = "No se encontró trades_final.csv. Crea o actualiza el archivo antes de usar la app."
        else:
            alert_msg = ""

        config = {"risk_usdt": 20.0, "atr_mult_orb": 1.2, "tp_multiplier": 2.0, "adx_min": 15.0}
        rec = get_today_trade_recommendation(symbol or "BTC/USDT:USDT", config)

        card = html.Div([
            html.Div([html.B("Estado: "), rec.get("status")]),
            html.Div([html.B("Sesgo macro: "), rec.get("macro_bias")]),
            html.Div([html.B("Dirección: "), rec.get("side") or "-"]),
            html.Div([html.B("Hora entrada: "), rec.get("entry_time") or "-"]),
            html.Div([html.B("Entrada: "), f"{rec.get('entry_price') or '-'}"]),
            html.Div([html.B("SL: "), f"{rec.get('stop_loss') or '-'}"]),
            html.Div([html.B("TP: "), f"{rec.get('take_profit') or '-'}"]),
            html.Div([html.B("ORB High/Low: "), f"{rec.get('orb_high')}/{rec.get('orb_low')}"]),
            html.Div([html.B("Notas: "), rec.get("notes") or "-"]),
        ])

        eq = figure_equity_curve(trades)
        pnl = figure_pnl_distribution(trades)
        dd = figure_drawdown(trades)
        tl = figure_trade_timeline(trades)

        return card, eq, pnl, dd, tl, bool(alert_msg), alert_msg

    return app


def main():
    app = create_app()
    app.run_server(host="0.0.0.0", port=8050, debug=True)


if __name__ == "__main__":
    main()



