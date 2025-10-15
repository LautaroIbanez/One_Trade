import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { RefreshCw, Download, TrendingUp, TrendingDown } from 'lucide-react'

export default function MarketData() {
  const [isLoading, setIsLoading] = useState(false)

  const handleRefresh = async () => {
    setIsLoading(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsLoading(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Market Data</h2>
          <p className="text-muted-foreground">
            Real-time and historical market data for supported symbols
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </Button>
          <Button onClick={handleRefresh} disabled={isLoading} size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Market Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* BTC/USDT */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold">BTC/USDT</h3>
              <p className="text-sm text-muted-foreground">Bitcoin</p>
            </div>
            <div className="flex items-center text-green-600">
              <TrendingUp className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">+2.4%</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Price</span>
              <span className="font-semibold">$67,250.00</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24h High</span>
              <span className="font-semibold">$68,420.00</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24h Low</span>
              <span className="font-semibold">$65,180.00</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24h Volume</span>
              <span className="font-semibold">$2.4B</span>
            </div>
          </div>
        </div>

        {/* ETH/USDT */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold">ETH/USDT</h3>
              <p className="text-sm text-muted-foreground">Ethereum</p>
            </div>
            <div className="flex items-center text-red-600">
              <TrendingDown className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">-1.8%</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Price</span>
              <span className="font-semibold">$3,420.50</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24h High</span>
              <span className="font-semibold">$3,520.00</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24h Low</span>
              <span className="font-semibold">$3,380.00</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24h Volume</span>
              <span className="font-semibold">$1.8B</span>
            </div>
          </div>
        </div>

        {/* ADA/USDT */}
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold">ADA/USDT</h3>
              <p className="text-sm text-muted-foreground">Cardano</p>
            </div>
            <div className="flex items-center text-green-600">
              <TrendingUp className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">+0.8%</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Price</span>
              <span className="font-semibold">$0.485</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24h High</span>
              <span className="font-semibold">$0.492</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24h Low</span>
              <span className="font-semibold">$0.478</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24h Volume</span>
              <span className="font-semibold">$245M</span>
            </div>
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="text-lg font-semibold mb-4">Data Management</h3>
        
        <div className="grid gap-6 md:grid-cols-2">
          {/* Supported Symbols */}
          <div>
            <h4 className="font-medium mb-3">Supported Symbols</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">BTC/USDT</span>
                <span className="text-sm text-green-600">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">ETH/USDT</span>
                <span className="text-sm text-green-600">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">ADA/USDT</span>
                <span className="text-sm text-green-600">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">SOL/USDT</span>
                <span className="text-sm text-yellow-600">Pending</span>
              </div>
            </div>
          </div>

          {/* Supported Timeframes */}
          <div>
            <h4 className="font-medium mb-3">Supported Timeframes</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">1m</span>
                <span className="text-sm text-green-600">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">5m</span>
                <span className="text-sm text-green-600">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">1h</span>
                <span className="text-sm text-green-600">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">4h</span>
                <span className="text-sm text-green-600">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <span className="font-medium">1d</span>
                <span className="text-sm text-green-600">Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Data Statistics */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="text-lg font-semibold mb-4">Data Statistics</h3>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Total Records</p>
            <p className="text-2xl font-bold">2.4M</p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Last Update</p>
            <p className="text-2xl font-bold">2 min ago</p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Data Coverage</p>
            <p className="text-2xl font-bold">99.8%</p>
          </div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Storage Used</p>
            <p className="text-2xl font-bold">1.2 GB</p>
          </div>
        </div>
      </div>
    </div>
  )
}

