import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export interface ExpanderProps {
  title: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  icon?: React.ReactNode;
}

export const Expander: React.FC<ExpanderProps> = ({
  title,
  children,
  defaultExpanded = false,
  icon,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="mb-4 bg-surface-700 rounded-lg border border-surface-600 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-surface-600 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="font-semibold text-primary-500">{title}</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-text-secondary" />
        ) : (
          <ChevronDown className="w-5 h-5 text-text-secondary" />
        )}
      </button>
      {isExpanded && (
        <div className="p-4 bg-surface-800 border-t border-surface-600">
          {children}
        </div>
      )}
    </div>
  );
};
