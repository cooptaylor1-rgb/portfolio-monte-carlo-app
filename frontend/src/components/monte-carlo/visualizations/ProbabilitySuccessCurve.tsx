/**
 * Probability of Success Over Time Chart
 * Shows how success probability evolves year by year based on portfolio sustainability
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
  formatAge,
  getTooltipStyle,
  chartContainerStyle,
  sectionHeaderStyle,
  keyTakeawayStyle,
  getRiskLevel,
} from './chartUtils';

interface ProbabilitySuccessCurveProps {
  stats: any[];
  currentAge: number;
  monthlySpending: number;
  showTakeaway?: boolean;
}

export const ProbabilitySuccessCurve: React.FC<ProbabilitySuccessCurveProps> = ({
  stats,
  currentAge,
  showTakeaway = true,
}) => {
  const chartData = useMemo(() => {
    // Calculate success probability for each year
    // Success = portfolio > 0 at that point
    return stats
      .filter((_, idx) => idx % 12 === 0)
      .map((stat) => {
        const year = Math.floor(stat.Month / 12);
        const age = currentAge + year;
        
        // Estimate probability based on P10 value
        // If P10 > 0, success prob is very high (>90%)
        // If Median <= 0, success prob is low (<50%)
        let successProb = 1.0;
        
        if (stat.P10 <= 0) {
          // Some scenarios depleted - reduce probability
          if (stat.Median <= 0) {
            successProb = 0.3; // Less than half succeed
          } else if (stat.P25 <= 0) {
            successProb = 0.7; // About 70% succeed
          } else {
            successProb = 0.9; // 90% succeed (10th percentile failed)
          }
        }
        
        return {
          year,
          age,
          successProbability: successProb,
          p10: stat.P10,
          median: stat.Median,
        };
      });
  }, [stats, currentAge]);

  const finalSuccessProb = chartData[chartData.length - 1]?.successProbability || 0;
  const riskLevel = getRiskLevel(finalSuccessProb);

  // Find year where success drops below 80%
  const criticalYear = chartData.find(d => d.successProbability < 0.8);

  const takeawayMessage = useMemo(() => {
    if (finalSuccessProb >= 0.90) {
      return 'Your plan shows excellent sustainability throughout the planning period. Success probability remains high even in later years, indicating strong resilience to market volatility.';
    }
    if (finalSuccessProb >= 0.80) {
      return `Your plan maintains good success probability through most years. ${criticalYear ? `Monitor closely around age ${criticalYear.age} where probability dips to ${formatPercent(criticalYear.successProbability)}.` : ''}`;
    }
    if (finalSuccessProb >= 0.70) {
      return 'Success probability declines significantly in later years. Consider reducing spending, increasing allocation to growth assets, or identifying additional income sources to improve long-term sustainability.';
    }
    return 'Plan faces substantial risk of depletion. Immediate adjustments recommended: reduce spending by 10-20%, delay retirement 2-3 years, or reassess asset allocation strategy.';
  }, [finalSuccessProb, criticalYear]);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Chances of Funding Your Plan Over Time</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        This chart shows the probability that your portfolio will successfully support your spending needs 
        at each age. Higher percentages indicate greater confidence in plan sustainability.
      </p>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart
          data={chartData}
          margin={chartTheme.spacing.chartMargin}
        >
          <defs>
            <linearGradient id="successGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={salemColors.success} stopOpacity={0.3} />
              <stop offset="100%" stopColor={salemColors.success} stopOpacity={0.05} />
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
            domain={[0, 1]}
            stroke={chartTheme.textColor}
            style={chartTheme.fonts.label}
            tickFormatter={(value) => formatPercent(value, 0)}
          />

          <Tooltip
            contentStyle={getTooltipStyle()}
            formatter={(value: number, name: string) => {
              if (name === 'successProbability') {
                return [formatPercent(value, 1), 'Success Probability'];
              }
              return [value, name];
            }}
            labelFormatter={(label) => `Age ${label}`}
          />

          <Legend wrapperStyle={{ paddingTop: '20px' }} />

          {/* Shaded area under curve */}
          <Area
            type="monotone"
            dataKey="successProbability"
            stroke="none"
            fill="url(#successGradient)"
            name="Success Zone"
          />

          {/* Main probability line */}
          <Line
            type="monotone"
            dataKey="successProbability"
            stroke={salemColors.navy}
            strokeWidth={3}
            dot={{ fill: salemColors.navy, r: 4 }}
            activeDot={{ r: 6 }}
            name="Plan Success Probability"
          />

          {/* Reference lines for key thresholds */}
          <ReferenceLine
            y={0.9}
            stroke={salemColors.success}
            strokeDasharray="3 3"
            label={{ value: '90% - Excellent', position: 'right', fontSize: 11, fill: salemColors.success }}
          />
          <ReferenceLine
            y={0.8}
            stroke={salemColors.info}
            strokeDasharray="3 3"
            label={{ value: '80% - Good', position: 'right', fontSize: 11, fill: salemColors.info }}
          />
          <ReferenceLine
            y={0.7}
            stroke={salemColors.warning}
            strokeDasharray="3 3"
            label={{ value: '70% - Acceptable', position: 'right', fontSize: 11, fill: salemColors.warning }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Risk level indicator */}
      <div style={{
        marginTop: '20px',
        padding: '16px',
        backgroundColor: `${riskLevel.color}15`,
        borderLeft: `4px solid ${riskLevel.color}`,
        borderRadius: '8px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <strong style={{ color: riskLevel.color }}>Final Success Probability:</strong>{' '}
            <span style={{ fontSize: '20px', fontWeight: 600, color: riskLevel.color }}>
              {formatPercent(finalSuccessProb, 1)}
            </span>
          </div>
          <div style={{
            padding: '8px 16px',
            backgroundColor: riskLevel.color,
            color: '#FFFFFF',
            borderRadius: '6px',
            fontWeight: 600,
            fontSize: '14px',
          }}>
            {riskLevel.level} Risk
          </div>
        </div>
        <p style={{ marginTop: '8px', marginBottom: 0, fontSize: '13px', color: '#374151' }}>
          {riskLevel.description}
        </p>
      </div>

      {showTakeaway && (
        <div style={keyTakeawayStyle}>
          <strong>Key Takeaway:</strong> {takeawayMessage}
        </div>
      )}
    </div>
  );
};

export default ProbabilitySuccessCurve;
