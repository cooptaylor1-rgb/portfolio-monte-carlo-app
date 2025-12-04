/**
 * FormField - Unified form field wrapper component
 * Provides consistent label, help text, error messages, and required indicators
 * 
 * Features:
 * - Automatic label/input association
 * - Required indicator (*)
 * - Optional indicator
 * - Help text with icon
 * - Error messages with icon
 * - Success state (green checkmark)
 * - Proper ARIA attributes
 * - Accessible error announcements
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
  labelClassName?: string;
  helpClassName?: string;
  errorClassName?: string;
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
  labelClassName = '',
  helpClassName = '',
  errorClassName = '',
}) => {
  const fieldId = id || `field-${label.toLowerCase().replace(/\s+/g, '-')}`;
  const helpId = `${fieldId}-help`;
  const errorId = `${fieldId}-error`;

  return (
    <div className={`mb-md ${className}`}>
      {/* Label with required/optional indicator */}
      <div className="flex items-center justify-between mb-2">
        <label
          htmlFor={fieldId}
          className={`block text-sm font-medium text-text-primary ${labelClassName}`}
        >
          {label}
          {required && (
            <span 
              className="ml-1 text-status-error-base" 
              aria-label="required"
              style={{ color: colors.status.error.base }}
            >
              *
            </span>
          )}
          {optional && !required && (
            <span className="ml-2 text-xs font-normal text-text-tertiary">
              (optional)
            </span>
          )}
        </label>
        
        {/* Success indicator */}
        {success && !error && (
          <CheckCircle 
            size={16} 
            className="text-status-success-base" 
            style={{ color: colors.status.success.base }}
            aria-label="valid"
          />
        )}
      </div>

      {/* Help text */}
      {help && !error && (
        <div 
          id={helpId}
          className={`flex items-start gap-2 mb-2 text-sm text-text-tertiary ${helpClassName}`}
        >
          <Info size={16} className="flex-shrink-0 mt-0.5" />
          <p>{help}</p>
        </div>
      )}

      {/* Input/children with enhanced props */}
      {React.cloneElement(children as React.ReactElement, {
        id: fieldId,
        'aria-invalid': !!error,
        'aria-describedby': error ? errorId : help ? helpId : undefined,
        'aria-required': required,
      })}

      {/* Error message */}
      {error && (
        <div
          id={errorId}
          className={`flex items-start gap-2 mt-2 text-sm ${errorClassName}`}
          style={{ color: colors.status.error.base }}
          role="alert"
          aria-live="polite"
        >
          <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

// Helper component for form sections
export const FormSection: React.FC<{
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}> = ({ title, description, children, className = '' }) => (
  <div className={`mb-xl ${className}`}>
    <div className="mb-lg">
      <h3 className="text-h3 font-semibold text-text-primary mb-2">{title}</h3>
      {description && (
        <p className="text-body text-text-tertiary">{description}</p>
      )}
    </div>
    <div className="space-y-md">
      {children}
    </div>
  </div>
);

// Helper component for form groups (inline fields)
export const FormGroup: React.FC<{
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4;
  className?: string;
}> = ({ children, columns = 2, className = '' }) => {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div className={`grid ${gridCols[columns]} gap-md ${className}`}>
      {children}
    </div>
  );
};

export default FormField;
