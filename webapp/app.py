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
import time
import logging
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for Python < 3.9
    from backports.zoneinfo import ZoneInfo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    "commission_rate": 0.001,  # 0.1% default
    "slippage_rate": 0.0005,   # 0.05% default
    "initial_capital": 1000.0, # Initial capital in USDT
    "leverage": 1.0,           # Leverage multiplier
    "full_day_trading": False,  # Default to session trading
    "force_one_trade": True,   # Always force one trade
    # Session trading parameters
    "session_trading": True,   # Enable session-based trading
    "entry_window": (11, 14),  # Entry window in local time (AR)
    "exit_window": (20, 22),   # Exit window in local time (AR)
    "session_timezone": "America/Argentina/Buenos_Aires",
    # Validation parameters
    "min_win_rate": 80.0,               # Minimum win rate percentage
    "min_pnl": 0.0,                     # Minimum PnL (must be > 0)
    "min_avg_r": 1.0,                   # Minimum average R-multiple
    "min_trades": 10,                   # Minimum number of trades
    "min_profit_factor": 1.2,           # Minimum profit factor
    # When rebuilding, start date or lookback control
    # IMPORTANT: Minimum 365 days (1 year) required for statistically significant backtests
    # This ensures sufficient data for both normal and inverted strategy validation
    "backtest_start_date": None,  # ISO date string e.g., "2024-01-01"
    "lookback_days": 365,  # Minimum 1 year of data
}
# Mode to assets mapping
MODE_ASSETS = {
    "conservative": [
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT"
    ],
    "moderate": [
        "BTC/USDT:USDT",
        "ETH/USDT:USDT", 
        "BNB/USDT:USDT",
        "SOL/USDT:USDT",
        "ADA/USDT:USDT"
    ],
    "aggressive": [
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "BNB/USDT:USDT", 
        "SOL/USDT:USDT",
        "ADA/USDT:USDT",
        "XRP/USDT:USDT",
        "DOGE/USDT:USDT",
        "AVAX/USDT:USDT"
    ]
}

MODE_CONFIG = {
    "conservative": {
        # Risk Management
        "risk_usdt": 15.0,
        "commission_rate": 0.001,
        "slippage_rate": 0.0005,
        "leverage": 1.0,
        "max_drawdown": 0.05,  # 5% max drawdown
        
        # Strategy: Mean Reversion + Bollinger/ATR/RSI
        "strategy_type": "mean_reversion",
        "bollinger_period": 20,
        "bollinger_std": 2.0,
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "atr_period": 14,
        "atr_multiplier": 1.5,
        "volume_threshold": 1.2,
        
        # Entry/Exit Rules
        "entry_conditions": ["bollinger_oversold", "rsi_oversold", "volume_confirmation"],
        "exit_conditions": ["bollinger_middle", "rsi_neutral", "atr_stop"],
        "target_r_multiple": 1.0,
        "risk_reward_ratio": 1.0,
        "allow_shorts": False,  # Conservative: long only
        
        # Validation
        "min_win_rate": 85.0,
        "min_avg_r": 1.0,
        "min_trades": 15,
        "min_profit_factor": 1.5,
    },
    "moderate": {
        # Risk Management
        "risk_usdt": 25.0,
        "commission_rate": 0.0012,
        "slippage_rate": 0.0008,
        "leverage": 1.0,
        "max_drawdown": 0.08,  # 8% max drawdown
        
        # Strategy: Trend Following + Heikin Ashi + ADX + EMA 9/21
        "strategy_type": "trend_following",
        "heikin_ashi": True,
        "adx_period": 14,
        "adx_threshold": 25,
        "ema_fast": 9,
        "ema_slow": 21,
        "atr_period": 14,
        "atr_multiplier": 2.0,
        "volume_threshold": 1.1,
        
        # Entry/Exit Rules
        "entry_conditions": ["trend_alignment", "adx_strength", "ema_crossover"],
        "exit_conditions": ["trend_reversal", "adx_weakness", "atr_stop"],
        "target_r_multiple": 1.5,
        "risk_reward_ratio": 1.5,
        "allow_shorts": True,  # Moderate: both directions
        
        # Validation
        "min_win_rate": 80.0,
        "min_avg_r": 1.5,
        "min_trades": 12,
        "min_profit_factor": 1.3,
    },
    "aggressive": {
        # Risk Management
        "risk_usdt": 40.0,
        "commission_rate": 0.0015,
        "slippage_rate": 0.001,
        "leverage": 1.0,
        "max_drawdown": 0.12,  # 12% max drawdown
        
        # Strategy: Breakout Fade + Counter-trend
        "strategy_type": "breakout_fade",
        "breakout_period": 20,
        "breakout_threshold": 0.02,  # 2% breakout
        "fade_conditions": ["volume_spike", "rsi_extreme", "bollinger_extreme"],
        "rsi_period": 14,
        "rsi_extreme_high": 80,
        "rsi_extreme_low": 20,
        "bollinger_period": 20,
        "bollinger_std": 2.5,
        "atr_period": 14,
        "atr_multiplier": 2.5,
        "volume_threshold": 1.5,
        
        # Entry/Exit Rules
        "entry_conditions": ["breakout_detected", "fade_signal", "volume_confirmation"],
        "exit_conditions": ["trend_continuation", "atr_stop", "time_exit"],
        "target_r_multiple": 2.0,
        "risk_reward_ratio": 2.0,
        "allow_shorts": True,  # Aggressive: both directions with shorts
        
        # Validation
        "min_win_rate": 75.0,
        "min_avg_r": 2.0,
        "min_trades": 10,
        "min_profit_factor": 1.2,
    },
}


def determine_price_date_range(symbol: str, since_date: str | None = None, lookback_days: int = 365) -> tuple[datetime, datetime]:
    """Guarantee the historical price chart always covers at least lookback_days (default 365), regardless of current mode or inversion state. Args: symbol: Trading symbol (e.g., 'BTC/USDT:USDT'), since_date: Optional ISO date string to use as start_date (will be expanded if too recent), lookback_days: Minimum number of days to cover (default 365). Returns: Tuple of (start_date, end_date) as timezone-aware datetimes in UTC."""
    end_date = datetime.now(timezone.utc)
    if since_date is None:
        start_date = end_date - timedelta(days=lookback_days)
    else:
        try:
            start_date = datetime.fromisoformat(since_date).replace(tzinfo=timezone.utc) if datetime.fromisoformat(since_date).tzinfo is None else datetime.fromisoformat(since_date).astimezone(timezone.utc)
        except Exception as e:
            logger.warning(f"Invalid since_date '{since_date}': {e}, falling back to {lookback_days} days ago")
            start_date = end_date - timedelta(days=lookback_days)
    days_diff = (end_date.date() - start_date.date()).days
    if days_diff < lookback_days:
        logger.info(f"Expanding date range from {days_diff} days to {lookback_days} days for {symbol}")
        start_date = end_date - timedelta(days=lookback_days)
    logger.info(f"Price chart date range for {symbol}: {start_date.date().isoformat()} to {end_date.date().isoformat()} ({(end_date.date() - start_date.date()).days} days)")
    return start_date, end_date


def build_candle_analysis_tasks(mode: str, inverted: bool = False) -> list[dict]:
    """Provide users with a dashboard card summarizing year-long candle review actions based on the selected mode and whether the strategy is inverted. Args: mode: Trading mode ('conservative', 'moderate', 'aggressive'), inverted: If True, adjust language for inverted strategy. Returns: List of dictionaries with 'title', 'description', and 'priority' fields."""
    inversion_note = " (estrategia invertida)" if inverted else ""
    base_tasks = [{"title": "Validar cobertura de datos", "description": f"Confirmar que el gráfico de precios muestra al menos 365 días de historia para análisis estadísticamente significativo{inversion_note}.", "priority": 1}, {"title": "Revisar patrones de largo plazo", "description": f"Identificar tendencias anuales, soportes/resistencias clave y eventos de mercado significativos{inversion_note}.", "priority": 2}]
    mode_tasks = {"conservative": [{"title": "Analizar zonas de sobrecompra/sobreventa anuales", "description": f"Revisar Bollinger Bands y RSI en gráfico anual para identificar zonas extremas{inversion_note}.", "priority": 2}, {"title": "Validar eficacia de reversión a la media", "description": f"Confirmar que la estrategia de reversión captura rebounds en zonas de sobreventa históricas{inversion_note}.", "priority": 3}], "moderate": [{"title": "Identificar tendencias dominantes anuales", "description": f"Analizar EMA 9/21 y ADX en timeframe anual para detectar fases alcistas/bajistas{inversion_note}.", "priority": 2}, {"title": "Evaluar consistencia de seguimiento de tendencia", "description": f"Verificar que las señales de Heikin Ashi se alineen con tendencias anuales confirmadas{inversion_note}.", "priority": 3}], "aggressive": [{"title": "Mapear breakouts y fakeouts históricos", "description": f"Revisar gráfico anual para identificar breakouts que fallaron y fueron faded exitosamente{inversion_note}.", "priority": 2}, {"title": "Analizar volatilidad extrema anual", "description": f"Estudiar eventos de RSI extremo (≥80/≤20) y Bollinger extremos en contexto anual{inversion_note}.", "priority": 3}]}
    mode_specific = mode_tasks.get(mode.lower(), mode_tasks["moderate"])
    all_tasks = base_tasks + mode_specific
    return all_tasks


