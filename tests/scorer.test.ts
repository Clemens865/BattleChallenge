import { describe, it, expect } from 'vitest';
import { medianOf, iqrOf, aggregateResults, formatProfile } from '../src/scorer/index.js';
import type { RunResult, MetricsProfile } from '../src/types/index.js';

describe('medianOf', () => {
  it('returns 0 for empty array', () => {
    expect(medianOf([])).toBe(0);
  });

  it('returns the middle value for odd-length arrays', () => {
    expect(medianOf([1, 3, 5])).toBe(3);
  });

  it('returns the average of two middle values for even-length arrays', () => {
    expect(medianOf([1, 2, 3, 4])).toBe(2.5);
  });

  it('handles single element', () => {
    expect(medianOf([42])).toBe(42);
  });

  it('handles unsorted input', () => {
    expect(medianOf([5, 1, 3])).toBe(3);
  });
});

describe('iqrOf', () => {
  it('returns 0 for arrays with fewer than 4 elements', () => {
    expect(iqrOf([1, 2, 3])).toBe(0);
  });

  it('computes IQR correctly', () => {
    const values = [1, 2, 3, 4, 5, 6, 7, 8];
    const result = iqrOf(values);
    expect(result).toBeGreaterThan(0);
  });
});

function makeRun(overrides: Partial<{ score: number; totalMs: number; totalCostUsd: number }> = {}): RunResult {
  const metrics: MetricsProfile = {
    correctness: {
      testsTotal: 10,
      testsPassed: overrides.score ? Math.round(overrides.score / 10) : 8,
      score: overrides.score ?? 80,
      edgeCasesHandled: 0,
      outcomeVerification: true,
    },
    cost: {
      inputTokens: 1000,
      outputTokens: 500,
      totalTokens: 1500,
      inputCostUsd: 0.01,
      outputCostUsd: 0.005,
      totalCostUsd: overrides.totalCostUsd ?? 0.015,
      costPerTestPassed: 0.002,
    },
    speed: {
      totalMs: overrides.totalMs ?? 5000,
      apiCallMs: 3000,
      processingMs: 2000,
      timeToFirstPassingTest: null,
    },
    reliability: {
      runsAttempted: 1,
      runsPassed: 1,
      varianceIqr: 0,
      failureMode: null,
    },
    quality: {
      hasTests: false,
      testCoveragePct: null,
      mutationScore: null,
      humanReviewScore: null,
      readabilityHeuristic: 60,
    },
    autonomy: 0,
  };

  return {
    id: `run-${Math.random().toString(36).slice(2)}`,
    frameworkName: 'test-framework',
    frameworkVersion: '1.0.0',
    taskId: 'task-001',
    runNumber: 1,
    metrics,
    metadata: {
      frameworkVersion: '1.0.0',
      modelUsed: 'test-model',
      modelVersion: 'v1',
      adapterType: 'reference',
      adapterVersion: '1.0.0',
      dockerImageHash: 'sha256:abc',
      runTimestamp: new Date().toISOString(),
    },
    outputHash: 'sha256:def',
    startedAt: new Date().toISOString(),
    completedAt: new Date().toISOString(),
  };
}

describe('aggregateResults', () => {
  it('returns null for empty runs', () => {
    expect(aggregateResults([])).toBeNull();
  });

  it('aggregates single run', () => {
    const result = aggregateResults([makeRun()]);
    expect(result).not.toBeNull();
    expect(result!.frameworkName).toBe('test-framework');
    expect(result!.median.correctness.score).toBe(80);
  });

  it('computes median across multiple runs', () => {
    const runs = [
      makeRun({ score: 60 }),
      makeRun({ score: 80 }),
      makeRun({ score: 70 }),
      makeRun({ score: 90 }),
      makeRun({ score: 85 }),
    ];
    const result = aggregateResults(runs);
    expect(result).not.toBeNull();
    expect(result!.median.correctness.score).toBe(80);
  });

  it('detects high variance', () => {
    const runs = [
      makeRun({ score: 20 }),
      makeRun({ score: 30 }),
      makeRun({ score: 80 }),
      makeRun({ score: 90 }),
      makeRun({ score: 95 }),
    ];
    const result = aggregateResults(runs);
    expect(result).not.toBeNull();
    expect(result!.highVariance).toBe(true);
  });

  it('no high variance for consistent runs', () => {
    const runs = [
      makeRun({ score: 78 }),
      makeRun({ score: 80 }),
      makeRun({ score: 82 }),
      makeRun({ score: 79 }),
      makeRun({ score: 81 }),
    ];
    const result = aggregateResults(runs);
    expect(result).not.toBeNull();
    expect(result!.highVariance).toBe(false);
  });
});

describe('formatProfile', () => {
  it('returns a formatted string with all metrics', () => {
    const run = makeRun();
    const output = formatProfile(run.metrics);
    expect(output).toContain('Correctness');
    expect(output).toContain('Cost');
    expect(output).toContain('Speed');
    expect(output).toContain('Reliability');
    expect(output).toContain('Quality');
  });
});
