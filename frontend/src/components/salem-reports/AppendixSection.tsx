/**
 * Appendix Section Component
 * Display methodology, disclaimers, and additional information
 */
import React from 'react';
import type { AppendixItem } from '../../types/reports';

interface AppendixSectionProps {
  items: AppendixItem[];
}

export const AppendixSection: React.FC<AppendixSectionProps> = ({ items }) => {
  return (
    <section className="salem-section">
      <h2>Appendix</h2>
      
      {items.map((item, index) => (
        <div key={index} className="salem-card">
          <h3>{item.title}</h3>
          {item.content.map((paragraph, pIndex) => (
            <p key={pIndex} style={{ 
              fontSize: 'var(--salem-text-sm)', 
              color: 'var(--salem-gray-600)',
              marginBottom: pIndex < item.content.length - 1 ? 'var(--salem-spacing-md)' : 0
            }}>
              {paragraph}
            </p>
          ))}
        </div>
      ))}
    </section>
  );
};
