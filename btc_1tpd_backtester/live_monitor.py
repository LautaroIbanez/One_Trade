from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

import pandas as pd

from .signals.today_signal import get_today_trade_recommendation
from .utils import fetch_historical_data, fetch_latest_price


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ACTIVE_TRADE_PATH = DATA_DIR / "active_trade.json"


@dataclass
class ActiveTrade:
    symbol: str
    side: str
    entry_price: float
    stop_loss: float
    take_profit: float
    entry_time: str  # ISO string
    mode: str
    full_day_trading: bool

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(text: str) -> "ActiveTrade":
        data = json.loads(text)
        return ActiveTrade(**data)


def save_active_trade(trade: ActiveTrade) -> None:
    ACTIVE_TRADE_PATH.write_text(trade.to_json(), encoding="utf-8")


def load_active_trade() -> Optional[ActiveTrade]:
    if not ACTIVE_TRADE_PATH.exists():
        return None
    try:
        return ActiveTrade.from_json(ACTIVE_TRADE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def clear_active_trade() -> None:
    try:
        if ACTIVE_TRADE_PATH.exists():
            ACTIVE_TRADE_PATH.unlink()
    except Exception:
        pass


def detect_or_update_active_trade(symbol: str, mode: str, full_day_trading: bool, config: Dict[str, Any]) -> Optional[ActiveTrade]:
    """Query recommendation and update the active trade file accordingly.

    If recommendation returns a live signal with params, persist it as active.
    """
    rec = get_today_trade_recommendation(symbol, config)
    status = (rec.get("status") or "").lower()
    side = (rec.get("side") or "").lower()
    # Only persist if we have an actionable signal with params
    # Accept both direct status and "signal" status
    if (status in {"long", "short", "signal"}) and side in {"long", "short"}:
        entry_price = float(rec.get("entry_price")) if rec.get("entry_price") is not None else None
        stop_loss = float(rec.get("stop_loss")) if rec.get("stop_loss") is not None else None
        take_profit = float(rec.get("take_profit")) if rec.get("take_profit") is not None else None
        entry_time = rec.get("entry_time")
        if entry_price and stop_loss and take_profit and entry_time:
            at = ActiveTrade(
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                entry_time=str(entry_time),
                mode=mode,
                full_day_trading=bool(full_day_trading),
            )
            save_active_trade(at)
            return at
    return load_active_trade()


def evaluate_active_trade_exit(active: ActiveTrade) -> Optional[Dict[str, Any]]:
    """Check if active trade has hit SL/TP by fetching latest price.

    Returns exit dict with exit_time, exit_price, exit_reason if closed; otherwise None.
    """
    price_info = fetch_latest_price(active.symbol)
    if not price_info or price_info.get("price") is None:
        return None
    last_price = float(price_info["price"])  # latest price
    now = price_info.get("timestamp") or datetime.now(timezone.utc)
    # Basic TP/SL hit checks
    if active.side == "long":
        if last_price >= active.take_profit:
            return {"exit_time": now, "exit_price": active.take_profit, "exit_reason": "take_profit"}
        if last_price <= active.stop_loss:
            return {"exit_time": now, "exit_price": active.stop_loss, "exit_reason": "stop_loss"}
    else:  # short
        if last_price <= active.take_profit:
            return {"exit_time": now, "exit_price": active.take_profit, "exit_reason": "take_profit"}
        if last_price >= active.stop_loss:
            return {"exit_time": now, "exit_price": active.stop_loss, "exit_reason": "stop_loss"}
    return None




