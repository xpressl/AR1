'use client';

import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Add hover effect */
  hoverable?: boolean;
  /** Remove padding */
  noPadding?: boolean;
  /** Border variant */
  variant?: 'default' | 'outlined' | 'elevated';
}

/**
 * Card component for containing content
 * Supports header, content, and footer sections
 */
export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ children, className, hoverable = false, noPadding = false, variant = 'default', ...props }, ref) => {
    const variantStyles = {
      default: 'bg-white border border-neutral-200 shadow-card',
      outlined: 'bg-white border border-neutral-200',
      elevated: 'bg-white shadow-lg',
    };

    return (
      <div
        ref={ref}
        className={twMerge(
          clsx(
            'rounded-lg',
            variantStyles[variant],
            hoverable && 'transition-shadow duration-200 hover:shadow-card-hover cursor-pointer',
            !noPadding && 'p-0',
            className
          )
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

// Card Header
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Title text */
  title?: string;
  /** Subtitle text */
  subtitle?: string;
  /** Action element (buttons, etc.) */
  action?: React.ReactNode;
  /** Whether to show bottom border */
  borderless?: boolean;
}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ children, className, title, subtitle, action, borderless = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge(
          clsx(
            'px-6 py-4',
            !borderless && 'border-b border-neutral-200',
            className
          )
        )}
        {...props}
      >
        {(title || subtitle || action) ? (
          <div className="flex items-start justify-between gap-4">
            <div>
              {title && (
                <h3 className="text-lg font-semibold text-neutral-900">{title}</h3>
              )}
              {subtitle && (
                <p className="text-sm text-neutral-500 mt-0.5">{subtitle}</p>
              )}
            </div>
            {action && <div className="flex-shrink-0">{action}</div>}
          </div>
        ) : (
          children
        )}
      </div>
    );
  }
);

CardHeader.displayName = 'CardHeader';

// Card Content
export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Remove default padding */
  noPadding?: boolean;
}

export const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ children, className, noPadding = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge(clsx(!noPadding && 'px-6 py-4', className))}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardContent.displayName = 'CardContent';

// Card Footer
export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Alignment of footer content */
  align?: 'left' | 'center' | 'right' | 'between';
  /** Whether to show top border */
  borderless?: boolean;
}

export const CardFooter = forwardRef<HTMLDivElement, CardFooterProps>(
  ({ children, className, align = 'right', borderless = false, ...props }, ref) => {
    const alignStyles = {
      left: 'justify-start',
      center: 'justify-center',
      right: 'justify-end',
      between: 'justify-between',
    };

    return (
      <div
        ref={ref}
        className={twMerge(
          clsx(
            'px-6 py-4 bg-neutral-50 rounded-b-lg',
            'flex items-center gap-3',
            alignStyles[align],
            !borderless && 'border-t border-neutral-200',
            className
          )
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardFooter.displayName = 'CardFooter';

// Stat Card - specialized card for displaying metrics
export interface StatCardProps {
  title: string;
  value: string | number;
  /** Optional icon */
  icon?: React.ReactNode;
  /** Trend indicator */
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
    label?: string;
  };
  /** Additional description */
  description?: string;
  /** Click handler */
  onClick?: () => void;
  className?: string;
}

export function StatCard({
  title,
  value,
  icon,
  trend,
  description,
  onClick,
  className,
}: StatCardProps) {
  const trendColors = {
    up: 'text-success-600',
    down: 'text-error-600',
    neutral: 'text-neutral-500',
  };

  const trendIcons = {
    up: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
      </svg>
    ),
    down: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
      </svg>
    ),
    neutral: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
      </svg>
    ),
  };

  return (
    <Card
      hoverable={Boolean(onClick)}
      onClick={onClick}
      className={twMerge('p-5', className)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-neutral-500">{title}</p>
          <p className="mt-1 text-2xl font-bold text-neutral-900">{value}</p>

          {trend && (
            <div className={clsx('flex items-center gap-1 mt-2 text-sm', trendColors[trend.direction])}>
              {trendIcons[trend.direction]}
              <span className="font-medium">{Math.abs(trend.value)}%</span>
              {trend.label && <span className="text-neutral-500">{trend.label}</span>}
            </div>
          )}

          {description && (
            <p className="mt-2 text-sm text-neutral-500">{description}</p>
          )}
        </div>

        {icon && (
          <div className="p-3 bg-primary-50 rounded-lg text-primary-600">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}

export default Card;
