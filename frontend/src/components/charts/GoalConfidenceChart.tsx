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

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getColor = (probability: number) => {
    if (probability >= 0.85) return '#10b981'; // green
    if (probability >= 0.70) return '#fbbf24'; // yellow
    return '#ef4444'; // red
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={goals}
        margin={{ top: 5, right: 30, left: 20, bottom: 80 }}
        layout="horizontal"
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis
          dataKey="name"
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
          angle={-45}
          textAnchor="end"
          height={100}
        />
        <YAxis
          tickFormatter={formatPercent}
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
          domain={[0, 1]}
          label={{
            value: 'Confidence Level',
            angle: -90,
            position: 'insideLeft',
            fill: '#94a3b8',
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
              ? `${label} (${formatCurrency(goal.targetAmount)} by age ${goal.targetAge})`
              : label;
          }}
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#e2e8f0',
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
