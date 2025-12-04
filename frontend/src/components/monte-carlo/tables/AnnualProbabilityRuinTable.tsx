/**
 * Annual Probability of Ruin Table
 * Pro-grade dark theme with accurate risk calculations and conservative messaging
 */

import React, { useMemo } from 'react';
import {
  salemColors,
  formatPercent,
} from '../visualizations/chartUtils';
import {
  EmptyState,
  SummaryCard,
  AnalysisSection,
  AssessmentCallout,
} from '../shared/AnalysisComponents';
import {
  processAnnualRiskData,
  calculateRiskSummary,
  generateRuinTakeaway,
} from '../shared/analysisUtils';
import type { SimulationStats } from '../shared/types';

interface AnnualProbabilityRuinTableProps {
  stats: SimulationStats[];
  currentAge: number;
  showTakeaway?: boolean;
}

export const AnnualProbabilityRuinTable: React.FC<AnnualProbabilityRuinTableProps> = ({
  stats,
  currentAge,
  showTakeaway = true,
}) => {
  // Process annual risk data (up to 30 years)
  const annualData = useMemo(() => 
    processAnnualRiskData(stats, currentAge, 30),
    [stats, currentAge]
  );

  const riskSummary = useMemo(() => 
    calculateRiskSummary(annualData),
    [annualData]
  );

  const takeawayMessage = useMemo(() => 
    generateRuinTakeaway(annualData, riskSummary),
    [annualData, riskSummary]
  );

  // Determine overall risk status
  const overallRisk = useMemo(() => {
    if (annualData.length === 0) return 'info';
    if (riskSummary.risk30Year < 0.10) return 'success';
    if (riskSummary.risk30Year < 0.25) return 'warning';
    return 'danger';
  }, [annualData, riskSummary]);

  // Empty state handling
  if (!stats || stats.length === 0) {
    return (
      <AnalysisSection
        title="Annual Probability of Ruin"
        subtitle="Year-by-year failure probability analysis"
      >
        <EmptyState
          title="Simulation Required"
          message="Run a Monte Carlo projection to unlock probability-of-ruin insights. This analysis identifies critical periods where portfolio is most vulnerable."
        />
      </AnalysisSection>
    );
  }

  if (annualData.length === 0) {
    return (
      <AnalysisSection
        title="Annual Probability of Ruin"
        subtitle="Year-by-year failure probability analysis"
      >
        <EmptyState
          title="Insufficient Data"
          message="We couldn't compute this metric. Please re-run the analysis or adjust inputs."
        />
      </AnalysisSection>
    );
  }

  // Split data into 3 columns for better readability
  const column1 = annualData.slice(0, 10);
  const column2 = annualData.slice(10, 20);
  const column3 = annualData.slice(20, 30);

  return (
    <AnalysisSection
      title="Annual Probability of Ruin"
      subtitle="Year-by-year analysis showing cumulative and marginal failure probabilities. Helps identify critical periods where portfolio is most vulnerable."
    >
      {/* Summary metrics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <SummaryCard
          label="Peak Risk Year"
          value={riskSummary.peakRiskYear ? `Year ${riskSummary.peakRiskYear}` : 'N/A'}
          sublabel={riskSummary.peakRiskYear ? formatPercent(riskSummary.peakRiskValue) + ' annual risk' : 'No data'}
          variant="primary"
        />
        <SummaryCard
          label="10-Year Risk"
          value={formatPercent(riskSummary.risk10Year)}
          sublabel={`Age ${currentAge + 10}`}
          variant={riskSummary.risk10Year < 0.10 ? 'success' : 'warning'}
        />
        <SummaryCard
          label="20-Year Risk"
          value={formatPercent(riskSummary.risk20Year)}
          sublabel={`Age ${currentAge + 20}`}
          variant={riskSummary.risk20Year < 0.15 ? 'success' : 'warning'}
        />
        <SummaryCard
          label="30-Year Risk"
          value={formatPercent(riskSummary.risk30Year)}
          sublabel={`Age ${currentAge + 30}`}
          variant={riskSummary.risk30Year < 0.20 ? 'success' : 'danger'}
        />
      </div>

      {/* Three-column table layout */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[column1, column2, column3].map((columnData, colIndex) => (
          <div 
            key={colIndex} 
            className="rounded-lg overflow-hidden border"
            style={{ borderColor: 'rgba(71, 85, 105, 0.3)' }}
          >
            <table className="w-full">
              <thead>
                <tr 
                  className="text-white text-xs font-semibold uppercase tracking-wide"
                  style={{ backgroundColor: salemColors.navy }}
                >
                  <th className="px-3 py-2.5 text-left">Year</th>
                  <th className="px-3 py-2.5 text-center">Age</th>
                  <th className="px-3 py-2.5 text-right">Cumulative Risk</th>
                  <th className="px-3 py-2.5 text-right">Annual Risk</th>
                </tr>
              </thead>
              <tbody>
                {columnData.map((row, index) => {
                  if (!row) return null;
                  const isEven = index % 2 === 0;
                  const isHighRisk = row.annualRisk > 0.03;

                  return (
                    <tr
                      key={row.year}
                      className="transition-colors hover:bg-opacity-70"
                      style={{
                        backgroundColor: isHighRisk 
                          ? 'rgba(153, 27, 27, 0.15)'
                          : isEven 
                            ? 'rgba(30, 41, 59, 0.3)' 
                            : 'rgba(15, 23, 42, 0.3)',
                      }}
                    >
                      <td className="px-3 py-2.5 font-semibold text-sm" style={{ color: salemColors.gold }}>
                        {row.year}
                      </td>
                      <td className="px-3 py-2.5 text-center text-sm" style={{ color: salemColors.mediumGray }}>
                        {row.age}
                      </td>
                      <td
                        className="px-3 py-2.5 text-right text-sm"
                        style={{
                          color: row.cumulativeRisk > 0.25 ? salemColors.danger : salemColors.white,
                          fontWeight: row.cumulativeRisk > 0.25 ? 600 : 400,
                        }}
                      >
                        {formatPercent(row.cumulativeRisk)}
                      </td>
                      <td
                        className="px-3 py-2.5 text-right text-sm"
                        style={{
                          color: isHighRisk ? salemColors.danger : salemColors.mediumGray,
                          fontWeight: isHighRisk ? 600 : 400,
                        }}
                      >
                        {formatPercent(row.annualRisk)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      {/* Assessment callout */}
      <div className="mb-6">
        <AssessmentCallout
          title="Risk Assessment"
          message={riskSummary.overallAssessment}
          variant={overallRisk}
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      {/* Key takeaway */}
      {showTakeaway && (
        <div 
          className="p-4 rounded-lg border-l-4"
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

export default AnnualProbabilityRuinTable;
