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
import { colors } from '../../theme';
import { formatChartCurrency } from '../../theme/chartUtils';

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
    if (isTotal) return colors.brand.gold;
    return value >= 0 ? colors.status.success.base : colors.status.error.base;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={waterfallData}
        margin={{ top: 5, right: 30, left: 20, bottom: 80 }}
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
          tickFormatter={formatChartCurrency}
          stroke={colors.text.secondary}
          style={{ fontSize: '12px' }}
          label={{
            value: 'Cash Flow',
            angle: -90,
            position: 'insideLeft',
            fill: colors.text.secondary,
          }}
        />
        <Tooltip
          formatter={(value: number) => [formatChartCurrency(Math.abs(value)), 'Amount']}
          contentStyle={{
            backgroundColor: colors.background.elevated,
            border: `1px solid ${colors.background.border}`,
            borderRadius: '8px',
            color: colors.text.primary,
          }}
        />
        <ReferenceLine y={0} stroke={colors.text.tertiary} strokeWidth={1} />
        
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
