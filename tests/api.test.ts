import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import http from 'node:http';
import { createApiServer } from '../src/api/index.js';
import { BattleChallengeDB } from '../src/db/index.js';
import fs from 'node:fs';
import path from 'node:path';

const TEST_DB = path.join(import.meta.dirname, '.test-api.db');
let server: http.Server;
let port: number;

function fetch(urlPath: string): Promise<{ status: number; body: unknown }> {
  return new Promise((resolve, reject) => {
    http.get(`http://localhost:${port}${urlPath}`, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        resolve({ status: res.statusCode!, body: JSON.parse(data) });
      });
    }).on('error', reject);
  });
}

beforeAll(async () => {
  // Clean slate
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);

  server = createApiServer(0, TEST_DB);
  await new Promise<void>((resolve) => {
    server.listen(0, () => {
      port = (server.address() as { port: number }).port;
      resolve();
    });
  });
});

afterAll(async () => {
  await new Promise<void>((resolve) => server.close(() => resolve()));
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
});

describe('API /v1/results', () => {
  it('returns empty results initially', async () => {
    const res = await fetch('/v1/results');
    expect(res.status).toBe(200);
    expect((res.body as { results: unknown[] }).results).toEqual([]);
  });
});

describe('API /v1/frameworks', () => {
  it('returns empty frameworks initially', async () => {
    const res = await fetch('/v1/frameworks');
    expect(res.status).toBe(200);
    expect((res.body as { frameworks: unknown[] }).frameworks).toEqual([]);
  });
});

describe('API /v1/frameworks/:name', () => {
  it('returns 404 for unknown framework', async () => {
    const res = await fetch('/v1/frameworks/nonexistent');
    expect(res.status).toBe(404);
  });
});

describe('API /v1/tasks', () => {
  it('returns empty tasks initially', async () => {
    const res = await fetch('/v1/tasks');
    expect(res.status).toBe(200);
    expect((res.body as { tasks: unknown[] }).tasks).toEqual([]);
  });
});

describe('API /v1/tasks/:id', () => {
  it('returns 404 for unknown task', async () => {
    const res = await fetch('/v1/tasks/nonexistent');
    expect(res.status).toBe(404);
  });
});

describe('API /v1/compare', () => {
  it('returns comparison data for two frameworks', async () => {
    const res = await fetch('/v1/compare/fw1/fw2');
    expect(res.status).toBe(200);
    expect((res.body as { frameworks: string[] }).frameworks).toEqual(['fw1', 'fw2']);
  });
});

describe('API routing', () => {
  it('returns 404 for unknown routes', async () => {
    const res = await fetch('/v1/nonexistent');
    expect(res.status).toBe(404);
  });
});
