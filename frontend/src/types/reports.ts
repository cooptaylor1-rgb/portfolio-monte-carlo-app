/**
 * TypeScript interfaces matching backend Pydantic models for Salem-branded reports
 */

export interface KeyMetric {
  label: string;
  value: string;
  tooltip?: string;
  variant?: 'success' | 'warning' | 'danger' | 'neutral';
}

export interface ReportSummary {
  client_name: string;
  scenario_name: string;
  as_of_date: string;
  advisor_name: string;
  firm_name: string;
  key_metrics: KeyMetric[];
}

export interface NarrativeBlock {
  key_findings: string[];
  key_risks: string[];
  recommendations: string[];
}

export interface PercentilePathPoint {
  year: number;
  p10: number;
  p50: number;
  p90: number;
}

export interface MonteCarloBlock {
  percentile_path: PercentilePathPoint[];
  success_probability: number;
  num_runs: number;
  horizon_years: number;
}

export interface StressMetric {
  label: string;
  base_value: string;
  stressed_value: string;
  change: string;
}

export interface StressScenarioResult {
  id: string;
  name: string;
  description: string;
  base_metrics: StressMetric[];
  stressed_metrics: StressMetric[];
}

export interface AssumptionsBlock {
  current_age: number;
  retirement_age: number;
  life_expectancy: number;
  initial_portfolio: string;
  annual_contribution: string;
  annual_spending: string;
  expected_return: string;
  inflation_rate: string;
  allocation: string;
}

export interface AppendixItem {
  title: string;
  content: string[];
}

export interface ReportData {
  summary: ReportSummary;
  narrative: NarrativeBlock;
  monte_carlo: MonteCarloBlock;
  stress_tests: StressScenarioResult[];
  assumptions: AssumptionsBlock;
  appendix: AppendixItem[];
}
