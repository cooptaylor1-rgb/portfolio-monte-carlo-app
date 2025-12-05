/**
 * Inputs Page - Configure simulation parameters
 * Redesigned with clear sections, better hierarchy, and improved UX
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  FormField,
} from '../components/forms';
import { SectionHeader, Button, FormSection, Card, Badge } from '../components/ui';
import { 
  User, 
  Wallet, 
  TrendingUp, 
  Calendar, 
  DollarSign, 
  Settings,
  Zap,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';

const InputsPage: React.FC = () => {
  const navigate = useNavigate();
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
    isLoading,
    validationErrors,
    validationWarnings,
  } = useSimulationStore();

  const [isSaving, setIsSaving] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<string>('');

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
    console.log('=== RUN SIMULATION CLICKED ===');
    console.log('Client Info:', JSON.stringify(clientInfo, null, 2));
    console.log('Model Inputs (raw):', JSON.stringify(modelInputs, null, 2));
    console.log('health_adjustment value:', modelInputs.health_adjustment, 'type:', typeof modelInputs.health_adjustment);
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Convert all numeric string fields to actual numbers
      const sanitizedInputs = Object.entries(modelInputs).reduce((acc, [key, value]) => {
        // Special handling for health_adjustment
        if (key === 'health_adjustment') {
          if (value === 'average' || value === 'poor' || value === 'excellent') {
            // Convert string health values to numbers
            const healthMap: Record<string, number> = {
              'poor': -5,
              'average': 0,
              'excellent': 5
            };
            acc[key] = healthMap[value as string] || 0;
          } else if (typeof value === 'string') {
            acc[key] = parseInt(value, 10) || 0;
          } else {
            acc[key] = value;
          }
        }
        // Convert other string numbers to actual numbers
        else if (typeof value === 'string' && !isNaN(Number(value)) && value !== '') {
          acc[key] = Number(value);
        } else {
          acc[key] = value;
        }
        return acc;
      }, {} as any);
      
      const payload = {
        client_info: clientInfo,
        inputs: sanitizedInputs,
      };
      
      console.log('health_adjustment after sanitization:', sanitizedInputs.health_adjustment);
      console.log('Sanitized inputs:', JSON.stringify(sanitizedInputs, null, 2));
      console.log('Sending request to /api/simulation/run');
      
      const response = await apiClient.axiosClient.post('/simulation/run', payload);
      
      console.log('Response received:', response.data);
      setSimulationResults(response.data);
      setHasRunSimulation(true);
      console.log('Navigating to dashboard...');
      navigate('/');
    } catch (err: any) {
      console.error('=== ERROR OCCURRED ===');
      console.error('Error object:', err);
      console.error('Error message:', err.message);
      console.error('Error response:', err.response);
      console.error('Error response data:', err.response?.data);
      console.error('Error response status:', err.response?.status);
      
      let errorMessage = 'Simulation failed';
      
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.detail) {
          if (Array.isArray(err.response.data.detail)) {
            // Pydantic validation errors
            errorMessage = err.response.data.detail.map((e: any) => 
              `${e.loc?.join('.')} : ${e.msg}`
            ).join('\n');
          } else {
            errorMessage = err.response.data.detail;
          }
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        } else {
          errorMessage = JSON.stringify(err.response.data);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      alert('ERROR:\n\n' + errorMessage);
    } finally {
      setIsLoading(false);
      console.log('=== RUN SIMULATION COMPLETE ===');
    }
  };

  const handleLoadPreset = async (presetName: string) => {
    try {
      setIsSaving(true);
      setSelectedPreset(presetName);
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

  const presets = [
    { value: 'conservative', label: 'Conservative Retiree', description: 'Low risk, stable income' },
    { value: 'moderate', label: 'Moderate Growth', description: 'Balanced approach' },
    { value: 'aggressive', label: 'Aggressive Accumulator', description: 'High growth potential' },
  ];

  return (
    <div className="space-y-xl pb-24">
      {/* Header with Preset Selection */}
      <SectionHeader
        title="Model Configuration"
        description="Configure client information and simulation parameters"
        icon={<Settings size={28} />}
      />

      {/* Quick Start with Presets */}
      <Card padding="lg">
        <div className="mb-4">
          <h3 className="text-h4 font-display text-text-primary mb-2">
            Quick Start
          </h3>
          <p className="text-small text-text-tertiary">
            Choose a preset to get started quickly, or configure custom parameters below
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {presets.map((preset) => (
            <button
              key={preset.value}
              onClick={() => handleLoadPreset(preset.value)}
              disabled={isSaving}
              className={`
                p-5 rounded-md border-2 transition-all text-left
                ${selectedPreset === preset.value
                  ? 'border-accent-gold bg-accent-gold bg-opacity-10'
                  : 'border-background-border hover:border-accent-gold hover:bg-background-hover'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="text-h4 font-semibold text-text-primary">
                  {preset.label}
                </h4>
                {selectedPreset === preset.value && (
                  <CheckCircle size={20} className="text-accent-gold flex-shrink-0" />
                )}
              </div>
              <p className="text-small text-text-tertiary">
                {preset.description}
              </p>
            </button>
          ))}
        </div>
      </Card>

      {/* Validation Messages */}
      {validationErrors.length > 0 && (
        <Card padding="md" variant="default" className="border-status-error-base bg-status-error-base bg-opacity-10">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-status-error-base flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-h4 font-semibold text-status-error-light mb-2">Validation Errors</h4>
              <ul className="space-y-1">
                {validationErrors.map((error, idx) => (
                  <li key={idx} className="text-small text-status-error-light">• {error}</li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      )}

      {validationWarnings.length > 0 && (
        <Card padding="md" variant="default" className="border-status-warning-base bg-status-warning-base bg-opacity-10">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-status-warning-base flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-h4 font-semibold text-status-warning-light mb-2">Warnings</h4>
              <ul className="space-y-1">
                {validationWarnings.map((warning, idx) => (
                  <li key={idx} className="text-small text-status-warning-light">• {warning}</li>
                ))}
              </ul>
            </div>
          </div>
        </Card>
      )}

      {/* Client Information */}
      <FormSection
        title="Client Information"
        description="Basic client and advisor details"
        icon={<User size={20} />}
        defaultExpanded={true}
        required
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField label="Client Name" required>
            <TextInput
              value={clientInfo.client_name}
              onChange={(value) => setClientInfo({ client_name: value })}
              placeholder="John Doe"
            />
          </FormField>
          <FormField label="Report Date" required>
            <DateInput
              value={clientInfo.report_date}
              onChange={(value) => setClientInfo({ report_date: value })}
            />
          </FormField>
          <FormField label="Advisor Name">
            <TextInput
              value={clientInfo.advisor_name || ''}
              onChange={(value) => setClientInfo({ advisor_name: value })}
              placeholder="Jane Smith"
            />
          </FormField>
          <FormField label="Client ID">
            <TextInput
              value={clientInfo.client_id || ''}
              onChange={(value) => setClientInfo({ client_id: value })}
              placeholder="C-12345"
            />
          </FormField>
        </div>
        <div className="mt-6">
          <FormField label="Client Notes" help="Additional notes or context">
            <TextInput
              value={clientInfo.client_notes || ''}
              onChange={(value) => setClientInfo({ client_notes: value })}
              placeholder="Additional notes or context..."
            />
          </FormField>
        </div>
      </FormSection>

      {/* Portfolio Configuration */}
      <FormSection
        title="Portfolio Configuration"
        description="Starting portfolio value and asset allocation"
        icon={<Wallet size={20} />}
        defaultExpanded={true}
        required
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="md:col-span-2">
            <FormField label="Starting Portfolio Value" required help="Total portfolio value at the beginning of simulation">
              <DollarInput
                value={modelInputs.starting_portfolio}
                onChange={(value) => setModelInputs({ starting_portfolio: value })}
              />
            </FormField>
          </div>

          <FormField label="Equity Allocation" required help="Percentage allocated to stocks">
            <PercentInput
              value={modelInputs.equity_pct}
              onChange={(value) => setModelInputs({ equity_pct: value })}
            />
          </FormField>
          <FormField label="Fixed Income Allocation" required help="Percentage allocated to bonds">
            <PercentInput
              value={modelInputs.fi_pct}
              onChange={(value) => setModelInputs({ fi_pct: value })}
            />
          </FormField>
          <FormField label="Cash Allocation" required help="Percentage held in cash">
            <PercentInput
              value={modelInputs.cash_pct}
              onChange={(value) => setModelInputs({ cash_pct: value })}
            />
          </FormField>
          
          <div className="flex items-center justify-center p-6 bg-background-hover rounded-sm border border-background-border">
            <div className="text-center">
              <p className="text-small text-text-tertiary mb-1">Total Allocation</p>
              <p className={`text-display font-display ${
                Math.abs((modelInputs.equity_pct + modelInputs.fi_pct + modelInputs.cash_pct) - 1.0) < 0.001
                  ? 'text-status-success-base'
                  : 'text-status-error-base'
              }`}>
                {((modelInputs.equity_pct + modelInputs.fi_pct + modelInputs.cash_pct) * 100).toFixed(1)}%
              </p>
              {Math.abs((modelInputs.equity_pct + modelInputs.fi_pct + modelInputs.cash_pct) - 1.0) >= 0.001 && (
                <p className="text-micro text-status-error-light mt-1">Must equal 100%</p>
              )}
            </div>
          </div>
        </div>
      </FormSection>

      {/* Market Assumptions */}
      <FormSection
        title="Market Assumptions"
        description="Expected returns, volatility, and correlations"
        icon={<TrendingUp size={20} />}
        defaultExpanded={false}
        required
      >
        <div className="space-y-8">
          {/* Equity Assumptions */}
          <div>
            <h4 className="text-h4 font-semibold text-text-primary mb-4 flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-chart-equity"></span>
              Equity Assumptions
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <FormField label="Annual Return" required>
                <PercentInput
                  value={modelInputs.equity_return_annual}
                  onChange={(value) => setModelInputs({ equity_return_annual: value })}
                />
              </FormField>
              <FormField label="Annual Volatility" required>
                <PercentInput
                  value={modelInputs.equity_vol_annual}
                  onChange={(value) => setModelInputs({ equity_vol_annual: value })}
                />
              </FormField>
              <FormField label="Distribution Rate">
                <PercentInput
                  value={modelInputs.equity_dist_rate}
                  onChange={(value) => setModelInputs({ equity_dist_rate: value })}
                />
              </FormField>
            </div>
          </div>

          {/* Fixed Income Assumptions */}
          <div>
            <h4 className="text-h4 font-semibold text-text-primary mb-4 flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-chart-fixed"></span>
              Fixed Income Assumptions
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <FormField label="Annual Return" required>
                <PercentInput
                  value={modelInputs.fi_return_annual}
                  onChange={(value) => setModelInputs({ fi_return_annual: value })}
                />
              </FormField>
              <FormField label="Annual Volatility" required>
                <PercentInput
                  value={modelInputs.fi_vol_annual}
                  onChange={(value) => setModelInputs({ fi_vol_annual: value })}
                />
              </FormField>
              <FormField label="Distribution Rate">
                <PercentInput
                  value={modelInputs.fi_dist_rate}
                  onChange={(value) => setModelInputs({ fi_dist_rate: value })}
                />
              </FormField>
            </div>
          </div>

          {/* Cash Assumptions */}
          <div>
            <h4 className="text-h4 font-semibold text-text-primary mb-4 flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-chart-cash"></span>
              Cash Assumptions
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <FormField label="Annual Return" required>
                <PercentInput
                  value={modelInputs.cash_return_annual}
                  onChange={(value) => setModelInputs({ cash_return_annual: value })}
                />
              </FormField>
            </div>
          </div>

          {/* Correlations */}
          <div>
            <h4 className="text-h4 font-semibold text-text-primary mb-4">
              Asset Correlations
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <NumberInput
                label="Equity / Fixed Income Correlation"
                value={modelInputs.corr_equity_fi}
                onChange={(value) => setModelInputs({ corr_equity_fi: value })}
                help="Value between -1 and 1"
              />
              <PercentInput
                label="Inflation Rate (Annual)"
                value={modelInputs.inflation_annual}
                onChange={(value) => setModelInputs({ inflation_annual: value })}
                required
              />
            </div>
          </div>
        </div>
      </FormSection>

      {/* Time Horizon & Spending */}
      <FormSection
        title="Time Horizon & Spending"
        description="Planning period and cash flow assumptions"
        icon={<Calendar size={20} />}
        defaultExpanded={false}
        required
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <NumberInput
            label="Years to Model"
            value={modelInputs.years_to_model}
            onChange={(value) => setModelInputs({ years_to_model: value })}
            required
            help="Length of simulation period"
          />
          <NumberInput
            label="Number of Simulations"
            value={modelInputs.num_sims}
            onChange={(value) => setModelInputs({ num_sims: value })}
            required
            help="More simulations = more accurate results (1000-10000)"
          />

          <div className="md:col-span-2 h-px bg-background-border my-2"></div>

          <DollarInput
            label="Monthly Income"
            value={modelInputs.monthly_income || 0}
            onChange={(value) => setModelInputs({ monthly_income: value })}
            help="Regular monthly income (salary, pension, etc.)"
          />
          <DollarInput
            label="Monthly Spending"
            value={modelInputs.monthly_spending}
            onChange={(value) => setModelInputs({ monthly_spending: value })}
            required
            help="Regular monthly withdrawal amount"
          />
          <Checkbox
            label="Adjust Spending for Inflation"
            checked={modelInputs.spending_inflation_adjusted}
            onChange={(checked) => setModelInputs({ spending_inflation_adjusted: checked })}
            help="Increase spending annually by inflation rate"
          />
        </div>
      </FormSection>

      {/* Additional Cash Flows */}
      <FormSection
        title="Additional Cash Flows"
        description="One-time contributions, withdrawals, and income streams"
        icon={<DollarSign size={20} />}
        defaultExpanded={false}
      >
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <DollarInput
              label="One-Time Contribution"
              value={modelInputs.one_time_contribution || 0}
              onChange={(value) => setModelInputs({ one_time_contribution: value })}
              help="Single large deposit"
            />
            <NumberInput
              label="Contribution Year"
              value={modelInputs.contribution_year || 0}
              onChange={(value) => setModelInputs({ contribution_year: value })}
              help="Year when contribution occurs"
            />
            <div></div>

            <DollarInput
              label="One-Time Withdrawal"
              value={modelInputs.one_time_withdrawal || 0}
              onChange={(value) => setModelInputs({ one_time_withdrawal: value })}
              help="Single large expense"
            />
            <NumberInput
              label="Withdrawal Year"
              value={modelInputs.withdrawal_year || 0}
              onChange={(value) => setModelInputs({ withdrawal_year: value })}
              help="Year when withdrawal occurs"
            />
            <div></div>

            <DollarInput
              label="Social Security (Monthly)"
              value={modelInputs.social_security_monthly || 0}
              onChange={(value) => setModelInputs({ social_security_monthly: value })}
              help="Monthly Social Security benefit"
            />
            <NumberInput
              label="Start Year"
              value={modelInputs.social_security_start_year || 0}
              onChange={(value) => setModelInputs({ social_security_start_year: value })}
              help="Year benefits begin"
            />
            <Checkbox
              label="Adjust for Inflation"
              checked={modelInputs.social_security_cola || false}
              onChange={(checked) => setModelInputs({ social_security_cola: checked })}
            />

            <DollarInput
              label="Pension (Monthly)"
              value={modelInputs.pension_monthly || 0}
              onChange={(value) => setModelInputs({ pension_monthly: value })}
              help="Monthly pension payment"
            />
            <NumberInput
              label="Start Year"
              value={modelInputs.pension_start_year || 0}
              onChange={(value) => setModelInputs({ pension_start_year: value })}
              help="Year pension begins"
            />
            <Checkbox
              label="Adjust for Inflation"
              checked={modelInputs.pension_cola || false}
              onChange={(checked) => setModelInputs({ pension_cola: checked })}
            />
          </div>
        </div>
      </FormSection>

      {/* Advanced Settings */}
      <FormSection
        title="Advanced Settings"
        description="Rebalancing, fees, and tax assumptions"
        icon={<Zap size={20} />}
        defaultExpanded={false}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Radio
            label="Rebalancing Strategy"
            value={modelInputs.rebalance_strategy}
            onChange={(value) => setModelInputs({ rebalance_strategy: value })}
            options={[
              { value: 'none', label: 'No Rebalancing' },
              { value: 'annual', label: 'Annual Rebalancing' },
              { value: 'quarterly', label: 'Quarterly Rebalancing' },
              { value: 'threshold', label: 'Threshold-Based' },
            ]}
          />

          <PercentInput
            label="Management Fee (Annual)"
            value={modelInputs.fee_pct || 0}
            onChange={(value) => setModelInputs({ fee_pct: value })}
            help="Total annual advisory and fund fees"
          />

          <PercentInput
            label="Tax Rate on Withdrawals"
            value={modelInputs.tax_rate || 0}
            onChange={(value) => setModelInputs({ tax_rate: value })}
            help="Effective tax rate on distributions"
          />

          <NumberInput
            label="Random Seed"
            value={modelInputs.random_seed || 42}
            onChange={(value) => setModelInputs({ random_seed: value })}
            help="For reproducible results"
          />
        </div>
      </FormSection>

      {/* Sticky Action Bar */}
      <div className="fixed bottom-0 left-60 right-0 bg-background-elevated border-t border-background-border shadow-xl z-50">
        <div className="max-w-container mx-auto px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {validationErrors.length > 0 && (
              <div className="flex items-center gap-2 text-status-error-base">
                <AlertCircle size={16} />
                <span className="text-small font-medium">{validationErrors.length} errors found</span>
              </div>
            )}
            {validationWarnings.length > 0 && validationErrors.length === 0 && (
              <div className="flex items-center gap-2 text-status-warning-base">
                <AlertCircle size={16} />
                <span className="text-small font-medium">{validationWarnings.length} warnings</span>
              </div>
            )}
            {validationErrors.length === 0 && validationWarnings.length === 0 && (
              <div className="flex items-center gap-2 text-text-tertiary">
                <CheckCircle size={16} />
                <span className="text-small">Ready to run</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleValidate}
              type="button"
              disabled={isLoading}
              className="px-6 py-3 text-body font-semibold rounded-sm transition-all bg-background-hover text-text-secondary hover:bg-background-border hover:text-text-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Validating...' : 'Validate Inputs'}
            </button>
            <button
              onClick={handleRunSimulation}
              type="button"
              disabled={isLoading}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 text-body font-semibold rounded-sm transition-all bg-accent-gold text-text-primary hover:bg-accent-gold-light shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Running...
                </>
              ) : (
                <>
                  <Zap size={18} />
                  Run Monte Carlo Simulation
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InputsPage;
