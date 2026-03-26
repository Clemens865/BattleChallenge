# PRD-Based Evaluation & Framework Comparison Criteria

## PRD-Based Agent Evaluation

### Key Differences from Traditional PRDs
- AI agents need **dependency-ordered, testable phases** rather than holistic human-readable docs
- Vague criteria like "fast" or "intuitive" must be replaced with **quantified thresholds**
  - e.g., ">= 90% accuracy on 10,000 labelled queries, hallucination rate < 2%"
- Sequential phased execution outperforms monolithic documents

### Recommended PRD Structure for Agent Testing
1. Research-before-specification mandates
2. Testable checkpoints between implementation phases
3. Explicit protection of existing functionality
4. Preference for platform-native services

### Evaluation Pattern
1. Give the agent a PRD as input
2. Measure: Does the generated code satisfy each requirement?
3. Grade against automated test suites derived from PRD acceptance criteria
4. Track token cost and time to complete each phase

## Standard Benchmark Criteria

### Task Completion & Correctness
- **SWE-bench**: Real GitHub issues; fix failing tests
- **FeatureBench**: Feature-level coding (11% vs 74% SWE-bench = massive difficulty gap)
- **pass@k**: Probability at least 1 of k solutions passes

### Token Efficiency
- Input vs output token ratio (input dominates due to trajectory snowball)
- Cost = (prompt tokens x cost) + (completion tokens x cost)
- **AgentDiet**: Reduces input tokens by 39.9-59.7%, cost by 21.1-35.9%
- **OPTIMA**: 2.8x performance with <10% token usage

### Code Quality
- CodeBLEU / BLEU similarity scores
- Static analysis (lint, cyclomatic complexity, maintainability)
- Security vulnerability detection

### Behavioral & Operational
- Multi-turn reasoning consistency
- Resilience to unexpected inputs
- Safety and compliance
- Latency and time-to-completion

### Enterprise Dimensions (Often Missing)
- Cost-efficiency measurement
- Safety and compliance
- Live adaptive benchmarks
- Multi-step granular evaluation

## Key Evaluation Harnesses

| Harness | Focus |
|---------|-------|
| **HAL** (Princeton) | Holistic: output, cost, failure modes |
| **VERO** | Reproducible: versioned snapshots, budget-controlled |
| **AstaBench** | Controlled: standardized baseline agents |
| **DPAI Arena** (JetBrains) | Enterprise: multi-track, issue-to-patch, PR review |

## Coding-Specific Agent Categories

### Multi-Agent Orchestration Frameworks
- CrewAI, LangGraph, AutoGen, Mastra, Strands (AWS)

### Coding-Specific Agents
- Claude Code, Cursor, Windsurf, Cline, OpenAI Codex Agent, Gemini Code Assist, GitHub Copilot Agent Mode

### Emerging
- GitAgent ("Docker for AI Agents")

## Sources

- Medium - How to Write PRDs for AI Coding Agents
- Addy Osmani - How to Write a Good Spec for AI Agents
- DataCamp - CrewAI vs LangGraph vs AutoGen
- arxiv - FeatureBench
- arxiv - Beyond Accuracy: Multi-Dimensional Enterprise Framework
- Anthropic - Demystifying Evals for AI Agents
- DX - Measuring AI Code Assistants and Agents
- arxiv - Tokenomics: Quantifying Token Usage in Agentic SE
- arxiv - VERO Evaluation Harness
- arxiv - HAL: Holistic Agent Leaderboard
- Snorkel AI - Agentic Coding Benchmark
