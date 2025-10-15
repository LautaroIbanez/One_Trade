import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Play, Download, Eye, Trash2 } from 'lucide-react'
import BacktestRunner from '@/components/BacktestRunner'
import BacktestComparison from '@/components/BacktestComparison'

export default function Backtests() {
  const [isRunning, setIsRunning] = useState(false)

  const handleRunBacktest = async () => {
    setIsRunning(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    setIsRunning(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Backtests</h2>
          <p className="text-muted-foreground">
            Historical performance analysis of trading strategies
          </p>
        </div>
        <Button onClick={handleRunBacktest} disabled={isRunning}>
          <Play className="h-4 w-4 mr-2" />
          {isRunning ? 'Running...' : 'Run New Backtest'}
        </Button>
      </div>

      {/* Backtesting Engine */}
      <BacktestRunner />

      {/* Backtest Comparison */}
      <BacktestComparison />
    </div>
  )
}

