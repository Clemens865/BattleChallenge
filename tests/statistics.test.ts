import { describe, it, expect } from 'vitest';
import {
  computeConfidenceInterval,
  compareFrameworks,
  isHighVariance,
  hasMinimumRuns,
  validateModelPin,
  formatComparisonLabel,
  MIN_RUNS,
} from '../src/scorer/statistics.js';

describe('computeConfidenceInterval', () => {
  it('returns zeros for empty array', () => {
    const ci = computeConfidenceInterval([]);
    expect(ci.median).toBe(0);
  });

  it('computes CI for 5+ values', () => {
    const ci = computeConfidenceInterval([70, 75, 80, 85, 90]);
    expect(ci.median).toBe(80);
    expect(ci.lower).toBeLessThan(ci.median);
    expect(ci.upper).toBeGreaterThan(ci.median);
  });

  it('uses min/max for small arrays', () => {
    const ci = computeConfidenceInterval([60, 80]);
    expect(ci.lower).toBe(60);
    expect(ci.upper).toBe(80);
  });
});

describe('compareFrameworks', () => {
  it('returns no-significant-difference with fewer than MIN_RUNS', () => {
    const result = compareFrameworks([80, 85], [70, 75]);
    expect(result).toBe('no-significant-difference');
  });

  it('detects significantly-better when CIs dont overlap', () => {
    const better = [90, 92, 91, 93, 90, 91, 92];
    const worse = [50, 52, 48, 51, 49, 50, 53];
    const result = compareFrameworks(better, worse);
    expect(result).toBe('significantly-better');
  });

  it('detects no-significant-difference when CIs overlap', () => {
    const a = [78, 80, 82, 79, 81];
    const b = [77, 79, 81, 80, 78];
    const result = compareFrameworks(a, b);
    expect(result).toBe('no-significant-difference');
  });
});

describe('isHighVariance', () => {
  it('detects high variance', () => {
    expect(isHighVariance([20, 30, 80, 90, 95])).toBe(true);
  });

  it('no high variance for consistent values', () => {
    expect(isHighVariance([78, 80, 82, 79, 81])).toBe(false);
  });
});

describe('hasMinimumRuns', () => {
  it('requires MIN_RUNS', () => {
    expect(hasMinimumRuns(MIN_RUNS)).toBe(true);
    expect(hasMinimumRuns(MIN_RUNS - 1)).toBe(false);
    expect(hasMinimumRuns(10)).toBe(true);
  });
});

describe('validateModelPin', () => {
  it('validates matching model', () => {
    const pin = { modelId: 'claude-opus-4-6', modelVersion: '20260301', pinnedAt: '2026-03-01' };
    const result = validateModelPin('claude-opus-4-6', pin);
    expect(result.valid).toBe(true);
  });

  it('rejects mismatched model', () => {
    const pin = { modelId: 'claude-opus-4-6', modelVersion: '20260301', pinnedAt: '2026-03-01' };
    const result = validateModelPin('claude-sonnet-4-6', pin);
    expect(result.valid).toBe(false);
    expect(result.message).toContain('mismatch');
  });
});

describe('formatComparisonLabel', () => {
  it('formats labels correctly', () => {
    expect(formatComparisonLabel('significantly-better')).toBe('Significantly better');
    expect(formatComparisonLabel('no-significant-difference')).toBe('No significant difference');
  });
});
