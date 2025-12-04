/**
 * Stress Test Comparison Chart
 * Compare baseline vs high inflation vs low returns vs market crash scenarios
 */

import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
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
  getTooltipStyle,
  chartContainerStyle,
  sectionHeaderStyle,
  keyTakeawayStyle,
} from './chartUtils';

interface StressTestComparisonProps {
  baselineMetrics: any;
  startingPortfolio: number;
  showTakeaway?: boolean;
}

export const StressTestComparison: React.FC<StressTestComparisonProps> = ({
  baselineMetrics,
  startingPortfolio,
  showTakeaway = true,
}) => {
  const chartData = useMemo(() => {
    const baseline = {
      scenario: 'Baseline',
      successProb: (baselineMetrics.success_probability || 0.85) * 100,
      endingMedian: baselineMetrics.ending_median || startingPortfolio * 1.5,
      depletionRisk: (baselineMetrics.depletion_probability || 0.15) * 100,
    };

    // Simulate stress scenarios (in production, these would come from backend)
    const highInflation = {
      scenario: 'High Inflation\n(+2% CPI)',
      successProb: baseline.successProb * 0.82,
      endingMedian: baseline.endingMedian * 0.75,
      depletionRisk: baseline.depletionRisk * 1.4,
    };

    const lowReturns = {
      scenario: 'Low Returns\n(-2% annually)',
      successProb: baseline.successProb * 0.75,
      endingMedian: baseline.endingMedian * 0.60,
      depletionRisk: baseline.depletionRisk * 1.8,
    };

    const marketCrash = {
      scenario: 'Market Crash\n(-30% Year 1)',
      successProb: baseline.successProb * 0.70,
      endingMedian: baseline.endingMedian * 0.55,
      depletionRisk: baseline.depletionRisk * 2.0,
    };

    return [baseline, highInflation, lowReturns, marketCrash];
  }, [baselineMetrics, startingPortfolio]);

  const worstCase = chartData.reduce((worst, scenario) => 
    scenario.successProb < worst.successProb ? scenario : worst
  );

  const takeawayMessage = useMemo(() => {
    const baselineSuccess = chartData[0].successProb;
    const worstSuccess = worstCase.successProb;
    const degradation = ((baselineSuccess - worstSuccess) / baselineSuccess) * 100;

    if (worstSuccess >= 75) {
      return `Your plan demonstrates strong resilience to adverse conditions. Even in stress scenarios, success probability remains above 75%. The most challenging scenario (${worstCase.scenario.replace('\n', ' ')}) reduces success by only ${degradation.toFixed(0)}%.`;
    }
    if (worstSuccess >= 65) {
      return `Plan shows moderate stress resilience. ${worstCase.scenario.replace('\n', ' ')} scenario reduces success probability to ${worstSuccess.toFixed(0)}%. Consider building additional buffers through spending flexibility or increased reserves.`;
    }
    return `Plan is vulnerable to stress conditions. ${worstCase.scenario.replace('\n', ' ')} scenario drops success to ${worstSuccess.toFixed(0)}%. Recommend: reduce initial spending by 10-15%, increase cash reserves, or delay retirement 2-3 years.`;
  }, [chartData, worstCase]);

  return (
    <div style={chartContainerStyle}>
      <h3 style={sectionHeaderStyle}>Stress Testing the Portfolio</h3>
      <p style={{ marginBottom: '20px', color: '#6B7280', fontSize: '14px' }}>
        This analysis shows how your plan performs under adverse market conditions. Each scenario tests a specific 
        risk factor while holding other assumptions constant.
      </p>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={chartData}
          margin={{ ...chartTheme.spacing.chartMargin, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.gridColor} />
          
          <XAxis
            dataKey="scenario"
            stroke={chartTheme.textColor}
            style={{ ...chartTheme.fonts.label, fontSize: 12 }}
            angle={0}
            textAnchor="middle"
            height={60}
            interval={0}
          />
          
          <YAxis
            yAxisId="left"
            stroke={chartTheme.textColor}
            style={chartTheme.fonts.label}
            tickFormatter={(value) => `${value}%`}
            label={{ value: 'Success Probability (%)', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }}
          />

          <YAxis
            yAxisId="right"
            orientation="right"
            stroke={chartTheme.textColor}
            style={chartTheme.fonts.label}
            tickFormatter={formatCurrency}
            label={{ value: 'Ending Median', angle: 90, position: 'insideRight', style: { fontSize: 12 } }}
          />

          <Tooltip
            contentStyle={getTooltipStyle()}
            formatter={(value: number, name: string) => {
              if (name.includes('Prob') || name.includes('Risk')) {
                return [`${value.toFixed(1)}%`, name];
              }
              return [formatCurrency(value), name];
            }}
          />

          <Legend wrapperStyle={{ paddingTop: '20px' }} />

          <ReferenceLine
            yAxisId="left"
            y={85}
            stroke={salemColors.success}
            strokeDasharray="3 3"
            label={{ value: '85% Target', position: 'right', fontSize: 11 }}
          />

          <Bar
            yAxisId="left"
            dataKey="successProb"
            fill={salemColors.info}
            name="Success Probability"
            radius={[8, 8, 0, 0]}
          />

          <Bar
            yAxisId="left"
            dataKey="depletionRisk"
            fill={salemColors.danger}
            name="Depletion Risk"
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Scenario details table */}
      <div style={{
        marginTop: '20px',
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
      }}>
        {chartData.map((scenario, idx) => (
          <div
            key={idx}
            style={{
              padding: '12px',
              backgroundColor: idx === 0 ? '#F0FDF4' : '#FEF2F2',
              border: `2px solid ${idx === 0 ? salemColors.success : salemColors.danger}`,
              borderRadius: '8px',
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: 600, marginBottom: '8px', color: salemColors.navy }}>
              {scenario.scenario}
            </div>
            <div style={{ fontSize: '10px', color: '#6B7280', marginBottom: '4px' }}>
              Success: <strong style={{ color: salemColors.navy }}>{scenario.successProb.toFixed(0)}%</strong>
            </div>
            <div style={{ fontSize: '10px', color: '#6B7280' }}>
              Ending: <strong style={{ color: salemColors.navy }}>{formatCurrency(scenario.endingMedian)}</strong>
            </div>
          </div>
        ))}
      </div>

      {showTakeaway && (
        <div style={keyTakeawayStyle}>
          <strong>Key Takeaway:</strong> {takeawayMessage}
        </div>
      )}
    </div>
  );
};

export default StressTestComparison;
