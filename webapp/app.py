import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

try:
    from btc_1tpd_backtester.utils import fetch_historical_data
except Exception:
    fetch_historical_data = None


def load_trades(csv_path: str = "trades_final.csv") -> pd.DataFrame:
    candidates = [
        csv_path,
        os.path.join("btc_1tpd_backtester", "trades_final.csv"),
    ]
    for path in candidates:
        try:
            if not os.path.exists(path):
                continue
            df = pd.read_csv(path)
            if df.empty:
                continue
            if "entry_time" in df.columns:
                df["entry_time"] = pd.to_datetime(df["entry_time"])
            return df
        except Exception:
            continue
    return pd.DataFrame()


def compute_metrics(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {"total_trades": 0, "win_rate": 0.0, "total_pnl": 0.0, "max_drawdown": 0.0}
    df = trades.copy()
    df["cumulative_pnl"] = df["pnl_usdt"].cumsum()
    df["running_max"] = df["cumulative_pnl"].cummax()
    df["drawdown"] = df["cumulative_pnl"] - df["running_max"]
    total_trades = len(df)
    wins = (df["pnl_usdt"] > 0).sum()
    win_rate = (wins / total_trades) * 100 if total_trades else 0.0
    total_pnl = float(df["pnl_usdt"].sum())
    max_drawdown = float(df["drawdown"].min()) if not df["drawdown"].empty else 0.0
    return {"total_trades": total_trades, "win_rate": win_rate, "total_pnl": total_pnl, "max_drawdown": max_drawdown}


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
            dbc.Col(dbc.Input(id="symbol", value="BTC/USDT:USDT", placeholder="Symbol"), md=4),
            dbc.Col(dbc.Button("Refrescar", id="refresh", color="primary"), md=2),
        ], className="mb-3"),

        dbc.Alert(id="alert", is_open=False, color="warning"),

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
        ]),
    ], fluid=True)

    @app.callback(
        Output("metrics", "children"),
        Output("equity-fig", "figure"),
        Output("pnl-fig", "figure"),
        Output("dd-fig", "figure"),
        Output("timeline-fig", "figure"),
        Output("monthly-fig", "figure"),
        Output("winloss-fig", "figure"),
        Output("price-fig", "figure"),
        Output("alert", "is_open"),
        Output("alert", "children"),
        Input("refresh", "n_clicks"),
        State("symbol", "value"),
        prevent_initial_call=False,
    )
    def update_dashboard(n_clicks, symbol):
        trades = load_trades()
        alert_msg = ""
        if trades.empty:
            alert_msg = "No se encontró trades_final.csv. Crea o actualiza el archivo antes de usar la app."

        m = compute_metrics(trades)
        metrics_children = html.Div([
            html.Div([html.B("Total trades: "), f"{m['total_trades']}"]),
            html.Div([html.B("Win rate: "), f"{m['win_rate']:.1f}%"]),
            html.Div([html.B("PnL acumulado: "), f"{m['total_pnl']:+.2f} USDT"]),
            html.Div([html.B("Drawdown máximo: "), f"{m['max_drawdown']:.2f} USDT"]),
        ])

        eq = figure_equity_curve(trades)
        pnl = figure_pnl_distribution(trades)
        dd = figure_drawdown(trades)
        tl = figure_trade_timeline(trades)
        mon = figure_monthly_performance(trades)
        wl = figure_win_loss(trades)
        price_fig = figure_trades_on_price(trades, (symbol or "BTC/USDT:USDT").strip())

        return metrics_children, eq, pnl, dd, tl, mon, wl, price_fig, bool(alert_msg), alert_msg

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8050, debug=True)


