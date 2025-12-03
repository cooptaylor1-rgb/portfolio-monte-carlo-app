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
      <MonteCarloChart data={reportData.monte_carlo} />
      <StressTestsSection stressTests={reportData.stress_tests} />
      <AssumptionsSection assumptions={reportData.assumptions} />
      <AppendixSection items={reportData.appendix} />
      <SalemFooter />
    </div>
  );
};

export default SalemReportPage;
