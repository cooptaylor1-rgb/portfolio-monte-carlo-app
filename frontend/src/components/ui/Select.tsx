/**
 * Select Component - Dropdown selection input
 * Part of the comprehensive design system
 * Replaces raw <select> usage throughout the app
 */
import React, { forwardRef } from 'react';
import { ChevronDown, AlertCircle } from 'lucide-react';

export type SelectSize = 'sm' | 'md' | 'lg';

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  /** Select label */
  label?: string;
  /** Helper text displayed below select */
  helperText?: string;
  /** Error message - when present, select shows error state */
  error?: string;
  /** Size variant */
  size?: SelectSize;
  /** Full width select */
  fullWidth?: boolean;
  /** Options array */
  options: SelectOption[];
  /** Placeholder text */
  placeholder?: string;
  /** Container className for wrapper div */
  containerClassName?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      label,
      helperText,
      error,
      size = 'md',
      fullWidth = false,
      options,
      placeholder,
      disabled,
      className = '',
      containerClassName = '',
      id,
      ...props
    },
    ref
  ) => {
    const selectId = id || `select-${label?.toLowerCase().replace(/\s+/g, '-')}`;
    const hasError = Boolean(error);

    const sizeStyles = {
      sm: 'px-3 py-1.5 text-small',
      md: 'px-4 py-2.5 text-body',
      lg: 'px-5 py-3 text-h4',
    };

    const baseStyles = `
      w-full
      bg-background-elevated
      border
      rounded-sm
      text-text-primary
      transition-all
      duration-default
      focus:outline-none
      focus:ring-2
      focus:ring-accent-gold
      focus:border-accent-gold
      disabled:opacity-50
      disabled:cursor-not-allowed
      disabled:bg-background-base
      appearance-none
      pr-10
      cursor-pointer
    `;

    const errorStyles = hasError
      ? 'border-status-error-base focus:ring-status-error-base focus:border-status-error-base'
      : 'border-background-border hover:border-background-border/80';

    return (
      <div className={`${fullWidth ? 'w-full' : ''} ${containerClassName}`}>
        {label && (
          <label
            htmlFor={selectId}
            className="block text-small font-medium text-text-secondary mb-1.5"
          >
            {label}
            {props.required && <span className="text-status-error-base ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          <select
            ref={ref}
            id={selectId}
            disabled={disabled}
            className={`
              ${baseStyles}
              ${sizeStyles[size]}
              ${errorStyles}
              ${className}
            `}
            aria-invalid={hasError}
            aria-describedby={
              error
                ? `${selectId}-error`
                : helperText
                ? `${selectId}-helper`
                : undefined
            }
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option
                key={option.value}
                value={option.value}
                disabled={option.disabled}
              >
                {option.label}
              </option>
            ))}
          </select>

          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            {hasError ? (
              <AlertCircle size={18} className="text-status-error-base" />
            ) : (
              <ChevronDown size={18} className="text-text-tertiary" />
            )}
          </div>
        </div>

        {error && (
          <p
            id={`${selectId}-error`}
            className="mt-1.5 text-small text-status-error-base flex items-center gap-1"
            role="alert"
          >
            {error}
          </p>
        )}

        {helperText && !error && (
          <p id={`${selectId}-helper`} className="mt-1.5 text-small text-text-tertiary">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';
