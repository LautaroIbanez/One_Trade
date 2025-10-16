import React from 'react';
import { LucideIcon } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  icon?: LucideIcon;
  className?: string;
}

const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Loading...",
  icon: Icon,
  className = ""
}) => {
  return (
    <div className={`flex items-center justify-center p-8 border border-gray-200 rounded-lg bg-gray-50 ${className}`}>
      <div className="text-center">
        {Icon && (
          <Icon className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-2" />
        )}
        {!Icon && (
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
        )}
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
};

export default LoadingState;

