/**
 * Two-tier submission model inspired by MLPerf.
 *
 * Verified Track:
 *   - Must use reference adapter template
 *   - Must run ALL task categories
 *   - Compliance tests required before submission
 *   - Results peer-reviewed before publication
 *
 * Open Track:
 *   - Custom adapters allowed
 *   - Pick any task subset
 *   - No compliance requirements
 *   - Shows what's possible, not what's standard
 */

import type { AdapterConfig, TaskDefinition, RunResult } from '../types/index.js';
import { hasMinimumRuns, MIN_RUNS } from '../scorer/statistics.js';

export type SubmissionTrack = 'verified' | 'open';

export interface SubmissionResult {
  track: SubmissionTrack;
  framework: string;
  adapterType: 'reference' | 'custom';
  tasksCovered: string[];
  totalTasks: number;
  complianceChecks: ComplianceCheck[];
  passed: boolean;
  submittedAt: string;
}

export interface ComplianceCheck {
  name: string;
  description: string;
  passed: boolean;
  message: string;
}

export function validateVerifiedSubmission(
  adapter: AdapterConfig,
  allTasks: TaskDefinition[],
  runsByTask: Map<string, RunResult[]>,
): SubmissionResult {
  const checks: ComplianceCheck[] = [];
  const activeTasks = allTasks.filter(t => t.status === 'active');
  const tasksCovered: string[] = [];

  // Check 1: Adapter must be reference type or follow reference template
  checks.push({
    name: 'reference-adapter',
    description: 'Adapter follows reference template',
    passed: adapter.tier === 'shell' || adapter.tier === 'structured',
    message: adapter.tier === 'shell' || adapter.tier === 'structured'
      ? 'Adapter uses supported tier'
      : 'Verified track requires shell or structured adapter tier',
  });

  // Check 2: Must run ALL active task categories
  const taskTypes = new Set(activeTasks.map(t => t.type));
  const coveredTypes = new Set<string>();

  for (const task of activeTasks) {
    const runs = runsByTask.get(task.id);
    if (runs && runs.length > 0) {
      tasksCovered.push(task.id);
      coveredTypes.add(task.type);
    }
  }

  checks.push({
    name: 'all-categories',
    description: 'All task categories covered',
    passed: taskTypes.size === coveredTypes.size,
    message: taskTypes.size === coveredTypes.size
      ? `All ${taskTypes.size} categories covered`
      : `Missing categories: ${[...taskTypes].filter(t => !coveredTypes.has(t)).join(', ')}`,
  });

  // Check 3: All tasks must have been run
  const allTasksRun = activeTasks.every(t => {
    const runs = runsByTask.get(t.id);
    return runs && runs.length > 0;
  });

  checks.push({
    name: 'all-tasks-run',
    description: 'All active tasks have been run',
    passed: allTasksRun,
    message: allTasksRun
      ? `All ${activeTasks.length} tasks run`
      : `Missing: ${activeTasks.filter(t => !runsByTask.has(t.id) || runsByTask.get(t.id)!.length === 0).map(t => t.id).join(', ')}`,
  });

  // Check 4: Minimum runs per task
  const allHaveMinRuns = activeTasks.every(t => {
    const runs = runsByTask.get(t.id);
    return runs && hasMinimumRuns(runs.length);
  });

  checks.push({
    name: 'minimum-runs',
    description: `Minimum ${MIN_RUNS} runs per task`,
    passed: allHaveMinRuns,
    message: allHaveMinRuns
      ? `All tasks have ${MIN_RUNS}+ runs`
      : 'Some tasks have fewer than minimum required runs',
  });

  // Check 5: No timeouts or crashes in majority of runs
  let totalRuns = 0;
  let failedRuns = 0;
  for (const [, runs] of runsByTask) {
    for (const run of runs) {
      totalRuns++;
      if (run.metrics.reliability.failureMode === 'crash' || run.metrics.reliability.failureMode === 'timeout') {
        failedRuns++;
      }
    }
  }
  const failRate = totalRuns > 0 ? failedRuns / totalRuns : 0;

  checks.push({
    name: 'stability',
    description: 'Less than 20% crash/timeout rate',
    passed: failRate < 0.2,
    message: failRate < 0.2
      ? `Failure rate: ${(failRate * 100).toFixed(1)}%`
      : `High failure rate: ${(failRate * 100).toFixed(1)}% (must be < 20%)`,
  });

  const passed = checks.every(c => c.passed);

  return {
    track: 'verified',
    framework: adapter.name,
    adapterType: 'reference',
    tasksCovered,
    totalTasks: activeTasks.length,
    complianceChecks: checks,
    passed,
    submittedAt: new Date().toISOString(),
  };
}

export function validateOpenSubmission(
  adapter: AdapterConfig,
  runsByTask: Map<string, RunResult[]>,
): SubmissionResult {
  const tasksCovered: string[] = [];

  for (const [taskId, runs] of runsByTask) {
    if (runs.length > 0) tasksCovered.push(taskId);
  }

  return {
    track: 'open',
    framework: adapter.name,
    adapterType: 'custom',
    tasksCovered,
    totalTasks: tasksCovered.length,
    complianceChecks: [],
    passed: true, // Open track always passes
    submittedAt: new Date().toISOString(),
  };
}

export function formatSubmissionResult(result: SubmissionResult): string {
  const lines: string[] = [];
  lines.push(`Track: ${result.track.toUpperCase()}`);
  lines.push(`Framework: ${result.framework}`);
  lines.push(`Adapter: ${result.adapterType}`);
  lines.push(`Tasks: ${result.tasksCovered.length}/${result.totalTasks}`);
  lines.push(`Status: ${result.passed ? 'PASSED' : 'FAILED'}`);

  if (result.complianceChecks.length > 0) {
    lines.push('');
    lines.push('Compliance Checks:');
    for (const check of result.complianceChecks) {
      const icon = check.passed ? '✓' : '✗';
      lines.push(`  ${icon} ${check.name}: ${check.message}`);
    }
  }

  return lines.join('\n');
}
