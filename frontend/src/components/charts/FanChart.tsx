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
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(value);
  };

  const formatYear = (month: number) => {
    return `Y${Math.floor(month / 12)}`;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis
          dataKey="month"
          tickFormatter={formatYear}
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          tickFormatter={formatCurrency}
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
        />
        <Tooltip
          formatter={(value: number) => formatCurrency(value)}
          labelFormatter={(label: number) => `Month ${label}`}
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#e2e8f0',
          }}
        />
        <Legend
          wrapperStyle={{ color: '#e2e8f0' }}
          iconType="line"
        />
        
        {/* P90 Line */}
        <Line
          type="monotone"
          dataKey="p90"
          stroke="#10b981"
          strokeWidth={2}
          dot={false}
          name="90th Percentile"
        />
        
        {/* P75 Line */}
        <Line
          type="monotone"
          dataKey="p75"
          stroke="#6ee7b7"
          strokeWidth={1.5}
          dot={false}
          name="75th Percentile"
          strokeDasharray="5 5"
        />
        
        {/* Median Line */}
        <Line
          type="monotone"
          dataKey="median"
          stroke="#B49759"
          strokeWidth={3}
          dot={false}
          name="Median"
        />
        
        {/* P25 Line */}
        <Line
          type="monotone"
          dataKey="p25"
          stroke="#fbbf24"
          strokeWidth={1.5}
          dot={false}
          name="25th Percentile"
          strokeDasharray="5 5"
        />
        
        {/* P10 Line */}
        <Line
          type="monotone"
          dataKey="p10"
          stroke="#ef4444"
          strokeWidth={2}
          dot={false}
          name="10th Percentile"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
