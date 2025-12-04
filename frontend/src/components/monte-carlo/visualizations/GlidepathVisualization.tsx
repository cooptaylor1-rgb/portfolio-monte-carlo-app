/**
 * Glidepath Visualization Chart
 * Shows equity/fixed income allocation changes over time
 */

import React, { useMemo } from 'react';
import {
  AreaChart,
  Area,
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
  formatAge,
  getTooltipStyle,
  chartContainerStyle,
  sectionHeaderStyle,
  keyTakeawayStyle,
} from './chartUtils';

interface GlidepathVisualizationProps {
  currentAge: number;
  planYears: number;
  initialEquity: number;
  showTakeaway?: boolean;
}

export const GlidepathVisualization: React.FC<GlidepathVisualizationProps> = ({
  currentAge,
  planYears,
  initialEquity,
  showTakeaway = true,
}) => {
  const chartData = useMemo(() => {
    // Common glidepath: reduce equity by 0.5-1% per year
    const equityDeclineRate = 0.006; // 0.6% per year
    const minEquity = 0.30; // Floor at 30% equity
    
    return Array.from({ length: Math.floor(planYears / 12) + 1 }, (_, year) => {
      const age = currentAge + year;
      
      // Calculate equity allocation
      const equity = Math.max(minEquity, initialEquity - (equityDeclineRate * year));
      const fixedIncome = 1 - equity;
      
      return {
        year,
        age,
        equity: equity * 100,
        fixedIncome: fixedIncome * 100,
      };
    });
  }, [currentAge, planYears, initialEquity]);

  const finalEquity = chartData[chartData.length - 1]?.equity || 0;
  const equityReduction = (initialEquity * 100) - finalEquity;

  const takeawayMessage = useMemo(() => {
    if (equityReduction < 10) {
      return `Minimal glidepath adjustment (${equityReduction.toFixed(1)}% equity reduction). Static allocation maintains consistent risk exposure throughout retirement. Appropriate if spending needs are stable and risk tolerance remains high. Consider more aggressive de-risking if circumstances change.`;
    }
    if (equityReduction < 25) {
      return `Moderate glidepath (${equityReduction.toFixed(1)}% equity reduction) gradually reduces portfolio volatility while maintaining growth potential. This balanced approach helps protect against sequence-of-returns risk in early retirement while sustaining later years. Aligns with typical longevity planning.`;
    }
    return `Aggressive glidepath (${equityReduction.toFixed(1)}% equity reduction) significantly de-risks over time. Starting at ${(initialEquity * 100).toFixed(0)}% equity and declining to ${finalEquity.toFixed(0)}% prioritizes capital preservation in later years. Well-suited for conservative clients or those with guaranteed income sources covering basic needs.`;
  }, [equityReduction, initialEquity, finalEquity]);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Asset Allocation Glidepath</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        The glidepath shows how your asset allocation evolves over time, typically becoming more 
        conservative as you age to reduce portfolio volatility in later retirement years.
      </p>

      <ResponsiveContainer width="100%" height={400}>
        <AreaChart
          data={chartData}
          margin={chartTheme.spacing.chartMargin}
        >
          <defs>
            <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={salemColors.gold} stopOpacity={0.8} />
              <stop offset="95%" stopColor={salemColors.gold} stopOpacity={0.3} />
            </linearGradient>
            <linearGradient id="colorFixed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={salemColors.navy} stopOpacity={0.8} />
              <stop offset="95%" stopColor={salemColors.navy} stopOpacity={0.3} />
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
            tickFormatter={(value) => `${value}%`}
            domain={[0, 100]}
            label={{ value: 'Allocation %', angle: -90, position: 'insideLeft' }}
          />

          <Tooltip
            contentStyle={getTooltipStyle()}
            formatter={(value: number, name: string) => [`${value.toFixed(1)}%`, name]}
            labelFormatter={(label) => `Age ${label}`}
          />

          <Legend wrapperStyle={{ paddingTop: '20px' }} />

          <ReferenceLine
            y={60}
            stroke="#9CA3AF"
            strokeDasharray="3 3"
            label={{ value: '60/40 Balanced', position: 'right', fontSize: 11 }}
          />

          <Area
            type="monotone"
            dataKey="equity"
            stackId="1"
            stroke={salemColors.gold}
            fill="url(#colorEquity)"
            name="Equity Allocation"
          />

          <Area
            type="monotone"
            dataKey="fixedIncome"
            stackId="1"
            stroke={salemColors.navy}
            fill="url(#colorFixed)"
            name="Fixed Income Allocation"
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Allocation milestones */}
      <div style={{
        marginTop: '20px',
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '12px',
      }}>
        <div style={{ padding: '12px', backgroundColor: '#FEF3C7', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#92400E', marginBottom: '4px' }}>
            Initial Allocation
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: salemColors.gold }}>
            {(initialEquity * 100).toFixed(0)}% Equity
          </div>
          <div style={{ fontSize: '10px', color: '#92400E', marginTop: '2px' }}>
            Age {currentAge}
          </div>
        </div>

        <div style={{ padding: '12px', backgroundColor: '#F9FAFB', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>
            Midpoint Allocation
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: '#374151' }}>
            {chartData[Math.floor(chartData.length / 2)]?.equity.toFixed(0)}% Equity
          </div>
          <div style={{ fontSize: '10px', color: '#6B7280', marginTop: '2px' }}>
            Age {chartData[Math.floor(chartData.length / 2)]?.age}
          </div>
        </div>

        <div style={{ padding: '12px', backgroundColor: '#DBEAFE', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#1E3A8A', marginBottom: '4px' }}>
            Final Allocation
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: salemColors.navy }}>
            {finalEquity.toFixed(0)}% Equity
          </div>
          <div style={{ fontSize: '10px', color: '#1E3A8A', marginTop: '2px' }}>
            Age {chartData[chartData.length - 1]?.age}
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

export default GlidepathVisualization;
