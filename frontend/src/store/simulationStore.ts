import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { 
  SimulationResponse, 
  ClientInfo, 
  ModelInputs 
} from '../types';

interface SimulationStore {
  // Client Information
  clientInfo: ClientInfo;
  setClientInfo: (info: Partial<ClientInfo>) => void;

  // Model Inputs
  modelInputs: ModelInputs;
  setModelInputs: (inputs: Partial<ModelInputs>) => void;

  // Simulation Results
  simulationResults: SimulationResponse | null;
  setSimulationResults: (results: SimulationResponse | null) => void;

  // Loading States
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;

  // Errors
  error: string | null;
  setError: (error: string | null) => void;

  // Validation
  validationErrors: string[];
  validationWarnings: string[];
  setValidation: (errors: string[], warnings: string[]) => void;

  // Has Run Simulation
  hasRunSimulation: boolean;
  setHasRunSimulation: (hasRun: boolean) => void;

  // Reset
  reset: () => void;
}

const defaultClientInfo: ClientInfo = {
  client_name: '',
  report_date: new Date().toISOString().split('T')[0],
  advisor_name: '',
  client_id: '',
  client_notes: '',
};

const defaultModelInputs: ModelInputs = {
  starting_portfolio: 4500000,
  years_to_model: 30,
  current_age: 48,
  horizon_age: 78,
  monthly_income: 0,
  monthly_spending: -20000,
  inflation_annual: 0.03,
  equity_pct: 0.70,
  fi_pct: 0.25,
  cash_pct: 0.05,
  equity_return_annual: 0.10,
  fi_return_annual: 0.03,
  cash_return_annual: 0.02,
  equity_vol_annual: 0.15,
  fi_vol_annual: 0.05,
  cash_vol_annual: 0.01,
  n_scenarios: 200,
  spending_rule: 1,
  spending_pct_annual: 0.04,
  one_time_cf: 0,
  one_time_cf_month: 0,
  taxable_pct: 0.33,
  ira_pct: 0.50,
  roth_pct: 0.17,
  tax_rate: 0.25,
  rmd_age: 73,
  social_security_monthly: 0,
  ss_start_age: 67,
  pension_monthly: 0,
  pension_start_age: 65,
  regular_income_monthly: 0,
  other_income_monthly: 0,
  other_income_start_age: 65,
  is_couple: false,
  spouse_age: 48,
  spouse_horizon_age: 78,
  spouse_ss_monthly: 0,
  spouse_ss_start_age: 67,
  healthcare_monthly: 0,
  healthcare_start_age: 65,
  healthcare_inflation: 0.05,
  roth_conversion_annual: 0,
  roth_conversion_start_age: 60,
  roth_conversion_end_age: 70,
  estate_tax_exemption: 13610000,
  estate_tax_rate: 0.40,
  legacy_goal: 0,
  use_actuarial_tables: false,
  health_adjustment: 0,
  use_glide_path: false,
  target_equity_pct: 0.40,
  glide_start_age: 65,
  use_lifestyle_phases: false,
  go_go_end_age: 75,
  go_go_spending_multiplier: 1.0,
  slow_go_end_age: 85,
  slow_go_spending_multiplier: 0.80,
  no_go_spending_multiplier: 0.60,
  use_guardrails: false,
  upper_guardrail: 0.20,
  lower_guardrail: 0.15,
  guardrail_adjustment: 0.10,
};

export const useSimulationStore = create<SimulationStore>()(
  persist(
    (set) => ({
      clientInfo: defaultClientInfo,
      setClientInfo: (info) =>
        set((state) => ({
          clientInfo: { ...state.clientInfo, ...info },
        })),

      modelInputs: defaultModelInputs,
      setModelInputs: (inputs) =>
        set((state) => ({
          modelInputs: { ...state.modelInputs, ...inputs },
        })),

      simulationResults: null,
      setSimulationResults: (results) => set({ simulationResults: results }),

      isLoading: false,
      setIsLoading: (loading) => set({ isLoading: loading }),

      error: null,
      setError: (error) => set({ error }),

      validationErrors: [],
      validationWarnings: [],
      setValidation: (errors, warnings) =>
        set({ validationErrors: errors, validationWarnings: warnings }),

      hasRunSimulation: false,
      setHasRunSimulation: (hasRun) => set({ hasRunSimulation: hasRun }),

      reset: () =>
        set({
          clientInfo: defaultClientInfo,
          modelInputs: defaultModelInputs,
          simulationResults: null,
          isLoading: false,
          error: null,
          validationErrors: [],
          validationWarnings: [],
          hasRunSimulation: false,
        }),
    }),
    {
      name: 'simulation-storage',
      partialize: (state) => ({
        clientInfo: state.clientInfo,
        modelInputs: state.modelInputs,
      }),
    }
  )
);
