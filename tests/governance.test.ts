import { describe, it, expect } from 'vitest';
import {
  validateBoardComposition,
  getDecisionRules,
  createDisputeTimeline,
} from '../src/governance/index.js';
import type { BoardMember } from '../src/governance/index.js';

describe('validateBoardComposition', () => {
  const validBoard: BoardMember[] = [
    { name: 'A', affiliation: 'Univ', role: 'chair', termStart: '2026-01', termEnd: '2028-01', coiDisclosure: 'None' },
    { name: 'B', affiliation: 'Corp', role: 'member', termStart: '2026-01', termEnd: '2028-01', coiDisclosure: 'None' },
    { name: 'C', affiliation: 'Ind', role: 'member', termStart: '2026-06', termEnd: '2028-06', coiDisclosure: 'None' },
    { name: 'D', affiliation: 'Univ', role: 'member', termStart: '2027-01', termEnd: '2029-01', coiDisclosure: 'None' },
    { name: 'E', affiliation: 'Corp', role: 'member', termStart: '2027-06', termEnd: '2029-06', coiDisclosure: 'None' },
  ];

  it('validates correct board', () => {
    const result = validateBoardComposition(validBoard);
    expect(result.valid).toBe(true);
    expect(result.issues).toEqual([]);
  });

  it('rejects too few members', () => {
    const result = validateBoardComposition(validBoard.slice(0, 3));
    expect(result.valid).toBe(false);
    expect(result.issues.some(i => i.includes('at least 5'))).toBe(true);
  });

  it('rejects no chair', () => {
    const noChair = validBoard.map(m => ({ ...m, role: 'member' as const }));
    const result = validateBoardComposition(noChair);
    expect(result.valid).toBe(false);
  });
});

describe('getDecisionRules', () => {
  it('returns rules for methodology-change', () => {
    const rules = getDecisionRules('methodology-change');
    expect(rules.commentPeriodDays).toBe(30);
  });

  it('returns rules for disqualification', () => {
    const rules = getDecisionRules('disqualification');
    expect(rules.majorityRequired).toBeCloseTo(2 / 3);
  });
});

describe('createDisputeTimeline', () => {
  it('creates 5-step timeline', () => {
    const timeline = createDisputeTimeline('2026-03-26T00:00:00Z');
    expect(timeline.length).toBe(5);
    expect(timeline[0].action).toContain('filed');
    expect(timeline[4].action).toContain('Appeal');
  });
});
