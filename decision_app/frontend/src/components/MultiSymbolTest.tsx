import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw, TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';

interface MultiSymbolTestProps {
  symbols?: string[];
}

const MultiSymbolTest: React.FC<MultiSymbolTestProps> = ({ 
  symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT'] 
}) => {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testMultipleSymbols = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const symbolsStr = symbols.join(',');
      const response = await fetch(
        `http://localhost:8000/api/v1/enhanced-recommendations/batch/${symbolsStr}?timeframe=1d&days=30`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const resultsArray = Object.entries(data).map(([symbol, result]) => ({
        symbol,
        ...result
      }));
      
      setResults(resultsArray);
    } catch (err) {
      console.error("Error testing multiple symbols:", err);
      setError(`Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'STRONG_BUY':
      case 'BUY':
        return 'bg-green-100 text-green-800 border-green-500';
      case 'STRONG_SELL':
      case 'SELL':
        return 'bg-red-100 text-red-800 border-red-500';
      case 'HOLD':
        return 'bg-yellow-100 text-yellow-800 border-yellow-500';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-500';
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
        return 'bg-green-500 text-white';
      case 'MEDIUM':
        return 'bg-yellow-500 text-black';
      case 'HIGH':
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Multi-Symbol Analysis</h2>
        <Button onClick={testMultipleSymbols} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Test All Symbols
        </Button>
      </div>

      {error && (
        <div className="flex flex-col items-center justify-center p-6 border border-red-300 rounded-lg bg-red-50 shadow-sm text-red-800">
          <AlertTriangle className="h-8 w-8 mb-3" />
          <p className="text-lg font-semibold">Error testing symbols</p>
          <p className="text-sm text-center">{error}</p>
          <Button onClick={testMultipleSymbols} className="mt-4 bg-red-600 hover:bg-red-700 text-white">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center p-6 border border-gray-200 rounded-lg bg-white shadow-sm">
          <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
          <span>Testing {symbols.length} symbols...</span>
        </div>
      )}

      {results.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {results.map((result) => (
            <div key={result.symbol} className="border border-gray-200 rounded-lg p-4 bg-white shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold">{result.symbol}</h3>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getRecommendationColor(result.recommendation)}`}>
                    {getRecommendationIcon(result.recommendation)}
                    <span className="ml-1">{result.recommendation}</span>
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(result.risk_assessment?.level || 'UNKNOWN')}`}>
                    {result.risk_assessment?.level || 'UNKNOWN'} Risk
                  </span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="text-2xl font-bold">${result.current_price?.toLocaleString() || 'N/A'}</div>
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Confidence:</span> {result.confidence ? (result.confidence * 100).toFixed(1) + '%' : 'N/A'}
                </div>
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Trend:</span> {result.market_context?.trend || 'N/A'}
                </div>
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Volatility:</span> {result.market_context?.volatility || 'N/A'}
                </div>
              </div>

              {result.strategy_signals && (
                <div className="mt-3 pt-3 border-t">
                  <h4 className="text-sm font-medium mb-2">Strategy Signals:</h4>
                  {result.strategy_signals.map((signal: any, idx: number) => (
                    <div key={idx} className="flex items-center text-xs text-gray-700 mb-1">
                      <span className="font-medium w-20 truncate">{signal.strategy}:</span>
                      <span className={`px-1 py-0.5 rounded text-xs font-medium ${getRecommendationColor(signal.signal)}`}>
                        {signal.signal} ({(signal.confidence * 100).toFixed(0)}%)
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {!loading && results.length === 0 && !error && (
        <div className="text-center py-8 text-gray-500">
          <p>Click "Test All Symbols" to analyze multiple trading symbols</p>
        </div>
      )}
    </div>
  );
};

export default MultiSymbolTest;
