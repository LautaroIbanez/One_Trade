"""
Intraday signal helper to compute today's ORB recommendation quickly.

Usage (CLI):
  python -m signals.today_signal --symbol BTC/USDT:USDT
"""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

import pandas as pd

# Local imports
from btc_1tpd_backtester.btc_1tpd_backtest_final import SimpleTradingStrategy
from btc_1tpd_backtester.utils import fetch_historical_data, resample_data
from btc_1tpd_backtester.indicators import get_macro_bias

__all__ = ["get_today_trade_recommendation"]


@dataclass
class Recommendation:
    status: str
    symbol: str
    date: str
    macro_bias: str
    side: Optional[str] = None
    entry_time: Optional[str] = None
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    orb_high: Optional[float] = None
    orb_low: Optional[float] = None
    minutes_to_orb: Optional[int] = None
    minutes_to_close: Optional[int] = None
    notes: Optional[str] = None


def _utc_floor_day(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)


def _compute_orb_levels(day_15m: pd.DataFrame, orb_window: tuple[int, int] = (11, 12)) -> (Optional[float], Optional[float]):
    if day_15m.empty:
        return None, None
    start_h, end_h = orb_window
    orb_data = day_15m[(day_15m.index.hour >= start_h) & (day_15m.index.hour < end_h)]
    if orb_data.empty:
        return None, None
    return float(orb_data["high"].max()), float(orb_data["low"].min())


def _find_breakout_in_entry_window(day_15m: pd.DataFrame, orb_high: float, orb_low: float, entry_window_hours: tuple[int, int] = (11, 13)):
    ew_start, ew_end = entry_window_hours
    entry_window = day_15m[(day_15m.index.hour >= ew_start) & (day_15m.index.hour < ew_end)]
    if entry_window.empty:
        return None, None, None
    for ts, row in entry_window.iterrows():
        high = row["high"]
        low = row["low"]
        if high >= orb_high:
            return "long", ts, float(max(row["open"], orb_high))
        if low <= orb_low:
            return "short", ts, float(min(row["open"], orb_low))
    return None, None, None


