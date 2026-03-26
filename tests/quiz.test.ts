import { describe, it, expect } from 'vitest';
import { computeRecommendation } from '../src/quiz/index.js';
import type { QuizAnswers } from '../src/quiz/index.js';
import type { MetricsProfile, FrameworkConfig } from '../src/types/index.js';

function makeFramework(name: string, tags: string[], overrides: Partial<{ score: number; cost: number; speed: number }> = {}): { config: FrameworkConfig; profile: MetricsProfile } {
  return {
    config: {
      name,
      version: '1.0.0',
      tags,
      tier: 'shell',
      run: './adapter.sh',
    },
    profile: {
      correctness: { testsTotal: 10, testsPassed: 8, score: overrides.score ?? 80, edgeCasesHandled: 0, outcomeVerification: true },
      cost: { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, inputCostUsd: 0.01, outputCostUsd: 0.005, totalCostUsd: overrides.cost ?? 0.1, costPerTestPassed: 0.01 },
      speed: { totalMs: overrides.speed ?? 10000, apiCallMs: 5000, processingMs: 5000, timeToFirstPassingTest: null },
      reliability: { runsAttempted: 5, runsPassed: 4, varianceIqr: 5, failureMode: null },
      quality: { hasTests: false, testCoveragePct: null, mutationScore: null, humanReviewScore: null, readabilityHeuristic: 60 },
      autonomy: 0,
    },
  };
}

describe('computeRecommendation', () => {
  const frameworks = [
    makeFramework('claude-code', ['coding-agent', 'cli', 'model-locked:claude'], { score: 90, cost: 0.15, speed: 15000 }),
    makeFramework('aider', ['coding-agent', 'cli', 'model-agnostic', 'python'], { score: 75, cost: 0.03, speed: 8000 }),
    makeFramework('langgraph', ['orchestration', 'library', 'python', 'model-agnostic', 'multi-agent'], { score: 82, cost: 0.14, speed: 18000 }),
  ];

  it('recommends cost-effective framework when cost is priority', () => {
    const answers: QuizAnswers = {
      projectType: 'api',
      priority: 'cost',
      modelPreference: 'no-preference',
      language: 'python',
      teamSize: 'solo',
    };
    const result = computeRecommendation(answers, frameworks);
    expect(result.recommended).toBe('aider');
    expect(result.score).toBeGreaterThan(0);
    expect(result.alternatives.length).toBeGreaterThan(0);
  });

  it('recommends accurate framework when correctness is priority', () => {
    const answers: QuizAnswers = {
      projectType: 'web-app',
      priority: 'correctness',
      modelPreference: 'claude',
      language: 'typescript',
      teamSize: 'small-team',
    };
    const result = computeRecommendation(answers, frameworks);
    expect(result.recommended).toBe('claude-code');
  });

  it('recommends multi-agent framework for multi-agent projects', () => {
    const answers: QuizAnswers = {
      projectType: 'multi-agent',
      priority: 'reliability',
      modelPreference: 'no-preference',
      language: 'python',
      teamSize: 'enterprise',
    };
    const result = computeRecommendation(answers, frameworks);
    expect(result.recommended).toBe('langgraph');
  });

  it('provides reasoning for recommendation', () => {
    const answers: QuizAnswers = {
      projectType: 'api',
      priority: 'speed',
      modelPreference: 'no-preference',
      language: 'python',
      teamSize: 'solo',
    };
    const result = computeRecommendation(answers, frameworks);
    expect(result.reasoning.length).toBeGreaterThan(0);
  });
});
