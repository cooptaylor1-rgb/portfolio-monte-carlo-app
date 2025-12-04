/**
 * Cash Flows Slide - Income and spending breakdown
 */

import React from 'react';
import { presentationTheme } from '../presentationTheme';
import { ArrowDownCircle, ArrowUpCircle, DollarSign } from 'lucide-react';

interface CashFlowsSlideProps {
  clientInfo: any;
  simulationResults: any;
  complianceMode: boolean;
}

const CashFlowsSlide: React.FC<CashFlowsSlideProps> = ({ 
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

  const inputs = simulationResults?.inputs || {};
  
  // Income sources
  const monthlyIncome = inputs.monthly_income || 0;
  const socialSecurity = inputs.social_security_monthly || 0;
  const pension = inputs.pension_monthly || 0;
  const otherIncome = inputs.other_income_monthly || 0;
  const totalMonthlyIncome = monthlyIncome + socialSecurity + pension + otherIncome;
  
  // Spending
  const monthlySpending = Math.abs(inputs.monthly_spending || 0);
  const healthcare = inputs.healthcare_monthly || 0;
  const totalMonthlySpending = monthlySpending + healthcare;
  
  // Net cash flow
  const netMonthlyCashFlow = totalMonthlyIncome - totalMonthlySpending;
  const netAnnualCashFlow = netMonthlyCashFlow * 12;
  
  // One-time events
  const oneTimeCF = inputs.one_time_cf || 0;
  const oneTimeCFMonth = inputs.one_time_cf_month || 0;
  
  const currentAge = inputs.current_age || 0;
  const ssStartAge = inputs.ss_start_age || 67;
  const pensionStartAge = inputs.pension_start_age || 65;
  const healthcareStartAge = inputs.healthcare_start_age || 65;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Cash Flow Analysis</h1>
      
      <div style={styles.content}>
        {/* Summary Cards */}
        <div style={styles.summaryRow}>
          <div style={styles.summaryCard}>
            <ArrowUpCircle size={32} color={presentationTheme.colors.chart.success} />
            <div style={styles.summaryLabel}>Total Monthly Income</div>
            <div style={{ ...styles.summaryValue, color: presentationTheme.colors.chart.success }}>
              {formatCurrency(totalMonthlyIncome)}
            </div>
          </div>
          
          <div style={styles.summaryCard}>
            <ArrowDownCircle size={32} color={presentationTheme.colors.chart.danger} />
            <div style={styles.summaryLabel}>Total Monthly Spending</div>
            <div style={{ ...styles.summaryValue, color: presentationTheme.colors.chart.danger }}>
              {formatCurrency(totalMonthlySpending)}
            </div>
          </div>
          
          <div style={styles.summaryCard}>
            <DollarSign size={32} color={netMonthlyCashFlow >= 0 ? presentationTheme.colors.chart.success : presentationTheme.colors.chart.warning} />
            <div style={styles.summaryLabel}>Net Monthly Cash Flow</div>
            <div style={{
              ...styles.summaryValue,
              color: netMonthlyCashFlow >= 0 ? presentationTheme.colors.chart.success : presentationTheme.colors.chart.warning
            }}>
              {netMonthlyCashFlow >= 0 ? '+' : '-'}{formatCurrency(netMonthlyCashFlow)}
            </div>
          </div>
        </div>

        {/* Details Grid */}
        <div style={styles.detailsGrid}>
          {/* Income Details */}
          <div style={styles.detailsCard}>
            <h3 style={styles.cardTitle}>Income Sources</h3>
            <div style={styles.itemList}>
              {monthlyIncome > 0 && (
                <div style={styles.item}>
                  <span style={styles.itemLabel}>Regular Income</span>
                  <span style={styles.itemValue}>{formatCurrency(monthlyIncome)}/mo</span>
                </div>
              )}
              {socialSecurity > 0 && (
                <div style={styles.item}>
                  <span style={styles.itemLabel}>Social Security (starts age {ssStartAge})</span>
                  <span style={styles.itemValue}>{formatCurrency(socialSecurity)}/mo</span>
                </div>
              )}
              {pension > 0 && (
                <div style={styles.item}>
                  <span style={styles.itemLabel}>Pension (starts age {pensionStartAge})</span>
                  <span style={styles.itemValue}>{formatCurrency(pension)}/mo</span>
                </div>
              )}
              {otherIncome > 0 && (
                <div style={styles.item}>
                  <span style={styles.itemLabel}>Other Income</span>
                  <span style={styles.itemValue}>{formatCurrency(otherIncome)}/mo</span>
                </div>
              )}
              {totalMonthlyIncome === 0 && (
                <div style={styles.emptyState}>No regular income sources configured</div>
              )}
              <div style={{ ...styles.item, ...styles.totalRow }}>
                <span style={styles.itemLabel}>Annual Total</span>
                <span style={styles.itemValue}>{formatCurrency(totalMonthlyIncome * 12)}/yr</span>
              </div>
            </div>
          </div>

          {/* Spending Details */}
          <div style={styles.detailsCard}>
            <h3 style={styles.cardTitle}>Spending</h3>
            <div style={styles.itemList}>
              <div style={styles.item}>
                <span style={styles.itemLabel}>Base Monthly Spending</span>
                <span style={styles.itemValue}>{formatCurrency(monthlySpending)}/mo</span>
              </div>
              {healthcare > 0 && (
                <div style={styles.item}>
                  <span style={styles.itemLabel}>Healthcare (starts age {healthcareStartAge})</span>
                  <span style={styles.itemValue}>{formatCurrency(healthcare)}/mo</span>
                </div>
              )}
              <div style={styles.item}>
                <span style={styles.itemLabel}>Annual Inflation</span>
                <span style={styles.itemValue}>{((inputs.inflation_annual || 0) * 100).toFixed(1)}%</span>
              </div>
              <div style={{ ...styles.item, ...styles.totalRow }}>
                <span style={styles.itemLabel}>Annual Total (Current)</span>
                <span style={styles.itemValue}>{formatCurrency(totalMonthlySpending * 12)}/yr</span>
              </div>
            </div>
          </div>
        </div>

        {/* One-time Events */}
        {oneTimeCF !== 0 && (
          <div style={styles.oneTimeCard}>
            <h3 style={styles.cardTitle}>One-Time Cash Flow Event</h3>
            <div style={styles.oneTimeContent}>
              <span style={styles.oneTimeLabel}>
                {oneTimeCF > 0 ? 'Inflow' : 'Outflow'} at month {oneTimeCFMonth} (Age {currentAge + Math.floor(oneTimeCFMonth / 12)})
              </span>
              <span style={{
                ...styles.oneTimeValue,
                color: oneTimeCF > 0 ? presentationTheme.colors.chart.success : presentationTheme.colors.chart.danger
              }}>
                {oneTimeCF > 0 ? '+' : '-'}{formatCurrency(oneTimeCF)}
              </span>
            </div>
          </div>
        )}
      </div>
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
  content: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2rem',
  },
  summaryRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '1.5rem',
  },
  summaryCard: {
    backgroundColor: presentationTheme.colors.background.secondary,
    border: `1px solid ${presentationTheme.colors.border}`,
    borderRadius: presentationTheme.borderRadius.md,
    padding: '1.5rem',
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '0.75rem',
  },
  summaryLabel: {
    ...presentationTheme.typography.label,
    color: presentationTheme.colors.text.muted,
  },
  summaryValue: {
    ...presentationTheme.typography.heading,
    fontWeight: 700,
  },
  detailsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '2rem',
  },
  detailsCard: {
    backgroundColor: presentationTheme.colors.background.secondary,
    border: `1px solid ${presentationTheme.colors.border}`,
    borderRadius: presentationTheme.borderRadius.md,
    padding: '1.5rem',
  },
  cardTitle: {
    ...presentationTheme.typography.subheading,
    color: presentationTheme.colors.gold,
    marginBottom: '1rem',
    paddingBottom: '0.75rem',
    borderBottom: `1px solid ${presentationTheme.colors.divider}`,
  },
  itemList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  item: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '0.5rem 0',
  },
  itemLabel: {
    ...presentationTheme.typography.body,
    color: presentationTheme.colors.text.secondary,
  },
  itemValue: {
    ...presentationTheme.typography.body,
    color: presentationTheme.colors.text.primary,
    fontWeight: 600,
  },
  totalRow: {
    borderTop: `2px solid ${presentationTheme.colors.divider}`,
    marginTop: '0.5rem',
    paddingTop: '1rem',
    fontWeight: 700,
  },
  emptyState: {
    ...presentationTheme.typography.body,
    color: presentationTheme.colors.text.muted,
    fontStyle: 'italic',
    textAlign: 'center',
    padding: '1rem',
  },
  oneTimeCard: {
    backgroundColor: presentationTheme.colors.background.secondary,
    border: `2px solid ${presentationTheme.colors.gold}`,
    borderRadius: presentationTheme.borderRadius.md,
    padding: '1.5rem',
  },
  oneTimeContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  oneTimeLabel: {
    ...presentationTheme.typography.body,
    color: presentationTheme.colors.text.secondary,
  },
  oneTimeValue: {
    ...presentationTheme.typography.heading,
    fontWeight: 700,
  },
};

export default CashFlowsSlide;