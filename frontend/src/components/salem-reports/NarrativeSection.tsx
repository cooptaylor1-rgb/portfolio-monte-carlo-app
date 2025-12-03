/**
 * Narrative Section Component
 * Display findings, risks, and recommendations in a professional format
 */
import React from 'react';
import type { NarrativeBlock } from '../../types/reports';

interface NarrativeSectionProps {
  narrative: NarrativeBlock;
}

export const NarrativeSection: React.FC<NarrativeSectionProps> = ({ narrative }) => {
  return (
    <section className="salem-section">
      <h2>Analysis & Recommendations</h2>
      
      <div className="salem-card">
        <h3>Key Findings</h3>
        <ul>
          {narrative.key_findings.map((finding, index) => (
            <li key={index}>{finding}</li>
          ))}
        </ul>
      </div>

      <div className="salem-card">
        <h3>Risk Considerations</h3>
        <ul>
          {narrative.key_risks.map((risk, index) => (
            <li key={index}>{risk}</li>
          ))}
        </ul>
      </div>

      <div className="salem-card">
        <h3>Recommendations</h3>
        <ul>
          {narrative.recommendations.map((rec, index) => (
            <li key={index}>{rec}</li>
          ))}
        </ul>
      </div>
    </section>
  );
};
