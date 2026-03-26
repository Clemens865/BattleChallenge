# BattleChallenge — Product Requirements Document

> **Version**: 2.0 | **Date**: 2026-03-26 | **Status**: Draft (Post-Adversarial Review)
>
> The open-source benchmarking system that compares agentic AI frameworks head-to-head on standardized tasks.

---

## 1. Problem Statement

### The Gap

There is no standardized way to compare agentic AI frameworks against each other. Existing benchmarks (SWE-bench, GAIA, AgentBench) test **models**, not **frameworks**. Developers choosing between LangGraph, CrewAI, Claude Code, Aider, or OpenAI Agents SDK have no objective, reproducible data to guide their decision.

### The Cost of This Gap

- **Developers** waste weeks on manual evaluation and regret-driven migration
- **Enterprises** make multi-year procurement decisions based on vendor marketing, not data
- **Framework authors** have no neutral arena to prove their improvements
- **The industry** lacks a common language for comparing agentic capabilities

### Market Context

- AI agent market: $10.9B (2026), growing 43-50% CAGR
- 72% of Global 2000 companies run AI agents in production
- 920% surge in framework usage (2023-2025)
- 32% of practitioners cite quality as the top barrier to production deployment
- **Zero** standardized framework-vs-framework comparison tools exist

---

## 2. Product Vision

**BattleChallenge is the TPC benchmark for agentic AI frameworks.**

Give every framework the same tasks. Measure everything. Publish everything. Let the data speak.

### Success Looks Like

In 12 months: "What's your BattleChallenge score?" is a normal question in framework selection conversations. Framework READMEs display BattleChallenge badges. Enterprise RFPs reference BattleChallenge results. Framework authors optimize against it.

---

## 3. Users & Personas

### P1: Indie Developer ("Maya")
- **Context**: Solo dev or small team, choosing a framework for a new project
- **Need**: Quick, trustworthy answer to "which framework should I use?"
- **Behavior**: Scans leaderboard, sorts by cost, reads top-5, makes a decision
- **Success metric**: Time from "confused" to "confident framework choice" < 10 minutes

### P2: Enterprise Evaluator ("David")
- **Context**: Engineering lead at Fortune 500, evaluating frameworks for production
- **Need**: Objective data to justify procurement decisions to leadership
- **Behavior**: Downloads raw data, runs internal reproduction, maps tasks to use cases, attaches report to procurement docs
- **Success metric**: BattleChallenge data accepted as valid reference in internal procurement review

### P3: Framework Author ("Priya")
- **Context**: Maintainer of an agentic framework, wants to prove quality
- **Need**: Neutral arena to demonstrate strengths and identify weaknesses
- **Behavior**: Submits adapter, reviews per-task results, optimizes, re-submits next round
- **Success metric**: BattleChallenge badge on README drives measurable adoption increase

### P4: Benchmark Skeptic ("Dr. Tanaka")
- **Context**: Academic or methodologist who scrutinizes evaluation rigor
- **Need**: Transparent, reproducible methodology they can audit and cite
- **Behavior**: Reads methodology paper, downloads raw data, reproduces results, publishes analysis
- **Success metric**: Willing to cite BattleChallenge in academic publications

---

## 4. Framework Taxonomy (Tag-Based)

Rigid categories become obsolete as frameworks converge (Claude Code is both a coding agent AND an orchestration framework; Cursor is both an IDE AND an agent). Instead of fixed categories, we use **tags**.

### Tag System

Each framework declares tags. The leaderboard filters by tags, not categories.

```yaml
# Example: Claude Code
framework: claude-code
tags:
  - coding-agent
  - orchestration
  - cli
  - model-locked:claude
  - multi-agent

# Example: LangGraph
framework: langgraph
tags:
  - orchestration
  - library
  - python
  - model-agnostic
  - stateful
  - multi-agent

# Example: Cursor
framework: cursor
tags:
  - ide-integrated
  - coding-agent
  - editor-plugin
  - multi-model
```

### Default Leaderboard Views

For simplicity, the website offers pre-built views based on common tag combinations:

| View | Tag Filter | For Users Who Ask |
|------|-----------|-------------------|
| **Orchestration** | `orchestration` + `library` | "Which orchestration framework?" |
| **Coding Agents** | `coding-agent` + (`cli` OR `library`) | "Which coding agent?" |
| **IDE Tools** | `ide-integrated` | "Which IDE AI tool?" |
| **All Frameworks** | No filter | "Show me everything" |

Users can create custom views by combining any tags. Tags evolve organically as the ecosystem changes — no rigid taxonomy to become obsolete.

### Interaction Model Tags (How We Connect)

Frameworks also declare their **interaction model**, which determines which adapter tier applies:

