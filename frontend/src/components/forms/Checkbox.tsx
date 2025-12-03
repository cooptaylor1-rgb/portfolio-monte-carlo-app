import React from 'react';

export interface CheckboxProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  help?: string;
  disabled?: boolean;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  label,
  checked,
  onChange,
  help,
  disabled = false,
}) => {
  return (
    <div className="mb-4">
      <label className="flex items-center cursor-pointer">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="w-5 h-5 text-brand-gold bg-surface-700 border-surface-600 rounded focus:ring-brand-gold focus:ring-2"
        />
        <span className="ml-2 text-text-primary">{label}</span>
      </label>
      {help && (
        <p className="text-text-muted text-sm mt-1 ml-7">{help}</p>
      )}
    </div>
  );
};
