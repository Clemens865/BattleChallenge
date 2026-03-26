/**
 * BattleChallenge Core Types
 *
 * These types define the fundamental data structures for the benchmarking system.
 */

// ============================================================================
// Framework & Adapter Types
// ============================================================================

export interface FrameworkConfig {
  name: string;
  version: string;
  tags: string[];
  tier: AdapterTier;
  setup?: string;
  run: string;
  modelDefault?: string;
}

export type AdapterTier = 'shell' | 'structured' | 'api' | 'recorded';

export interface AdapterConfig {
  name: string;
  version: string;
  tier: AdapterTier;
  tags: string[];
  setup?: string;
  run: string;
  modelDefault?: string;
  endpoint?: string;
  auth?: string;
  submit?: ApiSubmitConfig;
  poll?: ApiPollConfig;
  collect?: ApiCollectConfig;
}

export interface ApiSubmitConfig {
  method: string;
  body: Record<string, unknown>;
}

export interface ApiPollConfig {
  method: string;
  path: string;
  intervalMs: number;
  completeWhen: string;
}

export interface ApiCollectConfig {
  method: string;
  path: string;
}

// ============================================================================
// Task Types
// ============================================================================

export type TaskType = 'prd' | 'coding' | 'multi-step' | 'tool-use' | 'rag' | 'multi-agent';
export type DifficultyTier = 'T1' | 'T2' | 'T3' | 'T4';
export type TaskStatus = 'active' | 'secret' | 'retired';

export interface TaskDefinition {
  id: string;
  name: string;
  type: TaskType;
  tags: string[];
  difficulty: DifficultyTier;
  status: TaskStatus;
  passingThreshold: number;
  excellenceThreshold: number;
  autoScale: boolean;
  timeoutMs: number;
  tokenBudget?: number;
  requirementsPath: string;
  verifyPath: string;
  referencePath?: string;
}

export interface TaskContext {
  taskDir: string;
  outputDir: string;
  taskFile: string;
  task: TaskDefinition;
}

// ============================================================================
// Metrics Types
// ============================================================================

export interface MetricsProfile {
  correctness: CorrectnessMetrics;
  cost: CostMetrics;
  speed: SpeedMetrics;
  reliability: ReliabilityMetrics;
  quality: QualityMetrics;
  autonomy: AutonomyScore;
}

export interface CorrectnessMetrics {
  testsTotal: number;
  testsPassed: number;
  score: number;
  edgeCasesHandled: number;
  outcomeVerification: boolean;
}

export interface CostMetrics {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  inputCostUsd: number;
  outputCostUsd: number;
  totalCostUsd: number;
  costPerTestPassed: number;
}

export interface SpeedMetrics {
  totalMs: number;
  apiCallMs: number;
  processingMs: number;
  timeToFirstPassingTest: number | null;
}

export interface ReliabilityMetrics {
  runsAttempted: number;
  runsPassed: number;
  varianceIqr: number;
  failureMode: FailureMode | null;
}

export type FailureMode = 'timeout' | 'crash' | 'wrong_output' | 'partial';

export interface QualityMetrics {
  hasTests: boolean;
  testCoveragePct: number | null;
  mutationScore: number | null;
  humanReviewScore: number | null;
  readabilityHeuristic: number;
}

export type AutonomyScore = 0 | 1 | 2;

// ============================================================================
// Run & Result Types
// ============================================================================

export interface RunConfig {
  framework: string;
  task?: string;
  tags?: string[];
  model?: string;
  runs?: number;
  timeout?: number;
}

export interface RunResult {
  id: string;
  frameworkName: string;
  frameworkVersion: string;
  taskId: string;
  runNumber: number;
  metrics: MetricsProfile;
  metadata: RunMetadata;
  outputHash: string;
  startedAt: string;
  completedAt: string;
}

export interface RunMetadata {
  frameworkVersion: string;
  modelUsed: string;
  modelVersion: string;
  adapterType: 'reference' | 'custom';
  adapterVersion: string;
  dockerImageHash: string;
  runTimestamp: string;
}

export interface AggregatedResult {
  frameworkName: string;
  taskId: string;
  runs: RunResult[];
  median: MetricsProfile;
  iqr: Partial<MetricsProfile>;
  highVariance: boolean;
  verificationChain: VerificationChain;
}

export interface VerificationChain {
  taskHash: string;
  adapterHash: string;
  dockerImageHash: string;
  runnerVersion: string;
  modelVersion: string;
  environmentHash: string;
  outputHash: string;
}

// ============================================================================
// Leaderboard Types
// ============================================================================

export type LeaderboardView = 'best-performance' | 'controlled-model';
export type Track = 'verified' | 'open';

export interface LeaderboardEntry {
  framework: FrameworkConfig;
  profile: MetricsProfile;
  track: Track;
  adapterType: 'reference' | 'custom';
  view: LeaderboardView;
}

export interface LeaderboardFilter {
  tags?: string[];
  track?: Track;
  view?: LeaderboardView;
  adapterType?: 'reference' | 'custom';
}

// ============================================================================
// Runner Types
// ============================================================================

export interface RunnerConfig {
  memoryLimitMb: number;
  cpuLimit: number;
  timeoutMs: number;
  tokenProxyPort: number;
  networkIsolation: boolean;
}

export const DEFAULT_RUNNER_CONFIG: RunnerConfig = {
  memoryLimitMb: 4096,
  cpuLimit: 2,
  timeoutMs: 300_000,
  tokenProxyPort: 8989,
  networkIsolation: true,
};
