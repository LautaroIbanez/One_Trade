"""Trading strategy implementations with configurable signals."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class Signal:
    """Trading signal representation."""
    timestamp: datetime
    side: str
    entry_price: float
    stop_loss: float
    take_profit: float
    reason: str
    confidence: float = 1.0


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, config: dict):
        """Initialize strategy. Args: config: Strategy configuration dictionary."""
        self.config = config
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame, current_idx: int) -> Optional[Signal]:
        """Generate trading signal based on current data. Args: data: OHLCV DataFrame with datetime index. current_idx: Current position in data. Returns: Signal object or None if no signal."""
        pass
    
    @abstractmethod
    def should_close(self, data: pd.DataFrame, current_idx: int, position_side: str, entry_price: float, entry_time: datetime) -> Tuple[bool, str]:
        """Check if position should be closed. Args: data: OHLCV DataFrame. current_idx: Current position. position_side: 'long' or 'short'. entry_price: Entry price. entry_time: Entry timestamp. Returns: (should_close, reason)."""
        pass


class CurrentStrategy(BaseStrategy):
    """Current strategy based on existing system (ORB + EMA/RSI/MACD)."""
    
    def __init__(self, config: dict):
        """Initialize current strategy."""
        super().__init__(config)
        self.indicators = config.get("indicators", {})
        self.entry_conditions = config.get("entry_conditions", {})
        self.ema_fast = self.indicators.get("ema_fast", 12)
        self.ema_slow = self.indicators.get("ema_slow", 26)
        self.rsi_period = self.indicators.get("rsi_period", 14)
        self.rsi_oversold = self.indicators.get("rsi_oversold", 30)
        self.rsi_overbought = self.indicators.get("rsi_overbought", 70)
        self.macd_fast = self.indicators.get("macd_fast", 12)
        self.macd_slow = self.indicators.get("macd_slow", 26)
        self.macd_signal = self.indicators.get("macd_signal", 9)
        self.require_ema_cross = self.entry_conditions.get("require_ema_cross", True)
        self.require_rsi_confirmation = self.entry_conditions.get("require_rsi_confirmation", True)
        self.require_macd_confirmation = self.entry_conditions.get("require_macd_confirmation", True)
        self.atr_period = 14
        self.atr_mult_sl = 2.0
        self.atr_mult_tp = 3.0
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all required indicators."""
        df = data.copy()
        df["ema_fast"] = df["close"].ewm(span=self.ema_fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.ema_slow, adjust=False).mean()
        df["rsi"] = self._calculate_rsi(df["close"], self.rsi_period)
        macd_line, signal_line, _ = self._calculate_macd(df["close"], self.macd_fast, self.macd_slow, self.macd_signal)
        df["macd"] = macd_line
        df["macd_signal"] = signal_line
        df["atr"] = self._calculate_atr(df, self.atr_period)
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator."""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high = data["high"]
        low = data["low"]
        close = data["close"]
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def generate_signal(self, data: pd.DataFrame, current_idx: int) -> Optional[Signal]:
        """Generate signal based on EMA cross, RSI, and MACD."""
        if current_idx < max(self.ema_slow, self.rsi_period, self.macd_slow) + 10:
            return None
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        prev = df.iloc[current_idx - 1]
        if pd.isna(current["ema_fast"]) or pd.isna(current["rsi"]) or pd.isna(current["atr"]):
            return None
        long_signal = False
        short_signal = False
        if self.require_ema_cross:
            ema_cross_bullish = prev["ema_fast"] <= prev["ema_slow"] and current["ema_fast"] > current["ema_slow"]
            ema_cross_bearish = prev["ema_fast"] >= prev["ema_slow"] and current["ema_fast"] < current["ema_slow"]
        else:
            ema_cross_bullish = current["ema_fast"] > current["ema_slow"]
            ema_cross_bearish = current["ema_fast"] < current["ema_slow"]
        if self.require_rsi_confirmation:
            rsi_bullish = current["rsi"] < 70 and current["rsi"] > 30
            rsi_bearish = current["rsi"] > 30 and current["rsi"] < 70
        else:
            rsi_bullish = True
            rsi_bearish = True
        if self.require_macd_confirmation:
            macd_bullish = current["macd"] > current["macd_signal"]
            macd_bearish = current["macd"] < current["macd_signal"]
        else:
            macd_bullish = True
            macd_bearish = True
        long_signal = ema_cross_bullish and rsi_bullish and macd_bullish
        short_signal = ema_cross_bearish and rsi_bearish and macd_bearish
        if not long_signal and not short_signal:
            return None
        side = "long" if long_signal else "short"
        entry_price = current["close"]
        atr_value = current["atr"]
        if side == "long":
            stop_loss = entry_price - (atr_value * self.atr_mult_sl)
            take_profit = entry_price + (atr_value * self.atr_mult_tp)
            reason = "EMA_CROSS_LONG"
        else:
            stop_loss = entry_price + (atr_value * self.atr_mult_sl)
            take_profit = entry_price - (atr_value * self.atr_mult_tp)
            reason = "EMA_CROSS_SHORT"
        return Signal(timestamp=current.name, side=side, entry_price=entry_price, stop_loss=stop_loss, take_profit=take_profit, reason=reason, confidence=1.0)
    
    def should_close(self, data: pd.DataFrame, current_idx: int, position_side: str, entry_price: float, entry_time: datetime) -> Tuple[bool, str]:
        """Check if position should be closed based on indicators."""
        if current_idx >= len(data):
            return False, ""
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        if position_side == "long":
            if not pd.isna(current["ema_fast"]) and not pd.isna(current["ema_slow"]):
                if current["ema_fast"] < current["ema_slow"]:
                    return True, "EMA_CROSS_EXIT"
        elif position_side == "short":
            if not pd.isna(current["ema_fast"]) and not pd.isna(current["ema_slow"]):
                if current["ema_fast"] > current["ema_slow"]:
                    return True, "EMA_CROSS_EXIT"
        return False, ""


class BaselineStrategy(BaseStrategy):
    """Baseline simple strategy with EMA and RSI."""
    
    def __init__(self, config: dict):
        """Initialize baseline strategy."""
        super().__init__(config)
        self.indicators = config.get("indicators", {})
        self.entry_conditions = config.get("entry_conditions", {})
        self.ema_period = self.indicators.get("ema_period", 50)
        self.rsi_period = self.indicators.get("rsi_period", 14)
        self.rsi_oversold = self.indicators.get("rsi_oversold", 35)
        self.rsi_overbought = self.indicators.get("rsi_overbought", 65)
        self.price_above_ema = self.entry_conditions.get("price_above_ema", True)
        self.rsi_range = self.entry_conditions.get("rsi_range", True)
        self.atr_period = 14
        self.atr_mult_sl = 2.0
        self.atr_mult_tp = 3.0
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate EMA, RSI, and ATR."""
        df = data.copy()
        df["ema"] = df["close"].ewm(span=self.ema_period, adjust=False).mean()
        df["rsi"] = self._calculate_rsi(df["close"], self.rsi_period)
        df["atr"] = self._calculate_atr(df, self.atr_period)
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high = data["high"]
        low = data["low"]
        close = data["close"]
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def generate_signal(self, data: pd.DataFrame, current_idx: int) -> Optional[Signal]:
        """Generate simple signal: long when price > EMA and RSI not extreme."""
        if current_idx < max(self.ema_period, self.rsi_period) + 10:
            return None
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        prev = df.iloc[current_idx - 1]
        if pd.isna(current["ema"]) or pd.isna(current["rsi"]) or pd.isna(current["atr"]):
            return None
        price = current["close"]
        ema = current["ema"]
        rsi = current["rsi"]
        if self.price_above_ema:
            price_condition_long = price > ema
            price_condition_short = price < ema
        else:
            price_condition_long = True
            price_condition_short = True
        if self.rsi_range:
            rsi_condition = self.rsi_oversold < rsi < self.rsi_overbought
        else:
            rsi_condition = True
        long_signal = price_condition_long and rsi_condition and prev["close"] <= prev["ema"] and price > ema
        short_signal = price_condition_short and rsi_condition and prev["close"] >= prev["ema"] and price < ema
        if not long_signal and not short_signal:
            return None
        side = "long" if long_signal else "short"
        entry_price = current["close"]
        atr_value = current["atr"]
        if side == "long":
            stop_loss = entry_price - (atr_value * self.atr_mult_sl)
            take_profit = entry_price + (atr_value * self.atr_mult_tp)
            reason = "BASELINE_LONG"
        else:
            stop_loss = entry_price + (atr_value * self.atr_mult_sl)
            take_profit = entry_price - (atr_value * self.atr_mult_tp)
            reason = "BASELINE_SHORT"
        return Signal(timestamp=current.name, side=side, entry_price=entry_price, stop_loss=stop_loss, take_profit=take_profit, reason=reason, confidence=1.0)
    
    def should_close(self, data: pd.DataFrame, current_idx: int, position_side: str, entry_price: float, entry_time: datetime) -> Tuple[bool, str]:
        """Check if position should be closed (price crosses EMA opposite direction)."""
        if current_idx >= len(data):
            return False, ""
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        price = current["close"]
        ema = current["ema"]
        if pd.isna(ema):
            return False, ""
        if position_side == "long" and price < ema:
            return True, "PRICE_BELOW_EMA"
        elif position_side == "short" and price > ema:
            return True, "PRICE_ABOVE_EMA"
        return False, ""


class StrategyFactory:
    """Factory for creating strategy instances."""
    
    @staticmethod
    def create_strategy(strategy_type: str, config: dict) -> BaseStrategy:
        """Create strategy instance based on type. Args: strategy_type: 'current', 'baseline', or 'custom'. config: Strategy configuration. Returns: Strategy instance. Raises: ValueError: If strategy type is unknown."""
        if strategy_type == "current":
            return CurrentStrategy(config)
        elif strategy_type == "baseline":
            return BaselineStrategy(config)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")









