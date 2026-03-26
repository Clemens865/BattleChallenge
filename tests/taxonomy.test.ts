import { describe, it, expect } from 'vitest';
import {
  matchesFilter,
  filterFrameworks,
  DEFAULT_VIEWS,
  getViewByName,
  getAllTags,
  getInteractionModelTag,
  getAdapterTierForTag,
} from '../src/taxonomy/index.js';
import type { FrameworkConfig } from '../src/types/index.js';

const frameworks: FrameworkConfig[] = [
  { name: 'claude-code', version: '1.0', tags: ['coding-agent', 'orchestration', 'cli', 'model-locked:claude', 'multi-agent'], tier: 'shell', run: './adapter.sh' },
  { name: 'aider', version: '0.52', tags: ['coding-agent', 'cli', 'model-agnostic', 'python'], tier: 'shell', run: './adapter.sh' },
  { name: 'langgraph', version: '0.2', tags: ['orchestration', 'library', 'python', 'model-agnostic', 'stateful', 'multi-agent'], tier: 'shell', run: './adapter.sh' },
  { name: 'cursor', version: '0.48', tags: ['ide-integrated', 'coding-agent', 'editor-plugin', 'multi-model'], tier: 'recorded', run: '' },
];

describe('matchesFilter', () => {
  it('matches all filter', () => {
    expect(matchesFilter(['any', 'tag'], { type: 'all' })).toBe(true);
  });

  it('matches any filter', () => {
    expect(matchesFilter(['cli', 'python'], { type: 'any', tags: ['cli'] })).toBe(true);
    expect(matchesFilter(['cli', 'python'], { type: 'any', tags: ['library'] })).toBe(false);
  });

  it('matches every filter', () => {
    expect(matchesFilter(['cli', 'python'], { type: 'every', tags: ['cli', 'python'] })).toBe(true);
    expect(matchesFilter(['cli', 'python'], { type: 'every', tags: ['cli', 'library'] })).toBe(false);
  });

  it('matches and filter', () => {
    const filter = { type: 'and' as const, filters: [
      { type: 'any' as const, tags: ['orchestration'] },
      { type: 'any' as const, tags: ['library'] },
    ]};
    expect(matchesFilter(['orchestration', 'library'], filter)).toBe(true);
    expect(matchesFilter(['orchestration', 'cli'], filter)).toBe(false);
  });

  it('matches or filter', () => {
    const filter = { type: 'or' as const, filters: [
      { type: 'any' as const, tags: ['cli'] },
      { type: 'any' as const, tags: ['library'] },
    ]};
    expect(matchesFilter(['cli'], filter)).toBe(true);
    expect(matchesFilter(['library'], filter)).toBe(true);
    expect(matchesFilter(['ide-integrated'], filter)).toBe(false);
  });
});

describe('filterFrameworks', () => {
  it('all view returns all frameworks', () => {
    const view = getViewByName('all')!;
    const result = filterFrameworks(frameworks, view.tagFilter);
    expect(result.length).toBe(4);
  });

  it('orchestration view filters correctly', () => {
    const view = getViewByName('orchestration')!;
    const result = filterFrameworks(frameworks, view.tagFilter);
    expect(result.length).toBe(1);
    expect(result[0].name).toBe('langgraph');
  });

  it('coding-agents view filters correctly', () => {
    const view = getViewByName('coding-agents')!;
    const result = filterFrameworks(frameworks, view.tagFilter);
    expect(result.map(f => f.name)).toContain('claude-code');
    expect(result.map(f => f.name)).toContain('aider');
    expect(result.map(f => f.name)).not.toContain('cursor');
  });

  it('ide-tools view filters correctly', () => {
    const view = getViewByName('ide-tools')!;
    const result = filterFrameworks(frameworks, view.tagFilter);
    expect(result.length).toBe(1);
    expect(result[0].name).toBe('cursor');
  });
});

describe('getAllTags', () => {
  it('counts tags across all frameworks', () => {
    const tags = getAllTags(frameworks);
    expect(tags.get('coding-agent')).toBe(3);
    expect(tags.get('orchestration')).toBe(2);
    expect(tags.get('python')).toBe(2);
    expect(tags.get('ide-integrated')).toBe(1);
  });
});

describe('getInteractionModelTag', () => {
  it('returns the interaction model tag', () => {
    expect(getInteractionModelTag(['coding-agent', 'cli'])).toBe('cli');
    expect(getInteractionModelTag(['orchestration', 'library'])).toBe('library');
    expect(getInteractionModelTag(['ide-integrated'])).toBe('ide-integrated');
  });

  it('returns null if no interaction tag', () => {
    expect(getInteractionModelTag(['coding-agent', 'python'])).toBeNull();
  });
});

describe('getAdapterTierForTag', () => {
  it('maps tags to tiers', () => {
    expect(getAdapterTierForTag('library')).toBe('Tier 1: Library');
    expect(getAdapterTierForTag('cli')).toBe('Tier 2: CLI');
    expect(getAdapterTierForTag('api-hosted')).toBe('Tier 3: API');
    expect(getAdapterTierForTag('ide-integrated')).toBe('Tier 4: Recorded Run');
  });
});

describe('DEFAULT_VIEWS', () => {
  it('has 4 default views', () => {
    expect(DEFAULT_VIEWS.length).toBe(4);
  });

  it('includes all, orchestration, coding-agents, ide-tools', () => {
    const names = DEFAULT_VIEWS.map(v => v.name);
    expect(names).toContain('all');
    expect(names).toContain('orchestration');
    expect(names).toContain('coding-agents');
    expect(names).toContain('ide-tools');
  });
});
