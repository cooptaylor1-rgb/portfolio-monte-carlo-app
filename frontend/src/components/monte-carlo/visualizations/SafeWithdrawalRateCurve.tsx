/**
 * Safe Withdrawal Rate Analysis
 * Shows probability of success at different spending levels
 */

import React, { useMemo } from 'react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
} from 'recharts';
import {
  salemColors,
  chartTheme,
  formatPercent,
  formatCurrency,
  getTooltipStyle,
  chartContainerStyle,
  sectionHeaderStyle,
  keyTakeawayStyle,
} from './chartUtils';

interface SafeWithdrawalRateCurveProps {
  startingPortfolio: number;
  currentSpending: number;
  successProbability: number;
  showTakeaway?: boolean;
}

export const SafeWithdrawalRateCurve: React.FC<SafeWithdrawalRateCurveProps> = ({
  startingPortfolio,
  currentSpending,
  successProbability,
  showTakeaway = true,
}) => {
  const chartData = useMemo(() => {
    const currentRate = Math.abs(currentSpending * 12) / startingPortfolio;
    
    // Generate withdrawal rates from 2% to 8%
    const rates = [];
    for (let rate = 0.02; rate <= 0.08; rate += 0.005) {
      // Estimate success probability based on withdrawal rate
      // Rule of thumb: 4% rule has ~85-90% success
      // Lower rates = higher success, higher rates = lower success
      let estimatedSuccess;
      
      if (rate <= 0.03) {
        estimatedSuccess = 0.95 - (0.03 - rate) * 2; // Very high success
      } else if (rate <= 0.04) {
        estimatedSuccess = 0.85 + (0.04 - rate) * 10; // 4% rule zone
      } else if (rate <= 0.05) {
        estimatedSuccess = 0.70 + (0.05 - rate) * 15;
      } else if (rate <= 0.06) {
        estimatedSuccess = 0.50 + (0.06 - rate) * 20;
      } else {
        estimatedSuccess = Math.max(0.20, 0.50 - (rate - 0.06) * 15);
      }
      
      // Adjust based on actual success probability
      const adjustment = successProbability - (currentRate <= 0.04 ? 0.85 : 0.70);
      estimatedSuccess = Math.min(0.98, Math.max(0.15, estimatedSuccess + adjustment));
      
      rates.push({
        rate,
        ratePercent: rate * 100,
        successProbability: estimatedSuccess,
        annualAmount: rate * startingPortfolio,
        monthlyAmount: (rate * startingPortfolio) / 12,
        isCurrent: Math.abs(rate - currentRate) < 0.003,
      });
    }
    
    return rates;
  }, [startingPortfolio, currentSpending, successProbability]);

  const currentRate = Math.abs(currentSpending * 12) / startingPortfolio;
  const safeRate = chartData.find(d => d.successProbability >= 0.85)?.rate || 0.03;
  const conservativeRate = chartData.find(d => d.successProbability >= 0.90)?.rate || 0.025;

  const takeawayMessage = useMemo(() => {
    if (currentRate <= conservativeRate) {
      return `Your current withdrawal rate of ${formatPercent(currentRate)} is conservative and sustainable. This provides a strong buffer against market downturns and sequence risk.`;
    }
    if (currentRate <= safeRate) {
      return `Your current withdrawal rate of ${formatPercent(currentRate)} falls within the historically safe range (≥85% success). Plan shows good sustainability with reasonable flexibility.`;
    }
    if (currentRate <= 0.05) {
      return `Your current withdrawal rate of ${formatPercent(currentRate)} exceeds traditional safe levels. Consider reducing spending to ${formatPercent(safeRate)} (${formatCurrency((safeRate * startingPortfolio) / 12)}/month) to improve sustainability.`;
    }
    return `Your current withdrawal rate of ${formatPercent(currentRate)} is high and poses significant depletion risk. Strongly recommend reducing to ${formatPercent(safeRate)} or lower to ensure plan viability.`;
  }, [currentRate, safeRate, conservativeRate, startingPortfolio]);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Safe Withdrawal Rate Analysis</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        This chart shows how different annual withdrawal rates affect your plan's probability of success. 
        The "4% rule" traditionally targets 85-90% success. Your current rate is highlighted for comparison.
      </p>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart
          data={chartData}
          margin={chartTheme.spacing.chartMargin}
        >
          <defs>
            <linearGradient id="safeZone" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={salemColors.success} stopOpacity={0.3} />
              <stop offset="100%" stopColor={salemColors.success} stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.gridColor} />
          
          <XAxis
            dataKey="ratePercent"
            stroke={chartTheme.textColor}
            style={chartTheme.fonts.label}
            tickFormatter={(value) => `${value.toFixed(1)}%`}
            label={{ value: 'Annual Withdrawal Rate', position: 'insideBottom', offset: -10 }}
          />
          
          <YAxis
            domain={[0, 1]}
            stroke={chartTheme.textColor}
            style={chartTheme.fonts.label}
            tickFormatter={(value) => formatPercent(value, 0)}
            label={{ value: 'Success Probability', angle: -90, position: 'insideLeft' }}
          />

          <Tooltip
            contentStyle={getTooltipStyle()}
            formatter={(value: number, name: string) => {
              if (name === 'successProbability') {
                return [formatPercent(value, 1), 'Success Probability'];
              }
              return [value, name];
            }}
            labelFormatter={(label) => {
              const point = chartData.find(d => d.ratePercent === label);
              return `${label.toFixed(1)}% - ${formatCurrency(point?.monthlyAmount || 0)}/month`;
            }}
          />

          <Legend wrapperStyle={{ paddingTop: '20px' }} />

          {/* Safe zone shading (above 85% success) */}
          <Area
            type="monotone"
            dataKey="successProbability"
            stroke="none"
            fill="url(#safeZone)"
            name="Safe Zone (>85%)"
          />

          {/* Main success curve */}
          <Line
            type="monotone"
            dataKey="successProbability"
            stroke={salemColors.navy}
            strokeWidth={3}
            dot={(props: any) => {
              const { cx, cy, payload } = props;
              if (payload.isCurrent) {
                return (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={8}
                    fill={salemColors.gold}
                    stroke="#FFFFFF"
                    strokeWidth={2}
                  />
                );
              }
              return <circle cx={cx} cy={cy} r={0} />;
            }}
            name="Success Probability"
          />

          {/* Reference lines */}
          <ReferenceLine
            y={0.9}
            stroke={salemColors.success}
            strokeDasharray="3 3"
            label={{ value: '90% - Conservative', position: 'right', fontSize: 11 }}
          />
          <ReferenceLine
            y={0.85}
            stroke={salemColors.info}
            strokeDasharray="3 3"
            label={{ value: '85% - Traditional "Safe"', position: 'right', fontSize: 11 }}
          />
          <ReferenceLine
            y={0.7}
            stroke={salemColors.warning}
            strokeDasharray="3 3"
            label={{ value: '70% - Elevated Risk', position: 'right', fontSize: 11 }}
          />

          {/* Vertical line for current rate */}
          {currentRate <= 0.08 && (
            <ReferenceLine
              x={currentRate * 100}
              stroke={salemColors.gold}
              strokeWidth={2}
              label={{
                value: 'Your Current Rate',
                position: 'top',
                fontSize: 12,
                fill: salemColors.gold,
                fontWeight: 600,
              }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Rate comparison table */}
      <div style={{
        marginTop: '20px',
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '12px',
      }}>
        <div style={{
          padding: '12px',
          backgroundColor: '#ECFDF5',
          borderRadius: '8px',
          border: `2px solid ${salemColors.success}`,
        }}>
          <div style={{ fontSize: '12px', color: '#065F46', marginBottom: '4px' }}>
            Conservative (90%+)
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: salemColors.success }}>
            {formatPercent(conservativeRate)}
          </div>
          <div style={{ fontSize: '12px', color: '#065F46', marginTop: '4px' }}>
            {formatCurrency((conservativeRate * startingPortfolio) / 12)}/mo
          </div>
        </div>

        <div style={{
          padding: '12px',
          backgroundColor: '#FEF3C7',
          borderRadius: '8px',
          border: currentRate <= safeRate ? `2px solid ${salemColors.gold}` : '1px solid #E5E7EB',
        }}>
          <div style={{ fontSize: '12px', color: '#78350F', marginBottom: '4px' }}>
            Your Current Rate
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: salemColors.gold }}>
            {formatPercent(currentRate)}
          </div>
          <div style={{ fontSize: '12px', color: '#78350F', marginTop: '4px' }}>
            {formatCurrency(Math.abs(currentSpending))}/mo
          </div>
        </div>

        <div style={{
          padding: '12px',
          backgroundColor: '#EFF6FF',
          borderRadius: '8px',
          border: `2px solid ${salemColors.info}`,
        }}>
          <div style={{ fontSize: '12px', color: '#1E40AF', marginBottom: '4px' }}>
            Traditional Safe (85%+)
          </div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: salemColors.info }}>
            {formatPercent(safeRate)}
          </div>
          <div style={{ fontSize: '12px', color: '#1E40AF', marginTop: '4px' }}>
            {formatCurrency((safeRate * startingPortfolio) / 12)}/mo
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

export default SafeWithdrawalRateCurve;
