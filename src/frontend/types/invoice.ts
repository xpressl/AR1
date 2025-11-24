/**
 * Invoice Types for AR Control Hub
 */

export type InvoiceStatus = 'open' | 'partial' | 'paid' | 'void' | 'disputed';
export type InvoiceType = 'standard' | 'credit_memo' | 'debit_memo' | 'finance_charge';

export interface Invoice {
  id: string;
  invoiceNumber: string;
  customerId: string;
  customerNumber: string;
  customerName: string;
  invoiceType: InvoiceType;
  invoiceDate: string;
  dueDate: string;
  amount: number;
  taxAmount: number;
  totalAmount: number;
  balance: number;
  status: InvoiceStatus;
  poNumber?: string;
  reference?: string;
  terms: string;
  salesRep?: string;
  shipToAddress?: Address;
  lineItems: InvoiceLineItem[];
  payments: InvoicePaymentApplication[];
  createdAt: string;
  updatedAt: string;
}

export interface Address {
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
}

export interface InvoiceLineItem {
  id: string;
  lineNumber: number;
  itemCode: string;
  description: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  taxRate: number;
  taxAmount: number;
  lineTotal: number;
}

export interface InvoicePaymentApplication {
  id: string;
  paymentId: string;
  paymentDate: string;
  appliedAmount: number;
  reference: string;
  paymentMethod: string;
}

export interface InvoiceSummary {
  id: string;
  invoiceNumber: string;
  customerId: string;
  customerName: string;
  invoiceDate: string;
  dueDate: string;
  totalAmount: number;
  balance: number;
  status: InvoiceStatus;
  daysOverdue: number;
  hasDispute: boolean;
}

// Invoice filter params
export interface InvoiceFilterParams {
  search?: string;
  customerId?: string;
  status?: InvoiceStatus;
  invoiceType?: InvoiceType;
  minAmount?: number;
  maxAmount?: number;
  startDate?: string;
  endDate?: string;
  overdueOnly?: boolean;
  agingBucket?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Payment types
export type PaymentMethod = 'check' | 'ach' | 'wire' | 'credit_card' | 'cash' | 'other';
export type PaymentStatus = 'pending' | 'applied' | 'partial' | 'returned' | 'void';

export interface Payment {
  id: string;
  paymentNumber: string;
  customerId: string;
  customerNumber: string;
  customerName: string;
  paymentDate: string;
  amount: number;
  appliedAmount: number;
  unappliedAmount: number;
  paymentMethod: PaymentMethod;
  reference: string;
  checkNumber?: string;
  bankAccount?: string;
  status: PaymentStatus;
  applications: PaymentApplication[];
  createdAt: string;
  updatedAt: string;
}

export interface PaymentApplication {
  id: string;
  invoiceId: string;
  invoiceNumber: string;
  appliedAmount: number;
  appliedDate: string;
}

export interface PaymentSummary {
  id: string;
  paymentNumber: string;
  customerId: string;
  customerName: string;
  paymentDate: string;
  amount: number;
  appliedAmount: number;
  unappliedAmount: number;
  paymentMethod: PaymentMethod;
  status: PaymentStatus;
}

// Payment filter params
export interface PaymentFilterParams {
  search?: string;
  customerId?: string;
  status?: PaymentStatus;
  paymentMethod?: PaymentMethod;
  minAmount?: number;
  maxAmount?: number;
  startDate?: string;
  endDate?: string;
  hasUnapplied?: boolean;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Dispute types
export type DisputeStatus = 'open' | 'investigating' | 'resolved' | 'escalated' | 'closed';
export type DisputeReason =
  | 'pricing_error'
  | 'quantity_mismatch'
  | 'damaged_goods'
  | 'missing_items'
  | 'duplicate_invoice'
  | 'service_issue'
  | 'unauthorized_charge'
  | 'other';

export interface Dispute {
  id: string;
  invoiceId: string;
  invoiceNumber: string;
  customerId: string;
  customerName: string;
  amount: number;
  reason: DisputeReason;
  description: string;
  status: DisputeStatus;
  priority: 'low' | 'medium' | 'high';
  assignedTo: string | null;
  assignedToName: string | null;
  resolution?: string;
  resolvedAt?: string;
  resolvedBy?: string;
  createdAt: string;
  updatedAt: string;
}

export interface DisputeFilterParams {
  search?: string;
  customerId?: string;
  status?: DisputeStatus;
  reason?: DisputeReason;
  priority?: 'low' | 'medium' | 'high';
  assignedTo?: string;
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}
