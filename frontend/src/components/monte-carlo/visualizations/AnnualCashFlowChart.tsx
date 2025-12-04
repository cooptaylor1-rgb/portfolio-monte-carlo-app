/**
 * Annual Cash Flow vs Portfolio Balance Chart
 * Shows spending, withdrawals, and portfolio balance together over time
 */

import React, { useMemo } from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
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

interface AnnualCashFlowChartProps {
  stats: any[];
  currentAge: number;
  monthlySpending: number;
  monthlyIncome: number;
  showTakeaway?: boolean;
}

export const AnnualCashFlowChart: React.FC<AnnualCashFlowChartProps> = ({
  stats,
  currentAge,
  monthlySpending,
  monthlyIncome,
  showTakeaway = true,
}) => {
  const chartData = useMemo(() => {
    return stats
      .filter((_, idx) => idx % 12 === 0)
      .map((stat) => {
        const year = Math.floor(stat.Month / 12);
        const age = currentAge + year;
        
        // Calculate annual cash flows
        const annualSpending = Math.abs(monthlySpending * 12);
        const annualIncome = monthlyIncome * 12;
        const netWithdrawal = annualSpending - annualIncome;
        
        return {
          year,
          age,
          portfolioBalance: stat.Median,
          spending: annualSpending,
          income: annualIncome,
          netWithdrawal,
        };
      });
  }, [stats, currentAge, monthlySpending, monthlyIncome]);

  const totalWithdrawals = chartData.reduce((sum, d) => sum + d.netWithdrawal, 0);
  const finalBalance = chartData[chartData.length - 1]?.portfolioBalance || 0;

  const takeawayMessage = useMemo(() => {
    if (finalBalance > chartData[0]?.portfolioBalance) {
      return `Portfolio grows despite withdrawals, ending at ${formatCurrency(finalBalance)}. Total withdrawals of ${formatCurrency(totalWithdrawals)} are fully offset by investment returns. This indicates conservative spending relative to growth potential.`;
    }
    if (finalBalance > chartData[0]?.portfolioBalance * 0.5) {
      return `Portfolio maintains healthy balance while supporting spending needs. Ending value of ${formatCurrency(finalBalance)} represents ${((finalBalance / chartData[0]?.portfolioBalance) * 100).toFixed(0)}% of starting value after ${formatCurrency(totalWithdrawals)} in cumulative withdrawals.`;
    }
    return `Significant portfolio drawdown detected. Cumulative withdrawals of ${formatCurrency(totalWithdrawals)} reduce portfolio to ${formatCurrency(finalBalance)}. Consider reducing annual spending by 10-15% or increasing income sources to improve sustainability.`;
  }, [chartData, finalBalance, totalWithdrawals]);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Annual Cash Flow & Portfolio Balance</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        This chart illustrates the relationship between portfolio withdrawals and balance over time. 
        Bars show annual cash flows while the line tracks median portfolio value.
      </p>

      <ResponsiveContainer width="100%" height={450}>
        <ComposedChart
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
            yAxisId="left"
            stroke={chartTheme.textColor}
            style={chartTheme.fonts.label}
            tickFormatter={formatCurrency}
            label={{ value: 'Portfolio Balance', angle: -90, position: 'insideLeft' }}
          />

          <YAxis
            yAxisId="right"
            orientation="right"
            stroke={chartTheme.textColor}
            style={chartTheme.fonts.label}
            tickFormatter={formatCurrency}
            label={{ value: 'Annual Cash Flow', angle: 90, position: 'insideRight' }}
          />

          <Tooltip
            contentStyle={getTooltipStyle()}
            formatter={(value: number, name: string) => [formatCurrency(value), name]}
            labelFormatter={(label) => `Age ${label}`}
          />

          <Legend wrapperStyle={{ paddingTop: '20px' }} />

          <Bar
            yAxisId="right"
            dataKey="spending"
            fill={salemColors.danger}
            name="Annual Spending"
            opacity={0.6}
          />

          <Bar
            yAxisId="right"
            dataKey="income"
            fill={salemColors.success}
            name="Annual Income"
            opacity={0.6}
          />

          <Line
            yAxisId="left"
            type="monotone"
            dataKey="portfolioBalance"
            stroke={salemColors.gold}
            strokeWidth={3}
            dot={false}
            name="Portfolio Balance (Median)"
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Summary metrics */}
      <div style={{
        marginTop: '20px',
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
      }}>
        <div style={{ padding: '12px', backgroundColor: '#F9FAFB', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
            Cumulative Withdrawals
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: salemColors.danger }}>
            {formatCurrency(totalWithdrawals)}
          </div>
        </div>

        <div style={{ padding: '12px', backgroundColor: '#F9FAFB', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
            Final Balance
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: salemColors.gold }}>
            {formatCurrency(finalBalance)}
          </div>
        </div>

        <div style={{ padding: '12px', backgroundColor: '#F9FAFB', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
            Average Annual Spending
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: salemColors.navy }}>
            {formatCurrency(Math.abs(monthlySpending * 12))}
          </div>
        </div>

        <div style={{ padding: '12px', backgroundColor: '#F9FAFB', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
            Average Annual Income
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: salemColors.success }}>
            {formatCurrency(monthlyIncome * 12)}
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

export default AnnualCashFlowChart;
