import { useState } from 'react';
import { EnhancedRecommendation } from '../types/recommendations';
import { apiClient, ApiError } from '../lib/api-client';

export const useRecommendations = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getRecommendation = async (
    symbol: string,
    timeframe: string = '1d',
    days: number = 30
  ): Promise<EnhancedRecommendation> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await apiClient.get<EnhancedRecommendation>(
        `/enhanced-recommendations/generate/${symbol}`,
        { timeframe, days }
      );
      return data;
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const getSupportedSymbols = async (): Promise<string[]> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await apiClient.get<string[]>('/enhanced-recommendations/supported-symbols');
      return data;
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Unknown error';
      setError(errorMessage);
      // Return default symbols if API fails
      return ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'];
    } finally {
      setIsLoading(false);
    }
  };

  const getBatchRecommendations = async (
    symbols: string[],
    timeframe: string = '1d',
    days: number = 30
  ): Promise<Record<string, EnhancedRecommendation>> => {
    setIsRefreshing(true);
    setError(null);
    
    try {
      const symbolsStr = symbols.join(',');
      const data = await apiClient.get<Record<string, EnhancedRecommendation>>(
        `/enhanced-recommendations/batch/${symbolsStr}`,
        { timeframe, days }
      );
      return data;
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setIsRefreshing(false);
    }
  };

  const refreshRecommendations = async (
    symbols: string[],
    timeframe: string = '1d',
    days: number = 30
  ): Promise<Record<string, EnhancedRecommendation>> => {
    return getBatchRecommendations(symbols, timeframe, days);
  };

  return {
    getRecommendation,
    getSupportedSymbols,
    getBatchRecommendations,
    refreshRecommendations,
    isLoading,
    isRefreshing,
    error,
  };
};

