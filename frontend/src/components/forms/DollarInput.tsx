import React, { useState, useEffect } from 'react';

export interface DollarInputProps {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
  className?: string;
}

export const DollarInput: React.FC<DollarInputProps> = ({
  value,
  onChange,
  disabled = false,
  className = '',
}) => {
  const [displayValue, setDisplayValue] = useState('');

  useEffect(() => {
    // Format number as currency without $ sign
    setDisplayValue(Math.abs(value).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 }));
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/[^0-9.-]/g, '');
    setDisplayValue(raw);
    
    const parsed = parseFloat(raw);
    if (!isNaN(parsed)) {
      onChange(parsed);
    } else if (raw === '' || raw === '-') {
      onChange(0);
    }
  };

  const handleBlur = () => {
    // Re-format on blur
    setDisplayValue(Math.abs(value).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 }));
  };

  return (
    <div className="relative">
      <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary z-10">$</span>
      <input
        type="text"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        disabled={disabled}
        className={`input w-full pl-8 ${className}`}
      />
    </div>
  );
};
