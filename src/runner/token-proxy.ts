/**
 * Token counting proxy — sits between the framework and LLM API.
 * Intercepts all LLM API calls to count tokens transparently.
 * Framework-agnostic: works regardless of which LLM SDK is used.
 */

import http from 'node:http';
import https from 'node:https';

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  apiCalls: number;
  totalApiTimeMs: number;
}

export interface ProxyConfig {
  port: number;
  targetHost: string;
  targetPort: number;
  useTls: boolean;
}

const DEFAULT_PROXY_CONFIG: ProxyConfig = {
  port: 8989,
  targetHost: 'api.anthropic.com',
  targetPort: 443,
  useTls: true,
};

export class TokenCountingProxy {
  private server: http.Server | null = null;
  private config: ProxyConfig;
  private usage: TokenUsage = {
    inputTokens: 0,
    outputTokens: 0,
    totalTokens: 0,
    apiCalls: 0,
    totalApiTimeMs: 0,
  };

  constructor(config: Partial<ProxyConfig> = {}) {
    this.config = { ...DEFAULT_PROXY_CONFIG, ...config };
  }

  start(): Promise<void> {
    return new Promise((resolve) => {
      this.server = http.createServer((req, res) => {
        this.handleRequest(req, res);
      });

      this.server.listen(this.config.port, () => {
        resolve();
      });
    });
  }

  stop(): Promise<void> {
    return new Promise((resolve) => {
      if (this.server) {
        this.server.close(() => resolve());
      } else {
        resolve();
      }
    });
  }

  getUsage(): TokenUsage {
    return { ...this.usage };
  }

  resetUsage(): void {
    this.usage = {
      inputTokens: 0,
      outputTokens: 0,
      totalTokens: 0,
      apiCalls: 0,
      totalApiTimeMs: 0,
    };
  }

  private handleRequest(req: http.IncomingMessage, res: http.ServerResponse): void {
    const startTime = performance.now();
    this.usage.apiCalls++;

    let body = '';
    req.on('data', (chunk) => { body += chunk; });

    req.on('end', () => {
      // Parse request to estimate input tokens
      try {
        const parsed = JSON.parse(body);
        if (parsed.messages) {
          const inputText = parsed.messages.map((m: { content: string }) =>
            typeof m.content === 'string' ? m.content : JSON.stringify(m.content)
          ).join('');
          this.usage.inputTokens += estimateTokens(inputText);
        }
      } catch {
        // Non-JSON body, estimate from raw
        this.usage.inputTokens += estimateTokens(body);
      }

      // Forward to target
      const options = {
        hostname: this.config.targetHost,
        port: this.config.targetPort,
        path: req.url,
        method: req.method,
        headers: { ...req.headers, host: this.config.targetHost },
      };

      const transport = this.config.useTls ? https : http;
      const proxyReq = transport.request(options, (proxyRes) => {
        let responseBody = '';
        proxyRes.on('data', (chunk) => {
          responseBody += chunk;
          res.write(chunk);
        });

        proxyRes.on('end', () => {
          const elapsed = performance.now() - startTime;
          this.usage.totalApiTimeMs += elapsed;

          // Parse response to count output tokens
          try {
            const parsed = JSON.parse(responseBody);
            if (parsed.usage) {
              // Use actual token counts from API response if available
              this.usage.inputTokens += (parsed.usage.input_tokens || 0) - estimateTokens(body);
              this.usage.outputTokens += parsed.usage.output_tokens || 0;
            } else if (parsed.content) {
              const outputText = Array.isArray(parsed.content)
                ? parsed.content.map((c: { text?: string }) => c.text || '').join('')
                : typeof parsed.content === 'string' ? parsed.content : '';
              this.usage.outputTokens += estimateTokens(outputText);
            }
          } catch {
            this.usage.outputTokens += estimateTokens(responseBody);
          }

          this.usage.totalTokens = this.usage.inputTokens + this.usage.outputTokens;

          res.end();
        });

        res.writeHead(proxyRes.statusCode || 200, proxyRes.headers);
      });

      proxyReq.on('error', (err) => {
        res.writeHead(502);
        res.end(JSON.stringify({ error: 'Proxy error', message: err.message }));
      });

      proxyReq.write(body);
      proxyReq.end();
    });
  }
}

export function estimateTokens(text: string): number {
  // Rough estimate: ~4 characters per token for English text
  return Math.ceil(text.length / 4);
}

export function computeCost(
  usage: TokenUsage,
  inputPricePer1M: number = 15.0,
  outputPricePer1M: number = 75.0,
): { inputCostUsd: number; outputCostUsd: number; totalCostUsd: number } {
  const inputCostUsd = (usage.inputTokens / 1_000_000) * inputPricePer1M;
  const outputCostUsd = (usage.outputTokens / 1_000_000) * outputPricePer1M;
  return {
    inputCostUsd,
    outputCostUsd,
    totalCostUsd: inputCostUsd + outputCostUsd,
  };
}
