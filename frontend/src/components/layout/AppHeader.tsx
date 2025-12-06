/**
 * Application header with logo, title, and quick actions
 * Phase 3: Enhanced with responsive design and better mobile UX
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSimulationStore } from '../../store/simulationStore';
import { Button } from '../ui';
import { Play, FileDown, Save, Presentation } from 'lucide-react';
import apiClient from '../../lib/api';

const AppHeader: React.FC = () => {
  const navigate = useNavigate();
  const { 
    modelInputs, 
    clientInfo, 
    setSimulationResults, 
    setIsLoading, 
    setError,
    setHasRunSimulation,
    isLoading,
    hasRunSimulation 
  } = useSimulationStore();

  const handleRunSimulation = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiClient.axiosClient.post('/simulation/run', {
        client_info: clientInfo,
        model_inputs: modelInputs,
      });
      setSimulationResults(response.data);
      setHasRunSimulation(true);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Simulation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = () => {
    navigate('/reports');
  };

  return (
    <header 
      className="bg-background-elevated border-b border-background-border shadow-lg sticky top-0 z-dropdown backdrop-blur-sm"
      role="banner"
      aria-label="Site header"
    >
      <div className="flex items-center justify-between px-4 sm:px-6 lg:px-8 py-3 sm:py-4 max-w-container mx-auto">
        {/* Logo and Title */}
        <div className="flex items-center gap-3 sm:gap-4 min-w-0">
          <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-accent-gold to-accent-gold-dark rounded-lg flex items-center justify-center font-bold text-white shadow-md flex-shrink-0">
            <span className="text-lg sm:text-xl">S</span>
          </div>
          <div className="min-w-0">
            <h1 className="text-base sm:text-h3 font-display font-bold text-text-primary tracking-tight truncate">
              Portfolio Scenario Analysis
            </h1>
            <p className="text-micro sm:text-small text-text-tertiary hidden sm:block">
              Salem Investment Counselors
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
          {/* Presentation Mode - Hidden on mobile */}
          {hasRunSimulation && (
            <button
              onClick={() => navigate('/presentation')}
              className="hidden md:inline-flex items-center gap-2 px-4 lg:px-6 py-2 lg:py-3 bg-accent-gold text-text-primary font-semibold rounded-sm transition-all hover:bg-accent-gold-light shadow-md hover:shadow-lg"
              title="Enter Presentation Mode"
            >
              <Presentation size={18} />
              <span className="hidden lg:inline">Presentation Mode</span>
              <span className="lg:hidden">Present</span>
            </button>
          )}
          
          {/* Run Simulation - Always visible */}
          <Button
            variant="primary"
            size="sm"
            icon={<Play size={16} />}
            onClick={handleRunSimulation}
            loading={isLoading}
            disabled={isLoading}
            className="sm:hidden"
            aria-label={isLoading ? 'Running simulation...' : 'Run Monte Carlo simulation'}
          >
            Run
          </Button>
          
          <Button
            variant="primary"
            size="md"
            icon={<Play size={18} />}
            onClick={handleRunSimulation}
            loading={isLoading}
            disabled={isLoading}
            className="hidden sm:inline-flex"
            aria-label={isLoading ? 'Running simulation...' : 'Run Monte Carlo simulation'}
          >
            Run Simulation
          </Button>
          
          {/* Export & Save - Show only when simulation complete */}
          {hasRunSimulation && (
            <>
              {/* Export - Hidden on small mobile */}
              <Button
                variant="secondary"
                size="sm"
                icon={<FileDown size={16} />}
                onClick={handleExport}
                className="hidden sm:inline-flex"
                aria-label="Export reports"
              >
                <span className="hidden lg:inline">Export</span>
              </Button>
              
              {/* Save - Hidden on mobile */}
              <Button
                variant="tertiary"
                size="sm"
                icon={<Save size={16} />}
                onClick={() => console.log('Save functionality')}
                className="hidden lg:inline-flex"
                aria-label="Save current state"
              >
                Save
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default AppHeader;
