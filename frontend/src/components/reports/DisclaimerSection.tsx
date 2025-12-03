/**
 * DisclaimerSection Component
 * Important disclosures and limitations for financial reports
 */
import React from 'react';
import { AlertCircle } from 'lucide-react';

export const DisclaimerSection: React.FC = () => {
  return (
    <div className="report-section print:break-before-page">
      <div className="bg-background-base border-t-4 border-accent-navy rounded-lg p-8 print:p-6">
        <div className="flex items-start gap-4 mb-6">
          <AlertCircle size={24} className="text-accent-navy flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-h2 font-display text-text-primary mb-2 print:text-xl">
              Important Disclosures
            </h2>
            <p className="text-body text-text-tertiary">
              Please review these important limitations and considerations carefully
            </p>
          </div>
        </div>

        <div className="space-y-6 text-body text-text-primary leading-relaxed">
          <Section title="Purpose and Limitations">
            <p>
              This Monte Carlo analysis is provided for illustrative and educational purposes only. 
              It is not a guarantee of future performance and should not be considered as investment advice, 
              a recommendation to buy or sell securities, or a representation that any particular outcome 
              will be achieved.
            </p>
          </Section>

          <Section title="Simulation Methodology">
            <p>
              The projections are based on Monte Carlo simulation, which uses random sampling and statistical 
              modeling to estimate a range of possible outcomes. While this methodology incorporates market 
              volatility and uncertainty, it relies on historical data and assumptions that may not reflect 
              future market conditions. Actual results may differ materially from these projections.
            </p>
          </Section>

          <Section title="Assumptions and Inputs">
            <p>
              All projections depend on the accuracy of input assumptions, including expected returns, 
              volatility, inflation rates, spending patterns, and time horizons. Small changes in these 
              assumptions can significantly affect outcomes. Return and volatility assumptions are based 
              on long-term historical averages and may not represent future market conditions.
            </p>
          </Section>

          <Section title="Market Risk and Volatility">
            <p>
              Financial markets are subject to significant volatility and uncertainty. Past performance 
              is not indicative of future results. Market conditions, economic factors, geopolitical events, 
              and other variables can cause actual returns to differ significantly from projected returns. 
              The analysis assumes normal market conditions and may not adequately capture extreme events 
              or "black swan" scenarios.
            </p>
          </Section>

          <Section title="Sequence of Returns Risk">
            <p>
              The order and timing of investment returns can significantly impact portfolio longevity, 
              particularly during the early years of retirement. Experiencing poor returns early in the 
              withdrawal phase can materially reduce the probability of success, even if long-term average 
              returns match projections.
            </p>
          </Section>

          <Section title="Tax Considerations">
            <p>
              This analysis incorporates simplified tax assumptions and may not reflect the full complexity 
              of individual tax situations. Actual tax liability depends on numerous factors including income 
              levels, deductions, credits, state taxes, and changes in tax law. Consult with a qualified tax 
              professional for personalized tax advice.
            </p>
          </Section>

          <Section title="Inflation and Purchasing Power">
            <p>
              All dollar amounts are shown in today's dollars adjusted for assumed inflation. Actual inflation 
              rates may vary significantly from assumptions, affecting real purchasing power and required spending 
              levels. Healthcare costs, in particular, have historically inflated faster than general inflation.
            </p>
          </Section>

          <Section title="Regular Review Required">
            <p>
              Financial plans should be reviewed and updated regularly—at least annually or following significant 
              life events, market changes, or changes in goals. This analysis represents a snapshot based on current 
              information and assumptions. Circumstances change, and plans should evolve accordingly.
            </p>
          </Section>

          <Section title="Professional Advice">
            <p>
              This analysis does not replace the need for comprehensive financial planning and professional advice. 
              We recommend working with qualified financial advisors, tax professionals, and legal counsel to develop 
              and implement a complete financial strategy tailored to your specific circumstances, goals, and risk tolerance.
            </p>
          </Section>

          <Section title="No Guarantee of Results">
            <p>
              Neither the preparer of this analysis nor any affiliated persons guarantee the accuracy or completeness 
              of the information provided or the success of any strategy described herein. All investing involves risk, 
              including the potential loss of principal. There is no guarantee that any investment strategy will achieve 
              its objectives or avoid losses.
            </p>
          </Section>
        </div>

        <div className="mt-8 pt-6 border-t border-background-border text-center">
          <p className="text-small text-text-tertiary">
            <strong>Questions?</strong> Please contact your financial advisor to discuss this analysis and how it relates to your specific situation.
          </p>
        </div>
      </div>
    </div>
  );
};

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

const Section: React.FC<SectionProps> = ({ title, children }) => {
  return (
    <div>
      <h3 className="text-h4 font-semibold text-text-primary mb-2 print:text-base">
        {title}
      </h3>
      <div className="text-text-secondary">
        {children}
      </div>
    </div>
  );
};
