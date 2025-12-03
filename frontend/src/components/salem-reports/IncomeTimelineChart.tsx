/**
 * Income Sources Timeline Chart
 * Stacked area chart showing breakdown of income sources over time
 */
import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { IncomeSourcesTimeline } from '../../types/reports';

interface IncomeTimelineChartProps {
  data: IncomeSourcesTimeline[];
}

const formatCurrency = (value: number): string => {
  if (value >= 1e6) {
    return `$${(value / 1e6).toFixed(1)}M`;
  } else if (value >= 1e3) {
    return `$${(value / 1e3).toFixed(0)}K`;
  }
  return `$${value.toFixed(0)}`;
};

export const IncomeTimelineChart: React.FC<IncomeTimelineChartProps> = ({ data }) => {
  return (
    <div className="salem-card">
      <h3 style={{ fontSize: 'var(--salem-text-xl)', marginBottom: 'var(--salem-spacing-md)' }}>
        Income Sources Over Time
      </h3>
      <p style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)', marginBottom: 'var(--salem-spacing-md)' }}>
        Breakdown of income sources throughout the planning horizon
      </p>

      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <defs>
              <linearGradient id="socialSecurity" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="pension" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="annuity" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ec4899" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ec4899" stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="withdrawals" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="other" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.3} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
            <XAxis
              dataKey="year"
              label={{ value: 'Year', position: 'insideBottom', offset: -10 }}
              stroke="#6c757d"
            />
            <YAxis
              tickFormatter={formatCurrency}
              label={{ value: 'Annual Income', angle: -90, position: 'insideLeft' }}
              stroke="#6c757d"
            />
            <Tooltip
              formatter={(value: number) => formatCurrency(value)}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #ced4da',
                borderRadius: '4px',
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="social_security"
              stackId="1"
              stroke="#3b82f6"
              fill="url(#socialSecurity)"
              name="Social Security"
            />
            <Area
              type="monotone"
              dataKey="pension"
              stackId="1"
              stroke="#8b5cf6"
              fill="url(#pension)"
              name="Pension"
            />
            <Area
              type="monotone"
              dataKey="annuity"
              stackId="1"
              stroke="#ec4899"
              fill="url(#annuity)"
              name="Annuity"
            />
            <Area
              type="monotone"
              dataKey="portfolio_withdrawals"
              stackId="1"
              stroke="#f59e0b"
              fill="url(#withdrawals)"
              name="Portfolio Withdrawals"
            />
            <Area
              type="monotone"
              dataKey="other_income"
              stackId="1"
              stroke="#10b981"
              fill="url(#other)"
              name="Other Income"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginTop: 'var(--salem-spacing-md)', fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)' }}>
        <p>
          <strong>Note:</strong> Amounts shown are nominal (not inflation-adjusted) to reflect actual dollar values received in each year.
        </p>
      </div>
    </div>
  );
};
