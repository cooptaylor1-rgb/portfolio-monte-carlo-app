/**
 * Scenarios Page - Run and compare different scenarios
 */
import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import apiClient from '../lib/api';
import { Slider, SelectBox } from '../components/forms';
import { SensitivityHeatMap } from '../components/charts';
import { Plus, X } from 'lucide-react';

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

const ScenariosPage: React.FC = () => {
  const { modelInputs, clientInfo } = useSimulationStore();
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

  const addScenario = () => {
    const newId = (scenarios.length + 1).toString();
    setScenarios([
      ...scenarios,
      {
        id: newId,
        name: `Scenario ${newId}`,
        equityReturnAdj: 0,
        fiReturnAdj: 0,
        inflationAdj: 0,
        spendingAdj: 0,
      },
    ]);
  };

  const removeScenario = (id: string) => {
    if (scenarios.length > 1) {
      setScenarios(scenarios.filter((s) => s.id !== id));
    }
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
    setIsRunning(true);
    try {
      const variations = [-0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03];
      const response = await apiClient.axiosClient.post(
        '/simulation/sensitivity',
        {
          inputs: modelInputs,
          parameter: selectedParameter,
          variations,
        }
      );

      const heatmapData = response.data.results.map((result: any, index: number) => ({
        parameter: selectedParameter.replace(/_/g, ' ').toUpperCase(),
        variation: variations[index],
        successProbability: result.success_probability,
      }));

      setSensitivityData(heatmapData);
    } catch (error) {
      console.error('Failed to run sensitivity analysis:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const formatPercent = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
      signDisplay: 'always',
    }).format(value);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(value);
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h2 className="text-3xl font-bold text-text-primary mb-2">
          Scenarios & Analysis
        </h2>
        <p className="text-text-secondary">
          Run Monte Carlo simulations, stress tests, and what-if scenarios
        </p>
      </div>

      {/* Scenario Builder */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-text-primary">
            Scenario Builder
          </h3>
          <button
            onClick={addScenario}
            className="flex items-center gap-2 px-4 py-2 bg-brand-gold text-primary-900 rounded-lg hover:bg-brand-gold-dark transition-colors font-semibold"
          >
            <Plus size={20} />
            Add Scenario
          </button>
        </div>

        <div className="space-y-4">
          {scenarios.map((scenario) => (
            <div
              key={scenario.id}
              className="p-4 bg-surface-800 rounded-lg border border-surface-700"
            >
              <div className="flex items-center justify-between mb-4">
                <input
                  type="text"
                  value={scenario.name}
                  onChange={(e) =>
                    updateScenario(scenario.id, { name: e.target.value })
                  }
                  className="text-lg font-semibold bg-transparent border-none focus:outline-none text-text-primary"
                />
                {scenarios.length > 1 && (
                  <button
                    onClick={() => removeScenario(scenario.id)}
                    className="p-1 text-text-secondary hover:text-error-500 transition-colors"
                  >
                    <X size={20} />
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Slider
                    label="Equity Return Adjustment"
                    value={scenario.equityReturnAdj * 100}
                    onChange={(v) =>
                      updateScenario(scenario.id, { equityReturnAdj: v / 100 })
                    }
                    min={-5}
                    max={5}
                    step={0.1}
                    formatValue={(v) => formatPercent(v / 100)}
                  />
                </div>
                <div>
                  <Slider
                    label="Fixed Income Return Adjustment"
                    value={scenario.fiReturnAdj * 100}
                    onChange={(v) =>
                      updateScenario(scenario.id, { fiReturnAdj: v / 100 })
                    }
                    min={-5}
                    max={5}
                    step={0.1}
                    formatValue={(v) => formatPercent(v / 100)}
                  />
                </div>
                <div>
                  <Slider
                    label="Inflation Adjustment"
                    value={scenario.inflationAdj * 100}
                    onChange={(v) =>
                      updateScenario(scenario.id, { inflationAdj: v / 100 })
                    }
                    min={-3}
                    max={3}
                    step={0.1}
                    formatValue={(v) => formatPercent(v / 100)}
                  />
                </div>
                <div>
                  <Slider
                    label="Spending Adjustment"
                    value={scenario.spendingAdj * 100}
                    onChange={(v) =>
                      updateScenario(scenario.id, { spendingAdj: v / 100 })
                    }
                    min={-50}
                    max={50}
                    step={1}
                    formatValue={(v) => formatPercent(v / 100)}
                  />
                </div>
              </div>

              {scenario.successProbability !== undefined && (
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div className="p-3 bg-surface-900 rounded-lg">
                    <p className="text-sm text-text-secondary mb-1">
                      Success Probability
                    </p>
                    <p className="text-xl font-bold text-text-primary">
                      {(scenario.successProbability * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="p-3 bg-surface-900 rounded-lg">
                    <p className="text-sm text-text-secondary mb-1">
                      Median Ending Balance
                    </p>
                    <p className="text-xl font-bold text-text-primary">
                      {scenario.endingMedian
                        ? formatCurrency(scenario.endingMedian)
                        : '--'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <button
          onClick={runScenarios}
          disabled={isRunning}
          className="mt-6 w-full px-6 py-3 bg-brand-gold text-primary-900 rounded-lg hover:bg-brand-gold-dark transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isRunning ? 'Running Scenarios...' : 'Run All Scenarios'}
        </button>
      </div>

      {/* Comparison Table */}
      {scenarios.some((s) => s.successProbability !== undefined) && (
        <div className="card p-6">
          <h3 className="text-xl font-semibold text-text-primary mb-4">
            Scenario Comparison
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-surface-700">
                  <th className="text-left py-3 px-4 text-text-secondary font-medium">
                    Scenario
                  </th>
                  <th className="text-right py-3 px-4 text-text-secondary font-medium">
                    Success %
                  </th>
                  <th className="text-right py-3 px-4 text-text-secondary font-medium">
                    Median End
                  </th>
                  <th className="text-right py-3 px-4 text-text-secondary font-medium">
                    Equity Adj
                  </th>
                  <th className="text-right py-3 px-4 text-text-secondary font-medium">
                    Inflation Adj
                  </th>
                </tr>
              </thead>
              <tbody>
                {scenarios.map((scenario) => (
                  <tr
                    key={scenario.id}
                    className="border-b border-surface-800 hover:bg-surface-800 transition-colors"
                  >
                    <td className="py-3 px-4 text-text-primary font-medium">
                      {scenario.name}
                    </td>
                    <td className="text-right py-3 px-4 text-text-primary">
                      {scenario.successProbability !== undefined
                        ? `${(scenario.successProbability * 100).toFixed(1)}%`
                        : '--'}
                    </td>
                    <td className="text-right py-3 px-4 text-text-primary">
                      {scenario.endingMedian
                        ? formatCurrency(scenario.endingMedian)
                        : '--'}
                    </td>
                    <td className="text-right py-3 px-4 text-text-secondary">
                      {formatPercent(scenario.equityReturnAdj)}
                    </td>
                    <td className="text-right py-3 px-4 text-text-secondary">
                      {formatPercent(scenario.inflationAdj)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sensitivity Analysis */}
      <div className="card p-6">
        <h3 className="text-xl font-semibold text-text-primary mb-4">
          Sensitivity Analysis
        </h3>
        <div className="mb-6">
          <SelectBox
            label="Parameter to Analyze"
            value={selectedParameter}
            onChange={(value) => setSelectedParameter(value.toString())}
            options={[
              { value: 'equity_return_annual', label: 'Equity Return' },
              { value: 'fi_return_annual', label: 'Fixed Income Return' },
              { value: 'inflation_annual', label: 'Inflation Rate' },
              { value: 'monthly_spending', label: 'Monthly Spending' },
              { value: 'equity_pct', label: 'Equity Allocation' },
            ]}
          />
          <button
            onClick={runSensitivityAnalysis}
            disabled={isRunning}
            className="mt-4 px-6 py-2 bg-brand-gold text-primary-900 rounded-lg hover:bg-brand-gold-dark transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunning ? 'Analyzing...' : 'Run Sensitivity Analysis'}
          </button>
        </div>

        {sensitivityData.length > 0 && (
          <SensitivityHeatMap data={sensitivityData} height={300} />
        )}
      </div>
    </div>
  );
};

export default ScenariosPage;