| Tag | Meaning | Adapter Tier |
|-----|---------|-------------|
| `library` | Import and call functions | Tier 1: Library |
| `cli` | Run as command-line process | Tier 2: CLI |
| `api-hosted` | Cloud-hosted, HTTP API | Tier 3: API |
| `ide-integrated` | Requires editor UI | Tier 4: Recorded Run |
| `internal-only` | Not publicly accessible | Self-benchmark (run internally, optionally publish) |

---

## 5. Metrics

### Design Principle: Profiles, Not Composite Scores

We do **NOT** output a single ranking number. A composite score hides what matters and forces false comparisons between fundamentally different approaches. Instead, every framework gets a **multi-dimensional profile**.

```
LangGraph:
  ████████░░ Correctness:  82/100
  ██████░░░░ Efficiency:   61/100
  ███████░░░ Cost:         $0.14/task
  █████░░░░░ Speed:        18s avg
  ████████░░ Reliability:  85% (5/5 pass)
  ████████░░ Quality:      78/100

Aider:
  ███████░░░ Correctness:  74/100
  █████████░ Efficiency:   92/100
  █████████░ Cost:         $0.03/task
  ████████░░ Speed:        8s avg
  ██████░░░░ Reliability:  68% (3/5 pass)
  ██████░░░░ Quality:      62/100
```

The website lets users **set their own weights** to generate a personalized ranking. Default weights are provided but clearly labeled as "one perspective, not the truth."

### The Five Meta-Metrics (Paradigm-Proof)

These metrics work whether the framework produces code files, deployed apps, PRs, or running services. They survive paradigm shifts.

| Meta-Metric | What It Measures | How It's Measured | Why It's Future-Proof |
|-------------|-----------------|-------------------|----------------------|
| **Correctness** | Does the outcome work? | Automated test suite (unit, integration, e2e, HTTP assertions, Playwright) | Tests verify outcomes, not implementation |
| **Cost** | How much does it cost? | Token proxy tracks API spend in USD | Dollar cost is always relevant |
| **Speed** | How fast? | Wall-clock time from task start to completion | Time is always relevant |
| **Reliability** | How consistent? | % of runs that pass across N repetitions | Consistency always matters |
| **Autonomy** | How much human help needed? | 0 = fully autonomous, 1 = needed hints, 2 = needed intervention | Measures toward AGI-like capability |

### Implementation Metrics (Current Detail Layer)

Below the meta-metrics, we collect granular data that may evolve:

```
For each (framework × task × run):
  ├── Correctness
  │   ├── tests_total, tests_passed, score (0-100)
  │   ├── edge_cases_handled (adversarial test injection)
  │   └── outcome_verification (Playwright/HTTP/CLI assertions)
  ├── Cost
  │   ├── input_tokens, output_tokens, total_tokens
  │   ├── input_cost_usd, output_cost_usd, total_cost_usd
  │   └── cost_per_test_passed
  ├── Speed
  │   ├── total_ms, api_call_ms, processing_ms
  │   └── time_to_first_passing_test
  ├── Reliability
  │   ├── runs_attempted, runs_passed
  │   ├── variance_iqr (interquartile range across runs)
  │   └── failure_mode (timeout | crash | wrong_output | partial)
  ├── Quality (outcome-based, not static analysis)
  │   ├── has_tests: boolean (did framework generate its own tests?)
  │   ├── test_coverage_pct: number
  │   ├── mutation_score: number (mutation testing)
  │   ├── human_review_score?: 0-100 (sampled 20%)
  │   └── readability_heuristic: number
  └── Metadata
      ├── framework_version, model_used, model_version
      ├── adapter_type: 'reference' | 'custom'
      ├── adapter_version, docker_image_hash
      └── run_timestamp: ISO8601
```

### Two Leaderboard Views for Model Control

| View | What It Shows | Use Case |
|------|--------------|----------|
| **Best Performance** (default) | Each framework uses its best model config | "Which framework gives the best results?" |
| **Controlled Model** | All model-agnostic frameworks run with the SAME model (e.g., Claude Opus 4.6) | "Which framework adds the most value on top of the model?" |

The Controlled Model view is the **scientifically valid** comparison. The Best Performance view is the **practically useful** comparison. Both are clearly labeled.

Model-locked frameworks (Claude Code → Claude only) appear only in Best Performance view with a `model-locked` tag.

### Statistical Rigor

- **Minimum 5 runs** per task per framework (not 3)
- **Median + IQR** reported (not mean — resists outliers)
- Variance flagged when IQR > 20% of median → labeled "high variance"
- **Model versions pinned** explicitly (e.g., `claude-opus-4-6-20260301`)
- If model updated mid-round → re-run all affected results
- Rankings only when confidence intervals **don't overlap** → otherwise: "No significant difference"
- Per-run raw data published so anyone can do their own analysis

---

## 6. Task System

