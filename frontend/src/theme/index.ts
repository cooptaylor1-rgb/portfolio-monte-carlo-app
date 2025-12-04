/**
 * Design System - Central Export
 * Single source of truth for all design tokens and utilities
 * Import everything from here for consistency
 */

// Export all design tokens
export * from './tokens';

// Export chart utilities
export * from './chartUtils';

// Re-export for convenience
export {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  layout,
  chartTheme,
} from './tokens';

export {
  chartColors,
  getPercentileColor,
  getChartGradients,
  rechartsTheme,
  getDefaultChartConfig,
  formatChartCurrency,
  formatChartPercent,
  formatChartAge,
  getValueColor,
} from './chartUtils';
