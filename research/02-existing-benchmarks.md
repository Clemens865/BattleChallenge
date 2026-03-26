# Existing Benchmarking Systems for AI Agents

## Software Engineering & Coding Benchmarks

### SWE-bench / SWE-bench Verified
- 2,294 real GitHub issues with execution-based testing
- Top score early 2026: ~80.9% (Claude Opus 4.5)
- **Nearing saturation**; OpenAI stopped reporting Verified scores due to training data contamination
- Agent scaffolding matters: same model across 3 frameworks scored 17 issues apart on 731 problems

### SWE-bench Pro
- Harder variant: 1,865 multi-language tasks, less contamination
- 46% beats 81% on Verified — measures real capability gap
- GPT-5.3-Codex scores 57%

### HumanEval / MBPP
- Classic code generation (164/974 Python problems)
- Largely saturated: 96%+ pass@1 on frontier models
- Pro versions test self-invoking code: o1-mini drops from 96.2% to 76.2%

### FeatureBench
- Tests feature-level coding (not just bug-fixing)
- Even top models like Claude 4.5 Opus achieve only 11% — massive difficulty gap

### DPAI Arena (JetBrains)
- Launched October 2025, donated to Linux Foundation
- Multi-track: issue-to-patch, PR review, test coverage generation
- 140+ tasks mirroring enterprise requirements (Spring/Java focus)

### COFFE
- Benchmarks code **efficiency** specifically, not just correctness
- Measures runtime performance and resource usage

## General Agent Benchmarks

### GAIA (General AI Assistants)
- 466 real-world questions requiring reasoning, multimodality, tool use
- Exposes 77% human-AI performance gap
- Top Level 3: 61%; Top overall: ~90% (late 2025)

### AgentBench
- 8 environments: OS, databases, knowledge graphs, card games, puzzles, household, web shopping, web browsing

### WebArena
- 812 long-horizon web tasks
- Agents: ~14% success vs humans: 78%
- Extensions: WebChoreArena, ST-WebAgentBench, VisualWebArena, VideoWebArena

### OSWorld
- 369 computer tasks with real web/desktop apps
- Human: 72.36%, Best agent: 34.5%

## Evaluation Methodologies

### Correctness & Quality
- **Execution-based testing**: Unit/integration tests against output (gold standard)
- **pass@k**: Probability at least 1 of k samples passes
- **LLM-as-judge**: Second LLM grades open-ended outputs
- **CodeBLEU**: Similarity to reference implementations
- **Static analysis**: Lint errors, cyclomatic complexity, maintainability

### Token Efficiency & Cost
- Cost per token (direct pricing)
- Token utilization rate (meaningful content vs waste)
- Cost per business outcome
- Tokens per resolution (end-to-end)
- **AgentDiet**: Reduces input tokens by 39.9-59.7%, cost by 21.1-35.9%
- **OPTIMA**: 2.8x performance gain with <10% token usage

### Production Evaluation (Anthropic's Framework)
- Multi-turn evaluation with tool calls, reasoning, environment updates
- Start with 20-50 tasks from real failures, scale up
- Holistic: monitoring, user feedback, A/B testing, transcript review

## Critical Gaps in Current Benchmarking

1. **Benchmark Saturation & Contamination**: SWE-bench Verified went 30%->80%+ in one year. Training data contamination confirmed.
2. **Lab-to-Production Gap**: AWS research shows 37% performance gap.
3. **Missing Cost-Efficiency Measurement**: Very few jointly measure correctness AND token/cost efficiency.
4. **No Head-to-Head Framework Battles**: No standardized system for pitting entire agentic systems against each other. DPAI Arena closest but limited.
5. **Enterprise Requirements Ignored**: Missing multistep evaluation, cost-efficiency, safety, live adaptive benchmarks.
6. **No Multi-Dimensional Scoring**: Most produce single accuracy number. Missing combined correctness + efficiency + latency + safety + quality.
7. **Gamability**: Models exploit spurious correlations. Few anti-gaming mechanisms.
8. **No Longitudinal/Adaptive Benchmarks**: All static snapshots. No fresh, uncontaminated task generation.

## Sources

- o-mega.ai - Best AI Agent Evaluation Benchmarks 2025
- o-mega.ai - 2025-2026 AI Computer-Use Benchmarks Guide
- evidentlyai.com - 10 AI Agent Benchmarks
- GitHub philschmid - AI Agent Benchmark Compendium
- vals.ai - SWE-bench
- swebench.com - Leaderboards
- morphllm.com - SWE-Bench Pro
- simmering.dev - The Reliability Gap
- arxiv - Beyond Accuracy: Multi-Dimensional Framework
- arxiv - Benchmark Saturation Study
- Anthropic - Demystifying Evals for AI Agents
- JetBrains - DPAI Arena
- arxiv - OPTIMA
- arxiv - COFFE
- arxiv - TokenPowerBench
