/**
 * Main application layout with header and sidebar navigation
 * Phase 6: Enhanced with responsive design, accessibility, and mobile support
 */
import React, { ReactNode, useState } from 'react';
import AppHeader from './AppHeader';
import Sidebar from './Sidebar';

interface AppLayoutProps {
  children: ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
      <div className="flex">
        {/* Sidebar - Hidden on mobile, shown on desktop */}
        <div className="hidden lg:block">
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
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
