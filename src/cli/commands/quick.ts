/**
 * `battle quick` — Instant comparison of two frameworks (zero-install experience).
 * This is the "wow moment" for Maya (indie dev persona).
 *
 * Usage: npx battlechallenge quick claude-code aider
 */

import { Command } from 'commander';
import path from 'node:path';
import chalk from 'chalk';
import { loadAdapter } from '../../adapters/loader.js';
import { loadAllTasks } from '../../tasks/loader.js';
import { Runner } from '../../runner/index.js';
import { aggregateResults, formatProfile } from '../../scorer/index.js';
import { BattleChallengeDB } from '../../db/index.js';

export const quickCommand = new Command('quick')
  .description('Instantly compare two frameworks (quick benchmark)')
  .argument('<fw1>', 'First framework name or adapter path')
  .argument('<fw2>', 'Second framework name or adapter path')
  .option('--tasks-dir <path>', 'Path to tasks directory', './tasks')
  .option('--tier <tier>', 'Only run tasks of this difficulty tier', 'T1')
  .action(async (fw1: string, fw2: string, opts) => {
    try {
      console.log(chalk.bold(`\n⚡ BattleChallenge Quick Compare: ${fw1} vs ${fw2}\n`));

      const adaptersDir = path.resolve('./adapters');
      let adapter1, adapter2;

      try {
        adapter1 = loadAdapter(path.join(adaptersDir, fw1));
      } catch {
        console.error(chalk.red(`Adapter not found for '${fw1}'. Available adapters in ./adapters/`));
        process.exit(1);
      }

      try {
        adapter2 = loadAdapter(path.join(adaptersDir, fw2));
      } catch {
        console.error(chalk.red(`Adapter not found for '${fw2}'. Available adapters in ./adapters/`));
        process.exit(1);
      }

      const tasksDir = path.resolve(opts.tasksDir);
      let tasks = loadAllTasks(tasksDir).filter(t => t.status === 'active');

      if (opts.tier) {
        tasks = tasks.filter(t => t.difficulty === opts.tier);
      }

      // Quick mode: only 1 run per task (not the full 5)
      const runner = new Runner();
      const db = new BattleChallengeDB();

      for (const task of tasks) {
        console.log(chalk.dim(`Running ${task.id}...`));

        for (const adapter of [adapter1, adapter2]) {
          try {
            const result = await runner.executeTask(adapter, task, path.join(tasksDir, task.id), 1);
            db.saveRun(result);
          } catch (err) {
            console.error(chalk.dim(`  ${adapter.name}: ${(err as Error).message}`));
          }
        }
      }

      // Display results
      console.log(chalk.bold(`\n${'═'.repeat(60)}`));
      console.log(chalk.bold(`  ${fw1} vs ${fw2} — Quick Benchmark Results`));
      console.log(chalk.bold(`${'═'.repeat(60)}\n`));

      for (const adapter of [adapter1, adapter2]) {
        console.log(chalk.blue.bold(`${adapter.name} v${adapter.version}:`));
        console.log(chalk.dim(`  Tags: ${adapter.tags.join(', ') || 'none'}`));

        for (const task of tasks) {
          const runs = db.getRunsForFrameworkTask(adapter.name, task.id);
          const agg = aggregateResults(runs);
          if (agg) {
            console.log(chalk.dim(`\n  Task: ${task.id}`));
            console.log(formatProfile(agg.median));
          }
        }
        console.log();
      }

      console.log(chalk.dim('Note: Quick mode uses 1 run per task. For statistical rigor, use `battle run --runs 5`.'));

      db.close();
    } catch (err) {
      console.error(chalk.red(`Error: ${(err as Error).message}`));
      process.exit(1);
    }
  });
