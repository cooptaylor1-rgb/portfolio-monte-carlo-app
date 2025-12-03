/**
 * Stress Test Comparison Bar Chart
 * Side-by-side comparison of base vs stressed success probabilities
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
    if (probability >= 0.85) return '#4CAF50'; // green
    if (probability >= 0.70) return '#FFC107'; // amber
    return '#D9534F'; // red
  };

  return (
    <div className="salem-card">
      <h3 style={{ fontSize: 'var(--salem-text-xl)', marginBottom: 'var(--salem-spacing-md)' }}>
        Impact of Stress Scenarios on Plan Success
      </h3>
      <p style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)', marginBottom: 'var(--salem-spacing-md)' }}>
        Comparison of success probability under adverse conditions
      </p>

      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
            <XAxis
              dataKey="name"
              angle={-15}
              textAnchor="end"
              height={80}
              stroke="#6c757d"
            />
            <YAxis
              domain={[0, 1]}
              tickFormatter={formatPercent}
              label={{ value: 'Success Probability', angle: -90, position: 'insideLeft' }}
              stroke="#6c757d"
            />
            <Tooltip
              formatter={(value: number) => formatPercent(value)}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #ced4da',
                borderRadius: '4px',
              }}
            />
            <Legend />
            <Bar dataKey="base" name="Base Case" fill="#00335d" />
            <Bar dataKey="stressed" name="Stressed Case">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.stressed)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Impact Summary Table */}
      <div style={{ marginTop: 'var(--salem-spacing-lg)' }}>
        <table className="salem-table">
          <thead>
            <tr>
              <th>Scenario</th>
              <th style={{ textAlign: 'right' }}>Impact</th>
              <th style={{ textAlign: 'right' }}>Severity</th>
            </tr>
          </thead>
          <tbody>
            {scenarios.map((scenario) => {
              const impact = scenario.base_success_probability - scenario.stressed_success_probability;
              return (
                <tr key={scenario.id}>
                  <td>{scenario.name}</td>
                  <td style={{ textAlign: 'right', color: 'var(--salem-danger)', fontWeight: 600 }}>
                    {formatPercent(impact)}
                  </td>
                  <td style={{ textAlign: 'right', textTransform: 'capitalize' }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: 'var(--salem-text-xs)',
                      fontWeight: 600,
                      backgroundColor: scenario.impact_severity === 'high' ? '#fee2e2' :
                                    scenario.impact_severity === 'medium' ? '#fef3c7' : '#dbeafe',
                      color: scenario.impact_severity === 'high' ? '#991b1b' :
                            scenario.impact_severity === 'medium' ? '#92400e' : '#1e40af',
                    }}>
                      {scenario.impact_severity}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
