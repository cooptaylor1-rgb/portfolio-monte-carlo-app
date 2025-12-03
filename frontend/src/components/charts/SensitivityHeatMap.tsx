import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface SensitivityHeatMapProps {
  data: Array<{
    parameter: string;
    variation: number;
    successProbability: number;
  }>;
  height?: number;
}

export const SensitivityHeatMap: React.FC<SensitivityHeatMapProps> = ({
  data,
  height = 400,
}) => {
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // Get color based on success probability
  const getColor = (probability: number) => {
    // Red to yellow to green gradient
    if (probability >= 0.85) return '#10b981'; // green
    if (probability >= 0.75) return '#34d399';
    if (probability >= 0.65) return '#fbbf24'; // yellow
    if (probability >= 0.55) return '#fb923c'; // orange
    return '#ef4444'; // red
  };

  // Group data by parameter
  const parameters = [...new Set(data.map((d) => d.parameter))];
  const variations = [...new Set(data.map((d) => d.variation))].sort((a, b) => a - b);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-end gap-4 text-sm">
        <span className="text-text-secondary">Success Probability:</span>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ef4444' }} />
          <span className="text-text-secondary">Low</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#fbbf24' }} />
          <span className="text-text-secondary">Medium</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#10b981' }} />
          <span className="text-text-secondary">High</span>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={height}>
        <ScatterChart margin={{ top: 20, right: 30, left: 100, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            type="number"
            dataKey="variation"
            name="Variation"
            tickFormatter={formatPercent}
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            label={{
              value: 'Parameter Variation',
              position: 'insideBottom',
              offset: -10,
              fill: '#94a3b8',
            }}
          />
          <YAxis
            type="category"
            dataKey="parameter"
            name="Parameter"
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            width={90}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            formatter={(value: any, name: string) => {
              if (name === 'successProbability') {
                return [formatPercent(value), 'Success Probability'];
              }
              return [value, name];
            }}
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#e2e8f0',
            }}
          />
          <Scatter data={data} shape="square">
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getColor(entry.successProbability)}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};
