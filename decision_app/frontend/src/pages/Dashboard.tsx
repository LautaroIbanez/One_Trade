import { TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react'
import EnhancedRecommendations from '@/components/EnhancedRecommendations'
import RealTimeStats from '@/components/RealTimeStats'

export default function Dashboard() {
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

      {/* Real-Time Recommendations */}
      <EnhancedRecommendations />
    </div>
  )
}

