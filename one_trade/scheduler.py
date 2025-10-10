"""Trading scheduler with time windows and daily trade limits."""
from datetime import datetime, time
from typing import Optional

import pytz


class TradingScheduler:
    """Manages trading windows and enforces daily trade limits."""
    
    def __init__(self, scheduling_config: dict, validation_config: dict, local_tz: str = "America/Argentina/Buenos_Aires"):
        """Initialize TradingScheduler. Args: scheduling_config: Scheduling configuration dict. validation_config: Validation configuration dict. local_tz: Local timezone string."""
        self.entry_window_start = self._parse_time(scheduling_config["entry_window"]["start"])
        self.entry_window_end = self._parse_time(scheduling_config["entry_window"]["end"])
        self.forced_close_start = self._parse_time(scheduling_config["forced_close_window"]["start"])
        self.forced_close_end = self._parse_time(scheduling_config["forced_close_window"]["end"])
        self.max_trades_per_day = scheduling_config["max_trades_per_day"]
        self.enforce_daily_limit = scheduling_config["enforce_daily_limit"]
        self.strict_mode = validation_config["strict_mode"]
        self.check_trade_limit = validation_config["check_trade_limit_daily"]
        self.check_entry_windows = validation_config["check_entry_windows"]
        self.check_forced_close = validation_config["check_forced_close"]
        self.local_tz = pytz.timezone(local_tz)
        self.daily_trade_count = {}
        self.last_reset_date = None
    
    def _parse_time(self, time_str: str) -> time:
        """Parse time string in HH:MM format."""
        hour, minute = map(int, time_str.split(":"))
        return time(hour=hour, minute=minute)
    
    def _to_local_time(self, timestamp_utc: datetime) -> datetime:
        """Convert UTC timestamp to local timezone."""
        if timestamp_utc.tzinfo is None:
            timestamp_utc = timestamp_utc.replace(tzinfo=pytz.UTC)
        return timestamp_utc.astimezone(self.local_tz)
    
    def _reset_daily_counters_if_needed(self, timestamp_utc: datetime) -> None:
        """Reset daily counters if new day in local timezone."""
        local_time = self._to_local_time(timestamp_utc)
        current_date = local_time.date()
        if self.last_reset_date is None or current_date != self.last_reset_date:
            self.daily_trade_count = {}
            self.last_reset_date = current_date
    
    def can_enter_trade(self, timestamp_utc: datetime, symbol: str) -> tuple[bool, str]:
        """Check if entry is allowed at given timestamp. Args: timestamp_utc: UTC timestamp to check. symbol: Trading symbol. Returns: (can_enter, reason) tuple."""
        self._reset_daily_counters_if_needed(timestamp_utc)
        local_time = self._to_local_time(timestamp_utc)
        current_time = local_time.time()
        current_date = local_time.date()
        if self.check_entry_windows:
            in_entry_window = self.entry_window_start <= current_time <= self.entry_window_end
            if not in_entry_window:
                return False, f"Outside entry window (06:00-12:00 ART). Current: {current_time.strftime('%H:%M')}"
        if self.enforce_daily_limit and self.check_trade_limit:
            trades_today = self.daily_trade_count.get(current_date, {}).get(symbol, 0)
            if trades_today >= self.max_trades_per_day:
                msg = f"Daily trade limit reached ({trades_today}/{self.max_trades_per_day})"
                return False, msg
        return True, "OK"
    
    def register_trade(self, timestamp_utc: datetime, symbol: str) -> None:
        """Register a trade for daily counting. Args: timestamp_utc: UTC timestamp of trade. symbol: Trading symbol."""
        self._reset_daily_counters_if_needed(timestamp_utc)
        local_time = self._to_local_time(timestamp_utc)
        current_date = local_time.date()
        if current_date not in self.daily_trade_count:
            self.daily_trade_count[current_date] = {}
        if symbol not in self.daily_trade_count[current_date]:
            self.daily_trade_count[current_date][symbol] = 0
        self.daily_trade_count[current_date][symbol] += 1
        if self.strict_mode and self.check_trade_limit:
            trades_today = self.daily_trade_count[current_date][symbol]
            if trades_today > self.max_trades_per_day:
                raise RuntimeError(f"STRICT MODE VIOLATION: More than {self.max_trades_per_day} trades detected for {symbol} on {current_date}. Count: {trades_today}")
    
    def should_force_close(self, timestamp_utc: datetime) -> tuple[bool, str]:
        """Check if position should be force-closed. Args: timestamp_utc: UTC timestamp to check. Returns: (should_close, reason) tuple."""
        if not self.check_forced_close:
            return False, ""
        local_time = self._to_local_time(timestamp_utc)
        current_time = local_time.time()
        in_forced_close_window = self.forced_close_start <= current_time <= self.forced_close_end
        if in_forced_close_window:
            return True, f"FORCED_CLOSE_19-20_ART (local time: {current_time.strftime('%H:%M')})"
        return False, ""
    
    def get_trades_today(self, timestamp_utc: datetime, symbol: str) -> int:
        """Get number of trades executed today for symbol. Args: timestamp_utc: UTC timestamp. symbol: Trading symbol. Returns: Number of trades today."""
        self._reset_daily_counters_if_needed(timestamp_utc)
        local_time = self._to_local_time(timestamp_utc)
        current_date = local_time.date()
        return self.daily_trade_count.get(current_date, {}).get(symbol, 0)
    
    def validate_daily_limit(self, symbol: Optional[str] = None) -> None:
        """Validate that daily trade limits were not exceeded. Args: symbol: Optional symbol to check. If None, checks all symbols. Raises: AssertionError: If daily limit was exceeded."""
        if not self.check_trade_limit:
            return
        for date, symbols in self.daily_trade_count.items():
            if symbol:
                count = symbols.get(symbol, 0)
                assert count <= self.max_trades_per_day, f"Daily trade limit violated for {symbol} on {date}: {count} > {self.max_trades_per_day}"
            else:
                for sym, count in symbols.items():
                    assert count <= self.max_trades_per_day, f"Daily trade limit violated for {sym} on {date}: {count} > {self.max_trades_per_day}"
    
    def get_entry_window_info(self) -> dict:
        """Get entry window configuration."""
        return {"start": self.entry_window_start.strftime("%H:%M"), "end": self.entry_window_end.strftime("%H:%M"), "timezone": str(self.local_tz)}
    
    def get_forced_close_window_info(self) -> dict:
        """Get forced close window configuration."""
        return {"start": self.forced_close_start.strftime("%H:%M"), "end": self.forced_close_end.strftime("%H:%M"), "timezone": str(self.local_tz)}

