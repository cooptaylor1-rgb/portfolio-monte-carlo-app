/**
 * Terminal Wealth Distribution Histogram
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { TerminalWealthBucket } from '../../types/reports';
import { colors } from '../../theme';

interface TerminalWealthHistogramProps {
  data: TerminalWealthBucket[];
}

export const TerminalWealthHistogram: React.FC<TerminalWealthHistogramProps> = ({ data }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

  // Color gradient based on bucket position using design system colors
  const getColor = (index: number, total: number) => {
    const ratio = index / (total - 1);
    if (ratio < 0.33) return colors.status.error.base; // red for lower outcomes
    if (ratio < 0.66) return colors.status.warning.base; // amber for middle
    return colors.status.success.base; // green for higher outcomes
  };

  return (
    <div 
      className="salem-card"
      style={{ 
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border 
      }}
    >
      <h3 className="text-h3 font-display text-text-primary mb-3">
        Terminal Wealth Distribution
      </h3>
      <p className="text-body text-text-secondary mb-4">
        Distribution of portfolio values at the end of the planning horizon across all {data.reduce((sum, b) => sum + b.count, 0).toLocaleString()} simulations
      </p>

      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={colors.background.border} />
            <XAxis
              dataKey="bucket_label"
              angle={-45}
              textAnchor="end"
              height={80}
              stroke={colors.text.tertiary}
            />
            <YAxis
              label={{ value: 'Number of Scenarios', angle: -90, position: 'insideLeft' }}
              stroke={colors.text.tertiary}
            />
            <Tooltip
              formatter={(value: number, _name: string, props: any) => {
                return [
                  `${value.toLocaleString()} scenarios (${formatPercent(props.payload.percentage)})`,
                  'Count'
                ];
              }}
              contentStyle={{
                backgroundColor: colors.background.elevated,
                border: `1px solid ${colors.background.border}`,
                borderRadius: '8px',
              }}
            />
            <Bar dataKey="count" name="Scenarios">
              {data.map((_entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(index, data.length)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="text-body text-text-secondary mt-4">
        <p>
          <strong className="text-text-primary">Key Insight:</strong> This histogram shows the range of possible outcomes. 
          A wider distribution indicates greater uncertainty, while a narrow distribution suggests more predictable results.
        </p>
      </div>
    </div>
  );
};
