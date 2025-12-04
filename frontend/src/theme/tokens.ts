/**
 * Design System Tokens
 * Centralized design tokens matching Tailwind configuration
 * Single source of truth for colors, typography, spacing, and other design values
 */

// ============================================================================
// COLOR PALETTE
// ============================================================================

export const colors = {
  // Brand Colors
  brand: {
    navy: '#0F3B63',
    navyLight: '#1F4F7C',
    navyDark: '#082539',
    gold: '#B49759',
    goldLight: '#C4A76A',
    goldDark: '#9A834D',
  },

  // Background Palette (Dark Mode)
  background: {
    base: '#0A0C10',
    elevated: '#12141A',
    hover: '#1A1D24',
    border: '#262A33',
  },

  // Text Colors
  text: {
    primary: '#FFFFFF',
    secondary: '#B4B9C2',
    tertiary: '#6F767D',
    disabled: '#4A5057',
  },

  // Semantic Status Colors
  status: {
    success: {
      base: '#10B981',
      light: '#34D399',
      dark: '#059669',
    },
    warning: {
      base: '#F59E0B',
      light: '#FBBF24',
      dark: '#D97706',
    },
    error: {
      base: '#EF4444',
      light: '#F87171',
      dark: '#DC2626',
    },
    info: {
      base: '#3B82F6',
      light: '#60A5FA',
      dark: '#2563EB',
    },
  },

  // Chart-specific Colors
  chart: {
    equity: '#4CA6E8',
    fixed: '#7AC18D',
    cash: '#D7B46A',
    projection: '#7AA6C4',
    
    // Percentile colors
    p90: '#059669', // Best case - deep green
    p75: '#10B981', // Green
    p50: '#B49759', // Salem Gold - median
    p25: '#F59E0B', // Amber
    p10: '#DC2626', // Worst case - deep red
  },
} as const;

// ============================================================================
// TYPOGRAPHY
// ============================================================================

export const typography = {
  // Font Families
  fontFamily: {
    sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'].join(', '),
    display: ['Nunito Sans', 'system-ui', '-apple-system', 'sans-serif'].join(', '),
    mono: ['JetBrains Mono', 'Monaco', 'Courier New', 'monospace'].join(', '),
  },

  // Font Sizes with Line Heights
  fontSize: {
    display: { size: '36px', lineHeight: '44px', letterSpacing: '-0.02em', fontWeight: 700 },
    h1: { size: '32px', lineHeight: '40px', letterSpacing: '-0.02em', fontWeight: 700 },
    h2: { size: '24px', lineHeight: '32px', letterSpacing: '-0.01em', fontWeight: 600 },
    h3: { size: '18px', lineHeight: '28px', letterSpacing: '0', fontWeight: 600 },
    h4: { size: '16px', lineHeight: '24px', letterSpacing: '0', fontWeight: 600 },
    body: { size: '14px', lineHeight: '20px', letterSpacing: '0', fontWeight: 400 },
    small: { size: '12px', lineHeight: '16px', letterSpacing: '0', fontWeight: 400 },
    micro: { size: '11px', lineHeight: '14px', letterSpacing: '0', fontWeight: 400 },
  },

  // Font Weights
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
} as const;

// ============================================================================
// SPACING
// ============================================================================

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
  '3xl': '64px',
} as const;

// ============================================================================
// BORDER RADIUS
// ============================================================================

export const borderRadius = {
  sm: '6px',
  md: '8px',
  lg: '12px',
  xl: '16px',
} as const;

// ============================================================================
// SHADOWS
// ============================================================================

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.3)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.2)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.3)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.3)',
  glow: '0 0 20px rgb(180 151 89 / 0.3)',
  glowStrong: '0 0 30px rgb(180 151 89 / 0.5)',
} as const;

// ============================================================================
// TRANSITIONS
// ============================================================================

export const transitions = {
  duration: {
    fast: '150ms',
    default: '200ms',
    slow: '300ms',
  },
  timing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  },
} as const;

// ============================================================================
// LAYOUT
// ============================================================================

export const layout = {
  maxWidth: {
    container: '1440px',
    content: '1200px',
    narrow: '800px',
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
} as const;

// ============================================================================
// CHART THEME (for Recharts and other chart libraries)
// ============================================================================

export const chartTheme = {
  // Background colors
  background: colors.background.elevated,
  gridColor: colors.background.border,
  
  // Text styling
  textColor: colors.text.secondary,
  labelColor: colors.text.primary,
  
  // Tooltip styling
  tooltip: {
    background: colors.background.base,
    border: colors.background.border,
    textColor: colors.text.primary,
  },
  
  // Axis styling
  axis: {
    stroke: colors.background.border,
    tickColor: colors.text.secondary,
  },
  
  // Font configuration
  fonts: {
    title: { 
      fontSize: 20, 
      fontWeight: typography.fontWeight.semibold, 
      fontFamily: typography.fontFamily.display,
      fill: colors.text.primary,
    },
    subtitle: { 
      fontSize: 16, 
      fontWeight: typography.fontWeight.medium, 
      fontFamily: typography.fontFamily.sans,
      fill: colors.text.secondary,
    },
    label: { 
      fontSize: 14, 
      fontWeight: typography.fontWeight.normal, 
      fontFamily: typography.fontFamily.sans,
      fill: colors.text.secondary,
    },
    small: { 
      fontSize: 12, 
      fontWeight: typography.fontWeight.normal, 
      fontFamily: typography.fontFamily.sans,
      fill: colors.text.tertiary,
    },
  },
  
  // Standard margins for consistency
  margin: {
    top: 20,
    right: 30,
    left: 60,
    bottom: 40,
  },
} as const;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get status color based on success probability
 */
export function getSuccessColor(probability: number): string {
  if (probability >= 0.85) return colors.status.success.base;
  if (probability >= 0.70) return colors.status.warning.base;
  return colors.status.error.base;
}

/**
 * Get risk level based on value (inverse of success)
 */
export function getRiskColor(riskValue: number): string {
  if (riskValue <= 0.15) return colors.status.success.base;
  if (riskValue <= 0.30) return colors.status.warning.base;
  return colors.status.error.base;
}

/**
 * Format currency values consistently
 */
export function formatCurrency(value: number, decimals: number = 0): string {
  if (Math.abs(value) >= 1000000) {
    return `$${(value / 1000000).toFixed(decimals)}M`;
  }
  if (Math.abs(value) >= 1000) {
    return `$${(value / 1000).toFixed(decimals)}K`;
  }
  return `$${value.toFixed(decimals)}`;
}

/**
 * Format percentage values consistently
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Create CSS style object from typography tokens
 */
export function getTypographyStyle(size: keyof typeof typography.fontSize) {
  const style = typography.fontSize[size];
  return {
    fontSize: style.size,
    lineHeight: style.lineHeight,
    letterSpacing: style.letterSpacing,
    fontWeight: style.fontWeight,
  };
}