def get_effective_config(symbol: str, mode: str) -> dict:
    """
    Return merged BASE_CONFIG with selected mode overrides. Uses session trading only.
    
    IMPORTANT: Enforces minimum 365-day lookback period for statistical significance.
    This is critical for both normal and inverted strategy validation.
    
    Args:
        symbol: Trading symbol
        mode: Trading mode ('conservative', 'moderate', 'aggressive')
        
    Returns:
        dict: Effective configuration with minimum 1-year lookback
    """
    mode_cfg = MODE_CONFIG.get((mode or "moderate").lower(), {})
    
    # Start with base config, then apply mode config
    config = {**BASE_CONFIG, **mode_cfg}
    
    # Always use session trading
    config["full_day_trading"] = False
    config["session_trading"] = True
    
    # Enforce minimum 365-day lookback (1 year minimum for valid backtests)
    # This prevents insufficient data errors and ensures statistical significance
    if "lookback_days" in config:
        config["lookback_days"] = max(365, config.get("lookback_days", 365))
    else:
        config["lookback_days"] = 365
    
    # If backtest_start_date is set, ensure it's at least 365 days ago
    if config.get("backtest_start_date"):
        start_date = datetime.fromisoformat(config["backtest_start_date"]).date()
        today = datetime.now(timezone.utc).date()
        days_diff = (today - start_date).days
        
        if days_diff < 365:
            logger.warning(f"backtest_start_date too recent ({days_diff} days), adjusting to 365 days ago")
            config["backtest_start_date"] = (today - timedelta(days=365)).isoformat()
    
    return config


def retry_with_backoff(func, max_retries=3, initial_delay=1.0, backoff_factor=2.0, exception_types=(Exception,)):
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry (should be a callable)
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Factor to multiply delay by after each retry
        exception_types: Tuple of exception types to catch and retry
    
    Returns:
        Result of successful function call
        
    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exception_types as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)}. Retrying in {delay:.1f}s...")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_retries + 1} attempts failed. Last error: {str(e)}")
    
    raise last_exception


# Timezone helper
ARGENTINA_TZ = ZoneInfo("America/Argentina/Buenos_Aires")

def to_argentina_time(dt):
    """Convert a datetime to Argentina timezone."""
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = pd.to_datetime(dt)
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ARGENTINA_TZ)

def format_argentina_time(dt, format_str="%Y-%m-%d %H:%M:%S %Z"):
    """Format a datetime to Argentina timezone string."""
    arg_dt = to_argentina_time(dt)
    if arg_dt is None:
        return ""
    return arg_dt.strftime(format_str)

# Default symbols (will be updated based on mode)
DEFAULT_SYMBOLS = MODE_ASSETS["moderate"]  # Default to moderate mode symbols

def get_symbols_for_mode(mode: str) -> list:
    """Get available symbols for a given mode."""
    return MODE_ASSETS.get(mode.lower(), MODE_ASSETS["moderate"])

# Strategy descriptions for UI
STRATEGY_DESCRIPTIONS = {
    "conservative": {
        "name": "Mean Reversion",
        "description": "Conservative strategy focused on mean reversion using Bollinger Bands, RSI, and ATR. Targets oversold conditions for long entries with tight risk management.",
        "tools": ["Bollinger Bands (20, 2.0σ)", "RSI (14)", "ATR (14)", "Volume Confirmation"],
        "rules": [
            "Long only - no short positions",
            "Enter on oversold conditions (price ≤ lower BB, RSI ≤ 30)",
            "Volume must be 1.2x above average",
            "Target: 1R with 1:1 risk-reward ratio",
            "Max drawdown: 5%"
        ],
        "risk_profile": "Low risk, high win rate (85%+), consistent small gains"
    },
    "moderate": {
        "name": "Trend Following", 
        "description": "Moderate strategy using Heikin Ashi, ADX, and EMA crossovers to follow trends. Balances risk and reward with both long and short positions.",
        "tools": ["Heikin Ashi", "ADX (14)", "EMA 9/21", "ATR (14)", "Volume Confirmation"],
        "rules": [
            "Long and short positions allowed",
            "Enter on EMA crossover with ADX > 25",
            "Volume must be 1.1x above average", 
            "Target: 1.5R with 1.5:1 risk-reward ratio",
            "Max drawdown: 8%"
        ],
        "risk_profile": "Medium risk, balanced win rate (80%+), moderate gains"
    },
    "aggressive": {
        "name": "Breakout Fade",
        "description": "Aggressive counter-trend strategy that fades breakouts using extreme RSI levels and Bollinger Band extremes. High risk, high reward approach.",
        "tools": ["Bollinger Bands (20, 2.5σ)", "RSI (14)", "ATR (14)", "Volume Spike Detection"],
        "rules": [
            "Long and short positions allowed",
            "Fade breakouts with extreme RSI (≥80 or ≤20)",
            "Volume must be 1.5x above average",
            "Target: 2R with 2:1 risk-reward ratio", 
            "Max drawdown: 12%"
        ],
        "risk_profile": "High risk, lower win rate (75%+), high potential gains"
    }
}


