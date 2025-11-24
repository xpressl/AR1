'use client';

import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'link';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual variant of the button */
  variant?: ButtonVariant;
  /** Size of the button */
  size?: ButtonSize;
  /** Show loading spinner */
  isLoading?: boolean;
  /** Icon to display before the button text */
  leftIcon?: React.ReactNode;
  /** Icon to display after the button text */
  rightIcon?: React.ReactNode;
  /** Make button full width */
  fullWidth?: boolean;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: `
    bg-primary-600 text-white
    hover:bg-primary-700
    focus-visible:ring-primary-500
    disabled:bg-primary-300
  `,
  secondary: `
    bg-white text-neutral-700
    border border-neutral-300
    hover:bg-neutral-50
    focus-visible:ring-neutral-500
    disabled:bg-neutral-100 disabled:text-neutral-400
  `,
  danger: `
    bg-error-600 text-white
    hover:bg-error-700
    focus-visible:ring-error-500
    disabled:bg-error-300
  `,
  ghost: `
    bg-transparent text-neutral-600
    hover:bg-neutral-100 hover:text-neutral-900
    focus-visible:ring-neutral-500
    disabled:text-neutral-300 disabled:hover:bg-transparent
  `,
  link: `
    bg-transparent text-primary-600
    hover:text-primary-700 hover:underline
    focus-visible:ring-primary-500
    disabled:text-primary-300
    p-0
  `,
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm rounded',
  md: 'px-4 py-2 text-sm rounded-md',
  lg: 'px-6 py-3 text-base rounded-md',
};

/**
 * Button component with multiple variants and sizes
 * Supports loading state, icons, and full accessibility
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      type = 'button',
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || isLoading;

    return (
      <button
        ref={ref}
        type={type}
        disabled={isDisabled}
        className={twMerge(
          clsx(
            // Base styles
            'inline-flex items-center justify-center font-medium',
            'transition-colors duration-200',
            'focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
            'disabled:cursor-not-allowed',
            // Variant styles
            variantStyles[variant],
            // Size styles (except for link variant)
            variant !== 'link' && sizeStyles[size],
            // Full width
            fullWidth && 'w-full',
            // Custom className
            className
          )
        )}
        {...props}
      >
        {/* Loading spinner */}
        {isLoading && (
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
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
        )}

        {/* Left icon */}
        {!isLoading && leftIcon && (
          <span className="mr-2 -ml-0.5 flex-shrink-0">{leftIcon}</span>
        )}

        {/* Button text */}
        <span>{children}</span>

        {/* Right icon */}
        {rightIcon && (
          <span className="ml-2 -mr-0.5 flex-shrink-0">{rightIcon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

// Icon button variant
export interface IconButtonProps extends Omit<ButtonProps, 'leftIcon' | 'rightIcon' | 'children'> {
  /** Accessible label for the button */
  'aria-label': string;
  /** Icon to display */
  icon: React.ReactNode;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon, className, size = 'md', ...props }, ref) => {
    const iconSizeStyles: Record<ButtonSize, string> = {
      sm: 'p-1.5',
      md: 'p-2',
      lg: 'p-3',
    };

    return (
      <Button
        ref={ref}
        size={size}
        className={twMerge(clsx(iconSizeStyles[size], className))}
        {...props}
      >
        {icon}
      </Button>
    );
  }
);

IconButton.displayName = 'IconButton';

// Button group for related actions
export interface ButtonGroupProps {
  children: React.ReactNode;
  /** Orientation of the button group */
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

export function ButtonGroup({
  children,
  orientation = 'horizontal',
  className,
}: ButtonGroupProps) {
  return (
    <div
      role="group"
      className={twMerge(
        clsx(
          'inline-flex',
          orientation === 'horizontal'
            ? 'flex-row [&>*:not(:first-child)]:rounded-l-none [&>*:not(:last-child)]:rounded-r-none [&>*:not(:first-child)]:border-l-0'
            : 'flex-col [&>*:not(:first-child)]:rounded-t-none [&>*:not(:last-child)]:rounded-b-none [&>*:not(:first-child)]:border-t-0',
          className
        )
      )}
    >
      {children}
    </div>
  );
}

export default Button;
