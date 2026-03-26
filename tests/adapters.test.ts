import { describe, it, expect } from 'vitest';
import path from 'node:path';
import { loadAdapter } from '../src/adapters/loader.js';

const ADAPTERS_DIR = path.resolve('adapters');

describe('loadAdapter', () => {
  it('loads claude-code adapter', () => {
    const adapter = loadAdapter(path.join(ADAPTERS_DIR, 'claude-code'));
    expect(adapter.name).toBe('claude-code');
    expect(adapter.tier).toBe('shell');
    expect(adapter.tags).toContain('coding-agent');
    expect(adapter.tags).toContain('model-locked:claude');
  });

  it('loads aider adapter', () => {
    const adapter = loadAdapter(path.join(ADAPTERS_DIR, 'aider'));
    expect(adapter.name).toBe('aider');
    expect(adapter.tags).toContain('model-agnostic');
    expect(adapter.tags).toContain('python');
  });

  it('loads langgraph adapter', () => {
    const adapter = loadAdapter(path.join(ADAPTERS_DIR, 'langgraph'));
    expect(adapter.name).toBe('langgraph');
    expect(adapter.tags).toContain('orchestration');
    expect(adapter.tags).toContain('library');
    expect(adapter.tags).toContain('multi-agent');
  });

  it('throws for missing adapter', () => {
    expect(() => loadAdapter('/nonexistent/path')).toThrow();
  });
});
