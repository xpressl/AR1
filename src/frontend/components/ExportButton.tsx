'use client';

import React, { useState } from 'react';
import { Button, ButtonProps } from './common/Button';
import { clsx } from 'clsx';

export type ExportFormat = 'xlsx' | 'csv' | 'pdf';

export interface ExportButtonProps extends Omit<ButtonProps, 'onClick'> {
  /** Type of data to export */
  exportType: 'customers' | 'invoices' | 'aging-report' | 'payments';
  /** Query parameters for the export */
  filters?: Record<string, any>;
  /** Callback when export starts */
  onExportStart?: () => void;
  /** Callback when export completes */
  onExportComplete?: (filePath: string) => void;
  /** Callback when export fails */
  onExportError?: (error: Error) => void;
}

/**
 * ExportButton - Dropdown button for exporting data in various formats
 *
 * Supports Excel (xlsx), CSV, and PDF formats.
 * Downloads the file directly to the user's browser.
 */
export function ExportButton({
  exportType,
  filters = {},
  onExportStart,
  onExportComplete,
  onExportError,
  children = 'Export',
  variant = 'secondary',
  size = 'md',
  className,
  ...props
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleExport = async (format: ExportFormat) => {
    setShowMenu(false);
    setIsExporting(true);
    onExportStart?.();

    try {
      // Build query string from filters
      const queryParams = new URLSearchParams({
        format,
        ...filters,
      });

      // Call export API
      const response = await fetch(
        `/api/v1/export/${exportType}?${queryParams}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }

      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
        : `${exportType}_export.${format}`;

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      onExportComplete?.(filename);
    } catch (error) {
      console.error('Export error:', error);
      onExportError?.(error as Error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="relative inline-block">
      <Button
        variant={variant}
        size={size}
        className={className}
        isLoading={isExporting}
        onClick={() => setShowMenu(!showMenu)}
        rightIcon={
          <svg
            className={clsx(
              'w-4 h-4 transition-transform',
              showMenu && 'rotate-180'
            )}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        }
        {...props}
      >
        {isExporting ? 'Exporting...' : children}
      </Button>

      {/* Dropdown menu */}
      {showMenu && !isExporting && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setShowMenu(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-20">
            <div
              className="py-1"
              role="menu"
              aria-orientation="vertical"
              aria-labelledby="export-menu"
            >
              <button
                onClick={() => handleExport('xlsx')}
                className="flex items-center w-full px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900"
                role="menuitem"
              >
                <svg
                  className="w-5 h-5 mr-3 text-success-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Export to Excel
              </button>

              <button
                onClick={() => handleExport('csv')}
                className="flex items-center w-full px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900"
                role="menuitem"
              >
                <svg
                  className="w-5 h-5 mr-3 text-primary-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Export to CSV
              </button>

              <button
                onClick={() => handleExport('pdf')}
                className="flex items-center w-full px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900"
                role="menuitem"
              >
                <svg
                  className="w-5 h-5 mr-3 text-error-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                  />
                </svg>
                Export to PDF
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ExportButton;
