/**
 * Terminal Wealth Distribution Histogram
 * Shows distribution of ending portfolio values across all simulations
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

interface TerminalWealthHistogramProps {
  data: TerminalWealthBucket[];
}

export const TerminalWealthHistogram: React.FC<TerminalWealthHistogramProps> = ({ data }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

  // Color gradient based on bucket position
  const getColor = (index: number, total: number) => {
    const ratio = index / (total - 1);
    if (ratio < 0.33) return '#dc2626'; // red for lower outcomes
    if (ratio < 0.66) return '#d97706'; // amber for middle
    return '#4b8f29'; // green for higher outcomes
  };

  return (
    <div className="salem-card">
      <h3 style={{ fontSize: 'var(--salem-text-xl)', marginBottom: 'var(--salem-spacing-md)' }}>
        Terminal Wealth Distribution
      </h3>
      <p style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)', marginBottom: 'var(--salem-spacing-md)' }}>
        Distribution of portfolio values at the end of the planning horizon across all {data.reduce((sum, b) => sum + b.count, 0).toLocaleString()} simulations
      </p>

      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
            <XAxis
              dataKey="bucket_label"
              angle={-45}
              textAnchor="end"
              height={80}
              stroke="#6c757d"
            />
            <YAxis
              label={{ value: 'Number of Scenarios', angle: -90, position: 'insideLeft' }}
              stroke="#6c757d"
            />
            <Tooltip
              formatter={(value: number, name: string, props: any) => {
                return [
                  `${value.toLocaleString()} scenarios (${formatPercent(props.payload.percentage)})`,
                  'Count'
                ];
              }}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #ced4da',
                borderRadius: '4px',
              }}
            />
            <Bar dataKey="count" name="Scenarios">
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(index, data.length)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginTop: 'var(--salem-spacing-md)', fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)' }}>
        <p>
          <strong>Key Insight:</strong> This histogram shows the range of possible outcomes. 
          A wider distribution indicates greater uncertainty, while a narrow distribution suggests more predictable results.
        </p>
      </div>
    </div>
  );
};
