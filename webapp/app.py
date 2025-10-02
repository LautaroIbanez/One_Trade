import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

# Paths (ensure imports work when running from webapp/)
base_dir = Path(__file__).resolve().parent
repo_root = base_dir.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

try:
    from btc_1tpd_backtester.utils import fetch_historical_data
except Exception:
    fetch_historical_data = None
try:
    from btc_1tpd_backtester.utils import fetch_latest_price
except Exception:
    fetch_latest_price = None

try:
    from btc_1tpd_backtester.signals.today_signal import get_today_trade_recommendation
    from btc_1tpd_backtester.btc_1tpd_backtest_final import run_backtest
except Exception:
    get_today_trade_recommendation = None
    run_backtest = None

# Paths already defined above

# Centralized configuration for modes
BASE_CONFIG = {
    "risk_usdt": 20.0, 
    "atr_mult_orb": 1.2, 
    "tp_multiplier": 2.0, 
    "adx_min": 15.0,
    "commission_rate": 0.001,  # 0.1% default
    "slippage_rate": 0.0005,   # 0.05% default
    "initial_capital": 1000.0, # Initial capital in USDT
    "leverage": 1.0,           # Leverage multiplier
    "full_day_trading": False,  # Full day trading mode
    "force_one_trade": False,
    "fallback_mode": "EMA15_pullback",
    # When rebuilding, start date or lookback control
    "backtest_start_date": None,  # ISO date string e.g., "2024-01-01"
    "lookback_days": 30,
}
MODE_CONFIG = {
    "conservative": {
        "risk_usdt": 10.0, 
        "atr_mult_orb": 1.5, 
        "tp_multiplier": 1.5, 
        "orb_window": (11, 12), 
        "entry_window": (11, 18),  # Extended to 18:00 UTC
        "commission_rate": 0.0008,  # Lower commission for conservative
        "slippage_rate": 0.0003,
        "initial_capital": 1000.0,
        "leverage": 1.0,
        "full_day_overrides": {
            "risk_usdt": 15.0,  # Slightly higher risk for 24h
            "orb_window": (0, 1),  # ORB at midnight UTC
            "entry_window": (1, 24),  # Can enter throughout the day (0-24 range)
            "commission_rate": 0.001,  # Higher commission for 24h trading
            "slippage_rate": 0.0005
        }
    },
    "moderate": {
        "risk_usdt": 20.0, 
        "atr_mult_orb": 1.2, 
        "tp_multiplier": 2.0, 
        "orb_window": (11, 12), 
        "entry_window": (11, 18),  # Extended to 18:00 UTC
        "commission_rate": 0.001,   # Standard commission
        "slippage_rate": 0.0005,
        "initial_capital": 1000.0,
        "leverage": 1.0,
        "full_day_overrides": {
            "risk_usdt": 25.0,  # Higher risk for 24h
            "orb_window": (0, 1),  # ORB at midnight UTC
            "entry_window": (1, 24),  # Can enter throughout the day (0-24 range)
            "commission_rate": 0.0012,  # Higher commission for 24h trading
            "slippage_rate": 0.0008
        },
        "force_one_trade": True,
        "fallback_mode": "EMA15_pullback"
    },
    "aggressive": {
        "risk_usdt": 30.0, 
        "atr_mult_orb": 1.0, 
        "tp_multiplier": 2.5, 
        "orb_window": (10, 12), 
        "entry_window": (10, 18),  # Extended to 18:00 UTC
        "commission_rate": 0.0012,  # Higher commission for aggressive
        "slippage_rate": 0.0008,
        "initial_capital": 1000.0,
        "leverage": 1.0,
        "full_day_overrides": {
            "risk_usdt": 40.0,  # Even higher risk for 24h
            "orb_window": (0, 1),  # ORB at midnight UTC
            "entry_window": (1, 24),  # Can enter throughout the day (0-24 range)
            "commission_rate": 0.0015,  # Highest commission for 24h trading
            "slippage_rate": 0.001
        }
    },
}


def get_effective_config(symbol: str, mode: str, full_day_trading: bool = False) -> dict:
    """Return merged BASE_CONFIG with selected mode overrides and optionally full_day_overrides. Symbol kept for future symbol-specific tweaks."""
    mode_cfg = MODE_CONFIG.get((mode or "moderate").lower(), {})
    
    # Start with base config, then apply mode config
    config = {**BASE_CONFIG, **{k: v for k, v in mode_cfg.items() if k != "full_day_overrides"}}
    
    # If full_day_trading is True, apply the full_day_overrides
    if full_day_trading and "full_day_overrides" in mode_cfg:
        full_day_overrides = mode_cfg["full_day_overrides"]
        config = {**config, **full_day_overrides}
    
    # Set the full_day_trading flag based on the parameter
    config["full_day_trading"] = full_day_trading
    
    return config

