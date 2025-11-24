'use client';

import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  DollarSign,
  Calendar,
  User,
  Phone,
  ChevronRight,
  Filter,
  RefreshCw,
} from 'lucide-react';

interface Promise {
  id: number;
  customer_id: number;
  customer_name: string;
  customer_phone?: string;
  promise_amount: number;
  promise_date: string;
  status: 'pending' | 'kept' | 'broken';
  content: string;
  created_at: string;
  days_until_due: number;
  is_overdue: boolean;
}

interface PromiseStats {
  total_pending: number;
  total_amount_pending: number;
  due_today: number;
  overdue: number;
  kept_this_month: number;
  broken_this_month: number;
  kept_rate: number;
}

export default function PromisesPage() {
  const [promises, setPromises] = useState<Promise[]>([]);
  const [stats, setStats] = useState<PromiseStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'pending' | 'overdue' | 'due_today'>('pending');
  const [selectedPromise, setSelectedPromise] = useState<Promise | null>(null);

  useEffect(() => {
    fetchPromises();
    fetchStats();
  }, [filter]);

  const fetchPromises = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filter === 'pending') params.append('status', 'pending');
      if (filter === 'overdue') params.append('overdue', 'true');
      if (filter === 'due_today') params.append('due_today', 'true');

      const response = await fetch(`/api/promises?${params}`);
      const data = await response.json();
      setPromises(data);
    } catch (error) {
      console.error('Failed to fetch promises:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/promises/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const updatePromiseStatus = async (promiseId: number, status: 'kept' | 'broken') => {
    try {
      await fetch(`/api/notes/${promiseId}/promise-status?status=${status}`, {
        method: 'PUT',
      });
      fetchPromises();
      fetchStats();
    } catch (error) {
      console.error('Failed to update promise:', error);
    }
  };

  const getStatusBadge = (promise: Promise) => {
    if (promise.status === 'kept') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle2 className="h-3 w-3" />
          Kept
        </span>
      );
    }
    if (promise.status === 'broken') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <XCircle className="h-3 w-3" />
          Broken
        </span>
      );
    }
    if (promise.is_overdue) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 animate-pulse">
          <AlertTriangle className="h-3 w-3" />
          Overdue
        </span>
      );
    }
    if (promise.days_until_due <= 3) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          <Clock className="h-3 w-3" />
          Due Soon
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
        <Clock className="h-3 w-3" />
        Pending
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Promise-to-Pay Tracking</h1>
        <p className="text-gray-500">Monitor customer payment commitments and follow up on broken promises</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-gray-500">Pending Promises</div>
            <div className="text-2xl font-bold text-blue-600">{stats.total_pending}</div>
            <div className="text-xs text-gray-400">${stats.total_amount_pending.toLocaleString()}</div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-gray-500">Due Today</div>
            <div className="text-2xl font-bold text-yellow-600">{stats.due_today}</div>
          </div>

          <div className={`rounded-lg border p-4 ${stats.overdue > 0 ? 'bg-red-50 border-red-200 alert-critical-pulse' : 'bg-white'}`}>
            <div className="text-sm text-gray-500">Overdue</div>
            <div className={`text-2xl font-bold ${stats.overdue > 0 ? 'text-red-600' : 'text-gray-400'}`}>
              {stats.overdue}
            </div>
            {stats.overdue > 0 && <div className="text-xs text-red-500">Requires Action</div>}
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-gray-500">Kept (This Month)</div>
            <div className="text-2xl font-bold text-green-600">{stats.kept_this_month}</div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-gray-500">Broken (This Month)</div>
            <div className="text-2xl font-bold text-red-600">{stats.broken_this_month}</div>
          </div>

          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-gray-500">Kept Rate</div>
            <div className={`text-2xl font-bold ${stats.kept_rate >= 75 ? 'text-green-600' : 'text-orange-600'}`}>
              {stats.kept_rate}%
            </div>
            <div className="text-xs text-gray-400">Target: 75%+</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg border p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex gap-2">
              {[
                { value: 'pending', label: 'Pending' },
                { value: 'overdue', label: 'Overdue' },
                { value: 'due_today', label: 'Due Today' },
                { value: 'all', label: 'All' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setFilter(option.value as typeof filter)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    filter === option.value
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
          <button
            onClick={() => { fetchPromises(); fetchStats(); }}
            className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Promises List */}
      <div className="bg-white rounded-lg border">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading promises...</div>
        ) : promises.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No promises found for the selected filter.
          </div>
        ) : (
          <div className="divide-y">
            {promises.map((promise) => (
              <div
                key={promise.id}
                className={`p-4 hover:bg-gray-50 transition-colors ${
                  promise.is_overdue && promise.status === 'pending' ? 'bg-red-50' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {/* Status Icon */}
                    <div className={`p-2 rounded-full ${
                      promise.status === 'kept' ? 'bg-green-100' :
                      promise.status === 'broken' ? 'bg-red-100' :
                      promise.is_overdue ? 'bg-red-100' :
                      'bg-blue-100'
                    }`}>
                      {promise.status === 'kept' ? (
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                      ) : promise.status === 'broken' ? (
                        <XCircle className="h-5 w-5 text-red-600" />
                      ) : promise.is_overdue ? (
                        <AlertTriangle className="h-5 w-5 text-red-600" />
                      ) : (
                        <Clock className="h-5 w-5 text-blue-600" />
                      )}
                    </div>

                    {/* Customer Info */}
                    <div>
                      <div className="flex items-center gap-2">
                        <a
                          href={`/customers/${promise.customer_id}`}
                          className="font-medium text-gray-900 hover:text-blue-600"
                        >
                          {promise.customer_name}
                        </a>
                        {getStatusBadge(promise)}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                        <span className="flex items-center gap-1">
                          <DollarSign className="h-3 w-3" />
                          ${promise.promise_amount.toLocaleString()}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(promise.promise_date).toLocaleDateString()}
                          {promise.days_until_due > 0 && promise.status === 'pending' && (
                            <span className="text-gray-400">
                              ({promise.days_until_due} days)
                            </span>
                          )}
                          {promise.is_overdue && promise.status === 'pending' && (
                            <span className="text-red-500 font-medium">
                              ({Math.abs(promise.days_until_due)} days overdue)
                            </span>
                          )}
                        </span>
                        {promise.customer_phone && (
                          <span className="flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            {promise.customer_phone}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-1">
                        {promise.content}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {promise.status === 'pending' && (
                      <>
                        <button
                          onClick={() => updatePromiseStatus(promise.id, 'kept')}
                          className="px-3 py-1.5 text-sm font-medium text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition-colors"
                        >
                          Mark Kept
                        </button>
                        <button
                          onClick={() => updatePromiseStatus(promise.id, 'broken')}
                          className="px-3 py-1.5 text-sm font-medium text-red-700 bg-red-100 rounded-lg hover:bg-red-200 transition-colors"
                        >
                          Mark Broken
                        </button>
                      </>
                    )}
                    <a
                      href={`/customers/${promise.customer_id}`}
                      className="p-2 text-gray-400 hover:text-gray-600"
                    >
                      <ChevronRight className="h-5 w-5" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
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
