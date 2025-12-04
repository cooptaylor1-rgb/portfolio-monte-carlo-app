/**
 * Withdrawal Strategy Comparison Chart
 * Compares fixed spending vs dynamic spending strategies
 */

import React, { useMemo } from 'react';
import { Card } from '../../ui/Card';
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
      <p className="mb-5 text-text-secondary text-sm">
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
      <div className="mt-5 grid grid-cols-2 gap-4">
        <Card padding="md" className="border-2" style={{ borderColor: salemColors.navy }}>
          <div className="text-sm font-semibold mb-2" style={{ color: salemColors.navy }}>
            Fixed Spending Strategy
          </div>
          <div className="text-xs text-text-secondary mb-3">
            Maintains constant spending adjusted only for inflation
          </div>
          <div className="text-xs text-text-primary">
            <div><strong>Pros:</strong> Predictable lifestyle, easy planning</div>
            <div className="mt-1"><strong>Cons:</strong> May deplete portfolio faster in poor markets</div>
            <div className="mt-2 font-semibold">
              Average: {formatCurrency(avgFixed)}/year
            </div>
          </div>
        </Card>

        <Card padding="md" className="border-2" style={{ borderColor: salemColors.gold }}>
          <div className="text-sm font-semibold mb-2" style={{ color: salemColors.gold }}>
            Dynamic Guardrails Strategy
          </div>
          <div className="text-xs text-text-secondary mb-3">
            Adjusts spending within 20% bands based on portfolio performance
          </div>
          <div className="text-xs text-text-primary">
            <div><strong>Pros:</strong> Balances stability with sustainability</div>
            <div className="mt-1"><strong>Cons:</strong> Requires spending flexibility</div>
            <div className="mt-2 font-semibold">
              Average: {formatCurrency(avgDynamic)}/year
            </div>
          </div>
        </Card>
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
