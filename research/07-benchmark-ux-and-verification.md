# Benchmark UX, Verification, and User Journeys

## User Journeys by Persona

### Individual Developer ("Tool Chooser") — 80% of users
- **Discovery**: Blog posts, Twitter/X, Hacker News — rarely seeks benchmarks proactively
- **Evaluation**: Scans leaderboard for top-5, rarely reads methodology
- **Trust calibration**: Cross-references multiple sources; divergent rankings = trust drops
- **Decision**: Benchmark = one signal among many (price, experience, community)
- **Almost never runs benchmarks themselves** — SWE-bench requires x86_64, 120GB+ storage, 16GB RAM, Docker

### AI Researcher / Tool Builder ("Submitter")
- **Runs benchmarks themselves** using CLI tools
- **Submits results** via PRs or formal processes
- **Treats benchmarks as marketing** — Meta tested 27 private Llama-4 variants on Chatbot Arena before public release, selectively disclosing favorable results

### Enterprise Technical Evaluator ("Procurement Analyst")
- **Uses benchmarks for shortlisting**, not sole decisions
- **Demands full disclosure reports** (TPC requires complete system config, pricing, auditor attestation)
- **May commission custom benchmarks** — SPEC sells licenses for running on own hardware
- **Price/performance ratios matter more than raw scores**

### CIO / Budget Authority
- Never interacts directly
- Consumes through analyst reports and procurement summaries
- Looks for "certified" / "verified" labels as trust shortcuts

## Verification Models Ranked

| Model | Example | Trust Level |
|-------|---------|-------------|
| Independent audit | TPC certified auditors | Highest |
| Peer review | MLPerf review committees + COI rules | High |
| Human curation | SWE-bench Verified (500 curated tasks) | Medium-High |
| Open reproduction | HuggingFace (public Parquet datasets) | Medium |
| Community contribution | Aider (GitHub PRs) | Low-Medium |
| Self-reported | Most AI model announcements | Low |

**Critical finding**: "Leaderboard Illusion" study found selective submissions inflated Chatbot Arena scores by up to 100 points. Even popular leaderboards can be gamed without robust verification.

## Certification Programs

### TPC (Gold Standard)
- Results ONLY published after independent audit
- Full Disclosure Report required
- 60-day challenge period (competitors police each other)
- Pricing mandatory — prevents "benchmark-special" configurations

### MLPerf (Two-Tier)
- **Closed Division**: Apples-to-apples. Reference model required, all scenarios, compliance tests
- **Open Division**: Innovation-friendly. Any model, any scenario, no compliance
- Serves both standardization AND innovation without compromising either

### SPEC (Licensed)
- Benchmarks are licensed software (not free) — creates "skin in the game"
- Only serious evaluators run SPEC → filters out noise

## Distribution Channels

| Channel | Audience | Strength |
|---------|----------|----------|
| Leaderboard website | Broadest — devs, journalists | Quick visual comparison, shareability |
| API / downloadable data | Tool builders, analysts | Custom analysis, CI/CD integration |
| CLI tools | Researchers, vendors | Reproducibility, run-it-yourself |
| Full Disclosure Reports (PDF) | Enterprise procurement | Maximum detail for high-stakes decisions |
| GitHub repos | Contributors, auditors | Transparency, community trust |
| Digital badges | Marketing teams, product pages | Visual trust signal, viral sharing |

**HuggingFace as model for data access**: All leaderboard results stored as public Parquet datasets, loadable via `pandas`, queryable via API — most developer-friendly approach found.

## Key UX Lessons

### 1. Separate "comparable" from "innovative" submissions
MLPerf's Closed/Open division split. Without this → apples-to-oranges → trust erodes.

### 2. Make raw data programmatically accessible
HuggingFace approach: Parquet files, Hub API, public datasets. Leaderboard website alone is insufficient.

### 3. Verification is a spectrum, not binary
Offer tiers: self-reported < community-reviewed < independently audited. Let users filter by verification level.

### 4. Include cost/efficiency metrics
TPC's price/performance ratio makes it useful for procurement. Pure performance leaderboards invite "benchmark-special" configs.

### 5. Design for "run it yourself" even if most won't
Most devs won't run SWE-bench (120GB+ requirement). But the EXISTENCE of a reproducible harness IS a trust signal.

### 6. Prevent gaming through structural design
- Rotating/live test sets (SWE-bench-Live)
- Mandatory full disclosure (TPC)
- Peer review requirements (MLPerf)
- Public challenge periods (TPC's 60 days)

### 7. Governance determines longevity
TechEmpower Framework Benchmarks sunsetting due to centralized governance bottlenecks. Consortium/foundation governance proven more sustainable.

### 8. Serve "glancers" and "deep divers" simultaneously
- Glancers: sortable leaderboard, top-5, trust badges
- Deep divers: methodology docs, raw data, reproducibility instructions, full disclosure
- Both visit same URL; UX must accommodate both

## Sources

- SWE-bench Verified — Epoch AI
- SWE-bench Leaderboards (swebench.com)
- TPC Benchmarks Overview (tpc.org)
- InfoSizing — TPC Certified Auditors
- MLCommons MLPerf Inference Results
- MLPerf Submission Rules (GitHub)
- SPEC — Standard Performance Evaluation Corporation
- OLCF/ORNL — How to Use SPEC for Decision Making
- HPC Wiki — Benchmarking for Procurements
- TechEmpower Framework Benchmarks Sunsetting (GitHub Issue #10932)
- arXiv — The Leaderboard Illusion
- HuggingFace — Accessing Benchmark Leaderboard Data
- Aider LLM Leaderboards (aider.chat)
- METR — AI Impact on Developer Productivity Study