def get_today_trade_recommendation(symbol: str, config: Dict, now: Optional[datetime] = None) -> Dict:
    """
    Generate today's ORB recommendation using SimpleTradingStrategy with live data.

    Returns a dict with keys: status, symbol, date, macro_bias, side, entry_time,
    entry_price, stop_loss, take_profit, orb_high, orb_low, minutes_to_orb,
    minutes_to_close, notes.
    """
    now_utc = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    day_start = _utc_floor_day(now_utc)
    day_end = day_start + timedelta(days=1)

    # Fetch LTF 15m: include buffer from previous day 06:00 to ensure indicators
    since_15m = day_start - timedelta(hours=6)
    ltf_15m = fetch_historical_data(symbol, since_15m.isoformat(), day_end.isoformat(), timeframe="15m")

    # Fetch HTF 1h for macro bias: last ~300 hours
    since_1h = now_utc - timedelta(hours=300)
    htf_1h = fetch_historical_data(symbol, since_1h.isoformat(), now_utc.isoformat(), timeframe="1h")

    # Ensure indices and columns are correct
    if ltf_15m.empty or htf_1h.empty:
        return Recommendation(
            status="no_data",
            symbol=symbol,
            date=day_start.date().isoformat(),
            macro_bias="neutral",
            notes="No se pudieron obtener datos suficientes"
        ).__dict__

    # Keep only today's data for decision making
    day_15m = ltf_15m[(ltf_15m.index >= day_start) & (ltf_15m.index < day_end)]

    # Macro bias from 1h
    try:
        macro_bias = get_macro_bias(htf_1h)
    except Exception:
        macro_bias = "neutral"

    # Window configuration
    orb_window = config.get("orb_window", (11, 12))
    entry_window_hours = config.get("entry_window", (11, 13))
    full_day_trading = config.get("full_day_trading", False)
    
    # Adjust entry window for full day trading
    if full_day_trading:
        entry_window_hours = (0, 24)

    # ORB levels
    orb_high, orb_low = _compute_orb_levels(day_15m, orb_window)

    # Calculate window boundaries using timedelta
    orb_start = day_start + timedelta(hours=orb_window[0])
    orb_end = day_start + timedelta(hours=orb_window[1])
    
    entry_start = day_start + timedelta(hours=entry_window_hours[0])
    if entry_window_hours[1] == 24:
        entry_end = day_start + timedelta(days=1)
    else:
        entry_end = day_start + timedelta(hours=entry_window_hours[1])

    # Session times
    minutes_to_orb = max(0, int((orb_start - now_utc).total_seconds() // 60))
    minutes_to_close = max(0, int((entry_end - now_utc).total_seconds() // 60))

    # Before ORB window starts
    if now_utc < orb_start:
        return Recommendation(
            status="awaiting_orb",
            symbol=symbol,
            date=day_start.date().isoformat(),
            macro_bias=macro_bias,
            orb_high=orb_high,
            orb_low=orb_low,
            minutes_to_orb=minutes_to_orb,
            minutes_to_close=minutes_to_close,
            notes=f"Esperando ventana ORB ({orb_start.strftime('%H:%M')}–{orb_end.strftime('%H:%M')} UTC)"
        ).__dict__

    # During entry window
    if entry_start <= now_utc < entry_end:
        if orb_high is None or orb_low is None:
            return Recommendation(
                status="no_orb_levels",
                symbol=symbol,
                date=day_start.date().isoformat(),
                macro_bias=macro_bias,
                minutes_to_close=minutes_to_close,
                notes=f"Aún sin niveles ORB dentro de {orb_start.strftime('%H:%M')}–{orb_end.strftime('%H:%M')} UTC"
            ).__dict__

        side, breakout_time, entry_price = _find_breakout_in_entry_window(day_15m, orb_high, orb_low, entry_window_hours)
        if side is None:
            return Recommendation(
                status="awaiting_breakout",
                symbol=symbol,
                date=day_start.date().isoformat(),
                macro_bias=macro_bias,
                orb_high=orb_high,
                orb_low=orb_low,
                minutes_to_close=minutes_to_close,
                notes=f"Sin ruptura aún dentro de {entry_start.strftime('%H:%M')}–{entry_end.strftime('%H:%M')} UTC"
            ).__dict__

        # Compute SL/TP using SimpleTradingStrategy
        strat = SimpleTradingStrategy(config)
        # Calculate params using data only up to breakout_time
        prior_data = day_15m[day_15m.index <= breakout_time]
        trade_params = strat.calculate_trade_params(side, entry_price, prior_data, breakout_time)
        if not trade_params:
            return Recommendation(
                status="trigger_detected_params_unavailable",
                symbol=symbol,
                date=day_start.date().isoformat(),
                macro_bias=macro_bias,
                side=side,
                entry_time=breakout_time.isoformat(),
                entry_price=entry_price,
                orb_high=orb_high,
                orb_low=orb_low,
                notes="Ruptura detectada pero no se pudieron calcular SL/TP"
            ).__dict__

        return Recommendation(
            status="triggered",
            symbol=symbol,
            date=day_start.date().isoformat(),
            macro_bias=macro_bias,
            side=side,
            entry_time=breakout_time.isoformat(),
            entry_price=entry_price,
            stop_loss=float(trade_params["stop_loss"]),
            take_profit=float(trade_params["take_profit"]),
            orb_high=orb_high,
            orb_low=orb_low,
            notes="Ruptura ORB detectada dentro de la ventana de entrada"
        ).__dict__

    # After entry window
    if now_utc >= entry_end:
        # Session closed; check if a valid breakout occurred earlier in the window
        if orb_high is not None and orb_low is not None:
            side, breakout_time, entry_price = _find_breakout_in_entry_window(day_15m, orb_high, orb_low, entry_window_hours)
            if side is not None and breakout_time is not None and entry_price is not None:
                strat = SimpleTradingStrategy(config)
                prior_data = day_15m[day_15m.index <= breakout_time]
                trade_params = strat.calculate_trade_params(side, entry_price, prior_data, breakout_time)
                if not trade_params:
                    return Recommendation(
                        status="session_closed_params_unavailable",
                        symbol=symbol,
                        date=day_start.date().isoformat(),
                        macro_bias=macro_bias,
                        side=side,
                        entry_time=breakout_time.isoformat(),
                        entry_price=entry_price,
                        orb_high=orb_high,
                        orb_low=orb_low,
                        notes=f"Sesión cerrada: ruptura detectada pero no se pudieron calcular SL/TP"
                    ).__dict__
                return Recommendation(
                    status="session_closed_triggered",
                    symbol=symbol,
                    date=day_start.date().isoformat(),
                    macro_bias=macro_bias,
                    side=side,
                    entry_time=breakout_time.isoformat(),
                    entry_price=entry_price,
                    stop_loss=float(trade_params["stop_loss"]),
                    take_profit=float(trade_params["take_profit"]),
                    orb_high=orb_high,
                    orb_low=orb_low,
                    notes=f"Sesión cerrada: ruptura ORB ocurrió dentro de {entry_window_hours[0]:02d}:00–{entry_window_hours[1]:02d}:00 UTC"
                ).__dict__
        # No breakout at all during the window
        note = "Sesión cerrada: no hubo niveles ORB válidos" if orb_high is None or orb_low is None else f"Sesión cerrada: sin ruptura dentro de {entry_window_hours[0]:02d}:00–{entry_window_hours[1]:02d}:00 UTC"
        return Recommendation(
            status="session_closed",
            symbol=symbol,
            date=day_start.date().isoformat(),
            macro_bias=macro_bias,
            orb_high=orb_high,
            orb_low=orb_low,
            notes=note
        ).__dict__

    # Fallback
    return Recommendation(
        status="unknown_state",
        symbol=symbol,
        date=day_start.date().isoformat(),
        macro_bias=macro_bias,
        notes="Estado no reconocido"
    ).__dict__


def _parse_args():
    p = argparse.ArgumentParser(description="Get today's ORB recommendation")
    p.add_argument("--symbol", default="BTC/USDT:USDT")
    p.add_argument("--risk_usdt", type=float, default=20.0)
    p.add_argument("--adx_min", type=float, default=15.0)
    p.add_argument("--atr_mult_orb", type=float, default=1.2)
    p.add_argument("--tp_multiplier", type=float, default=2.0)
    return p.parse_args()


def main_cli():
    args = _parse_args()
    config = {
        "risk_usdt": args.risk_usdt,
        "daily_target": 50.0,
        "daily_max_loss": -30.0,
        "adx_min": args.adx_min,
        "atr_mult_orb": args.atr_mult_orb,
        "tp_multiplier": args.tp_multiplier,
    }
    rec = get_today_trade_recommendation(args.symbol, config)
    print(pd.Series(rec).to_string())


if __name__ == "__main__":
    main_cli()


