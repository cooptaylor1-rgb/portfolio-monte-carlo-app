/**
 * MonteCarloResults Component
 * Professional visualization of Monte Carlo simulation results with percentile bands
 */
import React from 'react';
import type { MonthlyStats, ModelInputs, SimulationMetrics } from '../../types';
import { formatCurrency, formatPercent } from '../../utils/reportFormatters';
import {
  LineChart,
  Line,
  Area,
  AreaChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface MonteCarloResultsProps {
  stats: MonthlyStats[];
  metrics: SimulationMetrics;
  modelInputs: ModelInputs;
}

export const MonteCarloResults: React.FC<MonteCarloResultsProps> = ({
  stats,
  metrics,
  modelInputs,
}) => {
  // Convert monthly stats to yearly for cleaner display
  const yearlyStats = stats.filter((_, index) => index % 12 === 0).map((stat, index) => ({
    year: index,
    age: modelInputs.current_age + index,
    p10: stat.P10,
    p25: stat.P25,
    median: stat.Median,
    p75: stat.P75,
    p90: stat.P90,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-background-elevated border border-background-border rounded-lg p-4 shadow-lg">
          <p className="text-small font-semibold text-text-primary mb-2">
            Year {data.year} (Age {data.age})
          </p>
          <div className="space-y-1 text-small">
            <div className="flex justify-between gap-4">
              <span className="text-text-tertiary">90th Percentile:</span>
              <span className="text-text-primary font-medium">{formatCurrency(data.p90)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-text-tertiary">75th Percentile:</span>
              <span className="text-text-primary font-medium">{formatCurrency(data.p75)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-text-tertiary">Median (50th):</span>
              <span className="text-text-primary font-medium">{formatCurrency(data.median)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-text-tertiary">25th Percentile:</span>
              <span className="text-text-primary font-medium">{formatCurrency(data.p25)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-text-tertiary">10th Percentile:</span>
              <span className="text-text-primary font-medium">{formatCurrency(data.p10)}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="report-section mb-12 print:mb-8 print:break-inside-avoid">
      <h2 className="text-h2 font-display text-text-primary mb-6 print:text-2xl">
        Monte Carlo Simulation Results
      </h2>

      <div className="bg-background-elevated border border-background-border rounded-lg p-6 mb-6 print:p-4">
        <p className="text-body text-text-primary mb-4">
          The chart below displays projected portfolio values over {modelInputs.years_to_model} years 
          based on {modelInputs.n_scenarios} Monte Carlo simulations. The shaded regions represent 
          the range of potential outcomes, with darker shading indicating more likely scenarios.
        </p>
        
        <div className="h-96 print:h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={yearlyStats} margin={{ top: 10, right: 30, left: 60, bottom: 40 }}>
              <defs>
                <linearGradient id="colorP10P90" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4CA6E8" stopOpacity={0.1} />
                  <stop offset="95%" stopColor="#4CA6E8" stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorP25P75" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4CA6E8" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#4CA6E8" stopOpacity={0.2} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#262A33" />
              <XAxis 
                dataKey="year" 
                stroke="#9CA3AF"
                label={{ value: 'Years from Now', position: 'insideBottom', offset: -10, fill: '#9CA3AF' }}
              />
              <YAxis 
                stroke="#9CA3AF"
                tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                label={{ value: 'Portfolio Value ($)', angle: -90, position: 'insideLeft', fill: '#9CA3AF' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="top" 
                height={36}
                wrapperStyle={{ paddingBottom: '20px' }}
              />
              
              {/* 10th-90th percentile band */}
              <Area
                type="monotone"
                dataKey="p90"
                stroke="none"
                fill="url(#colorP10P90)"
                name="10th-90th Percentile Range"
              />
              <Area
                type="monotone"
                dataKey="p10"
                stroke="none"
                fill="#0C0E12"
                name=""
              />
              
              {/* 25th-75th percentile band */}
              <Area
                type="monotone"
                dataKey="p75"
                stroke="none"
                fill="url(#colorP25P75)"
                name="25th-75th Percentile Range"
              />
              <Area
                type="monotone"
                dataKey="p25"
                stroke="none"
                fill="#0C0E12"
                name=""
              />
              
              {/* Median line */}
              <Line
                type="monotone"
                dataKey="median"
                stroke="#4CA6E8"
                strokeWidth={3}
                dot={false}
                name="Median Path"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-background-border print:grid-cols-3">
          <div className="text-center">
            <div className="w-full h-3 bg-chart-blue opacity-10 rounded mb-2"></div>
            <p className="text-small text-text-tertiary mb-1">10th-90th Percentile</p>
            <p className="text-body text-text-secondary font-medium">80% of scenarios</p>
          </div>
          <div className="text-center">
            <div className="w-full h-3 bg-chart-blue opacity-20 rounded mb-2"></div>
            <p className="text-small text-text-tertiary mb-1">25th-75th Percentile</p>
            <p className="text-body text-text-secondary font-medium">50% of scenarios</p>
          </div>
          <div className="text-center">
            <div className="w-full h-3 bg-chart-blue rounded mb-2"></div>
            <p className="text-small text-text-tertiary mb-1">Median Path</p>
            <p className="text-body text-text-secondary font-medium">Most likely outcome</p>
          </div>
        </div>
      </div>

      {/* Outcome Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 print:gap-4">
        <OutcomeCard
          title="Best Case (90th %ile)"
          value={formatCurrency(metrics.ending_p90)}
          description="In favorable market conditions, portfolio could grow to this level"
          variant="success"
        />
        <OutcomeCard
          title="Expected (Median)"
          value={formatCurrency(metrics.ending_median)}
          description="Most likely outcome based on central assumptions"
          variant="neutral"
        />
        <OutcomeCard
          title="Worst Case (10th %ile)"
          value={formatCurrency(metrics.ending_p10)}
          description="In adverse conditions, portfolio could decline to this level"
          variant="warning"
        />
      </div>
    </div>
  );
};

interface OutcomeCardProps {
  title: string;
  value: string;
  description: string;
  variant: 'success' | 'neutral' | 'warning';
}

const OutcomeCard: React.FC<OutcomeCardProps> = ({ title, value, description, variant }) => {
  const borderColor = 
    variant === 'success' ? 'border-status-success-base' :
    variant === 'warning' ? 'border-status-warning-base' :
    'border-accent-gold';

  return (
    <div className={`bg-background-elevated border-l-4 ${borderColor} border-y border-r border-background-border rounded-lg p-5 print:p-4`}>
      <p className="text-small font-semibold text-text-secondary uppercase tracking-wider mb-2">
        {title}
      </p>
      <p className="text-h2 font-display text-text-primary mb-3 print:text-xl">
        {value}
      </p>
      <p className="text-small text-text-tertiary leading-relaxed">
        {description}
      </p>
    </div>
  );
};
