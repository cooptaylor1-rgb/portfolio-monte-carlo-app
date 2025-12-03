/**
 * Scenarios Page - Run and compare different scenarios
 * Redesigned with templates, visual comparison, and better UX
 */
import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import apiClient from '../lib/api';
import { Slider, SelectBox } from '../components/forms';
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
  const [selectedParameter, setSelectedParameter] = useState('equity_return_annual');
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
    setIsSensitivityRunning(true);
    try {
      const variations = [-0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03];
      const results = await Promise.all(
        variations.map(async (variation) => {
          const response = await apiClient.axiosClient.post('/simulation/sensitivity', {
            client_info: clientInfo,
            model_inputs: modelInputs,
            parameter: selectedParameter,
            variation: variation,
          });

          return {
            parameter: selectedParameter,
            variation: variation,
            successProbability: response.data.metrics.success_probability,
            impact: response.data.metrics.success_probability,
          };
        })
      );

      setSensitivityData(results);
    } catch (error) {
      console.error('Failed to run sensitivity analysis:', error);
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
    <div className="space-y-xl pb-24">
      {/* Header */}
      <SectionHeader
        title="Scenario Analysis"
        description="Compare different market conditions and planning assumptions"
        icon={<GitCompare size={28} />}
        actions={
          <div className="flex gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={runScenarios}
              loading={isRunning}
              disabled={isRunning || scenarios.length === 0}
              icon={<Zap size={16} />}
            >
              Run All Scenarios
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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
            Sensitivity Analysis
          </h3>
          <p className="text-body text-text-tertiary">
            Analyze how sensitive your portfolio is to changes in key parameters
          </p>
        </div>

        <div className="flex items-end gap-4 mb-6">
          <div className="flex-1">
            <SelectBox
              label="Parameter to Analyze"
              value={selectedParameter}
              onChange={(value) => setSelectedParameter(value.toString())}
              options={[
                { value: 'equity_return_annual', label: 'Equity Return' },
                { value: 'fi_return_annual', label: 'Fixed Income Return' },
                { value: 'inflation_annual', label: 'Inflation Rate' },
                { value: 'monthly_spending', label: 'Monthly Spending' },
              ]}
            />
          </div>
          <Button
            variant="secondary"
            size="md"
            onClick={runSensitivityAnalysis}
            loading={isSensitivityRunning}
            disabled={isSensitivityRunning}
            icon={<Zap size={18} />}
          >
            Analyze Sensitivity
          </Button>
        </div>

        {sensitivityData.length > 0 && (
          <div className="h-96">
            <SensitivityHeatMap
              data={sensitivityData}
              height={384}
            />
          </div>
        )}
      </Card>
    </div>
  );
};

export default ScenariosPage;
