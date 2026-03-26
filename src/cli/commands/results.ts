/**
 * `battle results` — Display the latest leaderboard in the terminal.
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { BattleChallengeDB } from '../../db/index.js';
import { aggregateResults, formatProfile } from '../../scorer/index.js';

export const resultsCommand = new Command('results')
  .description('View latest benchmark results')
  .option('--tags <tags>', 'Filter by tags (comma-separated)')
  .option('--format <format>', 'Output format: text, json', 'text')
  .action((opts) => {
    try {
      const db = new BattleChallengeDB();
      const entries = db.getLatestResults();

      if (entries.length === 0) {
        console.log(chalk.yellow('No results yet. Run `battle run` to generate benchmarks.'));
        db.close();
        return;
      }

      const frameworkNames = [...new Set(entries.map(e => e.frameworkName))];

      if (opts.format === 'json') {
        const results: Record<string, unknown> = {};
        for (const fw of frameworkNames) {
          const fwEntries = entries.filter(e => e.frameworkName === fw);
          const taskResults: Record<string, unknown> = {};
          for (const entry of fwEntries) {
            const runs = db.getRunsForFrameworkTask(entry.frameworkName, entry.taskId);
            const agg = aggregateResults(runs);
            if (agg) {
              taskResults[entry.taskId] = {
                median: agg.median,
                highVariance: agg.highVariance,
                runs: agg.runs.length,
              };
            }
          }
          results[fw] = taskResults;
        }
        console.log(JSON.stringify(results, null, 2));
      } else {
        console.log(chalk.bold('\nBattleChallenge — Latest Results\n'));
        console.log(chalk.dim('Profiles show median across runs. No composite scores — compare dimensions.\n'));

        for (const fw of frameworkNames) {
          const framework = db.getFramework(fw);
          const tags = framework?.tags ?? [];

          if (opts.tags) {
            const filterTags = opts.tags.split(',').map((t: string) => t.trim());
            if (!filterTags.some((ft: string) => tags.includes(ft))) continue;
          }

          console.log(chalk.bold.blue(`${fw}:`));
          if (tags.length > 0) {
            console.log(chalk.dim(`  Tags: ${tags.join(', ')}`));
          }

          const fwEntries = entries.filter(e => e.frameworkName === fw);
          for (const entry of fwEntries) {
            const runs = db.getRunsForFrameworkTask(entry.frameworkName, entry.taskId);
            const agg = aggregateResults(runs);
            if (agg) {
              console.log(chalk.dim(`\n  Task: ${entry.taskId} (${entry.runCount} runs)`));
              console.log(formatProfile(agg.median));
              if (agg.highVariance) {
                console.log(chalk.yellow('  ⚠ High variance'));
              }
            }
          }
          console.log();
        }
      }

      db.close();
    } catch (err) {
      console.error(chalk.red(`Error: ${(err as Error).message}`));
      process.exit(1);
    }
  });
