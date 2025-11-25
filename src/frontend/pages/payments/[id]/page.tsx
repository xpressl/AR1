'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, Button, LoadingSpinner } from '@/components/common';
import { ArrowLeft } from 'lucide-react';

interface PaymentDetail {
  id: number;
  payment_number: string;
  customer_name: string;
  payment_date: string;
  amount: number;
  payment_method: string;
  reference_number: string;
  notes: string;
  applications: Array<{
    invoice_number: string;
    amount_applied: number;
  }>;
}

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

export default function PaymentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [payment, setPayment] = useState<PaymentDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) fetchPayment(params.id as string);
  }, [params.id]);

  const fetchPayment = async (id: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/payments/${id}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` },
      });
      if (!response.ok) throw new Error('Failed to fetch payment');
      const data = await response.json();
      setPayment(data);
    } catch (error) {
      console.error('Error:', error);
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

  if (!payment) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="text-center text-error-600">Payment not found</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <Button
        variant="ghost"
        leftIcon={<ArrowLeft className="w-4 h-4" />}
        onClick={() => router.back()}
        className="mb-6"
      >
        Back
      </Button>

      <h1 className="text-3xl font-bold text-neutral-900 mb-6">
        Payment {payment.payment_number}
      </h1>

      <Card className="p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Payment Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-neutral-600">Customer</div>
            <div className="font-medium">{payment.customer_name}</div>
          </div>
          <div>
            <div className="text-sm text-neutral-600">Payment Date</div>
            <div className="font-medium">{new Date(payment.payment_date).toLocaleDateString()}</div>
          </div>
          <div>
            <div className="text-sm text-neutral-600">Amount</div>
            <div className="text-2xl font-bold text-success-600">{formatCurrency(payment.amount)}</div>
          </div>
          <div>
            <div className="text-sm text-neutral-600">Payment Method</div>
            <div className="font-medium">{payment.payment_method}</div>
          </div>
          <div>
            <div className="text-sm text-neutral-600">Reference Number</div>
            <div className="font-medium">{payment.reference_number}</div>
          </div>
        </div>
        {payment.notes && (
          <div className="mt-4">
            <div className="text-sm text-neutral-600">Notes</div>
            <div className="mt-1">{payment.notes}</div>
          </div>
        )}
      </Card>

      {payment.applications && payment.applications.length > 0 && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Applied to Invoices</h2>
          <div className="space-y-2">
            {payment.applications.map((app, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-neutral-50 rounded">
                <div className="font-medium">{app.invoice_number}</div>
                <div className="text-success-600 font-semibold">{formatCurrency(app.amount_applied)}</div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
