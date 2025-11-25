'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, Badge, Button, LoadingSpinner } from '@/components/common';
import { ArrowLeft, Download, Mail } from 'lucide-react';

interface InvoiceDetail {
  id: number;
  invoice_number: string;
  customer_name: string;
  customer_number: string;
  invoice_date: string;
  due_date: string;
  amount: number;
  amount_paid: number;
  amount_due: number;
  status: string;
  po_number?: string;
  description?: string;
  line_items?: Array<{
    description: string;
    quantity: number;
    unit_price: number;
    amount: number;
  }>;
  payments?: Array<{
    payment_date: string;
    amount: number;
    reference_number: string;
  }>;
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
};

export default function InvoiceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      fetchInvoiceDetail(params.id as string);
    }
  }, [params.id]);

  const fetchInvoiceDetail = async (id: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/invoices/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch invoice');

      const data = await response.json();
      setInvoice(data);
    } catch (error) {
      console.error('Error fetching invoice:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="text-center text-error-600">Invoice not found</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <Button
          variant="ghost"
          leftIcon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => router.back()}
        >
          Back
        </Button>
      </div>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900">
            Invoice {invoice.invoice_number}
          </h1>
          <p className="text-neutral-600 mt-1">{invoice.customer_name}</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="secondary" leftIcon={<Mail className="w-4 h-4" />}>
            Send Email
          </Button>
          <Button variant="secondary" leftIcon={<Download className="w-4 h-4" />}>
            Download PDF
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="p-4">
          <div className="text-sm text-neutral-600">Total Amount</div>
          <div className="text-2xl font-bold text-neutral-900">
            {formatCurrency(invoice.amount)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-600">Amount Paid</div>
          <div className="text-2xl font-bold text-success-600">
            {formatCurrency(invoice.amount_paid)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-600">Amount Due</div>
          <div className="text-2xl font-bold text-error-600">
            {formatCurrency(invoice.amount_due)}
          </div>
        </Card>
      </div>

      <Card className="mb-6 p-6">
        <h2 className="text-lg font-semibold mb-4">Invoice Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-neutral-600">Invoice Date</div>
            <div className="font-medium">{new Date(invoice.invoice_date).toLocaleDateString()}</div>
          </div>
          <div>
            <div className="text-sm text-neutral-600">Due Date</div>
            <div className="font-medium">{new Date(invoice.due_date).toLocaleDateString()}</div>
          </div>
          <div>
            <div className="text-sm text-neutral-600">Status</div>
            <div>
              <Badge
                variant={
                  invoice.status === 'Paid' ? 'success' :
                  invoice.status === 'Past Due' ? 'error' :
                  'neutral'
                }
              >
                {invoice.status}
              </Badge>
            </div>
          </div>
          {invoice.po_number && (
            <div>
              <div className="text-sm text-neutral-600">PO Number</div>
              <div className="font-medium">{invoice.po_number}</div>
            </div>
          )}
        </div>
        {invoice.description && (
          <div className="mt-4">
            <div className="text-sm text-neutral-600">Description</div>
            <div className="mt-1">{invoice.description}</div>
          </div>
        )}
      </Card>

      {invoice.payments && invoice.payments.length > 0 && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Payment History</h2>
          <div className="space-y-2">
            {invoice.payments.map((payment, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-neutral-50 rounded">
                <div>
                  <div className="font-medium">{new Date(payment.payment_date).toLocaleDateString()}</div>
                  <div className="text-sm text-neutral-600">{payment.reference_number}</div>
                </div>
                <div className="text-success-600 font-semibold">
                  {formatCurrency(payment.amount)}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
