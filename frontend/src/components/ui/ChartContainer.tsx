/**
 * ChartContainer Component
 * Standardized wrapper for all data visualizations with loading states,
 * empty states, headers, and consistent styling
 */
import React from 'react';
import { Card } from './Card';
import { LoadingSkeleton } from './LoadingSkeleton';
import { EmptyState } from './EmptyState';
import { BarChart3, Info } from 'lucide-react';

export interface ChartContainerProps {
  /** Chart title displayed in header */
  title: string;
  
  /** Optional subtitle/description */
  subtitle?: string;
  
  /** The chart component to render */
  children: React.ReactNode;
  
  /** Loading state */
  isLoading?: boolean;
  
  /** Empty state - show when no data available */
  isEmpty?: boolean;
  
  /** Empty state message */
  emptyMessage?: string;
  
  /** Optional action button in header (e.g., export, settings) */
  action?: React.ReactNode;
  
  /** Chart height for loading skeleton */
  height?: number;
  
  /** Additional info/help text with tooltip */
  helpText?: string;
  
  /** Custom className for container */
  className?: string;
}

export const ChartContainer: React.FC<ChartContainerProps> = ({
  title,
  subtitle,
  children,
  isLoading = false,
  isEmpty = false,
  emptyMessage = 'No data available',
  action,
  height = 400,
  helpText,
  className = '',
}) => {
  return (
    <Card className={className}>
      {/* Chart Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-h4 font-semibold text-text-primary truncate">
              {title}
            </h3>
            {helpText && (
              <div className="group relative">
                <Info 
                  size={16} 
                  className="text-text-tertiary hover:text-accent-gold transition-colors cursor-help"
                />
                <div className="hidden group-hover:block absolute left-0 top-6 z-tooltip w-64 p-3 bg-background-elevated border border-background-border rounded-md shadow-lg">
                  <p className="text-small text-text-secondary">{helpText}</p>
                </div>
              </div>
            )}
          </div>
          {subtitle && (
            <p className="text-small text-text-tertiary">{subtitle}</p>
          )}
        </div>
        {action && (
          <div className="ml-4 flex-shrink-0">
            {action}
          </div>
        )}
      </div>

      {/* Chart Content */}
      <div className="w-full">
        {isLoading ? (
          <LoadingSkeleton 
            variant="card" 
            height={height}
            count={1}
          />
        ) : isEmpty ? (
          <div style={{ height }}>
            <EmptyState
              icon={<BarChart3 size={48} />}
              title="No Data Available"
              description={emptyMessage}
            />
          </div>
        ) : (
          <div role="img" aria-label={`${title} chart`}>
            {children}
          </div>
        )}
      </div>
    </Card>
  );
};

/**
 * ChartLegend Component
 * Reusable legend for charts with consistent styling
 */
export interface LegendItem {
  label: string;
  color: string;
  value?: string | number;
  dotType?: 'solid' | 'dashed';
}

export interface ChartLegendProps {
  items: LegendItem[];
  className?: string;
}

export const ChartLegend: React.FC<ChartLegendProps> = ({ items, className = '' }) => {
  return (
    <div className={`flex flex-wrap gap-4 ${className}`}>
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            {item.dotType === 'dashed' ? (
              <svg width="20" height="4" className="flex-shrink-0">
                <line
                  x1="0"
                  y1="2"
                  x2="20"
                  y2="2"
                  stroke={item.color}
                  strokeWidth="2"
                  strokeDasharray="4 2"
                />
              </svg>
            ) : (
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: item.color }}
              />
            )}
            <span className="text-small text-text-secondary">{item.label}</span>
          </div>
          {item.value !== undefined && (
            <span className="text-small font-semibold text-text-primary">
              {item.value}
            </span>
          )}
        </div>
      ))}
    </div>
  );
};

/**
 * ChartTooltipContent Component
 * Standardized tooltip content for consistent chart tooltips
 */
export interface TooltipItem {
  label: string;
  value: string | number;
  color?: string;
}

export interface ChartTooltipContentProps {
  title?: string;
  items: TooltipItem[];
}

export const ChartTooltipContent: React.FC<ChartTooltipContentProps> = ({
  title,
  items,
}) => {
  return (
    <div className="bg-background-elevated border border-background-border rounded-md shadow-lg p-3 min-w-[150px]">
      {title && (
        <p className="text-small font-semibold text-text-primary mb-2 border-b border-background-border pb-2">
          {title}
        </p>
      )}
      <div className="space-y-1.5">
        {items.map((item, index) => (
          <div key={index} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              {item.color && (
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: item.color }}
                />
              )}
              <span className="text-small text-text-secondary">{item.label}</span>
            </div>
            <span className="text-small font-semibold text-text-primary">
              {item.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
