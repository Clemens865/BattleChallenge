/**
 * Leaderboard construction with two views:
 * - Best Performance: each framework uses its best model config
 * - Controlled Model: all model-agnostic frameworks use the SAME model
 *
 * No composite scores. Multi-dimensional profiles only.
 */

import type {
  RunResult,
  MetricsProfile,
  FrameworkConfig,
  LeaderboardEntry,
  LeaderboardFilter,
  Track,
} from '../types/index.js';
import { aggregateResults } from './index.js';
import { compareFrameworks, type ComparisonResult } from './statistics.js';
import { filterFrameworks, type TagFilter } from '../taxonomy/index.js';

export interface LeaderboardData {
  entries: LeaderboardEntry[];
  view: 'best-performance' | 'controlled-model';
  controlledModel?: string;
  generatedAt: string;
}

export interface FrameworkComparison {
  metricName: string;
  frameworkA: string;
  frameworkB: string;
  result: ComparisonResult;
  valuesA: number[];
  valuesB: number[];
}

export function buildLeaderboard(
  frameworks: FrameworkConfig[],
  runsByFramework: Map<string, RunResult[]>,
  filter?: LeaderboardFilter,
): LeaderboardData {
  const view = filter?.view || 'best-performance';
  let filteredFrameworks = frameworks;

  if (filter?.tags) {
    const tagFilter: TagFilter = { type: 'any', tags: filter.tags };
    filteredFrameworks = filterFrameworks(frameworks, tagFilter);
  }

  if (view === 'controlled-model') {
    filteredFrameworks = filteredFrameworks.filter(
      fw => fw.tags.includes('model-agnostic')
    );
  }

  const entries: LeaderboardEntry[] = [];

  for (const fw of filteredFrameworks) {
    const runs = runsByFramework.get(fw.name) || [];
    if (runs.length === 0) continue;

    const agg = aggregateResults(runs);
    if (!agg) continue;

    const track: Track = filter?.track || 'open';
    const adapterType = filter?.adapterType || 'reference';

    entries.push({
      framework: fw,
      profile: agg.median,
      track,
      adapterType,
      view,
    });
  }

  return {
    entries,
    view,
    generatedAt: new Date().toISOString(),
  };
}

export function compareOnMetric(
  metricName: string,
  frameworkA: string,
  frameworkB: string,
  runsA: RunResult[],
  runsB: RunResult[],
  extractMetric: (m: MetricsProfile) => number,
): FrameworkComparison {
  const valuesA = runsA.map(r => extractMetric(r.metrics));
  const valuesB = runsB.map(r => extractMetric(r.metrics));
  const result = compareFrameworks(valuesA, valuesB);

  return { metricName, frameworkA, frameworkB, result, valuesA, valuesB };
}

export function sortByMetric(
  entries: LeaderboardEntry[],
  metric: 'correctness' | 'cost' | 'speed' | 'reliability' | 'quality',
  ascending = false,
): LeaderboardEntry[] {
  const extractor = (e: LeaderboardEntry): number => {
    switch (metric) {
      case 'correctness': return e.profile.correctness.score;
      case 'cost': return e.profile.cost.totalCostUsd;
      case 'speed': return e.profile.speed.totalMs;
      case 'reliability':
        return e.profile.reliability.runsAttempted > 0
          ? e.profile.reliability.runsPassed / e.profile.reliability.runsAttempted
          : 0;
      case 'quality': return e.profile.quality.readabilityHeuristic;
    }
  };

  return [...entries].sort((a, b) => {
    const va = extractor(a);
    const vb = extractor(b);
    return ascending ? va - vb : vb - va;
  });
}
