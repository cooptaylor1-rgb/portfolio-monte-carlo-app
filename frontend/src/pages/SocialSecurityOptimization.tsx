/**
 * Social Security Optimization Page
 * ================================
 * 
 * Comprehensive tool to determine optimal Social Security claiming strategies
 * for individuals and couples. Analyzes trade-offs between early claiming with
 * investment vs. delayed claiming for higher benefits.
 */

import React, { useState, useMemo } from 'react';
import { DollarSign, Users, Calculator, TrendingUp, HelpCircle } from 'lucide-react';
import {
  Card,
  Button,
  SectionHeader,
  Tooltip,
  LoadingSkeleton,
  Alert,
} from '../components/ui';

// Types
interface PersonInput {
  birth_year: number;
  birth_month: number;
  gender: 'male' | 'female' | 'other';
  benefit_at_fra: number;
  claiming_age_years: number;
  claiming_age_months: number;
}

interface Assumptions {
  investment_return_annual: number;
  inflation_annual: number;
  cola_annual: number;
  discount_rate_real: number;
  marginal_tax_rate: number;
  ss_taxable_portion: number;
  life_expectancy_override?: number;
}

interface ClaimingScenario {
  claiming_age: number;
  claiming_age_display: string;
  monthly_benefit_initial: number;
  annual_benefit_initial: number;
  benefit_stream: {
    ages: number[];
    annual_benefits_gross: number[];
    annual_benefits_net: number[];
    cumulative_gross: number[];
    cumulative_net: number[];
    cumulative_invested: number[];
  };
  npv_gross: number;
  npv_net: number;
  break_even_age?: number;
  break_even_age_display?: string;
  cumulative_at_75?: number;
  cumulative_at_80?: number;
  cumulative_at_85?: number;
  cumulative_at_90?: number;
}

interface IndividualAnalysisResponse {
  success: boolean;
  message: string;
  birth_year: number;
  birth_month: number;
  gender: string;
  fra_years: number;
  fra_months: number;
  fra_display: string;
  life_expectancy: number;
  primary_scenario: ClaimingScenario;
  comparison_scenarios: ClaimingScenario[];
  optimal_claiming_age: number;
  recommended_range_min: number;
  recommended_range_max: number;
  recommendation_notes: string[];
}

