/**
 * Salem Footer Component
 * Professional footer with disclaimers and firm information
 */
import React from 'react';

export const SalemFooter: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="salem-footer">
      <div style={{ marginBottom: 'var(--salem-spacing-sm)' }}>
        <strong>Salem Investment Counselors</strong>
      </div>
      <div style={{ fontSize: 'var(--salem-text-xs)', color: 'var(--salem-gray-500)' }}>
        This report is for informational purposes only and does not constitute investment advice. 
        Past performance does not guarantee future results. Projections are based on assumptions 
        that may not materialize. Please consult with your financial advisor before making investment decisions.
      </div>
      <div style={{ marginTop: 'var(--salem-spacing-sm)', fontSize: 'var(--salem-text-xs)' }}>
        © {currentYear} Salem Investment Counselors. All rights reserved.
      </div>
    </footer>
  );
};
