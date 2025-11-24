'use client';

import React, { forwardRef, useId } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export type InputType = 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'date';
export type InputSize = 'sm' | 'md' | 'lg';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Label text for the input */
  label?: string;
  /** Error message to display */
  error?: string;
  /** Helper text shown below the input */
  helperText?: string;
  /** Size of the input */
  size?: InputSize;
  /** Icon to display at the start of the input */
  leftIcon?: React.ReactNode;
  /** Icon or element to display at the end of the input */
  rightElement?: React.ReactNode;
  /** Make the input full width */
  fullWidth?: boolean;
  /** Show character count (requires maxLength) */
  showCharCount?: boolean;
}

const sizeStyles: Record<InputSize, { input: string; icon: string }> = {
  sm: {
    input: 'px-3 py-1.5 text-sm',
    icon: 'pl-8',
  },
  md: {
    input: 'px-3 py-2 text-sm',
    icon: 'pl-10',
  },
  lg: {
    input: 'px-4 py-3 text-base',
    icon: 'pl-12',
  },
};

/**
 * Input component with label, error state, icons, and helper text
 * Fully accessible with proper ARIA attributes
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      size = 'md',
      leftIcon,
      rightElement,
      fullWidth = true,
      showCharCount = false,
      className,
      id,
      type = 'text',
      disabled,
      required,
      maxLength,
      value,
      ...props
    },
    ref
  ) => {
    // Generate unique ID if not provided
    const generatedId = useId();
    const inputId = id || generatedId;
    const errorId = `${inputId}-error`;
    const helperId = `${inputId}-helper`;

    const hasError = Boolean(error);
    const charCount = typeof value === 'string' ? value.length : 0;

    return (
      <div className={clsx('relative', fullWidth && 'w-full')}>
        {/* Label */}
        {label && (
          <label
            htmlFor={inputId}
            className={clsx(
              'block text-sm font-medium text-neutral-700 mb-1',
              required && "after:content-['*'] after:ml-0.5 after:text-error-500"
            )}
          >
            {label}
          </label>
        )}

        {/* Input wrapper */}
        <div className="relative">
          {/* Left icon */}
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-neutral-400">
              {leftIcon}
            </div>
          )}

          {/* Input element */}
          <input
            ref={ref}
            id={inputId}
            type={type}
            disabled={disabled}
            required={required}
            maxLength={maxLength}
            value={value}
            aria-invalid={hasError}
            aria-describedby={clsx(
              hasError && errorId,
              helperText && helperId
            ) || undefined}
            className={twMerge(
              clsx(
                // Base styles
                'block rounded-md border bg-white',
                'text-neutral-900 placeholder:text-neutral-400',
                'transition-colors duration-200',
                'focus:outline-none focus:ring-1',
                // Size styles
                sizeStyles[size].input,
                // Left icon padding
                leftIcon && sizeStyles[size].icon,
                // Right element padding
                rightElement && 'pr-10',
                // Full width
                fullWidth && 'w-full',
                // Error state
                hasError
                  ? 'border-error-500 focus:border-error-500 focus:ring-error-500'
                  : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500',
                // Disabled state
                disabled && 'bg-neutral-100 cursor-not-allowed text-neutral-500',
                className
              )
            )}
            {...props}
          />

          {/* Right element */}
          {rightElement && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
              {rightElement}
            </div>
          )}
        </div>

        {/* Bottom section: error, helper text, and character count */}
        <div className="flex justify-between mt-1">
          <div>
            {/* Error message */}
            {hasError && (
              <p id={errorId} className="text-sm text-error-600" role="alert">
                {error}
              </p>
            )}

            {/* Helper text (shown when no error) */}
            {!hasError && helperText && (
              <p id={helperId} className="text-sm text-neutral-500">
                {helperText}
              </p>
            )}
          </div>

          {/* Character count */}
          {showCharCount && maxLength && (
            <p
              className={clsx(
                'text-sm',
                charCount > maxLength * 0.9 ? 'text-warning-600' : 'text-neutral-400'
              )}
            >
              {charCount}/{maxLength}
            </p>
          )}
        </div>
      </div>
    );
  }
);

Input.displayName = 'Input';

