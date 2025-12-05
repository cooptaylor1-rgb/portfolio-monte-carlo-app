/**
 * Assumptions Section Component
 * Display all planning assumptions in a clear format
 */
import React from 'react';
import type { AssumptionsBlock } from '../../types/reports';
import { AnalysisTable, type Column } from '../ui/AnalysisTable';

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
        <span style={{ color: 'var(--salem-gray-700)' }}>{value}</span>
      ),
    },
    {
      key: 'value',
      label: 'Value',
      align: 'right',
      format: (value: string) => (
        <span
          style={{
            fontFamily: 'var(--salem-font-mono)',
            fontSize: 'var(--salem-text-lg)',
            color: 'var(--salem-navy-primary)',
          }}
        >
          {value}
        </span>
      ),
    },
  ];

  return (
    <section className="salem-section">
      <h2>Planning Assumptions</h2>
      
      <div className="salem-card">
        <p style={{ marginBottom: 'var(--salem-spacing-lg)', color: 'var(--salem-gray-700)' }}>
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
