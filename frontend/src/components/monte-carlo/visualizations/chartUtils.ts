/**
 * Shared utilities for Monte Carlo visualizations
 * Provides consistent formatting, colors, and helper functions
 * Now uses centralized theme tokens for consistency
 */

import { colors, chartTheme as themeChartConfig, typography, spacing } from '../../../theme';

// Salem Investment Counselors Brand Colors (re-exported from theme for backwards compatibility)
export const salemColors = {
  navy: colors.brand.navy,
  gold: colors.brand.gold,
  white: colors.text.primary,
  lightGray: colors.background.hover,
  mediumGray: colors.background.border,
  darkGray: colors.text.tertiary,
  
  // Chart-specific colors
  success: colors.status.success.base,
  warning: colors.status.warning.base,
  danger: colors.status.error.base,
  info: colors.status.info.base,
  
  // Percentile colors
  p10: colors.chart.p10,
  p25: colors.chart.p25,
  p50: colors.chart.p50,
  p75: colors.chart.p75,
  p90: colors.chart.p90,
  
  // Chart lines (using status colors for variety)
  line1: colors.status.info.base,
  line2: '#8B5CF6',   // Purple (custom)
  line3: '#EC4899',   // Pink (custom)
  line4: colors.status.warning.base,
  line5: colors.status.success.base,
};

// Chart theme configuration from centralized theme
export const chartTheme = {
  backgroundColor: colors.background.elevated,
  textColor: colors.text.secondary,
  gridColor: colors.background.border,
  tooltipBackground: colors.background.base,
  tooltipBorder: colors.background.border,
  
  fonts: {
    title: { fontSize: 20, fontWeight: typography.fontWeight.semibold, fontFamily: typography.fontFamily.display },
    subtitle: { fontSize: 16, fontWeight: typography.fontWeight.medium, fontFamily: typography.fontFamily.sans },
    label: { fontSize: 14, fontWeight: typography.fontWeight.normal, fontFamily: typography.fontFamily.sans },
    small: { fontSize: 12, fontWeight: typography.fontWeight.normal, fontFamily: typography.fontFamily.sans },
  },
  
  spacing: {
    chartMargin: themeChartConfig.margin,
    padding: parseInt(spacing.md),
  },
};

// Currency formatting utilities
export const formatCurrency = (value: number, decimals: number = 0): string => {
  if (Math.abs(value) >= 1000000) {
    return `$${(value / 1000000).toFixed(decimals)}M`;
  }
  if (Math.abs(value) >= 1000) {
    return `$${(value / 1000).toFixed(decimals)}K`;
  }
  return `$${value.toFixed(decimals)}`;
};

export const formatCurrencyFull = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

// Percentage formatting
export const formatPercent = (value: number, decimals: number = 1): string => {
  return `${(value * 100).toFixed(decimals)}%`;
};

export const formatPercentSimple = (value: number): string => {
  return `${value.toFixed(0)}%`;
};

// Age/Year formatting
export const formatAge = (age: number): string => {
  return `Age ${Math.round(age)}`;
};

export const formatYear = (year: number): string => {
  return `Year ${Math.round(year)}`;
};

// Risk level determination
export interface RiskLevel {
  level: 'Low' | 'Moderate' | 'High' | 'Very High';
  color: string;
  description: string;
}

export const getRiskLevel = (successProbability: number): RiskLevel => {
  if (successProbability >= 0.90) {
    return {
      level: 'Low',
      color: salemColors.success,
      description: 'Excellent chance of meeting goals',
    };
  }
  if (successProbability >= 0.80) {
    return {
      level: 'Moderate',
      color: salemColors.info,
      description: 'Good chance of meeting goals',
    };
  }
  if (successProbability >= 0.70) {
    return {
      level: 'High',
      color: salemColors.warning,
      description: 'Moderate risk of shortfall',
    };
  }
  return {
    level: 'Very High',
    color: salemColors.danger,
    description: 'Significant risk of shortfall',
  };
};

