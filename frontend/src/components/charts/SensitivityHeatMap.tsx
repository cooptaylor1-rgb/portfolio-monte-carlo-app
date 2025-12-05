import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
  Area,
  ComposedChart,
} from 'recharts';
import { colors } from '../../theme';

// ==========================================
// TYPES & INTERFACES
// ==========================================

interface SensitivityDataPoint {
  parameter: string;
  variation: number;
  successProbability: number;
  impact?: number;
}

interface SensitivityHeatMapProps {
  data: SensitivityDataPoint[];
  height?: number;
}

// ==========================================
// CHART COLORS FROM DESIGN SYSTEM
// ==========================================

const CHART_COLORS = {
  equityReturn: colors.chart.equity,
  fixedIncomeReturn: colors.chart.fixed,
  inflationRate: colors.brand.gold,
  monthlySpending: colors.status.error.base,
  baseline: colors.text.tertiary,
  gridLines: colors.background.border,
  textPrimary: colors.text.primary,
  textSecondary: colors.text.secondary,
  successStrong: colors.status.success.base,
  successAdequate: colors.status.warning.base,
  successAtRisk: colors.status.error.base,
} as const;

const THRESHOLD_BANDS = {
  strong: { value: 0.80, label: 'Strong', color: CHART_COLORS.successStrong },
  adequate: { value: 0.60, label: 'At Risk', color: CHART_COLORS.successAtRisk },
} as const;

// ==========================================
// UTILITY FORMATTERS
// ==========================================

