/**
 * "Find My Framework" quiz logic (Maya persona).
 * 5 questions -> personalized recommendation backed by benchmark data.
 */

import type { MetricsProfile, FrameworkConfig } from '../types/index.js';

export interface QuizAnswers {
  projectType: 'web-app' | 'api' | 'data-pipeline' | 'multi-agent' | 'other';
  priority: 'cost' | 'speed' | 'correctness' | 'reliability';
  modelPreference: 'claude' | 'gpt' | 'gemini' | 'open-source' | 'no-preference';
  language: 'python' | 'typescript' | 'both' | 'other';
  teamSize: 'solo' | 'small-team' | 'enterprise';
}

export interface QuizResult {
  recommended: string;
  score: number;
  reasoning: string[];
  alternatives: Array<{ framework: string; score: number; note: string }>;
}

interface ScoredFramework {
  name: string;
  score: number;
  reasons: string[];
}

export function computeRecommendation(
  answers: QuizAnswers,
  frameworks: Array<{ config: FrameworkConfig; profile: MetricsProfile }>,
): QuizResult {
  const scored: ScoredFramework[] = frameworks.map(fw => {
    let score = 50; // baseline
    const reasons: string[] = [];

    // Priority weighting
    switch (answers.priority) {
      case 'cost':
        score += (1 - Math.min(fw.profile.cost.totalCostUsd, 1)) * 30;
        if (fw.profile.cost.totalCostUsd < 0.05) reasons.push('Very low cost per task');
        break;
      case 'speed':
        score += Math.max(0, 30 - fw.profile.speed.totalMs / 1000);
        if (fw.profile.speed.totalMs < 10000) reasons.push('Fast execution');
        break;
      case 'correctness':
        score += fw.profile.correctness.score * 0.3;
        if (fw.profile.correctness.score > 80) reasons.push('High correctness score');
        break;
      case 'reliability':
        if (fw.profile.reliability.runsAttempted > 0) {
          const relPct = fw.profile.reliability.runsPassed / fw.profile.reliability.runsAttempted;
          score += relPct * 30;
          if (relPct > 0.8) reasons.push('Highly reliable');
        }
        break;
    }

    // Model preference matching
    if (answers.modelPreference !== 'no-preference') {
      const modelTag = `model-locked:${answers.modelPreference}`;
      if (fw.config.tags.includes(modelTag)) {
        score += 10;
        reasons.push(`Uses preferred model (${answers.modelPreference})`);
      }
      if (fw.config.tags.includes('model-agnostic')) {
        score += 5;
        reasons.push('Model-agnostic (can use your preferred model)');
      }
    }

    // Language matching
    if (answers.language === 'python' && fw.config.tags.includes('python')) {
      score += 10;
      reasons.push('Python support');
    }
    if (answers.language === 'typescript' && fw.config.tags.includes('typescript')) {
      score += 10;
      reasons.push('TypeScript support');
    }

    // Team size considerations
    if (answers.teamSize === 'enterprise') {
      if (fw.config.tags.includes('orchestration')) {
        score += 5;
        reasons.push('Orchestration capabilities for team workflows');
      }
    }
    if (answers.teamSize === 'solo') {
      if (fw.config.tags.includes('cli') || fw.config.tags.includes('coding-agent')) {
        score += 5;
        reasons.push('Great for solo developers');
      }
    }

    // Project type bonuses
    if (answers.projectType === 'multi-agent' && fw.config.tags.includes('multi-agent')) {
      score += 10;
      reasons.push('Multi-agent support');
    }
    if (answers.projectType === 'api' && fw.config.tags.includes('coding-agent')) {
      score += 5;
      reasons.push('Strong at code generation');
    }

    return { name: fw.config.name, score: Math.min(score, 100), reasons };
  });

  scored.sort((a, b) => b.score - a.score);

  const best = scored[0];
  const alternatives = scored.slice(1, 4).map(s => ({
    framework: s.name,
    score: Math.round(s.score),
    note: s.reasons[0] || 'Good alternative',
  }));

  return {
    recommended: best.name,
    score: Math.round(best.score),
    reasoning: best.reasons,
    alternatives,
  };
}
