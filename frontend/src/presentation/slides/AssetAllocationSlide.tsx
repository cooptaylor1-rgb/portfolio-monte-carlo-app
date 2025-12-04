import React from 'react';
import { presentationTheme } from '../presentationTheme';

const AssetAllocationSlide: React.FC<any> = () => (
  <div style={{ padding: '5vh 5vw' }}>
    <h1 style={{ ...presentationTheme.typography.slideTitle, color: presentationTheme.colors.gold }}>Asset Allocation</h1>
    <p style={{ ...presentationTheme.typography.body, marginTop: '2rem' }}>Investment mix breakdown will be displayed here</p>
  </div>
);

export default AssetAllocationSlide;