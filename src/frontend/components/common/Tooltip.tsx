'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export type TooltipPlacement = 'top' | 'bottom' | 'left' | 'right';

export interface TooltipProps {
  /** Tooltip content */
  content: React.ReactNode;
  /** Trigger element */
  children: React.ReactElement;
  /** Tooltip placement */
  placement?: TooltipPlacement;
  /** Delay before showing (ms) */
  showDelay?: number;
  /** Delay before hiding (ms) */
  hideDelay?: number;
  /** Disable tooltip */
  disabled?: boolean;
  /** Custom max width */
  maxWidth?: number;
  className?: string;
}

interface Position {
  top: number;
  left: number;
}

/**
 * Tooltip component for displaying help text on hover
 * Automatically repositions to stay within viewport
 */
export function Tooltip({
  content,
  children,
  placement = 'top',
  showDelay = 200,
  hideDelay = 0,
  disabled = false,
  maxWidth = 200,
  className,
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState<Position>({ top: 0, left: 0 });
  const [actualPlacement, setActualPlacement] = useState(placement);

  const triggerRef = useRef<HTMLElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const showTimeoutRef = useRef<NodeJS.Timeout>();
  const hideTimeoutRef = useRef<NodeJS.Timeout>();

  const calculatePosition = useCallback(() => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const offset = 8;

    let top = 0;
    let left = 0;
    let finalPlacement = placement;

    // Calculate initial position based on placement
    switch (placement) {
      case 'top':
        top = triggerRect.top - tooltipRect.height - offset;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'bottom':
        top = triggerRect.bottom + offset;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'left':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.left - tooltipRect.width - offset;
        break;
      case 'right':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + offset;
        break;
    }

    // Check if tooltip goes outside viewport and flip if necessary
    if (placement === 'top' && top < 0) {
      top = triggerRect.bottom + offset;
      finalPlacement = 'bottom';
    } else if (placement === 'bottom' && top + tooltipRect.height > window.innerHeight) {
      top = triggerRect.top - tooltipRect.height - offset;
      finalPlacement = 'top';
    } else if (placement === 'left' && left < 0) {
      left = triggerRect.right + offset;
      finalPlacement = 'right';
    } else if (placement === 'right' && left + tooltipRect.width > window.innerWidth) {
      left = triggerRect.left - tooltipRect.width - offset;
      finalPlacement = 'left';
    }

    // Keep tooltip within viewport bounds
    left = Math.max(8, Math.min(left, window.innerWidth - tooltipRect.width - 8));
    top = Math.max(8, Math.min(top, window.innerHeight - tooltipRect.height - 8));

    setPosition({ top, left });
    setActualPlacement(finalPlacement);
  }, [placement]);

  const showTooltip = useCallback(() => {
    if (disabled) return;

    clearTimeout(hideTimeoutRef.current);
    showTimeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, showDelay);
  }, [disabled, showDelay]);

  const hideTooltip = useCallback(() => {
    clearTimeout(showTimeoutRef.current);
    hideTimeoutRef.current = setTimeout(() => {
      setIsVisible(false);
    }, hideDelay);
  }, [hideDelay]);

  // Update position when visible
  useEffect(() => {
    if (isVisible) {
      calculatePosition();
      window.addEventListener('scroll', calculatePosition, true);
      window.addEventListener('resize', calculatePosition);

      return () => {
        window.removeEventListener('scroll', calculatePosition, true);
        window.removeEventListener('resize', calculatePosition);
      };
    }
  }, [isVisible, calculatePosition]);

  // Cleanup timeouts
  useEffect(() => {
    return () => {
      clearTimeout(showTimeoutRef.current);
      clearTimeout(hideTimeoutRef.current);
    };
  }, []);

  // Arrow styles based on placement
  const arrowStyles: Record<TooltipPlacement, string> = {
    top: 'bottom-0 left-1/2 -translate-x-1/2 translate-y-full border-t-neutral-800 border-x-transparent border-b-transparent',
    bottom: 'top-0 left-1/2 -translate-x-1/2 -translate-y-full border-b-neutral-800 border-x-transparent border-t-transparent',
    left: 'right-0 top-1/2 -translate-y-1/2 translate-x-full border-l-neutral-800 border-y-transparent border-r-transparent',
    right: 'left-0 top-1/2 -translate-y-1/2 -translate-x-full border-r-neutral-800 border-y-transparent border-l-transparent',
  };

  // Clone child with ref and event handlers
  const trigger = React.cloneElement(children, {
    ref: triggerRef,
    onMouseEnter: (e: React.MouseEvent) => {
      showTooltip();
      children.props.onMouseEnter?.(e);
    },
    onMouseLeave: (e: React.MouseEvent) => {
      hideTooltip();
      children.props.onMouseLeave?.(e);
    },
    onFocus: (e: React.FocusEvent) => {
      showTooltip();
      children.props.onFocus?.(e);
    },
    onBlur: (e: React.FocusEvent) => {
      hideTooltip();
      children.props.onBlur?.(e);
    },
  });

  return (
    <>
      {trigger}
      {isVisible &&
        createPortal(
          <div
            ref={tooltipRef}
            role="tooltip"
            className={twMerge(
              clsx(
                'fixed z-[100] px-2.5 py-1.5 text-xs font-medium text-white bg-neutral-800 rounded shadow-lg',
                'animate-fade-in pointer-events-none',
                className
              )
            )}
            style={{
              top: position.top,
              left: position.left,
              maxWidth,
            }}
          >
            {content}
            {/* Arrow */}
            <span
              className={clsx(
                'absolute w-0 h-0 border-4',
                arrowStyles[actualPlacement]
              )}
            />
          </div>,
          document.body
        )}
    </>
  );
}

// Simple help icon with tooltip
export interface HelpTooltipProps {
  content: React.ReactNode;
  placement?: TooltipPlacement;
  className?: string;
}

export function HelpTooltip({ content, placement = 'top', className }: HelpTooltipProps) {
  return (
    <Tooltip content={content} placement={placement}>
      <button
        type="button"
        className={twMerge(
          clsx(
            'inline-flex items-center justify-center w-4 h-4 rounded-full',
            'text-neutral-400 hover:text-neutral-600',
            'bg-neutral-100 hover:bg-neutral-200',
            'transition-colors cursor-help',
            className
          )
        )}
        aria-label="Help"
      >
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
    </Tooltip>
  );
}

export default Tooltip;
