'use client';

import React, { useState, useMemo, useCallback } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export type SortDirection = 'asc' | 'desc' | null;

export interface TableColumn<T> {
  /** Unique key for the column */
  key: string;
  /** Header text */
  header: string;
  /** Column width (CSS width value) */
  width?: string;
  /** Whether column is sortable */
  sortable?: boolean;
  /** Text alignment */
  align?: 'left' | 'center' | 'right';
  /** Custom render function */
  render?: (value: unknown, row: T, rowIndex: number) => React.ReactNode;
  /** Accessor function to get value from row */
  accessor?: (row: T) => unknown;
}

export interface TableProps<T extends Record<string, unknown>> {
  /** Column definitions */
  columns: TableColumn<T>[];
  /** Data rows */
  data: T[];
  /** Unique key field for each row */
  rowKey: keyof T | ((row: T) => string);
  /** Currently selected row keys */
  selectedRows?: string[];
  /** Enable row selection */
  selectable?: boolean;
  /** Row selection change handler */
  onSelectionChange?: (selectedKeys: string[]) => void;
  /** Row click handler */
  onRowClick?: (row: T) => void;
  /** Current sort column */
  sortColumn?: string;
  /** Current sort direction */
  sortDirection?: SortDirection;
  /** Sort change handler */
  onSort?: (column: string, direction: SortDirection) => void;
  /** Enable client-side sorting */
  clientSort?: boolean;
  /** Loading state */
  isLoading?: boolean;
  /** Empty state message or component */
  emptyMessage?: React.ReactNode;
  /** Sticky header */
  stickyHeader?: boolean;
  /** Max height for scrollable table */
  maxHeight?: string;
  /** Additional table class */
  className?: string;
  /** Additional wrapper class */
  wrapperClassName?: string;
}

/**
 * Sortable data table component
 * Supports sorting, selection, and custom cell rendering
 */
