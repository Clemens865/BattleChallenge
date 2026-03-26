import { describe, it, expect } from 'vitest';
import { estimateTokens, computeCost, TokenCountingProxy } from '../src/runner/token-proxy.js';

describe('estimateTokens', () => {
  it('estimates ~4 chars per token', () => {
    expect(estimateTokens('hello world')).toBe(3); // 11 chars / 4 = 2.75 → 3
  });

  it('returns 0 for empty string', () => {
    expect(estimateTokens('')).toBe(0);
  });

  it('estimates longer text', () => {
    const text = 'a'.repeat(400);
    expect(estimateTokens(text)).toBe(100);
  });
});

describe('computeCost', () => {
  it('computes cost with default pricing', () => {
    const usage = { inputTokens: 1000, outputTokens: 500, totalTokens: 1500, apiCalls: 1, totalApiTimeMs: 100 };
    const cost = computeCost(usage);
    expect(cost.inputCostUsd).toBeCloseTo(0.015);
    expect(cost.outputCostUsd).toBeCloseTo(0.0375);
    expect(cost.totalCostUsd).toBeCloseTo(0.0525);
  });

  it('computes cost with custom pricing', () => {
    const usage = { inputTokens: 1_000_000, outputTokens: 500_000, totalTokens: 1_500_000, apiCalls: 10, totalApiTimeMs: 1000 };
    const cost = computeCost(usage, 3.0, 15.0);
    expect(cost.inputCostUsd).toBeCloseTo(3.0);
    expect(cost.outputCostUsd).toBeCloseTo(7.5);
    expect(cost.totalCostUsd).toBeCloseTo(10.5);
  });
});

describe('TokenCountingProxy', () => {
  it('initializes with zero usage', () => {
    const proxy = new TokenCountingProxy();
    const usage = proxy.getUsage();
    expect(usage.inputTokens).toBe(0);
    expect(usage.outputTokens).toBe(0);
    expect(usage.apiCalls).toBe(0);
  });

  it('resets usage', () => {
    const proxy = new TokenCountingProxy();
    proxy.resetUsage();
    const usage = proxy.getUsage();
    expect(usage.totalTokens).toBe(0);
  });
});
