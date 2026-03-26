/**
 * Scoring engine — computes the 5 meta-metrics from raw run data.
 * Produces multi-dimensional profiles, NOT composite scores.
 */

import type {
  RunResult,
  AggregatedResult,
  MetricsProfile,
  CorrectnessMetrics,
  CostMetrics,
  SpeedMetrics,
  ReliabilityMetrics,
  QualityMetrics,
  VerificationChain,
} from '../types/index.js';

export function aggregateResults(runs: RunResult[]): AggregatedResult | null {
  if (runs.length === 0) return null;

  const first = runs[0];
  const median = computeMedianProfile(runs);
  const iqr = computeIqrProfile(runs);
  const highVariance = detectHighVariance(runs);

  return {
    frameworkName: first.frameworkName,
    taskId: first.taskId,
    runs,
    median,
    iqr,
    highVariance,
    verificationChain: buildVerificationChain(first),
  };
}

function computeMedianProfile(runs: RunResult[]): MetricsProfile {
  return {
    correctness: {
      testsTotal: medianOf(runs.map(r => r.metrics.correctness.testsTotal)),
      testsPassed: medianOf(runs.map(r => r.metrics.correctness.testsPassed)),
      score: medianOf(runs.map(r => r.metrics.correctness.score)),
      edgeCasesHandled: medianOf(runs.map(r => r.metrics.correctness.edgeCasesHandled)),
      outcomeVerification: runs.every(r => r.metrics.correctness.outcomeVerification),
    },
    cost: {
      inputTokens: medianOf(runs.map(r => r.metrics.cost.inputTokens)),
      outputTokens: medianOf(runs.map(r => r.metrics.cost.outputTokens)),
      totalTokens: medianOf(runs.map(r => r.metrics.cost.totalTokens)),
      inputCostUsd: medianOf(runs.map(r => r.metrics.cost.inputCostUsd)),
      outputCostUsd: medianOf(runs.map(r => r.metrics.cost.outputCostUsd)),
      totalCostUsd: medianOf(runs.map(r => r.metrics.cost.totalCostUsd)),
      costPerTestPassed: medianOf(runs.map(r => r.metrics.cost.costPerTestPassed)),
    },
    speed: {
      totalMs: medianOf(runs.map(r => r.metrics.speed.totalMs)),
      apiCallMs: medianOf(runs.map(r => r.metrics.speed.apiCallMs)),
      processingMs: medianOf(runs.map(r => r.metrics.speed.processingMs)),
      timeToFirstPassingTest: medianOfNullable(runs.map(r => r.metrics.speed.timeToFirstPassingTest)),
    },
    reliability: {
      runsAttempted: runs.length,
      runsPassed: runs.filter(r => r.metrics.correctness.score >= 60).length,
      varianceIqr: iqrOf(runs.map(r => r.metrics.correctness.score)),
      failureMode: null,
    },
    quality: {
      hasTests: runs.some(r => r.metrics.quality.hasTests),
      testCoveragePct: medianOfNullable(runs.map(r => r.metrics.quality.testCoveragePct)),
      mutationScore: medianOfNullable(runs.map(r => r.metrics.quality.mutationScore)),
      humanReviewScore: medianOfNullable(runs.map(r => r.metrics.quality.humanReviewScore)),
      readabilityHeuristic: medianOf(runs.map(r => r.metrics.quality.readabilityHeuristic)),
    },
    autonomy: medianOf(runs.map(r => r.metrics.autonomy)) as 0 | 1 | 2,
  };
}

function computeIqrProfile(runs: RunResult[]): Partial<MetricsProfile> {
  return {
    correctness: {
      testsTotal: 0,
      testsPassed: 0,
      score: iqrOf(runs.map(r => r.metrics.correctness.score)),
      edgeCasesHandled: 0,
      outcomeVerification: false,
    },
    cost: {
      inputTokens: 0,
      outputTokens: 0,
      totalTokens: iqrOf(runs.map(r => r.metrics.cost.totalTokens)),
      inputCostUsd: 0,
      outputCostUsd: 0,
      totalCostUsd: iqrOf(runs.map(r => r.metrics.cost.totalCostUsd)),
      costPerTestPassed: 0,
    },
    speed: {
      totalMs: iqrOf(runs.map(r => r.metrics.speed.totalMs)),
      apiCallMs: 0,
      processingMs: 0,
      timeToFirstPassingTest: null,
    },
  };
}

function detectHighVariance(runs: RunResult[]): boolean {
  const scores = runs.map(r => r.metrics.correctness.score);
  const med = medianOf(scores);
  if (med === 0) return false;
  const iqr = iqrOf(scores);
  return iqr / med > 0.2;
}

function buildVerificationChain(run: RunResult): VerificationChain {
  return {
    taskHash: '',
    adapterHash: '',
    dockerImageHash: run.metadata.dockerImageHash,
    runnerVersion: '0.1.0',
    modelVersion: run.metadata.modelVersion,
    environmentHash: '',
    outputHash: run.outputHash,
  };
}

// ============================================================================
// Statistical Utilities
// ============================================================================

export function medianOf(values: number[]): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0
    ? sorted[mid]
    : (sorted[mid - 1] + sorted[mid]) / 2;
}

function medianOfNullable(values: (number | null)[]): number | null {
  const valid = values.filter((v): v is number => v !== null);
  return valid.length > 0 ? medianOf(valid) : null;
}

export function iqrOf(values: number[]): number {
  if (values.length < 4) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const q1Idx = Math.floor(sorted.length * 0.25);
  const q3Idx = Math.floor(sorted.length * 0.75);
  return sorted[q3Idx] - sorted[q1Idx];
}

export function formatProfile(profile: MetricsProfile): string {
  const bar = (value: number, max: number): string => {
    const filled = Math.round((value / max) * 10);
    return '█'.repeat(filled) + '░'.repeat(10 - filled);
  };

  const reliabilityPct = profile.reliability.runsAttempted > 0
    ? Math.round((profile.reliability.runsPassed / profile.reliability.runsAttempted) * 100)
    : 0;

  return [
    `  ${bar(profile.correctness.score, 100)} Correctness:  ${profile.correctness.score}/100`,
    `  ${bar(100 - profile.cost.totalCostUsd * 100, 100)} Cost:         $${profile.cost.totalCostUsd.toFixed(2)}/task`,
    `  ${bar(100 - Math.min(profile.speed.totalMs / 600, 100), 100)} Speed:        ${(profile.speed.totalMs / 1000).toFixed(1)}s avg`,
    `  ${bar(reliabilityPct, 100)} Reliability:  ${reliabilityPct}% (${profile.reliability.runsPassed}/${profile.reliability.runsAttempted} pass)`,
    `  ${bar(profile.quality.readabilityHeuristic, 100)} Quality:      ${profile.quality.readabilityHeuristic}/100`,
  ].join('\n');
}
