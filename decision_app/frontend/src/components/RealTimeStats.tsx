import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react';
import { useMockData } from '../hooks/useMockData';

interface RealTimeStatsProps {}

interface StatsData {
  activeRecommendations: number;
  totalPnL: number;
  winRate: number;
  maxDrawdown: number;
  lastUpdate: string;
}

const RealTimeStats: React.FC<RealTimeStatsProps> = () => {
  const { getStats, getSupportedSymbols, isLoading, lastUpdated, MOCK_MODE } = useMockData();
  const [stats, setStats] = useState<StatsData>({
    activeRecommendations: 0,
    totalPnL: 0,
    winRate: 0,
    maxDrawdown: 0,
    lastUpdate: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    
    try {
      if (MOCK_MODE) {
        // Use mock data
        const mockStatsData = await getStats();
        const symbols = await getSupportedSymbols();
        
        setStats({
          activeRecommendations: symbols.length,
          totalPnL: mockStatsData.totalReturn * 100,
          winRate: mockStatsData.winRate * 100,
          maxDrawdown: mockStatsData.maxDrawdown * 100,
          lastUpdate: lastUpdated.toLocaleTimeString()
        });
      } else {
        // Real API calls (original code)
        const symbolsResponse = await fetch('http://localhost:8000/api/v1/enhanced-recommendations/supported-symbols');
        const symbols = await symbolsResponse.json();
        
        // Get batch recommendations to calculate stats
        const symbolsStr = symbols.join(',');
        const recommendationsResponse = await fetch(
          `http://localhost:8000/api/v1/enhanced-recommendations/batch/${symbolsStr}?timeframe=1d&days=30`
        );
        const recommendations = await recommendationsResponse.json();
      
        // Calculate stats from real data
        const activeRecommendations = symbols.length;
        let totalConfidence = 0;
        let buySignals = 0;
        let sellSignals = 0;
        let holdSignals = 0;
        let totalPriceChange = 0;
        let maxDrawdown = 0;
        
        Object.values(recommendations).forEach((rec: any) => {
          if (rec.error) return;
          
          totalConfidence += rec.confidence || 0;
          
          if (rec.recommendation === 'BUY' || rec.recommendation === 'STRONG_BUY') {
            buySignals++;
          } else if (rec.recommendation === 'SELL' || rec.recommendation === 'STRONG_SELL') {
            sellSignals++;
          } else {
            holdSignals++;
          }
          
          // Calculate price change from market context
          if (rec.market_context?.recent_performance?.day_1) {
            totalPriceChange += rec.market_context.recent_performance.day_1;
          }
          
          // Estimate drawdown from volatility
          if (rec.market_context?.volatility === 'HIGH') {
            maxDrawdown = Math.max(maxDrawdown, -15);
          } else if (rec.market_context?.volatility === 'MEDIUM') {
            maxDrawdown = Math.max(maxDrawdown, -8);
          } else {
            maxDrawdown = Math.max(maxDrawdown, -3);
          }
        });
        
        const avgConfidence = activeRecommendations > 0 ? totalConfidence / activeRecommendations : 0;
        const winRate = buySignals > 0 ? (buySignals / (buySignals + sellSignals + holdSignals)) * 100 : 0;
        
        // Estimate P&L based on signal distribution and confidence
        const estimatedPnL = (buySignals * avgConfidence * 2.5) - (sellSignals * avgConfidence * 1.8);
        
        setStats({
          activeRecommendations,
          totalPnL: estimatedPnL,
          winRate: winRate,
          maxDrawdown: maxDrawdown,
          lastUpdate: new Date().toLocaleTimeString()
        });
      }
      
    } catch (err) {
      console.error("Error fetching stats:", err);
      setError('Error loading statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Refresh stats every 5 minutes
    const interval = setInterval(fetchStats, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="rounded-lg border bg-card p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-1"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="col-span-full rounded-lg border bg-red-50 p-6 text-red-800">
          <p className="font-medium">Error loading statistics</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center space-x-2">
          <TrendingUp className="h-4 w-4 text-green-600" />
          <span className="text-sm font-medium">Active Recommendations</span>
        </div>
        <div className="mt-2">
          <div className="text-2xl font-bold">{stats.activeRecommendations}</div>
          <p className="text-xs text-muted-foreground">
            Real-time analysis
          </p>
        </div>
      </div>

      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center space-x-2">
          <DollarSign className="h-4 w-4 text-blue-600" />
          <span className="text-sm font-medium">Estimated P&L</span>
        </div>
        <div className="mt-2">
          <div className={`text-2xl font-bold ${stats.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {stats.totalPnL >= 0 ? '+' : ''}${stats.totalPnL.toFixed(0)}
          </div>
          <p className="text-xs text-muted-foreground">
            Based on signal confidence
          </p>
        </div>
      </div>

      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center space-x-2">
          <Activity className="h-4 w-4 text-purple-600" />
          <span className="text-sm font-medium">Buy Signal Rate</span>
        </div>
        <div className="mt-2">
          <div className="text-2xl font-bold">{stats.winRate.toFixed(0)}%</div>
          <p className="text-xs text-muted-foreground">
            Current market conditions
          </p>
        </div>
      </div>

      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center space-x-2">
          <TrendingDown className="h-4 w-4 text-red-600" />
          <span className="text-sm font-medium">Max Drawdown</span>
        </div>
        <div className="mt-2">
          <div className="text-2xl font-bold text-red-600">{stats.maxDrawdown.toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground">
            Based on volatility
          </p>
        </div>
      </div>
    </div>
  );
};

export default RealTimeStats;