### Task Types

| Type | Description | Difficulty Range |
|------|-------------|-----------------|
| **PRD Tasks** | Full product requirement → working implementation | T2-T4 |
| **Coding Tasks** | Implement a specific function or module | T1-T3 |
| **Multi-Step Tasks** | Research → plan → implement → test | T3-T4 |
| **Tool-Use Tasks** | Use APIs, databases, file systems correctly | T2-T3 |
| **RAG Tasks** | Retrieve information and generate accurate responses | T2-T3 |
| **Multi-Agent Tasks** | Coordinate multiple agents to complete a goal | T3-T4 |

### Difficulty Tiers

| Tier | Scope | Example | Expected Duration |
|------|-------|---------|-------------------|
| **T1** | Single file, single step | "Validate email addresses with tests" | < 2 min |
| **T2** | Multi-file, 2-3 steps | "REST API with CRUD + tests" | 2-10 min |
| **T3** | Multi-component | "Full-stack feature with auth, DB, API, UI" | 10-30 min |
| **T4** | Multi-agent coordination | "Research, plan, implement, test a microservice" | 30-60 min |

### Task Structure (Outcome-Based)

Tasks define WHAT to verify, not HOW it was built. This works whether the framework produces code files, a deployed app, a PR, or a running service.

```
task-042-user-auth/
  task.yaml                # ID, type, tags, difficulty, expected token range
  requirements.md          # What the framework sees (the PRD or spec)
  verify/
    test_outcomes.py       # Outcome tests: "can a user log in?" (Playwright, HTTP, CLI)
    test_correctness.py    # Unit/integration tests on generated code
    test_edge_cases.py     # Adversarial inputs, boundary conditions
    test_quality.py        # Mutation testing, coverage checks, readability
  reference/
    solution/              # Reference implementation (never shown to frameworks)
  constraints.yaml         # Time limit, token budget, allowed dependencies
```

**Key change from v1**: The `verify/` directory tests **outcomes**, not code structure. Example:

```python
# test_outcomes.py — works regardless of HOW the framework built it

def test_user_can_register():
    """Outcome: a new user can create an account."""
    response = httpx.post(f"{BASE_URL}/register", json={"email": "test@x.com", "password": "Str0ng!"})
    assert response.status_code == 201

def test_user_can_login():
    """Outcome: a registered user can log in and get a token."""
    response = httpx.post(f"{BASE_URL}/login", json={"email": "test@x.com", "password": "Str0ng!"})
    assert response.status_code == 200
    assert "token" in response.json()

def test_invalid_password_rejected():
    """Outcome: wrong password is rejected."""
    response = httpx.post(f"{BASE_URL}/login", json={"email": "test@x.com", "password": "wrong"})
    assert response.status_code == 401
```

This approach future-proofs the benchmark: it works whether the framework generates Python files, deploys a Docker container, or produces a running Kubernetes service.

### Difficulty Auto-Scaling

Instead of fixed difficulty tiers that saturate, tasks have dynamic thresholds:

```yaml
# task.yaml
difficulty:
  passing_threshold: 60    # Minimum score to count as "solved"
  excellence_threshold: 95 # Maximum meaningful score
  auto_scale: true         # When >80% of frameworks pass, raise passing_threshold by 5
```

This prevents SWE-bench-style saturation: as frameworks improve, the bar rises automatically.

### Task Lifecycle & Anti-Gaming

```
ACTIVE (75%)          → Currently scored, publicly visible
SECRET (20%)          → Held-out, revealed only at evaluation time
RETIRED (rotated out) → Archived, available for practice but not scored

Quarterly: 25% of active tasks retire, replaced by new tasks
Secret tasks: Regenerated every round, never reused
```

### Task Contribution Pipeline

```
Community submits PR → Automated checks (tests pass, reference works)
                     → Peer review (2+ non-conflicted reviewers)
                     → Advisory board spot-check
                     → Added to rotation pool
```

Community-contributed tasks target 60%+ of task bank by Month 6.

---

## 7. Two-Tier Submission Model (Inspired by MLPerf)

### Verified Track
- Must use reference adapter template
- Must run ALL task categories
- Compliance tests required before submission
- Results peer-reviewed before publication
- **This is what enterprise procurement cites**

### Open Track
- Custom adapters allowed
- Pick any task subset
- No compliance requirements
- Shows what's possible, not what's standard
- **This is where innovation happens**

Results clearly labeled: `[Verified]` or `[Open]` — never mixed on the same leaderboard view.

---

## 8. System Architecture

### Components

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Task Bank   │     │   Runner    │     │   Scorer    │
│              │────>│             │────>│             │
│ .yaml + .md  │     │ Docker env  │     │ Correctness │
│ + tests      │     │ Token proxy │     │ Efficiency  │
│ + reference  │     │ Time track  │     │ Quality     │
└─────────────┘     └─────────────┘     │ Cost calc   │
                                         └──────┬──────┘
