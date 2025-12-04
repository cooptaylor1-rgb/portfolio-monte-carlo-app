/**
 * Reusable UI Components for Analysis Sections
 * Dark theme, pro-grade financial UI
 */

import React from 'react';
import { salemColors } from '../visualizations/chartUtils';

interface EmptyStateProps {
  title: string;
  message: string;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title, message, icon }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6">
      <div 
        className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
        style={{ backgroundColor: `${salemColors.gold}15` }}
      >
        {icon || (
          <svg className="w-8 h-8" style={{ color: salemColors.gold }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        )}
      </div>
      <h3 className="text-lg font-semibold mb-2" style={{ color: salemColors.white }}>
        {title}
      </h3>
      <p className="text-sm text-center max-w-md" style={{ color: salemColors.mediumGray }}>
        {message}
      </p>
    </div>
  );
};

interface SummaryCardProps {
  label: string;
  value: string;
  sublabel?: string;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  className?: string;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({ 
  label, 
  value, 
  sublabel, 
  variant = 'default',
  className = '' 
}) => {
  const variantStyles = {
    default: {
      bg: 'rgba(30, 41, 59, 0.5)',
      border: 'rgba(71, 85, 105, 0.3)',
      labelColor: salemColors.mediumGray,
      valueColor: salemColors.white,
    },
    primary: {
      bg: `${salemColors.gold}10`,
      border: `${salemColors.gold}30`,
      labelColor: salemColors.gold,
      valueColor: salemColors.gold,
    },
    success: {
      bg: `${salemColors.success}10`,
      border: `${salemColors.success}30`,
      labelColor: salemColors.success,
      valueColor: salemColors.success,
    },
    warning: {
      bg: `${salemColors.warning}10`,
      border: `${salemColors.warning}30`,
      labelColor: salemColors.warning,
      valueColor: salemColors.warning,
    },
    danger: {
      bg: `${salemColors.danger}10`,
      border: `${salemColors.danger}30`,
      labelColor: salemColors.danger,
      valueColor: salemColors.danger,
    },
  };

  const style = variantStyles[variant];

  return (
    <div 
      className={`rounded-lg p-4 border ${className}`}
      style={{ 
        backgroundColor: style.bg,
        borderColor: style.border,
      }}
    >
      <div className="text-xs font-medium uppercase tracking-wide mb-1.5" style={{ color: style.labelColor }}>
        {label}
      </div>
      <div className="text-xl font-semibold mb-0.5" style={{ color: style.valueColor }}>
        {value}
      </div>
      {sublabel && (
        <div className="text-xs" style={{ color: salemColors.mediumGray }}>
          {sublabel}
        </div>
      )}
    </div>
  );
};

interface RiskBadgeProps {
  level: 'Low' | 'Moderate' | 'High' | 'Very High';
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'md' }) => {
  const colors = {
    'Low': salemColors.success,
    'Moderate': salemColors.warning,
    'High': salemColors.danger,
    'Very High': '#DC2626',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-3 py-1 text-xs',
    lg: 'px-4 py-1.5 text-sm',
  };

  return (
    <span 
      className={`inline-flex items-center rounded font-semibold uppercase tracking-wide ${sizes[size]}`}
      style={{ 
        backgroundColor: colors[level],
        color: '#FFFFFF',
      }}
    >
      {level}
    </span>
  );
};

interface AnalysisSectionProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  className?: string;
}

export const AnalysisSection: React.FC<AnalysisSectionProps> = ({ 
  title, 
  subtitle, 
  children, 
  className = '' 
}) => {
  return (
    <div 
      className={`rounded-xl border shadow-lg ${className}`}
      style={{
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        borderColor: 'rgba(71, 85, 105, 0.3)',
      }}
    >
      <div className="border-b px-6 py-4" style={{ borderColor: 'rgba(71, 85, 105, 0.2)' }}>
        <h3 className="text-lg font-semibold mb-1" style={{ color: salemColors.gold }}>
          {title}
        </h3>
        <p className="text-sm" style={{ color: salemColors.mediumGray }}>
          {subtitle}
        </p>
      </div>
      <div className="p-6">
        {children}
      </div>
    </div>
  );
};

interface AssessmentCalloutProps {
  title: string;
  message: string;
  variant: 'success' | 'warning' | 'danger' | 'info';
  icon?: React.ReactNode;
}

export const AssessmentCallout: React.FC<AssessmentCalloutProps> = ({ 
  title, 
  message, 
  variant,
  icon 
}) => {
  const variantStyles = {
    success: {
      bg: `${salemColors.success}08`,
      border: salemColors.success,
      color: salemColors.success,
    },
    warning: {
      bg: `${salemColors.warning}08`,
      border: salemColors.warning,
      color: salemColors.warning,
    },
    danger: {
      bg: `${salemColors.danger}08`,
      border: salemColors.danger,
      color: salemColors.danger,
    },
    info: {
      bg: `${salemColors.info}08`,
      border: salemColors.info,
      color: salemColors.info,
    },
  };

  const style = variantStyles[variant];

  return (
    <div 
      className="rounded-lg p-4 border-l-4"
      style={{ 
        backgroundColor: style.bg,
        borderLeftColor: style.border,
      }}
    >
      <div className="flex items-start gap-3">
        {icon && (
          <div className="flex-shrink-0 mt-0.5" style={{ color: style.color }}>
            {icon}
          </div>
        )}
        <div className="flex-1">
          <div className="font-semibold text-sm mb-1" style={{ color: style.color }}>
            {title}
          </div>
          <div className="text-sm leading-relaxed" style={{ color: salemColors.white }}>
            {message}
          </div>
        </div>
      </div>
    </div>
  );
};
