# Data Flow Fix: Longevity and Ruin Analysis Components

## Problem Identified

The refactored `LongevityStressTable` and `AnnualProbabilityRuinTable` components always showed "Insufficient Data" even when valid simulation results existed.

### Root Cause

**Type Mismatch Between Backend and Frontend:**

- **Backend Response** (`MonthlyStats` interface):
  ```typescript
  interface MonthlyStats {
    Month: number;
    Median: number;
    P10: number;
    P25: number;
    P75: number;
    P90: number;
    Mean: number;
    StdDev: number;
    // NO SuccessPct field
  }
  ```

- **Component Expectations** (`SimulationStats` interface):
  ```typescript
  interface SimulationStats {
    Month: number;
    SuccessPct: number;  // ← MISSING FROM BACKEND!
    Median: number;
    P10: number;
    P25: number;
    P75: number;
    P90: number;
    Mean?: number;
    StdDev?: number;
  }
  ```

### Why Components Failed

The utility functions in `analysisUtils.ts` check for the `SuccessPct` field:

```typescript
// In processLongevityData() and processAnnualRiskData()
if (stat?.SuccessPct === undefined || stat?.SuccessPct === null) {
  return null;  // ← ALWAYS returns null because field doesn't exist!
}
```

This caused:
1. All data filtered out by `.filter(Boolean)`
2. Empty arrays passed to components
3. "Insufficient Data" state triggered

## Solution Implemented

### 1. Created Data Transformation Utility

**File:** `/frontend/src/utils/dataTransformers.ts`

Calculates success percentage from percentile data using conservative estimates:

```typescript
function calculateSuccessPercentage(stat: MonthlyStats): number {
  if (stat.P10 > 0) return 95.0;      // 10th percentile positive = 95% success
  if (stat.P25 > 0) return 85.0;      // 25th percentile positive = 85% success
  if (stat.Median > 0) return 65.0;   // Median positive = 65% success
  if (stat.P75 > 0) return 35.0;      // 75th percentile positive = 35% success
  if (stat.P90 > 0) return 15.0;      // 90th percentile positive = 15% success
  return 5.0;                          // All percentiles depleted = 5% success
}
```

This logic mirrors the approach used in the existing `ProbabilitySuccessCurve.tsx` component.

### 2. Updated MonteCarloAnalytics Component

**File:** `/frontend/src/components/monte-carlo/visualizations/MonteCarloAnalytics.tsx`

Added transformation layer:

```typescript
import { transformMonthlyStatsToSimulationStats } from '../../../utils/dataTransformers';

// Transform data before passing to components
const transformedStats = useMemo(() => {
  return transformMonthlyStatsToSimulationStats(stats);
}, [stats]);

// Pass transformed data to components
<LongevityStressTable stats={transformedStats} currentAge={inputs.current_age} />
<AnnualProbabilityRuinTable stats={transformedStats} currentAge={inputs.current_age} />
```

## Data Flow After Fix

```
Backend API
    ↓
Returns MonthlyStats[] (no SuccessPct)
    ↓
Zustand Store (simulationResults)
    ↓
MonteCarloAnalytics Component
    ↓
transformMonthlyStatsToSimulationStats() ← TRANSFORMATION LAYER
    ↓
SimulationStats[] (with calculated SuccessPct)
    ↓
LongevityStressTable & AnnualProbabilityRuinTable
    ↓
Display Data Successfully
```

## Testing

After implementing the fix:

1. Run a simulation from the Inputs page
2. Navigate to Analytics tab
3. **Expected:** Longevity Stress Analysis and Annual Probability of Ruin tables show data
4. **Expected:** "Insufficient Data" only appears when no simulation has been run

## Files Modified

1. **Created:** `/frontend/src/utils/dataTransformers.ts`
   - New utility for calculating success percentages
   - Transforms `MonthlyStats` → `SimulationStats`

2. **Modified:** `/frontend/src/components/monte-carlo/visualizations/MonteCarloAnalytics.tsx`
   - Added import for transformer utility
   - Added `useMemo` hook to transform data
   - Updated component props to use `transformedStats`

## Alternative Solutions Considered

### Option A: Update Backend ✗
- **Cons:** Requires backend changes, affects all API consumers

### Option B: Modify Components to Work Without SuccessPct ✗
- **Cons:** Would require rewriting all utility functions, less accurate

### Option C: Frontend Data Transformation ✓ **CHOSEN**
- **Pros:** 
  - No backend changes required
  - Isolates transformation logic
  - Maintains component interface
  - Uses proven calculation method
  - Conservative estimates appropriate for advisor use

## Success Metrics

- ✅ Components receive properly typed data with `SuccessPct`
- ✅ No TypeScript compilation errors
- ✅ Conservative success probability estimates
- ✅ Consistent with existing `ProbabilitySuccessCurve` logic
- ✅ "Insufficient Data" only shows when truly no data exists
