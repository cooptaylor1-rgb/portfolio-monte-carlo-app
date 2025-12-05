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
import { colors } from '../../theme';

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
        <CartesianGrid strokeDasharray="3 3" stroke={colors.background.border} />
        <XAxis
          dataKey="year"
          stroke={colors.text.secondary}
          style={{ fontSize: '12px' }}
          label={{ value: 'Years', position: 'insideBottom', offset: -5, fill: colors.text.secondary }}
        />
        <YAxis
          tickFormatter={formatPercent}
          stroke={colors.text.secondary}
          style={{ fontSize: '12px' }}
          label={{
            value: 'Cumulative Probability of Depletion',
            angle: -90,
            position: 'insideLeft',
            fill: colors.text.secondary,
          }}
        />
        <Tooltip
          formatter={(value: number) => formatPercent(value)}
          labelFormatter={(label: number) => `Year ${label}`}
          contentStyle={{
            backgroundColor: colors.background.elevated,
            border: `1px solid ${colors.background.border}`,
            borderRadius: '8px',
            color: colors.text.primary,
          }}
        />
        <Legend wrapperStyle={{ color: colors.text.primary }} />
        
        <Line
          type="monotone"
          dataKey="cumulativeProbability"
          stroke={colors.status.error.base}
          strokeWidth={3}
          dot={false}
          name="Depletion Probability"
        />
        
        {medianYears && (
          <ReferenceLine
            x={medianYears}
            stroke={colors.brand.gold}
            strokeWidth={2}
            strokeDasharray="5 5"
            label={{
              value: `Median: ${medianYears} years`,
              position: 'top',
              fill: colors.brand.gold,
            }}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
};
