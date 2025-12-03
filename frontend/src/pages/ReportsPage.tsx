/**
 * Reports Page - Professional advisor-grade portfolio analysis reports
 * Complete overhaul with institutional styling and client-ready outputs
 */
import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { useNavigate } from 'react-router-dom';
import { SectionHeader, Button, Card, EmptyState } from '../components/ui';
import { FileText, Download, Printer } from 'lucide-react';
import {
  ReportHeader,
  ExecutiveSummary,
  MonteCarloResults,
  StressTestSection,
  AssumptionsSection,
  DisclaimerSection,
} from '../components/reports';
import '../styles/print.css';

const ReportsPage: React.FC = () => {
  const navigate = useNavigate();
  const { simulationResults, clientInfo, modelInputs, hasRunSimulation } = useSimulationStore();
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);

  /**
   * Handle PDF generation via browser print
   */
  const handlePrintPDF = () => {
    setIsGeneratingPDF(true);
    setTimeout(() => {
      window.print();
      setIsGeneratingPDF(false);
    }, 100);
  };

  /**
   * Download report data as JSON
   */
  const downloadJSON = () => {
    const reportData = {
      report_metadata: {
        generated_at: new Date().toISOString(),
        client_name: clientInfo.client_name,
        report_date: clientInfo.report_date,
      },
      client_info: clientInfo,
      model_inputs: modelInputs,
      simulation_results: simulationResults,
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
  };

  if (!hasRunSimulation || !simulationResults) {
    return (
      <div className="space-y-xl">
        <SectionHeader
          title="Portfolio Analysis Report"
          description="Generate comprehensive, client-ready portfolio analysis reports"
          icon={<FileText size={28} />}
        />

        <Card padding="none">
          <EmptyState
            icon={<FileText size={64} strokeWidth={1.5} />}
            title="No Simulation Results Available"
            description="Run a Monte Carlo simulation to generate your comprehensive portfolio analysis report. Navigate to the Inputs page to configure your scenario and execute a simulation."
            action={{
              label: 'Configure & Run Simulation',
              onClick: () => navigate('/inputs'),
              variant: 'primary',
            }}
          />
        </Card>
      </div>
    );
  }

  return (
    <>
      {/* Action Bar - Hidden in print */}
      <div className="no-print mb-8">
        <SectionHeader
          title="Portfolio Analysis Report"
          description="Professional advisor-grade report with executive summary, Monte Carlo results, and stress testing"
          icon={<FileText size={28} />}
          actions={
            <div className="flex gap-3">
              <Button
                variant="secondary"
                size="sm"
                onClick={downloadJSON}
                icon={<Download size={16} />}
              >
                Download Data
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handlePrintPDF}
                icon={<Printer size={16} />}
                disabled={isGeneratingPDF}
              >
                {isGeneratingPDF ? 'Preparing...' : 'Print / Export PDF'}
              </Button>
            </div>
          }
        />
      </div>

      {/* Report Content - Optimized for print */}
      <div className="report-container">
        <div className="report-page bg-white">
          {/* Report Header */}
          <ReportHeader 
            clientInfo={clientInfo}
            scenarioName="Base Case Monte Carlo Analysis"
          />

          {/* Executive Summary */}
          <ExecutiveSummary 
            metrics={simulationResults.metrics}
            modelInputs={modelInputs}
          />

          {/* Monte Carlo Results with Charts */}
          <MonteCarloResults 
            stats={simulationResults.stats}
            metrics={simulationResults.metrics}
            modelInputs={modelInputs}
          />

          {/* Stress Test Analysis */}
          <StressTestSection 
            baseMetrics={simulationResults.metrics}
          />

          {/* Assumptions & Inputs */}
          <AssumptionsSection 
            modelInputs={modelInputs}
            clientInfo={clientInfo}
          />

          {/* Legal Disclaimers */}
          <DisclaimerSection />
        </div>
      </div>
    </>
  );
};

export default ReportsPage;
