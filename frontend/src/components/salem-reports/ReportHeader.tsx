/**
 * Salem Report Header Component
 * Conservative branding with firm name and report metadata
 */
import React from 'react';
import type { ReportSummary } from '../../types/reports';

interface ReportHeaderProps {
  summary: ReportSummary;
}

export const ReportHeader: React.FC<ReportHeaderProps> = ({ summary }) => {
  return (
    <header className="salem-header">
      <div className="salem-logo">Salem Investment Counselors</div>
      <h1 style={{ marginTop: '1rem', marginBottom: '0.5rem' }}>
        Retirement Analysis Report
      </h1>
      <div style={{ fontSize: 'var(--salem-text-lg)', color: 'var(--salem-gray-600)' }}>
        {summary.scenario_name}
      </div>
      <div style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-500)', marginTop: '0.5rem' }}>
        Prepared for <strong>{summary.client_name}</strong>
      </div>
      <div style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-500)' }}>
        As of {new Date(summary.as_of_date).toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        })}
      </div>
      <div style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-500)', marginTop: '0.5rem' }}>
        Prepared by {summary.advisor_name}
      </div>
    </header>
  );
};
