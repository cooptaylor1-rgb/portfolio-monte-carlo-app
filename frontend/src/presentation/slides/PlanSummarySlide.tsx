/**
 * Plan Summary Slide - Current plan overview
 */

import React from 'react';
import { presentationTheme } from '../presentationTheme';

interface PlanSummarySlideProps {
  clientInfo: any;
  simulationResults: any;
  complianceMode: boolean;
}

const PlanSummarySlide: React.FC<PlanSummarySlideProps> = ({ 
  simulationResults 
}) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(Math.abs(value));
  };
  
  const startingPortfolio = simulationResults?.inputs?.starting_portfolio || 0;
  const monthlySpending = Math.abs(simulationResults?.inputs?.monthly_spending || 0);
  const monthlyIncome = simulationResults?.inputs?.monthly_income || 0;
  const planningYears = simulationResults?.inputs?.years_to_model || 0;
  const equityPct = (simulationResults?.inputs?.equity_pct || 0) * 100;
  const fiPct = (simulationResults?.inputs?.fi_pct || 0) * 100;
  const cashPct = (simulationResults?.inputs?.cash_pct || 0) * 100;
  
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Plan Summary</h1>
      <div style={styles.grid}>
        <div style={styles.card}>
          <div style={styles.label}>Starting Portfolio</div>
          <div style={styles.value}>{formatCurrency(startingPortfolio)}</div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Monthly Net Cash Flow</div>
          <div style={styles.value}>
            {monthlyIncome > 0 ? '+' : ''}{formatCurrency(monthlyIncome)}
            {' / '}
            -{formatCurrency(monthlySpending)}
          </div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Planning Horizon</div>
          <div style={styles.value}>{planningYears} Years</div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Asset Allocation</div>
          <div style={styles.value}>
            {equityPct.toFixed(0)}% / {fiPct.toFixed(0)}% / {cashPct.toFixed(0)}%
          </div>
          <div style={styles.subLabel}>Equity / Fixed Income / Cash</div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Annual Inflation</div>
          <div style={styles.value}>
            {((simulationResults?.inputs?.inflation_annual || 0) * 100).toFixed(1)}%
          </div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Tax Rate</div>
          <div style={styles.value}>
            {((simulationResults?.inputs?.tax_rate || 0) * 100).toFixed(0)}%
          </div>
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: '100%',
    height: '100%',
    padding: '5vh 5vw',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  title: {
    ...presentationTheme.typography.slideTitle,
    color: presentationTheme.colors.gold,
    marginBottom: '3rem',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '2rem',
  },
  card: {
    backgroundColor: presentationTheme.colors.background.secondary,
    padding: '2rem',
    borderRadius: '12px',
    textAlign: 'center',
  },
  label: {
    ...presentationTheme.typography.label,
    color: presentationTheme.colors.text.muted,
    marginBottom: '1rem',
  },
  value: {
    ...presentationTheme.typography.metric,
    color: presentationTheme.colors.text.primary,
  },
  subLabel: {
    ...presentationTheme.typography.small,
    color: presentationTheme.colors.text.muted,
    marginTop: '0.5rem',
  },
};

export default PlanSummarySlide;
