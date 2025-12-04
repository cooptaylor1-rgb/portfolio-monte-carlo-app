/**
 * Presentation Mode - Main Container
 * 
 * Full-screen, client-facing presentation layer for financial advisors.
 * Features:
 * - Full-screen slide navigation
 * - Keyboard controls (arrow keys, ESC)
 * - Speaker notes panel
 * - Compliance mode toggle
 * - Export functionality
 * - Smooth transitions
 */

import React, { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSimulationStore } from '../store/simulationStore';
import { presentationTheme } from './presentationTheme';
import { 
  ChevronLeft, 
  ChevronRight, 
  X, 
  Download,
  FileText,
  Eye,
  EyeOff,
  Presentation
} from 'lucide-react';

// Lazy load slide components for better performance
const OverviewSlide = lazy(() => import('./slides/OverviewSlide'));
const PlanSummarySlide = lazy(() => import('./slides/PlanSummarySlide'));
const MonteCarloSlide = lazy(() => import('./slides/MonteCarloSlide'));
const StressTestsSlide = lazy(() => import('./slides/StressTestsSlide'));
const AssetAllocationSlide = lazy(() => import('./slides/AssetAllocationSlide'));
const CashFlowsSlide = lazy(() => import('./slides/CashFlowsSlide'));
const KeyRisksSlide = lazy(() => import('./slides/KeyRisksSlide'));
const NextStepsSlide = lazy(() => import('./slides/NextStepsSlide'));

// Slide configuration
const slides = [
  { id: 'overview', title: 'Overview', Component: OverviewSlide },
  { id: 'plan', title: 'Plan Summary', Component: PlanSummarySlide },
  { id: 'projection', title: 'Portfolio Projection', Component: MonteCarloSlide },
  { id: 'stress', title: 'Stress Tests', Component: StressTestsSlide },
  { id: 'allocation', title: 'Asset Allocation', Component: AssetAllocationSlide },
  { id: 'cashflows', title: 'Cash Flows', Component: CashFlowsSlide },
  { id: 'risks', title: 'Key Considerations', Component: KeyRisksSlide },
  { id: 'next', title: 'Next Steps', Component: NextStepsSlide },
];

