/**
 * Shared TypeScript types for Monte Carlo analysis components
 */

export interface SimulationStats {
  Month: number;
  SuccessPct: number;
  Median: number;
  P10: number;
  P25: number;
  P75: number;
  P90: number;
  Mean?: number;
  StdDev?: number;
}

export interface LongevityMilestone {
  age: number;
  yearsFromNow: number;
  successProbability: number;
  medianBalance: number;
  percentile10: number;
  depletionRisk: number;
  riskLevel: RiskAssessment;
}

export interface AnnualRiskData {
  year: number;
  age: number;
  successProbability: number;
  cumulativeRisk: number;
  annualRisk: number;
}

export interface RiskAssessment {
  level: 'Low' | 'Moderate' | 'High' | 'Very High';
  color: string;
  description: string;
}

export interface RiskSummary {
  peakRiskYear: number | null;
  peakRiskValue: number;
  risk10Year: number;
  risk20Year: number;
  risk30Year: number;
  overallAssessment: string;
}

export type RiskLevel = 'Low' | 'Moderate' | 'High' | 'Very High';
