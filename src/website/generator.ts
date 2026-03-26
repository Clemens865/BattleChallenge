/**
 * Static website generator for battlechallenge.dev
 *
 * Generates HTML pages from benchmark results:
 * - / (Home) — Hero + quick leaderboard preview
 * - /leaderboard — Full interactive leaderboard
 * - /compare/:fw1/:fw2 — Side-by-side comparison
 * - /framework/:name — Framework profile
 * - /methodology — Full scoring methodology
 */

import fs from 'node:fs';
import path from 'node:path';
import type { LeaderboardEntry, FrameworkConfig, MetricsProfile } from '../types/index.js';
import { createFrameworkBadge } from '../badges/index.js';

export interface SiteConfig {
  outputDir: string;
  baseUrl: string;
  title: string;
}

const DEFAULT_SITE_CONFIG: SiteConfig = {
  outputDir: './site',
  baseUrl: 'https://battlechallenge.dev',
  title: 'BattleChallenge — Agentic AI Framework Benchmarks',
};

export function generateSite(
  entries: LeaderboardEntry[],
  config: Partial<SiteConfig> = {},
): void {
  const siteConfig = { ...DEFAULT_SITE_CONFIG, ...config };
  const { outputDir } = siteConfig;

  fs.mkdirSync(path.join(outputDir, 'framework'), { recursive: true });
  fs.mkdirSync(path.join(outputDir, 'compare'), { recursive: true });
  fs.mkdirSync(path.join(outputDir, 'badge'), { recursive: true });

  // Generate pages
  fs.writeFileSync(path.join(outputDir, 'index.html'), generateHomePage(entries, siteConfig));
  fs.writeFileSync(path.join(outputDir, 'leaderboard.html'), generateLeaderboardPage(entries, siteConfig));
  fs.writeFileSync(path.join(outputDir, 'methodology.html'), generateMethodologyPage(siteConfig));

  // Framework profiles
  const frameworks = [...new Set(entries.map(e => e.framework.name))];
  for (const fw of frameworks) {
    const fwEntries = entries.filter(e => e.framework.name === fw);
    const dir = path.join(outputDir, 'framework', fw);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'index.html'), generateFrameworkPage(fwEntries, siteConfig));

    // Badges
    const badgeSvg = createFrameworkBadge(fw, 'verified', fwEntries[0]?.profile.correctness.score);
    fs.writeFileSync(path.join(outputDir, 'badge', `${fw}.svg`), badgeSvg);
  }

  // Compare pages (SEO: "langgraph vs crewai")
  for (let i = 0; i < frameworks.length; i++) {
    for (let j = i + 1; j < frameworks.length; j++) {
      const fw1 = frameworks[i];
      const fw2 = frameworks[j];
      const dir = path.join(outputDir, 'compare', fw1, fw2);
      fs.mkdirSync(dir, { recursive: true });
      const e1 = entries.filter(e => e.framework.name === fw1);
      const e2 = entries.filter(e => e.framework.name === fw2);
      fs.writeFileSync(path.join(dir, 'index.html'), generateComparePage(fw1, fw2, e1, e2, siteConfig));
    }
  }

  // API data files
  fs.mkdirSync(path.join(outputDir, 'api', 'v1'), { recursive: true });
  fs.writeFileSync(
    path.join(outputDir, 'api', 'v1', 'results.json'),
    JSON.stringify({ results: entries.map(e => ({ framework: e.framework.name, profile: e.profile, track: e.track })) }, null, 2),
  );
}

