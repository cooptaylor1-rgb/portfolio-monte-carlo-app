/**
 * Monte Carlo Slide - Portfolio projection visualization
 */

import React from 'react';
import { presentationTheme } from '../presentationTheme';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from 'recharts';

interface MonteCarloSlideProps {
  clientInfo: any;
  simulationResults: any;
  complianceMode: boolean;
}

const MonteCarloSlide: React.FC<MonteCarloSlideProps> = ({ 
  simulationResults, 
  complianceMode 
}) => {
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  // Transform monthly stats to yearly data for better readability
  const chartData = React.useMemo(() => {
    if (!simulationResults?.stats) return [];
    
    // Get every 12th month (yearly data)
    return simulationResults.stats
      .filter((_: any, idx: number) => idx % 12 === 0)
      .map((stat: any) => ({
        year: Math.floor(stat.Month / 12),
        median: stat.Median,
        p10: stat.P10,
        p90: stat.P90,
        p25: stat.P25,
        p75: stat.P75,
      }));
  }, [simulationResults]);

  const metrics = simulationResults?.metrics;
  const successProb = (metrics?.success_probability || 0) * 100;
  const endingMedian = metrics?.ending_median || 0;
  const depletionProb = (metrics?.depletion_probability || 0) * 100;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Portfolio Projection</h1>
      
      {/* Key Metrics Row */}
      <div style={styles.metricsRow}>
        <div style={styles.metricCard}>
          <div style={styles.metricLabel}>Success Probability</div>
          <div style={{
            ...styles.metricValue,
            color: successProb >= 85 ? presentationTheme.colors.chart.success : 
                   successProb >= 70 ? presentationTheme.colors.chart.warning :
                   presentationTheme.colors.chart.danger
          }}>
            {successProb.toFixed(0)}%
          </div>
        </div>
        
        <div style={styles.metricCard}>
          <div style={styles.metricLabel}>Median Ending Balance</div>
          <div style={styles.metricValue}>
            {formatCurrency(endingMedian)}
          </div>
        </div>
        
        <div style={styles.metricCard}>
          <div style={styles.metricLabel}>Depletion Risk</div>
          <div style={{
            ...styles.metricValue,
            color: depletionProb <= 15 ? presentationTheme.colors.chart.success :
                   depletionProb <= 30 ? presentationTheme.colors.chart.warning :
                   presentationTheme.colors.chart.danger
          }}>
            {depletionProb.toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Chart */}
      <div style={styles.chartContainer}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke={presentationTheme.colors.chart.grid}
              opacity={0.3}
            />
            <XAxis 
              dataKey="year" 
              stroke={presentationTheme.colors.text.secondary}
              style={{ fontSize: '14px' }}
              label={{ value: 'Years', position: 'insideBottom', offset: -10, fill: presentationTheme.colors.text.secondary }}
            />
            <YAxis 
              stroke={presentationTheme.colors.text.secondary}
              style={{ fontSize: '14px' }}
              tickFormatter={formatCurrency}
              label={{ value: 'Portfolio Value', angle: -90, position: 'insideLeft', fill: presentationTheme.colors.text.secondary }}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: presentationTheme.colors.background.secondary,
                border: `1px solid ${presentationTheme.colors.border}`,
                borderRadius: '8px',
                color: presentationTheme.colors.text.primary,
              }}
              formatter={(value: number) => formatCurrency(value)}
              labelFormatter={(label) => `Year ${label}`}
            />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="line"
            />
            
            {/* 10th-90th percentile range */}
            <Area
              type="monotone"
              dataKey="p90"
              fill={presentationTheme.colors.chart.percentile90}
              fillOpacity={0.15}
              stroke="none"
              name="90th Percentile"
            />
            <Area
              type="monotone"
              dataKey="p10"
              fill={presentationTheme.colors.background.primary}
              fillOpacity={1}
              stroke="none"
              name="10th Percentile"
            />
            
            {/* Median line - prominent */}
            <Line
              type="monotone"
              dataKey="median"
              stroke={presentationTheme.colors.gold}
              strokeWidth={4}
              dot={false}
              name="Median (50th)"
            />
            
            {/* P10 and P90 boundary lines */}
            <Line
              type="monotone"
              dataKey="p10"
              stroke={presentationTheme.colors.chart.danger}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="10th Percentile"
            />
            <Line
              type="monotone"
              dataKey="p90"
              stroke={presentationTheme.colors.chart.success}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="90th Percentile"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      
      {!complianceMode && (
        <div style={styles.note}>
          Note: The shaded area represents the range of potential outcomes from 10th to 90th percentile.
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
  },
  title: {
    ...presentationTheme.typography.slideTitle,
    color: presentationTheme.colors.gold,
    marginBottom: '2rem',
  },
  metricsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '1.5rem',
    marginBottom: '2rem',
  },
  metricCard: {
    backgroundColor: presentationTheme.colors.background.secondary,
    padding: '1.5rem',
    borderRadius: presentationTheme.borderRadius.md,
    textAlign: 'center',
    border: `1px solid ${presentationTheme.colors.border}`,
  },
  metricLabel: {
    ...presentationTheme.typography.label,
    color: presentationTheme.colors.text.muted,
    marginBottom: '0.5rem',
  },
  metricValue: {
    ...presentationTheme.typography.heading,
    fontWeight: 700,
  },
  chartContainer: {
    flex: 1,
    backgroundColor: presentationTheme.colors.background.secondary,
    borderRadius: presentationTheme.borderRadius.lg,
    padding: '2rem',
    border: `1px solid ${presentationTheme.colors.border}`,
  },
  note: {
    ...presentationTheme.typography.small,
    color: presentationTheme.colors.text.muted,
    textAlign: 'center',
    marginTop: '1rem',
    fontStyle: 'italic',
  },
};

export default MonteCarloSlide;