/**
 * Narrative Section Component
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import type { NarrativeBlock } from '../../types/reports';
import { colors } from '../../theme';

interface NarrativeSectionProps {
  narrative: NarrativeBlock;
}

export const NarrativeSection: React.FC<NarrativeSectionProps> = ({ narrative }) => {
  return (
    <section className="salem-section">
      <h2 className="text-h2 font-display text-text-primary mb-6">Analysis & Recommendations</h2>
      
      <div className="salem-card" style={{ 
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border 
      }}>
        <h3 className="text-h3 font-display text-text-primary mb-4">Key Findings</h3>
        <ul className="text-body text-text-secondary space-y-2">
          {narrative.key_findings.map((finding, index) => (
            <li key={index}>{finding}</li>
          ))}
        </ul>
      </div>

      <div className="salem-card" style={{ 
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border 
      }}>
        <h3 className="text-h3 font-display text-text-primary mb-4">Risk Considerations</h3>
        <ul className="text-body text-text-secondary space-y-2">
          {narrative.key_risks.map((risk, index) => (
            <li key={index}>{risk}</li>
          ))}
        </ul>
      </div>

      <div className="salem-card" style={{ 
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border 
      }}>
        <h3 className="text-h3 font-display text-text-primary mb-4">Recommendations</h3>
        <ul className="text-body text-text-secondary space-y-2">
          {narrative.recommendations.map((rec, index) => (
            <li key={index}>{rec}</li>
          ))}
        </ul>
      </div>
    </section>
  );
};
