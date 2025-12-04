/**
 * Comprehensive Monte Carlo Analytics Page
 * Displays full suite of charts, graphs, and tables for retirement portfolio analysis
 */

import React, { useState } from 'react';
import { useSimulationStore } from '../../../store/simulationStore';
import { salemColors, sectionHeaderStyle } from './chartUtils';

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

  return (
    <div style={styles.container}>
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
      <div style={styles.content}>
        
        {/* Summary Table */}
        {(activeSection === 'all' || activeSection === 'tables') && (
          <section style={styles.section}>
            <OutcomeSummaryTable
              metrics={metrics}
              stats={stats}
              startingPortfolio={inputs.starting_portfolio}
              years={inputs.years_to_model}
            />
          </section>
        )}

        {/* Core Probability Charts Section */}
        {(activeSection === 'all' || activeSection === 'probability') && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>
              📈 Core Probability Analysis
            </h2>
            <p style={styles.sectionDescription}>
              These visualizations show the range of potential outcomes and likelihood of meeting your financial goals.
            </p>

            <EnhancedFanChart
              stats={stats}
              currentAge={inputs.current_age}
              startingPortfolio={inputs.starting_portfolio}
            />

            <ProbabilitySuccessCurve
              stats={stats}
              currentAge={inputs.current_age}
              monthlySpending={inputs.monthly_spending}
            />

            <SafeWithdrawalRateCurve
              startingPortfolio={inputs.starting_portfolio}
              currentSpending={inputs.monthly_spending}
              successProbability={metrics.success_probability}
            />
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

            <StressTestComparison
              baselineMetrics={metrics}
              startingPortfolio={inputs.starting_portfolio}
            />

            <DrawdownDistribution
              stats={stats}
              startingPortfolio={inputs.starting_portfolio}
            />

            <TailRiskSummary
              stats={stats}
              startingPortfolio={inputs.starting_portfolio}
            />
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

            <AnnualCashFlowChart
              stats={stats}
              currentAge={inputs.current_age}
              monthlySpending={inputs.monthly_spending}
              monthlyIncome={inputs.social_security_monthly + inputs.pension_monthly + inputs.regular_income_monthly}
            />

            <WithdrawalStrategyComparison
              stats={stats}
              currentAge={inputs.current_age}
              initialSpending={inputs.monthly_spending}
            />

            <GlidepathVisualization
              currentAge={inputs.current_age}
              planYears={inputs.years_to_model * 12}
              initialEquity={inputs.equity_pct / 100}
            />
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

            <LongevityStressTable
              stats={stats}
              currentAge={inputs.current_age}
            />

            <AnnualProbabilityRuinTable
              stats={stats}
              currentAge={inputs.current_age}
            />
          </section>
        )}

      </div>

      {/* Footer with Export Options */}
      <div style={styles.footer}>
        <button style={styles.exportButton}>
          📄 Export to PDF
        </button>
        <button style={styles.exportButton}>
          📊 Export to PowerPoint
        </button>
        <button style={styles.exportButton}>
          🖼️ Export Charts as Images
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
    backgroundColor: '#F9FAFB',
    minHeight: '100vh',
  },
  header: {
    backgroundColor: salemColors.navy,
    color: '#FFFFFF',
    padding: '32px',
    borderRadius: '12px',
    marginBottom: '32px',
    textAlign: 'center',
  },
  pageTitle: {
    fontSize: '32px',
    fontWeight: 700,
    marginBottom: '8px',
    color: salemColors.gold,
  },
  pageSubtitle: {
    fontSize: '16px',
    opacity: 0.9,
    margin: 0,
  },
  sectionNav: {
    display: 'flex',
    gap: '8px',
    marginBottom: '32px',
    flexWrap: 'wrap',
    backgroundColor: '#FFFFFF',
    padding: '12px',
    borderRadius: '12px',
    border: '1px solid #E5E7EB',
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
    color: '#6B7280',
  },
  navButtonActive: {
    backgroundColor: salemColors.navy,
    color: '#FFFFFF',
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
  },
  sectionDescription: {
    fontSize: '15px',
    color: '#6B7280',
    marginBottom: '24px',
    lineHeight: 1.6,
  },
  comingSoon: {
    backgroundColor: '#FFFFFF',
    border: '2px dashed #D1D5DB',
    borderRadius: '12px',
    padding: '48px 32px',
    textAlign: 'center',
    color: '#6B7280',
  },
  emptyState: {
    textAlign: 'center',
    padding: '64px 32px',
    color: '#6B7280',
  },
  footer: {
    display: 'flex',
    gap: '16px',
    justifyContent: 'center',
    padding: '24px',
    backgroundColor: '#FFFFFF',
    borderRadius: '12px',
    border: '1px solid #E5E7EB',
  },
  exportButton: {
    padding: '12px 24px',
    backgroundColor: salemColors.navy,
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
};

export default MonteCarloAnalytics;
