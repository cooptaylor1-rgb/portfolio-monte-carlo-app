/**
 * Input Component - Text, number, email, and other input types
 * Part of the comprehensive design system
 * Replaces raw <input> usage throughout the app
 */
import React, { forwardRef } from 'react';
import { AlertCircle } from 'lucide-react';

export type InputType = 'text' | 'number' | 'email' | 'password' | 'tel' | 'url' | 'search';
export type InputSize = 'sm' | 'md' | 'lg';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Input label */
  label?: string;
  /** Helper text displayed below input */
  helperText?: string;
  /** Error message - when present, input shows error state */
  error?: string;
  /** Input type */
  type?: InputType;
  /** Size variant */
  size?: InputSize;
  /** Full width input */
  fullWidth?: boolean;
  /** Optional icon to display on the left */
  leftIcon?: React.ReactNode;
  /** Optional icon to display on the right */
  rightIcon?: React.ReactNode;
  /** Container className for wrapper div */
  containerClassName?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      helperText,
      error,
      type = 'text',
      size = 'md',
      fullWidth = false,
      leftIcon,
      rightIcon,
      disabled,
      className = '',
      containerClassName = '',
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${label?.toLowerCase().replace(/\s+/g, '-')}`;
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
      placeholder-text-tertiary
      transition-all
      duration-default
      focus:outline-none
      focus:ring-2
      focus:ring-accent-gold
      focus:border-accent-gold
      disabled:opacity-50
      disabled:cursor-not-allowed
      disabled:bg-background-base
    `;

    const errorStyles = hasError
      ? 'border-status-error-base focus:ring-status-error-base focus:border-status-error-base'
      : 'border-background-border hover:border-background-border/80';

    const iconPaddingStyles = leftIcon ? 'pl-10' : rightIcon ? 'pr-10' : '';

    return (
      <div className={`${fullWidth ? 'w-full' : ''} ${containerClassName}`}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-small font-medium text-text-secondary mb-1.5"
          >
            {label}
            {props.required && <span className="text-status-error-base ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary pointer-events-none">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            type={type}
            id={inputId}
            disabled={disabled}
            className={`
              ${baseStyles}
              ${sizeStyles[size]}
              ${errorStyles}
              ${iconPaddingStyles}
              ${className}
            `}
            aria-invalid={hasError}
            aria-describedby={
              error
                ? `${inputId}-error`
                : helperText
                ? `${inputId}-helper`
                : undefined
            }
            {...props}
          />

          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary pointer-events-none">
              {rightIcon}
            </div>
          )}

          {hasError && !rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-status-error-base">
              <AlertCircle size={18} />
            </div>
          )}
        </div>

        {error && (
          <p
            id={`${inputId}-error`}
            className="mt-1.5 text-small text-status-error-base flex items-center gap-1"
            role="alert"
          >
            {error}
          </p>
        )}

        {helperText && !error && (
          <p id={`${inputId}-helper`} className="mt-1.5 text-small text-text-tertiary">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
