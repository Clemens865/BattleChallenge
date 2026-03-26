/**
 * `battle compare` — Head-to-head comparison of two frameworks.
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { BattleChallengeDB } from '../../db/index.js';
import { aggregateResults, formatProfile } from '../../scorer/index.js';

export const compareCommand = new Command('compare')
  .description('Compare two frameworks head-to-head')
  .argument('<fw1>', 'First framework name')
  .argument('<fw2>', 'Second framework name')
  .option('--task <id>', 'Compare on a specific task')
  .option('--format <format>', 'Output format: text, json', 'text')
  .action((fw1: string, fw2: string, opts) => {
    try {
      const db = new BattleChallengeDB();
      const entries = db.getLatestResults();

      const fw1Entries = entries.filter(e => e.frameworkName === fw1);
      const fw2Entries = entries.filter(e => e.frameworkName === fw2);

      if (fw1Entries.length === 0) {
        console.error(chalk.red(`No results found for: ${fw1}`));
        db.close();
        process.exit(1);
      }
      if (fw2Entries.length === 0) {
        console.error(chalk.red(`No results found for: ${fw2}`));
        db.close();
        process.exit(1);
      }

      const commonTasks = fw1Entries
        .map(e => e.taskId)
        .filter(t => fw2Entries.some(e => e.taskId === t));

      const tasksToCompare = opts.task
        ? commonTasks.filter(t => t === opts.task)
        : commonTasks;

      if (tasksToCompare.length === 0) {
        console.log(chalk.yellow('No common tasks to compare.'));
        db.close();
        return;
      }

      if (opts.format === 'json') {
        const results: Record<string, unknown> = {};
        for (const taskId of tasksToCompare) {
          const runs1 = db.getRunsForFrameworkTask(fw1, taskId);
          const runs2 = db.getRunsForFrameworkTask(fw2, taskId);
          const agg1 = aggregateResults(runs1);
          const agg2 = aggregateResults(runs2);
          results[taskId] = { [fw1]: agg1?.median, [fw2]: agg2?.median };
        }
        console.log(JSON.stringify(results, null, 2));
      } else {
        console.log(chalk.bold(`\nBattleChallenge — ${fw1} vs ${fw2}\n`));
        console.log(chalk.dim(`Comparing on ${tasksToCompare.length} common task(s)\n`));

        for (const taskId of tasksToCompare) {
          console.log(chalk.dim(`--- Task: ${taskId} ---\n`));

          const runs1 = db.getRunsForFrameworkTask(fw1, taskId);
          const runs2 = db.getRunsForFrameworkTask(fw2, taskId);
          const agg1 = aggregateResults(runs1);
          const agg2 = aggregateResults(runs2);

          if (agg1) {
            console.log(chalk.blue.bold(`${fw1}:`));
            console.log(formatProfile(agg1.median));
            if (agg1.highVariance) console.log(chalk.yellow('  ⚠ High variance'));
            console.log();
          }

          if (agg2) {
            console.log(chalk.blue.bold(`${fw2}:`));
            console.log(formatProfile(agg2.median));
            if (agg2.highVariance) console.log(chalk.yellow('  ⚠ High variance'));
            console.log();
          }

          if (agg1 && agg2) {
            const scoreDiff = agg1.median.correctness.score - agg2.median.correctness.score;
            const costDiff = agg1.median.cost.totalCostUsd - agg2.median.cost.totalCostUsd;
            const speedDiff = agg1.median.speed.totalMs - agg2.median.speed.totalMs;

            console.log(chalk.dim('  Comparison:'));
            console.log(`    Correctness: ${scoreDiff > 0 ? chalk.green(`${fw1} +${scoreDiff}`) : scoreDiff < 0 ? chalk.green(`${fw2} +${-scoreDiff}`) : 'Tied'}`);
            console.log(`    Cost:        ${costDiff < 0 ? chalk.green(`${fw1} saves $${(-costDiff).toFixed(3)}`) : costDiff > 0 ? chalk.green(`${fw2} saves $${costDiff.toFixed(3)}`) : 'Tied'}`);
            console.log(`    Speed:       ${speedDiff < 0 ? chalk.green(`${fw1} ${(-speedDiff / 1000).toFixed(1)}s faster`) : speedDiff > 0 ? chalk.green(`${fw2} ${(speedDiff / 1000).toFixed(1)}s faster`) : 'Tied'}`);
            console.log();
          }
        }
      }

      db.close();
    } catch (err) {
      console.error(chalk.red(`Error: ${(err as Error).message}`));
      process.exit(1);
    }
  });
