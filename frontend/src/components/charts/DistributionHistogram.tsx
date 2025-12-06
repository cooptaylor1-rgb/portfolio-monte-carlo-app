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
  Cell,
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
  // Guard against empty or invalid data
  if (!data || data.length === 0) {
    return (
      <div 
        style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        className="text-text-secondary"
      >
        No distribution data available
      </div>
    );
  }

  // Color bars based on position relative to median
  const getBarColor = (value: number) => {
    if (!median) return colors.brand.gold;
    if (value >= median) return colors.chart.p90; // Above median = green
    if (value >= (p10 || 0)) return colors.brand.gold; // Between p10 and median = gold
    return colors.chart.p10; // Below p10 = red
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart 
        data={data} 
        margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
      >
        <defs>
          {/* Gradient for bars */}
          <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={colors.brand.gold} stopOpacity={0.9}/>
            <stop offset="100%" stopColor={colors.brand.gold} stopOpacity={0.6}/>
          </linearGradient>
        </defs>
        
        <CartesianGrid 
          strokeDasharray="3 3" 
          stroke={colors.background.border}
          opacity={0.5}
        />
        <XAxis
          dataKey="bin"
          stroke={colors.text.tertiary}
          style={{ fontSize: '11px', fontFamily: 'Inter, sans-serif' }}
          angle={-45}
          textAnchor="end"
          height={80}
          tick={{ fill: colors.text.tertiary }}
        />
        <YAxis
          stroke={colors.text.tertiary}
          style={{ fontSize: '12px', fontFamily: 'Inter, sans-serif' }}
          label={{ 
            value: 'Frequency', 
            angle: -90, 
            position: 'insideLeft', 
            fill: colors.text.secondary,
            style: { fontSize: '13px' }
          }}
          tick={{ fill: colors.text.tertiary }}
        />
        <Tooltip
          formatter={(value: number) => [`${value} scenarios`, 'Count']}
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
        
        <Bar 
          dataKey="count" 
          fill="url(#barGradient)"
          radius={[4, 4, 0, 0]}
          animationDuration={1000}
          animationEasing="ease-out"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={getBarColor(entry.value)} opacity={0.8} />
          ))}
        </Bar>
        
        {p10 && (
          <ReferenceLine
            x={formatChartCurrency(p10)}
            stroke={colors.chart.p10}
            strokeWidth={2.5}
            strokeDasharray="5 5"
            label={{ 
              value: '10th %ile', 
              position: 'top', 
              fill: colors.chart.p10,
              fontSize: 12,
              fontWeight: 600,
            }}
          />
        )}
        
        {median && (
          <ReferenceLine
            x={formatChartCurrency(median)}
            stroke={colors.brand.gold}
            strokeWidth={3}
            label={{ 
              value: 'Median', 
              position: 'top', 
              fill: colors.brand.gold,
              fontSize: 12,
              fontWeight: 700,
            }}
          />
        )}
        
        {p90 && (
          <ReferenceLine
            x={formatChartCurrency(p90)}
            stroke={colors.chart.p90}
            strokeWidth={2.5}
            strokeDasharray="5 5"
            label={{ 
              value: '90th %ile', 
              position: 'top', 
              fill: colors.chart.p90,
              fontSize: 12,
              fontWeight: 600,
            }}
          />
        )}
      </BarChart>
    </ResponsiveContainer>
  );
};
