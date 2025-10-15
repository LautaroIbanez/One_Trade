import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { RefreshCw, Filter, Download } from 'lucide-react'
import MultiSymbolTest from '@/components/MultiSymbolTest'
import RealRecommendations from '@/components/RealRecommendations'

export default function Recommendations() {
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
          <h2 className="text-3xl font-bold tracking-tight">Recommendations</h2>
          <p className="text-muted-foreground">
            Daily trading recommendations based on multiple strategies
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleRefresh} disabled={isLoading} size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Real-Time Recommendation Cards */}
      <RealRecommendations />

      {/* Multi-Symbol Analysis */}
      <MultiSymbolTest />
    </div>
  )
}

