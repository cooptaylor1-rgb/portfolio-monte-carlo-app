import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { colors } from '../../theme';

interface SuccessGaugeProps {
  probability: number; // 0-1
  size?: number;
  animated?: boolean;
}

export const SuccessGauge: React.FC<SuccessGaugeProps> = ({
  probability,
  size = 200,
  animated = true,
}) => {
  const [displayValue, setDisplayValue] = useState(animated ? 0 : probability * 100);

  // Animate the gauge on mount
  useEffect(() => {
    if (!animated) return;
    
    const targetValue = probability * 100;
    const duration = 1500; // 1.5 seconds
    const startTime = Date.now();
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (ease-out)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      setDisplayValue(targetValue * easeOut);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [probability, animated]);

  // Guard against invalid probability
  if (probability === null || probability === undefined || isNaN(probability)) {
    return (
      <div 
        style={{ width: size, height: size, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        className="text-text-secondary"
      >
        No data
      </div>
    );
  }

  const percentage = displayValue;
  
  // Determine color based on success probability
  const getColor = () => {
    if (percentage >= 85) return colors.status.success.base;
    if (percentage >= 70) return colors.status.warning.base;
    return colors.status.error.base;
  };

  // Determine status message
  const getStatusMessage = () => {
    if (percentage >= 85) return 'Excellent';
    if (percentage >= 70) return 'Good';
    if (percentage >= 50) return 'Fair';
    return 'Needs Review';
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
            innerRadius="65%"
            outerRadius="85%"
            dataKey="value"
            strokeWidth={0}
            animationDuration={animated ? 1500 : 0}
            animationEasing="ease-out"
          >
            {data.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index]} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div 
          className="text-display font-display font-bold transition-colors duration-300" 
          style={{ color: getColor(), fontSize: `${size * 0.18}px` }}
        >
          {percentage.toFixed(1)}%
        </div>
        <div 
          className="text-small font-medium mt-2 transition-colors duration-300"
          style={{ color: getColor(), fontSize: `${size * 0.065}px` }}
        >
          {getStatusMessage()}
        </div>
      </div>
    </div>
  );
};
