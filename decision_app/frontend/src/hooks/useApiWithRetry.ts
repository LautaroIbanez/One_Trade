import { useState, useCallback } from 'react';

interface RetryConfig {
  maxRetries?: number;
  retryDelay?: number;
  backoffMultiplier?: number;
}

interface UseApiWithRetryResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: () => Promise<void>;
  retry: () => Promise<void>;
}

/**
 * Hook personalizado para hacer requests con retry automático y backoff exponencial
 */
export function useApiWithRetry<T>(
  fetchFn: () => Promise<T>,
  config: RetryConfig = {}
): UseApiWithRetryResult<T> {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    backoffMultiplier = 2
  } = config;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    let currentRetry = 0;
    let currentDelay = retryDelay;

    while (currentRetry <= maxRetries) {
      try {
        const result = await fetchFn();
        setData(result);
        setLoading(false);
        setRetryCount(0);
        return;
      } catch (err) {
        console.error(`Request failed (attempt ${currentRetry + 1}/${maxRetries + 1}):`, err);
        
        if (currentRetry < maxRetries) {
          // Esperar antes de reintentar con backoff exponencial
          await new Promise(resolve => setTimeout(resolve, currentDelay));
          currentDelay *= backoffMultiplier;
          currentRetry++;
          setRetryCount(currentRetry);
        } else {
          // Se agotaron los reintentos
          const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
          setError(`Error después de ${maxRetries + 1} intentos: ${errorMessage}`);
          setLoading(false);
          break;
        }
      }
    }
  }, [fetchFn, maxRetries, retryDelay, backoffMultiplier]);

  const retry = useCallback(async () => {
    setRetryCount(0);
    await execute();
  }, [execute]);

  return {
    data,
    loading,
    error,
    execute,
    retry
  };
}

/**
 * Helper para crear funciones de fetch con manejo de errores
 */
export function createFetchFn<T>(url: string, options?: RequestInit): () => Promise<T> {
  return async () => {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data as T;
  };
}

/**
 * Hook simplificado para GET requests con retry
 */
export function useApiGet<T>(
  url: string,
  config: RetryConfig = {}
): UseApiWithRetryResult<T> {
  const fetchFn = useCallback(() => createFetchFn<T>(url)(), [url]);
  return useApiWithRetry<T>(fetchFn, config);
}
