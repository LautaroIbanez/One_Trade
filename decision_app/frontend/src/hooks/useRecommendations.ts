import { useState } from 'react';
import { EnhancedRecommendation } from '../types/recommendations';

const API_BASE_URL = 'http://localhost:8001/api/v1';

export const useRecommendations = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getRecommendation = async (
    symbol: string,
    timeframe: string = '1d',
    days: number = 30
  ): Promise<EnhancedRecommendation> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/enhanced-recommendations/${symbol}?timeframe=${timeframe}&days=${days}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
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
      const response = await fetch(
        `${API_BASE_URL}/enhanced-recommendations/supported-symbols`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
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
    setIsLoading(true);
    setError(null);
    
    try {
      const symbolsStr = symbols.join(',');
      const response = await fetch(
        `${API_BASE_URL}/enhanced-recommendations/batch/${symbolsStr}?timeframe=${timeframe}&days=${days}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    getRecommendation,
    getSupportedSymbols,
    getBatchRecommendations,
    isLoading,
    error,
  };
};

