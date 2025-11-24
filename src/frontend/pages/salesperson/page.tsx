'use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  DollarSign,
  AlertTriangle,
  Clock,
  FileText,
  Phone,
  Mail,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Search,
  Eye,
} from 'lucide-react';

interface CustomerSummary {
  id: number;
  epicor_customer_id: string;
  name: string;
  current_balance: number;
  credit_limit: number;
  credit_utilization: number;
  past_due_amount: number;
  oldest_invoice_days: number;
  alert_count: number;
  has_critical_alert: boolean;
  last_contact_date?: string;
  status: string;
}

interface SalespersonStats {
  total_customers: number;
  total_ar_balance: number;
  total_past_due: number;
  critical_alerts: number;
  accounts_over_limit: number;
  average_days_to_pay: number;
}

export default function SalespersonPortalPage() {
  const [customers, setCustomers] = useState<CustomerSummary[]>([]);
  const [stats, setStats] = useState<SalespersonStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'balance' | 'past_due' | 'alerts'>('past_due');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // In production, this would filter by the logged-in salesperson's ID
      const [customersRes, statsRes] = await Promise.all([
        fetch('/api/salesperson/customers'),
        fetch('/api/salesperson/stats')
      ]);

      const customersData = await customersRes.json();
      const statsData = await statsRes.json();

      setCustomers(customersData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers
    .filter(c =>
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.epicor_customer_id.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'balance') return b.current_balance - a.current_balance;
      if (sortBy === 'past_due') return b.past_due_amount - a.past_due_amount;
      if (sortBy === 'alerts') return b.alert_count - a.alert_count;
      return 0;
    });

  const getStatusColor = (customer: CustomerSummary) => {
    if (customer.has_critical_alert) return 'border-l-red-500';
    if (customer.past_due_amount > 0) return 'border-l-yellow-500';
    if (customer.credit_utilization > 80) return 'border-l-orange-500';
    return 'border-l-green-500';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
          <Users className="h-4 w-4" />
          <span>Salesperson Portal</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900">My Accounts</h1>
        <p className="text-gray-500">View AR status for your assigned customers (read-only)</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
              <Users className="h-4 w-4" />
              My Customers
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_customers}</div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
              <DollarSign className="h-4 w-4" />
              Total AR Balance
            </div>
            <div className="text-2xl font-bold text-gray-900">
              ${stats.total_ar_balance.toLocaleString()}
            </div>
          </div>

          <div className={`rounded-lg border p-4 ${stats.total_past_due > 0 ? 'bg-yellow-50 border-yellow-200' : 'bg-white'}`}>
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
              <Clock className="h-4 w-4" />
              Past Due
            </div>
            <div className={`text-2xl font-bold ${stats.total_past_due > 0 ? 'text-yellow-600' : 'text-gray-400'}`}>
              ${stats.total_past_due.toLocaleString()}
            </div>
          </div>

          <div className={`rounded-lg border p-4 ${stats.critical_alerts > 0 ? 'bg-red-50 border-red-200 alert-critical-pulse' : 'bg-white'}`}>
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
              <AlertTriangle className="h-4 w-4" />
              Critical Alerts
            </div>
            <div className={`text-2xl font-bold ${stats.critical_alerts > 0 ? 'text-red-600' : 'text-gray-400'}`}>
              {stats.critical_alerts}
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
              <TrendingUp className="h-4 w-4" />
              Over Credit Limit
            </div>
            <div className={`text-2xl font-bold ${stats.accounts_over_limit > 0 ? 'text-orange-600' : 'text-gray-400'}`}>
              {stats.accounts_over_limit}
            </div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
              <Clock className="h-4 w-4" />
              Avg Days to Pay
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.average_days_to_pay}</div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border p-4 mb-6">
        <div className="flex flex-col md:flex-row md:items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search customers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="past_due">Past Due Amount</option>
              <option value="balance">Total Balance</option>
              <option value="alerts">Alert Count</option>
            </select>
          </div>
        </div>
      </div>

      {/* Customer List */}
      <div className="bg-white rounded-lg border">
        <div className="p-4 border-b">
          <h2 className="font-semibold text-gray-900">Customer Accounts</h2>
          <p className="text-sm text-gray-500">{filteredCustomers.length} accounts</p>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading accounts...</div>
        ) : filteredCustomers.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No accounts found.
          </div>
        ) : (
          <div className="divide-y">
            {filteredCustomers.map((customer) => (
              <div
                key={customer.id}
                className={`p-4 border-l-4 ${getStatusColor(customer)} hover:bg-gray-50 transition-colors`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-medium text-gray-900">{customer.name}</h3>
                      <span className="text-sm text-gray-500">#{customer.epicor_customer_id}</span>
                      {customer.has_critical_alert && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700 animate-pulse">
                          <AlertTriangle className="h-3 w-3" />
                          Critical Alert
                        </span>
                      )}
                      {customer.status === 'Inactive' && (
                        <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                          Inactive
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Balance:</span>
                        <span className="ml-2 font-medium">${customer.current_balance.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Past Due:</span>
                        <span className={`ml-2 font-medium ${customer.past_due_amount > 0 ? 'text-red-600' : 'text-gray-600'}`}>
                          ${customer.past_due_amount.toLocaleString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Credit Used:</span>
                        <span className={`ml-2 font-medium ${customer.credit_utilization > 80 ? 'text-orange-600' : 'text-gray-600'}`}>
                          {customer.credit_utilization}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Oldest Invoice:</span>
                        <span className={`ml-2 font-medium ${customer.oldest_invoice_days > 60 ? 'text-red-600' : customer.oldest_invoice_days > 30 ? 'text-yellow-600' : 'text-gray-600'}`}>
                          {customer.oldest_invoice_days} days
                        </span>
                      </div>
                    </div>

                    {/* Credit Utilization Bar */}
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>Credit Limit: ${customer.credit_limit.toLocaleString()}</span>
                        <span>{customer.credit_utilization}% used</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            customer.credit_utilization > 100 ? 'bg-red-500' :
                            customer.credit_utilization > 80 ? 'bg-orange-500' :
                            customer.credit_utilization > 50 ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(customer.credit_utilization, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 ml-4">
                    <a
                      href={`/customers/${customer.id}`}
                      className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                      title="View Details"
                    >
                      <Eye className="h-5 w-5" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Read-Only Notice */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-3">
          <Eye className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-900">Read-Only Access</h3>
            <p className="text-sm text-blue-700 mt-1">
              This portal provides view-only access to your assigned customer accounts.
              To request credit limit changes or report issues, please contact the AR team.
            </p>
          </div>
        </div>
      </div>

      {/* CSS for blinking animation */}
      <style jsx global>{`
        .alert-critical-pulse {
          animation: critical-pulse 1.5s ease-in-out infinite;
        }
        @keyframes critical-pulse {
          0%, 100% {
            background-color: #FEF2F2;
            border-color: #FECACA;
          }
          50% {
            background-color: #FEE2E2;
            border-color: #FCA5A5;
          }
        }
      `}</style>
    </div>
  );
}
