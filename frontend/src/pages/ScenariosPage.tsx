/**
 * Scenarios Page - Run and compare different scenarios
 * Redesigned with templates, visual comparison, and better UX
 */
import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import apiClient from '../lib/api';
import { Slider } from '../components/forms';
import { SensitivityHeatMap } from '../components/charts';
import { SectionHeader, Button, Card, Badge, EmptyState } from '../components/ui';
import { Plus, X, GitCompare, TrendingUp, TrendingDown, Zap, Copy } from 'lucide-react';

interface Scenario {
  id: string;
  name: string;
  equityReturnAdj: number;
  fiReturnAdj: number;
  inflationAdj: number;
  spendingAdj: number;
  successProbability?: number;
  endingMedian?: number;
}

const ScenarioTemplates = [
  {
    name: 'Optimistic Market',
    icon: <TrendingUp size={20} />,
    description: '+2% equity returns, -0.5% inflation',
    adjustments: { equityReturnAdj: 0.02, fiReturnAdj: 0.01, inflationAdj: -0.005, spendingAdj: 0 },
  },
  {
    name: 'Pessimistic Market',
    icon: <TrendingDown size={20} />,
    description: '-2% equity returns, +1% inflation',
    adjustments: { equityReturnAdj: -0.02, fiReturnAdj: -0.01, inflationAdj: 0.01, spendingAdj: 0 },
  },
  {
    name: 'Reduced Spending',
    icon: <TrendingDown size={20} />,
    description: '20% lower monthly expenses',
    adjustments: { equityReturnAdj: 0, fiReturnAdj: 0, inflationAdj: 0, spendingAdj: -0.2 },
  },
  {
    name: 'Increased Spending',
    icon: <TrendingUp size={20} />,
    description: '20% higher monthly expenses',
    adjustments: { equityReturnAdj: 0, fiReturnAdj: 0, inflationAdj: 0, spendingAdj: 0.2 },
  },
];