// Tooltip styling for recharts
export const getTooltipStyle = () => ({
  backgroundColor: chartTheme.tooltipBackground,
  border: `1px solid ${chartTheme.tooltipBorder}`,
  borderRadius: '8px',
  padding: '12px',
  boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
});

// Custom tooltip formatter
export const formatTooltipValue = (value: number, name: string): [string, string] => {
  if (name.toLowerCase().includes('probability') || name.toLowerCase().includes('rate')) {
    return [formatPercent(value), name];
  }
  return [formatCurrency(value), name];
};

// Calculate percentile from array
export const calculatePercentile = (arr: number[], percentile: number): number => {
  const sorted = [...arr].sort((a, b) => a - b);
  const index = (percentile / 100) * (sorted.length - 1);
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  const weight = index % 1;
  
  if (lower === upper) return sorted[lower];
  return sorted[lower] * (1 - weight) + sorted[upper] * weight;
};

// Generate year labels for charts
export const generateYearLabels = (startAge: number, years: number): string[] => {
  return Array.from({ length: years + 1 }, (_, i) => formatAge(startAge + i));
};

// Color interpolation for gradients
export const interpolateColor = (color1: string, color2: string, factor: number): string => {
  const c1 = parseInt(color1.slice(1), 16);
  const c2 = parseInt(color2.slice(1), 16);
  
  const r1 = (c1 >> 16) & 0xff;
  const g1 = (c1 >> 8) & 0xff;
  const b1 = c1 & 0xff;
  
  const r2 = (c2 >> 16) & 0xff;
  const g2 = (c2 >> 8) & 0xff;
  const b2 = c2 & 0xff;
  
  const r = Math.round(r1 + factor * (r2 - r1));
  const g = Math.round(g1 + factor * (g2 - g1));
  const b = Math.round(b1 + factor * (b2 - b1));
  
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
};

// Conservative messaging helper
export const getConservativeMessage = (metric: string, value: number): string => {
  const messages: Record<string, (v: number) => string> = {
    successProbability: (v) => {
      if (v >= 0.90) return 'Strong likelihood of meeting your financial goals';
      if (v >= 0.80) return 'Good chance of success with some buffer for adverse conditions';
      if (v >= 0.70) return 'Consider adjustments to improve plan resilience';
      return 'Plan may benefit from significant adjustments';
    },
    depletionRisk: (v) => {
      if (v <= 0.10) return 'Low risk of running out of funds during planning period';
      if (v <= 0.20) return 'Moderate risk suggests reviewing spending or allocation';
      if (v <= 0.30) return 'Elevated risk warrants plan modifications';
      return 'High risk indicates need for substantial plan changes';
    },
  };
  
  return messages[metric]?.(value) || '';
};

// Export-friendly chart dimensions
export const exportDimensions = {
  fullWidth: 1200,
  halfWidth: 580,
  standardHeight: 400,
  tallHeight: 600,
  shortHeight: 300,
};

// Key takeaway box styling (using theme tokens)
export const keyTakeawayStyle: React.CSSProperties = {
  backgroundColor: colors.background.elevated,
  border: `2px solid ${colors.brand.gold}`,
  borderRadius: '8px',
  padding: spacing.md,
  marginTop: spacing.md,
  fontFamily: typography.fontFamily.sans,
  fontSize: typography.fontSize.body.size,
  lineHeight: typography.fontSize.body.lineHeight,
  color: colors.status.warning.light,
};

// Chart container styling (using theme tokens)
export const chartContainerStyle: React.CSSProperties = {
  backgroundColor: colors.background.elevated,
  border: `1px solid ${colors.background.border}`,
  borderRadius: '12px',
  padding: spacing.lg,
  marginBottom: spacing.lg,
  boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
};

// Section header styling (using theme tokens)
export const sectionHeaderStyle: React.CSSProperties = {
  color: colors.brand.gold,
  fontSize: typography.fontSize.h2.size,
  fontWeight: typography.fontWeight.semibold,
  fontFamily: typography.fontFamily.display,
  marginBottom: spacing.md,
  paddingBottom: spacing.sm,
  borderBottom: `3px solid ${colors.brand.gold}`,
};
