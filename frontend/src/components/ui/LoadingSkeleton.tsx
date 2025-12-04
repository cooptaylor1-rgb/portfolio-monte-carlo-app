/**
 * LoadingSkeleton - Animated loading placeholder
 * Provides visual feedback during data loading
 * 
 * Features:
 * - Animated pulse effect
 * - Multiple variants (text, circle, rectangle, card)
 * - Configurable sizes
 * - Composable for complex layouts
 * - Smooth animation using design system
 */

import React from 'react';
import { colors } from '../../theme';

export interface LoadingSkeletonProps {
  variant?: 'text' | 'circle' | 'rectangle' | 'card';
  width?: string | number;
  height?: string | number;
  className?: string;
  count?: number;
  gap?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className = '',
  count = 1,
  gap = '0.5rem',
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'text':
        return {
          height: height || '1rem',
          width: width || '100%',
          borderRadius: '0.25rem',
        };
      case 'circle':
        const size = width || height || '3rem';
        return {
          height: size,
          width: size,
          borderRadius: '50%',
        };
      case 'rectangle':
        return {
          height: height || '10rem',
          width: width || '100%',
          borderRadius: '0.5rem',
        };
      case 'card':
        return {
          height: height || '15rem',
          width: width || '100%',
          borderRadius: '0.5rem',
        };
      default:
        return {};
    }
  };

  const skeletonElement = (
    <div
      className={`animate-pulse ${className}`}
      style={{
        backgroundColor: colors.background.hover,
        ...getVariantStyles(),
      }}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );

  if (count === 1) {
    return skeletonElement;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap }}>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index}>{skeletonElement}</div>
      ))}
    </div>
  );
};

// Preset skeleton layouts
export const TableSkeleton: React.FC<{ rows?: number; columns?: number }> = ({
  rows = 5,
  columns = 4,
}) => (
  <div className="space-y-2">
    {/* Header */}
    <div className="flex gap-4">
      {Array.from({ length: columns }).map((_, i) => (
        <LoadingSkeleton key={`header-${i}`} variant="text" height="2rem" />
      ))}
    </div>
    
    {/* Rows */}
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={`row-${rowIndex}`} className="flex gap-4">
        {Array.from({ length: columns }).map((_, colIndex) => (
          <LoadingSkeleton key={`cell-${rowIndex}-${colIndex}`} variant="text" height="1.5rem" />
        ))}
      </div>
    ))}
  </div>
);

export const CardSkeleton: React.FC<{ count?: number }> = ({ count = 1 }) => (
  <div className="space-y-4">
    {Array.from({ length: count }).map((_, index) => (
      <div key={index} className="p-lg rounded-lg" style={{ backgroundColor: colors.background.elevated }}>
        <LoadingSkeleton variant="text" width="60%" height="1.5rem" className="mb-4" />
        <LoadingSkeleton variant="text" count={3} className="mb-2" />
        <div className="flex gap-4 mt-4">
          <LoadingSkeleton variant="rectangle" width="100%" height="8rem" />
        </div>
      </div>
    ))}
  </div>
);

export const ChartSkeleton: React.FC<{ height?: string }> = ({ height = '20rem' }) => (
  <div className="p-lg rounded-lg" style={{ backgroundColor: colors.background.elevated }}>
    <LoadingSkeleton variant="text" width="40%" height="1.5rem" className="mb-4" />
    <LoadingSkeleton variant="rectangle" height={height} />
    <div className="flex justify-center gap-4 mt-4">
      <LoadingSkeleton variant="text" width="6rem" height="1rem" />
      <LoadingSkeleton variant="text" width="6rem" height="1rem" />
      <LoadingSkeleton variant="text" width="6rem" height="1rem" />
    </div>
  </div>
);

export const FormSkeleton: React.FC<{ fields?: number }> = ({ fields = 4 }) => (
  <div className="space-y-4">
    {Array.from({ length: fields }).map((_, index) => (
      <div key={index}>
        <LoadingSkeleton variant="text" width="30%" height="1rem" className="mb-2" />
        <LoadingSkeleton variant="text" height="2.5rem" />
      </div>
    ))}
  </div>
);

export const DashboardSkeleton: React.FC = () => (
  <div className="space-y-6">
    {/* Header */}
    <LoadingSkeleton variant="text" width="40%" height="2rem" />
    
    {/* Stats Grid */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <CardSkeleton count={3} />
    </div>
    
    {/* Chart */}
    <ChartSkeleton />
    
    {/* Table */}
    <TableSkeleton rows={5} columns={4} />
  </div>
);

export default LoadingSkeleton;
