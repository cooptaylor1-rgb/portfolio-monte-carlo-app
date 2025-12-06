/**
 * Tabs Component - Tabbed navigation interface
 * Part of the comprehensive design system
 * WCAG AA compliant with keyboard navigation
 */
import React, { useState, useEffect } from 'react';

export interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  badge?: string | number;
}

export interface TabsProps {
  /** Array of tabs */
  tabs: Tab[];
  /** Currently active tab ID */
  activeTab?: string;
  /** Callback when tab changes */
  onChange?: (tabId: string) => void;
  /** Tab content */
  children?: React.ReactNode;
  /** Variant style */
  variant?: 'underline' | 'pills' | 'enclosed';
  /** Full width tabs */
  fullWidth?: boolean;
  /** Additional className */
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab: controlledActiveTab,
  onChange,
  children,
  variant = 'underline',
  fullWidth = false,
  className = '',
}) => {
  const [activeTab, setActiveTab] = useState(controlledActiveTab || tabs[0]?.id);

  useEffect(() => {
    if (controlledActiveTab) {
      setActiveTab(controlledActiveTab);
    }
  }, [controlledActiveTab]);

  const handleTabClick = (tabId: string, disabled?: boolean) => {
    if (disabled) return;
    setActiveTab(tabId);
    onChange?.(tabId);
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number, disabled?: boolean) => {
    if (disabled) return;

    if (e.key === 'ArrowRight') {
      e.preventDefault();
      const nextIndex = (index + 1) % tabs.length;
      const nextTab = tabs[nextIndex];
      if (!nextTab.disabled) {
        handleTabClick(nextTab.id);
      }
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const prevIndex = index === 0 ? tabs.length - 1 : index - 1;
      const prevTab = tabs[prevIndex];
      if (!prevTab.disabled) {
        handleTabClick(prevTab.id);
      }
    }
  };

  const getVariantStyles = (tab: Tab, isActive: boolean) => {
    const baseStyles = 'px-4 py-2.5 text-body font-medium transition-all duration-default focus:outline-none focus:ring-2 focus:ring-accent-gold focus:ring-offset-2 focus:ring-offset-background-base';

    if (variant === 'underline') {
      return `
        ${baseStyles}
        border-b-2
        ${isActive
          ? 'border-accent-gold text-text-primary'
          : 'border-transparent text-text-tertiary hover:text-text-secondary hover:border-background-border'
        }
        ${tab.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `;
    }

    if (variant === 'pills') {
      return `
        ${baseStyles}
        rounded-full
        ${isActive
          ? 'bg-accent-gold text-background-base'
          : 'bg-transparent text-text-secondary hover:bg-background-hover hover:text-text-primary'
        }
        ${tab.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `;
    }

    // enclosed variant
    return `
      ${baseStyles}
      rounded-t-md
      border-t
      border-l
      border-r
      ${isActive
        ? 'bg-background-elevated border-background-border text-text-primary border-b-0 -mb-px'
        : 'bg-background-base border-transparent text-text-tertiary hover:text-text-secondary hover:border-background-border'
      }
      ${tab.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
    `;
  };

  return (
    <div className={className}>
      <div
        role="tablist"
        className={`
          flex
          ${fullWidth ? 'w-full' : ''}
          ${variant === 'underline' ? 'border-b border-background-border' : ''}
          ${variant === 'enclosed' ? 'border-b border-background-border' : ''}
          ${variant === 'pills' ? 'gap-2 bg-background-elevated p-1 rounded-full' : ''}
        `}
      >
        {tabs.map((tab, index) => {
          const isActive = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.id}`}
              id={`tab-${tab.id}`}
              tabIndex={isActive ? 0 : -1}
              disabled={tab.disabled}
              className={`
                ${getVariantStyles(tab, isActive)}
                ${fullWidth ? 'flex-1' : ''}
              `}
              onClick={() => handleTabClick(tab.id, tab.disabled)}
              onKeyDown={(e) => handleKeyDown(e, index, tab.disabled)}
            >
              <span className="flex items-center justify-center gap-2">
                {tab.icon}
                <span>{tab.label}</span>
                {tab.badge !== undefined && (
                  <span className={`
                    px-2 py-0.5 text-micro font-semibold rounded-full
                    ${isActive ? 'bg-background-base text-accent-gold' : 'bg-background-hover text-text-secondary'}
                  `}>
                    {tab.badge}
                  </span>
                )}
              </span>
            </button>
          );
        })}
      </div>

      {children && (
        <div
          role="tabpanel"
          id={`tabpanel-${activeTab}`}
          aria-labelledby={`tab-${activeTab}`}
          className="py-4"
        >
          {children}
        </div>
      )}
    </div>
  );
};
