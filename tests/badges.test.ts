import { describe, it, expect } from 'vitest';
import { generateBadgeSvg, createFrameworkBadge, getBadgeMarkdown } from '../src/badges/index.js';

describe('generateBadgeSvg', () => {
  it('generates valid SVG', () => {
    const svg = generateBadgeSvg({
      framework: 'langgraph',
      tier: 'verified',
      label: 'BattleChallenge',
      value: '82/100',
      color: '#4c1',
    });
    expect(svg).toContain('<svg');
    expect(svg).toContain('BattleChallenge');
    expect(svg).toContain('82/100');
    expect(svg).toContain('#4c1');
  });
});

describe('createFrameworkBadge', () => {
  it('creates verified badge with score', () => {
    const svg = createFrameworkBadge('langgraph', 'verified', 82);
    expect(svg).toContain('82/100');
    expect(svg).toContain('Verified');
  });

  it('creates top3 badge', () => {
    const svg = createFrameworkBadge('aider', 'top3', 1);
    expect(svg).toContain('#1');
  });

  it('creates efficiency leader badge', () => {
    const svg = createFrameworkBadge('aider', 'efficiency-leader', 0.03);
    expect(svg).toContain('$0.030/task');
  });

  it('creates community choice badge', () => {
    const svg = createFrameworkBadge('crewai', 'community-choice', 15);
    expect(svg).toContain('15 repros');
  });
});

describe('getBadgeMarkdown', () => {
  it('returns valid markdown image link', () => {
    const md = getBadgeMarkdown('langgraph');
    expect(md).toContain('[![BattleChallenge]');
    expect(md).toContain('battlechallenge.dev/badge/langgraph');
    expect(md).toContain('battlechallenge.dev/framework/langgraph');
  });
});