┌─────────────┐     ┌─────────────┐            │
│  Website    │<────│  Results DB │<───────────┘
│             │     │             │
│ Leaderboard │     │ Raw JSON    │     ┌─────────────┐
│ Compare     │     │ History     │     │   API       │
│ Download    │     │ Reprodn log │     │ /v1/results │
│ Badges      │     │             │     │ /v1/tasks   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Runner Engine

Each benchmark run executes in an isolated Docker container:

- **Resource limits**: 4GB RAM, 2 CPUs, configurable timeout per tier
- **Token counting proxy**: Sits between framework and LLM API, counts every token transparently
- **Network isolation**: Framework can only reach the LLM API (via proxy) — no internet access to prevent lookup of solutions
- **Deterministic environment**: Pinned base image, fixed dependencies, seeded randomness where possible

### Adapter System (Three Tiers)

The v1 PRD had a single TypeScript interface that only worked for ~40% of frameworks. The 18-framework analysis revealed radically different interaction models (bash loops, IDE plugins, cloud SaaS, libraries). We now support three tiers.

#### Tier 1: Shell Script Adapter (30 minutes to implement)

The **minimum viable adapter**. Captures 80% of benchmarking value with 10% of effort.

```bash
#!/bin/bash
# adapter.sh — This is ALL a framework author needs to provide

# Input: $TASK_FILE contains the task requirements
# Input: $OUTPUT_DIR is where to put generated files
# Output: Generated files in $OUTPUT_DIR
# Token counting: Handled automatically by the runner's proxy

# Example: Aider
aider --message-file "$TASK_FILE" --yes --auto-commits --output-dir "$OUTPUT_DIR"

# Example: Claude Code
cat "$TASK_FILE" | claude --output-dir "$OUTPUT_DIR" --print

# Example: Ralph Loop pattern
for i in {1..5}; do cat "$TASK_FILE" | claude-code; done
```

The runner handles everything else: Docker environment, token proxy, timing, scoring.

**Adapter config** (adapter.yaml):
```yaml
name: aider
version: "0.52.0"
tier: shell
tags: [coding-agent, cli, model-agnostic]
setup: |
  pip install aider-chat
run: ./adapter.sh
model_default: claude-opus-4-6
```

#### Tier 2: Structured Adapter (half day to implement)

For frameworks that benefit from lifecycle hooks and structured output.

```typescript
interface BattleChallengeAdapter {
  name: string;
  version: string;
  tags: string[];

  initialize(context: TaskContext): Promise<void>;
  execute(task: Task): Promise<ExecutionResult>;
  teardown(): Promise<void>;
  getTokenUsage(): TokenUsage;
  getModelInfo(): ModelInfo;
}
```

#### Tier 3: API Adapter (for cloud-hosted services)

For frameworks like Lovable, Devin, bolt.new that are cloud SaaS products.

```yaml
name: lovable
version: "2026.3"
tier: api
tags: [coding-agent, api-hosted, model-locked:proprietary]
endpoint: https://api.lovable.dev/v1/generate
auth: Bearer $LOVABLE_API_KEY
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
```

#### Tier 4: Recorded Run (for IDE tools)

For Cursor, Windsurf, etc. that require a GUI. Framework author records a session.

```yaml
name: cursor
version: "0.48"
tier: recorded
tags: [ide-integrated, coding-agent, multi-model]
recording_format: screencast + file_diff + token_log
# Author records themselves completing the task in the IDE
# Submits: recording, final file state, token usage log
# Verification: Advisory board spot-checks recordings
```

**Honest caveat**: Tier 4 results are less reproducible. They're labeled `[Recorded]` on the leaderboard and excluded from the Controlled Model view.

#### Reference Adapters (Maintained by BattleChallenge Team)

To prevent adapter quality from biasing results, the BattleChallenge team maintains **reference adapters** for the top 5-8 frameworks.

- Reference adapters are the "gold standard" — maintained and optimized by us
- Framework authors can submit custom adapters that MAY outperform reference adapters
- Results labeled: `[Reference]` vs `[Custom]`
- Consumers can filter to reference-only for the fairest comparison

### Transparency: What We Actually Measure

**We are honest about this**: BattleChallenge measures the **framework + model + adapter** combination, not "the framework" in isolation. This is stated clearly on every results page:

> "Results reflect the complete stack: framework orchestration + underlying model + adapter implementation. Use the Controlled Model view to isolate framework contribution."

### Verification Chain

Every published result includes:

