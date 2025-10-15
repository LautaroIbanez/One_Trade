import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Play, BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';

interface BacktestResult {
  symbol: string;
  strategy: string;
  days: number;
  success: boolean;
  total_return?: number;
  total_trades?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  error?: string;
}

const BacktestComparison: React.FC = () => {
  const [results, setResults] = useState<BacktestResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const testConfigurations = [
    { symbol: 'BTCUSDT', strategy: 'RSI Strategy', days: 90, label: 'BTC + RSI (90d)' },
    { symbol: 'BTCUSDT', strategy: 'MACD Strategy', days: 90, label: 'BTC + MACD (90d)' },
    { symbol: 'BTCUSDT', strategy: 'Bollinger Bands Strategy', days: 90, label: 'BTC + Bollinger (90d)' },
    { symbol: 'ETHUSDT', strategy: 'RSI Strategy', days: 90, label: 'ETH + RSI (90d)' },
    { symbol: 'ETHUSDT', strategy: 'MACD Strategy', days: 90, label: 'ETH + MACD (90d)' },
    { symbol: 'ADAUSDT', strategy: 'RSI Strategy', days: 90, label: 'ADA + RSI (90d)' },
    { symbol: 'SOLUSDT', strategy: 'RSI Strategy', days: 90, label: 'SOL + RSI (90d)' },
  ];

  const runComparison = async () => {
    setLoading(true);
    setError(null);
    setResults([]);

    const newResults: BacktestResult[] = [];

    for (const config of testConfigurations) {
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/backtests/quick-test/${config.symbol}?strategy=${encodeURIComponent(config.strategy)}&days=${config.days}&initial_capital=10000`
        );

        if (response.ok) {
          const result = await response.json();
          newResults.push({
            symbol: config.symbol,
            strategy: config.strategy,
            days: config.days,
            success: true,
            total_return: result.total_return,
            total_trades: result.total_trades,
            sharpe_ratio: result.sharpe_ratio,
            max_drawdown: result.max_drawdown,
            win_rate: result.win_rate,
          });
        } else {
          newResults.push({
            symbol: config.symbol,
            strategy: config.strategy,
            days: config.days,
            success: false,
            error: `HTTP ${response.status}`,
          });
        }
      } catch (err) {
        newResults.push({
          symbol: config.symbol,
          strategy: config.strategy,
          days: config.days,
          success: false,
          error: err instanceof Error ? err.message : String(err),
        });
      }

      // Update results progressively
      setResults([...newResults]);
      
      // Small delay to show progress
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setLoading(false);
  };

  const getReturnColor = (returnValue: number) => {
    if (returnValue > 0) return 'text-green-600';
    if (returnValue < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getTradesColor = (trades: number) => {
    if (trades >= 5) return 'text-blue-600';
    if (trades >= 2) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold">Backtest Comparison</h3>
          <p className="text-sm text-gray-600">
            Compare multiple symbol/strategy combinations with extended periods
          </p>
        </div>
        <Button 
          onClick={runComparison} 
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Play className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Running Tests...' : 'Run Comparison'}
        </Button>
      </div>

      {error && (
        <div className="flex items-center p-4 border border-red-300 rounded-lg bg-red-50 text-red-800">
          <AlertTriangle className="h-5 w-5 mr-2" />
          <span>{error}</span>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <div className="grid gap-4">
            {results.map((result, index) => (
              <div 
                key={index} 
                className={`p-4 border rounded-lg ${
                  result.success 
                    ? 'border-green-200 bg-green-50' 
                    : 'border-red-200 bg-red-50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">
                      {result.symbol} + {result.strategy} ({result.days}d)
                    </span>
                    {result.success ? (
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                        Success
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
                        Failed
                      </span>
                    )}
                  </div>
                </div>

                {result.success ? (
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Return:</span>
                      <div className={`font-semibold ${getReturnColor(result.total_return!)}`}>
                        {(result.total_return! * 100).toFixed(2)}%
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Trades:</span>
                      <div className={`font-semibold ${getTradesColor(result.total_trades!)}`}>
                        {result.total_trades}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Sharpe:</span>
                      <div className="font-semibold">
                        {result.sharpe_ratio!.toFixed(3)}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Max DD:</span>
                      <div className="font-semibold text-red-600">
                        {(result.max_drawdown! * 100).toFixed(2)}%
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600">Win Rate:</span>
                      <div className="font-semibold text-green-600">
                        {(result.win_rate! * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-sm text-red-600">
                    Error: {result.error}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Summary Statistics */}
          {results.filter(r => r.success).length > 0 && (
            <div className="mt-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
              <h4 className="font-semibold mb-3 flex items-center">
                <BarChart3 className="h-4 w-4 mr-2" />
                Summary Statistics
              </h4>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Successful Tests:</span>
                  <div className="font-semibold text-green-600">
                    {results.filter(r => r.success).length}/{results.length}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Best Return:</span>
                  <div className="font-semibold text-green-600">
                    {Math.max(...results.filter(r => r.success).map(r => r.total_return! * 100)).toFixed(2)}%
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Most Trades:</span>
                  <div className="font-semibold text-blue-600">
                    {Math.max(...results.filter(r => r.success).map(r => r.total_trades!))}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Best Sharpe:</span>
                  <div className="font-semibold text-purple-600">
                    {Math.max(...results.filter(r => r.success).map(r => r.sharpe_ratio!)).toFixed(3)}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {loading && results.length === 0 && (
        <div className="flex items-center justify-center p-8 border border-gray-200 rounded-lg bg-gray-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-gray-600">Running backtest comparison...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default BacktestComparison;
