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
import '../styles/salem-theme.css';

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
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        fontFamily: 'var(--salem-font-sans)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            fontSize: 'var(--salem-text-2xl)', 
            color: 'var(--salem-navy-primary)',
            marginBottom: 'var(--salem-spacing-md)'
          }}>
            Loading Report...
          </div>
          <div style={{ 
            fontSize: 'var(--salem-text-base)', 
            color: 'var(--salem-gray-600)' 
          }}>
            Generating your retirement analysis
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !reportData) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        fontFamily: 'var(--salem-font-sans)'
      }}>
        <div style={{ 
          textAlign: 'center',
          padding: 'var(--salem-spacing-xl)',
          maxWidth: '600px'
        }}>
          <div style={{ 
            fontSize: 'var(--salem-text-2xl)', 
            color: 'var(--salem-danger)',
            marginBottom: 'var(--salem-spacing-md)'
          }}>
            Error Loading Report
          </div>
          <div style={{ 
            fontSize: 'var(--salem-text-base)', 
            color: 'var(--salem-gray-600)' 
          }}>
            {error || 'An unexpected error occurred'}
          </div>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: 'var(--salem-spacing-lg)',
              padding: 'var(--salem-spacing-sm) var(--salem-spacing-lg)',
              backgroundColor: 'var(--salem-navy-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--salem-border-radius)',
              cursor: 'pointer',
              fontSize: 'var(--salem-text-base)',
              fontWeight: 500,
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--salem-navy-dark)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--salem-navy-primary)';
            }}
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
      <div className="no-print" style={{ 
        position: 'fixed', 
        top: '20px', 
        right: '20px', 
        zIndex: 1000 
      }}>
        <button
          onClick={() => window.print()}
          style={{
            padding: 'var(--salem-spacing-sm) var(--salem-spacing-lg)',
            backgroundColor: 'var(--salem-navy-primary)',
            color: 'white',
            border: 'none',
            borderRadius: 'var(--salem-border-radius)',
            cursor: 'pointer',
            fontSize: 'var(--salem-text-base)',
            fontWeight: 500,
            boxShadow: 'var(--salem-shadow-lg)',
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--salem-navy-dark)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--salem-navy-primary)';
          }}
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
        <p style={{ marginBottom: 'var(--salem-spacing-lg)', color: 'var(--salem-gray-700)' }}>
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
