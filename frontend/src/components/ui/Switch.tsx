/**
 * Switch Component - Toggle switch for boolean values
 * Part of the comprehensive design system
 * WCAG AA compliant with keyboard support
 */
import React, { forwardRef } from 'react';

export type SwitchSize = 'sm' | 'md' | 'lg';

export interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  /** Switch label */
  label?: string;
  /** Helper text displayed below switch */
  helperText?: string;
  /** Size variant */
  size?: SwitchSize;
  /** Label position */
  labelPosition?: 'left' | 'right';
  /** Container className */
  containerClassName?: string;
}

export const Switch = forwardRef<HTMLInputElement, SwitchProps>(
  (
    {
      label,
      helperText,
      size = 'md',
      labelPosition = 'right',
      disabled,
      checked,
      className = '',
      containerClassName = '',
      id,
      ...props
    },
    ref
  ) => {
    const switchId = id || `switch-${label?.toLowerCase().replace(/\s+/g, '-')}`;

    const sizeStyles = {
      sm: {
        track: 'w-9 h-5',
        thumb: 'w-3.5 h-3.5',
        translate: 'translate-x-4',
      },
      md: {
        track: 'w-11 h-6',
        thumb: 'w-4 h-4',
        translate: 'translate-x-5',
      },
      lg: {
        track: 'w-14 h-7',
        thumb: 'w-5 h-5',
        translate: 'translate-x-7',
      },
    };

    const currentSize = sizeStyles[size];

    return (
      <div className={`flex items-start ${containerClassName}`}>
        {label && labelPosition === 'left' && (
          <label
            htmlFor={switchId}
            className="mr-3 text-body font-medium text-text-primary cursor-pointer select-none"
          >
            {label}
          </label>
        )}

        <div className="flex flex-col">
          <div className="relative inline-flex items-center">
            <input
              ref={ref}
              type="checkbox"
              id={switchId}
              checked={checked}
              disabled={disabled}
              className="sr-only peer"
              aria-describedby={helperText ? `${switchId}-helper` : undefined}
              {...props}
            />
            <div
              className={`
                ${currentSize.track}
                bg-background-border
                peer-checked:bg-accent-gold
                peer-focus:ring-2
                peer-focus:ring-accent-gold
                peer-focus:ring-offset-2
                peer-focus:ring-offset-background-base
                rounded-full
                transition-colors
                duration-default
                cursor-pointer
                peer-disabled:opacity-50
                peer-disabled:cursor-not-allowed
                ${className}
              `}
            >
              <div
                className={`
                  ${currentSize.thumb}
                  bg-white
                  rounded-full
                  shadow-md
                  transform
                  transition-transform
                  duration-default
                  translate-x-1
                  ${checked ? currentSize.translate : 'translate-x-1'}
                `}
              />
            </div>
          </div>

          {helperText && (
            <p id={`${switchId}-helper`} className="mt-1.5 text-small text-text-tertiary">
              {helperText}
            </p>
          )}
        </div>

        {label && labelPosition === 'right' && (
          <label
            htmlFor={switchId}
            className="ml-3 text-body font-medium text-text-primary cursor-pointer select-none"
          >
            {label}
          </label>
        )}
      </div>
    );
  }
);

Switch.displayName = 'Switch';
