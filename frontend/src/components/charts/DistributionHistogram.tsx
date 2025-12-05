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
import { colors } from '../../theme';
import { formatChartCurrency } from '../../theme/chartUtils';

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
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={colors.background.border} />
        <XAxis
          dataKey="bin"
          stroke={colors.text.secondary}
          style={{ fontSize: '12px' }}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis
          stroke={colors.text.secondary}
          style={{ fontSize: '12px' }}
          label={{ value: 'Frequency', angle: -90, position: 'insideLeft', fill: colors.text.secondary }}
        />
        <Tooltip
          formatter={(value: number) => [`${value} scenarios`, 'Count']}
          contentStyle={{
            backgroundColor: colors.background.elevated,
            border: `1px solid ${colors.background.border}`,
            borderRadius: '8px',
            color: colors.text.primary,
          }}
        />
        
        <Bar dataKey="count" fill={colors.brand.gold} />
        
        {p10 && (
          <ReferenceLine
            x={formatChartCurrency(p10)}
            stroke={colors.status.error.base}
            strokeWidth={2}
            label={{ value: 'P10', position: 'top', fill: colors.status.error.base }}
          />
        )}
        
        {median && (
          <ReferenceLine
            x={formatChartCurrency(median)}
            stroke={colors.brand.gold}
            strokeWidth={2}
            label={{ value: 'Median', position: 'top', fill: colors.brand.gold }}
          />
        )}
        
        {p90 && (
          <ReferenceLine
            x={formatChartCurrency(p90)}
            stroke={colors.status.success.base}
            strokeWidth={2}
            label={{ value: 'P90', position: 'top', fill: colors.status.success.base }}
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
};