```json
{
  "resultId": "bc-q2-2026-langgraph-042",
  "verificationChain": {
    "taskHash": "sha256:...",
    "adapterHash": "sha256:...",
    "dockerImageHash": "sha256:...",
    "runnerVersion": "1.2.0",
    "modelVersion": "claude-opus-4-6-20260301",
    "environmentHash": "sha256:...",
    "outputHash": "sha256:..."
  }
}
```

Anyone can download exact inputs and reproduce.

---

## 9. Product Surface Areas

### Priority Order: Website First, CLI Second

80% of users (Maya the indie dev) will **never install anything**. She'll Google "langraph vs crewai benchmark", click our link, scan the leaderboard, and decide. The website is the product. The CLI is power-user infrastructure.

### 9A. Website (battlechallenge.dev) — PRIMARY PRODUCT

The main interface for discovery, comparison, and decision-making.

**Pages:**

| Page | Purpose |
|------|---------|
| **/ (Home)** | Hero + quick leaderboard preview + "Find My Framework" CTA |
| **/leaderboard** | Full interactive leaderboard with category/metric filters |
| **/compare/:fw1/:fw2** | Side-by-side comparison of two frameworks |
| **/framework/:name** | Framework profile: scores, history, per-task breakdown |
| **/task/:id** | Task detail: description, scores by framework, methodology |
| **/methodology** | Full scoring methodology, task design, governance |
| **/reproduce** | Guide to reproducing results + reproduction registry |
| **/contribute** | How to submit adapters and tasks |
| **/api** | API documentation |
| **/report/:round** | Quarterly report (also downloadable as PDF) |

**Leaderboard features:**
- **Multi-dimensional profiles** — radar chart per framework, not a single score
- **Custom weighting** — slider to set your own metric weights ("I care about cost more than speed")
- Sort by any metric column
- Filter by tags (not rigid categories)
- Toggle Verified vs Open track
- Toggle Best Performance vs Controlled Model view
- Filter by adapter type: Reference only / All
- Historical trend sparklines per framework
- Click any cell → drill down to per-task detail with **full generated source code**
- Download visible data as CSV/JSON
- **Social-media-ready comparison cards** — shareable images for Twitter/LinkedIn
- SEO-optimized: "langgraph vs crewai" → lands on `/compare/langgraph/crewai`
- Mobile-friendly, < 2s load time, no login required

**"Find My Framework" Quiz:**
5 questions → personalized recommendation with data backing.
```
Q1: What type of project? [Web app / API / Data pipeline / Multi-agent / Other]
Q2: What matters most? [Cost / Speed / Correctness / Reliability]
Q3: Model preference? [Claude / GPT / Gemini / Open source / No preference]
Q4: Language? [Python / TypeScript / Both / Other]
Q5: Team size? [Solo / Small team / Enterprise]
→ Result: "Based on your profile, we recommend X. Here's why: [data]"
```

### 9B. Instant Quick-Start (Zero Install)

The "wow moment" that drives adoption — no Docker, no global install:

```bash
# Compare two frameworks instantly via hosted runner
npx battlechallenge quick claude-code aider

# Output: results in terminal + shareable link
# Uses hosted runner (free for T1-T2 tasks)
# Full local Docker runs available for serious verification
```

### 9C. CLI Tool (`battlechallenge`) — POWER USER TOOL

For verifiers (15% of users) and contributors (5%).

```bash
# Install (for local Docker-based runs)
npm install -g battlechallenge

# --- RUNNING BENCHMARKS ---
battle run --framework <name>              # Run all tasks locally
battle run --framework <name> --tags coding-agent  # Filter by tags
battle run --framework <name> --task 042   # Run single task
battle compare <fw1> <fw2>                 # Head-to-head
battle compare <fw1> <fw2> --model claude-opus-4-6  # Controlled model comparison

# --- VERIFICATION ---
battle reproduce --result-id <id>          # Reproduce a published result
battle verify --result-id <id>             # Run + compare to published

# --- ADAPTER DEVELOPMENT ---
battle adapter init --framework <name> --tier shell  # Scaffold (30 min)
battle adapter init --framework <name> --tier structured  # Scaffold (half day)
battle adapter test                        # Validate locally
battle adapter submit                      # Open PR

# --- TASK DEVELOPMENT ---
battle task init --type prd --tier t2      # Scaffold new task
battle task validate                       # Check tests + reference
battle task submit                         # Open PR

# --- DATA ACCESS ---
battle results                             # Latest leaderboard in terminal
battle results --tags orchestration        # Filter by tags
battle results --format json               # Machine-readable
battle export --round q2-2026 --format csv # Full round data
```

### 9D. API (api.battlechallenge.dev)

