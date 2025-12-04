/**
 * Outcome Summary Table
 * Comprehensive metrics table showing key simulation results
 */

import React from 'react';
import {
  salemColors,
  formatCurrency,
  formatPercent,
  getRiskLevel,
} from '../visualizations/chartUtils';

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

  const data = [
    {
      label: 'Starting Portfolio',
      value: formatCurrency(startingPortfolio),
      context: 'Initial investment value',
    },
    {
      label: 'Planning Horizon',
      value: `${years} years`,
      context: 'Time period analyzed',
    },
    {
      label: 'Success Probability',
      value: formatPercent(metrics.success_probability || 0, 1),
      context: riskLevel.description,
      highlight: true,
      color: riskLevel.color,
    },
    {
      label: 'Median Ending Balance',
      value: formatCurrency(metrics.ending_median || 0),
      context: '50th percentile outcome',
    },
    {
      label: 'Best Case (90th Percentile)',
      value: formatCurrency(endingStats.P90 || 0),
      context: 'Optimistic scenario',
      color: salemColors.success,
    },
    {
      label: 'Worst Case (10th Percentile)',
      value: formatCurrency(endingStats.P10 || 0),
      context: 'Conservative scenario',
      color: endingStats.P10 < 0 ? salemColors.danger : salemColors.success,
    },
    {
      label: 'Depletion Risk',
      value: formatPercent(metrics.depletion_probability || 0, 1),
      context: 'Probability of running out',
      color: (metrics.depletion_probability || 0) > 0.2 ? salemColors.danger : salemColors.success,
    },
    {
      label: 'Shortfall Risk',
      value: formatPercent(metrics.shortfall_risk || 0, 1),
      context: 'Risk of insufficient funds',
    },
  ];

  return (
    <div className="bg-white border border-background-border rounded-xl p-6 mb-6">
      <h3 
        className="text-xl font-semibold mb-1 pb-2 border-b-[3px]"
        style={{ color: salemColors.navy, borderBottomColor: salemColors.gold }}
      >
        Outcome Summary
      </h3>
      <p className="text-sm text-text-secondary mt-2 mb-4">
        Key metrics from {metrics.n_scenarios || 200} Monte Carlo simulations
      </p>

      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b-2" style={{ borderBottomColor: salemColors.navy }}>
            <th className="p-3 text-[13px] font-semibold uppercase tracking-wide text-left" style={{ color: salemColors.navy }}>
              Metric
            </th>
            <th className="p-3 text-[13px] font-semibold uppercase tracking-wide text-right" style={{ color: salemColors.navy }}>
              Value
            </th>
            <th className="p-3 text-[13px] font-semibold uppercase tracking-wide text-left" style={{ color: salemColors.navy }}>
              Context
            </th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr
              key={index}
              className="border-b border-background-border transition-colors"
              style={{
                backgroundColor: row.highlight ? `${row.color}10` : index % 2 === 0 ? '#FFFFFF' : '#F9FAFB',
              }}
            >
              <td className="p-3.5 text-sm">
                <strong>{row.label}</strong>
              </td>
              <td
                className="p-3.5 text-base font-semibold text-right"
                style={{ color: row.color || salemColors.navy }}
              >
                {row.value}
              </td>
              <td className="p-3.5 text-[13px] text-text-secondary">
                {row.context}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Risk badge */}
      <div
        className="mt-4 px-4 py-3 rounded-lg flex justify-between items-center border-l-4"
        style={{
          backgroundColor: `${riskLevel.color}15`,
          borderLeftColor: riskLevel.color,
        }}
      >
        <div>
          <strong>Overall Plan Risk:</strong> {riskLevel.description}
        </div>
        <div
          className="px-3 py-1.5 text-white rounded-md font-semibold text-sm"
          style={{ backgroundColor: riskLevel.color }}
        >
          {riskLevel.level}
        </div>
      </div>
    </div>
  );
};

export default OutcomeSummaryTable;
