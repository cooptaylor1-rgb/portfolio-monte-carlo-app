import React from 'react';
import { presentationTheme } from '../presentationTheme';

const KeyRisksSlide: React.FC<any> = () => (
  <div style={{ padding: '5vh 5vw' }}>
    <h1 style={{ ...presentationTheme.typography.slideTitle, color: presentationTheme.colors.gold }}>Key Considerations</h1>
    <p style={{ ...presentationTheme.typography.body, marginTop: '2rem' }}>Risk factors and mitigation strategies will be displayed here</p>
  </div>
);

export default KeyRisksSlide;