const formatters = {
  percent: (value: number, decimals: number = 1): string => {
    return `${(value * 100).toFixed(decimals)}%`;
  },
  
  variation: (value: number): string => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${(value * 100).toFixed(1)}%`;
  },
  
  parameterLabel: (param: string): string => {
    const labels: Record<string, string> = {
      'equity_return_annual': 'Equity Return',
      'fi_return_annual': 'Fixed Income Return',
      'inflation_annual': 'Inflation Rate',
      'monthly_spending': 'Monthly Spending',
    };
    return labels[param] || param.replace(/_/g, ' ');
  },
  
  successLevel: (probability: number): string => {
    if (probability >= 0.80) return 'Strong';
    if (probability >= 0.60) return 'Adequate';
    return 'At Risk';
  },
} as const;

export const SensitivityHeatMap: React.FC<SensitivityHeatMapProps> = ({
  data,
  height = 500,
}) => {
  // ==========================================
  // DATA TRANSFORMATION
  // ==========================================

  // Transform data for line chart - group by variation
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    const grouped = data.reduce((acc, point) => {
      const key = point.variation.toFixed(4);
      if (!acc[key]) {
        acc[key] = { variation: point.variation };
      }
      acc[key][point.parameter] = point.successProbability;
      return acc;
    }, {} as Record<string, any>);

    return Object.values(grouped).sort((a, b) => a.variation - b.variation);
  }, [data]);

  // Get unique parameters present in data
  const parameters = useMemo(() => {
    return Array.from(new Set(data.map(d => d.parameter)));
  }, [data]);

  // ==========================================
  // INSIGHTS CALCULATION
  // ==========================================

  const insights = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    const results: string[] = [];
    
    parameters.forEach(param => {
      const paramData = data.filter(d => d.parameter === param);
      if (paramData.length === 0) return;
      
      const minPoint = paramData.reduce((min, p) => 
        p.successProbability < min.successProbability ? p : min
      );
      const maxPoint = paramData.reduce((max, p) => 
        p.successProbability > max.successProbability ? p : max
      );
      const range = maxPoint.successProbability - minPoint.successProbability;
      
      const paramLabel = formatters.parameterLabel(param);
      
      if (range > 0.20) {
        results.push(`${paramLabel}: Highly sensitive (${formatters.percent(range, 0)} range)`);
      } else if (range > 0.10) {
        results.push(`${paramLabel}: Moderately sensitive (${formatters.percent(range, 0)} range)`);
      } else {
        results.push(`${paramLabel}: Low sensitivity (${formatters.percent(range, 0)} range)`);
      }
    });
    
    return results;
  }, [data, parameters]);

  // Parameter styling configuration
  const parameterConfig: Record<string, { color: string; label: string; zIndex: number }> = {
    'monthly_spending': { 
      color: CHART_COLORS.monthlySpending, 
      label: 'Monthly Spending',
      zIndex: 4, // Top priority
    },
    'inflation_annual': { 
      color: CHART_COLORS.inflationRate, 
      label: 'Inflation Rate',
      zIndex: 3,
    },
    'equity_return_annual': { 
      color: CHART_COLORS.equityReturn, 
      label: 'Equity Return',
      zIndex: 2,
    },
    'fi_return_annual': { 
      color: CHART_COLORS.fixedIncomeReturn, 
      label: 'Fixed Income Return',
      zIndex: 1,
    },
  };

  // ==========================================
  // CUSTOM TOOLTIP
  // ==========================================

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || payload.length === 0) return null;

    return (
      <div className="bg-surface-elevated border border-border rounded-lg shadow-xl p-4 min-w-[240px]">
        <div className="text-text-secondary text-xs font-medium mb-2 pb-2 border-b border-border">
          Parameter Shift: {formatters.variation(label)}
        </div>
        <div className="space-y-2">
          {payload.map((entry: any, index: number) => {
            const config = parameterConfig[entry.dataKey];
            if (!config) return null;
            
            return (
              <div key={index} className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: entry.color }}
                  />
                  <span className="text-text-primary text-sm font-medium">
                    {config.label}
                  </span>
                </div>
                <span className="text-text-primary text-sm font-semibold">
                  {formatters.percent(entry.value, 1)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // ==========================================
  // CUSTOM LEGEND
  // ==========================================

  const CustomLegend = ({ payload }: any) => {
    if (!payload || payload.length === 0) return null;

    return (
      <div className="flex flex-wrap items-center justify-center gap-6 px-4 py-3">
        {payload.map((entry: any, index: number) => {
          const config = parameterConfig[entry.dataKey];
          if (!config) return null;
          
          return (
            <div key={index} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-text-primary text-sm font-medium">
                {config.label}
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  // ==========================================
  // RENDER
  // ==========================================

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-text-tertiary">
        No sensitivity data available. Click "Analyze Sensitivity" to generate analysis.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Chart */}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart 
          data={chartData} 
          margin={{ top: 20, right: 40, left: 20, bottom: 70 }}
        >
          <defs>
            {/* Success band gradients */}
            <linearGradient id="strongGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={CHART_COLORS.successStrong} stopOpacity={0.05} />
              <stop offset="100%" stopColor={CHART_COLORS.successStrong} stopOpacity={0} />
            </linearGradient>
          </defs>
          
          {/* Grid */}
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke={CHART_COLORS.gridLines}
            opacity={0.5}
          />
          
          {/* X-Axis */}
          <XAxis
            dataKey="variation"
            tickFormatter={formatters.variation}
            stroke={CHART_COLORS.textSecondary}
            style={{ fontSize: '13px', fontWeight: 500 }}
            tick={{ fill: CHART_COLORS.textSecondary }}
            label={{
              value: 'Parameter Change from Baseline',
              position: 'insideBottom',
              offset: -50,
              fill: CHART_COLORS.textPrimary,
              style: { fontSize: '14px', fontWeight: 600 },
            }}
            axisLine={{ stroke: CHART_COLORS.textSecondary, strokeWidth: 1 }}
            tickLine={{ stroke: CHART_COLORS.textSecondary }}
          />
          
          {/* Y-Axis */}
          <YAxis
            tickFormatter={(value) => formatters.percent(value, 0)}
            stroke={CHART_COLORS.textSecondary}
            style={{ fontSize: '13px', fontWeight: 500 }}
            tick={{ fill: CHART_COLORS.textSecondary }}
            domain={[0, 1]}
            ticks={[0, 0.2, 0.4, 0.6, 0.8, 1.0]}
            label={{
              value: 'Success Probability',
              angle: -90,
              position: 'insideLeft',
              fill: CHART_COLORS.textPrimary,
              style: { fontSize: '14px', fontWeight: 600 },
            }}
            axisLine={{ stroke: CHART_COLORS.textSecondary, strokeWidth: 1 }}
            tickLine={{ stroke: CHART_COLORS.textSecondary }}
          />
          
          {/* Tooltip */}
          <Tooltip content={<CustomTooltip />} />
          
          {/* Legend */}
          <Legend 
            content={<CustomLegend />}
            wrapperStyle={{ paddingTop: '24px' }}
          />
          
          {/* Baseline Reference Line */}
          <ReferenceLine
            x={0}
            stroke={CHART_COLORS.baseline}
            strokeWidth={1.5}
            strokeDasharray="4 4"
            strokeOpacity={0.6}
          >
            <text
              x={0}
              y={15}
              textAnchor="middle"
              fill={CHART_COLORS.textPrimary}
              fontSize={12}
              fontWeight={600}
              style={{ 
                textShadow: '0 0 4px rgba(0,0,0,0.8)',
              }}
            >
              Baseline
            </text>
          </ReferenceLine>

          {/* Success Threshold Bands */}
          <ReferenceLine
            y={THRESHOLD_BANDS.strong.value}
            stroke={THRESHOLD_BANDS.strong.color}
            strokeWidth={1}
            strokeDasharray="4 4"
            strokeOpacity={0.25}
          >
            <text
              x="95%"
              y={THRESHOLD_BANDS.strong.value * height - 10}
              textAnchor="end"
              fill={THRESHOLD_BANDS.strong.color}
              fontSize={11}
              fontWeight={500}
              opacity={0.6}
            >
              {THRESHOLD_BANDS.strong.label}
            </text>
          </ReferenceLine>
          
          <ReferenceLine
            y={THRESHOLD_BANDS.adequate.value}
            stroke={THRESHOLD_BANDS.adequate.color}
            strokeWidth={1}
            strokeDasharray="4 4"
            strokeOpacity={0.25}
          >
            <text
              x="95%"
              y={THRESHOLD_BANDS.adequate.value * height + 20}
              textAnchor="end"
              fill={THRESHOLD_BANDS.adequate.color}
              fontSize={11}
              fontWeight={500}
              opacity={0.6}
            >
              {THRESHOLD_BANDS.adequate.label}
            </text>
          </ReferenceLine>

          {/* Lines for each parameter - ordered by z-index */}
          {parameters
            .sort((a, b) => {
              const zIndexA = parameterConfig[a]?.zIndex || 0;
              const zIndexB = parameterConfig[b]?.zIndex || 0;
              return zIndexA - zIndexB;
            })
            .map((param) => {
              const config = parameterConfig[param];
              if (!config) return null;
              
              return (
                <Line
                  key={param}
                  type="monotone"
                  dataKey={param}
                  stroke={config.color}
                  strokeWidth={3}
                  dot={{ 
                    fill: config.color, 
                    r: 4,
                    strokeWidth: 2,
                    stroke: '#1A1D24',
                  }}
                  activeDot={{ 
                    r: 7, 
                    strokeWidth: 3, 
                    stroke: CHART_COLORS.textPrimary,
                    fill: config.color,
                  }}
                  name={param}
                  connectNulls
                />
              );
            })
          }
        </ComposedChart>
      </ResponsiveContainer>

      {/* Insights Panel */}
      {insights.length > 0 && (
        <div className="bg-surface-elevated border border-border rounded-lg p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-lg bg-brand-primary/10 flex items-center justify-center">
              <svg
                className="w-5 h-5 text-brand-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-text-primary">
              Sensitivity Analysis Insights
            </h3>
          </div>
          <div className="grid gap-3">
            {insights.map((insight, index) => {
              // Extract parameter name to show colored indicator
              const paramMatch = insight.match(/^([^:]+):/);
              const paramName = paramMatch ? paramMatch[1].toLowerCase() : '';
              
              let indicatorColor = CHART_COLORS.textSecondary;
              if (paramName.includes('equity')) indicatorColor = CHART_COLORS.equityReturn;
              else if (paramName.includes('fixed') || paramName.includes('income')) indicatorColor = CHART_COLORS.fixedIncomeReturn;
              else if (paramName.includes('inflation')) indicatorColor = CHART_COLORS.inflationRate;
              else if (paramName.includes('spending')) indicatorColor = CHART_COLORS.monthlySpending;
              
              return (
                <div key={index} className="flex items-start gap-3 group">
                  <div 
                    className="w-1 h-6 rounded-full flex-shrink-0 mt-0.5"
                    style={{ backgroundColor: indicatorColor }}
                  />
                  <span className="text-text-secondary text-sm leading-relaxed group-hover:text-text-primary transition-colors">
                    {insight}
                  </span>
                </div>
              );
            })}
          </div>
          
          {/* Interpretation Guide */}
          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-text-tertiary text-xs leading-relaxed">
              <span className="font-semibold text-text-secondary">How to interpret:</span> Higher sensitivity indicates 
              greater impact on success probability. Parameters with wider ranges require more careful planning and 
              may benefit from conservative assumptions or risk mitigation strategies.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
