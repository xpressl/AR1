'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Card, Badge, Button, LoadingSpinner, Modal } from '@/components/common';
import {
  Phone, Mail, FileText, Plus, AlertCircle, AlertTriangle,
  Clock, CreditCard, DollarSign, Calendar, MessageSquare,
  ChevronDown, Check, X, User, Building, MapPin
} from 'lucide-react';

interface Customer360Data {
  customer: {
    id: number;
    epicor_customer_id: string;
    name: string;
    dba_trade_name: string | null;
    billing_email: string | null;
    billing_phone: string | null;
    primary_contact_name: string | null;
    salesperson_id: string | null;
    terms_code: string | null;
    credit_limit: number;
    current_balance: number;
    status: string;
    customer_type: string | null;
    branch_id: string | null;
    credit_utilization: number;
    is_inactive: boolean;
    is_over_credit_limit: boolean;
    is_near_credit_limit: boolean;
    days_since_last_invoice: number | null;
    last_invoice_date: string | null;
    last_payment_date: string | null;
  };
  aging: {
    current: number;
    '1-30': number;
    '31-60': number;
    '61-90': number;
    '90+': number;
  };
  recent_invoices: Array<{
    id: number;
    invoice_number: string;
    invoice_date: string;
    due_date: string;
    original_amount: number;
    open_balance: number;
    days_past_due: number;
    aging_bucket: string;
    status: string;
  }>;
  recent_payments: Array<{
    id: number;
    payment_date: string;
    amount: number;
    payment_type: string | null;
    check_number: string | null;
  }>;
  recent_notes: Array<{
    id: number;
    note_type: string;
    content: string;
    created_at: string;
    promise_amount: number | null;
    promise_date: string | null;
    promise_status: string | null;
  }>;
  active_alerts: Array<{
    id: number;
    alert_type: string;
    severity: string;
    message: string | null;
    triggered_at: string;
    css_class: string;
    icon: string;
  }>;
  open_tasks: Array<{
    id: number;
    task_type: string;
    description: string | null;
    due_at: string;
    status: string;
  }>;
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(amount);
};

const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

