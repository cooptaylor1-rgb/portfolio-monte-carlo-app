import React from 'react';

export interface SelectOption {
  value: string | number;
  label: string;
}

export interface SelectBoxProps {
  label: string;
  options: SelectOption[];
  value: string | number;
  onChange: (value: string | number) => void;
  placeholder?: string;
  help?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

export const SelectBox: React.FC<SelectBoxProps> = ({
  label,
  options,
  value,
  onChange,
  placeholder = 'Select an option',
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
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={`input w-full ${error ? 'border-danger' : ''}`}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {help && !error && (
        <p className="text-text-muted text-sm mt-1">{help}</p>
      )}
      {error && (
        <p className="text-danger text-sm mt-1">{error}</p>
      )}
    </div>
  );
};
