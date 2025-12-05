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
} from 'recharts';
import { colors } from '../../theme';
import { formatChartCurrency } from '../../theme/chartUtils';

interface FanChartProps {
  data: Array<{
    month: number;
    p10: number;
    p25: number;
    median: number;
    p75: number;
    p90: number;
  }>;
  height?: number;
}

export const FanChart: React.FC<FanChartProps> = ({ data, height = 400 }) => {
  const formatYear = (month: number) => {
    return `Y${Math.floor(month / 12)}`;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={colors.background.border} />
        <XAxis
          dataKey="month"
          tickFormatter={formatYear}
          stroke={colors.text.secondary}
          style={{ fontSize: '12px' }}
        />
        <YAxis
          tickFormatter={formatChartCurrency}
          stroke={colors.text.secondary}
          style={{ fontSize: '12px' }}
        />
        <Tooltip
          formatter={(value: number) => formatChartCurrency(value)}
          labelFormatter={(label: number) => `Month ${label}`}
          contentStyle={{
            backgroundColor: colors.background.elevated,
            border: `1px solid ${colors.background.border}`,
            borderRadius: '8px',
            color: colors.text.primary,
          }}
        />
        <Legend
          wrapperStyle={{ color: colors.text.primary }}
          iconType="line"
        />
        
        {/* P90 Line */}
        <Line
          type="monotone"
          dataKey="p90"
          stroke={colors.status.success.base}
          strokeWidth={2}
          dot={false}
          name="90th Percentile"
        />
        
        {/* P75 Line */}
        <Line
          type="monotone"
          dataKey="p75"
          stroke={colors.status.success.light}
          strokeWidth={1.5}
          dot={false}
          name="75th Percentile"
          strokeDasharray="5 5"
        />
        
        {/* Median Line */}
        <Line
          type="monotone"
          dataKey="median"
          stroke={colors.brand.gold}
          strokeWidth={3}
          dot={false}
          name="Median"
        />
        
        {/* P25 Line */}
        <Line
          type="monotone"
          dataKey="p25"
          stroke={colors.status.warning.base}
          strokeWidth={1.5}
          dot={false}
          name="25th Percentile"
          strokeDasharray="5 5"
        />
        
        {/* P10 Line */}
        <Line
          type="monotone"
          dataKey="p10"
          stroke={colors.status.error.base}
          strokeWidth={2}
          dot={false}
          name="10th Percentile"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
