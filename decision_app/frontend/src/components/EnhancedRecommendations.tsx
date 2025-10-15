import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw, TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';
import { useMockData } from '../hooks/useMockData';

interface StrategySignal {
  strategy: string;
  signal: string;
  confidence: number;
  weight: number;
  reasoning: string;
  timestamp: string;
}

interface RiskAssessment {
  level: string;
  consistency: number;
  signal_distribution: Record<string, number>;
  factors: string[];
}

interface MarketContext {
  trend: string;
  volatility: string;
  recent_performance: {
    day_1: number;
    day_7: number;
    volatility: number;
  };
  market_activity: {
    volume_24h: number;
    trades_24h: number;
  };
}

interface EnhancedRecommendation {
  symbol: string;
  current_price: number;
  recommendation: string;
  confidence: number;
  reasoning: string;
  risk_assessment: RiskAssessment;
  strategy_signals: StrategySignal[];
  scores: {
    buy_score: number;
    sell_score: number;
    hold_score: number;
  };
  market_context: MarketContext;
  timestamp: string;
}

const EnhancedRecommendations: React.FC = () => {
  const { getRecommendation, getSupportedSymbols, MOCK_MODE } = useMockData();
  const [recommendations, setRecommendations] = useState<EnhancedRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      if (MOCK_MODE) {
        // Use mock data
        const symbols = await getSupportedSymbols();
        const mockRecommendations = [];
        
        for (const symbol of symbols.slice(0, 3)) { // Show first 3 symbols
          const mockRec = await getRecommendation(symbol, '1d', 30);
          mockRecommendations.push({
            symbol: mockRec.symbol,
            recommendation: mockRec.recommendation,
            confidence: mockRec.confidence,
            timestamp: mockRec.timestamp,
            strategy_signals: [
              {
                strategy: mockRec.details.strategy,
                signal: mockRec.recommendation,
                confidence: mockRec.confidence,
                weight: 1.0,
                reasoning: `Mock ${mockRec.details.strategy} signal`,
                timestamp: mockRec.timestamp
              }
            ],
            risk_assessment: {
              level: mockRec.confidence > 0.7 ? 'LOW' : mockRec.confidence > 0.5 ? 'MEDIUM' : 'HIGH',
              consistency: mockRec.confidence,
              signal_distribution: { [mockRec.recommendation]: 1.0 },
              factors: ['Mock volatility', 'Mock trend analysis']
            },
            market_context: {
              trend: 'BULLISH',
              volatility: 'MEDIUM',
              recent_performance: {
                day_1: (Math.random() - 0.5) * 0.1,
                day_7: (Math.random() - 0.5) * 0.2,
                volatility: Math.random() * 0.1
              },
              market_activity: {
                volume_24h: Math.random() * 1000000,
                price_momentum: Math.random() * 0.1
              }
            }
          });
        }
        
        setRecommendations(mockRecommendations);
      } else {
        // Real API calls (original code)
        const symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'];
        const promises = symbols.map(symbol => 
          fetch(`http://localhost:8000/api/v1/enhanced-recommendations/generate/${symbol}?timeframe=1d&days=30`)
            .then(res => res.json())
        );
        
        const results = await Promise.all(promises);
        setRecommendations(results);
      }
    } catch (err) {
      setError('Error fetching recommendations');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'STRONG_BUY':
      case 'BUY':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'STRONG_SELL':
      case 'SELL':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'HOLD':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation) {
      case 'STRONG_BUY':
      case 'BUY':
        return <TrendingUp className="h-4 w-4" />;
      case 'STRONG_SELL':
      case 'SELL':
        return <TrendingDown className="h-4 w-4" />;
      case 'HOLD':
        return <Minus className="h-4 w-4" />;
      default:
        return <Minus className="h-4 w-4" />;
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW':
        return 'bg-green-100 text-green-800';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800';
      case 'HIGH':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading real-time recommendations...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <AlertTriangle className="h-8 w-8 text-red-500" />
        <span className="ml-2 text-red-500">{error}</span>
        <Button onClick={fetchRecommendations} className="ml-4">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Real-Time Trading Recommendations</h2>
        <Button onClick={fetchRecommendations} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid gap-6">
        {recommendations.map((rec) => (
          <div key={rec.symbol} className="border border-gray-200 rounded-lg p-6 bg-white shadow-sm">
            <div className="border-b pb-4 mb-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold">{rec.symbol}</h3>
                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getRecommendationColor(rec.recommendation)}`}>
                    {getRecommendationIcon(rec.recommendation)}
                    <span className="ml-1">{rec.recommendation}</span>
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(rec.risk_assessment.level)}`}>
                    {rec.risk_assessment.level} Risk
                  </span>
                </div>
              </div>
            </div>
            <div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Price and Confidence */}
                <div className="space-y-2">
                  <div className="text-2xl font-bold">${rec.current_price.toLocaleString()}</div>
                  <div className="text-sm text-gray-600">
                    Confidence: <span className="font-semibold">{(rec.confidence * 100).toFixed(1)}%</span>
                  </div>
                </div>

                {/* Market Context */}
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="font-semibold">Trend:</span> {rec.market_context.trend}
                  </div>
                  <div className="text-sm">
                    <span className="font-semibold">Volatility:</span> {rec.market_context.volatility}
                  </div>
                  <div className="text-sm">
                    <span className="font-semibold">24h Change:</span> 
                    <span className={rec.market_context.recent_performance.day_1 >= 0 ? 'text-green-600' : 'text-red-600'}>
                      {rec.market_context.recent_performance.day_1 >= 0 ? '+' : ''}{rec.market_context.recent_performance.day_1.toFixed(2)}%
                    </span>
                  </div>
                </div>

                {/* Signal Scores */}
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="font-semibold">BUY Score:</span> {(rec.scores.buy_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm">
                    <span className="font-semibold">SELL Score:</span> {(rec.scores.sell_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm">
                    <span className="font-semibold">HOLD Score:</span> {(rec.scores.hold_score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Strategy Signals */}
              <div className="mt-4 pt-4 border-t">
                <h4 className="font-semibold mb-2">Strategy Signals:</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  {rec.strategy_signals.map((signal, index) => (
                    <div key={index} className="text-sm p-2 bg-gray-50 rounded">
                      <div className="font-medium">{signal.strategy}</div>
                      <div className="text-gray-600">
                        {signal.signal} ({(signal.confidence * 100).toFixed(1)}%)
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {signal.reasoning}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Reasoning */}
              <div className="mt-4 pt-4 border-t">
                <h4 className="font-semibold mb-2">Reasoning:</h4>
                <p className="text-sm text-gray-600">{rec.reasoning}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EnhancedRecommendations;
