import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

try:
    from btc_1tpd_backtester.utils import fetch_historical_data
except Exception:
    fetch_historical_data = None

try:
    from btc_1tpd_backtester.signals.today_signal import get_today_trade_recommendation
except Exception:
    get_today_trade_recommendation = None

# Symbols supported (reused from dashboards)
DEFAULT_SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "BNB/USDT:USDT",
    "SOL/USDT:USDT",
    "ADA/USDT:USDT",
    "XRP/USDT:USDT",
]


def load_trades(symbol: str | None = None, csv_path: str = "trades_final.csv") -> pd.DataFrame:
    slug = None
    if symbol:
        slug = symbol.replace('/', '_').replace(':', '_')
    candidates = []
    if slug:
        candidates.append(f"trades_final_{slug}.csv")
        candidates.append(os.path.join("btc_1tpd_backtester", f"trades_final_{slug}.csv"))
    candidates.extend([
        csv_path,
        os.path.join("btc_1tpd_backtester", "trades_final.csv"),
    ])
    for path in candidates:
        try:
            if not os.path.exists(path):
                continue
            df = pd.read_csv(path)
            if df.empty:
                continue
            if "entry_time" in df.columns:
                df["entry_time"] = pd.to_datetime(df["entry_time"])
            # Filter by symbol if column exists and symbol provided
            if symbol and "symbol" in df.columns:
                df = df[df["symbol"] == symbol]
            return df
        except Exception:
            continue
    return pd.DataFrame()


