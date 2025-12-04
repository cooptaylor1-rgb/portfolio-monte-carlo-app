/**
 * Annual Probability of Ruin Table
 * Shows year-by-year probability of portfolio depletion
 */

import React, { useMemo } from 'react';
import {
  salemColors,
  formatPercent,
  chartContainerStyle,
  sectionHeaderStyle,
  keyTakeawayStyle,
} from '../visualizations/chartUtils';

interface AnnualProbabilityRuinTableProps {
  stats: any[];
  currentAge: number;
  showTakeaway?: boolean;
}

export const AnnualProbabilityRuinTable: React.FC<AnnualProbabilityRuinTableProps> = ({
  stats,
  currentAge,
  showTakeaway = true,
}) => {
  const annualData = useMemo(() => {
    return stats
      .filter((_, idx) => idx % 12 === 0)
      .slice(0, 31) // First 30 years
      .map((stat, yearIndex) => {
        const age = currentAge + yearIndex;
        const successProb = stat.SuccessPct / 100;
        const failureProb = 1 - successProb;
        
        // Calculate marginal failure risk (new failures this year)
        const prevStat = yearIndex > 0 ? stats[(yearIndex - 1) * 12] : stat;
        const prevFailureProb = 1 - (prevStat.SuccessPct / 100);
        const marginalRisk = Math.max(0, failureProb - prevFailureProb);
        
        return {
          year: yearIndex + 1,
          age,
          successProb,
          failureProb,
          marginalRisk,
        };
      });
  }, [stats, currentAge]);

  const peakRiskYear = annualData.reduce((max, curr) => 
    curr.marginalRisk > max.marginalRisk ? curr : max
  , annualData[0]);

  const cumulativeRisk10 = annualData[9]?.failureProb || 0;
  const cumulativeRisk20 = annualData[19]?.failureProb || 0;
  const cumulativeRisk30 = annualData[29]?.failureProb || 0;

  const takeawayMessage = useMemo(() => {
    if (peakRiskYear.marginalRisk < 0.02) {
      return `Low and stable failure risk throughout planning period. Peak annual risk of ${formatPercent(peakRiskYear.marginalRisk)} occurs in year ${peakRiskYear.year} (age ${peakRiskYear.age}). Gradual risk accumulation indicates well-balanced plan without acute stress periods. Portfolio positioned for sustainable multi-decade withdrawals.`;
    }
    if (peakRiskYear.year <= 10) {
      return `Sequence-of-returns risk detected. Peak failure probability of ${formatPercent(peakRiskYear.marginalRisk)} in year ${peakRiskYear.year} (age ${peakRiskYear.age}) indicates early retirement vulnerability. First decade critical: poor market returns could significantly impact long-term success. Mitigation strategies: maintain 2-3 years cash reserves, flexible spending framework, or delay retirement 1-2 years for additional buffer.`;
    }
    return `Elevated risk in mid-to-late retirement years. Peak annual risk of ${formatPercent(peakRiskYear.marginalRisk)} at year ${peakRiskYear.year} (age ${peakRiskYear.age}) suggests longevity or spending pressure. Consider: gradual spending reduction (5-10% after age ${peakRiskYear.age - 5}), increased fixed income allocation, or deferred annuity starting age ${Math.min(peakRiskYear.age, 85)}.`;
  }, [peakRiskYear]);

  // Split into 3 columns for better readability
  const column1 = annualData.slice(0, 10);
  const column2 = annualData.slice(10, 20);
  const column3 = annualData.slice(20, 30);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Annual Probability of Ruin</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        Year-by-year analysis showing cumulative and marginal failure probabilities. Helps identify 
        critical periods where portfolio is most vulnerable.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        {[column1, column2, column3].map((columnData, colIndex) => (
          <div key={colIndex}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '12px',
            }}>
              <thead>
                <tr style={{ backgroundColor: salemColors.navy, color: '#FFFFFF' }}>
                  <th style={{ padding: '8px', textAlign: 'left', fontSize: '11px' }}>Year</th>
                  <th style={{ padding: '8px', textAlign: 'center', fontSize: '11px' }}>Age</th>
                  <th style={{ padding: '8px', textAlign: 'right', fontSize: '11px' }}>Cumulative Risk</th>
                  <th style={{ padding: '8px', textAlign: 'right', fontSize: '11px' }}>Annual Risk</th>
                </tr>
              </thead>
              <tbody>
                {columnData.map((row, index) => {
                  const bgColor = index % 2 === 0 ? '#F9FAFB' : '#FFFFFF';
                  const isHighRisk = row.marginalRisk > 0.03;
                  
                  return (
                    <tr key={row.year} style={{ backgroundColor: isHighRisk ? '#FEF2F2' : bgColor }}>
                      <td style={{ padding: '8px', fontWeight: 600, color: salemColors.navy }}>
                        {row.year}
                      </td>
                      <td style={{ padding: '8px', textAlign: 'center', color: '#6B7280' }}>
                        {row.age}
                      </td>
                      <td style={{
                        padding: '8px',
                        textAlign: 'right',
                        color: row.failureProb > 0.2 ? salemColors.danger : '#374151',
                      }}>
                        {formatPercent(row.failureProb)}
                      </td>
                      <td style={{
                        padding: '8px',
                        textAlign: 'right',
                        fontWeight: isHighRisk ? 600 : 400,
                        color: isHighRisk ? salemColors.danger : '#6B7280',
                      }}>
                        {formatPercent(row.marginalRisk)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      {/* Key milestones */}
      <div style={{
        marginTop: '20px',
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
      }}>
        <div style={{ padding: '12px', backgroundColor: '#FEF3C7', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#92400E', marginBottom: '4px' }}>
            Peak Risk Year
          </div>
          <div style={{ fontSize: '16px', fontWeight: 600, color: salemColors.gold }}>
            Year {peakRiskYear.year}
          </div>
          <div style={{ fontSize: '10px', color: '#92400E', marginTop: '2px' }}>
            {formatPercent(peakRiskYear.marginalRisk)} annual risk
          </div>
        </div>

        <div style={{ padding: '12px', backgroundColor: '#F9FAFB', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
            10-Year Risk
          </div>
          <div style={{ fontSize: '16px', fontWeight: 600, color: salemColors.navy }}>
            {formatPercent(cumulativeRisk10)}
          </div>
          <div style={{ fontSize: '10px', color: '#6B7280', marginTop: '2px' }}>
            Age {currentAge + 10}
          </div>
        </div>

        <div style={{ padding: '12px', backgroundColor: '#F9FAFB', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
            20-Year Risk
          </div>
          <div style={{ fontSize: '16px', fontWeight: 600, color: salemColors.navy }}>
            {formatPercent(cumulativeRisk20)}
          </div>
          <div style={{ fontSize: '10px', color: '#6B7280', marginTop: '2px' }}>
            Age {currentAge + 20}
          </div>
        </div>

        <div style={{ padding: '12px', backgroundColor: '#F9FAFB', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
            30-Year Risk
          </div>
          <div style={{ fontSize: '16px', fontWeight: 600, color: salemColors.navy }}>
            {formatPercent(cumulativeRisk30)}
          </div>
          <div style={{ fontSize: '10px', color: '#6B7280', marginTop: '2px' }}>
            Age {currentAge + 30}
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

export default AnnualProbabilityRuinTable;
