/**
 * Alert Types for AR Control Hub
 */

export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low';
export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'snoozed';
export type AlertCategory =
  | 'payment_overdue'
  | 'credit_limit_exceeded'
  | 'broken_promise'
  | 'aging_threshold'
  | 'large_balance'
  | 'payment_returned'
  | 'dispute_opened'
  | 'credit_hold'
  | 'new_customer_risk'
  | 'unusual_activity';

export interface Alert {
  id: string;
  customerId: string;
  customerNumber: string;
  customerName: string;
  category: AlertCategory;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  description: string;
  amount?: number;
  invoiceId?: string;
  invoiceNumber?: string;
  metadata: AlertMetadata;
  acknowledgedAt?: string;
  acknowledgedBy?: string;
  resolvedAt?: string;
  resolvedBy?: string;
  snoozedUntil?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AlertMetadata {
  daysOverdue?: number;
  creditUtilization?: number;
  promiseDate?: string;
  previousBalance?: number;
  currentBalance?: number;
  thresholdAmount?: number;
  triggerRule?: string;
  relatedAlertIds?: string[];
  [key: string]: string | number | string[] | undefined;
}

export interface AlertSummary {
  id: string;
  customerId: string;
  customerName: string;
  category: AlertCategory;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  amount?: number;
  createdAt: string;
}

// Alert filter params
export interface AlertFilterParams {
  search?: string;
  customerId?: string;
  category?: AlertCategory;
  severity?: AlertSeverity;
  status?: AlertStatus;
  collectorId?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Alert count by severity
export interface AlertCounts {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  byCategory: Record<AlertCategory, number>;
}

// Alert actions
export interface AcknowledgeAlertRequest {
  note?: string;
}

export interface ResolveAlertRequest {
  resolution: string;
  preventRecurrence?: boolean;
}

export interface SnoozeAlertRequest {
  snoozeUntil: string;
  reason: string;
}

// Alert rules for automated alerts
export interface AlertRule {
  id: string;
  name: string;
  description: string;
  category: AlertCategory;
  severity: AlertSeverity;
  isActive: boolean;
  conditions: AlertCondition[];
  actions: AlertAction[];
  createdAt: string;
  updatedAt: string;
}

export interface AlertCondition {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'not_in' | 'contains';
  value: string | number | string[];
}

export interface AlertAction {
  type: 'create_alert' | 'send_email' | 'assign_task' | 'notify_user';
  config: Record<string, string | number | boolean>;
}

// Alert display helpers
export const ALERT_SEVERITY_CONFIG: Record<AlertSeverity, {
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: string;
}> = {
  critical: {
    label: 'Critical',
    color: 'text-alert-critical',
    bgColor: 'bg-alert-critical-bg',
    borderColor: 'border-alert-critical',
    icon: 'AlertTriangle',
  },
  high: {
    label: 'High',
    color: 'text-alert-high',
    bgColor: 'bg-alert-high-bg',
    borderColor: 'border-alert-high',
    icon: 'AlertCircle',
  },
  medium: {
    label: 'Medium',
    color: 'text-alert-medium',
    bgColor: 'bg-alert-medium-bg',
    borderColor: 'border-alert-medium',
    icon: 'Info',
  },
  low: {
    label: 'Low',
    color: 'text-alert-low',
    bgColor: 'bg-alert-low-bg',
    borderColor: 'border-alert-low',
    icon: 'Bell',
  },
};

export const ALERT_CATEGORY_LABELS: Record<AlertCategory, string> = {
  payment_overdue: 'Payment Overdue',
  credit_limit_exceeded: 'Credit Limit Exceeded',
  broken_promise: 'Broken Promise to Pay',
  aging_threshold: 'Aging Threshold Crossed',
  large_balance: 'Large Balance Alert',
  payment_returned: 'Payment Returned',
  dispute_opened: 'Dispute Opened',
  credit_hold: 'Credit Hold Required',
  new_customer_risk: 'New Customer Risk',
  unusual_activity: 'Unusual Activity',
};
