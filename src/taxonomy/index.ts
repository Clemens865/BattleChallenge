/**
 * Tag-based framework taxonomy.
 * Replaces rigid categories with flexible, evolving tags.
 * Frameworks declare tags; leaderboard filters by tags.
 */

import type { FrameworkConfig } from '../types/index.js';

export interface LeaderboardView {
  name: string;
  label: string;
  description: string;
  tagFilter: TagFilter;
}

export type TagFilter =
  | { type: 'all' }
  | { type: 'any'; tags: string[] }
  | { type: 'every'; tags: string[] }
  | { type: 'and'; filters: TagFilter[] }
  | { type: 'or'; filters: TagFilter[] };

export const DEFAULT_VIEWS: LeaderboardView[] = [
  {
    name: 'all',
    label: 'All Frameworks',
    description: 'Show me everything',
    tagFilter: { type: 'all' },
  },
  {
    name: 'orchestration',
    label: 'Orchestration',
    description: 'Which orchestration framework?',
    tagFilter: { type: 'and', filters: [
      { type: 'any', tags: ['orchestration'] },
      { type: 'any', tags: ['library'] },
    ]},
  },
  {
    name: 'coding-agents',
    label: 'Coding Agents',
    description: 'Which coding agent?',
    tagFilter: { type: 'and', filters: [
      { type: 'any', tags: ['coding-agent'] },
      { type: 'any', tags: ['cli', 'library'] },
    ]},
  },
  {
    name: 'ide-tools',
    label: 'IDE Tools',
    description: 'Which IDE AI tool?',
    tagFilter: { type: 'any', tags: ['ide-integrated'] },
  },
];

export function matchesFilter(tags: string[], filter: TagFilter): boolean {
  switch (filter.type) {
    case 'all':
      return true;
    case 'any':
      return filter.tags.some(t => tags.includes(t));
    case 'every':
      return filter.tags.every(t => tags.includes(t));
    case 'and':
      return filter.filters.every(f => matchesFilter(tags, f));
    case 'or':
      return filter.filters.some(f => matchesFilter(tags, f));
  }
}

export function filterFrameworks(
  frameworks: FrameworkConfig[],
  filter: TagFilter,
): FrameworkConfig[] {
  return frameworks.filter(fw => matchesFilter(fw.tags, filter));
}

export function getViewByName(name: string): LeaderboardView | undefined {
  return DEFAULT_VIEWS.find(v => v.name === name);
}

export function getAllTags(frameworks: FrameworkConfig[]): Map<string, number> {
  const tagCounts = new Map<string, number>();
  for (const fw of frameworks) {
    for (const tag of fw.tags) {
      tagCounts.set(tag, (tagCounts.get(tag) || 0) + 1);
    }
  }
  return tagCounts;
}

export function getInteractionModelTag(tags: string[]): string | null {
  const interactionTags = ['library', 'cli', 'api-hosted', 'ide-integrated', 'internal-only'];
  return tags.find(t => interactionTags.includes(t)) || null;
}

export function getAdapterTierForTag(tag: string): string {
  switch (tag) {
    case 'library': return 'Tier 1: Library';
    case 'cli': return 'Tier 2: CLI';
    case 'api-hosted': return 'Tier 3: API';
    case 'ide-integrated': return 'Tier 4: Recorded Run';
    case 'internal-only': return 'Self-benchmark';
    default: return 'Unknown';
  }
}

// Well-known tags for validation/suggestions
export const WELL_KNOWN_TAGS = [
  'coding-agent', 'orchestration', 'cli', 'library',
  'api-hosted', 'ide-integrated', 'internal-only',
  'model-agnostic', 'model-locked:claude', 'model-locked:gpt', 'model-locked:gemini',
  'multi-agent', 'stateful', 'python', 'typescript',
  'editor-plugin', 'multi-model',
] as const;
