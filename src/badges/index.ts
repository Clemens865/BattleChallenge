/**
 * Badge generation for framework authors (Priya persona).
 * Generates SVG badges that auto-update each round.
 */

export type BadgeTier = 'verified' | 'top3' | 'efficiency-leader' | 'community-choice';

interface BadgeConfig {
  framework: string;
  tier: BadgeTier;
  label: string;
  value: string;
  color: string;
}

const BADGE_COLORS: Record<BadgeTier, string> = {
  'verified': '#4c1',
  'top3': '#dfb317',
  'efficiency-leader': '#007ec6',
  'community-choice': '#e05d44',
};

const BADGE_LABELS: Record<BadgeTier, string> = {
  'verified': 'BattleChallenge Verified',
  'top3': 'BattleChallenge Top 3',
  'efficiency-leader': 'BattleChallenge Efficiency',
  'community-choice': 'BattleChallenge Community',
};

export function generateBadgeSvg(config: BadgeConfig): string {
  const labelWidth = config.label.length * 6.5 + 10;
  const valueWidth = config.value.length * 6.5 + 10;
  const totalWidth = labelWidth + valueWidth;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${totalWidth}" height="20" role="img" aria-label="${config.label}: ${config.value}">
  <title>${config.label}: ${config.value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="${totalWidth}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="${labelWidth}" height="20" fill="#555"/>
    <rect x="${labelWidth}" width="${valueWidth}" height="20" fill="${config.color}"/>
    <rect width="${totalWidth}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="11">
    <text aria-hidden="true" x="${labelWidth / 2}" y="15" fill="#010101" fill-opacity=".3">${config.label}</text>
    <text x="${labelWidth / 2}" y="14">${config.label}</text>
    <text aria-hidden="true" x="${labelWidth + valueWidth / 2}" y="15" fill="#010101" fill-opacity=".3">${config.value}</text>
    <text x="${labelWidth + valueWidth / 2}" y="14">${config.value}</text>
  </g>
</svg>`;
}

export function createFrameworkBadge(
  framework: string,
  tier: BadgeTier,
  score?: number,
): string {
  const label = BADGE_LABELS[tier];
  let value: string;

  switch (tier) {
    case 'verified':
      value = score !== undefined ? `${score}/100` : 'Verified';
      break;
    case 'top3':
      value = score !== undefined ? `#${score}` : 'Top 3';
      break;
    case 'efficiency-leader':
      value = score !== undefined ? `$${score.toFixed(3)}/task` : 'Leader';
      break;
    case 'community-choice':
      value = score !== undefined ? `${score} repros` : 'Choice';
      break;
  }

  return generateBadgeSvg({
    framework,
    tier,
    label,
    value,
    color: BADGE_COLORS[tier],
  });
}

export function getBadgeUrl(framework: string): string {
  return `https://battlechallenge.dev/badge/${framework}/latest.svg`;
}

export function getBadgeMarkdown(framework: string): string {
  const url = getBadgeUrl(framework);
  const link = `https://battlechallenge.dev/framework/${framework}`;
  return `[![BattleChallenge](${url})](${link})`;
}
