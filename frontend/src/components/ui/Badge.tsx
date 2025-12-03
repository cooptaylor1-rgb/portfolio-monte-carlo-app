/**
 * Badge Component - Small status or label indicators
 */
import React from 'react';

export type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info';
export type BadgeSize = 'sm' | 'md';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}) => {
  const baseStyles = 'inline-flex items-center font-medium rounded-full';
  
  const variantStyles = {
    default: 'bg-background-border text-text-secondary',
    success: 'bg-status-success-dark bg-opacity-20 text-status-success-light',
    warning: 'bg-status-warning-dark bg-opacity-20 text-status-warning-light',
    error: 'bg-status-error-dark bg-opacity-20 text-status-error-light',
    info: 'bg-status-info-dark bg-opacity-20 text-status-info-light',
  };
  
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-micro',
    md: 'px-3 py-1 text-small',
  };
  
  return (
    <span className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}>
      {children}
    </span>
  );
};
