/**
 * Monte Carlo Chart Component
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart,
  Line,
} from 'recharts';
import type { MonteCarloBlock } from '../../types/reports';
import { colors, formatChartCurrency } from '../../theme';

interface MonteCarloChartProps {
  data: MonteCarloBlock;
}

export const MonteCarloChart: React.FC<MonteCarloChartProps> = ({ data }) => {
  // Transform data for Recharts
  const chartData = data.percentile_path.map((point) => ({
    year: point.year,
    p10: point.p10,
    p50: point.p50,
    p90: point.p90,
  }));

  const getSuccessColor = (probability: number) => {
    if (probability >= 80) return colors.status.success.base;
    if (probability >= 60) return colors.status.warning.base;
    return colors.status.error.base;
  };

  return (
    <section className="salem-section">
      <h2 className="text-h2 font-display text-text-primary mb-6">Monte Carlo Simulation Results</h2>
      
      <div className="salem-card" style={{ 
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border 
      }}>
        <div className="mb-6">
          <p className="text-h3 text-text-secondary">
            Success Probability: <strong 
              className="text-display font-display"
              style={{ color: getSuccessColor(data.success_probability) }}
            >
              {data.success_probability.toFixed(1)}%
            </strong>
          </p>
          <p className="text-body text-text-tertiary mt-2">
            Based on {data.num_runs.toLocaleString()} simulations over {data.horizon_years} years
          </p>
        </div>

        <div style={{ width: '100%', height: 400 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={chartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
            >
              <defs>
                <linearGradient id="salemGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={colors.brand.navy} stopOpacity={0.1} />
                  <stop offset="95%" stopColor={colors.brand.navy} stopOpacity={0.05} />
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
                label={{ value: 'Portfolio Value', angle: -90, position: 'insideLeft' }}
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
              <Legend
                verticalAlign="top"
                height={36}
                iconType="line"
              />
              {/* Shaded area between p10 and p90 */}
              <Area
                type="monotone"
                dataKey="p90"
                stroke="none"
                fill="url(#salemGradient)"
                name="90th Percentile Band"
              />
              <Area
                type="monotone"
                dataKey="p10"
                stroke="none"
                fill={colors.background.elevated}
                name="10th Percentile Band"
              />
              {/* Percentile lines */}
              <Line
                type="monotone"
                dataKey="p90"
                stroke={colors.status.success.base}
                strokeWidth={2}
                dot={false}
                name="90th Percentile (Optimistic)"
              />
              <Line
                type="monotone"
                dataKey="p50"
                stroke={colors.brand.navy}
                strokeWidth={3}
                dot={false}
                name="50th Percentile (Median)"
              />
              <Line
                type="monotone"
                dataKey="p10"
                stroke={colors.status.warning.base}
                strokeWidth={2}
                dot={false}
                name="10th Percentile (Conservative)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-6 text-body text-text-secondary">
          <p>
            <strong className="text-text-primary">Interpretation:</strong> The chart shows the projected range of portfolio values over time. 
            The median line (50th percentile) represents the most likely outcome, while the shaded area shows 
            the range between the 10th and 90th percentiles, covering 80% of simulated scenarios.
          </p>
        </div>
      </div>
    </section>
  );
};
