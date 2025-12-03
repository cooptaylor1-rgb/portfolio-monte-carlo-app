import React from 'react';

export interface SliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  formatValue?: (value: number) => string;
  help?: string;
  error?: string;
  disabled?: boolean;
}

export const Slider: React.FC<SliderProps> = ({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  formatValue = (v) => v.toString(),
  help,
  error,
  disabled = false,
}) => {
  return (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-2">
        <label className="label mb-0">{label}</label>
        <span className="text-primary-300 font-semibold">{formatValue(value)}</span>
      </div>
      <input
        type="range"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        className="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer slider"
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
