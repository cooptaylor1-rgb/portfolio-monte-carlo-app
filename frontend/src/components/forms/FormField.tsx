/**
 * FormField - Unified form field wrapper
 * Handles label, help text, errors, required indicator, and success states
 */

import React from 'react';
import { AlertCircle, Info, CheckCircle } from 'lucide-react';
import { colors } from '../../theme';

export interface FormFieldProps {
  label: string;
  help?: string;
  error?: string;
  success?: boolean;
  required?: boolean;
  optional?: boolean;
  children: React.ReactNode;
  id?: string;
  className?: string;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  help,
  error,
  success = false,
  required = false,
  optional = false,
  children,
  id,
  className = '',
}) => {
  const fieldId = id || `field-${label.toLowerCase().replace(/\s+/g, '-')}`;

  return (
    <div className={`mb-md ${className}`}>
      <label
        htmlFor={fieldId}
        className="block text-small font-medium text-text-primary mb-2"
      >
        {label}
        {required && (
          <span 
            className="ml-1" 
            style={{ color: colors.status.error.base }}
            aria-label="required"
          >
            *
          </span>
        )}
        {optional && !required && (
          <span className="text-text-tertiary ml-2 text-micro font-normal">
            (optional)
          </span>
        )}
        {success && !error && (
          <CheckCircle 
            size={16} 
            className="inline ml-2" 
            style={{ color: colors.status.success.base }}
            aria-label="valid"
          />
        )}
      </label>

      {help && !error && (
        <div className="flex items-start gap-2 mb-2 text-small text-text-tertiary">
          <Info size={16} className="flex-shrink-0 mt-0.5" />
          <p>{help}</p>
        </div>
      )}

      {React.cloneElement(children as React.ReactElement, {
        id: fieldId,
        'aria-invalid': !!error,
        'aria-describedby': error ? `${fieldId}-error` : help ? `${fieldId}-help` : undefined,
        className: `${(children as React.ReactElement).props.className || ''} ${
          error ? 'input-error' : ''
        }`,
      })}

      {error && (
        <div
          id={`${fieldId}-error`}
          className="flex items-start gap-2 mt-2 text-small"
          style={{ color: colors.status.error.base }}
          role="alert"
        >
          <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};