const PresentationMode: React.FC = () => {
  const navigate = useNavigate();
  const { clientInfo, simulationResults, hasRunSimulation } = useSimulationStore();
  
  // Presentation state
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showSpeakerNotes, setShowSpeakerNotes] = useState(false);
  const [complianceMode, setComplianceMode] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [showControls, setShowControls] = useState(true);
  
  // Auto-hide controls after inactivity
  useEffect(() => {
    let timeout: NodeJS.Timeout;
    
    const resetTimer = () => {
      setShowControls(true);
      clearTimeout(timeout);
      timeout = setTimeout(() => setShowControls(false), 3000);
    };
    
    window.addEventListener('mousemove', resetTimer);
    window.addEventListener('keydown', resetTimer);
    resetTimer();
    
    return () => {
      clearTimeout(timeout);
      window.removeEventListener('mousemove', resetTimer);
      window.removeEventListener('keydown', resetTimer);
    };
  }, []);
  
  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowRight':
        case ' ':
        case 'PageDown':
          e.preventDefault();
          nextSlide();
          break;
        case 'ArrowLeft':
        case 'PageUp':
          e.preventDefault();
          prevSlide();
          break;
        case 'Home':
          e.preventDefault();
          setCurrentSlide(0);
          break;
        case 'End':
          e.preventDefault();
          setCurrentSlide(slides.length - 1);
          break;
        case 'Escape':
          exitPresentation();
          break;
        case 'n':
        case 'N':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            setShowSpeakerNotes(prev => !prev);
          }
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentSlide]);
  
  // Navigation functions
  const nextSlide = useCallback(() => {
    setCurrentSlide(prev => Math.min(prev + 1, slides.length - 1));
  }, []);
  
  const prevSlide = useCallback(() => {
    setCurrentSlide(prev => Math.max(prev - 1, 0));
  }, []);
  
  const goToSlide = useCallback((index: number) => {
    setCurrentSlide(index);
  }, []);
  
  const exitPresentation = useCallback(() => {
    navigate('/');
  }, [navigate]);
  
  // Export handlers (placeholder - implement in task 6)
  const handleExportPDF = async () => {
    setIsExporting(true);
    // TODO: Implement PDF export
    console.log('Exporting PDF...');
    setTimeout(() => setIsExporting(false), 2000);
  };
  
  const handleExportPPTX = async () => {
    setIsExporting(true);
    // TODO: Implement PowerPoint export
    console.log('Exporting PowerPoint...');
    setTimeout(() => setIsExporting(false), 2000);
  };
  
  const handleExportPNG = async () => {
    setIsExporting(true);
    // TODO: Implement PNG export
    console.log('Exporting PNG...');
    setTimeout(() => setIsExporting(false), 2000);
  };
  
  // Check if we have data to present
  if (!hasRunSimulation) {
    return (
      <div style={styles.noData}>
        <Presentation size={64} color={presentationTheme.colors.gold} />
        <h2 style={styles.noDataTitle}>No Simulation Data</h2>
        <p style={styles.noDataText}>
          Please run a Monte Carlo simulation first to view the presentation.
        </p>
        <button onClick={() => navigate('/inputs')} style={styles.noDataButton}>
          Go to Inputs
        </button>
      </div>
    );
  }
  
  const CurrentSlideComponent = slides[currentSlide].Component;
  
  return (
    <div style={styles.container}>
      {/* Main slide area */}
      <div style={styles.slideContainer}>
        <Suspense fallback={<SlideLoader />}>
          <CurrentSlideComponent
            clientInfo={clientInfo}
            simulationResults={simulationResults}
            complianceMode={complianceMode}
          />
        </Suspense>
      </div>
      
      {/* Controls overlay */}
      <div 
        style={{
          ...styles.controls,
          opacity: showControls ? 1 : 0,
          pointerEvents: showControls ? 'auto' : 'none',
        }}
      >
        {/* Top bar */}
        <div style={styles.topBar}>
          <div style={styles.clientName}>
            {clientInfo.client_name}
          </div>
          
          <div style={styles.topBarControls}>
            {/* Compliance mode toggle */}
            <button
              onClick={() => setComplianceMode(!complianceMode)}
              style={styles.iconButton}
              title="Toggle Compliance Mode"
            >
              {complianceMode ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
            
            {/* Speaker notes toggle */}
            <button
              onClick={() => setShowSpeakerNotes(!showSpeakerNotes)}
              style={{
                ...styles.iconButton,
                backgroundColor: showSpeakerNotes ? presentationTheme.colors.gold : 'transparent',
              }}
              title="Toggle Speaker Notes (Ctrl+N)"
            >
              <FileText size={20} />
            </button>
            
            {/* Export menu */}
            <div style={styles.exportMenu}>
              <button
                style={styles.iconButton}
                title="Export Options"
                disabled={isExporting}
              >
                <Download size={20} />
              </button>
              <div style={styles.exportDropdown}>
                <button onClick={handleExportPDF} style={styles.exportOption}>
                  Export as PDF
                </button>
                <button onClick={handleExportPPTX} style={styles.exportOption}>
                  Export as PowerPoint
                </button>
                <button onClick={handleExportPNG} style={styles.exportOption}>
                  Export as Images
                </button>
              </div>
            </div>
            
            {/* Exit button */}
            <button
              onClick={exitPresentation}
              style={styles.exitButton}
              title="Exit Presentation (ESC)"
            >
              <X size={24} />
            </button>
          </div>
        </div>
        
        {/* Bottom navigation */}
        <div style={styles.bottomBar}>
          {/* Previous button */}
          <button
            onClick={prevSlide}
            disabled={currentSlide === 0}
            style={{
              ...styles.navButton,
              opacity: currentSlide === 0 ? 0.3 : 1,
            }}
          >
            <ChevronLeft size={32} />
          </button>
          
          {/* Slide indicators */}
          <div style={styles.slideIndicators}>
            {slides.map((slide, index) => (
              <button
                key={slide.id}
                onClick={() => goToSlide(index)}
                style={{
                  ...styles.indicator,
                  backgroundColor: index === currentSlide 
                    ? presentationTheme.colors.gold 
                    : presentationTheme.colors.background.tertiary,
                }}
                title={slide.title}
              />
            ))}
          </div>
          
          {/* Slide counter */}
          <div style={styles.slideCounter}>
            {currentSlide + 1} / {slides.length}
          </div>
          
          {/* Next button */}
          <button
            onClick={nextSlide}
            disabled={currentSlide === slides.length - 1}
            style={{
              ...styles.navButton,
              opacity: currentSlide === slides.length - 1 ? 0.3 : 1,
            }}
          >
            <ChevronRight size={32} />
          </button>
        </div>
      </div>
      
      {/* Speaker notes panel */}
      {showSpeakerNotes && (
        <div style={styles.speakerNotesPanel}>
          <div style={styles.speakerNotesHeader}>
            <h3 style={styles.speakerNotesTitle}>Speaker Notes</h3>
            <button
              onClick={() => setShowSpeakerNotes(false)}
              style={styles.closeNotesButton}
            >
              <X size={16} />
            </button>
          </div>
          <div style={styles.speakerNotesContent}>
            <p style={styles.speakerNotesSlide}>
              Slide {currentSlide + 1}: {slides[currentSlide].title}
            </p>
            <ul style={styles.speakerNotesList}>
              <li>Review key points for this slide</li>
              <li>Address client questions</li>
              <li>Transition to next topic</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

// Loading component for lazy-loaded slides
const SlideLoader: React.FC = () => (
  <div style={styles.loader}>
    <div style={styles.loaderSpinner} />
    <p style={styles.loaderText}>Loading slide...</p>
  </div>
);

// Styles
const styles: Record<string, React.CSSProperties> = {
  container: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: presentationTheme.colors.background.primary,
    color: presentationTheme.colors.text.primary,
    fontFamily: presentationTheme.typography.fonts.primary,
    overflow: 'hidden',
    zIndex: 9999,
  },
  
  slideContainer: {
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  
  controls: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    pointerEvents: 'none',
    transition: `opacity ${presentationTheme.animation.normal} ${presentationTheme.animation.easing.standard}`,
  },
  
  topBar: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.5rem 2rem',
    background: 'linear-gradient(to bottom, rgba(0,0,0,0.8), transparent)',
    pointerEvents: 'auto',
  },
  
  clientName: {
    fontSize: '1.25rem',
    fontWeight: 600,
    color: presentationTheme.colors.text.primary,
  },
  
  topBarControls: {
    display: 'flex',
    gap: '0.75rem',
    alignItems: 'center',
  },
  
  iconButton: {
    background: 'rgba(255, 255, 255, 0.1)',
    border: 'none',
    borderRadius: presentationTheme.borderRadius.md,
    padding: '0.75rem',
    color: presentationTheme.colors.text.primary,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: `all ${presentationTheme.animation.fast}`,
  },
  
  exitButton: {
    background: 'rgba(239, 68, 68, 0.2)',
    border: 'none',
    borderRadius: presentationTheme.borderRadius.md,
    padding: '0.75rem',
    color: '#EF4444',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: `all ${presentationTheme.animation.fast}`,
  },
  
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.5rem 2rem',
    background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)',
    pointerEvents: 'auto',
  },
  
  navButton: {
    background: 'transparent',
    border: 'none',
    color: presentationTheme.colors.text.primary,
    cursor: 'pointer',
    padding: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    transition: `all ${presentationTheme.animation.fast}`,
  },
  
  slideIndicators: {
    display: 'flex',
    gap: '0.5rem',
    flex: 1,
    justifyContent: 'center',
  },
  
  indicator: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    border: 'none',
    cursor: 'pointer',
    transition: `all ${presentationTheme.animation.fast}`,
  },
  
  slideCounter: {
    fontSize: '1rem',
    fontWeight: 500,
    color: presentationTheme.colors.text.secondary,
    minWidth: '80px',
    textAlign: 'right',
  },
  
  speakerNotesPanel: {
    position: 'absolute',
    bottom: '100px',
    right: '2rem',
    width: '350px',
    maxHeight: '400px',
    backgroundColor: presentationTheme.colors.background.secondary,
    border: `1px solid ${presentationTheme.colors.border}`,
    borderRadius: presentationTheme.borderRadius.lg,
    boxShadow: presentationTheme.shadows.xl,
    overflow: 'hidden',
    pointerEvents: 'auto',
  },
  
  speakerNotesHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem',
    borderBottom: `1px solid ${presentationTheme.colors.border}`,
    backgroundColor: presentationTheme.colors.background.tertiary,
  },
  
  speakerNotesTitle: {
    fontSize: '1rem',
    fontWeight: 600,
    margin: 0,
  },
  
  closeNotesButton: {
    background: 'transparent',
    border: 'none',
    color: presentationTheme.colors.text.secondary,
    cursor: 'pointer',
    padding: '0.25rem',
    display: 'flex',
  },
  
  speakerNotesContent: {
    padding: '1rem',
    overflowY: 'auto',
    maxHeight: '340px',
  },
  
  speakerNotesSlide: {
    fontSize: '0.875rem',
    fontWeight: 600,
    color: presentationTheme.colors.gold,
    marginBottom: '0.75rem',
  },
  
  speakerNotesList: {
    fontSize: '0.875rem',
    lineHeight: 1.6,
    paddingLeft: '1.25rem',
    margin: 0,
  },
  
  exportMenu: {
    position: 'relative',
  },
  
  exportDropdown: {
    position: 'absolute',
    top: '100%',
    right: 0,
    marginTop: '0.5rem',
    backgroundColor: presentationTheme.colors.background.secondary,
    border: `1px solid ${presentationTheme.colors.border}`,
    borderRadius: presentationTheme.borderRadius.md,
    boxShadow: presentationTheme.shadows.lg,
    opacity: 0,
    pointerEvents: 'none',
    transition: `all ${presentationTheme.animation.fast}`,
    minWidth: '200px',
  },
  
  exportOption: {
    display: 'block',
    width: '100%',
    padding: '0.75rem 1rem',
    background: 'transparent',
    border: 'none',
    color: presentationTheme.colors.text.primary,
    textAlign: 'left',
    cursor: 'pointer',
    fontSize: '0.875rem',
    transition: `all ${presentationTheme.animation.fast}`,
  },
  
  loader: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '1rem',
  },
  
  loaderSpinner: {
    width: '48px',
    height: '48px',
    border: `4px solid ${presentationTheme.colors.background.tertiary}`,
    borderTop: `4px solid ${presentationTheme.colors.gold}`,
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  
  loaderText: {
    fontSize: '1rem',
    color: presentationTheme.colors.text.muted,
  },
  
  noData: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    gap: '1.5rem',
  },
  
  noDataTitle: {
    fontSize: '2rem',
    fontWeight: 600,
    margin: 0,
  },
  
  noDataText: {
    fontSize: '1.125rem',
    color: presentationTheme.colors.text.secondary,
    textAlign: 'center',
    maxWidth: '500px',
  },
  
  noDataButton: {
    padding: '0.75rem 2rem',
    backgroundColor: presentationTheme.colors.gold,
    color: presentationTheme.colors.background.primary,
    border: 'none',
    borderRadius: presentationTheme.borderRadius.md,
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: `all ${presentationTheme.animation.fast}`,
  },
};

// Add keyframe animation for spinner
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .export-menu:hover .export-dropdown {
    opacity: 1 !important;
    pointer-events: auto !important;
  }
  
  .export-option:hover {
    background-color: ${presentationTheme.colors.background.tertiary} !important;
  }
  
  .icon-button:hover {
    background-color: rgba(255, 255, 255, 0.2) !important;
    transform: translateY(-2px);
  }
  
  .exit-button:hover {
    background-color: rgba(239, 68, 68, 0.3) !important;
  }
  
  .nav-button:hover:not(:disabled) {
    transform: scale(1.1);
  }
  
  .indicator:hover {
    transform: scale(1.3);
  }
`;
document.head.appendChild(styleSheet);

export default PresentationMode;
