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

export const SensitivityHeatMap: React.FC<SensitivityHeatMapProps> = ({
  data,
  height = 500,
}) => {
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatVariation = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${(value * 100).toFixed(1)}%`;
  };

  // Transform data for line chart
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // Group by variation value
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

  // Get unique parameters
  const parameters = useMemo(() => {
    return Array.from(new Set(data.map(d => d.parameter)));
  }, [data]);

  // Calculate insights
  const insights = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    const results: string[] = [];
    const baselinePoint = data.find(d => Math.abs(d.variation) < 0.001);
    
    if (!baselinePoint) return results;
    
    parameters.forEach(param => {
      const paramData = data.filter(d => d.parameter === param);
      const minPoint = paramData.reduce((min, p) => p.successProbability < min.successProbability ? p : min);
      const maxPoint = paramData.reduce((max, p) => p.successProbability > max.successProbability ? p : max);
      const range = maxPoint.successProbability - minPoint.successProbability;
      
      const paramLabel = param.replace(/_/g, ' ').replace(/annual/g, '').trim();
      
      if (range > 0.20) {
        results.push(`${paramLabel}: Highly sensitive (${formatPercent(range)} range)`);
      } else if (range > 0.10) {
        results.push(`${paramLabel}: Moderately sensitive (${formatPercent(range)} range)`);
      } else {
        results.push(`${paramLabel}: Low sensitivity (${formatPercent(range)} range)`);
      }
    });
    
    return results;
  }, [data, parameters]);

  // Color scheme for different parameters
  const parameterColors: Record<string, string> = {
    'equity_return_annual': '#4CA6E8',
    'fi_return_annual': '#7AC18D',
    'inflation_annual': '#FFC107',
    'monthly_spending': '#D9534F',
  };

  const parameterLabels: Record<string, string> = {
    'equity_return_annual': 'Equity Return',
    'fi_return_annual': 'Fixed Income Return',
    'inflation_annual': 'Inflation Rate',
    'monthly_spending': 'Monthly Spending',
  };

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
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <defs>
            <linearGradient id="successGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4CAF50" stopOpacity={0.1} />
              <stop offset="100%" stopColor="#4CAF50" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#262A33" />
          <XAxis
            dataKey="variation"
            tickFormatter={formatVariation}
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
            label={{
              value: 'Parameter Change from Baseline',
              position: 'insideBottom',
              offset: -45,
              fill: '#9CA3AF',
              style: { fontSize: '13px' },
            }}
          />
          <YAxis
            tickFormatter={formatPercent}
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
            domain={['dataMin - 0.05', 'dataMax + 0.05']}
            label={{
              value: 'Success Probability',
              angle: -90,
              position: 'insideLeft',
              fill: '#9CA3AF',
              style: { fontSize: '13px' },
            }}
          />
          
          {/* Baseline reference line */}
          <ReferenceLine 
            x={0} 
            stroke="#B49759" 
            strokeDasharray="3 3" 
            strokeWidth={2}
            label={{ 
              value: 'Baseline', 
              position: 'top', 
              fill: '#B49759',
              fontSize: 12,
            }}
          />
          
          {/* Critical success thresholds */}
          <ReferenceLine 
            y={0.85} 
            stroke="#4CAF50" 
            strokeDasharray="2 2" 
            strokeOpacity={0.3}
            label={{ 
              value: 'Strong (85%)', 
              position: 'right', 
              fill: '#4CAF50',
              fontSize: 11,
            }}
          />
          <ReferenceLine 
            y={0.70} 
            stroke="#FFC107" 
            strokeDasharray="2 2" 
            strokeOpacity={0.3}
            label={{ 
              value: 'Adequate (70%)', 
              position: 'right', 
              fill: '#FFC107',
              fontSize: 11,
            }}
          />
          
          <Tooltip
            contentStyle={{
              backgroundColor: '#12141A',
              border: '1px solid #262A33',
              borderRadius: '8px',
              padding: '12px',
            }}
            labelStyle={{ color: '#E6E8EC', fontWeight: 600, marginBottom: '8px' }}
            formatter={(value: any, name: string) => {
              const label = parameterLabels[name] || name;
              return [formatPercent(value), label];
            }}
            labelFormatter={(value) => `Change: ${formatVariation(value)}`}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value) => parameterLabels[value] || value}
          />
          
          {/* Plot lines for each parameter */}
          {parameters.map((param, index) => (
            <Line
              key={param}
              type="monotone"
              dataKey={param}
              stroke={parameterColors[param] || '#94A3B8'}
              strokeWidth={3}
              dot={{ r: 5, strokeWidth: 2, fill: '#12141A' }}
              activeDot={{ r: 7 }}
              name={param}
            />
          ))}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Key Insights */}
      {insights.length > 0 && (
        <div className="bg-background-elevated border border-background-border rounded-lg p-5">
          <h4 className="text-h4 font-semibold text-text-primary mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-accent-gold" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Key Sensitivity Insights
          </h4>
          <div className="space-y-2">
            {insights.map((insight, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-accent-gold mt-2 flex-shrink-0" />
                <p className="text-body text-text-secondary">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Legend explanation */}
      <div className="bg-background-base bg-opacity-50 rounded-lg p-4 border border-background-border">
        <p className="text-small text-text-tertiary">
          <strong className="text-text-secondary">How to interpret:</strong> Steeper lines indicate greater sensitivity. 
          Parameters with flatter lines have less impact on success probability. Focus risk management efforts on 
          the most sensitive parameters (steepest lines).
        </p>
      </div>
    </div>
  );
};
