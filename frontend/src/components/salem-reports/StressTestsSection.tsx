/**
 * Stress Tests Section Component
 * Display stress test scenarios with base vs stressed comparisons
 */
import React from 'react';
import type { StressScenarioResult } from '../../types/reports';
import { AnalysisTable, type Column } from '../ui/AnalysisTable';

interface StressTestsSectionProps {
  stressTests: StressScenarioResult[];
}

export const StressTestsSection: React.FC<StressTestsSectionProps> = ({ stressTests }) => {
  type MetricRow = {
    metric: string;
    base_value: string;
    stressed_value: string;
    change: string;
  };

  const columns: Column<MetricRow>[] = [
    {
      key: 'metric',
      label: 'Metric',
      align: 'left',
      cellClassName: 'font-medium',
    },
    {
      key: 'base_value',
      label: 'Base Case',
      align: 'right',
    },
    {
      key: 'stressed_value',
      label: 'Stressed Case',
      align: 'right',
    },
    {
      key: 'change',
      label: 'Change',
      align: 'right',
      format: (value: string) => {
        const changeValue = parseFloat(value);
        const isNegative = changeValue < 0;
        return (
          <span
            className="font-semibold"
            style={{
              color: isNegative ? 'var(--salem-danger)' : 'var(--salem-success)',
            }}
          >
            {value}
          </span>
        );
      },
    },
  ];

  return (
    <section className="salem-section">
      <h2>Stress Test Analysis</h2>
      <p style={{ marginBottom: 'var(--salem-spacing-lg)', color: 'var(--salem-gray-700)' }}>
        The following scenarios test the resilience of your retirement plan under adverse market conditions.
      </p>

      {stressTests.map((scenario) => {
        const tableData: MetricRow[] = scenario.base_metrics.map((metric, index) => ({
          metric: metric.label,
          base_value: metric.base_value,
          stressed_value: scenario.stressed_metrics[index].stressed_value,
          change: metric.change,
        }));

        return (
          <div key={scenario.id} className="salem-card">
            <h3>{scenario.name}</h3>
            <p style={{ color: 'var(--salem-gray-600)', marginBottom: 'var(--salem-spacing-md)' }}>
              {scenario.description}
            </p>

            <AnalysisTable<MetricRow>
              columns={columns}
              data={tableData}
              variant="striped"
            />
          </div>
        );
      })}
    </section>
  );
};
