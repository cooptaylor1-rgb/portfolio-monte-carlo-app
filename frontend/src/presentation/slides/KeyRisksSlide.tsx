/**
 * Key Risks Slide - Risk analysis and considerations
 */

import React from 'react';
import { presentationTheme } from '../presentationTheme';
import { AlertTriangle, TrendingDown, Clock, DollarSign } from 'lucide-react';

interface KeyRisksSlideProps {
  clientInfo: any;
  simulationResults: any;
  complianceMode: boolean;
}

const KeyRisksSlide: React.FC<KeyRisksSlideProps> = ({ 
  simulationResults,
  complianceMode 
}) => {
  const metrics = simulationResults?.metrics || {};
  const inputs = simulationResults?.inputs || {};
  
  const depletionProb = (metrics.depletion_probability || 0) * 100;
  const shortfallRisk = (metrics.shortfall_risk || 0) * 100;
  const successProb = (metrics.success_probability || 0) * 100;
  const equityPct = (inputs.equity_pct || 0) * 100;
  const equityVol = (inputs.equity_vol_annual || 0) * 100;
  const yearsToModel = inputs.years_to_model || 30;
  const monthlySpending = Math.abs(inputs.monthly_spending || 0);
  const inflationRate = (inputs.inflation_annual || 0) * 100;

  // Calculate risk level
  const getRiskLevel = () => {
    if (successProb >= 85) return { level: 'Low', color: presentationTheme.colors.chart.success };
    if (successProb >= 70) return { level: 'Moderate', color: presentationTheme.colors.chart.warning };
    return { level: 'High', color: presentationTheme.colors.chart.danger };
  };
  
  const riskLevel = getRiskLevel();

  // Generate risk factors
  const riskFactors = [
    {
      icon: TrendingDown,
      title: 'Market Volatility Risk',
      description: `Portfolio has ${equityPct.toFixed(0)}% equity allocation with ${equityVol.toFixed(0)}% annual volatility`,
      severity: equityPct > 80 ? 'high' : equityPct > 60 ? 'moderate' : 'low',
    },
    {
      icon: Clock,
      title: 'Longevity Risk',
      description: `Planning horizon of ${yearsToModel} years may need extension if longevity exceeds expectations`,
      severity: yearsToModel < 25 ? 'high' : yearsToModel < 35 ? 'moderate' : 'low',
    },
    {
      icon: DollarSign,
      title: 'Inflation Risk',
      description: `${inflationRate.toFixed(1)}% annual inflation will significantly impact purchasing power over time`,
      severity: inflationRate > 4 ? 'high' : inflationRate > 2.5 ? 'moderate' : 'low',
    },
    {
      icon: AlertTriangle,
      title: 'Sequence of Returns Risk',
      description: `Poor early returns could impact plan success, especially with high withdrawal rates`,
      severity: depletionProb > 30 ? 'high' : depletionProb > 15 ? 'moderate' : 'low',
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return presentationTheme.colors.chart.danger;
      case 'moderate': return presentationTheme.colors.chart.warning;
      default: return presentationTheme.colors.chart.success;
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Key Considerations</h1>
      
      {/* Overall Risk Assessment */}
      <div style={styles.riskSummary}>
        <div style={styles.riskCard}>
          <div style={styles.riskLabel}>Overall Plan Risk</div>
          <div style={{ ...styles.riskValue, color: riskLevel.color }}>
            {riskLevel.level}
          </div>
          <div style={styles.riskMetrics}>
            <div style={styles.miniMetric}>
              <span>Success Rate:</span>
              <span style={{ color: riskLevel.color }}>{successProb.toFixed(0)}%</span>
            </div>
            <div style={styles.miniMetric}>
              <span>Depletion Risk:</span>
              <span style={{ color: getSeverityColor(depletionProb > 30 ? 'high' : depletionProb > 15 ? 'moderate' : 'low') }}>
                {depletionProb.toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Factors Grid */}
      <div style={styles.riskGrid}>
        {riskFactors.map((risk, index) => (
          <div key={index} style={styles.riskFactorCard}>
            <div style={styles.riskHeader}>
              <risk.icon 
                size={28} 
                color={getSeverityColor(risk.severity)} 
              />
              <div style={styles.severityBadge} data-severity={risk.severity}>
                {risk.severity.toUpperCase()}
              </div>
            </div>
            <h3 style={styles.riskTitle}>{risk.title}</h3>
            <p style={styles.riskDescription}>{risk.description}</p>
          </div>
        ))}
      </div>

      {!complianceMode && (
        <div style={styles.disclaimer}>
          Note: Risk assessments are based on historical data and assumptions. Actual results may vary.
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: '100%',
    height: '100%',
    padding: '4vh 5vw',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'auto',
  },
  title: {
    ...presentationTheme.typography.slideTitle,
    color: presentationTheme.colors.gold,
    marginBottom: '2rem',
  },
  riskSummary: {
    marginBottom: '2rem',
  },
  riskCard: {
    backgroundColor: presentationTheme.colors.background.secondary,
    border: `2px solid ${presentationTheme.colors.border}`,
    borderRadius: presentationTheme.borderRadius.lg,
    padding: '2rem',
    textAlign: 'center',
    maxWidth: '500px',
    margin: '0 auto',
  },
  riskLabel: {
    ...presentationTheme.typography.label,
    color: presentationTheme.colors.text.muted,
    marginBottom: '0.5rem',
  },
  riskValue: {
    ...presentationTheme.typography.slideTitle,
    fontSize: '48px',
    fontWeight: 700,
    marginBottom: '1.5rem',
  },
  riskMetrics: {
    display: 'flex',
    justifyContent: 'space-around',
    gap: '2rem',
    paddingTop: '1rem',
    borderTop: `1px solid ${presentationTheme.colors.divider}`,
  },
  miniMetric: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
    ...presentationTheme.typography.body,
  },
  riskGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '1.5rem',
    flex: 1,
  },
  riskFactorCard: {
    backgroundColor: presentationTheme.colors.background.secondary,
    border: `1px solid ${presentationTheme.colors.border}`,
    borderRadius: presentationTheme.borderRadius.md,
    padding: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  riskHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  severityBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 700,
    letterSpacing: '0.5px',
  },
  riskTitle: {
    ...presentationTheme.typography.subheading,
    color: presentationTheme.colors.text.primary,
    margin: 0,
  },
  riskDescription: {
    ...presentationTheme.typography.body,
    color: presentationTheme.colors.text.secondary,
    margin: 0,
    lineHeight: 1.5,
  },
  disclaimer: {
    ...presentationTheme.typography.small,
    color: presentationTheme.colors.text.muted,
    textAlign: 'center',
    marginTop: '2rem',
    fontStyle: 'italic',
  },
};

// Add dynamic styles for severity badges using CSS-in-JS workaround
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  [data-severity="high"] {
    background-color: ${presentationTheme.colors.chart.danger}33;
    color: ${presentationTheme.colors.chart.danger};
  }
  [data-severity="moderate"] {
    background-color: ${presentationTheme.colors.chart.warning}33;
    color: ${presentationTheme.colors.chart.warning};
  }
  [data-severity="low"] {
    background-color: ${presentationTheme.colors.chart.success}33;
    color: ${presentationTheme.colors.chart.success};
  }
`;
document.head.appendChild(styleSheet);

export default KeyRisksSlide;