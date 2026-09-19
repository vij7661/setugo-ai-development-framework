# Ruflo R2 Source Appendix A

Exact source excerpts/full files used by the R2 selective-adoption review.

These sources are contextual evidence only. Ruflo-declared status does not confer authority in this project.


---

# SOURCE: AGENTS.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `68590f47c3a5cd47a0599548bf16ac7e4d0655b9`

# Claude Flow V3 - Agent Guide

> **For OpenAI Codex CLI** - Agentic AI Foundation standard
> Skills: `$skill-name` | Config: `.agents/config.toml`

---

## 📢 TL;DR - READ THIS FIRST

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  1. claude-flow = LEDGER (tracks state, stores memory, coordinates)       ║
║  2. Codex = EXECUTOR (writes code, runs commands, creates files)          ║
║  3. NEVER stop after calling claude-flow - IMMEDIATELY continue working   ║
║  4. If you need something BUILT/EXECUTED, YOU do it, not claude-flow      ║
║  5. ALWAYS search memory BEFORE starting: memory search --query "task"    ║
║  6. ALWAYS store patterns AFTER success: memory store --namespace patterns║
╚═══════════════════════════════════════════════════════════════════════════╝
```

**Workflow (Use MCP Tools):**
1. `memory_search(query="task keywords")` → LEARN from past patterns (score > 0.7 = use it)
2. `swarm_init(topology="hierarchical")` → coordination record (instant)
3. **YOU write the code / run the commands** ← THIS IS WHERE WORK HAPPENS
4. `memory_store(key="pattern-x", value="what worked", namespace="patterns")` → REMEMBER for next time

---

## Ruflo Policy-Governed Concurrent Codex Workflow

Ruflo is the coordination ledger and policy decision point. Codex agents are
the executors. Coordination records do not write code or run tests.

Use `guidance_brain({ mode: "recommend", task: "..." })` to select Ruflo
capabilities from the live MCP registry. A registered tool is not necessarily
configured, reachable, healthy, or authorized. If it is unavailable, continue
with compatible guidance tools, CLI discovery, and repository instructions.

1. Recall relevant AgentDB memory and ADRs.
2. Inspect source, runtime, dependencies, policy, and health.
3. Route to the smallest capable topology, agents, skills, and tools.
4. Plan acceptance criteria, safety envelope, ownership, and validation.
5. Execute with Codex workers in isolated scopes; Ruflo records coordination.
6. Test focused, regression, and failure paths.
7. Validate types, security, policy, compatibility, and artifact integrity.
8. Benchmark a source-bound candidate against a source-bound baseline.
9. Optimize only measured bottlenecks without weakening safety.
10. Bind claims and evidence into exact source/build receipts.
11. Reconcile handoffs and disclose unresolved limitations.
12. Publish only through a separately authorized release gate.

Hard invariants:

- Never run two writers in one worktree.
- Delegation may only reduce tools, servers, namespaces, network, spend,
  concurrency, expiry, and depth.
- Policy denial cancels dependent work before side effects.
- MetaHarness may evaluate candidates concurrently, but only ADR-322A may
  promote them and MetaHarness may never expand its own SafetyEnvelope.
- Do not commit, push, merge, release, or remove worktrees unless authorized.
- Existing installations migrate in `legacy` policy mode; use `observe` before
  switching to `enforce`.

Repository harness integration:

- If tracked repository instructions define a collaboration harness, start its
  session only after assigning an isolated worktree.
- Inspect existing claims, acquire exact paths/resources/ports, renew leases,
  check acknowledged inbox messages at integration boundaries, and release ownership on
  handoff or exit.
- A repository lease coordinates ownership; it does not grant authorization.
  Protected work still requires the ADR-324/325 action capability and current
  fencing epoch.
- In-memory reference adapters demonstrate semantics; they are not distributed,
  restart-durable release authorities.
- Heartbeats and lease expiry establish liveness; a PID is diagnostic only.
- `HEAD` alone is not an exact source-state identity in a dirty worktree.
  Release evidence must bind a clean commit or an immutable snapshot of tracked
  and untracked changes.

Useful checks:

```bash
npx ruflo policy status
npx ruflo policy verify
npx ruflo metaharness flywheel status
```

Repository release contract:

- The stable public train is exactly `@claude-flow/cli`, `claude-flow`, and
  `ruflo`; internal `@claude-flow/*` components are bundled and are not part of
  a normal standalone publish.
- Publish from a clean, reviewed source state in that order.
- Only the CLI publish receives the helper-signing configuration from
  `ruv-dev`; use the existing authenticated npm session for publication.
- Run `node scripts/audit-umbrella-version-lockstep.mjs`, verify all three
  registry versions, and align `latest`, `alpha`, and `v3alpha`.

---

## 🚨 CRITICAL: CODEX DOES THE WORK, CLAUDE-FLOW ORCHESTRATES

```
┌─────────────────────────────────────────────────────────────┐
│  CLAUDE-FLOW = ORCHESTRATOR (tracks state, coordinates)     │
│  CODEX = WORKER (writes code, runs commands, implements)    │
└─────────────────────────────────────────────────────────────┘
```

### ❌ WRONG: Expecting claude-flow to execute tasks
```bash
npx claude-flow swarm start --objective "Build API"
# WRONG: Waiting for claude-flow to build the API
# Claude-flow does NOT execute code!
```

### ✅ CORRECT: Codex executes, claude-flow tracks
```bash
# 1. Tell claude-flow what you're doing (optional coordination)
npx claude-flow swarm init --topology hierarchical --max-agents 1
npx claude-flow agent spawn --type coder --name codex-worker

# 2. YOU (CODEX) DO THE ACTUAL WORK:
mkdir -p src
cat > src/api.ts << 'EOF'
export function hello() { return "Hello World"; }
EOF

# 3. Report to claude-flow what you did (optional)
npx claude-flow memory store --key "api-created" --value "src/api.ts" --namespace results
```

### The Division of Labor

| Component | Role | Examples |
|-----------|------|----------|
| **CODEX** | EXECUTES | Write files, run tests, create code, shell commands |
| **claude-flow** | ORCHESTRATES | Track agents, store memory, coordinate tasks |

---

## ⛔ DON'T STOP AFTER CALLING CLAUDE-FLOW

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ❌ WRONG: Call claude-flow → STOP → Wait for results                   │
│  ✅ RIGHT: Call claude-flow → IMMEDIATELY continue → YOU do the work    │
└─────────────────────────────────────────────────────────────────────────┘
```

### ❌ WRONG Pattern (Stopping)
```bash
npx claude-flow swarm init --topology hierarchical
npx claude-flow agent spawn --type coder --name worker-1
npx claude-flow swarm start --objective "Build hello world"
# WRONG: Codex stops here and waits for something to happen
# Nothing will happen! Claude-flow doesn't execute code!
```

### ✅ CORRECT Pattern (Continue Immediately)
```bash
# Step 1: Coordination (optional)
npx claude-flow swarm init --topology hierarchical
npx claude-flow agent spawn --type coder --name worker-1

# Step 2: IMMEDIATELY DO THE WORK YOURSELF - DON'T WAIT!
echo 'console.log("Hello World!");' > hello.js
node hello.js

# Step 3: Report what you did
npx claude-flow memory store --key "result" --value "Hello World printed" --namespace results
```

### The Rule
**After ANY claude-flow command, IMMEDIATELY continue with your own work.**

Claude-flow commands return instantly. They create coordination RECORDS only.
You must ALWAYS follow up with YOUR OWN execution.

| After This... | IMMEDIATELY Do This... |
|---------------|----------------------|
| `swarm init` | Start writing code |
| `agent spawn` | Continue implementation |
| `task create` | Execute the task yourself |
| `swarm start` | Begin actual work |

---

### When to Use Claude-Flow Commands

| Use Case | Claude-Flow Command | Then Codex Does |
|----------|---------------------|-----------------|
| Track progress | `memory store --key "step1" --value "done"` | Continue to next step |
| Multi-step tasks | `task create --description "step 2"` | Execute step 2 |
| Store results | `memory store --key "output" --value "..."` | Move on |
| Coordinate | `swarm init` | Start working |

### Hello World - Correct Pattern

```bash
# STEP 1: Optional - register with orchestrator
npx claude-flow swarm init --topology mesh --max-agents 1

# STEP 2: CODEX DOES THE WORK
echo 'console.log("Hello World!");' > hello.js
node hello.js

# STEP 3: Optional - report completion
npx claude-flow memory store --key "hello-result" --value "printed Hello World" --namespace results
```

**REMEMBER: If you need something DONE, YOU do it. Claude-flow just tracks.**

---

## ⚡ QUICK COMMANDS (NO DISCOVERY NEEDED)

### Spawn N-Agent Swarm (Copy-Paste Ready)

```bash
# 5-AGENT SWARM - Run these commands in sequence:
npx claude-flow swarm init --topology hierarchical --max-agents 8
npx claude-flow agent spawn --type coordinator --name coord-1
npx claude-flow agent spawn --type coder --name coder-1
npx claude-flow agent spawn --type coder --name coder-2
npx claude-flow agent spawn --type tester --name tester-1
npx claude-flow agent spawn --type reviewer --name reviewer-1
npx claude-flow swarm start --objective "Your task here" --strategy development
```

### Common Swarm Patterns

| Task | Exact Command |
|------|---------------|
| Init hierarchical swarm | `npx claude-flow swarm init --topology hierarchical --max-agents 8` |
| Init mesh swarm | `npx claude-flow swarm init --topology mesh --max-agents 5` |
| Init V3 mode (15 agents) | `npx claude-flow swarm init --v3-mode` |
| Spawn coder | `npx claude-flow agent spawn --type coder --name coder-1` |
| Spawn tester | `npx claude-flow agent spawn --type tester --name tester-1` |
| Spawn coordinator | `npx claude-flow agent spawn --type coordinator --name coord-1` |
| Spawn architect | `npx claude-flow agent spawn --type architect --name arch-1` |
| Spawn reviewer | `npx claude-flow agent spawn --type reviewer --name rev-1` |
| Spawn researcher | `npx claude-flow agent spawn --type researcher --name res-1` |
| Start swarm | `npx claude-flow swarm start --objective "task" --strategy development` |
| Check swarm status | `npx claude-flow swarm status` |
| List agents | `npx claude-flow agent list` |
| Stop swarm | `npx claude-flow swarm stop` |

### Agent Types (Use with `--type`)

| Type | Purpose |
|------|---------|
| `coordinator` | Orchestrates other agents |
| `coder` | Writes code |
| `tester` | Writes tests |
| `reviewer` | Reviews code |
| `architect` | Designs systems |
| `researcher` | Analyzes requirements |
| `security-architect` | Security design |
| `performance-engineer` | Optimization |

### Task Commands

| Action | Command |
|--------|---------|
| Create task | `npx claude-flow task create --type implementation --description "desc"` |
| List tasks | `npx claude-flow task list` |
| Assign task | `npx claude-flow task assign TASK_ID --agent AGENT_NAME` |
| Task status | `npx claude-flow task status TASK_ID` |
| Cancel task | `npx claude-flow task cancel TASK_ID` |

### Memory Commands

| Action | Command |
|--------|---------|
| Store | `npx claude-flow memory store --key "key" --value "value" --namespace patterns` |
| Search | `npx claude-flow memory search --query "search terms"` |
| List | `npx claude-flow memory list --namespace patterns` |
| Retrieve | `npx claude-flow memory retrieve --key "key"` |

---

## 🚀 SWARM RECIPES

### Recipe 1: Hello World Test (COMPLETE EXAMPLE)

**Step 1: Setup coordination** (returns instantly - don't stop!)
```bash
npx claude-flow swarm init --topology mesh --max-agents 5
npx claude-flow agent spawn --type coder --name hello-main
# ⚠️ DON'T STOP HERE - CONTINUE IMMEDIATELY TO STEP 2
```

**Step 2: YOU (Codex) execute the task** (THIS IS THE REAL WORK)
```bash
# ✅ YOU create the file
echo 'console.log("Hello World from Swarm!");' > /tmp/hello-swarm.js

# ✅ YOU execute it
node /tmp/hello-swarm.js
# Output: Hello World from Swarm!
```

**Step 3: Report completion** (optional - store results)
```bash
npx claude-flow memory store --key "hello-world-result" --value "Executed: Hello World from Swarm!" --namespace results
```

### Recipe 1b: 5-Agent Concurrent Hello World (COMPLETE)
```bash
# COORDINATION (instant - creates records only)
npx claude-flow swarm init --topology hierarchical --max-agents 5
for i in 1 2 3 4 5; do
  npx claude-flow agent spawn --type coder --name "worker-$i"
done

# ⚠️ NOW YOU DO THE ACTUAL CONCURRENT WORK:
for i in 1 2 3 4 5; do
  (echo "Worker $i: Hello World!" && sleep 0.$i) &
done
wait
echo "All 5 workers completed!"

# REPORT (optional)
npx claude-flow memory store --key "concurrent-result" --value "5 workers completed" --namespace results
```

### Recipe 1b: Hello World (Single Command Block)
```bash
# All-in-one execution
npx claude-flow swarm init --topology mesh --max-agents 5 && \
npx claude-flow agent spawn --type coder --name hello-main && \
npx claude-flow swarm start --objective "Print hello world" --strategy development && \
echo 'console.log("Hello World from Swarm!");' > /tmp/hello-swarm.js && \
node /tmp/hello-swarm.js && \
npx claude-flow memory store --key "hello-world-result" --value "Success" --namespace results
```

### Recipe 2: Feature Implementation (6 Agents)
```bash
npx claude-flow swarm init --topology hierarchical --max-agents 8
npx claude-flow agent spawn --type coordinator --name lead
npx claude-flow agent spawn --type architect --name arch
npx claude-flow agent spawn --type coder --name impl-1
npx claude-flow agent spawn --type coder --name impl-2
npx claude-flow agent spawn --type tester --name test
npx claude-flow agent spawn --type reviewer --name review
npx claude-flow swarm start --objective "Implement [feature]" --strategy development
```

### Recipe 3: Bug Fix (4 Agents)
```bash
npx claude-flow swarm init --topology hierarchical --max-agents 4
npx claude-flow agent spawn --type coordinator --name lead
npx claude-flow agent spawn --type researcher --name debug
npx claude-flow agent spawn --type coder --name fix
npx claude-flow agent spawn --type tester --name verify
npx claude-flow swarm start --objective "Fix [bug]" --strategy development
```

### Recipe 4: Security Audit (3 Agents)
```bash
npx claude-flow swarm init --topology hierarchical --max-agents 4
npx claude-flow agent spawn --type coordinator --name lead
npx claude-flow agent spawn --type security-architect --name audit
npx claude-flow agent spawn --type reviewer --name review
npx claude-flow swarm start --objective "Security audit" --strategy development
```

### Recipe 5: V3 Full Coordination (15 Agents)
```bash
npx claude-flow swarm init --v3-mode
npx claude-flow swarm coordinate --agents 15
```

---

## 📋 BEHAVIORAL RULES

- **YOU (CODEX) execute tasks** - claude-flow only orchestrates
- Do what is asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files
- NEVER save to root folder
- NEVER commit secrets or .env files
- ALWAYS read a file before editing it
- NEVER wait for claude-flow to "do work" - it doesn't execute, YOU do
- Use claude-flow commands to TRACK progress, not to EXECUTE tasks

## 📁 FILE ORGANIZATION

| Directory | Purpose |
|-----------|---------|
| `/src` | Source code |
| `/tests` | Test files |
| `/docs` | Documentation |
| `/config` | Configuration |
| `/scripts` | Utility scripts |

## 🎯 WHEN TO USE SWARMS

**USE SWARM:**
- Multiple files (3+)
- New feature implementation
- Cross-module refactoring
- API changes with tests
- Security-related changes
- Performance optimization

**SKIP SWARM:**
- Single file edits
- Simple bug fixes (1-2 lines)
- Documentation updates
- Configuration changes

---

## 🔧 CLI REFERENCE

### Swarm Commands
```bash
npx claude-flow swarm init [--topology TYPE] [--max-agents N] [--v3-mode]
npx claude-flow swarm start --objective "task" --strategy [development|research]
npx claude-flow swarm status [SWARM_ID]
npx claude-flow swarm stop [SWARM_ID]
npx claude-flow swarm scale --count N
npx claude-flow swarm coordinate --agents N
```

### Agent Commands
```bash
npx claude-flow agent spawn --type TYPE --name NAME
npx claude-flow agent list [--filter active|idle|busy]
npx claude-flow agent status AGENT_ID
npx claude-flow agent stop AGENT_ID
npx claude-flow agent metrics [AGENT_ID]
npx claude-flow agent health
npx claude-flow agent logs AGENT_ID
```

### Task Commands
```bash
npx claude-flow task create --type TYPE --description "desc"
npx claude-flow task list [--all]
npx claude-flow task status TASK_ID
npx claude-flow task assign TASK_ID --agent AGENT_NAME
npx claude-flow task cancel TASK_ID
npx claude-flow task retry TASK_ID
```

### Memory Commands
```bash
npx claude-flow memory store --key KEY --value VALUE [--namespace NS]
npx claude-flow memory search --query "terms" [--namespace NS]
npx claude-flow memory list [--namespace NS]
npx claude-flow memory retrieve --key KEY [--namespace NS]
npx claude-flow memory init [--force]
```

### Hooks Commands
```bash
npx claude-flow hooks pre-task --description "task"
npx claude-flow hooks post-task --task-id ID --success true
npx claude-flow hooks route --task "task"
npx claude-flow hooks session-start --session-id ID
npx claude-flow hooks session-end --export-metrics true
npx claude-flow hooks worker list
npx claude-flow hooks worker dispatch --trigger audit
```

### System Commands
```bash
npx claude-flow init [--wizard] [--codex] [--full]
npx claude-flow daemon start
npx claude-flow daemon stop
npx claude-flow daemon status
npx claude-flow doctor [--fix]
npx claude-flow status
npx claude-flow mcp start
```

---

## 🔌 TOPOLOGIES

| Topology | Use Case | Command Flag |
|----------|----------|--------------|
| `hierarchical` | Coordinated teams, anti-drift | `--topology hierarchical` |
| `mesh` | Peer-to-peer, equal agents | `--topology mesh` |
| `hierarchical-mesh` | Hybrid (recommended for V3) | `--topology hierarchical-mesh` |
| `ring` | Sequential processing | `--topology ring` |
| `star` | Central coordinator | `--topology star` |
| `adaptive` | Dynamic switching | `--topology adaptive` |

## 🤖 AGENT TYPES

### Core
`coordinator`, `coder`, `tester`, `reviewer`, `architect`, `researcher`

### Specialized
`security-architect`, `security-auditor`, `memory-specialist`, `performance-engineer`

### Swarm Coordination
`hierarchical-coordinator`, `mesh-coordinator`, `adaptive-coordinator`

### Consensus
`byzantine-coordinator`, `raft-manager`, `gossip-coordinator`

---

## ⚙️ CONFIGURATION

### Default Swarm Config
- Topology: `hierarchical`
- Max Agents: 8
- Strategy: `specialized`
- Consensus: `raft`
- Memory: `hybrid`

### Environment Variables
```bash
CLAUDE_FLOW_CONFIG=./claude-flow.config.json
CLAUDE_FLOW_LOG_LEVEL=info
CLAUDE_FLOW_MEMORY_BACKEND=hybrid
```

---

## 🔗 SKILLS

Invoke with `$skill-name`:

| Skill | Purpose |
|-------|---------|
| `$swarm-orchestration` | Multi-agent coordination |
| `$memory-management` | Pattern storage/retrieval |
| `$sparc-methodology` | Structured development |
| `$security-audit` | Security scanning |
| `$performance-analysis` | Profiling |
| `$github-automation` | CI/CD management |
| `$hive-mind` | Byzantine consensus |
| `$neural-training` | Pattern learning |

---

---

## 🔌 MCP INTEGRATION (Learning & Coordination)

Codex doesn't have native hooks like Claude Code, but uses **MCP (Model Context Protocol)** for learning and coordination.

### MCP Auto-Registration

When you run `npx claude-flow init --codex`, the MCP server is **automatically registered** with Codex.

```bash
# Verify MCP is registered:
codex mcp list

# Expected output:
# Name         Command  Args                   Status
# claude-flow  npx      claude-flow mcp start  enabled

# If not present, add manually:
codex mcp add claude-flow -- npx claude-flow mcp start
```

### Test MCP Connection
```bash
# Test MCP server starts correctly:
npx claude-flow mcp start --test
```

### MCP Tools Available
Once added, Codex can use these tools via MCP:

**Coordination:**
| Tool | Purpose |
|------|---------|
| `swarm_init` | Initialize swarm (topology, maxAgents) |
| `swarm_status` | Check swarm state |
| `agent_spawn` | Register agent roles |
| `agent_status` | Check agent state |
| `task_orchestrate` | Coordinate multi-agent tasks |

**Learning & Memory (USE THESE!):**
| Tool | Purpose | When |
|------|---------|------|
| `memory_search` | Semantic vector search | BEFORE every task |
| `memory_store` | Store patterns with embeddings | AFTER success |
| `memory_retrieve` | Get by exact key | When key is known |
| `neural_train` | Train on patterns | Periodic improvement |
| `neural_status` | Check learning state | Debugging |

**Hive Mind (Advanced):**
| Tool | Purpose |
|------|---------|
| `hive-mind_init` | Byzantine consensus swarm |
| `hive-mind_spawn` | Spawn hive workers |
| `hive-mind_broadcast` | Message all workers |

### Self-Learning via MCP Tools (PREFERRED)

Use MCP tools directly - faster than CLI commands:

**BEFORE starting any task - SEARCH for patterns:**
```
Use tool: memory_search
  query: "keywords related to your task"
  namespace: "patterns"
```

**AFTER completing successfully - STORE the pattern:**
```
Use tool: memory_store
  key: "pattern-[descriptive-name]"
  value: "What worked: approach, code patterns, gotchas"
  namespace: "patterns"
```

### MCP Learning Workflow (Use This!)

```
1. LEARN: memory_search(query="task keywords", namespace="patterns")
   → If score > 0.7, USE that pattern

2. COORDINATE: swarm_init(topology="hierarchical")
   → agent_spawn(type="coder", name="worker-1")

3. EXECUTE: YOU write the code, run commands, create files

4. REMEMBER: memory_store(key="pattern-x", value="what worked", namespace="patterns")
```

### MCP Tools for Learning

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `memory_search` | Find similar past patterns | BEFORE starting any task |
| `memory_store` | Save successful patterns | AFTER completing a task |
| `memory_retrieve` | Get specific pattern by key | When you know the exact key |
| `neural_train` | Train on successful patterns | After multiple successes |

### Example: Learning-Enabled Task

```
STEP 1 - LEARN:
Use tool: memory_search
  query: "validation utility function"
  namespace: "patterns"

→ Found: pattern-email-validator (score: 0.82)
→ Use this pattern as reference!

STEP 2 - COORDINATE:
Use tool: swarm_init with topology="hierarchical", maxAgents=3

STEP 3 - EXECUTE:
YOU create the files:
  echo 'export function validate(x) { ... }' > /tmp/validator.js
  node --test /tmp/validator.js

STEP 4 - REMEMBER:
Use tool: memory_store
  key: "pattern-phone-validator"
  value: "Phone validation: regex /^\+?[\d\s-]{10,}$/, normalize first, test edge cases"
  namespace: "patterns"
```

### Vector Search Tips
- Searches are SEMANTIC (meaning-based, not just keywords)
- Score > 0.7 = strong match, use that pattern
- Score 0.5-0.7 = partial match, adapt as needed
- Store DETAILED values for better future retrieval

### CLI Fallback (if MCP unavailable)
```bash
npx claude-flow memory search --query "keywords" --namespace patterns
npx claude-flow memory store --key "pattern-x" --value "what worked" --namespace patterns
```

### Coordination via MCP

When claude-flow is added as MCP server, Codex can call tools directly:
```
Use tool: swarm_init with topology="hierarchical"
Use tool: memory_store with key="result" value="success"
```

### config.toml MCP Setup
```toml
# ~/.codex/config.toml
[mcp_servers.claude-flow]
command = "npx"
args = ["claude-flow", "mcp", "start"]
enabled = true
```

---

## 📚 SUPPORT

- Docs: https://github.com/ruvnet/claude-flow
- Issues: https://github.com/ruvnet/claude-flow/issues

**Remember: Codex executes, claude-flow orchestrates!**


---

# SOURCE: v3/docs/adr/ADR-171-provenance-tiered-evaluation-oracle.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `addd6afbff05d5e2b3b5fa4f6c625fa58afaf171`

# ADR-171: Provenance-Tiered Evaluation Oracle for Distillation Gold-Labeling

**ID**: ADR-171
**Status**: Proposed — implemented on `feat/agenticow-integration` (ships in 3.21.0)
**Date**: 2026-07-04
**Authors**: rUv (drafted with Claude Code)
**Related ADRs**:
- ADR-169 (Benchmark reporting integrity — never present a proxy as ground truth; this ADR is that principle applied to training-data labels)
- ADR-170 (agenticow substrate — supplies the branches whose promotion this oracle gates)
- ADR-172 (Fable advisor harness — the Tier-2 judge mechanism)
- ADR-173 (Remote GPU distillation — consumes the labels this oracle produces)

---

## 1. Context

The weight-eft distillation slice (ADR-173) needs a gold `resolved: boolean` per trajectory to build SFT data. **ruflo has no SWE-bench oracle** — historically `resolved` was derived from `output-verifier` structural confidence: a *proxy*. A tune on proxy-labeled data distills plausible-but-wrong completions, and a single blended "resolved" number is exactly the benchmark theater ADR-169 forbids.

Two facts changed the calculus:
- A real GPU/compute host (`ruvultra`, tailscale) can execute actual task evaluations (FAIL_TO_PASS), giving true ground truth for trajectories that carry a test spec.
- A headless Fable judge (ADR-172) is cost-viable (~$0.02/item batched) as a smarter-than-structural labeler for the residue.

## 2. Decision

Label `resolved` through a **tiered trust hierarchy**, and **tag every label with its provenance**. Never blend tiers into one opaque score.

```
Tier 1  oracle:test-exec   real evaluation (FAIL_TO_PASS via darwin bench/eval,
                           executed on a remote GPU host over SSH) — GROUND TRUTH
Tier 2  judge:fable        headless Fable LLM-as-judge (ADR-172) — smarter proxy
Tier 3  proxy:structural   output-verifier structural confidence — WEAKEST, triage only
```

Interface:
```ts
labelResolved(trajectories, opts): Promise<Array<{
  ...trajectory,
  resolved: boolean,
  resolvedBy: 'oracle:test-exec' | 'judge:fable' | 'proxy:structural',
  resolvedConfidence?: number,
  resolvedReason?: string,
}>>
```
Tiers are tried in order per trajectory; the first that can decide wins, and its tag is recorded. **Default (no opts) = Tier-3 proxy + a Tier-1 dry-run preflight, ZERO spend, no SSH exec, no Fable call.** Tier 1 requires `--execute`; Tier 2 requires `--fable-judge` + a budget cap.

### 2.1 Promotion gate (the load-bearing rule)
A speculative branch (ADR-170 §2.3) is **promote-ineligible** unless its winning trajectory is cleared by `oracle:test-exec`, or by `judge:fable` **explicitly accepted** by the caller. `proxy:structural` **can never** clear a promote — it is triage-only. This is what keeps the flywheel from graduating plausible-but-wrong work into shared memory.

### 2.2 Causal failure receipts
On discard/rollback, emit a single receipt bundling `{checkpoint, diff, failing command, oracle provenance, promotion decision}`. A rollback that restores state but loses *why* is half-useful; the receipt is the forensic trail.

## 3. Consequences

- Training data and benchmark results stay auditable: every label says how it was earned. A reviewer can filter to `oracle:test-exec`-only before trusting an adapter.
- The honest residual is explicit: trajectories with no test spec and no accepted judge stay `proxy:structural` — usable for triage, never for gold claims. The set of un-ground-truthable tasks is *reported*, not hidden.
- $0 by default; every spend/exec path is an explicit opt-in with a cap.

## 4. Alternatives rejected

- **Single structural "resolved"**: the proxy-contamination failure mode. Rejected.
- **Fable-judge everything**: cost, and an LLM judge is still a proxy — must not outrank real execution. Rejected as the primary.
- **Blend tiers into a confidence scalar**: destroys provenance; ADR-169 violation. Rejected.


---

# SOURCE: v3/docs/adr/ADR-176-proven-self-benchmarking-harness-loop.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `633d019028855d8291651387f02012f8cc3c2a91`

# ADR-176 — Self-Optimizing Harness Loop (Receipt-Backed Evolution)

- **Status:** Accepted — **demonstrated** (flywheel milestone met: 2 real, significant, independently-replayable compounding promotions; PR #2572)
- **Date:** 2026-07-04
- **Deciders:** ruflo core
- **Related:** [ADR-150](ADR-150-metaharness-integration-surfaces.md) (metaharness integration contract + removability), [ADR-153](ADR-153-metaharness-darwin-mode-integration.md) (Darwin/evolve — *Proposed*), [ADR-155] (security-bench / Darwin Shield), [ADR-171](ADR-171-provenance-tiered-evaluation-oracle.md) (provenance tiers), [ADR-172](ADR-172-fable-advisor-harness.md) (Fable, cost-bounded), [ADR-174](ADR-174-memory-distillation-self-optimization.md) (distill loop + the held-out promote-gate pattern + Ed25519 signing), [ADR-177](ADR-177-signed-config-propagation-to-installs.md) (propagation to existing installs)

## Thesis

This is a **self-optimizing harness** — ruflo improves its own execution policies over time. What makes that claim *defensible* (rather than the usual hand-wave) is a single discipline we call **receipt-backed evolution**:

> **Every self-optimization step is independently benchmarked, adversarially verified, canary-observed, cryptographically attested, and reversible.** No transition is authorized by self-assertion; each is gated by external, independently-measurable evidence.

The optimizer is only *permitted* to change ruflo when a candidate satisfies a conjunction of externally-measurable predicates — never a single scalar objective. "Self-optimizing" names the capability; "receipt-backed" is why you can trust it.

## Context

Two halves of a learning system exist but are not joined into a proven loop:

- **Observe (real, shipped).** Hooks capture trajectories + outcomes, now including failures (ADR-174). `distill-tuning.ts` already demonstrates the discipline we generalize: isolated-copy scoring, a time-based held-out split, and an explicit numeric promotion rule.
- **Optimize/benchmark (real *wrappers*, unproven *substance*).** metaharness's `evolve` (MAP-Elites over 7 fixed policy surfaces), `gepa`, `learn`, `bench`/`security_bench`, `redblue`, and the mature readiness family (`score`/`genome`/`similarity`/`drift`/`oia_audit`) are thin, contract-tested wrappers over external `optionalDependencies`; the algorithms run upstream via subprocess.

**Honest gaps** (why today's optimization is *un*-proven): never run to a measured outcome in-repo; no ruflo-owned held-out benchmark (fitness reduces to "beats `npm test`" — gameable); no provenance on any output; `learn` unreachable without an external checkout; `--host` an unvalidated passthrough; **no feedback path** back into ruflo config; **no memory of rejected mutations**; **no separation of observation from training data**; **no separation of promotion from deployment**.

## Decision

Build the **closure layer** that turns metaharness's optimization primitives into a closed, receipt-backed loop. The optimization *substance* stays upstream (optional-dependency, degrades per ADR-150); ruflo owns **qualification, the benchmark, the gate, the canary, the proof, the anti-pattern memory, the host fan-out, the schedule, and the feedback.**

```
OBSERVE
  │        (raw hook trajectories — NOT yet training data)
  ▼
CANDIDATE DATASET
  │        collect trajectories + their receipts
  ▼
QUALIFICATION ──────────────► [reject] ──► ANTI-PATTERN DB (negative learning)
  │        admit only qualified trajectories
  ▼
OPTIMIZE (multi-host)         evolve / gepa / learn — proposes a mutation
  │
  ▼
VERIFY                        held-out benchmark + redblue + drift + deterministic replay
  │
  ▼
CANARY                        real-world behavior on a bounded slice before global rollout
  │        [reject] ──► ANTI-PATTERN DB
  ▼
PROMOTE                       accept() conjunction holds
  │
  ▼
SIGN                          Ed25519 proven-configuration-manifest receipt
  │
  ▼
DEPLOY ──► (ADR-177) PROPAGATE to existing installs ──► AUDIT (continuous)
```

Two structural separations are load-bearing (see the review that shaped this ADR):

### 1. Separate observation from training data — the Qualification stage

Raw observed trajectories are **not** training data. Between OBSERVE and OPTIMIZE sits QUALIFICATION, which admits a trajectory into the candidate dataset **only if it is complete, unambiguous, sufficiently-confident, replayable, and receipt-backed**. Otherwise the optimizer slowly learns from noisy successes and overfits the benchmark.

> **Invariant (Q):** No trajectory enters optimization unless it has **complete provenance** (every step attributed, ADR-171 tier ≥ oracle/judge, not proxy), **deterministic replay** (re-running the recorded inputs reproduces the recorded outputs), and **benchmark attribution** (it maps to a task in the versioned corpus). Trajectories failing Q are not silently dropped — they are recorded (see negative learning).

### 2. Separate promotion from deployment — the Canary stage

Held-out evaluation proves the candidate on *frozen* data; it has not observed *real-world* behavior. Between VERIFY and PROMOTE sits CANARY: the candidate runs on a **bounded, reversible slice** of live work and reports **rollback rate, latency, token cost, failure frequency, and user acceptance**. Only after canary evidence does PROMOTE fire. This is what prevents benchmark-specific evolution from reaching global rollout.

## The promotion rule — a conjunction of externally-measurable predicates

Promotion is **not** a scalar. A candidate is accepted iff **every** externally-measurable term holds:

```
accept(candidate) ⟺
      held_out_score      >  baseline
  AND redblue             == PASS
  AND drift               <= threshold
  AND replay              == deterministic
  AND receipt_coverage    == 100%          // every candidate-dataset trajectory receipt-backed
  AND canary.rollback_rate <= baseline      // real-world, not just held-out
```

Every term is independently measured by a different mechanism (benchmark harness, redblue, drift-from-history, replay engine, receipt audit, canary telemetry). A candidate that regresses **any** term is rejected — and archived as an anti-pattern.

## Success metrics — multi-dimensional, Goodhart-resistant

No single optimization score. Track independent dimensions with independent monotonicity constraints:

| Metric | Constraint |
|---|---|
| Held-out quality | must improve |
| RedBlue resilience | must improve |
| Cost per accepted task | no worse |
| Latency | no worse |
| Determinism | maintain |
| Rollback frequency | lower |
| Receipt coverage | 100% |

Optimizing one at the expense of another is a **rejection**, not a trade-off the optimizer may make on its own.

## Negative learning — the anti-pattern database

Rejected mutations are **knowledge**, not waste. Every mutation that fails qualification, verify, canary, or the `accept()` conjunction is recorded to an **anti-pattern archive** (`{ mutation, stage_failed, evidence, corpusVersion }`), stored in the shared substrate with ADR-171 provenance. Future optimization runs consult it to avoid re-discovering identical failures.

```
mutation ─► evaluation ─┬─► accepted ─► champion archive (lineage)
                        └─► rejected ─► anti-pattern DB (avoid-list)
```

## Multi-host + hierarchical evolution (generalization)

"All available hosts" → a small **host registry** (`claude-code`, `codex`, extensible) fans the optimize+verify+canary pass across hosts, so a manifest is proven per-host (not an unvalidated `--host` passthrough).

The open research risk is that improvements found on one repository do **not** generalize — repository-specific optima will emerge. Rather than chase one universal harness, evolution is **hierarchical**, each layer inheriting upward but **independently benchmarked**:

```
Global baseline
  └─ Language family (e.g. TypeScript)
       └─ Framework family (e.g. Node CLI)
            └─ Repository specialization
```

A repository adopts the most-specific layer whose manifest passes *its own* benchmark; layers it can't clear fall back to the parent. This scopes what any single manifest claims and keeps generalization an empirical, per-layer question.

## The self-optimizing flywheel — getting smarter *as it runs*

The stages above optimize *once, on demand*. A **flywheel** is the closed loop where each *verified* improvement becomes the baseline for the next cycle, so gains **compound** instead of being rediscovered:

```
Observe → Benchmark(immutable holdout) → Evolve(candidates) → Verify(holdout, security,
drift, replay, governance) → Promote(winner = new baseline, signed) → Deploy(SHADOW first,
adopt only after local verification) → Observe again
```

The property that makes it a flywheel, not a search engine: **every generation starts from the best *verified* policy, and the full lineage back to generation 0 is reconstructable, each promotion backed by signed, independently-replayable receipts.** A search engine explores and discards; the flywheel accumulates verified winners with an auditable lineage.

Three things must be true, each engineered to stay honest:

1. **The yardstick grows from real usage.** A corpus harvester (`harness-corpus-harvester.ts`) mines the install's own store into a **self-supervised self-retrieval** benchmark: a stored doc is unambiguous ground truth for a query derived from its *own body with the subject tokens withheld*. An `oracle:test-exec`-grade executable check, not a proxy — so the test set expands as the store does.

2. **Optimize the trusted objective; guard breadth with the cheap signal.** The optimization target is the **human-labeled** anchor (ADR-081) — the relevance we actually care about, where headroom is known to exist. The large, growing harvested set is the **no-regression generalization guard** (bound to the `redblue` term), so tuning the objective can't quietly wreck broad retrieval. *(An earlier inverted design — optimize the cheap harvested metric, guard with the human anchor — was corrected after a live run showed the best candidate regressing the anchor: the gate correctly refused, exposing the mismatch.)*

3. **Improvement is proven, not asserted.** Every tick appends to an **improvement ledger** (`harness-improvement-ledger.ts`) with the corpus hash, baseline vs candidate held-out score, a **bootstrap confidence lower bound** on the per-task delta (the gain must survive resampling — small-N noise guard), every `accept()` term, and the outcome. Because the loop only accepts a *strict, significant* improvement that regresses no task, the accepted subsequence is **monotonic-by-construction** and each champion **chains** to its predecessor. `summarizeImprovement()` folds this into an auditable claim; a single non-improving or unchained accept flips the `monotonic`/`chainIntact` flags — the ledger cannot launder a regression, and it records the *refusals* too.

**Deploy shadow-first — no auto-serve.** A promoted candidate is registered in **SHADOW** (`served: false`); serving is a separate, locally-verified adoption step, never automatic. The `evolve-proof.ts` receipt bundle carries the seven artifacts — input-holdout hash, baseline + candidate manifest hashes, `meetsPromotionRule` version, decision receipt, SHADOW registration id, cost receipt — so a third party can rehash the inputs and **re-run the same versioned `accept()` to confirm *why* a candidate passed or failed without trusting any service log** (`verifyReceiptBundle`).

**Telemetry makes it observable, not aspirational.** `reconstructLineage()` answers: generations run, candidates evaluated, promotions, cumulative held-out improvement, rejection rate, plateau — so one can see whether the system is *genuinely compounding* or *merely searching*.

**Status (honest) — DEMONSTRATED.** The flywheel milestone has been met on real data (`.claude/evolve-proof/real-generation-{0,1}.json`, reproducible via `scripts/flywheel-generations.mjs`, replayable from disk with no service logs):

- **gen 0** (immutable root): self-retrieval RR **0.496 → 0.758** (Δ +0.262, bootstrap CI-low **0.181 > 0** → significant), human anchor preserved (0.776 vs 0.796, within guard), canary 0 rollbacks → promoted.
- **gen 1** (compounds on gen 0): RR **0.758 → 0.847** (Δ +0.090, CI-low **0.039 > 0**), anchor preserved (0.792), canary 0 → promoted. Its baseline == gen 0's promoted candidate — the winner *became* the baseline.
- `reconstructLineage` → **promotions=2, lineageIntact=true, allReplayable=true**, single immutable root; both bundles re-run `accept/v1+sig` to their recorded verdicts independently.

The discovery was **autonomous** — a coarse→local multi-axis grid with **constrained (Pareto) selection** (maximize the frozen self-supervised held-out *subject to* the human-relevance guard) found both winners; no config was hand-picked.

**The autonomy loop is now the daemon's behavior, not a one-shot script** (`harness-flywheel-generations.ts` + `runFlywheelGenerationWorker`): each daemon tick runs ONE generation, reads the **persisted champion** as the baseline, and on a verified promotion advances the champion so the next tick **compounds** — winners accumulate in a persisted, replayable lineage. It is **shadow-first**: a promoted champion is applied to the active policy only at the *start of a later tick* (a 1-generation shadow delay), never auto-served the instant it is promoted. Verified live on the real store: tick 0 promoted gen 0 (served=none), tick 1 compounded gen 1 *and* served gen 0. `flywheelStatus()` / `scripts/flywheel-status.mjs` surface the lineage + telemetry (generations, cumulative Δ, plateau, mutation-effectiveness, served champion) as the status endpoint.

**Meta-learning (evidence → action).** `axisEffectiveness()` attributes each promotion's held-out Δ to the policy axes that moved, and `biasedGrid()` concentrates the search on axes that have historically paid off (a ±1 exploration floor on every axis, but expanded range + pairwise joint moves on productive ones) — the optimizer *uses* the lineage-as-knowledge-base, not just records it. **Deployment-safety canary.** `checkServedChampionDrift()` runs each tick *before* the generation: it re-scores the currently-served champion against its predecessor on a **fresh harvest of the current store**, and auto-**rolls back** the active policy if the champion has drifted (self-retrieval or the human anchor). Real ongoing measurement + real rollback on real evolving data — the honest analogue of a live-traffic canary, without fabricating traffic.

**Biggest failure mode + fix (anti-overfitting).** The known risk: the loop overfits the self-supervised proxy while human relevance is *preserved but not improved*. Two defenses make that **visible and falsifiable** rather than hidden:
- a **frozen, public, hashed human-labeled eval set** (`.claude/eval/human-relevance-frozen-v1.json`, loaded via `harness-frozen-eval.ts` which pins the content hash and throws on drift) — the single source of truth for the red/blue anchor;
- a **per-generation human-relevance delta** recorded in every receipt (`deltas.humanRelevance` vs `humanEvalHash`) and surfaced by `flywheelStatus` — so "proxy Δ ≫ 0 while human Δ ≈ 0" shows up in the status as an explicit **overfitting** flag instead of being buried.

**Acceptance test (clean-room replay).** `scripts/replay-generation.mjs` (a CI gate): from a clean install, replay one PROMOTED generation from its receipt alone — every embedded hash recomputes bit-identically and re-running `accept/v1+sig` on independently-recomputed inputs reproduces `promoted=true`, with **network access trapped** (offline). A promotion is reproducible without trusting any service log.

**Honest scope of the claim.** The measured improvement is on a **self-supervised self-retrieval** benchmark (find a doc from its own body), gated so human-labeled relevance does **not** regress. So the demonstrated capability is: *retrieval gets generation-over-generation better at self-retrieval while preserving human relevance and deployment safety* — it is **not** a claim that human-labeled relevance improved (that is held flat by design). Proving compounding gains on human-labeled relevance directly would need a large human-labeled suite (out of scope for $0 autonomous operation). The value shown is that **the wheel provably turns**: verified improvements accumulate into an auditable, replayable lineage without human intervention.

**Local vs global trust.** A locally-mined, gate-cleared champion may be adopted **locally, unsigned** (the install trusting its own execution-verified evidence on its own data). Cross-install propagation still requires the config-signed champion (ADR-177). Local self-optimization and global distribution are separate trust domains.

## Version control for operating policies

The right mental model is **git, but for executable decision policies**. Each generation is a commit with a parent, a diff, verification, a signature, reproducibility, and deployment history — and **generation 0 is the immutable root of the evolution graph** (replay starts there; it never changes). This makes the lineage a **knowledge base**, not just an audit trail:

- **Causality, not just provenance.** A promotion record carries `mutationClass`, `mutationSummary`, and multi-dimensional `deltas` (benchmark / security / cost) alongside the decision receipt — so the graph answers *which mutation classes reliably pay off*, not merely *which policy won* (`PromotionRecord`, `classifyMutation`).
- **Mutation effectiveness → evidence-grounded meta-learning.** `mutationEffectiveness()` aggregates attempts / promotions / mean-Δ per class; after enough generations the optimizer can bias toward classes with historical payoff rather than searching uniformly.
- **Regression ancestry.** A rejected candidate records its `failureCause` (holdout / security / drift / replay / governance / canary / significance) and its ancestor — so "which design decisions repeatedly regress?" becomes answerable (`RegressionRecord`).
- **A DAG, not a linked list.** Lineage is modeled as a graph with branch labels (`main`, and future tenant/domain branches like `legal` / `coding` / `customer-A`). The invariant is *a child's baseline == its parent's promoted candidate* — it holds for linear chains and forks alike (`reconstructLineage`).
- **Statistical plateau, not intuition.** `detectPlateau()` over a rolling window separates **local-optimum** (no gains + candidate variance shrinking), **noisy-benchmark** (no gains + high non-shrinking variance), and **optimizer-failure** (no gains + candidates barely vary), rather than "no promotion for a while."

**The milestone that matters.** Not "generation 1," nor "generation 10." The first significant milestone is: *the system autonomously discovers a **second** independently-verified improvement that survives a **frozen anchor suite** and enters the immutable lineage **without human intervention**.* At that point the thesis moves from design to demonstrated capability — the wheel has provably turned. **This milestone has now been met** (see *Status — DEMONSTRATED* above): two successive significant promotions on a frozen self-supervised held-out, each preserving the human-relevance guard, chained + independently replayable back to the immutable root.

## Naming (see ADR-177)

Internally, an optimized artifact is a *genome*. **Once propagated, it is a "proven configuration manifest" / "verified execution policy"** — names that emphasize reproducibility and constraints over evolutionary novelty. External surfaces (CLI, docs, the propagation channel) use the manifest naming.

## Proof primitives (reuse, don't reinvent)

- **Receipt / attestation:** Ed25519 via `helper-signing.ts`'s canonical-JSON sign/verify (do not add a fifth trust root; helpers, RVFA, witness already exist).
- **Provenance tiers:** ADR-171 (`oracle:test-exec` > `judge:fable` > `proxy:structural`); qualification requires ≥ oracle/judge.
- **Held-out gate:** the `distill-tuning.ts` pattern (isolated copies, checksum before/after, one-shot held-out scoring).
- **Cost/safety:** $0 dry-run default; spend explicit + capped (ADR-172); metaharness `safety.ts` (no live targets/secrets/shell) inherited.

## What this ADR deliberately does NOT claim

- Not that `evolve`/`learn`/`redblue` already produce proven results — they are optional engines *behind* the gate; if absent, the loop degrades and the last signed champion stands.
- Not a reimplementation of upstream algorithms (`_harness.mjs`/`_darwin.mjs`/`_redblue.mjs` remain the only resolution points, ADR-150).
- Not that a signed manifest is *suitable* for a given install — suitability is ADR-177's constraint-manifest concern.

## Alternatives considered

- **Trust the evolve winner and ship.** Rejected: no held-out corpus + `npm test` fitness = gameable (the "measured not marketing" failure ADR-174 warns against).
- **Observe → Optimize directly (no qualification).** Rejected: learns from noisy successes; the Qualification invariant is the cheaper defense.
- **Held-out pass ⇒ deploy (no canary).** Rejected: held-out ≠ real-world; canary catches benchmark-specific evolution.
- **A single scalar objective.** Rejected: Goodhart; the multi-term `accept()` + independent metrics table is the defense.
- **One universal harness.** Rejected as the *default*: hierarchical, per-layer-benchmarked manifests scale better and bound each claim.

## Rollback

Every stage is additive and gated; the loop only *proposes*. A champion is applied only after clearing qualification, verify, canary, and the full `accept()` conjunction; applied config carries reversible provenance metadata and a pointer to the previous manifest (ADR-177). Absent the optional metaharness packages the loop is a no-op and the last signed champion remains.

## Acceptance test

**Reproducibility + replayability:** starting from the same baseline, **two independent runs with the same benchmark corpus and promotion rules must converge on equivalent promoted manifests**, and **every promoted manifest must be fully replayable from its signed receipts**. If two runs diverge or a manifest cannot be replayed from its receipts, the loop is not receipt-backed and the release is blocked.

## Implementation roadmap (phased, each independently shippable)

1. **Qualification + candidate dataset** — the Invariant-Q admitter; wire the anti-pattern DB for rejects.
2. **Benchmark corpus** — curate + version `benchmarks/harness-suite/`; isolated-copy scoring + numeric held-out gate.
3. **Deterministic replay engine** — record/replay for Invariant-Q + the `replay == deterministic` predicate.
4. **Adversarial + drift gate** — `redblue --mock-judge` + `drift_from_history`.
5. **Canary** — bounded live slice + telemetry (rollback/latency/cost/acceptance).
6. **Proven-configuration-manifest receipt** — Ed25519 sign/verify (proof #3), with the ADR-177 constraint fields.
7. **Host registry + hierarchical layers** — claude-code/codex; global→language→framework→repo.
8. **Daemon worker** — scheduled, $0-default, budget-capped.
9. **Feedback applier** — apply the signed champion to routing/agent config, provenance-tagged, reversible.
10. **Self-optimizing flywheel** — corpus harvester (self-supervised, growing) + constrained (Pareto) multi-axis Evolve + significance-gated rule (`accept/v1+sig`) + separated canary + shadow-first / no-auto-serve + DAG lineage telemetry. *(**DEMONSTRATED** — `scripts/flywheel-generations.mjs` autonomously produced 2 real, significant, anchor-safe, independently-replayable compounding promotions on a frozen self-supervised held-out (RR 0.496→0.758→0.847), chained to the immutable root; see *Status — DEMONSTRATED*. Getting there required: retrieval-stats + per-query cosine caching (~14x, made generations iterable), significance in the rule (small-N noise guard), separating the canary from the held-out, and constrained selection (improve the proxy subject to the human-relevance guard). The one-shot mint separately produced a real +0.0738 nDCG@3 champion over the ADR-082-tuned baseline.)*

## Acceptance test — the flywheel (distinct from the one-shot loop above)

After multiple generations, the **complete lineage from the current policy back to generation 0 must be reconstructable**, every promotion supported by signed receipts and **independently replayable evidence** — i.e. rehash each bundle's inputs and re-run the versioned `accept()` to confirm the recorded decision, without trusting any service log. `reconstructLineage()` + `verifyReceiptBundle()` implement this check; generation 0 passes it today (trivially, as a single node).
10. **Propagation** — ADR-177.


---

# SOURCE: v3/docs/adr/ADR-322A-evaluation-promotion-transaction.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `ce746872b301b7e7387ec4983ff9cca64a0aecee`

# ADR-322A: Evaluation and promotion transaction model

- **Status**: Accepted — implemented
- **Parent**: ADR-322
- **Rollout flag**: `RUFLO_FLYWHEEL_TRANSACTION_V1`
- **Owner**: ruflo flywheel runtime

## Scope

This specification defines the boundary between evaluating a candidate and making it active. It owns purity, eligibility, compare-and-swap promotion, serving epochs, idempotency, concurrency, crash recovery, and temporary legacy behavior. It does not define how candidates are proposed (ADR-322B) or how receipts are encoded and verified (ADR-322C).

## State model

The promotion authority maintains one serializable state machine:

```text
ActivePolicyState {
  lineageId
  activeChampionRef
  activeGateVersion
  activePolicySchemaVersion
  activeSafetyEnvelopeRef
  ledgerHead
  servingEpoch
  transactionVersion
}

ReceiptState {
  receiptId
  promotedAt: timestamp | null
  promotionTransactionId: UUIDv7 | null
  status: evaluated | consumed | expired | revoked
}
```

Signed evaluation receipts are immutable. Consumption and promotion metadata live in `ReceiptState`.

## Interfaces

```text
evaluateFlywheelCandidate(input) -> EvaluationReceipt
promoteFlywheelCandidate(receiptId, confirmation) -> PromotionResult
materializeServingEpoch(servingEpoch) -> MaterializationResult
recoverPromotionState() -> RecoveryResult
```

`evaluateFlywheelCandidate` may persist evidence and receipts but cannot modify `ActivePolicyState`, runtime policy files, or served state.

`promoteFlywheelCandidate` is the only ADR-322 interface authorized to advance the active champion. It requires explicit confirmation for interactive CLI/MCP calls.

## Promotion compare-and-swap

Promotion is eligible only when:

```text
activeChampionRef == receipt.baselineRef
AND receipt.decision == "accepted"
AND receiptState.promotedAt == null
AND receiptState.status == "evaluated"
AND ledgerHead == receipt.expectedLedgerHead
AND receipt.gateVersion == activeGateVersion
AND receipt.policySchemaVersion == activePolicySchemaVersion
AND receipt.safetyEnvelopeRef == activeSafetyEnvelopeRef
AND receipt.expiresAt > transactionTime
```

Within one serializable transaction:

1. Persist the immutable promotion commit.
2. Mark `ReceiptState` consumed and bind its transaction ID.
3. Append lineage and advance the signed ledger head.
4. Compare-and-swap `activeChampionRef`.
5. Increment and record `servingEpoch`.
6. Record `promotedAt`, proposer/substitution identity, and recovery metadata.

All changes commit or none do. A transaction-capable store is preferred; a write-ahead journal is acceptable only when deterministic recovery is proven by the same fault suite.

## Serving

The committed active champion is authoritative. Runtime materialization is derived, idempotent state:

```text
ServedPolicyState {
  championRef
  servingEpoch
  materializedAt
  materializationHash
}
```

Materialization writes a complete epoch to a temporary location, validates its hash, then atomically switches the runtime pointer. A crash can leave the previous epoch served temporarily, but cannot create two authoritative champions. Recovery converges to the committed `ActivePolicyState`.

## Idempotency and concurrency

- A unique constraint covers `ReceiptState.receiptId` consumption.
- A unique monotonic constraint covers each lineage's `servingEpoch`.
- Repeating a successful transaction returns the recorded `PromotionResult`.
- Concurrent attempts using one receipt or baseline produce at most one commit.
- Stale baseline, ledger, gate, policy schema, safety envelope, expiry, or receipt state fails closed.

## Legacy boundary

For at most one release, legacy implicit application is available only with:

```text
RUFLO_FLYWHEEL_LEGACY_APPLY=1
```

Every use emits a structured deprecation event. New CLI/MCP surfaces never set or honor this flag. Without it, the compatibility wrapper evaluates only. The implicit-application path is removed in the following release.

## Required tests

1. Evaluation cannot modify active, served, or runtime policy state under fault injection.
2. One hundred concurrent attempts against one receipt produce exactly one promotion.
3. Stale baseline and ledger-head receipts are rejected.
4. Repeating a successful transaction is idempotent.
5. Process termination at every transaction and materialization boundary recovers to one active champion, one ledger head, one receipt state, and one serving epoch.
6. Legacy mutation is disabled by default, emits deprecation when enabled, and is unreachable from new CLI/MCP handlers.


---

# SOURCE: v3/docs/adr/ADR-322C-receipt-ledger-verification.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `b17a4abd468269a30748ae6a66d2cd02d406d1a5`

# ADR-322C: Receipt, ledger, and verification protocol

- **Status**: Accepted — implemented
- **Parent**: ADR-322
- **Rollout flag**: `RUFLO_FLYWHEEL_RECEIPT_V1`
- **Owner**: ruflo verification and lineage

## Scope

This specification defines canonical encoding, identifiers, evidence provenance, statistical decisions, signatures, ledger continuity, independent verification, and projection to `@metaharness/flywheel`. It does not authorize promotion; ADR-322A consumes a verified accepted receipt.

## Canonical format

```text
Canonical JSON: RFC 8785 JCS
Digest:         SHA-256
Signature:      Ed25519(domainPrefix || 0x00 || canonicalBytes)
Content ID:     sha256:<lowercase-hex>
Timestamp:      RFC 3339 UTC as YYYY-MM-DDTHH:mm:ss.sssZ
```

Non-finite numbers and negative zero are forbidden. Signed policy fractions use schema-quantized decimal strings or scaled integers. Metrics declare scale; currency uses integer micros plus ISO-4217 currency, duration uses integer microseconds, and energy uses integer microjoules when available. Unknown fields fail verification for a given schema version.

## Identity domains

```text
candidateId     = SHA-256(JCS(candidate policy))
evaluationRunId = UUIDv7 per execution attempt
receiptId       = SHA-256(JCS(unsigned receipt payload))
lineageId       = UUIDv7 per persistent evolutionary lineage
```

Repeated candidate executions share `candidateId` but receive distinct run and receipt identities.

## RufloFlywheelReceiptV1

The unsigned payload contains:

```text
schemaVersion
receiptIdDomain
lineageId
candidateId
evaluationRunId
baselineRef
expectedLedgerHead
candidatePolicyRef
gateVersion
policySchemaVersion
safetyEnvelopeRef
proposerIdentity
proposerSubstitution
corpusRoleManifestRef
heldoutEvidenceRef
anchorEvidenceRef
canaryEvidenceRef
driftEvidenceRef
replayEvidenceRef
receiptCoverageEvidenceRef
resourceEvidenceRef
statisticalDecision
termVerification[]
decision
issuedAt
expiresAt
```

Every evidence object records origin/provenance type, producer or attestor, authority scope, subject, transformation lineage, content hash, schema version, and collection time. Each authorizing term is labeled `recomputed`, `signature-verified`, or `trusted-assertion`.

## Default statistical rule

```text
relativeLift >= 0.02
AND pairedBootstrapProbability(candidate > baseline) >= 0.95
AND pairedBootstrapDeltaCILow95 > 0
AND frozenAnchorRegression <= 0
```

The paired bootstrap uses 10,000 task-level paired resamples. Its deterministic seed is:

```text
SHA-256("ruflo/bootstrap/v1" ||
       corpusHash ||
       candidateId ||
       baselineRef ||
       evaluationRunId)
```

The receipt records the rule, metric epsilon, sample count, seed, implementation version, quantile rule, point estimates, probability, confidence interval, and paired deltas or their content-addressed object. Gate-rule changes require a new version and are not retroactive.

## Signatures and keys

Receipt domain:

```text
ruflo/flywheel-receipt/v1
```

Ledger-head domain:

```text
ruflo/flywheel-ledger-head/v1
```

Keys use ADR-103's provider mechanism but a distinct purpose/domain. Private material remains outside the repository. Receipts carry public-key ID, algorithm, purpose, issuance time, and rotation/revocation metadata.

## Ledger

The ledger consists of immutable, content-addressed segments. Each segment binds:

```text
segmentId
previousSegmentId
firstSequence
lastSequence
commits[]
segmentMerkleRoot
createdAt
```

A signed head binds `lineageId`, current segment, current sequence, active champion, gate version, and timestamp. Archiving may move segments but cannot delete continuity evidence or report a truncated chain as complete.

Promotion fails closed if the promotion commit and new head cannot be durably committed by ADR-322A.

## Verification

A verifier:

1. Parses the declared schema and rejects unknown or invalid fields.
2. Reconstructs JCS bytes and verifies content IDs and signatures.
3. Resolves every evidence reference and verifies provenance/authority.
4. Recomputes all reproducible terms, statistics, and the decision.
5. Checks corpus-role disjointness and sealed manifests.
6. Checks baseline, safety envelope, gate, policy schema, expiry, and ledger continuity.
7. Reports every term as recomputed, signature-verified, or trusted assertion.

Verification cannot label a promotion independently verified while any authorizing term remains an unapproved assertion.

## Flywheel projection

The adapter projects ruflo policy and evidence into `@metaharness/flywheel` types and round-trips the ruflo envelope unchanged. Because the upstream string-valued policy and four-axis evidence are narrower, projection loss is explicit. Any loss affecting an authorizing term prevents an interoperability claim and can never weaken the ruflo gate.

## Required tests

1. Altering any canonical receipt byte or referenced object fails verification.
2. All authorizing terms reproduce from the fixture or bind to an approved scoped attestor.
3. Float/decimal fixtures produce identical hashes across supported runtimes.
4. Repeated candidate runs retain candidate identity but have distinct run and receipt identities.
5. Segment removal, reordering, or parent alteration breaks head-to-genesis verification.
6. Key revocation and rotation produce the declared historical/current verification behavior.
7. The Flywheel adapter round-trips without loss of ruflo-authorizing evidence; projection loss blocks interoperability claims.
8. Removing optional packages does not disable native receipt or ledger verification.

## Update (2026-08-19) — normative recomputation procedure, ledger status, projection status

Raised by ruflo#3069 during the ADR-322C contract extraction for the RuV Perpetual
Intelligence Runtime (ruflo#3066, PR #3067). Appended rather than edited into the
text above, per this repo's norms around honest documentation.

**The problem.** This ADR's central claim is that a verifier *recomputes* the
statistics rather than trusting the proposer's reported numbers. But the sections
above specify only the bootstrap **seed**, not the generator it drives, the
resampling procedure, or the decimal encoding of the results. An independent
verifier therefore could not reproduce a receipt's statistics from this document —
the only way to recompute correctly was to read `flywheel-receipt.ts`, which is a
copy, not an independent check. The recomputation requirement was unverifiable in
practice. The procedure below closes that; it is transcribed from
`flywheel-receipt.ts:206-307` and is normative from this Update onward.

### 1. Deterministic PRNG

```text
digest = SHA-256("ruflo/bootstrap/v1" || corpusHash || candidateId ||
                 baselineRef || evaluationRunId)      # concatenation, no separator
seedHex = lowercase hex of the full 32-byte digest    # recorded in the receipt
state   = uint32 big-endian read of digest[0..4]      # FIRST FOUR BYTES ONLY
```

Each draw advances a linear congruential generator and returns a value in `[0, 1)`:

```text
state = (1664525 * state + 1013904223) mod 2^32
draw  = state / 2^32
```

The multiplier, increment, and modulus are exact. `state` is unsigned throughout.
The first draw uses the *advanced* state, never the seed value itself.

### 2. Resampling procedure

`iterations` defaults to 10,000, must be an integer, and must be `>= 100`. Let `n`
be the length of `heldOutDeltas`.

```text
if n == 0:
    every resample mean is 0
else:
    for b in 0 .. iterations-1:
        total = 0
        for i in 0 .. n-1:
            total += heldOutDeltas[ floor(draw() * n) ]
        means[b] = total / n
```

Draw order is load-bearing: exactly `n` draws per iteration, consumed in sequence.
An implementation that draws indices in a different order, or draws once per
iteration, produces a different — and non-conforming — result.

```text
pairedBootstrapProbability  = count(means[b] > 0) / iterations      # strictly greater
pairedBootstrapDeltaCILow95 = the floor(0.025 * iterations)-th smallest of means
                              # 0-based order statistic (selection, not sorting;
                              # any correct selection algorithm is conforming)
```

### 3. Decision

```text
relativeLift = (candidateScore - baselineScore) / max(|baselineScore|, metricEpsilon)
metricEpsilon defaults to 1e-12
significant  = pairedBootstrapProbability >= 0.95 AND pairedBootstrapDeltaCILow95 > 0
accepted     = relativeLift >= 0.02 AND significant AND frozenAnchorRegression <= 0
decision     = "accepted" if (accepted AND every value in gates is true) else "rejected"
```

Comparisons are on the numeric values, before decimal encoding.

### 4. Decimal encoding of results

The `statistics` object must reproduce **byte-for-byte** under JCS, so its encoding
is part of the contract. Every fractional field is encoded by:

```text
1. fixed-point render at scale 12 (twelve digits after the decimal point)
2. strip trailing zeros, then a trailing decimal point if one remains
3. if the result is "" or "-0", emit "0"
```

So `0.0928571428571...` renders `"0.092857142857"`, `1` renders `"1"`, and `0`
renders `"0"`. This applies to `relativeLift`, `pairedBootstrapProbability`,
`pairedBootstrapDeltaCILow95`, and `frozenAnchorRegression`, and to the
`baselineScore`, `candidateScore`, and `heldOutDeltas` fields.

**A producer must compute the statistics from the encoded values, not from its
internal full-precision values.** A verifier has only the encoded strings, so any
precision the producer used but did not record is precision the verifier cannot
reproduce. Stated as a rule: decode `baselineScore`, `candidateScore`, and
`heldOutDeltas` back from their encoded form and compute from *those*, so producer
and verifier are evaluating identical inputs by construction.

**Known divergence (2026-08-19).** `createFlywheelReceipt` currently violates this:
it computes `statistics` from full-precision means while storing scale-12 strings,
so a receipt whose mean needs more than twelve decimals fails its own
`verifyFlywheelReceipt` with `statistical decision does not recompute`. Reproduced
with twenty-four 3-decimal task scores (mean `0.7687083333333332`, stored
`"0.768708333333"`), which shifts `relativeLift` by one unit in the last place.
Receipts with exactly-representable means are unaffected, which is why existing
fixtures pass. This is a defect against the rule above, not a change to it.

### 5. Ledger: what is implemented, what is aspirational

The §Ledger section above describes content-addressed segments binding
`segmentId`/`previousSegmentId`/`firstSequence`/`lastSequence`/`commits[]`/
`segmentMerkleRoot`/`createdAt`, plus a **signed** head under
`ruflo/flywheel-ledger-head/v1`. **That is not what `main` implements.** The
implementation (`flywheel-transaction.ts:553-568`, `619-636`) is a flat,
sequence-numbered `commits[]` array inside one transaction-state file:

```text
commitId   = SHA-256(JCS(commit with commitId omitted))
ledgerHead = SHA-256(JCS({ previous: <prior head>, commitId: <commitId> }))
genesis    = sha256:<64 zeros>
```

There are no segments, no `segmentMerkleRoot`, and **the head is not signed** — the
`ruflo/flywheel-ledger-head/v1` domain is specified but unused on `main`. Chain
integrity today rests on the hash chain plus the signed receipt each commit
consumes, not on a head signature.

Consumers anchoring across a repo boundary must therefore anchor the **receipt**
(`ruflo.flywheel-receipt/v1`), the only record type whose signature is implemented.
Anchoring a ledger head today means anchoring an unsigned hash-chain value, and
must be described that way. Segments and head signing remain the intended target;
this Update records the divergence rather than leaving consumers to read the ADR as
a description of what exists.

### 6. Flywheel projection is disabled

Per ADR-322 §"Current Metaharness capability inventory", external Flywheel receipt
projection is intentionally disabled until a projection can preserve ruflo's gate
and evidence semantics without information loss. No upstream round-trip is
available, so a consumer cannot export state and feed it back to confirm the
round-trip preserves meaning. Re-enabling it is gated on the ADR-322 phase-3
projection cross-check landing in CI; until then §Flywheel projection describes an
intended capability, not a shipped one.

### 7. Strictness is versioned

Unknown fields fail verification for a given schema version (§Canonical format).
A consequence worth stating: a verifier implementing `ruflo.flywheel-receipt/v1`
will reject a receipt from a future version that adds fields. That is the correct
behavior for a security property — fail closed on the unrecognized — but it means
schema evolution requires consumers to upgrade before they can verify newer
receipts, not merely to tolerate them.

A language-neutral extraction of this protocol, with JSON Schemas, worked examples,
and a conformance checklist, is maintained at
[`../spec/witness-receipt-contract.md`](../spec/witness-receipt-contract.md).


---

# SOURCE: v3/docs/adr/ADR-323-typed-memory-provenance.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `126110d64a67dd3deb5be4839cf3559bd381ea45`

# ADR-323: Typed Memory Provenance in AgentDB

**Status:** Accepted
**Date:** 2026-07-28
**Supersedes:** the dream-cycle research PR #2804's `ADR-322-dream-cycle-memory-typed-provenance.md` (closed as superseded — its filename collided with the already-merged `ADR-322-metaharness-flywheel-integration.md` from #2817, and its proposed schema target was wrong; see "Correction" below).

## Context

Ruflo's AgentDB (`memory_entries` table) stores every memory entry as flat text with an HNSW vector embedding — no typing of *who or what produced it*. In multi-agent deployments, a user's stated claim, an agent's own output, a raw tool result, and a system observation can all land in the same shared namespace (e.g. `collaboration`, `patterns`) indistinguishably.

The 2026-07-28 dream-cycle research report (PR #2804) identified this as "provenance-role collapse," citing:
- **arXiv 2605.25869 (MemIR, May 2026)** — a 3-layer typed representation (raw evidence → retrieval cues → factual claims) with provenance-scoped utilization outperforms flat baselines on LoCoMo + BEAM-100K.
- **arXiv 2607.01071 (MemSyco-Bench, Jul 2026)** — retrieved memories induce sycophancy: agents over-align with user-stated facts at the cost of factual accuracy when provenance isn't enforced at retrieval time.

## Correction to the original dream-cycle proposal

The dream-cycle PR's proposed decision was:

```sql
ALTER TABLE vector_indexes ADD COLUMN provenance_type TEXT ...
```

This targets the wrong table. `vector_indexes` is per-*namespace* HNSW index metadata (id, name, dimensions, HNSW params, `total_vectors`) — one row per namespace, not one row per memory entry. The correct target, and what this ADR actually implements, is `memory_entries` — the per-record table that already carries `tags`/`metadata`/a `type` enum (`semantic`/`episodic`/`procedural`/`working`/`pattern`) in exactly the shape a new typed column belongs in.

The dream-cycle PR (#2804) was closed without merging; this ADR and its implementation replace it, corrected against the real schema.

## Decision

Add a `provenance_type` column to `memory_entries`, mirroring the existing `type` column's convention (`TEXT DEFAULT ... CHECK(...)` on fresh installs; plain `TEXT DEFAULT` — no CHECK — in the `ensureSchemaColumns()` migration path for existing DBs, consistent with how `type`/`status` are backfilled):

```sql
-- Fresh installs (memory-initializer.ts CREATE TABLE)
provenance_type TEXT DEFAULT 'unknown' CHECK(provenance_type IN (
  'user_claim', 'agent_output', 'system_observation', 'tool_result', 'unknown'
))

-- Existing DBs (ensureSchemaColumns() migration)
ALTER TABLE memory_entries ADD COLUMN provenance_type TEXT DEFAULT 'unknown'
```

Application-level validation (`isValidProvenanceType()`, exported from `memory-initializer.ts`) is the actual enforcement mechanism — both `storeEntry()` and `bridgeStoreEntry()` reject an invalid value with a typed error before touching either backend, rather than surfacing a raw SQLite CHECK-constraint failure. This is why the migration path omits the CHECK: it's belt-and-suspenders on fresh installs, not the primary guard.

### Write path

- CLI: `memory store --provenance <type>` (choices-validated by the CLI parser itself, then re-validated in `storeEntry()`).
- MCP tool: `memory_store`'s `provenance_type` parameter.
- Both default to `'unknown'` when omitted — the same value existing (pre-ADR-323) entries get on migration, so there is no behavior change for callers that don't opt in.

### Read path

- CLI: `memory search --provenance-filter <comma-separated types>`.
- MCP tool: `memory_search`'s `provenance_filter` array parameter.
- Applies across all three internal search strategies (RaBitQ pre-filter, in-memory HNSW, and the brute-force/BM25-hybrid SQL path) — see "Implementation note" below for why this needed a specific design after an initial approach crashed the CLI.
- Applies to SmartRetrieval (RRF/MMR) by binding the provenance filter into every raw search used for query expansion. The external package does not need to understand the field and cannot widen the caller's trust scope.

## Implementation note: why RaBitQ/HNSW aren't skipped for a filtered search

The first implementation attempt, when a provenance filter was requested, skipped the RaBitQ and in-memory-HNSW acceleration paths entirely (neither carries `provenance_type` on their candidates) and went straight to a brute-force SQL query with the filter applied server-side. This was simpler to write, but reproducibly **crashed the CLI process on exit** (`Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c, line 76` on Windows) — after printing correct JSON output. Confirmed via bisection: removing the `if (!provenanceFilter?.length) { …RaBitQ…HNSW… }` skip and always executing those two dynamic-import branches (regardless of whether a filter was requested) eliminated the crash across repeated runs.

The root cause was not fully isolated (a libuv async-handle timing issue tied to skipping the `import('./rabitq-index.js')` / `searchHNSWIndex()` calls, likely interacting with the embedder's own async initialization) — rather than ship a fix for a symptom without full confidence in the mechanism, the design was changed to avoid the crashing code shape entirely:

- **RaBitQ path**: `provenance_type` is now fetched in the *same* per-candidate SQL query that already looks up `content`/`embedding` for reranking — no extra round-trip, and the branch always runs.
- **HNSW path**: after the existing threshold filter, a single batched lookup by `(namespace, key)` — the schema's natural unique pair — fetches `provenance_type` for the candidate set, and results are filtered against it. This branch also always runs; on lookup failure it fails closed (returns no results) rather than silently ignoring the filter.
- **Brute-force path**: filters directly in the SQL `WHERE` clause (`provenance_type IN (...)`) — no candidates to reconcile after the fact.

Net effect: correctness is now handled per-path rather than by bypassing acceleration, and the crash reproduced 100% of the time before the fix and 0% of the time (multiple repeated runs) after it.

## Consequences

**Positive:**
- Retrieval can now distinguish "the user said X" from "an agent inferred X" from "a tool reported X," addressing MemSyco-Bench's sycophancy finding directly.
- Fully backward compatible: existing entries read as `'unknown'`; no caller is required to pass a provenance type.
- No acceleration path (RaBitQ/HNSW) is sacrificed for provenance-filtered queries.

**Negative / open gaps (stated plainly, not glossed over):**
- Filtering an ANN candidate window can underfill the requested page. Filtered RaBitQ/HNSW searches therefore fall through to the authoritative filtered SQL scan whenever the accelerated window does not fill the requested limit.
- Plugin SDK enforcement (requiring official plugins to pass `provenance_type` on writes, with a `pre-edit` lint gate) — proposed in the original dream-cycle research — is **not implemented** in this ADR. Scoped out as a separate, larger change touching the plugin SDK contract.
- The `audit` worker webhook-trigger idea from the same dream-cycle report is unrelated to provenance typing and is not part of this ADR.
- No governance/rollback layer (the dream-cycle report's AOEP-v0 reference) — this ADR is the typing primitive only, not a full governance system.

## References

- arXiv 2605.25869 — MemIR: Typed Memory Intermediate Representation
- arXiv 2607.01071 — MemSyco-Bench: Sycophancy in Agent Memory
- Dream-cycle research: PR #2804 (closed, superseded by this ADR)
- `v3/@claude-flow/cli/src/memory/memory-initializer.ts` — schema, `storeEntry()`, `searchEntries()`
- `v3/@claude-flow/cli/src/memory/memory-bridge.ts` — `bridgeStoreEntry()`, `bridgeSearchEntries()`
- `v3/@claude-flow/cli/src/commands/memory.ts` — `memory store --provenance`, `memory search --provenance-filter`
- `v3/@claude-flow/cli/src/mcp-tools/memory-tools.ts`, `v3/@claude-flow/cli-core/src/mcp-tools/memory-defs.ts` — MCP tool schemas
- `v3/@claude-flow/cli/__tests__/adr-323-memory-provenance.test.ts` — end-to-end regression guard, including the crash-repro test


---

# SOURCE: v3/docs/adr/ADR-324-agentic-policy-engine-codex-swarm.md

Ruflo commit: `e558f0c0fc29c1a658085f6e6f80ad27d4fe811f`
Blob: `bf82b697b32d01f272197ae7d13318416418ad6f`

# ADR-324: Agentic Policy Engine and Policy-Governed Codex Swarms

**Status:** Accepted
**Date:** 2026-07-28
**Implementation:** Complete on `feat/adr-324-agentic-policy-engine`
**Related:** ADR-053 (AgentDB), ADR-101 (federated claims), ADR-131 (tool-output guardrail), ADR-144 (authorization propagation), ADR-145 (memory governance), ADR-176 (self-benchmarking loop), ADR-322/A/B/C (MetaHarness proposer, promotion transaction, receipts)

## Context

Ruflo already contains useful but disconnected controls:

- AgentDB memory, owner/access metadata, typed provenance, HNSW/RaBitQ and legacy SQL.js paths.
- `AgentAuthorizationPropagator`, whose monotonic `AuthScope` was not wired into production dispatch.
- Federation message policy, guidance authority levels, launch budgets, plugin integrity, and tool-output guardrails.
- ADR-322's signed evaluation receipts and compare-and-swap promotion transaction.
- A Codex adapter that registers Ruflo MCP and generates `AGENTS.md`, but whose concurrent workers could share one checkout and whose generated defaults did not define a single authorization authority.

No component answered the general question:

> May this identity perform this action on this resource, with this evidence,
> authority, cost, concurrency, and delegation chain, right now?

The missing authority also made concurrency unsafe. A coordinator could record work, but it could not prevent child agents or MetaHarness proposers from widening tools, network access, namespaces, spend, or promotion rights.

## Decision

Ruflo adopts `@claude-flow/security`'s `AgenticPolicyEngine` as the local authorization authority.

```text
identity + action + resource + evidence + capability envelope
                  + approval + budget + policy version
                               |
              allow | deny | require_approval
                               |
              hash-chained decision receipt
```

The engine is deterministic and side-effect free except for its state transaction. Adapters translate existing subsystem concepts into this request model. Existing specialized controls remain responsible for their domain mechanics; they no longer act as independent authorization authorities.

### Modes and backwards compatibility

| Mode | Logical decision | Runtime behavior |
|---|---|---|
| `legacy` | Existing behavior/default allow | allow and issue receipt |
| `observe` | Evaluate default-deny policy | allow, record would-deny |
| `enforce` | Evaluate default-deny policy | enforce allow/deny/approval |

Existing installations are auto-migrated to a versioned policy state in `legacy` mode. Migration is additive and detects legacy AgentDB/RVF locations and strict-mode flags without rewriting memory rows, indexes, receipts, namespaces, controller state, ReasoningBank, SkillLibrary, or HNSW data.

New policy fields default to absent/`unknown`. ANN index refreshes must never replace authoritative AgentDB rows. CLI/MCP command names and existing namespaces remain valid.

No automatic update may:

- upgrade across a major version;
- replace user `AGENTS.md` text or unknown TOML keys;
- delete or recreate a memory database;
- rewrite v1 Flywheel receipts or ledger entries;
- enable unattended fanout or enforcement without an explicit policy transition.

Generated configuration may raise a persisted mode (`legacy` → `observe` →
`enforce`) but cannot lower it. A downgrade is an explicit, interactive local
administrator action.

### Rule evaluation

Rules match action/resource patterns, principals, identity types, roles, environments, provenance, and hard constraints. Evaluation order is:

1. Validate the request.
2. Enforce the capability envelope.
3. Apply matching rules in deterministic priority/id order.
4. Deny overrides approval and allow.
5. Approval overrides allow until a valid scoped approval is consumed.
6. Apply budget ceilings.
7. Apply mode (`legacy`, `observe`, `enforce`).
8. Persist the decision receipt before returning authority.

Unmatched actions allow only in `legacy`; `observe` records default-deny but does not block; `enforce` blocks.

### Capability envelopes and delegation

An envelope may constrain actions, resources, tools, MCP servers, read/write namespaces, environments, network/destructive access, cost, tokens, concurrency, expiry, and delegation depth.

Every child envelope must be a monotonic reduction. A child cannot:

- add a pattern not granted by its parent;
- raise any numeric ceiling;
- extend expiry or depth;
- enable network/destructive access disabled by its parent.

Envelope violations are always enforced, including in `legacy` and `observe`;
those modes apply to policy-rule rollout, not delegated authority boundaries.

Agents and optimizers cannot approve themselves. Approvals are scoped, expiring, revocable, and limited-use.
Approval creation requires a deployment-supplied authenticated issuer
verifier. An arbitrary `issuedBy` string, environment allowlist, or local TTY
is not an authority credential. The default local CLI therefore cannot issue
approvals. The unregistered administrative MCP adapter derives the issuer from
authenticated user context and cannot accept a caller-supplied issuer.

### Budgets

Budgets match principal, action, and resource and limit USD/tokens per fixed window. Authorization and usage update occur under one cross-process policy-state lock. A denied action does not consume budget. Domain-specific budget providers may reserve additional resources but cannot weaken this ceiling.

Cost, token, and concurrency fields are declared reservations supplied by a
trusted adapter, not measurements from a provider invoice. A rule or budget
that constrains one of these dimensions fails closed when its value is absent.
Adapters must reserve before execution and reconcile separately; provider-side
hard caps remain the final ceiling against a compromised or under-reporting
adapter.

### Receipts and ledger

Every decision binds:

- canonical request and evidence;
- logical and enforced outcomes;
- matched rules and obligations;
- approval id, if consumed;
- policy bundle hash;
- previous receipt hash, sequence, and timestamp.

Canonical JSON sorts object keys and rejects non-finite numbers. SHA-256 content identifiers and a hash chain make alteration evident. A configured local key adds an HMAC authentication tag. Cross-install/federated policy bundles continue to require their existing Ed25519 trust model; a local HMAC is not represented as third-party attestation.

When a signing key is configured, unsigned receipts are invalid. Conversely, a
signed ledger cannot be declared valid without the matching verification key.
Signed policy evidence uses a trusted key selected by `keyId` from
`CLAUDE_FLOW_POLICY_EVIDENCE_KEYS`; its HMAC binds id, provenance, attestor,
observation time, content hash, and key id. The legacy caller-authored
`signed: true` field is retained for transport compatibility but confers no
authority.

### Enforcement surfaces

The first authoritative surface is the CLI MCP dispatcher: policy evaluates before tool handlers can produce side effects. The standalone MCP registry exposes the same middleware contract and can require an authorizer at construction; required mode cannot later remove its authorizer. Deployments must opt into that required mode. This ADR does not claim that every independently embedded MCP server or native Codex/Claude action is automatically wired.

Learning, metrics, and pattern storage remain fail-open. Policy enforcement is synchronous and authoritative:

- a first-run installation with no trust anchor may enter compatibility mode;
- once enforcement creates a trust anchor, missing, modified, or unauthenticated
  state fails closed and cannot silently return to legacy;
- host or user-account compromise remains outside this local trust boundary.

### AgentDB compatibility

ADR-323 provenance values are valid evidence types:

`user_claim`, `agent_output`, `system_observation`, `tool_result`, `unknown`.

Policy adapters preserve all previous AgentDB capabilities and add namespace decisions without changing retrieval algorithms. `tool_result` and `system_observation` may be required for factual or production actions. A user claim is not silently upgraded into an observation.

## Codex and Ruflo workflow

Ruflo is the ledger/coordinator/policy decision point. Codex workers execute.

1. Search AgentDB patterns.
2. Initialize one bounded hierarchical swarm.
3. Split only independent work.
4. Assign one git worktree and declared reduced envelope to each writer.
5. Run workers under hard concurrency/output/time budgets.
6. Consume committed handoffs in dependency order.
7. Run scoped tests, full tests, security guards, and MetaHarness.
8. Store the validated pattern and retain decision/evaluation receipts.

Read-only workers may share a checkout. Writers may not. A designated integration agent owns shared manifests and lockfiles. Dependency cycles, missing dependencies, shared writer paths, non-zero worker exits, and dependency failures are errors rather than implicit success.

`[swarm.automation]` defaults:

```toml
enabled = false
max_concurrent = 4
max_writers = 2
worktree_isolation = true
dependency_failure = "cancel"
agent_timeout_seconds = 1800
max_output_bytes = 1048576
```

Worktree cleanup removes only registry-owned, clean worktrees. Dirty worktrees remain for recovery. No force removal or broad path deletion is permitted.

The worker preflight, sanitized environment, declared envelope, and Codex
sandbox are workflow controls, not an operating-system security boundary. A
locally compromised child process can invoke tools outside Ruflo unless the
host also applies container/VM, filesystem, network, and provider controls.
For Ruflo MCP calls made from a linked worktree, the authoritative policy root
is derived from Git's canonical common directory, so the worker cannot
accidentally initialize an independent legacy policy state.

## Concurrent MetaHarness development

MetaHarness/Darwin proposes; Ruflo policy and ADR-322 dispose.

- Candidate/task evaluation uses a bounded worker pool.
- Result aggregation is deterministic in input/candidate-id order, independent of completion order.
- Timeout cancellation covers queued and cooperative running work.
- The run receives a local concurrency ceiling and evaluation wall-time budget.
- Proposers and evaluators receive no `promote` or `materialize` capability.
- `metaharness.flywheel.run` and `metaharness.candidate.promote` are distinct policy actions.
- Promotion still requires ADR-322A confirmation, trusted signature, fresh baseline, fresh ledger head, and atomic compare-and-swap.
- A policy denial happens before proposer, search, filesystem, or promotion side effects.

Legacy v1 Flywheel receipts remain verifiable byte-for-byte. ADR-324 receipts are additional authorization evidence; they do not rewrite the Flywheel ledger.

## Security model

The design addresses:

1. malicious candidate policy;
2. compromised child/proposer process;
3. stale or replayed approval;
4. concurrent budget/promotion races;
5. tampered decision ledger;
6. namespace poisoning;
7. resource-exhaustion through fanout;
8. accidental destructive upgrades of prior AgentDB installations.

It does not claim that a local HMAC protects against compromise of the host or signing key. Remote trust requires the established Ed25519 attestation paths.

## Consequences

Positive:

- One auditable authorization result across CLI, MCP, Codex, AgentDB evidence, and MetaHarness.
- Existing installations continue to work and can rehearse policy in observation mode.
- Concurrent development has executable worktree and resource boundaries.
- Optimizers can improve policy/configuration without becoming promotion authorities.

Costs:

- Every consequential action adds a small locked state transaction.
- Administrators must define rules before enabling enforcement.
- Legacy permissive behavior remains until a deliberate mode transition.

## Implementation

The normative implementation is split across existing package boundaries:

| Concern | Implementation |
|---|---|
| Rules, envelopes, approvals, budgets, canonical receipts | `@claude-flow/security/src/policy` |
| Cross-process transaction, migration, CLI/MCP adapter | `@claude-flow/cli/src/services/policy-runtime.ts` |
| Administrator CLI | `ruflo policy status/init/evaluate/rule/budget/revoke/audit/verify`; approval issuance requires an authenticated adapter |
| Policy MCP tools | Remote default: `policy_evaluate`, `policy_status`; administrative handlers exist for authenticated deployments but are not registered by default |
| CLI MCP enforcement | `@claude-flow/cli/src/mcp-client.ts` |
| Standalone MCP enforcement contract | `ToolRegistry.setAuthorizer` / `MCPServer.setToolAuthorizer` |
| Bounded MetaHarness evaluation | `bounded-worker-pool.ts`, `harness-flywheel.ts`, `harness-flywheel-runtime.ts` |
| Codex automation | bounded dual-mode orchestrator plus the worktree coordinator |
| Upgrade behavior | additive Codex settings migration and CLI policy-state auto-migration |

The policy state lives at `.claude-flow/policy/state.json`. Mutations acquire
`.claude-flow/policy/state.lock` using exclusive creation and replace state by
atomic rename. Decision, approval consumption, budget usage, and receipt append
therefore commit as one transaction. A stale lock may be recovered after 30
seconds; lock acquisition otherwise fails after five seconds.

When enforcement is first enabled, an HMAC key and state authentication record
are stored outside the workspace under
`~/.config/ruflo/policy-trust/<project-hash>/`, where the project hash uses
the canonical real path and cannot be redirected by a worker environment
variable. Subsequent state loads authenticate the complete state. On first
enforcement the anchor is written before enforce state, so any crash leaves
either a valid pair or a fail-closed mismatch. A later crash
between state and anchor replacement may fail closed and require administrator
recovery; it cannot produce a silent downgrade.

Generated and migrated Codex configurations install the dedicated
`claude-flow-mcp` binary, preserve unrelated MCP servers, set policy mode to
`legacy`, and leave swarm automation disabled. Windows uses `cmd /c`; POSIX
uses `npx` directly. Existing `AGENTS.md` content is not replaced by runtime
migration.

Policy administration is not exempt from authorization. Bootstrap and recovery
mutations use the interactive local `ruflo policy` command. Remote MCP registers
only evaluation and status by default; administrative handlers require a
deployment-specific authenticated human identity adapter. Approval issuance
also requires the issuer allowlist. A standalone MCP server can set
`requireToolAuthorization = true`, in which case construction fails unless an
authorizer is supplied.

### Validation evidence

Validated on 2026-07-28:

- Security: 22 files, 537 tests.
- Codex generation, migration, dual-mode, and worktrees: 7 files, 211 tests.
- Standalone MCP registry/server: 2 files, 69 tests.
- Policy runtime, concurrent budget accounting, bounded worker pool,
  MetaHarness ADR-322 paths, and ADR-323 compatibility: 5 files, 46 tests.
- TypeScript: security, Codex, MCP, and the changed CLI surface compile cleanly.
- `git diff --check`: clean.

The policy microbenchmark records:

```text
pure evaluation:       1,590,091 decisions/second (0.629 µs/decision)
transaction receipt:      43,251 decisions/second (23.121 µs/decision)
receipt ledger:         valid
```

These figures are local microbenchmarks, not a production latency guarantee.
The receipt number excludes filesystem lock contention and disk latency.

## Acceptance tests

1. Legacy install migration preserves existing memory and defaults to `legacy`.
2. Observe mode records deny while allowing the action.
3. Enforce mode default-denies unmatched actions.
4. Deny overrides allow and approval.
5. A child cannot expand any envelope dimension.
6. Self-approval, expired approval, replay beyond `maxUses`, and revoked approval fail.
7. Concurrent budget decisions cannot overspend a ceiling.
8. Altering one receipt byte breaks ledger verification.
9. Native and fallback AgentDB paths preserve provenance and prior capabilities.
10. CLI and MCP policy decisions occur before side effects.
11. Two concurrent writers cannot share a worktree.
12. Missing dependencies and cycles fail before workers launch.
13. Worker fanout never exceeds configured concurrency and output bounds.
14. Dirty registry-owned worktrees survive cleanup.
15. MetaHarness peak concurrency never exceeds its envelope.
16. Timeout cancels queued MetaHarness work.
17. MetaHarness cannot promote without a separate policy allow/approval and ADR-322A authorization.
18. Removing or lowering generated configuration cannot downgrade an enforced
    policy; removing or modifying anchored state fails closed.
19. A budgeted or constrained request with missing metering is denied.
20. Worker environments strip common secret variables and policy authority
    variables before launch.

