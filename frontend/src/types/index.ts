/**
 * TypeScript types for the Portfolio Analysis application.
 * These match the backend Pydantic models.
 */

export interface ClientInfo {
  client_name: string;
  report_date: string;
  advisor_name: string;
  client_id: string;
  client_notes: string;
}

export interface ModelInputs {
  // Portfolio configuration
  starting_portfolio: number;
  years_to_model: number;
  current_age: number;
  horizon_age: number;
  
  // Spending parameters
  monthly_spending: number;
  inflation_annual: number;
  spending_rule: 1 | 2;
  spending_pct_annual: number;
  
  // Asset allocation
  equity_pct: number;
  fi_pct: number;
  cash_pct: number;
  
  // Return assumptions
  equity_return_annual: number;
  fi_return_annual: number;
  cash_return_annual: number;
  
  // Volatility assumptions
  equity_vol_annual: number;
  fi_vol_annual: number;
  cash_vol_annual: number;
  
  // Monte Carlo settings
  n_scenarios: number;
  
  // One-time cash flows
  one_time_cf: number;
  one_time_cf_month: number;
  
  // Tax-advantaged accounts
  taxable_pct: number;
  ira_pct: number;
  roth_pct: number;
  tax_rate: number;
  rmd_age: number;
  
  // Income sources
  social_security_monthly: number;
  ss_start_age: number;
  pension_monthly: number;
  pension_start_age: number;
  regular_income_monthly: number;
  other_income_monthly: number;
  other_income_start_age: number;
  
  // Couple planning
  is_couple: boolean;
  spouse_age: number;
  spouse_horizon_age: number;
  spouse_ss_monthly: number;
  spouse_ss_start_age: number;
  
  // Healthcare costs
  healthcare_monthly: number;
  healthcare_start_age: number;
  healthcare_inflation: number;
  
  // Advanced features
  roth_conversion_annual: number;
  roth_conversion_start_age: number;
  roth_conversion_end_age: number;
  estate_tax_exemption: number;
  estate_tax_rate: number;
  legacy_goal: number;
  
  // Longevity planning
  use_actuarial_tables: boolean;
  health_adjustment: number;
  
  // Dynamic allocation (glide path)
  use_glide_path: boolean;
  target_equity_pct: number;
  glide_start_age: number;
  
  // Lifestyle spending phases
  use_lifestyle_phases: boolean;
  go_go_end_age: number;
  go_go_spending_multiplier: number;
  slow_go_end_age: number;
  slow_go_spending_multiplier: number;
  no_go_spending_multiplier: number;
  
  // Guardrails
  use_guardrails: boolean;
  upper_guardrail: number;
  lower_guardrail: number;
  guardrail_adjustment: number;
  
  // UI-only optional fields (not sent to backend)
  equity_dist_rate?: number;
  fi_dist_rate?: number;
  corr_equity_fi?: number;
  num_sims?: number;
  spending_inflation_adjusted?: boolean;
  one_time_contribution?: number;
  contribution_year?: number;
  one_time_withdrawal?: number;
  withdrawal_year?: number;
  social_security_start_year?: number;
  social_security_cola?: boolean;
  pension_start_year?: number;
  pension_cola?: boolean;
  rebalance_strategy?: string;
  fee_pct?: number;
  random_seed?: number;
}

export interface FinancialGoal {
  name: string;
  target_amount: number;
  target_age: number;
  priority: string;
}

export interface StressTestScenario {
  name: string;
  description: string;
  equity_return_adj: number;
  fi_return_adj: number;
  inflation_adj: number;
  spending_adj: number;
  volatility_multiplier: number;
}

export interface SimulationRequest {
  client_info: ClientInfo;
  inputs: ModelInputs;
  financial_goals?: FinancialGoal[];
  stress_scenarios?: StressTestScenario[];
  seed?: number;
}

export interface SimulationMetrics {
  success_probability: number;
  ending_median: number;
  ending_p10: number;
  ending_p90: number;
  years_depleted: number;
  depletion_probability: number;
  shortfall_risk: number;
}

export interface MonthlyStats {
  Month: number;
  Median: number;
  P10: number;
  P25: number;
  P75: number;
  P90: number;
  Mean: number;
  StdDev: number;
}

export interface GoalProbability {
  goal_name: string;
  target_amount: number;
  target_age: number;
  probability: number;
  median_value: number;
}

export interface SimulationResponse {
  metrics: SimulationMetrics;
  stats: MonthlyStats[];
  goal_probabilities?: GoalProbability[];
  success: boolean;
  message: string;
}

export interface AssumptionPreset {
  name: string;
  equity_return: number;
  fi_return: number;
  cash_return: number;
  equity_vol: number;
  fi_vol: number;
  cash_vol: number;
}

export interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface HealthCheck {
  status: string;
  version: string;
  timestamp: string;
}
