/**
 * Central Types Export for AR Control Hub
 */

// API types
export type {
  ApiResponse,
  PaginatedResponse,
  PaginationInfo,
  ApiError,
  PaginationParams,
  SortParams,
  DateRangeParams,
  BaseFilterParams,
  LoginRequest,
  LoginResponse,
  RefreshTokenResponse,
  UserRole,
  DashboardStats,
  AgingBucketData,
  CollectorPerformance,
  WorklistParams,
  WorklistItem,
  SearchParams,
  SearchResult,
} from './api';

// Customer types
export type {
  Customer,
  CustomerStatus,
  PaymentTerms,
  ContactInfo,
  CustomerSummary,
  CustomerDetail,
  CustomerAccountSummary,
  CustomerAgingBucket,
  CustomerInvoiceSummary,
  CustomerPaymentSummary,
  CreditHistoryEntry,
  CustomerNote,
  CustomerFilterParams,
  UpdateCreditLimitRequest,
  PlaceCreditHoldRequest,
  AssignCollectorRequest,
  AddNoteRequest,
} from './customer';

// Invoice types
export type {
  Invoice,
  InvoiceStatus,
  InvoiceType,
  InvoiceLineItem,
  InvoicePaymentApplication,
  InvoiceSummary,
  InvoiceFilterParams,
  Payment,
  PaymentMethod,
  PaymentStatus,
  PaymentApplication,
  PaymentSummary,
  PaymentFilterParams,
  Dispute,
  DisputeStatus,
  DisputeReason,
  DisputeFilterParams,
} from './invoice';

// Alert types
export type {
  Alert,
  AlertSeverity,
  AlertStatus,
  AlertCategory,
  AlertMetadata,
  AlertSummary,
  AlertFilterParams,
  AlertCounts,
  AcknowledgeAlertRequest,
  ResolveAlertRequest,
  SnoozeAlertRequest,
  AlertRule,
  AlertCondition,
  AlertAction,
} from './alert';

export { ALERT_SEVERITY_CONFIG, ALERT_CATEGORY_LABELS } from './alert';

// Common types used across the application
export interface User {
  id: string;
  email: string;
  name: string;
  role: import('./api').UserRole;
  department?: string;
  isActive: boolean;
  createdAt: string;
  lastLoginAt?: string;
}

export interface Task {
  id: string;
  customerId: string;
  customerName: string;
  title: string;
  description: string;
  dueDate: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  assignedTo: string;
  assignedToName: string;
  createdBy: string;
  createdByName: string;
  completedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuditLogEntry {
  id: string;
  entityType: string;
  entityId: string;
  action: string;
  userId: string;
  userName: string;
  previousValues?: Record<string, unknown>;
  newValues?: Record<string, unknown>;
  ipAddress?: string;
  userAgent?: string;
  timestamp: string;
}

// Utility types
export type SortDirection = 'asc' | 'desc';

export interface SelectOption<T = string> {
  value: T;
  label: string;
  disabled?: boolean;
}

export interface TableColumn<T> {
  key: keyof T | string;
  header: string;
  width?: string;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  render?: (value: unknown, row: T) => React.ReactNode;
}

export interface FilterOption {
  field: string;
  label: string;
  type: 'text' | 'select' | 'date' | 'number' | 'boolean';
  options?: SelectOption[];
}

// Component prop types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface FormFieldProps {
  label?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  helperText?: string;
}
