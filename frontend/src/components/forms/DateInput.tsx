import React from 'react';

export interface DateInputProps {
  label: string;
  value: string; // ISO date string (YYYY-MM-DD)
  onChange: (value: string) => void;
  min?: string;
  max?: string;
  help?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

export const DateInput: React.FC<DateInputProps> = ({
  label,
  value,
  onChange,
  min,
  max,
  help,
  error,
  disabled = false,
  required = false,
}) => {
  return (
    <div className="mb-4">
      <label className="label">
        {label}
        {required && <span className="text-danger ml-1">*</span>}
      </label>
      <input
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        min={min}
        max={max}
        disabled={disabled}
        className={`input w-full ${error ? 'border-danger' : ''}`}
      />
      {help && !error && (
        <p className="text-text-muted text-sm mt-1">{help}</p>
      )}
      {error && (
        <p className="text-danger text-sm mt-1">{error}</p>
      )}
    </div>
  );
};