```
GET  /v1/results                          # Latest round, all categories
GET  /v1/results?category=orchestration   # Filter
GET  /v1/results?round=q2-2026           # Historical
GET  /v1/frameworks                       # All frameworks
GET  /v1/frameworks/:name                 # Single framework profile
GET  /v1/frameworks/:name/history         # Score history across rounds
GET  /v1/tasks                            # All public tasks
GET  /v1/tasks/:id                        # Single task detail
GET  /v1/compare/:fw1/:fw2               # Head-to-head data
GET  /v1/reproductions                    # Community reproduction log
POST /v1/reproductions                    # Submit a reproduction
GET  /v1/export/:round                    # Full round data (CSV/JSON)
```

Rate limited: 100 req/min unauthenticated, 1000 req/min with API key (free).

### 9D. Badge System

```
[![BattleChallenge Verified](https://battlechallenge.dev/badge/<framework>/latest.svg)](https://battlechallenge.dev/framework/<framework>)
```

Badge tiers:
- **Verified** — Participated in Verified track, results published
- **Top 3** — Ranked top 3 in category
- **Efficiency Leader** — Best cost-per-task in category
- **Community Choice** — Most reproduced results

Badges are SVG, auto-update each round, and link to full results.

---

## 10. Anti-Gaming System

### Detection Layers

| Layer | Method | Catches |
|-------|--------|---------|
| **Static Analysis** | Scan adapter code for task IDs, known answers, benchmark-specific strings | Direct cheating |
| **Behavioral Analysis** | Compare scores on public vs secret tasks; flag >15% gap | Overfitting to known tasks |
| **Token Pattern Analysis** | Unusually low tokens on specific tasks = suspicious | Hardcoded shortcuts |
| **Community Auditing** | All adapters open-source; anyone can file a dispute | Subtle gaming |
| **Peer Review** | Verified track submissions reviewed before publication | Adapter manipulation |

### Enforcement

| Severity | Trigger | Action |
|----------|---------|--------|
| **Warning** | Minor adapter issue, first offense | Private notice, fix required before next round |
| **Flag** | Suspicious score pattern | Result marked with caveat, investigation opened |
| **Disqualification** | Proven benchmark-specific optimization | Removed from round, public explanation published |
| **Ban** | Repeated or egregious gaming | Removed from all leaderboards, adapter rejected |

### Dispute Resolution

```
Day 0:  Dispute filed (GitHub issue with evidence)
Day 1:  Automated re-run triggered
Day 3:  Advisory board preliminary review
Day 7:  Decision published (dismiss / flag / disqualify)
Day 14: Appeal window closes
```

All decisions published with full reasoning. No secret enforcement.

---

## 11. Governance

### Advisory Board

- 5-7 members: academics, independent engineers, enterprise practitioners
- **No** framework authors, employees of framework companies, or investors
- Published COI disclosures
- 2-year rotating terms, staggered (never full replacement)
- Responsibilities: methodology approval, dispute resolution, task review oversight

### Decision-Making

| Decision Type | Who Decides |
|--------------|-------------|
| Task approval | Peer reviewers + advisory board spot-check |
| Methodology changes | Advisory board with 30-day public comment period |
| Disqualification | Advisory board (2/3 majority) |
| Category definitions | Advisory board + community RFC |
| Scoring weight changes | Advisory board + 60-day public comment period |

### Path to Foundation

Month 1-6: Project governed by core team + advisory board
Month 6-12: RFC for foundation structure
Year 2: Formal foundation (model: MLCommons) with member organizations

---

## 12. Rollout Phases

### Phase 1: Foundation (Weeks 1-4)

**Goal**: Runnable benchmark + first published results on a website.

| Deliverable | Priority |
|-------------|----------|
| Task runner engine (Docker-based, resource-limited) | P0 |
| Token counting proxy | P0 |
| **Three-tier adapter system** (shell script + structured + API) | P0 |
| 10 initial tasks with **outcome-based tests** (T1-T2) | P0 |
| **5 meta-metrics** scoring engine (correctness, cost, speed, reliability, autonomy) | P0 |
| CLI: `battle run`, `battle results` | P0 |
| **3 reference adapters** (Claude Code, Aider, LangGraph — shell script tier) | P0 |
| **Website v1**: static leaderboard with multi-dimensional profiles | P0 |
| `npx battlechallenge quick` instant comparison (hosted runner) | P1 |
| README + quickstart guide | P0 |

**Exit criteria**: `npx battlechallenge quick claude-code aider` works. Results visible on website. < 5 minutes from zero to first comparison.

### Phase 2: Expansion (Weeks 5-8)

**Goal**: 8+ frameworks, credible enough to share publicly.

