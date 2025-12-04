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
  clientInfo, 
  simulationResults 
}) => {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Plan Summary</h1>
      <div style={styles.grid}>
        <div style={styles.card}>
          <div style={styles.label}>Starting Portfolio</div>
          <div style={styles.value}>$4,500,000</div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Monthly Spending</div>
          <div style={styles.value}>$20,000</div>
        </div>
        <div style={styles.card}>
          <div style={styles.label}>Planning Horizon</div>
          <div style={styles.value}>30 Years</div>
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
};

export default PlanSummarySlide;
