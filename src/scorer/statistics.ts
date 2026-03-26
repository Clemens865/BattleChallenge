/**
 * Statistical rigor module for BattleChallenge.
 *
 * - Minimum 5 runs per task per framework
 * - Median + IQR (not mean — resists outliers)
 * - Confidence interval comparison
 * - "No significant difference" when CIs overlap
 * - Model version pinning
 */

import { medianOf, iqrOf } from './index.js';

export interface ConfidenceInterval {
  lower: number;
  median: number;
  upper: number;
}

export type ComparisonResult = 'significantly-better' | 'significantly-worse' | 'no-significant-difference';

export const MIN_RUNS = 5;
export const HIGH_VARIANCE_THRESHOLD = 0.2; // IQR > 20% of median

export function computeConfidenceInterval(values: number[]): ConfidenceInterval {
  if (values.length === 0) return { lower: 0, median: 0, upper: 0 };

  const sorted = [...values].sort((a, b) => a - b);
  const med = medianOf(sorted);

  if (sorted.length < 4) {
    return { lower: sorted[0], median: med, upper: sorted[sorted.length - 1] };
  }

  const q1Idx = Math.floor(sorted.length * 0.25);
  const q3Idx = Math.floor(sorted.length * 0.75);
  const iqr = sorted[q3Idx] - sorted[q1Idx];

  return {
    lower: med - 1.5 * iqr,
    median: med,
    upper: med + 1.5 * iqr,
  };
}

export function compareFrameworks(
  scoresA: number[],
  scoresB: number[],
): ComparisonResult {
  if (scoresA.length < MIN_RUNS || scoresB.length < MIN_RUNS) {
    return 'no-significant-difference';
  }

  const ciA = computeConfidenceInterval(scoresA);
  const ciB = computeConfidenceInterval(scoresB);

  if (ciA.lower > ciB.upper) return 'significantly-better';
  if (ciB.lower > ciA.upper) return 'significantly-worse';
  return 'no-significant-difference';
}

export function isHighVariance(values: number[]): boolean {
  const med = medianOf(values);
  if (med === 0) return false;
  const iqr = iqrOf(values);
  return iqr / med > HIGH_VARIANCE_THRESHOLD;
}

export function hasMinimumRuns(runCount: number): boolean {
  return runCount >= MIN_RUNS;
}

export interface ModelPin {
  modelId: string;
  modelVersion: string;
  pinnedAt: string;
}

export function validateModelPin(
  currentModel: string,
  pin: ModelPin,
): { valid: boolean; message: string } {
  if (currentModel !== pin.modelId) {
    return {
      valid: false,
      message: `Model mismatch: expected ${pin.modelId}, got ${currentModel}. Results must be re-run.`,
    };
  }
  return { valid: true, message: 'Model version matches pin.' };
}

export function formatComparisonLabel(result: ComparisonResult): string {
  switch (result) {
    case 'significantly-better': return 'Significantly better';
    case 'significantly-worse': return 'Significantly worse';
    case 'no-significant-difference': return 'No significant difference';
  }
}

export function formatConfidenceInterval(ci: ConfidenceInterval): string {
  return `${ci.lower.toFixed(1)} — [${ci.median.toFixed(1)}] — ${ci.upper.toFixed(1)}`;
}