| Deliverable | Priority |
|-------------|----------|
| 20 additional tasks (T1-T3, all task types, outcome-based) | P0 |
| PRD-based task format | P0 |
| Cost-per-task calculation with real API pricing | P0 |
| **5 more adapters** (CrewAI, OpenAI SDK, Anthropic SDK, Mastra, Codex) | P0 |
| **Tag-based taxonomy** on website (replace rigid categories) | P0 |
| **Custom weighting sliders** on leaderboard | P0 |
| `battle compare` + `battle reproduce` commands | P1 |
| **Controlled Model view** (same model across frameworks) | P1 |
| Raw data export (JSON/CSV) + API v1 | P1 |
| **Compare pages** SEO-optimized ("langgraph vs crewai") | P1 |
| Verification chain on all results | P1 |

**Exit criteria**: 8 frameworks, profiles published, compare pages ranking in search, `battle reproduce` works.

### Phase 3: Credibility (Weeks 9-16)

**Goal**: Trusted enough for enterprise reference and academic citation.

| Deliverable | Priority |
|-------------|----------|
| Advisory board formed + announced | P0 |
| Methodology paper published | P0 |
| 20 more tasks (total 50, T1-T4) with **auto-scaling difficulty** | P0 |
| **Statistical rigor**: 5 runs, median+IQR, CI-based rankings | P0 |
| Human review sampling (20% of tasks) | P0 |
| Secret held-out task set (10 tasks) | P0 |
| Verified vs Open track separation | P0 |
| **"Find My Framework" quiz** | P1 |
| Badge system | P1 |
| Community task contribution pipeline | P1 |
| Quarterly rotation infrastructure | P1 |
| **Social-media-ready comparison cards** | P1 |
| Enterprise private benchmark option (`battle run --tasks ./my-tasks/`) | P2 |

**Exit criteria**: Advisory board published, methodology paper cited, 3+ independent reproductions, framework authors submitting adapters proactively.

### Phase 4: Standardization (Months 5-12)

**Goal**: Industry standard.

| Deliverable | Priority |
|-------------|----------|
| 12+ frameworks benchmarked (including 2+ API-tier cloud services) | P0 |
| Quarterly cadence (2+ rounds completed) | P0 |
| Community reproduction registry on website | P0 |
| Adapter certification program | P1 |
| Compliance track (experimental) | P1 |
| CI/CD integration (GitHub Actions — auto-run on framework release) | P1 |
| Quarterly PDF report for enterprise | P2 |
| Foundation governance RFC | P2 |
| Analyst outreach (Gartner/Forrester) | P2 |
| Recorded Run format for IDE tools (Tier 4) | P2 |

**Exit criteria**: Enterprise RFPs reference BattleChallenge. Framework READMEs display badges. 1000+ GitHub stars. "What's your BattleChallenge profile?" is a normal question.

---

## 13. Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | TypeScript (CLI + runner + API) | Matches agentic ecosystem, npm distribution |
| Task tests | Python (pytest) | Most frameworks output Python; universal test runner |
| Containerization | Docker | Reproducibility standard; pinnable by hash |
| Database | SQLite (local) + PostgreSQL (API) | Zero-config local, scalable remote |
| Website | Static site (Astro/Next) + API | Fast, cheap to host, SEO-friendly |
| Hosting | GitHub Pages (site) + Railway/Fly (API) | Free tier for site, cheap for API |
| CI | GitHub Actions | Free for open source, familiar |
| Token proxy | HTTP proxy intercepting LLM API calls | Framework-agnostic, can't be bypassed |

---

## 14. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Framework authors refuse to participate | Medium | High | Shell-script adapter (30 min effort); community can submit; non-participation is itself a signal |
| Goodhart's Law / gaming | High | High | Quarterly rotation, secret tasks, behavioral analysis, auto-scaling difficulty, public disqualification |
| Results don't match production reality | Medium | High | Outcome-based tests, enterprise private benchmarks, lab-to-production gap acknowledged in methodology |
| Adapter quality biases results | High | High | Reference adapters maintained by us; results labeled `[Reference]` vs `[Custom]` |
| Model variable confounds comparison | High | High | Controlled Model view (same model across frameworks); model-locked frameworks labeled |
| Composite scores mislead users | High | Medium | Profiles not scores; user-configurable weights; no forced ranking when CIs overlap |
| Benchmark saturation | Medium | Medium | Auto-scaling difficulty thresholds; new task types quarterly |
| Categories become obsolete | Medium | Medium | Tag-based taxonomy evolves organically |
| IDE tools can't be benchmarked fairly | Medium | Medium | Recorded Run format (Tier 4); labeled `[Recorded]`; honest about lower reproducibility |
| Single-entity governance concern | Medium | Medium | Advisory board from day 1, foundation RFC by month 6 |
| Non-determinism in agent output | High | Medium | 5 runs, median+IQR, "no significant difference" when CIs overlap |
| Legal risk from framework naming | Low | Medium | Only publish for consented frameworks or community-submitted adapters |

---

## 15. Success Metrics

### Phase 1-2 (Months 1-2)

