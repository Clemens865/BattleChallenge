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

// ============================================================================
// Reproducibility (Principle #11)
// ============================================================================

/**
 * Acceptable variance band (Schwankungsbreite).
 * A benchmark result is "reproducible" if repeated runs with the
 * same model + framework stay within this band.
 *
 * - coefficient of variation (CV) = stddev / mean
 * - For binary pass/fail tasks, we measure pass-rate consistency
 */

export const REPRODUCIBILITY_CV_THRESHOLD = 0.15; // 15% coefficient of variation max

export interface ReproducibilityReport {
  reproducible: boolean;
  passRate: number;
  coefficientOfVariation: number;
  maxAcceptableCV: number;
  scores: number[];
  mean: number;
  stddev: number;
  verdict: string;
}

export function assessReproducibility(
  scores: number[],
  maxCV: number = REPRODUCIBILITY_CV_THRESHOLD,
): ReproducibilityReport {
  if (scores.length < MIN_RUNS) {
    return {
      reproducible: false,
      passRate: 0,
      coefficientOfVariation: Infinity,
      maxAcceptableCV: maxCV,
      scores,
      mean: 0,
      stddev: 0,
      verdict: `Insufficient runs: need ${MIN_RUNS}, have ${scores.length}`,
    };
  }

  const mean = scores.reduce((a, b) => a + b, 0) / scores.length;
  const variance = scores.reduce((sum, s) => sum + (s - mean) ** 2, 0) / scores.length;
  const stddev = Math.sqrt(variance);
  const cv = mean > 0 ? stddev / mean : Infinity;
  const passRate = scores.filter(s => s > 0).length / scores.length;

  const reproducible = cv <= maxCV;

  let verdict: string;
  if (cv === 0) {
    verdict = 'Perfectly reproducible (zero variance)';
  } else if (reproducible) {
    verdict = `Reproducible (CV: ${(cv * 100).toFixed(1)}% <= ${(maxCV * 100).toFixed(0)}% threshold)`;
  } else {
    verdict = `NOT reproducible (CV: ${(cv * 100).toFixed(1)}% > ${(maxCV * 100).toFixed(0)}% threshold)`;
  }

  return {
    reproducible,
    passRate,
    coefficientOfVariation: cv,
    maxAcceptableCV: maxCV,
    scores,
    mean,
    stddev,
    verdict,
  };
}

/**
 * For binary pass/fail scoring:
 * A result is reproducible if the pass rate is consistent.
 * E.g., if a framework passes 4/5 runs, that's 80% reproducible.
 * If it passes 5/5, that's 100%. If 1/5, still reproducible but at 20%.
 * Non-reproducible = wild swings like [pass, fail, pass, fail, pass].
 */
export function assessBinaryReproducibility(
  passed: boolean[],
): { reproducible: boolean; passRate: number; verdict: string } {
  if (passed.length < MIN_RUNS) {
    return { reproducible: false, passRate: 0, verdict: `Need ${MIN_RUNS} runs` };
  }

  const passRate = passed.filter(Boolean).length / passed.length;

  // Binary results are reproducible if they're consistently pass or consistently fail
  // A 60/40 split or worse is not reproducible
  const reproducible = passRate >= 0.8 || passRate <= 0.2;

  const verdict = reproducible
    ? `Reproducible: ${(passRate * 100).toFixed(0)}% pass rate`
    : `NOT reproducible: ${(passRate * 100).toFixed(0)}% pass rate (inconsistent)`;

  return { reproducible, passRate, verdict };
}
