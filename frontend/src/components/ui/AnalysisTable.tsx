/**
 * AnalysisTable - Unified table component for all data tables
 * Replaces inconsistent table implementations with a single, reusable component
 * 
 * Features:
 * - TypeScript generics for type-safe data
 * - Multiple variants (default, striped, compact)
 * - Sticky header support
 * - Loading states with skeleton
 * - Empty states
 * - Responsive with horizontal scroll
 * - Accessible (ARIA labels, keyboard navigation)
 * - Custom column formatting
 * - Alignment support (left, center, right)
 */

import React from 'react';
import { colors, spacing } from '../../theme';

export interface Column<T> {
  key: keyof T;
  label: string;
  align?: 'left' | 'center' | 'right';
  format?: (value: any, row: T) => React.ReactNode;
  width?: string;
  headerClassName?: string;
  cellClassName?: string;
}

export interface AnalysisTableProps<T> {
  columns: Column<T>[];
  data: T[];
  variant?: 'default' | 'striped' | 'compact';
  stickyHeader?: boolean;
  caption?: string;
  emptyState?: React.ReactNode;
  loading?: boolean;
  className?: string;
  rowClassName?: (row: T, index: number) => string;
  onRowClick?: (row: T, index: number) => void;
}

export function AnalysisTable<T extends Record<string, any>>({
  columns,
  data,
  variant = 'striped',
  stickyHeader = false,
  caption,
  emptyState,
  loading = false,
  className = '',
  rowClassName,
  onRowClick,
}: AnalysisTableProps<T>) {
  // Loading skeleton
  if (loading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="h-12 bg-background-hover rounded mb-2"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 bg-background-elevated rounded mb-1"></div>
        ))}
      </div>
    );
  }

  // Empty state
  if (data.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        {emptyState || (
          <div className="text-text-tertiary">
            <p className="text-body">No data available</p>
          </div>
        )}
      </div>
    );
  }

  const getAlignmentClass = (align?: 'left' | 'center' | 'right') => {
    switch (align) {
      case 'center':
        return 'text-center';
      case 'right':
        return 'text-right';
      default:
        return 'text-left';
    }
  };

  const getRowBackgroundClass = (index: number) => {
    if (variant === 'striped') {
      return index % 2 === 0 ? 'bg-background-elevated' : 'bg-background-base';
    }
    return 'bg-background-elevated';
  };

  const getPaddingClass = () => {
    return variant === 'compact' ? 'px-md py-sm' : 'px-md py-3.5';
  };

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full border-collapse">
        {caption && (
          <caption className="text-left mb-4 text-h4 font-semibold text-text-primary">
            {caption}
          </caption>
        )}
        
        <thead className={stickyHeader ? 'sticky top-0 z-10' : ''}>
          <tr 
            className="border-b-2"
            style={{ borderColor: colors.brand.gold }}
          >
            {columns.map((col) => (
              <th
                key={String(col.key)}
                className={`${getPaddingClass()} text-micro font-semibold uppercase tracking-wider ${getAlignmentClass(col.align)} ${col.headerClassName || ''}`}
                style={{ 
                  color: colors.brand.gold,
                  width: col.width,
                  backgroundColor: stickyHeader ? colors.background.elevated : undefined,
                }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        
        <tbody>
          {data.map((row, rowIndex) => {
            const customRowClass = rowClassName ? rowClassName(row, rowIndex) : '';
            const isClickable = !!onRowClick;
            
            return (
              <tr
                key={rowIndex}
                className={`
                  border-b transition-colors
                  ${getRowBackgroundClass(rowIndex)}
                  ${isClickable ? 'cursor-pointer hover:bg-background-hover' : 'hover:bg-background-hover'}
                  ${customRowClass}
                `}
                style={{ borderColor: colors.background.border }}
                onClick={isClickable ? () => onRowClick(row, rowIndex) : undefined}
                role={isClickable ? 'button' : undefined}
                tabIndex={isClickable ? 0 : undefined}
                onKeyPress={isClickable ? (e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onRowClick(row, rowIndex);
                  }
                } : undefined}
              >
                {columns.map((col) => (
                  <td
                    key={String(col.key)}
                    className={`${getPaddingClass()} text-sm ${getAlignmentClass(col.align)} ${col.cellClassName || ''}`}
                    style={{ color: colors.text.primary }}
                  >
                    {col.format
                      ? col.format(row[col.key], row)
                      : row[col.key]}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// Helper component for common empty states
export const TableEmptyState: React.FC<{
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}> = ({ icon, title, description, action }) => (
  <div className="text-center py-12">
    {icon && <div className="mb-4 flex justify-center text-text-tertiary">{icon}</div>}
    <h3 className="text-h4 font-semibold text-text-primary mb-2">{title}</h3>
    {description && <p className="text-body text-text-tertiary mb-4">{description}</p>}
    {action && <div>{action}</div>}
  </div>
);

export default AnalysisTable;