| Metric | Target |
|--------|--------|
| Frameworks benchmarked | 5 |
| Tasks in bank | 30 |
| CLI installs | 100 |
| GitHub stars | 200 |

### Phase 3 (Months 3-4)

| Metric | Target |
|--------|--------|
| Frameworks benchmarked | 8 |
| Tasks in bank | 50 |
| Independent reproductions | 5 |
| Advisory board seated | Yes |
| Methodology paper published | Yes |

### Phase 4 (Months 5-12)

| Metric | Target |
|--------|--------|
| Frameworks benchmarked | 12+ |
| Tasks in bank | 75+ |
| Independent reproductions | 20+ |
| Enterprise citations in procurement | 3+ |
| Community task contributors | 20+ |
| GitHub stars | 1000+ |
| API requests per month | 10,000+ |
| Quarterly rounds completed | 2+ |

---

## 16. What This PRD Does NOT Cover

- **Building a framework**: BattleChallenge benchmarks frameworks, it doesn't build one
- **Pure model evaluation**: SWE-bench does this; we test framework+model+adapter stacks (and are honest about it)
- **Observability/tracing**: LangSmith, Langfuse do this; we do comparative benchmarking
- **Paid tiers**: Everything is free and open source (foundation funding model TBD for year 2)
- **Non-software agents**: Initial scope is code-generating / software-building agentic frameworks

## 17. Honest Limitations

Things we cannot fully solve, stated transparently on the website:

1. **We benchmark framework+model+adapter, not "the framework" alone.** The Controlled Model view isolates framework contribution, but adapter quality always matters.
2. **IDE tools (Cursor, Windsurf) are hard to benchmark fairly.** Recorded Runs are less reproducible than automated runs. Results labeled accordingly.
3. **Production performance may differ.** AWS research found a 37% lab-to-production gap. Our outcome-based tasks reduce but don't eliminate this.
4. **Agents are non-deterministic.** Even with 5 runs, variance can be high. We report it honestly rather than hiding it behind averages.
5. **Taxonomy will evolve.** Today's tags may not capture tomorrow's framework landscape. The tag system is designed to evolve, but transitions may be messy.

---

## Appendix A: Inspiration Sources

| Source | What We Learned |
|--------|----------------|
| **TPC** (36-year standard) | Mandatory price/performance, independent auditors, 60-day challenge period |
| **MLPerf** (ML standard) | Two-tier system (Verified/Open), simultaneous publication, consortium governance |
| **SPEC** (CPU standard) | Competitor consortium, peer-reviewed results, regular evolution |
| **SWE-bench** (coding agents) | Open data + leaderboard = organic adoption; but static tasks saturate |
| **90-agent simulation** | Enforcement > perfection; cost data > quality scores; taxonomy first |

## Appendix B: Frameworks Researched

From analysis of 18 frameworks (Lazy-Fetch research):

Aider, Bolt/Lovable, Claude Agent SDK, Claude Code, Cline/Roo Code, CrewAI, Cursor IDE, Devin/Goose, Karpathy AutoResearch, LangGraph, OpenAI Agents SDK, OpenHands, Paperclip AI, Ralph Loop, Ruvnet Agentic Tools, Shopify Roast, Stripe Minions, SWE-Agent

Key finding: **Simpler frameworks often outperform complex ones.** Mini-swe-agent (~100 LOC) matches SWE-agent's performance. As models improve, simpler scaffolding wins.

## Appendix C: Adversarial Review Changes (v1 → v2)

12 problems identified by stress-testing the PRD against 18 real frameworks. See `ADVERSARIAL-REVIEW.md` for full analysis.

| # | v1 Problem | v2 Fix |
|---|-----------|--------|
| 1 | Adapter interface only works for libraries | Three-tier adapter system (shell/structured/API) + recorded runs |
| 2 | "Framework" too narrow a category | Tag-based taxonomy, evolves organically |
| 3 | Adapter quality varies, biases results | Reference adapters maintained by BattleChallenge team |
| 4 | Model variable not controlled | Two views: Best Performance + Controlled Model |
| 5 | Non-determinism hard to handle | 5 runs, median+IQR, "no significant difference" when CIs overlap |
| 6 | Task format assumes code generation | Outcome-based testing (HTTP, Playwright, CLI assertions) |
| 7 | Categories will be obsolete in 2 years | Tags replace categories |
| 8 | AGI-level agents break the model | Meta-metrics (cost, speed, reliability, autonomy, correctness) survive paradigm shifts |
| 9 | Composite scores mislead | Multi-dimensional profiles + user-configurable weights |
| 10 | "Code quality" is subjective | Outcome-based quality (mutation testing, coverage, human review) |
| 11 | 80% of users won't install CLI | Website is primary product; `npx` quick-start for zero-install |
| 12 | Adapter too hard for small teams | Shell script adapter: 30 minutes to implement |
