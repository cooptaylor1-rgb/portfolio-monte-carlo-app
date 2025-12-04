/**
 * Monte Carlo Analytics Page
 * Full-featured analytics page with comprehensive visualizations
 */

import React from 'react';
import MonteCarloAnalytics from '../components/monte-carlo/visualizations/MonteCarloAnalytics';

const MonteCarloAnalyticsPage: React.FC = () => {
  return <MonteCarloAnalytics showAllCharts={true} />;
};

export default MonteCarloAnalyticsPage;
