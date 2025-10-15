"""
MACD (Moving Average Convergence Divergence) trading strategy.
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy, Signal, SignalType


class MACDStrategy(BaseStrategy):
    """
    MACD-based trading strategy.
    
    Generates BUY signals when MACD crosses above signal line
    and SELL signals when MACD crosses below signal line.
    """
    
    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        min_confidence: float = 0.6
    ):
        """
        Initialize MACD strategy.
        
        Args:
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line EMA period (default 9)
            min_confidence: Minimum confidence for signals (default 0.6)
        """
        parameters = {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period,
            "min_confidence": min_confidence
        }
        
        super().__init__(
            name="MACD Strategy",
            description="MACD-based trading strategy with signal line crossovers",
            parameters=parameters,
            min_data_points=slow_period + signal_period + 5  # MACD needs slow_period + signal_period + buffer
        )
    
    def _validate_parameters(self) -> None:
        """Validate MACD strategy parameters."""
        fast = self.parameters["fast_period"]
        slow = self.parameters["slow_period"]
        signal = self.parameters["signal_period"]
        min_conf = self.parameters["min_confidence"]
        
        if fast <= 0:
            raise ValueError("Fast period must be positive")
        
        if slow <= 0:
            raise ValueError("Slow period must be positive")
        
        if signal <= 0:
            raise ValueError("Signal period must be positive")
        
        if fast >= slow:
            raise ValueError("Fast period must be less than slow period")
        
        if not 0 <= min_conf <= 1:
            raise ValueError("Minimum confidence must be between 0 and 1")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD indicators.
        
        Args:
            data: OHLCV data
            
        Returns:
            DataFrame with MACD, signal line, and histogram columns
        """
        fast_period = self.parameters["fast_period"]
        slow_period = self.parameters["slow_period"]
        signal_period = self.parameters["signal_period"]
        
        # Calculate EMAs
        ema_fast = data['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = data['close'].ewm(span=slow_period, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line (EMA of MACD)
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        # Add indicators to data
        data['macd'] = macd_line
        data['macd_signal'] = signal_line
        data['macd_histogram'] = histogram
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals based on MACD crossovers.
        
        Args:
            data: OHLCV data with MACD indicators
            
        Returns:
            List of trading signals
        """
        signals = []
        min_conf = self.parameters["min_confidence"]
        
        # Only process data where MACD is available
        valid_data = data.dropna(subset=['macd', 'macd_signal'])
        
        if len(valid_data) < 2:
            return signals
        
        # Calculate MACD crossovers
        macd = valid_data['macd']
        signal_line = valid_data['macd_signal']
        
        # Find crossover points
        for i in range(1, len(valid_data)):
            prev_macd = macd.iloc[i-1]
            curr_macd = macd.iloc[i]
            prev_signal = signal_line.iloc[i-1]
            curr_signal = signal_line.iloc[i]
            
            row = valid_data.iloc[i]
            price = row['close']
            timestamp = row.name if hasattr(row.name, 'to_pydatetime') else pd.Timestamp.now()
            
            signal_type = None
            confidence = 0.0
            reasoning = ""
            
            # BUY signal: MACD crosses above signal line
            if prev_macd <= prev_signal and curr_macd > curr_signal:
                signal_type = SignalType.BUY
                # Calculate confidence based on the strength of the crossover
                crossover_strength = abs(curr_macd - curr_signal)
                confidence = min(1.0, crossover_strength / abs(curr_macd) + 0.5)
                reasoning = f"MACD bullish crossover: {curr_macd:.4f} > {curr_signal:.4f}"
            
            # SELL signal: MACD crosses below signal line
            elif prev_macd >= prev_signal and curr_macd < curr_signal:
                signal_type = SignalType.SELL
                # Calculate confidence based on the strength of the crossover
                crossover_strength = abs(curr_macd - curr_signal)
                confidence = min(1.0, crossover_strength / abs(curr_macd) + 0.5)
                reasoning = f"MACD bearish crossover: {curr_macd:.4f} < {curr_signal:.4f}"
            
            # Generate signal if confidence meets threshold
            if signal_type and confidence >= min_conf:
                signal = Signal(
                    signal=signal_type,
                    confidence=confidence,
                    price=price,
                    timestamp=timestamp,
                    reasoning=reasoning,
                    metadata={
                        "macd_value": curr_macd,
                        "signal_value": curr_signal,
                        "histogram": row['macd_histogram'],
                        "strategy": self.name,
                        "parameters": self.parameters
                    }
                )
                signals.append(signal)
        
        return signals
    
    def get_macd_values(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Get the latest MACD values for the given data.
        
        Args:
            data: OHLCV data
            
        Returns:
            Dictionary with MACD, signal, and histogram values
        """
        data_with_macd = self.calculate_indicators(data)
        
        if data_with_macd['macd'].isna().all():
            return {"macd": np.nan, "signal": np.nan, "histogram": np.nan}
        
        return {
            "macd": data_with_macd['macd'].iloc[-1],
            "signal": data_with_macd['macd_signal'].iloc[-1],
            "histogram": data_with_macd['macd_histogram'].iloc[-1]
        }
