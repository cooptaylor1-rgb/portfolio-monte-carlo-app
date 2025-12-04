/**
 * Export Utilities for Monte Carlo Analytics
 * Handles PDF, PowerPoint, and Image exports
 */

import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

interface ExportOptions {
  filename?: string;
  includeCharts?: string[];
  quality?: number;
}

/**
 * Export a single chart as PNG image
 */
export const exportChartAsPNG = async (
  elementId: string,
  filename: string = 'chart.png'
): Promise<void> => {
  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`Element with id "${elementId}" not found`);
    return;
  }

  try {
    const canvas = await html2canvas(element, {
      scale: 2,
      backgroundColor: '#ffffff',
      logging: false,
      useCORS: true,
    });

    const link = document.createElement('a');
    link.download = filename;
    link.href = canvas.toDataURL('image/png');
    link.click();
  } catch (error) {
    console.error('Error exporting chart as PNG:', error);
    throw error;
  }
};

/**
 * Export all visible charts as PNG images (zipped)
 */
export const exportAllChartsAsPNG = async (
  chartIds: string[],
  baseFilename: string = 'chart'
): Promise<void> => {
  for (let i = 0; i < chartIds.length; i++) {
    const elementId = chartIds[i];
    const filename = `${baseFilename}_${i + 1}.png`;
    await exportChartAsPNG(elementId, filename);
    // Add delay between exports to avoid overwhelming the browser
    await new Promise(resolve => setTimeout(resolve, 500));
  }
};

/**
 * Export analytics page as PDF
 */
export const exportAnalyticsAsPDF = async (
  containerId: string = 'analytics-container',
  options: ExportOptions = {}
): Promise<void> => {
  const { filename = 'Monte_Carlo_Analytics.pdf', quality = 2 } = options;
  
  const element = document.getElementById(containerId);
  if (!element) {
    console.error(`Container with id "${containerId}" not found`);
    return;
  }

  try {
    // Create canvas from HTML
    const canvas = await html2canvas(element, {
      scale: quality,
      backgroundColor: '#ffffff',
      logging: false,
      useCORS: true,
      windowHeight: element.scrollHeight,
      windowWidth: element.scrollWidth,
    });

    const imgData = canvas.toDataURL('image/png');
    
    // Calculate PDF dimensions
    const imgWidth = 210; // A4 width in mm
    const pageHeight = 297; // A4 height in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    
    const pdf = new jsPDF('p', 'mm', 'a4');
    let heightLeft = imgHeight;
    let position = 0;

    // Add first page
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    // Add additional pages if content is longer than one page
    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    pdf.save(filename);
  } catch (error) {
    console.error('Error exporting as PDF:', error);
    throw error;
  }
};

/**
 * Export individual charts as separate PDF pages
 */
export const exportChartsAsSeparatePDFs = async (
  chartIds: string[],
  baseFilename: string = 'chart'
): Promise<void> => {
  for (let i = 0; i < chartIds.length; i++) {
    const elementId = chartIds[i];
    const element = document.getElementById(elementId);
    
    if (!element) {
      console.warn(`Chart "${elementId}" not found, skipping...`);
      continue;
    }

    try {
      const canvas = await html2canvas(element, {
        scale: 2,
        backgroundColor: '#ffffff',
        logging: false,
        useCORS: true,
      });

      const imgData = canvas.toDataURL('image/png');
      const imgWidth = 210; // A4 width in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      // Center image if it's smaller than page
      const yPosition = imgHeight < 297 ? (297 - imgHeight) / 2 : 0;
      pdf.addImage(imgData, 'PNG', 0, yPosition, imgWidth, Math.min(imgHeight, 297));
      
      const filename = `${baseFilename}_${i + 1}.pdf`;
      pdf.save(filename);
      
      // Add delay between exports
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (error) {
      console.error(`Error exporting chart "${elementId}" as PDF:`, error);
    }
  }
};

/**
 * Export analytics as PowerPoint (simplified version using images)
 * Note: Full PPTX generation would require pptxgenjs library
 */
export const exportAnalyticsAsPowerPoint = async (
  chartIds: string[],
  clientName: string = 'Client',
  filename: string = 'Monte_Carlo_Analytics.pptx'
): Promise<void> => {
  // This is a placeholder for PowerPoint export
  // In production, you would use pptxgenjs or similar library
  
  console.log('PowerPoint export coming soon. For now, exporting as PDF...');
  await exportAnalyticsAsPDF('analytics-container', { filename: filename.replace('.pptx', '.pdf') });
};

/**
 * Generate summary statistics for export
 */
export const generateExportSummary = (
  metrics: any,
  inputs: any,
  clientName: string
): string => {
  return `
Monte Carlo Analysis Summary
Client: ${clientName}
Date: ${new Date().toLocaleDateString()}

Portfolio Inputs:
- Starting Portfolio: $${inputs.starting_portfolio.toLocaleString()}
- Planning Horizon: ${inputs.years_to_model} years (Age ${inputs.current_age} to ${inputs.horizon_age})
- Monthly Spending: $${Math.abs(inputs.monthly_spending).toLocaleString()}
- Asset Allocation: ${inputs.equity_pct}% Equity, ${inputs.fi_pct}% Fixed Income, ${inputs.cash_pct}% Cash

Key Results:
- Success Probability: ${(metrics.success_probability * 100).toFixed(1)}%
- Ending Median: $${metrics.ending_median.toLocaleString()}
- 10th Percentile: $${metrics.ending_p10.toLocaleString()}
- 90th Percentile: $${metrics.ending_p90.toLocaleString()}
- Depletion Probability: ${(metrics.depletion_probability * 100).toFixed(1)}%
  `;
};

/**
 * Copy summary to clipboard
 */
export const copySummaryToClipboard = async (summary: string): Promise<void> => {
  try {
    await navigator.clipboard.writeText(summary);
    console.log('Summary copied to clipboard');
  } catch (error) {
    console.error('Failed to copy summary:', error);
    throw error;
  }
};

/**
 * Download text summary as file
 */
export const downloadTextSummary = (
  summary: string,
  filename: string = 'analysis_summary.txt'
): void => {
  const blob = new Blob([summary], { type: 'text/plain' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
};

export default {
  exportChartAsPNG,
  exportAllChartsAsPNG,
  exportAnalyticsAsPDF,
  exportChartsAsSeparatePDFs,
  exportAnalyticsAsPowerPoint,
  generateExportSummary,
  copySummaryToClipboard,
  downloadTextSummary,
};
