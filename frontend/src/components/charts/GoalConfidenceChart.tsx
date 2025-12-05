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
import { colors } from '../../theme';
import { formatChartCurrency } from '../../theme/chartUtils';

interface GoalConfidenceChartProps {
  goals: Array<{
    name: string;
    probability: number;
    targetAmount: number;
    targetAge: number;
  }>;
  height?: number;
}

export const GoalConfidenceChart: React.FC<GoalConfidenceChartProps> = ({
  goals,
  height = 300,
}) => {
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getColor = (probability: number) => {
    if (probability >= 0.85) return colors.status.success.base;
    if (probability >= 0.70) return colors.status.warning.base;
    return colors.status.error.base;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={goals}
        margin={{ top: 5, right: 30, left: 20, bottom: 80 }}
        layout="horizontal"
      >
        <CartesianGrid strokeDasharray="3 3" stroke={colors.background.border} />
        <XAxis
          dataKey="name"
          stroke={colors.text.secondary}
          style={{ fontSize: '12px' }}
          angle={-45}
          textAnchor="end"
          height={100}
        />
        <YAxis
          tickFormatter={formatPercent}
          stroke={colors.text.secondary}
          style={{ fontSize: '12px' }}
          domain={[0, 1]}
          label={{
            value: 'Confidence Level',
            angle: -90,
            position: 'insideLeft',
            fill: colors.text.secondary,
          }}
        />
        <Tooltip
          formatter={(value: number) => [
            formatPercent(value),
            'Confidence',
          ]}
          labelFormatter={(label: string) => {
            const goal = goals.find((g) => g.name === label);
            return goal
              ? `${label} (${formatChartCurrency(goal.targetAmount)} by age ${goal.targetAge})`
              : label;
          }}
          contentStyle={{
            backgroundColor: colors.background.elevated,
            border: `1px solid ${colors.background.border}`,
            borderRadius: '8px',
            color: colors.text.primary,
          }}
        />
        
        <Bar dataKey="probability" radius={[8, 8, 0, 0]}>
          {goals.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getColor(entry.probability)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};
