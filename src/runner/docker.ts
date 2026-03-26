/**
 * Docker container management for isolated benchmark execution.
 *
 * Each benchmark run executes in an isolated Docker container:
 * - Resource limits: 4GB RAM, 2 CPUs
 * - Network isolation: only LLM API reachable via token proxy
 * - Deterministic environment: pinned base image
 */

import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import type { RunnerConfig, AdapterConfig, TaskDefinition } from '../types/index.js';

export interface DockerRunOptions {
  adapter: AdapterConfig;
  task: TaskDefinition;
  taskDir: string;
  outputDir: string;
  config: RunnerConfig;
  proxyPort: number;
}

export function isDockerAvailable(): boolean {
  try {
    execSync('docker --version', { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

export function generateDockerfile(adapter: AdapterConfig): string {
  return `FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    git curl nodejs npm \\
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Copy adapter files
COPY . /adapter/

# Run adapter setup
${adapter.setup ? `RUN ${adapter.setup}` : '# No setup step'}

# Environment
ENV TASK_FILE=/workspace/task/requirements.md
ENV OUTPUT_DIR=/workspace/output

ENTRYPOINT ["/bin/bash", "/adapter/${typeof adapter.run === 'string' ? adapter.run : 'adapter.sh'}"]
`;
}

export function buildDockerImage(
  adapter: AdapterConfig,
  adapterDir: string,
): string {
  const tag = `battlechallenge/${adapter.name}:${adapter.version}`;

  const dockerfile = generateDockerfile(adapter);
  const dockerfilePath = path.join(adapterDir, 'Dockerfile.battlechallenge');
  fs.writeFileSync(dockerfilePath, dockerfile);

  try {
    execSync(`docker build -t ${tag} -f ${dockerfilePath} ${adapterDir}`, {
      stdio: 'pipe',
      timeout: 300_000,
    });
  } finally {
    // Clean up generated Dockerfile
    if (fs.existsSync(dockerfilePath)) {
      fs.unlinkSync(dockerfilePath);
    }
  }

  return tag;
}

export function runInDocker(options: DockerRunOptions): { exitCode: number; stdout: string; stderr: string } {
  const tag = `battlechallenge/${options.adapter.name}:${options.adapter.version}`;

  const args = [
    'docker', 'run',
    '--rm',
    `--memory=${options.config.memoryLimitMb}m`,
    `--cpus=${options.config.cpuLimit}`,
    `--network=none`,  // Network isolation
    `-v`, `${options.taskDir}:/workspace/task:ro`,
    `-v`, `${options.outputDir}:/workspace/output`,
    `-e`, `TASK_FILE=/workspace/task/${path.basename(options.task.requirementsPath)}`,
    `-e`, `OUTPUT_DIR=/workspace/output`,
    `-e`, `HTTP_PROXY=http://host.docker.internal:${options.proxyPort}`,
    `-e`, `HTTPS_PROXY=http://host.docker.internal:${options.proxyPort}`,
    tag,
  ];

  try {
    const output = execSync(args.join(' '), {
      timeout: options.task.timeoutMs,
      stdio: 'pipe',
      maxBuffer: 50 * 1024 * 1024,
    });

    return { exitCode: 0, stdout: output.toString(), stderr: '' };
  } catch (err: unknown) {
    const error = err as { status?: number; stdout?: Buffer; stderr?: Buffer };
    return {
      exitCode: error.status ?? 1,
      stdout: error.stdout?.toString() ?? '',
      stderr: error.stderr?.toString() ?? '',
    };
  }
}

export function getDockerImageHash(tag: string): string {
  try {
    const output = execSync(`docker inspect --format='{{.Id}}' ${tag}`, { stdio: 'pipe' });
    return output.toString().trim();
  } catch {
    return '';
  }
}

export function cleanupDockerImages(prefix = 'battlechallenge/'): void {
  try {
    const output = execSync(`docker images --format '{{.Repository}}:{{.Tag}}' | grep '^${prefix}'`, { stdio: 'pipe' });
    const images = output.toString().trim().split('\n').filter(Boolean);
    for (const image of images) {
      execSync(`docker rmi ${image}`, { stdio: 'pipe' });
    }
  } catch {
    // No images to clean up
  }
}
