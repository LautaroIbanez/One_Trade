import { useState, useEffect } from 'react'; import { EnhancedRecommendation, StrategySignal, RiskAssessment, MarketContext, SignalScores } from '../types/recommendations'; const MOCK_MODE = true; const MOCK_DELAY = 1000; const UPDATE_INTERVAL = 5000; const mockSymbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']; const mockPrices: Record<string, number> = { BTCUSDT: 45000, ETHUSDT: 3200, ADAUSDT: 0.45, SOLUSDT: 180, BNBUSDT: 320, XRPUSDT: 0.52 }; const mockRecommendations = { BTCUSDT: { recommendation: 'BUY', confidence: 0.75, details: { strategy: 'RSI + MACD', indicators: { rsi: 45.2, macd: 0.001, bollinger_position: 0.6 } } }, ETHUSDT: { recommendation: 'HOLD', confidence: 0.65, details: { strategy: 'MACD', indicators: { rsi: 52.1, macd: -0.002, bollinger_position: 0.4 } } }, ADAUSDT: { recommendation: 'SELL', confidence: 0.55, details: { strategy: 'Bollinger Bands', indicators: { rsi: 68.3, macd: -0.005, bollinger_position: 0.8 } } }, SOLUSDT: { recommendation: 'BUY', confidence: 0.70, details: { strategy: 'RSI', indicators: { rsi: 38.9, macd: 0.003, bollinger_position: 0.3 } } }, BNBUSDT: { recommendation: 'HOLD', confidence: 0.60, details: { strategy: 'MACD', indicators: { rsi: 48.7, macd: 0.000, bollinger_position: 0.5 } } }, XRPUSDT: { recommendation: 'BUY', confidence: 0.68, details: { strategy: 'RSI + Bollinger', indicators: { rsi: 42.5, macd: 0.002, bollinger_position: 0.35 } } } };

const mockStats = {
  totalTrades: 156,
  winRate: 0.68,
  totalReturn: 0.15,
  sharpeRatio: 1.8,
  maxDrawdown: 0.08,
  avgTradeDuration: 2.5,
  profitFactor: 1.45
};

const mockMarketData = {
  BTCUSDT: { price: 45000, change: 0.025, volume: 1250000 },
  ETHUSDT: { price: 3200, change: -0.015, volume: 890000 },
  ADAUSDT: { price: 0.45, change: 0.035, volume: 2100000 },
  SOLUSDT: { price: 180, change: 0.012, volume: 450000 },
  BNBUSDT: { price: 320, change: -0.008, volume: 670000 },
  XRPUSDT: { price: 0.52, change: 0.018, volume: 980000 }
};

