# Framework Orchestration Deep Dive: What Actually Differentiates Agentic Frameworks

> Research Date: 2026-03-26
> Purpose: Identify framework-level capabilities (not model-level) to design benchmark challenges where orchestration strategy is the differentiator.

---

## Part 1: Framework-by-Framework Analysis

### 1. Claude Code (Raw)

**What it does beyond sending prompts:**

- **Tool use system**: File read/write, bash execution, glob/grep search, web fetch — all as structured tool calls with approval gates. The agent decides which tools to invoke based on task context.
- **Context window management**: Auto-compaction via `/compact` when approaching limits. Output quality degrades at ~60% context utilization (empirically measured across 50 sessions). Context-aware models (Sonnet 4.6, Opus 4.6) track their remaining token budget in real-time.
- **CLAUDE.md injection**: Project-level instructions loaded every session (~50-200 lines). Acts as persistent memory across sessions. Path-scoped rules load context only when relevant files are touched.
- **Subagent isolation**: Spawns child agents with separate context windows and tool permissions. This is divide-and-conquer for context management — critical for large tasks that would overflow a single window.
- **Hooks system**: Deterministic shell scripts triggered on 17 lifecycle events (pre-edit, post-command, etc.). Unlike LLM-driven decisions, these fire reliably every time.
- **MCP integration**: Open protocol connecting to external tools (Jira, Slack, databases) via JSON-RPC 2.0. Extends tool surface beyond local filesystem.
- **Auto mode (March 2026)**: Delegates permission decisions to the AI itself, with a safety classifier checking for dangerous patterns (mass deletion, data exfiltration).
- **Git integration**: Automatic commit creation, branch management, diff analysis.

**Unique framework-level capability**: Subagent context isolation + path-scoped rules. No other CLI agent has this level of context engineering infrastructure. The combination of deterministic hooks + LLM-driven tool selection creates a hybrid control model.

**Measured impact**: Augment, Cursor, and Claude Code all ran Opus 4.5 but scored 17 problems apart on 731 SWE-bench issues (80.9% vs 63.9%). Same model, different scaffolding.

---

### 2. Lazy-Fetch / Blueprint Systems

**What structured workflows buy you:**

- **Context gathering before action**: `lazy gather <task>` finds relevant files and symbols before the agent starts coding. This front-loads the right context instead of letting the agent discover it mid-task (and potentially overflow or miss files).
- **Checkpoint-based workflows**: Blueprints enforce a deterministic sequence: gather context → git checkpoint → implement → validate (typecheck + tests) → remember. Validation gates retry on failure.
- **Persistent memory**: `lazy remember` stores decisions/facts that survive across sessions. `lazy recall` retrieves them. This solves the "amnesia problem" where agents lose architectural decisions between sessions.
- **Plan decomposition**: `lazy plan <goal>` breaks goals into phased tasks. `lazy status` tracks progress. This prevents the common failure mode of agents losing track of multi-step work.
- **Blueprint templates**: Pre-built workflows for common patterns (fix-bug, add-feature, experiment, review-code). Each blueprint knows the right sequence of gather/implement/validate steps for its category.

**Unique framework-level capability**: The enforcement of validation gates. A blueprint will not advance past implementation until typecheck + tests pass. This catches errors that a single-shot agent would ship. The gather-before-implement pattern also ensures context is curated before the agent starts, rather than discovered ad-hoc.

**When it matters**: On multi-step tasks where the agent needs to maintain coherence across steps. On tasks where the first implementation attempt is likely wrong and needs iteration. On projects where decisions from previous sessions matter.

---

### 3. Aider

**What's unique at the framework level:**

- **Repository map via tree-sitter + PageRank**: Parses the entire repo into an AST using tree-sitter (130+ languages). Builds a dependency graph where files are nodes and edges represent cross-file references. Ranks symbols using PageRank — a function called by 20 other files ranks higher than a private helper. Binary-search algorithm selects the most important symbols that fit in the token budget.
- **Edit format system**: Multiple edit formats (whole-file, search/replace, unified diff) matched to model capabilities. Unified diff format raised GPT-4 Turbo's score from 20% to 61% and reduced "lazy coding" (placeholder comments) by 3x. The format itself changes model behavior.
- **Git-first philosophy**: Every AI edit becomes an automatic git commit with a descriptive message. Every session can run on its own branch. Git history becomes a complete audit trail. This is not a feature — it's the foundation. Rollback is always one `git revert` away.
- **Linting loop**: When an edit is applied, Aider runs a linter. If the linter fails, it feeds the errors back to the model for correction. This creates a tight verify-fix loop that catches syntax errors before they propagate.
- **Architect mode**: `/mode architect` separates planning from implementation. The model discusses structure, design patterns, and system architecture before making changes. This prevents the "dive in and code" failure mode.
- **Multi-model support**: Works with 100+ models. Can assign different models to architect vs. coder roles (e.g., expensive model for planning, cheap model for execution).

