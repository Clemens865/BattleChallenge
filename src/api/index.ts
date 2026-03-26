/**
 * BattleChallenge REST API
 *
 * Endpoints:
 *   GET  /v1/results           — Latest round results
 *   GET  /v1/frameworks        — All frameworks
 *   GET  /v1/frameworks/:name  — Single framework profile
 *   GET  /v1/tasks             — All public tasks
 *   GET  /v1/tasks/:id         — Single task detail
 *   GET  /v1/compare/:fw1/:fw2 — Head-to-head comparison
 *   GET  /v1/export/:round     — Full round data
 */

import http from 'node:http';
import { BattleChallengeDB } from '../db/index.js';
import { aggregateResults } from '../scorer/index.js';

interface RouteHandler {
  (params: Record<string, string>, query: Record<string, string>, db: BattleChallengeDB): { status: number; body: unknown };
}

const routes: Map<string, RouteHandler> = new Map();

routes.set('GET /v1/results', (_params, query, db) => {
  const entries = db.getLatestResults();
  const results: Record<string, unknown>[] = [];

  for (const entry of entries) {
    const runs = db.getRunsForFrameworkTask(entry.frameworkName, entry.taskId);
    const agg = aggregateResults(runs);
    if (agg) {
      results.push({
        framework: entry.frameworkName,
        task: entry.taskId,
        runs: entry.runCount,
        median: agg.median,
        highVariance: agg.highVariance,
      });
    }
  }

  return { status: 200, body: { results, count: results.length } };
});

routes.set('GET /v1/frameworks', (_params, _query, db) => {
  const frameworks = db.listFrameworks();
  return { status: 200, body: { frameworks, count: frameworks.length } };
});

routes.set('GET /v1/frameworks/:name', (params, _query, db) => {
  const framework = db.getFramework(params.name);
  if (!framework) {
    return { status: 404, body: { error: 'Framework not found' } };
  }

  const entries = db.getLatestResults().filter(e => e.frameworkName === params.name);
  const taskResults: Record<string, unknown> = {};

  for (const entry of entries) {
    const runs = db.getRunsForFrameworkTask(entry.frameworkName, entry.taskId);
    const agg = aggregateResults(runs);
    if (agg) {
      taskResults[entry.taskId] = { median: agg.median, highVariance: agg.highVariance, runs: agg.runs.length };
    }
  }

  return { status: 200, body: { framework, results: taskResults } };
});

routes.set('GET /v1/tasks', (_params, query, db) => {
  const status = query.status || 'active';
  const tasks = db.listTasks(status);
  return { status: 200, body: { tasks, count: tasks.length } };
});

routes.set('GET /v1/tasks/:id', (params, _query, db) => {
  const task = db.getTask(params.id);
  if (!task) {
    return { status: 404, body: { error: 'Task not found' } };
  }
  return { status: 200, body: { task } };
});

routes.set('GET /v1/compare/:fw1/:fw2', (params, _query, db) => {
  const entries = db.getLatestResults();
  const fw1Tasks = entries.filter(e => e.frameworkName === params.fw1).map(e => e.taskId);
  const fw2Tasks = entries.filter(e => e.frameworkName === params.fw2).map(e => e.taskId);
  const commonTasks = fw1Tasks.filter(t => fw2Tasks.includes(t));

  const comparison: Record<string, unknown> = {};
  for (const taskId of commonTasks) {
    const runs1 = db.getRunsForFrameworkTask(params.fw1, taskId);
    const runs2 = db.getRunsForFrameworkTask(params.fw2, taskId);
    const agg1 = aggregateResults(runs1);
    const agg2 = aggregateResults(runs2);
    comparison[taskId] = {
      [params.fw1]: agg1 ? { median: agg1.median, highVariance: agg1.highVariance } : null,
      [params.fw2]: agg2 ? { median: agg2.median, highVariance: agg2.highVariance } : null,
    };
  }

  return {
    status: 200,
    body: {
      frameworks: [params.fw1, params.fw2],
      commonTasks: commonTasks.length,
      comparison,
    },
  };
});

function matchRoute(method: string, path: string): { handler: RouteHandler; params: Record<string, string> } | null {
  for (const [pattern, handler] of routes) {
    const [routeMethod, routePath] = pattern.split(' ');
    if (method !== routeMethod) continue;

    const routeParts = routePath.split('/');
    const pathParts = path.split('/');

    if (routeParts.length !== pathParts.length) continue;

    const params: Record<string, string> = {};
    let match = true;

    for (let i = 0; i < routeParts.length; i++) {
      if (routeParts[i].startsWith(':')) {
        params[routeParts[i].slice(1)] = pathParts[i];
      } else if (routeParts[i] !== pathParts[i]) {
        match = false;
        break;
      }
    }

    if (match) return { handler, params };
  }
  return null;
}

function parseQuery(url: string): Record<string, string> {
  const query: Record<string, string> = {};
  const idx = url.indexOf('?');
  if (idx === -1) return query;
  const search = url.slice(idx + 1);
  for (const pair of search.split('&')) {
    const [key, value] = pair.split('=');
    if (key) query[decodeURIComponent(key)] = decodeURIComponent(value || '');
  }
  return query;
}

export function createApiServer(port: number = 3001, dbPath?: string): http.Server {
  const db = new BattleChallengeDB(dbPath);

  const server = http.createServer((req, res) => {
    const url = req.url || '/';
    const pathname = url.split('?')[0];
    const method = req.method || 'GET';
    const query = parseQuery(url);

    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Content-Type', 'application/json');

    if (method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    const route = matchRoute(method, pathname);
    if (!route) {
      res.writeHead(404);
      res.end(JSON.stringify({ error: 'Not found' }));
      return;
    }

    try {
      const result = route.handler(route.params, query, db);
      res.writeHead(result.status);
      res.end(JSON.stringify(result.body));
    } catch (err) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: 'Internal server error' }));
    }
  });

  server.on('close', () => db.close());

  return server;
}

export function startApiServer(port: number = 3001, dbPath?: string): http.Server {
  const server = createApiServer(port, dbPath);
  server.listen(port, () => {
    console.log(`BattleChallenge API running on http://localhost:${port}`);
  });
  return server;
}
