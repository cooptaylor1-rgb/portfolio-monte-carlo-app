/**
 * Analysis utility functions
 * Conservative risk assessment and data processing
 */

import { SimulationStats, LongevityMilestone, AnnualRiskData, RiskAssessment, RiskSummary } from './types';
import { salemColors } from '../visualizations/chartUtils';

/**
 * Assess risk level based on success probability
 * Uses conservative thresholds appropriate for wealth management
 */
export function assessRiskLevel(successProbability: number): RiskAssessment {
  if (successProbability >= 0.90) {
    return {
      level: 'Low',
      color: salemColors.success,
      description: 'Strong resilience with minimal risk of portfolio depletion',
    };
  }
  if (successProbability >= 0.75) {
    return {
      level: 'Moderate',
      color: salemColors.warning,
      description: 'Solid fundamentals but monitor conditions and consider safeguards',
    };
  }
  if (successProbability >= 0.60) {
    return {
      level: 'High',
      color: salemColors.danger,
      description: 'Heightened risk requiring strategic adjustments',
    };
  }
  return {
    level: 'Very High',
    color: '#DC2626',
    description: 'Significant vulnerability requiring immediate action',
  };
}

/**
 * Process longevity milestones from simulation data
 */
export function processLongevityData(
  stats: SimulationStats[],
  currentAge: number,
  milestones: number[] = [70, 75, 80, 85, 90, 95, 100]
): LongevityMilestone[] {
  return milestones
    .map(age => {
      const yearsFromNow = age - currentAge;
      const monthIndex = yearsFromNow * 12;

      // Skip if out of bounds or in the past
      if (monthIndex < 0 || monthIndex >= stats.length) {
        return null;
      }

      const stat = stats[monthIndex];

      // Skip if critical data is missing
      if (
        stat?.SuccessPct === undefined || 
        stat?.SuccessPct === null ||
        stat?.Median === undefined ||
        stat?.P10 === undefined
      ) {
        return null;
      }

      const successProbability = stat.SuccessPct / 100;

      return {
        age,
        yearsFromNow,
        successProbability,
        medianBalance: stat.Median,
        percentile10: stat.P10,
        depletionRisk: 1 - successProbability,
        riskLevel: assessRiskLevel(successProbability),
      };
    })
    .filter((item): item is LongevityMilestone => item !== null);
}

/**
 * Generate conservative longevity assessment message
 */
export function generateLongevityAssessment(data: LongevityMilestone[]): string {
  if (data.length === 0) {
    return 'Insufficient data to assess longevity resilience. Run a Monte Carlo projection.';
  }

  const age100 = data.find(d => d.age === 100);
  const age95 = data.find(d => d.age === 95);
  const age90 = data.find(d => d.age === 90);

  // Check best available milestone
  const latestMilestone = age100 || age95 || age90 || data[data.length - 1];

  if (latestMilestone.successProbability > 0.90) {
    return `Strong resilience across all age milestones through age ${latestMilestone.age}`;
  }

  if (latestMilestone.successProbability > 0.75) {
    return `Solid but monitor: ${(latestMilestone.successProbability * 100).toFixed(1)}% success probability at age ${latestMilestone.age}`;
  }

  // Find first stress point
  const stressPoint = data.find(d => d.successProbability < 0.85);
  if (stressPoint) {
    return `First stress point at age ${stressPoint.age} with ${(stressPoint.successProbability * 100).toFixed(1)}% success probability`;
  }

  return `Conservative planning through age ${latestMilestone.age}`;
}

/**
 * Generate detailed longevity takeaway
 */
export function generateLongevityTakeaway(data: LongevityMilestone[]): string {
  if (data.length === 0) {
    return 'A simulation has not been run yet. Run a projection to unlock longevity insights.';
  }

  const latestAge = data[data.length - 1].age;
  const latestSuccess = data[data.length - 1].successProbability;

  if (latestSuccess > 0.90) {
    return `Portfolio demonstrates strong longevity resilience across all age milestones. Even at age ${latestAge}, success probability remains above 90%. This indicates conservative planning assumptions and robust portfolio sustainability. Consider whether spending can be increased to enhance lifestyle without compromising security.`;
  }

  const criticalAge = data.find(d => d.successProbability < 0.85);

  if (!criticalAge) {
    return `Portfolio performs well through age ${latestAge} with ${(latestSuccess * 100).toFixed(1)}% success probability. Demonstrates solid fundamentals with appropriate risk management for longevity planning.`;
  }

  if (criticalAge.age >= 90) {
    return `Portfolio performs well through typical life expectancy but shows stress at advanced ages (${criticalAge.age}+). Success probability of ${(criticalAge.successProbability * 100).toFixed(1)}% at age ${criticalAge.age}. For extreme longevity planning, consider partial annuitization for guaranteed lifetime income, or reduced spending starting age 85.`;
  }

  return `Longevity stress appears at age ${criticalAge.age} with ${(criticalAge.successProbability * 100).toFixed(1)}% success probability. This suggests plan vulnerability if client lives longer than average. Recommended actions: reduce annual spending 10-15%, increase conservative allocation after age ${criticalAge.age - 5}, or purchase longevity insurance (deferred annuity starting age 80-85).`;
}

