/**
 * Longevity Stress Analysis Table
 * Pro-grade dark theme with accurate data and conservative messaging
 */

import React, { useMemo } from 'react';
import {
  salemColors,
  formatCurrency,
  formatPercent,
} from '../visualizations/chartUtils';
import {
  EmptyState,
  SummaryCard,
  RiskBadge,
  AnalysisSection,
  AssessmentCallout,
} from '../shared/AnalysisComponents';
import {
  processLongevityData,
  generateLongevityAssessment,
  generateLongevityTakeaway,
} from '../shared/analysisUtils';
import type { SimulationStats } from '../shared/types';

interface LongevityStressTableProps {
  stats: SimulationStats[];
  currentAge: number;
  showTakeaway?: boolean;
}

export const LongevityStressTable: React.FC<LongevityStressTableProps> = ({
  stats,
  currentAge,
  showTakeaway = true,
}) => {
  // Process longevity milestones (70, 75, 80, 85, 90, 95, 100)
  const longevityData = useMemo(() => 
    processLongevityData(stats, currentAge),
    [stats, currentAge]
  );

  const assessmentMessage = useMemo(() => 
    generateLongevityAssessment(longevityData),
    [longevityData]
  );

  const takeawayMessage = useMemo(() => 
    generateLongevityTakeaway(longevityData),
    [longevityData]
  );

  // Determine overall risk status for callout variant
  const overallRisk = useMemo(() => {
    if (longevityData.length === 0) return 'info';
    const latestSuccess = longevityData[longevityData.length - 1].successProbability;
    if (latestSuccess > 0.90) return 'success';
    if (latestSuccess > 0.75) return 'warning';
    return 'danger';
  }, [longevityData]);

  // Empty state handling
  if (!stats || stats.length === 0) {
    return (
      <AnalysisSection
        title="Longevity Stress Analysis"
        subtitle="Portfolio sustainability at key age milestones"
      >
        <EmptyState
          title="Simulation Required"
          message="Run a Monte Carlo projection to view longevity and risk metrics. This analysis shows portfolio sustainability across critical age milestones."
        />
      </AnalysisSection>
    );
  }

  if (longevityData.length === 0) {
    return (
      <AnalysisSection
        title="Longevity Stress Analysis"
        subtitle="Portfolio sustainability at key age milestones"
      >
        <EmptyState
          title="Insufficient Data"
          message="We couldn't compute longevity metrics. Please re-run the analysis with valid inputs or adjust the planning horizon."
        />
      </AnalysisSection>
    );
  }

  return (
    <AnalysisSection
      title="Longevity Stress Analysis"
      subtitle="Portfolio sustainability at key age milestones. Understanding longevity risk helps identify when additional safeguards may be needed."
    >
      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {longevityData.slice(-3).reverse().map((milestone) => (
          <SummaryCard
            key={milestone.age}
            label={`Age ${milestone.age}`}
            value={formatPercent(milestone.successProbability)}
            sublabel={`${milestone.yearsFromNow} years from now`}
            variant={
              milestone.successProbability > 0.90 ? 'success' :
              milestone.successProbability > 0.75 ? 'warning' :
              'danger'
            }
          />
        ))}
      </div>

      {/* Data table */}
      <div className="rounded-lg overflow-hidden border" style={{ borderColor: 'rgba(71, 85, 105, 0.3)' }}>
        <table className="w-full">
          <thead>
            <tr 
              className="text-white text-sm font-semibold uppercase tracking-wide"
              style={{ backgroundColor: salemColors.navy }}
            >
              <th className="px-4 py-3 text-left">Age</th>
              <th className="px-4 py-3 text-right">Years from Now</th>
              <th className="px-4 py-3 text-right">Success Probability</th>
              <th className="px-4 py-3 text-right">Median Balance</th>
              <th className="px-4 py-3 text-right">10th Percentile</th>
              <th className="px-4 py-3 text-right">Depletion Risk</th>
              <th className="px-4 py-3 text-center">Risk Level</th>
            </tr>
          </thead>
          <tbody>
            {longevityData.map((row, index) => {
              const isEven = index % 2 === 0;
              return (
                <tr
                  key={row.age}
                  className="transition-colors hover:bg-opacity-70"
                  style={{
                    backgroundColor: isEven ? 'rgba(30, 41, 59, 0.3)' : 'rgba(15, 23, 42, 0.3)',
                  }}
                >
                  <td className="px-4 py-3.5 font-semibold" style={{ color: salemColors.gold }}>
                    {row.age}
                  </td>
                  <td className="px-4 py-3.5 text-right text-sm" style={{ color: salemColors.mediumGray }}>
                    {row.yearsFromNow}
                  </td>
                  <td
                    className="px-4 py-3.5 text-right font-semibold"
                    style={{
                      color: row.successProbability >= 0.90 ? salemColors.success :
                             row.successProbability >= 0.75 ? salemColors.warning :
                             salemColors.danger,
                    }}
                  >
                    {formatPercent(row.successProbability)}
                  </td>
                  <td className="px-4 py-3.5 text-right font-medium" style={{ color: salemColors.white }}>
                    {formatCurrency(row.medianBalance)}
                  </td>
                  <td className="px-4 py-3.5 text-right" style={{ color: salemColors.mediumGray }}>
                    {formatCurrency(row.percentile10)}
                  </td>
                  <td
                    className="px-4 py-3.5 text-right"
                    style={{
                      color: row.depletionRisk <= 0.10 ? salemColors.mediumGray : salemColors.danger,
                    }}
                  >
                    {formatPercent(row.depletionRisk)}
                  </td>
                  <td className="px-4 py-3.5 text-center">
                    <RiskBadge level={row.riskLevel.level} size="sm" />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Assessment callout */}
      <div className="mt-6">
        <AssessmentCallout
          title="Longevity Assessment"
          message={assessmentMessage}
          variant={overallRisk}
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          }
        />
      </div>

      {/* Key takeaway */}
      {showTakeaway && (
        <div 
          className="mt-6 p-4 rounded-lg border-l-4"
          style={{
            backgroundColor: 'rgba(200, 162, 75, 0.05)',
            borderLeftColor: salemColors.gold,
          }}
        >
          <div className="text-sm leading-relaxed" style={{ color: salemColors.white }}>
            <strong className="font-semibold" style={{ color: salemColors.gold }}>Key Takeaway:</strong>{' '}
            {takeawayMessage}
          </div>
        </div>
      )}
    </AnalysisSection>
  );
};

export default LongevityStressTable;
