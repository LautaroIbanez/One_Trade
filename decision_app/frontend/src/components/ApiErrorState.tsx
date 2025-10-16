import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ApiErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  retryText?: string;
  className?: string;
}

const ApiErrorState: React.FC<ApiErrorStateProps> = ({
  title = "Error",
  message,
  onRetry,
  retryText = "Retry",
  className = ""
}) => {
  return (
    <div className={`p-4 border border-red-300 rounded-lg bg-red-50 text-red-800 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5" />
          <div>
            <p className="font-medium">{title}</p>
            <p className="text-sm">{message}</p>
          </div>
        </div>
        {onRetry && (
          <Button onClick={onRetry} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            {retryText}
          </Button>
        )}
      </div>
    </div>
  );
};

export default ApiErrorState;

