/**
 * Success Probability Over Time Chart
 * Shows how success probability evolves throughout the planning horizon
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

interface SuccessProbabilityChartProps {
  data: SuccessProbabilityPoint[];
}

export const SuccessProbabilityChart: React.FC<SuccessProbabilityChartProps> = ({ data }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(0)}%`;

  return (
    <div className="salem-card">
      <h3 style={{ fontSize: 'var(--salem-text-xl)', marginBottom: 'var(--salem-spacing-md)' }}>
        Success Probability Over Time
      </h3>
      <p style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)', marginBottom: 'var(--salem-spacing-md)' }}>
        Probability of meeting all spending goals throughout the planning period
      </p>

      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 10, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
            <XAxis
              dataKey="year"
              label={{ value: 'Year', position: 'insideBottom', offset: -10 }}
              stroke="#6c757d"
            />
            <YAxis
              domain={[0, 1]}
              tickFormatter={formatPercent}
              label={{ value: 'Success Probability', angle: -90, position: 'insideLeft' }}
              stroke="#6c757d"
            />
            <Tooltip
              formatter={(value: number) => formatPercent(value)}
              labelFormatter={(label) => `Year ${label}`}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #ced4da',
                borderRadius: '4px',
              }}
            />
            <ReferenceLine y={0.85} stroke="#4CAF50" strokeDasharray="3 3" label="Strong (85%)" />
            <ReferenceLine y={0.70} stroke="#FFC107" strokeDasharray="3 3" label="Adequate (70%)" />
            <Line
              type="monotone"
              dataKey="success_probability"
              stroke="#00335d"
              strokeWidth={3}
              dot={{ fill: '#00335d', r: 3 }}
              name="Success Probability"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
