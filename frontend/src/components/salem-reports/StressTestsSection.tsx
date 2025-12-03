/**
 * Stress Tests Section Component
 * Display stress test scenarios with base vs stressed comparisons
 */
import React from 'react';
import type { StressScenarioResult } from '../../types/reports';

interface StressTestsSectionProps {
  stressTests: StressScenarioResult[];
}

export const StressTestsSection: React.FC<StressTestsSectionProps> = ({ stressTests }) => {
  return (
    <section className="salem-section">
      <h2>Stress Test Analysis</h2>
      <p style={{ marginBottom: 'var(--salem-spacing-lg)', color: 'var(--salem-gray-700)' }}>
        The following scenarios test the resilience of your retirement plan under adverse market conditions.
      </p>

      {stressTests.map((scenario) => (
        <div key={scenario.id} className="salem-card">
          <h3>{scenario.name}</h3>
          <p style={{ color: 'var(--salem-gray-600)', marginBottom: 'var(--salem-spacing-md)' }}>
            {scenario.description}
          </p>

          <table className="salem-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Base Case</th>
                <th>Stressed Case</th>
                <th>Change</th>
              </tr>
            </thead>
            <tbody>
              {scenario.base_metrics.map((metric, index) => {
                const stressedMetric = scenario.stressed_metrics[index];
                const changeValue = parseFloat(metric.change);
                const isNegative = changeValue < 0;
                
                return (
                  <tr key={index}>
                    <td style={{ fontWeight: 500 }}>{metric.label}</td>
                    <td>{metric.base_value}</td>
                    <td>{stressedMetric.stressed_value}</td>
                    <td style={{ 
                      color: isNegative ? 'var(--salem-danger)' : 'var(--salem-success)',
                      fontWeight: 600
                    }}>
                      {metric.change}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ))}
    </section>
  );
};
