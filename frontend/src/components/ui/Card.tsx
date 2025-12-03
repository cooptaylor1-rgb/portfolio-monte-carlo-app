/**
 * Card Component - Container for content grouping
 * Follows design system specifications
 */
import React from 'react';

export type CardVariant = 'default' | 'interactive' | 'highlighted';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  padding = 'lg',
  className = '',
  children,
  ...props
}) => {
  const baseStyles = 'bg-background-elevated rounded-md transition-all duration-default';
  
  const variantStyles = {
    default: 'border border-background-border shadow-sm',
    interactive: 'border border-background-border shadow-sm hover:border-accent-gold hover:shadow-md cursor-pointer',
    highlighted: 'border-2 border-accent-gold shadow-glow',
  };
  
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-lg',
  };
  
  return (
    <div
      className={`${baseStyles} ${variantStyles[variant]} ${paddingStyles[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
