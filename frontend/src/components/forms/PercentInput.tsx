import React, { useState, useEffect } from 'react';

export interface PercentInputProps {
  value: number; // Stored as decimal (0.05 = 5%)
  onChange: (value: number) => void;
  disabled?: boolean;
  className?: string;
}

export const PercentInput: React.FC<PercentInputProps> = ({
  value,
  onChange,
  disabled = false,
  className = '',
}) => {
  const [displayValue, setDisplayValue] = useState('');

  useEffect(() => {
    // Convert decimal to percentage for display
    setDisplayValue((value * 100).toFixed(2));
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/[^0-9.-]/g, '');
    setDisplayValue(raw);
    
    const parsed = parseFloat(raw);
    if (!isNaN(parsed)) {
      // Convert percentage to decimal
      onChange(parsed / 100);
    } else if (raw === '' || raw === '-') {
      onChange(0);
    }
  };

  const handleBlur = () => {
    // Re-format on blur
    setDisplayValue((value * 100).toFixed(2));
  };

  return (
    <div className="relative">
      <input
        type="text"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        disabled={disabled}
        className={`input w-full pr-8 ${className}`}
      />
      <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary z-10">%</span>
    </div>
  );
};
