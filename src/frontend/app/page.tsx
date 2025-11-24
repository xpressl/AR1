'use client';

import React from 'react';
import Link from 'next/link';

/**
 * Home page - Landing/redirect to dashboard
 * In production, this would redirect to /dashboard or /login based on auth state
 */
export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-4xl mx-auto text-center">
        {/* Logo/Brand */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-neutral-900 mb-2">
            AR Control Hub
          </h1>
          <p className="text-lg text-neutral-600">
            Accounts Receivable Management System
          </p>
        </div>

        {/* Feature highlights */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <FeatureCard
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
            title="Dashboard Analytics"
            description="Real-time visibility into AR metrics, aging analysis, and collection performance."
          />
          <FeatureCard
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            }
            title="Smart Alerts"
            description="Automated alerts for overdue payments, credit limit breaches, and broken promises."
          />
          <FeatureCard
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            }
            title="Collector Worklist"
            description="Prioritized work queues with customer history and one-click actions."
          />
        </div>

        {/* CTA Button */}
        <div className="space-y-4">
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center px-8 py-3 text-base font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors shadow-sm"
          >
            Go to Dashboard
            <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
          <p className="text-sm text-neutral-500">
            Demo mode - No login required
          </p>
        </div>

        {/* Alert severity demo */}
        <div className="mt-16 p-6 bg-white rounded-xl shadow-card border border-neutral-200">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4">
            Alert Severity Indicators
          </h2>
          <div className="flex flex-wrap justify-center gap-4">
            <AlertDemo severity="critical" label="Critical" pulse />
            <AlertDemo severity="high" label="High" />
            <AlertDemo severity="medium" label="Medium" />
            <AlertDemo severity="low" label="Low" />
          </div>
        </div>
      </div>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="p-6 bg-white rounded-xl shadow-card border border-neutral-200 text-left hover:shadow-card-hover transition-shadow">
      <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center text-primary-600 mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-neutral-900 mb-2">{title}</h3>
      <p className="text-neutral-600 text-sm">{description}</p>
    </div>
  );
}

function AlertDemo({
  severity,
  label,
  pulse = false,
}: {
  severity: 'critical' | 'high' | 'medium' | 'low';
  label: string;
  pulse?: boolean;
}) {
  const colors = {
    critical: {
      bg: 'bg-alert-critical-bg',
      border: 'border-alert-critical',
      text: 'text-alert-critical',
    },
    high: {
      bg: 'bg-alert-high-bg',
      border: 'border-alert-high',
      text: 'text-alert-high',
    },
    medium: {
      bg: 'bg-alert-medium-bg',
      border: 'border-alert-medium',
      text: 'text-alert-medium',
    },
    low: {
      bg: 'bg-alert-low-bg',
      border: 'border-alert-low',
      text: 'text-alert-low',
    },
  };

  return (
    <div
      className={`
        px-4 py-2 rounded-lg border-2 flex items-center gap-2
        ${colors[severity].bg}
        ${colors[severity].border}
        ${pulse ? 'alert-critical-pulse' : ''}
      `}
    >
      <span className={`${pulse ? 'alert-icon-pulse' : ''}`}>
        <svg
          className={`w-5 h-5 ${colors[severity].text}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </span>
      <span className={`font-medium ${colors[severity].text}`}>{label}</span>
    </div>
  );
}
