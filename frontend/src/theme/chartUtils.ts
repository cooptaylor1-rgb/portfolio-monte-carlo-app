/**
 * Chart Utilities - Design System Integration
 * All chart colors and configurations sourced from design system
 * Use these utilities for consistent chart styling across the app
 */

import { colors } from './tokens';

// ============================================================================
// CHART COLORS
// ============================================================================

export const chartColors = {
  // Asset allocation
  equity: colors.chart.equity,
  fixed: colors.chart.fixed,
  cash: colors.chart.cash,
  projection: colors.chart.projection,
  
  // Percentile bands (ordered best to worst)
  percentiles: {
    p90: colors.chart.p90,
    p75: colors.chart.p75,
    p50: colors.chart.p50,
    p25: colors.chart.p25,
    p10: colors.chart.p10,
  },
  
  // Status colors for charts
  success: colors.status.success.base,
  warning: colors.status.warning.base,
  error: colors.status.error.base,
  info: colors.status.info.base,
  
  // Brand colors
  navy: colors.brand.navy,
  gold: colors.brand.gold,
};

// ============================================================================
// CHART UTILITIES
// ============================================================================

/**
 * Get color for percentile value
 * @param percentile - 10, 25, 50, 75, or 90
 * @returns Hex color string
 */
export function getPercentileColor(percentile: 10 | 25 | 50 | 75 | 90): string {
  const key = `p${percentile}` as keyof typeof chartColors.percentiles;
  return chartColors.percentiles[key];
}

/**
 * Get chart gradient definitions for Recharts
 * @returns Object with gradient configurations
 */
export function getChartGradients() {
  return {
    percentileGradient: [
      { offset: '0%', color: chartColors.percentiles.p90, opacity: 0.3 },
      { offset: '100%', color: chartColors.percentiles.p90, opacity: 0.1 },
    ],
    successGradient: [
      { offset: '0%', color: chartColors.success, opacity: 0.3 },
      { offset: '100%', color: chartColors.success, opacity: 0.1 },
    ],
    warningGradient: [
      { offset: '0%', color: chartColors.warning, opacity: 0.3 },
      { offset: '100%', color: chartColors.warning, opacity: 0.1 },
    ],
    errorGradient: [
      { offset: '0%', color: chartColors.error, opacity: 0.3 },
      { offset: '100%', color: chartColors.error, opacity: 0.1 },
    ],
  };
}

/**
 * Common Recharts theme configuration
 * Use this for consistent chart styling
 */
export const rechartsTheme = {
  // Background
  background: colors.background.elevated,
  
  // Grid and axes
  gridColor: colors.background.border,
  axisColor: colors.text.tertiary,
  
  // Text colors
  textColor: colors.text.secondary,
  labelColor: colors.text.primary,
  
  // Tooltip styling
  tooltip: {
    background: colors.background.base,
    border: colors.background.border,
    textColor: colors.text.primary,
    labelColor: colors.text.secondary,
  },
  
  // Legend styling
  legend: {
    textColor: colors.text.secondary,
    iconSize: 12,
  },
  
  // Line and area defaults
  strokeWidth: {
    thin: 1,
    default: 2,
    thick: 3,
  },
  
  // Opacity levels
  opacity: {
    full: 1,
    high: 0.8,
    medium: 0.6,
    low: 0.4,
    veryLow: 0.2,
  },
};

/**
 * Get default Recharts configuration
 * @returns Object with common Recharts props
 */
export function getDefaultChartConfig() {
  return {
    margin: { top: 20, right: 30, left: 20, bottom: 20 },
    style: {
      fontFamily: 'Inter, system-ui, sans-serif',
      fontSize: '12px',
    },
  };
}

/**
 * Format currency for chart labels
 * @param value - Number to format
 * @param compact - Use compact notation (K, M, B)
 * @returns Formatted string
 */
export function formatChartCurrency(value: number, compact: boolean = false): string {
  if (compact) {
    if (Math.abs(value) >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(1)}B`;
    }
    if (Math.abs(value) >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(1)}M`;
    }
    if (Math.abs(value) >= 1_000) {
      return `$${(value / 1_000).toFixed(0)}K`;
    }
  }
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Format percentage for chart labels
 * @param value - Number to format (0-1 or 0-100)
 * @param asDecimal - Whether input is decimal (0-1) or percentage (0-100)
 * @returns Formatted string
 */
export function formatChartPercent(value: number, asDecimal: boolean = true): string {
  const percentValue = asDecimal ? value * 100 : value;
  return `${percentValue.toFixed(1)}%`;
}

/**
 * Format age for chart labels
 * @param age - Age value
 * @returns Formatted string
 */
export function formatChartAge(age: number): string {
  return `Age ${age}`;
}

/**
 * Get color based on value range (for heatmaps, risk indicators)
 * @param value - Value between 0-1
 * @param reverse - Reverse color scale (green for low, red for high)
 * @returns Hex color string
 */
export function getValueColor(value: number, reverse: boolean = false): string {
  // Clamp value between 0 and 1
  const clampedValue = Math.max(0, Math.min(1, value));
  
  if (reverse) {
    // Green for low values, red for high (risk)
    if (clampedValue < 0.33) return chartColors.success;
    if (clampedValue < 0.67) return chartColors.warning;
    return chartColors.error;
  } else {
    // Green for high values, red for low (success)
    if (clampedValue < 0.33) return chartColors.error;
    if (clampedValue < 0.67) return chartColors.warning;
    return chartColors.success;
  }
}
