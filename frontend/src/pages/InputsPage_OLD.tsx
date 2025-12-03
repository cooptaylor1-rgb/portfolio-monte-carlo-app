/**
 * Inputs Page - Configure simulation parameters
 */
import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import apiClient from '../lib/api';
import {
  TextInput,
  NumberInput,
  DollarInput,
  PercentInput,
  Slider,
  Checkbox,
  Radio,
  DateInput,
  SelectBox,
  Expander,
} from '../components/forms';

const InputsPage: React.FC = () => {
  const {
    clientInfo,
    setClientInfo,
    modelInputs,
    setModelInputs,
    setSimulationResults,
    setIsLoading,
    setError,
    setValidation,
    setHasRunSimulation,
  } = useSimulationStore();

  const [isSaving, setIsSaving] = useState(false);

  const handleValidate = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.axiosClient.post('/simulation/validate', {
        client_info: clientInfo,
        model_inputs: modelInputs,
      });
      setValidation(response.data.errors, response.data.warnings);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Validation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunSimulation = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiClient.axiosClient.post('/simulation/run', {
        client_info: clientInfo,
        model_inputs: modelInputs,
      });
      setSimulationResults(response.data);
      setHasRunSimulation(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Simulation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadPreset = async (presetName: string) => {
    try {
      setIsSaving(true);
      const response = await apiClient.axiosClient.get(`/presets/${presetName}`);
      setClientInfo(response.data.client_info);
      setModelInputs(response.data.model_inputs);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load preset');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-text-primary">Model Inputs</h1>
        <div className="flex gap-3">
          <SelectBox
            label=""
            value=""
            onChange={(value: string | number) => {
              if (value) handleLoadPreset(value.toString());
            }}
            options={[
              { value: 'conservative', label: 'Conservative Retiree' },
              { value: 'moderate', label: 'Moderate Growth' },
              { value: 'aggressive', label: 'Aggressive Accumulator' },
            ]}
            placeholder="Load Preset..."
            disabled={isSaving}
          />
          <button
            onClick={handleValidate}
            className="px-6 py-2 bg-surface-700 text-text-primary rounded-lg hover:bg-surface-600 transition-colors border border-surface-600"
          >
            Validate
          </button>
          <button
            onClick={handleRunSimulation}
            className="px-6 py-2 bg-brand-gold text-primary-900 rounded-lg hover:bg-brand-gold-dark transition-colors font-semibold"
          >
            Run Simulation
          </button>
        </div>
      </div>

      {/* Client Information */}
      <Expander title="Client Information" defaultExpanded={true}>
        <div className="grid grid-cols-2 gap-6">
          <TextInput
            label="Client Name"
            value={clientInfo.client_name}
            onChange={(value) => setClientInfo({ client_name: value })}
            placeholder="John Doe"
            required
          />
          <DateInput
            label="Report Date"
            value={clientInfo.report_date}
            onChange={(value) => setClientInfo({ report_date: value })}
            required
          />
          <TextInput
            label="Advisor Name"
            value={clientInfo.advisor_name || ''}
            onChange={(value) => setClientInfo({ advisor_name: value })}
            placeholder="Jane Smith"
          />
          <TextInput
            label="Client ID"
            value={clientInfo.client_id || ''}
            onChange={(value) => setClientInfo({ client_id: value })}
            placeholder="C-12345"
          />
        </div>
        <div className="mt-4">
          <TextInput
            label="Client Notes"
            value={clientInfo.client_notes || ''}
            onChange={(value) => setClientInfo({ client_notes: value })}
            placeholder="Additional notes or context..."
          />
        </div>
      </Expander>

      {/* Portfolio & Horizon */}
      <Expander title="Portfolio & Time Horizon" defaultExpanded={true}>
        <div className="grid grid-cols-2 gap-6">
          <DollarInput
            label="Starting Portfolio Value"
            value={modelInputs.starting_portfolio}
            onChange={(value) => setModelInputs({ starting_portfolio: value })}
            help="Total investable assets at the start of planning"
            required
          />
          <NumberInput
            label="Years to Model"
            value={modelInputs.years_to_model}
            onChange={(value) => setModelInputs({ years_to_model: value })}
            min={1}
            max={75}
            step={1}
            help="Number of years to project forward"
            required
          />
          <NumberInput
            label="Current Age"
            value={modelInputs.current_age}
            onChange={(value) => setModelInputs({ current_age: value })}
            min={18}
            max={120}
            step={1}
            required
          />
          <NumberInput
            label="Horizon Age"
            value={modelInputs.horizon_age}
            onChange={(value) => setModelInputs({ horizon_age: value })}
            min={18}
            max={120}
            step={1}
            help="Planning endpoint age"
            required
          />
        </div>
      </Expander>

      {/* Couple Planning */}
      <Expander title="Couple Planning">
        <Checkbox
          label="Is this a couple?"
          checked={modelInputs.is_couple}
          onChange={(checked) => setModelInputs({ is_couple: checked })}
          help="Enable spouse inputs"
        />
        {modelInputs.is_couple && (
          <div className="grid grid-cols-2 gap-6 mt-4">
            <NumberInput
              label="Spouse Current Age"
              value={modelInputs.spouse_age}
              onChange={(value) => setModelInputs({ spouse_age: value })}
              min={18}
              max={120}
              step={1}
            />
            <NumberInput
              label="Spouse Horizon Age"
              value={modelInputs.spouse_horizon_age}
              onChange={(value) => setModelInputs({ spouse_horizon_age: value })}
              min={18}
              max={120}
              step={1}
            />
            <DollarInput
              label="Spouse Social Security (Monthly)"
              value={modelInputs.spouse_ss_monthly}
              onChange={(value) => setModelInputs({ spouse_ss_monthly: value })}
            />
            <NumberInput
              label="Spouse SS Start Age"
              value={modelInputs.spouse_ss_start_age}
              onChange={(value) => setModelInputs({ spouse_ss_start_age: value })}
              min={62}
              max={70}
              step={1}
            />
          </div>
        )}
      </Expander>

      {/* Spending */}
      <Expander title="Spending & Inflation">
        <div className="grid grid-cols-2 gap-6">
          <DollarInput
            label="Monthly Spending"
            value={Math.abs(modelInputs.monthly_spending)}
            onChange={(value) => setModelInputs({ monthly_spending: -Math.abs(value) })}
            help="Base living expenses (entered as positive, stored as negative)"
            required
          />
          <PercentInput
            label="Annual Inflation"
            value={modelInputs.inflation_annual}
            onChange={(value) => setModelInputs({ inflation_annual: value })}
            help="General inflation rate"
            required
          />
          <Radio
            label="Spending Rule"
            value={modelInputs.spending_rule.toString()}
            onChange={(value: string | number) => setModelInputs({ spending_rule: parseInt(value.toString()) as 1 | 2 })}
            options={[
              { value: '1', label: 'Fixed Real' },
              { value: '2', label: 'Percent of Portfolio' },
            ]}
          />
          {modelInputs.spending_rule === 2 && (
            <PercentInput
              label="Spending % of Portfolio (Annual)"
              value={modelInputs.spending_pct_annual}
              onChange={(value) => setModelInputs({ spending_pct_annual: value })}
            />
          )}
        </div>
      </Expander>

      {/* Account Types */}
      <Expander title="Account Types & Taxes">
        <div className="grid grid-cols-3 gap-6">
          <PercentInput
            label="Taxable %"
            value={modelInputs.taxable_pct}
            onChange={(value) => setModelInputs({ taxable_pct: value })}
            help="Percent of portfolio in taxable accounts"
          />
          <PercentInput
            label="IRA %"
            value={modelInputs.ira_pct}
            onChange={(value) => setModelInputs({ ira_pct: value })}
            help="Percent in traditional IRA/401k"
          />
          <PercentInput
            label="Roth %"
            value={modelInputs.roth_pct}
            onChange={(value) => setModelInputs({ roth_pct: value })}
            help="Percent in Roth accounts"
          />
        </div>
        <div className="grid grid-cols-2 gap-6 mt-4">
          <PercentInput
            label="Tax Rate"
            value={modelInputs.tax_rate}
            onChange={(value) => setModelInputs({ tax_rate: value })}
            help="Marginal tax rate on withdrawals"
          />
          <NumberInput
            label="RMD Start Age"
            value={modelInputs.rmd_age}
            onChange={(value) => setModelInputs({ rmd_age: value })}
            min={70}
            max={75}
            step={1}
            help="Required minimum distribution age"
          />
        </div>
      </Expander>

      {/* Income Streams */}
      <Expander title="Income Streams">
        <div className="grid grid-cols-2 gap-6">
          <DollarInput
            label="Social Security (Monthly)"
            value={modelInputs.social_security_monthly}
            onChange={(value) => setModelInputs({ social_security_monthly: value })}
          />
          <NumberInput
            label="SS Start Age"
            value={modelInputs.ss_start_age}
            onChange={(value) => setModelInputs({ ss_start_age: value })}
            min={62}
            max={70}
            step={1}
          />
          <DollarInput
            label="Pension (Monthly)"
            value={modelInputs.pension_monthly}
            onChange={(value) => setModelInputs({ pension_monthly: value })}
          />
          <NumberInput
            label="Pension Start Age"
            value={modelInputs.pension_start_age}
            onChange={(value) => setModelInputs({ pension_start_age: value })}
            min={50}
            max={75}
            step={1}
          />
          <DollarInput
            label="Regular Income (Monthly)"
            value={modelInputs.regular_income_monthly}
            onChange={(value) => setModelInputs({ regular_income_monthly: value })}
            help="Part-time work, rental income, etc."
          />
          <DollarInput
            label="Other Income (Monthly)"
            value={modelInputs.other_income_monthly}
            onChange={(value) => setModelInputs({ other_income_monthly: value })}
          />
          <NumberInput
            label="Other Income Start Age"
            value={modelInputs.other_income_start_age}
            onChange={(value) => setModelInputs({ other_income_start_age: value })}
            min={50}
            max={100}
            step={1}
          />
        </div>
      </Expander>

      {/* Asset Allocation */}
      <Expander title="Asset Allocation" defaultExpanded={true}>
        <div className="grid grid-cols-3 gap-6">
          <div>
            <PercentInput
              label="Equity %"
              value={modelInputs.equity_pct}
              onChange={(value) => setModelInputs({ equity_pct: value })}
              required
            />
            <Slider
              label=""
              value={modelInputs.equity_pct * 100}
              onChange={(value) => setModelInputs({ equity_pct: value / 100 })}
              min={0}
              max={100}
              step={1}
              formatValue={(v) => `${v}%`}
            />
          </div>
          <div>
            <PercentInput
              label="Fixed Income %"
              value={modelInputs.fi_pct}
              onChange={(value) => setModelInputs({ fi_pct: value })}
              required
            />
            <Slider
              label=""
              value={modelInputs.fi_pct * 100}
              onChange={(value) => setModelInputs({ fi_pct: value / 100 })}
              min={0}
              max={100}
              step={1}
              formatValue={(v) => `${v}%`}
            />
          </div>
          <div>
            <PercentInput
              label="Cash %"
              value={modelInputs.cash_pct}
              onChange={(value) => setModelInputs({ cash_pct: value })}
              required
            />
            <Slider
              label=""
              value={modelInputs.cash_pct * 100}
              onChange={(value) => setModelInputs({ cash_pct: value / 100 })}
              min={0}
              max={100}
              step={1}
              formatValue={(v) => `${v}%`}
            />
          </div>
        </div>
        <div className="mt-4 p-4 bg-surface-800 rounded-lg border border-surface-700">
          <p className="text-sm text-text-secondary">
            Total Allocation:{' '}
            <span className="text-text-primary font-semibold">
              {((modelInputs.equity_pct + modelInputs.fi_pct + modelInputs.cash_pct) * 100).toFixed(1)}%
            </span>
            {Math.abs((modelInputs.equity_pct + modelInputs.fi_pct + modelInputs.cash_pct) - 1) > 0.01 && (
              <span className="text-error-500 ml-2">⚠️ Must sum to 100%</span>
            )}
          </p>
        </div>
      </Expander>

      {/* Return Assumptions */}
      <Expander title="Return Assumptions">
        <div className="grid grid-cols-3 gap-6">
          <PercentInput
            label="Equity Return (Annual)"
            value={modelInputs.equity_return_annual}
            onChange={(value) => setModelInputs({ equity_return_annual: value })}
            help="Expected annual return"
            required
          />
          <PercentInput
            label="Fixed Income Return (Annual)"
            value={modelInputs.fi_return_annual}
            onChange={(value) => setModelInputs({ fi_return_annual: value })}
            required
          />
          <PercentInput
            label="Cash Return (Annual)"
            value={modelInputs.cash_return_annual}
            onChange={(value) => setModelInputs({ cash_return_annual: value })}
            required
          />
          <PercentInput
            label="Equity Volatility (Annual)"
            value={modelInputs.equity_vol_annual}
            onChange={(value) => setModelInputs({ equity_vol_annual: value })}
            help="Standard deviation"
            required
          />
          <PercentInput
            label="Fixed Income Volatility (Annual)"
            value={modelInputs.fi_vol_annual}
            onChange={(value) => setModelInputs({ fi_vol_annual: value })}
            required
          />
          <PercentInput
            label="Cash Volatility (Annual)"
            value={modelInputs.cash_vol_annual}
            onChange={(value) => setModelInputs({ cash_vol_annual: value })}
            required
          />
        </div>
      </Expander>

      {/* Monte Carlo Settings */}
      <Expander title="Monte Carlo Settings">
        <div className="grid grid-cols-2 gap-6">
          <NumberInput
            label="Number of Scenarios"
            value={modelInputs.n_scenarios}
            onChange={(value) => setModelInputs({ n_scenarios: value })}
            min={100}
            max={10000}
            step={100}
            help="More scenarios = more accurate but slower"
            required
          />
        </div>
      </Expander>

      {/* Cash Flows */}
      <Expander title="One-Time Cash Flows">
        <div className="grid grid-cols-2 gap-6">
          <DollarInput
            label="One-Time Cash Flow"
            value={modelInputs.one_time_cf}
            onChange={(value) => setModelInputs({ one_time_cf: value })}
            help="Positive = inflow, Negative = outflow"
          />
          <NumberInput
            label="Cash Flow Month"
            value={modelInputs.one_time_cf_month}
            onChange={(value) => setModelInputs({ one_time_cf_month: value })}
            min={0}
            max={360}
            step={1}
            help="Month number (0 = start)"
          />
        </div>
      </Expander>

      {/* Healthcare Costs */}
      <Expander title="Healthcare Costs">
        <div className="grid grid-cols-3 gap-6">
          <DollarInput
            label="Healthcare (Monthly)"
            value={modelInputs.healthcare_monthly}
            onChange={(value) => setModelInputs({ healthcare_monthly: value })}
          />
          <NumberInput
            label="Healthcare Start Age"
            value={modelInputs.healthcare_start_age}
            onChange={(value) => setModelInputs({ healthcare_start_age: value })}
            min={50}
            max={75}
            step={1}
          />
          <PercentInput
            label="Healthcare Inflation"
            value={modelInputs.healthcare_inflation}
            onChange={(value) => setModelInputs({ healthcare_inflation: value })}
            help="Typically higher than general inflation"
          />
        </div>
      </Expander>

      {/* Roth Conversions */}
      <Expander title="Roth Conversions">
        <div className="grid grid-cols-3 gap-6">
          <DollarInput
            label="Annual Conversion Amount"
            value={modelInputs.roth_conversion_annual}
            onChange={(value) => setModelInputs({ roth_conversion_annual: value })}
          />
          <NumberInput
            label="Conversion Start Age"
            value={modelInputs.roth_conversion_start_age}
            onChange={(value) => setModelInputs({ roth_conversion_start_age: value })}
            min={50}
            max={75}
            step={1}
          />
          <NumberInput
            label="Conversion End Age"
            value={modelInputs.roth_conversion_end_age}
            onChange={(value) => setModelInputs({ roth_conversion_end_age: value })}
            min={50}
            max={75}
            step={1}
          />
        </div>
      </Expander>

      {/* Estate Planning */}
      <Expander title="Estate Planning">
        <div className="grid grid-cols-3 gap-6">
          <DollarInput
            label="Estate Tax Exemption"
            value={modelInputs.estate_tax_exemption}
            onChange={(value) => setModelInputs({ estate_tax_exemption: value })}
          />
          <PercentInput
            label="Estate Tax Rate"
            value={modelInputs.estate_tax_rate}
            onChange={(value) => setModelInputs({ estate_tax_rate: value })}
          />
          <DollarInput
            label="Legacy Goal"
            value={modelInputs.legacy_goal}
            onChange={(value) => setModelInputs({ legacy_goal: value })}
            help="Target bequest amount"
          />
        </div>
      </Expander>

      {/* Longevity */}
      <Expander title="Longevity Assumptions">
        <Checkbox
          label="Use Actuarial Life Tables"
          checked={modelInputs.use_actuarial_tables}
          onChange={(checked) => setModelInputs({ use_actuarial_tables: checked })}
          help="Calculate probabilities based on mortality tables"
        />
        {modelInputs.use_actuarial_tables && (
          <div className="mt-4">
            <Radio
              label="Health Adjustment"
              value={modelInputs.health_adjustment}
              onChange={(value) => setModelInputs({ health_adjustment: value as any })}
              options={[
                { value: 'poor', label: 'Poor Health (-5 years)' },
                { value: 'average', label: 'Average Health' },
                { value: 'excellent', label: 'Excellent Health (+5 years)' },
              ]}
            />
          </div>
        )}
      </Expander>

      {/* Glide Path */}
      <Expander title="Equity Glide Path">
        <Checkbox
          label="Use Equity Glide Path"
          checked={modelInputs.use_glide_path}
          onChange={(checked) => setModelInputs({ use_glide_path: checked })}
          help="Automatically reduce equity allocation over time"
        />
        {modelInputs.use_glide_path && (
          <div className="grid grid-cols-2 gap-6 mt-4">
            <PercentInput
              label="Target Equity %"
              value={modelInputs.target_equity_pct}
              onChange={(value) => setModelInputs({ target_equity_pct: value })}
              help="Final equity allocation"
            />
            <NumberInput
              label="Glide Start Age"
              value={modelInputs.glide_start_age}
              onChange={(value) => setModelInputs({ glide_start_age: value })}
              min={50}
              max={75}
              step={1}
            />
          </div>
        )}
      </Expander>

      {/* Lifestyle Phases */}
      <Expander title="Lifestyle Spending Phases">
        <Checkbox
          label="Use Lifestyle Phases"
          checked={modelInputs.use_lifestyle_phases}
          onChange={(checked) => setModelInputs({ use_lifestyle_phases: checked })}
          help="Model Go-Go, Slow-Go, No-Go spending patterns"
        />
        {modelInputs.use_lifestyle_phases && (
          <div className="grid grid-cols-3 gap-6 mt-4">
            <div>
              <NumberInput
                label="Go-Go End Age"
                value={modelInputs.go_go_end_age}
                onChange={(value) => setModelInputs({ go_go_end_age: value })}
                min={60}
                max={90}
                step={1}
              />
              <PercentInput
                label="Go-Go Multiplier"
                value={modelInputs.go_go_spending_multiplier - 1}
                onChange={(value) => setModelInputs({ go_go_spending_multiplier: 1 + value })}
                help="Adjustment from base spending"
              />
            </div>
            <div>
              <NumberInput
                label="Slow-Go End Age"
                value={modelInputs.slow_go_end_age}
                onChange={(value) => setModelInputs({ slow_go_end_age: value })}
                min={70}
                max={100}
                step={1}
              />
              <PercentInput
                label="Slow-Go Multiplier"
                value={modelInputs.slow_go_spending_multiplier - 1}
                onChange={(value) => setModelInputs({ slow_go_spending_multiplier: 1 + value })}
              />
            </div>
            <div>
              <PercentInput
                label="No-Go Multiplier"
                value={modelInputs.no_go_spending_multiplier - 1}
                onChange={(value) => setModelInputs({ no_go_spending_multiplier: 1 + value })}
                help="Final phase spending"
              />
            </div>
          </div>
        )}
      </Expander>

      {/* Guardrails */}
      <Expander title="Dynamic Spending Guardrails">
        <Checkbox
          label="Use Guardrails"
          checked={modelInputs.use_guardrails}
          onChange={(checked) => setModelInputs({ use_guardrails: checked })}
          help="Adjust spending based on portfolio performance"
        />
        {modelInputs.use_guardrails && (
          <div className="grid grid-cols-3 gap-6 mt-4">
            <PercentInput
              label="Upper Guardrail"
              value={modelInputs.upper_guardrail}
              onChange={(value) => setModelInputs({ upper_guardrail: value })}
              help="Trigger for spending increase"
            />
            <PercentInput
              label="Lower Guardrail"
              value={modelInputs.lower_guardrail}
              onChange={(value) => setModelInputs({ lower_guardrail: value })}
              help="Trigger for spending reduction"
            />
            <PercentInput
              label="Adjustment Amount"
              value={modelInputs.guardrail_adjustment}
              onChange={(value) => setModelInputs({ guardrail_adjustment: value })}
              help="% change when triggered"
            />
          </div>
        )}
      </Expander>
    </div>
  );
};

export default InputsPage;
