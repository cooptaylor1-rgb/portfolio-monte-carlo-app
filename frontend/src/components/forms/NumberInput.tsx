import React from 'react';

export interface NumberInputProps {
  label?: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  help?: string;
  error?: string;
  className?: string;
}

export const NumberInput: React.FC<NumberInputProps> = ({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  placeholder,
  disabled = false,
  required = false,
  help,
  error,
  className = '',
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    if (!isNaN(val)) {
      onChange(val);
    } else if (e.target.value === '') {
      onChange(0);
    }
  };

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-text-secondary mb-1">
          {label}
          {required && <span className="text-status-error-base ml-1">*</span>}
        </label>
      )}
      <input
        type="number"
        value={value}
        onChange={handleChange}
        min={min}
        max={max}
        step={step}
        placeholder={placeholder}
        disabled={disabled}
        className={`input w-full ${error ? 'border-status-error-base' : ''} ${className}`}
      />
      {help && !error && (
        <p className="text-xs text-text-tertiary mt-1">{help}</p>
      )}
      {error && (
        <p className="text-xs text-status-error-base mt-1">{error}</p>
      )}
    </div>
  );
};
