/**
 * Longevity Stress Table
 * Shows portfolio survival at different ages
 */

import React, { useMemo } from 'react';
import {
  salemColors,
  formatCurrency,
  formatPercent,
  getRiskLevel,
  chartContainerStyle,
  sectionHeaderStyle,
  keyTakeawayStyle,
} from '../visualizations/chartUtils';

interface LongevityStressTableProps {
  stats: any[];
  currentAge: number;
  showTakeaway?: boolean;
}

export const LongevityStressTable: React.FC<LongevityStressTableProps> = ({
  stats,
  currentAge,
  showTakeaway = true,
}) => {
  const longevityData = useMemo(() => {
    const milestones = [70, 75, 80, 85, 90, 95, 100];
    
    return milestones.map(age => {
      const yearsFromNow = age - currentAge;
      const monthIndex = yearsFromNow * 12;
      
      if (monthIndex < 0 || monthIndex >= stats.length) {
        return null;
      }
      
      const stat = stats[monthIndex] || stats[stats.length - 1];
      const successProb = stat.SuccessPct / 100;
      const median = stat.Median;
      const p10 = stat.P10;
      const depletionRisk = 1 - successProb;
      
      return {
        age,
        yearsFromNow,
        successProb,
        median,
        p10,
        depletionRisk,
        riskLevel: getRiskLevel(successProb),
      };
    }).filter(Boolean);
  }, [stats, currentAge]);

  const criticalAge = longevityData.find(d => d!.successProb < 0.85);

  const takeawayMessage = useMemo(() => {
    if (!criticalAge) {
      return `Portfolio demonstrates strong longevity resilience across all age milestones. Even at age 100, success probability remains above 85%. This indicates conservative planning assumptions and robust portfolio sustainability. Consider whether spending can be increased to enhance lifestyle without compromising security.`;
    }
    if (criticalAge.age >= 90) {
      return `Portfolio performs well through typical life expectancy but shows stress at advanced ages (${criticalAge.age}+). Success probability drops to ${formatPercent(criticalAge.successProb)} at age ${criticalAge.age}. For extreme longevity planning, consider: partial annuitization for guaranteed lifetime income, or reduced spending starting age 85.`;
    }
    return `Longevity stress appears at age ${criticalAge.age} with ${formatPercent(criticalAge.successProb)} success probability. This suggests plan vulnerability if client lives longer than average. Immediate actions recommended: reduce annual spending 10-15%, increase conservative allocation after age ${criticalAge.age - 5}, or purchase longevity insurance (deferred annuity starting age 80-85).`;
  }, [criticalAge]);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Longevity Stress Analysis</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        This table shows portfolio sustainability at key age milestones. Understanding longevity risk 
        helps identify when additional safeguards may be needed.
      </p>

      <table style={{
        width: '100%',
        borderCollapse: 'collapse',
        fontSize: '13px',
      }}>
        <thead>
          <tr style={{ backgroundColor: salemColors.navy, color: '#FFFFFF' }}>
            <th style={{ padding: '12px', textAlign: 'left', borderRadius: '8px 0 0 0' }}>Age</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Years from Now</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Success Probability</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Median Balance</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>10th Percentile</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Depletion Risk</th>
            <th style={{ padding: '12px', textAlign: 'center', borderRadius: '0 8px 0 0' }}>Risk Level</th>
          </tr>
        </thead>
        <tbody>
          {longevityData.map((row, index) => {
            const bgColor = index % 2 === 0 ? '#F9FAFB' : '#FFFFFF';
            const isLast = index === longevityData.length - 1;
            
            return (
              <tr key={row!.age} style={{ backgroundColor: bgColor }}>
                <td style={{
                  padding: '12px',
                  fontWeight: 600,
                  color: salemColors.navy,
                  borderRadius: isLast ? '0 0 0 8px' : '0',
                }}>
                  {row!.age}
                </td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#6B7280' }}>
                  {row!.yearsFromNow}
                </td>
                <td style={{
                  padding: '12px',
                  textAlign: 'right',
                  fontWeight: 600,
                  color: row!.successProb >= 0.85 ? salemColors.success : 
                         row!.successProb >= 0.75 ? salemColors.warning : salemColors.danger,
                }}>
                  {formatPercent(row!.successProb)}
                </td>
                <td style={{ padding: '12px', textAlign: 'right', color: salemColors.navy }}>
                  {formatCurrency(row!.median)}
                </td>
                <td style={{ padding: '12px', textAlign: 'right', color: '#6B7280' }}>
                  {formatCurrency(row!.p10)}
                </td>
                <td style={{
                  padding: '12px',
                  textAlign: 'right',
                  color: row!.depletionRisk <= 0.15 ? '#6B7280' : salemColors.danger,
                }}>
                  {formatPercent(row!.depletionRisk)}
                </td>
                <td style={{
                  padding: '12px',
                  textAlign: 'center',
                  borderRadius: isLast ? '0 0 8px 0' : '0',
                }}>
                  <span style={{
                    padding: '4px 12px',
                    backgroundColor: row!.riskLevel.level === 'Low' ? salemColors.success :
                                   row!.riskLevel.level === 'Moderate' ? salemColors.warning : salemColors.danger,
                    color: '#FFFFFF',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: 600,
                  }}>
                    {row!.riskLevel.level}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Summary callout */}
      <div style={{
        marginTop: '20px',
        padding: '16px',
        backgroundColor: criticalAge && criticalAge.age < 90 ? '#FEF2F2' : '#F0FDF4',
        border: `2px solid ${criticalAge && criticalAge.age < 90 ? salemColors.danger : salemColors.success}`,
        borderRadius: '8px',
      }}>
        <div style={{ fontSize: '14px', color: salemColors.navy }}>
          <strong>Longevity Assessment: </strong>
          {criticalAge ? (
            <>First stress point at age <strong>{criticalAge.age}</strong> ({formatPercent(criticalAge.successProb)} success)</>
          ) : (
            <>Strong resilience across all age milestones through age 100</>
          )}
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

export default LongevityStressTable;
