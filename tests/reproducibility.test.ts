import { describe, it, expect } from 'vitest';
import {
  assessReproducibility,
  assessBinaryReproducibility,
  REPRODUCIBILITY_CV_THRESHOLD,
  MIN_RUNS,
} from '../src/scorer/statistics.js';

describe('assessReproducibility', () => {
  it('requires minimum runs', () => {
    const report = assessReproducibility([80, 82]);
    expect(report.reproducible).toBe(false);
    expect(report.verdict).toContain('Insufficient');
  });

  it('marks consistent scores as reproducible', () => {
    const report = assessReproducibility([80, 82, 79, 81, 80]);
    expect(report.reproducible).toBe(true);
    expect(report.coefficientOfVariation).toBeLessThan(REPRODUCIBILITY_CV_THRESHOLD);
  });

  it('marks wildly varying scores as not reproducible', () => {
    const report = assessReproducibility([10, 90, 20, 80, 50]);
    expect(report.reproducible).toBe(false);
    expect(report.coefficientOfVariation).toBeGreaterThan(REPRODUCIBILITY_CV_THRESHOLD);
  });

  it('marks identical scores as perfectly reproducible', () => {
    const report = assessReproducibility([100, 100, 100, 100, 100]);
    expect(report.reproducible).toBe(true);
    expect(report.coefficientOfVariation).toBe(0);
    expect(report.verdict).toContain('Perfectly');
  });

  it('computes correct mean and stddev', () => {
    const report = assessReproducibility([60, 60, 60, 60, 60]);
    expect(report.mean).toBe(60);
    expect(report.stddev).toBe(0);
  });

  it('reports pass rate', () => {
    const report = assessReproducibility([100, 0, 100, 0, 100]);
    expect(report.passRate).toBe(0.6);
  });

  it('allows custom CV threshold', () => {
    const scores = [70, 80, 75, 85, 72];
    const strict = assessReproducibility(scores, 0.05);
    const lenient = assessReproducibility(scores, 0.20);
    expect(strict.reproducible).toBe(false);
    expect(lenient.reproducible).toBe(true);
  });
});

describe('assessBinaryReproducibility', () => {
  it('requires minimum runs', () => {
    const result = assessBinaryReproducibility([true, false]);
    expect(result.reproducible).toBe(false);
  });

  it('consistent pass is reproducible', () => {
    const result = assessBinaryReproducibility([true, true, true, true, true]);
    expect(result.reproducible).toBe(true);
    expect(result.passRate).toBe(1.0);
  });

  it('consistent fail is reproducible', () => {
    const result = assessBinaryReproducibility([false, false, false, false, false]);
    expect(result.reproducible).toBe(true);
    expect(result.passRate).toBe(0.0);
  });

  it('4/5 pass is reproducible', () => {
    const result = assessBinaryReproducibility([true, true, true, true, false]);
    expect(result.reproducible).toBe(true);
    expect(result.passRate).toBe(0.8);
  });

  it('3/5 split is NOT reproducible', () => {
    const result = assessBinaryReproducibility([true, false, true, false, true]);
    expect(result.reproducible).toBe(false);
    expect(result.passRate).toBe(0.6);
  });

  it('2/5 pass is NOT reproducible', () => {
    const result = assessBinaryReproducibility([true, true, false, false, false]);
    expect(result.reproducible).toBe(false);
  });
});
