/**
 * Alert Component - Contextual feedback messages
 * Part of the comprehensive design system
 * Supports success, warning, error, and info variants
 */
import React from 'react';
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export type AlertVariant = 'success' | 'warning' | 'error' | 'info';
export type AlertSize = 'sm' | 'md' | 'lg';

export interface AlertProps {
  /** Alert variant determining color scheme */
  variant: AlertVariant;
  /** Alert title */
  title?: string;
  /** Alert message content */
  children: React.ReactNode;
  /** Size variant */
  size?: AlertSize;
  /** Show icon */
  showIcon?: boolean;
  /** Allow dismissing alert */
  dismissible?: boolean;
  /** Callback when alert is dismissed */
  onDismiss?: () => void;
  /** Additional className */
  className?: string;
}

const variantConfig = {
  success: {
    icon: CheckCircle,
    bg: 'bg-status-success-base/10',
    border: 'border-status-success-base/30',
    text: 'text-status-success-base',
    title: 'text-status-success-light',
  },
  warning: {
    icon: AlertTriangle,
    bg: 'bg-status-warning-base/10',
    border: 'border-status-warning-base/30',
    text: 'text-status-warning-base',
    title: 'text-status-warning-light',
  },
  error: {
    icon: AlertCircle,
    bg: 'bg-status-error-base/10',
    border: 'border-status-error-base/30',
    text: 'text-status-error-base',
    title: 'text-status-error-light',
  },
  info: {
    icon: Info,
    bg: 'bg-status-info-base/10',
    border: 'border-status-info-base/30',
    text: 'text-status-info-base',
    title: 'text-status-info-light',
  },
};

const sizeConfig = {
  sm: {
    padding: 'p-3',
    iconSize: 16,
    titleText: 'text-small',
    bodyText: 'text-small',
  },
  md: {
    padding: 'p-4',
    iconSize: 20,
    titleText: 'text-body',
    bodyText: 'text-body',
  },
  lg: {
    padding: 'p-5',
    iconSize: 24,
    titleText: 'text-h4',
    bodyText: 'text-body',
  },
};

export const Alert: React.FC<AlertProps> = ({
  variant,
  title,
  children,
  size = 'md',
  showIcon = true,
  dismissible = false,
  onDismiss,
  className = '',
}) => {
  const config = variantConfig[variant];
  const sizeStyles = sizeConfig[size];
  const Icon = config.icon;

  return (
    <div
      className={`
        ${config.bg}
        ${config.border}
        ${sizeStyles.padding}
        border
        rounded-sm
        ${className}
      `}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {showIcon && (
          <div className={`${config.text} flex-shrink-0 mt-0.5`}>
            <Icon size={sizeStyles.iconSize} />
          </div>
        )}

        <div className="flex-1 min-w-0">
          {title && (
            <h4 className={`${config.title} ${sizeStyles.titleText} font-semibold mb-1`}>
              {title}
            </h4>
          )}
          <div className={`${config.text} ${sizeStyles.bodyText}`}>
            {children}
          </div>
        </div>

        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className={`
              ${config.text}
              flex-shrink-0
              hover:opacity-70
              transition-opacity
              focus:outline-none
              focus:ring-2
              focus:ring-accent-gold
              focus:ring-offset-2
              focus:ring-offset-background-base
              rounded-sm
              p-1
            `}
            aria-label="Dismiss alert"
          >
            <X size={16} />
          </button>
        )}
      </div>
    </div>
  );
};
