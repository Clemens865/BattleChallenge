/**
 * Database layer using SQLite for local storage.
 * Stores run results, framework configs, and task definitions.
 */

import Database from 'better-sqlite3';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import type { RunResult, AggregatedResult, MetricsProfile, FrameworkConfig, TaskDefinition } from '../types/index.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_DB_PATH = path.join(__dirname, '..', '..', 'battlechallenge.db');

export class BattleChallengeDB {
  private db: Database.Database;

  constructor(dbPath: string = DEFAULT_DB_PATH) {
    this.db = new Database(dbPath);
    this.db.pragma('journal_mode = WAL');
    this.init();
  }

  private init(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS frameworks (
        name TEXT PRIMARY KEY,
        version TEXT NOT NULL,
        tags TEXT NOT NULL,
        tier TEXT NOT NULL,
        config TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        tags TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        passing_threshold INTEGER DEFAULT 60,
        excellence_threshold INTEGER DEFAULT 95,
        auto_scale INTEGER DEFAULT 1,
        timeout_ms INTEGER DEFAULT 300000,
        config TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
      );

      CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY,
        framework_name TEXT NOT NULL,
        framework_version TEXT NOT NULL,
        task_id TEXT NOT NULL,
        run_number INTEGER NOT NULL,
        metrics TEXT NOT NULL,
        metadata TEXT NOT NULL,
        output_hash TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT NOT NULL,
        FOREIGN KEY (framework_name) REFERENCES frameworks(name),
        FOREIGN KEY (task_id) REFERENCES tasks(id)
      );

      CREATE INDEX IF NOT EXISTS idx_runs_framework ON runs(framework_name);
      CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(task_id);
      CREATE INDEX IF NOT EXISTS idx_runs_framework_task ON runs(framework_name, task_id);
    `);
  }

  saveFramework(config: FrameworkConfig): void {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO frameworks (name, version, tags, tier, config, updated_at)
      VALUES (?, ?, ?, ?, ?, datetime('now'))
    `);
    stmt.run(config.name, config.version, JSON.stringify(config.tags), config.tier, JSON.stringify(config));
  }

  getFramework(name: string): FrameworkConfig | null {
    const row = this.db.prepare('SELECT config FROM frameworks WHERE name = ?').get(name) as { config: string } | undefined;
    return row ? JSON.parse(row.config) as FrameworkConfig : null;
  }

  listFrameworks(): FrameworkConfig[] {
    const rows = this.db.prepare('SELECT config FROM frameworks ORDER BY name').all() as { config: string }[];
    return rows.map(r => JSON.parse(r.config) as FrameworkConfig);
  }

  saveTask(task: TaskDefinition): void {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO tasks (id, name, type, tags, difficulty, status, passing_threshold, excellence_threshold, auto_scale, timeout_ms, config)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(task.id, task.name, task.type, JSON.stringify(task.tags), task.difficulty, task.status, task.passingThreshold, task.excellenceThreshold, task.autoScale ? 1 : 0, task.timeoutMs, JSON.stringify(task));
  }

  getTask(id: string): TaskDefinition | null {
    const row = this.db.prepare('SELECT config FROM tasks WHERE id = ?').get(id) as { config: string } | undefined;
    return row ? JSON.parse(row.config) as TaskDefinition : null;
  }

  listTasks(status?: string): TaskDefinition[] {
    const query = status
      ? 'SELECT config FROM tasks WHERE status = ? ORDER BY id'
      : 'SELECT config FROM tasks ORDER BY id';
    const rows = (status
      ? this.db.prepare(query).all(status)
      : this.db.prepare(query).all()) as { config: string }[];
    return rows.map(r => JSON.parse(r.config) as TaskDefinition);
  }

  saveRun(result: RunResult): void {
    const stmt = this.db.prepare(`
      INSERT INTO runs (id, framework_name, framework_version, task_id, run_number, metrics, metadata, output_hash, started_at, completed_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      result.id,
      result.frameworkName,
      result.frameworkVersion,
      result.taskId,
      result.runNumber,
      JSON.stringify(result.metrics),
      JSON.stringify(result.metadata),
      result.outputHash,
      result.startedAt,
      result.completedAt,
    );
  }

  getRunsForFrameworkTask(frameworkName: string, taskId: string): RunResult[] {
    const rows = this.db.prepare(
      'SELECT id, framework_name, framework_version, task_id, run_number, metrics, metadata, output_hash, started_at, completed_at FROM runs WHERE framework_name = ? AND task_id = ? ORDER BY run_number'
    ).all(frameworkName, taskId) as Array<{
      id: string; framework_name: string; framework_version: string; task_id: string;
      run_number: number; metrics: string; metadata: string; output_hash: string;
      started_at: string; completed_at: string;
    }>;

    return rows.map(r => ({
      id: r.id,
      frameworkName: r.framework_name,
      frameworkVersion: r.framework_version,
      taskId: r.task_id,
      runNumber: r.run_number,
      metrics: JSON.parse(r.metrics) as MetricsProfile,
      metadata: JSON.parse(r.metadata),
      outputHash: r.output_hash,
      startedAt: r.started_at,
      completedAt: r.completed_at,
    }));
  }

  getLatestResults(): Array<{ frameworkName: string; taskId: string; runCount: number }> {
    const rows = this.db.prepare(`
      SELECT framework_name, task_id, COUNT(*) as run_count
      FROM runs
      GROUP BY framework_name, task_id
      ORDER BY framework_name, task_id
    `).all() as Array<{ framework_name: string; task_id: string; run_count: number }>;

    return rows.map(r => ({
      frameworkName: r.framework_name,
      taskId: r.task_id,
      runCount: r.run_count,
    }));
  }

  close(): void {
    this.db.close();
  }
}
