/**
 * Unit tests for report formatting utilities
 * Tests edge cases: null, undefined, NaN, Infinity, negative, zero, very large
 */

import {
  formatCurrency,
  formatCurrencyFull,
  formatPercent,
  formatPercentDecimal,
  getSuccessRating,
  hasValidData,
  getLastElement,
} from '../reportFormatters';

describe('formatCurrency', () => {
  test('formats small positive numbers correctly', () => {
    expect(formatCurrency(500)).toBe('$500');
    expect(formatCurrency(999)).toBe('$999');
  });

  test('formats thousands with K abbreviation', () => {
    expect(formatCurrency(1000)).toBe('$1K');
    expect(formatCurrency(50000)).toBe('$50K');
    expect(formatCurrency(999999)).toBe('$1000K');
  });

  test('formats millions with M abbreviation', () => {
    expect(formatCurrency(1000000)).toBe('$1.0M');
    expect(formatCurrency(4500000)).toBe('$4.5M');
    expect(formatCurrency(1234567)).toBe('$1.2M');
  });

  test('formats billions with B abbreviation', () => {
    expect(formatCurrency(1000000000)).toBe('$1.0B');
    expect(formatCurrency(2500000000)).toBe('$2.5B');
  });

  test('handles negative values correctly', () => {
    expect(formatCurrency(-5000)).toBe('-$5K');
    expect(formatCurrency(-1500000)).toBe('-$1.5M');
  });

  test('handles null and undefined gracefully', () => {
    expect(formatCurrency(null)).toBe('$0');
    expect(formatCurrency(undefined)).toBe('$0');
  });

  test('handles NaN and Infinity gracefully', () => {
    expect(formatCurrency(NaN)).toBe('$0');
    expect(formatCurrency(Infinity)).toBe('$0');
    expect(formatCurrency(-Infinity)).toBe('$0');
  });

  test('respects abbreviated option', () => {
    expect(formatCurrency(5000, { abbreviated: false })).toBe('$5,000');
    expect(formatCurrency(1500000, { abbreviated: false })).toBe('$1,500,000');
  });

  test('respects decimals option', () => {
    expect(formatCurrency(1234567, { decimals: 2 })).toBe('$1.23M');
    expect(formatCurrency(5500, { decimals: 1 })).toBe('$5.5K');
  });
});

describe('formatCurrencyFull', () => {
  test('formats without abbreviation', () => {
    expect(formatCurrencyFull(1500000)).toBe('$1,500,000');
    expect(formatCurrencyFull(45000)).toBe('$45,000');
  });

  test('respects decimal places', () => {
    expect(formatCurrencyFull(1234.567, 2)).toBe('$1,234.57');
    expect(formatCurrencyFull(1000, 0)).toBe('$1,000');
  });

  test('handles null and undefined', () => {
    expect(formatCurrencyFull(null)).toBe('$0');
    expect(formatCurrencyFull(undefined)).toBe('$0');
  });
});

describe('formatPercent', () => {
  test('formats decimal values (0-1) as percentages', () => {
    expect(formatPercent(0.85)).toBe('85.0%');
    expect(formatPercent(0.5)).toBe('50.0%');
    expect(formatPercent(0.123)).toBe('12.3%');
  });

  test('formats percentage values (>1) correctly', () => {
    expect(formatPercent(85)).toBe('85.0%');
    expect(formatPercent(100)).toBe('100.0%');
  });

  test('clamps values to 0-100 range', () => {
    expect(formatPercent(-0.5)).toBe('0.0%');
    expect(formatPercent(1.5)).toBe('100.0%');
    expect(formatPercent(200)).toBe('100.0%');
  });

  test('handles null and undefined', () => {
    expect(formatPercent(null)).toBe('0.0%');
    expect(formatPercent(undefined)).toBe('0.0%');
  });

  test('handles NaN and Infinity', () => {
    expect(formatPercent(NaN)).toBe('0.0%');
    expect(formatPercent(Infinity)).toBe('100.0%');
  });

  test('respects decimal precision', () => {
    expect(formatPercent(0.8567, 0)).toBe('86%');
    expect(formatPercent(0.8567, 2)).toBe('85.67%');
    expect(formatPercent(0.8567, 3)).toBe('85.670%');
  });
});

describe('formatPercentDecimal', () => {
  test('formats decimal values correctly', () => {
    expect(formatPercentDecimal(0.85)).toBe('85.0%');
    expect(formatPercentDecimal(0.5)).toBe('50.0%');
  });

  test('clamps to 0-1 range', () => {
    expect(formatPercentDecimal(-0.5)).toBe('0.0%');
    expect(formatPercentDecimal(1.5)).toBe('100.0%');
  });

  test('handles null and undefined', () => {
    expect(formatPercentDecimal(null)).toBe('0.0%');
    expect(formatPercentDecimal(undefined)).toBe('0.0%');
  });
});

describe('getSuccessRating', () => {
  test('returns Strong for high success probability', () => {
    const rating = getSuccessRating(0.9);
    expect(rating.label).toBe('Strong');
    expect(rating.variant).toBe('success');
    expect(rating.color).toBe('#4CAF50');
  });

  test('returns Moderate for mid-range success', () => {
    const rating = getSuccessRating(0.75);
    expect(rating.label).toBe('Moderate');
    expect(rating.variant).toBe('warning');
    expect(rating.color).toBe('#FFC107');
  });

  test('returns Low for low success probability', () => {
    const rating = getSuccessRating(0.5);
    expect(rating.label).toBe('Low');
    expect(rating.variant).toBe('error');
    expect(rating.color).toBe('#D9534F');
  });

  test('handles boundary conditions', () => {
    expect(getSuccessRating(0.85).label).toBe('Strong');
    expect(getSuccessRating(0.849).label).toBe('Moderate');
    expect(getSuccessRating(0.70).label).toBe('Moderate');
    expect(getSuccessRating(0.699).label).toBe('Low');
  });

  test('handles null and undefined', () => {
    expect(getSuccessRating(null).label).toBe('Low');
    expect(getSuccessRating(undefined).label).toBe('Low');
  });
});

describe('hasValidData', () => {
  test('returns true for non-empty arrays', () => {
    expect(hasValidData([1, 2, 3])).toBe(true);
    expect(hasValidData(['a'])).toBe(true);
  });

  test('returns false for empty arrays', () => {
    expect(hasValidData([])).toBe(false);
  });

  test('returns false for null and undefined', () => {
    expect(hasValidData(null)).toBe(false);
    expect(hasValidData(undefined)).toBe(false);
  });

  test('returns false for non-arrays', () => {
    expect(hasValidData({} as any)).toBe(false);
    expect(hasValidData('string' as any)).toBe(false);
  });
});

describe('getLastElement', () => {
  test('returns last element of array', () => {
    expect(getLastElement([1, 2, 3])).toBe(3);
    expect(getLastElement(['a', 'b', 'c'])).toBe('c');
  });

  test('returns undefined for empty array', () => {
    expect(getLastElement([])).toBeUndefined();
  });

  test('returns default for empty array when provided', () => {
    expect(getLastElement([], 999)).toBe(999);
  });

  test('returns default for null and undefined', () => {
    expect(getLastElement(null, 999)).toBe(999);
    expect(getLastElement(undefined, 999)).toBe(999);
  });

  test('handles single-element arrays', () => {
    expect(getLastElement([42])).toBe(42);
  });
});
