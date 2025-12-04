/**
 * Analytics Page Template
 * Reusable template for analytics and dashboard pages
 * Provides consistent structure, navigation, and export functionality
 * 
 * @example
 * ```tsx
 * <AnalyticsPageTemplate
 *   title="Monte Carlo Analytics"
 *   description="Comprehensive portfolio analysis"
 *   icon={<BarChart3 />}
 *   sections={[
 *     { id: 'overview', label: 'Overview' },
 *     { id: 'details', label: 'Details' }
 *   ]}
 *   activeSection={activeSection}
 *   onSectionChange={setActiveSection}
 *   exportActions={[
 *     { label: 'Export PDF', onClick: handlePDF, icon: <FileText /> },
 *   ]}
 * >
 *   {Your content here}
 * </AnalyticsPageTemplate>
 * ```
 */

import React, { ReactNode } from 'react';
import { SectionHeader, Button, Card } from '../ui';
import { LucideIcon } from 'lucide-react';

export interface AnalyticsSection {
  id: string;
  label: string;
  icon?: ReactNode;
}

export interface ExportAction {
  label: string;
  onClick: () => void;
  icon?: ReactNode;
  variant?: 'primary' | 'secondary' | 'tertiary';
  loading?: boolean;
  disabled?: boolean;
}

export interface AnalyticsPageTemplateProps {
  // Header configuration
  title: string;
  description?: string;
  icon?: ReactNode;
  headerActions?: ReactNode;

  // Section navigation
  sections?: AnalyticsSection[];
  activeSection?: string;
  onSectionChange?: (sectionId: string) => void;

  // Export options
  exportActions?: ExportAction[];
  showExportFooter?: boolean;

  // Content
  children: ReactNode;

  // Layout options
  maxWidth?: 'container' | 'content' | 'narrow';
  spacing?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export const AnalyticsPageTemplate: React.FC<AnalyticsPageTemplateProps> = ({
  title,
  description,
  icon,
  headerActions,
  sections,
  activeSection,
  onSectionChange,
  exportActions,
  showExportFooter = true,
  children,
  maxWidth = 'container',
  spacing = 'xl',
  className = '',
}) => {
  const spacingClass = {
    sm: 'space-y-md',
    md: 'space-y-lg',
    lg: 'space-y-xl',
    xl: 'space-y-2xl',
  }[spacing];

  const maxWidthClass = {
    container: 'max-w-container',
    content: 'max-w-content',
    narrow: 'max-w-narrow',
  }[maxWidth];

  return (
    <div className={`${maxWidthClass} mx-auto ${spacingClass} ${className}`}>
      {/* Page Header */}
      <SectionHeader
        title={title}
        description={description}
        icon={icon}
        actions={headerActions}
      />

      {/* Section Navigation (if provided) */}
      {sections && sections.length > 0 && onSectionChange && (
        <Card padding="none">
          <div className="flex flex-wrap gap-2 p-4 border-b border-background-border">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => onSectionChange(section.id)}
                className={`
                  flex items-center gap-2 px-4 py-2 rounded-sm text-small font-medium 
                  transition-all duration-fast
                  ${activeSection === section.id
                    ? 'bg-accent-gold text-background-base shadow-sm'
                    : 'bg-background-hover text-text-secondary hover:bg-background-border hover:text-text-primary'
                  }
                `}
              >
                {section.icon && <span className="flex-shrink-0">{section.icon}</span>}
                {section.label}
              </button>
            ))}
          </div>
        </Card>
      )}

      {/* Main Content */}
      <div className={spacingClass}>
        {children}
      </div>

      {/* Export Footer (if export actions provided and enabled) */}
      {showExportFooter && exportActions && exportActions.length > 0 && (
        <Card padding="md">
          <div className="flex flex-wrap gap-4 justify-center items-center">
            {exportActions.map((action, index) => (
              <Button
                key={index}
                variant={action.variant || 'primary'}
                size="md"
                onClick={action.onClick}
                disabled={action.disabled}
                loading={action.loading}
                icon={action.icon}
              >
                {action.label}
              </Button>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default AnalyticsPageTemplate;
