/**
 * Shared utilities for Monte Carlo visualizations
 * Provides consistent formatting, colors, and helper functions
 */

// Salem Investment Counselors Brand Colors
export const salemColors = {
  navy: '#0F3B63',
  gold: '#B49759',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  mediumGray: '#E0E0E0',
  darkGray: '#424242',
  
  // Chart-specific colors
  success: '#10B981', // Green
  warning: '#F59E0B', // Amber
  danger: '#EF4444',  // Red
  info: '#3B82F6',    // Blue
  
  // Percentile colors (conservative blue-to-gold gradient)
  p10: '#DC2626',     // Deep red for worst case
  p25: '#F59E0B',     // Amber
  p50: '#B49759',     // Salem Gold for median
  p75: '#10B981',     // Green
  p90: '#059669',     // Deep green for best case
  
  // Chart lines
  line1: '#3B82F6',   // Blue
  line2: '#8B5CF6',   // Purple
  line3: '#EC4899',   // Pink
  line4: '#F59E0B',   // Amber
  line5: '#10B981',   // Green
};

// Chart theme configuration matching Salem branding
export const chartTheme = {
  backgroundColor: '#1E293B',
  textColor: '#E2E8F0',
  gridColor: '#334155',
  tooltipBackground: '#0F172A',
  tooltipBorder: '#475569',
  
  fonts: {
    title: { fontSize: 20, fontWeight: 600, fontFamily: 'Inter, sans-serif' },
    subtitle: { fontSize: 16, fontWeight: 500, fontFamily: 'Inter, sans-serif' },
    label: { fontSize: 14, fontWeight: 400, fontFamily: 'Inter, sans-serif' },
    small: { fontSize: 12, fontWeight: 400, fontFamily: 'Inter, sans-serif' },
  },
  
  spacing: {
    chartMargin: { top: 20, right: 30, left: 60, bottom: 40 },
    padding: 16,
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

// Key takeaway box styling
export const keyTakeawayStyle: React.CSSProperties = {
  backgroundColor: '#1E293B',
  border: `2px solid ${salemColors.gold}`,
  borderRadius: '8px',
  padding: '16px 20px',
  marginTop: '16px',
  fontFamily: 'Inter, sans-serif',
  fontSize: '14px',
  lineHeight: '1.6',
  color: '#FCD34D',
};

// Chart container styling
export const chartContainerStyle: React.CSSProperties = {
  backgroundColor: '#1E293B',
  border: '1px solid #334155',
  borderRadius: '12px',
  padding: '24px',
  marginBottom: '24px',
  boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
};

// Section header styling
export const sectionHeaderStyle: React.CSSProperties = {
  color: salemColors.gold,
  fontSize: '24px',
  fontWeight: 600,
  fontFamily: 'Inter, sans-serif',
  marginBottom: '16px',
  paddingBottom: '12px',
  borderBottom: `3px solid ${salemColors.gold}`,
};
