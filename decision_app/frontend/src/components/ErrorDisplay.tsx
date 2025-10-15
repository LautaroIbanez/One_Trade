import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorDisplayProps {
  error: string;
  onRetry?: () => void;
  showRetry?: boolean;
  className?: string;
}

/**
 * Componente para mostrar errores de forma amigable con opción de reintentar
 */
export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  onRetry,
  showRetry = true,
  className = ''
}) => {
  return (
    <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <AlertTriangle className="h-6 w-6 text-red-600" />
        </div>
        <div className="ml-4 flex-1">
          <h3 className="text-sm font-medium text-red-800">Error al cargar los datos</h3>
          <p className="mt-2 text-sm text-red-700">{error}</p>
          
          {showRetry && onRetry && (
            <div className="mt-4">
              <Button
                onClick={onRetry}
                variant="outline"
                className="border-red-300 text-red-700 hover:bg-red-100"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Reintentar
              </Button>
            </div>
          )}
          
          <div className="mt-4 text-xs text-red-600">
            <p className="font-semibold">Posibles soluciones:</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Verifica que el backend esté corriendo en http://localhost:8000</li>
              <li>Revisa la consola del navegador para más detalles</li>
              <li>Verifica tu conexión a internet</li>
              <li>Intenta recargar la página</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Componente para mostrar estado de carga
 */
export const LoadingDisplay: React.FC<{ message?: string; className?: string }> = ({
  message = 'Cargando datos...',
  className = ''
}) => {
  return (
    <div className={`bg-blue-50 border border-blue-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <RefreshCw className="h-6 w-6 text-blue-600 animate-spin" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-blue-800">{message}</p>
        </div>
      </div>
    </div>
  );
};

/**
 * Componente para mostrar cuando no hay datos
 */
export const EmptyDisplay: React.FC<{ message?: string; className?: string }> = ({
  message = 'No hay datos disponibles',
  className = ''
}) => {
  return (
    <div className={`bg-gray-50 border border-gray-200 rounded-lg p-6 ${className}`}>
      <div className="text-center">
        <p className="text-sm text-gray-600">{message}</p>
      </div>
    </div>
  );
};
