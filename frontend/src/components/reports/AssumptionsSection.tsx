/**
 * AssumptionsSection Component
 * Detailed breakdown of all assumptions and inputs used in the analysis
 */
import React from 'react';
import type { ModelInputs, ClientInfo } from '../../types';
import { 
  formatCurrency, 
  formatPercent, 
  formatAgeRange,
  formatSpendingSummary 
} from '../../utils/reportFormatters';

interface AssumptionsSectionProps {
  modelInputs: ModelInputs;
  clientInfo: ClientInfo;
}

export const AssumptionsSection: React.FC<AssumptionsSectionProps> = ({
  modelInputs,
  clientInfo,
}) => {
  return (
    <div className="report-section mb-12 print:mb-8 print:break-before-page">
      <h2 className="text-h2 font-display text-text-primary mb-6 print:text-2xl">
        Planning Assumptions & Inputs
      </h2>

      <p className="text-body text-text-tertiary mb-8">
        This analysis is based on the assumptions and parameters detailed below. 
        Changes to these inputs can materially affect projected outcomes and should be 
        reviewed periodically to ensure they remain appropriate.
      </p>

      <div className="space-y-8">
        {/* Portfolio & Time Horizon */}
        <AssumptionGroup title="Portfolio & Time Horizon">
          <AssumptionRow 
            label="Starting Portfolio Value"
            value={formatCurrency(modelInputs.starting_portfolio)}
          />
          <AssumptionRow 
            label="Planning Period"
            value={`${modelInputs.years_to_model} years`}
          />
          <AssumptionRow 
            label="Current Age"
            value={`${modelInputs.current_age} years old`}
          />
          <AssumptionRow 
            label="Planning Horizon Age"
            value={`${modelInputs.horizon_age} years old`}
          />
        </AssumptionGroup>

        {/* Asset Allocation */}
        <AssumptionGroup title="Asset Allocation">
          <div className="mb-4">
            <div className="flex items-center gap-4 mb-2">
              <div className="flex-1 h-8 rounded flex overflow-hidden">
                <div 
                  className="bg-chart-blue flex items-center justify-center text-white text-small font-semibold"
                  style={{ width: `${modelInputs.equity_pct * 100}%` }}
                >
                  {formatPercent(modelInputs.equity_pct, 0)}
                </div>
                <div 
                  className="bg-chart-green flex items-center justify-center text-white text-small font-semibold"
                  style={{ width: `${modelInputs.fi_pct * 100}%` }}
                >
                  {formatPercent(modelInputs.fi_pct, 0)}
                </div>
                <div 
                  className="bg-accent-gold flex items-center justify-center text-background-base text-small font-semibold"
                  style={{ width: `${modelInputs.cash_pct * 100}%` }}
                >
                  {formatPercent(modelInputs.cash_pct, 0)}
                </div>
              </div>
            </div>
          </div>
          <AssumptionRow 
            label="Equity"
            value={formatPercent(modelInputs.equity_pct)}
            note={`${formatCurrency(modelInputs.starting_portfolio * modelInputs.equity_pct)}`}
          />
          <AssumptionRow 
            label="Fixed Income"
            value={formatPercent(modelInputs.fi_pct)}
            note={`${formatCurrency(modelInputs.starting_portfolio * modelInputs.fi_pct)}`}
          />
          <AssumptionRow 
            label="Cash"
            value={formatPercent(modelInputs.cash_pct)}
            note={`${formatCurrency(modelInputs.starting_portfolio * modelInputs.cash_pct)}`}
          />
          {modelInputs.use_glide_path && (
            <div className="mt-4 p-4 bg-background-base bg-opacity-30 rounded border border-background-border">
              <p className="text-small text-text-secondary mb-2">
                <strong>Glide Path Active:</strong> Allocation will gradually shift to {formatPercent(modelInputs.target_equity_pct)} equity 
                starting at age {modelInputs.glide_start_age}
              </p>
            </div>
          )}
        </AssumptionGroup>

        {/* Return Assumptions */}
        <AssumptionGroup title="Return & Volatility Assumptions">
          <div className="overflow-x-auto">
            <table className="w-full text-body">
              <thead>
                <tr className="border-b border-background-border">
                  <th className="text-left py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    Asset Class
                  </th>
                  <th className="text-right py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    Expected Return
                  </th>
                  <th className="text-right py-3 px-4 text-small font-semibold text-text-secondary uppercase tracking-wider">
                    Volatility
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-background-border">
                  <td className="py-3 px-4 text-text-primary">Equity</td>
                  <td className="py-3 px-4 text-right text-text-primary font-medium">
                    {formatPercent(modelInputs.equity_return_annual)}
                  </td>
                  <td className="py-3 px-4 text-right text-text-tertiary">
                    {formatPercent(modelInputs.equity_vol_annual)}
                  </td>
                </tr>
                <tr className="border-b border-background-border">
                  <td className="py-3 px-4 text-text-primary">Fixed Income</td>
                  <td className="py-3 px-4 text-right text-text-primary font-medium">
                    {formatPercent(modelInputs.fi_return_annual)}
                  </td>
                  <td className="py-3 px-4 text-right text-text-tertiary">
                    {formatPercent(modelInputs.fi_vol_annual)}
                  </td>
                </tr>
                <tr>
                  <td className="py-3 px-4 text-text-primary">Cash</td>
                  <td className="py-3 px-4 text-right text-text-primary font-medium">
                    {formatPercent(modelInputs.cash_return_annual)}
                  </td>
                  <td className="py-3 px-4 text-right text-text-tertiary">
                    {formatPercent(modelInputs.cash_vol_annual)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </AssumptionGroup>

        {/* Spending Parameters */}
        <AssumptionGroup title="Spending & Inflation">
          <AssumptionRow 
            label="Monthly Spending"
            value={formatCurrency(Math.abs(modelInputs.monthly_spending))}
            note={`${formatCurrency(Math.abs(modelInputs.monthly_spending) * 12)}/year`}
          />
          <AssumptionRow 
            label="Spending Strategy"
            value={modelInputs.spending_rule === 1 ? 'Fixed (Inflation-Adjusted)' : 'Variable (Portfolio %)'}
          />
          {modelInputs.spending_rule === 2 && (
            <AssumptionRow 
              label="Withdrawal Rate"
              value={formatPercent(modelInputs.spending_pct_annual)}
            />
          )}
          <AssumptionRow 
            label="Inflation Rate"
            value={formatPercent(modelInputs.inflation_annual)}
          />
          {modelInputs.use_lifestyle_phases && (
            <div className="mt-4 p-4 bg-background-base bg-opacity-30 rounded border border-background-border">
              <p className="text-small text-text-secondary mb-2">
                <strong>Lifestyle Phases Active:</strong>
              </p>
              <ul className="text-small text-text-tertiary space-y-1 ml-4">
                <li>• Go-Go Years (to age {modelInputs.go_go_end_age}): {formatPercent(modelInputs.go_go_spending_multiplier)} of base spending</li>
                <li>• Slow-Go Years (to age {modelInputs.slow_go_end_age}): {formatPercent(modelInputs.slow_go_spending_multiplier)} of base spending</li>
                <li>• No-Go Years: {formatPercent(modelInputs.no_go_spending_multiplier)} of base spending</li>
              </ul>
            </div>
          )}
        </AssumptionGroup>

        {/* Income Sources */}
        {(modelInputs.social_security_monthly > 0 || 
          modelInputs.pension_monthly > 0 || 
          modelInputs.regular_income_monthly > 0 ||
          modelInputs.other_income_monthly > 0) && (
          <AssumptionGroup title="Income Sources">
            {modelInputs.social_security_monthly > 0 && (
              <AssumptionRow 
                label="Social Security"
                value={formatCurrency(modelInputs.social_security_monthly)}
                note={`Starting at age ${modelInputs.ss_start_age}`}
              />
            )}
            {modelInputs.pension_monthly > 0 && (
              <AssumptionRow 
                label="Pension Income"
                value={formatCurrency(modelInputs.pension_monthly)}
                note={`Starting at age ${modelInputs.pension_start_age}`}
              />
            )}
            {modelInputs.regular_income_monthly > 0 && (
              <AssumptionRow 
                label="Regular Income"
                value={formatCurrency(modelInputs.regular_income_monthly)}
                note="Throughout planning period"
              />
            )}
            {modelInputs.other_income_monthly > 0 && (
              <AssumptionRow 
                label="Other Income"
                value={formatCurrency(modelInputs.other_income_monthly)}
                note={`Starting at age ${modelInputs.other_income_start_age}`}
              />
            )}
          </AssumptionGroup>
        )}

        {/* Tax Considerations */}
        <AssumptionGroup title="Tax Considerations">
          <AssumptionRow 
            label="Taxable Accounts"
            value={formatPercent(modelInputs.taxable_pct)}
          />
          <AssumptionRow 
            label="Traditional IRA/401(k)"
            value={formatPercent(modelInputs.ira_pct)}
          />
          <AssumptionRow 
            label="Roth IRA/401(k)"
            value={formatPercent(modelInputs.roth_pct)}
          />
          <AssumptionRow 
            label="Assumed Tax Rate"
            value={formatPercent(modelInputs.tax_rate)}
          />
          <AssumptionRow 
            label="RMD Starting Age"
            value={`${modelInputs.rmd_age} years old`}
          />
        </AssumptionGroup>

        {/* Healthcare */}
        {modelInputs.healthcare_monthly > 0 && (
          <AssumptionGroup title="Healthcare Costs">
            <AssumptionRow 
              label="Monthly Healthcare Costs"
              value={formatCurrency(modelInputs.healthcare_monthly)}
              note={`Starting at age ${modelInputs.healthcare_start_age}`}
            />
            <AssumptionRow 
              label="Healthcare Inflation"
              value={formatPercent(modelInputs.healthcare_inflation)}
            />
          </AssumptionGroup>
        )}

        {/* Simulation Settings */}
        <AssumptionGroup title="Simulation Parameters">
          <AssumptionRow 
            label="Number of Scenarios"
            value={modelInputs.n_scenarios.toLocaleString()}
          />
          <AssumptionRow 
            label="Analysis Method"
            value="Monte Carlo Simulation"
            note="Stochastic modeling with geometric Brownian motion"
          />
        </AssumptionGroup>
      </div>
    </div>
  );
};

interface AssumptionGroupProps {
  title: string;
  children: React.ReactNode;
}

const AssumptionGroup: React.FC<AssumptionGroupProps> = ({ title, children }) => {
  return (
    <div className="bg-background-elevated border border-background-border rounded-lg p-6 print:p-4">
      <h3 className="text-h3 font-display text-text-primary mb-4 pb-3 border-b border-background-border print:text-lg">
        {title}
      </h3>
      <div className="space-y-3">
        {children}
      </div>
    </div>
  );
};

interface AssumptionRowProps {
  label: string;
  value: string;
  note?: string;
}

const AssumptionRow: React.FC<AssumptionRowProps> = ({ label, value, note }) => {
  return (
    <div className="flex items-start justify-between py-2">
      <div className="flex-1">
        <p className="text-body text-text-tertiary">{label}</p>
        {note && <p className="text-small text-text-secondary mt-1">{note}</p>}
      </div>
      <p className="text-body font-medium text-text-primary ml-4">{value}</p>
    </div>
  );
};
