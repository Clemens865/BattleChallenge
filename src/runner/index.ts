/**
 * Runner engine — executes benchmark tasks against framework adapters.
 * Manages Docker containers, token proxy, timing, and result collection.
 */

import { execSync, spawn, type ChildProcess } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import type {
  AdapterConfig,
  TaskDefinition,
  TaskContext,
  RunResult,
  MetricsProfile,
  RunnerConfig,
  RunConfig,
} from '../types/index.js';
import { DEFAULT_RUNNER_CONFIG } from '../types/index.js';

export class Runner {
  private config: RunnerConfig;

  constructor(config: Partial<RunnerConfig> = {}) {
    this.config = { ...DEFAULT_RUNNER_CONFIG, ...config };
  }

  async executeTask(
    adapter: AdapterConfig,
    task: TaskDefinition,
    taskDir: string,
    runNumber: number,
  ): Promise<RunResult> {
    const runId = `bc-${adapter.name}-${task.id}-${runNumber}-${Date.now()}`;
    const outputDir = path.join(taskDir, '.output', runId);
    fs.mkdirSync(outputDir, { recursive: true });

    const taskFile = path.join(taskDir, task.requirementsPath);
    const startedAt = new Date().toISOString();
    const startMs = performance.now();

    let exitCode: number;
    let stdout = '';
    let stderr = '';

    if (adapter.tier === 'shell') {
      const result = this.executeShellAdapter(adapter, taskFile, outputDir, task.timeoutMs);
      exitCode = result.exitCode;
      stdout = result.stdout;
      stderr = result.stderr;
    } else {
      // Structured and API tiers will be implemented in later phases
      throw new Error(`Adapter tier '${adapter.tier}' not yet implemented`);
    }

    const endMs = performance.now();
    const completedAt = new Date().toISOString();
    const totalMs = endMs - startMs;

    const outputHash = this.hashDirectory(outputDir);

    const metrics = await this.scoreRun(task, taskDir, outputDir, totalMs, exitCode);

    return {
      id: runId,
      frameworkName: adapter.name,
      frameworkVersion: adapter.version,
      taskId: task.id,
      runNumber,
      metrics,
      metadata: {
        frameworkVersion: adapter.version,
        modelUsed: adapter.modelDefault || 'unknown',
        modelVersion: adapter.modelDefault || 'unknown',
        adapterType: 'reference',
        adapterVersion: adapter.version,
        dockerImageHash: '',
        runTimestamp: startedAt,
      },
      outputHash,
      startedAt,
      completedAt,
    };
  }

  private executeShellAdapter(
    adapter: AdapterConfig,
    taskFile: string,
    outputDir: string,
    timeoutMs: number,
  ): { exitCode: number; stdout: string; stderr: string } {
    const env = {
      ...process.env,
      TASK_FILE: taskFile,
      OUTPUT_DIR: outputDir,
    };

    try {
      if (adapter.setup) {
        execSync(adapter.setup, { env, timeout: 60_000, stdio: 'pipe' });
      }

      const output = execSync(adapter.run, {
        env,
        timeout: timeoutMs || this.config.timeoutMs,
        stdio: 'pipe',
        maxBuffer: 50 * 1024 * 1024,
      });

      return {
        exitCode: 0,
        stdout: output.toString(),
        stderr: '',
      };
    } catch (err: unknown) {
      const error = err as { status?: number; stdout?: Buffer; stderr?: Buffer };
      return {
        exitCode: error.status ?? 1,
        stdout: error.stdout?.toString() ?? '',
        stderr: error.stderr?.toString() ?? '',
      };
    }
  }

  private async scoreRun(
    task: TaskDefinition,
    taskDir: string,
    outputDir: string,
    totalMs: number,
    exitCode: number,
  ): Promise<MetricsProfile> {
    const verifyDir = path.join(taskDir, task.verifyPath);
    let testsTotal = 0;
    let testsPassed = 0;

    if (fs.existsSync(verifyDir)) {
      try {
        const result = execSync(
          `cd "${outputDir}" && python3 -m pytest "${verifyDir}" --tb=short -q 2>&1 || true`,
          { timeout: 120_000, stdio: 'pipe' },
        );
        const output = result.toString();
        const match = output.match(/(\d+) passed(?:.*?)(\d+)? failed/);
        if (match) {
          testsPassed = parseInt(match[1], 10);
          testsTotal = testsPassed + (match[2] ? parseInt(match[2], 10) : 0);
        } else {
          const passedMatch = output.match(/(\d+) passed/);
          if (passedMatch) {
            testsPassed = parseInt(passedMatch[1], 10);
            testsTotal = testsPassed;
          }
        }
      } catch {
        // Test execution failed
      }
    }

    const score = testsTotal > 0 ? Math.round((testsPassed / testsTotal) * 100) : 0;

    return {
      correctness: {
        testsTotal,
        testsPassed,
        score,
        edgeCasesHandled: 0,
        outcomeVerification: exitCode === 0,
      },
      cost: {
        inputTokens: 0,
        outputTokens: 0,
        totalTokens: 0,
        inputCostUsd: 0,
        outputCostUsd: 0,
        totalCostUsd: 0,
        costPerTestPassed: 0,
      },
      speed: {
        totalMs,
        apiCallMs: 0,
        processingMs: totalMs,
        timeToFirstPassingTest: null,
      },
      reliability: {
        runsAttempted: 1,
        runsPassed: exitCode === 0 ? 1 : 0,
        varianceIqr: 0,
        failureMode: exitCode !== 0 ? 'crash' : null,
      },
      quality: {
        hasTests: false,
        testCoveragePct: null,
        mutationScore: null,
        humanReviewScore: null,
        readabilityHeuristic: 0,
      },
      autonomy: 0,
    };
  }

  private hashDirectory(dir: string): string {
    const hash = crypto.createHash('sha256');
    if (!fs.existsSync(dir)) return hash.digest('hex');

    const files = this.walkDir(dir).sort();
    for (const file of files) {
      hash.update(file);
      hash.update(fs.readFileSync(path.join(dir, file)));
    }
    return hash.digest('hex');
  }

  private walkDir(dir: string, prefix = ''): string[] {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    const files: string[] = [];
    for (const entry of entries) {
      const rel = path.join(prefix, entry.name);
      if (entry.isDirectory()) {
        files.push(...this.walkDir(path.join(dir, entry.name), rel));
      } else {
        files.push(rel);
      }
    }
    return files;
  }
}
