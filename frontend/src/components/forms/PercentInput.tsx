import React, { useState, useEffect } from 'react';

export interface PercentInputProps {
  label: string;
  value: number; // Stored as decimal (0.05 = 5%)
  onChange: (value: number) => void;
  help?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

export const PercentInput: React.FC<PercentInputProps> = ({
  label,
  value,
  onChange,
  help,
  error,
  disabled = false,
  required = false,
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
    <div className="mb-4">
      <label className="label">
        {label}
        {required && <span className="text-danger ml-1">*</span>}
      </label>
      <div className="relative">
        <input
          type="text"
          value={displayValue}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={disabled}
          className={`input w-full pr-8 ${error ? 'border-danger' : ''}`}
        />
        <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary">%</span>
      </div>
      {help && !error && (
        <p className="text-text-muted text-sm mt-1">{help}</p>
      )}
      {error && (
        <p className="text-danger text-sm mt-1">{error}</p>
      )}
    </div>
  );
};