/**
 * Process annual probability of ruin data
 */
export function processAnnualRiskData(
  stats: SimulationStats[],
  currentAge: number,
  maxYears: number = 30
): AnnualRiskData[] {
  return stats
    .filter((_, idx) => idx % 12 === 0) // Annual data points
    .slice(0, maxYears + 1)
    .map((stat, yearIndex) => {
      // Skip if SuccessPct is missing
      if (stat?.SuccessPct === undefined || stat?.SuccessPct === null) {
        return null;
      }

      const successProbability = stat.SuccessPct / 100;
      const cumulativeRisk = 1 - successProbability;

      // Calculate marginal annual risk (new failures this year)
      const prevStat = yearIndex > 0 ? stats[(yearIndex - 1) * 12] : stat;
      const prevSuccess = (prevStat?.SuccessPct !== undefined && prevStat?.SuccessPct !== null)
        ? prevStat.SuccessPct / 100
        : successProbability;
      
      const annualRisk = Math.max(0, cumulativeRisk - (1 - prevSuccess));

      return {
        year: yearIndex + 1,
        age: currentAge + yearIndex,
        successProbability,
        cumulativeRisk,
        annualRisk,
      };
    })
    .filter((item): item is AnnualRiskData => item !== null);
}

/**
 * Calculate risk summary metrics
 */
export function calculateRiskSummary(data: AnnualRiskData[]): RiskSummary {
  if (data.length === 0) {
    return {
      peakRiskYear: null,
      peakRiskValue: 0,
      risk10Year: 0,
      risk20Year: 0,
      risk30Year: 0,
      overallAssessment: 'Simulation required',
    };
  }

  // Find peak annual risk year
  const peakRisk = data.reduce((max, curr) => 
    curr.annualRisk > max.annualRisk ? curr : max
  , data[0]);

  const risk10 = data[9]?.cumulativeRisk ?? 0;
  const risk20 = data[19]?.cumulativeRisk ?? 0;
  const risk30 = data[29]?.cumulativeRisk ?? 0;

  // Overall assessment
  let assessment: string;
  if (risk30 < 0.05) {
    assessment = 'No material risk detected over modeled timeframe';
  } else if (risk30 < 0.15) {
    assessment = 'Low risk with strong fundamentals';
  } else if (risk30 < 0.30) {
    assessment = 'Moderate risk - monitor conditions';
  } else {
    assessment = 'Heightened risk - strategic adjustments recommended';
  }

  return {
    peakRiskYear: peakRisk.year,
    peakRiskValue: peakRisk.annualRisk,
    risk10Year: risk10,
    risk20Year: risk20,
    risk30Year: risk30,
    overallAssessment: assessment,
  };
}

/**
 * Generate probability of ruin takeaway
 */
export function generateRuinTakeaway(data: AnnualRiskData[], summary: RiskSummary): string {
  if (data.length === 0) {
    return 'Insufficient data to calculate risk analysis. Please run a simulation first.';
  }

  if (summary.peakRiskValue < 0.02) {
    return `Low and stable failure risk throughout planning period. Peak annual risk of ${(summary.peakRiskValue * 100).toFixed(1)}% occurs in year ${summary.peakRiskYear}. Gradual risk accumulation indicates well-balanced plan without acute stress periods. Portfolio positioned for sustainable multi-decade withdrawals.`;
  }

  if (summary.peakRiskYear && summary.peakRiskYear <= 10) {
    const peakAge = data[0].age + summary.peakRiskYear - 1;
    return `Sequence-of-returns risk detected. Peak failure probability of ${(summary.peakRiskValue * 100).toFixed(1)}% in year ${summary.peakRiskYear} (age ${peakAge}) indicates early retirement vulnerability. First decade critical: poor market returns could significantly impact long-term success. Mitigation strategies: maintain 2-3 years cash reserves, flexible spending framework, or delay retirement 1-2 years for additional buffer.`;
  }

  if (summary.peakRiskYear) {
    const peakAge = data[0].age + summary.peakRiskYear - 1;
    return `Elevated risk in mid-to-late retirement years. Peak annual risk of ${(summary.peakRiskValue * 100).toFixed(1)}% at year ${summary.peakRiskYear} (age ${peakAge}) suggests longevity or spending pressure. Consider: gradual spending reduction (5-10% after age ${peakAge - 5}), increased fixed income allocation, or deferred annuity starting age ${Math.min(peakAge, 85)}.`;
  }

  return `Risk analysis complete. Review detailed metrics for planning adjustments.`;
}
