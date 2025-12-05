/**
 * Income Sources Timeline Chart
 * Phase 7: Updated with design system styling
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
import { colors, formatChartCurrency } from '../../theme';

interface IncomeTimelineChartProps {
  data: IncomeSourcesTimeline[];
}

export const IncomeTimelineChart: React.FC<IncomeTimelineChartProps> = ({ data }) => {
  return (
    <div 
      className="salem-card"
      style={{ 
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border 
      }}
    >
      <h3 className="text-h3 font-display text-text-primary mb-3">
        Income Sources Over Time
      </h3>
      <p className="text-body text-text-secondary mb-4">
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
                <stop offset="5%" stopColor={colors.chart.equity} stopOpacity={0.8} />
                <stop offset="95%" stopColor={colors.chart.equity} stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="pension" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors.chart.fixed} stopOpacity={0.8} />
                <stop offset="95%" stopColor={colors.chart.fixed} stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="annuity" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors.status.info.base} stopOpacity={0.8} />
                <stop offset="95%" stopColor={colors.status.info.base} stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="withdrawals" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors.brand.gold} stopOpacity={0.8} />
                <stop offset="95%" stopColor={colors.brand.gold} stopOpacity={0.3} />
              </linearGradient>
              <linearGradient id="other" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors.status.success.base} stopOpacity={0.8} />
                <stop offset="95%" stopColor={colors.status.success.base} stopOpacity={0.3} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.background.border} />
            <XAxis
              dataKey="year"
              label={{ value: 'Year', position: 'insideBottom', offset: -10 }}
              stroke={colors.text.tertiary}
            />
            <YAxis
              tickFormatter={(value: number) => formatChartCurrency(value)}
              label={{ value: 'Annual Income', angle: -90, position: 'insideLeft' }}
              stroke={colors.text.tertiary}
            />
            <Tooltip
              formatter={(value: number) => formatChartCurrency(value)}
              contentStyle={{
                backgroundColor: colors.background.elevated,
                border: `1px solid ${colors.background.border}`,
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Legend />
            <Area
              type="monotone"
              dataKey="social_security"
              stackId="1"
              stroke={colors.chart.equity}
              fill="url(#socialSecurity)"
              name="Social Security"
            />
            <Area
              type="monotone"
              dataKey="pension"
              stackId="1"
              stroke={colors.chart.fixed}
              fill="url(#pension)"
              name="Pension"
            />
            <Area
              type="monotone"
              dataKey="annuity"
              stackId="1"
              stroke={colors.status.info.base}
              fill="url(#annuity)"
              name="Annuity"
            />
            <Area
              type="monotone"
              dataKey="portfolio_withdrawals"
              stackId="1"
              stroke={colors.brand.gold}
              fill="url(#withdrawals)"
              name="Portfolio Withdrawals"
            />
            <Area
              type="monotone"
              dataKey="other_income"
              stackId="1"
              stroke={colors.status.success.base}
              fill="url(#other)"
              name="Other Income"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="text-body text-text-secondary mt-4">
        <p>
          <strong className="text-text-primary">Note:</strong> Amounts shown are nominal (not inflation-adjusted) to reflect actual dollar values received in each year.
        </p>
      </div>
    </div>
  );
};
