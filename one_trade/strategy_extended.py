"""Extended trading strategies for enhanced recommendation engine."""
from datetime import datetime
from typing import Optional, Tuple
import numpy as np
import pandas as pd
from one_trade.strategy import BaseStrategy, Signal


class RSIStrategy(BaseStrategy):
    """Strategy based on RSI levels with divergence detection."""
    
    def __init__(self, config: dict):
        """Initialize RSI strategy."""
        super().__init__(config)
        self.indicators = config.get("indicators", {})
        self.entry_conditions = config.get("entry_conditions", {})
        self.rsi_period = self.indicators.get("rsi_period", 14)
        self.rsi_oversold = self.indicators.get("rsi_oversold", 30)
        self.rsi_overbought = self.indicators.get("rsi_overbought", 70)
        self.rsi_extreme_oversold = self.indicators.get("rsi_extreme_oversold", 20)
        self.rsi_extreme_overbought = self.indicators.get("rsi_extreme_overbought", 80)
        self.detect_divergence = self.entry_conditions.get("detect_divergence", False)
        self.atr_period = 14
        self.atr_mult_sl = 2.0
        self.atr_mult_tp = 3.0
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI and ATR."""
        df = data.copy()
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
        """Generate signal based on RSI levels."""
        if current_idx < self.rsi_period + 10:
            return None
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        prev = df.iloc[current_idx - 1]
        if pd.isna(current["rsi"]) or pd.isna(current["atr"]):
            return None
        rsi = current["rsi"]
        prev_rsi = prev["rsi"]
        long_signal = False
        short_signal = False
        reason = ""
        confidence = 0.5
        if rsi < self.rsi_extreme_oversold and prev_rsi >= self.rsi_extreme_oversold:
            long_signal = True
            reason = "RSI_EXTREME_OVERSOLD"
            confidence = 0.9
        elif rsi < self.rsi_oversold and prev_rsi >= rsi:
            long_signal = True
            reason = "RSI_OVERSOLD"
            confidence = 0.7
        elif rsi > self.rsi_extreme_overbought and prev_rsi <= self.rsi_extreme_overbought:
            short_signal = True
            reason = "RSI_EXTREME_OVERBOUGHT"
            confidence = 0.9
        elif rsi > self.rsi_overbought and prev_rsi <= rsi:
            short_signal = True
            reason = "RSI_OVERBOUGHT"
            confidence = 0.7
        if not long_signal and not short_signal:
            return None
        side = "long" if long_signal else "short"
        entry_price = current["close"]
        atr_value = current["atr"]
        if side == "long":
            stop_loss = entry_price - (atr_value * self.atr_mult_sl)
            take_profit = entry_price + (atr_value * self.atr_mult_tp)
        else:
            stop_loss = entry_price + (atr_value * self.atr_mult_sl)
            take_profit = entry_price - (atr_value * self.atr_mult_tp)
        return Signal(timestamp=current.name, side=side, entry_price=entry_price, stop_loss=stop_loss, take_profit=take_profit, reason=reason, confidence=confidence)
    
    def should_close(self, data: pd.DataFrame, current_idx: int, position_side: str, entry_price: float, entry_time: datetime) -> Tuple[bool, str]:
        """Check if position should be closed based on RSI crossing back."""
        if current_idx >= len(data):
            return False, ""
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        rsi = current["rsi"]
        if pd.isna(rsi):
            return False, ""
        if position_side == "long" and rsi > self.rsi_overbought:
            return True, "RSI_OVERBOUGHT_EXIT"
        elif position_side == "short" and rsi < self.rsi_oversold:
            return True, "RSI_OVERSOLD_EXIT"
        return False, ""


class BollingerBandsStrategy(BaseStrategy):
    """Strategy based on Bollinger Bands breakouts and squeezes."""
    
    def __init__(self, config: dict):
        """Initialize Bollinger Bands strategy."""
        super().__init__(config)
        self.indicators = config.get("indicators", {})
        self.entry_conditions = config.get("entry_conditions", {})
        self.bb_period = self.indicators.get("bb_period", 20)
        self.bb_std = self.indicators.get("bb_std", 2.0)
        self.require_squeeze = self.entry_conditions.get("require_squeeze", False)
        self.atr_period = 14
        self.atr_mult_sl = 2.0
        self.atr_mult_tp = 3.0
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and ATR."""
        df = data.copy()
        df["bb_middle"] = df["close"].rolling(window=self.bb_period).mean()
        rolling_std = df["close"].rolling(window=self.bb_period).std()
        df["bb_upper"] = df["bb_middle"] + (rolling_std * self.bb_std)
        df["bb_lower"] = df["bb_middle"] - (rolling_std * self.bb_std)
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
        df["atr"] = self._calculate_atr(df, self.atr_period)
        return df
    
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
        """Generate signal based on Bollinger Bands breakouts."""
        if current_idx < self.bb_period + 10:
            return None
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        prev = df.iloc[current_idx - 1]
        if pd.isna(current["bb_upper"]) or pd.isna(current["atr"]):
            return None
        price = current["close"]
        prev_price = prev["close"]
        bb_upper = current["bb_upper"]
        bb_lower = current["bb_lower"]
        prev_bb_upper = prev["bb_upper"]
        prev_bb_lower = prev["bb_lower"]
        long_signal = False
        short_signal = False
        reason = ""
        if prev_price <= prev_bb_lower and price > bb_lower:
            long_signal = True
            reason = "BB_LOWER_BREAKOUT"
        elif prev_price >= prev_bb_upper and price < bb_upper:
            short_signal = True
            reason = "BB_UPPER_BREAKOUT"
        if not long_signal and not short_signal:
            return None
        side = "long" if long_signal else "short"
        entry_price = current["close"]
        atr_value = current["atr"]
        if side == "long":
            stop_loss = entry_price - (atr_value * self.atr_mult_sl)
            take_profit = entry_price + (atr_value * self.atr_mult_tp)
        else:
            stop_loss = entry_price + (atr_value * self.atr_mult_sl)
            take_profit = entry_price - (atr_value * self.atr_mult_tp)
        confidence = 0.75
        return Signal(timestamp=current.name, side=side, entry_price=entry_price, stop_loss=stop_loss, take_profit=take_profit, reason=reason, confidence=confidence)
    
    def should_close(self, data: pd.DataFrame, current_idx: int, position_side: str, entry_price: float, entry_time: datetime) -> Tuple[bool, str]:
        """Check if position should be closed when price touches opposite band."""
        if current_idx >= len(data):
            return False, ""
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        price = current["close"]
        bb_middle = current["bb_middle"]
        if pd.isna(bb_middle):
            return False, ""
        if position_side == "long" and price >= bb_middle:
            return True, "BB_MIDDLE_REACHED"
        elif position_side == "short" and price <= bb_middle:
            return True, "BB_MIDDLE_REACHED"
        return False, ""


