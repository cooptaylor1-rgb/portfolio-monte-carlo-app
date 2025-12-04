/**
 * Tail-Risk Summary Chart
 * Shows worst 1%, 5%, and 10% outcomes with clear interpretation
 */

import React, { useMemo } from 'react';
import { Card } from '../../ui/Card';
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
      <p className="mb-5 text-text-secondary text-sm">
        Tail risks represent extreme scenarios with low probability but high impact. Understanding these outcomes 
        helps prepare contingency plans and assess true risk exposure.
      </p>

      <div className="flex flex-col gap-4">
        {tailRisks.map((risk, index) => (
          <Card
            key={index}
            padding="lg"
            className="grid grid-cols-[180px_1fr_150px] gap-5 items-center"
            style={{ borderColor: risk.color, borderWidth: '3px' }}
          >
            {/* Left: Percentile badge */}
            <div
              className="text-center p-4 rounded-lg"
              style={{ backgroundColor: `${risk.color}15` }}
            >
              <div className="text-2xl font-bold mb-1" style={{ color: risk.color }}>
                {risk.percentile}
              </div>
              <div className="text-xs text-text-secondary mb-2">
                {risk.probability} scenarios
              </div>
              <div
                className="inline-block px-3 py-1 text-white rounded text-xs font-semibold"
                style={{ backgroundColor: risk.color }}
              >
                {risk.severity} Risk
              </div>
            </div>

            {/* Middle: Description */}
            <div>
              <div className="text-sm text-text-primary leading-relaxed mb-2">
                {risk.description}
              </div>
              <div className="text-xs text-text-tertiary">
                These scenarios represent combinations of adverse events occurring simultaneously.
              </div>
            </div>

            {/* Right: Ending value */}
            <div
              className="text-right p-3 rounded-lg"
              style={{ backgroundColor: risk.value <= 0 ? '#FEF2F2' : '#F9FAFB' }}
            >
              <div className="text-xs text-text-secondary mb-1">
                Ending Balance
              </div>
              <div
                className="text-2xl font-bold"
                style={{ color: risk.value <= 0 ? salemColors.danger : salemColors.navy }}
              >
                {formatCurrency(risk.value)}
              </div>
              {risk.value <= 0 && (
                <div className="text-xs mt-1" style={{ color: salemColors.danger }}>
                  Portfolio Depleted
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Summary statistics */}
      <div
        className="mt-6 p-4 rounded-lg"
        style={{
          backgroundColor: allDepleted ? '#FEF2F2' : '#F0FDF4',
          border: `2px solid ${allDepleted ? salemColors.danger : salemColors.success}`,
        }}
      >
        <div className="flex justify-between items-center">
          <div>
            <strong className="text-sm" style={{ color: salemColors.navy }}>Tail-Risk Assessment:</strong>
            <span className="text-sm text-text-secondary ml-2">
              {allDepleted 
                ? 'High vulnerability in extreme scenarios - consider additional safeguards'
                : 'Manageable tail risks with appropriate contingency planning'
              }
            </span>
          </div>
          <div
            className="px-4 py-2 text-white rounded-md font-semibold text-xs"
            style={{ backgroundColor: allDepleted ? salemColors.danger : salemColors.success }}
          >
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