def refresh_trades(symbol: str, mode: str) -> str:
    """
    Refresh trades data by running backtest from last available date to today for a given symbol and mode.
    Uses session trading only.
    
    Args:
        symbol: Trading symbol (e.g., 'BTC/USDT:USDT')
        mode: Trading mode ('conservative', 'moderate', 'aggressive')
    
    Returns:
        Status message indicating success or failure
    """
    if run_backtest is None:
        return "Backtest module not available"
    
    print(f"[RUN] refresh_trades called: symbol={symbol}, mode={mode}")
    try:
        # Load existing trades for the current mode
        existing_trades = load_trades(symbol, mode)
        
        # Check for mode change by comparing file existence and current mode
        slug = symbol.replace('/', '_').replace(':', '_')
        mode_suffix = (mode or "moderate").lower()
        data_dir = repo_root / "data"
        
        expected_file = data_dir / f"trades_final_{slug}_{mode_suffix}.csv"

        # Sidecar meta path and stored full_day flag
        stored_full_day_flag = None
        try:
            sidecar_in = Path(str(expected_file.with_suffix("")) + "_meta.json")
            if sidecar_in.exists():
                import json as _json
                meta_in = _json.loads(sidecar_in.read_text(encoding="utf-8"))
                stored_full_day_flag = bool(meta_in.get("full_day_trading"))
        except Exception as e:
            print(f"[WARN] Could not read sidecar for mode detection: {e}")
            stored_full_day_flag = None

        # Mode change detected if expected CSV missing OR stored flag differs from 24h mode
        mode_change_detected = (
            not expected_file.exists() or
            (stored_full_day_flag is not None and stored_full_day_flag != True)
        )
        
        # Determine default since using config lookback/backtest_start_date
        # IMPORTANT: get_effective_config enforces minimum 365 days
        cfg_for_since = get_effective_config(symbol, mode)
        start_override = cfg_for_since.get("backtest_start_date")
        lb_days = cfg_for_since.get("lookback_days", 365)  # Will be at least 365 from get_effective_config
        default_since = (start_override or (datetime.now(timezone.utc).date() - timedelta(days=int(lb_days))).isoformat())
        
        # Check if existing trades cover sufficient history (365 days minimum)
        insufficient_history = False
        if not existing_trades.empty and "entry_time" in existing_trades.columns:
            df_dates = pd.to_datetime(existing_trades["entry_time"])
            earliest_date = df_dates.min().date()
            today = datetime.now(timezone.utc).date()
            days_coverage = (today - earliest_date).days
            
            if days_coverage < 365:
                logger.warning(f"Insufficient history: only {days_coverage} days, need 365+ for valid backtest")
                insufficient_history = True
        
        if mode_change_detected:
            logger.info(f"[RUN] Mode change detected: switching to session mode with 1-year history")
            # Clear existing trades and force rebuild
            existing_trades = pd.DataFrame()
            since = default_since
            logger.info(f"📅 Mode change: using default since date: {since} (365+ days)")
        elif insufficient_history:
            logger.info(f"[RUN] Insufficient history detected: forcing full rebuild with 1-year data")
            # Clear existing trades and force rebuild from 365 days ago
            existing_trades = pd.DataFrame()
            since = default_since
            logger.info(f"📅 Rebuilding from: {since} (365+ days)")
        elif not existing_trades.empty and "entry_time" in existing_trades.columns:
            # Incremental update: continue from last trade date
            df_dates = pd.to_datetime(existing_trades["entry_time"])
            last_date = df_dates.max().date()
            since = (last_date + timedelta(days=1)).isoformat()
            logger.info(f"📅 Incremental update from last trade date + 1 day: {since}")
        else:
            # No existing trades, start from default (365+ days ago)
            since = default_since
            logger.info(f"📅 No existing trades, using default since: {since} (365+ days)")
        
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
            print(f"[WARN] since/until parsing failed (continuing): {e}")
        
        # Merge base and mode config
        config = get_effective_config(symbol, mode)
        logger.info(f"[DATA] Effective config for {symbol} {mode}: {config}")
        
        # Run backtest with retry logic for network errors
        results = None
        error_type = None
        error_detail = None
        
        try:
            def run_backtest_with_params():
                return run_backtest(symbol, since, until, config)
            
            # Retry with backoff for common transient errors
            results = retry_with_backoff(
                run_backtest_with_params,
                max_retries=3,
                initial_delay=2.0,
                backoff_factor=2.0,
                exception_types=(ConnectionError, TimeoutError, OSError)
            )
            logger.info(f"[OK] Backtest completed successfully for {symbol} {mode}")
        except (ConnectionError, TimeoutError, OSError) as e:
            error_type = "network"
            error_detail = str(e)
            logger.error(f"[FAIL] Network error after retries: {error_detail}")
        except Exception as e:
            error_type = "general"
            error_detail = str(e)
            logger.error(f"[FAIL] Backtest error: {error_detail}")
        
        # Extract trades DataFrame from results
        trades_df = results.trades_df if results is not None else pd.DataFrame()
        
        # Check if strategy is suitable (only if we have results)
        if results is not None and not results.is_strategy_suitable():
            logger.warning("\n[WARN] WARNING: Strategy failed validation criteria!")
            logger.warning("Consider adjusting parameters or strategy configuration.")
            logger.warning(f"Validation summary: {results.get_validation_summary()}")

        # Sync with live active trade state
        try:
            from btc_1tpd_backtester.live_monitor import load_active_trade, evaluate_active_trade_exit, clear_active_trade
            active = load_active_trade()
        except Exception:
            active = None
        
        # Determine filename with absolute path
        slug = symbol.replace('/', '_').replace(':', '_')
        mode_suffix = (mode or "moderate").lower()
        data_dir = repo_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        filename = data_dir / f"trades_final_{slug}_{mode_suffix}.csv"
        
        # Determine if complete rebuild is needed
        # Rebuild when: mode changed, no existing trades, or insufficient history (< 365 days)
        rebuild_completely = mode_change_detected or existing_trades.empty or insufficient_history
        
        # Define standard columns early to avoid FutureWarning
        standard_cols = [
            "day_key","entry_time","side","entry_price","sl","tp","exit_time","exit_price","exit_reason","pnl_usdt","r_multiple","used_fallback","mode"
        ]
        
        logger.info(f"ℹ️  session mode: {'forcing complete rebuild' if rebuild_completely else 'incremental update'}.")

        if rebuild_completely:
            print(f"[RUN] Rebuilding completely for {symbol} {mode}")
            # Replace CSV completely with new results, no concatenation
            combined = trades_df.copy() if not trades_df.empty else pd.DataFrame()
        else:
            print(f"[RUN] Incremental update for {symbol} {mode}")
            # Concatenate existing trades with new results
            if not trades_df.empty:
                combined = pd.concat([existing_trades, trades_df], ignore_index=True)
            else:
                combined = existing_trades.copy()

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
                # Create new row with standard columns to avoid FutureWarning
                new_row_df = pd.DataFrame([new_row], columns=standard_cols)
                if combined.empty:
                    combined = new_row_df
                else:
                    combined = pd.concat([combined, new_row_df], ignore_index=True)
                try:
                    clear_active_trade()
                except Exception:
                    pass
        
        # Initialize combined with standard columns to avoid FutureWarning
        if combined is None or combined.empty:
            combined = pd.DataFrame(columns=standard_cols)
        else:
            # Ensure combined has all standard columns
            for col in standard_cols:
                if col not in combined.columns:
                    combined[col] = None
        
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
        
        # CRITICAL VALIDATION: Block persistence if coverage < 365 days
        actual_lookback_days_check = None
        if not combined.empty and "entry_time" in combined.columns:
            try:
                dates = pd.to_datetime(combined["entry_time"])
                if not dates.empty:
                    min_entry = dates.min()
                    max_entry = dates.max()
                    if pd.notna(min_entry) and pd.notna(max_entry):
                        actual_lookback_days_check = (max_entry.date() - min_entry.date()).days
            except Exception as e:
                logger.error(f"Failed to check coverage before save: {e}")
        
        if actual_lookback_days_check is not None and actual_lookback_days_check < 365:
            error_msg = f"BLOCKED: Refusing to persist data with insufficient coverage: {actual_lookback_days_check} days < 365 days minimum. Symbol: {symbol}, Mode: {mode}. Please force a complete rebuild: python manage_backtests.py --since=full --force-rebuild"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"
        
        if combined.empty and rebuild_completely:
            error_msg = f"BLOCKED: Refusing to persist empty DataFrame after complete rebuild. Symbol: {symbol}, Mode: {mode}. Check logs for fetch errors. Last error: {error_detail if error_detail else 'None'}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"
        
        # Save combined DataFrame
        combined.to_csv(filename, index=False)
        
        # Write sidecar meta with last_backtest_until, symbol, mode, full_day_trading and last_trade_date
        # IMPORTANT: Always update meta.json even if there were errors, to mark that we attempted an update
        try:
            import json as _json
            base_no_ext = filename.with_suffix("")
            sidecar_out = Path(str(base_no_ext) + "_meta.json")
            
            # Calculate last_trade_date and first_trade_date from actual trades
            last_trade_date = None
            first_trade_date = None
            actual_lookback_days = None
            
            if not combined.empty and "entry_time" in combined.columns:
                try:
                    dates = pd.to_datetime(combined["entry_time"])
                    max_entry = dates.max()
                    min_entry = dates.min()
                    
                    if pd.notna(max_entry):
                        last_trade_date = max_entry.date().isoformat()
                    if pd.notna(min_entry):
                        first_trade_date = min_entry.date().isoformat()
                    
                    # Calculate actual coverage in days
                    if pd.notna(min_entry) and pd.notna(max_entry):
                        actual_lookback_days = (max_entry.date() - min_entry.date()).days
                except Exception as e:
                    logger.warning(f"Could not calculate trade date range: {e}")
            
            meta_payload = {
                "last_backtest_until": until,
                "last_trade_date": last_trade_date,  # Last actual trade date
                "first_trade_date": first_trade_date,  # First actual trade date
                "actual_lookback_days": actual_lookback_days,  # Actual coverage in days
                "last_update_attempt": datetime.now(timezone.utc).isoformat(),  # Track when we last tried
                "symbol": symbol,
                "mode": mode,
                "full_day_trading": config.get("full_day_trading", False),
                "session_trading": config.get("session_trading", True),
                "validation_results": results.validation_results if results is not None else None,
                "is_strategy_suitable": results.is_strategy_suitable() if results is not None else None,
                "backtest_start_date": since,  # Actual 'since' used for this backtest
                "configured_lookback_days": lb_days,  # Configured lookback (should be >= 365)
                "total_trades": len(combined),  # Total trades in file
                "rebuild_type": "complete" if rebuild_completely else "incremental",
                "last_error": None if error_type is None else {
                    "type": error_type,
                    "detail": error_detail,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            sidecar_out.write_text(_json.dumps(meta_payload, indent=2, ensure_ascii=False))
            logger.info(f"[OK] Updated meta.json for {symbol} {mode}")
        except Exception as e:
            logger.error(f"[WARN] Could not write sidecar meta: {e}")
        
        logger.info(f"[OK] Saved {len(combined)} total trades to {filename}")
        
        # Construct detailed return message based on outcome
        if error_type == "network":
            return f"WARNING: Network error after retries ({error_detail}). Data refreshed to {until} but may be incomplete. Check your internet connection."
        elif error_type == "general":
            return f"ERROR: Backtest failed ({error_detail}). Data refreshed to {until} but may be incomplete."
        elif len(trades_df) == 0 and results is not None:
            return f"OK: No new trades generated (since {since} until {until}). Total: {len(combined)} trades."
        else:
            return f"OK: Saved {len(combined)} total trades to {filename} (since {since} until {until})"
            
    except Exception as e:
        logger.exception(f"[ERROR] Critical error in refresh_trades for {symbol} {mode}")
        return f"ERROR: refresh_trades failed for {symbol} {mode}: {str(e)}"


def load_trades(symbol: str | None = None, mode: str | None = None, csv_path: str = "trades_final.csv") -> pd.DataFrame:
    """
    Load trades data from CSV files. Always uses 24-hour trading mode.
    
    Args:
        symbol: Trading symbol (e.g., 'BTC/USDT:USDT')
        mode: Trading mode ('conservative', 'moderate', 'aggressive')
        csv_path: Fallback CSV path if specific files not found
    
    Returns:
        DataFrame with trades data
        
    Note:
        Files are searched in order of preference:
        1. trades_final_{symbol}_{mode}.csv
        2. Generic fallbacks
    """
    slug = None
    if symbol:
        slug = symbol.replace('/', '_').replace(':', '_')
    mode_suffix = (mode or "").lower().strip()
    
    print(f"[FOLDER] load_trades called: symbol={symbol}, mode={mode}, 24h=True")
    
    # Build absolute paths based on repo_root, restricted to data/ and explicit csv_path
    candidates = []
    data_dir = repo_root / "data"
    if slug:
        if mode_suffix:
            candidates.append(data_dir / f"trades_final_{slug}_{mode_suffix}.csv")
        candidates.append(data_dir / f"trades_final_{slug}.csv")
    if mode_suffix:
        candidates.append(data_dir / f"trades_final_{mode_suffix}.csv")
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
            
            # Tolerant date parsing for entry_time and exit_time columns
            if "entry_time" in df.columns:
                try:
                    # Use ISO8601 format with error coercion for tolerant parsing
                    df["entry_time"] = pd.to_datetime(df["entry_time"], format='ISO8601', errors='coerce', utc=True)
                    # Remove rows with invalid dates (NaT)
                    invalid_dates = df["entry_time"].isna().sum()
                    if invalid_dates > 0:
                        print(f"[WARN] Removed {invalid_dates} rows with invalid entry_time in {path}")
                        df = df.dropna(subset=["entry_time"])
                except Exception as e:
                    print(f"[WARN] Error parsing entry_time in {path}: {e}")
            
            if "exit_time" in df.columns:
                try:
                    # Use ISO8601 format with error coercion for tolerant parsing
                    df["exit_time"] = pd.to_datetime(df["exit_time"], format='ISO8601', errors='coerce', utc=True)
                    # Don't remove rows with invalid exit_time (might be active trades)
                except Exception as e:
                    print(f"[WARN] Error parsing exit_time in {path}: {e}")
            
            # Freshness validation via sidecar
            is_stale = False
            last_until = None
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
                        max_entry = df["entry_time"].max()
                        if pd.notna(max_entry):
                            max_entry_date = max_entry.date().isoformat()
                            # Accept if max_entry_date <= today (not future) and sidecar covers today
                            if max_entry_date > today_date:
                                print(f"[WARN] Future entry date ignored: {path} (max_entry={max_entry_date})")
                                continue
                        # If no valid entry_time or empty, but sidecar covers today, accept empty file
                    # If no entry_time column but sidecar is fresh, accept the file
                else:
                    # Sidecar doesn't cover current session, mark as stale but preserve data
                    is_stale = True
                    print(f"[WARN] Stale sidecar detected: {path} (last_until={last_until}, today={today_date}) - preserving data")
            except Exception as e:
                print(f"[WARN] Freshness validation failed for {path}: {e}")
                continue
            
            # Mark DataFrame as stale if needed
            if is_stale and last_until is not None:
                df.attrs["stale_last_until"] = last_until
            print(f"[OK] Loaded trades from: {path} ({len(df)} rows)")
            # Times are already normalized above with tolerant parsing 
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
            print(f"[ERROR] Failed to load {path}: {e}")
            continue
    print(f"[ERROR] No valid trades found for {symbol} {mode}")
    return pd.DataFrame()


def invert_trade(trade: dict) -> dict:
    """
    Invert a single trade by flipping direction and PnL.
    
    Args:
        trade: Dictionary containing trade data
        
    Returns:
        Dictionary with inverted trade data
    """
    inverted = trade.copy()
    
    # Invert side
    if "side" in inverted:
        if inverted["side"].lower() == "long":
            inverted["side"] = "short"
        elif inverted["side"].lower() == "short":
            inverted["side"] = "long"
    
    # Invert PnL
    if "pnl_usdt" in inverted and inverted["pnl_usdt"] is not None:
        inverted["pnl_usdt"] = -inverted["pnl_usdt"]
    
    # Invert R-multiple
    if "r_multiple" in inverted and inverted["r_multiple"] is not None:
        inverted["r_multiple"] = -inverted["r_multiple"]
    
    # Invert exit reason if applicable
    if "exit_reason" in inverted:
        if inverted["exit_reason"] == "take_profit":
            inverted["exit_reason"] = "stop_loss"
        elif inverted["exit_reason"] == "stop_loss":
            inverted["exit_reason"] = "take_profit"
    
    return inverted


def invert_trades_dataframe(trades: pd.DataFrame) -> pd.DataFrame:
    """
    Invert all trades in a DataFrame.
    
    Args:
        trades: DataFrame containing trade data
        
    Returns:
        DataFrame with all trades inverted
    """
    if trades.empty:
        return trades.copy()
    
    df = trades.copy()
    
    # Invert side
    if "side" in df.columns:
        df["side"] = df["side"].apply(lambda x: "short" if x.lower() == "long" else "long" if x.lower() == "short" else x)
    
    # Invert PnL
    if "pnl_usdt" in df.columns:
        df["pnl_usdt"] = -df["pnl_usdt"]
    
    # Invert R-multiple
    if "r_multiple" in df.columns:
        df["r_multiple"] = -df["r_multiple"]
    
    # Invert exit reason
    if "exit_reason" in df.columns:
        df["exit_reason"] = df["exit_reason"].apply(
            lambda x: "stop_loss" if x == "take_profit" else "take_profit" if x == "stop_loss" else x
        )
    
    return df


def invert_metrics(metrics: dict) -> dict:
    """
    [DEPRECATED] This function is no longer needed.
    Use compute_metrics_pure(..., invertido=True) instead.
    
    Kept for backwards compatibility with existing tests.
    When invertido=True is used in compute_metrics_pure, metrics are
    calculated correctly from inverted trades with standard interpretation.
    
    This function implements the OLD behavior for legacy tests only.
    """
    inverted = metrics.copy()
    
    # OLD BEHAVIOR - DEPRECATED
    # This transformation is no longer recommended as it changes metric interpretation
    # Instead, compute_metrics_pure with invertido=True should be used
    
    # Invert PnL-related metrics
    if "total_pnl" in inverted:
        inverted["total_pnl"] = -inverted["total_pnl"]
    
    if "current_capital" in inverted and "initial_capital" in inverted:
        inverted["current_capital"] = inverted["initial_capital"] + inverted["total_pnl"]
    
    if "roi" in inverted:
        inverted["roi"] = -inverted["roi"]
    
    if "max_drawdown" in inverted:
        inverted["max_drawdown"] = -inverted["max_drawdown"]
    
    if "win_rate" in inverted:
        inverted["win_rate"] = 100.0 - inverted["win_rate"]
    
    return inverted


def compute_metrics_pure(trades: pd.DataFrame, initial_capital: float = 1000.0, leverage: float = 1.0, invertido: bool = False) -> dict:
    """
    Calcula métricas de performance de manera pura, con soporte para inversión.
    
    Args:
        trades: DataFrame con datos de trades
        initial_capital: Capital inicial
        leverage: Apalancamiento
        invertido: Si True, calcula métricas como si la estrategia estuviera invertida
        
    Returns:
        Dict con métricas calculadas
    """
    if trades.empty:
        return {
            "total_trades": 0, "win_rate": 0.0, "total_pnl": 0.0, "max_drawdown": 0.0, 
            "avg_risk_per_trade": 0.0, "dd_in_r": 0.0, "initial_capital": initial_capital,
            "current_capital": initial_capital, "roi": 0.0, "leverage": leverage,
            "profit_factor": 0.0, "expectancy": 0.0, "avg_pnl": 0.0, "best_trade": 0.0, "worst_trade": 0.0
        }
    
    df = trades.copy()
    if "entry_time" in df.columns:
        df["entry_time"] = pd.to_datetime(df["entry_time"])
        df = df.sort_values(by="entry_time", ascending=True)
    
    # Aplicar inversión si está habilitada
    if invertido:
        df = invert_trades_dataframe(df)
    
    # Calcular métricas básicas
    df["cumulative_pnl"] = df["pnl_usdt"].cumsum()
    df["running_max"] = df["cumulative_pnl"].cummax()
    df["drawdown"] = df["cumulative_pnl"] - df["running_max"]
    
    total_trades = len(df)
    wins = (df["pnl_usdt"] > 0).sum()
    losses = (df["pnl_usdt"] < 0).sum()
    win_rate = (wins / total_trades) * 100 if total_trades else 0.0
    
    # Métricas monetarias
    total_pnl = float(df["pnl_usdt"].sum())
    avg_pnl = float(df["pnl_usdt"].mean()) if total_trades else 0.0
    best_trade = float(df["pnl_usdt"].max()) if total_trades else 0.0
    worst_trade = float(df["pnl_usdt"].min()) if total_trades else 0.0
    max_drawdown = float(df["drawdown"].min()) if not df["drawdown"].empty else 0.0
    
    # Profit factor
    gross_profit = float(df[df["pnl_usdt"] > 0]["pnl_usdt"].sum()) if wins > 0 else 0.0
    gross_loss = abs(float(df[df["pnl_usdt"] < 0]["pnl_usdt"].sum())) if losses > 0 else 0.0
    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float('inf')  # No losses, only profits
    else:
        profit_factor = 0.0  # No profits, no losses
    
    # Expectancy
    expectancy = avg_pnl  # En este contexto, expectancy = promedio de PnL
    
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
        "total_trades": total_trades, 
        "win_rate": win_rate, 
        "total_pnl": total_pnl, 
        "avg_pnl": avg_pnl,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "max_drawdown": max_drawdown, 
        "avg_risk_per_trade": avg_risk, 
        "dd_in_r": dd_in_r,
        "initial_capital": initial_capital, 
        "current_capital": current_capital, 
        "roi": roi, 
        "leverage": leverage,
        "profit_factor": profit_factor,
        "expectancy": expectancy
    }


def compute_metrics(trades: pd.DataFrame, initial_capital: float = 1000.0, leverage: float = 1.0) -> dict:
    """
    Wrapper para mantener compatibilidad con código existente.
    """
    return compute_metrics_pure(trades, initial_capital, leverage, invertido=False)


def figure_equity_curve(trades: pd.DataFrame):
    if trades.empty:
        return go.Figure()
    df = trades.copy()
    if "entry_time" in df.columns:
        df["entry_time"] = pd.to_datetime(df["entry_time"])  # ensure
        df = df.sort_values(by="entry_time", ascending=True)
        # Convert to Argentina timezone for display
        df["entry_time"] = df["entry_time"].apply(lambda x: to_argentina_time(x))
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
        # Convert to Argentina timezone for display
        df["entry_time"] = df["entry_time"].apply(lambda x: to_argentina_time(x))
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
    # Convert entry_time to Argentina timezone for display
    if "entry_time" in df.columns:
        df["entry_time"] = df["entry_time"].apply(lambda x: to_argentina_time(x))
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
    # Convert to Argentina timezone for monthly grouping
    df["entry_time"] = df["entry_time"].apply(lambda x: to_argentina_time(x))
    # Convert to naive datetime to avoid timezone issues with to_period
    df["entry_time"] = df["entry_time"].dt.tz_localize(None)
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


def figure_trades_on_price(trades: pd.DataFrame, symbol: str, timeframe: str = "1h", today_recommendation: dict = None, mode: str = "moderate"):
    if fetch_historical_data is None:
        logger.warning("fetch_historical_data function not available. Check API configuration or ccxt installation.")
        # Return empty figure with explanatory message
        fig = go.Figure()
        fig.add_annotation(
            text="Historical data not available<br>Configure API credentials to load price charts",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        return fig
    
    try:
        since_date = None
        if not trades.empty:
            df = trades.copy()
            df["entry_time"] = pd.to_datetime(df["entry_time"])
            since_date = df["entry_time"].min().date().isoformat()
        start_date_dt, end_date_dt = determine_price_date_range(symbol, since_date, lookback_days=365)
        start_date = start_date_dt.date().isoformat()
        end_date = end_date_dt.date().isoformat()
        
        logger.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}")
        price = fetch_historical_data(symbol, start_date, end_date, timeframe)
        
        if price is None or price.empty:
            logger.warning(f"No data returned for {symbol}, trying alternative symbol format")
            alt_symbol = symbol.replace(":USDT", "") if ":USDT" in symbol else symbol
            price = fetch_historical_data(alt_symbol, start_date, end_date, timeframe)
        
        if price is None or price.empty:
            logger.error(f"Could not fetch historical data for {symbol} or {alt_symbol}")
            # Try to load from cached CSV if available
            cached_file = base_dir.parent / "data" / f"{symbol.replace('/', '_').replace(':', '_')}_historical.csv"
            if cached_file.exists():
                logger.info(f"Loading cached data from {cached_file}")
                price = pd.read_csv(cached_file, parse_dates=['time'])
            else:
                logger.error(f"No cached data available at {cached_file}")
                # Return empty figure with message
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No historical data available for {symbol}<br>Run backtest first to cache data",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14, color="red")
                )
                return fig
        price = price.copy()
        price = price.reset_index().rename(columns={"timestamp": "time"}) if "timestamp" in price.columns else price.reset_index(names=["time"]) 
        fig = px.line(price, x="time", y="close", title=f"{symbol} Price with Trades (365+ days)")
        
        # Add horizontal lines for today's recommendation levels
        if today_recommendation:
            entry_price = today_recommendation.get('entry_price')
            stop_loss = today_recommendation.get('stop_loss')
            take_profit = today_recommendation.get('take_profit')
            side = today_recommendation.get('side', '').lower()
            
            # Determine colors based on side
            entry_color = "blue"
            sl_color = "red"
            tp_color = "green"
            
            if entry_price:
                fig.add_hline(y=entry_price, line_dash="dot", line_color=entry_color, line_width=2, annotation_text=f"Entry: ${entry_price:,.2f}", annotation_position="right")
            if stop_loss:
                fig.add_hline(y=stop_loss, line_dash="dot", line_color=sl_color, line_width=2, annotation_text=f"SL: ${stop_loss:,.2f}", annotation_position="right")
            if take_profit:
                fig.add_hline(y=take_profit, line_dash="dot", line_color=tp_color, line_width=2, annotation_text=f"TP: ${take_profit:,.2f}", annotation_position="right")
        
        # entries separated by side
        if "side" in df.columns:
            longs = df[df["side"].str.lower() == "long"]
            shorts = df[df["side"].str.lower() == "short"]
        else:
            longs = df.iloc[0:0]
            shorts = df.iloc[0:0]

        if not longs.empty:
            # Convert entry times to Argentina timezone
            longs_entry_times = longs["entry_time"].apply(lambda x: to_argentina_time(x))
            fig.add_trace(go.Scatter(x=longs_entry_times, y=longs["entry_price"], mode="markers", name="Entry Long", marker=dict(color="green", symbol="triangle-up", size=9)))
        if not shorts.empty:
            # Convert entry times to Argentina timezone
            shorts_entry_times = shorts["entry_time"].apply(lambda x: to_argentina_time(x))
            fig.add_trace(go.Scatter(x=shorts_entry_times, y=shorts["entry_price"], mode="markers", name="Entry Short", marker=dict(color="red", symbol="triangle-down", size=9)))

        # exits separated by side
        if "exit_time" in df.columns and "exit_price" in df.columns:
            if not longs.empty:
                # Convert exit times to Argentina timezone
                longs_exit_times = longs["exit_time"].apply(lambda x: to_argentina_time(x))
                fig.add_trace(go.Scatter(x=longs_exit_times, y=longs["exit_price"], mode="markers", name="Exit Long", marker=dict(color="green", symbol="x", size=9)))
            if not shorts.empty:
                # Convert exit times to Argentina timezone
                shorts_exit_times = shorts["exit_time"].apply(lambda x: to_argentina_time(x))
                fig.add_trace(go.Scatter(x=shorts_exit_times, y=shorts["exit_price"], mode="markers", name="Exit Short", marker=dict(color="red", symbol="x", size=9)))
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
                dbc.Col(dbc.Select(id="symbol-dropdown", options=[{"label": s, "value": s} for s in DEFAULT_SYMBOLS], value="ETH/USDT:USDT" , className="me-2"), md="auto"),
                dbc.Col(dbc.RadioItems(id="investment-mode", options=[{"label": "Conservador", "value": "conservative"}, {"label": "Moderado", "value": "moderate"}, {"label": "Arriesgado", "value": "aggressive"}], value="moderate", inline=True, className="me-3", labelClassName="text-white"), md="auto"),
                dbc.Col([
                    dbc.Switch(
                        id="invert-strategy-switch",
                        label="Invertir Estrategia",
                        value=False,
                        className="me-2"
                    ),
                    html.Small("Mostrar datos invertidos", className="text-white-50 d-block")
                ], md="auto", className="me-3"),
                dbc.Col(dbc.Button("Refrescar", id="refresh", color="primary", className="text-white"), md="auto"),
            ], align="center", className="g-2"), id="navbar-collapse", is_open=True)
        ]), color="dark", dark=True, className="mb-3"
    )

    app.layout = dbc.Container([
        navbar,
        
        # Store for inversion state
        dcc.Store(id="inversion-state", data={"inverted": False}),
        
        # Hero Section - Daily Price Dashboard
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    # Main Price Display
                    dbc.Col([
                        html.Div([
                            html.Small(id="hero-symbol", className="text-muted mb-1"),
                            html.H1(id="hero-price", className="display-3 fw-bold text-primary mb-0"),
                            html.Div([
                                html.Span(id="hero-change", className="fs-5 me-2"),
                                html.Span(id="hero-change-pct", className="fs-5")
                            ], className="d-flex align-items-center mt-1")
                        ])
                    ], md=4, sm=12, className="text-center text-md-start mb-3 mb-md-0"),
                    
                    # Trading Session Info
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Ventana de Entrada", className="text-muted mb-2"),
                                html.H5(id="hero-entry-window", className="mb-0"),
                                html.Small(id="hero-session-status", className="text-muted")
                            ], className="py-2")
                        ], className="h-100", color="light")
                    ], md=3, sm=6, xs=12, className="mb-3 mb-md-0"),
                    
                    # Risk & Mode Info
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Riesgo por Trade", className="text-muted mb-2"),
                                html.H5(id="hero-risk", className="mb-0"),
                                html.Small(id="hero-mode", className="text-muted")
                            ], className="py-2")
                        ], className="h-100", color="light")
                    ], md=3, sm=6, xs=12, className="mb-3 mb-md-0"),
                    
                    # Active Trade Indicator
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Estado", className="text-muted mb-2"),
                                html.H5(id="hero-active-trade", className="mb-0"),
                                dbc.Badge(id="hero-inversion-badge", children="INVERTIDA", color="warning", className="mt-1", style={"display": "none"})
                            ], className="py-2")
                        ], className="h-100", color="light")
                    ], md=2, sm=12, xs=12)
                ], className="g-3")
            ], className="py-3")
        ], className="mb-4 shadow-sm"),

        # Alert Section
        dbc.Alert(id="alert", is_open=False, color="warning", className="mb-4"),

        # Today's Recommendation - Compact Display
        dbc.Card([
            dbc.CardHeader([
                html.I(className="bi bi-lightbulb-fill me-2"),
                html.Span("Recomendación de Hoy")
            ]),
            dbc.CardBody(id="today-reco"),
        ], className="mb-4"),
        
        # Annual Candle Analysis Tasks - Collapsible
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.Button([
                        html.I(className="bi bi-bar-chart-line me-2"),
                        html.Span("Tareas de Análisis Anual", id="candle-tasks-header")
                    ], className="btn btn-link text-decoration-none text-dark p-0", id="candle-tasks-collapse-button"),
                    dbc.Badge("365+ días", color="info", className="ms-2")
                ], className="d-flex align-items-center")
            ]),
            dbc.Collapse([
                dbc.CardBody([
                    html.P("Revise estas tareas para validar la estrategia con al menos un año de datos históricos:", className="text-muted mb-3"),
                    html.Div(id="candle-analysis-tasks")
                ])
            ], id="candle-tasks-collapse", is_open=False)
        ], className="mb-4", id="candle-tasks-panel"),
        
        # Strategy Description Panel - Collapsible
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.Button([
                        html.I(className="bi bi-info-circle me-2"),
                        html.Span("Estrategia Actual", id="strategy-header")
                    ], className="btn btn-link text-decoration-none text-dark p-0", id="strategy-collapse-button"),
                    dbc.Badge("INVERTIDA", color="warning", className="ms-2", id="inversion-badge", style={"display": "none"})
                ], className="d-flex align-items-center")
            ]),
            dbc.Collapse([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Descripción:", className="fw-bold"),
                            html.P(id="strategy-description"),
                            html.H6("Herramientas:", className="fw-bold mt-3"),
                            html.Ul(id="strategy-tools"),
                        ], md=6),
                        dbc.Col([
                            html.H6("Reglas:", className="fw-bold"),
                            html.Ul(id="strategy-rules"),
                            html.H6("Perfil de Riesgo:", className="fw-bold mt-3"),
                            html.P(id="strategy-risk-profile", className="text-muted"),
                        ], md=6),
                    ])
                ])
            ], id="strategy-collapse", is_open=False)
        ], className="mb-4", id="strategy-panel"),

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
        Output("inversion-state", "data"),
        Input("invert-strategy-switch", "value"),
    )
    def update_inversion_state(invert_switch):
        """Update inversion state when switch is toggled."""
        return {"inverted": invert_switch}
    
    @app.callback(
        Output("strategy-collapse", "is_open"),
        Input("strategy-collapse-button", "n_clicks"),
        State("strategy-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_strategy_collapse(n_clicks, is_open):
        """Toggle strategy panel collapse."""
        if n_clicks:
            return not is_open
        return is_open
    
    @app.callback(
        Output("candle-tasks-collapse", "is_open"),
        Input("candle-tasks-collapse-button", "n_clicks"),
        State("candle-tasks-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_candle_tasks_collapse(n_clicks, is_open):
        """Toggle candle analysis tasks panel collapse."""
        if n_clicks:
            return not is_open
        return is_open
    
    @app.callback(
        Output("candle-analysis-tasks", "children"),
        Input("investment-mode", "value"),
        Input("inversion-state", "data"),
    )
    def update_candle_analysis_tasks(mode, inversion_state):
        """Update candle analysis tasks based on mode and inversion state."""
        if not mode:
            mode = "moderate"
        is_inverted = inversion_state.get("inverted", False) if inversion_state else False
        tasks = build_candle_analysis_tasks(mode, is_inverted)
        priority_colors = {1: "danger", 2: "warning", 3: "info"}
        task_elements = []
        for task in tasks:
            task_card = dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H6([
                            task["title"],
                            dbc.Badge(f"P{task['priority']}", color=priority_colors.get(task["priority"], "secondary"), className="ms-2", pill=True)
                        ], className="mb-2"),
                        html.P(task["description"], className="text-muted mb-0 small")
                    ])
                ])
            ], className="mb-2", color="light")
            task_elements.append(task_card)
        return task_elements

    @app.callback(
        Output("symbol-dropdown", "options"),
        Output("symbol-dropdown", "value"),
        Output("strategy-header", "children"),
        Output("strategy-description", "children"),
        Output("strategy-tools", "children"),
        Output("strategy-rules", "children"),
        Output("strategy-risk-profile", "children"),
        Output("inversion-badge", "style"),
        Input("investment-mode", "value"),
        Input("inversion-state", "data"),
    )
    def update_strategy_panel(mode, inversion_state):
        """Update strategy panel and symbol dropdown based on selected mode."""
        if not mode:
            mode = "moderate"
        
        # Extract inversion state
        is_inverted = inversion_state.get("inverted", False) if inversion_state else False
        
        # Get symbols for the mode
        symbols = get_symbols_for_mode(mode)
        symbol_options = [{"label": s, "value": s} for s in symbols]
        # Prefer ETH/USDT:USDT if available (has historical data), otherwise first symbol
        default_symbol = "ETH/USDT:USDT" if "ETH/USDT:USDT" in symbols else (symbols[0] if symbols else "ETH/USDT:USDT")
        
        # Get strategy description
        strategy_info = STRATEGY_DESCRIPTIONS.get(mode, STRATEGY_DESCRIPTIONS["moderate"])
        
        # Create tools list
        tools_list = [html.Li(tool) for tool in strategy_info["tools"]]
        
        # Create rules list
        rules_list = [html.Li(rule) for rule in strategy_info["rules"]]
        
        # Show/hide inversion badge
        badge_style = {"display": "block"} if is_inverted else {"display": "none"}
        
        return (
            symbol_options,
            default_symbol,
            f"Estrategia: {strategy_info['name']} ({mode.title()})",
            strategy_info["description"],
            tools_list,
            rules_list,
            strategy_info["risk_profile"],
            badge_style
        )

    @app.callback(
        Output("hero-symbol", "children"),
        Output("hero-price", "children"),
        Output("hero-change", "children"),
        Output("hero-change", "className"),
        Output("hero-change-pct", "children"),
        Output("hero-entry-window", "children"),
        Output("hero-session-status", "children"),
        Output("hero-risk", "children"),
        Output("hero-mode", "children"),
        Output("hero-active-trade", "children"),
        Output("hero-inversion-badge", "style"),
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
        Output("alert", "color"),
        Input("symbol-dropdown", "value"),
        Input("refresh", "n_clicks"),
        Input("investment-mode", "value"),
        Input("inversion-state", "data"),
        prevent_initial_call=False,
    )
    def update_dashboard(symbol, n_clicks, mode, inversion_state):
        symbol = (symbol or "BTC/USDT:USDT").strip()
        
        # Extract inversion state
        is_inverted = inversion_state.get("inverted", False) if inversion_state else False
        
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
            refresh_msg = refresh_trades(symbol, mode or "moderate")
        except Exception as e:
            refresh_msg = f"Error refreshing trades: {str(e)}"
        
        # Load updated trades
        trades = load_trades(symbol, mode or "moderate")
        
        # Note: Inversion is now handled in compute_metrics_pure with invertido flag
        # No need to invert trades here to avoid double inversion
        
        # Load active trade if any to reflect in UI
        active_trade = None
        try:
            from btc_1tpd_backtester.live_monitor import load_active_trade
            active_trade = load_active_trade()
            # Apply inversion to active trade if enabled
            if is_inverted and active_trade is not None:
                active_trade_dict = {
                    "side": active_trade.side,
                    "entry_price": active_trade.entry_price,
                    "stop_loss": active_trade.stop_loss,
                    "take_profit": active_trade.take_profit,
                    "entry_time": active_trade.entry_time
                }
                inverted_active = invert_trade(active_trade_dict)
                # Update active_trade object with inverted values
                active_trade.side = inverted_active["side"]
                active_trade.entry_price = inverted_active["entry_price"]
                active_trade.stop_loss = inverted_active["stop_loss"]
                active_trade.take_profit = inverted_active["take_profit"]
        except Exception:
            active_trade = None
        alert_msg = ""
        
        # Check for stale data in the loaded trades and read meta file
        stale_last_until = None
        last_error_info = None
        last_update_attempt = None
        
        if hasattr(trades, 'attrs') and "stale_last_until" in trades.attrs:
            stale_last_until = trades.attrs["stale_last_until"]
        
        # Read sidecar for last_backtest_until and error info
        try:
            slug = symbol.replace('/', '_').replace(':', '_')
            mode_suffix = (mode or "moderate").lower()
            meta_path = (repo_root / "data" / f"trades_final_{slug}_{mode_suffix}").with_suffix("")
            meta_path = Path(str(meta_path) + "_meta.json")
            last_until = None
            if meta_path.exists():
                import json
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                last_until = meta.get("last_backtest_until")
                last_error_info = meta.get("last_error")
                last_update_attempt = meta.get("last_update_attempt")
                
                # If no stale attribute from load_trades, check freshness here
                if stale_last_until is None and last_until:
                    today_iso = datetime.now(timezone.utc).date().isoformat()
                    if last_until < today_iso:
                        stale_last_until = last_until
        except Exception:
            last_until = None
            last_error_info = None
            last_update_attempt = None
        
        # Construct detailed alert message based on stale data and errors
        if stale_last_until is not None:
            alert_msg = f"[WARN] Datos actualizados hasta {format_argentina_time(datetime.fromisoformat(stale_last_until), '%Y-%m-%d')}. "
            
            if last_error_info:
                error_type = last_error_info.get('type')
                error_detail = last_error_info.get('detail', 'Unknown error')
                
                if error_type == 'network':
                    alert_msg += f"Último error: Problema de conexión ({error_detail[:100]}). Verifica tu conexión a internet y presiona 'Refrescar'."
                else:
                    alert_msg += f"Último error: {error_detail[:150]}. Presiona 'Refrescar' para reintentar."
            else:
                alert_msg += "Presiona 'Refrescar' para actualizar los datos."
        mode_display = {"conservative": "Conservador", "moderate": "Moderado", "aggressive": "Agresivo"}.get((mode or "moderate").lower(), (mode or "moderate").capitalize())
        
        # Handle different alert scenarios
        if stale_last_until is not None:
            # Stale data warning takes precedence
            pass  # alert_msg already set above
        elif trades.empty and active_trade is None:
            # If last_backtest_until is today, clarify there were no trades
            today_iso = datetime.now(timezone.utc).date().isoformat()
            if last_until == today_iso:
                alert_msg = f"Actualizado al {format_argentina_time(datetime.now(timezone.utc), '%Y-%m-%d')}. No hubo operaciones en la sesión."
            else:
                alert_msg = f"No hay datos para {symbol} en modo {mode_display}. {refresh_msg}"
        elif refresh_msg and "Error" in refresh_msg:
            alert_msg = f"Error en modo {mode_display}: {refresh_msg}"
        elif active_trade is not None:
            alert_msg = f"Operación activa: {active_trade.side.upper()} a {active_trade.entry_price} (SL {active_trade.stop_loss}, TP {active_trade.take_profit})."

        # Get effective configuration
        config = get_effective_config(symbol, mode or "moderate")
        
        # Use pure metrics calculation with inversion flag
        m = compute_metrics_pure(trades, config.get('initial_capital', 1000.0), config.get('leverage', 1.0), invertido=is_inverted)
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

        # Colors use standard interpretation in both modes
        # Since metrics are calculated consistently, color logic is the same
        win_color = "success" if m['win_rate'] >= 50 else "warning" if m['win_rate'] > 0 else "secondary"
        pnl_color = "success" if m['total_pnl'] >= 0 else "danger"
        dd_color = "danger" if m['max_drawdown'] < 0 else "secondary"
        roi_color = "success" if m['roi'] >= 0 else "danger"

        # Labels remain standard in both normal and inverted modes
        # Metrics maintain their standard interpretation
        win_rate_label = "Win rate"
        win_rate_tooltip = "Porcentaje de operaciones ganadoras (calculado sobre trades invertidos si el modo está activo)" if is_inverted else "Porcentaje de operaciones ganadoras vs perdedoras"
        dd_label = "Max DD"
        dd_tooltip = "Máxima pérdida desde un pico de capital (calculada sobre trades invertidos si el modo está activo, siempre negativa)" if is_inverted else "Máxima pérdida desde un pico de capital (en USDT y múltiplos de riesgo)"
        pf_label = "Profit Factor"
        pf_tooltip = "Ratio entre ganancias brutas y pérdidas brutas (calculado sobre trades invertidos si el modo está activo)" if is_inverted else "Ratio entre ganancias brutas y pérdidas brutas"
        
        metrics_children = dbc.Row([
            kpi_card("Total trades", f"{m['total_trades']}", "primary", "bi-collection", 
                    "Número total de operaciones ejecutadas", "tooltip-trades"),
            kpi_card(win_rate_label, f"{m['win_rate']:.1f}%", win_color, "bi-bullseye", 
                    win_rate_tooltip, "tooltip-winrate"),
            kpi_card("PnL", f"{m['total_pnl']:+,.2f} USDT", pnl_color, "bi-cash-stack", 
                    "Ganancia o pérdida total en USDT", "tooltip-pnl"),
            kpi_card(dd_label, f"{m['max_drawdown']:.2f} USDT ({m['dd_in_r']:.2f} R)", dd_color, "bi-graph-down", 
                    dd_tooltip, "tooltip-dd"),
            kpi_card(pf_label, f"{m['profit_factor']:.2f}", "info", "bi-calculator", 
                    pf_tooltip, "tooltip-pf"),
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

        # Today recommendation via live monitor
        reco_children = html.Div("Se requiere módulo de señales.")
        strategy_signal = None
        today_recommendation = None
        try:
            from btc_1tpd_backtester.live_monitor import detect_or_update_active_trade
            merged_cfg = get_effective_config(symbol, mode)
            active_or_rec = detect_or_update_active_trade(symbol, mode, merged_cfg)
            # Build card from active_or_rec when we have params
            if active_or_rec is not None:
                side = getattr(active_or_rec, 'side', None) or (active_or_rec.get('side') if isinstance(active_or_rec, dict) else None)
                entry_price = getattr(active_or_rec, 'entry_price', None) or (active_or_rec.get('entry_price') if isinstance(active_or_rec, dict) else None)
                stop_loss = getattr(active_or_rec, 'stop_loss', None) or (active_or_rec.get('stop_loss') if isinstance(active_or_rec, dict) else None)
                take_profit = getattr(active_or_rec, 'take_profit', None) or (active_or_rec.get('take_profit') if isinstance(active_or_rec, dict) else None)
                entry_time_val = getattr(active_or_rec, 'entry_time', None) or (active_or_rec.get('entry_time') if isinstance(active_or_rec, dict) else None)
                
                # Store original signal for validation
                strategy_signal = side
                
                # Build today_recommendation dictionary for price chart levels
                today_recommendation = {
                    'side': side,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'entry_time': entry_time_val
                }
                
                # Apply inversion to display if enabled
                display_side = side
                if is_inverted and side:
                    display_side = "short" if side.lower() == "long" else "long"
                
                badge_color = "secondary" if not display_side else ("success" if display_side == "long" else "danger")
                reco_children = html.Div([
                    html.Div([html.B("Símbolo: "), html.Span(symbol)]),
                    html.Div([html.B("Dirección: "), dbc.Badge((display_side or "-").lower(), color=badge_color, className="ms-1")]),
                    html.Div([html.B("Hora entrada: "), format_argentina_time(entry_time_val, "%H:%M:%S %Z") if entry_time_val else "-"]),
                    html.Div([html.B("Entrada: "), f"{entry_price if entry_price is not None else '-'}"]),
                    html.Div([html.B("SL: "), f"{stop_loss if stop_loss is not None else '-'}"]),
                    html.Div([html.B("TP: "), f"{take_profit if take_profit is not None else '-'}"]),
                ])
        except Exception:
            pass
        
        # Validate daily trade vs strategy signal
        validation_alert = ""
        if strategy_signal and not trades.empty and "side" in trades.columns:
            # Get the most recent trade
            recent_trade = trades.iloc[0] if len(trades) > 0 else None
            if recent_trade is not None:
                recent_side = recent_trade.get("side")
                if recent_side:
                    # Compare original signals (not inverted for display)
                    if strategy_signal.lower() != recent_side.lower():
                        validation_alert = f"[WARN] Inconsistencia detectada: Señal de estrategia ({strategy_signal.upper()}) no coincide con trade más reciente ({recent_side.upper()})"
        
        # Update alert message to include validation
        if validation_alert:
            if alert_msg:
                alert_msg = f"{alert_msg} | {validation_alert}"
            else:
                alert_msg = validation_alert
        
        # Determine alert color based on content and error type
        alert_color = "warning"
        if last_error_info and last_error_info.get('type') == 'network':
            alert_color = "danger"  # Network errors are critical
        elif "Error" in alert_msg or "Inconsistencia" in alert_msg:
            alert_color = "danger"
        elif "Operación activa" in alert_msg:
            alert_color = "info"
        elif "Actualizado" in alert_msg and "No hubo" not in alert_msg and stale_last_until is None:
            alert_color = "success"

        # Hero Section - Price and Symbol
        hero_symbol_text = f"{symbol.split('/')[0]} / {symbol.split('/')[1]}" if '/' in symbol else symbol
        hero_price_text = f"${price_info['price']:,.2f}" if price_info and price_info.get('price') else "---"
        
        # Calculate price change (comparing with yesterday's close if available)
        hero_change_text = ""
        hero_change_class = "fs-5 me-2"
        hero_change_pct_text = ""
        if price_info and price_info.get('price') and not trades.empty:
            try:
                # Get yesterday's last trade price for comparison
                yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()
                yesterday_trades = trades[pd.to_datetime(trades['entry_time']).dt.date == yesterday]
                if not yesterday_trades.empty:
                    last_price = yesterday_trades.iloc[0]['exit_price']
                    change = price_info['price'] - last_price
                    change_pct = (change / last_price) * 100
                    hero_change_text = f"{change:+,.2f}"
                    hero_change_pct_text = f"({change_pct:+.2f}%)"
                    hero_change_class = f"fs-5 me-2 {'text-success' if change >= 0 else 'text-danger'}"
            except Exception:
                pass
        
        # Hero Section - Trading Window
        config = get_effective_config(symbol, mode or "moderate")
        entry_window = config.get('entry_window', (11, 14))
        exit_window = config.get('exit_window', (20, 22))
        hero_entry_window_text = f"{entry_window[0]:02d}:00 - {entry_window[1]:02d}:00"
        
        # Check if currently in trading window
        now_ar = datetime.now(ARGENTINA_TZ)
        current_hour = now_ar.hour
        in_entry_window = entry_window[0] <= current_hour < entry_window[1]
        in_exit_window = exit_window[0] <= current_hour < exit_window[1]
        
        if in_entry_window:
            hero_session_status_text = "[PASS] Ventana de entrada activa"
        elif in_exit_window:
            hero_session_status_text = "[FAIL] Ventana de salida activa"
        else:
            hero_session_status_text = "[PAUSE] Fuera de ventana"
        
        # Hero Section - Risk and Mode
        risk_usdt = config.get('risk_usdt', 20.0)
        hero_risk_text = f"${risk_usdt:.2f} USDT"
        mode_display = {"conservative": "Conservador", "moderate": "Moderado", "aggressive": "Agresivo"}.get((mode or "moderate").lower(), mode.capitalize())
        hero_mode_text = f"Modo {mode_display}"
        
        # Hero Section - Active Trade Status
        if active_trade is not None:
            hero_active_trade_text = "Trade Activo"
        else:
            hero_active_trade_text = "Sin Trade"
        
        # Hero Section - Inversion Badge
        hero_inversion_badge_style = {"display": "inline-block"} if is_inverted else {"display": "none"}

        # Prepare trades for display
        # Apply inversion for display if enabled
        trades_display = trades.copy() if not trades.empty else trades
        if is_inverted and not trades_display.empty:
            trades_display = invert_trades_dataframe(trades_display)
        
        # Prepare figures with inverted trades for display
        eq = figure_equity_curve(trades_display)
        pnl = figure_pnl_distribution(trades_display)
        dd = figure_drawdown(trades_display)
        tl = figure_trade_timeline(trades_display)
        mon = figure_monthly_performance(trades_display)
        wl = figure_win_loss(trades_display)
        price_fig = figure_trades_on_price(trades_display, symbol, timeframe="1h", today_recommendation=today_recommendation, mode=mode or "moderate")
        
        # Prepare table data
        table_data = []
        if not trades_display.empty:
            tbl = trades_display.copy()
            # Ordering recent first
            if "entry_time" in tbl.columns:
                tbl = tbl.sort_values(by="entry_time", ascending=False)
            # Convert datetimes to Argentina timezone for DataTable
            for col in ["entry_time", "exit_time"]:
                if col in tbl.columns:
                    # Convert to Argentina timezone and format
                    tbl[col] = pd.to_datetime(tbl[col]).apply(lambda x: format_argentina_time(x, "%Y-%m-%d %H:%M:%S"))
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
                    "entry_time": format_argentina_time(active_trade.entry_time, "%Y-%m-%d %H:%M:%S"),
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

        return (
            hero_symbol_text,
            hero_price_text,
            hero_change_text,
            hero_change_class,
            hero_change_pct_text,
            hero_entry_window_text,
            hero_session_status_text,
            hero_risk_text,
            hero_mode_text,
            hero_active_trade_text,
            hero_inversion_badge_style,
            reco_children,
            [capital_info, metrics_children],
            eq, pnl, dd, tl, mon, wl, price_fig,
            table_data,
            bool(alert_msg),
            alert_msg,
            alert_color
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8050, debug=True)


