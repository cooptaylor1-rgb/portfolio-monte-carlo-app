import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface DepletionChartProps {
  data: Array<{
    year: number;
    cumulativeProbability: number;
  }>;
  medianYears?: number;
  height?: number;
}

export const DepletionChart: React.FC<DepletionChartProps> = ({
  data,
  medianYears,
  height = 300,
}) => {
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis
          dataKey="year"
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
          label={{ value: 'Years', position: 'insideBottom', offset: -5, fill: '#94a3b8' }}
        />
        <YAxis
          tickFormatter={formatPercent}
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
          label={{
            value: 'Cumulative Probability of Depletion',
            angle: -90,
            position: 'insideLeft',
            fill: '#94a3b8',
          }}
        />
        <Tooltip
          formatter={(value: number) => formatPercent(value)}
          labelFormatter={(label: number) => `Year ${label}`}
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#e2e8f0',
          }}
        />
        <Legend wrapperStyle={{ color: '#e2e8f0' }} />
        
        <Line
          type="monotone"
          dataKey="cumulativeProbability"
          stroke="#ef4444"
          strokeWidth={3}
          dot={false}
          name="Depletion Probability"
        />
        
        {medianYears && (
          <ReferenceLine
            x={medianYears}
            stroke="#B49759"
            strokeWidth={2}
            strokeDasharray="5 5"
            label={{
              value: `Median: ${medianYears} years`,
              position: 'top',
              fill: '#B49759',
            }}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
};
