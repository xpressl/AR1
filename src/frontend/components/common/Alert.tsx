'use client';

import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export type AlertVariant = 'success' | 'warning' | 'error' | 'info' | 'critical';

export interface AlertProps {
  /** Alert variant/type */
  variant: AlertVariant;
  /** Alert title */
  title?: string;
  /** Alert message/content */
  children: React.ReactNode;
  /** Show icon */
  showIcon?: boolean;
  /** Custom icon */
  icon?: React.ReactNode;
  /** Dismissible */
  dismissible?: boolean;
  /** Dismiss handler */
  onDismiss?: () => void;
  /** Add pulsing animation for critical */
  pulse?: boolean;
  /** Action button */
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

const variantStyles: Record<AlertVariant, {
  container: string;
  icon: string;
  title: string;
  text: string;
}> = {
  success: {
    container: 'bg-success-50 border-success-500',
    icon: 'text-success-600',
    title: 'text-success-800',
    text: 'text-success-700',
  },
  warning: {
    container: 'bg-warning-50 border-warning-500',
    icon: 'text-warning-600',
    title: 'text-warning-800',
    text: 'text-warning-700',
  },
  error: {
    container: 'bg-error-50 border-error-500',
    icon: 'text-error-600',
    title: 'text-error-800',
    text: 'text-error-700',
  },
  info: {
    container: 'bg-info-50 border-info-500',
    icon: 'text-info-600',
    title: 'text-info-800',
    text: 'text-info-700',
  },
  critical: {
    container: 'bg-alert-critical-bg border-alert-critical',
    icon: 'text-alert-critical',
    title: 'text-red-900',
    text: 'text-red-800',
  },
};

const defaultIcons: Record<AlertVariant, React.ReactNode> = {
  success: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  ),
  warning: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
  error: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  info: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  critical: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
};

/**
 * Alert component for displaying messages and notifications
 * Supports different variants including critical with pulsing animation
 */
export function Alert({
  variant,
  title,
  children,
  showIcon = true,
  icon,
  dismissible = false,
  onDismiss,
  pulse = false,
  action,
  className,
}: AlertProps) {
  const styles = variantStyles[variant];
  const displayIcon = icon || defaultIcons[variant];

  return (
    <div
      role="alert"
      className={twMerge(
        clsx(
          'rounded-lg border-l-4 p-4',
          styles.container,
          pulse && variant === 'critical' && 'alert-critical-pulse',
          className
        )
      )}
    >
      <div className="flex">
        {/* Icon */}
        {showIcon && (
          <div
            className={clsx(
              'flex-shrink-0',
              styles.icon,
              pulse && variant === 'critical' && 'alert-icon-pulse'
            )}
          >
            {displayIcon}
          </div>
        )}

        {/* Content */}
        <div className={clsx('flex-1', showIcon && 'ml-3')}>
          {title && (
            <h3 className={clsx('text-sm font-semibold', styles.title)}>
              {title}
            </h3>
          )}
          <div className={clsx('text-sm', styles.text, title && 'mt-1')}>
            {children}
          </div>

          {/* Action button */}
          {action && (
            <div className="mt-3">
              <button
                type="button"
                onClick={action.onClick}
                className={clsx(
                  'text-sm font-medium underline hover:no-underline',
                  styles.text
                )}
              >
                {action.label}
              </button>
            </div>
          )}
        </div>

        {/* Dismiss button */}
        {dismissible && onDismiss && (
          <div className="flex-shrink-0 ml-4">
            <button
              type="button"
              onClick={onDismiss}
              className={clsx(
                'inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2',
                styles.icon,
                'hover:bg-black/5'
              )}
              aria-label="Dismiss alert"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// Inline alert for form fields or smaller contexts
export interface InlineAlertProps {
  variant: 'success' | 'warning' | 'error' | 'info';
  children: React.ReactNode;
  className?: string;
}

export function InlineAlert({ variant, children, className }: InlineAlertProps) {
  const colors = {
    success: 'text-success-600',
    warning: 'text-warning-600',
    error: 'text-error-600',
    info: 'text-info-600',
  };

  return (
    <p className={twMerge(clsx('flex items-center gap-1.5 text-sm', colors[variant], className))}>
      {defaultIcons[variant]}
      <span>{children}</span>
    </p>
  );
}

// Banner alert for page-level notifications
export interface AlertBannerProps {
  variant: AlertVariant;
  children: React.ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function AlertBanner({
  variant,
  children,
  dismissible = false,
  onDismiss,
  action,
  className,
}: AlertBannerProps) {
  const bgColors: Record<AlertVariant, string> = {
    success: 'bg-success-600',
    warning: 'bg-warning-500',
    error: 'bg-error-600',
    info: 'bg-info-600',
    critical: 'bg-alert-critical',
  };

  return (
    <div
      role="alert"
      className={twMerge(
        clsx(
          'px-4 py-3 text-white',
          bgColors[variant],
          variant === 'critical' && 'animate-pulse',
          className
        )
      )}
    >
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <span className="flex-shrink-0">{defaultIcons[variant]}</span>
          <span className="text-sm font-medium">{children}</span>
        </div>
        <div className="flex items-center gap-4">
          {action && (
            <button
              type="button"
              onClick={action.onClick}
              className="text-sm font-medium underline hover:no-underline"
            >
              {action.label}
            </button>
          )}
          {dismissible && onDismiss && (
            <button
              type="button"
              onClick={onDismiss}
              className="p-1 hover:bg-white/10 rounded"
              aria-label="Dismiss"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default Alert;
