import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Play, BarChart3, TrendingUp, TrendingDown, Clock, AlertTriangle } from 'lucide-react';
import { useBacktestsApi } from '../hooks/useBacktestsApi';
import { normalizeQuickBacktestResult } from '../types/backtests';
import { formatPrice, formatNumber } from '../lib/formatters';

interface BacktestRunnerProps {}

const BacktestRunner: React.FC<BacktestRunnerProps> = () => {
  const { 
    strategies, 
    symbols, 
    loadingStrategies, 
    loadingSymbols, 
    runQuickBacktest, 
    runFullBacktest,
    compareStrategies: apiCompareStrategies, 
    error: apiError 
  } = useBacktestsApi();

  const [symbol, setSymbol] = useState('BTCUSDT');
  const [strategy, setStrategy] = useState('RSI');
  const [days, setDays] = useState(30);
  const [initialCapital, setInitialCapital] = useState(10000);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReturnType<typeof normalizeQuickBacktestResult> | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auto-select first available strategy and symbol when they load
  useEffect(() => {
    if (strategies.length > 0 && !strategies.includes(strategy)) {
      setStrategy(strategies[0]);
    }
  }, [strategies, strategy]);

  useEffect(() => {
    if (symbols.length > 0 && !symbols.includes(symbol)) {
      setSymbol(symbols[0]);
    }
  }, [symbols, symbol]);

  const runBacktest = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await runQuickBacktest(symbol, strategy, days, initialCapital);
      setResult(data);
    } catch (err) {
      console.error('Error running backtest:', err);
      setError(`Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const runFullBacktestWithDates = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - days);

      const backtestRequest = {
        symbol,
        strategy,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        initial_capital: initialCapital,
        params: {}
      };

      const data = await runFullBacktest(backtestRequest);
      
      // Convert full backtest result to normalized format for display
      const normalizedResult = normalizeQuickBacktestResult({
        symbol: data.symbol,
        strategy: data.strategy,
        period: `${days} days`,
        initial_capital: data.initial_capital,
        final_capital: data.final_capital || data.initial_capital,
        total_return: data.total_return || 0,
        total_trades: data.total_trades || 0,
        sharpe_ratio: data.sharpe_ratio || 0,
        max_drawdown: data.max_drawdown || 0,
        win_rate: data.win_rate || 0,
        annualized_return: data.annualized_return || '0%',
        best_trade: data.best_trade || '0%',
        worst_trade: data.worst_trade || '0%',
        profit_factor: data.profit_factor || '0',
        calmar_ratio: data.calmar_ratio || '0',
        sortino_ratio: data.sortino_ratio || '0',
        avg_trade_duration: data.avg_trade_duration || '0 days'
      });

      setResult(normalizedResult);
    } catch (err) {
      console.error('Error running full backtest:', err);
      setError(`Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const compareStrategies = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiCompareStrategies(symbol, days, initialCapital);
      console.log('Strategy comparison:', data);

      if (data.strategies && Object.keys(data.strategies).length > 0) {
        const firstStrategyName = Object.keys(data.strategies)[0];
        const firstStrategyData = data.strategies[firstStrategyName];

        if (!firstStrategyData.error) {
          const mockResult = normalizeQuickBacktestResult({
            symbol: data.symbol,
            strategy: `Comparison (${Object.keys(data.strategies).length} strategies)`,
            period: data.period,
            initial_capital: data.initial_capital,
            final_capital: data.initial_capital,
            ...firstStrategyData
          } as any);
          setResult(mockResult);
        } else {
          setError(`Strategy comparison failed: ${firstStrategyData.error}`);
        }
      }
    } catch (err) {
      console.error('Error comparing strategies:', err);
      setError(`Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const getReturnColor = (returnValue: string) => {
    const value = parseFloat(returnValue.replace('%', ''));
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Backtesting Engine</h2>
        <div className="flex space-x-2">
          <Button onClick={runBacktest} disabled={loading}>
            <Play className="h-4 w-4 mr-2" />
            {loading ? 'Running...' : 'Quick Backtest'}
          </Button>
          <Button onClick={runFullBacktestWithDates} disabled={loading} variant="outline">
            <BarChart3 className="h-4 w-4 mr-2" />
            Full Backtest
          </Button>
          <Button onClick={compareStrategies} disabled={loading} variant="outline">
            <BarChart3 className="h-4 w-4 mr-2" />
            Compare Strategies
          </Button>
        </div>
      </div>

      {/* Configuration Panel */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border rounded-lg bg-gray-50">
        <div>
          <label className="block text-sm font-medium mb-1">Symbol</label>
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            disabled={loadingSymbols || symbols.length === 0}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loadingSymbols ? (
              <option>Loading...</option>
            ) : symbols.length === 0 ? (
              <option>No symbols available</option>
            ) : (
              symbols.map(s => (
                <option key={s} value={s}>{s}</option>
              ))
            )}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Strategy</label>
          <select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            disabled={loadingStrategies || strategies.length === 0}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loadingStrategies ? (
              <option>Loading...</option>
            ) : strategies.length === 0 ? (
              <option>No strategies available</option>
            ) : (
              strategies.map(s => (
                <option key={s} value={s}>{s}</option>
              ))
            )}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Days</label>
          <input
            type="number"
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            min="7"
            max="365"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Initial Capital</label>
          <input
            type="number"
            value={initialCapital}
            onChange={(e) => setInitialCapital(parseFloat(e.target.value))}
            min="1000"
            step="1000"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* API Error Display */}
      {apiError && (
        <div className="p-4 border border-red-300 rounded-lg bg-red-50 text-red-800">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5" />
            <p className="font-medium">API Error</p>
          </div>
          <p className="text-sm">{apiError}</p>
        </div>
      )}

      {/* Backtest Error Display */}
      {error && (
        <div className="p-4 border border-red-300 rounded-lg bg-red-50 text-red-800">
          <p className="font-medium">Error running backtest</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !result && !error && !apiError && (
        <div className="text-center p-8 border border-gray-200 rounded-lg bg-gray-50">
          <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Select parameters and run a backtest to see results</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          <div className="p-4 border rounded-lg bg-white">
            <h3 className="text-lg font-semibold mb-4">Backtest Results</h3>
            
            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-3 border rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{formatPrice(result.final_capital)}</div>
                <div className="text-sm text-gray-600">Final Capital</div>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <div className={`text-2xl font-bold ${getReturnColor(result.total_return)}`}>
                  {result.total_return}
                </div>
                <div className="text-sm text-gray-600">Total Return</div>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{formatNumber(result.sharpe_ratio_num, 2)}</div>
                <div className="text-sm text-gray-600">Sharpe Ratio</div>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{result.total_trades}</div>
                <div className="text-sm text-gray-600">Total Trades</div>
              </div>
            </div>

            {/* Detailed Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-3 flex items-center">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Performance Metrics
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Annualized Return:</span>
                    <span className={`font-medium ${getReturnColor(result.annualized_return)}`}>
                      {result.annualized_return}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Best Trade:</span>
                    <span className="font-medium text-green-600">{result.best_trade}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Worst Trade:</span>
                    <span className="font-medium text-red-600">{result.worst_trade}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Profit Factor:</span>
                    <span className="font-medium">{result.profit_factor}</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-3 flex items-center">
                  <TrendingDown className="h-4 w-4 mr-2" />
                  Risk Metrics
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Max Drawdown:</span>
                    <span className="font-medium text-red-600">{result.max_drawdown}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Win Rate:</span>
                    <span className="font-medium">{result.win_rate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Calmar Ratio:</span>
                    <span className="font-medium">{result.calmar_ratio}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Sortino Ratio:</span>
                    <span className="font-medium">{result.sortino_ratio}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Trade Statistics */}
            <div className="mt-6 p-4 border rounded-lg bg-gray-50">
              <h4 className="font-semibold mb-3 flex items-center">
                <Clock className="h-4 w-4 mr-2" />
                Trade Statistics
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-lg font-bold">{result.total_trades}</div>
                  <div className="text-sm text-gray-600">Total Trades</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold">{result.avg_trade_duration}</div>
                  <div className="text-sm text-gray-600">Avg Duration</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold">{result.win_rate}</div>
                  <div className="text-sm text-gray-600">Win Rate</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center p-8 border border-gray-200 rounded-lg bg-gray-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-gray-600">Running backtest...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default BacktestRunner;