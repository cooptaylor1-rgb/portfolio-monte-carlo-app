/**
 * Summary Section Component
 * Display key metrics in a grid layout
 */
import React from 'react';
import type { ReportSummary } from '../../types/reports';

interface SummarySectionProps {
  summary: ReportSummary;
}

export const SummarySection: React.FC<SummarySectionProps> = ({ summary }) => {
  return (
    <section className="salem-section">
      <h2>Executive Summary</h2>
      <div className="salem-metrics-grid">
        {summary.key_metrics.map((metric, index) => (
          <div 
            key={index} 
            className={`salem-metric ${metric.variant || 'neutral'}`}
            title={metric.tooltip}
          >
            <div className="salem-metric-label">{metric.label}</div>
            <div className="salem-metric-value">{metric.value}</div>
          </div>
        ))}
      </div>
    </section>
  );
};
