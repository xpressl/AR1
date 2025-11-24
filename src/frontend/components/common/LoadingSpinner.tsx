'use client';

import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export type SpinnerSize = 'sm' | 'md' | 'lg' | 'xl';

export interface LoadingSpinnerProps {
  /** Spinner size */
  size?: SpinnerSize;
  /** Show loading text */
  text?: string;
  /** Center spinner in container */
  center?: boolean;
  /** Full screen overlay */
  fullScreen?: boolean;
  /** Custom color */
  color?: string;
  className?: string;
}

const sizeStyles: Record<SpinnerSize, { spinner: string; text: string }> = {
  sm: { spinner: 'w-4 h-4', text: 'text-xs' },
  md: { spinner: 'w-6 h-6', text: 'text-sm' },
  lg: { spinner: 'w-8 h-8', text: 'text-base' },
  xl: { spinner: 'w-12 h-12', text: 'text-lg' },
};

/**
 * Loading spinner component for async operations
 */
export function LoadingSpinner({
  size = 'md',
  text,
  center = false,
  fullScreen = false,
  color,
  className,
}: LoadingSpinnerProps) {
  const spinner = (
    <div
      className={twMerge(
        clsx(
          'flex flex-col items-center justify-center gap-2',
          center && 'absolute inset-0',
          fullScreen && 'fixed inset-0 z-50 bg-white/80 backdrop-blur-sm',
          className
        )
      )}
      role="status"
      aria-label={text || 'Loading'}
    >
      <svg
        className={clsx('animate-spin', sizeStyles[size].spinner, color || 'text-primary-600')}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {text && (
        <span className={clsx('text-neutral-600 font-medium', sizeStyles[size].text)}>
          {text}
        </span>
      )}
    </div>
  );

  return spinner;
}

// Inline loading indicator (for buttons, etc.)
export interface InlineLoaderProps {
  size?: 'sm' | 'md';
  className?: string;
}

export function InlineLoader({ size = 'sm', className }: InlineLoaderProps) {
  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
  };

  return (
    <svg
      className={twMerge(clsx('animate-spin', sizeClasses[size], className))}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

// Skeleton loader for content placeholders
export interface SkeletonProps {
  /** Skeleton variant */
  variant?: 'text' | 'circular' | 'rectangular';
  /** Width (CSS value) */
  width?: string | number;
  /** Height (CSS value) */
  height?: string | number;
  /** Number of lines (for text variant) */
  lines?: number;
  className?: string;
}

export function Skeleton({
  variant = 'text',
  width,
  height,
  lines = 1,
  className,
}: SkeletonProps) {
  const baseStyles = 'bg-neutral-200 animate-pulse';

  const variantStyles = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  if (variant === 'text' && lines > 1) {
    return (
      <div className={clsx('space-y-2', className)}>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={clsx(baseStyles, variantStyles[variant])}
            style={{
              width: index === lines - 1 ? '60%' : '100%',
            }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={twMerge(clsx(baseStyles, variantStyles[variant], className))}
      style={style}
    />
  );
}

// Page loading overlay
export interface PageLoaderProps {
  /** Loading message */
  message?: string;
}

export function PageLoader({ message = 'Loading...' }: PageLoaderProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50">
      <div className="text-center">
        <LoadingSpinner size="xl" />
        <p className="mt-4 text-lg text-neutral-600">{message}</p>
      </div>
    </div>
  );
}

// Table skeleton loader
export interface TableSkeletonProps {
  rows?: number;
  columns?: number;
}

export function TableSkeleton({ rows = 5, columns = 5 }: TableSkeletonProps) {
  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex gap-4 px-4 py-3 bg-neutral-50 border-b border-neutral-200">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} variant="text" className="flex-1" />
        ))}
      </div>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={rowIndex}
          className="flex gap-4 px-4 py-4 border-b border-neutral-100"
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} variant="text" className="flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

// Card skeleton loader
export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={twMerge(
        'bg-white rounded-lg border border-neutral-200 p-5',
        className
      )}
    >
      <Skeleton variant="text" width="40%" className="h-5" />
      <Skeleton variant="text" width="70%" className="h-8 mt-2" />
      <div className="flex items-center gap-2 mt-4">
        <Skeleton variant="text" width={60} />
        <Skeleton variant="text" width={80} />
      </div>
    </div>
  );
}

export default LoadingSpinner;
