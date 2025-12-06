/**
 * Sidebar navigation menu
 * Redesigned with clearer hierarchy and workflow guidance
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileEdit, GitCompare, FileText, CheckCircle, BarChart3, DollarSign, Home, Target, TrendingUp } from 'lucide-react';
import { useSimulationStore } from '../../store/simulationStore';

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
  description: string;
  step?: number;
}

const navItems: NavItem[] = [
  {
    path: '/',
    label: 'Overview',
    icon: <LayoutDashboard size={20} />,
    description: 'Dashboard & Results',
  },
  {
    path: '/inputs',
    label: 'Inputs',
    icon: <FileEdit size={20} />,
    description: 'Model Configuration',
    step: 1,
  },
  {
    path: '/scenarios',
    label: 'Scenarios',
    icon: <GitCompare size={20} />,
    description: 'Compare & Analyze',
    step: 2,
  },
  {
    path: '/analytics',
    label: 'Analytics',
    icon: <BarChart3 size={20} />,
    description: 'Deep Insights',
    step: 3,
  },
  {
    path: '/reports',
    label: 'Reports',
    icon: <FileText size={20} />,
    description: 'Export & Share',
    step: 4,
  },
  {
    path: '/social-security',
    label: 'Social Security',
    icon: <DollarSign size={20} />,
    description: 'Claiming Strategy',
  },
  {
    path: '/annuity',
    label: 'Annuity Analysis',
    icon: <TrendingUp size={20} />,
    description: 'SPIA/DIA/QLAC Pricing',
  },
  {
    path: '/estate',
    label: 'Estate Planning',
    icon: <Home size={20} />,
    description: 'Tax & Legacy Planning',
  },
  {
    path: '/tax-optimization',
    label: 'Tax Optimization',
    icon: <DollarSign size={20} />,
    description: 'Roth Conversions',
  },
  {
    path: '/goals',
    label: 'Goal Planning',
    icon: <Target size={20} />,
    description: 'Financial Goals',
  },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const { hasRunSimulation } = useSimulationStore();

  return (
    <aside className="w-60 bg-background-elevated border-r border-background-border fixed h-[calc(100vh-73px)] top-[73px] overflow-y-auto">
      <nav className="p-4">
        {/* Workflow Section */}
        <div className="mb-6">
          <div className="px-3 mb-3">
            <p className="text-micro uppercase tracking-wider text-text-tertiary font-semibold">
              Workflow
            </p>
          </div>
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              const isCompleted = item.step && item.step === 1 && hasRunSimulation;
              
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`
                      group flex items-start gap-3 px-3 py-2.5 rounded-sm transition-all duration-fast
                      ${isActive
                        ? 'bg-primary-navy text-white shadow-md'
                        : 'text-text-secondary hover:bg-background-hover hover:text-text-primary'
                      }
                    `}
                  >
                    <div className={`flex-shrink-0 mt-0.5 ${isActive ? 'text-accent-gold' : ''}`}>
                      {item.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        {item.step && (
                          <span className={`
                            text-micro font-semibold px-1.5 py-0.5 rounded
                            ${isActive 
                              ? 'bg-accent-gold text-background-base' 
                              : 'bg-background-border text-text-tertiary'
                            }
                          `}>
                            {item.step}
                          </span>
                        )}
                        <span className="font-semibold text-body truncate">
                          {item.label}
                        </span>
                        {isCompleted && (
                          <CheckCircle size={14} className="text-status-success-base flex-shrink-0" />
                        )}
                      </div>
                      <p className={`text-micro truncate ${isActive ? 'text-text-secondary' : 'text-text-tertiary'}`}>
                        {item.description}
                      </p>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Status Section */}
        {hasRunSimulation && (
          <div className="px-3 py-4 bg-background-hover rounded-md border border-background-border">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle size={16} className="text-status-success-base" />
              <p className="text-small font-semibold text-text-primary">
                Simulation Complete
              </p>
            </div>
            <p className="text-micro text-text-tertiary">
              Results are ready to view in the Overview and Reports sections.
            </p>
          </div>
        )}

        {!hasRunSimulation && (
          <div className="px-3 py-4 bg-background-hover rounded-md border border-background-border">
            <p className="text-small font-semibold text-text-primary mb-2">
              Getting Started
            </p>
            <p className="text-micro text-text-tertiary">
              Configure your model inputs and run a simulation to see results.
            </p>
          </div>
        )}
      </nav>
    </aside>
  );
};

export default Sidebar;
