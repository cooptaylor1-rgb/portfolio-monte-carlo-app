/**
 * StatTile Component - Display key metrics with optional trends
 */
import React from 'react';

export interface StatTileProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: {
    value: string;
    direction: 'up' | 'down' | 'neutral';
  };
  variant?: 'default' | 'success' | 'warning' | 'error';
  loading?: boolean;
  className?: string;
}

export const StatTile: React.FC<StatTileProps> = ({
  label,
  value,
  icon,
  trend,
  variant = 'default',
  loading = false,
  className = '',
}) => {
  const variantColors = {
    default: 'text-text-primary',
    success: 'text-status-success-base',
    warning: 'text-status-warning-base',
    error: 'text-status-error-base',
  };
  
  const trendColors = {
    up: 'text-status-success-base',
    down: 'text-status-error-base',
    neutral: 'text-text-tertiary',
  };
  
  return (
    <div className={`bg-background-elevated border border-background-border rounded-md p-5 ${className}`}>
      <div className="flex items-start justify-between mb-2">
        <p className="text-small text-text-tertiary uppercase tracking-wide font-medium">
          {label}
        </p>
        {icon && (
          <div className={`flex-shrink-0 ${variantColors[variant]}`}>
            {icon}
          </div>
        )}
      </div>
      
      {loading ? (
        <div className="h-10 bg-background-hover animate-pulse rounded" />
      ) : (
        <>
          <p className={`text-display font-display ${variantColors[variant]} mb-1`}>
            {value}
          </p>
          {trend && (
            <p className={`text-small ${trendColors[trend.direction]} font-medium`}>
              {trend.direction === 'up' && '↑ '}
              {trend.direction === 'down' && '↓ '}
              {trend.value}
            </p>
          )}
        </>
      )}
    </div>
  );
};
