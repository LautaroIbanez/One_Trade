"""
RSI (Relative Strength Index) trading strategy.
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy, Signal, SignalType


class RSIStrategy(BaseStrategy):
    """
    RSI-based trading strategy.
    
    Generates BUY signals when RSI < oversold_threshold (default 30)
    and SELL signals when RSI > overbought_threshold (default 70).
    """
    
    def __init__(
        self,
        period: int = 14,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0,
        min_confidence: float = 0.6
    ):
        """
        Initialize RSI strategy.
        
        Args:
            period: RSI calculation period (default 14)
            oversold_threshold: RSI level for BUY signals (default 30)
            overbought_threshold: RSI level for SELL signals (default 70)
            min_confidence: Minimum confidence for signals (default 0.6)
        """
        parameters = {
            "period": period,
            "oversold_threshold": oversold_threshold,
            "overbought_threshold": overbought_threshold,
            "min_confidence": min_confidence
        }
        
        super().__init__(
            name="RSI Strategy",
            description="RSI-based trading strategy with configurable thresholds",
            parameters=parameters,
            min_data_points=period + 5  # RSI needs period + some buffer
        )
    
    def _validate_parameters(self) -> None:
        """Validate RSI strategy parameters."""
        period = self.parameters["period"]
        oversold = self.parameters["oversold_threshold"]
        overbought = self.parameters["overbought_threshold"]
        min_conf = self.parameters["min_confidence"]
        
        if period <= 0:
            raise ValueError("RSI period must be positive")
        
        if not 0 <= oversold <= 100:
            raise ValueError("Oversold threshold must be between 0 and 100")
        
        if not 0 <= overbought <= 100:
            raise ValueError("Overbought threshold must be between 0 and 100")
        
        if oversold >= overbought:
            raise ValueError("Oversold threshold must be less than overbought threshold")
        
        if not 0 <= min_conf <= 1:
            raise ValueError("Minimum confidence must be between 0 and 1")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI indicator.
        
        Args:
            data: OHLCV data
            
        Returns:
            DataFrame with RSI column added
        """
        period = self.parameters["period"]
        
        # Calculate price changes
        delta = data['close'].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses using exponential moving average
        avg_gains = gains.ewm(span=period, adjust=False).mean()
        avg_losses = losses.ewm(span=period, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        # Add RSI to data
        data['rsi'] = rsi
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals based on RSI values.
        
        Args:
            data: OHLCV data with RSI indicator
            
        Returns:
            List of trading signals
        """
        signals = []
        oversold = self.parameters["oversold_threshold"]
        overbought = self.parameters["overbought_threshold"]
        min_conf = self.parameters["min_confidence"]
        
        # Only process data where RSI is available
        valid_data = data.dropna(subset=['rsi'])
        
        for idx, row in valid_data.iterrows():
            rsi_value = row['rsi']
            price = row['close']
            timestamp = row.name if hasattr(row.name, 'to_pydatetime') else pd.Timestamp.now()
            
            signal_type = None
            confidence = 0.0
            reasoning = ""
            
            # Generate BUY signal (oversold condition)
            if rsi_value <= oversold:
                signal_type = SignalType.BUY
                # Calculate confidence based on how oversold the RSI is
                confidence = min(1.0, (oversold - rsi_value) / oversold + 0.5)
                reasoning = f"RSI oversold: {rsi_value:.2f} <= {oversold}"
            
            # Generate SELL signal (overbought condition)
            elif rsi_value >= overbought:
                signal_type = SignalType.SELL
                # Calculate confidence based on how overbought the RSI is
                confidence = min(1.0, (rsi_value - overbought) / (100 - overbought) + 0.5)
                reasoning = f"RSI overbought: {rsi_value:.2f} >= {overbought}"
            
            # Generate HOLD signal (neutral zone)
            else:
                signal_type = SignalType.HOLD
                # Lower confidence for hold signals
                confidence = 0.3
                reasoning = f"RSI neutral: {rsi_value:.2f} between {oversold} and {overbought}"
            
            # Only create signal if confidence meets minimum threshold
            if confidence >= min_conf:
                signal = Signal(
                    signal=signal_type,
                    confidence=confidence,
                    price=price,
                    timestamp=timestamp,
                    reasoning=reasoning,
                    metadata={
                        "rsi_value": rsi_value,
                        "strategy": self.name,
                        "parameters": self.parameters
                    }
                )
                signals.append(signal)
        
        return signals
    
    def get_rsi_value(self, data: pd.DataFrame) -> float:
        """
        Get the latest RSI value for the given data.
        
        Args:
            data: OHLCV data
            
        Returns:
            Latest RSI value
        """
        data_with_rsi = self.calculate_indicators(data)
        return data_with_rsi['rsi'].iloc[-1] if not data_with_rsi['rsi'].isna().all() else np.nan
