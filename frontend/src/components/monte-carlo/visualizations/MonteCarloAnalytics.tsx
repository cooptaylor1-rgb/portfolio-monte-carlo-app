/**
 * Comprehensive Monte Carlo Analytics Page
 * Displays full suite of charts, graphs, and tables for retirement portfolio analysis
 */

import React, { useState, useMemo, useRef } from 'react';
import { useSimulationStore } from '../../../store/simulationStore';
import { salemColors, sectionHeaderStyle } from './chartUtils';
import { exportAllChartsAsPNG, exportAnalyticsAsPDF } from '../../../utils/exportUtils';

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
      <div style={styles.emptyState}>
        <h3>No Simulation Results Available</h3>
        <p>Please run a Monte Carlo simulation first to view analytics.</p>
      </div>
    );
  }

  const { metrics, stats } = simulationResults;
  const inputs = simulationResults.inputs || modelInputs;

  const sections = [
    { id: 'all', label: 'All Analytics', icon: '📊' },
    { id: 'probability', label: 'Probability Analysis', icon: '📈' },
    { id: 'risk', label: 'Risk & Stress Tests', icon: '⚠️' },
    { id: 'cashflow', label: 'Cash Flow Analysis', icon: '💵' },
    { id: 'tables', label: 'Summary Tables', icon: '📋' },
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
    <div ref={containerRef} style={styles.container}>
      {/* Page Header */}
      <div style={styles.header}>
        <h1 style={styles.pageTitle}>
          Monte Carlo Portfolio Analytics
        </h1>
        <p style={styles.pageSubtitle}>
          Comprehensive retirement planning analysis for {clientInfo.client_name || 'Client'}
        </p>
      </div>

      {/* Section Navigation */}
      <div style={styles.sectionNav}>
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            style={{
              ...styles.navButton,
              ...(activeSection === section.id ? styles.navButtonActive : {}),
            }}
          >
            <span style={{ marginRight: '8px' }}>{section.icon}</span>
            {section.label}
          </button>
        ))}
      </div>

      {/* Main Content */}
      <div id="analytics-content" style={styles.content}>
        
        {/* Core Probability Charts Section */}
        {(activeSection === 'all' || activeSection === 'probability') && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>
              📈 Core Probability Analysis
            </h2>
            <p style={styles.sectionDescription}>
              These visualizations show the range of potential outcomes and likelihood of meeting your financial goals.
            </p>

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
          </section>
        )}

        {/* Risk & Stress Tests Section */}
        {(activeSection === 'all' || activeSection === 'risk') && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>
              ⚠️ Risk Analysis & Stress Testing
            </h2>
            <p style={styles.sectionDescription}>
              Evaluate how your portfolio performs under adverse market conditions and identify key risk factors.
            </p>

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
          </section>
        )}

        {/* Cash Flow Section */}
        {(activeSection === 'all' || activeSection === 'cashflow') && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>
              💵 Cash Flow & Spending Analysis
            </h2>
            <p style={styles.sectionDescription}>
              Detailed breakdown of income sources, withdrawals, and portfolio balance over time.
            </p>

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
          </section>
        )}

        {/* Additional Tables Section */}
        {(activeSection === 'all' || activeSection === 'tables') && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>
              📋 Detailed Analysis Tables
            </h2>
            <p style={styles.sectionDescription}>
              Comprehensive tables for advisor review and client discussion.
            </p>

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
              stats={stats}
              currentAge={inputs.current_age}
            />
            </div>

            <div id="ruin-table" data-chart-export>
            <AnnualProbabilityRuinTable
              stats={stats}
              currentAge={inputs.current_age}
            />
            </div>
          </section>
        )}

      </div>

      {/* Footer with Export Options */}
      <div style={styles.footer}>
        <button 
          style={styles.exportButton}
          onClick={handleExportPDF}
          disabled={isExporting}
        >
          {isExporting ? '⏳ Exporting...' : '📄 Export to PDF'}
        </button>
        <button 
          style={styles.exportButton}
          onClick={handleExportPNG}
          disabled={isExporting}
        >
          🖼️ Export Charts as PNG
        </button>
        <button 
          style={styles.exportButton}
          onClick={handleExportPPT}
        >
          📊 Copy for PowerPoint
        </button>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '32px',
    backgroundColor: '#0F172A',
    minHeight: '100vh',
  },
  header: {
    background: 'linear-gradient(135deg, #0F3B63 0%, #1E5A8E 100%)',
    color: '#FFFFFF',
    padding: '40px',
    borderRadius: '16px',
    marginBottom: '32px',
    textAlign: 'center',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
  },
  pageTitle: {
    fontSize: '36px',
    fontWeight: 700,
    marginBottom: '8px',
    color: salemColors.gold,
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
  },
  pageSubtitle: {
    fontSize: '16px',
    opacity: 0.9,
    margin: 0,
    color: '#E2E8F0',
  },
  sectionNav: {
    display: 'flex',
    gap: '8px',
    marginBottom: '32px',
    flexWrap: 'wrap',
    backgroundColor: '#1E293B',
    padding: '12px',
    borderRadius: '12px',
    border: '1px solid #334155',
  },
  navButton: {
    padding: '12px 20px',
    backgroundColor: 'transparent',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.2s',
    color: '#94A3B8',
  },
  navButtonActive: {
    backgroundColor: salemColors.navy,
    color: '#FFFFFF',
    boxShadow: '0 2px 8px rgba(15, 59, 99, 0.3)',
  },
  content: {
    marginBottom: '32px',
  },
  section: {
    marginBottom: '48px',
  },
  sectionTitle: {
    ...sectionHeaderStyle,
    fontSize: '28px',
    marginBottom: '12px',
    color: salemColors.gold,
  },
  sectionDescription: {
    fontSize: '15px',
    color: '#94A3B8',
    marginBottom: '24px',
    lineHeight: 1.6,
  },
  comingSoon: {
    backgroundColor: '#1E293B',
    border: '2px dashed #334155',
    borderRadius: '12px',
    padding: '48px 32px',
    textAlign: 'center',
    color: '#94A3B8',
  },
  emptyState: {
    textAlign: 'center',
    padding: '64px 32px',
    color: '#94A3B8',
  },
  footer: {
    display: 'flex',
    gap: '16px',
    justifyContent: 'center',
    padding: '24px',
    backgroundColor: '#1E293B',
    borderRadius: '12px',
    border: '1px solid #334155',
  },
  exportButton: {
    padding: '12px 24px',
    backgroundColor: salemColors.gold,
    color: '#0F172A',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '0 2px 8px rgba(180, 151, 89, 0.3)',
  },
};

export default MonteCarloAnalytics;
