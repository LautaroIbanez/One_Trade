import { useState, useEffect, useCallback } from 'react';
import { apiClient, ApiError } from '../lib/api-client';
import { QuickBacktestResult, StrategyComparison, normalizeQuickBacktestResult } from '../types/backtests';

export const useBacktestsApi = () => {
  const [strategies, setStrategies] = useState<string[]>([]);
  const [symbols, setSymbols] = useState<string[]>([]);
  const [loadingStrategies, setLoadingStrategies] = useState(false);
  const [loadingSymbols, setLoadingSymbols] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStrategies = useCallback(async () => {
    setLoadingStrategies(true);
    setError(null);
    
    try {
      const data = await apiClient.get<string[]>('/backtests/strategies');
      setStrategies(data);
      return data;
    } catch (err) {
      const errorMsg = err instanceof ApiError ? err.message : 'Failed to fetch strategies';
      setError(errorMsg);
      return [];
    } finally {
      setLoadingStrategies(false);
    }
  }, []);

  const fetchSymbols = useCallback(async () => {
    setLoadingSymbols(true);
    setError(null);
    
    try {
      const data = await apiClient.get<string[]>('/backtests/symbols');
      setSymbols(data);
      return data;
    } catch (err) {
      const errorMsg = err instanceof ApiError ? err.message : 'Failed to fetch symbols';
      setError(errorMsg);
      return [];
    } finally {
      setLoadingSymbols(false);
    }
  }, []);

  const runQuickBacktest = useCallback(async (
    symbol: string, 
    strategy: string, 
    days: number, 
    initialCapital: number
  ) => {
    setError(null);
    
    try {
      const raw = await apiClient.get<QuickBacktestResult>(
        `/backtests/quick-test/${symbol}`,
        { strategy, days, initial_capital: initialCapital }
      );
      return normalizeQuickBacktestResult(raw);
    } catch (err) {
      const errorMsg = err instanceof ApiError ? err.message : 'Failed to run backtest';
      setError(errorMsg);
      throw err;
    }
  }, []);

  const compareStrategies = useCallback(async (
    symbol: string, 
    days: number, 
    initialCapital: number
  ) => {
    setError(null);
    
    try {
      const data = await apiClient.get<StrategyComparison>(
        `/backtests/compare/${symbol}`,
        { days, initial_capital: initialCapital }
      );
      return data;
    } catch (err) {
      const errorMsg = err instanceof ApiError ? err.message : 'Failed to compare strategies';
      setError(errorMsg);
      throw err;
    }
  }, []);

  const runFullBacktest = useCallback(async (backtestRequest: {
    symbol: string;
    strategy: string;
    start_date: string;
    end_date: string;
    initial_capital: number;
    params?: Record<string, any>;
  }) => {
    setError(null);
    
    try {
      const data = await apiClient.post<any>('/backtests/run', backtestRequest);
      return data;
    } catch (err) {
      const errorMsg = err instanceof ApiError ? err.message : 'Failed to run full backtest';
      setError(errorMsg);
      throw err;
    }
  }, []);

  useEffect(() => {
    fetchStrategies();
    fetchSymbols();
  }, [fetchStrategies, fetchSymbols]);

  return {
    strategies,
    symbols,
    loadingStrategies,
    loadingSymbols,
    error,
    runQuickBacktest,
    compareStrategies,
    runFullBacktest,
    refetchStrategies: fetchStrategies,
    refetchSymbols: fetchSymbols,
  };
};

