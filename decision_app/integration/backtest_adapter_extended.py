"""Extended adapter with 5 strategies for enhanced recommendations."""
import sys
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from one_trade.backtest import BacktestEngine
from one_trade.strategy import BaseStrategy
from one_trade.strategy_extended import RSIStrategy, BollingerBandsStrategy, MACDHistogramStrategy, ExtendedStrategyFactory
from config.models import Config
from decision_app.recommendation_engine.recommendation import RecommendationEngine, Recommendation


class ExtendedRecommendationAdapter:
    """Adapter with 5 strategies: Current, Baseline, RSI, Bollinger, MACD."""
    
    PRESET_WEIGHTS = {"balanced": {"CurrentStrategy": 0.25, "BaselineStrategy": 0.20, "RSIStrategy": 0.20, "BollingerStrategy": 0.20, "MACDStrategy": 0.15}, "conservative": {"CurrentStrategy": 0.30, "BaselineStrategy": 0.30, "RSIStrategy": 0.15, "BollingerStrategy": 0.15, "MACDStrategy": 0.10}, "aggressive": {"CurrentStrategy": 0.15, "BaselineStrategy": 0.10, "RSIStrategy": 0.25, "BollingerStrategy": 0.25, "MACDStrategy": 0.25}, "momentum_focused": {"CurrentStrategy": 0.20, "BaselineStrategy": 0.10, "RSIStrategy": 0.10, "BollingerStrategy": 0.20, "MACDStrategy": 0.40}, "trend_focused": {"CurrentStrategy": 0.35, "BaselineStrategy": 0.30, "RSIStrategy": 0.15, "BollingerStrategy": 0.10, "MACDStrategy": 0.10}}
    
    def __init__(self, config: Config, preset: str = "balanced", custom_weights: Optional[Dict[str, float]] = None, confidence_threshold: float = 0.6):
        """Initialize extended adapter."""
        self.config = config
        self.backtest_engine = BacktestEngine(config)
        strategies = self._initialize_strategies()
        if custom_weights:
            strategy_weights = custom_weights
        elif preset in self.PRESET_WEIGHTS:
            strategy_weights = self.PRESET_WEIGHTS[preset]
        else:
            strategy_weights = self.PRESET_WEIGHTS["balanced"]
        self.preset = preset
        self.strategy_weights = strategy_weights
        self.recommendation_engine = RecommendationEngine(strategies=strategies, strategy_weights=strategy_weights, confidence_threshold=confidence_threshold)
    
    def _initialize_strategies(self) -> List[BaseStrategy]:
        """Initialize all 5 strategies."""
        strategies = []
        current_config = self.config.strategy.current.model_dump()
        current_strategy = ExtendedStrategyFactory.create_strategy("current", current_config)
        current_strategy.name = "CurrentStrategy"
        strategies.append(current_strategy)
        baseline_config = self.config.strategy.baseline.model_dump()
        baseline_strategy = ExtendedStrategyFactory.create_strategy("baseline", baseline_config)
        baseline_strategy.name = "BaselineStrategy"
        strategies.append(baseline_strategy)
        rsi_config = {"indicators": {"rsi_period": 14, "rsi_oversold": 30, "rsi_overbought": 70, "rsi_extreme_oversold": 20, "rsi_extreme_overbought": 80}, "entry_conditions": {"detect_divergence": False}}
        rsi_strategy = ExtendedStrategyFactory.create_strategy("rsi", rsi_config)
        rsi_strategy.name = "RSIStrategy"
        strategies.append(rsi_strategy)
        bollinger_config = {"indicators": {"bb_period": 20, "bb_std": 2.0}, "entry_conditions": {"require_squeeze": False}}
        bollinger_strategy = ExtendedStrategyFactory.create_strategy("bollinger", bollinger_config)
        bollinger_strategy.name = "BollingerStrategy"
        strategies.append(bollinger_strategy)
        macd_config = {"indicators": {"macd_fast": 12, "macd_slow": 26, "macd_signal": 9}, "entry_conditions": {"require_increasing": True}}
        macd_strategy = ExtendedStrategyFactory.create_strategy("macd_histogram", macd_config)
        macd_strategy.name = "MACDStrategy"
        strategies.append(macd_strategy)
        return strategies
    
    def generate_daily_recommendations(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate daily recommendations for historical period."""
        data_15m, _ = self.backtest_engine.data_store.read_data_filtered(symbol, "15m", start_date, end_date)
        if data_15m is None or data_15m.empty:
            raise ValueError(f"No data available for {symbol} from {start_date} to {end_date}")
        data_15m = data_15m.sort_values("timestamp_utc").set_index("timestamp_utc")
        daily_recommendations = []
        warmup_periods = self.config.backtest.warmup_periods
        last_date = None
        for idx in range(warmup_periods, len(data_15m)):
            current_timestamp = data_15m.index[idx]
            current_date = current_timestamp.date()
            if last_date is not None and current_date <= last_date:
                continue
            recommendation = self.recommendation_engine.generate_recommendation(symbol, data_15m, idx)
            daily_recommendations.append({"date": current_date, "timestamp": current_timestamp, "symbol": recommendation.symbol, "action": recommendation.action.value, "confidence": recommendation.confidence, "entry_price": recommendation.entry_price, "stop_loss": recommendation.stop_loss, "take_profit": recommendation.take_profit, "reasoning": recommendation.reasoning, "invalidation_condition": recommendation.invalidation_condition, "supporting_signals_count": len(recommendation.supporting_signals), "preset": self.preset})
            last_date = current_date
        return pd.DataFrame(daily_recommendations)
    
    def get_latest_recommendation(self, symbol: str) -> Recommendation:
        """Get latest recommendation for a symbol."""
        data_15m, _ = self.backtest_engine.data_store.read_data(symbol, "15m")
        if data_15m is None or data_15m.empty:
            raise ValueError(f"No data available for {symbol}")
        data_15m = data_15m.sort_values("timestamp_utc").set_index("timestamp_utc")
        current_idx = len(data_15m) - 1
        recommendation = self.recommendation_engine.generate_recommendation(symbol, data_15m, current_idx)
        return recommendation
    
    def compare_presets(self, symbol: str, start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """Compare recommendations from different weight presets."""
        results = {}
        for preset_name in self.PRESET_WEIGHTS.keys():
            temp_adapter = ExtendedRecommendationAdapter(config=self.config, preset=preset_name, confidence_threshold=0.6)
            try:
                df = temp_adapter.generate_daily_recommendations(symbol, start_date, end_date)
                results[preset_name] = df
            except Exception as e:
                print(f"Error with preset {preset_name}: {e}")
        return results
    
    def get_preset_info(self) -> Dict:
        """Get information about current preset."""
        return {"preset": self.preset, "weights": self.strategy_weights, "strategies": list(self.strategy_weights.keys()), "confidence_threshold": self.recommendation_engine.confidence_threshold}

