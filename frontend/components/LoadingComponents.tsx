import React from 'react';
import { Loader2, RefreshCw } from 'lucide-react';

// Skeleton loader for cards
export const CardSkeleton: React.FC = () => (
  <div className="animate-pulse">
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
        <div className="h-8 w-8 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
      </div>
      <div className="space-y-3">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
      </div>
    </div>
  </div>
);

// Table skeleton loader
export const TableSkeleton: React.FC = () => (
  <div className="animate-pulse">
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
      </div>
      <div className="p-6 space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex items-center space-x-4">
            <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
            <div className="h-8 w-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// Loading spinner component
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <Loader2 className={`animate-spin ${sizeClasses[size]} ${className}`} />
  );
};

// Full page loading component
export const PageLoader: React.FC = () => (
  <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
    <div className="text-center">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-blue-200 dark:border-blue-800 rounded-full animate-spin border-t-blue-600 dark:border-t-blue-400"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 bg-blue-600 dark:bg-blue-400 rounded-full animate-pulse"></div>
        </div>
      </div>
      <h2 className="mt-4 text-lg font-semibold text-gray-900 dark:text-white">
        Loading YouTube Automation Platform
      </h2>
      <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
        Please wait while we prepare your dashboard...
      </p>
    </div>
  </div>
);

// Button loading state
interface LoadingButtonProps {
  loading?: boolean;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'outline';
}

export const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  children,
  className = '',
  onClick,
  disabled = false,
  variant = 'primary'
}) => {
  const baseClasses = 'inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors';
  
  const variantClasses = {
    primary: 'border-transparent text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 disabled:bg-blue-400',
    secondary: 'border-transparent text-blue-700 bg-blue-100 hover:bg-blue-200 focus:ring-blue-500 disabled:bg-blue-50',
    outline: 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-blue-500 disabled:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700'
  };

  return (
    <button
      type="button"
      disabled={disabled || loading}
      onClick={onClick}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
    >
      {loading && (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      )}
      {children}
    </button>
  );
};

// Progress bar component
interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  showPercentage?: boolean;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  className = '',
  showPercentage = false,
  color = 'blue'
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500'
  };

  return (
    <div className={`w-full ${className}`}>
      {showPercentage && (
        <div className="flex justify-between mb-1">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Progress</span>
          <span className="text-sm text-gray-500 dark:text-gray-400">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ease-in-out ${colorClasses[color]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

// Pulse loading for avatars/images
export const AvatarSkeleton: React.FC = () => (
  <div className="animate-pulse">
    <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
  </div>
);

// Loading state for lists
export const ListSkeleton: React.FC<{ items?: number }> = ({ items = 3 }) => (
  <div className="animate-pulse space-y-4">
    {[...Array(items)].map((_, i) => (
      <div key={i} className="flex items-center space-x-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
        </div>
        <div className="w-20 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    ))}
  </div>
);

// Content loading placeholder
interface ContentPlaceholderProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export const ContentPlaceholder: React.FC<ContentPlaceholderProps> = ({
  icon,
  title,
  description,
  action
}) => (
  <div className="text-center py-12">
    {icon && (
      <div className="mx-auto mb-4 text-gray-400 dark:text-gray-500">
        {icon}
      </div>
    )}
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
      {title}
    </h3>
    <p className="text-gray-500 dark:text-gray-400 mb-4 max-w-sm mx-auto">
      {description}
    </p>
    {action}
  </div>
);

// Loading overlay
interface LoadingOverlayProps {
  show: boolean;
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  show,
  message = 'Loading...'
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl">
        <div className="flex items-center space-x-3">
          <LoadingSpinner size="md" className="text-blue-600" />
          <span className="text-gray-900 dark:text-white font-medium">{message}</span>
        </div>
      </div>
    </div>
  );
};