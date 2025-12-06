/**
 * Breadcrumb Navigation Component
 * Provides hierarchical navigation context with accessibility support
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: React.ReactNode;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items, className = '' }) => {
  return (
    <nav aria-label="Breadcrumb" className={`flex items-center gap-2 text-sm ${className}`}>
      <ol className="flex items-center gap-2 flex-wrap">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          const isFirst = index === 0;
          
          return (
            <li key={index} className="flex items-center gap-2">
              {!isFirst && (
                <ChevronRight 
                  size={16} 
                  className="text-text-tertiary flex-shrink-0" 
                  aria-hidden="true"
                />
              )}
              
              {item.path && !isLast ? (
                <Link
                  to={item.path}
                  className="inline-flex items-center gap-1.5 text-text-secondary hover:text-accent-gold transition-colors duration-fast"
                  aria-label={isFirst ? 'Navigate to home' : `Navigate to ${item.label}`}
                >
                  {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
                  <span className="truncate max-w-[200px]">{item.label}</span>
                </Link>
              ) : (
                <span
                  className={`inline-flex items-center gap-1.5 ${
                    isLast 
                      ? 'text-text-primary font-semibold' 
                      : 'text-text-tertiary'
                  }`}
                  aria-current={isLast ? 'page' : undefined}
                >
                  {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
                  <span className="truncate max-w-[200px]">{item.label}</span>
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

/**
 * Hook to generate breadcrumbs from route path
 */
export const useBreadcrumbs = (pathname: string, customLabels?: Record<string, string>): BreadcrumbItem[] => {
  const defaultLabels: Record<string, string> = {
    '/': 'Dashboard',
    '/inputs': 'Model Inputs',
    '/scenarios': 'Scenarios',
    '/analytics': 'Analytics',
    '/reports': 'Reports',
    '/social-security': 'Social Security',
    '/annuity': 'Annuity Analysis',
    '/estate': 'Estate Planning',
    '/tax-optimization': 'Tax Optimization',
    '/goals': 'Goal Planning',
    '/presentation': 'Presentation Mode',
    '/salem-report': 'Salem Report',
  };

  const labels = { ...defaultLabels, ...customLabels };

  // Always include home
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Home', path: '/', icon: <Home size={16} /> }
  ];

  // Don't show breadcrumb on home page
  if (pathname === '/') {
    return [];
  }

  // Add current page
  const currentLabel = labels[pathname] || pathname.replace('/', '').replace('-', ' ');
  breadcrumbs.push({
    label: currentLabel,
    path: pathname,
  });

  return breadcrumbs;
};
