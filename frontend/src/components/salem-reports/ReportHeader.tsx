/**
 * Salem Report Header Component
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import type { ReportSummary } from '../../types/reports';
import { colors } from '../../theme';

interface ReportHeaderProps {
  summary: ReportSummary;
}

export const ReportHeader: React.FC<ReportHeaderProps> = ({ summary }) => {
  return (
    <header className="salem-header" style={{ borderBottomColor: colors.background.border }}>
      <div className="salem-logo" style={{ color: colors.brand.gold }}>
        Salem Investment Counselors
      </div>
      <h1 className="text-display font-display text-text-primary mt-4 mb-2">
        Retirement Analysis Report
      </h1>
      <div className="text-h3 text-text-secondary mt-2">
        {summary.scenario_name}
      </div>
      <div className="text-body text-text-tertiary mt-3">
        Prepared for <strong className="text-text-primary">{summary.client_name}</strong>
      </div>
      <div className="text-body text-text-tertiary">
        As of {new Date(summary.as_of_date).toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        })}
      </div>
      <div className="text-body text-text-tertiary mt-2">
        Prepared by {summary.advisor_name}
      </div>
    </header>
  );
};