**Unique framework-level capability**: The repo map is Aider's signature innovation. No other tool uses PageRank over an AST dependency graph to select context. This means Aider can work in large repos without reading everything — it knows which files are structurally important. The edit format system is also unique: the choice of how edits are represented to the model measurably changes output quality.

**Measured impact**: 39K+ GitHub stars, 4.1M+ installations. Aider's benchmark shows 52.7% combined score with 257 seconds average and 126K tokens per task — the most balanced efficiency profile among CLI tools.

---

### 4. Ralph Loop

**What iterative looping does that single-shot doesn't:**

- **Core pattern**: Run the same prompt against the codebase in a loop. The agent sees its own previous output, identifies failures via test execution, and iterates. Loop continues until all tests pass or a max iteration count is hit.
- **Verify-then-iterate**: Unlike single-shot (generate once, hope it works), Ralph forces the agent to prove correctness through test execution. If tests fail, the agent sees the failure output and tries again with that knowledge.
- **No framework — just a pattern**: Ralph is not a product. It's a shell loop: `while tests fail; do run agent; done`. The "framework" is the iteration strategy itself.

**What it buys you**:
- Bugfixes with reproducible test cases: high success rate because the loop converges
- Framework migrations with well-defined target states: measurable progress per iteration
- Test coverage expansion: each iteration adds tests that pass
- Greenfield projects backed by detailed specs: converges when spec is clear

**What it costs**:
- 50-iteration loop on a medium codebase: $50-100+ in API credits
- Code quality degrades: architecture reflects the path to solution, not intentional design
- No structural coherence: Ralph-generated codebases run but lack maintainability

**Unique framework-level capability**: The loop itself. Single-shot agents succeed or fail on attempt one. Ralph converts any agent into a self-correcting system by running it repeatedly with test feedback. This is the simplest possible "framework" — and it works for any underlying tool.

**When it matters**: When the task has a clear, executable definition of "done" (test suite passes). When the first attempt is expected to fail. When cost is less important than completion.

---

### 5. LangGraph

**When graph orchestration matters:**

- **State machines with typed state**: Explicit, reducer-driven state schemas using TypedDict. State transitions are defined as graph edges. Each node is a computation step. This is not prompt chaining — it's a formal state machine with typed state, defined transitions, and reducer functions that prevent data loss.
- **Checkpointing**: Saves state at every node execution. If the process crashes at step 7 of 10, it resumes from step 7, not step 1. Conceptually similar to BizTalk's dehydration/rehydration. This matters for long-running workflows (hours/days).
- **Human-in-the-loop**: Runtime pauses execution, saves state, waits for human input (seconds or hours), then resumes from the exact pause point. No thread blocking. This enables workflows requiring human judgment (QA, compliance, decision-making).
- **Branching and looping**: Supports conditional branching, parallel execution, and loops within the graph. A node can route to different downstream nodes based on state.
- **Time-travel debugging**: Because every state transition is checkpointed, you can replay the workflow from any point. This enables debugging complex multi-step failures.
- **LangGraph 1.0 (October 2025)**: Production-ready with durable execution, streaming, human oversight, and memory management.

**Unique framework-level capability**: Formalized state machines with checkpointing + human-in-the-loop. No other framework provides this combination. LangGraph is the only framework where you can pause a workflow for human review, resume hours later, and replay from any checkpoint. This is infrastructure for complex, long-running, compliance-sensitive workflows.

**When it matters**: When workflows take hours/days and must survive crashes. When human approval is required at specific steps. When you need to audit exactly what happened at each step. When branching logic is complex (if X then do A, else do B, then merge results).

**Measured impact**: LangGraph finished 2.2x faster than CrewAI on identical five-agent travel-planning benchmarks. LangChain and AutoGen showed 8-9x differences in token efficiency on the same task.

---

### 6. CrewAI

**When specialized multi-agent roles help:**

- **Role-based agent assignment**: Each agent gets a role (Manager, Worker, Researcher), a goal, a backstory, and scoped tools. The Manager coordinates, Workers execute, Researchers gather information. This mimics organizational structure.
- **Process types**: Sequential (A then B then C), Hierarchical (Manager delegates to Workers, validates results), and Hybrid. The hierarchical process auto-assigns a manager agent that handles delegation and result validation.
- **LLM-agnostic per-agent**: Different agents can use different models. Assign expensive models to complex reasoning tasks and cheap models to simple execution. This optimizes cost without sacrificing quality where it matters.
- **CrewAI Flows (2025)**: Enterprise architecture for event-driven orchestration. Enables granular control over agent coordination, supports Crews natively.
- **Tool scoping**: Tools are scoped per task, not per agent. A researcher agent gets search tools; a coder agent gets file tools. This prevents agents from using inappropriate tools.

