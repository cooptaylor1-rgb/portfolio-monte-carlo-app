/**
 * Success Probability Over Time Chart
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { SuccessProbabilityPoint } from '../../types/reports';
import { colors } from '../../theme';

interface SuccessProbabilityChartProps {
  data: SuccessProbabilityPoint[];
}

export const SuccessProbabilityChart: React.FC<SuccessProbabilityChartProps> = ({ data }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(0)}%`;

  return (
    <div 
      className="salem-card"
      style={{ 
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border 
      }}
    >
      <h3 className="text-h3 font-display text-text-primary mb-3">
        Success Probability Over Time
      </h3>
      <p className="text-body text-text-secondary mb-4">
        Probability of meeting all spending goals throughout the planning period
      </p>

      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 10, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={colors.background.border} />
            <XAxis
              dataKey="year"
              label={{ value: 'Year', position: 'insideBottom', offset: -10 }}
              stroke={colors.text.tertiary}
            />
            <YAxis
              domain={[0, 1]}
              tickFormatter={formatPercent}
              label={{ value: 'Success Probability', angle: -90, position: 'insideLeft' }}
              stroke={colors.text.tertiary}
            />
            <Tooltip
              formatter={(value: number) => formatPercent(value)}
              labelFormatter={(label) => `Year ${label}`}
              contentStyle={{
                backgroundColor: colors.background.elevated,
                border: `1px solid ${colors.background.border}`,
                borderRadius: '8px',
              }}
            />
            <ReferenceLine y={0.85} stroke={colors.status.success.base} strokeDasharray="3 3" label="Strong (85%)" />
            <ReferenceLine y={0.70} stroke={colors.status.warning.base} strokeDasharray="3 3" label="Adequate (70%)" />
            <Line
              type="monotone"
              dataKey="success_probability"
              stroke={colors.brand.navy}
              strokeWidth={3}
              dot={{ fill: colors.brand.navy, r: 3 }}
              name="Success Probability"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