// Credit Limit Bar Component
const CreditLimitBar: React.FC<{
  balance: number;
  limit: number;
  utilization: number;
}> = ({ balance, limit, utilization }) => {
  const isOver = balance > limit;
  const barPercent = Math.min(100, utilization);

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span>Balance: {formatCurrency(balance)}</span>
        <span>Limit: {formatCurrency(limit)}</span>
      </div>
      <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${
            isOver ? 'bg-red-500' :
            utilization >= 80 ? 'bg-orange-500' : 'bg-green-500'
          }`}
          style={{ width: `${barPercent}%` }}
        />
      </div>
      <div className="text-right text-sm">
        <span className={isOver ? 'text-red-600 font-bold' : ''}>
          {utilization.toFixed(1)}% utilized
          {isOver && ` (Over by ${formatCurrency(balance - limit)})`}
        </span>
      </div>
    </div>
  );
};

// Alert Banner Component (with blinking)
const AlertBanner: React.FC<{ alerts: Customer360Data['active_alerts'] }> = ({ alerts }) => {
  const criticalAlerts = alerts.filter(a => a.severity === 'Critical');

  if (criticalAlerts.length === 0) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 alert-critical-pulse">
      <div className="flex items-center gap-2 text-red-800 font-medium mb-2">
        <AlertCircle className="h-5 w-5 alert-icon-pulse" />
        CRITICAL ALERTS ({criticalAlerts.length})
      </div>
      <ul className="space-y-1 text-sm text-red-700">
        {criticalAlerts.map(alert => (
          <li key={alert.id} className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            {alert.message || alert.alert_type.replace(/_/g, ' ')}
          </li>
        ))}
      </ul>
    </div>
  );
};

// Aging Summary Component
const AgingSummary: React.FC<{ aging: Customer360Data['aging'] }> = ({ aging }) => {
  const buckets = [
    { key: 'current', label: 'Current', color: 'text-green-600' },
    { key: '1-30', label: '1-30', color: 'text-lime-600' },
    { key: '31-60', label: '31-60', color: 'text-yellow-600' },
    { key: '61-90', label: '61-90', color: 'text-orange-600' },
    { key: '90+', label: '90+', color: 'text-red-600' },
  ];

  return (
    <div className="grid grid-cols-5 gap-2">
      {buckets.map(({ key, label, color }) => (
        <div key={key} className="text-center">
          <div className="text-xs text-gray-500 uppercase">{label}</div>
          <div className={`text-lg font-bold ${color}`}>
            {formatCurrency(aging[key as keyof typeof aging])}
          </div>
        </div>
      ))}
    </div>
  );
};

// Invoice List Component
const InvoiceList: React.FC<{ invoices: Customer360Data['recent_invoices'] }> = ({ invoices }) => {
  return (
    <div className="space-y-2 max-h-[400px] overflow-y-auto">
      {invoices.map(inv => (
        <div
          key={inv.id}
          className={`p-3 rounded-lg border ${
            inv.days_past_due >= 90 ? 'border-red-200 bg-red-50' :
            inv.days_past_due >= 60 ? 'border-orange-200 bg-orange-50' :
            inv.days_past_due >= 30 ? 'border-yellow-200 bg-yellow-50' :
            'border-gray-200 bg-gray-50'
          }`}
        >
          <div className="flex justify-between items-start">
            <div>
              <div className="font-medium">{inv.invoice_number}</div>
              <div className="text-sm text-gray-500">
                Due: {formatDate(inv.due_date)}
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold">{formatCurrency(inv.open_balance)}</div>
              {inv.days_past_due > 0 && (
                <Badge
                  variant={inv.days_past_due >= 90 ? 'danger' : inv.days_past_due >= 60 ? 'warning' : 'default'}
                  size="sm"
                >
                  {inv.days_past_due} days
                </Badge>
              )}
            </div>
          </div>
        </div>
      ))}
      {invoices.length === 0 && (
        <div className="text-center py-4 text-gray-500">No open invoices</div>
      )}
    </div>
  );
};

// Notes Timeline Component
const NotesTimeline: React.FC<{ notes: Customer360Data['recent_notes'] }> = ({ notes }) => {
  const noteTypeIcons: Record<string, React.ReactNode> = {
    call: <Phone className="h-4 w-4" />,
    email: <Mail className="h-4 w-4" />,
    promise_to_pay: <DollarSign className="h-4 w-4" />,
    dispute: <AlertTriangle className="h-4 w-4" />,
    internal: <MessageSquare className="h-4 w-4" />,
  };

  const noteTypeColors: Record<string, string> = {
    call: 'bg-blue-100 text-blue-600',
    email: 'bg-green-100 text-green-600',
    promise_to_pay: 'bg-purple-100 text-purple-600',
    dispute: 'bg-orange-100 text-orange-600',
    internal: 'bg-gray-100 text-gray-600',
  };

  return (
    <div className="space-y-3 max-h-[400px] overflow-y-auto">
      {notes.map(note => (
        <div key={note.id} className="flex gap-3">
          <div className={`p-2 rounded-full ${noteTypeColors[note.note_type] || noteTypeColors.internal}`}>
            {noteTypeIcons[note.note_type] || noteTypeIcons.internal}
          </div>
          <div className="flex-1">
            <div className="flex justify-between items-start">
              <span className="font-medium capitalize">{note.note_type.replace(/_/g, ' ')}</span>
              <span className="text-xs text-gray-400">{formatDate(note.created_at)}</span>
            </div>
            <p className="text-sm text-gray-600 mt-1">{note.content}</p>
            {note.note_type === 'promise_to_pay' && note.promise_amount && (
              <div className="mt-2 p-2 bg-purple-50 rounded text-sm">
                <strong>Promise:</strong> {formatCurrency(note.promise_amount)} by {note.promise_date && formatDate(note.promise_date)}
                {note.promise_status && (
                  <Badge
                    variant={note.promise_status === 'kept' ? 'success' : note.promise_status === 'broken' ? 'danger' : 'default'}
                    size="sm"
                    className="ml-2"
                  >
                    {note.promise_status}
                  </Badge>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
      {notes.length === 0 && (
        <div className="text-center py-4 text-gray-500">No notes yet</div>
      )}
    </div>
  );
};

// Quick Actions Bar Component
const QuickActionsBar: React.FC<{
  onLogCall: () => void;
  onSendEmail: () => void;
  onAddNote: () => void;
  onSendStatement: () => void;
  onScheduleFollowup: () => void;
}> = ({ onLogCall, onSendEmail, onAddNote, onSendStatement, onScheduleFollowup }) => {
  return (
    <div className="flex flex-wrap gap-2">
      <Button variant="primary" size="sm" onClick={onLogCall}>
        <Phone className="h-4 w-4 mr-1" /> Log Call
      </Button>
      <Button variant="secondary" size="sm" onClick={onSendEmail}>
        <Mail className="h-4 w-4 mr-1" /> Send Email
      </Button>
      <Button variant="secondary" size="sm" onClick={onSendStatement}>
        <FileText className="h-4 w-4 mr-1" /> Statement
      </Button>
      <Button variant="secondary" size="sm" onClick={onAddNote}>
        <Plus className="h-4 w-4 mr-1" /> Add Note
      </Button>
      <Button variant="secondary" size="sm" onClick={onScheduleFollowup}>
        <Calendar className="h-4 w-4 mr-1" /> Follow-up
      </Button>
    </div>
  );
};

// Main Customer 360 Page
export default function Customer360Page() {
  const params = useParams();
  const customerId = params?.id as string;

  const [data, setData] = useState<Customer360Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCustomer360 = async () => {
      try {
        const res = await fetch(`/api/customers/${customerId}/360`);
        if (!res.ok) throw new Error('Customer not found');
        const customerData = await res.json();
        setData(customerData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading customer');
      } finally {
        setLoading(false);
      }
    };

    if (customerId) {
      fetchCustomer360();
    }
  }, [customerId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6">
        <Card className="p-8 text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900">Customer Not Found</h2>
          <p className="text-gray-500 mt-2">{error}</p>
          <Button className="mt-4" onClick={() => window.history.back()}>
            Go Back
          </Button>
        </Card>
      </div>
    );
  }

  const { customer, aging, recent_invoices, recent_payments, recent_notes, active_alerts } = data;

  return (
    <div className="p-6 space-y-6">
      {/* Header Section */}
      <Card className={`p-6 ${customer.status === 'On Hold' ? 'border-red-500 border-2' : ''}`}>
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{customer.name}</h1>
              <Badge
                variant={
                  customer.status === 'Active' ? 'success' :
                  customer.status === 'On Hold' ? 'danger' :
                  customer.status === 'Inactive' ? 'warning' : 'default'
                }
              >
                {customer.status}
              </Badge>
              {customer.is_inactive && (
                <Badge variant="danger" className="alert-icon-pulse">
                  INACTIVE {customer.days_since_last_invoice}+ DAYS
                </Badge>
              )}
            </div>
            {customer.dba_trade_name && (
              <p className="text-gray-500">DBA: {customer.dba_trade_name}</p>
            )}
            <p className="text-sm text-gray-400">ID: {customer.epicor_customer_id}</p>
          </div>

          <div className="text-right">
            <div className="text-sm text-gray-500">Terms: {customer.terms_code || 'N/A'}</div>
            <div className="text-sm text-gray-500">Salesperson: {customer.salesperson_id || 'N/A'}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div className="flex items-center gap-2 text-sm">
            <User className="h-4 w-4 text-gray-400" />
            {customer.primary_contact_name || 'No contact'}
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Phone className="h-4 w-4 text-gray-400" />
            {customer.billing_phone || 'No phone'}
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Mail className="h-4 w-4 text-gray-400" />
            {customer.billing_email || 'No email'}
          </div>
        </div>

        <div className="mt-4">
          <CreditLimitBar
            balance={customer.current_balance}
            limit={customer.credit_limit}
            utilization={customer.credit_utilization}
          />
        </div>
      </Card>

      {/* Critical Alerts Banner */}
      <AlertBanner alerts={active_alerts} />

      {/* Quick Actions */}
      <QuickActionsBar
        onLogCall={() => console.log('Log call')}
        onSendEmail={() => console.log('Send email')}
        onAddNote={() => console.log('Add note')}
        onSendStatement={() => console.log('Send statement')}
        onScheduleFollowup={() => console.log('Schedule followup')}
      />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Aging Summary */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Aging Summary</h2>
            <AgingSummary aging={aging} />
            <div className="mt-4 pt-4 border-t flex justify-between">
              <span className="font-medium">Total Balance:</span>
              <span className="font-bold text-xl">{formatCurrency(customer.current_balance)}</span>
            </div>
          </Card>

          {/* Open Invoices */}
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Open Invoices ({recent_invoices.length})</h2>
              <a href="#" className="text-blue-600 text-sm hover:underline">View All</a>
            </div>
            <InvoiceList invoices={recent_invoices} />
          </Card>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Activity Timeline */}
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Activity Timeline</h2>
              <Button variant="ghost" size="sm">
                <Plus className="h-4 w-4 mr-1" /> Add Note
              </Button>
            </div>
            <NotesTimeline notes={recent_notes} />
          </Card>

          {/* Active Alerts */}
          {active_alerts.length > 0 && (
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">Active Alerts ({active_alerts.length})</h2>
              <div className="space-y-2">
                {active_alerts.map(alert => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded-lg border-l-4 ${
                      alert.severity === 'Critical' ? 'border-red-500 bg-red-50 alert-critical-pulse' :
                      alert.severity === 'High' ? 'border-orange-500 bg-orange-50' :
                      alert.severity === 'Medium' ? 'border-yellow-500 bg-yellow-50' :
                      'border-blue-500 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <AlertCircle className={`h-4 w-4 ${
                        alert.severity === 'Critical' ? 'text-red-600 alert-icon-pulse' :
                        alert.severity === 'High' ? 'text-orange-600' :
                        'text-yellow-600'
                      }`} />
                      <span className="font-medium capitalize">{alert.alert_type.replace(/_/g, ' ')}</span>
                      <Badge
                        variant={
                          alert.severity === 'Critical' ? 'danger' :
                          alert.severity === 'High' ? 'warning' : 'default'
                        }
                        size="sm"
                      >
                        {alert.severity}
                      </Badge>
                    </div>
                    {alert.message && (
                      <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Recent Payments */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Recent Payments</h2>
            <div className="space-y-2">
              {recent_payments.slice(0, 5).map(payment => (
                <div key={payment.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <div>
                    <div className="font-medium">{formatCurrency(payment.amount)}</div>
                    <div className="text-sm text-gray-500">
                      {payment.payment_type} {payment.check_number && `#${payment.check_number}`}
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">{formatDate(payment.payment_date)}</div>
                </div>
              ))}
              {recent_payments.length === 0 && (
                <div className="text-center py-4 text-gray-500">No recent payments</div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
