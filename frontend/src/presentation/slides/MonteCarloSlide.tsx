import React from 'react';
import { presentationTheme } from '../presentationTheme';

const MonteCarloSlide: React.FC<any> = () => (
  <div style={{ padding: '5vh 5vw' }}>
    <h1 style={{ ...presentationTheme.typography.slideTitle, color: presentationTheme.colors.gold }}>Portfolio Projection</h1>
    <p style={{ ...presentationTheme.typography.body, marginTop: '2rem' }}>Monte Carlo simulation results will be displayed here</p>
  </div>
);

export default MonteCarloSlide;