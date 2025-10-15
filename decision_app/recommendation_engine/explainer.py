"""Explainability Module - Generates human-readable explanations."""
from typing import Dict, List
import pandas as pd
from decision_app.recommendation_engine.recommendation import RecommendationAction


class ExplainabilityModule:
    """Generates natural language explanations for recommendations."""
    
    def __init__(self):
        """Initialize ExplainabilityModule."""
        pass
    
    def explain(self, decision: Dict, strategy_signals: List, data: pd.DataFrame, current_idx: int) -> Dict:
        """Generate explanation for a decision. Args: decision: Decision dict from DecisionGenerator. strategy_signals: List of StrategySignal objects. data: OHLCV DataFrame. current_idx: Current position. Returns: Dict with 'reasoning' and 'invalidation' strings."""
        action = decision["action"]
        confidence = decision["confidence"]
        signal_count = decision.get("signal_count", 0)
        long_signals = decision.get("long_signals", 0)
        short_signals = decision.get("short_signals", 0)
        if action == RecommendationAction.HOLD: reasoning = self._explain_hold(signal_count, long_signals, short_signals, confidence)
        elif action == RecommendationAction.BUY: reasoning = self._explain_buy(long_signals, short_signals, confidence, strategy_signals, data, current_idx)
        else: reasoning = self._explain_sell(long_signals, short_signals, confidence, strategy_signals, data, current_idx)
        invalidation = self._generate_invalidation(action, decision, data, current_idx)
        return {"reasoning": reasoning, "invalidation": invalidation}
    
    def _explain_hold(self, signal_count: int, long_signals: int, short_signals: int, confidence: float) -> str:
        """Generate explanation for HOLD decision."""
        if signal_count == 0: return "No hay señales activas de ninguna estrategia. El mercado no presenta condiciones claras para operar. Es recomendable esperar."
        if long_signals > 0 and short_signals > 0: return f"Señales mixtas detectadas ({long_signals} alcistas, {short_signals} bajistas). La falta de consenso sugiere esperar mayor claridad antes de operar."
        return f"Señales detectadas pero con confianza insuficiente ({confidence:.1%}). Es mejor esperar señales más fuertes y confirmadas."
    
    def _explain_buy(self, long_signals: int, short_signals: int, confidence: float, strategy_signals: List, data: pd.DataFrame, current_idx: int) -> str:
        """Generate explanation for BUY decision."""
        current_bar = data.iloc[current_idx]
        price = current_bar["close"]
        reasons = []
        for signal in strategy_signals:
            if signal.signal_type == "long": reasons.append(signal.details.get("reason", "").replace("_", " ").title())
        reason_text = ", ".join(set(reasons[:3])) if reasons else "Tendencia alcista"
        market_context = self._get_market_context(data, current_idx)
        explanation = f"Tendencia alcista confirmada por {long_signals} estrategia(s). {reason_text}. {market_context}"
        if short_signals > 0: explanation += f" Nota: {short_signals} estrategia(s) muestran señales bajistas, pero la mayoría sugiere compra."
        return explanation
    
    def _explain_sell(self, long_signals: int, short_signals: int, confidence: float, strategy_signals: List, data: pd.DataFrame, current_idx: int) -> str:
        """Generate explanation for SELL decision."""
        current_bar = data.iloc[current_idx]
        price = current_bar["close"]
        reasons = []
        for signal in strategy_signals:
            if signal.signal_type == "short": reasons.append(signal.details.get("reason", "").replace("_", " ").title())
        reason_text = ", ".join(set(reasons[:3])) if reasons else "Tendencia bajista"
        market_context = self._get_market_context(data, current_idx)
        explanation = f"Tendencia bajista confirmada por {short_signals} estrategia(s). {reason_text}. {market_context}"
        if long_signals > 0: explanation += f" Nota: {long_signals} estrategia(s) muestran señales alcistas, pero la mayoría sugiere venta."
        return explanation
    
    def _get_market_context(self, data: pd.DataFrame, current_idx: int) -> str:
        """Get additional market context (volume, volatility)."""
        if current_idx < 5: return ""
        recent_data = data.iloc[max(0, current_idx - 20):current_idx + 1]
        current_volume = data.iloc[current_idx]["volume"]
        avg_volume = recent_data["volume"].mean()
        volume_change = ((current_volume / avg_volume) - 1) * 100 if avg_volume > 0 else 0
        context_parts = []
        if abs(volume_change) > 20:
            if volume_change > 0: context_parts.append(f"Volumen creciente (+{volume_change:.0f}%)")
            else: context_parts.append(f"Volumen decreciente ({volume_change:.0f}%)")
        price_change = ((data.iloc[current_idx]["close"] / data.iloc[max(0, current_idx - 5)]["close"]) - 1) * 100
        if abs(price_change) > 3: context_parts.append(f"Precio {'subió' if price_change > 0 else 'bajó'} {abs(price_change):.1f}% en últimas 5 velas")
        return ". ".join(context_parts) if context_parts else ""
    
    def _generate_invalidation(self, action: RecommendationAction, decision: Dict, data: pd.DataFrame, current_idx: int) -> str:
        """Generate invalidation condition for the recommendation."""
        if action == RecommendationAction.HOLD: return ""
        stop_loss = decision.get("stop_loss")
        entry_price = decision.get("entry_price")
        if stop_loss is None or entry_price is None: return ""
        if action == RecommendationAction.BUY: return f"Invalidar si el precio cae por debajo de ${stop_loss:.2f} (pérdida máxima aceptable)"
        else: return f"Invalidar si el precio sube por encima de ${stop_loss:.2f} (pérdida máxima aceptable)"




