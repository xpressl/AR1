'use client';

import React, { useState, useEffect } from 'react';
import { Card, Table, LoadingSpinner, Badge, Button } from '@/components/common';
import { ExportButton } from '@/components/ExportButton';
import { BatchActionToolbar } from '@/components/BatchActionToolbar';
import { useRouter } from 'next/navigation';
import { Search, Filter } from 'lucide-react';

interface Invoice {
  id: number;
  invoice_number: string;
  customer_name: string;
  customer_number: string;
  invoice_date: string;
  due_date: string;
  amount: number;
  amount_due: number;
  status: string;
  days_past_due: number;
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export default function InvoicesPage() {
  const router = useRouter();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchInvoices();
  }, [statusFilter]);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter !== 'all') params.append('status', statusFilter);

      const response = await fetch(`/api/invoices?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch invoices');

      const data = await response.json();
      setInvoices(data.invoices || []);
    } catch (error) {
      console.error('Error fetching invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredInvoices = invoices.filter((inv) =>
    inv.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inv.customer_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleRowClick = (id: number) => {
    router.push(`/invoices/${id}`);
  };

  const handleBatchAction = async (action: string, ids: string[]) => {
    console.log(`Batch action: ${action}`, ids);
    // Implement batch actions here
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-neutral-900">Invoices</h1>
        <p className="text-neutral-600 mt-2">Manage and track customer invoices</p>
      </div>

      <BatchActionToolbar
        selectedCount={selectedIds.length}
        selectedIds={selectedIds}
        onClearSelection={() => setSelectedIds([])}
        onBatchAction={handleBatchAction}
        availableActions={['send-emails', 'export']}
      />

      <Card className="mb-6">
        <div className="flex items-center justify-between gap-4 p-4">
          <div className="flex items-center space-x-4 flex-1">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search invoices..."
                className="pl-10 pr-4 py-2 border border-neutral-300 rounded-md w-full"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <select
              className="border border-neutral-300 rounded-md px-3 py-2"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="Open">Open</option>
              <option value="Paid">Paid</option>
              <option value="Past Due">Past Due</option>
              <option value="Disputed">Disputed</option>
            </select>
          </div>

          <ExportButton exportType="invoices" filters={{ status: statusFilter }} />
        </div>
      </Card>

      <Card>
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <LoadingSpinner />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-neutral-200">
              <thead className="bg-neutral-50">
                <tr>
                  <th className="px-6 py-3 text-left">
                    <input type="checkbox" onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedIds(filteredInvoices.map(i => String(i.id)));
                      } else {
                        setSelectedIds([]);
                      }
                    }} />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">
                    Invoice #
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase">
                    Due Date
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase">
                    Amount Due
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-neutral-500 uppercase">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-neutral-200">
                {filteredInvoices.map((invoice) => (
                  <tr
                    key={invoice.id}
                    className="hover:bg-neutral-50 cursor-pointer"
                    onClick={() => handleRowClick(invoice.id)}
                  >
                    <td className="px-6 py-4" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(String(invoice.id))}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedIds([...selectedIds, String(invoice.id)]);
                          } else {
                            setSelectedIds(selectedIds.filter(id => id !== String(invoice.id)));
                          }
                        }}
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-600">
                      {invoice.invoice_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-neutral-900">
                        {invoice.customer_name}
                      </div>
                      <div className="text-sm text-neutral-500">
                        {invoice.customer_number}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                      {new Date(invoice.invoice_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                      {new Date(invoice.due_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-neutral-900">
                      {formatCurrency(invoice.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-semibold text-neutral-900">
                      {formatCurrency(invoice.amount_due)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <Badge
                        variant={
                          invoice.status === 'Paid' ? 'success' :
                          invoice.status === 'Past Due' ? 'error' :
                          invoice.status === 'Disputed' ? 'warning' :
                          'neutral'
                        }
                      >
                        {invoice.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredInvoices.length === 0 && (
              <div className="text-center py-12 text-neutral-500">
                No invoices found
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
