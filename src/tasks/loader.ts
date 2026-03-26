/**
 * Task loader — reads task.yaml definitions and validates task structure.
 */

import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';
import type { TaskDefinition, TaskType, DifficultyTier, TaskStatus } from '../types/index.js';

const VALID_TYPES: TaskType[] = ['prd', 'coding', 'multi-step', 'tool-use', 'rag', 'multi-agent'];
const VALID_DIFFICULTIES: DifficultyTier[] = ['T1', 'T2', 'T3', 'T4'];
const VALID_STATUSES: TaskStatus[] = ['active', 'secret', 'retired'];

export function loadTask(taskDir: string): TaskDefinition {
  const configPath = path.join(taskDir, 'task.yaml');
  if (!fs.existsSync(configPath)) {
    throw new Error(`Task config not found: ${configPath}`);
  }

  const raw = fs.readFileSync(configPath, 'utf-8');
  const parsed = YAML.parse(raw) as Record<string, unknown>;

  return validateTask(parsed, taskDir);
}

function validateTask(raw: Record<string, unknown>, taskDir: string): TaskDefinition {
  if (!raw.id || typeof raw.id !== 'string') {
    throw new Error('Task must have an "id" field');
  }
  if (!raw.name || typeof raw.name !== 'string') {
    throw new Error('Task must have a "name" field');
  }
  if (!raw.type || !VALID_TYPES.includes(raw.type as TaskType)) {
    throw new Error(`Task type must be one of: ${VALID_TYPES.join(', ')}`);
  }

  const difficulty = raw.difficulty as Record<string, unknown> | string;
  let tier: DifficultyTier;
  let passingThreshold = 60;
  let excellenceThreshold = 95;
  let autoScale = true;

  if (typeof difficulty === 'string') {
    if (!VALID_DIFFICULTIES.includes(difficulty as DifficultyTier)) {
      throw new Error(`Task difficulty must be one of: ${VALID_DIFFICULTIES.join(', ')}`);
    }
    tier = difficulty as DifficultyTier;
  } else if (difficulty && typeof difficulty === 'object') {
    tier = (difficulty.tier as DifficultyTier) || 'T1';
    passingThreshold = (difficulty.passing_threshold as number) ?? 60;
    excellenceThreshold = (difficulty.excellence_threshold as number) ?? 95;
    autoScale = (difficulty.auto_scale as boolean) ?? true;
  } else {
    tier = 'T1';
  }

  const requirementsPath = (raw.requirements_path as string) || 'requirements.md';
  const verifyPath = (raw.verify_path as string) || 'verify';

  if (!fs.existsSync(path.join(taskDir, requirementsPath))) {
    throw new Error(`Requirements file not found: ${path.join(taskDir, requirementsPath)}`);
  }

  const tags = Array.isArray(raw.tags) ? raw.tags.map(String) : [];
  const status = VALID_STATUSES.includes(raw.status as TaskStatus) ? (raw.status as TaskStatus) : 'active';
  const timeoutMs = typeof raw.timeout_ms === 'number' ? raw.timeout_ms : getDefaultTimeout(tier);

  return {
    id: raw.id as string,
    name: raw.name as string,
    type: raw.type as TaskType,
    tags,
    difficulty: tier,
    status,
    passingThreshold,
    excellenceThreshold,
    autoScale,
    timeoutMs,
    tokenBudget: typeof raw.token_budget === 'number' ? raw.token_budget : undefined,
    requirementsPath,
    verifyPath,
    referencePath: typeof raw.reference_path === 'string' ? raw.reference_path : undefined,
  };
}

function getDefaultTimeout(tier: DifficultyTier): number {
  switch (tier) {
    case 'T1': return 120_000;
    case 'T2': return 600_000;
    case 'T3': return 1_800_000;
    case 'T4': return 3_600_000;
  }
}

export function loadAllTasks(tasksDir: string): TaskDefinition[] {
  if (!fs.existsSync(tasksDir)) return [];

  const entries = fs.readdirSync(tasksDir, { withFileTypes: true });
  const tasks: TaskDefinition[] = [];

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const taskDir = path.join(tasksDir, entry.name);
    if (!fs.existsSync(path.join(taskDir, 'task.yaml'))) continue;

    try {
      tasks.push(loadTask(taskDir));
    } catch (err) {
      console.error(`Warning: Failed to load task ${entry.name}: ${(err as Error).message}`);
    }
  }

  return tasks.sort((a, b) => a.id.localeCompare(b.id));
}

export function scaffoldTask(
  id: string,
  type: TaskType,
  tier: DifficultyTier,
  outputDir: string,
): string {
  const dir = path.join(outputDir, id);
  fs.mkdirSync(path.join(dir, 'verify'), { recursive: true });
  fs.mkdirSync(path.join(dir, 'reference', 'solution'), { recursive: true });

  const yaml = `id: "${id}"
name: "${id.replace(/[-_]/g, ' ')}"
type: ${type}
tags: []
difficulty:
  tier: ${tier}
  passing_threshold: 60
  excellence_threshold: 95
  auto_scale: true
status: active
timeout_ms: ${getDefaultTimeout(tier)}
requirements_path: requirements.md
verify_path: verify
reference_path: reference/solution
`;
  fs.writeFileSync(path.join(dir, 'task.yaml'), yaml);

  fs.writeFileSync(path.join(dir, 'requirements.md'), `# ${id}\n\n## Requirements\n\nTODO: Describe what the framework should build.\n\n## Acceptance Criteria\n\nTODO: Define what success looks like.\n`);

  fs.writeFileSync(path.join(dir, 'verify', 'test_outcomes.py'), `"""Outcome-based tests for ${id}."""\nimport pytest\n\n\ndef test_placeholder():\n    """TODO: Replace with actual outcome tests."""\n    assert True\n`);

  return dir;
}
