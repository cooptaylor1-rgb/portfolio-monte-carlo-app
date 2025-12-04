/**
 * Presentation Mode Theme Configuration
 * 
 * High-contrast dark theme optimized for:
 * - Conference room projectors
 * - Zoom screen sharing
 * - iPad presentations
 * - Client-facing meetings
 */

export const presentationTheme = {
  // Color palette - Salem brand with high contrast
  colors: {
    // Primary brand colors
    navy: '#0F3B63',
    navyLight: '#1A4D7D',
    gold: '#B49759',
    goldLight: '#D4B97A',
    
    // Dark theme backgrounds
    background: {
      primary: '#0A0A0A',
      secondary: '#1A1A1A',
      tertiary: '#2A2A2A',
      overlay: 'rgba(0, 0, 0, 0.95)',
    },
    
    // Text colors - high contrast
    text: {
      primary: '#FFFFFF',
      secondary: '#E0E0E0',
      muted: '#9CA3AF',
      accent: '#B49759',
    },
    
    // Chart colors - professional and accessible
    chart: {
      primary: '#B49759',      // Gold - main metric
      secondary: '#0F3B63',    // Navy - secondary data
      success: '#10B981',      // Green - positive outcomes
      warning: '#F59E0B',      // Amber - caution areas
      danger: '#EF4444',       // Red - risk/concern areas
      info: '#3B82F6',         // Blue - informational
      
      // Gradient colors for distributions
      gradients: {
        positive: ['#10B981', '#059669', '#047857'],
        neutral: ['#B49759', '#9A7D47', '#806636'],
        negative: ['#EF4444', '#DC2626', '#B91C1C'],
      },
      
      // Percentile lines
      percentiles: {
        p10: '#EF4444',   // 10th percentile - red
        p25: '#F59E0B',   // 25th percentile - amber
        p50: '#B49759',   // Median - gold (highlighted)
        p75: '#10B981',   // 75th percentile - green
        p90: '#059669',   // 90th percentile - dark green
      },
    },
    
    // UI elements
    border: '#374151',
    divider: '#2A2A2A',
    shadow: 'rgba(0, 0, 0, 0.5)',
  },
  
  // Typography system
  typography: {
    // Font families
    fonts: {
      primary: 'Inter, system-ui, -apple-system, sans-serif',
      secondary: 'Nunito Sans, system-ui, sans-serif',
      mono: 'SF Mono, Monaco, monospace',
    },
    
    // Slide titles - large and impactful
    slideTitle: {
      fontSize: '3.5rem',      // 56px
      fontWeight: 700,
      lineHeight: 1.1,
      letterSpacing: '-0.02em',
    },
    
    // Section headings
    heading: {
      fontSize: '2.25rem',     // 36px
      fontWeight: 600,
      lineHeight: 1.2,
      letterSpacing: '-0.01em',
    },
    
    // Subheadings
    subheading: {
      fontSize: '1.5rem',      // 24px
      fontWeight: 600,
      lineHeight: 1.3,
    },
    
    // Body text - readable from distance
    body: {
      fontSize: '1.25rem',     // 20px
      fontWeight: 400,
      lineHeight: 1.6,
    },
    
    // Metric values - large and bold
    metric: {
      fontSize: '3rem',        // 48px
      fontWeight: 700,
      lineHeight: 1,
    },
    
    // Labels
    label: {
      fontSize: '1rem',        // 16px
      fontWeight: 500,
      lineHeight: 1.4,
      textTransform: 'uppercase' as const,
      letterSpacing: '0.05em',
    },
    
    // Small text (legends, footnotes)
    small: {
      fontSize: '0.875rem',    // 14px
      fontWeight: 400,
      lineHeight: 1.4,
    },
  },
  
  // Spacing system (8px base)
  spacing: {
    xs: '0.5rem',    // 8px
    sm: '1rem',      // 16px
    md: '1.5rem',    // 24px
    lg: '2rem',      // 32px
    xl: '3rem',      // 48px
    '2xl': '4rem',   // 64px
    '3xl': '6rem',   // 96px
  },
  
  // Slide dimensions and layout
  layout: {
    slideWidth: '100vw',
    slideHeight: '100vh',
    contentMaxWidth: '1400px',
    
    // Safe areas for text (avoid screen edges)
    padding: {
      horizontal: '5vw',
      vertical: '8vh',
    },
    
    // Grid system
    columns: 12,
    gap: '2rem',
  },
  
  // Animation timings
  animation: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
    slide: '600ms',
    
    // Easing functions
    easing: {
      standard: 'cubic-bezier(0.4, 0.0, 0.2, 1)',
      decelerate: 'cubic-bezier(0.0, 0.0, 0.2, 1)',
      accelerate: 'cubic-bezier(0.4, 0.0, 1, 1)',
      spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
    },
  },
  
  // Chart configuration
  charts: {
    // Default dimensions
    height: {
      small: '300px',
      medium: '400px',
      large: '500px',
      full: '60vh',
    },
    
    // Margins
    margin: {
      top: 20,
      right: 40,
      bottom: 60,
      left: 80,
    },
    
    // Grid and axis styling
    grid: {
      strokeDasharray: '4 4',
      stroke: '#374151',
      strokeOpacity: 0.3,
    },
    
    axis: {
      stroke: '#6B7280',
      fontSize: '14px',
      fontWeight: 500,
    },
    
    // Tooltip styling
    tooltip: {
      background: '#1A1A1A',
      border: '1px solid #374151',
      borderRadius: '8px',
      padding: '12px',
      fontSize: '14px',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
    },
    
    // Legend
    legend: {
      fontSize: '14px',
      spacing: 20,
      iconSize: 12,
    },
  },
  
  // Shadow system
  shadows: {
    sm: '0 1px 3px rgba(0, 0, 0, 0.5)',
    md: '0 4px 12px rgba(0, 0, 0, 0.5)',
    lg: '0 8px 24px rgba(0, 0, 0, 0.6)',
    xl: '0 12px 40px rgba(0, 0, 0, 0.7)',
  },
  
  // Border radius
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },
};