const SocialSecurityOptimization: React.FC = () => {
  const [mode, setMode] = useState<'individual' | 'couple'>('individual');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<IndividualAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Individual form state
  const [birthYear, setBirthYear] = useState<number>(1960);
  const [birthMonth, setBirthMonth] = useState<number>(6);
  const [gender, setGender] = useState<'male' | 'female' | 'other'>('male');
  const [benefitAtFra, setBenefitAtFra] = useState<number>(2500);
  const [claimingAge, setClaimingAge] = useState<number>(67);
  const [compareAges, setCompareAges] = useState<boolean>(true);

  // Assumptions
  const [investmentReturn, setInvestmentReturn] = useState<number>(5.0);
  const [cola, setCola] = useState<number>(2.5);
  const [taxRate, setTaxRate] = useState<number>(22);
  const [lifeExpectancy, setLifeExpectancy] = useState<number | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);

    try {
      const requestBody = {
        person: {
          birth_year: birthYear,
          birth_month: birthMonth,
          gender,
          benefit_at_fra: benefitAtFra,
          claiming_age_years: claimingAge,
          claiming_age_months: 0,
        },
        assumptions: {
          investment_return_annual: investmentReturn / 100,
          inflation_annual: 0.025,
          cola_annual: cola / 100,
          discount_rate_real: 0.02,
          marginal_tax_rate: taxRate / 100,
          ss_taxable_portion: 0.85,
          life_expectancy_override: lifeExpectancy || undefined,
        },
        compare_ages: compareAges ? [62, 65, 67, 70] : undefined,
      };

      const response = await fetch('/api/social-security/analyze-individual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data: IndividualAnalysisResponse = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const currentYear = new Date().getFullYear();

  return (
    <div className="space-y-6 lg:space-y-8">
      {/* Page Header */}
      <SectionHeader
        title="Social Security Optimization"
        description="Determine the optimal claiming strategy to maximize lifetime benefits"
        icon={<DollarSign size={28} />}
      />

      {/* Mode Toggle */}
      <Card padding="none" variant="default">
        <div className="flex border-b border-neutral-soft">
          <button
            onClick={() => setMode('individual')}
            className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
              mode === 'individual'
                ? 'text-accent-gold border-b-2 border-accent-gold bg-neutral-lighter'
                : 'text-text-secondary hover:text-text-primary hover:bg-neutral-lighter'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <Calculator size={18} />
              Individual Analysis
            </div>
          </button>
          <button
            onClick={() => setMode('couple')}
            className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
              mode === 'couple'
                ? 'text-accent-gold border-b-2 border-accent-gold bg-neutral-lighter'
                : 'text-text-secondary hover:text-text-primary hover:bg-neutral-lighter'
            }`}
          >
            <div className="flex items-center justify-center gap-2">
              <Users size={18} />
              Couple Analysis
            </div>
          </button>
        </div>
      </Card>

      {mode === 'individual' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Inputs */}
          <div className="space-y-6">
            {/* Personal Information */}
            <Card padding="lg" variant="default">
              <h3 className="text-h4 font-display font-bold text-text-primary mb-4">
                Personal Information
              </h3>

              <div className="space-y-4">
                {/* Birth Date */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Birth Year
                    </label>
                    <input
                      type="number"
                      min={1940}
                      max={currentYear - 18}
                      value={birthYear}
                      onChange={(e) => setBirthYear(parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-neutral-soft rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-1">
                      Birth Month
                    </label>
                    <select
                      value={birthMonth}
                      onChange={(e) => setBirthMonth(parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-neutral-soft rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                    >
                      {Array.from({ length: 12 }, (_, i) => (
                        <option key={i + 1} value={i + 1}>
                          {new Date(2000, i).toLocaleString('default', { month: 'long' })}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Gender */}
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">
                    Gender (for life expectancy)
                  </label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value as 'male' | 'female' | 'other')}
                    className="w-full px-3 py-2 border border-neutral-soft rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                {/* Benefit at FRA */}
                <div>
                  <label className="flex items-center gap-1 text-sm font-medium text-text-secondary mb-1">
                    Monthly Benefit at Full Retirement Age
                    <Tooltip content="Your estimated monthly benefit at FRA from SSA.gov">
                      <HelpCircle size={14} className="text-text-muted" />
                    </Tooltip>
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-2.5 text-text-muted">$</span>
                    <input
                      type="number"
                      min={500}
                      max={5000}
                      step={50}
                      value={benefitAtFra}
                      onChange={(e) => setBenefitAtFra(parseFloat(e.target.value))}
                      className="w-full pl-8 pr-3 py-2 border border-neutral-soft rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                    />
                  </div>
                  <p className="text-xs text-text-muted mt-1">
                    Annual: {formatCurrency(benefitAtFra * 12)}
                  </p>
                </div>

                {/* Claiming Age */}
                <div>
                  <label className="flex items-center gap-1 text-sm font-medium text-text-secondary mb-1">
                    Claiming Age
                    <Tooltip content="Age at which you plan to claim Social Security">
                      <HelpCircle size={14} className="text-text-muted" />
                    </Tooltip>
                  </label>
                  <input
                    type="range"
                    min={62}
                    max={70}
                    value={claimingAge}
                    onChange={(e) => setClaimingAge(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-text-secondary mt-1">
                    <span>62</span>
                    <span className="font-bold text-accent-gold">{claimingAge}</span>
                    <span>70</span>
                  </div>
                </div>

                {/* Life Expectancy Override */}
                <div>
                  <label className="flex items-center gap-1 text-sm font-medium text-text-secondary mb-1">
                    Life Expectancy Override (optional)
                    <Tooltip content="Leave blank to use SSA actuarial tables">
                      <HelpCircle size={14} className="text-text-muted" />
                    </Tooltip>
                  </label>
                  <input
                    type="number"
                    min={70}
                    max={120}
                    value={lifeExpectancy || ''}
                    onChange={(e) => setLifeExpectancy(e.target.value ? parseInt(e.target.value) : null)}
                    placeholder="Auto (actuarial table)"
                    className="w-full px-3 py-2 border border-neutral-soft rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                  />
                </div>
              </div>
            </Card>

            {/* Assumptions */}
            <Card padding="lg" variant="default">
              <h3 className="text-h4 font-display font-bold text-text-primary mb-4">
                Economic Assumptions
              </h3>

              <div className="space-y-4">
                {/* Investment Return */}
                <div>
                  <label className="flex items-center gap-1 text-sm font-medium text-text-secondary mb-1">
                    Investment Return (%)
                    <Tooltip content="Annual return if benefits are invested">
                      <HelpCircle size={14} className="text-text-muted" />
                    </Tooltip>
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={15}
                    step={0.5}
                    value={investmentReturn}
                    onChange={(e) => setInvestmentReturn(parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-neutral-soft rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                  />
                </div>

                {/* COLA */}
                <div>
                  <label className="flex items-center gap-1 text-sm font-medium text-text-secondary mb-1">
                    COLA Rate (%)
                    <Tooltip content="Social Security cost-of-living adjustments">
                      <HelpCircle size={14} className="text-text-muted" />
                    </Tooltip>
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={10}
                    step={0.1}
                    value={cola}
                    onChange={(e) => setCola(parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-neutral-soft rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                  />
                </div>

                {/* Tax Rate */}
                <div>
                  <label className="flex items-center gap-1 text-sm font-medium text-text-secondary mb-1">
                    Marginal Tax Rate (%)
                    <Tooltip content="Tax rate on ordinary income">
                      <HelpCircle size={14} className="text-text-muted" />
                    </Tooltip>
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={50}
                    step={1}
                    value={taxRate}
                    onChange={(e) => setTaxRate(parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-neutral-soft rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-gold"
                  />
                </div>

                {/* Compare Ages */}
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="compare-ages"
                    checked={compareAges}
                    onChange={(e) => setCompareAges(e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="compare-ages" className="text-sm text-text-secondary">
                    Compare multiple claiming ages (62, 65, 67, 70)
                  </label>
                </div>
              </div>
            </Card>

            {/* Analyze Button */}
            <Button
              onClick={handleAnalyze}
              variant="primary"
              size="lg"
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Analyzing...
                </>
              ) : (
                <>
                  <Calculator size={18} className="mr-2" />
                  Analyze Claiming Strategy
                </>
              )}
            </Button>
          </div>

          {/* Right Column: Results */}
          <div className="space-y-6">
            {loading && (
              <Card padding="lg" variant="default">
                <LoadingSkeleton count={10} />
              </Card>
            )}

            {error && (
              <Alert variant="error" title="Analysis Error">
                {error}
              </Alert>
            )}

            {results && !loading && (
              <>
                {/* Summary */}
                <Card padding="lg" variant="success">
                  <h3 className="text-h4 font-display font-bold text-text-primary mb-2">
                    Recommendation
                  </h3>
                  <p className="text-lg text-text-secondary mb-3">
                    Optimal Claiming Age: <strong className="text-accent-gold">{Math.floor(results.optimal_claiming_age)}</strong>
                  </p>
                  <p className="text-sm text-text-secondary mb-2">
                    Recommended Range: {results.recommended_range_min}-{results.recommended_range_max} years
                  </p>
                  <div className="mt-4 space-y-2">
                    {results.recommendation_notes.map((note, idx) => (
                      <p key={idx} className="text-sm text-text-secondary flex items-start gap-2">
                        <TrendingUp size={16} className="text-accent-gold mt-0.5 flex-shrink-0" />
                        <span>{note}</span>
                      </p>
                    ))}
                  </div>
                </Card>

                {/* FRA Info */}
                <Card padding="lg" variant="default">
                  <h3 className="text-h4 font-display font-bold text-text-primary mb-3">
                    Your Information
                  </h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-text-muted">Full Retirement Age:</span>
                      <p className="text-text-primary font-medium">{results.fra_display}</p>
                    </div>
                    <div>
                      <span className="text-text-muted">Life Expectancy:</span>
                      <p className="text-text-primary font-medium">{results.life_expectancy} years</p>
                    </div>
                  </div>
                </Card>

                {/* Primary Scenario */}
                <Card padding="lg" variant="default">
                  <h3 className="text-h4 font-display font-bold text-text-primary mb-3">
                    Claiming at Age {results.primary_scenario.claiming_age_display}
                  </h3>
                  
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-xs text-text-muted">Monthly Benefit</span>
                        <p className="text-h5 font-bold text-accent-gold">
                          {formatCurrency(results.primary_scenario.monthly_benefit_initial)}
                        </p>
                      </div>
                      <div>
                        <span className="text-xs text-text-muted">Annual Benefit</span>
                        <p className="text-h5 font-bold text-text-primary">
                          {formatCurrency(results.primary_scenario.annual_benefit_initial)}
                        </p>
                      </div>
                    </div>

                    <div className="border-t border-neutral-soft pt-3">
                      <span className="text-xs text-text-muted">Net Present Value (NPV)</span>
                      <p className="text-h5 font-bold text-success-dark">
                        {formatCurrency(results.primary_scenario.npv_net)}
                      </p>
                    </div>

                    {results.primary_scenario.break_even_age && (
                      <div className="border-t border-neutral-soft pt-3">
                        <span className="text-xs text-text-muted">Break-Even Age</span>
                        <p className="text-base font-medium text-text-primary">
                          {results.primary_scenario.break_even_age_display}
                        </p>
                      </div>
                    )}

                    <div className="border-t border-neutral-soft pt-3">
                      <span className="text-xs text-text-muted block mb-2">Cumulative Benefits</span>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        {results.primary_scenario.cumulative_at_75 && (
                          <div>
                            <span className="text-text-muted">Age 75:</span>{' '}
                            <span className="font-medium">{formatCurrency(results.primary_scenario.cumulative_at_75)}</span>
                          </div>
                        )}
                        {results.primary_scenario.cumulative_at_80 && (
                          <div>
                            <span className="text-text-muted">Age 80:</span>{' '}
                            <span className="font-medium">{formatCurrency(results.primary_scenario.cumulative_at_80)}</span>
                          </div>
                        )}
                        {results.primary_scenario.cumulative_at_85 && (
                          <div>
                            <span className="text-text-muted">Age 85:</span>{' '}
                            <span className="font-medium">{formatCurrency(results.primary_scenario.cumulative_at_85)}</span>
                          </div>
                        )}
                        {results.primary_scenario.cumulative_at_90 && (
                          <div>
                            <span className="text-text-muted">Age 90:</span>{' '}
                            <span className="font-medium">{formatCurrency(results.primary_scenario.cumulative_at_90)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Comparison Scenarios */}
                {results.comparison_scenarios.length > 0 && (
                  <Card padding="lg" variant="default">
                    <h3 className="text-h4 font-display font-bold text-text-primary mb-3">
                      Comparison Scenarios
                    </h3>
                    <div className="space-y-3">
                      {results.comparison_scenarios.map((scenario) => (
                        <div
                          key={scenario.claiming_age}
                          className="border border-neutral-soft rounded-lg p-3"
                        >
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <span className="text-sm font-medium">Age {scenario.claiming_age_display}</span>
                              <p className="text-xs text-text-muted">
                                {formatCurrency(scenario.monthly_benefit_initial)}/month
                              </p>
                            </div>
                            <div className="text-right">
                              <span className="text-xs text-text-muted">NPV</span>
                              <p className="text-sm font-bold text-success-dark">
                                {formatCurrency(scenario.npv_net)}
                              </p>
                            </div>
                          </div>
                          {scenario.break_even_age_display && (
                            <p className="text-xs text-text-muted">
                              Break-even: {scenario.break_even_age_display}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </Card>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {mode === 'couple' && (
        <Card padding="lg" variant="default">
          <Alert variant="info" title="Coming Soon">
            Couple analysis is currently under development. Use individual analysis for now.
          </Alert>
        </Card>
      )}
    </div>
  );
};

export default SocialSecurityOptimization;
