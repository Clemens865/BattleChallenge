/**
 * Adapter loader — reads adapter.yaml configs and validates them.
 */

import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';
import type { AdapterConfig, AdapterTier } from '../types/index.js';

const VALID_TIERS: AdapterTier[] = ['shell', 'structured', 'api', 'recorded'];

export function loadAdapter(adapterPath: string): AdapterConfig {
  const configPath = fs.statSync(adapterPath).isDirectory()
    ? path.join(adapterPath, 'adapter.yaml')
    : adapterPath;

  if (!fs.existsSync(configPath)) {
    throw new Error(`Adapter config not found: ${configPath}`);
  }

  const raw = fs.readFileSync(configPath, 'utf-8');
  const parsed = YAML.parse(raw) as Record<string, unknown>;

  return validateAdapter(parsed, path.dirname(configPath));
}

function validateAdapter(raw: Record<string, unknown>, baseDir: string): AdapterConfig {
  if (!raw.name || typeof raw.name !== 'string') {
    throw new Error('Adapter must have a "name" field');
  }
  if (!raw.version || typeof raw.version !== 'string') {
    throw new Error('Adapter must have a "version" field');
  }
  if (!raw.tier || !VALID_TIERS.includes(raw.tier as AdapterTier)) {
    throw new Error(`Adapter tier must be one of: ${VALID_TIERS.join(', ')}`);
  }
  if (!raw.run || typeof raw.run !== 'string') {
    throw new Error('Adapter must have a "run" field');
  }

  const tags = Array.isArray(raw.tags) ? raw.tags.map(String) : [];

  const config: AdapterConfig = {
    name: raw.name as string,
    version: raw.version as string,
    tier: raw.tier as AdapterTier,
    tags,
    run: raw.run as string,
    setup: typeof raw.setup === 'string' ? raw.setup : undefined,
    modelDefault: typeof raw.model_default === 'string' ? raw.model_default : undefined,
  };

  if (raw.tier === 'api') {
    config.endpoint = raw.endpoint as string | undefined;
    config.auth = raw.auth as string | undefined;
  }

  return config;
}

export function scaffoldAdapter(
  name: string,
  tier: AdapterTier,
  outputDir: string,
): string {
  const dir = path.join(outputDir, name);
  fs.mkdirSync(dir, { recursive: true });

  if (tier === 'shell') {
    const yaml = `name: ${name}
version: "0.1.0"
tier: shell
tags: []
setup: |
  # Install dependencies here
  # pip install ${name}
run: ./adapter.sh
model_default: claude-opus-4-6
`;
    fs.writeFileSync(path.join(dir, 'adapter.yaml'), yaml);

    const script = `#!/bin/bash
# BattleChallenge adapter for ${name}
# Input: $TASK_FILE contains the task requirements
# Input: $OUTPUT_DIR is where to put generated files
# Output: Generated files in $OUTPUT_DIR

# Replace this with your framework's command:
echo "TODO: Implement ${name} adapter"
echo "Task file: $TASK_FILE"
echo "Output dir: $OUTPUT_DIR"
`;
    fs.writeFileSync(path.join(dir, 'adapter.sh'), script, { mode: 0o755 });
  } else if (tier === 'api') {
    const yaml = `name: ${name}
version: "0.1.0"
tier: api
tags: [api-hosted]
endpoint: https://api.example.com/v1/generate
auth: Bearer $${name.toUpperCase().replace(/-/g, '_')}_API_KEY
submit:
  method: POST
  body: { "prompt": "{{task_content}}" }
poll:
  method: GET
  path: /status/{{job_id}}
  interval_ms: 5000
  complete_when: "status == 'done'"
collect:
  method: GET
  path: /output/{{job_id}}
`;
    fs.writeFileSync(path.join(dir, 'adapter.yaml'), yaml);
  } else {
    const yaml = `name: ${name}
version: "0.1.0"
tier: ${tier}
tags: []
run: ./adapter.sh
model_default: claude-opus-4-6
`;
    fs.writeFileSync(path.join(dir, 'adapter.yaml'), yaml);
  }

  return dir;
}
