/**
 * EmptyState Component - User-friendly empty state with guidance
 */
import React from 'react';
import { Button, ButtonProps } from './Button';

export interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: ButtonProps['variant'];
  };
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center text-center py-12 px-6 ${className}`}>
      <div className="text-text-tertiary mb-4">
        {icon}
      </div>
      <h3 className="text-h3 font-display text-text-primary mb-2">
        {title}
      </h3>
      <p className="text-body text-text-secondary max-w-md mb-6">
        {description}
      </p>
      {action && (
        <Button
          variant={action.variant || 'primary'}
          onClick={action.onClick}
        >
          {action.label}
        </Button>
      )}
    </div>
  );
};
