"""Adapter to integrate Recommendation Engine with One Trade v2.0 Backtester."""
import sys
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from one_trade.strategy import BaseStrategy, CurrentStrategy, BaselineStrategy
from one_trade.backtest import BacktestEngine
from config.models import Config
from decision_app.recommendation_engine.recommendation import RecommendationEngine, Recommendation


class RecommendationBacktestAdapter:
    """Adapts RecommendationEngine to work with One Trade v2.0 backtester."""
    
    def __init__(self, config: Config, strategy_weights: Optional[Dict[str, float]] = None):
        """Initialize adapter. Args: config: One Trade configuration. strategy_weights: Weights for each strategy in recommendation engine."""
        self.config = config
        self.backtest_engine = BacktestEngine(config)
        strategies = self._initialize_strategies()
        if strategy_weights is None:
            strategy_weights = {f"strategy_{i}": 1.0 for i in range(len(strategies))}
        self.recommendation_engine = RecommendationEngine(strategies=strategies, strategy_weights=strategy_weights, confidence_threshold=0.6)
    
    def _initialize_strategies(self) -> List[BaseStrategy]:
        """Initialize strategies from config."""
        strategies = []
        current_config = self.config.strategy.current.model_dump()
        current_strategy = CurrentStrategy(current_config)
        current_strategy.name = "CurrentStrategy"
        strategies.append(current_strategy)
        baseline_config = self.config.strategy.baseline.model_dump()
        baseline_strategy = BaselineStrategy(baseline_config)
        baseline_strategy.name = "BaselineStrategy"
        strategies.append(baseline_strategy)
        return strategies
    
    def generate_daily_recommendations(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate daily recommendations for historical period. Args: symbol: Trading symbol (e.g., 'BTC/USDT'). start_date: Start date (YYYY-MM-DD). end_date: End date (YYYY-MM-DD). Returns: DataFrame with daily recommendations."""
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
            daily_recommendations.append({"date": current_date, "timestamp": current_timestamp, "symbol": recommendation.symbol, "action": recommendation.action.value, "confidence": recommendation.confidence, "entry_price": recommendation.entry_price, "stop_loss": recommendation.stop_loss, "take_profit": recommendation.take_profit, "reasoning": recommendation.reasoning, "invalidation_condition": recommendation.invalidation_condition, "supporting_signals_count": len(recommendation.supporting_signals)})
            last_date = current_date
        return pd.DataFrame(daily_recommendations)
    
    def backtest_with_recommendations(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """Run backtest using recommendation engine instead of single strategy. Args: symbol: Trading symbol. start_date: Start date. end_date: End date. Returns: Backtest results dict."""
        recommendations_df = self.generate_daily_recommendations(symbol, start_date, end_date)
        results = self.backtest_engine.run_backtest(symbol, start_date, end_date)
        results["recommendations"] = recommendations_df
        return results
    
    def get_latest_recommendation(self, symbol: str) -> Recommendation:
        """Get latest recommendation for a symbol using most recent data. Args: symbol: Trading symbol. Returns: Recommendation object."""
        data_15m, _ = self.backtest_engine.data_store.read_data(symbol, "15m")
        if data_15m is None or data_15m.empty:
            raise ValueError(f"No data available for {symbol}")
        data_15m = data_15m.sort_values("timestamp_utc").set_index("timestamp_utc")
        current_idx = len(data_15m) - 1
        recommendation = self.recommendation_engine.generate_recommendation(symbol, data_15m, current_idx)
        return recommendation

