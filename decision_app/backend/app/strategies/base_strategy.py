"""
Base strategy class for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import pandas as pd
from pydantic import BaseModel, ConfigDict


class SignalType(str, Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Signal(BaseModel):
    """Trading signal model."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    signal: SignalType
    confidence: float  # 0.0 to 1.0
    price: float
    timestamp: pd.Timestamp
    reasoning: str
    metadata: Dict[str, Any] = {}


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    All strategies must implement the required methods to generate
    trading signals based on market data.
    """
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any], min_data_points: int = 20):
        """
        Initialize the strategy.
        
        Args:
            name: Strategy name
            description: Strategy description
            parameters: Strategy parameters
            min_data_points: Minimum number of data points required for the strategy
        """
        self.name = name
        self.description = description
        self.parameters = parameters
        self.min_data_points = min_data_points
        self._validate_parameters()
    
    @abstractmethod
    def _validate_parameters(self) -> None:
        """Validate strategy parameters."""
        pass
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the given data.
        
        Args:
            data: OHLCV data with columns ['open', 'high', 'low', 'close', 'volume']
            
        Returns:
            DataFrame with additional indicator columns
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        Generate trading signals based on the data and indicators.
        
        Args:
            data: OHLCV data with calculated indicators
            
        Returns:
            List of trading signals
        """
        pass
    
    def analyze(self, data: pd.DataFrame) -> List[Signal]:
        """
        Complete analysis pipeline: calculate indicators and generate signals.
        
        Args:
            data: OHLCV data
            
        Returns:
            List of trading signals
        """
        # Validate input data
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"Data must contain columns: {required_columns}")
        
        # Calculate indicators
        data_with_indicators = self.calculate_indicators(data.copy())
        
        # Generate signals
        signals = self.generate_signals(data_with_indicators)
        
        return signals
    
    def get_info(self) -> Dict[str, Any]:
        """Get strategy information."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "signal_types": [signal.value for signal in SignalType]
        }
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
