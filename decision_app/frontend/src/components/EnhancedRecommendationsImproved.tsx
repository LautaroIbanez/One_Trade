import React, { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useApiWithRetry, createFetchFn } from '../hooks/useApiWithRetry';
import { ErrorDisplay, LoadingDisplay, EmptyDisplay } from './ErrorDisplay';

interface Recommendation {
  symbol: string;
  recommendation: string;
  confidence: number;
  timestamp: string;
  details: {
    timeframe: string;
    days: number;
    strategy: string;
    indicators?: {
      rsi: number;
      macd: number;
      bollinger_position: number;
    };
  };
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const EnhancedRecommendationsImproved: React.FC = () => {
  const {
    data: symbols,
    loading: loadingSymbols,
    error: symbolsError,
    execute: fetchSymbols,
    retry: retrySymbols
  } = useApiWithRetry<string[]>(
    createFetchFn<string[]>(`${API_BASE_URL}/api/v1/enhanced-recommendations/supported-symbols`),
    { maxRetries: 3, retryDelay: 1000 }
  );

  const {
    data: recommendations,
    loading: loadingRecs,
    error: recsError,
    execute: fetchRecommendations,
    retry: retryRecommendations
  } = useApiWithRetry<Record<string, Recommendation>>(
    async () => {
      if (!symbols || symbols.length === 0) {
        throw new Error('No symbols available');
      }
      
      const symbolsStr = symbols.slice(0, 6).join(',');
      const fetchFn = createFetchFn<Record<string, Recommendation>>(
        `${API_BASE_URL}/api/v1/enhanced-recommendations/batch/${symbolsStr}?timeframe=1d&days=30`
      );
      return await fetchFn();
    },
    { maxRetries: 3, retryDelay: 1000 }
  );

  useEffect(() => {
    fetchSymbols();
  }, []);

  useEffect(() => {
    if (symbols && symbols.length > 0) {
      fetchRecommendations();
    }
  }, [symbols]);

  const handleRefresh = () => {
    fetchSymbols();
    if (symbols && symbols.length > 0) {
      fetchRecommendations();
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation.toUpperCase()) {
      case 'BUY':
      case 'STRONG_BUY':
        return 'bg-green-100 text-green-800';
      case 'SELL':
      case 'STRONG_SELL':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation.toUpperCase()) {
      case 'BUY':
      case 'STRONG_BUY':
        return <TrendingUp className="h-4 w-4" />;
      case 'SELL':
      case 'STRONG_SELL':
        return <TrendingDown className="h-4 w-4" />;
      default:
        return <Minus className="h-4 w-4" />;
    }
  };

  // Manejo de estados de carga y error
  if (symbolsError) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Qué hacer ahora</h2>
        <ErrorDisplay error={symbolsError} onRetry={retrySymbols} />
      </div>
    );
  }

  if (recsError) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Enhanced Recommendations</h2>
        <ErrorDisplay error={recsError} onRetry={retryRecommendations} />
      </div>
    );
  }

  if (loadingSymbols || (loadingRecs && !recommendations)) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Qué hacer ahora</h2>
        <LoadingDisplay message="Analizando el mercado para ti..." />
      </div>
    );
  }

  if (!recommendations || Object.keys(recommendations).length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Qué hacer ahora</h2>
        <EmptyDisplay message="Todavía no tenemos señales claras. Vuelve en unos minutos." />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      {/* Header */}
      <div className="px-6 py-4 border-b">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Qué hacer ahora</h2>
          <Button
            onClick={handleRefresh}
            disabled={loadingRecs}
            className="bg-blue-600 text-white hover:bg-blue-700"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${loadingRecs ? 'animate-spin' : ''}`} />
            {loadingRecs ? 'Revisando...' : 'Revisar de nuevo'}
          </Button>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="p-6">
        <div className="space-y-4">
          {Object.values(recommendations).map((rec) => (
            <div key={rec.symbol} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    <span className="font-semibold text-lg">{rec.symbol}</span>
                  </div>
                  
                  <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRecommendationColor(rec.recommendation)}`}>
                    {getRecommendationIcon(rec.recommendation)}
                    <span className="ml-2">{rec.recommendation}</span>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div>
                      <p className="text-xs text-gray-500">Qué tan seguro estoy</p>
                      <p className="text-sm font-medium">{(rec.confidence * 100).toFixed(1)}%</p>
                    </div>
                    
                    <div>
                      <p className="text-xs text-gray-500">Método usado</p>
                      <p className="text-sm font-medium">{rec.details.strategy}</p>
                    </div>
                    
                    {rec.details.indicators && (
                      <>
                        <div>
                          <p className="text-xs text-gray-500">RSI</p>
                          <p className="text-sm font-medium">{rec.details.indicators.rsi.toFixed(1)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">MACD</p>
                          <p className="text-sm font-medium">{rec.details.indicators.macd.toFixed(4)}</p>
                        </div>
                      </>
                    )}
                  </div>
                </div>
                
                <div className="text-xs text-gray-400">
                  {new Date(rec.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EnhancedRecommendationsImproved;
