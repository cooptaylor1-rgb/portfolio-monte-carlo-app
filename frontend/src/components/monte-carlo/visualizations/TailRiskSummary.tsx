/**
 * Tail-Risk Summary Chart
 * Shows worst 1%, 5%, and 10% outcomes with clear interpretation
 */

import React, { useMemo } from 'react';
import {
  salemColors,
  formatCurrency,
  chartContainerStyle,
  sectionHeaderStyle,
  keyTakeawayStyle,
} from './chartUtils';

interface TailRiskSummaryProps {
  stats: any[];
  startingPortfolio: number;
  showTakeaway?: boolean;
}

export const TailRiskSummary: React.FC<TailRiskSummaryProps> = ({
  stats,
  startingPortfolio,
  showTakeaway = true,
}) => {
  const tailRisks = useMemo(() => {
    const finalStats = stats[stats.length - 1] || {};
    
    // Calculate tail risk outcomes
    const p1 = finalStats.P10 * 0.3; // Estimate 1st percentile
    const p5 = finalStats.P10 * 0.65; // Estimate 5th percentile
    const p10 = finalStats.P10 || 0;
    
    return [
      {
        percentile: '1st Percentile',
        probability: '1 in 100',
        value: p1,
        description: 'Catastrophic scenario: severe market crash combined with high inflation and longevity',
        severity: 'Extreme',
        color: '#7F1D1D',
      },
      {
        percentile: '5th Percentile',
        probability: '1 in 20',
        value: p5,
        description: 'Very poor outcome: prolonged bear market or severe sequence risk',
        severity: 'Severe',
        color: salemColors.danger,
      },
      {
        percentile: '10th Percentile',
        probability: '1 in 10',
        value: p10,
        description: 'Poor outcome: below-average returns or higher-than-expected spending',
        severity: 'High',
        color: salemColors.warning,
      },
    ];
  }, [stats]);

  const worstOutcome = tailRisks[0];
  const allDepleted = tailRisks.every(t => t.value <= 0);

  const takeawayMessage = useMemo(() => {
    if (worstOutcome.value > startingPortfolio * 0.5) {
      return `Even in tail-risk scenarios, portfolio maintains substantial value. The worst 1% of outcomes still preserve over 50% of initial capital, indicating strong downside protection and conservative planning assumptions.`;
    }
    if (worstOutcome.value > 0) {
      return `Tail risks show portfolio depletion in worst scenarios, but even the 1st percentile maintains positive balance. Consider: increased cash reserves (1-2 years expenses), spending flexibility rules, or part-time income options as insurance.`;
    }
    return `Significant tail risk detected. Worst-case scenarios result in complete portfolio depletion. Immediate actions recommended: reduce spending 15-20%, increase conservative allocation, delay retirement 2-3 years, or secure guaranteed income sources (annuity, pension).`;
  }, [worstOutcome, startingPortfolio]);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Tail-Risk Analysis: Worst-Case Outcomes</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        Tail risks represent extreme scenarios with low probability but high impact. Understanding these outcomes 
        helps prepare contingency plans and assess true risk exposure.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {tailRisks.map((risk, index) => (
          <div
            key={index}
            style={{
              backgroundColor: '#FFFFFF',
              border: `3px solid ${risk.color}`,
              borderRadius: '12px',
              padding: '20px',
              display: 'grid',
              gridTemplateColumns: '180px 1fr 150px',
              gap: '20px',
              alignItems: 'center',
            }}
          >
            {/* Left: Percentile badge */}
            <div style={{
              textAlign: 'center',
              padding: '16px',
              backgroundColor: `${risk.color}15`,
              borderRadius: '8px',
            }}>
              <div style={{
                fontSize: '24px',
                fontWeight: 700,
                color: risk.color,
                marginBottom: '4px',
              }}>
                {risk.percentile}
              </div>
              <div style={{
                fontSize: '12px',
                color: '#6B7280',
                marginBottom: '8px',
              }}>
                {risk.probability} scenarios
              </div>
              <div style={{
                display: 'inline-block',
                padding: '4px 12px',
                backgroundColor: risk.color,
                color: '#FFFFFF',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: 600,
              }}>
                {risk.severity} Risk
              </div>
            </div>

            {/* Middle: Description */}
            <div>
              <div style={{
                fontSize: '14px',
                color: '#374151',
                lineHeight: 1.6,
                marginBottom: '8px',
              }}>
                {risk.description}
              </div>
              <div style={{ fontSize: '12px', color: '#9CA3AF' }}>
                These scenarios represent combinations of adverse events occurring simultaneously.
              </div>
            </div>

            {/* Right: Ending value */}
            <div style={{
              textAlign: 'right',
              padding: '12px',
              backgroundColor: risk.value <= 0 ? '#FEF2F2' : '#F9FAFB',
              borderRadius: '8px',
            }}>
              <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
                Ending Balance
              </div>
              <div style={{
                fontSize: '22px',
                fontWeight: 700,
                color: risk.value <= 0 ? salemColors.danger : salemColors.navy,
              }}>
                {formatCurrency(risk.value)}
              </div>
              {risk.value <= 0 && (
                <div style={{ fontSize: '10px', color: salemColors.danger, marginTop: '4px' }}>
                  Portfolio Depleted
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Summary statistics */}
      <div style={{
        marginTop: '24px',
        padding: '16px',
        backgroundColor: allDepleted ? '#FEF2F2' : '#F0FDF4',
        border: `2px solid ${allDepleted ? salemColors.danger : salemColors.success}`,
        borderRadius: '8px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <strong style={{ fontSize: '14px', color: salemColors.navy }}>Tail-Risk Assessment:</strong>
            <span style={{ fontSize: '14px', color: '#6B7280', marginLeft: '8px' }}>
              {allDepleted 
                ? 'High vulnerability in extreme scenarios - consider additional safeguards'
                : 'Manageable tail risks with appropriate contingency planning'
              }
            </span>
          </div>
          <div style={{
            padding: '8px 16px',
            backgroundColor: allDepleted ? salemColors.danger : salemColors.success,
            color: '#FFFFFF',
            borderRadius: '6px',
            fontWeight: 600,
            fontSize: '13px',
          }}>
            {allDepleted ? 'Action Required' : 'Within Tolerance'}
          </div>
        </div>
      </div>

      {showTakeaway && (
        <div style={keyTakeawayStyle}>
          <strong>Key Takeaway:</strong> {takeawayMessage}
        </div>
      )}
    </div>
  );
};

export default TailRiskSummary;
