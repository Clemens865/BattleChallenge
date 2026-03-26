# Recent News & Developments (2025-2026)

## Major Framework Launches & Updates

1. **OpenAI Agents SDK** (March 2025) -- Production-grade Swarm replacement. Core abstraction: "handoff" pattern for agent control transfer.
2. **Google ADK** (April 2025, Google Cloud NEXT) -- Open-source, code-first Python. Model-agnostic. v2.0.0a1 released March 2026.
3. **Anthropic Agent SDK** (September 2025) -- Tool-use-first approach. Agents = Claude models with tools, including invoking other agents as tools.
4. **MCP donated to Linux Foundation** (December 2025) -- 150+ supporting organizations. Google's A2A also donated.
5. **Microsoft merges AutoGen -> Microsoft Agent Framework** (late 2025) -- AutoGen in maintenance mode. Unified SDK targeting Q1 2026 GA.
6. **Claude Opus 4.6 takes #1 on SWE-bench** (early 2026) -- 80.9% Verified, but 45.9% on SWE-bench Pro.
7. **LangChain State of Agent Engineering** (2026) -- 32% of practitioners cite quality as top production barrier.

## Published Framework Comparisons

### Orchestration Frameworks
- **LangGraph**: Consensus leader for complex, stateful production workflows (47M+ PyPI downloads)
- **CrewAI**: Excels at rapid role-based prototyping
- **AutoGen**: Maintenance mode, superseded by Microsoft Agent Framework

### Vendor SDKs
- **OpenAI Agents SDK**: Handoff patterns
- **Anthropic Agent SDK**: Tool-use-first, safety-critical applications
- **Google ADK**: Bidirectional audio/video streaming, multi-agent

### Benchmark Reliability
- SWE-bench Verified vs Pro: 80.9% vs 45.9% for same model = contamination signal
- MCPlato deep comparison: Devin vs Manus vs Claude Code (2026)

## Industry Debates

1. **The Reliability Gap**: At 85% per-action accuracy, a 10-step workflow succeeds only ~20% (compounding errors). Fortune, March 2026.
2. **Benchmark Contamination**: Verified vs Pro divergence raises questions about all headline numbers.
3. **Cost at Scale**: Output tokens cost 4-8x input. Uncontrolled loops waste 60-80% of cost. Fixable with caching, routing, batching.
4. **Autonomy vs Supervision**: Harvard Berkman Klein "Towards a Science of AI Agent Reliability" (Feb 2026). Industry shifting to evaluation-driven + human-in-the-loop.
5. **"Overhyped"**: Agents remain "junior staffers who work quickly, confidently and often incorrectly."

## Emerging Patterns

- **Protocol Standardization**: MCP + A2A -> Linux Foundation = convergence on interop
- **Evaluation-Driven Development**: "Can we measure agent quality?" is the new question. 7+ eval platforms emerged in 2026.
- **Model Routing as Default**: Cheap models for simple tasks, capable models for hard tasks = standard
- **Framework Consolidation**: LangGraph (Python), Mastra (TypeScript), vendor SDKs
- **Multi-Benchmark Evaluation**: Single scores losing credibility. Teams demand SWE-bench Pro + GAIA + CUB + domain-specific.
- **Cost as First-Class Metric**: Routinely included alongside accuracy now.

## Sources

- Medium - AI Agent Framework Landscape 2025
- Shakudo - Top 9 AI Agent Frameworks March 2026
- The Conversation - AI Agents Arrived in 2025
- Nextgov - 2026 Year of Agentic AI
- StackOne - 120+ Agentic AI Tools Landscape 2026
- Evidently AI - AI Agent Benchmarks
- O-Mega - 2025-2026 AI Computer-Use Benchmarks Guide
- Simmering.dev - Agent Benchmarks Reliability Gap
- Fortune - AI Agents Capable but Reliability Lagging (March 2026)
- Harvard Berkman Klein - Towards a Science of AI Agent Reliability (Feb 2026)
- LangChain - State of Agent Engineering
- MorphLLM - SWE-Bench Pro
- Simon Willison - SWE-bench February 2026 Update
- MCPlato - Devin vs Manus vs Claude Code Comparison