**Unique framework-level capability**: Role-based decomposition with per-agent model assignment. CrewAI is the fastest path from "we need an agent for this" to "it's running in production" (reportedly possible in one week). The organizational metaphor (manager/worker) is intuitive for non-technical stakeholders.

**When it matters**: When tasks naturally decompose into specialized roles (research, implement, review). When different subtasks need different models (cost optimization). When you need rapid prototyping of multi-agent systems.

**Critical caveat**: Empirical research shows multi-agent systems do NOT consistently outperform single agents. The 45% accuracy threshold finding: once a single-agent baseline exceeds ~45% accuracy, adding more agents yields diminishing or negative returns. In "independent" multi-agent systems without communication, errors were amplified 17.2x vs single-agent baseline. CrewAI's hierarchical process mitigates this by having the Manager validate results, but the coordination overhead is real.

---

### 7. OpenAI Agents SDK / Anthropic Agent SDK

**Tool orchestration and handoffs:**

- **OpenAI Agents SDK (March 2025)**: Lightweight Python framework with three primitives: Agents (LLM + instructions + tools), Handoffs (agent-to-agent delegation carrying conversation context), and Guardrails (input/output validation).
- **Built-in agent loop**: Handles tool invocation, sends results back to LLM, continues until task complete. No manual loop management needed.
- **Handoffs as tools**: A handoff is implemented as a tool/function call. Agent A can "call" Agent B, transferring full conversation context. This enables dynamic routing — a triage agent routes to specialist agents based on input.
- **Built-in tracing**: Visualize and debug agentic flows. Trace every tool call, handoff, and guardrail check.
- **MCP integration (Anthropic)**: MCP has crossed 97M monthly SDK downloads. OpenAI adopted MCP in March 2025. Google confirmed MCP support in April 2025. By December 2025, Anthropic donated MCP to the Linux Foundation. MCP exposes four capability types: Resources, Tools, Prompts, and Sampling.
- **Agent Skills (Anthropic, October 2025)**: Teachable, repeatable workflows for Claude. Now an open standard.

**Unique framework-level capability**: Handoffs with context propagation. The OpenAI SDK's handoff primitive is unique — it allows one agent to transfer control to another while carrying the full conversation context. This enables dynamic multi-agent routing without a centralized orchestrator. The Anthropic SDK's MCP ecosystem is unique in that it's become the de facto standard for tool integration across all major providers.

**When it matters**: When you need dynamic agent routing (not predetermined workflows). When you need guardrails for safety-critical applications. When you need interoperability across different LLM providers (MCP).

---

### 8. SWE-Agent

**Custom interfaces and navigation tools:**

- **Agent-Computer Interface (ACI)**: Purpose-built interface replacing standard shell/editor interactions. The key insight: conventional user-facing interfaces (shells, editors) are mismatched with LLM capabilities. SWE-Agent provides a custom interface optimized for how LLMs process information.
- **Custom file viewer**: Displays 100 lines per turn (empirically determined optimal). Standard `cat` dumps entire files, overwhelming the model. The viewer provides pagination and focused context.
- **Search/navigation commands**: `findfile`, `searchfile`, `searchdir` provide summary results to locate content without overwhelming with data. This replaces the brute-force approach of reading entire directories.
- **Linting gate on edits**: The linter runs on every edit command. Syntactically incorrect edits are rejected before being applied. The agent must fix syntax errors before proceeding. This prevents error propagation.
- **Docker isolation**: Each environment runs in an isolated container (local, Modal, or AWS). SWE-ReX manages shell sessions within the container.

**Unique framework-level capability**: The ACI itself. SWE-Agent proved that the interface between the LLM and the computer matters as much as the model. By replacing standard tools (cat, vim, grep) with LLM-optimized equivalents, SWE-Agent achieved 3-5x improvement over RAG baselines (12.47% vs 3.8% pass@1 on GPT-4 Turbo).

**When it matters**: When the task requires navigating large, unfamiliar codebases. When edit precision matters (the linting gate prevents syntactically broken edits). When the agent needs to search and explore rather than operate on pre-selected files.

---

### 9. OpenHands / Devin

**Full environment control:**

