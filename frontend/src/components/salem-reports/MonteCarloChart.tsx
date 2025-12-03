/**
 * Monte Carlo Chart Component
 * Display percentile paths using Recharts with Salem branding
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

interface MonteCarloChartProps {
  data: MonteCarloBlock;
}

const formatCurrency = (value: number): string => {
  if (value >= 1e6) {
    return `$${(value / 1e6).toFixed(1)}M`;
  } else if (value >= 1e3) {
    return `$${(value / 1e3).toFixed(0)}K`;
  }
  return `$${value.toFixed(0)}`;
};

export const MonteCarloChart: React.FC<MonteCarloChartProps> = ({ data }) => {
  // Transform data for Recharts
  const chartData = data.percentile_path.map((point) => ({
    year: point.year,
    p10: point.p10,
    p50: point.p50,
    p90: point.p90,
  }));

  return (
    <section className="salem-section">
      <h2>Monte Carlo Simulation Results</h2>
      
      <div className="salem-card">
        <div style={{ marginBottom: 'var(--salem-spacing-lg)' }}>
          <p style={{ fontSize: 'var(--salem-text-lg)', color: 'var(--salem-gray-700)' }}>
            Success Probability: <strong style={{ 
              color: data.success_probability >= 80 ? 'var(--salem-success)' : 
                     data.success_probability >= 60 ? 'var(--salem-warning)' : 
                     'var(--salem-danger)',
              fontSize: 'var(--salem-text-2xl)'
            }}>
              {data.success_probability.toFixed(1)}%
            </strong>
          </p>
          <p style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)' }}>
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
                  <stop offset="5%" stopColor="#00335d" stopOpacity={0.1} />
                  <stop offset="95%" stopColor="#00335d" stopOpacity={0.05} />
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
                label={{ value: 'Portfolio Value', angle: -90, position: 'insideLeft' }}
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
                fill="white"
                name="10th Percentile Band"
              />
              {/* Percentile lines */}
              <Line
                type="monotone"
                dataKey="p90"
                stroke="#4b8f29"
                strokeWidth={2}
                dot={false}
                name="90th Percentile (Optimistic)"
              />
              <Line
                type="monotone"
                dataKey="p50"
                stroke="#00335d"
                strokeWidth={3}
                dot={false}
                name="50th Percentile (Median)"
              />
              <Line
                type="monotone"
                dataKey="p10"
                stroke="#d97706"
                strokeWidth={2}
                dot={false}
                name="10th Percentile (Conservative)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div style={{ marginTop: 'var(--salem-spacing-lg)', fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)' }}>
          <p>
            <strong>Interpretation:</strong> The chart shows the projected range of portfolio values over time. 
            The median line (50th percentile) represents the most likely outcome, while the shaded area shows 
            the range between the 10th and 90th percentiles, covering 80% of simulated scenarios.
          </p>
        </div>
      </div>
    </section>
  );
};
