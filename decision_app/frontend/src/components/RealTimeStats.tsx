import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, DollarSign, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { apiClient, ApiError } from '../lib/api-client';

interface RealTimeStatsProps {}

interface StatsData {
  activeRecommendations: number;
  totalPnL: number;
  winRate: number;
  maxDrawdown: number;
  lastUpdate: string;
}

interface BackendStatsResponse {
  activeRecommendations: number;
  totalPnL: number;
  winRate: number;
  maxDrawdown: number;
  lastUpdate: string;
}

const RealTimeStats: React.FC<RealTimeStatsProps> = () => {
  const [stats, setStats] = useState<StatsData>({
    activeRecommendations: 0,
    totalPnL: 0,
    winRate: 0,
    maxDrawdown: 0,
    lastUpdate: ''
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);
    
    try {
      // Try to get stats from dedicated endpoint first
      try {
        const statsData = await apiClient.get<BackendStatsResponse>('/stats');
        
        // Check if we have real backtest data
        const hasRealData = (statsData as any).dataSource === 'backtests';
        
        setStats({
          activeRecommendations: statsData.activeRecommendations,
          totalPnL: statsData.totalPnL,
          winRate: statsData.winRate,
          maxDrawdown: statsData.maxDrawdown,
          lastUpdate: new Date().toLocaleTimeString()
        });
        
        // If we don't have real backtest data, show a warning
        if (!hasRealData) {
          setError('No historical backtest data available. Showing estimated metrics.');
        }
        
        return;
      } catch (statsError) {
        console.log('Stats endpoint not available');
        setError('Historical metrics not available. Please run backtests to see real performance data.');
        return;
      }

    } catch (err) {
      console.error("Error fetching stats:", err);
      const errorMessage = err instanceof ApiError ? err.message : 'Error loading statistics';
      setError(errorMessage);
    } finally {
      if (isRefresh) {
        setRefreshing(false);
      } else {
        setLoading(false);
      }
    }
  };

  const handleRefresh = () => {
    fetchStats(true);
  };

  useEffect(() => {
    fetchStats();
    // Refresh stats every 5 minutes
    const interval = setInterval(() => fetchStats(true), 5 * 60 * 1000);
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
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Error loading statistics</p>
              <p className="text-sm">{error}</p>
            </div>
            <Button onClick={handleRefresh} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Real-Time Statistics</h3>
        <Button 
          onClick={handleRefresh} 
          disabled={refreshing}
          variant="outline"
          size="sm"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </Button>
      </div>
      
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
              {stats.totalPnL >= 0 ? '+' : ''}{stats.totalPnL.toFixed(2)}%
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
      
      <div className="text-xs text-muted-foreground text-center">
        Last updated: {stats.lastUpdate}
      </div>
    </div>
  );
};

export default RealTimeStats;