'use client';

import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { AlertSeverity, CustomerStatus, InvoiceStatus, PaymentStatus, DisputeStatus } from '@/types';

export type BadgeVariant =
  | 'default'
  | 'primary'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  | 'critical'
  | 'high'
  | 'medium'
  | 'low';

export type BadgeSize = 'sm' | 'md' | 'lg';

export interface BadgeProps {
  /** Badge text content */
  children: React.ReactNode;
  /** Visual variant */
  variant?: BadgeVariant;
  /** Badge size */
  size?: BadgeSize;
  /** Show as pill (rounded ends) */
  pill?: boolean;
  /** Show dot indicator */
  dot?: boolean;
  /** Dot color override */
  dotColor?: string;
  /** Add pulsing animation (for critical alerts) */
  pulse?: boolean;
  /** Click handler (makes badge interactive) */
  onClick?: () => void;
  /** Remove handler (shows X button) */
  onRemove?: () => void;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-neutral-100 text-neutral-700 border-neutral-300',
  primary: 'bg-primary-50 text-primary-700 border-primary-300',
  success: 'bg-success-50 text-success-700 border-success-300',
  warning: 'bg-warning-50 text-warning-700 border-warning-300',
  error: 'bg-error-50 text-error-700 border-error-300',
  info: 'bg-info-50 text-info-700 border-info-300',
  critical: 'bg-alert-critical-bg text-alert-critical border-alert-critical',
  high: 'bg-alert-high-bg text-alert-high border-alert-high',
  medium: 'bg-alert-medium-bg text-alert-medium border-alert-medium',
  low: 'bg-alert-low-bg text-alert-low border-alert-low',
};

const sizeStyles: Record<BadgeSize, string> = {
  sm: 'px-1.5 py-0.5 text-xs',
  md: 'px-2.5 py-0.5 text-xs',
  lg: 'px-3 py-1 text-sm',
};

const dotSizeStyles: Record<BadgeSize, string> = {
  sm: 'w-1.5 h-1.5',
  md: 'w-2 h-2',
  lg: 'w-2.5 h-2.5',
};

/**
 * Badge component for status indicators and labels
 * Supports different variants including alert severity colors
 */
export function Badge({
  children,
  variant = 'default',
  size = 'md',
  pill = true,
  dot = false,
  dotColor,
  pulse = false,
  onClick,
  onRemove,
  className,
}: BadgeProps) {
  const isInteractive = Boolean(onClick);

  const badgeContent = (
    <>
      {/* Dot indicator */}
      {dot && (
        <span
          className={clsx(
            'rounded-full',
            dotSizeStyles[size],
            pulse && 'animate-pulse',
            dotColor || 'bg-current'
          )}
          style={dotColor ? { backgroundColor: dotColor } : undefined}
        />
      )}

      {/* Badge text */}
      <span>{children}</span>

      {/* Remove button */}
      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="ml-1 -mr-1 hover:bg-black/10 rounded p-0.5 transition-colors"
          aria-label="Remove"
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </>
  );

  const classes = twMerge(
    clsx(
      'inline-flex items-center gap-1.5 font-medium border',
      variantStyles[variant],
      sizeStyles[size],
      pill ? 'rounded-full' : 'rounded',
      pulse && variant === 'critical' && 'alert-critical-pulse',
      isInteractive && 'cursor-pointer hover:opacity-80 transition-opacity',
      className
    )
  );

  if (onClick) {
    return (
      <button type="button" onClick={onClick} className={classes}>
        {badgeContent}
      </button>
    );
  }

  return <span className={classes}>{badgeContent}</span>;
}

// Specialized badge for alert severity
export interface AlertBadgeProps {
  severity: AlertSeverity;
  showLabel?: boolean;
  pulse?: boolean;
  className?: string;
}

export function AlertBadge({ severity, showLabel = true, pulse, className }: AlertBadgeProps) {
  const labels: Record<AlertSeverity, string> = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
  };

  return (
    <Badge
      variant={severity}
      pulse={pulse ?? severity === 'critical'}
      dot
      className={className}
    >
      {showLabel ? labels[severity] : null}
    </Badge>
  );
}

// Specialized badge for customer status
export interface StatusBadgeProps {
  status: CustomerStatus | InvoiceStatus | PaymentStatus | DisputeStatus | string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const statusConfig: Record<string, { variant: BadgeVariant; label: string }> = {
    // Customer status
    active: { variant: 'success', label: 'Active' },
    inactive: { variant: 'default', label: 'Inactive' },
    hold: { variant: 'error', label: 'Hold' },
    cod: { variant: 'warning', label: 'COD' },

    // Invoice status
    open: { variant: 'info', label: 'Open' },
    partial: { variant: 'warning', label: 'Partial' },
    paid: { variant: 'success', label: 'Paid' },
    void: { variant: 'default', label: 'Void' },
    disputed: { variant: 'error', label: 'Disputed' },

    // Payment status
    pending: { variant: 'warning', label: 'Pending' },
    applied: { variant: 'success', label: 'Applied' },
    returned: { variant: 'error', label: 'Returned' },

    // Dispute status
    investigating: { variant: 'info', label: 'Investigating' },
    resolved: { variant: 'success', label: 'Resolved' },
    escalated: { variant: 'error', label: 'Escalated' },
    closed: { variant: 'default', label: 'Closed' },
  };

  const config = statusConfig[status] || { variant: 'default' as BadgeVariant, label: status };

  return (
    <Badge variant={config.variant} dot className={className}>
      {config.label}
    </Badge>
  );
}

// Aging bucket badge
export interface AgingBadgeProps {
  bucket: 'current' | '1-30' | '31-60' | '61-90' | '90+' | string;
  className?: string;
}

export function AgingBadge({ bucket, className }: AgingBadgeProps) {
  const bucketConfig: Record<string, { color: string; label: string }> = {
    current: { color: 'bg-aging-current', label: 'Current' },
    '1-30': { color: 'bg-aging-30', label: '1-30 Days' },
    '31-60': { color: 'bg-aging-60', label: '31-60 Days' },
    '61-90': { color: 'bg-aging-90', label: '61-90 Days' },
    '90+': { color: 'bg-aging-over', label: '90+ Days' },
  };

  const config = bucketConfig[bucket] || { color: 'bg-neutral-400', label: bucket };

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white',
          config.color,
          className
        )
      )}
    >
      {config.label}
    </span>
  );
}

// Count badge (for notifications)
export interface CountBadgeProps {
  count: number;
  max?: number;
  variant?: 'default' | 'primary' | 'error';
  className?: string;
}

export function CountBadge({ count, max = 99, variant = 'primary', className }: CountBadgeProps) {
  if (count <= 0) return null;

  const displayCount = count > max ? `${max}+` : count;

  const variantColors = {
    default: 'bg-neutral-500',
    primary: 'bg-primary-600',
    error: 'bg-error-600',
  };

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1.5',
          'rounded-full text-xs font-semibold text-white',
          variantColors[variant],
          className
        )
      )}
    >
      {displayCount}
    </span>
  );
}

export default Badge;
