'use client';

import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Target,
  Users,
  AlertCircle,
  Calendar,
  BarChart3,
  RefreshCw,
} from 'lucide-react';

interface DSOData {
  as_of_date: string;
  total_ar: number;
  dso: {
    current: number;
    '30_day_basis': number;
    '60_day_basis': number;
    '90_day_basis': number;
  };
  target_dso: number;
  variance_from_target: number;
  status: string;
}

interface DSOTrend {
  month: string;
  month_name: string;
  dso: number;
  ar_balance: number;
  monthly_sales: number;
  target: number;
}

interface DSOAlert {
  customer_id: number;
  customer_name: string;
  customer_dso: number;
  company_dso: number;
  variance: number;
  variance_pct: number;
  ar_balance: number;
  severity: string;
}

export default function DSOAnalysisPage() {
  const [currentDSO, setCurrentDSO] = useState<DSOData | null>(null);
  const [trend, setTrend] = useState<DSOTrend[]>([]);
  const [alerts, setAlerts] = useState<DSOAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [trendMonths, setTrendMonths] = useState(12);

  useEffect(() => {
    fetchData();
  }, [trendMonths]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [dsoRes, trendRes, alertsRes] = await Promise.all([
        fetch('/api/analytics/dso/current'),
        fetch(`/api/analytics/dso/trend?months=${trendMonths}`),
        fetch('/api/analytics/dso/alerts'),
      ]);

      const dsoData = await dsoRes.json();
      const trendData = await trendRes.json();
      const alertsData = await alertsRes.json();

      setCurrentDSO(dsoData);
      setTrend(trendData);
      setAlerts(alertsData);
    } catch (error) {
      console.error('Failed to fetch DSO data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (variance: number) => {
    if (variance <= 0) return 'text-green-600';
    if (variance <= 5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusBg = (variance: number) => {
    if (variance <= 0) return 'bg-green-50 border-green-200';
    if (variance <= 5) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const maxDSO = trend.length > 0 ? Math.max(...trend.map((t) => t.dso)) : 0;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">DSO Analysis</h1>
        <p className="text-gray-500">
          Days Sales Outstanding - Measure how quickly customers pay invoices
        </p>
      </div>

      {loading ? (
        <div className="bg-white rounded-lg border p-8 text-center text-gray-500">
          Loading DSO analysis...
        </div>
      ) : currentDSO ? (
        <>
          {/* Current DSO Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div
              className={`rounded-lg border p-4 ${getStatusBg(currentDSO.variance_from_target)}`}
            >
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                <Target className="h-4 w-4" />
                Current DSO
              </div>
              <div className={`text-3xl font-bold ${getStatusColor(currentDSO.variance_from_target)}`}>
                {currentDSO.dso.current}
              </div>
              <div className="text-xs text-gray-500">days</div>
            </div>

            <div className="bg-white rounded-lg border p-4">
              <div className="text-sm text-gray-500 mb-1">Target DSO</div>
              <div className="text-2xl font-bold text-gray-900">{currentDSO.target_dso}</div>
              <div className="text-xs text-gray-400">Industry standard</div>
            </div>

            <div className="bg-white rounded-lg border p-4">
              <div className="text-sm text-gray-500 mb-1">Variance</div>
              <div
                className={`text-2xl font-bold flex items-center gap-1 ${getStatusColor(currentDSO.variance_from_target)}`}
              >
                {currentDSO.variance_from_target > 0 ? (
                  <TrendingUp className="h-5 w-5" />
                ) : (
                  <TrendingDown className="h-5 w-5" />
                )}
                {Math.abs(currentDSO.variance_from_target)}
              </div>
              <div className="text-xs text-gray-400">days from target</div>
            </div>

            <div className="bg-white rounded-lg border p-4">
              <div className="text-sm text-gray-500 mb-1">Total AR</div>
              <div className="text-2xl font-bold text-gray-900">
                ${(currentDSO.total_ar / 1000).toFixed(0)}k
              </div>
              <div className="text-xs text-gray-400">Receivables balance</div>
            </div>

            <div className="bg-white rounded-lg border p-4">
              <div className="text-sm text-gray-500 mb-1">90-Day Basis</div>
              <div className="text-2xl font-bold text-gray-900">
                {currentDSO.dso['90_day_basis']}
              </div>
              <div className="text-xs text-gray-400">More accurate</div>
            </div>
          </div>

          {/* DSO Trend Chart */}
          <div className="bg-white rounded-lg border p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">DSO Trend</h2>
              <select
                value={trendMonths}
                onChange={(e) => setTrendMonths(parseInt(e.target.value))}
                className="px-3 py-1.5 text-sm border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="6">6 Months</option>
                <option value="12">12 Months</option>
                <option value="18">18 Months</option>
              </select>
            </div>

            <div className="h-64 flex items-end gap-2">
              {trend.map((month, idx) => (
                <div key={month.month} className="flex-1 flex flex-col items-center gap-2">
                  <div className="w-full flex flex-col-reverse h-52">
                    {/* DSO Bar */}
                    <div
                      className={`w-full rounded-t transition-all ${
                        month.dso > month.target
                          ? 'bg-red-500 hover:bg-red-600'
                          : 'bg-green-500 hover:bg-green-600'
                      }`}
                      style={{ height: `${(month.dso / maxDSO) * 100}%` }}
                      title={`DSO: ${month.dso} days`}
                    />
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-medium text-gray-900">{month.dso}</div>
                    <div className="text-xs text-gray-500 rotate-45 origin-left whitespace-nowrap">
                      {month.month_name.split(' ')[0]}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Target Line Legend */}
            <div className="flex justify-center gap-6 mt-6 pt-4 border-t">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span className="text-sm text-gray-600">On/Below Target</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span className="text-sm text-gray-600">Above Target</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-0.5 bg-gray-400 border-t-2 border-dashed"></div>
                <span className="text-sm text-gray-600">
                  Target: {currentDSO.target_dso} days
                </span>
              </div>
            </div>
          </div>

          {/* Problem Accounts */}
          {alerts.length > 0 && (
            <div className="bg-white rounded-lg border">
              <div className="p-4 border-b">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-orange-500" />
                  <h2 className="text-lg font-semibold text-gray-900">
                    Problem Accounts - High DSO
                  </h2>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Customers with DSO significantly above company average
                </p>
              </div>
              <div className="divide-y">
                {alerts.slice(0, 10).map((alert) => (
                  <div key={alert.customer_id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <a
                            href={`/customers/${alert.customer_id}`}
                            className="font-medium text-gray-900 hover:text-blue-600"
                          >
                            {alert.customer_name}
                          </a>
                          <span
                            className={`px-2 py-0.5 rounded text-xs font-medium ${
                              alert.severity === 'high'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-orange-100 text-orange-700'
                            }`}
                          >
                            {alert.severity.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                          <span>AR Balance: ${alert.ar_balance.toLocaleString()}</span>
                          <span>Customer DSO: {alert.customer_dso} days</span>
                          <span>Company Avg: {alert.company_dso} days</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-red-600">
                          +{alert.variance} days
                        </div>
                        <div className="text-xs text-gray-500">{alert.variance_pct}% above avg</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white rounded-lg border p-8 text-center text-gray-500">
          No DSO data available
        </div>
      )}
    </div>
  );
}
