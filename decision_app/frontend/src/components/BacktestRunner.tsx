import React, { useState, useEffect } from 'react'; import { Button } from '@/components/ui/button'; import { Play, BarChart3, TrendingUp, TrendingDown, Clock } from 'lucide-react'; import { useBacktestsApi } from '../hooks/useBacktestsApi'; import { normalizeQuickBacktestResult } from '../types/backtests'; import { formatPrice, formatNumber } from '../lib/formatters'; interface BacktestRunnerProps {} const BacktestRunner: React.FC<BacktestRunnerProps> = () => { const { strategies, symbols, loadingStrategies, loadingSymbols, runQuickBacktest, compareStrategies: apiCompareStrategies, error: apiError } = useBacktestsApi(); const [symbol, setSymbol] = useState('BTCUSDT'); const [strategy, setStrategy] = useState('RSI Strategy'); const [days, setDays] = useState(30); const [initialCapital, setInitialCapital] = useState(10000); const [loading, setLoading] = useState(false); const [result, setResult] = useState<ReturnType<typeof normalizeQuickBacktestResult> | null>(null); const [error, setError] = useState<string | null>(null); useEffect(() => { if (strategies.length > 0 && !strategies.includes(strategy)) { setStrategy(strategies[0]); } }, [strategies, strategy]); useEffect(() => { if (symbols.length > 0 && !symbols.includes(symbol)) { setSymbol(symbols[0]); } }, [symbols, symbol]);

  const runBacktest = async () => { setLoading(true); setError(null); setResult(null); try { const data = await runQuickBacktest(symbol, strategy, days, initialCapital); setResult(data); } catch (err) { console.error('Error running backtest:', err); setError(`Error: ${err instanceof Error ? err.message : String(err)}`); } finally { setLoading(false); } }; const compareStrategies = async () => { setLoading(true); setError(null); setResult(null); try { const data = await apiCompareStrategies(symbol, days, initialCapital); console.log('Strategy comparison:', data); if (data.strategies && Object.keys(data.strategies).length > 0) { const firstStrategyName = Object.keys(data.strategies)[0]; const firstStrategyData = data.strategies[firstStrategyName]; if (!firstStrategyData.error) { const mockResult = normalizeQuickBacktestResult({ symbol: data.symbol, strategy: `Comparison (${Object.keys(data.strategies).length} strategies)`, period: data.period, initial_capital: data.initial_capital, final_capital: data.initial_capital, ...firstStrategyData } as any); setResult(mockResult); } else { setError(`Strategy comparison failed: ${firstStrategyData.error}`); } } } catch (err) { console.error('Error comparing strategies:', err); setError(`Error: ${err instanceof Error ? err.message : String(err)}`); } finally { setLoading(false); } };

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

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border rounded-lg bg-gray-50"> <div> <label className="block text-sm font-medium mb-1">Symbol</label> <select value={symbol} onChange={(e) => setSymbol(e.target.value)} disabled={loadingSymbols || symbols.length === 0} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed" > {loadingSymbols ? ( <option>Loading...</option> ) : symbols.length === 0 ? ( <option>No symbols available</option> ) : ( symbols.map(s => ( <option key={s} value={s}>{s}</option> )) )} </select> </div> <div> <label className="block text-sm font-medium mb-1">Strategy</label> <select value={strategy} onChange={(e) => setStrategy(e.target.value)} disabled={loadingStrategies || strategies.length === 0} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed" > {loadingStrategies ? ( <option>Loading...</option> ) : strategies.length === 0 ? ( <option>No strategies available</option> ) : ( strategies.map(s => ( <option key={s} value={s}>{s}</option> )) )} </select> </div>

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
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6"> <div className="text-center p-3 border rounded-lg"> <div className="text-2xl font-bold text-blue-600">{formatPrice(result.final_capital)}</div> <div className="text-sm text-gray-600">Final Capital</div> </div> <div className="text-center p-3 border rounded-lg"> <div className={`text-2xl font-bold ${getReturnColor(result.total_return)}`}> {result.total_return} </div> <div className="text-sm text-gray-600">Total Return</div> </div> <div className="text-center p-3 border rounded-lg"> <div className="text-2xl font-bold text-purple-600">{formatNumber(result.sharpe_ratio_num, 2)}</div> <div className="text-sm text-gray-600">Sharpe Ratio</div> </div> <div className="text-center p-3 border rounded-lg"> <div className="text-2xl font-bold text-orange-600">{result.total_trades}</div> <div className="text-sm text-gray-600">Total Trades</div> </div> </div>

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
