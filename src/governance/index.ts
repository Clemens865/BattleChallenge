/**
 * Governance module — Advisory Board and decision-making.
 *
 * - 5-7 members: academics, independent engineers, enterprise practitioners
 * - No framework authors, employees of framework companies, or investors
 * - Published COI disclosures
 * - 2-year rotating terms, staggered
 */

export interface BoardMember {
  name: string;
  affiliation: string;
  role: 'chair' | 'member';
  termStart: string;
  termEnd: string;
  coiDisclosure: string;
}

export type DecisionType =
  | 'task-approval'
  | 'methodology-change'
  | 'disqualification'
  | 'category-definition'
  | 'scoring-weight-change';

export interface Decision {
  id: string;
  type: DecisionType;
  title: string;
  description: string;
  proposedBy: string;
  proposedAt: string;
  status: 'draft' | 'public-comment' | 'voting' | 'approved' | 'rejected';
  publicCommentDeadline?: string;
  votes?: { member: string; vote: 'approve' | 'reject' | 'abstain' }[];
  resolvedAt?: string;
}

export interface Dispute {
  id: string;
  framework: string;
  filedBy: string;
  filedAt: string;
  evidence: string;
  status: 'filed' | 'rerun-triggered' | 'under-review' | 'dismissed' | 'flagged' | 'disqualified';
  timeline: DisputeEvent[];
}

export interface DisputeEvent {
  date: string;
  action: string;
  details: string;
}

const DECISION_RULES: Record<DecisionType, { approver: string; commentPeriodDays: number; majorityRequired: number }> = {
  'task-approval': { approver: 'peer-reviewers + advisory board', commentPeriodDays: 0, majorityRequired: 0 },
  'methodology-change': { approver: 'advisory board', commentPeriodDays: 30, majorityRequired: 0.5 },
  'disqualification': { approver: 'advisory board', commentPeriodDays: 0, majorityRequired: 2 / 3 },
  'category-definition': { approver: 'advisory board + community RFC', commentPeriodDays: 30, majorityRequired: 0.5 },
  'scoring-weight-change': { approver: 'advisory board', commentPeriodDays: 60, majorityRequired: 0.5 },
};

export function getDecisionRules(type: DecisionType) {
  return DECISION_RULES[type];
}

export function validateBoardComposition(members: BoardMember[]): { valid: boolean; issues: string[] } {
  const issues: string[] = [];

  if (members.length < 5) issues.push(`Need at least 5 members (have ${members.length})`);
  if (members.length > 7) issues.push(`Maximum 7 members (have ${members.length})`);

  const chairs = members.filter(m => m.role === 'chair');
  if (chairs.length !== 1) issues.push(`Need exactly 1 chair (have ${chairs.length})`);

  // Check for staggered terms
  const endYears = members.map(m => new Date(m.termEnd).getFullYear());
  const uniqueEndYears = new Set(endYears);
  if (uniqueEndYears.size < 2) issues.push('Terms should be staggered across different years');

  return { valid: issues.length === 0, issues };
}

export function createDisputeTimeline(filedAt: string): DisputeEvent[] {
  const filed = new Date(filedAt);
  const day1 = new Date(filed.getTime() + 1 * 86400000);
  const day3 = new Date(filed.getTime() + 3 * 86400000);
  const day7 = new Date(filed.getTime() + 7 * 86400000);
  const day14 = new Date(filed.getTime() + 14 * 86400000);

  return [
    { date: filed.toISOString(), action: 'Dispute filed', details: 'GitHub issue with evidence' },
    { date: day1.toISOString(), action: 'Automated re-run triggered', details: 'System re-runs affected benchmark' },
    { date: day3.toISOString(), action: 'Advisory board preliminary review', details: 'Board reviews evidence and re-run results' },
    { date: day7.toISOString(), action: 'Decision published', details: 'Dismiss / flag / disqualify with full reasoning' },
    { date: day14.toISOString(), action: 'Appeal window closes', details: 'Final decision' },
  ];
}
