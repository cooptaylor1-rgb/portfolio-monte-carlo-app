/**
 * Outcome Summary Table
 * Comprehensive metrics table showing key simulation results
 * Refactored to match app-wide design system
 */

import React, { useMemo } from 'react';
import {
  salemColors,
  formatCurrency,
  formatPercent,
  getRiskLevel,
} from '../visualizations/chartUtils';
import {
  AnalysisSection,
  AssessmentCallout,
  SummaryCard,
  RiskBadge,
} from '../shared/AnalysisComponents';

interface OutcomeSummaryTableProps {
  metrics: any;
  stats: any[];
  startingPortfolio: number;
  years: number;
}

export const OutcomeSummaryTable: React.FC<OutcomeSummaryTableProps> = ({
  metrics,
  stats,
  startingPortfolio,
  years,
}) => {
  const endingStats = stats[stats.length - 1] || {};
  const riskLevel = getRiskLevel(metrics.success_probability || 0);

  // Prepare table data with proper categorization
  const data = useMemo(() => [
    {
      label: 'Starting Portfolio',
      value: formatCurrency(startingPortfolio),
      context: 'Initial investment value',
      category: 'input',
    },
    {
      label: 'Planning Horizon',
      value: `${years} years`,
      context: 'Time period analyzed',
      category: 'input',
    },
    {
      label: 'Success Probability',
      value: formatPercent(metrics.success_probability || 0, 1),
      context: riskLevel.description,
      highlight: true,
      color: riskLevel.color,
      category: 'key',
    },
    {
      label: 'Median Ending Balance',
      value: formatCurrency(metrics.ending_median || 0),
      context: '50th percentile outcome',
      category: 'projection',
    },
    {
      label: 'Best Case (90th Percentile)',
      value: formatCurrency(endingStats.P90 || 0),
      context: 'Optimistic scenario',
      color: salemColors.success,
      category: 'projection',
    },
    {
      label: 'Worst Case (10th Percentile)',
      value: formatCurrency(endingStats.P10 || 0),
      context: 'Conservative scenario',
      color: endingStats.P10 < 0 ? salemColors.danger : salemColors.success,
      category: 'projection',
    },
    {
      label: 'Depletion Risk',
      value: formatPercent(metrics.depletion_probability || 0, 1),
      context: 'Probability of running out',
      color: (metrics.depletion_probability || 0) > 0.2 ? salemColors.danger : salemColors.success,
      category: 'risk',
    },
    {
      label: 'Shortfall Risk',
      value: formatPercent(metrics.shortfall_risk || 0, 1),
      context: 'Risk of insufficient funds',
      color: (metrics.shortfall_risk || 0) > 0.2 ? salemColors.warning : salemColors.success,
      category: 'risk',
    },
  ], [metrics, endingStats, startingPortfolio, years, riskLevel]);

  // Determine overall risk variant for callout
  const riskVariant = useMemo(() => {
    const successProb = metrics.success_probability || 0;
    if (successProb >= 0.85) return 'success';
    if (successProb >= 0.70) return 'warning';
    return 'danger';
  }, [metrics.success_probability]);

  return (
    <AnalysisSection
      title="Outcome Summary"
      subtitle={`Key metrics from ${metrics.n_scenarios || 200} Monte Carlo simulations`}
    >
      {/* Summary cards at top */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <SummaryCard
          label="Success Rate"
          value={formatPercent(metrics.success_probability || 0, 1)}
          sublabel={riskLevel.description}
          variant={riskVariant}
        />
        <SummaryCard
          label="Median Final Value"
          value={formatCurrency(metrics.ending_median || 0)}
          sublabel="50th percentile outcome"
          variant="default"
        />
        <SummaryCard
          label="Depletion Risk"
          value={formatPercent(metrics.depletion_probability || 0, 1)}
          sublabel="Probability of running out"
          variant={(metrics.depletion_probability || 0) > 0.2 ? 'danger' : 'success'}
        />
      </div>

      {/* Main data table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr 
              className="border-b-2"
              style={{ borderBottomColor: salemColors.gold }}
            >
              <th 
                className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                style={{ color: salemColors.gold }}
              >
                Metric
              </th>
              <th 
                className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider"
                style={{ color: salemColors.gold }}
              >
                Value
              </th>
              <th 
                className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                style={{ color: salemColors.gold }}
              >
                Context
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr
                key={index}
                className="border-b transition-colors hover:bg-opacity-70"
                style={{
                  backgroundColor: row.highlight 
                    ? `${row.color}10` 
                    : index % 2 === 0 
                      ? 'rgba(30, 41, 59, 0.3)' 
                      : 'rgba(30, 41, 59, 0.15)',
                  borderBottomColor: 'rgba(71, 85, 105, 0.2)',
                }}
              >
                <td 
                  className="px-4 py-3.5 text-sm font-medium"
                  style={{ color: salemColors.white }}
                >
                  {row.label}
                </td>
                <td
                  className="px-4 py-3.5 text-base font-semibold text-right tabular-nums"
                  style={{ color: row.color || salemColors.white }}
                >
                  {row.value}
                </td>
                <td 
                  className="px-4 py-3.5 text-sm"
                  style={{ color: salemColors.mediumGray }}
                >
                  {row.context}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Overall Plan Risk Assessment */}
      <div className="mt-6">
        <AssessmentCallout
          title="Overall Plan Risk Assessment"
          message={`Your retirement plan shows a ${formatPercent(metrics.success_probability || 0, 1)} probability of success with ${riskLevel.level.toLowerCase()} risk. ${riskLevel.description}`}
          variant={riskVariant}
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>
    </AnalysisSection>
  );
};

export default OutcomeSummaryTable;
