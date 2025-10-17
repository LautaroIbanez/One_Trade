import React, { useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, DollarSign, Zap, BarChart2 } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import { useApiWithRetry, createFetchFn } from '../hooks/useApiWithRetry';
import { ErrorDisplay, LoadingDisplay } from './ErrorDisplay';

interface StatsData {
  activeRecommendations: number;
  totalPnL: number;
  winRate: number;
  maxDrawdown: number;
  lastUpdate: string;
  momentum?: number[];
  volume?: number[];
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const RealTimeStatsImproved: React.FC = () => {
  const {
    data: stats,
    loading,
    error,
    execute,
    retry
  } = useApiWithRetry<StatsData>(
    createFetchFn<StatsData>(`${API_BASE_URL}/api/v1/stats`),
    {
      maxRetries: 3,
      retryDelay: 1000,
      backoffMultiplier: 2
    }
  );

  useEffect(() => {
    execute();
    
    // Actualizar cada 30 segundos
    const interval = setInterval(() => {
      execute();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [execute]);

  if (loading && !stats) {
    return <LoadingDisplay message="Cargando estadísticas..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} onRetry={retry} />;
  }

  if (!stats) {
    return <ErrorDisplay error="No se pudieron cargar las estadísticas" onRetry={retry} />;
  }

  const momentumData = stats.momentum ? stats.momentum.map((value, index) => ({ index, value })) : Array.from({ length: 10 }, (_, index) => ({ index, value: Math.random() * 100 - 50 }));
  const volumeData = stats.volume ? stats.volume.map((value, index) => ({ index, value })) : Array.from({ length: 10 }, (_, index) => ({ index, value: Math.random() * 100 }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Active Recommendations */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Activity className="h-8 w-8 text-blue-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">Recomendaciones Activas</p>
            <p className="text-2xl font-bold text-gray-900">{stats.activeRecommendations}</p>
          </div>
        </div>
      </div>

      {/* Total P&L */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            {stats.totalPnL >= 0 ? (
              <TrendingUp className="h-8 w-8 text-green-600" />
            ) : (
              <TrendingDown className="h-8 w-8 text-red-600" />
            )}
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">P&L Total</p>
            <p className={`text-2xl font-bold ${stats.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {stats.totalPnL >= 0 ? '+' : ''}{stats.totalPnL.toFixed(2)}%
            </p>
          </div>
        </div>
      </div>

      {/* Win Rate */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <DollarSign className="h-8 w-8 text-blue-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">Tasa de Éxito</p>
            <p className="text-2xl font-bold text-gray-900">{stats.winRate.toFixed(1)}%</p>
          </div>
        </div>
      </div>

      {/* Max Drawdown */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <TrendingDown className="h-8 w-8 text-red-600" />
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">Drawdown Máximo</p>
            <p className="text-2xl font-bold text-red-600">{stats.maxDrawdown.toFixed(2)}%</p>
          </div>
        </div>
      </div>

      {/* Momentum Sparkline */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            <Zap className="h-5 w-5 text-purple-600 mr-2" />
            <p className="text-sm font-medium text-gray-500">Momentum</p>
          </div>
        </div>
        <div className="h-12">
          <ResponsiveContainer width="99%" height="100%">
            <LineChart data={momentumData}>
              <Line type="monotone" dataKey="value" stroke="#9333ea" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="text-xs text-gray-400 mt-2">Últimos 10 períodos</p>
      </div>

      {/* Volume Sparkline */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            <BarChart2 className="h-5 w-5 text-orange-600 mr-2" />
            <p className="text-sm font-medium text-gray-500">Volumen</p>
          </div>
        </div>
        <div className="h-12">
          <ResponsiveContainer width="99%" height="100%">
            <LineChart data={volumeData}>
              <Line type="monotone" dataKey="value" stroke="#ea580c" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="text-xs text-gray-400 mt-2">Actividad reciente</p>
      </div>
    </div>
  );
};

export default RealTimeStatsImproved;
