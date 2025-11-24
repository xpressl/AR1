'use client';

import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  DollarSign,
  Calendar,
  Target,
  BarChart3,
  RefreshCw,
  Download,
  ChevronDown,
} from 'lucide-react';

interface WeekData {
  week: number;
  week_start: string;
  week_end: string;
  invoice_based: number;
  promise_based: number;
  total: number;
  cumulative: number;
}

interface ForecastData {
  generated_at: string;
  forecast_period: {
    start: string;
    end: string;
    weeks: number;
  };
  summary: {
    total_forecasted: number;
    from_invoices: number;
    from_promises: number;
    forecast_accuracy: {
      period: string;
      forecasted: number;
      actual: number;
      accuracy_percentage: number;
      variance: number;
    };
  };
  weekly_breakdown: WeekData[];
}

export default function CashForecastPage() {
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);
  const [weeks, setWeeks] = useState(8);
  const [includePromises, setIncludePromises] = useState(true);

  useEffect(() => {
    fetchForecast();
  }, [weeks, includePromises]);

  const fetchForecast = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        weeks: weeks.toString(),
        include_promises: includePromises.toString(),
      });
      const response = await fetch(`/api/analytics/forecast/cash?${params}`);
      const data = await response.json();
      setForecast(data);
    } catch (error) {
      console.error('Failed to fetch forecast:', error);
    } finally {
      setLoading(false);
    }
  };

  const getBarHeight = (amount: number, maxAmount: number) => {
    return `${(amount / maxAmount * 100)}%`;
  };

  const maxWeeklyAmount = forecast
    ? Math.max(...forecast.weekly_breakdown.map((w) => w.total))
    : 0;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Cash Flow Forecast</h1>
        <p className="text-gray-500">
          Predict future cash receipts based on invoice due dates and payment promises
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg border p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Forecast Period
              </label>
              <select
                value={weeks}
                onChange={(e) => setWeeks(parseInt(e.target.value))}
                className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="4">4 Weeks</option>
                <option value="8">8 Weeks</option>
                <option value="12">12 Weeks</option>
                <option value="16">16 Weeks</option>
              </select>
            </div>

            <div className="flex items-center gap-2 pt-6">
              <input
                type="checkbox"
                id="promises"
                checked={includePromises}
                onChange={(e) => setIncludePromises(e.target.checked)}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded"
              />
              <label htmlFor="promises" className="text-sm text-gray-700">
                Include Promises-to-Pay
              </label>
            </div>
          </div>

          <button
            onClick={fetchForecast}
            className="flex items-center gap-2 px-4 py-2 text-sm text-blue-600 hover:text-blue-700"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="bg-white rounded-lg border p-8 text-center text-gray-500">
          Loading forecast...
        </div>
      ) : forecast ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg border p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                <DollarSign className="h-4 w-4" />
                Total Forecasted
              </div>
              <div className="text-2xl font-bold text-gray-900">
                ${forecast.summary.total_forecasted.toLocaleString()}
              </div>
            </div>

            <div className="bg-white rounded-lg border p-4">
              <div className="text-sm text-gray-500 mb-1">From Invoices</div>
              <div className="text-2xl font-bold text-blue-600">
                ${forecast.summary.from_invoices.toLocaleString()}
              </div>
              <div className="text-xs text-gray-400">
                {((forecast.summary.from_invoices / forecast.summary.total_forecasted) * 100).toFixed(0)}
                % of total
              </div>
            </div>

            <div className="bg-white rounded-lg border p-4">
              <div className="text-sm text-gray-500 mb-1">From Promises</div>
              <div className="text-2xl font-bold text-green-600">
                ${forecast.summary.from_promises.toLocaleString()}
              </div>
              <div className="text-xs text-gray-400">
                {((forecast.summary.from_promises / forecast.summary.total_forecasted) * 100).toFixed(0)}
                % of total
              </div>
            </div>

            <div className="bg-white rounded-lg border p-4">
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                <Target className="h-4 w-4" />
                Forecast Accuracy
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {forecast.summary.forecast_accuracy.accuracy_percentage}%
              </div>
              <div className="text-xs text-gray-400">
                {forecast.summary.forecast_accuracy.period}
              </div>
            </div>
          </div>

          {/* Weekly Chart */}
          <div className="bg-white rounded-lg border p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Weekly Cash Flow Projection
            </h2>

            <div className="h-80 flex items-end gap-3">
              {forecast.weekly_breakdown.map((week) => (
                <div key={week.week} className="flex-1 flex flex-col items-center gap-2">
                  {/* Bars */}
                  <div className="w-full flex flex-col-reverse gap-1 h-64">
                    {/* Promise bar */}
                    {week.promise_based > 0 && (
                      <div
                        className="w-full bg-green-500 rounded-t transition-all hover:bg-green-600"
                        style={{ height: getBarHeight(week.promise_based, maxWeeklyAmount) }}
                        title={`Promises: $${week.promise_based.toLocaleString()}`}
                      />
                    )}
                    {/* Invoice bar */}
                    {week.invoice_based > 0 && (
                      <div
                        className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                        style={{ height: getBarHeight(week.invoice_based, maxWeeklyAmount) }}
                        title={`Invoices: $${week.invoice_based.toLocaleString()}`}
                      />
                    )}
                  </div>

                  {/* Labels */}
                  <div className="text-center">
                    <div className="text-sm font-medium text-gray-900">
                      ${(week.total / 1000).toFixed(0)}k
                    </div>
                    <div className="text-xs text-gray-500">Week {week.week}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Legend */}
            <div className="flex justify-center gap-6 mt-6">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-500 rounded"></div>
                <span className="text-sm text-gray-600">Invoice Due Dates</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span className="text-sm text-gray-600">Promises to Pay</span>
              </div>
            </div>
          </div>

          {/* Weekly Breakdown Table */}
          <div className="bg-white rounded-lg border">
            <div className="p-4 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Weekly Breakdown</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Week
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Period
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      From Invoices
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      From Promises
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Total
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Cumulative
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {forecast.weekly_breakdown.map((week) => (
                    <tr key={week.week} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">Week {week.week}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {new Date(week.week_start).toLocaleDateString()} -{' '}
                        {new Date(week.week_end).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-right text-sm text-gray-900">
                        ${week.invoice_based.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right text-sm text-gray-900">
                        ${week.promise_based.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right font-medium text-gray-900">
                        ${week.total.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right text-sm text-gray-500">
                        ${week.cumulative.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-lg border p-8 text-center text-gray-500">
          No forecast data available
        </div>
      )}
    </div>
  );
}
