/**
 * Enhanced Fan Chart - Core Monte Carlo Visualization
 * Shows median portfolio value with 10th-90th percentile confidence bands
 */

import React, { useMemo } from 'react';
import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import {
  salemColors,
  chartTheme,
  formatCurrency,
  formatAge,
  getTooltipStyle,
  chartContainerStyle,
  sectionHeaderStyle,
  keyTakeawayStyle,
} from './chartUtils';

interface EnhancedFanChartProps {
  stats: any[];
  currentAge: number;
  startingPortfolio: number;
  showTakeaway?: boolean;
}

export const EnhancedFanChart: React.FC<EnhancedFanChartProps> = ({
  stats,
  currentAge,
  startingPortfolio,
  showTakeaway = true,
}) => {
  const chartData = useMemo(() => {
    // Convert monthly data to annual for cleaner visualization
    return stats
      .filter((_, idx) => idx % 12 === 0)
      .map((stat) => ({
        year: Math.floor(stat.Month / 12),
        age: currentAge + Math.floor(stat.Month / 12),
        p10: stat.P10,
        p25: stat.P25,
        median: stat.Median,
        p75: stat.P75,
        p90: stat.P90,
        mean: stat.Mean,
      }));
  }, [stats, currentAge]);

  const endingMedian = chartData[chartData.length - 1]?.median || 0;
  const endingP10 = chartData[chartData.length - 1]?.p10 || 0;
  const endingP90 = chartData[chartData.length - 1]?.p90 || 0;

  const takeawayMessage = useMemo(() => {
    const growth = endingMedian > startingPortfolio;
    const p10Positive = endingP10 > 0;
    
    if (growth && p10Positive) {
      return 'Your portfolio shows strong growth potential with healthy margins even in adverse scenarios. The median outcome significantly exceeds your starting value, and even the 10th percentile maintains positive balance.';
    }
    if (growth) {
      return 'Your portfolio demonstrates growth potential in typical scenarios. However, adverse market conditions (10th percentile) show portfolio depletion risk. Consider stress testing spending levels or allocation.';
    }
    return 'Current projections show portfolio depletion risk in median scenarios. We recommend reviewing spending levels, income sources, or investment strategy to improve sustainability.';
  }, [endingMedian, endingP10, startingPortfolio]);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Portfolio Projection: Confidence Bands</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        This "fan chart" shows how your portfolio may evolve over time. The gold line represents the median (50th percentile) 
        outcome, with shaded bands showing the range of likely results from worst case (10th percentile) to best case (90th percentile).
      </p>

      <ResponsiveContainer width="100%" height={450}>
        <ComposedChart
          data={chartData}
          margin={chartTheme.spacing.chartMargin}
        >
          <defs>
            {/* Gradient fills for percentile bands */}
            <linearGradient id="fanGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={salemColors.p90} stopOpacity={0.2} />
              <stop offset="100%" stopColor={salemColors.p90} stopOpacity={0.05} />
            </linearGradient>
            <linearGradient id="fanGradient25" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={salemColors.p75} stopOpacity={0.15} />
              <stop offset="100%" stopColor={salemColors.p75} stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.gridColor} />
          
          <XAxis
            dataKey="age"
            stroke={chartTheme.textColor}
            style={chartTheme.fonts.label}
            tickFormatter={(value) => formatAge(value)}
          />
          
          <YAxis
            stroke={chartTheme.textColor}
            style={chartTheme.fonts.label}
            tickFormatter={formatCurrency}
          />

          <Tooltip
            contentStyle={getTooltipStyle()}
            formatter={(value: number, name: string) => {
              const labels: Record<string, string> = {
                p10: '10th Percentile (Worst Case)',
                p25: '25th Percentile',
                median: 'Median (Most Likely)',
                p75: '75th Percentile',
                p90: '90th Percentile (Best Case)',
              };
              return [formatCurrency(value), labels[name] || name];
            }}
            labelFormatter={(label) => `Age ${label}`}
          />

          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />

          {/* 90th percentile upper bound */}
          <Area
            type="monotone"
            dataKey="p90"
            stroke="none"
            fill="url(#fanGradient)"
            name="90th Percentile Range"
          />

          {/* 75th percentile */}
          <Area
            type="monotone"
            dataKey="p75"
            stroke="none"
            fill="url(#fanGradient25)"
            name="75th Percentile Range"
          />

          {/* Median - most prominent */}
          <Line
            type="monotone"
            dataKey="median"
            stroke={salemColors.gold}
            strokeWidth={4}
            dot={false}
            name="Median (50th)"
          />

          {/* 25th percentile boundary */}
          <Line
            type="monotone"
            dataKey="p25"
            stroke={salemColors.warning}
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="25th Percentile"
          />

          {/* 10th percentile - worst case */}
          <Line
            type="monotone"
            dataKey="p10"
            stroke={salemColors.danger}
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="10th Percentile"
          />

          {/* Zero reference line */}
          <ReferenceLine
            y={0}
            stroke="#374151"
            strokeDasharray="3 3"
            label={{ value: 'Portfolio Depletion', position: 'right', fontSize: 12 }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Key metrics summary */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '16px',
        marginTop: '20px',
      }}>
        <div style={{
          padding: '12px',
          backgroundColor: '#FEF2F2',
          borderRadius: '8px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '12px', color: '#991B1B', marginBottom: '4px' }}>
            Worst Case (10th)
          </div>
          <div style={{ fontSize: '20px', fontWeight: 600, color: salemColors.danger }}>
            {formatCurrency(endingP10)}
          </div>
        </div>

        <div style={{
          padding: '12px',
          backgroundColor: '#FEF3C7',
          borderRadius: '8px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '12px', color: '#78350F', marginBottom: '4px' }}>
            Median Outcome
          </div>
          <div style={{ fontSize: '20px', fontWeight: 600, color: salemColors.gold }}>
            {formatCurrency(endingMedian)}
          </div>
        </div>

        <div style={{
          padding: '12px',
          backgroundColor: '#ECFDF5',
          borderRadius: '8px',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: '12px', color: '#065F46', marginBottom: '4px' }}>
            Best Case (90th)
          </div>
          <div style={{ fontSize: '20px', fontWeight: 600, color: salemColors.success }}>
            {formatCurrency(endingP90)}
          </div>
        </div>
      </div>

      {showTakeaway && (
        <div style={keyTakeawayStyle}>
          <strong>Key Takeaway:</strong> {takeawayMessage}
        </div>
      )}
    </div>
  );
};

export default EnhancedFanChart;
