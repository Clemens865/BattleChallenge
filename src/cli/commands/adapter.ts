/**
 * `battle adapter` — Manage framework adapters.
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { loadAdapter, scaffoldAdapter } from '../../adapters/loader.js';
import type { AdapterTier } from '../../types/index.js';

export const adapterCommand = new Command('adapter')
  .description('Manage framework adapters');

adapterCommand
  .command('init')
  .description('Scaffold a new adapter')
  .requiredOption('--framework <name>', 'Framework name')
  .option('--tier <tier>', 'Adapter tier: shell, structured, api', 'shell')
  .option('--output <dir>', 'Output directory', './adapters')
  .action((opts) => {
    try {
      const dir = scaffoldAdapter(opts.framework, opts.tier as AdapterTier, opts.output);
      console.log(chalk.green(`Adapter scaffolded at: ${dir}`));
      console.log(chalk.dim('\nNext steps:'));
      console.log(chalk.dim('  1. Edit adapter.yaml with your framework details'));
      if (opts.tier === 'shell') {
        console.log(chalk.dim('  2. Edit adapter.sh with your framework command'));
      }
      console.log(chalk.dim(`  3. Run: battle adapter test --path ${dir}`));
    } catch (err) {
      console.error(chalk.red(`Error: ${(err as Error).message}`));
      process.exit(1);
    }
  });

adapterCommand
  .command('test')
  .description('Validate an adapter configuration')
  .requiredOption('--path <path>', 'Path to adapter directory')
  .action((opts) => {
    try {
      const adapter = loadAdapter(opts.path);
      console.log(chalk.green('Adapter is valid:'));
      console.log(`  Name:    ${adapter.name}`);
      console.log(`  Version: ${adapter.version}`);
      console.log(`  Tier:    ${adapter.tier}`);
      console.log(`  Tags:    ${adapter.tags.join(', ') || 'none'}`);
      console.log(`  Run:     ${adapter.run}`);
    } catch (err) {
      console.error(chalk.red(`Validation failed: ${(err as Error).message}`));
      process.exit(1);
    }
  });
