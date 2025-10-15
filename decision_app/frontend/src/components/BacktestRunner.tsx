import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Play, BarChart3, TrendingUp, TrendingDown, Clock, DollarSign } from 'lucide-react';

interface BacktestRunnerProps {}

interface BacktestResult {
  symbol: string;
  strategy: string;
  period: string;
  initial_capital: number;
  final_capital: number;
  total_return: string;
  annualized_return: string;
  sharpe_ratio: string;
  max_drawdown: string;
  win_rate: string;
  total_trades: number;
  avg_trade_duration: string;
  best_trade: string;
  worst_trade: string;
  profit_factor: string;
  calmar_ratio: string;
  sortino_ratio: string;
}

const BacktestRunner: React.FC<BacktestRunnerProps> = () => {
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [strategy, setStrategy] = useState('RSI Strategy');
  const [days, setDays] = useState(30);
  const [initialCapital, setInitialCapital] = useState(10000);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const availableStrategies = [
    'RSI Strategy',
    'MACD Strategy',
    'Bollinger Bands Strategy'
  ];

  const availableSymbols = [
    'BTCUSDT',
    'ETHUSDT',
    'ADAUSDT',
    'SOLUSDT'
  ];

  const runBacktest = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/backtests/quick-test/${symbol}?strategy=${encodeURIComponent(strategy)}&days=${days}&initial_capital=${initialCapital}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Error running backtest:', err);
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
      const response = await fetch(
        `http://localhost:8000/api/v1/backtests/compare/${symbol}?days=${days}&initial_capital=${initialCapital}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Strategy comparison:', data);
      // For now, just show the first strategy result
      if (data.strategies && Object.keys(data.strategies).length > 0) {
        const firstStrategy = Object.keys(data.strategies)[0];
        setResult({
          symbol: data.symbol,
          strategy: `Comparison (${Object.keys(data.strategies).length} strategies)`,
          period: data.period,
          initial_capital: data.initial_capital,
          ...data.strategies[firstStrategy]
        });
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
            {loading ? 'Running...' : 'Run Backtest'}
          </Button>
          <Button onClick={compareStrategies} disabled={loading} variant="outline">
            <BarChart3 className="h-4 w-4 mr-2" />
            Compare Strategies
          </Button>
        </div>
      </div>

      {/* Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border rounded-lg bg-gray-50">
        <div>
          <label className="block text-sm font-medium mb-1">Symbol</label>
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {availableSymbols.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Strategy</label>
          <select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {availableStrategies.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Days</label>
          <input
            type="number"
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            min="7"
            max="90"
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

      {/* Error Display */}
      {error && (
        <div className="p-4 border border-red-300 rounded-lg bg-red-50 text-red-800">
          <p className="font-medium">Error running backtest</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          <div className="p-4 border rounded-lg bg-white">
            <h3 className="text-lg font-semibold mb-4">Backtest Results</h3>
            
            {/* Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-3 border rounded-lg">
                <div className="text-2xl font-bold text-blue-600">${result.final_capital.toLocaleString()}</div>
                <div className="text-sm text-gray-600">Final Capital</div>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <div className={`text-2xl font-bold ${getReturnColor(result.total_return)}`}>
                  {result.total_return}
                </div>
                <div className="text-sm text-gray-600">Total Return</div>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{result.sharpe_ratio}</div>
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
    </div>
  );
};

export default BacktestRunner;
