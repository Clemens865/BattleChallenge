#!/usr/bin/env node

/**
 * BattleChallenge CLI — the power-user interface for running benchmarks.
 *
 * Commands:
 *   battle run       — Run benchmarks against a framework
 *   battle results   — View latest leaderboard
 *   battle compare   — Head-to-head comparison
 *   battle adapter   — Manage adapters
 *   battle task      — Manage tasks
 */

import { Command } from 'commander';
import { runCommand } from './commands/run.js';
import { resultsCommand } from './commands/results.js';
import { compareCommand } from './commands/compare.js';
import { adapterCommand } from './commands/adapter.js';
import { taskCommand } from './commands/task.js';
import { quickCommand } from './commands/quick.js';
import { exportCommand } from './commands/export.js';
import { reproduceCommand } from './commands/reproduce.js';

const program = new Command();

program
  .name('battle')
  .description('BattleChallenge — benchmark agentic AI frameworks head-to-head')
  .version('0.1.0');

program.addCommand(runCommand);
program.addCommand(resultsCommand);
program.addCommand(compareCommand);
program.addCommand(adapterCommand);
program.addCommand(taskCommand);
program.addCommand(quickCommand);
program.addCommand(exportCommand);
program.addCommand(reproduceCommand);

program.parse();