def compute_metrics(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {"total_trades": 0, "win_rate": 0.0, "total_pnl": 0.0, "max_drawdown": 0.0, "avg_risk_per_trade": 0.0, "dd_in_r": 0.0}
    df = trades.copy()
    df["cumulative_pnl"] = df["pnl_usdt"].cumsum()
    df["running_max"] = df["cumulative_pnl"].cummax()
    df["drawdown"] = df["cumulative_pnl"] - df["running_max"]
    total_trades = len(df)
    wins = (df["pnl_usdt"] > 0).sum()
    win_rate = (wins / total_trades) * 100 if total_trades else 0.0
    total_pnl = float(df["pnl_usdt"].sum())
    max_drawdown = float(df["drawdown"].min()) if not df["drawdown"].empty else 0.0
    # Risk per trade estimated from pnl_usdt and r_multiple
    risk_estimates = []
    if "r_multiple" in df.columns:
        for pnl, r in zip(df["pnl_usdt"], df["r_multiple"]):
            if pd.notna(r) and r != 0:
                risk_estimates.append(abs(pnl / r))
    avg_risk = float(pd.Series(risk_estimates).mean()) if risk_estimates else 0.0
    dd_in_r = (max_drawdown / avg_risk) if avg_risk else 0.0
    return {"total_trades": total_trades, "win_rate": win_rate, "total_pnl": total_pnl, "max_drawdown": max_drawdown, "avg_risk_per_trade": avg_risk, "dd_in_r": dd_in_r}


def figure_equity_curve(trades: pd.DataFrame):
    if trades.empty:
        return go.Figure()
    df = trades.copy()
    df["cumulative_pnl"] = df["pnl_usdt"].cumsum()
    fig = px.line(df, x="entry_time", y="cumulative_pnl", title="Equity Curve")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def figure_pnl_distribution(trades: pd.DataFrame):
    if trades.empty:
        return go.Figure()
    fig = px.histogram(trades, x="pnl_usdt", nbins=30, title="PnL Distribution")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def figure_drawdown(trades: pd.DataFrame):
    if trades.empty:
        return go.Figure()
    df = trades.copy()
    df["cumulative_pnl"] = df["pnl_usdt"].cumsum()
    df["running_max"] = df["cumulative_pnl"].cummax()
    df["drawdown"] = df["cumulative_pnl"] - df["running_max"]
    fig = px.area(df, x=df.index, y="drawdown", title="Drawdown")
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def figure_trade_timeline(trades: pd.DataFrame):
    if trades.empty:
        return go.Figure()
    df = trades.copy()
    wins = df[df["pnl_usdt"] > 0]
    losses = df[df["pnl_usdt"] < 0]
    fig = go.Figure()
    if not wins.empty:
        fig.add_trace(go.Scatter(x=wins["entry_time"], y=wins["pnl_usdt"], mode="markers", name="Wins", marker=dict(color="green")))
    if not losses.empty:
        fig.add_trace(go.Scatter(x=losses["entry_time"], y=losses["pnl_usdt"], mode="markers", name="Losses", marker=dict(color="red")))
    fig.update_layout(title="Trade Timeline", xaxis_title="Time", yaxis_title="PnL (USDT)", margin=dict(l=10, r=10, t=40, b=10))
    return fig


def figure_monthly_performance(trades: pd.DataFrame):
    if trades.empty or "entry_time" not in trades.columns:
        return go.Figure()
    df = trades.copy()
    df["entry_time"] = pd.to_datetime(df["entry_time"])  # ensure datetime
    df["month"] = df["entry_time"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["pnl_usdt"].sum().reset_index()
    monthly["color"] = monthly["pnl_usdt"].apply(lambda x: "green" if x > 0 else "red")
    fig = go.Figure(data=[go.Bar(x=monthly["month"], y=monthly["pnl_usdt"], marker_color=monthly["color"])])
    fig.update_layout(title="Monthly Performance", xaxis_title="Month", yaxis_title="PnL (USDT)", margin=dict(l=10, r=10, t=40, b=10))
    return fig


def figure_win_loss(trades: pd.DataFrame):
    if trades.empty:
        return go.Figure()
    wins = int((trades["pnl_usdt"] > 0).sum())
    losses = int((trades["pnl_usdt"] < 0).sum())
    breaks = int((trades["pnl_usdt"] == 0).sum())
    labels = ["Wins", "Losses"] + (["Break-even"] if breaks > 0 else [])
    values = [wins, losses] + ([breaks] if breaks > 0 else [])
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_layout(title="Win/Loss Distribution", margin=dict(l=10, r=10, t=40, b=10))
    return fig


def figure_trades_on_price(trades: pd.DataFrame, symbol: str, timeframe: str = "1h"):
    if trades.empty or fetch_historical_data is None:
        return go.Figure()
    try:
        df = trades.copy()
        df["entry_time"] = pd.to_datetime(df["entry_time"])  # ensure
        start_date = df["entry_time"].min().date().isoformat()
        end_date = df["entry_time"].max().date().isoformat()
        price = fetch_historical_data(symbol, start_date, end_date, timeframe)
        if price is None or price.empty:
            return go.Figure()
        price = price.copy()
        price = price.reset_index().rename(columns={"timestamp": "time"}) if "timestamp" in price.columns else price.reset_index(names=["time"]) 
        fig = px.line(price, x="time", y="close", title=f"{symbol} Price with Trades")
        # entries separated by side
        if "side" in df.columns:
            longs = df[df["side"].str.lower() == "long"]
            shorts = df[df["side"].str.lower() == "short"]
        else:
            longs = df.iloc[0:0]
            shorts = df.iloc[0:0]

        if not longs.empty:
            fig.add_trace(go.Scatter(x=longs["entry_time"], y=longs["entry_price"], mode="markers", name="Entry Long", marker=dict(color="green", symbol="triangle-up", size=9)))
        if not shorts.empty:
            fig.add_trace(go.Scatter(x=shorts["entry_time"], y=shorts["entry_price"], mode="markers", name="Entry Short", marker=dict(color="red", symbol="triangle-down", size=9)))

        # exits separated by side
        if "exit_time" in df.columns and "exit_price" in df.columns:
            if not longs.empty:
                fig.add_trace(go.Scatter(x=pd.to_datetime(longs["exit_time"]), y=longs["exit_price"], mode="markers", name="Exit Long", marker=dict(color="green", symbol="x", size=9)))
            if not shorts.empty:
                fig.add_trace(go.Scatter(x=pd.to_datetime(shorts["exit_time"]), y=shorts["exit_price"], mode="markers", name="Exit Short", marker=dict(color="red", symbol="x", size=9)))
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), xaxis_title="Time", yaxis_title="Price")
        return fig
    except Exception:
        return go.Figure()