// Textarea component
export interface TextareaProps extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'size'> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  showCharCount?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      label,
      error,
      helperText,
      fullWidth = true,
      showCharCount = false,
      className,
      id,
      disabled,
      required,
      maxLength,
      value,
      rows = 4,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const textareaId = id || generatedId;
    const errorId = `${textareaId}-error`;
    const helperId = `${textareaId}-helper`;

    const hasError = Boolean(error);
    const charCount = typeof value === 'string' ? value.length : 0;

    return (
      <div className={clsx('relative', fullWidth && 'w-full')}>
        {label && (
          <label
            htmlFor={textareaId}
            className={clsx(
              'block text-sm font-medium text-neutral-700 mb-1',
              required && "after:content-['*'] after:ml-0.5 after:text-error-500"
            )}
          >
            {label}
          </label>
        )}

        <textarea
          ref={ref}
          id={textareaId}
          disabled={disabled}
          required={required}
          maxLength={maxLength}
          value={value}
          rows={rows}
          aria-invalid={hasError}
          aria-describedby={clsx(hasError && errorId, helperText && helperId) || undefined}
          className={twMerge(
            clsx(
              'block rounded-md border bg-white px-3 py-2 text-sm',
              'text-neutral-900 placeholder:text-neutral-400',
              'transition-colors duration-200 resize-y',
              'focus:outline-none focus:ring-1',
              fullWidth && 'w-full',
              hasError
                ? 'border-error-500 focus:border-error-500 focus:ring-error-500'
                : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500',
              disabled && 'bg-neutral-100 cursor-not-allowed text-neutral-500',
              className
            )
          )}
          {...props}
        />

        <div className="flex justify-between mt-1">
          <div>
            {hasError && (
              <p id={errorId} className="text-sm text-error-600" role="alert">
                {error}
              </p>
            )}
            {!hasError && helperText && (
              <p id={helperId} className="text-sm text-neutral-500">
                {helperText}
              </p>
            )}
          </div>
          {showCharCount && maxLength && (
            <p
              className={clsx(
                'text-sm',
                charCount > maxLength * 0.9 ? 'text-warning-600' : 'text-neutral-400'
              )}
            >
              {charCount}/{maxLength}
            </p>
          )}
        </div>
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

// Select component
export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  label?: string;
  error?: string;
  helperText?: string;
  size?: InputSize;
  options: SelectOption[];
  placeholder?: string;
  fullWidth?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      label,
      error,
      helperText,
      size = 'md',
      options,
      placeholder,
      fullWidth = true,
      className,
      id,
      disabled,
      required,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const selectId = id || generatedId;
    const errorId = `${selectId}-error`;
    const helperId = `${selectId}-helper`;

    const hasError = Boolean(error);

    return (
      <div className={clsx('relative', fullWidth && 'w-full')}>
        {label && (
          <label
            htmlFor={selectId}
            className={clsx(
              'block text-sm font-medium text-neutral-700 mb-1',
              required && "after:content-['*'] after:ml-0.5 after:text-error-500"
            )}
          >
            {label}
          </label>
        )}

        <div className="relative">
          <select
            ref={ref}
            id={selectId}
            disabled={disabled}
            required={required}
            aria-invalid={hasError}
            aria-describedby={clsx(hasError && errorId, helperText && helperId) || undefined}
            className={twMerge(
              clsx(
                'block rounded-md border bg-white appearance-none pr-10',
                'text-neutral-900',
                'transition-colors duration-200',
                'focus:outline-none focus:ring-1',
                sizeStyles[size].input,
                fullWidth && 'w-full',
                hasError
                  ? 'border-error-500 focus:border-error-500 focus:ring-error-500'
                  : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-500',
                disabled && 'bg-neutral-100 cursor-not-allowed text-neutral-500',
                className
              )
            )}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </option>
            ))}
          </select>

          {/* Dropdown arrow */}
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <svg
              className="h-4 w-4 text-neutral-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        {hasError && (
          <p id={errorId} className="mt-1 text-sm text-error-600" role="alert">
            {error}
          </p>
        )}
        {!hasError && helperText && (
          <p id={helperId} className="mt-1 text-sm text-neutral-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';

export default Input;
