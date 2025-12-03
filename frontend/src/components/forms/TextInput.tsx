import React from 'react';

export interface TextInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  help?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

export const TextInput: React.FC<TextInputProps> = ({
  label,
  value,
  onChange,
  placeholder,
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
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
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
