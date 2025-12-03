/**
 * Reports Page - Generate and download analysis reports
 */
import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { FileText, Download, Eye, Printer } from 'lucide-react';
import { Link } from 'react-router-dom';

const ReportsPage: React.FC = () => {
  const { simulationResults, clientInfo, modelInputs, hasRunSimulation } =
    useSimulationStore();
  const [isGenerating, setIsGenerating] = useState(false);

  const generateReport = async (_format: 'pdf' | 'excel') => {
    setIsGenerating(true);
    try {
      const reportData = {
        client_info: clientInfo,
        model_inputs: modelInputs,
        simulation_results: simulationResults,
        generated_at: new Date().toISOString(),
      };

      const blob = new Blob([JSON.stringify(reportData, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `portfolio-analysis-${clientInfo.client_name || 'report'}-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const printReport = () => {
    window.print();
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(value);
  };

  if (!hasRunSimulation || !simulationResults) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-text-primary mb-2">Reports</h2>
          <p className="text-text-secondary">
            Generate comprehensive analysis reports
          </p>
        </div>

        <div className="card p-8 text-center">
          <FileText className="w-16 h-16 text-text-secondary mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-text-primary mb-2">
            No Simulation Data
          </h3>
          <p className="text-text-secondary mb-6">
            Run a simulation first to generate reports
          </p>
          <Link
            to="/inputs"
            className="inline-block px-6 py-3 bg-brand-gold text-primary-900 rounded-lg hover:bg-brand-gold-dark transition-colors font-semibold"
          >
            Go to Inputs
          </Link>
        </div>
      </div>
    );
  }

  const metrics = simulationResults.metrics;

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h2 className="text-3xl font-bold text-text-primary mb-2">Reports</h2>
        <p className="text-text-secondary">
          Generate and download comprehensive analysis reports
        </p>
      </div>

      {/* Report Actions */}
      <div className="card p-6">
        <h3 className="text-xl font-semibold text-text-primary mb-4">
          Report Generation
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => generateReport('pdf')}
            disabled={isGenerating}
            className="flex items-center justify-center gap-3 p-4 bg-surface-800 rounded-lg border border-surface-700 hover:border-brand-gold transition-colors disabled:opacity-50"
          >
            <Download size={24} className="text-brand-gold" />
            <div className="text-left">
              <p className="font-semibold text-text-primary">Download Data</p>
              <p className="text-sm text-text-secondary">JSON format</p>
            </div>
          </button>

          <button
            onClick={() => generateReport('excel')}
            disabled={isGenerating}
            className="flex items-center justify-center gap-3 p-4 bg-surface-800 rounded-lg border border-surface-700 hover:border-brand-gold transition-colors disabled:opacity-50"
          >
            <Download size={24} className="text-brand-gold" />
            <div className="text-left">
              <p className="font-semibold text-text-primary">Download Excel</p>
              <p className="text-sm text-text-secondary">Data export</p>
            </div>
          </button>

          <button
            onClick={printReport}
            className="flex items-center justify-center gap-3 p-4 bg-surface-800 rounded-lg border border-surface-700 hover:border-brand-gold transition-colors"
          >
            <Printer size={24} className="text-brand-gold" />
            <div className="text-left">
              <p className="font-semibold text-text-primary">Print Report</p>
              <p className="text-sm text-text-secondary">Print view</p>
            </div>
          </button>
        </div>
      </div>

      {/* Report Preview */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-6">
          <Eye size={24} className="text-brand-gold" />
          <h3 className="text-xl font-semibold text-text-primary">
            Report Preview
          </h3>
        </div>

        <div className="space-y-6">
          {/* Executive Summary */}
          <div>
            <h4 className="text-lg font-semibold text-text-primary mb-4 border-b border-surface-700 pb-2">
              Executive Summary
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h5 className="text-sm font-semibold text-text-secondary uppercase mb-3">
                  Client Information
                </h5>
                <dl className="space-y-2">
                  <div className="flex justify-between">
                    <dt className="text-text-secondary">Name:</dt>
                    <dd className="text-text-primary font-medium">
                      {clientInfo.client_name || 'N/A'}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-text-secondary">Date:</dt>
                    <dd className="text-text-primary font-medium">
                      {clientInfo.report_date || 'N/A'}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-text-secondary">Advisor:</dt>
                    <dd className="text-text-primary font-medium">
                      {clientInfo.advisor_name || 'N/A'}
                    </dd>
                  </div>
                </dl>
              </div>

              <div>
                <h5 className="text-sm font-semibold text-text-secondary uppercase mb-3">
                  Portfolio Overview
                </h5>
                <dl className="space-y-2">
                  <div className="flex justify-between">
                    <dt className="text-text-secondary">Starting Value:</dt>
                    <dd className="text-text-primary font-medium">
                      {formatCurrency(modelInputs.starting_portfolio)}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-text-secondary">Time Horizon:</dt>
                    <dd className="text-text-primary font-medium">
                      {modelInputs.years_to_model} years
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-text-secondary">Allocation:</dt>
                    <dd className="text-text-primary font-medium text-sm">
                      {formatPercent(modelInputs.equity_pct)} /{' '}
                      {formatPercent(modelInputs.fi_pct)} /{' '}
                      {formatPercent(modelInputs.cash_pct)}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>

          {/* Key Findings */}
          <div>
            <h4 className="text-lg font-semibold text-text-primary mb-4 border-b border-surface-700 pb-2">
              Key Findings
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-surface-800 rounded-lg">
                <p className="text-sm text-text-secondary mb-1">Success Rate</p>
                <p className="text-2xl font-bold text-text-primary">
                  {formatPercent(metrics.success_probability)}
                </p>
              </div>
              <div className="p-4 bg-surface-800 rounded-lg">
                <p className="text-sm text-text-secondary mb-1">Median End</p>
                <p className="text-2xl font-bold text-text-primary">
                  {formatCurrency(metrics.ending_median)}
                </p>
              </div>
              <div className="p-4 bg-surface-800 rounded-lg">
                <p className="text-sm text-text-secondary mb-1">10th %ile</p>
                <p className="text-2xl font-bold text-text-primary">
                  {formatCurrency(metrics.ending_p10)}
                </p>
              </div>
              <div className="p-4 bg-surface-800 rounded-lg">
                <p className="text-sm text-text-secondary mb-1">90th %ile</p>
                <p className="text-2xl font-bold text-text-primary">
                  {formatCurrency(metrics.ending_p90)}
                </p>
              </div>
            </div>
          </div>

          {/* Risk Analysis */}
          <div>
            <h4 className="text-lg font-semibold text-text-primary mb-4 border-b border-surface-700 pb-2">
              Risk Analysis
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-surface-800 rounded-lg">
                <p className="text-sm text-text-secondary mb-2">
                  Depletion Probability
                </p>
                <p className="text-3xl font-bold text-text-primary mb-1">
                  {formatPercent(metrics.depletion_probability)}
                </p>
                <p className="text-xs text-text-secondary">
                  Probability of running out of funds
                </p>
              </div>
              <div className="p-4 bg-surface-800 rounded-lg">
                <p className="text-sm text-text-secondary mb-2">Shortfall Risk</p>
                <p className="text-3xl font-bold text-text-primary mb-1">
                  {formatPercent(metrics.shortfall_risk)}
                </p>
                <p className="text-xs text-text-secondary">
                  Risk of not meeting objectives
                </p>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          <div>
            <h4 className="text-lg font-semibold text-text-primary mb-4 border-b border-surface-700 pb-2">
              Recommendations
            </h4>
            <div className="space-y-3">
              {metrics.success_probability < 0.7 && (
                <div className="p-4 bg-error-900 bg-opacity-20 border border-error-500 rounded-lg">
                  <p className="text-error-400 font-semibold mb-1">
                    ⚠️ Low Success Probability
                  </p>
                  <p className="text-text-secondary text-sm">
                    Consider increasing contributions, reducing expenses, or
                    adjusting return assumptions.
                  </p>
                </div>
              )}
              {metrics.success_probability >= 0.7 &&
                metrics.success_probability < 0.85 && (
                  <div className="p-4 bg-warning-900 bg-opacity-20 border border-warning-500 rounded-lg">
                    <p className="text-warning-400 font-semibold mb-1">
                      ⚡ Moderate Success Probability
                    </p>
                    <p className="text-text-secondary text-sm">
                      Plan appears reasonable but may benefit from optimization.
                    </p>
                  </div>
                )}
              {metrics.success_probability >= 0.85 && (
                <div className="p-4 bg-success-900 bg-opacity-20 border border-success-500 rounded-lg">
                  <p className="text-success-400 font-semibold mb-1">
                    ✓ Strong Success Probability
                  </p>
                  <p className="text-text-secondary text-sm">
                    Plan shows strong likelihood of success. Consider additional
                    goals or legacy planning.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="card p-4 bg-surface-900 border-surface-700">
        <p className="text-xs text-text-secondary text-center">
          This report is for illustrative purposes only and should not be
          considered as investment advice. Consult with a qualified financial
          advisor before making investment decisions.
        </p>
      </div>
    </div>
  );
};

export default ReportsPage;