export function Table<T extends Record<string, unknown>>({
  columns,
  data,
  rowKey,
  selectedRows = [],
  selectable = false,
  onSelectionChange,
  onRowClick,
  sortColumn,
  sortDirection,
  onSort,
  clientSort = false,
  isLoading = false,
  emptyMessage = 'No data available',
  stickyHeader = false,
  maxHeight,
  className,
  wrapperClassName,
}: TableProps<T>) {
  // Internal sort state for client-side sorting
  const [internalSortColumn, setInternalSortColumn] = useState<string | null>(null);
  const [internalSortDirection, setInternalSortDirection] = useState<SortDirection>(null);

  // Use internal or external sort state
  const activeSortColumn = clientSort ? internalSortColumn : sortColumn;
  const activeSortDirection = clientSort ? internalSortDirection : sortDirection;

  // Get row key value
  const getRowKey = useCallback(
    (row: T): string => {
      if (typeof rowKey === 'function') {
        return rowKey(row);
      }
      return String(row[rowKey]);
    },
    [rowKey]
  );

  // Handle sort click
  const handleSort = useCallback(
    (column: string) => {
      let newDirection: SortDirection;

      if (activeSortColumn === column) {
        if (activeSortDirection === 'asc') {
          newDirection = 'desc';
        } else if (activeSortDirection === 'desc') {
          newDirection = null;
        } else {
          newDirection = 'asc';
        }
      } else {
        newDirection = 'asc';
      }

      if (clientSort) {
        setInternalSortColumn(newDirection ? column : null);
        setInternalSortDirection(newDirection);
      } else if (onSort) {
        onSort(column, newDirection);
      }
    },
    [activeSortColumn, activeSortDirection, clientSort, onSort]
  );

  // Handle row selection
  const handleSelectAll = useCallback(
    (checked: boolean) => {
      if (onSelectionChange) {
        onSelectionChange(checked ? data.map(getRowKey) : []);
      }
    },
    [data, getRowKey, onSelectionChange]
  );

  const handleSelectRow = useCallback(
    (key: string, checked: boolean) => {
      if (onSelectionChange) {
        if (checked) {
          onSelectionChange([...selectedRows, key]);
        } else {
          onSelectionChange(selectedRows.filter((k) => k !== key));
        }
      }
    },
    [selectedRows, onSelectionChange]
  );

  // Sort data if client-side sorting enabled
  const sortedData = useMemo(() => {
    if (!clientSort || !internalSortColumn || !internalSortDirection) {
      return data;
    }

    const column = columns.find((c) => c.key === internalSortColumn);
    if (!column) return data;

    return [...data].sort((a, b) => {
      const aValue = column.accessor ? column.accessor(a) : a[internalSortColumn];
      const bValue = column.accessor ? column.accessor(b) : b[internalSortColumn];

      let comparison = 0;
      if (aValue == null && bValue == null) comparison = 0;
      else if (aValue == null) comparison = 1;
      else if (bValue == null) comparison = -1;
      else if (typeof aValue === 'string' && typeof bValue === 'string') {
        comparison = aValue.localeCompare(bValue);
      } else if (typeof aValue === 'number' && typeof bValue === 'number') {
        comparison = aValue - bValue;
      } else {
        comparison = String(aValue).localeCompare(String(bValue));
      }

      return internalSortDirection === 'desc' ? -comparison : comparison;
    });
  }, [data, columns, clientSort, internalSortColumn, internalSortDirection]);

  // Check if all rows are selected
  const allSelected = data.length > 0 && selectedRows.length === data.length;
  const someSelected = selectedRows.length > 0 && selectedRows.length < data.length;

  // Get cell value
  const getCellValue = (row: T, column: TableColumn<T>, rowIndex: number): React.ReactNode => {
    const value = column.accessor ? column.accessor(row) : row[column.key];

    if (column.render) {
      return column.render(value, row, rowIndex);
    }

    if (value == null) return '-';
    return String(value);
  };

  return (
    <div
      className={twMerge(
        clsx('overflow-auto', maxHeight && 'overflow-y-auto'),
        wrapperClassName
      )}
      style={{ maxHeight }}
    >
      <table className={twMerge('w-full text-sm text-left', className)}>
        {/* Header */}
        <thead
          className={clsx(
            'bg-neutral-50 border-b-2 border-neutral-200',
            stickyHeader && 'sticky top-0 z-10'
          )}
        >
          <tr>
            {/* Selection checkbox */}
            {selectable && (
              <th className="w-12 px-4 py-3">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el) => {
                    if (el) el.indeterminate = someSelected;
                  }}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                  className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  aria-label="Select all rows"
                />
              </th>
            )}

            {/* Column headers */}
            {columns.map((column) => (
              <th
                key={column.key}
                className={clsx(
                  'px-4 py-3 font-semibold text-neutral-700 whitespace-nowrap',
                  column.sortable && 'cursor-pointer select-none hover:bg-neutral-100',
                  column.align === 'center' && 'text-center',
                  column.align === 'right' && 'text-right'
                )}
                style={{ width: column.width }}
                onClick={column.sortable ? () => handleSort(column.key) : undefined}
              >
                <div
                  className={clsx(
                    'inline-flex items-center gap-1',
                    column.align === 'right' && 'flex-row-reverse'
                  )}
                >
                  <span>{column.header}</span>
                  {column.sortable && (
                    <SortIcon
                      active={activeSortColumn === column.key}
                      direction={
                        activeSortColumn === column.key ? activeSortDirection : null
                      }
                    />
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>

        {/* Body */}
        <tbody>
          {isLoading ? (
            // Loading skeleton
            Array.from({ length: 5 }).map((_, index) => (
              <tr key={index}>
                {selectable && (
                  <td className="px-4 py-3">
                    <div className="w-4 h-4 bg-neutral-200 rounded animate-pulse" />
                  </td>
                )}
                {columns.map((column) => (
                  <td key={column.key} className="px-4 py-3">
                    <div className="h-4 bg-neutral-200 rounded animate-pulse" />
                  </td>
                ))}
              </tr>
            ))
          ) : sortedData.length === 0 ? (
            // Empty state
            <tr>
              <td
                colSpan={columns.length + (selectable ? 1 : 0)}
                className="px-4 py-12 text-center text-neutral-500"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            // Data rows
            sortedData.map((row, rowIndex) => {
              const key = getRowKey(row);
              const isSelected = selectedRows.includes(key);

              return (
                <tr
                  key={key}
                  className={clsx(
                    'border-b border-neutral-100 transition-colors',
                    isSelected && 'bg-primary-50',
                    onRowClick && 'cursor-pointer hover:bg-neutral-50',
                    !isSelected && !onRowClick && 'hover:bg-neutral-50'
                  )}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                >
                  {selectable && (
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => handleSelectRow(key, e.target.checked)}
                        className="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                        aria-label={`Select row ${key}`}
                      />
                    </td>
                  )}
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={clsx(
                        'px-4 py-3',
                        column.align === 'center' && 'text-center',
                        column.align === 'right' && 'text-right'
                      )}
                    >
                      {getCellValue(row, column, rowIndex)}
                    </td>
                  ))}
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}

// Sort direction icon
function SortIcon({
  active,
  direction,
}: {
  active: boolean;
  direction: SortDirection;
}) {
  return (
    <span className={clsx('flex flex-col', !active && 'opacity-40')}>
      <svg
        className={clsx(
          'w-3 h-3 -mb-1',
          active && direction === 'asc' ? 'text-primary-600' : 'text-neutral-400'
        )}
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path d="M10 3l7 7H3l7-7z" />
      </svg>
      <svg
        className={clsx(
          'w-3 h-3',
          active && direction === 'desc' ? 'text-primary-600' : 'text-neutral-400'
        )}
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path d="M10 17l-7-7h14l-7 7z" />
      </svg>
    </span>
  );
}

// Pagination component
export interface PaginationProps {
  /** Current page (1-indexed) */
  currentPage: number;
  /** Total number of pages */
  totalPages: number;
  /** Total items count */
  totalItems?: number;
  /** Items per page */
  pageSize?: number;
  /** Page change handler */
  onPageChange: (page: number) => void;
  /** Page size change handler */
  onPageSizeChange?: (pageSize: number) => void;
  /** Available page sizes */
  pageSizeOptions?: number[];
  className?: string;
}

export function Pagination({
  currentPage,
  totalPages,
  totalItems,
  pageSize,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 25, 50, 100],
  className,
}: PaginationProps) {
  // Generate page numbers to display
  const pageNumbers = useMemo(() => {
    const pages: (number | 'ellipsis')[] = [];
    const maxVisible = 7;

    if (totalPages <= maxVisible) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    pages.push(1);

    if (currentPage > 3) {
      pages.push('ellipsis');
    }

    const start = Math.max(2, currentPage - 1);
    const end = Math.min(totalPages - 1, currentPage + 1);

    for (let i = start; i <= end; i++) {
      if (!pages.includes(i)) {
        pages.push(i);
      }
    }

    if (currentPage < totalPages - 2) {
      pages.push('ellipsis');
    }

    if (!pages.includes(totalPages)) {
      pages.push(totalPages);
    }

    return pages;
  }, [currentPage, totalPages]);

  return (
    <div
      className={twMerge(
        'flex items-center justify-between gap-4 px-4 py-3 border-t border-neutral-200',
        className
      )}
    >
      {/* Items info */}
      <div className="text-sm text-neutral-500">
        {totalItems !== undefined && pageSize !== undefined && (
          <>
            Showing {Math.min((currentPage - 1) * pageSize + 1, totalItems)} to{' '}
            {Math.min(currentPage * pageSize, totalItems)} of {totalItems} results
          </>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* Page size selector */}
        {onPageSizeChange && pageSize && (
          <div className="flex items-center gap-2">
            <label htmlFor="pageSize" className="text-sm text-neutral-500">
              Show
            </label>
            <select
              id="pageSize"
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              className="rounded border-neutral-300 text-sm focus:border-primary-500 focus:ring-primary-500"
            >
              {pageSizeOptions.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Page navigation */}
        <nav className="flex items-center gap-1" aria-label="Pagination">
          {/* Previous button */}
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className={clsx(
              'px-2 py-1 rounded text-sm font-medium',
              currentPage === 1
                ? 'text-neutral-300 cursor-not-allowed'
                : 'text-neutral-600 hover:bg-neutral-100'
            )}
            aria-label="Previous page"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          {/* Page numbers */}
          {pageNumbers.map((page, index) =>
            page === 'ellipsis' ? (
              <span key={`ellipsis-${index}`} className="px-2 py-1 text-neutral-400">
                ...
              </span>
            ) : (
              <button
                key={page}
                onClick={() => onPageChange(page)}
                className={clsx(
                  'min-w-[2rem] px-2 py-1 rounded text-sm font-medium',
                  currentPage === page
                    ? 'bg-primary-600 text-white'
                    : 'text-neutral-600 hover:bg-neutral-100'
                )}
                aria-current={currentPage === page ? 'page' : undefined}
              >
                {page}
              </button>
            )
          )}

          {/* Next button */}
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className={clsx(
              'px-2 py-1 rounded text-sm font-medium',
              currentPage === totalPages
                ? 'text-neutral-300 cursor-not-allowed'
                : 'text-neutral-600 hover:bg-neutral-100'
            )}
            aria-label="Next page"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </nav>
      </div>
    </div>
  );
}

export default Table;
