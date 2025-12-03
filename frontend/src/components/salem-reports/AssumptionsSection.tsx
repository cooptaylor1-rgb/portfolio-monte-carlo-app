/**
 * Assumptions Section Component
 * Display all planning assumptions in a clear format
 */
import React from 'react';
import type { AssumptionsBlock } from '../../types/reports';

interface AssumptionsSectionProps {
  assumptions: AssumptionsBlock;
}

export const AssumptionsSection: React.FC<AssumptionsSectionProps> = ({ assumptions }) => {
  const assumptionRows = [
    { label: 'Current Age', value: assumptions.current_age },
    { label: 'Retirement Age', value: assumptions.retirement_age },
    { label: 'Life Expectancy', value: assumptions.life_expectancy },
    { label: 'Initial Portfolio Value', value: assumptions.initial_portfolio },
    { label: 'Annual Contribution (Pre-Retirement)', value: assumptions.annual_contribution },
    { label: 'Annual Spending (Post-Retirement)', value: assumptions.annual_spending },
    { label: 'Expected Annual Return', value: assumptions.expected_return },
    { label: 'Expected Inflation Rate', value: assumptions.inflation_rate },
    { label: 'Asset Allocation', value: assumptions.allocation },
  ];

  return (
    <section className="salem-section">
      <h2>Planning Assumptions</h2>
      
      <div className="salem-card">
        <p style={{ marginBottom: 'var(--salem-spacing-lg)', color: 'var(--salem-gray-700)' }}>
          This analysis is based on the following assumptions. Changes to these inputs may materially 
          affect the projected outcomes.
        </p>

        <table className="salem-table">
          <tbody>
            {assumptionRows.map((row, index) => (
              <tr key={index}>
                <td style={{ 
                  fontWeight: 500, 
                  width: '60%',
                  color: 'var(--salem-gray-700)'
                }}>
                  {row.label}
                </td>
                <td style={{ 
                  fontFamily: 'var(--salem-font-mono)',
                  fontSize: 'var(--salem-text-lg)',
                  color: 'var(--salem-navy-primary)'
                }}>
                  {row.value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};
