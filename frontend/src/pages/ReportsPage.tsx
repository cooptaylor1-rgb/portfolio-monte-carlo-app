/**
 * Reports Page - Generate and download analysis reports
 * Redesigned with better preview layout and export options
 */
import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { useNavigate } from 'react-router-dom';
import { SectionHeader, Button, Card, Badge, EmptyState } from '../components/ui';
import { FileText, Download, Printer, FileSpreadsheet, FileImage, Share2, ChevronDown } from 'lucide-react';

const ReportsPage: React.FC = () => {
  const navigate = useNavigate();
  const { simulationResults, clientInfo, modelInputs, hasRunSimulation } = useSimulationStore();
  const [isGenerating, setIsGenerating] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    clientInfo: true,
    portfolio: true,
    keyFindings: true,
    risk: true,
    recommendations: true,
  });

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections({ ...expandedSections, [section]: !expandedSections[section] });
  };

  const generateReport = async (format: 'pdf' | 'excel' | 'json' | 'ppt') => {
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
      a.download = `portfolio-analysis-${clientInfo.client_name || 'report'}-${Date.now()}.${format}`;
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

  const shareReport = () => {
    // TODO: Implement share functionality
    console.log('Share report');
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

  const getSuccessVariant = (probability: number): 'success' | 'warning' | 'error' => {
    if (probability >= 0.85) return 'success';
    if (probability >= 0.70) return 'warning';
    return 'error';
  };

  if (!hasRunSimulation || !simulationResults) {
    return (
      <div className="space-y-xl">
        <SectionHeader
          title="Analysis Reports"
          description="Generate comprehensive portfolio analysis reports"
          icon={<FileText size={28} />}
        />

        <Card padding="none">
          <EmptyState
            icon={<FileText size={64} strokeWidth={1.5} />}
            title="No Report Data Available"
            description="You need to run a Monte Carlo simulation before generating reports. Configure your inputs and run a simulation to get started."
            action={{
              label: 'Go to Inputs',
              onClick: () => navigate('/inputs'),
              variant: 'primary',
            }}
          />
        </Card>
      </div>
    );
  }

  const metrics = simulationResults.metrics;

  return (
    <div className="space-y-xl pb-24">
      {/* Header */}
      <SectionHeader
        title="Analysis Reports"
        description="Generate and download comprehensive portfolio analysis reports"
        icon={<FileText size={28} />}
        actions={
          <div className="flex gap-3">
            <Button
              variant="tertiary"
              size="sm"
              onClick={shareReport}
              icon={<Share2 size={16} />}
            >
              Share
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={printReport}
              icon={<Printer size={16} />}
            >
              Print
            </Button>
          </div>
        }
      />

      {/* Export Options */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Export Options
          </h3>
          <p className="text-body text-text-tertiary">
            Download your analysis report in various formats
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => generateReport('pdf')}
            disabled={isGenerating}
            className="group p-6 text-left rounded-md border border-background-border hover:border-accent-gold hover:bg-background-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 bg-status-error-base bg-opacity-10 rounded-md text-status-error-base group-hover:bg-opacity-20 transition-colors">
                <FileText size={24} />
              </div>
              <div className="flex-1">
                <h4 className="text-h4 font-semibold text-text-primary mb-1">
                  PDF Report
                </h4>
                <p className="text-small text-text-tertiary mb-2">
                  Full report with charts and analysis
                </p>
                <Badge variant="default" size="sm">Client-ready</Badge>
              </div>
            </div>
          </button>

          <button
            onClick={() => generateReport('excel')}
            disabled={isGenerating}
            className="group p-6 text-left rounded-md border border-background-border hover:border-accent-gold hover:bg-background-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 bg-status-success-base bg-opacity-10 rounded-md text-status-success-base group-hover:bg-opacity-20 transition-colors">
                <FileSpreadsheet size={24} />
              </div>
              <div className="flex-1">
                <h4 className="text-h4 font-semibold text-text-primary mb-1">
                  Excel Export
                </h4>
                <p className="text-small text-text-tertiary mb-2">
                  Raw data for further analysis
                </p>
                <Badge variant="default" size="sm">Data only</Badge>
              </div>
            </div>
          </button>

          <button
            onClick={() => generateReport('ppt')}
            disabled={isGenerating}
            className="group p-6 text-left rounded-md border border-background-border hover:border-accent-gold hover:bg-background-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 bg-status-warning-base bg-opacity-10 rounded-md text-status-warning-base group-hover:bg-opacity-20 transition-colors">
                <FileImage size={24} />
              </div>
              <div className="flex-1">
                <h4 className="text-h4 font-semibold text-text-primary mb-1">
                  PowerPoint
                </h4>
                <p className="text-small text-text-tertiary mb-2">
                  Presentation-ready slides
                </p>
                <Badge variant="default" size="sm">Visual</Badge>
              </div>
            </div>
          </button>

          <button
            onClick={() => generateReport('json')}
            disabled={isGenerating}
            className="group p-6 text-left rounded-md border border-background-border hover:border-accent-gold hover:bg-background-hover transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 bg-accent-navy bg-opacity-30 rounded-md text-accent-navy group-hover:bg-opacity-40 transition-colors">
                <Download size={24} />
              </div>
              <div className="flex-1">
                <h4 className="text-h4 font-semibold text-text-primary mb-1">
                  JSON Data
                </h4>
                <p className="text-small text-text-tertiary mb-2">
                  Machine-readable format
                </p>
                <Badge variant="default" size="sm">Developer</Badge>
              </div>
            </div>
          </button>
        </div>
      </Card>

      {/* Report Preview */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Report Preview
          </h3>
          <p className="text-body text-text-tertiary">
            Preview of your generated report with key findings and recommendations
          </p>
        </div>

        <div className="space-y-6">
          {/* Client Information */}
          <div className="border border-background-border rounded-md overflow-hidden">
            <button
              onClick={() => toggleSection('clientInfo')}
              className="w-full flex items-center justify-between p-5 bg-background-hover hover:bg-background-border transition-colors"
            >
              <h4 className="text-h4 font-display font-semibold text-text-primary">
                Client Information
              </h4>
              <ChevronDown
                size={20}
                className={`text-text-tertiary transition-transform ${
                  expandedSections.clientInfo ? 'rotate-180' : ''
                }`}
              />
            </button>
            {expandedSections.clientInfo && (
              <div className="p-6 border-t border-background-border bg-background-base bg-opacity-30">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <p className="text-small font-semibold text-text-secondary uppercase tracking-wider mb-3">
                      Client Details
                    </p>
                    <dl className="space-y-3">
                      <div className="flex justify-between items-center">
                        <dt className="text-body text-text-tertiary">Client Name:</dt>
                        <dd className="text-body font-medium text-text-primary">
                          {clientInfo.client_name || 'N/A'}
                        </dd>
                      </div>
                      <div className="flex justify-between items-center">
                        <dt className="text-body text-text-tertiary">Report Date:</dt>
                        <dd className="text-body font-medium text-text-primary">
                          {clientInfo.report_date || 'N/A'}
                        </dd>
                      </div>
                      <div className="flex justify-between items-center">
                        <dt className="text-body text-text-tertiary">Client ID:</dt>
                        <dd className="text-body font-medium text-text-primary">
                          {clientInfo.client_id || 'N/A'}
                        </dd>
                      </div>
                    </dl>
                  </div>
                  <div>
                    <p className="text-small font-semibold text-text-secondary uppercase tracking-wider mb-3">
                      Advisor Information
                    </p>
                    <dl className="space-y-3">
                      <div className="flex justify-between items-center">
                        <dt className="text-body text-text-tertiary">Advisor Name:</dt>
                        <dd className="text-body font-medium text-text-primary">
                          {clientInfo.advisor_name || 'N/A'}
                        </dd>
                      </div>
                      <div className="flex justify-between items-center">
                        <dt className="text-body text-text-tertiary">Generated:</dt>
                        <dd className="text-body font-medium text-text-primary">
                          {new Date().toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          })}
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>
                {clientInfo.client_notes && (
                  <div className="mt-6 pt-6 border-t border-background-border">
                    <p className="text-small font-semibold text-text-secondary uppercase tracking-wider mb-2">
                      Notes
                    </p>
                    <p className="text-body text-text-primary">{clientInfo.client_notes}</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Portfolio Overview */}
          <div className="border border-background-border rounded-md overflow-hidden">
            <button
              onClick={() => toggleSection('portfolio')}
              className="w-full flex items-center justify-between p-5 bg-background-hover hover:bg-background-border transition-colors"
            >
              <h4 className="text-h4 font-display font-semibold text-text-primary">
                Portfolio Overview
              </h4>
              <ChevronDown
                size={20}
                className={`text-text-tertiary transition-transform ${
                  expandedSections.portfolio ? 'rotate-180' : ''
                }`}
              />
            </button>
            {expandedSections.portfolio && (
              <div className="p-6 border-t border-background-border bg-background-base bg-opacity-30">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-4 bg-background-elevated rounded-sm border border-background-border">
                    <p className="text-small text-text-tertiary mb-2">Starting Portfolio</p>
                    <p className="text-h2 font-display text-text-primary">
                      {formatCurrency(modelInputs.starting_portfolio)}
                    </p>
                  </div>
                  <div className="p-4 bg-background-elevated rounded-sm border border-background-border">
                    <p className="text-small text-text-tertiary mb-2">Time Horizon</p>
                    <p className="text-h2 font-display text-text-primary">
                      {modelInputs.years_to_model} <span className="text-h4 text-text-tertiary">years</span>
                    </p>
                  </div>
                  <div className="p-4 bg-background-elevated rounded-sm border border-background-border">
                    <p className="text-small text-text-tertiary mb-2">Monthly Spending</p>
                    <p className="text-h2 font-display text-text-primary">
                      {formatCurrency(modelInputs.monthly_spending)}
                    </p>
                  </div>
                </div>

                <div className="mt-6">
                  <p className="text-small font-semibold text-text-secondary uppercase tracking-wider mb-3">
                    Asset Allocation
                  </p>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-background-elevated rounded-sm border border-background-border">
                      <div className="w-3 h-3 bg-chart-blue rounded-full mx-auto mb-2"></div>
                      <p className="text-small text-text-tertiary mb-1">Equity</p>
                      <p className="text-h3 font-display text-text-primary">
                        {formatPercent(modelInputs.equity_pct)}
                      </p>
                    </div>
                    <div className="text-center p-4 bg-background-elevated rounded-sm border border-background-border">
                      <div className="w-3 h-3 bg-chart-green rounded-full mx-auto mb-2"></div>
                      <p className="text-small text-text-tertiary mb-1">Fixed Income</p>
                      <p className="text-h3 font-display text-text-primary">
                        {formatPercent(modelInputs.fi_pct)}
                      </p>
                    </div>
                    <div className="text-center p-4 bg-background-elevated rounded-sm border border-background-border">
                      <div className="w-3 h-3 bg-accent-gold rounded-full mx-auto mb-2"></div>
                      <p className="text-small text-text-tertiary mb-1">Cash</p>
                      <p className="text-h3 font-display text-text-primary">
                        {formatPercent(modelInputs.cash_pct)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Key Findings */}
          <div className="border border-background-border rounded-md overflow-hidden">
            <button
              onClick={() => toggleSection('keyFindings')}
              className="w-full flex items-center justify-between p-5 bg-background-hover hover:bg-background-border transition-colors"
            >
              <h4 className="text-h4 font-display font-semibold text-text-primary">
                Key Findings
              </h4>
              <ChevronDown
                size={20}
                className={`text-text-tertiary transition-transform ${
                  expandedSections.keyFindings ? 'rotate-180' : ''
                }`}
              />
            </button>
            {expandedSections.keyFindings && (
              <div className="p-6 border-t border-background-border bg-background-base bg-opacity-30">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-background-elevated rounded-sm border border-background-border">
                    <p className="text-small text-text-tertiary mb-2">Success Probability</p>
                    <div className="flex items-center gap-2 mb-2">
                      <p className={`text-h2 font-display ${
                        metrics.success_probability >= 0.85
                          ? 'text-status-success-base'
                          : metrics.success_probability >= 0.70
                          ? 'text-status-warning-base'
                          : 'text-status-error-base'
                      }`}>
                        {formatPercent(metrics.success_probability)}
                      </p>
                    </div>
                    <Badge variant={getSuccessVariant(metrics.success_probability)} size="sm">
                      {metrics.success_probability >= 0.85
                        ? 'Strong'
                        : metrics.success_probability >= 0.70
                        ? 'Moderate'
                        : 'Low'}
                    </Badge>
                  </div>
                  <div className="p-4 bg-background-elevated rounded-sm border border-background-border">
                    <p className="text-small text-text-tertiary mb-2">Median Ending</p>
                    <p className="text-h3 font-display text-text-primary">
                      {formatCurrency(metrics.ending_median)}
                    </p>
                  </div>
                  <div className="p-4 bg-background-elevated rounded-sm border border-background-border">
                    <p className="text-small text-text-tertiary mb-2">10th Percentile</p>
                    <p className="text-h3 font-display text-text-primary">
                      {formatCurrency(metrics.ending_p10)}
                    </p>
                  </div>
                  <div className="p-4 bg-background-elevated rounded-sm border border-background-border">
                    <p className="text-small text-text-tertiary mb-2">90th Percentile</p>
                    <p className="text-h3 font-display text-text-primary">
                      {formatCurrency(metrics.ending_p90)}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Risk Analysis */}
          <div className="border border-background-border rounded-md overflow-hidden">
            <button
              onClick={() => toggleSection('risk')}
              className="w-full flex items-center justify-between p-5 bg-background-hover hover:bg-background-border transition-colors"
            >
              <h4 className="text-h4 font-display font-semibold text-text-primary">
                Risk Analysis
              </h4>
              <ChevronDown
                size={20}
                className={`text-text-tertiary transition-transform ${
                  expandedSections.risk ? 'rotate-180' : ''
                }`}
              />
            </button>
            {expandedSections.risk && (
              <div className="p-6 border-t border-background-border bg-background-base bg-opacity-30">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-6 bg-status-error-base bg-opacity-5 rounded-md border border-status-error-base border-opacity-20">
                    <p className="text-small text-text-secondary mb-3 uppercase tracking-wider font-semibold">
                      Depletion Probability
                    </p>
                    <p className="text-display font-display text-status-error-base mb-2">
                      {formatPercent(metrics.depletion_probability)}
                    </p>
                    <p className="text-small text-text-tertiary">
                      Probability of portfolio running out of funds during the planning period
                    </p>
                  </div>
                  <div className="p-6 bg-status-warning-base bg-opacity-5 rounded-md border border-status-warning-base border-opacity-20">
                    <p className="text-small text-text-secondary mb-3 uppercase tracking-wider font-semibold">
                      Shortfall Risk
                    </p>
                    <p className="text-display font-display text-status-warning-base mb-2">
                      {formatPercent(metrics.shortfall_risk)}
                    </p>
                    <p className="text-small text-text-tertiary">
                      Risk of not meeting financial objectives and goals
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Recommendations */}
          <div className="border border-background-border rounded-md overflow-hidden">
            <button
              onClick={() => toggleSection('recommendations')}
              className="w-full flex items-center justify-between p-5 bg-background-hover hover:bg-background-border transition-colors"
            >
              <h4 className="text-h4 font-display font-semibold text-text-primary">
                Recommendations
              </h4>
              <ChevronDown
                size={20}
                className={`text-text-tertiary transition-transform ${
                  expandedSections.recommendations ? 'rotate-180' : ''
                }`}
              />
            </button>
            {expandedSections.recommendations && (
              <div className="p-6 border-t border-background-border bg-background-base bg-opacity-30">
                <div className="space-y-4">
                  {metrics.success_probability < 0.7 && (
                    <div className="p-5 bg-status-error-base bg-opacity-10 border border-status-error-base rounded-md">
                      <div className="flex items-start gap-3">
                        <Badge variant="error" size="sm">Action Required</Badge>
                      </div>
                      <p className="text-h4 font-semibold text-status-error-base mt-3 mb-2">
                        Low Success Probability
                      </p>
                      <p className="text-body text-text-primary mb-3">
                        The current plan shows a {formatPercent(metrics.success_probability)} probability of success, which is below recommended thresholds.
                      </p>
                      <ul className="space-y-2 text-body text-text-secondary">
                        <li>• Consider increasing regular contributions to the portfolio</li>
                        <li>• Review and potentially reduce monthly spending requirements</li>
                        <li>• Evaluate allocation strategy for appropriate risk/return profile</li>
                        <li>• Explore extending the planning horizon if feasible</li>
                      </ul>
                    </div>
                  )}

                  {metrics.success_probability >= 0.7 && metrics.success_probability < 0.85 && (
                    <div className="p-5 bg-status-warning-base bg-opacity-10 border border-status-warning-base rounded-md">
                      <div className="flex items-start gap-3">
                        <Badge variant="warning" size="sm">Moderate</Badge>
                      </div>
                      <p className="text-h4 font-semibold text-status-warning-base mt-3 mb-2">
                        Moderate Success Probability
                      </p>
                      <p className="text-body text-text-primary mb-3">
                        The plan shows a {formatPercent(metrics.success_probability)} probability of success. While reasonable, there may be opportunities for optimization.
                      </p>
                      <ul className="space-y-2 text-body text-text-secondary">
                        <li>• Consider scenario analysis to test plan sensitivity</li>
                        <li>• Review spending flexibility for market downturns</li>
                        <li>• Evaluate potential tax optimization strategies</li>
                        <li>• Regular monitoring and periodic plan updates recommended</li>
                      </ul>
                    </div>
                  )}

                  {metrics.success_probability >= 0.85 && (
                    <div className="p-5 bg-status-success-base bg-opacity-10 border border-status-success-base rounded-md">
                      <div className="flex items-start gap-3">
                        <Badge variant="success" size="sm">Strong Plan</Badge>
                      </div>
                      <p className="text-h4 font-semibold text-status-success-base mt-3 mb-2">
                        Strong Success Probability
                      </p>
                      <p className="text-body text-text-primary mb-3">
                        The plan demonstrates a {formatPercent(metrics.success_probability)} probability of success, indicating strong likelihood of meeting objectives.
                      </p>
                      <ul className="space-y-2 text-body text-text-secondary">
                        <li>• Consider additional goals such as legacy planning or charitable giving</li>
                        <li>• Evaluate opportunities for increased spending or lifestyle enhancements</li>
                        <li>• Review estate planning and wealth transfer strategies</li>
                        <li>• Maintain regular monitoring to ensure plan stays on track</li>
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Disclaimer */}
      <Card padding="lg" variant="ghost">
        <div className="text-center">
          <p className="text-small text-text-tertiary leading-relaxed">
            <strong>Important Disclosure:</strong> This report is for illustrative purposes only and should not be considered as investment advice. 
            Past performance is not indicative of future results. Monte Carlo simulations are based on assumptions and may not reflect actual outcomes. 
            Consult with a qualified financial advisor before making investment decisions.
          </p>
        </div>
      </Card>
    </div>
  );
};

export default ReportsPage;
