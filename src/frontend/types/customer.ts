/**
 * Customer Types for AR Control Hub
 */

export type CustomerStatus = 'active' | 'inactive' | 'hold' | 'cod';
export type PaymentTerms = 'net_10' | 'net_15' | 'net_30' | 'net_45' | 'net_60' | 'cod' | 'cia';

export interface Customer {
  id: string;
  customerNumber: string;
  name: string;
  status: CustomerStatus;
  creditLimit: number;
  currentBalance: number;
  availableCredit: number;
  paymentTerms: PaymentTerms;
  primaryContact: ContactInfo | null;
  billingAddress: Address;
  shippingAddress: Address | null;
  collectorId: string | null;
  collectorName: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ContactInfo {
  name: string;
  email: string;
  phone: string;
  title?: string;
}

export interface Address {
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
}

export interface CustomerSummary {
  id: string;
  customerNumber: string;
  name: string;
  status: CustomerStatus;
  currentBalance: number;
  overdueBalance: number;
  creditLimit: number;
  utilizationPercent: number;
  lastPaymentDate: string | null;
  lastPaymentAmount: number | null;
  avgDaysToPay: number | null;
  alertCount: number;
}

export interface CustomerDetail extends Customer {
  summary: CustomerAccountSummary;
  agingBuckets: CustomerAgingBucket[];
  recentInvoices: CustomerInvoiceSummary[];
  recentPayments: CustomerPaymentSummary[];
  creditHistory: CreditHistoryEntry[];
  notes: CustomerNote[];
}

export interface CustomerAccountSummary {
  totalBalance: number;
  currentBalance: number;
  overdueBalance: number;
  unappliedPayments: number;
  creditMemos: number;
  avgDaysToPay: number;
  dso: number;
  invoiceCount: number;
  openInvoiceCount: number;
}

export interface CustomerAgingBucket {
  bucket: 'current' | '1-30' | '31-60' | '61-90' | '90+';
  amount: number;
  invoiceCount: number;
}

export interface CustomerInvoiceSummary {
  id: string;
  invoiceNumber: string;
  invoiceDate: string;
  dueDate: string;
  amount: number;
  balance: number;
  status: 'open' | 'partial' | 'paid' | 'void';
  daysOverdue: number;
}

export interface CustomerPaymentSummary {
  id: string;
  paymentDate: string;
  amount: number;
  paymentMethod: string;
  reference: string;
  appliedAmount: number;
  unappliedAmount: number;
}

export interface CreditHistoryEntry {
  id: string;
  date: string;
  action: 'limit_change' | 'status_change' | 'hold_placed' | 'hold_released' | 'cod_assigned';
  previousValue: string;
  newValue: string;
  reason: string;
  userId: string;
  userName: string;
}

export interface CustomerNote {
  id: string;
  content: string;
  noteType: 'general' | 'call' | 'email' | 'payment' | 'dispute' | 'promise';
  createdAt: string;
  createdBy: string;
  createdByName: string;
  followUpDate?: string;
  isPrivate: boolean;
}

// Customer filter params
export interface CustomerFilterParams {
  search?: string;
  status?: CustomerStatus;
  collectorId?: string;
  minBalance?: number;
  maxBalance?: number;
  overdueOnly?: boolean;
  agingBucket?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Customer actions
export interface UpdateCreditLimitRequest {
  newLimit: number;
  reason: string;
}

export interface PlaceCreditHoldRequest {
  reason: string;
  holdType: 'full' | 'partial';
  threshold?: number;
}

export interface AssignCollectorRequest {
  collectorId: string;
}

export interface AddNoteRequest {
  content: string;
  noteType: CustomerNote['noteType'];
  followUpDate?: string;
  isPrivate?: boolean;
}
