"""
Signal consolidation service for combining multiple strategy signals.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from enum import Enum

from app.strategies.base_strategy import Signal, SignalType
from app.services.strategy_service import strategy_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class RecommendationType(str, Enum):
    """Final recommendation types."""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class SignalConsolidator:
    """Service for consolidating signals from multiple strategies."""
    
    def __init__(self):
        """Initialize the signal consolidator."""
        self.strategy_weights = {
            "RSI Strategy": 0.4,  # 40% weight
            "MACD Strategy": 0.4,  # 40% weight
            "Bollinger Bands Strategy": 0.2,  # 20% weight
        }
        
        # Confidence thresholds for final recommendations
        self.confidence_thresholds = {
            RecommendationType.STRONG_BUY: 0.85,
            RecommendationType.BUY: 0.65,
            RecommendationType.HOLD: 0.35,
            RecommendationType.SELL: 0.65,
            RecommendationType.STRONG_SELL: 0.85,
        }
    
    def consolidate_signals(
        self, 
        strategy_signals: Dict[str, List[Signal]],
        current_price: float,
        symbol: str = "BTCUSDT"
    ) -> Dict[str, Any]:
        """
        Consolidate signals from multiple strategies into a final recommendation.
        
        Args:
            strategy_signals: Dictionary mapping strategy names to their signals
            current_price: Current market price
            symbol: Trading symbol
            
        Returns:
            Consolidated recommendation with reasoning
        """
        try:
            # Calculate weighted scores for each signal type
            buy_score = 0.0
            sell_score = 0.0
            hold_score = 0.0
            
            signal_details = []
            total_weight = 0.0
            
            for strategy_name, signals in strategy_signals.items():
                if not signals:
                    continue
                
                weight = self.strategy_weights.get(strategy_name, 0.0)
                if weight == 0:
                    continue
                
                # Get the latest signal from this strategy
                latest_signal = signals[-1]
                
                # Calculate weighted contribution
                if latest_signal.signal == SignalType.BUY:
                    buy_score += weight * latest_signal.confidence
                elif latest_signal.signal == SignalType.SELL:
                    sell_score += weight * latest_signal.confidence
                else:  # HOLD
                    hold_score += weight * latest_signal.confidence
                
                total_weight += weight
                
                signal_details.append({
                    "strategy": strategy_name,
                    "signal": latest_signal.signal.value,
                    "confidence": latest_signal.confidence,
                    "weight": weight,
                    "reasoning": latest_signal.reasoning,
                    "timestamp": latest_signal.timestamp.isoformat()
                })
            
            # Normalize scores
            if total_weight > 0:
                buy_score /= total_weight
                sell_score /= total_weight
                hold_score /= total_weight
            
            # Determine final recommendation
            final_recommendation = self._determine_final_recommendation(
                buy_score, sell_score, hold_score
            )
            
            # Calculate overall confidence
            overall_confidence = max(buy_score, sell_score, hold_score)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                signal_details, buy_score, sell_score, hold_score
            )
            
            # Calculate risk assessment
            risk_assessment = self._assess_risk(signal_details, overall_confidence)
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "recommendation": final_recommendation.value,
                "confidence": round(overall_confidence, 3),
                "reasoning": reasoning,
                "risk_assessment": risk_assessment,
                "strategy_signals": signal_details,
                "scores": {
                    "buy_score": round(buy_score, 3),
                    "sell_score": round(sell_score, 3),
                    "hold_score": round(hold_score, 3)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error consolidating signals: {e}")
            raise
    
    def _determine_final_recommendation(
        self, 
        buy_score: float, 
        sell_score: float, 
        hold_score: float
    ) -> RecommendationType:
        """Determine final recommendation based on scores."""
        
        max_score = max(buy_score, sell_score, hold_score)
        
        if max_score < 0.3:
            return RecommendationType.HOLD
        
        if buy_score == max_score:
            if buy_score >= self.confidence_thresholds[RecommendationType.STRONG_BUY]:
                return RecommendationType.STRONG_BUY
            elif buy_score >= self.confidence_thresholds[RecommendationType.BUY]:
                return RecommendationType.BUY
            else:
                return RecommendationType.HOLD
        
        elif sell_score == max_score:
            if sell_score >= self.confidence_thresholds[RecommendationType.STRONG_SELL]:
                return RecommendationType.STRONG_SELL
            elif sell_score >= self.confidence_thresholds[RecommendationType.SELL]:
                return RecommendationType.SELL
            else:
                return RecommendationType.HOLD
        
        else:
            return RecommendationType.HOLD
    
    def _generate_reasoning(
        self, 
        signal_details: List[Dict], 
        buy_score: float, 
        sell_score: float, 
        hold_score: float
    ) -> str:
        """Generate human-readable reasoning for the recommendation."""
        
        reasoning_parts = []
        
        # Add strategy-specific reasoning
        for signal in signal_details:
            if signal["confidence"] > 0.6:  # Only include high-confidence signals
                reasoning_parts.append(
                    f"{signal['strategy']}: {signal['signal']} "
                    f"({signal['confidence']:.1%} confidence) - {signal['reasoning']}"
                )
        
        # Add overall assessment
        if buy_score > sell_score and buy_score > hold_score:
            reasoning_parts.append(
                f"Overall assessment: BUY signals dominate with {buy_score:.1%} weighted score"
            )
        elif sell_score > buy_score and sell_score > hold_score:
            reasoning_parts.append(
                f"Overall assessment: SELL signals dominate with {sell_score:.1%} weighted score"
            )
        else:
            reasoning_parts.append(
                f"Overall assessment: Mixed signals, recommending HOLD with {hold_score:.1%} weighted score"
            )
        
        return " | ".join(reasoning_parts)
    
    def _assess_risk(
        self, 
        signal_details: List[Dict], 
        overall_confidence: float
    ) -> Dict[str, Any]:
        """Assess risk level based on signal consistency and confidence."""
        
        if not signal_details:
            return {"level": "UNKNOWN", "factors": ["No signals available"]}
        
        # Count signal types
        signal_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
        for signal in signal_details:
            signal_counts[signal["signal"]] += 1
        
        # Calculate consistency
        total_signals = len(signal_details)
        max_signals = max(signal_counts.values())
        consistency = max_signals / total_signals if total_signals > 0 else 0
        
        # Determine risk level
        if overall_confidence >= 0.8 and consistency >= 0.7:
            risk_level = "LOW"
        elif overall_confidence >= 0.6 and consistency >= 0.5:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Identify risk factors
        risk_factors = []
        if consistency < 0.5:
            risk_factors.append("Conflicting signals between strategies")
        if overall_confidence < 0.6:
            risk_factors.append("Low overall confidence")
        if total_signals < 2:
            risk_factors.append("Limited strategy coverage")
        
        return {
            "level": risk_level,
            "consistency": round(consistency, 3),
            "signal_distribution": signal_counts,
            "factors": risk_factors if risk_factors else ["No significant risk factors identified"]
        }
    
    def update_strategy_weights(self, new_weights: Dict[str, float]) -> None:
        """Update strategy weights dynamically."""
        self.strategy_weights.update(new_weights)
        logger.info(f"Updated strategy weights: {self.strategy_weights}")
    
    def get_strategy_weights(self) -> Dict[str, float]:
        """Get current strategy weights."""
        return self.strategy_weights.copy()


# Global signal consolidator instance
signal_consolidator = SignalConsolidator()
