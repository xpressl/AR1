'use client';

import React, { useEffect, useState } from 'react';
import { Card, Badge, LoadingSpinner, Alert as AlertComponent } from '@/components/common';
import { AlertCircle, TrendingDown, Users, DollarSign, Clock, AlertTriangle } from 'lucide-react';

// Types
interface AgingBucket {
  count: number;
  amount: number;
}

interface DashboardData {
  total_ar: number;
  total_past_due: number;
  past_due_percent: number;
  aging: {
    current: AgingBucket;
    '1-30': AgingBucket;
    '31-60': AgingBucket;
    '61-90': AgingBucket;
    '90+': AgingBucket;
  };
  alerts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    total: number;
  };
  risk_indicators: {
    inactive_but_owing: { count: number; amount: number };
    over_credit_limit: { count: number; amount: number };
    broken_promises: number;
  };
  recent_cash_7_days: number;
  last_import: {
    status: string | null;
    timestamp: string | null;
  };
}

interface TopCustomer {
  id: number;
  name: string;
  total_balance: number;
  past_due_amount: number;
  oldest_days_past_due: number;
  credit_utilization: number;
  is_inactive: boolean;
}

// Format currency
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

// Aging Bar Chart Component
const AgingChart: React.FC<{ aging: DashboardData['aging'] }> = ({ aging }) => {
  const buckets = [
    { key: 'current', label: 'Current', color: 'bg-green-500' },
    { key: '1-30', label: '1-30', color: 'bg-lime-500' },
    { key: '31-60', label: '31-60', color: 'bg-yellow-500' },
    { key: '61-90', label: '61-90', color: 'bg-orange-500' },
    { key: '90+', label: '90+', color: 'bg-red-500' },
  ];

  const total = Object.values(aging).reduce((sum, b) => sum + b.amount, 0);

  return (
    <div className="space-y-4">
      <div className="flex h-8 rounded-lg overflow-hidden">
        {buckets.map(({ key, color }) => {
          const bucket = aging[key as keyof typeof aging];
          const percent = total > 0 ? (bucket.amount / total) * 100 : 0;
          return (
            <div
              key={key}
              className={`${color} transition-all duration-300`}
              style={{ width: `${percent}%` }}
              title={`${key}: ${formatCurrency(bucket.amount)}`}
            />
          );
        })}
      </div>
      <div className="grid grid-cols-5 gap-2 text-center">
        {buckets.map(({ key, label, color }) => {
          const bucket = aging[key as keyof typeof aging];
          const percent = total > 0 ? (bucket.amount / total) * 100 : 0;
          return (
            <div key={key} className="text-sm">
              <div className={`h-2 w-full ${color} rounded mb-1`} />
              <div className="font-medium">{label}</div>
              <div className="text-gray-600">{formatCurrency(bucket.amount)}</div>
              <div className="text-gray-400 text-xs">{percent.toFixed(0)}%</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Alert Tile Component with Blinking
const AlertTile: React.FC<{
  title: string;
  count: number;
  amount?: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  icon: React.ReactNode;
}> = ({ title, count, amount, severity, icon }) => {
  const severityStyles = {
    critical: 'bg-red-50 border-red-500 alert-critical-pulse',
    high: 'bg-orange-50 border-orange-500',
    medium: 'bg-yellow-50 border-yellow-500',
    low: 'bg-blue-50 border-blue-500',
  };

  const iconStyles = {
    critical: 'text-red-600 alert-icon-pulse',
    high: 'text-orange-600',
    medium: 'text-yellow-600',
    low: 'text-blue-600',
  };

  return (
    <div
      className={`p-4 rounded-lg border-l-4 cursor-pointer hover:shadow-md transition-shadow ${severityStyles[severity]}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-medium text-gray-600">{title}</div>
          <div className="text-2xl font-bold">{count}</div>
          {amount !== undefined && (
            <div className="text-sm text-gray-500">{formatCurrency(amount)}</div>
          )}
        </div>
        <div className={`${iconStyles[severity]}`}>{icon}</div>
      </div>
    </div>
  );
};

// Metric Card Component
const MetricCard: React.FC<{
  title: string;
  value: string;
  subtitle?: string;
  trend?: 'up' | 'down';
  icon: React.ReactNode;
}> = ({ title, value, subtitle, trend, icon }) => {
  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-medium text-gray-500">{title}</div>
          <div className="text-3xl font-bold mt-1">{value}</div>
          {subtitle && (
            <div className={`text-sm mt-1 ${trend === 'up' ? 'text-red-500' : 'text-green-500'}`}>
              {subtitle}
            </div>
          )}
        </div>
        <div className="text-gray-400">{icon}</div>
      </div>
    </Card>
  );
};

// Top Overdue Table Component
const TopOverdueTable: React.FC<{ customers: TopCustomer[] }> = ({ customers }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Past Due</th>
            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Days</th>
            <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Flags</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {customers.map((customer) => (
            <tr
              key={customer.id}
              className={`hover:bg-gray-50 cursor-pointer ${
                customer.oldest_days_past_due >= 90 ? 'alert-critical-pulse' : ''
              }`}
            >
              <td className="px-4 py-3">
                <div className="font-medium text-gray-900">{customer.name}</div>
              </td>
              <td className="px-4 py-3 text-right">
                <span className="font-medium text-red-600">
                  {formatCurrency(customer.past_due_amount)}
                </span>
              </td>
              <td className="px-4 py-3 text-right">
                <span
                  className={`font-medium ${
                    customer.oldest_days_past_due >= 90
                      ? 'text-red-600'
                      : customer.oldest_days_past_due >= 60
                      ? 'text-orange-600'
                      : 'text-yellow-600'
                  }`}
                >
                  {customer.oldest_days_past_due}
                </span>
              </td>
              <td className="px-4 py-3 text-center">
                <div className="flex justify-center gap-1">
                  {customer.is_inactive && (
                    <Badge variant="danger" size="sm">Inactive</Badge>
                  )}
                  {customer.credit_utilization >= 100 && (
                    <Badge variant="danger" size="sm">Over Limit</Badge>
                  )}
                  {customer.oldest_days_past_due >= 90 && (
                    <Badge variant="danger" size="sm">90+</Badge>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Main Dashboard Component
export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [topOverdue, setTopOverdue] = useState<TopCustomer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [summaryRes, overdueRes] = await Promise.all([
          fetch('/api/dashboard/summary'),
          fetch('/api/dashboard/top-overdue?limit=10'),
        ]);

        if (!summaryRes.ok || !overdueRes.ok) {
          throw new Error('Failed to fetch dashboard data');
        }

        const summaryData = await summaryRes.json();
        const overdueData = await overdueRes.json();

        setData(summaryData);
        setTopOverdue(overdueData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // Refresh every 5 minutes
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <AlertComponent variant="error" title="Error">
        {error}
      </AlertComponent>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AR Dashboard</h1>
          <p className="text-sm text-gray-500">
            Last import: {data.last_import.timestamp ? new Date(data.last_import.timestamp).toLocaleString() : 'Never'}
            {data.last_import.status && (
              <Badge
                variant={data.last_import.status === 'Success' ? 'success' : 'danger'}
                size="sm"
                className="ml-2"
              >
                {data.last_import.status}
              </Badge>
            )}
          </p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Refresh Data
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total AR"
          value={formatCurrency(data.total_ar)}
          icon={<DollarSign className="h-8 w-8" />}
        />
        <MetricCard
          title="Past Due"
          value={formatCurrency(data.total_past_due)}
          subtitle={`${data.past_due_percent.toFixed(0)}% of total`}
          trend="up"
          icon={<Clock className="h-8 w-8" />}
        />
        <MetricCard
          title="90+ Days"
          value={formatCurrency(data.aging['90+'].amount)}
          subtitle={`${data.aging['90+'].count} invoices`}
          icon={<AlertTriangle className="h-8 w-8" />}
        />
        <MetricCard
          title="Cash Last 7 Days"
          value={formatCurrency(data.recent_cash_7_days)}
          icon={<TrendingDown className="h-8 w-8" />}
        />
      </div>

      {/* Aging Chart */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Aging Summary</h2>
        <AgingChart aging={data.aging} />
      </Card>

      {/* Alert Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <AlertTile
          title="Inactive But Owing"
          count={data.risk_indicators.inactive_but_owing.count}
          amount={data.risk_indicators.inactive_but_owing.amount}
          severity={data.risk_indicators.inactive_but_owing.count > 0 ? 'critical' : 'low'}
          icon={<Users className="h-8 w-8" />}
        />
        <AlertTile
          title="Over Credit Limit"
          count={data.risk_indicators.over_credit_limit.count}
          amount={data.risk_indicators.over_credit_limit.amount}
          severity={data.risk_indicators.over_credit_limit.count > 0 ? 'critical' : 'low'}
          icon={<AlertCircle className="h-8 w-8" />}
        />
        <AlertTile
          title="Broken Promises"
          count={data.risk_indicators.broken_promises}
          severity={data.risk_indicators.broken_promises > 0 ? 'critical' : 'low'}
          icon={<AlertTriangle className="h-8 w-8" />}
        />
        <AlertTile
          title="Total Alerts"
          count={data.alerts.total}
          severity={data.alerts.critical > 0 ? 'critical' : data.alerts.high > 0 ? 'high' : 'medium'}
          icon={<AlertCircle className="h-8 w-8" />}
        />
      </div>

      {/* Top Overdue Customers */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Top Overdue Customers</h2>
          <a href="/worklist" className="text-blue-600 hover:underline text-sm">
            View Full Worklist →
          </a>
        </div>
        <TopOverdueTable customers={topOverdue} />
      </Card>
    </div>
  );
}
