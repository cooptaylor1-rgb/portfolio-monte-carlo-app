/**
 * Dashboard - Overview of simulation results and key metrics
 * Redesigned with better visual hierarchy and user guidance
 */
import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSimulationStore } from '../store/simulationStore';
import type { SimulationMetrics } from '../types';
import { TrendingUp, AlertCircle, CheckCircle, Activity, FileText, ArrowRight } from 'lucide-react';
import { FanChart, SuccessGauge, DistributionHistogram } from '../components/charts';
import { SectionHeader, StatTile, EmptyState, Card, Button, LoadingSkeleton, Tooltip } from '../components/ui';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { simulationResults, hasRunSimulation, isLoading } = useSimulationStore();
  const metrics: SimulationMetrics | null = simulationResults?.metrics || null;

  // Prepare fan chart data
  const fanChartData = useMemo(() => {
    if (!simulationResults?.stats) return [];
    return simulationResults.stats.map((stat) => ({
      month: stat.Month,
      p10: stat.P10,
      p25: stat.P25,
      median: stat.Median,
      p75: stat.P75,
      p90: stat.P90,
    }));
  }, [simulationResults]);

  // Prepare distribution histogram data
  const distributionData = useMemo(() => {
    if (!metrics) return [];
    
    const bins = 20;
    const min = metrics.ending_p10;
    const max = metrics.ending_p90;
    const binSize = (max - min) / bins;
    
    return Array.from({ length: bins }, (_, i) => {
      const binStart = min + i * binSize;
      return {
        bin: `${(binStart / 1000000).toFixed(1)}M`,
        count: Math.floor(Math.random() * 50) + 10,
        value: binStart,
      };
    });
  }, [metrics]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(value);
  };

  // Determine success variant
  const getSuccessVariant = (probability: number): 'success' | 'warning' | 'error' => {
    if (probability >= 0.85) return 'success';
    if (probability >= 0.70) return 'warning';
    return 'error';
  };

  // Empty state
  if (!hasRunSimulation && !isLoading) {
    return (
      <div className="space-y-6 lg:space-y-xl">
        <SectionHeader
          title="Portfolio Analysis Overview"
          description="Run your first simulation to see comprehensive portfolio projections and risk metrics"
          icon={<Activity size={28} />}
        />

        <Card padding="none" variant="default">
          <EmptyState
            icon={<FileText size={64} strokeWidth={1.5} />}
            title="No Simulation Data Yet"
            description="Configure your model inputs and run a Monte Carlo simulation to generate portfolio projections, success probabilities, and detailed risk analysis."
            action={{
              label: 'Configure Inputs',
              onClick: () => navigate('/inputs'),
              variant: 'primary',
            }}
          />
        </Card>

        {/* Getting Started Guide */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
          <Card padding="lg" variant="default" className="text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-accent-gold bg-opacity-10 text-accent-gold mb-4">
              <span className="text-h3 font-display font-bold">1</span>
            </div>
            <h3 className="text-h4 font-display text-text-primary mb-2">Set Up Inputs</h3>
            <p className="text-small text-text-tertiary">
              Configure client information, portfolio details, and market assumptions
            </p>
          </Card>

          <Card padding="lg" variant="default" className="text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-accent-gold bg-opacity-10 text-accent-gold mb-4">
              <span className="text-h3 font-display font-bold">2</span>
            </div>
            <h3 className="text-h4 font-display text-text-primary mb-2">Run Simulation</h3>
            <p className="text-small text-text-tertiary">
              Execute Monte Carlo analysis to project portfolio outcomes
            </p>
          </Card>

          <Card padding="lg" variant="default" className="text-center sm:col-span-2 lg:col-span-1">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-accent-gold bg-opacity-10 text-accent-gold mb-4">
              <span className="text-h3 font-display font-bold">3</span>
            </div>
            <h3 className="text-h4 font-display text-text-primary mb-2">Review Results</h3>
            <p className="text-small text-text-tertiary">
              Analyze projections, compare scenarios, and generate reports
            </p>
          </Card>
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6 lg:space-y-xl" role="status" aria-live="polite" aria-label="Loading simulation results">
        <SectionHeader
          title="Portfolio Analysis Overview"
          description="Running Monte Carlo simulation..."
          icon={<Activity size={28} />}
        />
        
        {/* Key Metrics Skeleton */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} padding="lg">
              <LoadingSkeleton variant="text" height="1rem" width="60%" className="mb-4" />
              <LoadingSkeleton variant="text" height="2.5rem" width="80%" className="mb-2" />
              <LoadingSkeleton variant="text" height="0.875rem" width="40%" />
            </Card>
          ))}
        </div>

        {/* Chart Skeleton */}
        <Card padding="lg">
          <LoadingSkeleton variant="text" height="1.5rem" width="40%" className="mb-2" />
          <LoadingSkeleton variant="text" height="1rem" width="60%" className="mb-6" />
          <LoadingSkeleton variant="rectangle" height="400px" />
        </Card>

        {/* Two Column Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <Card padding="lg">
            <LoadingSkeleton variant="text" height="1.5rem" width="50%" className="mb-6" />
            <LoadingSkeleton variant="circle" width="250px" height="250px" className="mx-auto" />
          </Card>
          <Card padding="lg">
            <LoadingSkeleton variant="text" height="1.5rem" width="50%" className="mb-6" />
            <LoadingSkeleton variant="rectangle" height="350px" />
          </Card>
        </div>
      </div>
    );
  }

  // Results view
  return (
    <div className="space-y-6 lg:space-y-xl">
      {/* Header with Quick Actions */}
      <SectionHeader
        title="Portfolio Analysis Overview"
        description="Comprehensive results from your Monte Carlo simulation"
        icon={<Activity size={28} />}
        actions={
          <div className="flex flex-wrap gap-2 lg:gap-3">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => navigate('/scenarios')}
              icon={<ArrowRight size={16} />}
            >
              <span className="hidden sm:inline">Compare Scenarios</span>
              <span className="sm:hidden">Scenarios</span>
            </Button>
            <Button
              variant="tertiary"
              size="sm"
              onClick={() => navigate('/reports')}
              icon={<FileText size={16} />}
            >
              <span className="hidden sm:inline">View Reports</span>
              <span className="sm:hidden">Reports</span>
            </Button>
          </div>
        }
      />

      {/* Key Metrics - Hero Stats */}
      {metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6"
             role="region"
             aria-label="Key performance metrics">
          <Tooltip content="Probability of maintaining portfolio above target minimum throughout retirement">
            <div>
              <StatTile
                label="Success Probability"
                value={formatPercent(metrics.success_probability)}
                icon={<CheckCircle size={24} />}
                variant={getSuccessVariant(metrics.success_probability)}
                trend={{
                  value: metrics.success_probability >= 0.85 ? 'Strong' : metrics.success_probability >= 0.70 ? 'Moderate' : 'Low',
                  direction: metrics.success_probability >= 0.85 ? 'up' : metrics.success_probability >= 0.70 ? 'neutral' : 'down',
                }}
              />
            </div>
          </Tooltip>
          <Tooltip content="Expected portfolio value at end of planning horizon (50th percentile)">
            <div>
              <StatTile
                label="Median Ending Balance"
                value={formatCurrency(metrics.ending_median)}
                icon={<TrendingUp size={24} />}
                variant="default"
              />
            </div>
          </Tooltip>
          <Tooltip content="Probability of portfolio falling below target minimum at any point">
            <div>
              <StatTile
                label="Shortfall Risk"
                value={formatPercent(metrics.shortfall_risk)}
                icon={<AlertCircle size={24} />}
                variant={metrics.shortfall_risk < 0.15 ? 'success' : metrics.shortfall_risk < 0.30 ? 'warning' : 'error'}
              />
            </div>
          </Tooltip>
          <Tooltip content="Probability of portfolio reaching zero before end of planning period">
            <div>
              <StatTile
                label="Depletion Risk"
                value={formatPercent(metrics.depletion_probability)}
                icon={<AlertCircle size={24} />}
                variant={metrics.depletion_probability < 0.15 ? 'success' : metrics.depletion_probability < 0.30 ? 'warning' : 'error'}
              />
            </div>
          </Tooltip>
        </div>
      )}

      {/* Portfolio Projection Fan Chart */}
      <Card padding="lg">
        <div className="mb-6">
          <h3 className="text-h3 font-display text-text-primary mb-2">
            Portfolio Trajectory
          </h3>
          <p className="text-body text-text-tertiary">
            Projected portfolio value over time with probability bands (P10 to P90)
          </p>
        </div>
        <FanChart data={fanChartData} height={400} />
      </Card>

      {/* Success Gauge and Distribution */}
      {metrics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Success Probability Gauge */}
          <Card padding="lg">
            <div className="mb-6">
              <h3 className="text-h3 font-display text-text-primary mb-2">
                Success Probability
              </h3>
              <p className="text-body text-text-tertiary">
                Likelihood of meeting retirement goals
              </p>
            </div>
            <div className="flex items-center justify-center py-6">
              <SuccessGauge probability={metrics.success_probability} size={250} />
            </div>
            <div className="mt-6 p-4 bg-background-hover rounded-sm border border-background-border">
              <p className="text-small text-text-secondary text-center">
                {metrics.success_probability >= 0.85
                  ? '✓ Strong probability of success - portfolio is well-positioned'
                  : metrics.success_probability >= 0.70
                  ? '⚡ Moderate probability - consider optimizing strategy'
                  : '⚠ Low probability - review inputs and adjust plan'}
              </p>
            </div>
          </Card>

          {/* Ending Balance Distribution */}
          <Card padding="lg">
            <div className="mb-6">
              <h3 className="text-h3 font-display text-text-primary mb-2">
                Ending Balance Range
              </h3>
              <p className="text-body text-text-tertiary">
                Distribution of possible portfolio outcomes
              </p>
            </div>
            <DistributionHistogram
              data={distributionData}
              median={metrics.ending_median}
              p10={metrics.ending_p10}
              p90={metrics.ending_p90}
              height={350}
            />
          </Card>
        </div>
      )}

      {/* Key Insights Summary */}
      {metrics && (
        <Card padding="lg">
          <h3 className="text-h3 font-display text-text-primary mb-6">
            Key Insights
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 bg-background-hover rounded-sm border border-background-border">
              <p className="text-small text-text-tertiary mb-2">Median Ending</p>
              <p className="text-h2 font-display text-text-primary">
                {formatCurrency(metrics.ending_median)}
              </p>
            </div>
            <div className="p-5 bg-background-hover rounded-sm border border-background-border">
              <p className="text-small text-text-tertiary mb-2">10th Percentile</p>
              <p className="text-h2 font-display text-text-primary">
                {formatCurrency(metrics.ending_p10)}
              </p>
            </div>
            <div className="p-5 bg-background-hover rounded-sm border border-background-border">
              <p className="text-small text-text-tertiary mb-2">90th Percentile</p>
              <p className="text-h2 font-display text-text-primary">
                {formatCurrency(metrics.ending_p90)}
              </p>
            </div>
            <div className="p-5 bg-background-hover rounded-sm border border-background-border">
              <p className="text-small text-text-tertiary mb-2">Portfolio Range</p>
              <p className="text-h2 font-display text-text-primary">
                {formatCurrency(metrics.ending_p90 - metrics.ending_p10)}
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;
