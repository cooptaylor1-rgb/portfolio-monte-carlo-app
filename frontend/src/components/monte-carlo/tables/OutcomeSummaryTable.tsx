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
    <div style={styles.container}>
      <h3 style={styles.title}>Outcome Summary</h3>
      <p style={styles.subtitle}>
        Key metrics from {metrics.n_scenarios || 200} Monte Carlo simulations
      </p>

      <table style={styles.table}>
        <thead>
          <tr style={styles.headerRow}>
            <th style={{...styles.th, textAlign: 'left'}}>Metric</th>
            <th style={{...styles.th, textAlign: 'right'}}>Value</th>
            <th style={{...styles.th, textAlign: 'left'}}>Context</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr
              key={index}
              style={{
                ...styles.row,
                backgroundColor: row.highlight ? `${row.color}10` : index % 2 === 0 ? '#FFFFFF' : '#F9FAFB',
              }}
            >
              <td style={styles.td}>
                <strong>{row.label}</strong>
              </td>
              <td style={{
                ...styles.td,
                textAlign: 'right',
                fontSize: '16px',
                fontWeight: 600,
                color: row.color || salemColors.navy,
              }}>
                {row.value}
              </td>
              <td style={{
                ...styles.td,
                fontSize: '13px',
                color: '#6B7280',
              }}>
                {row.context}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Risk badge */}
      <div style={{
        marginTop: '16px',
        padding: '12px 16px',
        backgroundColor: `${riskLevel.color}15`,
        borderLeft: `4px solid ${riskLevel.color}`,
        borderRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div>
          <strong>Overall Plan Risk:</strong> {riskLevel.description}
        </div>
        <div style={{
          padding: '6px 12px',
          backgroundColor: riskLevel.color,
          color: '#FFFFFF',
          borderRadius: '6px',
          fontWeight: 600,
          fontSize: '14px',
        }}>
          {riskLevel.level}
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: '#FFFFFF',
    border: '1px solid #E5E7EB',
    borderRadius: '12px',
    padding: '24px',
    marginBottom: '24px',
  },
  title: {
    color: salemColors.navy,
    fontSize: '20px',
    fontWeight: 600,
    marginBottom: '4px',
    borderBottom: `3px solid ${salemColors.gold}`,
    paddingBottom: '8px',
  },
  subtitle: {
    fontSize: '14px',
    color: '#6B7280',
    marginTop: '8px',
    marginBottom: '16px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  headerRow: {
    borderBottom: `2px solid ${salemColors.navy}`,
  },
  th: {
    padding: '12px',
    fontSize: '13px',
    fontWeight: 600,
    color: salemColors.navy,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  row: {
    borderBottom: '1px solid #E5E7EB',
    transition: 'background-color 0.2s',
  },
  td: {
    padding: '14px 12px',
    fontSize: '14px',
  },
};

export default OutcomeSummaryTable;
