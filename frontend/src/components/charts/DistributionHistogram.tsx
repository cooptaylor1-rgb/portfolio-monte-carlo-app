import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface DistributionHistogramProps {
  data: Array<{
    bin: string;
    count: number;
    value: number;
  }>;
  median?: number;
  p10?: number;
  p90?: number;
  height?: number;
}

export const DistributionHistogram: React.FC<DistributionHistogramProps> = ({
  data,
  median,
  p10,
  p90,
  height = 300,
}) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(value);
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis
          dataKey="bin"
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
          label={{ value: 'Frequency', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
        />
        <Tooltip
          formatter={(value: number) => [`${value} scenarios`, 'Count']}
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#e2e8f0',
          }}
        />
        
        <Bar dataKey="count" fill="#B49759" />
        
        {p10 && (
          <ReferenceLine
            x={formatCurrency(p10)}
            stroke="#ef4444"
            strokeWidth={2}
            label={{ value: 'P10', position: 'top', fill: '#ef4444' }}
          />
        )}
        
        {median && (
          <ReferenceLine
            x={formatCurrency(median)}
            stroke="#B49759"
            strokeWidth={2}
            label={{ value: 'Median', position: 'top', fill: '#B49759' }}
          />
        )}
        
        {p90 && (
          <ReferenceLine
            x={formatCurrency(p90)}
            stroke="#10b981"
            strokeWidth={2}
            label={{ value: 'P90', position: 'top', fill: '#10b981' }}
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
};
