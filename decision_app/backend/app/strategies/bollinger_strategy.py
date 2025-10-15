"""
Bollinger Bands trading strategy.
"""

from typing import Dict, List, Any
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy, Signal, SignalType


class BollingerStrategy(BaseStrategy):
    """
    Bollinger Bands-based trading strategy.
    
    Generates BUY signals when price touches lower band and bounces
    and SELL signals when price touches upper band and retreats.
    """
    
    def __init__(
        self,
        period: int = 20,
        std_dev: float = 2.0,
        min_confidence: float = 0.6
    ):
        """
        Initialize Bollinger Bands strategy.
        
        Args:
            period: SMA period for Bollinger Bands (default 20)
            std_dev: Standard deviation multiplier (default 2.0)
            min_confidence: Minimum confidence for signals (default 0.6)
        """
        parameters = {
            "period": period,
            "std_dev": std_dev,
            "min_confidence": min_confidence
        }
        
        super().__init__(
            name="Bollinger Bands Strategy",
            description="Bollinger Bands-based trading strategy with band touch signals",
            parameters=parameters,
            min_data_points=period + 5  # Bollinger Bands need period + buffer
        )
    
    def _validate_parameters(self) -> None:
        """Validate Bollinger Bands strategy parameters."""
        period = self.parameters["period"]
        std_dev = self.parameters["std_dev"]
        min_conf = self.parameters["min_confidence"]
        
        if period <= 0:
            raise ValueError("Period must be positive")
        
        if std_dev <= 0:
            raise ValueError("Standard deviation must be positive")
        
        if not 0 <= min_conf <= 1:
            raise ValueError("Minimum confidence must be between 0 and 1")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands indicators.
        
        Args:
            data: OHLCV data
            
        Returns:
            DataFrame with Bollinger Bands columns
        """
        period = self.parameters["period"]
        std_dev = self.parameters["std_dev"]
        
        # Calculate Simple Moving Average
        sma = data['close'].rolling(window=period).mean()
        
        # Calculate Standard Deviation
        std = data['close'].rolling(window=period).std()
        
        # Calculate Bollinger Bands
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        # Calculate Band Width (volatility indicator)
        band_width = (upper_band - lower_band) / sma
        
        # Calculate %B (position within bands)
        percent_b = (data['close'] - lower_band) / (upper_band - lower_band)
        
        # Add indicators to data
        data['bb_upper'] = upper_band
        data['bb_middle'] = sma
        data['bb_lower'] = lower_band
        data['bb_width'] = band_width
        data['bb_percent'] = percent_b
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals based on Bollinger Bands touches.
        
        Args:
            data: OHLCV data with Bollinger Bands indicators
            
        Returns:
            List of trading signals
        """
        signals = []
        min_conf = self.parameters["min_confidence"]
        
        # Only process data where Bollinger Bands are available
        valid_data = data.dropna(subset=['bb_upper', 'bb_middle', 'bb_lower'])
        
        if len(valid_data) < 2:
            return signals
        
        # Look for band touches and bounces
        for i in range(1, len(valid_data)):
            prev_row = valid_data.iloc[i-1]
            curr_row = valid_data.iloc[i]
            
            price = curr_row['close']
            timestamp = curr_row.name if hasattr(curr_row.name, 'to_pydatetime') else pd.Timestamp.now()
            
            upper_band = curr_row['bb_upper']
            lower_band = curr_row['bb_lower']
            middle_band = curr_row['bb_middle']
            percent_b = curr_row['bb_percent']
            
            signal_type = None
            confidence = 0.0
            reasoning = ""
            
            # BUY signal: Price touches lower band and bounces
            if (prev_row['close'] <= prev_row['bb_lower'] and 
                price > lower_band and 
                percent_b > 0.1):  # Bounced above 10% of band width
                
                signal_type = SignalType.BUY
                # Calculate confidence based on bounce strength
                bounce_strength = (price - lower_band) / (upper_band - lower_band)
                confidence = min(1.0, bounce_strength + 0.5)
                reasoning = f"Bollinger lower band bounce: {price:.2f} > {lower_band:.2f} (bounce: {bounce_strength:.2%})"
            
            # SELL signal: Price touches upper band and retreats
            elif (prev_row['close'] >= prev_row['bb_upper'] and 
                  price < upper_band and 
                  percent_b < 0.9):  # Retreated below 90% of band width
                
                signal_type = SignalType.SELL
                # Calculate confidence based on retreat strength
                retreat_strength = (upper_band - price) / (upper_band - lower_band)
                confidence = min(1.0, retreat_strength + 0.5)
                reasoning = f"Bollinger upper band retreat: {price:.2f} < {upper_band:.2f} (retreat: {retreat_strength:.2%})"
            
            # Generate signal if confidence meets threshold
            if signal_type and confidence >= min_conf:
                signal = Signal(
                    signal=signal_type,
                    confidence=confidence,
                    price=price,
                    timestamp=timestamp,
                    reasoning=reasoning,
                    metadata={
                        "upper_band": upper_band,
                        "middle_band": middle_band,
                        "lower_band": lower_band,
                        "percent_b": percent_b,
                        "band_width": curr_row['bb_width'],
                        "strategy": self.name,
                        "parameters": self.parameters
                    }
                )
                signals.append(signal)
        
        return signals
    
    def get_bollinger_values(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Get the latest Bollinger Bands values for the given data.
        
        Args:
            data: OHLCV data
            
        Returns:
            Dictionary with Bollinger Bands values
        """
        data_with_bb = self.calculate_indicators(data)
        
        if data_with_bb['bb_upper'].isna().all():
            return {
                "upper_band": np.nan,
                "middle_band": np.nan,
                "lower_band": np.nan,
                "percent_b": np.nan,
                "band_width": np.nan
            }
        
        return {
            "upper_band": data_with_bb['bb_upper'].iloc[-1],
            "middle_band": data_with_bb['bb_middle'].iloc[-1],
            "lower_band": data_with_bb['bb_lower'].iloc[-1],
            "percent_b": data_with_bb['bb_percent'].iloc[-1],
            "band_width": data_with_bb['bb_width'].iloc[-1]
        }
