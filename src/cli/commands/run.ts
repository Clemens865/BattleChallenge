/**
 * `battle run` — Execute benchmark tasks against a framework adapter.
 */

import { Command } from 'commander';
import fs from 'node:fs';
import path from 'node:path';
import chalk from 'chalk';
import { loadAdapter } from '../../adapters/loader.js';
import { loadTask, loadAllTasks } from '../../tasks/loader.js';
import { Runner } from '../../runner/index.js';
import { aggregateResults, formatProfile } from '../../scorer/index.js';
import { BattleChallengeDB } from '../../db/index.js';

export const runCommand = new Command('run')
  .description('Run benchmark tasks against a framework')
  .requiredOption('--framework <path>', 'Path to adapter directory or adapter.yaml')
  .option('--task <id>', 'Run a single task by ID')
  .option('--tags <tags>', 'Filter tasks by tags (comma-separated)')
  .option('--category <cat>', 'Filter by challenge category (recovery, navigation, tdd, etc.)')
  .option('--tasks-dir <path>', 'Path to tasks directory', './tasks')
  .option('--runs <n>', 'Number of runs per task', '5')
  .option('--timeout <ms>', 'Override timeout per task (ms)')
  .action(async (opts) => {
    try {
      const frameworkPath = path.resolve(opts.framework);
      const adapter = loadAdapter(frameworkPath);
      const adapterDir = fs.statSync(frameworkPath).isDirectory() ? frameworkPath : path.dirname(frameworkPath);
      console.log(chalk.bold(`\nBattleChallenge — Running ${adapter.name} v${adapter.version}`));
      console.log(chalk.dim(`Tier: ${adapter.tier} | Tags: ${adapter.tags.join(', ') || 'none'}\n`));

      const tasksDir = path.resolve(opts.tasksDir);
      let tasks = loadAllTasks(tasksDir);

      if (opts.task) {
        tasks = tasks.filter(t => t.id === opts.task);
        if (tasks.length === 0) {
          console.error(chalk.red(`Task not found: ${opts.task}`));
          process.exit(1);
        }
      }

      if (opts.category) {
        tasks = tasks.filter(t => t.category === opts.category);
      }

      if (opts.tags) {
        const filterTags = opts.tags.split(',').map((t: string) => t.trim());
        tasks = tasks.filter(t => filterTags.some((ft: string) => t.tags.includes(ft)));
      }

      tasks = tasks.filter(t => t.status === 'active');

      if (tasks.length === 0) {
        console.log(chalk.yellow('No matching tasks found.'));
        return;
      }

      console.log(chalk.dim(`Found ${tasks.length} task(s). Running ${opts.runs} run(s) each.\n`));

      const runner = new Runner(opts.timeout ? { timeoutMs: parseInt(opts.timeout) } : {});
      const db = new BattleChallengeDB();
      const numRuns = parseInt(opts.runs);

      // Register framework and tasks in DB before saving runs
      db.saveFramework(adapter);
      for (const task of tasks) {
        db.saveTask(task);
      }

      for (const task of tasks) {
        console.log(chalk.blue(`Task: ${task.id} (${task.type}, ${task.difficulty})`));

        for (let run = 1; run <= numRuns; run++) {
          process.stdout.write(chalk.dim(`  Run ${run}/${numRuns}... `));
          const taskDir = path.join(tasksDir, task.id);

          try {
            const result = await runner.executeTask(adapter, task, taskDir, run, adapterDir);
            db.saveRun(result);

            const status = result.metrics.correctness.score >= task.passingThreshold
              ? chalk.green('PASS')
              : chalk.red('FAIL');
            console.log(`${status} (score: ${result.metrics.correctness.score}, ${(result.metrics.speed.totalMs / 1000).toFixed(1)}s)`);
          } catch (err) {
            console.log(chalk.red(`ERROR: ${(err as Error).message}`));
          }
        }

        const runs = db.getRunsForFrameworkTask(adapter.name, task.id);
        const aggregated = aggregateResults(runs);
        if (aggregated) {
          console.log(chalk.dim('\n  Aggregated profile:'));
          console.log(formatProfile(aggregated.median));
          if (aggregated.highVariance) {
            console.log(chalk.yellow('  ⚠ High variance detected (IQR > 20% of median)'));
          }
        }
        console.log();
      }

      db.close();
      console.log(chalk.green('Done.'));
    } catch (err) {
      console.error(chalk.red(`Error: ${(err as Error).message}`));
      process.exit(1);
    }
  });
