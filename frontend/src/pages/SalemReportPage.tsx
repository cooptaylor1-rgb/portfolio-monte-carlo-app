/**
 * Salem Report Page
 * Main page for displaying Salem-branded retirement analysis reports
 */
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../lib/api';
import type { ReportData } from '../types/reports';
import {
  ReportHeader,
  SummarySection,
  NarrativeSection,
  MonteCarloChart,
  StressTestsSection,
  AssumptionsSection,
  AppendixSection,
  SalemFooter,
  SuccessProbabilityChart,
  StressTestChart,
  TerminalWealthHistogram,
  CashFlowTable,
  IncomeTimelineChart,
} from '../components/salem-reports';

export const SalemReportPage: React.FC = () => {
  const { planId = 'demo-plan-001' } = useParams<{ planId?: string }>();
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiClient.fetchReport(planId);
        setReportData(data);
      } catch (err) {
        console.error('Failed to fetch report:', err);
        setError('Failed to load report. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [planId]);

  // Loading state
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen font-sans">
        <div className="text-center">
          <div className="text-h2 text-primary-navy mb-md">
            Loading Report...
          </div>
          <div className="text-body text-text-tertiary">
            Generating your retirement analysis
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !reportData) {
    return (
      <div className="flex justify-center items-center min-h-screen font-sans">
        <div className="text-center p-xl max-w-[600px]">
          <div className="text-h2 text-status-error-base mb-md">
            Error Loading Report
          </div>
          <div className="text-body text-text-tertiary">
            {error || 'An unexpected error occurred'}
          </div>
          <button
            onClick={() => window.location.reload()}
            className="mt-lg px-lg py-sm bg-primary-navy text-white border-none rounded-md cursor-pointer text-body font-medium hover:bg-primary-navy-dark transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Main report view
  return (
    <div className="salem-report">
      {/* Print button (hidden when printing) */}
      <div className="no-print fixed top-5 right-5 z-50">
        <button
          onClick={() => window.print()}
          className="px-lg py-sm bg-primary-navy text-white border-none rounded-md cursor-pointer text-body font-medium hover:bg-primary-navy-dark transition-colors shadow-lg"
        >
          Print / Save PDF
        </button>
      </div>

      {/* Report Content */}
      <ReportHeader summary={reportData.summary} />
      <SummarySection summary={reportData.summary} />
      <NarrativeSection narrative={reportData.narrative} />
      
      {/* Monte Carlo Results with New Charts */}
      <MonteCarloChart data={reportData.monte_carlo} />
      
      {/* Success Probability Over Time */}
      {reportData.monte_carlo.success_probability_over_time && (
        <SuccessProbabilityChart data={reportData.monte_carlo.success_probability_over_time} />
      )}
      
      {/* Terminal Wealth Distribution */}
      {reportData.monte_carlo.terminal_wealth_distribution && (
        <TerminalWealthHistogram data={reportData.monte_carlo.terminal_wealth_distribution} />
      )}
      
      {/* Stress Tests with Comparison Chart */}
      <section className="salem-section">
        <h2>Stress Test Analysis</h2>
        <p className="mb-lg text-text-tertiary">
          Testing plan resilience under adverse market conditions
        </p>
        {reportData.stress_tests.length > 0 && (
          <StressTestChart scenarios={reportData.stress_tests} />
        )}
        <StressTestsSection stressTests={reportData.stress_tests} />
      </section>
      
      {/* Cash Flow Details */}
      {reportData.cash_flow_projection && reportData.cash_flow_projection.length > 0 && (
        <section className="salem-section">
          <h2>Financial Projections</h2>
          <CashFlowTable data={reportData.cash_flow_projection} />
        </section>
      )}
      
      {/* Income Timeline */}
      {reportData.income_timeline && reportData.income_timeline.length > 0 && (
        <IncomeTimelineChart data={reportData.income_timeline} />
      )}
      
      <AssumptionsSection assumptions={reportData.assumptions} />
      <AppendixSection items={reportData.appendix} />
      <SalemFooter />
    </div>
  );
};

export default SalemReportPage;
