/**
 * Report Formatting Utilities
 * Professional formatting functions for advisor-grade reports
 */

/**
 * Format a number as currency with proper commas and no decimals
 */
export const formatCurrency = (value: number, decimals: number = 0): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

/**
 * Format a number as a percentage with specified precision
 */
export const formatPercent = (value: number, decimals: number = 1): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

/**
 * Format a date string for report display
 */
export const formatReportDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
};

/**
 * Format current timestamp for report generation
 */
export const formatGeneratedDate = (): string => {
  return new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

/**
 * Determine success probability rating category
 */
export const getSuccessRating = (probability: number): {
  label: string;
  variant: 'success' | 'warning' | 'error';
  color: string;
} => {
  if (probability >= 0.85) {
    return { label: 'Strong', variant: 'success', color: '#4CAF50' };
  }
  if (probability >= 0.70) {
    return { label: 'Moderate', variant: 'warning', color: '#FFC107' };
  }
  return { label: 'Low', variant: 'error', color: '#D9534F' };
};

/**
 * Generate narrative key findings based on simulation metrics
 */
export const generateKeyFindings = (
  successProbability: number,
  medianEnding: number,
  p10Ending: number,
  depletionProbability: number,
  startingPortfolio: number
): string[] => {
  const findings: string[] = [];

  // Success probability finding
  const rating = getSuccessRating(successProbability);
  findings.push(
    `Plan shows ${rating.label.toLowerCase()} success probability of ${formatPercent(successProbability)} ` +
    `based on ${successProbability >= 0.85 ? 'conservative' : successProbability >= 0.70 ? 'moderate' : 'aggressive'} assumptions.`
  );

  // Portfolio growth/decline finding
  const medianChange = ((medianEnding - startingPortfolio) / startingPortfolio);
  if (medianChange > 0.50) {
    findings.push(
      `Median scenario projects substantial portfolio growth to ${formatCurrency(medianEnding)}, ` +
      `representing a ${formatPercent(medianChange)} increase from starting value.`
    );
  } else if (medianChange > 0) {
    findings.push(
      `Median scenario projects modest portfolio growth to ${formatCurrency(medianEnding)}.`
    );
  } else if (medianChange > -0.30) {
    findings.push(
      `Median scenario projects controlled portfolio decline to ${formatCurrency(medianEnding)}, ` +
      `within acceptable spend-down range.`
    );
  } else {
    findings.push(
      `Median scenario projects significant portfolio depletion to ${formatCurrency(medianEnding)}, ` +
      `indicating spending may exceed sustainable levels.`
    );
  }

  // Downside risk finding
  if (depletionProbability > 0.20) {
    findings.push(
      `Elevated depletion risk of ${formatPercent(depletionProbability)} suggests ` +
      `plan may be sensitive to market downturns or spending shocks.`
    );
  } else if (p10Ending < startingPortfolio * 0.25) {
    findings.push(
      `In adverse scenarios (10th percentile), portfolio could decline to ${formatCurrency(p10Ending)}, ` +
      `requiring contingency planning.`
    );
  }

  return findings;
};

/**
 * Generate risk assessment narrative
 */
export const generateRiskAssessment = (
  successProbability: number,
  depletionProbability: number,
  shortfallRisk: number,
  equityPct: number
): string[] => {
  const risks: string[] = [];

  // Success probability risk
  if (successProbability < 0.70) {
    risks.push(
      `Current plan success probability of ${formatPercent(successProbability)} falls below ` +
      `recommended thresholds, indicating meaningful risk of not meeting objectives.`
    );
  }

  // Depletion risk
  if (depletionProbability > 0.15) {
    risks.push(
      `Portfolio depletion risk of ${formatPercent(depletionProbability)} requires monitoring ` +
      `and potential adjustments to spending or allocation strategy.`
    );
  }

  // Shortfall risk
  if (shortfallRisk > 0.25) {
    risks.push(
      `Shortfall risk of ${formatPercent(shortfallRisk)} suggests material uncertainty ` +
      `around meeting all financial goals as currently defined.`
    );
  }

  // Allocation-related risk
  if (equityPct > 0.80) {
    risks.push(
      `Aggressive equity allocation of ${formatPercent(equityPct)} increases exposure ` +
      `to market volatility and sequence-of-returns risk.`
    );
  } else if (equityPct < 0.30) {
    risks.push(
      `Conservative equity allocation of ${formatPercent(equityPct)} may limit growth ` +
      `potential and increase longevity/inflation risk.`
    );
  }

  // Add generic risk if no specific concerns
  if (risks.length === 0) {
    risks.push(
      `Plan demonstrates manageable risk profile with reasonable probability of success ` +
      `and adequate downside protection.`
    );
  }

  return risks;
};

/**
 * Generate recommendations based on success probability
 */
export const generateRecommendations = (
  successProbability: number,
  depletionProbability: number,
  medianEnding: number,
  startingPortfolio: number,
  monthlySpending: number,
  equityPct: number
): string[] => {
  const recommendations: string[] = [];

  if (successProbability < 0.70) {
    // Low success - urgent recommendations
    recommendations.push(
      'Consider reducing annual spending by 10-15% to improve plan sustainability.'
    );
    recommendations.push(
      'Explore opportunities to increase income through part-time work or deferred retirement.'
    );
    recommendations.push(
      'Review allocation strategy with advisor to ensure appropriate risk/return profile.'
    );
    recommendations.push(
      'Develop contingency plans for flexible spending categories that can be reduced if needed.'
    );
  } else if (successProbability < 0.85) {
    // Moderate success - optimization recommendations
    recommendations.push(
      'Continue current strategy with annual monitoring and periodic rebalancing.'
    );
    recommendations.push(
      'Consider stress-testing plan against various market scenarios and inflation rates.'
    );
    recommendations.push(
      'Maintain spending flexibility to adjust in response to market conditions.'
    );
    recommendations.push(
      'Review plan annually or after major life events to ensure alignment with goals.'
    );
  } else {
    // Strong success - opportunity recommendations
    const surplus = medianEnding - startingPortfolio;
    if (surplus > startingPortfolio * 0.50) {
      recommendations.push(
        'Plan shows significant margin of success; consider enhancing lifestyle spending or legacy goals.'
      );
      recommendations.push(
        'Explore tax-efficient gifting strategies to transfer wealth during lifetime.'
      );
    }
    recommendations.push(
      'Review estate planning documents to ensure they reflect current intentions.'
    );
    recommendations.push(
      'Consider charitable giving opportunities aligned with values and tax objectives.'
    );
    recommendations.push(
      'Maintain diversified portfolio with regular rebalancing to target allocation.'
    );
  }

  return recommendations;
};

/**
 * Generate stress test narrative
 */
export const generateStressTestNarrative = (
  baseSuccess: number,
  stressSuccess: number,
  scenarioName: string
): string => {
  const delta = stressSuccess - baseSuccess;
  const deltaPercent = formatPercent(Math.abs(delta));

  if (Math.abs(delta) < 0.05) {
    return `Plan remains resilient under ${scenarioName} scenario with minimal impact on success probability.`;
  } else if (delta < 0) {
    const severity = Math.abs(delta) > 0.20 ? 'significantly' : Math.abs(delta) > 0.10 ? 'materially' : 'modestly';
    return `${scenarioName} scenario ${severity} reduces success probability by ${deltaPercent}, ` +
           `highlighting sensitivity to this risk factor.`;
  } else {
    return `Interestingly, ${scenarioName} scenario improves outcomes, though base case remains primary planning assumption.`;
  }
};

/**
 * Format age range for display
 */
export const formatAgeRange = (startAge: number, endAge: number): string => {
  return `${startAge}-${endAge} years old`;
};

/**
 * Format time horizon
 */
export const formatTimeHorizon = (years: number): string => {
  if (years === 1) return '1 year';
  return `${years} years`;
};

/**
 * Generate spending summary text
 */
export const formatSpendingSummary = (
  monthlySpending: number,
  inflationRate: number,
  spendingRule: 1 | 2
): string => {
  const annualSpending = Math.abs(monthlySpending * 12);
  const ruleText = spendingRule === 1 ? 'Fixed (inflation-adjusted)' : 'Variable (portfolio %)';
  
  return `${formatCurrency(annualSpending)}/year (${formatCurrency(Math.abs(monthlySpending))}/month) · ` +
         `${ruleText} · ${formatPercent(inflationRate)} annual inflation`;
};
