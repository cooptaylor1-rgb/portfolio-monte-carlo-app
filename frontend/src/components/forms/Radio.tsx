import React from 'react';

export interface RadioOption {
  value: string | number;
  label: string;
}

export interface RadioProps {
  label: string;
  options: RadioOption[];
  value: string | number;
  onChange: (value: string | number) => void;
  help?: string;
  disabled?: boolean;
}

export const Radio: React.FC<RadioProps> = ({
  label,
  options,
  value,
  onChange,
  help,
  disabled = false,
}) => {
  return (
    <div className="mb-4">
      <label className="label mb-2">{label}</label>
      <div className="space-y-2">
        {options.map((option) => (
          <label key={option.value} className="flex items-center cursor-pointer">
            <input
              type="radio"
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              disabled={disabled}
              className="w-4 h-4 text-brand-gold bg-surface-700 border-surface-600 focus:ring-brand-gold focus:ring-2"
            />
            <span className="ml-2 text-text-primary">{option.label}</span>
          </label>
        ))}
      </div>
      {help && (
        <p className="text-text-muted text-sm mt-1">{help}</p>
      )}
    </div>
  );
};
