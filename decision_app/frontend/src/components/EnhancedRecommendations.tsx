import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw, TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';
import { useRecommendations } from '../hooks/useRecommendations';
import { EnhancedRecommendation } from '../types/recommendations';
import { formatPrice, formatPercentage, formatNumber, formatRiskLevel, formatTrend, safeGet } from '../lib/formatters';

const EnhancedRecommendations: React.FC = () => {
  const { 
    getBatchRecommendations, 
    getSupportedSymbols, 
    refreshRecommendations,
    isLoading: hookLoading, 
    isRefreshing,
    error: hookError 
  } = useRecommendations();

  const [recommendations, setRecommendations] = useState<Record<string, EnhancedRecommendation>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [symbols, setSymbols] = useState<string[]>([]);

  const fetchRecommendations = async (isRefresh = false) => {
    if (!isRefresh) {
      setLoading(true);
    }
    setError(null);
    
    try {
      // Get supported symbols first
      const supportedSymbols = await getSupportedSymbols();
      setSymbols(supportedSymbols);
      
      // Use first 3 symbols for display
      const defaultSymbols = supportedSymbols.slice(0, 3);
      
      // Get batch recommendations
      const recs = await getBatchRecommendations(defaultSymbols, '1d', 30);
      setRecommendations(recs);
      
    } catch (err) {
      const errorMessage = hookError || 'Error fetching recommendations';
      setError(errorMessage);
      console.error('Error:', err);
    } finally {
      if (!isRefresh) {
        setLoading(false);
      }
    }
  };

  const handleRefresh = async () => {
    if (symbols.length > 0) {
      try {
        const defaultSymbols = symbols.slice(0, 3);
        const recs = await refreshRecommendations(defaultSymbols, '1d', 30);
        setRecommendations(recs);
        setError(null);
      } catch (err) {
        const errorMessage = hookError || 'Error refreshing recommendations';
        setError(errorMessage);
      }
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
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Real-Time Trading Recommendations</h2>
          <Button disabled>
            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            Loading...
          </Button>
        </div>
        <div className="flex items-center justify-center p-8">
          <RefreshCw className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading real-time recommendations...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Real-Time Trading Recommendations</h2>
          <Button onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
        <div className="flex items-center justify-center p-8">
          <AlertTriangle className="h-8 w-8 text-red-500" />
          <span className="ml-2 text-red-500">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Real-Time Trading Recommendations</h2>
        <Button onClick={handleRefresh} disabled={isRefreshing}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          {isRefreshing ? 'Refreshing...' : 'Refresh'}
        </Button>
      </div>

      <div className="grid gap-6">
        {Object.entries(recommendations).map(([symbol, rec]) => (
          rec.error ? (
            <div key={symbol} className="border border-yellow-200 rounded-lg p-6 bg-yellow-50">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <span className="font-medium text-yellow-800">{symbol}</span>
              </div>
              <p className="text-sm text-yellow-700 mt-2">
                {rec.error || 'Error loading recommendation'}
              </p>
            </div>
          ) : (
            <div key={symbol} className="border border-gray-200 rounded-lg p-6 bg-white shadow-sm">
              <div className="border-b pb-4 mb-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold">{symbol}</h3>
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getRecommendationColor(rec.recommendation ?? 'HOLD')}`}>
                      {getRecommendationIcon(rec.recommendation ?? 'HOLD')}
                      <span className="ml-1">{rec.recommendation ?? 'HOLD'}</span>
                    </span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(rec.risk_assessment?.level ?? 'MEDIUM')}`}>
                      {formatRiskLevel(rec.risk_assessment?.level)} Risk
                    </span>
                  </div>
                </div>
              </div>
              
              <div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="text-2xl font-bold">{formatPrice(rec.current_price)}</div>
                    <div className="text-sm text-gray-600">
                      Confidence: <span className="font-semibold">{formatPercentage(rec.confidence)}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-semibold">Trend:</span> {formatTrend(rec.market_context?.trend)}
                    </div>
                    <div className="text-sm">
                      <span className="font-semibold">Volatility:</span> {rec.market_context?.volatility ?? 'N/A'}
                    </div>
                    <div className="text-sm">
                      <span className="font-semibold">24h Change:</span>
                      <span className={safeGet(rec.market_context?.recent_performance?.day_1, 0) >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {safeGet(rec.market_context?.recent_performance?.day_1, 0) >= 0 ? '+' : ''}{formatNumber(safeGet(rec.market_context?.recent_performance?.day_1, 0))}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-semibold">BUY Score:</span> {formatPercentage(rec.scores?.buy_score)}
                    </div>
                    <div className="text-sm">
                      <span className="font-semibold">SELL Score:</span> {formatPercentage(rec.scores?.sell_score)}
                    </div>
                    <div className="text-sm">
                      <span className="font-semibold">HOLD Score:</span> {formatPercentage(rec.scores?.hold_score)}
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t">
                  <h4 className="font-semibold mb-2">Strategy Signals:</h4>
                  {rec.strategy_signals && rec.strategy_signals.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                      {rec.strategy_signals.map((signal, index) => (
                        <div key={index} className="text-sm p-2 bg-gray-50 rounded">
                          <div className="font-medium">{signal.strategy ?? 'N/A'}</div>
                          <div className="text-gray-600">
                            {signal.signal ?? 'N/A'} ({formatPercentage(signal.confidence)})
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {signal.reasoning ?? 'No reasoning provided'}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No strategy signals available</p>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t">
                  <h4 className="font-semibold mb-2">Reasoning:</h4>
                  <p className="text-sm text-gray-600">{rec.reasoning ?? 'No reasoning available'}</p>
                </div>

                {rec.trading_levels && (
                  <div className="mt-4 pt-4 border-t">
                    <h4 className="font-semibold mb-3">Trading Levels</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {rec.trading_levels.entry_long && (
                        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                          <div className="flex items-center space-x-2 mb-2">
                            <TrendingUp className="h-4 w-4 text-green-600" />
                            <span className="font-semibold text-green-800">LONG Position</span>
                          </div>
                          <div className="space-y-1 text-sm">
                            <div>
                              <span className="text-gray-600">Entry Range:</span>
                              <span className="ml-2 font-medium text-green-700">
                                {formatPrice(rec.trading_levels.entry_long.min)} - {formatPrice(rec.trading_levels.entry_long.max)}
                              </span>
                            </div>
                            {rec.trading_levels.take_profit_long && (
                              <div>
                                <span className="text-gray-600">Take Profit:</span>
                                <span className="ml-2 font-medium text-green-700">
                                  {formatPrice(rec.trading_levels.take_profit_long)}
                                </span>
                              </div>
                            )}
                            {rec.trading_levels.stop_loss_long && (
                              <div>
                                <span className="text-gray-600">Stop Loss:</span>
                                <span className="ml-2 font-medium text-red-700">
                                  {formatPrice(rec.trading_levels.stop_loss_long)}
                                </span>
                              </div>
                            )}
                            <div className="text-xs text-gray-500 mt-2">
                              Confidence: {formatPercentage(rec.trading_levels.entry_long.confidence)}
                            </div>
                          </div>
                        </div>
                      )}

                      {rec.trading_levels.entry_short && (
                        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                          <div className="flex items-center space-x-2 mb-2">
                            <TrendingDown className="h-4 w-4 text-red-600" />
                            <span className="font-semibold text-red-800">SHORT Position</span>
                          </div>
                          <div className="space-y-1 text-sm">
                            <div>
                              <span className="text-gray-600">Entry Range:</span>
                              <span className="ml-2 font-medium text-red-700">
                                {formatPrice(rec.trading_levels.entry_short.min)} - {formatPrice(rec.trading_levels.entry_short.max)}
                              </span>
                            </div>
                            {rec.trading_levels.take_profit_short && (
                              <div>
                                <span className="text-gray-600">Take Profit:</span>
                                <span className="ml-2 font-medium text-green-700">
                                  {formatPrice(rec.trading_levels.take_profit_short)}
                                </span>
                              </div>
                            )}
                            {rec.trading_levels.stop_loss_short && (
                              <div>
                                <span className="text-gray-600">Stop Loss:</span>
                                <span className="ml-2 font-medium text-red-700">
                                  {formatPrice(rec.trading_levels.stop_loss_short)}
                                </span>
                              </div>
                            )}
                            <div className="text-xs text-gray-500 mt-2">
                              Confidence: {formatPercentage(rec.trading_levels.entry_short.confidence)}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    {rec.trading_levels.atr && (
                      <div className="mt-2 text-xs text-gray-500">
                        ATR (14): {formatNumber(rec.trading_levels.atr)}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        ))}
      </div>
    </div>
  );
};

export default EnhancedRecommendations;