const ScenariosPage: React.FC = () => {
  const { modelInputs, clientInfo, hasRunSimulation } = useSimulationStore();
  const [scenarios, setScenarios] = useState<Scenario[]>([
    {
      id: '1',
      name: 'Base Case',
      equityReturnAdj: 0,
      fiReturnAdj: 0,
      inflationAdj: 0,
      spendingAdj: 0,
    },
  ]);
  const [isRunning, setIsRunning] = useState(false);
  const [sensitivityData, setSensitivityData] = useState<any[]>([]);
  const [isSensitivityRunning, setIsSensitivityRunning] = useState(false);

  const addScenario = (template?: typeof ScenarioTemplates[0]) => {
    const newId = (scenarios.length + 1).toString();
    const newScenario: Scenario = {
      id: newId,
      name: template ? template.name : `Scenario ${newId}`,
      equityReturnAdj: template?.adjustments.equityReturnAdj || 0,
      fiReturnAdj: template?.adjustments.fiReturnAdj || 0,
      inflationAdj: template?.adjustments.inflationAdj || 0,
      spendingAdj: template?.adjustments.spendingAdj || 0,
    };
    setScenarios([...scenarios, newScenario]);
  };

  const removeScenario = (id: string) => {
    if (scenarios.length > 1 && id !== '1') {
      setScenarios(scenarios.filter((s) => s.id !== id));
    }
  };

  const duplicateScenario = (scenario: Scenario) => {
    const newId = (scenarios.length + 1).toString();
    setScenarios([...scenarios, { ...scenario, id: newId, name: `${scenario.name} (Copy)` }]);
  };

  const updateScenario = (id: string, updates: Partial<Scenario>) => {
    setScenarios(
      scenarios.map((s) => (s.id === id ? { ...s, ...updates } : s))
    );
  };

  const runScenarios = async () => {
    setIsRunning(true);
    try {
      const results = await Promise.all(
        scenarios.map(async (scenario) => {
          const adjustedInputs = {
            ...modelInputs,
            equity_return_annual:
              modelInputs.equity_return_annual + scenario.equityReturnAdj,
            fi_return_annual: modelInputs.fi_return_annual + scenario.fiReturnAdj,
            inflation_annual: modelInputs.inflation_annual + scenario.inflationAdj,
            monthly_spending:
              modelInputs.monthly_spending * (1 + scenario.spendingAdj),
          };

          const response = await apiClient.axiosClient.post('/simulation/run', {
            client_info: clientInfo,
            model_inputs: adjustedInputs,
          });

          return {
            ...scenario,
            successProbability: response.data.metrics.success_probability,
            endingMedian: response.data.metrics.ending_median,
          };
        })
      );

      setScenarios(results);
    } catch (error) {
      console.error('Failed to run scenarios:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const runSensitivityAnalysis = async () => {
    // Check if we have base inputs
    if (!modelInputs.starting_portfolio || modelInputs.starting_portfolio === 0) {
      alert('Please configure your inputs and run a base simulation first.');
      navigate('/inputs');
      return;
    }

    setIsSensitivityRunning(true);
    setSensitivityData([]);
    
    try {
      // Define parameters to analyze
      const parametersToAnalyze = [
        'equity_return_annual',
        'fi_return_annual', 
        'inflation_annual',
        'monthly_spending',
      ];
      
      // Transform modelInputs to match backend schema exactly
      // Remove frontend-only fields and map field names correctly
      const backendInputs = {
        starting_portfolio: modelInputs.starting_portfolio,
        years_to_model: modelInputs.years_to_model,
        current_age: modelInputs.current_age,
        horizon_age: modelInputs.horizon_age,
        monthly_income: 0, // Default to 0
        monthly_spending: modelInputs.monthly_spending,
        inflation_annual: modelInputs.inflation_annual,
        spending_rule: modelInputs.spending_rule,
        spending_pct_annual: modelInputs.spending_pct_annual,
        equity_pct: modelInputs.equity_pct,
        fi_pct: modelInputs.fi_pct,
        cash_pct: modelInputs.cash_pct,
        equity_return_annual: modelInputs.equity_return_annual,
        fi_return_annual: modelInputs.fi_return_annual,
        cash_return_annual: modelInputs.cash_return_annual,
        equity_vol_annual: modelInputs.equity_vol_annual,
        fi_vol_annual: modelInputs.fi_vol_annual,
        cash_vol_annual: modelInputs.cash_vol_annual,
        n_scenarios: modelInputs.n_scenarios,
        one_time_cf: modelInputs.one_time_cf || 0,
        one_time_cf_month: modelInputs.one_time_cf_month || 0,
        taxable_pct: modelInputs.taxable_pct,
        ira_pct: modelInputs.ira_pct,
        roth_pct: modelInputs.roth_pct,
        taxable_basis_pct: 0.6, // Default
        tax_rate: modelInputs.tax_rate,
        filing_status: 'single', // Default
        state_tax_rate: 0.0, // Default
        rmd_age: modelInputs.rmd_age,
        use_tax_optimization: true, // Default
        optimize_roth_conversions: false, // Default
        roth_conversion_start_age: modelInputs.roth_conversion_start_age || 60,
        roth_conversion_end_age: modelInputs.roth_conversion_end_age || 72,
        avoid_irmaa: true, // Default
        social_security_monthly: modelInputs.social_security_monthly || 0,
        ss_start_age: modelInputs.ss_start_age || 67,
        pension_monthly: modelInputs.pension_monthly || 0,
        pension_start_age: modelInputs.pension_start_age || 65,
        monthly_healthcare: modelInputs.healthcare_monthly || 0,
        healthcare_start_age: modelInputs.healthcare_start_age || 65,
        healthcare_inflation: modelInputs.healthcare_inflation || 0.05,
        roth_conversion_annual: modelInputs.roth_conversion_annual || 0,
        estate_tax_exemption: modelInputs.estate_tax_exemption || 13610000,
        legacy_goal: modelInputs.legacy_goal || 0,
        use_actuarial_tables: modelInputs.use_actuarial_tables || false,
        health_adjustment: modelInputs.health_adjustment || 0,
        use_glide_path: modelInputs.use_glide_path || false,
        target_equity_at_end: modelInputs.target_equity_pct || 0.4, // Map field name
        use_lifestyle_phases: modelInputs.use_lifestyle_phases || false,
        slow_go_age: modelInputs.go_go_end_age || 75, // Map field name
        no_go_age: modelInputs.slow_go_end_age || 85, // Map field name
        slow_go_spending_pct: modelInputs.go_go_spending_multiplier || 1.0, // Map field name
        no_go_spending_pct: modelInputs.no_go_spending_multiplier || 0.6, // Map field name
        use_guardrails: modelInputs.use_guardrails || false,
        upper_guardrail: modelInputs.upper_guardrail || 0.2,
        lower_guardrail: modelInputs.lower_guardrail || 0.15,
      };
      
      // Use more practical variation ranges for each parameter
      const variationsByParameter: Record<string, number[]> = {
        'equity_return_annual': [-0.04, -0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03, 0.04],
        'fi_return_annual': [-0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03],
        'inflation_annual': [-0.02, -0.01, 0, 0.01, 0.02, 0.03],
        'monthly_spending': [-0.30, -0.20, -0.10, 0, 0.10, 0.20, 0.30],
      };

      // Run sensitivity analysis for all parameters in parallel
      const allResults = await Promise.all(
        parametersToAnalyze.map(async (param) => {
          try {
            let variations = variationsByParameter[param] || [-0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03];
            
            // For monthly_spending, convert percentage variations to actual dollar amounts
            // Note: monthly_spending is negative (outflow), so we need to handle the math correctly
            if (param === 'monthly_spending') {
              const baseSpending = Math.abs(modelInputs.monthly_spending); // Work with positive amount
              variations = variations.map(pct => -baseSpending * (1 + pct)); // Keep negative sign
            }
            
            console.log(`Running sensitivity for ${param} with variations:`, variations);
            const response = await apiClient.axiosClient.post('/simulation/sensitivity', {
              inputs: backendInputs,
              parameter: param,
              variations: variations,
            });

            console.log(`Got ${response.data.results.length} results for ${param}`);
            
            // Transform results for this parameter
            return response.data.results.map((result: any) => {
              let displayVariation = result.parameter_value;
              
              // For monthly_spending, convert back to percentage for display
              if (param === 'monthly_spending') {
                const baseSpending = modelInputs.monthly_spending;
                // Calculate percentage change from baseline
                displayVariation = (result.parameter_value - baseSpending) / Math.abs(baseSpending);
              }
              
              return {
                parameter: param,
                variation: displayVariation,
                successProbability: result.success_probability,
                impact: result.success_probability,
              };
            });
          } catch (error: any) {
            console.error(`Failed to analyze ${param}:`, error);
            console.error(`Error details:`, error.response?.data);
            return [];
          }
        })
      );

      // Flatten all results
      const combinedResults = allResults.flat();
      console.log(`Total combined results: ${combinedResults.length}`);
      setSensitivityData(combinedResults);
      
      if (combinedResults.length === 0) {
        alert('No sensitivity results were generated. Please check your inputs and try again.\n\nMake sure you have run a base simulation first and all required fields are filled in.');
      }
    } catch (error: any) {
      console.error('Failed to run sensitivity analysis:', error);
      console.error('Error details:', error.response?.data);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to run sensitivity analysis';
      alert(`Error: ${errorMsg}`);
    } finally {
      setIsSensitivityRunning(false);
    }
  };

  const formatPercent = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(value);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getSuccessVariant = (probability?: number): 'success' | 'warning' | 'error' | 'default' => {
    if (probability === undefined) return 'default';
    if (probability >= 0.85) return 'success';
    if (probability >= 0.70) return 'warning';
    return 'error';
  };

  if (!hasRunSimulation) {
    return (
      <div className="space-y-xl">
        <SectionHeader
          title="Scenario Analysis"
          description="Compare different market conditions and planning assumptions"
          icon={<GitCompare size={28} />}
        />

        <Card padding="none">
          <EmptyState
            icon={<GitCompare size={64} strokeWidth={1.5} />}
            title="Run Base Simulation First"
            description="You need to run a base simulation before comparing alternative scenarios. Configure your inputs and run a Monte Carlo simulation to get started."
            action={{
              label: 'Go to Inputs',
              onClick: () => window.location.href = '/inputs',
              variant: 'primary',
            }}
          />
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 lg:space-y-xl pb-16 lg:pb-24">
      {/* Header */}
      <SectionHeader
        title="Scenario Analysis"
        description="Compare different market conditions and planning assumptions"
        icon={<GitCompare size={28} />}
        actions={
          <div className="flex gap-2 lg:gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={runScenarios}
              loading={isRunning}
              disabled={isRunning || scenarios.length === 0}
              icon={<Zap size={16} />}
            >
              <span className="hidden sm:inline">Run All Scenarios</span>
              <span className="sm:hidden">Run All</span>
            </Button>
          </div>
        }
      />

      {/* Scenario Templates */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Quick Templates
          </h3>
          <p className="text-body text-text-tertiary">
            Add common scenario variations with pre-configured adjustments
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4">
          {ScenarioTemplates.map((template, idx) => (
            <button
              key={idx}
              onClick={() => addScenario(template)}
              className="p-4 text-left rounded-md border border-background-border hover:border-accent-gold hover:bg-background-hover transition-all"
            >
              <div className="flex items-start gap-3 mb-2">
                <div className="text-accent-gold flex-shrink-0">
                  {template.icon}
                </div>
                <div>
                  <h4 className="text-h4 font-semibold text-text-primary mb-1">
                    {template.name}
                  </h4>
                  <p className="text-small text-text-tertiary">
                    {template.description}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </Card>

      {/* Scenario Builder */}
      <Card padding="lg">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-h3 font-display text-text-primary mb-2">
              Scenario Configurations
            </h3>
            <p className="text-body text-text-tertiary">
              Adjust parameters for each scenario to test different assumptions
            </p>
          </div>
          <Button
            variant="tertiary"
            size="sm"
            onClick={() => addScenario()}
            icon={<Plus size={16} />}
          >
            Add Custom Scenario
          </Button>
        </div>

        <div className="space-y-6">
          {scenarios.map((scenario) => (
            <div
              key={scenario.id}
              className="p-6 bg-background-hover rounded-md border border-background-border"
            >
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <input
                    type="text"
                    value={scenario.name}
                    onChange={(e) => updateScenario(scenario.id, { name: e.target.value })}
                    className="text-h4 font-display font-semibold text-text-primary bg-transparent border-none outline-none focus:outline-none mb-1"
                  />
                  {scenario.id === '1' && (
                    <Badge variant="info" size="sm">Base Case</Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {scenario.id !== '1' && (
                    <>
                      <button
                        onClick={() => duplicateScenario(scenario)}
                        className="p-2 text-text-tertiary hover:text-text-primary hover:bg-background-border rounded transition-colors"
                        title="Duplicate scenario"
                      >
                        <Copy size={16} />
                      </button>
                      <button
                        onClick={() => removeScenario(scenario.id)}
                        className="p-2 text-text-tertiary hover:text-status-error-base hover:bg-status-error-base hover:bg-opacity-10 rounded transition-colors"
                        title="Remove scenario"
                      >
                        <X size={16} />
                      </button>
                    </>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div>
                  <Slider
                    label="Equity Return Adjustment"
                    value={scenario.equityReturnAdj}
                    onChange={(value) => updateScenario(scenario.id, { equityReturnAdj: value })}
                    min={-0.05}
                    max={0.05}
                    step={0.005}
                    formatValue={(v) => `${v >= 0 ? '+' : ''}${formatPercent(v)}`}
                  />
                </div>
                <div>
                  <Slider
                    label="Fixed Income Return Adj."
                    value={scenario.fiReturnAdj}
                    onChange={(value) => updateScenario(scenario.id, { fiReturnAdj: value })}
                    min={-0.05}
                    max={0.05}
                    step={0.005}
                    formatValue={(v) => `${v >= 0 ? '+' : ''}${formatPercent(v)}`}
                  />
                </div>
                <div>
                  <Slider
                    label="Inflation Adjustment"
                    value={scenario.inflationAdj}
                    onChange={(value) => updateScenario(scenario.id, { inflationAdj: value })}
                    min={-0.03}
                    max={0.03}
                    step={0.005}
                    formatValue={(v) => `${v >= 0 ? '+' : ''}${formatPercent(v)}`}
                  />
                </div>
                <div>
                  <Slider
                    label="Spending Adjustment"
                    value={scenario.spendingAdj}
                    onChange={(value) => updateScenario(scenario.id, { spendingAdj: value })}
                    min={-0.5}
                    max={0.5}
                    step={0.05}
                    formatValue={(v) => `${v >= 0 ? '+' : ''}${formatPercent(v)}`}
                  />
                </div>
              </div>

              {/* Results */}
              {scenario.successProbability !== undefined && (
                <div className="mt-6 pt-6 border-t border-background-border">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-background-base rounded-sm border border-background-border">
                      <p className="text-small text-text-tertiary mb-2">Success Probability</p>
                      <div className="flex items-center gap-3">
                        <p className={`text-h2 font-display ${
                          scenario.successProbability >= 0.85
                            ? 'text-status-success-base'
                            : scenario.successProbability >= 0.70
                            ? 'text-status-warning-base'
                            : 'text-status-error-base'
                        }`}>
                          {formatPercent(scenario.successProbability)}
                        </p>
                        <Badge variant={getSuccessVariant(scenario.successProbability)} size="sm">
                          {scenario.successProbability >= 0.85
                            ? 'Strong'
                            : scenario.successProbability >= 0.70
                            ? 'Moderate'
                            : 'Low'}
                        </Badge>
                      </div>
                    </div>
                    <div className="p-4 bg-background-base rounded-sm border border-background-border">
                      <p className="text-small text-text-tertiary mb-2">Median Ending Balance</p>
                      <p className="text-h2 font-display text-text-primary">
                        {formatCurrency(scenario.endingMedian || 0)}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Comparison Table */}
      {scenarios.some(s => s.successProbability !== undefined) && (
        <Card padding="lg">
          <div className="mb-6">
            <h3 className="text-h3 font-display text-text-primary mb-2">
              Scenario Comparison
            </h3>
            <p className="text-body text-text-tertiary">
              Side-by-side comparison of all scenario results
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-background-border">
                  <th className="text-left py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    Scenario
                  </th>
                  <th className="text-right py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    Success %
                  </th>
                  <th className="text-right py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    Median End
                  </th>
                  <th className="text-right py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    Equity Adj
                  </th>
                  <th className="text-right py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    FI Adj
                  </th>
                  <th className="text-right py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    Inflation Adj
                  </th>
                  <th className="text-right py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    Spending Adj
                  </th>
                </tr>
              </thead>
              <tbody>
                {scenarios
                  .filter(s => s.successProbability !== undefined)
                  .map((scenario) => (
                    <tr key={scenario.id} className="border-b border-background-border hover:bg-background-hover transition-colors">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="text-body font-medium text-text-primary">
                            {scenario.name}
                          </span>
                          {scenario.id === '1' && (
                            <Badge variant="info" size="sm">Base</Badge>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <span className={`text-body font-semibold ${
                            scenario.successProbability! >= 0.85
                              ? 'text-status-success-base'
                              : scenario.successProbability! >= 0.70
                              ? 'text-status-warning-base'
                              : 'text-status-error-base'
                          }`}>
                            {formatPercent(scenario.successProbability!)}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right text-body text-text-primary">
                        {formatCurrency(scenario.endingMedian!)}
                      </td>
                      <td className="py-3 px-4 text-right text-body text-text-secondary">
                        {scenario.equityReturnAdj >= 0 ? '+' : ''}{formatPercent(scenario.equityReturnAdj)}
                      </td>
                      <td className="py-3 px-4 text-right text-body text-text-secondary">
                        {scenario.fiReturnAdj >= 0 ? '+' : ''}{formatPercent(scenario.fiReturnAdj)}
                      </td>
                      <td className="py-3 px-4 text-right text-body text-text-secondary">
                        {scenario.inflationAdj >= 0 ? '+' : ''}{formatPercent(scenario.inflationAdj)}
                      </td>
                      <td className="py-3 px-4 text-right text-body text-text-secondary">
                        {scenario.spendingAdj >= 0 ? '+' : ''}{formatPercent(scenario.spendingAdj)}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Sensitivity Analysis */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Multi-Parameter Sensitivity Analysis
          </h3>
          <p className="text-body text-text-tertiary">
            Analyze how changes in key parameters affect plan success probability. Compare sensitivity across equity returns, fixed income returns, inflation, and spending levels.
          </p>
        </div>

        <div className="flex items-center justify-between mb-6 p-4 bg-background-elevated border border-background-border rounded-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-accent-gold bg-opacity-10 flex items-center justify-center">
              <Zap size={20} className="text-accent-gold" />
            </div>
            <div>
              <p className="text-body font-medium text-text-primary">
                Comprehensive Analysis
              </p>
              <p className="text-small text-text-tertiary">
                Tests {sensitivityData.length > 0 ? `${new Set(sensitivityData.map(d => d.parameter)).size} parameters` : '4 key parameters'} with multiple variations each
              </p>
            </div>
          </div>
          <Button
            variant="secondary"
            size="md"
            onClick={runSensitivityAnalysis}
            loading={isSensitivityRunning}
            disabled={isSensitivityRunning}
            icon={<Zap size={18} />}
          >
            {isSensitivityRunning ? 'Analyzing...' : 'Run Full Analysis'}
          </Button>
        </div>

        {sensitivityData.length > 0 ? (
          <SensitivityHeatMap
            data={sensitivityData}
            height={500}
          />
        ) : (
          <div className="h-96 flex flex-col items-center justify-center text-center border-2 border-dashed border-background-border rounded-lg">
            <div className="w-16 h-16 rounded-full bg-background-elevated flex items-center justify-center mb-4">
              <TrendingUp size={32} className="text-text-tertiary" />
            </div>
            <h4 className="text-h4 font-semibold text-text-primary mb-2">
              Ready to Analyze Sensitivity
            </h4>
            <p className="text-body text-text-tertiary max-w-md mb-6">
              Click "Run Full Analysis" to test how different market conditions and spending levels affect your plan's success probability.
            </p>
            <div className="grid grid-cols-2 gap-4 text-left max-w-2xl">
              <div className="p-3 bg-background-elevated rounded-lg border border-background-border">
                <p className="text-small font-semibold text-text-primary mb-1">Will Analyze:</p>
                <ul className="text-small text-text-tertiary space-y-1">
                  <li>• Equity returns (±4%)</li>
                  <li>• Fixed income returns (±3%)</li>
                </ul>
              </div>
              <div className="p-3 bg-background-elevated rounded-lg border border-background-border">
                <p className="text-small font-semibold text-text-primary mb-1">And Also:</p>
                <ul className="text-small text-text-tertiary space-y-1">
                  <li>• Inflation rates (±3%)</li>
                  <li>• Spending levels (±30%)</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default ScenariosPage;
