/**
 * Comprehensive Monte Carlo Analytics Page
 * Displays full suite of charts, graphs, and tables for retirement portfolio analysis
 * Fully integrated with design system for visual consistency
 */

import React, { useState, useMemo, useRef } from 'react';
import { useSimulationStore } from '../../../store/simulationStore';
import { exportAllChartsAsPNG, exportAnalyticsAsPDF } from '../../../utils/exportUtils';
import { transformMonthlyStatsToSimulationStats } from '../../../utils/dataTransformers';
import { SectionHeader, Button, Card, EmptyState } from '../../ui';
import { FileText, Download, Image, BarChart3 } from 'lucide-react';

// Import visualizations
import EnhancedFanChart from './EnhancedFanChart';
import ProbabilitySuccessCurve from './ProbabilitySuccessCurve';
import SafeWithdrawalRateCurve from './SafeWithdrawalRateCurve';
import StressTestComparison from './StressTestComparison';
import DrawdownDistribution from './DrawdownDistribution';
import TailRiskSummary from './TailRiskSummary';
import AnnualCashFlowChart from './AnnualCashFlowChart';
import WithdrawalStrategyComparison from './WithdrawalStrategyComparison';
import GlidepathVisualization from './GlidepathVisualization';

// Import tables
import OutcomeSummaryTable from '../tables/OutcomeSummaryTable';
import LongevityStressTable from '../tables/LongevityStressTable';
import AnnualProbabilityRuinTable from '../tables/AnnualProbabilityRuinTable';

interface MonteCarloAnalyticsProps {
  showAllCharts?: boolean;
}

