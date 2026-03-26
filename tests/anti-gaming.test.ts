import { describe, it, expect } from 'vitest';
import {
  detectPublicSecretGap,
  detectAnomalousTokenUsage,
  scanAdapterForHardcodedAnswers,
  determineSeverity,
} from '../src/anti-gaming/index.js';
import type { RunResult, MetricsProfile } from '../src/types/index.js';

describe('detectPublicSecretGap', () => {
  it('detects significant gap', () => {
    const result = detectPublicSecretGap([90, 85, 88], [60, 55, 58]);
    expect(result).not.toBeNull();
    expect(result!.severity).toBe('flag');
    expect(result!.detectionType).toBe('behavioral-analysis');
  });

  it('returns null when no significant gap', () => {
    const result = detectPublicSecretGap([80, 82, 78], [77, 79, 75]);
    expect(result).toBeNull();
  });

  it('returns null for empty arrays', () => {
    expect(detectPublicSecretGap([], [80])).toBeNull();
    expect(detectPublicSecretGap([80], [])).toBeNull();
  });
});

function makeRun(taskId: string, totalTokens: number): RunResult {
  const metrics: MetricsProfile = {
    correctness: { testsTotal: 10, testsPassed: 8, score: 80, edgeCasesHandled: 0, outcomeVerification: true },
    cost: { inputTokens: totalTokens / 2, outputTokens: totalTokens / 2, totalTokens, inputCostUsd: 0, outputCostUsd: 0, totalCostUsd: 0, costPerTestPassed: 0 },
    speed: { totalMs: 5000, apiCallMs: 3000, processingMs: 2000, timeToFirstPassingTest: null },
    reliability: { runsAttempted: 1, runsPassed: 1, varianceIqr: 0, failureMode: null },
    quality: { hasTests: false, testCoveragePct: null, mutationScore: null, humanReviewScore: null, readabilityHeuristic: 60 },
    autonomy: 0,
  };
  return {
    id: 'r1', frameworkName: 'test', frameworkVersion: '1.0', taskId, runNumber: 1, metrics,
    metadata: { frameworkVersion: '1.0', modelUsed: 't', modelVersion: 'v1', adapterType: 'reference', adapterVersion: '1.0', dockerImageHash: '', runTimestamp: '' },
    outputHash: '', startedAt: '', completedAt: '',
  };
}

describe('detectAnomalousTokenUsage', () => {
  it('flags unusually low token usage', () => {
    const runs = [makeRun('task-001', 50)]; // 50 tokens vs median 1000
    const detections = detectAnomalousTokenUsage(runs, 1000);
    expect(detections.length).toBe(1);
    expect(detections[0].severity).toBe('flag');
  });

  it('does not flag normal usage', () => {
    const runs = [makeRun('task-001', 800)]; // 800 vs median 1000
    const detections = detectAnomalousTokenUsage(runs, 1000);
    expect(detections.length).toBe(0);
  });
});

describe('scanAdapterForHardcodedAnswers', () => {
  it('detects task ID references in adapter code', () => {
    const code = 'if task == "task-001-validate-email": return cached_answer';
    const detections = scanAdapterForHardcodedAnswers(code, ['task-001-validate-email']);
    expect(detections.some(d => d.severity === 'disqualification')).toBe(true);
  });

  it('detects suspicious patterns', () => {
    const code = 'hardcoded = True';
    const detections = scanAdapterForHardcodedAnswers(code, []);
    expect(detections.length).toBeGreaterThan(0);
  });

  it('returns empty for clean code', () => {
    const code = 'def run_task(prompt): return llm.generate(prompt)';
    const detections = scanAdapterForHardcodedAnswers(code, ['task-001']);
    expect(detections.length).toBe(0);
  });
});

describe('determineSeverity', () => {
  it('returns highest severity', () => {
    expect(determineSeverity([
      { framework: 'x', severity: 'warning', detectionType: 'a', evidence: '', confidence: 0.5 },
      { framework: 'x', severity: 'disqualification', detectionType: 'b', evidence: '', confidence: 0.9 },
    ])).toBe('disqualification');
  });

  it('returns null for empty detections', () => {
    expect(determineSeverity([])).toBeNull();
  });
});
