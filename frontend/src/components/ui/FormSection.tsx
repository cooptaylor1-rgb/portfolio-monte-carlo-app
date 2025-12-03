/**
 * FormSection Component - Collapsible form sections with visual hierarchy
 */
import React, { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

export interface FormSectionProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  defaultExpanded?: boolean;
  children: React.ReactNode;
  required?: boolean;
}

export const FormSection: React.FC<FormSectionProps> = ({
  title,
  description,
  icon,
  defaultExpanded = true,
  children,
  required = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="bg-background-elevated border border-background-border rounded-md overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-background-hover transition-colors"
      >
        <div className="flex items-center gap-3">
          {icon && (
            <div className="flex-shrink-0 text-accent-gold">
              {icon}
            </div>
          )}
          <div className="text-left">
            <h3 className="text-h4 font-display text-text-primary flex items-center gap-2">
              {title}
              {required && <span className="text-status-error-base text-small">*</span>}
            </h3>
            {description && (
              <p className="text-small text-text-tertiary mt-0.5">
                {description}
              </p>
            )}
          </div>
        </div>
        {isExpanded ? (
          <ChevronDown size={20} className="text-text-tertiary flex-shrink-0" />
        ) : (
          <ChevronRight size={20} className="text-text-tertiary flex-shrink-0" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-6 py-6 border-t border-background-border bg-background-base bg-opacity-30">
          {children}
        </div>
      )}
    </div>
  );
};