function htmlShell(title: string, content: string, config: SiteConfig): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} | ${config.title}</title>
  <meta name="description" content="Compare agentic AI frameworks with standardized benchmarks. Open-source, transparent, reproducible.">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: #e0e0e0; line-height: 1.6; }
    .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
    nav { padding: 16px 0; border-bottom: 1px solid #222; }
    nav a { color: #9cf; text-decoration: none; margin-right: 24px; }
    nav a:hover { text-decoration: underline; }
    h1 { font-size: 2.5rem; margin: 48px 0 16px; }
    h2 { font-size: 1.5rem; margin: 32px 0 16px; color: #9cf; }
    .hero { text-align: center; padding: 80px 0; }
    .hero h1 { font-size: 3rem; background: linear-gradient(135deg, #9cf, #f9c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero p { font-size: 1.25rem; color: #888; max-width: 600px; margin: 16px auto; }
    table { width: 100%; border-collapse: collapse; margin: 24px 0; }
    th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #222; }
    th { color: #9cf; font-weight: 600; }
    tr:hover { background: #111; }
    .bar { display: inline-block; height: 16px; background: #4c1; border-radius: 2px; }
    .metric { font-family: monospace; }
    footer { padding: 48px 0; text-align: center; color: #666; border-top: 1px solid #222; margin-top: 64px; }
    .badge { display: inline-block; margin: 8px; }
    .cta { display: inline-block; padding: 12px 32px; background: #9cf; color: #000; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 24px; }
    .cta:hover { background: #7af; }
    @media (max-width: 768px) { .hero h1 { font-size: 2rem; } table { font-size: 0.9rem; } }
  </style>
</head>
<body>
  <nav class="container">
    <a href="/"><strong>BattleChallenge</strong></a>
    <a href="/leaderboard.html">Leaderboard</a>
    <a href="/methodology.html">Methodology</a>
  </nav>
  <main class="container">
    ${content}
  </main>
  <footer class="container">
    <p>BattleChallenge is open source. <a href="https://github.com/battlechallenge/battlechallenge">GitHub</a></p>
    <p>Results reflect framework + model + adapter stacks.</p>
  </footer>
</body>
</html>`;
}

function generateHomePage(entries: LeaderboardEntry[], config: SiteConfig): string {
  const top5 = entries.slice(0, 5);
  const tableRows = top5.map(e => `
    <tr>
      <td><a href="/framework/${e.framework.name}/">${e.framework.name}</a></td>
      <td class="metric">${e.profile.correctness.score}/100</td>
      <td class="metric">$${e.profile.cost.totalCostUsd.toFixed(3)}</td>
      <td class="metric">${(e.profile.speed.totalMs / 1000).toFixed(1)}s</td>
      <td>${e.framework.tags.slice(0, 3).join(', ')}</td>
    </tr>`).join('');

  return htmlShell('Home', `
    <div class="hero">
      <h1>BattleChallenge</h1>
      <p>The open-source benchmark that compares agentic AI frameworks head-to-head on standardized tasks.</p>
      <p style="color:#666">Give every framework the same tasks. Measure everything. Publish everything.</p>
      <a href="/leaderboard.html" class="cta">View Leaderboard</a>
    </div>
    <h2>Latest Results</h2>
    <table>
      <thead><tr><th>Framework</th><th>Correctness</th><th>Cost/Task</th><th>Speed</th><th>Tags</th></tr></thead>
      <tbody>${tableRows}</tbody>
    </table>
  `, config);
}

function generateLeaderboardPage(entries: LeaderboardEntry[], config: SiteConfig): string {
  const tableRows = entries.map(e => {
    const relPct = e.profile.reliability.runsAttempted > 0
      ? Math.round((e.profile.reliability.runsPassed / e.profile.reliability.runsAttempted) * 100)
      : 0;
    return `
    <tr>
      <td><a href="/framework/${e.framework.name}/">${e.framework.name}</a></td>
      <td class="metric"><div class="bar" style="width:${e.profile.correctness.score}px"></div> ${e.profile.correctness.score}</td>
      <td class="metric">$${e.profile.cost.totalCostUsd.toFixed(3)}</td>
      <td class="metric">${(e.profile.speed.totalMs / 1000).toFixed(1)}s</td>
      <td class="metric">${relPct}%</td>
      <td class="metric">${e.profile.quality.readabilityHeuristic}</td>
      <td>${e.framework.tags.join(', ')}</td>
    </tr>`;
  }).join('');

  return htmlShell('Leaderboard', `
    <h1>Leaderboard</h1>
    <p style="color:#888">Multi-dimensional profiles. No composite scores. Compare what matters to you.</p>
    <table>
      <thead><tr><th>Framework</th><th>Correctness</th><th>Cost/Task</th><th>Speed</th><th>Reliability</th><th>Quality</th><th>Tags</th></tr></thead>
      <tbody>${tableRows}</tbody>
    </table>
  `, config);
}

function generateFrameworkPage(entries: LeaderboardEntry[], config: SiteConfig): string {
  if (entries.length === 0) return htmlShell('Unknown', '<p>Framework not found.</p>', config);

  const fw = entries[0].framework;
  const profile = entries[0].profile;

  return htmlShell(fw.name, `
    <h1>${fw.name} <span style="color:#666">v${fw.version}</span></h1>
    <p>Tags: ${fw.tags.join(', ')}</p>
    <h2>Profile</h2>
    <table>
      <tr><td>Correctness</td><td class="metric">${profile.correctness.score}/100</td></tr>
      <tr><td>Cost per Task</td><td class="metric">$${profile.cost.totalCostUsd.toFixed(3)}</td></tr>
      <tr><td>Speed</td><td class="metric">${(profile.speed.totalMs / 1000).toFixed(1)}s</td></tr>
      <tr><td>Reliability</td><td class="metric">${profile.reliability.runsPassed}/${profile.reliability.runsAttempted} passed</td></tr>
      <tr><td>Quality</td><td class="metric">${profile.quality.readabilityHeuristic}/100</td></tr>
    </table>
  `, config);
}

function generateComparePage(fw1: string, fw2: string, e1: LeaderboardEntry[], e2: LeaderboardEntry[], config: SiteConfig): string {
  const p1 = e1[0]?.profile;
  const p2 = e2[0]?.profile;

  if (!p1 || !p2) return htmlShell(`${fw1} vs ${fw2}`, '<p>Insufficient data.</p>', config);

  return htmlShell(`${fw1} vs ${fw2}`, `
    <h1>${fw1} vs ${fw2}</h1>
    <table>
      <thead><tr><th>Metric</th><th>${fw1}</th><th>${fw2}</th></tr></thead>
      <tbody>
        <tr><td>Correctness</td><td class="metric">${p1.correctness.score}</td><td class="metric">${p2.correctness.score}</td></tr>
        <tr><td>Cost/Task</td><td class="metric">$${p1.cost.totalCostUsd.toFixed(3)}</td><td class="metric">$${p2.cost.totalCostUsd.toFixed(3)}</td></tr>
        <tr><td>Speed</td><td class="metric">${(p1.speed.totalMs / 1000).toFixed(1)}s</td><td class="metric">${(p2.speed.totalMs / 1000).toFixed(1)}s</td></tr>
        <tr><td>Reliability</td><td class="metric">${p1.reliability.runsPassed}/${p1.reliability.runsAttempted}</td><td class="metric">${p2.reliability.runsPassed}/${p2.reliability.runsAttempted}</td></tr>
        <tr><td>Quality</td><td class="metric">${p1.quality.readabilityHeuristic}</td><td class="metric">${p2.quality.readabilityHeuristic}</td></tr>
      </tbody>
    </table>
  `, config);
}

function generateMethodologyPage(config: SiteConfig): string {
  return htmlShell('Methodology', `
    <h1>Methodology</h1>
    <h2>What We Measure</h2>
    <p>BattleChallenge measures the <strong>framework + model + adapter</strong> combination, not "the framework" in isolation.</p>
    <h2>Five Meta-Metrics</h2>
    <table>
      <tr><td><strong>Correctness</strong></td><td>Does the outcome work? Automated tests verify results.</td></tr>
      <tr><td><strong>Cost</strong></td><td>Token proxy tracks API spend in USD.</td></tr>
      <tr><td><strong>Speed</strong></td><td>Wall-clock time from task start to completion.</td></tr>
      <tr><td><strong>Reliability</strong></td><td>% of runs that pass across N repetitions.</td></tr>
      <tr><td><strong>Autonomy</strong></td><td>0 = fully autonomous, 1 = needed hints, 2 = needed intervention.</td></tr>
    </table>
    <h2>Statistical Rigor</h2>
    <ul style="padding-left:24px;color:#aaa">
      <li>Minimum 5 runs per task per framework</li>
      <li>Median + IQR reported (not mean)</li>
      <li>High variance flagged when IQR > 20% of median</li>
      <li>Rankings only when confidence intervals don't overlap</li>
      <li>Per-run raw data published</li>
    </ul>
    <h2>Two Leaderboard Views</h2>
    <p><strong>Best Performance</strong>: Each framework uses its optimal model configuration.</p>
    <p><strong>Controlled Model</strong>: All model-agnostic frameworks use the same model for fair comparison.</p>
    <h2>Honest Limitations</h2>
    <ul style="padding-left:24px;color:#aaa">
      <li>We benchmark framework+model+adapter, not "the framework" alone.</li>
      <li>IDE tools are harder to benchmark fairly (Recorded Run format).</li>
      <li>Production performance may differ.</li>
      <li>Agents are non-deterministic — we report variance honestly.</li>
    </ul>
  `, config);
}
