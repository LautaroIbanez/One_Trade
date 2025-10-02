"""
Today's trading signal module for BTC 1 Trade Per Day strategy.
"""

from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple


def _find_breakout_in_entry_window(entry_data: pd.DataFrame, orb_high: float, orb_low: float) -> Tuple[Optional[str], Optional[datetime], Optional[float]]:
    """
    Find ORB breakouts in the entry window using strict comparisons.
    
    Args:
        entry_data: DataFrame with OHLC data for the entry window
        orb_high: ORB high level
        orb_low: ORB low level
    
    Returns:
        Tuple of (side, timestamp, entry_price) or (None, None, None) if no breakout
    """
    for timestamp, row in entry_data.iterrows():
        high_price = row['high']
        low_price = row['low']
        open_price = row['open']
        
        # Long breakout: high strictly greater than orb_high
        if high_price > orb_high:
            # Entry price reflects the breakout (max of open and orb_high)
            entry_price = max(open_price, orb_high)
            return 'long', timestamp, entry_price
        
        # Short breakout: low strictly less than orb_low
        elif low_price < orb_low:
            # Entry price reflects the breakout (min of open and orb_low)
            entry_price = min(open_price, orb_low)
            return 'short', timestamp, entry_price
    
    return None, None, None


def get_today_trade_recommendation(symbol: str, config: Dict[str, Any], now: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get today's trade recommendation based on ORB breakout strategy.
    
    Args:
        symbol: Trading symbol (e.g., "BTC/USDT:USDT")
        config: Configuration dictionary with trading parameters
        now: Current time (defaults to UTC now)
    
    Returns:
        Dictionary with trade recommendation details
    """
    if now is None:
        now = datetime.now(timezone.utc)
    
    # Default configuration
    default_config = {
        "risk_usdt": 20.0,
        "atr_mult_orb": 1.2,
        "tp_multiplier": 2.0,
        "adx_min": 15.0,
        "orb_window": (11, 12),
        "entry_window": (11, 13),
        "full_day_trading": False
    }
    
    # Merge with provided config
    config = {**default_config, **config}
    
    # Prepare cache path
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    cache_file = data_dir / "last_recommendation.json"
    
    # Try to fetch minimal context; if no data, serve cache
    try:
        # Lazy import to avoid circulars
        from btc_1tpd_backtester.utils import fetch_historical_data
    except Exception:
        fetch_historical_data = None
    
    # Helper: evaluate a single day ORB based on provided config
    def _evaluate_orb_single_day(day_df: pd.DataFrame, session_date: datetime.date, cfg: Dict[str, Any]) -> Dict[str, Any]:
        if day_df is None or day_df.empty or len(day_df) < 50:
            return {"status": "no_data"}
        # Determine ORB/entry windows
        orb_window = cfg.get("orb_window", (11, 12))
        entry_window = cfg.get("entry_window", (11, 13))
        full_day = cfg.get("full_day_trading", False)
        # ORB window
        orb_data = day_df[(day_df.index.hour >= orb_window[0]) & (day_df.index.hour < orb_window[1])]
        if orb_data.empty:
            return {"status": "awaiting_breakout", "orb_high": None, "orb_low": None}
        orb_high = float(orb_data['high'].max())
        orb_low = float(orb_data['low'].min())
        # Entry window
        if full_day:
            ew_start = max(orb_window[1], entry_window[0])
            ew_end = 24
            entry_win = (ew_start, ew_end)
        else:
            entry_win = entry_window
        ew_start, ew_end = entry_win
        entry_data = day_df[(day_df.index.hour >= ew_start) & (day_df.index.hour < ew_end)]
        if entry_data.empty:
            return {"status": "no_breakout", "orb_high": orb_high, "orb_low": orb_low}
        # Scan for strict breakout
        for ts, row in entry_data.iterrows():
            high_p = row['high']; low_p = row['low']; open_p = row['open']
            if high_p > orb_high:
                entry_price = max(open_p, orb_high)
                side = 'long'
            elif low_p < orb_low:
                entry_price = min(open_p, orb_low)
                side = 'short'
            else:
                continue
            # Found breakout
            rec = {
                "status": "signal",
                "symbol": symbol,
                "date": session_date.strftime("%Y-%m-%d"),
                "macro_bias": "neutral",
                "side": side,
                "entry_time": ts.isoformat(),
                "entry_price": float(entry_price),
                "orb_high": orb_high,
                "orb_low": orb_low,
                "notes": "ORB breakout detected",
                "from_cache": False
            }
            # Compute simple SL/TP using ATR-like multipliers if available candles
            try:
                # Use last 14 candles up to entry
                hist = day_df[day_df.index <= ts]
                if len(hist) >= 14:
                    tr_high = hist['high'].rolling(14).max().iloc[-1]
                    tr_low = hist['low'].rolling(14).min().iloc[-1]
                    atr_proxy = (tr_high - tr_low) / 14 if pd.notna(tr_high) and pd.notna(tr_low) else None
                else:
                    atr_proxy = None
                atr_mult = cfg.get('atr_mult_orb', 1.2)
                tp_mult = cfg.get('tp_multiplier', 2.0)
                if atr_proxy and pd.notna(atr_proxy) and atr_proxy > 0:
                    if side == 'long':
                        rec['stop_loss'] = float(entry_price - atr_proxy * atr_mult)
                        rec['take_profit'] = float(entry_price + atr_proxy * tp_mult)
                    else:
                        rec['stop_loss'] = float(entry_price + atr_proxy * atr_mult)
                        rec['take_profit'] = float(entry_price - atr_proxy * tp_mult)
            except Exception:
                pass
            return rec
        return {"status": "no_breakout", "orb_high": orb_high, "orb_low": orb_low}

    # Fetch today's session data (and next day if 24h) in 15m
    df = None
    if fetch_historical_data is not None:
        try:
            today = now.date()
            since = today.isoformat()
            until = today.isoformat()
            df = fetch_historical_data(symbol, since, until, "15m")
            if config.get("full_day_trading", False):
                # Fetch next day to allow late breakouts and context
                next_day = (today + timedelta(days=1)).isoformat()
                extra = fetch_historical_data(symbol, until, next_day, "15m")
                if extra is not None and not extra.empty:
                    try:
                        df = pd.concat([df, extra]).sort_index().drop_duplicates()
                    except Exception:
                        pass
        except Exception:
            df = None

    # If no data, attempt cache
    if df is None or df.empty:
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                cached["from_cache"] = True
                return cached
            except Exception:
                pass
        return {
            "status": "no_data",
            "symbol": symbol,
            "date": now.strftime("%Y-%m-%d"),
            "macro_bias": "neutral",
            "orb_high": None,
            "orb_low": None,
            "notes": "No data and no cache available",
            "from_cache": True
        }

    rec = _evaluate_orb_single_day(df, now.date(), config)
    
    # If no signal and force_one_trade is enabled, try fallback
    if rec.get("status") != "signal" and config.get("force_one_trade", False):
        # Simple fallback logic similar to SimpleTradingStrategy
        try:
            if len(df) >= 15:
                ema15 = df['close'].ewm(span=15, adjust=False).mean().iloc[-1]
                current_price = df['close'].iloc[-1]
                
                # Try both sides
                for side in ['long', 'short']:
                    if side == 'long':
                        pullback_ok = current_price <= ema15 * 1.001
                    else:
                        pullback_ok = current_price >= ema15 * 0.999
                    
                    if pullback_ok:
                        # Calculate simple SL/TP using ATR proxy
                        if len(df) >= 14:
                            tr_high = df['high'].rolling(14).max().iloc[-1]
                            tr_low = df['low'].rolling(14).min().iloc[-1]
                            atr_proxy = (tr_high - tr_low) / 14 if pd.notna(tr_high) and pd.notna(tr_low) else None
                        else:
                            atr_proxy = None
                        
                        if atr_proxy and pd.notna(atr_proxy) and atr_proxy > 0:
                            atr_mult = config.get('atr_mult_orb', 1.2)
                            tp_mult = config.get('tp_multiplier', 2.0)
                            
                            if side == 'long':
                                stop_loss = current_price - (atr_proxy * atr_mult)
                                take_profit = current_price + (atr_proxy * tp_mult)
                            else:
                                stop_loss = current_price + (atr_proxy * atr_mult)
                                take_profit = current_price - (atr_proxy * tp_mult)
                            
                            # Create fallback signal
                            rec = {
                                "status": "signal",
                                "symbol": symbol,
                                "date": now.strftime("%Y-%m-%d"),
                                "macro_bias": "neutral",
                                "side": side,
                                "entry_time": df.index[-1].isoformat(),
                                "entry_price": float(current_price),
                                "stop_loss": float(stop_loss),
                                "take_profit": float(take_profit),
                                "orb_high": None,
                                "orb_low": None,
                                "notes": "Trade forzado por fallback EMA15",
                                "from_cache": False,
                                "used_fallback": True
                            }
                            break
        except Exception:
            pass
    
    # Save latest recommendation if it is a signal or meaningful state
    try:
        to_store = {**rec, "symbol": symbol, "date": now.strftime("%Y-%m-%d")}
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(to_store, f, ensure_ascii=False, indent=2, default=str)
    except Exception:
        pass
    return rec