export const MonteCarloAnalytics: React.FC<MonteCarloAnalyticsProps> = () => {
  const { simulationResults, modelInputs, clientInfo } = useSimulationStore();
  const [activeSection, setActiveSection] = useState<string>('all');
  const [isExporting, setIsExporting] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  if (!simulationResults) {
    return (
      <div className="space-y-xl">
        <SectionHeader
          title="Monte Carlo Portfolio Analytics"
          description="Run a simulation to view comprehensive portfolio analysis"
          icon={<BarChart3 size={28} />}
        />
        <Card padding="none">
          <EmptyState
            icon={<BarChart3 size={64} strokeWidth={1.5} />}
            title="No Analytics Available"
            description="Please run a Monte Carlo simulation first to view detailed analytics, risk analysis, and projections."
          />
        </Card>
      </div>
    );
  }

  const { metrics, stats } = simulationResults;
  const inputs = simulationResults.inputs || modelInputs;

  // Transform MonthlyStats to SimulationStats with calculated SuccessPct
  const transformedStats = useMemo(() => {
    return transformMonthlyStatsToSimulationStats(stats);
  }, [stats]);

  const sections = [
    { id: 'all', label: 'All Analytics' },
    { id: 'probability', label: 'Probability Analysis' },
    { id: 'risk', label: 'Risk & Stress Tests' },
    { id: 'cashflow', label: 'Cash Flow Analysis' },
    { id: 'tables', label: 'Summary Tables' },
  ];

  // Memoize chart IDs for export
  const chartIds = useMemo(() => [
    'outcome-summary',
    'fan-chart',
    'success-curve',
    'withdrawal-rate',
    'stress-test',
    'drawdown-dist',
    'tail-risk',
    'cash-flow',
    'withdrawal-strategy',
    'glidepath',
    'longevity-table',
    'ruin-table',
  ], []);

  // Export handlers
  const handleExportPDF = async () => {
    setIsExporting(true);
    try {
      const filename = `${clientInfo.client_name?.replace(/\s+/g, '_') || 'Client'}_Analytics.pdf`;
      await exportAnalyticsAsPDF('analytics-content', { filename });
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export PDF. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportPNG = async () => {
    setIsExporting(true);
    try {
      await exportAllChartsAsPNG(chartIds, 'analytics-charts');
      alert('Charts exported successfully! Check your downloads folder.');
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export images. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportPPT = () => {
    alert('PowerPoint export: Copy individual charts to clipboard and paste into PowerPoint.\n\nTip: Right-click any chart and select "Copy Image" for best quality.');
  };

  return (
    <div ref={containerRef} className="space-y-xl">
      {/* Page Header */}
      <SectionHeader
        title="Monte Carlo Portfolio Analytics"
        description={`Comprehensive retirement planning analysis for ${clientInfo.client_name || 'Client'}`}
        icon={<BarChart3 size={28} />}
        actions={
          <div className="flex gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleExportPNG}
              disabled={isExporting}
              icon={<Image size={16} />}
            >
              Export PNG
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleExportPDF}
              disabled={isExporting}
              icon={<Download size={16} />}
            >
              Export PDF
            </Button>
          </div>
        }
      />

      {/* Section Navigation Tabs */}
      <Card padding="none">
        <div className="flex flex-wrap gap-2 p-4 border-b border-background-border">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`
                px-4 py-2 rounded-sm text-small font-medium transition-all duration-fast
                ${activeSection === section.id
                  ? 'bg-accent-gold text-background-base shadow-sm'
                  : 'bg-background-hover text-text-secondary hover:bg-background-border hover:text-text-primary'
                }
              `}
            >
              {section.label}
            </button>
          ))}
        </div>
      </Card>

      {/* Main Content */}
      <div id="analytics-content" className="space-y-2xl">
        
        {/* Core Probability Charts Section */}
        {(activeSection === 'all' || activeSection === 'probability') && (
          <div className="space-y-lg">
            <div>
              <h2 className="text-h2 font-display font-semibold text-accent-gold mb-2">
                Probability Analysis
              </h2>
              <p className="text-body text-text-secondary">
                These visualizations show the range of potential outcomes and likelihood of meeting your financial goals.
              </p>
            </div>

            <div id="fan-chart" data-chart-export>
              <EnhancedFanChart
                stats={stats}
                currentAge={inputs.current_age}
                startingPortfolio={inputs.starting_portfolio}
              />
            </div>

            <div id="success-curve" data-chart-export>
              <ProbabilitySuccessCurve
                stats={stats}
                currentAge={inputs.current_age}
                monthlySpending={inputs.monthly_spending}
              />
            </div>

            <div id="withdrawal-rate" data-chart-export>
              <SafeWithdrawalRateCurve
                startingPortfolio={inputs.starting_portfolio}
                currentSpending={inputs.monthly_spending}
                successProbability={metrics.success_probability}
              />
            </div>
          </div>
        )}

        {/* Risk & Stress Tests Section */}
        {(activeSection === 'all' || activeSection === 'risk') && (
          <div className="space-y-lg">
            <div>
              <h2 className="text-h2 font-display font-semibold text-accent-gold mb-2">
                Risk Analysis & Stress Testing
              </h2>
              <p className="text-body text-text-secondary">
                Evaluate how your portfolio performs under adverse market conditions and identify key risk factors.
              </p>
            </div>

            <div id="stress-test" data-chart-export>
              <StressTestComparison
                baselineMetrics={metrics}
                startingPortfolio={inputs.starting_portfolio}
              />
            </div>

            <div id="drawdown-dist" data-chart-export>
              <DrawdownDistribution
                stats={stats}
                startingPortfolio={inputs.starting_portfolio}
              />
            </div>

            <div id="tail-risk" data-chart-export>
              <TailRiskSummary
                stats={stats}
                startingPortfolio={inputs.starting_portfolio}
              />
            </div>
          </div>
        )}

        {/* Cash Flow Section */}
        {(activeSection === 'all' || activeSection === 'cashflow') && (
          <div className="space-y-lg">
            <div>
              <h2 className="text-h2 font-display font-semibold text-accent-gold mb-2">
                Cash Flow & Spending Analysis
              </h2>
              <p className="text-body text-text-secondary">
                Detailed breakdown of income sources, withdrawals, and portfolio balance over time.
              </p>
            </div>

            <div id="cash-flow" data-chart-export>
              <AnnualCashFlowChart
                stats={stats}
                currentAge={inputs.current_age}
                monthlySpending={inputs.monthly_spending}
                monthlyIncome={inputs.social_security_monthly + inputs.pension_monthly + inputs.regular_income_monthly}
              />
            </div>

            <div id="withdrawal-strategy" data-chart-export>
              <WithdrawalStrategyComparison
                stats={stats}
                currentAge={inputs.current_age}
                initialSpending={inputs.monthly_spending}
              />
            </div>

            <div id="glidepath" data-chart-export>
              <GlidepathVisualization
                currentAge={inputs.current_age}
                planYears={inputs.years_to_model * 12}
                initialEquity={inputs.equity_pct / 100}
              />
            </div>
          </div>
        )}

        {/* Additional Tables Section */}
        {(activeSection === 'all' || activeSection === 'tables') && (
          <div className="space-y-lg">
            <div>
              <h2 className="text-h2 font-display font-semibold text-accent-gold mb-2">
                Detailed Analysis Tables
              </h2>
              <p className="text-body text-text-secondary">
                Comprehensive tables for advisor review and client discussion.
              </p>
            </div>

            <div id="outcome-summary" data-chart-export>
              <OutcomeSummaryTable
                metrics={metrics}
                stats={stats}
                startingPortfolio={inputs.starting_portfolio}
                years={inputs.years_to_model}
              />
            </div>

            <div id="longevity-table" data-chart-export>
              <LongevityStressTable
                stats={transformedStats}
                currentAge={inputs.current_age}
              />
            </div>

            <div id="ruin-table" data-chart-export>
              <AnnualProbabilityRuinTable
                stats={transformedStats}
                currentAge={inputs.current_age}
              />
            </div>
          </div>
        )}

      </div>

      {/* Footer with Export Options */}
      <Card padding="md">
        <div className="flex flex-wrap gap-4 justify-center items-center">
          <Button
            variant="primary"
            size="md"
            onClick={handleExportPDF}
            disabled={isExporting}
            loading={isExporting}
            icon={<FileText size={20} />}
          >
            Export to PDF
          </Button>
          <Button
            variant="secondary"
            size="md"
            onClick={handleExportPNG}
            disabled={isExporting}
            icon={<Image size={20} />}
          >
            Export Charts as PNG
          </Button>
          <Button
            variant="tertiary"
            size="md"
            onClick={handleExportPPT}
            icon={<Download size={20} />}
          >
            Copy for PowerPoint
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default MonteCarloAnalytics;
