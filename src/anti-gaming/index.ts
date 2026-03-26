/**
 * Anti-gaming detection system.
 *
 * Detection layers:
 * - Static analysis: Scan adapter code for hardcoded answers
 * - Behavioral analysis: Compare public vs secret task scores
 * - Token pattern analysis: Flag unusually low token usage
 * - Community auditing: All adapters open-source
 */

import type { RunResult } from '../types/index.js';

export type GamingSeverity = 'warning' | 'flag' | 'disqualification' | 'ban';

export interface GamingDetection {
  framework: string;
  severity: GamingSeverity;
  detectionType: string;
  evidence: string;
  taskId?: string;
  confidence: number;
}

export function detectPublicSecretGap(
  publicScores: number[],
  secretScores: number[],
  threshold = 0.15,
): GamingDetection | null {
  if (publicScores.length === 0 || secretScores.length === 0) return null;

  const publicAvg = publicScores.reduce((a, b) => a + b, 0) / publicScores.length;
  const secretAvg = secretScores.reduce((a, b) => a + b, 0) / secretScores.length;

  if (publicAvg === 0) return null;

  const gap = (publicAvg - secretAvg) / publicAvg;

  if (gap > threshold) {
    return {
      framework: '',
      severity: 'flag',
      detectionType: 'behavioral-analysis',
      evidence: `Public task average: ${publicAvg.toFixed(1)}, Secret task average: ${secretAvg.toFixed(1)}, Gap: ${(gap * 100).toFixed(1)}% (threshold: ${(threshold * 100).toFixed(1)}%)`,
      confidence: Math.min(gap / threshold, 1),
    };
  }

  return null;
}

export function detectAnomalousTokenUsage(
  runs: RunResult[],
  medianTokens: number,
  anomalyThreshold = 0.3,
): GamingDetection[] {
  const detections: GamingDetection[] = [];

  for (const run of runs) {
    const tokens = run.metrics.cost.totalTokens;
    if (medianTokens > 0 && tokens < medianTokens * anomalyThreshold) {
      detections.push({
        framework: run.frameworkName,
        severity: 'flag',
        detectionType: 'token-pattern-analysis',
        evidence: `Task ${run.taskId}: used ${tokens} tokens vs median ${medianTokens} (${((tokens / medianTokens) * 100).toFixed(1)}% of expected)`,
        taskId: run.taskId,
        confidence: 1 - (tokens / medianTokens),
      });
    }
  }

  return detections;
}

export function scanAdapterForHardcodedAnswers(
  adapterCode: string,
  taskIds: string[],
): GamingDetection[] {
  const detections: GamingDetection[] = [];

  for (const taskId of taskIds) {
    if (adapterCode.includes(taskId)) {
      detections.push({
        framework: '',
        severity: 'disqualification',
        detectionType: 'static-analysis',
        evidence: `Adapter code references task ID: ${taskId}`,
        taskId,
        confidence: 0.9,
      });
    }
  }

  // Check for suspiciously specific strings
  const suspiciousPatterns = [
    /def validate_email/,
    /hardcoded|precomputed|cached_answer/i,
    /benchmark_specific/i,
  ];

  for (const pattern of suspiciousPatterns) {
    if (pattern.test(adapterCode)) {
      detections.push({
        framework: '',
        severity: 'warning',
        detectionType: 'static-analysis',
        evidence: `Adapter code matches suspicious pattern: ${pattern.source}`,
        confidence: 0.5,
      });
    }
  }

  return detections;
}

export function determineSeverity(detections: GamingDetection[]): GamingSeverity | null {
  if (detections.length === 0) return null;

  const severityOrder: GamingSeverity[] = ['ban', 'disqualification', 'flag', 'warning'];
  for (const severity of severityOrder) {
    if (detections.some(d => d.severity === severity)) return severity;
  }

  return 'warning';
}
