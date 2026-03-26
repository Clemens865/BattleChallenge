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
    adapterDir?: string,
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
      const result = this.executeShellAdapter(adapter, taskFile, outputDir, task.timeoutMs, adapterDir);
      exitCode = result.exitCode;
      stdout = result.stdout;
      stderr = result.stderr;
    } else {
      throw new Error(`Adapter tier '${adapter.tier}' not yet implemented`);
    }

    // Two-pass scoring (principle #7): if first attempt fails, show test output
    // and let the framework try again. This tests both generation AND debugging.
    if (task.twoPass && exitCode === 0) {
      const verifyDir = path.join(taskDir, task.verifyPath);
      if (fs.existsSync(verifyDir)) {
        const firstPass = this.runPytest(verifyDir, outputDir, true);
        if (firstPass.testsFailed > 0) {
          // Write test feedback for the framework to read
          const feedbackFile = path.join(outputDir, '.test-feedback.txt');
          fs.writeFileSync(feedbackFile, [
            '# TEST FEEDBACK — Second attempt',
            `# ${firstPass.testsPassed}/${firstPass.testsTotal} tests passed. Fix the failures below:`,
            '',
            firstPass.output,
          ].join('\n'));

          // Run adapter again with FEEDBACK_FILE env var
          const env = { ...process.env, TASK_FILE: taskFile, OUTPUT_DIR: outputDir, FEEDBACK_FILE: feedbackFile };
          try {
            execSync(adapter.run, {
              env,
              cwd: adapterDir || process.cwd(),
              timeout: task.timeoutMs,
              stdio: 'pipe',
              maxBuffer: 50 * 1024 * 1024,
            });
          } catch {
            // Second pass failed — score based on whatever state we have
          }
        }
      }
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
    adapterDir?: string,
  ): { exitCode: number; stdout: string; stderr: string } {
    const env = {
      ...process.env,
      TASK_FILE: taskFile,
      OUTPUT_DIR: outputDir,
    };

    const cwd = adapterDir || process.cwd();

    try {
      if (adapter.setup) {
        execSync(adapter.setup, { env, cwd, timeout: 60_000, stdio: 'pipe' });
      }

      const output = execSync(adapter.run, {
        env,
        cwd,
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

  private runPytest(
    verifyDir: string,
    outputDir: string,
    verbose = false,
  ): { testsTotal: number; testsPassed: number; testsFailed: number; output: string } {
    let testsTotal = 0;
    let testsPassed = 0;
    let testsFailed = 0;
    let output = '';

    try {
      const tbFlag = verbose ? '--tb=long' : '--tb=short';
      const result = execSync(
        `cd "${outputDir}" && python3 -m pytest "${verifyDir}" ${tbFlag} -q 2>&1 || true`,
        { timeout: 120_000, stdio: 'pipe', env: { ...process.env, OUTPUT_DIR: outputDir } },
      );
      output = result.toString();

      // Parse "X passed, Y failed" or just "X passed"
      const failMatch = output.match(/(\d+) failed/);
      const passMatch = output.match(/(\d+) passed/);
      const errorMatch = output.match(/(\d+) error/);

      testsPassed = passMatch ? parseInt(passMatch[1], 10) : 0;
      testsFailed = (failMatch ? parseInt(failMatch[1], 10) : 0) +
                    (errorMatch ? parseInt(errorMatch[1], 10) : 0);
      testsTotal = testsPassed + testsFailed;
    } catch {
      // Test execution failed entirely
    }

    return { testsTotal, testsPassed, testsFailed, output };
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
      const result = this.runPytest(verifyDir, outputDir);
      testsTotal = result.testsTotal;
      testsPassed = result.testsPassed;
    }

    // Binary scoring (principle #1): ALL tests must pass or score is 0
    // Graduated scoring: proportional to tests passed
    let score: number;
    if (task.scoring === 'binary') {
      score = (testsTotal > 0 && testsPassed === testsTotal) ? 100 : 0;
    } else {
      score = testsTotal > 0 ? Math.round((testsPassed / testsTotal) * 100) : 0;
    }

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
