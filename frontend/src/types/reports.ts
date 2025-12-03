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
  p5?: number;
  p10: number;
  p25?: number;
  p50: number;
  p75?: number;
  p90: number;
  p95?: number;
}

export interface SuccessProbabilityPoint {
  year: number;
  success_probability: number;
}

export interface TerminalWealthBucket {
  bucket_label: string;
  count: number;
  min_value: number;
  max_value: number;
  percentage: number;
}

export interface CashFlowProjection {
  year: number;
  age?: number;
  beginning_balance: number;
  withdrawals: number;
  income_sources_total: number;
  taxes: number;
  investment_return: number;
  ending_balance: number;
}

export interface IncomeSourcesTimeline {
  year: number;
  social_security: number;
  pension: number;
  annuity: number;
  portfolio_withdrawals: number;
  other_income: number;
}

export interface MonteCarloBlock {
  percentile_path: PercentilePathPoint[];
  success_probability: number;
  num_runs: number;
  horizon_years: number;
  success_probability_over_time?: SuccessProbabilityPoint[];
  terminal_wealth_distribution?: TerminalWealthBucket[];
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
  base_success_probability: number;
  stressed_success_probability: number;
  impact_severity?: 'Low' | 'Moderate' | 'High' | 'Severe';
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
  cash_flow_projection?: CashFlowProjection[];
  income_timeline?: IncomeSourcesTimeline[];
}
