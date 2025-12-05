/**
 * Assumptions Section Component
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import type { AssumptionsBlock } from '../../types/reports';
import { AnalysisTable, type Column } from '../ui/AnalysisTable';
import { colors } from '../../theme';

interface AssumptionsSectionProps {
  assumptions: AssumptionsBlock;
}

export const AssumptionsSection: React.FC<AssumptionsSectionProps> = ({ assumptions }) => {
  type AssumptionRow = {
    label: string;
    value: string;
  };

  const assumptionRows: AssumptionRow[] = [
    { label: 'Current Age', value: String(assumptions.current_age) },
    { label: 'Retirement Age', value: String(assumptions.retirement_age) },
    { label: 'Life Expectancy', value: String(assumptions.life_expectancy) },
    { label: 'Initial Portfolio Value', value: assumptions.initial_portfolio },
    { label: 'Annual Contribution (Pre-Retirement)', value: assumptions.annual_contribution },
    { label: 'Annual Spending (Post-Retirement)', value: assumptions.annual_spending },
    { label: 'Expected Annual Return', value: assumptions.expected_return },
    { label: 'Expected Inflation Rate', value: assumptions.inflation_rate },
    { label: 'Asset Allocation', value: assumptions.allocation },
  ];

  const columns: Column<AssumptionRow>[] = [
    {
      key: 'label',
      label: 'Assumption',
      align: 'left',
      width: '60%',
      cellClassName: 'font-medium',
      format: (value: string) => (
        <span style={{ color: colors.text.secondary }}>{value}</span>
      ),
    },
    {
      key: 'value',
      label: 'Value',
      align: 'right',
      format: (value: string) => (
        <span
          className="font-mono text-h4"
          style={{
            color: colors.brand.navy,
          }}
        >
          {value}
        </span>
      ),
    },
  ];

  return (
    <section className="salem-section">
      <h2 className="text-h2 font-display text-text-primary mb-6">Planning Assumptions</h2>
      
      <div 
        className="salem-card"
        style={{ 
          backgroundColor: colors.background.elevated,
          borderColor: colors.background.border 
        }}
      >
        <p className="text-body text-text-secondary mb-6">
          This analysis is based on the following assumptions. Changes to these inputs may materially 
          affect the projected outcomes.
        </p>

        <AnalysisTable<AssumptionRow>
          columns={columns}
          data={assumptionRows}
          variant="striped"
        />
      </div>
    </section>
  );
};
