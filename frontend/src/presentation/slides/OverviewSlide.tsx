/**
 * Overview Slide - Opening slide for presentation
 * 
 * Displays:
 * - Client name and meeting date
 * - Planning period and key milestones
 * - Meeting agenda overview
 */

import React from 'react';
import { presentationTheme } from '../presentationTheme';
import { Calendar, Target, TrendingUp } from 'lucide-react';

interface OverviewSlideProps {
  clientInfo: any;
  simulationResults: any;
  complianceMode: boolean;
}

const OverviewSlide: React.FC<OverviewSlideProps> = ({ 
  clientInfo, 
  simulationResults,
  complianceMode 
}) => {
  const currentDate = clientInfo?.report_date 
    ? new Date(clientInfo.report_date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
  
  const planningYears = simulationResults?.inputs?.years_to_model || 30;
  const currentAge = simulationResults?.inputs?.current_age || 48;
  const horizonAge = simulationResults?.inputs?.horizon_age || 78;
  const successProb = simulationResults?.metrics?.success_probability || 0;
  
  return (
    <div style={styles.container}>
      {/* Top section - Client name */}
      <div style={styles.header}>
        <div style={styles.clientNameLarge}>
          {clientInfo?.client_name || 'Client Portfolio Analysis'}
        </div>
        <div style={styles.subtitle}>
          Portfolio Analysis & Financial Plan Review
        </div>
        <div style={styles.date}>{currentDate}</div>
      </div>
      
      {/* Middle section - Key highlights */}
      <div style={styles.highlights}>
        <div style={styles.highlightCard}>
          <Calendar size={32} color={presentationTheme.colors.gold} />
          <div style={styles.highlightLabel}>Planning Period</div>
          <div style={styles.highlightValue}>{planningYears} Years (Age {currentAge}-{horizonAge})</div>
        </div>
        
        <div style={styles.highlightCard}>
          <Target size={32} color={presentationTheme.colors.gold} />
          <div style={styles.highlightLabel}>Success Probability</div>
          <div style={styles.highlightValue}>{(successProb * 100).toFixed(0)}%</div>
        </div>
        
        <div style={styles.highlightCard}>
          <TrendingUp size={32} color={presentationTheme.colors.gold} />
          <div style={styles.highlightLabel}>Analysis Type</div>
          <div style={styles.highlightValue}>Monte Carlo Simulation</div>
        </div>
      </div>
      
      {/* Bottom section - Agenda */}
      <div style={styles.agenda}>
        <h3 style={styles.agendaTitle}>Today's Discussion</h3>
        <div style={styles.agendaGrid}>
          <div style={styles.agendaItem}>1. Current Plan Summary</div>
          <div style={styles.agendaItem}>2. Portfolio Projections</div>
          <div style={styles.agendaItem}>3. Stress Test Results</div>
          <div style={styles.agendaItem}>4. Asset Allocation Review</div>
          <div style={styles.agendaItem}>5. Cash Flow Analysis</div>
          <div style={styles.agendaItem}>6. Key Considerations</div>
          <div style={styles.agendaItem}>7. Next Steps</div>
        </div>
      </div>
      
      {/* Footer */}
      <div style={styles.footer}>
        Salem Investment Counselors | Confidential Client Presentation
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    padding: presentationTheme.layout.padding.vertical + ' ' + presentationTheme.layout.padding.horizontal,
    maxWidth: presentationTheme.layout.contentMaxWidth,
    margin: '0 auto',
  },
  
  header: {
    textAlign: 'center',
    marginBottom: presentationTheme.spacing['2xl'],
  },
  
  clientNameLarge: {
    ...presentationTheme.typography.slideTitle,
    color: presentationTheme.colors.gold,
    marginBottom: presentationTheme.spacing.lg,
  },
  
  subtitle: {
    ...presentationTheme.typography.heading,
    color: presentationTheme.colors.text.secondary,
    marginBottom: presentationTheme.spacing.sm,
  },
  
  date: {
    ...presentationTheme.typography.body,
    color: presentationTheme.colors.text.muted,
  },
  
  highlights: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: presentationTheme.spacing.xl,
    margin: `${presentationTheme.spacing['2xl']} 0`,
  },
  
  highlightCard: {
    backgroundColor: presentationTheme.colors.background.secondary,
    border: `2px solid ${presentationTheme.colors.border}`,
    borderRadius: presentationTheme.borderRadius.lg,
    padding: presentationTheme.spacing.xl,
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: presentationTheme.spacing.md,
  },
  
  highlightLabel: {
    ...presentationTheme.typography.label,
    color: presentationTheme.colors.text.muted,
  },
  
  highlightValue: {
    ...presentationTheme.typography.subheading,
    color: presentationTheme.colors.text.primary,
    fontWeight: 600,
  },
  
  agenda: {
    marginTop: presentationTheme.spacing['2xl'],
  },
  
  agendaTitle: {
    ...presentationTheme.typography.heading,
    marginBottom: presentationTheme.spacing.lg,
    textAlign: 'center',
  },
  
  agendaGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: presentationTheme.spacing.md,
  },
  
  agendaItem: {
    ...presentationTheme.typography.body,
    padding: presentationTheme.spacing.md,
    backgroundColor: presentationTheme.colors.background.secondary,
    borderLeft: `4px solid ${presentationTheme.colors.gold}`,
    borderRadius: presentationTheme.borderRadius.sm,
  },
  
  footer: {
    ...presentationTheme.typography.small,
    textAlign: 'center',
    color: presentationTheme.colors.text.muted,
    paddingTop: presentationTheme.spacing.xl,
    borderTop: `1px solid ${presentationTheme.colors.divider}`,
    marginTop: 'auto',
  },
};

export default OverviewSlide;
