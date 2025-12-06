/**
 * Main application layout with header and sidebar navigation
 * Phase 3: Enhanced with mobile navigation, breadcrumbs, and responsive design
 */
import React, { ReactNode, useState } from 'react';
import { useLocation } from 'react-router-dom';
import AppHeader from './AppHeader';
import Sidebar from './Sidebar';
import { Breadcrumb, useBreadcrumbs } from '../ui/Breadcrumb';
import { Menu, X } from 'lucide-react';

interface AppLayoutProps {
  children: ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const breadcrumbs = useBreadcrumbs(location.pathname);

  // Close mobile menu when route changes
  React.useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-background-base">
      {/* Skip to main content - Accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-accent-gold focus:text-background-base focus:rounded-sm"
      >
        Skip to main content
      </a>

      <AppHeader />

      {/* Mobile Menu Button */}
      <div className="lg:hidden fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="flex items-center justify-center w-14 h-14 bg-accent-gold text-background-base rounded-full shadow-lg hover:shadow-xl transition-all duration-fast hover:scale-105"
          aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={isMobileMenuOpen}
        >
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-background-base/80 backdrop-blur-sm z-40 animate-fade-in"
          onClick={() => setIsMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      <div className="flex">
        {/* Desktop Sidebar */}
        <div className="hidden lg:block">
          <Sidebar />
        </div>

        {/* Mobile Sidebar */}
        <div
          className={`
            lg:hidden fixed left-0 top-[73px] bottom-0 w-72 bg-background-elevated border-r border-background-border z-40 overflow-y-auto
            transition-transform duration-300 ease-in-out
            ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
          `}
        >
          <Sidebar />
        </div>

        {/* Main Content */}
        <main
          id="main-content"
          className="flex-1 lg:ml-60 min-h-[calc(100vh-73px)] w-full"
          role="main"
          aria-label="Main content"
        >
          <div className="max-w-container mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
            {/* Breadcrumbs */}
            {breadcrumbs.length > 0 && (
              <div className="mb-6">
                <Breadcrumb items={breadcrumbs} />
              </div>
            )}
            
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
