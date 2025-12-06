/**
 * Table Component
 * Responsive data table with sorting, pagination, and accessibility
 */
import React, { useState } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';
import { Button } from './Button';

export interface TableColumn<T = any> {
  /** Column key (must match data object key) */
  key: string;
  
  /** Column header label */
  label: string;
  
  /** Align content (default: left) */
  align?: 'left' | 'center' | 'right';
  
  /** Enable sorting for this column */
  sortable?: boolean;
  
  /** Custom render function */
  render?: (value: any, row: T, index: number) => React.ReactNode;
  
  /** Column width (CSS value) */
  width?: string;
  
  /** Hide on mobile */
  hideOnMobile?: boolean;
}

export interface TableProps<T = any> {
  /** Table columns configuration */
  columns: TableColumn<T>[];
  
  /** Table data rows */
  data: T[];
  
  /** Enable striped rows */
  striped?: boolean;
  
  /** Enable hover effect */
  hoverable?: boolean;
  
  /** Loading state */
  isLoading?: boolean;
  
  /** Empty state message */
  emptyMessage?: string;
  
  /** Enable pagination */
  pagination?: boolean;
  
  /** Rows per page (default: 10) */
  pageSize?: number;
  
  /** Sticky header */
  stickyHeader?: boolean;
  
  /** Custom className */
  className?: string;
  
  /** Row click handler */
  onRowClick?: (row: T, index: number) => void;
}

export const Table = <T extends Record<string, any>>({
  columns,
  data,
  striped = false,
  hoverable = true,
  isLoading = false,
  emptyMessage = 'No data available',
  pagination = false,
  pageSize = 10,
  stickyHeader = false,
  className = '',
  onRowClick,
}: TableProps<T>) => {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);

  // Sorting logic
  const sortedData = React.useMemo(() => {
    if (!sortKey) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];

      if (aVal === bVal) return 0;

      const comparison = aVal < bVal ? -1 : 1;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortKey, sortDirection]);

  // Pagination logic
  const paginatedData = React.useMemo(() => {
    if (!pagination) return sortedData;

    const startIndex = (currentPage - 1) * pageSize;
    return sortedData.slice(startIndex, startIndex + pageSize);
  }, [sortedData, pagination, currentPage, pageSize]);

  const totalPages = Math.ceil(sortedData.length / pageSize);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className={className}>
      {/* Table Container with horizontal scroll */}
      <div className="overflow-x-auto border border-background-border rounded-md">
        <table className="w-full min-w-[640px]">
          {/* Table Header */}
          <thead
            className={`bg-background-hover border-b-2 border-background-border ${
              stickyHeader ? 'sticky top-0 z-10' : ''
            }`}
          >
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`
                    px-4 py-3 text-left text-small font-semibold text-text-primary uppercase tracking-wider
                    ${column.align === 'center' ? 'text-center' : ''}
                    ${column.align === 'right' ? 'text-right' : ''}
                    ${column.hideOnMobile ? 'hidden md:table-cell' : ''}
                    ${column.sortable ? 'cursor-pointer select-none hover:bg-background-base transition-colors' : ''}
                  `}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className="flex items-center gap-2">
                    <span>{column.label}</span>
                    {column.sortable && (
                      <span className="text-text-tertiary">
                        {sortKey === column.key ? (
                          sortDirection === 'asc' ? (
                            <ChevronUp size={16} />
                          ) : (
                            <ChevronDown size={16} />
                          )
                        ) : (
                          <ChevronsUpDown size={16} />
                        )}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>

          {/* Table Body */}
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center">
                  <div className="flex items-center justify-center gap-2 text-text-secondary">
                    <div className="w-5 h-5 border-2 border-accent-gold border-t-transparent rounded-full animate-spin" />
                    <span>Loading...</span>
                  </div>
                </td>
              </tr>
            ) : paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-text-secondary">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paginatedData.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className={`
                    border-b border-background-border last:border-b-0
                    ${striped && rowIndex % 2 === 1 ? 'bg-background-hover/50' : ''}
                    ${hoverable ? 'hover:bg-background-hover transition-colors' : ''}
                    ${onRowClick ? 'cursor-pointer' : ''}
                  `}
                  onClick={() => onRowClick?.(row, rowIndex)}
                >
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={`
                        px-4 py-3 text-body text-text-secondary
                        ${column.align === 'center' ? 'text-center' : ''}
                        ${column.align === 'right' ? 'text-right' : ''}
                        ${column.hideOnMobile ? 'hidden md:table-cell' : ''}
                      `}
                    >
                      {column.render
                        ? column.render(row[column.key], row, rowIndex)
                        : row[column.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 px-2">
          <div className="text-small text-text-tertiary">
            Showing {(currentPage - 1) * pageSize + 1} to{' '}
            {Math.min(currentPage * pageSize, sortedData.length)} of{' '}
            {sortedData.length} results
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="secondary"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            
            {/* Page numbers */}
            <div className="flex items-center gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter((page) => {
                  // Show first, last, current, and adjacent pages
                  return (
                    page === 1 ||
                    page === totalPages ||
                    Math.abs(page - currentPage) <= 1
                  );
                })
                .map((page, index, array) => {
                  // Add ellipsis
                  if (index > 0 && page - array[index - 1] > 1) {
                    return (
                      <React.Fragment key={`ellipsis-${page}`}>
                        <span className="px-2 text-text-tertiary">...</span>
                        <button
                          onClick={() => handlePageChange(page)}
                          className={`
                            w-8 h-8 rounded text-small font-medium transition-colors
                            ${
                              page === currentPage
                                ? 'bg-accent-gold text-background-base'
                                : 'text-text-secondary hover:bg-background-hover'
                            }
                          `}
                        >
                          {page}
                        </button>
                      </React.Fragment>
                    );
                  }

                  return (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`
                        w-8 h-8 rounded text-small font-medium transition-colors
                        ${
                          page === currentPage
                            ? 'bg-accent-gold text-background-base'
                            : 'text-text-secondary hover:bg-background-hover'
                        }
                      `}
                    >
                      {page}
                    </button>
                  );
                })}
            </div>

            <Button
              size="sm"
              variant="secondary"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
