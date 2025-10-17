export interface StrategySignal {
  strategy: string;
  signal: string;
  confidence: number;
  weight: number;
  reasoning: string;
  timestamp: string;
}

export interface RiskAssessment {
  level: 'LOW' | 'MEDIUM' | 'HIGH';
  consistency: number;
  signal_distribution: Record<string, number>;
  factors: string[];
}

export interface MarketContext {
  trend: string;
  volatility: string;
  recent_performance: {
    day_1: number;
    day_7: number;
    volatility: number;
  };
  market_activity: {
    volume_24h: number;
    trades_24h?: number;
    price_momentum?: number;
  };
}

export interface SignalScores {
  buy_score: number;
  sell_score: number;
  hold_score: number;
}

export interface EntryRange {
  min: number;
  max: number;
  confidence: number;
  methodology?: string;
}

export interface TradingLevels {
  entry_long?: EntryRange;
  entry_short?: EntryRange;
  take_profit_long?: number;
  stop_loss_long?: number;
  take_profit_short?: number;
  stop_loss_short?: number;
  atr?: number;
  support_level?: number;
  resistance_level?: number;
  calculation_note?: string;
}

export interface EnhancedRecommendation {
  symbol: string;
  current_price: number;
  recommendation: string;
  confidence: number;
  reasoning: string;
  risk_assessment: RiskAssessment;
  strategy_signals: StrategySignal[];
  scores: SignalScores;
  market_context: MarketContext;
  trading_levels?: TradingLevels;
  entry_price?: number;
  take_profit_targets?: number[];
  stop_loss?: number;
  timestamp: string;
  error?: string;
}

export interface PriceDataPoint {
  timestamp: string;
  date: string;
  price: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  signal?: 'BUY' | 'SELL' | null;
}

export interface ChartData {
  symbol: string;
  timeframe: string;
  data_points: number;
  data: PriceDataPoint[];
  current_price?: number;
  trading_levels?: TradingLevels;
}

export const DEFAULT_RISK_ASSESSMENT: RiskAssessment = {
  level: 'MEDIUM',
  consistency: 0.5,
  signal_distribution: {},
  factors: []
};

export const DEFAULT_MARKET_CONTEXT: MarketContext = {
  trend: 'NEUTRAL',
  volatility: 'MEDIUM',
  recent_performance: {
    day_1: 0,
    day_7: 0,
    volatility: 0
  },
  market_activity: {
    volume_24h: 0
  }
};

export const DEFAULT_SCORES: SignalScores = {
  buy_score: 0.33,
  sell_score: 0.33,
  hold_score: 0.34
};
