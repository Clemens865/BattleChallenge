/**
 * `battle export` — Export benchmark data as CSV or JSON.
 * Serves David (enterprise evaluator) who needs raw data for procurement docs.
 */

import { Command } from 'commander';
import fs from 'node:fs';
import chalk from 'chalk';
import { BattleChallengeDB } from '../../db/index.js';
import { aggregateResults } from '../../scorer/index.js';

export const exportCommand = new Command('export')
  .description('Export benchmark results as CSV or JSON')
  .option('--format <format>', 'Output format: csv, json', 'json')
  .option('--output <file>', 'Output file path (stdout if omitted)')
  .option('--framework <name>', 'Filter by framework')
  .option('--task <id>', 'Filter by task')
  .action((opts) => {
    try {
      const db = new BattleChallengeDB();
      const entries = db.getLatestResults();

      let filtered = entries;
      if (opts.framework) {
        filtered = filtered.filter(e => e.frameworkName === opts.framework);
      }
      if (opts.task) {
        filtered = filtered.filter(e => e.taskId === opts.task);
      }

      if (filtered.length === 0) {
        console.error(chalk.yellow('No results to export.'));
        db.close();
        return;
      }

      let output: string;

      if (opts.format === 'csv') {
        const headers = [
          'framework', 'task', 'runs',
          'correctness_score', 'tests_total', 'tests_passed',
          'cost_usd', 'input_tokens', 'output_tokens', 'total_tokens',
          'speed_ms', 'api_call_ms',
          'reliability_pct', 'runs_passed', 'runs_attempted',
          'quality_readability', 'has_tests',
          'autonomy', 'high_variance',
        ];

        const rows = [headers.join(',')];

        for (const entry of filtered) {
          const runs = db.getRunsForFrameworkTask(entry.frameworkName, entry.taskId);
          const agg = aggregateResults(runs);
          if (!agg) continue;

          const m = agg.median;
          const reliabilityPct = m.reliability.runsAttempted > 0
            ? Math.round((m.reliability.runsPassed / m.reliability.runsAttempted) * 100)
            : 0;

          rows.push([
            entry.frameworkName, entry.taskId, entry.runCount,
            m.correctness.score, m.correctness.testsTotal, m.correctness.testsPassed,
            m.cost.totalCostUsd, m.cost.inputTokens, m.cost.outputTokens, m.cost.totalTokens,
            m.speed.totalMs, m.speed.apiCallMs,
            reliabilityPct, m.reliability.runsPassed, m.reliability.runsAttempted,
            m.quality.readabilityHeuristic, m.quality.hasTests ? 1 : 0,
            m.autonomy, agg.highVariance ? 1 : 0,
          ].join(','));
        }

        output = rows.join('\n') + '\n';
      } else {
        const results = [];
        for (const entry of filtered) {
          const runs = db.getRunsForFrameworkTask(entry.frameworkName, entry.taskId);
          const agg = aggregateResults(runs);
          if (!agg) continue;

          results.push({
            framework: entry.frameworkName,
            task: entry.taskId,
            runCount: entry.runCount,
            median: agg.median,
            iqr: agg.iqr,
            highVariance: agg.highVariance,
            verificationChain: agg.verificationChain,
            rawRuns: agg.runs.map(r => ({
              id: r.id,
              runNumber: r.runNumber,
              metrics: r.metrics,
              metadata: r.metadata,
              outputHash: r.outputHash,
              startedAt: r.startedAt,
              completedAt: r.completedAt,
            })),
          });
        }

        output = JSON.stringify({
          exportedAt: new Date().toISOString(),
          version: '0.1.0',
          results,
        }, null, 2) + '\n';
      }

      if (opts.output) {
        fs.writeFileSync(opts.output, output);
        console.log(chalk.green(`Exported ${filtered.length} result(s) to ${opts.output}`));
      } else {
        process.stdout.write(output);
      }

      db.close();
    } catch (err) {
      console.error(chalk.red(`Error: ${(err as Error).message}`));
      process.exit(1);
    }
  });
