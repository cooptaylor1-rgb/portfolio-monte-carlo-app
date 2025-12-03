/**
 * Application header with logo, title, and quick actions
 * Redesigned with better visual hierarchy and CTAs
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSimulationStore } from '../../store/simulationStore';
import { Button } from '../ui';
import { Play, FileDown, Save } from 'lucide-react';
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
    <header className="bg-background-elevated border-b border-background-border shadow-lg sticky top-0 z-50">
      <div className="flex items-center justify-between px-8 py-4 max-w-container mx-auto">
        {/* Logo and Title */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-accent-gold to-accent-gold-dark rounded-lg flex items-center justify-center font-bold text-white shadow-md">
            <span className="text-xl">S</span>
          </div>
          <div>
            <h1 className="text-h3 font-display font-bold text-text-primary tracking-tight">
              Portfolio Scenario Analysis
            </h1>
            <p className="text-small text-text-tertiary">
              Salem Investment Counselors
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-3">
          <Button
            variant="primary"
            size="md"
            icon={<Play size={18} />}
            onClick={handleRunSimulation}
            loading={isLoading}
            disabled={isLoading}
          >
            Run Simulation
          </Button>
          
          {hasRunSimulation && (
            <>
              <Button
                variant="secondary"
                size="md"
                icon={<FileDown size={18} />}
                onClick={handleExport}
              >
                Export
              </Button>
              
              <Button
                variant="tertiary"
                size="md"
                icon={<Save size={18} />}
                onClick={() => console.log('Save functionality')}
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
