# BattleChallenge

> The open-source benchmarking system that compares agentic AI frameworks head-to-head on standardized tasks.

**Give every framework the same tasks. Measure everything. Publish everything. Let the data speak.**

## Quick Start

```bash
# Install
npm install -g battlechallenge

# Compare two frameworks instantly
npx battlechallenge quick claude-code aider

# Run full benchmark
battle run --framework ./adapters/claude-code --runs 5

# View results
battle results

# Compare head-to-head
battle compare claude-code aider

# Export data
battle export --format csv --output results.csv
```

## What This Is

There is no standardized way to compare agentic AI frameworks. Developers choosing between LangGraph, CrewAI, Claude Code, Aider, or OpenAI Agents SDK have no objective data. BattleChallenge fixes this.

## Five Meta-Metrics (No Composite Scores)

Every framework gets a multi-dimensional profile, not a single ranking number:

| Metric | What It Measures |
|--------|-----------------|
| **Correctness** | Does the outcome work? (automated tests) |
| **Cost** | How much does it cost? (token proxy) |
| **Speed** | How fast? (wall-clock time) |
| **Reliability** | How consistent? (% across N runs) |
| **Autonomy** | How much human help needed? |

## Adapters

Adapters connect frameworks to BattleChallenge. Three tiers:

```bash
# Tier 1: Shell script (30 min to implement)
battle adapter init --framework my-framework --tier shell

# Tier 2: Structured (half day)
battle adapter init --framework my-framework --tier structured

# Tier 3: API (for cloud services)
battle adapter init --framework my-framework --tier api
```

## Tasks

```bash
# List available tasks
battle task list

# Create a new task
battle task init --id task-042-my-task --type coding --tier T2

# Validate
battle task validate --path ./tasks/task-042-my-task
```

## Statistical Rigor

- Minimum 5 runs per task per framework
- Median + IQR (not mean)
- High variance flagged when IQR > 20% of median
- Rankings only when confidence intervals don't overlap
- Raw data published

## Tag-Based Taxonomy

No rigid categories. Frameworks declare tags:

```yaml
tags: [coding-agent, cli, model-agnostic, python]
```

Default leaderboard views: Orchestration, Coding Agents, IDE Tools, All.

## Two Tracks

- **Verified**: Reference adapter, all tasks, compliance checks, peer-reviewed
- **Open**: Custom adapters, any task subset, no restrictions

## Project Structure

```
src/
  cli/          # Command-line interface
  runner/       # Docker-based benchmark executor
  scorer/       # 5-metric scoring engine + statistics
  api/          # REST API server
  db/           # SQLite storage
  adapters/     # Adapter loader
  tasks/        # Task loader
  taxonomy/     # Tag-based framework classification
  badges/       # SVG badge generation
  quiz/         # "Find My Framework" recommendation
  submission/   # Verified/Open track validation
  governance/   # Advisory board & disputes
  anti-gaming/  # Cheating detection
  website/      # Static site generator
tasks/          # Benchmark task bank
adapters/       # Reference adapter configs
```

## License

MIT
