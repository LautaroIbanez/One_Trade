"""Unit tests for Recommendation Engine components."""
import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from one_trade.strategy import CurrentStrategy, BaselineStrategy, Signal
from decision_app.recommendation_engine.recommendation import RecommendationEngine, RecommendationAction, StrategySignal
from decision_app.recommendation_engine.condenser import SignalCondenser
from decision_app.recommendation_engine.decisor import DecisionGenerator
from decision_app.recommendation_engine.explainer import ExplainabilityModule


@pytest.fixture
def sample_ohlcv_data():
    """Generate sample OHLCV data for testing."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="15min", tz=timezone.utc)
    np.random.seed(42)
    close_prices = 50000 + np.cumsum(np.random.randn(100) * 100)
    data = pd.DataFrame({"timestamp_utc": dates, "open": close_prices + np.random.randn(100) * 50, "high": close_prices + np.abs(np.random.randn(100)) * 100, "low": close_prices - np.abs(np.random.randn(100)) * 100, "close": close_prices, "volume": np.random.randint(100, 1000, 100)})
    data = data.set_index("timestamp_utc")
    return data


@pytest.fixture
def sample_strategies():
    """Create sample strategies for testing."""
    current_config = {"indicators": {"ema_fast": 12, "ema_slow": 26, "rsi_period": 14}, "entry_conditions": {"require_ema_cross": True, "require_rsi_confirmation": True, "require_macd_confirmation": True}}
    baseline_config = {"indicators": {"ema_period": 50, "rsi_period": 14}, "entry_conditions": {"price_above_ema": True, "rsi_range": True}}
    current_strategy = CurrentStrategy(current_config)
    current_strategy.name = "CurrentStrategy"
    baseline_strategy = BaselineStrategy(baseline_config)
    baseline_strategy.name = "BaselineStrategy"
    return [current_strategy, baseline_strategy]


class TestSignalCondenser:
    """Test SignalCondenser functionality."""
    
    def test_condense_empty_signals(self):
        """Test condensing with no signals."""
        condenser = SignalCondenser(strategy_weights={"Strategy_A": 0.6, "Strategy_B": 0.4})
        result = condenser.condense_signals([])
        assert result["signal_count"] == 0
        assert result["aggregated_strength"] == 0.0
    
    def test_condense_single_long_signal(self):
        """Test condensing single long signal."""
        condenser = SignalCondenser(strategy_weights={"Strategy_A": 1.0})
        signal = StrategySignal(strategy_name="Strategy_A", signal_type="long", strength=1.0, details={"confidence": 0.8}, timestamp=datetime.now(timezone.utc))
        result = condenser.condense_signals([signal])
        assert result["signal_count"] == 1
        assert result["long_signals"] == 1
        assert result["short_signals"] == 0
        assert result["aggregated_strength"] > 0
    
    def test_condense_multiple_signals_same_direction(self):
        """Test condensing multiple signals in same direction."""
        condenser = SignalCondenser(strategy_weights={"Strategy_A": 0.6, "Strategy_B": 0.4})
        signal1 = StrategySignal(strategy_name="Strategy_A", signal_type="long", strength=1.0, details={"confidence": 0.8}, timestamp=datetime.now(timezone.utc))
        signal2 = StrategySignal(strategy_name="Strategy_B", signal_type="long", strength=1.0, details={"confidence": 0.9}, timestamp=datetime.now(timezone.utc))
        result = condenser.condense_signals([signal1, signal2])
        assert result["signal_count"] == 2
        assert result["long_signals"] == 2
        assert result["aggregated_strength"] > 0
    
    def test_condense_conflicting_signals(self):
        """Test condensing conflicting long and short signals."""
        condenser = SignalCondenser(strategy_weights={"Strategy_A": 0.5, "Strategy_B": 0.5})
        signal1 = StrategySignal(strategy_name="Strategy_A", signal_type="long", strength=1.0, details={"confidence": 0.8}, timestamp=datetime.now(timezone.utc))
        signal2 = StrategySignal(strategy_name="Strategy_B", signal_type="short", strength=-1.0, details={"confidence": 0.8}, timestamp=datetime.now(timezone.utc))
        result = condenser.condense_signals([signal1, signal2])
        assert result["signal_count"] == 2
        assert result["long_signals"] == 1
        assert result["short_signals"] == 1
        assert abs(result["aggregated_strength"]) < 0.3


class TestDecisionGenerator:
    """Test DecisionGenerator functionality."""
    
    def test_generate_decision_no_signals(self, sample_ohlcv_data):
        """Test decision generation with no signals."""
        decisor = DecisionGenerator(confidence_threshold=0.6)
        aggregated_signal = {"aggregated_strength": 0.0, "signal_count": 0, "long_signals": 0, "short_signals": 0, "average_confidence": 0.0}
        decision = decisor.generate_decision(aggregated_signal, sample_ohlcv_data, 50)
        assert decision["action"] == RecommendationAction.HOLD
        assert decision["confidence"] == 0.0
    
    def test_generate_decision_strong_long(self, sample_ohlcv_data):
        """Test decision generation with strong long signal."""
        decisor = DecisionGenerator(confidence_threshold=0.6)
        aggregated_signal = {"aggregated_strength": 0.85, "signal_count": 2, "long_signals": 2, "short_signals": 0, "average_confidence": 0.9}
        decision = decisor.generate_decision(aggregated_signal, sample_ohlcv_data, 50)
        assert decision["action"] == RecommendationAction.BUY
        assert decision["confidence"] >= 0.6
        assert decision["entry_price"] > 0
        assert decision["stop_loss"] < decision["entry_price"]
        assert decision["take_profit"] > decision["entry_price"]
    
    def test_generate_decision_weak_signal_holds(self, sample_ohlcv_data):
        """Test decision generation with weak signal results in HOLD."""
        decisor = DecisionGenerator(confidence_threshold=0.6)
        aggregated_signal = {"aggregated_strength": 0.3, "signal_count": 1, "long_signals": 1, "short_signals": 0, "average_confidence": 0.5}
        decision = decisor.generate_decision(aggregated_signal, sample_ohlcv_data, 50)
        assert decision["action"] == RecommendationAction.HOLD


class TestExplainabilityModule:
    """Test ExplainabilityModule functionality."""
    
    def test_explain_hold_no_signals(self, sample_ohlcv_data):
        """Test explanation for HOLD with no signals."""
        explainer = ExplainabilityModule()
        decision = {"action": RecommendationAction.HOLD, "confidence": 0.0, "signal_count": 0}
        explanation = explainer.explain(decision, [], sample_ohlcv_data, 50)
        assert "No hay señales" in explanation["reasoning"]
        assert explanation["invalidation"] == ""
    
    def test_explain_buy(self, sample_ohlcv_data):
        """Test explanation for BUY decision."""
        explainer = ExplainabilityModule()
        decision = {"action": RecommendationAction.BUY, "confidence": 0.75, "signal_count": 2, "long_signals": 2, "short_signals": 0, "entry_price": 50000.0, "stop_loss": 49000.0}
        signal = StrategySignal(strategy_name="TestStrategy", signal_type="long", strength=1.0, details={"reason": "EMA_CROSS_LONG"}, timestamp=datetime.now(timezone.utc))
        explanation = explainer.explain(decision, [signal], sample_ohlcv_data, 50)
        assert "alcista" in explanation["reasoning"].lower()
        assert "Invalidar" in explanation["invalidation"]


class TestRecommendationEngine:
    """Test full RecommendationEngine integration."""
    
    def test_generate_recommendation_with_real_strategies(self, sample_ohlcv_data, sample_strategies):
        """Test recommendation generation with real strategies."""
        engine = RecommendationEngine(strategies=sample_strategies, strategy_weights={"CurrentStrategy": 0.6, "BaselineStrategy": 0.4}, confidence_threshold=0.6)
        recommendation = engine.generate_recommendation(symbol="BTC/USDT", data=sample_ohlcv_data.reset_index(drop=True), current_idx=70)
        assert recommendation.symbol == "BTC/USDT"
        assert recommendation.action in [RecommendationAction.BUY, RecommendationAction.SELL, RecommendationAction.HOLD]
        assert 0.0 <= recommendation.confidence <= 1.0
        assert len(recommendation.reasoning) > 0
    
    def test_recommendation_consistency(self, sample_ohlcv_data, sample_strategies):
        """Test that same data produces same recommendation."""
        engine = RecommendationEngine(strategies=sample_strategies, strategy_weights={"CurrentStrategy": 0.6, "BaselineStrategy": 0.4})
        rec1 = engine.generate_recommendation(symbol="BTC/USDT", data=sample_ohlcv_data.reset_index(drop=True), current_idx=70)
        rec2 = engine.generate_recommendation(symbol="BTC/USDT", data=sample_ohlcv_data.reset_index(drop=True), current_idx=70)
        assert rec1.action == rec2.action
        assert rec1.confidence == rec2.confidence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




