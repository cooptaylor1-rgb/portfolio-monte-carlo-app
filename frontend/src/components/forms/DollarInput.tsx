import React, { useState, useEffect } from 'react';

export interface DollarInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  help?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

export const DollarInput: React.FC<DollarInputProps> = ({
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
    <div className="mb-4">
      <label className="label">
        {label}
        {required && <span className="text-danger ml-1">*</span>}
      </label>
      <div className="relative">
        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary">$</span>
        <input
          type="text"
          value={displayValue}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={disabled}
          className={`input w-full pl-8 ${error ? 'border-danger' : ''}`}
        />
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
