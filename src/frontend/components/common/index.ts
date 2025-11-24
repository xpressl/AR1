/**
 * Common Components Index
 * Central export point for all base UI components
 */

// Button components
export { Button, IconButton, ButtonGroup } from './Button';
export type { ButtonProps, ButtonVariant, ButtonSize, IconButtonProps, ButtonGroupProps } from './Button';

// Input components
export { Input, Textarea, Select } from './Input';
export type { InputProps, InputType, InputSize, TextareaProps, SelectProps, SelectOption } from './Input';

// Card components
export { Card, CardHeader, CardContent, CardFooter, StatCard } from './Card';
export type { CardProps, CardHeaderProps, CardContentProps, CardFooterProps, StatCardProps } from './Card';

// Table components
export { Table, Pagination } from './Table';
export type { TableProps, TableColumn, SortDirection, PaginationProps } from './Table';

// Badge components
export { Badge, AlertBadge, StatusBadge, AgingBadge, CountBadge } from './Badge';
export type { BadgeProps, BadgeVariant, BadgeSize, AlertBadgeProps, StatusBadgeProps, AgingBadgeProps, CountBadgeProps } from './Badge';

// Modal components
export { Modal, ConfirmDialog, FormModal } from './Modal';
export type { ModalProps, ModalSize, ConfirmDialogProps, FormModalProps } from './Modal';

// Alert components
export { Alert, InlineAlert, AlertBanner } from './Alert';
export type { AlertProps, AlertVariant, InlineAlertProps, AlertBannerProps } from './Alert';

// Tooltip components
export { Tooltip, HelpTooltip } from './Tooltip';
export type { TooltipProps, TooltipPlacement, HelpTooltipProps } from './Tooltip';

// Loading components
export {
  LoadingSpinner,
  InlineLoader,
  Skeleton,
  PageLoader,
  TableSkeleton,
  CardSkeleton,
} from './LoadingSpinner';
export type {
  LoadingSpinnerProps,
  SpinnerSize,
  InlineLoaderProps,
  SkeletonProps,
  PageLoaderProps,
  TableSkeletonProps,
} from './LoadingSpinner';

// Empty state components
export {
  EmptyState,
  EmptyStateIcons,
  NoSearchResults,
  NoData,
  NoAlerts,
  ErrorState,
} from './EmptyState';
export type { EmptyStateProps } from './EmptyState';