# Symbols supported (reused from dashboards)
DEFAULT_SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "BNB/USDT:USDT",
    "SOL/USDT:USDT",
    "ADA/USDT:USDT",
    "XRP/USDT:USDT",
]


def refresh_trades(symbol: str, mode: str, full_day_trading: bool = False) -> str:
    """
    Refresh trades data by running backtest from last available date to today for a given symbol and mode.
    
    Args:
        symbol: Trading symbol (e.g., 'BTC/USDT:USDT')
        mode: Trading mode ('conservative', 'moderate', 'aggressive')
        full_day_trading: If True, enables 24-hour trading mode with separate file storage
    
    Returns:
        Status message indicating success or failure
        
    Note:
        When full_day_trading mode changes, the system will rebuild the entire backtest
        to avoid mixing different trading session types. Files are stored with _24h suffix
        for full day trading mode to maintain separation.
    """
    if run_backtest is None:
        return "Backtest module not available"
    
    print(f"🔄 refresh_trades called: symbol={symbol}, mode={mode}, 24h={full_day_trading}")
    try:
        # Load existing trades for the current mode
        existing_trades = load_trades(symbol, mode, full_day_trading)
        
        # Check for mode change by comparing file existence and current mode
        # Mode change occurs when switching between normal and 24h files
        slug = symbol.replace('/', '_').replace(':', '_')
        mode_suffix = (mode or "moderate").lower()
        data_dir = repo_root / "data"
        
        normal_file = data_dir / f"trades_final_{slug}_{mode_suffix}.csv"
        file_24h = data_dir / f"trades_final_{slug}_{mode_suffix}_24h.csv"
        
        # Determine which file should exist for the current mode
        expected_file = file_24h if full_day_trading else normal_file
        opposite_file = normal_file if full_day_trading else file_24h

        # Sidecar meta path and stored full_day flag
        stored_full_day_flag = None
        try:
            sidecar_in = Path(str(expected_file.with_suffix("")) + "_meta.json")
            if sidecar_in.exists():
                import json as _json
                meta_in = _json.loads(sidecar_in.read_text(encoding="utf-8"))
                stored_full_day_flag = bool(meta_in.get("full_day_trading"))
        except Exception as e:
            print(f"⚠️ Could not read sidecar for mode detection: {e}")
            stored_full_day_flag = None

        # Mode change detected if expected CSV missing OR stored flag differs from requested
        mode_change_detected = (
            not expected_file.exists() or
            (stored_full_day_flag is not None and stored_full_day_flag != bool(full_day_trading)) or
            (normal_file.exists() and file_24h.exists() and existing_trades.empty)
        )
        
        # Determine default since using config lookback/backtest_start_date
        cfg_for_since = get_effective_config(symbol, mode, full_day_trading)
        cfg_for_since["full_day_trading"] = bool(full_day_trading)
        start_override = cfg_for_since.get("backtest_start_date")
        lb_days = cfg_for_since.get("lookback_days", 30)
        default_since = (start_override or (datetime.now(timezone.utc).date() - timedelta(days=int(lb_days))).isoformat())
        
        if mode_change_detected:
            print(f"🔄 Mode change detected: switching to {'24h' if full_day_trading else 'normal'} mode")
            # Clear existing trades and force rebuild
            existing_trades = pd.DataFrame()
            since = default_since
            print(f"📅 Mode change: using default since date: {since}")
        elif not existing_trades.empty and "entry_time" in existing_trades.columns:
            df_dates = pd.to_datetime(existing_trades["entry_time"])  # ensure datetime
            last_date = df_dates.max().date()
            since = (last_date + timedelta(days=1)).isoformat()
            print(f"📅 Using last trade date + 1 day: {since}")
        else:
            since = default_since
        
        until = datetime.now(timezone.utc).date().isoformat()

        # Guard: parse since/until and early-exit if since > until
        try:
            from datetime import datetime as _dt
            since_dt = _dt.fromisoformat(str(since))
            until_dt = _dt.fromisoformat(str(until))
            if since_dt > until_dt:
                msg = f"ℹ️ since ({since}) is after until ({until}); skipping backtest and keeping existing CSV."
                print(msg)
                return f"OK: {msg}"
        except Exception as e:
            print(f"⚠️ since/until parsing failed (continuing): {e}")
        
        # Merge base and mode config with full_day_trading parameter
        config = get_effective_config(symbol, mode, full_day_trading)
        # Set full_day_trading flag
        config["full_day_trading"] = bool(full_day_trading)
        print(f"📊 Effective config for {symbol} {mode} (24h: {full_day_trading}): {config}")
        
        # Run backtest
        results = run_backtest(symbol, since, until, config)

        # Sync with live active trade state
        try:
            from btc_1tpd_backtester.live_monitor import load_active_trade, evaluate_active_trade_exit, clear_active_trade
            active = load_active_trade()
        except Exception:
            active = None
        
        # Determine filename with absolute path
        slug = symbol.replace('/', '_').replace(':', '_')
        mode_suffix = (mode or "moderate").lower()
        trading_suffix = "_24h" if full_day_trading else ""
        data_dir = repo_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        filename = data_dir / f"trades_final_{slug}_{mode_suffix}{trading_suffix}.csv"
        
        # Use mode change detection from earlier
        rebuild_completely = mode_change_detected or existing_trades.empty
        
        # In 24h mode or if current expected CSV has too few distinct days, force rebuild
        min_days_required = 3
        if full_day_trading:
            rebuild_completely = True
            print("ℹ️  24h mode: forcing complete rebuild using default since range.")
        else:
            # Check coverage if file exists
            try:
                if filename.exists():
                    temp_df = pd.read_csv(filename)
                    if "entry_time" in temp_df.columns and not temp_df.empty:
                        distinct_days = pd.to_datetime(temp_df["entry_time"]).dt.date.nunique()
                        if distinct_days < min_days_required:
                            rebuild_completely = True
                            print(f"ℹ️  Coverage below threshold ({distinct_days}<{min_days_required}): forcing rebuild.")
            except Exception:
                pass

        if rebuild_completely:
            print(f"🔄 Rebuilding completely for {symbol} {mode} (24h: {full_day_trading})")
            # Replace CSV completely with new results, no concatenation
            combined = results.copy() if results is not None and not results.empty else pd.DataFrame()
        else:
            # Incremental update: merge existing and new results
            print(f"📈 Incremental update for {symbol} {mode} (24h: {full_day_trading})")
            combined = pd.DataFrame()
            if existing_trades is not None and not existing_trades.empty:
                combined = existing_trades.copy()
            if results is not None and not results.empty:
                combined = pd.concat([combined, results], ignore_index=True) if not combined.empty else results.copy()

        # If there is an active trade and we have a detected exit, append it if not present
        if active is not None:
            try:
                exit_eval = evaluate_active_trade_exit(active)
            except Exception:
                exit_eval = None
            if exit_eval is not None:
                # Build one-row DataFrame matching columns
                new_row = {
                    "day_key": pd.to_datetime(active.entry_time).date().isoformat(),
                    "entry_time": pd.to_datetime(active.entry_time),
                    "side": active.side,
                    "entry_price": active.entry_price,
                    "sl": active.stop_loss,
                    "tp": active.take_profit,
                    "exit_time": exit_eval["exit_time"],
                    "exit_price": exit_eval["exit_price"],
                    "exit_reason": exit_eval["exit_reason"],
                    "pnl_usdt": (exit_eval["exit_price"] - active.entry_price) if active.side == "long" else (active.entry_price - exit_eval["exit_price"]),
                    "r_multiple": None,
                    "used_fallback": None,
                    "mode": mode,
                }
                combined = pd.concat([combined, pd.DataFrame([new_row])], ignore_index=True) if combined is not None else pd.DataFrame([new_row])
                try:
                    clear_active_trade()
                except Exception:
                    pass
        
        # Always write CSV even if empty, with standard columns
        standard_cols = [
            "day_key","entry_time","side","entry_price","sl","tp","exit_time","exit_price","exit_reason","pnl_usdt","r_multiple","used_fallback","mode"
        ]
        if combined is None or combined.empty:
            combined = pd.DataFrame(columns=standard_cols)
        
        # Normalize datetime and sort
        if "entry_time" in combined.columns:
            combined["entry_time"] = pd.to_datetime(combined["entry_time"]) 
        if "exit_time" in combined.columns:
            combined["exit_time"] = pd.to_datetime(combined["exit_time"]) 
        
        # Drop duplicates by key columns
        dedup_keys = [col for col in ["entry_time", "exit_time", "side", "entry_price", "exit_price"] if col in combined.columns]
        if dedup_keys:
            combined = combined.drop_duplicates(subset=dedup_keys, keep="first")
        
        # Add mode column to track which mode generated these trades
        combined["mode"] = mode
        
        # Sort by entry_time
        if "entry_time" in combined.columns:
            combined = combined.sort_values(by="entry_time").reset_index(drop=True)
        
        # Save combined DataFrame
        combined.to_csv(filename, index=False)
        # Write sidecar meta with last_backtest_until, symbol, mode, full_day_trading and last_trade_date
        try:
            import json as _json
            base_no_ext = filename.with_suffix("")
            sidecar_out = Path(str(base_no_ext) + "_meta.json")
            
            # Calculate last_trade_date from actual trades
            last_trade_date = None
            if not combined.empty and "entry_time" in combined.columns:
                try:
                    max_entry = pd.to_datetime(combined["entry_time"]).max()
                    if pd.notna(max_entry):
                        last_trade_date = max_entry.date().isoformat()
                except Exception:
                    pass
            
            meta_payload = {
                "last_backtest_until": until,
                "last_trade_date": last_trade_date,  # Last actual trade date
                "symbol": symbol,
                "mode": mode,
                "full_day_trading": bool(full_day_trading),
                "backtest_start_date": (start_override or default_since),
            }
            sidecar_out.write_text(_json.dumps(meta_payload, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"⚠️ Could not write sidecar meta: {e}")
        print(f"✅ Saved {len(combined)} total trades to {filename}")
        return f"OK: Saved {len(combined)} total trades to {filename} (since {since} until {until})"
            
    except Exception as e:
        return f"ERROR: refresh_trades failed for {symbol} {mode}: {str(e)}"


def load_trades(symbol: str | None = None, mode: str | None = None, full_day_trading: bool = False, csv_path: str = "trades_final.csv") -> pd.DataFrame:
    """
    Load trades data from CSV files with support for different trading modes.
    
    Args:
        symbol: Trading symbol (e.g., 'BTC/USDT:USDT')
        mode: Trading mode ('conservative', 'moderate', 'aggressive')
        full_day_trading: If True, loads 24-hour trading data (files with _24h suffix)
        csv_path: Fallback CSV path if specific files not found
    
    Returns:
        DataFrame with trades data
        
    Note:
        Files are searched in order of preference:
        1. trades_final_{symbol}_{mode}_{24h}.csv (if full_day_trading=True)
        2. trades_final_{symbol}_{mode}.csv (if full_day_trading=False)
        3. Generic fallbacks
    """
    slug = None
    if symbol:
        slug = symbol.replace('/', '_').replace(':', '_')
    mode_suffix = (mode or "").lower().strip()
    
    # Create suffix for full_day_trading mode
    trading_suffix = "_24h" if full_day_trading else ""
    
    print(f"📂 load_trades called: symbol={symbol}, mode={mode}, 24h={full_day_trading}")
    
    # Build absolute paths based on repo_root, restricted to data/ and explicit csv_path
    candidates = []
    data_dir = repo_root / "data"
    if slug:
        if mode_suffix:
            candidates.append(data_dir / f"trades_final_{slug}_{mode_suffix}{trading_suffix}.csv")
        candidates.append(data_dir / f"trades_final_{slug}{trading_suffix}.csv")
    if mode_suffix:
        candidates.append(data_dir / f"trades_final_{mode_suffix}{trading_suffix}.csv")
    candidates.append(repo_root / "data" / "trades_final.csv")
    # Explicit parameter path last
    candidates.append(repo_root / csv_path)
    
    for path in candidates:
        try:
            if not path.exists():
                continue
            df = pd.read_csv(path)
            if df.empty:
                continue
            # Freshness validation via sidecar
            try:
                meta_base = path.with_suffix("")
                meta_path = Path(str(meta_base) + "_meta.json")
                if not meta_path.exists():
                    raise FileNotFoundError("Missing sidecar meta")
                import json as _json
                meta = _json.loads(meta_path.read_text(encoding="utf-8"))
                last_until = meta.get("last_backtest_until")
                last_trade_date = meta.get("last_trade_date")  # New field for last actual trade
                today_date = datetime.now(timezone.utc).date().isoformat()
                
                # Check if sidecar covers current session
                if last_until is not None and last_until >= today_date:
                    # File is fresh, but check if we have actual trades
                    if "entry_time" in df.columns and not df["entry_time"].isna().all():
                        max_entry = pd.to_datetime(df["entry_time"]).max()
                        if pd.notna(max_entry):
                            max_entry_date = max_entry.date().isoformat()
                            # Accept if max_entry_date <= today (not future) and sidecar covers today
                            if max_entry_date > today_date:
                                print(f"⚠️ Future entry date ignored: {path} (max_entry={max_entry_date})")
                                continue
                        # If no valid entry_time or empty, but sidecar covers today, accept empty file
                    # If no entry_time column but sidecar is fresh, accept the file
                else:
                    # Sidecar doesn't cover current session, reject
                    print(f"⚠️ Stale sidecar ignored: {path} (last_until={last_until}, today={today_date})")
                    continue
            except Exception as e:
                print(f"⚠️ Freshness validation failed for {path}: {e}")
                continue
            print(f"✅ Loaded trades from: {path} ({len(df)} rows)")
            # Normalize times
            if "entry_time" in df.columns:
                df["entry_time"] = pd.to_datetime(df["entry_time"])
            if "exit_time" in df.columns:
                df["exit_time"] = pd.to_datetime(df["exit_time"]) 
            # Filter by symbol if column exists and symbol provided
            if symbol and "symbol" in df.columns:
                df = df[df["symbol"] == symbol]
            # Sort recent first
            if "entry_time" in df.columns:
                df = df.sort_values(by="entry_time", ascending=False)
            # Return only if any data remains
            if df is not None and not df.empty:
                return df
        except Exception as e:
            print(f"❌ Failed to load {path}: {e}")
            continue
    print(f"❌ No valid trades found for {symbol} {mode}")
    return pd.DataFrame()


def compute_metrics(trades: pd.DataFrame, initial_capital: float = 1000.0, leverage: float = 1.0) -> dict:
    if trades.empty:
        return {
            "total_trades": 0, "win_rate": 0.0, "total_pnl": 0.0, "max_drawdown": 0.0, 
            "avg_risk_per_trade": 0.0, "dd_in_r": 0.0, "initial_capital": initial_capital,
            "current_capital": initial_capital, "roi": 0.0, "leverage": leverage
        }
    df = trades.copy()
    if "entry_time" in df.columns:
        df["entry_time"] = pd.to_datetime(df["entry_time"])  # ensure
        df = df.sort_values(by="entry_time", ascending=True)
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
    
    # Capital metrics
    current_capital = initial_capital + total_pnl
    roi = (total_pnl / initial_capital) * 100 if initial_capital > 0 else 0.0
    
    return {
        "total_trades": total_trades, "win_rate": win_rate, "total_pnl": total_pnl, 
        "max_drawdown": max_drawdown, "avg_risk_per_trade": avg_risk, "dd_in_r": dd_in_r,
        "initial_capital": initial_capital, "current_capital": current_capital, 
        "roi": roi, "leverage": leverage
    }


def figure_equity_curve(trades: pd.DataFrame):
    if trades.empty:
        return go.Figure()
    df = trades.copy()
    if "entry_time" in df.columns:
        df["entry_time"] = pd.to_datetime(df["entry_time"])  # ensure
        df = df.sort_values(by="entry_time", ascending=True)
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
    if "entry_time" in df.columns:
        df["entry_time"] = pd.to_datetime(df["entry_time"])  # ensure
        df = df.sort_values(by="entry_time", ascending=True)
    df["cumulative_pnl"] = df["pnl_usdt"].cumsum()
    df["running_max"] = df["cumulative_pnl"].cummax()
    df["drawdown"] = df["cumulative_pnl"] - df["running_max"]
    fig = px.area(df, x="entry_time", y="drawdown", title="Drawdown")
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

        # Try original symbol first; if empty, try without futures settle suffix
        price = fetch_historical_data(symbol, start_date, end_date, timeframe)
        if price is None or price.empty:
            alt_symbol = symbol.replace(":USDT", "") if ":USDT" in symbol else symbol
            price = fetch_historical_data(alt_symbol, start_date, end_date, timeframe)
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
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
    app.title = "One Trade"

    navbar = dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("One Trade", className="fw-bold"),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(dbc.Row([
                dbc.Col(dbc.Select(id="symbol-dropdown", options=[{"label": s, "value": s} for s in DEFAULT_SYMBOLS], value="BTC/USDT:USDT" , className="me-2"), md="auto"),
                dbc.Col(dbc.RadioItems(id="investment-mode", options=[{"label": "Conservador", "value": "conservative"}, {"label": "Moderado", "value": "moderate"}, {"label": "Arriesgado", "value": "aggressive"}], value="moderate", inline=True, className="me-3", labelClassName="text-white"), md="auto"),
                dbc.Col(dbc.Switch(id="full-day-trading", label="Trading 24h", value=False, className="me-3", labelClassName="text-white"), md="auto"),
                dbc.Col(dbc.Button("Refrescar", id="refresh", color="primary", className="text-white"), md="auto"),
            ], align="center", className="g-2"), id="navbar-collapse", is_open=True)
        ]), color="dark", dark=True, className="mb-3"
    )

    app.layout = dbc.Container([
        navbar,

        dbc.Alert(id="alert", is_open=False, color="warning"),

        dbc.Card([
            dbc.CardHeader("Precio Actual"),
            dbc.CardBody(id="current-price"),
        ], className="mb-4"),

        dbc.Card([
            dbc.CardHeader("Recomendación de hoy"),
            dbc.CardBody(id="today-reco"),
        ], className="mb-4"),

        dbc.Card([
            dbc.CardHeader("Métricas"),
            dbc.CardBody(id="metrics"),
        ], className="mb-4"),

        dcc.Tabs([
            dcc.Tab(label="Equity Curve", children=[dcc.Loading(children=dcc.Graph(id="equity-fig"), type="dot")]),
            dcc.Tab(label="PnL Distribution", children=[dcc.Loading(children=dcc.Graph(id="pnl-fig"), type="dot")]),
            dcc.Tab(label="Drawdown", children=[dcc.Loading(children=dcc.Graph(id="dd-fig"), type="dot")]),
            dcc.Tab(label="Trade Timeline", children=[dcc.Loading(children=dcc.Graph(id="timeline-fig"), type="dot")]),
            dcc.Tab(label="Monthly Performance", children=[dcc.Loading(children=dcc.Graph(id="monthly-fig"), type="dot")]),
            dcc.Tab(label="Win/Loss", children=[dcc.Loading(children=dcc.Graph(id="winloss-fig"), type="dot")]),
            dcc.Tab(label="Price Chart", children=[dcc.Loading(children=dcc.Graph(id="price-fig"), type="dot")]),
            dcc.Tab(label="Trades", children=[
                dbc.Card([
                    dbc.CardHeader([
                        html.H6("Historial de Operaciones", className="mb-0"),
                        html.Small("Detalle de todas las operaciones ejecutadas", className="text-muted")
                    ]),
                    dbc.CardBody([
                        html.Div([
                            html.H6("Descripción de Columnas:", className="mb-2"),
                            html.Ul([
                                html.Li([html.Strong("Entry Time: "), "Momento de entrada a la operación"]),
                                html.Li([html.Strong("Side: "), "Dirección de la operación (Long/Short)"]),
                                html.Li([html.Strong("Entry: "), "Precio de entrada"]),
                                html.Li([html.Strong("Exit: "), "Precio de salida"]),
                                html.Li([html.Strong("PnL: "), "Ganancia/pérdida neta en USDT"]),
                                html.Li([html.Strong("R: "), "Múltiplo de riesgo (ganancia/pérdida vs riesgo asumido)"]),
                                html.Li([html.Strong("Exit Time: "), "Momento de salida de la operación"]),
                                html.Li([html.Strong("Reason: "), "Razón de salida (take_profit, stop_loss, session_end)"])
                            ], className="mb-3")
                        ]),
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
                    ])
                ])
            ]),
        ]),
    ], fluid=True)

    @app.callback(
        Output("current-price", "children"),
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
        Input("symbol-dropdown", "value"),
        Input("refresh", "n_clicks"),
        Input("investment-mode", "value"),
        Input("full-day-trading", "value"),
        prevent_initial_call=False,
    )
    def update_dashboard(symbol, n_clicks, mode, full_day_trading):
        symbol = (symbol or "BTC/USDT:USDT").strip()
        
        # Fetch latest price
        price_info = None
        if fetch_latest_price is not None:
            try:
                price_info = fetch_latest_price(symbol)
            except Exception as e:
                print(f"Error fetching latest price: {e}")
        
        # Refresh trades data first
        refresh_msg = ""
        try:
            refresh_msg = refresh_trades(symbol, mode or "moderate", full_day_trading or False)
        except Exception as e:
            refresh_msg = f"Error refreshing trades: {str(e)}"
        
        # Load updated trades
        trades = load_trades(symbol, mode or "moderate", full_day_trading or False)
        # Load active trade if any to reflect in UI
        active_trade = None
        try:
            from btc_1tpd_backtester.live_monitor import load_active_trade
            active_trade = load_active_trade()
        except Exception:
            active_trade = None
        alert_msg = ""
        # Read sidecar for last_backtest_until
        try:
            slug = symbol.replace('/', '_').replace(':', '_')
            mode_suffix = (mode or "moderate").lower()
            trading_suffix = "_24h" if (full_day_trading or False) else ""
            meta_path = (repo_root / "data" / f"trades_final_{slug}_{mode_suffix}{trading_suffix}").with_suffix("")
            meta_path = Path(str(meta_path) + "_meta.json")
            last_until = None
            if meta_path.exists():
                import json
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                last_until = meta.get("last_backtest_until")
        except Exception:
            last_until = None
        mode_display = {"conservative": "Conservador", "moderate": "Moderado", "aggressive": "Agresivo"}.get((mode or "moderate").lower(), (mode or "moderate").capitalize())
        if trades.empty and active_trade is None:
            # If last_backtest_until is today, clarify there were no trades
            today_iso = datetime.now(timezone.utc).date().isoformat()
            if last_until == today_iso:
                alert_msg = f"Actualizado al {today_iso}. No hubo operaciones en la sesión."
            else:
                alert_msg = f"No hay datos para {symbol} en modo {mode_display}. {refresh_msg}"
        elif refresh_msg and "Error" in refresh_msg:
            alert_msg = f"Error en modo {mode_display}: {refresh_msg}"
        elif active_trade is not None:
            alert_msg = f"Operación activa: {active_trade.side.upper()} a {active_trade.entry_price} (SL {active_trade.stop_loss}, TP {active_trade.take_profit})."

        # Get effective configuration with full_day_trading parameter
        config = get_effective_config(symbol, mode or "moderate", full_day_trading or False)
        # Add full_day_trading to config
        config['full_day_trading'] = full_day_trading or False
        m = compute_metrics(trades, config.get('initial_capital', 1000.0), config.get('leverage', 1.0))
        def kpi_card(title: str, value: str, color: str, icon: str, description: str = None, tooltip_id: str = None):
            help_icon = html.I(className="bi bi-question-circle ms-1 text-muted", id=tooltip_id) if description else None
            title_with_help = html.Div([
                html.I(className=f"bi {icon} me-2"), 
                html.Small(title, className="text-muted"),
                help_icon
            ])
            
            card_content = dbc.Card([
                dbc.CardBody([
                    title_with_help,
                    html.H4(value, className=f"mt-2 text-{color}"),
                ])
            ], className="shadow-sm")
            
            if description and tooltip_id:
                return dbc.Col([
                    card_content,
                    dbc.Tooltip(description, target=tooltip_id, placement="top")
                ], md=3, sm=6, xs=12)
            else:
                return dbc.Col(card_content, md=3, sm=6, xs=12)

        win_color = "success" if m['win_rate'] >= 50 else "warning" if m['win_rate'] > 0 else "secondary"
        pnl_color = "success" if m['total_pnl'] >= 0 else "danger"
        dd_color = "danger" if m['max_drawdown'] < 0 else "secondary"
        roi_color = "success" if m['roi'] >= 0 else "danger"

        metrics_children = dbc.Row([
            kpi_card("Total trades", f"{m['total_trades']}", "primary", "bi-collection", 
                    "Número total de operaciones ejecutadas", "tooltip-trades"),
            kpi_card("Win rate", f"{m['win_rate']:.1f}%", win_color, "bi-bullseye", 
                    "Porcentaje de operaciones ganadoras vs perdedoras", "tooltip-winrate"),
            kpi_card("PnL", f"{m['total_pnl']:+,.2f} USDT", pnl_color, "bi-cash-stack", 
                    "Ganancia o pérdida total en USDT", "tooltip-pnl"),
            kpi_card("Max DD", f"{m['max_drawdown']:.2f} USDT ({m['dd_in_r']:.2f} R)", dd_color, "bi-graph-down", 
                    "Máxima pérdida desde un pico de capital (en USDT y múltiplos de riesgo)", "tooltip-dd"),
            kpi_card("Riesgo/trade", f"{m['avg_risk_per_trade']:.2f} USDT", "info", "bi-shield", 
                    "Promedio de riesgo por operación en USDT", "tooltip-risk"),
            kpi_card("ROI", f"{m['roi']:+.1f}%", roi_color, "bi-graph-up", 
                    "Retorno sobre inversión inicial", "tooltip-roi"),
        ], className="g-3")
        
        # Capital information section
        capital_info = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Información de Capital", className="card-title"),
                        html.P([
                            html.Strong("Capital inicial: "), f"{m['initial_capital']:,.2f} USDT", html.Br(),
                            html.Strong("Capital actual: "), f"{m['current_capital']:,.2f} USDT", html.Br(),
                            html.Strong("Apalancamiento: "), f"{m['leverage']:.1f}x", html.Br(),
                            html.Strong("Inversión efectiva: "), f"{m['initial_capital'] * m['leverage']:,.2f} USDT"
                        ])
                    ])
                ], className="shadow-sm")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Resumen de Rendimiento", className="card-title"),
                        html.P([
                            html.Strong("ROI: "), f"{m['roi']:+.2f}%", html.Br(),
                            html.Strong("PnL vs Capital: "), f"{(m['total_pnl']/m['initial_capital']*100):+.2f}%", html.Br(),
                            html.Strong("Drawdown máximo: "), f"{abs(m['max_drawdown']/m['initial_capital']*100):.2f}% del capital"
                        ])
                    ])
                ], className="shadow-sm")
            ], md=6)
        ], className="g-3 mb-4")

        eq = figure_equity_curve(trades)
        pnl = figure_pnl_distribution(trades)
        dd = figure_drawdown(trades)
        tl = figure_trade_timeline(trades)
        mon = figure_monthly_performance(trades)
        wl = figure_win_loss(trades)
        price_fig = figure_trades_on_price(trades, symbol)

        # Today recommendation via live monitor
        reco_children = html.Div("Se requiere módulo de señales.")
        try:
            from btc_1tpd_backtester.live_monitor import detect_or_update_active_trade
            merged_cfg = get_effective_config(symbol, mode, full_day_trading or False)
            merged_cfg['full_day_trading'] = full_day_trading or False
            active_or_rec = detect_or_update_active_trade(symbol, mode, full_day_trading or False, merged_cfg)
            # Build card from active_or_rec when we have params
            if active_or_rec is not None:
                side = getattr(active_or_rec, 'side', None) or (active_or_rec.get('side') if isinstance(active_or_rec, dict) else None)
                entry_price = getattr(active_or_rec, 'entry_price', None) or (active_or_rec.get('entry_price') if isinstance(active_or_rec, dict) else None)
                stop_loss = getattr(active_or_rec, 'stop_loss', None) or (active_or_rec.get('stop_loss') if isinstance(active_or_rec, dict) else None)
                take_profit = getattr(active_or_rec, 'take_profit', None) or (active_or_rec.get('take_profit') if isinstance(active_or_rec, dict) else None)
                entry_time_val = getattr(active_or_rec, 'entry_time', None) or (active_or_rec.get('entry_time') if isinstance(active_or_rec, dict) else None)
                badge_color = "secondary" if not side else ("success" if side == "long" else "danger")
                reco_children = html.Div([
                    html.Div([html.B("Símbolo: "), html.Span(symbol)]),
                    html.Div([html.B("Dirección: "), dbc.Badge((side or "-").lower(), color=badge_color, className="ms-1")]),
                    html.Div([html.B("Hora entrada: "), str(entry_time_val or "-")]),
                    html.Div([html.B("Entrada: "), f"{entry_price if entry_price is not None else '-'}"]),
                    html.Div([html.B("SL: "), f"{stop_loss if stop_loss is not None else '-'}"]),
                    html.Div([html.B("TP: "), f"{take_profit if take_profit is not None else '-'}"]),
                ])
        except Exception:
            pass

        # Current price display
        if price_info and price_info.get('price'):
            price_display = html.Div([
                html.Div([
                    html.H4(f"${price_info['price']:,.2f}", className="text-primary mb-1"),
                    html.Small(f"{symbol} • {price_info['timestamp'].strftime('%H:%M:%S UTC')}", className="text-muted")
                ], className="d-flex justify-content-between align-items-center"),
                html.Hr(className="my-2"),
                html.Div([
                    html.Small([
                        html.Strong("Bid: "), f"${price_info.get('bid', 0):,.2f}" if price_info.get('bid') is not None else "N/A", " • ",
                        html.Strong("Ask: "), f"${price_info.get('ask', 0):,.2f}" if price_info.get('ask') is not None else "N/A", " • ",
                        html.Strong("Vol: "), f"{price_info.get('volume', 0):,.0f}"
                    ], className="text-muted")
                ])
            ])
        else:
            missing_msg = "fetch_latest_price no disponible" if fetch_latest_price is None else "No se pudo obtener el precio actual"
            price_display = html.Div([
                html.P(missing_msg, className="text-muted mb-0"),
                html.Small(f"{symbol} • {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}", className="text-muted")
            ])

        # If no data, still return empty figures but show alert clearly
        table_data = []
        if not trades.empty:
            tbl = trades.copy()
            # Ordering recent first
            if "entry_time" in tbl.columns:
                tbl = tbl.sort_values(by="entry_time", ascending=False)
            # Convert datetimes to ISO for DataTable
            for col in ["entry_time", "exit_time"]:
                if col in tbl.columns:
                    tbl[col] = pd.to_datetime(tbl[col]).dt.strftime("%Y-%m-%d %H:%M:%S")
            # Columns to show (only those that exist)
            desired_cols = [
                "entry_time", "side", "entry_price", "exit_price", "pnl_usdt", "r_multiple", "exit_time", "exit_reason"
            ]
            cols = [c for c in desired_cols if c in tbl.columns]
            table_data = tbl[cols].to_dict("records")
        # Prepend active trade row (without exit) at top of table if present
        if active_trade is not None:
            try:
                active_row = {
                    "entry_time": pd.to_datetime(active_trade.entry_time).strftime("%Y-%m-%d %H:%M:%S"),
                    "side": active_trade.side,
                    "entry_price": active_trade.entry_price,
                    "exit_price": None,
                    "pnl_usdt": None,
                    "r_multiple": None,
                    "exit_time": None,
                    "exit_reason": "active",
                }
                table_data = [active_row] + table_data
            except Exception:
                pass

        return price_display, reco_children, [capital_info, metrics_children], eq, pnl, dd, tl, mon, wl, price_fig, table_data, bool(alert_msg), alert_msg

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8050, debug=True)


