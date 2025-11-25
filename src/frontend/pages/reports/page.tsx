'use client';

import React, { useState, useEffect } from 'react';
import { Card, Table, LoadingSpinner, Badge } from '@/components/common';
import { ExportButton } from '@/components/ExportButton';
import { Search, Filter, Download } from 'lucide-react';

interface AgingReportRow {
  customer_id: string;
  customer_name: string;
  customer_number: string;
  total_balance: number;
  current: number;
  days_1_30: number;
  days_31_60: number;
  days_61_90: number;
  days_90_plus: number;
  oldest_invoice_days: number;
  contact_email: string;
  phone: string;
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(amount);
};

export default function AgingReportPage() {
  const [data, setData] = useState<AgingReportRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [minBalance, setMinBalance] = useState<number>(0);

  useEffect(() => {
    fetchAgingReport();
  }, [minBalance]);

  const fetchAgingReport = async () => {
    setLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams();
      if (minBalance > 0) {
        queryParams.append('min_balance', minBalance.toString());
      }

      const response = await fetch(
        `/api/v1/reports/aging-detail?${queryParams}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch aging report');
      }

      const result = await response.json();
      setData(result.invoices || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const filteredData = data.filter((row) =>
    row.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    row.customer_number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totals = filteredData.reduce(
    (acc, row) => ({
      total_balance: acc.total_balance + row.total_balance,
      current: acc.current + row.current,
      days_1_30: acc.days_1_30 + row.days_1_30,
      days_31_60: acc.days_31_60 + row.days_31_60,
      days_61_90: acc.days_61_90 + row.days_61_90,
      days_90_plus: acc.days_90_plus + row.days_90_plus,
    }),
    {
      total_balance: 0,
      current: 0,
      days_1_30: 0,
      days_31_60: 0,
      days_61_90: 0,
      days_90_plus: 0,
    }
  );

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-neutral-900">Aging Report</h1>
        <p className="text-neutral-600 mt-2">
          Detailed accounts receivable aging analysis
        </p>
      </div>

      {/* Filters and Actions */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4 p-4">
          <div className="flex items-center space-x-4 flex-1">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search customers..."
                className="pl-10 pr-4 py-2 border border-neutral-300 rounded-md w-full focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Min Balance Filter */}
            <div className="flex items-center space-x-2">
              <Filter className="w-5 h-5 text-neutral-400" />
              <select
                className="border border-neutral-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={minBalance}
                onChange={(e) => setMinBalance(Number(e.target.value))}
              >
                <option value="0">All Balances</option>
                <option value="100">$100+</option>
                <option value="500">$500+</option>
                <option value="1000">$1,000+</option>
                <option value="5000">$5,000+</option>
                <option value="10000">$10,000+</option>
              </select>
            </div>
          </div>

          {/* Export Button */}
          <ExportButton
            exportType="aging-report"
            filters={{ min_balance: minBalance }}
            onExportComplete={(filename) => {
              console.log('Export complete:', filename);
            }}
            onExportError={(error) => {
              console.error('Export failed:', error);
            }}
          />
        </div>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
        <Card className="p-4">
          <div className="text-sm text-neutral-600">Total AR</div>
          <div className="text-2xl font-bold text-neutral-900">
            {formatCurrency(totals.total_balance)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-600">Current</div>
          <div className="text-2xl font-bold text-success-600">
            {formatCurrency(totals.current)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-600">1-30 Days</div>
          <div className="text-2xl font-bold text-warning-600">
            {formatCurrency(totals.days_1_30)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-600">31-60 Days</div>
          <div className="text-2xl font-bold text-warning-600">
            {formatCurrency(totals.days_31_60)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-600">61-90 Days</div>
          <div className="text-2xl font-bold text-error-500">
            {formatCurrency(totals.days_61_90)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-neutral-600">90+ Days</div>
          <div className="text-2xl font-bold text-error-600">
            {formatCurrency(totals.days_90_plus)}
          </div>
        </Card>
      </div>

      {/* Table */}
      <Card>
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div className="p-6 text-center text-error-600">{error}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-neutral-200">
              <thead className="bg-neutral-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
                    Total Balance
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
                    Current
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
                    1-30
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
                    31-60
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
                    61-90
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-neutral-500 uppercase tracking-wider">
                    90+
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-neutral-500 uppercase tracking-wider">
                    Oldest
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-neutral-200">
                {filteredData.map((row) => (
                  <tr key={row.customer_id} className="hover:bg-neutral-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-neutral-900">
                        {row.customer_name}
                      </div>
                      <div className="text-sm text-neutral-500">
                        {row.customer_number}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-semibold text-neutral-900">
                      {formatCurrency(row.total_balance)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-success-600">
                      {formatCurrency(row.current)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-warning-600">
                      {formatCurrency(row.days_1_30)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-warning-600">
                      {formatCurrency(row.days_31_60)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-error-500">
                      {formatCurrency(row.days_61_90)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-error-600">
                      {formatCurrency(row.days_90_plus)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <Badge variant={row.oldest_invoice_days > 90 ? 'error' : row.oldest_invoice_days > 30 ? 'warning' : 'success'}>
                        {row.oldest_invoice_days} days
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredData.length === 0 && !loading && (
              <div className="text-center py-12 text-neutral-500">
                No customers found
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
