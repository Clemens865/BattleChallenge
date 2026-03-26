import { describe, it, expect } from 'vitest';
import path from 'node:path';
import { loadTask, loadAllTasks } from '../src/tasks/loader.js';

const TASKS_DIR = path.resolve('tasks');

describe('loadTask', () => {
  it('loads task-001-validate-email', () => {
    const task = loadTask(path.join(TASKS_DIR, 'task-001-validate-email'));
    expect(task.id).toBe('task-001-validate-email');
    expect(task.type).toBe('coding');
    expect(task.difficulty).toBe('T1');
    expect(task.status).toBe('active');
    expect(task.passingThreshold).toBe(60);
  });

  it('loads task-002-rest-api-crud', () => {
    const task = loadTask(path.join(TASKS_DIR, 'task-002-rest-api-crud'));
    expect(task.id).toBe('task-002-rest-api-crud');
    expect(task.type).toBe('coding');
    expect(task.difficulty).toBe('T2');
    expect(task.timeoutMs).toBe(600000);
  });

  it('throws for missing task directory', () => {
    expect(() => loadTask('/nonexistent/path')).toThrow();
  });
});

describe('loadAllTasks', () => {
  it('loads all tasks from directory', () => {
    const tasks = loadAllTasks(TASKS_DIR);
    expect(tasks.length).toBeGreaterThanOrEqual(2);
    expect(tasks[0].id).toBe('task-001-validate-email');
  });

  it('returns empty array for nonexistent directory', () => {
    const tasks = loadAllTasks('/nonexistent/path');
    expect(tasks).toEqual([]);
  });
});
