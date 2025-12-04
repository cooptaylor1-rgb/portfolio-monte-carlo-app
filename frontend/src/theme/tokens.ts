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
    gold: '#C4A76A',        // Updated for better contrast (WCAG AA)
    goldLight: '#D4B77A',
    goldDark: '#A4875A',
  },

  // Background Palette (Dark Mode) - Updated for better contrast
  background: {
    base: '#0F1419',        // Slightly lighter for better contrast
    elevated: '#1A1F26',    // Clearer elevation
    hover: '#252B33',       // Better hover indication
    border: '#34393F',      // More visible borders
  },

  // Text Colors - WCAG AA Compliant
  text: {
    primary: '#FFFFFF',
    secondary: '#C9D1D9',   // Updated for better contrast
    tertiary: '#8B949E',    // Updated to meet WCAG AA standard
    disabled: '#6A737D',    // Clearer disabled state
  },

  // Semantic Status Colors - Professional and accessible
  status: {
    success: {
      base: '#3FB950',      // Better for financial context
      light: '#56D364',
      dark: '#2EA043',
    },
    warning: {
      base: '#D29922',      // Warmer amber
      light: '#E3B341',
      dark: '#BB8009',
    },
    error: {
      base: '#F85149',      // Softer red, less alarming
      light: '#FF7B72',
      dark: '#DA3633',
    },
    info: {
      base: '#58A6FF',      // Softer blue
      light: '#79C0FF',
      dark: '#388BFD',
    },
  },

  // Chart-specific Colors - Color blind friendly
  chart: {
    equity: '#58A6FF',     // Blue - distinguishable
    fixed: '#56D364',      // Green
    cash: '#D29922',       // Amber/gold
    projection: '#7AA6C4',
    
    // Percentile colors - sequential, distinguishable
    p90: '#56D364',        // Best case - green
    p75: '#7EE787',        // Light green
    p50: '#D29922',        // Median - amber/gold
    p25: '#FF9A56',        // Orange
    p10: '#F85149',        // Worst case - red
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
// BORDER RADIUS - Refined for professional financial software
// ============================================================================

export const borderRadius = {
  sm: '4px',    // Inputs, small buttons, tags
  md: '8px',    // Cards, modals, large buttons
  lg: '12px',   // Hero cards, feature panels
  xl: '16px',   // Special emphasis, overlays
  full: '9999px', // Pills, badges
} as const;

// ============================================================================
// SHADOWS - Stronger for dark theme
// ============================================================================

export const shadows = {
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.5)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.6)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.7)',
  glow: '0 0 20px rgba(196, 167, 106, 0.25)',        // Updated gold value
  glowStrong: '0 0 30px rgba(196, 167, 106, 0.4)',   // Updated gold value
} as const;

// ============================================================================
// TRANSITIONS - Fast and purposeful
// ============================================================================

export const transitions = {
  duration: {
    fast: '100ms',      // Micro interactions
    default: '200ms',   // Standard transitions
    slow: '350ms',      // Complex animations
  },
  timing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',            // Ease-in-out
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',   // Bouncy
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
