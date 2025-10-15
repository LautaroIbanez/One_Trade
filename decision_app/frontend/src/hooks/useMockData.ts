import { useState, useEffect } from 'react';

// Mock data configuration
const MOCK_MODE = true; // Set to false when backend is working
const MOCK_DELAY = 1000; // Simulate network delay
const UPDATE_INTERVAL = 5000; // Update every 5 seconds

// Mock data
const mockSymbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT'];

const mockRecommendations = {
  BTCUSDT: { 
    recommendation: 'BUY', 
    confidence: 0.75,
    details: {
      strategy: 'RSI + MACD',
      indicators: { rsi: 45.2, macd: 0.001, bollinger_position: 0.6 }
    }
  },
  ETHUSDT: { 
    recommendation: 'HOLD', 
    confidence: 0.65,
    details: {
      strategy: 'MACD',
      indicators: { rsi: 52.1, macd: -0.002, bollinger_position: 0.4 }
    }
  },
  ADAUSDT: { 
    recommendation: 'SELL', 
    confidence: 0.55,
    details: {
      strategy: 'Bollinger Bands',
      indicators: { rsi: 68.3, macd: -0.005, bollinger_position: 0.8 }
    }
  },
  SOLUSDT: { 
    recommendation: 'BUY', 
    confidence: 0.70,
    details: {
      strategy: 'RSI',
      indicators: { rsi: 38.9, macd: 0.003, bollinger_position: 0.3 }
    }
  },
  BNBUSDT: { 
    recommendation: 'HOLD', 
    confidence: 0.60,
    details: {
      strategy: 'MACD',
      indicators: { rsi: 48.7, macd: 0.000, bollinger_position: 0.5 }
    }
  },
  XRPUSDT: { 
    recommendation: 'BUY', 
    confidence: 0.68,
    details: {
      strategy: 'RSI + Bollinger',
      indicators: { rsi: 42.5, macd: 0.002, bollinger_position: 0.35 }
    }
  }
};

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

  // Get recommendation for a symbol
  const getRecommendation = async (symbol: string, timeframe: string = '1d', days: number = 30) => {
    if (!MOCK_MODE) {
      // Real API call would go here
      const response = await fetch(`/api/v1/enhanced-recommendations/generate/${symbol}?timeframe=${timeframe}&days=${days}`);
      return response.json();
    }

    setIsLoading(true);
    await simulateDelay();
    setIsLoading(false);
    setLastUpdated(new Date());

    const symbolUpper = symbol.toUpperCase();
    const mockData = mockRecommendations[symbolUpper] || {
      recommendation: 'HOLD',
      confidence: 0.60,
      details: {
        strategy: 'Default',
        indicators: { rsi: 50, macd: 0, bollinger_position: 0.5 }
      }
    };

    return {
      symbol: symbolUpper,
      recommendation: mockData.recommendation,
      confidence: mockData.confidence,
      timestamp: new Date().toISOString(),
      details: {
        timeframe,
        days,
        strategy: mockData.details.strategy,
        indicators: mockData.details.indicators
      }
    };
  };

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
