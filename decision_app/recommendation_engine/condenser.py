"""Signal Condenser - Aggregates signals from multiple strategies."""
from typing import Dict, List
import numpy as np


class SignalCondenser:
    """Condenses multiple strategy signals into a single aggregated signal."""
    
    def __init__(self, strategy_weights: Dict[str, float]):
        """Initialize SignalCondenser. Args: strategy_weights: Dict mapping strategy names to weights (0.0 to 1.0)."""
        self.strategy_weights = strategy_weights
        total_weight = sum(strategy_weights.values())
        if total_weight > 0: self.normalized_weights = {k: v / total_weight for k, v in strategy_weights.items()}
        else: self.normalized_weights = strategy_weights
    
    def condense_signals(self, signals: List) -> Dict:
        """Aggregate multiple signals into single signal. Args: signals: List of StrategySignal objects. Returns: Dict with aggregated signal info."""
        if not signals: return {"aggregated_strength": 0.0, "signal_count": 0, "long_signals": 0, "short_signals": 0, "average_confidence": 0.0, "weighted_strength": 0.0}
        long_signals = sum(1 for s in signals if s.signal_type == "long")
        short_signals = sum(1 for s in signals if s.signal_type == "short")
        weighted_sum = 0.0
        total_weight = 0.0
        confidences = []
        for signal in signals:
            weight = self.normalized_weights.get(signal.strategy_name, 1.0 / len(signals))
            weighted_sum += signal.strength * weight
            total_weight += weight
            signal_confidence = signal.details.get("confidence", 1.0)
            confidences.append(signal_confidence)
        weighted_strength = weighted_sum / total_weight if total_weight > 0 else 0.0
        average_confidence = np.mean(confidences) if confidences else 0.0
        aggregated_strength = weighted_strength * average_confidence
        return {"aggregated_strength": aggregated_strength, "signal_count": len(signals), "long_signals": long_signals, "short_signals": short_signals, "average_confidence": average_confidence, "weighted_strength": weighted_strength, "signals": signals}