- **Sandboxed workspace**: Filesystem + terminal + web browser in an isolated container. The agent can observe program output, run tests, and browse documentation.
- **Browser-based IDE (VSCode)**: Built-in visual code editing, not just file writes.
- **VNC desktop**: Full graphical desktop access for GUI interactions.
- **Persistent Chromium browser**: Can browse the web, read documentation, interact with web UIs.
- **Event-sourced state model**: Deterministic replay of all agent actions. Every action is logged as an event; the full trajectory can be replayed.
- **V1 SDK (modular)**: Refactored from monolithic V0. Clear boundaries between agent, tool, and workspace packages. Opt-in sandboxing. Same agent runs locally or remotely with minimal code changes.
- **MCP integration**: Typed tool system connecting to external services.

**Unique framework-level capability**: Full environment control — browser + terminal + editor + desktop in a single sandboxed container. No other framework provides browser access alongside code editing. This enables tasks that require reading web documentation, interacting with web UIs, or testing web applications as part of the coding workflow.

**When it matters**: When the task requires web browsing (reading docs, checking APIs, testing web apps). When full isolation is needed (production-like environments). When the agent needs to install packages, configure environments, and run end-to-end tests.

**Measured impact**: OpenHands raised $18.8M, claims 87% of bug tickets resolved same day. Devin achieves 67% PR merge rate on well-defined tasks but fails ~85% on complex work.

---

## Part 2: The Evidence — Framework Architecture Matters

### Hard Data Points

| Finding | Source | Implication |
|---------|--------|-------------|
| Same model (Opus 4.5), three frameworks scored 17 problems apart on 731 SWE-bench issues | Morph LLM 2026 test | Scaffolding causes 2-4% absolute performance swings even with identical models |
| Single-agent systems consistently outperformed multi-agent systems across 3 tasks on same model (DeepSeek-v3.1) | arXiv 2511.00872 | More agents != better. Coordination overhead can hurt. |
| AgentOrchestra spent $292.01 vs GPTswarm $13.49 on same software development task | arXiv 2511.00872 | 21.6x cost difference for same task, same model |
| Planning agent consumed 67.2% of tokens in multi-agent systems | arXiv 2511.00872 | Orchestration overhead is real and measurable |
| LangGraph 2.2x faster than CrewAI on identical five-agent task | Latenode benchmark | Graph orchestration is faster than role-based for structured workflows |
| Unified diff edit format raised GPT-4 Turbo from 20% to 61% | Aider benchmark | How you represent edits to the model changes output quality by 3x |
| SWE-Agent ACI achieved 3-5x improvement over RAG baselines | arXiv 2405.15793 | Custom LLM-optimized interfaces dramatically outperform standard tools |
| Claude 4.5 Opus: 74.4% on SWE-bench but only 11.0% on FeatureBench | FeatureBench ICLR 2026 | Complex feature development is 6-7x harder than bug fixing — framework strategy matters more |
| Output quality degrades at ~60% context utilization | Blake Crosley 50-session study | Context management is a real engineering problem, not just a limit |
| Errors amplified 17.2x in independent multi-agent systems vs single-agent | VentureBeat / research | Uncoordinated agents multiply errors instead of fixing them |

---

## Part 3: Capability Taxonomy

| Capability | Claude Code | Aider | LangGraph | CrewAI | SWE-Agent | OpenHands | OpenAI SDK | Ralph Loop |
|------------|:-----------:|:-----:|:---------:|:------:|:---------:|:---------:|:----------:|:----------:|
| Repo-wide context selection | Subagents + glob | PageRank repo map | Manual state | Per-agent scope | ACI search tools | Full filesystem | Manual | None |
| Edit verification | None built-in | Lint loop | N/A | N/A | Lint gate | Test execution | Guardrails | Test loop |
| Error recovery | Retry via hooks | Lint + retry | Checkpoint resume | Manager validation | Lint rejection | Event replay | Handoff to specialist | Full re-run |
| State persistence | CLAUDE.md + memory | Git commits | Checkpointer | N/A | N/A | Event store | Tracing | None |
| Human-in-the-loop | Approval gates | Git review | Formal pause/resume | N/A | N/A | VNC/IDE | Guardrails | None |
| Multi-step coordination | Subagents | Architect mode | Graph edges | Process types | N/A | Orchestrator | Handoffs | Loop iterations |
| Cost optimization | Subagent model choice | Multi-model | N/A | Per-agent models | N/A | Model-agnostic | Provider-agnostic | N/A (expensive) |
| Browser access | No | No | No | No | No | Yes | No | No |
| Parallel execution | Subagents | No | Graph branches | Hierarchical | No | Multiple agents | Handoffs | No |

