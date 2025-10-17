import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { ChartData } from '@/types/recommendations';

interface UseChartDataOptions {
  symbol: string;
  timeframe?: string;
  days?: number;
  autoFetch?: boolean;
}

export function useChartData({
  symbol,
  timeframe = '1d',
  days = 30,
  autoFetch = true
}: UseChartDataOptions) {
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchChartData = async () => {
    if (!symbol) {
      setError('No symbol provided');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<ChartData>(
        `/enhanced-recommendations/chart-data/${symbol}`,
        { timeframe, days }
      );

      // The API client returns the parsed JSON body directly
      setChartData(response);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Error fetching chart data';
      setError(errorMessage);
      console.error('Error fetching chart data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (autoFetch && symbol) {
      fetchChartData();
    }
  }, [symbol, timeframe, days, autoFetch]);

  return {
    chartData,
    isLoading,
    error,
    refetch: fetchChartData
  };
}

