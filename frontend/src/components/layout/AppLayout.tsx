/**
 * Main application layout with header and sidebar navigation
 * Redesigned with proper spacing and max-width container
 */
import React, { ReactNode } from 'react';
import AppHeader from './AppHeader';
import Sidebar from './Sidebar';

interface AppLayoutProps {
  children: ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background-base">
      <AppHeader />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 ml-60 min-h-[calc(100vh-73px)]">
          <div className="max-w-container mx-auto p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
