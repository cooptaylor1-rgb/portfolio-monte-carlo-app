import React from 'react';

export interface NumberInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
  help?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

export const NumberInput: React.FC<NumberInputProps> = ({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  placeholder,
  help,
  error,
  disabled = false,
  required = false,
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
    <div className="mb-4">
      <label className="label">
        {label}
        {required && <span className="text-danger ml-1">*</span>}
      </label>
      <input
        type="number"
        value={value}
        onChange={handleChange}
        min={min}
        max={max}
        step={step}
        placeholder={placeholder}
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
