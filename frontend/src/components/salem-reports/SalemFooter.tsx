/**
 * Salem Footer Component
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import { colors } from '../../theme';

export const SalemFooter: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="salem-footer" style={{ borderTopColor: colors.background.border }}>
      <div className="text-body text-text-primary font-medium mb-3">
        <strong>Salem Investment Counselors</strong>
      </div>
      <div className="text-small text-text-tertiary leading-relaxed">
        This report is for informational purposes only and does not constitute investment advice. 
        Past performance does not guarantee future results. Projections are based on assumptions 
        that may not materialize. Please consult with your financial advisor before making investment decisions.
      </div>
      <div className="text-small text-text-tertiary mt-3">
        © {currentYear} Salem Investment Counselors. All rights reserved.
      </div>
    </footer>
  );
};
