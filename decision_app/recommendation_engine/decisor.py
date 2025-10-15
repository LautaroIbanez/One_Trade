"""Decision Generator - Converts aggregated signals into actionable decisions."""
from typing import Dict
import pandas as pd
from decision_app.recommendation_engine.recommendation import RecommendationAction


class DecisionGenerator:
    """Generates trading decisions from aggregated signals."""
    
    def __init__(self, confidence_threshold: float = 0.6, strong_threshold: float = 0.75):
        """Initialize DecisionGenerator. Args: confidence_threshold: Minimum confidence for BUY/SELL (below this is HOLD). strong_threshold: Threshold for strong signals (affects confidence calculation)."""
        self.confidence_threshold = confidence_threshold
        self.strong_threshold = strong_threshold
    
    def generate_decision(self, aggregated_signal: Dict, data: pd.DataFrame, current_idx: int) -> Dict:
        """Generate decision from aggregated signal. Args: aggregated_signal: Output from SignalCondenser. data: OHLCV DataFrame. current_idx: Current position. Returns: Dict with action, confidence, and trade parameters."""
        aggregated_strength = aggregated_signal["aggregated_strength"]
        signal_count = aggregated_signal["signal_count"]
        long_signals = aggregated_signal["long_signals"]
        short_signals = aggregated_signal["short_signals"]
        avg_confidence = aggregated_signal["average_confidence"]
        if signal_count == 0: return {"action": RecommendationAction.HOLD, "confidence": 0.0}
        base_confidence = abs(aggregated_strength)
        consensus_factor = max(long_signals, short_signals) / signal_count
        final_confidence = (base_confidence * 0.6) + (consensus_factor * 0.4)
        final_confidence = min(final_confidence, 1.0)
        if final_confidence < self.confidence_threshold: action = RecommendationAction.HOLD
        elif aggregated_strength > 0: action = RecommendationAction.BUY
        else: action = RecommendationAction.SELL
        current_bar = data.iloc[current_idx]
        entry_price = float(current_bar["close"])
        atr = self._estimate_atr(data, current_idx)
        if action == RecommendationAction.BUY:
            stop_loss = entry_price - (atr * 2.0)
            take_profit = entry_price + (atr * 3.0)
        elif action == RecommendationAction.SELL:
            stop_loss = entry_price + (atr * 2.0)
            take_profit = entry_price - (atr * 3.0)
        else:
            stop_loss = None
            take_profit = None
        return {"action": action, "confidence": final_confidence, "entry_price": entry_price, "stop_loss": stop_loss, "take_profit": take_profit, "signal_count": signal_count, "long_signals": long_signals, "short_signals": short_signals, "aggregated_strength": aggregated_strength}
    
    def _estimate_atr(self, data: pd.DataFrame, current_idx: int, period: int = 14) -> float:
        """Estimate ATR for stop loss / take profit calculation."""
        if current_idx < period: period = max(1, current_idx)
        recent_data = data.iloc[max(0, current_idx - period):current_idx + 1]
        if len(recent_data) < 2: return float(data.iloc[current_idx]["close"]) * 0.02
        high = recent_data["high"]
        low = recent_data["low"]
        close = recent_data["close"]
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.mean()
        return float(atr) if pd.notna(atr) else float(data.iloc[current_idx]["close"]) * 0.02




