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
  ReferenceLine,
} from 'recharts';

interface WaterfallChartProps {
  data: Array<{
    name: string;
    value: number;
    isTotal?: boolean;
  }>;
  height?: number;
}

export const WaterfallChart: React.FC<WaterfallChartProps> = ({
  data,
  height = 400,
}) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(Math.abs(value));
  };

  // Calculate cumulative values for waterfall effect
  const waterfallData = data.map((item, index) => {
    const previousSum = data
      .slice(0, index)
      .reduce((sum, d) => sum + d.value, 0);
    
    return {
      ...item,
      start: item.value >= 0 ? previousSum : previousSum + item.value,
      end: previousSum + item.value,
      displayValue: item.value,
    };
  });

  const getColor = (value: number, isTotal?: boolean) => {
    if (isTotal) return '#B49759'; // gold for totals
    return value >= 0 ? '#10b981' : '#ef4444'; // green for positive, red for negative
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={waterfallData}
        margin={{ top: 5, right: 30, left: 20, bottom: 80 }}
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
          tickFormatter={formatCurrency}
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
          label={{
            value: 'Cash Flow',
            angle: -90,
            position: 'insideLeft',
            fill: '#94a3b8',
          }}
        />
        <Tooltip
          formatter={(value: number) => [formatCurrency(value), 'Amount']}
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#e2e8f0',
          }}
        />
        <ReferenceLine y={0} stroke="#64748b" strokeWidth={1} />
        
        <Bar dataKey="end" stackId="a" radius={[8, 8, 0, 0]}>
          {waterfallData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={getColor(entry.displayValue, entry.isTotal)}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};
