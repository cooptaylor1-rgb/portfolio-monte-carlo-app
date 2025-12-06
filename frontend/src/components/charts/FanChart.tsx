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
  Area,
  AreaChart,
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
  showLegend?: boolean;
}

export const FanChart: React.FC<FanChartProps> = ({ 
  data, 
  height = 400,
  showLegend = true 
}) => {
  const formatYear = (month: number) => {
    return `Year ${Math.floor(month / 12)}`;
  };

  // Guard against empty or invalid data
  if (!data || data.length === 0) {
    return (
      <div 
        style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        className="text-text-secondary"
      >
        No trajectory data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart 
        data={data} 
        margin={{ top: 10, right: 30, left: 20, bottom: 5 }}
      >
        <defs>
          {/* Gradient for area fills */}
          <linearGradient id="goldGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={colors.brand.gold} stopOpacity={0.3}/>
            <stop offset="95%" stopColor={colors.brand.gold} stopOpacity={0.05}/>
          </linearGradient>
        </defs>
        
        <CartesianGrid 
          strokeDasharray="3 3" 
          stroke={colors.background.border}
          opacity={0.5}
        />
        <XAxis
          dataKey="month"
          tickFormatter={formatYear}
          stroke={colors.text.tertiary}
          style={{ fontSize: '12px', fontFamily: 'Inter, sans-serif' }}
          tick={{ fill: colors.text.tertiary }}
        />
        <YAxis
          tickFormatter={formatChartCurrency}
          stroke={colors.text.tertiary}
          style={{ fontSize: '12px', fontFamily: 'Inter, sans-serif' }}
          tick={{ fill: colors.text.tertiary }}
        />
        <Tooltip
          formatter={(value: number) => [formatChartCurrency(value), '']}
          labelFormatter={(label: number) => `Month ${label} (Year ${Math.floor(label / 12)})`}
          contentStyle={{
            backgroundColor: colors.background.elevated,
            border: `1px solid ${colors.background.border}`,
            borderRadius: '8px',
            color: colors.text.primary,
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          }}
          itemStyle={{
            color: colors.text.secondary,
            fontSize: '12px',
          }}
        />
        {showLegend && (
          <Legend
            wrapperStyle={{ 
              color: colors.text.primary,
              paddingTop: '20px',
            }}
            iconType="line"
            formatter={(value) => <span style={{ color: colors.text.secondary, fontSize: '13px' }}>{value}</span>}
          />
        )}
        
        {/* P90 Line - Best case */}
        <Line
          type="monotone"
          dataKey="p90"
          stroke={colors.chart.p90}
          strokeWidth={2.5}
          dot={false}
          name="90th Percentile (Best Case)"
          activeDot={{ r: 6, fill: colors.chart.p90 }}
        />
        
        {/* P75 Line */}
        <Line
          type="monotone"
          dataKey="p75"
          stroke={colors.chart.p75}
          strokeWidth={1.5}
          dot={false}
          name="75th Percentile"
          strokeDasharray="5 5"
          activeDot={{ r: 5, fill: colors.chart.p75 }}
        />
        
        {/* Median Line - Most important */}
        <Line
          type="monotone"
          dataKey="median"
          stroke={colors.brand.gold}
          strokeWidth={3.5}
          dot={false}
          name="Median (Expected)"
          activeDot={{ r: 7, fill: colors.brand.gold, stroke: colors.background.elevated, strokeWidth: 2 }}
        />
        
        {/* P25 Line */}
        <Line
          type="monotone"
          dataKey="p25"
          stroke={colors.chart.p25}
          strokeWidth={1.5}
          dot={false}
          name="25th Percentile"
          strokeDasharray="5 5"
          activeDot={{ r: 5, fill: colors.chart.p25 }}
        />
        
        {/* P10 Line - Worst case */}
        <Line
          type="monotone"
          dataKey="p10"
          stroke={colors.chart.p10}
          strokeWidth={2.5}
          dot={false}
          name="10th Percentile (Worst Case)"
          activeDot={{ r: 6, fill: colors.chart.p10 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