export type PresentationTheme = typeof presentationTheme;

/**
 * Client-friendly language mappings
 * Replaces technical terms with advisor-appropriate language
 */
export const clientLanguage = {
  // Simulation terms
  'Monte Carlo': 'Portfolio Projection',
  'Scenarios': 'Possible Outcomes',
  'Iterations': 'Simulations',
  'Median': 'Typical Outcome',
  'Percentile': 'Confidence Level',
  
  // Risk terms
  'Volatility': 'Market Fluctuation',
  'Standard Deviation': 'Expected Range',
  'Drawdown': 'Decline from Peak',
  'Sharpe Ratio': 'Risk-Adjusted Return',
  
  // Portfolio terms
  'Asset Allocation': 'Investment Mix',
  'Equity': 'Stocks',
  'Fixed Income': 'Bonds',
  'Rebalancing': 'Portfolio Adjustments',
  
  // Planning terms
  'Depletion': 'Portfolio Exhaustion',
  'Success Rate': 'Confidence Level',
  'Horizon': 'Planning Period',
  'Withdrawal Rate': 'Spending Strategy',
};

/**
 * Speaker notes templates for each slide type
 */
export const speakerNotes = {
  overview: [
    'Welcome and introduction',
    'Review client goals and timeline',
    'Overview of analysis approach',
  ],
  
  planSummary: [
    'Starting portfolio and contributions',
    'Monthly spending and income',
    'Key planning assumptions',
  ],
  
  monteCarlo: [
    'Explain projection methodology',
    'Highlight median outcome (typical case)',
    'Discuss range of possibilities',
    'Address success probability',
  ],
  
  stressTests: [
    'Review historical market scenarios',
    'Discuss portfolio resilience',
    'Identify vulnerabilities',
  ],
  
  assetAllocation: [
    'Current investment mix',
    'Rationale for allocation',
    'Expected returns and risks',
    'Diversification benefits',
  ],
  
  cashFlows: [
    'Income sources over time',
    'Planned withdrawals',
    'Social Security / pension timing',
    'Tax considerations',
  ],
  
  keyRisks: [
    'Primary planning risks',
    'Mitigation strategies',
    'Monitoring approach',
  ],
  
  nextSteps: [
    'Action items',
    'Follow-up schedule',
    'Questions and discussion',
  ],
};
