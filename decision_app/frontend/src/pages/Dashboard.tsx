import { useState } from 'react'
import { TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react'
import EnhancedRecommendations from '@/components/EnhancedRecommendations'
import RealTimeStats from '@/components/RealTimeStats'
import PriceChart from '@/components/PriceChart'
import { useChartData } from '@/hooks/useChartData'
import { Button } from '@/components/ui/button'
import { RefreshCw } from 'lucide-react'

export default function Dashboard() {
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT')
  const { chartData, isLoading, error, refetch } = useChartData({
    symbol: selectedSymbol,
    timeframe: '1d',
    days: 30
  })

  const symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT']

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          Overview of your trading recommendations and performance
        </p>
      </div>

      {/* Real-Time Stats */}
      <RealTimeStats />

      {/* Price Chart Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">Price Analysis</h3>
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              {symbols.map((symbol) => (
                <button
                  key={symbol}
                  onClick={() => setSelectedSymbol(symbol)}
                  className={`px-3 py-1 text-sm rounded ${
                    selectedSymbol === symbol
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {symbol.replace('USDT', '')}
                </button>
              ))}
            </div>
            <Button onClick={refetch} disabled={isLoading} size="sm" variant="outline">
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center h-80">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">Loading chart data...</span>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center h-80 text-red-600">
            <span>Error: {error}</span>
          </div>
        )}

        {!isLoading && !error && chartData && (
          <PriceChart
            data={chartData.data}
            symbol={chartData.symbol}
            currentPrice={chartData.current_price}
            entryLong={chartData.trading_levels?.entry_long}
            entryShort={chartData.trading_levels?.entry_short}
            takeProfitLong={chartData.trading_levels?.take_profit_long}
            stopLossLong={chartData.trading_levels?.stop_loss_long}
            takeProfitShort={chartData.trading_levels?.take_profit_short}
            stopLossShort={chartData.trading_levels?.stop_loss_short}
          />
        )}
      </div>

      {/* Real-Time Recommendations */}
      <EnhancedRecommendations />
    </div>
  )
}

