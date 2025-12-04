import React from 'react';
import { presentationTheme } from '../presentationTheme';

const NextStepsSlide: React.FC<any> = () => (
  <div style={{ padding: '5vh 5vw', display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%' }}>
    <h1 style={{ ...presentationTheme.typography.slideTitle, color: presentationTheme.colors.gold, marginBottom: '3rem' }}>Next Steps</h1>
    <ul style={{ ...presentationTheme.typography.body, listStyle: 'none', padding: 0 }}>
      <li style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: presentationTheme.colors.background.secondary, borderLeft: `4px solid ${presentationTheme.colors.gold}` }}>Review and approve recommendations</li>
      <li style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: presentationTheme.colors.background.secondary, borderLeft: `4px solid ${presentationTheme.colors.gold}` }}>Schedule follow-up meeting</li>
      <li style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: presentationTheme.colors.background.secondary, borderLeft: `4px solid ${presentationTheme.colors.gold}` }}>Questions and discussion</li>
    </ul>
  </div>
);

export default NextStepsSlide;