def create_app():
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.title = "1TPD Web Dashboard"

    app.layout = dbc.Container([
        html.H2("BTC 1 Trade Per Day - Web Dashboard"),
        dbc.Row([
            dbc.Col(dbc.Select(id="symbol-dropdown", options=[{"label": s, "value": s} for s in DEFAULT_SYMBOLS], value="BTC/USDT:USDT" , className="mb-2"), md=4),
            dbc.Col(dbc.Button("Refrescar", id="refresh", color="primary"), md=2),
        ], className="mb-3"),

        dbc.Alert(id="alert", is_open=False, color="warning"),

        dbc.Card([
            dbc.CardHeader("Recomendación de hoy"),
            dbc.CardBody(id="today-reco"),
        ], className="mb-4"),

        dbc.Card([
            dbc.CardHeader("Métricas"),
            dbc.CardBody(id="metrics"),
        ], className="mb-4"),

        dcc.Tabs([
            dcc.Tab(label="Equity Curve", children=[dcc.Graph(id="equity-fig")]),
            dcc.Tab(label="PnL Distribution", children=[dcc.Graph(id="pnl-fig")]),
            dcc.Tab(label="Drawdown", children=[dcc.Graph(id="dd-fig")]),
            dcc.Tab(label="Trade Timeline", children=[dcc.Graph(id="timeline-fig")]),
            dcc.Tab(label="Monthly Performance", children=[dcc.Graph(id="monthly-fig")]),
            dcc.Tab(label="Win/Loss", children=[dcc.Graph(id="winloss-fig")]),
            dcc.Tab(label="Price Chart", children=[dcc.Graph(id="price-fig")]),
            dcc.Tab(label="Trades", children=[
                dash_table.DataTable(
                    id="trades-table",
                    columns=[
                        {"name": "Entry Time", "id": "entry_time", "type": "datetime"},
                        {"name": "Side", "id": "side"},
                        {"name": "Entry", "id": "entry_price", "type": "numeric", "format": {"specifier": ".2f"}},
                        {"name": "Exit", "id": "exit_price", "type": "numeric", "format": {"specifier": ".2f"}},
                        {"name": "PnL (USDT)", "id": "pnl_usdt", "type": "numeric", "format": {"specifier": "+.2f"}},
                        {"name": "R", "id": "r_multiple", "type": "numeric", "format": {"specifier": "+.2f"}},
                        {"name": "Exit Time", "id": "exit_time", "type": "datetime"},
                        {"name": "Reason", "id": "exit_reason"},
                    ],
                    page_size=10,
                    sort_action="native",
                    filter_action="native",
                    style_cell={"padding": "6px", "fontSize": 12},
                    style_table={"overflowX": "auto"},
                )
            ]),
        ]),
    ], fluid=True)

    @app.callback(
        Output("today-reco", "children"),
        Output("metrics", "children"),
        Output("equity-fig", "figure"),
        Output("pnl-fig", "figure"),
        Output("dd-fig", "figure"),
        Output("timeline-fig", "figure"),
        Output("monthly-fig", "figure"),
        Output("winloss-fig", "figure"),
        Output("price-fig", "figure"),
        Output("trades-table", "data"),
        Output("alert", "is_open"),
        Output("alert", "children"),
        Input("refresh", "n_clicks"),
        State("symbol-dropdown", "value"),
        prevent_initial_call=False,
    )
    def update_dashboard(n_clicks, symbol):
        symbol = (symbol or "BTC/USDT:USDT").strip()
        trades = load_trades(symbol)
        alert_msg = ""
        if trades.empty:
            alert_msg = f"No hay datos para {symbol}. Genera trades_final para este símbolo y vuelve a intentar."

        m = compute_metrics(trades)
        def kpi_card(title: str, value: str, color: str, icon: str):
            return dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.Div([html.I(className=f"bi {icon} me-2"), html.Small(title, className="text-muted")]),
                    html.H4(value, className=f"mt-2 text-{color}"),
                ])
            ], className="shadow-sm"), md=3, sm=6, xs=12)

        win_color = "success" if m['win_rate'] >= 50 else "warning" if m['win_rate'] > 0 else "secondary"
        pnl_color = "success" if m['total_pnl'] >= 0 else "danger"
        dd_color = "danger" if m['max_drawdown'] < 0 else "secondary"

        metrics_children = dbc.Row([
            kpi_card("Total trades", f"{m['total_trades']}", "primary", "bi-collection"),
            kpi_card("Win rate", f"{m['win_rate']:.1f}%", win_color, "bi-bullseye"),
            kpi_card("PnL", f"{m['total_pnl']:+,.2f} USDT", pnl_color, "bi-cash-stack"),
            kpi_card("Max DD", f"{m['max_drawdown']:.2f} USDT ({m['dd_in_r']:.2f} R)", dd_color, "bi-graph-down"),
            kpi_card("Riesgo/trade", f"{m['avg_risk_per_trade']:.2f} USDT", "info", "bi-shield"),
        ], className="g-3")

        eq = figure_equity_curve(trades)
        pnl = figure_pnl_distribution(trades)
        dd = figure_drawdown(trades)
        tl = figure_trade_timeline(trades)
        mon = figure_monthly_performance(trades)
        wl = figure_win_loss(trades)
        price_fig = figure_trades_on_price(trades, symbol)

        # Today recommendation card
        reco_children = html.Div("Se requiere módulo de señales.")
        if get_today_trade_recommendation is not None:
            try:
                config = {"risk_usdt": 20.0, "atr_mult_orb": 1.2, "tp_multiplier": 2.0, "adx_min": 15.0}
                rec = get_today_trade_recommendation(symbol, config)
                status = rec.get("status") or "-"
                side = (rec.get("side") or "-").lower()
                badge_color = "secondary" if side == "-" else ("success" if side == "long" else "danger")
                reco_children = html.Div([
                    html.Div([html.B("Estado: "), html.Span(status)]),
                    html.Div([html.B("Sesgo macro: "), rec.get("macro_bias") or "-"]),
                    html.Div([html.B("Dirección: "), dbc.Badge(side or "-", color=badge_color, className="ms-1")]),
                    html.Div([html.B("Hora entrada: "), str(rec.get("entry_time") or "-")]),
                    html.Div([html.B("Entrada: "), f"{rec.get('entry_price') or '-'}"]),
                    html.Div([html.B("SL: "), f"{rec.get('stop_loss') or '-'}"]),
                    html.Div([html.B("TP: "), f"{rec.get('take_profit') or '-'}"]),
                ])
            except Exception:
                pass

        # If no data, still return empty figures but show alert clearly
        table_data = []
        if not trades.empty:
            tbl = trades.copy()
            # Ordering recent first
            tbl = tbl.sort_values(by="entry_time", ascending=False)
            # Convert datetimes to ISO for DataTable
            for col in ["entry_time", "exit_time"]:
                if col in tbl.columns:
                    tbl[col] = pd.to_datetime(tbl[col]).dt.strftime("%Y-%m-%d %H:%M:%S")
            table_data = tbl[[c for c in ["entry_time", "side", "entry_price", "exit_price", "pnl_usdt", "r_multiple", "exit_time", "exit_reason"] if c in tbl.columns]].to_dict("records")

        return reco_children, metrics_children, eq, pnl, dd, tl, mon, wl, price_fig, table_data, bool(alert_msg), alert_msg

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8050, debug=True)


