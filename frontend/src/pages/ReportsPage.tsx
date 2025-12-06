/**
 * Reports Page - Integrated portfolio analysis with dark mode styling
 * Matches main app design with comprehensive charts and export capabilities
 * Robust data validation and professional advisor-ready outputs
 */
import React, { useState, useMemo } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { useNavigate } from 'react-router-dom';
import { SectionHeader, Button, Card, EmptyState, Badge, ExportCard, ExportProgress, ChartContainer } from '../components/ui';
import type { ExportFormat } from '../components/ui';
import { FileText, Download, FileSpreadsheet, Presentation, Eye, AlertCircle } from 'lucide-react';
import apiClient from '../lib/api';
import {
  Line,
  BarChart,
  Bar,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  ComposedChart,
} from 'recharts';
import {
  formatCurrency,
  formatPercent,
  getSuccessRating,
  hasValidData,
  getLastElement,
} from '../utils/reportFormatters';
import '../styles/print.css';

interface PercentileDataPoint {
  year: number;
  p10: number;
  p25: number;
  median: number;
  p75: number;
  p90: number;
}

interface DistributionDataPoint {
  percentile: string;
  value: number;
  color: string;
}

const ReportsPage: React.FC = () => {
  const navigate = useNavigate();
  const { simulationResults, clientInfo, modelInputs, hasRunSimulation } = useSimulationStore();
  const [exportingFormat, setExportingFormat] = useState<string | null>(null);
  const [exportStatus, setExportStatus] = useState<'preparing' | 'generating' | 'complete' | 'error'>('preparing');
  const [exportMessage, setExportMessage] = useState<string>('');
  const [showExportProgress, setShowExportProgress] = useState(false);

  /**
   * Export format configurations
   */
  const exportFormats: ExportFormat[] = [
    {
      id: 'pdf',
      name: 'PDF Report',
      description: 'Professional PDF report with charts, analysis, and branding. Perfect for client presentations.',
      icon: FileText,
      fileType: 'PDF',
      includes: [
        'Executive summary with key metrics',
        'Portfolio trajectory fan chart',
        'Success probability analysis',
        'Distribution histograms',
        'Input assumptions table',
        'Professional Salem branding',
      ],
      recommended: true,
      size: '2-5 MB',
    },
    {
      id: 'powerpoint',
      name: 'PowerPoint Deck',
      description: 'Editable presentation slides with charts and data. Ideal for customized client meetings.',
      icon: Presentation,
      fileType: 'PPTX',
      includes: [
        'Title slide with client info',
        'Key findings summary',
        'Embedded chart images',
        'Data tables and metrics',
        'Fully editable slides',
        'Salem template styling',
      ],
      size: '3-6 MB',
    },
    {
      id: 'excel',
      name: 'Excel Spreadsheet',
      description: 'Comprehensive data export with raw numbers. Best for detailed analysis and modeling.',
      icon: FileSpreadsheet,
      fileType: 'CSV',
      includes: [
        'Summary metrics table',
        'Percentile projections (annual)',
        'Distribution data',
        'Input parameters',
        'Easy to import into Excel',
        'Machine-readable format',
      ],
      size: '< 1 MB',
    },
  ];

  /**
   * Handle export with progress tracking
   */
  const handleExport = async (formatId: string) => {
    setExportingFormat(formatId);
    setShowExportProgress(true);
    setExportStatus('preparing');
    setExportMessage('Preparing your export...');

    try {
      // Simulate preparation delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setExportStatus('generating');
      setExportMessage('Generating file...');

      // Call appropriate export function
      if (formatId === 'pdf') {
        await exportToPDF();
      } else if (formatId === 'powerpoint') {
        await exportToPowerPoint();
      } else if (formatId === 'excel') {
        await exportToExcel();
      }

      setExportStatus('complete');
      setExportMessage('Export completed successfully!');
      
      // Auto-hide after 3 seconds
      setTimeout(() => {
        setShowExportProgress(false);
        setExportingFormat(null);
      }, 3000);
    } catch (error) {
      console.error('Export error:', error);
      setExportStatus('error');
      setExportMessage('Export failed. Please try again.');
      
      // Auto-hide after 5 seconds
      setTimeout(() => {
        setShowExportProgress(false);
        setExportingFormat(null);
      }, 5000);
    }
  };

  /**
   * Validate and prepare chart data with comprehensive error handling
   */
  const chartData = useMemo(() => {
    if (!simulationResults || !hasValidData(simulationResults.stats)) {
      return {
        percentileData: [],
        distributionData: [],
        hasData: false,
      };
    }

    try {
      // Percentile chart data - annual data points only
      const percentileData: PercentileDataPoint[] = simulationResults.stats
        .filter((stat, idx) => idx % 12 === 0 && stat.Month !== undefined)
        .map((stat) => ({
          year: Math.round(stat.Month / 12),
          p10: stat.P10 ?? 0,
          p25: stat.P25 ?? 0,
          median: stat.Median ?? 0,
          p75: stat.P75 ?? 0,
          p90: stat.P90 ?? 0,
        }))
        .filter((point) => !isNaN(point.year));

      // Distribution data - final year percentiles
      const lastPoint = getLastElement(percentileData);
      const distributionData: DistributionDataPoint[] = lastPoint
        ? [
            { percentile: 'P10', value: lastPoint.p10, color: '#FFC107' },
            { percentile: 'P25', value: lastPoint.p25, color: '#FFD54F' },
            { percentile: 'Median', value: lastPoint.median, color: '#00335D' },
            { percentile: 'P75', value: lastPoint.p75, color: '#81C784' },
            { percentile: 'P90', value: lastPoint.p90, color: '#4B8F29' },
          ]
        : [];

      return {
        percentileData,
        distributionData,
        hasData: percentileData.length > 0,
      };
    } catch (error) {
      console.error('Error preparing chart data:', error);
      return {
        percentileData: [],
        distributionData: [],
        hasData: false,
      };
    }
  }, [simulationResults]);

  /**
   * Calculate success rating with validation
   */
  const successRating = useMemo(() => {
    return getSuccessRating(simulationResults?.metrics?.success_probability);
  }, [simulationResults]);

  /**
   * Export to Excel (comprehensive CSV with multiple data sections)
   */
  const exportToExcel = async () => {
    if (!simulationResults || !chartData.hasData) {
      console.warn('No data available for export');
      return;
    }

    setExportingFormat('excel');
    try {
      // Build comprehensive CSV with multiple sections
      const sections: string[] = [];
      
      // Section 1: Summary Metrics
      sections.push('PORTFOLIO ANALYSIS SUMMARY');
      sections.push(`Client: ${clientInfo.client_name || 'N/A'}`);
      sections.push(`Report Date: ${new Date().toISOString().split('T')[0]}`);
      sections.push('');
      sections.push('Key Metrics');
      sections.push('Metric,Value');
      sections.push(`Success Probability,${formatPercent(simulationResults.metrics.success_probability)}`);
      sections.push(`Median Ending Portfolio,${formatCurrency(simulationResults.metrics.ending_median)}`);
      sections.push(`10th Percentile,${formatCurrency(simulationResults.metrics.ending_p10)}`);
      sections.push(`90th Percentile,${formatCurrency(simulationResults.metrics.ending_p90)}`);
      sections.push(`Depletion Risk,${formatPercent(simulationResults.metrics.depletion_probability)}`);
      sections.push('');
      sections.push('');
      
      // Section 2: Percentile Paths
      sections.push('WEALTH PERCENTILE PROJECTIONS');
      sections.push('Year,P5,P10,P25,Median,P75,P90,P95');
      chartData.percentileData.forEach((point) => {
        sections.push([
          point.year,
          point.p5?.toFixed(0) || '',
          point.p10.toFixed(0),
          point.p25.toFixed(0),
          point.median.toFixed(0),
          point.p75.toFixed(0),
          point.p90.toFixed(0),
          point.p95?.toFixed(0) || ''
        ].join(','));
      });
      sections.push('');
      sections.push('');
      
      // Section 3: Distribution Data (if available)
      if (chartData.distributionData && chartData.distributionData.length > 0) {
        sections.push('TERMINAL WEALTH DISTRIBUTION');
        sections.push('Range,Count,Percentage');
        chartData.distributionData.forEach((bucket) => {
          sections.push(`"${bucket.range}",${bucket.count},${(bucket.percentage * 100).toFixed(1)}%`);
        });
        sections.push('');
        sections.push('');
      }
      
      // Section 4: Input Parameters
      sections.push('INPUT PARAMETERS');
      sections.push('Parameter,Value');
      sections.push(`Starting Portfolio,$${modelInputs.portfolio_value.toLocaleString()}`);
      sections.push(`Monthly Spending,$${Math.abs(modelInputs.monthly_spending).toLocaleString()}`);
      sections.push(`Planning Horizon,${modelInputs.years_in_retirement} years`);
      sections.push(`Equity Return,${(modelInputs.equity_return_annual * 100).toFixed(1)}%`);
      sections.push(`Fixed Income Return,${(modelInputs.fi_return_annual * 100).toFixed(1)}%`);
      sections.push(`Inflation Rate,${(modelInputs.inflation_annual * 100).toFixed(1)}%`);
      sections.push(`Simulation Runs,${modelInputs.num_simulations}`);
      
      // Create CSV blob
      const csv = sections.join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Generate filename
      const clientName = clientInfo.client_name || 'Client';
      const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
      a.download = `Portfolio_Analysis_${clientName.replace(/\s+/g, '_')}_${date}.csv`;
      
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      console.log('Excel/CSV exported successfully');
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      alert('Export failed. Please try again or contact support if the issue persists.');
    } finally {
      setExportingFormat(null);
    }
  };

  /**
   * Export to PDF (professional Salem-branded report with actual data)
   */
  const exportToPDF = async () => {
    if (!simulationResults || !chartData.hasData) {
      console.warn('No simulation results available for export');
      return;
    }

    setExportingFormat('pdf');
    try {
      // Prepare actual simulation data for PDF generation
      const exportData = {
        metrics: {
          success_probability: simulationResults.metrics.success_probability,
          ending_median: simulationResults.metrics.ending_median,
          ending_p10: simulationResults.metrics.ending_p10,
          ending_p90: simulationResults.metrics.ending_p90,
          ending_p95: simulationResults.metrics.ending_p95,
          ending_p5: simulationResults.metrics.ending_p5,
          depletion_probability: simulationResults.metrics.depletion_probability,
        },
        percentile_paths: chartData.percentileData.map(point => ({
          year: point.year,
          p5: point.p5,
          p10: point.p10,
          p25: point.p25,
          median: point.median,
          p50: point.median,
          p75: point.p75,
          p90: point.p90,
          p95: point.p95,
        })),
        inputs: modelInputs,
        client_info: {
          client_name: clientInfo.client_name || 'Client',
        },
      };

      // Call backend endpoint to generate PDF with actual data
      const response = await apiClient.axiosClient.post(
        `/reports/export/pdf`,
        exportData,
        {
          responseType: 'blob', // Important: treat response as binary
        }
      );

      // Create blob from response
      const blob = new Blob([response.data], {
        type: 'application/pdf',
      });

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Generate filename
      const clientName = clientInfo.client_name || 'Client';
      const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
      a.download = `Portfolio_Analysis_${clientName.replace(/\s+/g, '_')}_${date}.pdf`;
      
      // Trigger download
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      console.log('PDF exported successfully with actual simulation data');
    } catch (error: any) {
      console.error('Error exporting to PDF:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to export PDF';
      alert(`Export failed: ${errorMessage}\n\nPlease try again or contact support if the issue persists.`);
    } finally {
      setExportingFormat(null);
    }
  };

  /**
   * Export to PowerPoint (real .pptx file)
   */
  const exportToPowerPoint = async () => {
    if (!simulationResults) {
      console.warn('No simulation results available for export');
      return;
    }

    setExportingFormat('powerpoint');
    try {
      // Prepare actual simulation data for PowerPoint generation
      const exportData = {
        metrics: {
          success_probability: simulationResults.metrics.success_probability,
          ending_median: simulationResults.metrics.ending_median,
          ending_p10: simulationResults.metrics.ending_p10,
          ending_p90: simulationResults.metrics.ending_p90,
          ending_p95: simulationResults.metrics.ending_p95,
          ending_p5: simulationResults.metrics.ending_p5,
          depletion_probability: simulationResults.metrics.depletion_probability,
        },
        percentile_paths: chartData.percentileData.map(point => ({
          year: point.year,
          p5: point.p5,
          p10: point.p10,
          p25: point.p25,
          median: point.median,
          p50: point.median,
          p75: point.p75,
          p90: point.p90,
          p95: point.p95,
        })),
        inputs: modelInputs,
        client_info: {
          client_name: clientInfo.client_name || 'Client',
        },
      };

      // Call backend endpoint to generate PowerPoint with actual data
      const response = await apiClient.axiosClient.post(
        `/reports/export/powerpoint`,
        exportData,
        {
          responseType: 'blob', // Important: treat response as binary
        }
      );

      // Create blob from response
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      });

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Generate filename
      const clientName = clientInfo.client_name || 'Client';
      const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
      a.download = `Portfolio_Analysis_${clientName.replace(/\s+/g, '_')}_${date}.pptx`;
      
      // Trigger download
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      console.log('PowerPoint exported successfully with actual simulation data');
    } catch (error: any) {
      console.error('Error exporting to PowerPoint:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to export PowerPoint';
      alert(`Export failed: ${errorMessage}\n\nPlease try again or contact support if the issue persists.`);
    } finally {
      setExportingFormat(null);
    }
  };

  if (!hasRunSimulation || !simulationResults) {
    return (
      <div className="space-y-xl">
        <SectionHeader
          title="Portfolio Analysis Report"
          description="Comprehensive portfolio analysis with charts and exports"
          icon={<FileText size={28} />}
        />

        <Card padding="none">
          <EmptyState
            icon={<FileText size={64} strokeWidth={1.5} />}
            title="No Simulation Results Available"
            description="Run a Monte Carlo simulation to generate your portfolio analysis report with charts and data."
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

  // Show data error state if chart data failed to prepare
  if (!chartData.hasData) {
    return (
      <div className="space-y-xl">
        <SectionHeader
          title="Portfolio Analysis Report"
          description="Comprehensive portfolio analysis with charts and exports"
          icon={<FileText size={28} />}
        />

        <Card padding="lg">
          <div className="flex items-center gap-4 p-6 bg-status-warning-light rounded-md border border-status-warning-base">
            <AlertCircle className="text-status-warning-base" size={32} />
            <div>
              <h3 className="text-h3 font-display text-text-primary mb-2">
                Data Processing Error
              </h3>
              <p className="text-body text-text-tertiary">
                Unable to process simulation results. Please run the simulation again or contact support if the issue persists.
              </p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-xl pb-24">
      {/* Header */}
      <SectionHeader
        title="Portfolio Analysis Report"
        description="Comprehensive Monte Carlo analysis with exportable charts and data"
        icon={<FileText size={28} />}
      />

      {/* Export Formats Section */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Export Your Report
          </h3>
          <p className="text-body text-text-tertiary">
            Choose your preferred format to download this analysis. All exports include your latest simulation results.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {exportFormats.map((format) => (
            <ExportCard
              key={format.id}
              format={format}
              onExport={handleExport}
              isExporting={exportingFormat === format.id}
            />
          ))}
        </div>
      </Card>

      {/* Executive Summary Cards */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Executive Summary
          </h3>
          <p className="text-body text-text-tertiary">
            Client: <strong className="text-text-primary">{clientInfo.client_name || 'N/A'}</strong> • 
            Report Date: {clientInfo.report_date ? new Date(clientInfo.report_date).toLocaleDateString() : 'N/A'}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-6 bg-background-hover rounded-md border border-background-border">
            <p className="text-small text-text-tertiary mb-2">Success Probability</p>
            <div className="flex items-center gap-3">
              <p
                className="text-h1 font-display font-bold"
                style={{ color: successRating.color }}
              >
                {formatPercent(simulationResults.metrics.success_probability)}
              </p>
              <Badge
                variant={successRating.variant}
                size="sm"
              >
                {successRating.label}
              </Badge>
            </div>
          </div>

          <div className="p-6 bg-background-hover rounded-md border border-background-border">
            <p className="text-small text-text-tertiary mb-2">Median Ending Portfolio</p>
            <p className="text-h1 font-display font-bold text-text-primary">
              {formatCurrency(simulationResults.metrics.ending_median)}
            </p>
          </div>

          <div className="p-6 bg-background-hover rounded-md border border-background-border">
            <p className="text-small text-text-tertiary mb-2">10th Percentile (Downside)</p>
            <p className="text-h1 font-display font-bold text-text-primary">
              {formatCurrency(simulationResults.metrics.ending_p10)}
            </p>
          </div>

          <div className="p-6 bg-background-hover rounded-md border border-background-border">
            <p className="text-small text-text-tertiary mb-2">90th Percentile (Upside)</p>
            <p className="text-h1 font-display font-bold text-text-primary">
              {formatCurrency(simulationResults.metrics.ending_p90)}
            </p>
          </div>
        </div>
      </Card>

      {/* Monte Carlo Fan Chart */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Portfolio Projection (Monte Carlo Simulation)
          </h3>
          <p className="text-body text-text-tertiary">
            Percentile bands showing range of potential outcomes over {modelInputs.years_to_model || 'N/A'} years
          </p>
        </div>

        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData.percentileData}>
              <defs>
                <linearGradient id="percentileGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00335D" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#00335D" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
              <XAxis
                dataKey="year"
                stroke="#94a3b8"
                tick={{ fill: '#94a3b8', fontSize: 12 }}
                label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#94a3b8' }}
              />
              <YAxis
                tickFormatter={(value: number) => formatCurrency(value)}
                stroke="#94a3b8"
                tick={{ fill: '#94a3b8', fontSize: 12 }}
                label={{ value: 'Portfolio Value', angle: -90, position: 'insideLeft', fill: '#94a3b8', offset: 10 }}
                width={80}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  padding: '12px',
                }}
                labelStyle={{ color: '#e2e8f0', marginBottom: '8px' }}
                formatter={(value: number) => [formatCurrency(value), '']}
                labelFormatter={(year: number) => `Year ${year}`}
              />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              <Area
                type="monotone"
                dataKey="p90"
                stroke="none"
                fill="url(#percentileGradient)"
                fillOpacity={1}
                name="10th-90th Percentile Range"
              />
              <Area type="monotone" dataKey="p10" stroke="none" fill="#0C0E12" />
              <Line
                type="monotone"
                dataKey="p90"
                stroke="#4B8F29"
                strokeWidth={2.5}
                dot={false}
                name="90th Percentile (Optimistic)"
              />
              <Line
                type="monotone"
                dataKey="median"
                stroke="#00335D"
                strokeWidth={3.5}
                dot={false}
                name="Median (Most Likely)"
              />
              <Line
                type="monotone"
                dataKey="p10"
                stroke="#FFC107"
                strokeWidth={2.5}
                dot={false}
                name="10th Percentile (Conservative)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Distribution Chart */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Outcome Distribution
          </h3>
          <p className="text-body text-text-tertiary">
            Percentile breakdown of portfolio values at year {modelInputs.years_to_model || 'N/A'}
          </p>
        </div>

        {chartData.distributionData.length > 0 ? (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData.distributionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis 
                  dataKey="percentile" 
                  stroke="#94a3b8"
                  tick={{ fill: '#94a3b8', fontSize: 12 }}
                />
                <YAxis 
                  tickFormatter={(value: number) => formatCurrency(value)} 
                  stroke="#94a3b8"
                  tick={{ fill: '#94a3b8', fontSize: 12 }}
                  width={80}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    padding: '12px',
                  }}
                  labelStyle={{ color: '#e2e8f0', marginBottom: '8px' }}
                  formatter={(value: number) => [formatCurrency(value, { decimals: 0 }), 'Portfolio Value']}
                />
                <Bar dataKey="value" name="Portfolio Value" radius={[4, 4, 0, 0]}>
                  {chartData.distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-80 flex items-center justify-center">
            <p className="text-body text-text-tertiary">Distribution data not available</p>
          </div>
        )}
      </Card>

      {/* Key Metrics Table */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Detailed Metrics
          </h3>
          <p className="text-body text-text-tertiary">
            Comprehensive simulation results and risk metrics
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-background-border">
                <th className="text-left py-3 px-4 text-small font-semibold text-text-secondary uppercase">
                  Metric
                </th>
                <th className="text-right py-3 px-4 text-small font-semibold text-text-secondary uppercase">
                  Value
                </th>
                <th className="text-left py-3 px-4 text-small font-semibold text-text-secondary uppercase">
                  Description
                </th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-background-border hover:bg-background-hover transition-colors">
                <td className="py-3 px-4 text-body font-medium text-text-primary">
                  Success Probability
                </td>
                <td className="py-3 px-4 text-right text-body font-semibold" style={{ color: successRating.color }}>
                  {formatPercent(simulationResults.metrics.success_probability)}
                </td>
                <td className="py-3 px-4 text-small text-text-tertiary">
                  Probability of meeting spending needs throughout planning horizon
                </td>
              </tr>
              <tr className="border-b border-background-border hover:bg-background-hover transition-colors">
                <td className="py-3 px-4 text-body font-medium text-text-primary">
                  Depletion Risk
                </td>
                <td className="py-3 px-4 text-right text-body font-semibold text-status-warning-base">
                  {formatPercent(simulationResults.metrics.depletion_probability)}
                </td>
                <td className="py-3 px-4 text-small text-text-tertiary">
                  Probability of portfolio depleting before end of horizon
                </td>
              </tr>
              <tr className="border-b border-background-border hover:bg-background-hover transition-colors">
                <td className="py-3 px-4 text-body font-medium text-text-primary">
                  Median Ending Value
                </td>
                <td className="py-3 px-4 text-right text-body font-semibold text-text-primary">
                  {formatCurrency(simulationResults.metrics.ending_median)}
                </td>
                <td className="py-3 px-4 text-small text-text-tertiary">
                  50th percentile outcome at end of planning period
                </td>
              </tr>
              <tr className="border-b border-background-border hover:bg-background-hover transition-colors">
                <td className="py-3 px-4 text-body font-medium text-text-primary">
                  Downside (10th Percentile)
                </td>
                <td className="py-3 px-4 text-right text-body font-semibold text-text-primary">
                  {formatCurrency(simulationResults.metrics.ending_p10)}
                </td>
                <td className="py-3 px-4 text-small text-text-tertiary">
                  Conservative outcome - 90% of scenarios exceed this value
                </td>
              </tr>
              <tr className="border-b border-background-border hover:bg-background-hover transition-colors">
                <td className="py-3 px-4 text-body font-medium text-text-primary">
                  Upside (90th Percentile)
                </td>
                <td className="py-3 px-4 text-right text-body font-semibold text-text-primary">
                  {formatCurrency(simulationResults.metrics.ending_p90)}
                </td>
                <td className="py-3 px-4 text-small text-text-tertiary">
                  Optimistic outcome - only 10% of scenarios exceed this value
                </td>
              </tr>
              <tr className="border-b border-background-border hover:bg-background-hover transition-colors">
                <td className="py-3 px-4 text-body font-medium text-text-primary">
                  Years Until Depletion
                </td>
                <td className="py-3 px-4 text-right text-body font-semibold text-text-primary">
                  {(simulationResults.metrics.years_depleted ?? 999) > 100
                    ? 'Never'
                    : `Year ${Math.round(simulationResults.metrics.years_depleted ?? 0)}`}
                </td>
                <td className="py-3 px-4 text-small text-text-tertiary">
                  Average time until portfolio depletion across failed scenarios
                </td>
              </tr>
              <tr className="hover:bg-background-hover transition-colors">
                <td className="py-3 px-4 text-body font-medium text-text-primary">
                  Shortfall Risk
                </td>
                <td className="py-3 px-4 text-right text-body font-semibold text-status-warning-base">
                  {formatPercent(simulationResults.metrics.shortfall_risk)}
                </td>
                <td className="py-3 px-4 text-small text-text-tertiary">
                  Risk of not meeting financial goals throughout planning period
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* Planning Assumptions */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Planning Assumptions
          </h3>
          <p className="text-body text-text-tertiary">
            Input parameters used for this simulation
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-h4 font-semibold text-text-primary mb-4">Portfolio</h4>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-body text-text-tertiary">Starting Portfolio</span>
                <span className="text-body font-medium text-text-primary">
                  {formatCurrency(modelInputs.starting_portfolio, { decimals: 0 })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-body text-text-tertiary">Equity Allocation</span>
                <span className="text-body font-medium text-text-primary">
                  {formatPercent(modelInputs.equity_pct)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-body text-text-tertiary">Fixed Income</span>
                <span className="text-body font-medium text-text-primary">
                  {formatPercent(modelInputs.fi_pct)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-body text-text-tertiary">Cash</span>
                <span className="text-body font-medium text-text-primary">
                  {formatPercent(modelInputs.cash_pct)}
                </span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-h4 font-semibold text-text-primary mb-4">Returns & Spending</h4>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-body text-text-tertiary">Equity Return (Annual)</span>
                <span className="text-body font-medium text-text-primary">
                  {formatPercent(modelInputs.equity_return_annual)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-body text-text-tertiary">Monthly Spending</span>
                <span className="text-body font-medium text-text-primary">
                  {formatCurrency(Math.abs(modelInputs.monthly_spending ?? 0), { decimals: 0 })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-body text-text-tertiary">Inflation Rate</span>
                <span className="text-body font-medium text-text-primary">
                  {formatPercent(modelInputs.inflation_annual)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-body text-text-tertiary">Planning Horizon</span>
                <span className="text-body font-medium text-text-primary">
                  {modelInputs.years_to_model || 'N/A'} years
                </span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Disclaimer */}
      <Card padding="lg">
        <div className="text-small text-text-tertiary space-y-2">
          <p className="font-semibold text-text-secondary">Important Disclaimers:</p>
          <p>
            This analysis is based on Monte Carlo simulation using historical return and volatility assumptions. 
            Past performance does not guarantee future results. Actual outcomes may differ materially from projections.
          </p>
          <p>
            Consult with qualified financial, tax, and legal professionals before making investment decisions. 
            This report does not constitute investment advice.
          </p>
        </div>
      </Card>

      {/* Export Progress Notification */}
      {showExportProgress && (
        <ExportProgress
          format={exportFormats.find(f => f.id === exportingFormat)?.name || 'Report'}
          status={exportStatus}
          message={exportMessage}
          onClose={() => setShowExportProgress(false)}
        />
      )}
    </div>
  );
};

export default ReportsPage;