class MACDHistogramStrategy(BaseStrategy):
    """Strategy based on MACD histogram momentum."""
    
    def __init__(self, config: dict):
        """Initialize MACD Histogram strategy."""
        super().__init__(config)
        self.indicators = config.get("indicators", {})
        self.entry_conditions = config.get("entry_conditions", {})
        self.macd_fast = self.indicators.get("macd_fast", 12)
        self.macd_slow = self.indicators.get("macd_slow", 26)
        self.macd_signal = self.indicators.get("macd_signal", 9)
        self.require_increasing = self.entry_conditions.get("require_increasing", True)
        self.atr_period = 14
        self.atr_mult_sl = 2.0
        self.atr_mult_tp = 3.0
    
    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD and histogram."""
        df = data.copy()
        ema_fast = df["close"].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = df["close"].ewm(span=self.macd_slow, adjust=False).mean()
        df["macd"] = ema_fast - ema_slow
        df["macd_signal"] = df["macd"].ewm(span=self.macd_signal, adjust=False).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]
        df["atr"] = self._calculate_atr(df, self.atr_period)
        return df
    
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
        """Generate signal based on MACD histogram momentum."""
        if current_idx < self.macd_slow + 10:
            return None
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        prev = df.iloc[current_idx - 1]
        prev2 = df.iloc[current_idx - 2]
        if pd.isna(current["macd_histogram"]) or pd.isna(current["atr"]):
            return None
        hist = current["macd_histogram"]
        prev_hist = prev["macd_histogram"]
        prev2_hist = prev2["macd_histogram"]
        long_signal = False
        short_signal = False
        reason = ""
        if prev_hist < 0 and hist > 0:
            long_signal = True
            reason = "MACD_HIST_CROSS_ABOVE"
        elif prev_hist > 0 and hist < 0:
            short_signal = True
            reason = "MACD_HIST_CROSS_BELOW"
        elif self.require_increasing:
            if hist > 0 and hist > prev_hist and prev_hist > prev2_hist:
                long_signal = True
                reason = "MACD_HIST_INCREASING"
            elif hist < 0 and hist < prev_hist and prev_hist < prev2_hist:
                short_signal = True
                reason = "MACD_HIST_DECREASING"
        if not long_signal and not short_signal:
            return None
        side = "long" if long_signal else "short"
        entry_price = current["close"]
        atr_value = current["atr"]
        if side == "long":
            stop_loss = entry_price - (atr_value * self.atr_mult_sl)
            take_profit = entry_price + (atr_value * self.atr_mult_tp)
        else:
            stop_loss = entry_price + (atr_value * self.atr_mult_sl)
            take_profit = entry_price - (atr_value * self.atr_mult_tp)
        confidence = 0.8
        return Signal(timestamp=current.name, side=side, entry_price=entry_price, stop_loss=stop_loss, take_profit=take_profit, reason=reason, confidence=confidence)
    
    def should_close(self, data: pd.DataFrame, current_idx: int, position_side: str, entry_price: float, entry_time: datetime) -> Tuple[bool, str]:
        """Check if position should be closed when histogram crosses zero."""
        if current_idx >= len(data):
            return False, ""
        df = self._calculate_indicators(data)
        current = df.iloc[current_idx]
        hist = current["macd_histogram"]
        if pd.isna(hist):
            return False, ""
        if position_side == "long" and hist < 0:
            return True, "MACD_HIST_NEGATIVE"
        elif position_side == "short" and hist > 0:
            return True, "MACD_HIST_POSITIVE"
        return False, ""


class ExtendedStrategyFactory:
    """Factory for creating extended strategy instances."""
    
    @staticmethod
    def create_strategy(strategy_type: str, config: dict) -> BaseStrategy:
        """Create strategy instance based on type."""
        from one_trade.strategy import CurrentStrategy, BaselineStrategy
        if strategy_type == "current":
            return CurrentStrategy(config)
        elif strategy_type == "baseline":
            return BaselineStrategy(config)
        elif strategy_type == "rsi":
            return RSIStrategy(config)
        elif strategy_type == "bollinger":
            return BollingerBandsStrategy(config)
        elif strategy_type == "macd_histogram":
            return MACDHistogramStrategy(config)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")




