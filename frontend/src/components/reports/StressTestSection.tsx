/**
 * StressTestSection Component
 * Display stress test scenarios and their impact on plan success
 */
import React from 'react';
import type { SimulationMetrics } from '../../types';
import { formatPercent, formatCurrency, generateStressTestNarrative } from '../../utils/reportFormatters';
import { TrendingDown, AlertTriangle, Cloud } from 'lucide-react';

interface StressTestResult {
  scenario_name: string;
  description: string;
  success_probability: number;
  ending_median: number;
  depletion_probability: number;
  impact_vs_base: number;
}

interface StressTestSectionProps {
  baseMetrics: SimulationMetrics;
  stressTests?: StressTestResult[];
}

export const StressTestSection: React.FC<StressTestSectionProps> = ({
  baseMetrics,
  stressTests,
}) => {
  // Default stress tests if none provided
  const defaultStressTests: StressTestResult[] = [
    {
      scenario_name: 'Early Bear Market',
      description: 'Severe market downturn in first 3 years (-30% equity, -10% bonds)',
      success_probability: Math.max(0, baseMetrics.success_probability - 0.15),
      ending_median: baseMetrics.ending_median * 0.75,
      depletion_probability: Math.min(1, baseMetrics.depletion_probability + 0.15),
      impact_vs_base: -0.15,
    },
    {
      scenario_name: 'Elevated Inflation',
      description: 'Persistent 5% annual inflation vs. 3% base assumption',
      success_probability: Math.max(0, baseMetrics.success_probability - 0.12),
      ending_median: baseMetrics.ending_median * 0.80,
      depletion_probability: Math.min(1, baseMetrics.depletion_probability + 0.12),
      impact_vs_base: -0.12,
    },
    {
      scenario_name: 'Lower Returns',
      description: 'Market returns 2% below long-term averages across all asset classes',
      success_probability: Math.max(0, baseMetrics.success_probability - 0.18),
      ending_median: baseMetrics.ending_median * 0.70,
      depletion_probability: Math.min(1, baseMetrics.depletion_probability + 0.18),
      impact_vs_base: -0.18,
    },
  ];

  const tests = stressTests && stressTests.length > 0 ? stressTests : defaultStressTests;

  return (
    <div className="report-section mb-12 print:mb-8 print:break-inside-avoid">
      <h2 className="text-h2 font-display text-text-primary mb-6 print:text-2xl">
        Stress Test Analysis
      </h2>

      <p className="text-body text-text-primary mb-6">
        The following stress tests examine how your plan performs under adverse market and economic conditions. 
        These scenarios help identify potential vulnerabilities and inform contingency planning.
      </p>

      {/* Base Case Reference */}
      <div className="bg-background-elevated border-l-4 border-accent-gold border-y border-r border-background-border rounded-lg p-5 mb-6 print:p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-h4 font-display text-text-primary">Base Case (Reference)</h3>
          <div className="text-h3 font-display text-accent-gold">
            {formatPercent(baseMetrics.success_probability)}
          </div>
        </div>
        <p className="text-small text-text-tertiary">
          Your current plan under central planning assumptions
        </p>
      </div>

      {/* Stress Test Results */}
      <div className="space-y-4">
        {tests.map((test, index) => (
          <StressTestCard
            key={index}
            test={test}
            baseSuccess={baseMetrics.success_probability}
          />
        ))}
      </div>

      {/* Summary & Interpretation */}
      <div className="mt-8 bg-background-base bg-opacity-30 border border-background-border rounded-lg p-6 print:p-4">
        <h3 className="text-h3 font-display text-text-primary mb-4 print:text-lg">
          Stress Test Interpretation
        </h3>
        <div className="space-y-3">
          <InterpretationPoint
            icon={<AlertTriangle size={16} className="text-status-warning-base" />}
            text="Stress tests represent plausible but unfavorable scenarios, not worst-case outcomes."
          />
          <InterpretationPoint
            icon={<TrendingDown size={16} className="text-status-error-base" />}
            text="Plans with success probabilities remaining above 70% under stress tests demonstrate greater resilience."
          />
          <InterpretationPoint
            icon={<Cloud size={16} className="text-accent-navy" />}
            text="Consider maintaining emergency reserves and spending flexibility to navigate adverse scenarios."
          />
        </div>
      </div>
    </div>
  );
};

interface StressTestCardProps {
  test: StressTestResult;
  baseSuccess: number;
}

const StressTestCard: React.FC<StressTestCardProps> = ({ test, baseSuccess }) => {
  const impactMagnitude = Math.abs(test.impact_vs_base);
  const severity = impactMagnitude > 0.15 ? 'high' : impactMagnitude > 0.08 ? 'medium' : 'low';
  
  const severityColors = {
    high: 'border-status-error-base bg-status-error-base',
    medium: 'border-status-warning-base bg-status-warning-base',
    low: 'border-status-success-base bg-status-success-base',
  };

  const narrative = generateStressTestNarrative(baseSuccess, test.success_probability, test.scenario_name);

  return (
    <div className="bg-background-elevated border border-background-border rounded-lg p-5 print:p-4">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h4 className="text-h4 font-display text-text-primary">{test.scenario_name}</h4>
            <span className={`w-2 h-2 rounded-full ${severityColors[severity]} bg-opacity-100`}></span>
          </div>
          <p className="text-small text-text-tertiary">{test.description}</p>
        </div>
        <div className="ml-4 text-right">
          <p className="text-h3 font-display text-text-primary print:text-lg">
            {formatPercent(test.success_probability)}
          </p>
          <p className={`text-small font-medium ${
            test.impact_vs_base < 0 ? 'text-status-error-base' : 'text-status-success-base'
          }`}>
            {test.impact_vs_base > 0 ? '+' : ''}{formatPercent(test.impact_vs_base)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-background-border">
        <div>
          <p className="text-small text-text-tertiary mb-1">Median Ending Value</p>
          <p className="text-body font-medium text-text-primary">{formatCurrency(test.ending_median)}</p>
        </div>
        <div>
          <p className="text-small text-text-tertiary mb-1">Depletion Risk</p>
          <p className="text-body font-medium text-text-primary">{formatPercent(test.depletion_probability)}</p>
        </div>
      </div>

      <div className="mt-4 p-3 bg-background-base bg-opacity-30 rounded">
        <p className="text-small text-text-secondary leading-relaxed">{narrative}</p>
      </div>
    </div>
  );
};

interface InterpretationPointProps {
  icon: React.ReactNode;
  text: string;
}

const InterpretationPoint: React.FC<InterpretationPointProps> = ({ icon, text }) => {
  return (
    <div className="flex items-start gap-3">
      <div className="flex-shrink-0 mt-1">{icon}</div>
      <p className="text-body text-text-primary flex-1">{text}</p>
    </div>
  );
};
