/**
 * ExecutiveSummary Component
 * High-level overview with success probability and key metrics
 */
import React from 'react';
import type { SimulationMetrics, ModelInputs } from '../../types';
import { 
  formatCurrency, 
  formatPercent, 
  getSuccessRating,
  generateKeyFindings,
  generateRiskAssessment,
  generateRecommendations
} from '../../utils/reportFormatters';
import { Badge } from '../ui';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';

interface ExecutiveSummaryProps {
  metrics: SimulationMetrics;
  modelInputs: ModelInputs;
}

export const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({
  metrics,
  modelInputs,
}) => {
  const successRating = getSuccessRating(metrics.success_probability);
  const keyFindings = generateKeyFindings(
    metrics.success_probability,
    metrics.ending_median,
    metrics.ending_p10,
    metrics.depletion_probability,
    modelInputs.starting_portfolio
  );
  const risks = generateRiskAssessment(
    metrics.success_probability,
    metrics.depletion_probability,
    metrics.shortfall_risk,
    modelInputs.equity_pct
  );
  const recommendations = generateRecommendations(
    metrics.success_probability,
    metrics.depletion_probability,
    metrics.ending_median,
    modelInputs.starting_portfolio,
    modelInputs.monthly_spending,
    modelInputs.equity_pct
  );

  return (
    <div className="report-section mb-12 print:mb-8">
      <h2 className="text-h2 font-display text-text-primary mb-6 print:text-2xl">
        Executive Summary
      </h2>

      {/* Success Probability Highlight */}
      <div className={`p-8 rounded-lg border-2 mb-8 print:p-6 print:mb-6 ${
        successRating.variant === 'success' 
          ? 'bg-status-success-base bg-opacity-10 border-status-success-base'
          : successRating.variant === 'warning'
          ? 'bg-status-warning-base bg-opacity-10 border-status-warning-base'
          : 'bg-status-error-base bg-opacity-10 border-status-error-base'
      }`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {successRating.variant === 'success' && <CheckCircle size={32} color={successRating.color} />}
            {successRating.variant === 'warning' && <AlertCircle size={32} color={successRating.color} />}
            {successRating.variant === 'error' && <AlertTriangle size={32} color={successRating.color} />}
            <div>
              <p className="text-small text-text-secondary uppercase tracking-wider font-semibold">
                Plan Success Probability
              </p>
              <p className={`text-display font-display ${
                successRating.variant === 'success' ? 'text-status-success-base' :
                successRating.variant === 'warning' ? 'text-status-warning-base' :
                'text-status-error-base'
              } print:text-5xl`}>
                {formatPercent(metrics.success_probability)}
              </p>
            </div>
          </div>
          <Badge variant={successRating.variant} size="lg">
            {successRating.label}
          </Badge>
        </div>
        <p className="text-body text-text-primary">
          Based on Monte Carlo simulation of {modelInputs.n_scenarios} scenarios over {modelInputs.years_to_model} years, 
          your financial plan demonstrates a <strong>{successRating.label.toLowerCase()} probability</strong> of 
          successfully meeting all spending needs and financial objectives.
        </p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 print:gap-3 print:mb-6">
        <MetricCard
          label="Median Ending Portfolio"
          value={formatCurrency(metrics.ending_median)}
          icon={<TrendingUp size={20} />}
          trend={metrics.ending_median > modelInputs.starting_portfolio ? 'positive' : 'negative'}
        />
        <MetricCard
          label="10th Percentile (Downside)"
          value={formatCurrency(metrics.ending_p10)}
          icon={<TrendingDown size={20} />}
          trend="neutral"
        />
        <MetricCard
          label="90th Percentile (Upside)"
          value={formatCurrency(metrics.ending_p90)}
          icon={<TrendingUp size={20} />}
          trend="positive"
        />
        <MetricCard
          label="Depletion Risk"
          value={formatPercent(metrics.depletion_probability)}
          icon={<AlertTriangle size={20} />}
          trend={metrics.depletion_probability > 0.15 ? 'negative' : 'neutral'}
        />
      </div>

      {/* Key Findings */}
      <div className="mb-8 print:mb-6">
        <h3 className="text-h3 font-display text-text-primary mb-4 print:text-xl">
          Key Findings
        </h3>
        <div className="space-y-3">
          {keyFindings.map((finding, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <div className="w-2 h-2 bg-accent-gold rounded-full"></div>
              </div>
              <p className="text-body text-text-primary flex-1">{finding}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Considerations */}
      <div className="mb-8 print:mb-6">
        <h3 className="text-h3 font-display text-text-primary mb-4 print:text-xl">
          Risk Considerations
        </h3>
        <div className="space-y-3">
          {risks.map((risk, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <AlertCircle size={16} className="text-status-warning-base" />
              </div>
              <p className="text-body text-text-primary flex-1">{risk}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-background-elevated border border-background-border rounded-lg p-6 print:p-4">
        <h3 className="text-h3 font-display text-text-primary mb-4 print:text-xl">
          Recommendations & Next Steps
        </h3>
        <div className="space-y-3">
          {recommendations.map((recommendation, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <CheckCircle size={16} className="text-accent-gold" />
              </div>
              <p className="text-body text-text-primary flex-1">{recommendation}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Helper component for metric cards
interface MetricCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
  trend: 'positive' | 'negative' | 'neutral';
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, icon, trend }) => {
  const trendColor = 
    trend === 'positive' ? 'text-status-success-base' :
    trend === 'negative' ? 'text-status-error-base' :
    'text-text-secondary';

  return (
    <div className="bg-background-elevated border border-background-border rounded-lg p-4 print:p-3">
      <div className="flex items-center gap-2 mb-2">
        <div className={trendColor}>{icon}</div>
        <p className="text-small text-text-tertiary font-medium">{label}</p>
      </div>
      <p className="text-h3 font-display text-text-primary print:text-xl">{value}</p>
    </div>
  );
};
