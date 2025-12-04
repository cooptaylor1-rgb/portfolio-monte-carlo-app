/**
 * Asset Allocation Slide - Investment mix breakdown
 */

import React from 'react';
import { presentationTheme } from '../presentationTheme';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface AssetAllocationSlideProps {
  clientInfo: any;
  simulationResults: any;
  complianceMode: boolean;
}

const AssetAllocationSlide: React.FC<AssetAllocationSlideProps> = ({ 
  simulationResults 
}) => {
  const equityPct = (simulationResults?.inputs?.equity_pct || 0) * 100;
  const fiPct = (simulationResults?.inputs?.fi_pct || 0) * 100;
  const cashPct = (simulationResults?.inputs?.cash_pct || 0) * 100;
  const startingPortfolio = simulationResults?.inputs?.starting_portfolio || 0;

  const allocationData = [
    { name: 'Equities', value: equityPct, amount: startingPortfolio * (equityPct / 100) },
    { name: 'Fixed Income', value: fiPct, amount: startingPortfolio * (fiPct / 100) },
    { name: 'Cash', value: cashPct, amount: startingPortfolio * (cashPct / 100) },
  ];

  const COLORS = [
    presentationTheme.colors.chart.line1,
    presentationTheme.colors.chart.line2,
    presentationTheme.colors.chart.line3,
  ];

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const equityReturn = ((simulationResults?.inputs?.equity_return_annual || 0) * 100).toFixed(1);
  const fiReturn = ((simulationResults?.inputs?.fi_return_annual || 0) * 100).toFixed(1);
  const cashReturn = ((simulationResults?.inputs?.cash_return_annual || 0) * 100).toFixed(1);
  
  const equityVol = ((simulationResults?.inputs?.equity_vol_annual || 0) * 100).toFixed(1);
  const fiVol = ((simulationResults?.inputs?.fi_vol_annual || 0) * 100).toFixed(1);

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Asset Allocation</h1>
      
      <div style={styles.content}>
        {/* Pie Chart */}
        <div style={styles.chartSection}>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={allocationData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value.toFixed(0)}%`}
                outerRadius={140}
                fill="#8884d8"
                dataKey="value"
              >
                {allocationData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: number) => `${value.toFixed(1)}%`}
                contentStyle={{
                  backgroundColor: presentationTheme.colors.background.secondary,
                  border: `1px solid ${presentationTheme.colors.border}`,
                  borderRadius: '8px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Details Table */}
        <div style={styles.detailsSection}>
          <div style={styles.allocationCard}>
            <div style={styles.assetHeader}>
              <div style={{ ...styles.colorDot, backgroundColor: COLORS[0] }} />
              <div style={styles.assetName}>Equities</div>
            </div>
            <div style={styles.assetStats}>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Allocation:</span>
                <span style={styles.statValue}>{equityPct.toFixed(0)}%</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Amount:</span>
                <span style={styles.statValue}>{formatCurrency(allocationData[0].amount)}</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Expected Return:</span>
                <span style={styles.statValue}>{equityReturn}%</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Volatility:</span>
                <span style={styles.statValue}>{equityVol}%</span>
              </div>
            </div>
          </div>

          <div style={styles.allocationCard}>
            <div style={styles.assetHeader}>
              <div style={{ ...styles.colorDot, backgroundColor: COLORS[1] }} />
              <div style={styles.assetName}>Fixed Income</div>
            </div>
            <div style={styles.assetStats}>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Allocation:</span>
                <span style={styles.statValue}>{fiPct.toFixed(0)}%</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Amount:</span>
                <span style={styles.statValue}>{formatCurrency(allocationData[1].amount)}</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Expected Return:</span>
                <span style={styles.statValue}>{fiReturn}%</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Volatility:</span>
                <span style={styles.statValue}>{fiVol}%</span>
              </div>
            </div>
          </div>

          <div style={styles.allocationCard}>
            <div style={styles.assetHeader}>
              <div style={{ ...styles.colorDot, backgroundColor: COLORS[2] }} />
              <div style={styles.assetName}>Cash</div>
            </div>
            <div style={styles.assetStats}>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Allocation:</span>
                <span style={styles.statValue}>{cashPct.toFixed(0)}%</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Amount:</span>
                <span style={styles.statValue}>{formatCurrency(allocationData[2].amount)}</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Expected Return:</span>
                <span style={styles.statValue}>{cashReturn}%</span>
              </div>
              <div style={styles.statRow}>
                <span style={styles.statLabel}>Volatility:</span>
                <span style={styles.statValue}>Low</span>
              </div>
            </div>
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
    padding: '4vh 5vw',
    display: 'flex',
    flexDirection: 'column',
  },
  title: {
    ...presentationTheme.typography.slideTitle,
    color: presentationTheme.colors.gold,
    marginBottom: '2rem',
  },
  content: {
    display: 'flex',
    gap: '3rem',
    flex: 1,
  },
  chartSection: {
    flex: '0 0 45%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  detailsSection: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  allocationCard: {
    backgroundColor: presentationTheme.colors.background.secondary,
    border: `1px solid ${presentationTheme.colors.border}`,
    borderRadius: presentationTheme.borderRadius.md,
    padding: '1.5rem',
  },
  assetHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    marginBottom: '1rem',
    paddingBottom: '1rem',
    borderBottom: `1px solid ${presentationTheme.colors.divider}`,
  },
  colorDot: {
    width: '16px',
    height: '16px',
    borderRadius: '50%',
  },
  assetName: {
    ...presentationTheme.typography.subheading,
    fontWeight: 600,
    color: presentationTheme.colors.text.primary,
  },
  assetStats: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  statRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statLabel: {
    ...presentationTheme.typography.body,
    color: presentationTheme.colors.text.muted,
  },
  statValue: {
    ...presentationTheme.typography.body,
    color: presentationTheme.colors.text.primary,
    fontWeight: 600,
  },
};

export default AssetAllocationSlide;