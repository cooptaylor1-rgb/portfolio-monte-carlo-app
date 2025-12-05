/**
 * Stress Test Comparison Bar Chart
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { StressScenarioResult } from '../../types/reports';
import { AnalysisTable } from '../ui/AnalysisTable';
import { colors } from '../../theme';

interface StressTestChartProps {
  scenarios: StressScenarioResult[];
}

export const StressTestChart: React.FC<StressTestChartProps> = ({ scenarios }) => {
  const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

  // Transform data for chart
  const chartData = scenarios.map((scenario) => ({
    name: scenario.name,
    base: scenario.base_success_probability,
    stressed: scenario.stressed_success_probability,
    impact: scenario.base_success_probability - scenario.stressed_success_probability,
  }));

  const getColor = (probability: number) => {
    if (probability >= 0.85) return colors.status.success.base;
    if (probability >= 0.70) return colors.status.warning.base;
    return colors.status.error.base;
  };

  const getSeverityStyle = (value: string) => {
    if (value === 'High' || value === 'Severe') {
      return {
        backgroundColor: `${colors.status.error.base}15`,
        color: colors.status.error.dark,
      };
    }
    if (value === 'Moderate') {
      return {
        backgroundColor: `${colors.status.warning.base}15`,
        color: colors.status.warning.dark,
      };
    }
    return {
      backgroundColor: `${colors.status.info.base}15`,
      color: colors.status.info.dark,
    };
  };

  return (
    <div 
      className="salem-card"
      style={{ 
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border 
      }}
    >
      <h3 className="text-h3 font-display text-text-primary mb-3">
        Impact of Stress Scenarios on Plan Success
      </h3>
      <p className="text-body text-text-secondary mb-4">
        Comparison of success probability under adverse conditions
      </p>

      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke={colors.background.border} />
            <XAxis
              dataKey="name"
              angle={-15}
              textAnchor="end"
              height={80}
              stroke={colors.text.tertiary}
            />
            <YAxis
              domain={[0, 1]}
              tickFormatter={formatPercent}
              label={{ value: 'Success Probability', angle: -90, position: 'insideLeft' }}
              stroke={colors.text.tertiary}
            />
            <Tooltip
              formatter={(value: number) => formatPercent(value)}
              contentStyle={{
                backgroundColor: colors.background.elevated,
                border: `1px solid ${colors.background.border}`,
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Bar dataKey="base" name="Base Case" fill={colors.brand.navy} />
            <Bar dataKey="stressed" name="Stressed Case">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.stressed)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Impact Summary Table */}
      <div className="mt-6">
        <AnalysisTable<{
          scenario: string;
          impact: number;
          severity: string;
        }>
          columns={[
            {
              key: 'scenario',
              label: 'Scenario',
              align: 'left',
            },
            {
              key: 'impact',
              label: 'Impact',
              align: 'right',
              format: (value: number) => (
                <span style={{ color: colors.status.error.base, fontWeight: 600 }}>
                  {formatPercent(value)}
                </span>
              ),
            },
            {
              key: 'severity',
              label: 'Severity',
              align: 'right',
              format: (value: string) => {
                const severityStyle = getSeverityStyle(value);
                return (
                  <span
                    className="text-small font-semibold uppercase px-2 py-1 rounded"
                    style={severityStyle}
                  >
                    {value}
                  </span>
                );
              },
            },
          ]}
          data={scenarios.map((scenario) => ({
            scenario: scenario.name,
            impact: scenario.base_success_probability - scenario.stressed_success_probability,
            severity: scenario.impact_severity || 'Low',
          }))}
          variant="striped"
        />
      </div>
    </div>
  );
};
