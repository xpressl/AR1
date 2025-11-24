'use client';

import React, { useEffect, useState } from 'react';
import { Card, Badge, Button, Input, LoadingSpinner } from '@/components/common';
import {
  Phone, Mail, Calendar, AlertCircle, AlertTriangle,
  Users, CreditCard, Clock, ChevronRight, Search,
  Filter, SortAsc, SortDesc
} from 'lucide-react';

interface WorklistItem {
  customer_id: number;
  customer_name: string;
  priority_score: number;
  total_balance: number;
  oldest_days_past_due: number;
  credit_utilization: number;
  is_inactive: boolean;
  is_over_limit: boolean;
  alert_types: string[];
  has_critical_alert: boolean;
  last_contact_date?: string;
  next_followup_date?: string;
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

// Priority indicator component
const PriorityIndicator: React.FC<{ score: number }> = ({ score }) => {
  let color = 'bg-green-500';
  if (score >= 100) color = 'bg-red-500';
  else if (score >= 75) color = 'bg-orange-500';
  else if (score >= 50) color = 'bg-yellow-500';

  return (
    <div className="flex items-center gap-2">
      <div className={`w-3 h-3 rounded-full ${color}`} />
      <span className="text-sm font-medium">{score}</span>
    </div>
  );
};

// Alert icons component
const AlertIcons: React.FC<{ item: WorklistItem }> = ({ item }) => {
  const icons = [];

  if (item.is_inactive) {
    icons.push(
      <div key="inactive" className="tooltip" title="Inactive (no purchases 90+ days)">
        <Users className={`h-4 w-4 ${item.has_critical_alert ? 'text-red-600 alert-icon-pulse' : 'text-orange-500'}`} />
      </div>
    );
  }

  if (item.is_over_limit) {
    icons.push(
      <div key="over-limit" className="tooltip" title="Over credit limit">
        <CreditCard className="h-4 w-4 text-red-600 alert-icon-pulse" />
      </div>
    );
  }

  if (item.oldest_days_past_due >= 90) {
    icons.push(
      <div key="90plus" className="tooltip" title="90+ days past due">
        <Clock className="h-4 w-4 text-red-600 alert-icon-pulse" />
      </div>
    );
  } else if (item.oldest_days_past_due >= 60) {
    icons.push(
      <div key="60plus" className="tooltip" title="60+ days past due">
        <Clock className="h-4 w-4 text-orange-500" />
      </div>
    );
  }

  if (item.alert_types.includes('broken_promise')) {
    icons.push(
      <div key="broken-promise" className="tooltip" title="Broken promise">
        <AlertTriangle className="h-4 w-4 text-red-600 alert-icon-pulse" />
      </div>
    );
  }

  return <div className="flex gap-1">{icons}</div>;
};

// Worklist row component
const WorklistRow: React.FC<{
  item: WorklistItem;
  onSelect: (id: number) => void;
}> = ({ item, onSelect }) => {
  const rowClass = item.has_critical_alert
    ? 'alert-critical-pulse cursor-pointer'
    : 'hover:bg-gray-50 cursor-pointer';

  return (
    <tr
      className={rowClass}
      onClick={() => onSelect(item.customer_id)}
    >
      <td className="px-4 py-3">
        <PriorityIndicator score={item.priority_score} />
      </td>
      <td className="px-4 py-3">
        <div className="font-medium text-gray-900">{item.customer_name}</div>
        <div className="text-sm text-gray-500">ID: {item.customer_id}</div>
      </td>
      <td className="px-4 py-3 text-right">
        <span className="font-medium">{formatCurrency(item.total_balance)}</span>
      </td>
      <td className="px-4 py-3 text-right">
        <span className={`font-medium ${
          item.oldest_days_past_due >= 90 ? 'text-red-600' :
          item.oldest_days_past_due >= 60 ? 'text-orange-600' :
          item.oldest_days_past_due >= 30 ? 'text-yellow-600' : 'text-gray-600'
        }`}>
          {item.oldest_days_past_due} days
        </span>
      </td>
      <td className="px-4 py-3 text-right">
        <div className="flex items-center justify-end gap-2">
          <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${
                item.credit_utilization >= 100 ? 'bg-red-500' :
                item.credit_utilization >= 80 ? 'bg-orange-500' : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(100, item.credit_utilization)}%` }}
            />
          </div>
          <span className="text-sm w-12 text-right">{item.credit_utilization.toFixed(0)}%</span>
        </div>
      </td>
      <td className="px-4 py-3 text-center">
        <AlertIcons item={item} />
      </td>
      <td className="px-4 py-3 text-center">
        <div className="flex gap-1 justify-center">
          <button
            className="p-1.5 hover:bg-blue-100 rounded"
            title="Log Call"
            onClick={(e) => { e.stopPropagation(); /* TODO: Open call modal */ }}
          >
            <Phone className="h-4 w-4 text-blue-600" />
          </button>
          <button
            className="p-1.5 hover:bg-green-100 rounded"
            title="Send Email"
            onClick={(e) => { e.stopPropagation(); /* TODO: Open email modal */ }}
          >
            <Mail className="h-4 w-4 text-green-600" />
          </button>
          <button
            className="p-1.5 hover:bg-purple-100 rounded"
            title="Schedule Follow-up"
            onClick={(e) => { e.stopPropagation(); /* TODO: Open schedule modal */ }}
          >
            <Calendar className="h-4 w-4 text-purple-600" />
          </button>
        </div>
      </td>
      <td className="px-4 py-3 text-center">
        <ChevronRight className="h-5 w-5 text-gray-400" />
      </td>
    </tr>
  );
};

// Main Worklist Page
export default function WorklistPage() {
  const [items, setItems] = useState<WorklistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'priority_score' | 'total_balance' | 'oldest_days_past_due'>('priority_score');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filters, setFilters] = useState({
    criticalOnly: false,
    inactiveOnly: false,
    overLimitOnly: false,
  });

  useEffect(() => {
    const fetchWorklist = async () => {
      try {
        const res = await fetch('/api/dashboard/worklist-preview?limit=100');
        if (!res.ok) throw new Error('Failed to fetch');
        const data = await res.json();
        setItems(data);
      } catch (err) {
        console.error('Error fetching worklist:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWorklist();
  }, []);

  // Filter and sort items
  const filteredItems = items
    .filter(item => {
      if (search) {
        const searchLower = search.toLowerCase();
        if (!item.customer_name.toLowerCase().includes(searchLower) &&
            !item.customer_id.toString().includes(searchLower)) {
          return false;
        }
      }
      if (filters.criticalOnly && !item.has_critical_alert) return false;
      if (filters.inactiveOnly && !item.is_inactive) return false;
      if (filters.overLimitOnly && !item.is_over_limit) return false;
      return true;
    })
    .sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
    });

  const handleSort = (column: typeof sortBy) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const handleSelectCustomer = (customerId: number) => {
    window.location.href = `/customers/${customerId}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Collections Worklist</h1>
          <p className="text-sm text-gray-500">
            {filteredItems.length} accounts to contact
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary">
            <Mail className="h-4 w-4 mr-2" />
            Bulk Statements
          </Button>
          <Button variant="primary">
            <Phone className="h-4 w-4 mr-2" />
            Start Calling
          </Button>
        </div>
      </div>

      {/* Filters Bar */}
      <Card className="p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Search customers..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <button
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                filters.criticalOnly
                  ? 'bg-red-100 text-red-700 border border-red-300'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              onClick={() => setFilters(f => ({ ...f, criticalOnly: !f.criticalOnly }))}
            >
              <AlertCircle className="h-3 w-3 inline mr-1" />
              Critical Only
            </button>
            <button
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                filters.inactiveOnly
                  ? 'bg-orange-100 text-orange-700 border border-orange-300'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              onClick={() => setFilters(f => ({ ...f, inactiveOnly: !f.inactiveOnly }))}
            >
              <Users className="h-3 w-3 inline mr-1" />
              Inactive
            </button>
            <button
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                filters.overLimitOnly
                  ? 'bg-purple-100 text-purple-700 border border-purple-300'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              onClick={() => setFilters(f => ({ ...f, overLimitOnly: !f.overLimitOnly }))}
            >
              <CreditCard className="h-3 w-3 inline mr-1" />
              Over Limit
            </button>
          </div>
        </div>
      </Card>

      {/* Worklist Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('priority_score')}
                >
                  <div className="flex items-center gap-1">
                    Priority
                    {sortBy === 'priority_score' && (sortOrder === 'desc' ? <SortDesc className="h-3 w-3" /> : <SortAsc className="h-3 w-3" />)}
                  </div>
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Customer
                </th>
                <th
                  className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('total_balance')}
                >
                  <div className="flex items-center justify-end gap-1">
                    Balance
                    {sortBy === 'total_balance' && (sortOrder === 'desc' ? <SortDesc className="h-3 w-3" /> : <SortAsc className="h-3 w-3" />)}
                  </div>
                </th>
                <th
                  className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('oldest_days_past_due')}
                >
                  <div className="flex items-center justify-end gap-1">
                    Oldest Due
                    {sortBy === 'oldest_days_past_due' && (sortOrder === 'desc' ? <SortDesc className="h-3 w-3" /> : <SortAsc className="h-3 w-3" />)}
                  </div>
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Credit Util
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Alerts
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
                <th className="px-4 py-3 w-10"></th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredItems.map((item) => (
                <WorklistRow
                  key={item.customer_id}
                  item={item}
                  onSelect={handleSelectCustomer}
                />
              ))}
            </tbody>
          </table>
        </div>

        {filteredItems.length === 0 && (
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No accounts found</h3>
            <p className="text-gray-500">Try adjusting your filters</p>
          </div>
        )}
      </Card>
    </div>
  );
}
