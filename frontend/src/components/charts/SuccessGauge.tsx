import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { colors } from '../../theme';

interface SuccessGaugeProps {
  probability: number; // 0-1
  size?: number;
}

export const SuccessGauge: React.FC<SuccessGaugeProps> = ({
  probability,
  size = 200,
}) => {
  const percentage = probability * 100;
  
  // Determine color based on success probability
  const getColor = () => {
    if (percentage >= 85) return colors.status.success.base;
    if (percentage >= 70) return colors.status.warning.base;
    return colors.status.error.base;
  };

  const data = [
    { name: 'Success', value: percentage },
    { name: 'Remaining', value: 100 - percentage },
  ];

  const COLORS = [getColor(), colors.background.border];

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            startAngle={180}
            endAngle={0}
            innerRadius="60%"
            outerRadius="80%"
            dataKey="value"
            strokeWidth={0}
          >
            {data.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index]} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-display font-display" style={{ color: getColor() }}>
          {percentage.toFixed(1)}%
        </div>
        <div className="text-small text-text-secondary mt-1">Success Rate</div>
      </div>
    </div>
  );
};
