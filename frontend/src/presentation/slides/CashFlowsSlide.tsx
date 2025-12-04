import React from 'react';
import { presentationTheme } from '../presentationTheme';

const CashFlowsSlide: React.FC<any> = () => (
  <div style={{ padding: '5vh 5vw' }}>
    <h1 style={{ ...presentationTheme.typography.slideTitle, color: presentationTheme.colors.gold }}>Cash Flows</h1>
    <p style={{ ...presentationTheme.typography.body, marginTop: '2rem' }}>Income and spending timeline will be displayed here</p>
  </div>
);

export default CashFlowsSlide;