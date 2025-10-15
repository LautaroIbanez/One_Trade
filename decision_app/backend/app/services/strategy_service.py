"""
Strategy service for managing and executing trading strategies.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from app.strategies import BaseStrategy, RSIStrategy, MACDStrategy, BollingerStrategy
from app.strategies.base_strategy import Signal
from app.core.logging import get_logger

logger = get_logger(__name__)


class StrategyService:
    """Service for managing trading strategies."""
    
    def __init__(self):
        """Initialize the strategy service."""
        self._strategies: Dict[str, BaseStrategy] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self) -> None:
        """Register default strategies."""
        # Register RSI strategy with default parameters
        rsi_strategy = RSIStrategy()
        self._strategies[rsi_strategy.name] = rsi_strategy
        logger.info(f"Registered strategy: {rsi_strategy.name}")
        
        # Register MACD strategy with default parameters
        macd_strategy = MACDStrategy()
        self._strategies[macd_strategy.name] = macd_strategy
        logger.info(f"Registered strategy: {macd_strategy.name}")
        
        # Register Bollinger Bands strategy with default parameters
        bollinger_strategy = BollingerStrategy()
        self._strategies[bollinger_strategy.name] = bollinger_strategy
        logger.info(f"Registered strategy: {bollinger_strategy.name}")
    
    def register_strategy(self, strategy: BaseStrategy) -> None:
        """
        Register a new strategy.
        
        Args:
            strategy: Strategy instance to register
        """
        self._strategies[strategy.name] = strategy
        logger.info(f"Registered strategy: {strategy.name}")
    
    def get_strategy(self, name: str) -> Optional[BaseStrategy]:
        """
        Get a strategy by name.
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy instance or None if not found
        """
        return self._strategies.get(name)
    
    def list_strategies(self) -> List[Dict[str, Any]]:
        """
        List all available strategies.
        
        Returns:
            List of strategy information
        """
        return [strategy.get_info() for strategy in self._strategies.values()]
    
    def analyze_with_strategy(
        self, 
        strategy_name: str, 
        data: pd.DataFrame
    ) -> List[Signal]:
        """
        Analyze data with a specific strategy.
        
        Args:
            strategy_name: Name of the strategy to use
            data: OHLCV market data
            
        Returns:
            List of trading signals
            
        Raises:
            ValueError: If strategy not found
        """
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            raise ValueError(f"Strategy '{strategy_name}' not found")
        
        try:
            signals = strategy.analyze(data)
            logger.info(f"Generated {len(signals)} signals using {strategy_name}")
            return signals
        except Exception as e:
            logger.error(f"Error analyzing with {strategy_name}: {str(e)}")
            raise
    
    def analyze_with_all_strategies(self, data: pd.DataFrame) -> Dict[str, List[Signal]]:
        """
        Analyze data with all available strategies.
        
        Args:
            data: OHLCV market data
            
        Returns:
            Dictionary mapping strategy names to their signals
        """
        results = {}
        
        for strategy_name in self._strategies.keys():
            try:
                signals = self.analyze_with_strategy(strategy_name, data)
                results[strategy_name] = signals
            except Exception as e:
                logger.error(f"Error with strategy {strategy_name}: {str(e)}")
                results[strategy_name] = []
        
        return results
    
    def get_strategy_performance(
        self, 
        strategy_name: str, 
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a strategy.
        
        Args:
            strategy_name: Name of the strategy
            data: OHLCV market data
            
        Returns:
            Performance metrics
        """
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            raise ValueError(f"Strategy '{strategy_name}' not found")
        
        try:
            signals = strategy.analyze(data)
            
            if not signals:
                return {
                    "strategy": strategy_name,
                    "total_signals": 0,
                    "buy_signals": 0,
                    "sell_signals": 0,
                    "hold_signals": 0,
                    "avg_confidence": 0.0
                }
            
            buy_signals = sum(1 for s in signals if s.signal.value == "BUY")
            sell_signals = sum(1 for s in signals if s.signal.value == "SELL")
            hold_signals = sum(1 for s in signals if s.signal.value == "HOLD")
            avg_confidence = sum(s.confidence for s in signals) / len(signals)
            
            return {
                "strategy": strategy_name,
                "total_signals": len(signals),
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "hold_signals": hold_signals,
                "avg_confidence": round(avg_confidence, 3)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance for {strategy_name}: {str(e)}")
            raise


# Global strategy service instance
strategy_service = StrategyService()