// Hook for mock data
export const useMockData = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Simulate API call delay
  const simulateDelay = (ms: number = MOCK_DELAY) => {
    return new Promise(resolve => setTimeout(resolve, ms));
  };

  // Get supported symbols
  const getSupportedSymbols = async (): Promise<string[]> => {
    if (!MOCK_MODE) {
      // Real API call would go here
      const response = await fetch('/api/v1/enhanced-recommendations/supported-symbols');
      return response.json();
    }
    
    setIsLoading(true);
    await simulateDelay();
    setIsLoading(false);
    setLastUpdated(new Date());
    return mockSymbols;
  };

  const getRecommendation = async (symbol: string, timeframe: string = '1d', days: number = 30): Promise<EnhancedRecommendation> => { if (!MOCK_MODE) { const response = await fetch(`/api/v1/enhanced-recommendations/generate/${symbol}?timeframe=${timeframe}&days=${days}`); return response.json(); } setIsLoading(true); await simulateDelay(); setIsLoading(false); setLastUpdated(new Date()); const symbolUpper = symbol.toUpperCase(); const mockData = mockRecommendations[symbolUpper] || { recommendation: 'HOLD', confidence: 0.60, details: { strategy: 'Default', indicators: { rsi: 50, macd: 0, bollinger_position: 0.5 } } }; const basePrice = mockPrices[symbolUpper] || 100; const priceVariation = (Math.random() - 0.5) * 0.02; const currentPrice = basePrice * (1 + priceVariation); const riskLevel = mockData.confidence > 0.7 ? 'LOW' : mockData.confidence > 0.5 ? 'MEDIUM' : 'HIGH'; const scores: SignalScores = { buy_score: mockData.recommendation === 'BUY' ? mockData.confidence : (1 - mockData.confidence) / 2, sell_score: mockData.recommendation === 'SELL' ? mockData.confidence : (1 - mockData.confidence) / 2, hold_score: mockData.recommendation === 'HOLD' ? mockData.confidence : (1 - mockData.confidence) / 2 }; const riskAssessment: RiskAssessment = { level: riskLevel, consistency: mockData.confidence, signal_distribution: { [mockData.recommendation]: 1.0 }, factors: ['Mock volatility analysis', 'Mock trend confirmation', 'Mock volume pattern'] }; const marketContext: MarketContext = { trend: mockData.recommendation === 'BUY' ? 'BULLISH' : mockData.recommendation === 'SELL' ? 'BEARISH' : 'NEUTRAL', volatility: mockData.details.indicators.bollinger_position > 0.7 ? 'HIGH' : mockData.details.indicators.bollinger_position < 0.3 ? 'LOW' : 'MEDIUM', recent_performance: { day_1: (Math.random() - 0.5) * 0.1, day_7: (Math.random() - 0.5) * 0.2, volatility: Math.random() * 0.1 }, market_activity: { volume_24h: Math.random() * 1000000, price_momentum: Math.random() * 0.1, trades_24h: Math.floor(Math.random() * 50000) } }; const strategySignal: StrategySignal = { strategy: mockData.details.strategy, signal: mockData.recommendation, confidence: mockData.confidence, weight: 1.0, reasoning: `${mockData.details.strategy} indicator suggests ${mockData.recommendation.toLowerCase()} based on RSI: ${mockData.details.indicators.rsi.toFixed(1)}, MACD: ${mockData.details.indicators.macd.toFixed(4)}`, timestamp: new Date().toISOString() }; const reasoning = `Based on ${mockData.details.strategy} analysis with ${(mockData.confidence * 100).toFixed(1)}% confidence. Current RSI at ${mockData.details.indicators.rsi.toFixed(1)} indicates ${mockData.details.indicators.rsi > 70 ? 'overbought' : mockData.details.indicators.rsi < 30 ? 'oversold' : 'neutral'} conditions. MACD momentum is ${mockData.details.indicators.macd > 0 ? 'positive' : 'negative'}.`; return { symbol: symbolUpper, current_price: currentPrice, recommendation: mockData.recommendation, confidence: mockData.confidence, reasoning, risk_assessment: riskAssessment, strategy_signals: [strategySignal], scores, market_context: marketContext, timestamp: new Date().toISOString() }; };

  // Get statistics
  const getStats = async () => {
    if (!MOCK_MODE) {
      // Real API call would go here
      const response = await fetch('/api/v1/stats');
      return response.json();
    }

    setIsLoading(true);
    await simulateDelay();
    setIsLoading(false);
    setLastUpdated(new Date());

    // Add some randomness to make it feel real
    return {
      ...mockStats,
      totalTrades: mockStats.totalTrades + Math.floor(Math.random() * 5),
      winRate: mockStats.winRate + (Math.random() - 0.5) * 0.02,
      totalReturn: mockStats.totalReturn + (Math.random() - 0.5) * 0.01,
      sharpeRatio: mockStats.sharpeRatio + (Math.random() - 0.5) * 0.1
    };
  };

  // Get market data
  const getMarketData = async (symbol: string) => {
    if (!MOCK_MODE) {
      // Real API call would go here
      const response = await fetch(`/api/v1/market-data/${symbol}`);
      return response.json();
    }

    setIsLoading(true);
    await simulateDelay();
    setIsLoading(false);
    setLastUpdated(new Date());

    const symbolUpper = symbol.toUpperCase();
    const mockData = mockMarketData[symbolUpper] || {
      price: 100,
      change: 0,
      volume: 100000
    };

    return {
      symbol: symbolUpper,
      price: mockData.price,
      change: mockData.change,
      volume: mockData.volume,
      timestamp: new Date().toISOString()
    };
  };

  // Auto-update data
  useEffect(() => {
    if (MOCK_MODE) {
      const interval = setInterval(() => {
        setLastUpdated(new Date());
      }, UPDATE_INTERVAL);

      return () => clearInterval(interval);
    }
  }, []);

  return {
    MOCK_MODE,
    isLoading,
    lastUpdated,
    getSupportedSymbols,
    getRecommendation,
    getStats,
    getMarketData,
    mockSymbols,
    mockRecommendations,
    mockStats,
    mockMarketData
  };
};

// Export configuration
export const MOCK_CONFIG = {
  MOCK_MODE,
  MOCK_DELAY,
  UPDATE_INTERVAL,
  API_BASE_URL: 'http://localhost:8000'
};
