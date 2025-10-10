"""Broker simulation with order fills, stops, and fees."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pandas as pd


@dataclass
class Position:
    """Represents an open position."""
    symbol: str
    side: str
    entry_time_utc: datetime
    entry_time_art: datetime
    entry_price: float
    size: float
    stop_loss: float
    take_profit: float
    entry_reason: str
    entry_fees: float = 0.0


@dataclass
class Trade:
    """Represents a closed trade."""
    symbol: str
    side: str
    entry_time_utc: datetime
    entry_time_art: datetime
    entry_price: float
    exit_time_utc: datetime
    exit_time_art: datetime
    exit_price: float
    size: float
    pnl: float
    pnl_pct: float
    fees: float
    entry_reason: str
    exit_reason: str
    stop_loss: float = 0.0
    take_profit: float = 0.0


@dataclass
class BrokerState:
    """Broker state tracking."""
    capital: float
    equity: float
    position: Optional[Position] = None
    trades: list[Trade] = field(default_factory=list)
    total_fees: float = 0.0


class BrokerSimulator:
    """Simulates broker with order execution, stops, and fees."""
    
    def __init__(self, broker_config: dict, risk_config: dict, local_tz: str = "America/Argentina/Buenos_Aires"):
        """Initialize BrokerSimulator. Args: broker_config: Broker configuration dict. risk_config: Risk management configuration dict. local_tz: Local timezone string."""
        self.initial_capital = broker_config["initial_capital"]
        self.quote_currency = broker_config["quote_currency"]
        self.maker_fee = broker_config["fees"]["maker"]
        self.taker_fee = broker_config["fees"]["taker"]
        self.slippage_enabled = broker_config["slippage"]["enabled"]
        self.slippage_pct = broker_config["slippage"]["percentage"]
        self.risk_config = risk_config
        self.state = BrokerState(capital=self.initial_capital, equity=self.initial_capital)
        import pytz
        self.local_tz = pytz.timezone(local_tz)
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, current_equity: float) -> float:
        """Calculate position size based on risk management. Args: entry_price: Entry price. stop_loss: Stop loss price. current_equity: Current account equity. Returns: Position size in base currency."""
        sizing_config = self.risk_config["position_sizing"]
        method = sizing_config["method"]
        risk_per_trade_pct = sizing_config["risk_per_trade_pct"]
        max_position_pct = sizing_config["max_position_pct"]
        if method == "fixed_risk":
            risk_amount = current_equity * (risk_per_trade_pct / 100.0)
            price_diff = abs(entry_price - stop_loss)
            if price_diff == 0:
                return 0.0
            position_size = risk_amount / price_diff
            max_position_size = current_equity * (max_position_pct / 100.0) / entry_price
            position_size = min(position_size, max_position_size)
            return position_size
        elif method == "fixed_amount":
            return current_equity * (max_position_pct / 100.0) / entry_price
        else:
            return 0.0
    
    def apply_slippage(self, price: float, side: str) -> float:
        """Apply slippage to execution price. Args: price: Original price. side: 'long' or 'short'. Returns: Price with slippage."""
        if not self.slippage_enabled:
            return price
        if side == "long":
            return price * (1 + self.slippage_pct / 100.0)
        else:
            return price * (1 - self.slippage_pct / 100.0)
    
    def open_position(self, symbol: str, side: str, timestamp_utc: datetime, entry_price: float, stop_loss: float, take_profit: float, reason: str) -> bool:
        """Open a new position. Args: symbol: Trading symbol. side: 'long' or 'short'. timestamp_utc: Entry timestamp UTC. entry_price: Entry price. stop_loss: Stop loss price. take_profit: Take profit price. reason: Entry reason. Returns: True if position opened successfully."""
        if self.state.position is not None:
            return False
        actual_entry_price = self.apply_slippage(entry_price, side)
        position_size = self.calculate_position_size(actual_entry_price, stop_loss, self.state.equity)
        if position_size <= 0:
            return False
        entry_fees = position_size * actual_entry_price * self.taker_fee
        if timestamp_utc.tzinfo is None:
            import pytz
            timestamp_utc = timestamp_utc.replace(tzinfo=pytz.UTC)
        timestamp_art = timestamp_utc.astimezone(self.local_tz)
        self.state.position = Position(symbol=symbol, side=side, entry_time_utc=timestamp_utc, entry_time_art=timestamp_art, entry_price=actual_entry_price, size=position_size, stop_loss=stop_loss, take_profit=take_profit, entry_reason=reason, entry_fees=entry_fees)
        self.state.total_fees += entry_fees
        return True
    
    def check_stops(self, current_bar: pd.Series) -> tuple[bool, float, str]:
        """Check if stops are hit. Args: current_bar: Current OHLCV bar with high, low, close. Returns: (hit, exit_price, reason) tuple."""
        if self.state.position is None:
            return False, 0.0, ""
        position = self.state.position
        high = current_bar["high"]
        low = current_bar["low"]
        close = current_bar["close"]
        if position.side == "long":
            if low <= position.stop_loss:
                return True, position.stop_loss, "STOP_LOSS"
            elif high >= position.take_profit:
                return True, position.take_profit, "TAKE_PROFIT"
        elif position.side == "short":
            if high >= position.stop_loss:
                return True, position.stop_loss, "STOP_LOSS"
            elif low <= position.take_profit:
                return True, position.take_profit, "TAKE_PROFIT"
        return False, close, ""
    
    def close_position(self, timestamp_utc: datetime, exit_price: float, reason: str) -> Optional[Trade]:
        """Close current position. Args: timestamp_utc: Exit timestamp UTC. exit_price: Exit price. reason: Exit reason. Returns: Trade object or None if no position."""
        if self.state.position is None:
            return None
        position = self.state.position
        actual_exit_price = self.apply_slippage(exit_price, "short" if position.side == "long" else "long")
        exit_fees = position.size * actual_exit_price * self.taker_fee
        if position.side == "long":
            pnl = (actual_exit_price - position.entry_price) * position.size - position.entry_fees - exit_fees
        else:
            pnl = (position.entry_price - actual_exit_price) * position.size - position.entry_fees - exit_fees
        pnl_pct = (pnl / (position.entry_price * position.size)) * 100
        if timestamp_utc.tzinfo is None:
            import pytz
            timestamp_utc = timestamp_utc.replace(tzinfo=pytz.UTC)
        timestamp_art = timestamp_utc.astimezone(self.local_tz)
        trade = Trade(symbol=position.symbol, side=position.side, entry_time_utc=position.entry_time_utc, entry_time_art=position.entry_time_art, entry_price=position.entry_price, exit_time_utc=timestamp_utc, exit_time_art=timestamp_art, exit_price=actual_exit_price, size=position.size, pnl=pnl, pnl_pct=pnl_pct, fees=position.entry_fees + exit_fees, entry_reason=position.entry_reason, exit_reason=reason, stop_loss=position.stop_loss, take_profit=position.take_profit)
        self.state.equity += pnl
        self.state.total_fees += exit_fees
        self.state.trades.append(trade)
        self.state.position = None
        return trade
    
    def has_position(self) -> bool:
        """Check if there is an open position."""
        return self.state.position is not None
    
    def get_current_position(self) -> Optional[Position]:
        """Get current open position."""
        return self.state.position
    
    def get_equity(self) -> float:
        """Get current equity."""
        return self.state.equity
    
    def get_trades(self) -> list[Trade]:
        """Get all closed trades."""
        return self.state.trades
    
    def get_trade_count(self) -> int:
        """Get number of closed trades."""
        return len(self.state.trades)
    
    def reset(self) -> None:
        """Reset broker to initial state."""
        self.state = BrokerState(capital=self.initial_capital, equity=self.initial_capital)

