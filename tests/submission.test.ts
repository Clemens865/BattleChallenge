import { describe, it, expect } from 'vitest';
import {
  validateVerifiedSubmission,
  validateOpenSubmission,
  formatSubmissionResult,
} from '../src/submission/index.js';
import type { AdapterConfig, TaskDefinition, RunResult, MetricsProfile } from '../src/types/index.js';

function makeAdapter(name = 'test-fw'): AdapterConfig {
  return { name, version: '1.0', tier: 'shell', tags: ['coding-agent'], run: './adapter.sh' };
}

function makeTask(id: string, type = 'coding'): TaskDefinition {
  return {
    id, name: id, type: type as any, tags: [], difficulty: 'T1', status: 'active',
    passingThreshold: 60, excellenceThreshold: 95, autoScale: true, timeoutMs: 120000,
    requirementsPath: 'requirements.md', verifyPath: 'verify',
  };
}

function makeRun(taskId: string): RunResult {
  const metrics: MetricsProfile = {
    correctness: { testsTotal: 10, testsPassed: 8, score: 80, edgeCasesHandled: 0, outcomeVerification: true },
    cost: { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, inputCostUsd: 0.01, outputCostUsd: 0.005, totalCostUsd: 0.015, costPerTestPassed: 0.002 },
    speed: { totalMs: 5000, apiCallMs: 3000, processingMs: 2000, timeToFirstPassingTest: null },
    reliability: { runsAttempted: 1, runsPassed: 1, varianceIqr: 0, failureMode: null },
    quality: { hasTests: false, testCoveragePct: null, mutationScore: null, humanReviewScore: null, readabilityHeuristic: 60 },
    autonomy: 0,
  };
  return {
    id: `run-${Math.random()}`, frameworkName: 'test-fw', frameworkVersion: '1.0',
    taskId, runNumber: 1, metrics,
    metadata: { frameworkVersion: '1.0', modelUsed: 'test', modelVersion: 'v1', adapterType: 'reference', adapterVersion: '1.0', dockerImageHash: '', runTimestamp: '' },
    outputHash: '', startedAt: '', completedAt: '',
  };
}

describe('validateVerifiedSubmission', () => {
  it('passes when all checks satisfied', () => {
    const adapter = makeAdapter();
    const tasks = [makeTask('t1', 'coding'), makeTask('t2', 'prd')];
    const runs = new Map<string, RunResult[]>();
    runs.set('t1', Array.from({ length: 5 }, () => makeRun('t1')));
    runs.set('t2', Array.from({ length: 5 }, () => makeRun('t2')));

    const result = validateVerifiedSubmission(adapter, tasks, runs);
    expect(result.passed).toBe(true);
    expect(result.track).toBe('verified');
    expect(result.complianceChecks.every(c => c.passed)).toBe(true);
  });

  it('fails when not all tasks run', () => {
    const adapter = makeAdapter();
    const tasks = [makeTask('t1'), makeTask('t2')];
    const runs = new Map<string, RunResult[]>();
    runs.set('t1', [makeRun('t1'), makeRun('t1'), makeRun('t1'), makeRun('t1'), makeRun('t1')]);
    // t2 missing

    const result = validateVerifiedSubmission(adapter, tasks, runs);
    expect(result.passed).toBe(false);
  });

  it('fails when insufficient runs', () => {
    const adapter = makeAdapter();
    const tasks = [makeTask('t1')];
    const runs = new Map<string, RunResult[]>();
    runs.set('t1', [makeRun('t1'), makeRun('t1')]); // Only 2, need 5

    const result = validateVerifiedSubmission(adapter, tasks, runs);
    expect(result.passed).toBe(false);
  });
});

describe('validateOpenSubmission', () => {
  it('always passes', () => {
    const adapter = makeAdapter();
    const runs = new Map<string, RunResult[]>();
    runs.set('t1', [makeRun('t1')]);

    const result = validateOpenSubmission(adapter, runs);
    expect(result.passed).toBe(true);
    expect(result.track).toBe('open');
  });
});

describe('formatSubmissionResult', () => {
  it('formats verified result', () => {
    const adapter = makeAdapter();
    const tasks = [makeTask('t1')];
    const runs = new Map<string, RunResult[]>();
    runs.set('t1', Array.from({ length: 5 }, () => makeRun('t1')));

    const result = validateVerifiedSubmission(adapter, tasks, runs);
    const formatted = formatSubmissionResult(result);
    expect(formatted).toContain('VERIFIED');
    expect(formatted).toContain('PASSED');
  });
});
