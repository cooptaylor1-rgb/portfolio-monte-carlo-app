/**
 * Data transformation utilities
 * Converts backend MonthlyStats to frontend SimulationStats with calculated SuccessPct
 */

import type { MonthlyStats } from '../types';
import type { SimulationStats } from '../components/monte-carlo/shared/types';

/**
 * Calculate success percentage from percentile data
 * Success rate is estimated based on how many percentiles show positive balance
 * This matches the logic used in ProbabilitySuccessCurve.tsx
 */
export function calculateSuccessPercentage(stat: MonthlyStats): number {
  // If P10 > 0, at least 90% of scenarios succeeded
  if (stat.P10 > 0) {
    return 95.0; // Conservative estimate: 95%
  }
  
  // If P25 > 0, at least 75% succeeded
  if (stat.P25 > 0) {
    return 85.0; // 85% success rate
  }
  
  // If Median > 0, at least 50% succeeded
  if (stat.Median > 0) {
    return 65.0; // 65% success rate
  }
  
  // If P75 > 0, at least 25% succeeded
  if (stat.P75 > 0) {
    return 35.0; // 35% success rate
  }
  
  // If P90 > 0, at least 10% succeeded
  if (stat.P90 > 0) {
    return 15.0; // 15% success rate
  }
  
  // All percentiles depleted
  return 5.0; // 5% success rate (nearly complete failure)
}

/**
 * Transform MonthlyStats array to SimulationStats array
 * Adds calculated SuccessPct field for longevity and ruin analysis
 */
export function transformMonthlyStatsToSimulationStats(
  monthlyStats: MonthlyStats[]
): SimulationStats[] {
  return monthlyStats.map(stat => ({
    Month: stat.Month,
    SuccessPct: calculateSuccessPercentage(stat),
    Median: stat.Median,
    P10: stat.P10,
    P25: stat.P25,
    P75: stat.P75,
    P90: stat.P90,
    Mean: stat.Mean,
    StdDev: stat.StdDev,
  }));
}
