/**
 * Stress Tests Section Component
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import type { StressScenarioResult } from '../../types/reports';
import { AnalysisTable, type Column } from '../ui/AnalysisTable';
import { colors } from '../../theme';

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
              color: isNegative ? colors.status.error.base : colors.status.success.base,
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
      <h2 className="text-h2 font-display text-text-primary mb-6">Stress Test Analysis</h2>
      <p className="text-body text-text-secondary mb-6">
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
          <div 
            key={scenario.id} 
            className="salem-card"
            style={{ 
              backgroundColor: colors.background.elevated,
              borderColor: colors.background.border 
            }}
          >
            <h3 className="text-h3 font-display text-text-primary mb-3">{scenario.name}</h3>
            <p className="text-body text-text-secondary mb-4">
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
