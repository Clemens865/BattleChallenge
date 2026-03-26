/**
 * `battle reproduce` — Reproduce a published benchmark result.
 * Serves David (enterprise evaluator) and Dr. Tanaka (benchmark skeptic).
 */

import { Command } from 'commander';
import path from 'node:path';
import chalk from 'chalk';
import { BattleChallengeDB } from '../../db/index.js';
import { loadAdapter } from '../../adapters/loader.js';
import { loadTask } from '../../tasks/loader.js';
import { Runner } from '../../runner/index.js';
import { aggregateResults, formatProfile } from '../../scorer/index.js';

export const reproduceCommand = new Command('reproduce')
  .description('Reproduce a benchmark result for verification')
  .requiredOption('--framework <name>', 'Framework to reproduce')
  .requiredOption('--task <id>', 'Task to reproduce')
  .option('--adapter <path>', 'Path to adapter (defaults to ./adapters/<framework>)')
  .option('--tasks-dir <path>', 'Path to tasks directory', './tasks')
  .option('--runs <n>', 'Number of reproduction runs', '5')
  .action(async (opts) => {
    try {
      const adapterPath = opts.adapter || path.join('./adapters', opts.framework);
      const adapter = loadAdapter(adapterPath);
      const taskDir = path.join(path.resolve(opts.tasksDir), opts.task);
      const task = loadTask(taskDir);

      console.log(chalk.bold(`\nReproducing: ${opts.framework} on ${opts.task}`));
      console.log(chalk.dim(`Adapter: ${adapterPath}`));
      console.log(chalk.dim(`Runs: ${opts.runs}\n`));

      // Load original results for comparison
      const db = new BattleChallengeDB();
      const originalRuns = db.getRunsForFrameworkTask(opts.framework, opts.task);
      const originalAgg = aggregateResults(originalRuns);

      if (originalAgg) {
        console.log(chalk.dim('Original results:'));
        console.log(formatProfile(originalAgg.median));
        console.log();
      }

      // Run reproduction
      console.log(chalk.bold('Reproduction runs:'));
      const runner = new Runner();
      const numRuns = parseInt(opts.runs);
      const reproRuns = [];

      for (let i = 1; i <= numRuns; i++) {
        process.stdout.write(chalk.dim(`  Run ${i}/${numRuns}... `));
        try {
          const result = await runner.executeTask(adapter, task, taskDir, i);
          reproRuns.push(result);
          const status = result.metrics.correctness.score >= task.passingThreshold
            ? chalk.green('PASS')
            : chalk.red('FAIL');
          console.log(`${status} (score: ${result.metrics.correctness.score})`);
        } catch (err) {
          console.log(chalk.red(`ERROR: ${(err as Error).message}`));
        }
      }

      if (reproRuns.length === 0) {
        console.log(chalk.red('\nNo successful reproduction runs.'));
        db.close();
        return;
      }

      const reproAgg = aggregateResults(reproRuns);
      if (reproAgg) {
        console.log(chalk.bold('\nReproduction results:'));
        console.log(formatProfile(reproAgg.median));

        if (originalAgg) {
          const scoreDiff = Math.abs(reproAgg.median.correctness.score - originalAgg.median.correctness.score);
          console.log(chalk.bold('\nReproducibility:'));

          if (scoreDiff <= 5) {
            console.log(chalk.green(`  ✓ Correctness within 5 points (diff: ${scoreDiff})`));
          } else if (scoreDiff <= 15) {
            console.log(chalk.yellow(`  ~ Correctness within 15 points (diff: ${scoreDiff})`));
          } else {
            console.log(chalk.red(`  ✗ Significant correctness divergence (diff: ${scoreDiff})`));
          }
        }
      }

      db.close();
    } catch (err) {
      console.error(chalk.red(`Error: ${(err as Error).message}`));
      process.exit(1);
    }
  });
