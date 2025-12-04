/**
 * Withdrawal Strategy Comparison Chart
 * Compares fixed spending vs dynamic spending strategies
 */

import React, { useMemo } from 'react';
import {
  LineChart,
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

interface WithdrawalStrategyComparisonProps {
  stats: any[];
  currentAge: number;
  initialSpending: number;
  showTakeaway?: boolean;
}

export const WithdrawalStrategyComparison: React.FC<WithdrawalStrategyComparisonProps> = ({
  stats,
  currentAge,
  initialSpending,
  showTakeaway = true,
}) => {
  const chartData = useMemo(() => {
    // Simulate different withdrawal strategies
    return stats
      .filter((_, idx) => idx % 12 === 0)
      .map((stat, idx) => {
        const year = idx;
        const age = currentAge + year;
        
        // Fixed spending: constant in real terms (inflation-adjusted)
        const fixedSpending = Math.abs(initialSpending * 12);
        
        // 4% rule: 4% of current portfolio balance
        const fourPercentRule = stat.Median * 0.04;
        
        // Dynamic (guardrails): adjusts within 20% band
        const targetSpending = fixedSpending;
        const currentBalance = stat.Median;
        const safeDynamic = Math.max(
          targetSpending * 0.8,
          Math.min(targetSpending * 1.2, currentBalance * 0.045)
        );
        
        // RMD-based (simulated): scales with portfolio and age
        const rmdFactor = Math.min(0.04 + (age - currentAge) * 0.001, 0.08);
        const rmdBased = currentBalance * rmdFactor;
        
        return {
          year,
          age,
          fixedSpending,
          fourPercentRule,
          dynamicGuardrails: safeDynamic,
          rmdBased,
        };
      });
  }, [stats, currentAge, initialSpending]);

  const avgFixed = chartData.reduce((sum, d) => sum + d.fixedSpending, 0) / chartData.length;
  const avgDynamic = chartData.reduce((sum, d) => sum + d.dynamicGuardrails, 0) / chartData.length;
  const variability = Math.abs(avgFixed - avgDynamic) / avgFixed;

  const takeawayMessage = useMemo(() => {
    if (variability < 0.1) {
      return `Dynamic guardrails closely track fixed spending (${(variability * 100).toFixed(1)}% difference), suggesting stable portfolio that can support consistent withdrawals. Fixed spending strategy is appropriate given low variability and strong success probability.`;
    }
    if (variability < 0.25) {
      return `Moderate variability between strategies (${(variability * 100).toFixed(1)}% difference). Dynamic guardrails provide ${avgDynamic > avgFixed ? 'upside potential' : 'downside protection'} while maintaining reasonable stability. Consider dynamic approach for flexibility without significant lifestyle disruption.`;
    }
    return `Significant variability between strategies (${(variability * 100).toFixed(1)}% difference). Dynamic guardrails suggest portfolio volatility requires spending adjustments. Recommend flexible spending framework: essential expenses covered by fixed income, discretionary spending adjusted based on portfolio performance.`;
  }, [variability, avgFixed, avgDynamic]);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Withdrawal Strategy Comparison</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        Different withdrawal strategies balance spending stability against portfolio sustainability. 
        This comparison helps identify the most appropriate approach for your situation.
      </p>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={chartTheme.spacing.chartMargin}
        >
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
            label={{ value: 'Annual Spending', angle: -90, position: 'insideLeft' }}
          />

          <Tooltip
            contentStyle={getTooltipStyle()}
            formatter={(value: number, name: string) => [formatCurrency(value), name]}
            labelFormatter={(label) => `Age ${label}`}
          />

          <Legend wrapperStyle={{ paddingTop: '20px' }} />

          <ReferenceLine
            y={Math.abs(initialSpending * 12)}
            stroke="#9CA3AF"
            strokeDasharray="3 3"
            label={{ value: 'Initial Spending', position: 'right' }}
          />

          <Line
            type="monotone"
            dataKey="fixedSpending"
            stroke={salemColors.navy}
            strokeWidth={3}
            dot={false}
            name="Fixed Spending"
          />

          <Line
            type="monotone"
            dataKey="dynamicGuardrails"
            stroke={salemColors.gold}
            strokeWidth={3}
            dot={false}
            name="Dynamic (Guardrails)"
          />

          <Line
            type="monotone"
            dataKey="fourPercentRule"
            stroke={salemColors.success}
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="4% Rule"
          />

          <Line
            type="monotone"
            dataKey="rmdBased"
            stroke="#9CA3AF"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="RMD-Based"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Strategy comparison cards */}
      <div style={{
        marginTop: '20px',
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '16px',
      }}>
        <div style={{
          padding: '16px',
          backgroundColor: '#FFFFFF',
          border: `2px solid ${salemColors.navy}`,
          borderRadius: '8px',
        }}>
          <div style={{ fontSize: '14px', fontWeight: 600, color: salemColors.navy, marginBottom: '8px' }}>
            Fixed Spending Strategy
          </div>
          <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '12px' }}>
            Maintains constant spending adjusted only for inflation
          </div>
          <div style={{ fontSize: '11px', color: '#374151' }}>
            <div><strong>Pros:</strong> Predictable lifestyle, easy planning</div>
            <div style={{ marginTop: '4px' }}><strong>Cons:</strong> May deplete portfolio faster in poor markets</div>
            <div style={{ marginTop: '8px', fontWeight: 600 }}>
              Average: {formatCurrency(avgFixed)}/year
            </div>
          </div>
        </div>

        <div style={{
          padding: '16px',
          backgroundColor: '#FFFFFF',
          border: `2px solid ${salemColors.gold}`,
          borderRadius: '8px',
        }}>
          <div style={{ fontSize: '14px', fontWeight: 600, color: salemColors.gold, marginBottom: '8px' }}>
            Dynamic Guardrails Strategy
          </div>
          <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '12px' }}>
            Adjusts spending within 20% bands based on portfolio performance
          </div>
          <div style={{ fontSize: '11px', color: '#374151' }}>
            <div><strong>Pros:</strong> Balances stability with sustainability</div>
            <div style={{ marginTop: '4px' }}><strong>Cons:</strong> Requires spending flexibility</div>
            <div style={{ marginTop: '8px', fontWeight: 600 }}>
              Average: {formatCurrency(avgDynamic)}/year
            </div>
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

export default WithdrawalStrategyComparison;
