/**
 * `battle task` — Manage benchmark tasks.
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { loadTask, loadAllTasks, scaffoldTask } from '../../tasks/loader.js';
import type { TaskType, DifficultyTier } from '../../types/index.js';

export const taskCommand = new Command('task')
  .description('Manage benchmark tasks');

taskCommand
  .command('init')
  .description('Scaffold a new task')
  .requiredOption('--id <id>', 'Task ID (e.g., task-042-user-auth)')
  .option('--type <type>', 'Task type: prd, coding, multi-step, tool-use, rag, multi-agent', 'coding')
  .option('--tier <tier>', 'Difficulty tier: T1, T2, T3, T4', 'T1')
  .option('--output <dir>', 'Output directory', './tasks')
  .action((opts) => {
    try {
      const dir = scaffoldTask(opts.id, opts.type as TaskType, opts.tier as DifficultyTier, opts.output);
      console.log(chalk.green(`Task scaffolded at: ${dir}`));
      console.log(chalk.dim('\nNext steps:'));
      console.log(chalk.dim('  1. Edit requirements.md with the task description'));
      console.log(chalk.dim('  2. Write outcome tests in verify/test_outcomes.py'));
      console.log(chalk.dim('  3. Create a reference solution in reference/solution/'));
      console.log(chalk.dim(`  4. Run: battle task validate --path ${dir}`));
    } catch (err) {
      console.error(chalk.red(`Error: ${(err as Error).message}`));
      process.exit(1);
    }
  });

taskCommand
  .command('validate')
  .description('Validate a task definition')
  .requiredOption('--path <path>', 'Path to task directory')
  .action((opts) => {
    try {
      const task = loadTask(opts.path);
      console.log(chalk.green('Task is valid:'));
      console.log(`  ID:         ${task.id}`);
      console.log(`  Name:       ${task.name}`);
      console.log(`  Type:       ${task.type}`);
      console.log(`  Difficulty: ${task.difficulty}`);
      console.log(`  Status:     ${task.status}`);
      console.log(`  Tags:       ${task.tags.join(', ') || 'none'}`);
      console.log(`  Timeout:    ${task.timeoutMs / 1000}s`);
    } catch (err) {
      console.error(chalk.red(`Validation failed: ${(err as Error).message}`));
      process.exit(1);
    }
  });

taskCommand
  .command('list')
  .description('List all available tasks')
  .option('--tasks-dir <path>', 'Path to tasks directory', './tasks')
  .option('--status <status>', 'Filter by status: active, secret, retired')
  .action((opts) => {
    try {
      let tasks = loadAllTasks(opts.tasksDir);

      if (opts.status) {
        tasks = tasks.filter(t => t.status === opts.status);
      }

      if (tasks.length === 0) {
        console.log(chalk.yellow('No tasks found.'));
        return;
      }

      console.log(chalk.bold(`\nFound ${tasks.length} task(s):\n`));
      console.log(chalk.dim('  ID                          Type         Tier  Status  Tags'));
      console.log(chalk.dim('  ' + '─'.repeat(75)));

      for (const task of tasks) {
        const status = task.status === 'active' ? chalk.green(task.status)
          : task.status === 'secret' ? chalk.yellow(task.status)
          : chalk.dim(task.status);
        console.log(`  ${task.id.padEnd(30)} ${task.type.padEnd(13)} ${task.difficulty}    ${status.padEnd(18)} ${task.tags.join(', ')}`);
      }
      console.log();
    } catch (err) {
      console.error(chalk.red(`Error: ${(err as Error).message}`));
      process.exit(1);
    }
  });
