/**
 * Appendix Section Component
 * Phase 7: Updated with design system styling
 */
import React from 'react';
import type { AppendixItem } from '../../types/reports';
import { colors } from '../../theme';

interface AppendixSectionProps {
  items: AppendixItem[];
}

export const AppendixSection: React.FC<AppendixSectionProps> = ({ items }) => {
  return (
    <section className="salem-section">
      <h2 className="text-h2 font-display text-text-primary mb-6">Appendix</h2>
      
      {items.map((item, index) => (
        <div 
          key={index} 
          className="salem-card"
          style={{ 
            backgroundColor: colors.background.elevated,
            borderColor: colors.background.border 
          }}
        >
          <h3 className="text-h3 font-display text-text-primary mb-4">{item.title}</h3>
          {item.content.map((paragraph, pIndex) => (
            <p key={pIndex} className="text-body text-text-secondary mb-4 last:mb-0">
              {paragraph}
            </p>
          ))}
        </div>
      ))}
    </section>
  );
};
