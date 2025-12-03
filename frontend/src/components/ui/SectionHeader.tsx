/**
 * SectionHeader Component - Consistent section titles with descriptions
 */
import React from 'react';

export interface SectionHeaderProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  description,
  icon,
  actions,
  className = '',
}) => {
  return (
    <div className={`flex items-start justify-between gap-4 ${className}`}>
      <div className="flex items-start gap-3 flex-1">
        {icon && (
          <div className="flex-shrink-0 mt-1 text-accent-gold">
            {icon}
          </div>
        )}
        <div>
          <h2 className="text-h2 font-display font-semibold text-text-primary">
            {title}
          </h2>
          {description && (
            <p className="text-body text-text-secondary mt-1">
              {description}
            </p>
          )}
        </div>
      </div>
      {actions && (
        <div className="flex-shrink-0">
          {actions}
        </div>
      )}
    </div>
  );
};
