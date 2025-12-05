/**
 * Summary Section Component
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import type { ReportSummary } from '../../types/reports';
import { colors } from '../../theme';

interface SummarySectionProps {
  summary: ReportSummary;
}

const getVariantStyles = (variant?: string) => {
  switch (variant) {
    case 'success':
      return {
        backgroundColor: `${colors.status.success.base}10`,
        borderColor: colors.status.success.base,
      };
    case 'warning':
      return {
        backgroundColor: `${colors.status.warning.base}10`,
        borderColor: colors.status.warning.base,
      };
    case 'error':
      return {
        backgroundColor: `${colors.status.error.base}10`,
        borderColor: colors.status.error.base,
      };
    default:
      return {
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border,
      };
  }
};

export const SummarySection: React.FC<SummarySectionProps> = ({ summary }) => {
  return (
    <section className="salem-section">
      <h2 className="text-h2 font-display text-text-primary mb-6">Executive Summary</h2>
      <div className="salem-metrics-grid">
        {summary.key_metrics.map((metric, index) => {
          const variantStyles = getVariantStyles(metric.variant);
          return (
            <div 
              key={index} 
              className="salem-metric"
              style={variantStyles}
              title={metric.tooltip}
            >
              <div className="salem-metric-label text-small text-text-tertiary">{metric.label}</div>
              <div className="salem-metric-value text-h2 font-display text-text-primary">{metric.value}</div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
