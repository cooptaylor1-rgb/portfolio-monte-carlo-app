/**
 * Button Component - Primary UI element for actions
 * Follows design system specifications
 */
import React from 'react';
import { Loader2 } from 'lucide-react';

export type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  fullWidth = false,
  disabled,
  className = '',
  children,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center gap-2 font-semibold rounded-sm transition-all duration-fast focus:outline-none focus:ring-2 focus:ring-accent-gold focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantStyles = {
    primary: 'bg-accent-gold text-text-primary hover:bg-accent-gold-light active:bg-accent-gold-dark shadow-sm hover:shadow-md',
    secondary: 'bg-transparent border border-accent-gold text-accent-gold hover:bg-background-hover active:bg-background-border',
    tertiary: 'bg-background-hover text-text-secondary hover:bg-background-border hover:text-text-primary',
    danger: 'bg-status-error-base text-text-primary hover:bg-status-error-dark active:bg-status-error-dark shadow-sm',
  };
  
  const sizeStyles = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-6 py-3 text-body',
    lg: 'px-8 py-4 text-h4',
  };
  
  const widthStyles = fullWidth ? 'w-full' : '';
  
  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${widthStyles} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="animate-spin" size={size === 'sm' ? 16 : 20} />
      ) : icon ? (
        <span className="flex-shrink-0">{icon}</span>
      ) : null}
      {children}
    </button>
  );
};
