"""Core recommendation types and orchestrator."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import pandas as pd


class RecommendationAction(Enum):
    """Possible recommendation actions."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Recommendation:
    """Trading recommendation with explanation."""
    timestamp: datetime
    symbol: str
    action: RecommendationAction
    confidence: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    reasoning: str = ""
    invalidation_condition: str = ""
    supporting_signals: List[Dict] = None
    
    def __post_init__(self):
        if self.supporting_signals is None: self.supporting_signals = []
        if not 0.0 <= self.confidence <= 1.0: raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")


@dataclass
class StrategySignal:
    """Internal representation of a strategy signal with metadata."""
    strategy_name: str
    signal_type: str
    strength: float
    details: Dict
    timestamp: datetime


class RecommendationEngine:
    """Orchestrator for generating recommendations from multiple strategies."""
    
    def __init__(self, strategies: List, strategy_weights: Optional[Dict[str, float]] = None, confidence_threshold: float = 0.6):
        """Initialize RecommendationEngine. Args: strategies: List of strategy instances implementing BaseStrategy. strategy_weights: Optional dict mapping strategy names to weights. confidence_threshold: Minimum confidence for non-HOLD recommendations."""
        self.strategies = strategies
        self.strategy_weights = strategy_weights or {f"strategy_{i}": 1.0 for i in range(len(strategies))}
        self.confidence_threshold = confidence_threshold
        from decision_app.recommendation_engine.condenser import SignalCondenser
        from decision_app.recommendation_engine.decisor import DecisionGenerator
        from decision_app.recommendation_engine.explainer import ExplainabilityModule
        self.condenser = SignalCondenser(strategy_weights=self.strategy_weights)
        self.decisor = DecisionGenerator(confidence_threshold=self.confidence_threshold)
        self.explainer = ExplainabilityModule()
    
    def generate_recommendation(self, symbol: str, data: pd.DataFrame, current_idx: int) -> Recommendation:
        """Generate recommendation for a given symbol and data state. Args: symbol: Trading symbol. data: OHLCV DataFrame with datetime index. current_idx: Current position in data. Returns: Recommendation object with action, confidence, and reasoning."""
        if isinstance(data.index, pd.DatetimeIndex):
            timestamp = data.index[current_idx]
        elif 'timestamp_utc' in data.columns:
            timestamp = data.iloc[current_idx]['timestamp_utc']
        else:
            from datetime import datetime, timezone
            timestamp = datetime.now(timezone.utc)
        strategy_signals = []
        for i, strategy in enumerate(self.strategies):
            strategy_name = getattr(strategy, 'name', f"Strategy_{i}")
            signal = strategy.generate_signal(data, current_idx)
            if signal is not None:
                signal_strength = 1.0 if signal.side == "long" else -1.0
                strategy_signals.append(StrategySignal(strategy_name=strategy_name, signal_type=signal.side, strength=signal_strength, details={"entry_price": signal.entry_price, "stop_loss": signal.stop_loss, "take_profit": signal.take_profit, "reason": signal.reason, "confidence": getattr(signal, 'confidence', 1.0)}, timestamp=signal.timestamp))
        if not strategy_signals:
            return Recommendation(timestamp=timestamp, symbol=symbol, action=RecommendationAction.HOLD, confidence=0.0, reasoning="No hay señales activas de ninguna estrategia. Esperar mejores condiciones de mercado.", invalidation_condition="")
        aggregated_signal = self.condenser.condense_signals(strategy_signals)
        decision = self.decisor.generate_decision(aggregated_signal, data, current_idx)
        explanation = self.explainer.explain(decision, strategy_signals, data, current_idx)
        return Recommendation(timestamp=timestamp, symbol=symbol, action=decision["action"], confidence=decision["confidence"], entry_price=decision.get("entry_price"), stop_loss=decision.get("stop_loss"), take_profit=decision.get("take_profit"), reasoning=explanation["reasoning"], invalidation_condition=explanation["invalidation"], supporting_signals=[{"strategy": s.strategy_name, "type": s.signal_type, "strength": s.strength} for s in strategy_signals])

