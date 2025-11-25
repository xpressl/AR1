'use client';

import React, { useState } from 'react';
import { Button } from './common/Button';
import { clsx } from 'clsx';

export type BatchAction =
  | 'send-emails'
  | 'assign-tasks'
  | 'update-status'
  | 'add-notes'
  | 'export';

export interface BatchActionToolbarProps {
  /** Number of selected items */
  selectedCount: number;
  /** IDs of selected items */
  selectedIds: string[];
  /** Callback to clear selection */
  onClearSelection: () => void;
  /** Callback when batch action is triggered */
  onBatchAction: (action: BatchAction, selectedIds: string[]) => void;
  /** Available actions (defaults to all) */
  availableActions?: BatchAction[];
  className?: string;
}

/**
 * BatchActionToolbar - Toolbar for performing bulk operations on selected items
 *
 * Appears when items are selected, provides quick access to batch operations.
 */
export function BatchActionToolbar({
  selectedCount,
  selectedIds,
  onClearSelection,
  onBatchAction,
  availableActions = [
    'send-emails',
    'assign-tasks',
    'update-status',
    'add-notes',
    'export',
  ],
  className,
}: BatchActionToolbarProps) {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleAction = async (action: BatchAction) => {
    setIsProcessing(true);
    try {
      await onBatchAction(action, selectedIds);
    } finally {
      setIsProcessing(false);
    }
  };

  if (selectedCount === 0) {
    return null;
  }

  return (
    <div
      className={clsx(
        'sticky top-0 z-10',
        'bg-primary-50 border-b-2 border-primary-200',
        'px-4 py-3',
        'shadow-sm',
        className
      )}
    >
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Selection info */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-semibold">
                {selectedCount}
              </span>
            </div>
            <span className="ml-3 text-sm font-medium text-neutral-900">
              {selectedCount} {selectedCount === 1 ? 'item' : 'items'} selected
            </span>
          </div>

          <button
            onClick={onClearSelection}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Clear selection
          </button>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-2">
          {availableActions.includes('send-emails') && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handleAction('send-emails')}
              isLoading={isProcessing}
              leftIcon={
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              }
            >
              Send Emails
            </Button>
          )}

          {availableActions.includes('assign-tasks') && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handleAction('assign-tasks')}
              isLoading={isProcessing}
              leftIcon={
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              }
            >
              Assign Tasks
            </Button>
          )}

          {availableActions.includes('update-status') && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handleAction('update-status')}
              isLoading={isProcessing}
              leftIcon={
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
              }
            >
              Update Status
            </Button>
          )}

          {availableActions.includes('add-notes') && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handleAction('add-notes')}
              isLoading={isProcessing}
              leftIcon={
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              }
            >
              Add Notes
            </Button>
          )}

          {availableActions.includes('export') && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handleAction('export')}
              isLoading={isProcessing}
              leftIcon={
                <svg
                  className="w-4 h-4"
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
              }
            >
              Export Selected
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

export default BatchActionToolbar;
