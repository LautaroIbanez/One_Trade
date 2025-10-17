import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';

interface RealRecommendationsProps {}

interface RecommendationData {
  symbol: string;
  current_price: number;
  recommendation: string;
  confidence: number;
  reasoning: string;
  risk_assessment: {
    level: string;
  };
  market_context: {
    trend: string;
    volatility: string;
  };
  strategy_signals: Array<{
    strategy: string;
    signal: string;
    confidence: number;
    reasoning: string;
  }>;
}

const RealRecommendations: React.FC<RealRecommendationsProps> = () => {
  const [recommendations, setRecommendations] = useState<RecommendationData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get supported symbols
      const symbolsResponse = await fetch('http://localhost:8000/api/v1/enhanced-recommendations/supported-symbols');
      const symbols = await symbolsResponse.json();
      
      // Get recommendations for each symbol
      const promises = symbols.map(symbol => 
        fetch(`http://localhost:8000/api/v1/enhanced-recommendations/generate/${symbol}?timeframe=1d&days=30`)
          .then(res => {
            if (!res.ok) {
              throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
          })
      );
      
      const results = await Promise.all(promises);
      setRecommendations(results);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      setError(`Error: ${err instanceof Error ? err.message : String(err)}`);
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
        return 'text-green-600';
      case 'STRONG_SELL':
      case 'SELL':
        return 'text-red-600';
      case 'HOLD':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
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
        return null;
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW':
        return 'bg-green-500';
      case 'MEDIUM':
        return 'bg-yellow-500';
      case 'HIGH':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getTrendColor = (trend: string) => {
    if (trend.includes('DOWNTREND')) return 'text-red-600';
    if (trend.includes('UPTREND')) return 'text-green-600';
    return 'text-yellow-600';
  };

  if (loading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="rounded-lg border bg-card p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="space-y-3">
              <div className="h-3 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border bg-red-50 p-6 text-red-800">
        <p className="font-medium">Ups, algo salió mal</p>
        <p className="text-sm">{error}</p>
        <button 
          onClick={fetchRecommendations}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          <RefreshCw className="h-4 w-4 mr-2 inline" />
          Intentar otra vez
        </button>
      </div>
    );
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {recommendations.map((rec) => (
        <div key={rec.symbol} className="rounded-lg border bg-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getRiskColor(rec.risk_assessment.level)}`}></div>
              <span className="font-semibold">{rec.symbol}</span>
            </div>
            <span className="text-sm text-muted-foreground">En vivo</span>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Qué hacer</span>
              <span className={`font-semibold flex items-center ${getRecommendationColor(rec.recommendation)}`}>
                {getRecommendationIcon(rec.recommendation)}
                <span className="ml-1">{rec.recommendation}</span>
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Qué tan seguro</span>
              <span className="font-semibold">{(rec.confidence * 100).toFixed(1)}%</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Precio ahora</span>
              <span className="font-semibold">${rec.current_price.toLocaleString()}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Nivel de riesgo</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium text-white ${getRiskColor(rec.risk_assessment.level)}`}>
                {rec.risk_assessment.level === 'LOW' ? 'BAJO' : rec.risk_assessment.level === 'MEDIUM' ? 'MEDIO' : 'ALTO'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Tendencia</span>
              <span className={`font-semibold ${getTrendColor(rec.market_context.trend)}`}>
                {rec.market_context.trend}
              </span>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-muted rounded-md">
            <p className="text-sm">
              <strong>Señales que encontré:</strong>
            </p>
            <div className="mt-2 space-y-1">
              {rec.strategy_signals.map((signal, idx) => (
                <div key={idx} className="text-xs">
                  <span className="font-medium">{signal.strategy}:</span> {signal.signal} ({(signal.confidence * 100).toFixed(0)}%)
                </div>
              ))}
            </div>
            <p className="text-sm mt-2">
              <strong>Por qué:</strong> {rec.reasoning.substring(0, 100)}...
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default RealRecommendations;
