/**
 * API Types for AR Control Hub
 * Defines all request/response types for API communication
 */

// Base API response wrapper
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

// Paginated response
export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: PaginationInfo;
  timestamp: string;
}

export interface PaginationInfo {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

// API Error response
export interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
  timestamp: string;
}

// Request types
export interface PaginationParams {
  page?: number;
  pageSize?: number;
}

export interface SortParams {
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface DateRangeParams {
  startDate?: string;
  endDate?: string;
}

// Common filter params
export interface BaseFilterParams extends PaginationParams, SortParams {
  search?: string;
}

// Authentication
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: {
    id: string;
    email: string;
    name: string;
    role: UserRole;
  };
  token: string;
  expiresAt: string;
}

export interface RefreshTokenResponse {
  token: string;
  expiresAt: string;
}

export type UserRole = 'admin' | 'manager' | 'collector' | 'viewer';

// Dashboard API
export interface DashboardStats {
  totalAR: number;
  totalCustomers: number;
  overdueAmount: number;
  overdueCount: number;
  avgDSO: number;
  collectedThisMonth: number;
  collectionsTarget: number;
  activeAlerts: number;
  criticalAlerts: number;
}

export interface AgingBucketData {
  bucket: 'current' | '1-30' | '31-60' | '61-90' | '90+';
  amount: number;
  count: number;
  percentage: number;
}

export interface CollectorPerformance {
  collectorId: string;
  collectorName: string;
  assignedCustomers: number;
  totalAR: number;
  collected: number;
  target: number;
  targetPercentage: number;
}

// Worklist API
export interface WorklistParams extends BaseFilterParams {
  collectorId?: string;
  priority?: 'critical' | 'high' | 'medium' | 'low';
  status?: 'pending' | 'in_progress' | 'completed';
  agingBucket?: string;
}

export interface WorklistItem {
  id: string;
  customerId: string;
  customerName: string;
  customerNumber: string;
  balance: number;
  overdueAmount: number;
  oldestInvoiceAge: number;
  lastContactDate: string | null;
  lastPaymentDate: string | null;
  priority: 'critical' | 'high' | 'medium' | 'low';
  alertCount: number;
  noteCount: number;
  nextAction: string | null;
  nextActionDate: string | null;
}

// Search API
export interface SearchParams {
  query: string;
  type?: 'all' | 'customer' | 'invoice' | 'payment';
  limit?: number;
}

export interface SearchResult {
  type: 'customer' | 'invoice' | 'payment';
  id: string;
  title: string;
  subtitle: string;
  metadata: Record<string, string | number>;
}
