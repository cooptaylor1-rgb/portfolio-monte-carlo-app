import React from 'react';
import { presentationTheme } from '../presentationTheme';

const StressTestsSlide: React.FC<any> = () => (
  <div style={{ padding: '5vh 5vw' }}>
    <h1 style={{ ...presentationTheme.typography.slideTitle, color: presentationTheme.colors.gold }}>Stress Tests</h1>
    <p style={{ ...presentationTheme.typography.body, marginTop: '2rem' }}>Historical scenario analysis will be displayed here</p>
  </div>
);

export default StressTestsSlide;