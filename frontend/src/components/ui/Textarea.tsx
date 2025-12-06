/**
 * Textarea Component - Multi-line text input
 * Part of the comprehensive design system
 */
import React, { forwardRef } from 'react';
import { AlertCircle } from 'lucide-react';

export type TextareaSize = 'sm' | 'md' | 'lg';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  /** Textarea label */
  label?: string;
  /** Helper text displayed below textarea */
  helperText?: string;
  /** Error message - when present, textarea shows error state */
  error?: string;
  /** Size variant */
  size?: TextareaSize;
  /** Full width textarea */
  fullWidth?: boolean;
  /** Show character count */
  showCount?: boolean;
  /** Container className for wrapper div */
  containerClassName?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      label,
      helperText,
      error,
      size = 'md',
      fullWidth = false,
      showCount = false,
      disabled,
      className = '',
      containerClassName = '',
      id,
      maxLength,
      value,
      ...props
    },
    ref
  ) => {
    const textareaId = id || `textarea-${label?.toLowerCase().replace(/\s+/g, '-')}`;
    const hasError = Boolean(error);
    const currentLength = typeof value === 'string' ? value.length : 0;

    const sizeStyles = {
      sm: 'px-3 py-2 text-small min-h-[80px]',
      md: 'px-4 py-2.5 text-body min-h-[120px]',
      lg: 'px-5 py-3 text-h4 min-h-[160px]',
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
      resize-vertical
    `;

    const errorStyles = hasError
      ? 'border-status-error-base focus:ring-status-error-base focus:border-status-error-base'
      : 'border-background-border hover:border-background-border/80';

    return (
      <div className={`${fullWidth ? 'w-full' : ''} ${containerClassName}`}>
        <div className="flex items-center justify-between mb-1.5">
          {label && (
            <label
              htmlFor={textareaId}
              className="block text-small font-medium text-text-secondary"
            >
              {label}
              {props.required && <span className="text-status-error-base ml-1">*</span>}
            </label>
          )}
          {showCount && maxLength && (
            <span className="text-micro text-text-tertiary">
              {currentLength} / {maxLength}
            </span>
          )}
        </div>

        <div className="relative">
          <textarea
            ref={ref}
            id={textareaId}
            disabled={disabled}
            maxLength={maxLength}
            value={value}
            className={`
              ${baseStyles}
              ${sizeStyles[size]}
              ${errorStyles}
              ${className}
            `}
            aria-invalid={hasError}
            aria-describedby={
              error
                ? `${textareaId}-error`
                : helperText
                ? `${textareaId}-helper`
                : undefined
            }
            {...props}
          />

          {hasError && (
            <div className="absolute right-3 top-3 text-status-error-base">
              <AlertCircle size={18} />
            </div>
          )}
        </div>

        {error && (
          <p
            id={`${textareaId}-error`}
            className="mt-1.5 text-small text-status-error-base flex items-center gap-1"
            role="alert"
          >
            {error}
          </p>
        )}

        {helperText && !error && (
          <p id={`${textareaId}-helper`} className="mt-1.5 text-small text-text-tertiary">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
