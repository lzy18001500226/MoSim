# COAGENT-ARCH-LONGRUN-01 Department Dispatch Plan

Date: 2026-05-30
Status: active dispatch plan

## Dispatch Principle

This task is not a one-shot research summary. Every department must return
architecture decisions, risks, and concrete updates to project files or review
packets.

## Shared Input For All Departments

- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_charter.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/shared_task_board.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_pack.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/architecture_problem_matrix.md`
- `CoAgent/docs/architecture/coagent_solution_synthesis.md`
- `CoAgent/docs/architecture/coagent_dynamic_task_team_v2_design.md`

## Department Work Orders

### DispatchAgent

Objective:

Define the canonical task lifecycle, topology selector, task-team creation
rules, mailbox flow, and closeout state transitions for long-running CoAgent
tasks.

Required output:

- refine topology thresholds;
- define when to create task-scoped conversations;
- define when to keep work in main thread;
- define when to use short-lived subagents;
- define result import and closeout rules.

Forbidden:

- do not become the implementation owner;
- do not change the canonical goal without PMO/user record.

### ProductStrategyAgent

Objective:

Convert CoAgent architecture into product-facing value and guard against
overengineering that does not help MoSim or portable CoAgent reuse.

Required output:

- appetite and non-goals for CoAgent V1;
- product definition of done for PX4 parameter identification;
- product definition of done for UE scene truth / RflySim-like simulation;
- criteria for promoting conditional departments.

Forbidden:

- do not define tool/runtime implementation details;
- do not turn every future idea into P0 scope.

### RuntimePlatformAgent

Objective:

Design how Codex conversations, CLI/App/VSCode state, resume paths, worktrees,
and transport adapters map to CoAgent task objects.

Required output:

- Codex feature-use matrix;
- conversation creation/fork/recovery design;
- transport risk list;
- implementation gates for app-server transport and automatic conversation
  creation;
- runtime state fields needed for task teams.

Forbidden:

- do not implement app-server transport;
- do not mutate external Codex state except through approved diagnostics.

### ContextMemoryAgent

Objective:

Design the context and memory system that lets new conversations understand
prior work without full transcript dumps or stale assumptions.

Required output:

- shared context versus slice context;
- context-pack size/quality gates;
- context delta and refresh flow;
- stale-context detection;
- memory promotion and retrieval rules.

Forbidden:

- do not propose loading all skills or all docs by default;
- do not treat hooks as optional context.

### ToolchainMCPAgent

Objective:

Design tool/MCP capability boundaries for CoAgent, especially MWORKS, UE, Fab,
Git, filesystem, and future tool surfaces.

Required output:

- capability-card template;
- MCP health-gate protocol;
- fallback/stop rules when tool capability is absent;
- UE/Fab scene-truth workflow risks;
- MWORKS activation/license blocker handling.

Forbidden:

- do not expand MCP tool surfaces in this task;
- do not call interactive MCP tools just to prove activity.

### KnowledgeSecretaryAgent

Objective:

Design how accepted decisions, repeated lessons, external research, and user
corrections are promoted into docs, indexes, skills, hooks, doctor checks, or
runtime tasks.

Required output:

- document ownership map;
- stale-doc detection plan;
- knowledge promotion decision tree;
- secretary boundary: what it records versus what it must not decide.

Forbidden:

- do not promote raw chat as accepted policy;
- do not own cross-department task routing.

### VerificationAgent

Objective:

Design independent verification for both task outputs and the CoAgent operating
system itself.

Required output:

- acceptance rubric for architecture decisions;
- evidence checklist for PX4 and UE stress tests;
- process metrics: drift, blocked time, fake parallelism, handoff failure,
  review escape, closeout latency;
- minimal closed-loop test criteria.

Forbidden:

- do not accept claims without evidence paths;
- do not merge verification and implementation ownership.

### SafetyComplianceAgent

Objective:

Design safety, policy, and human-intervention boundaries for long-running
multi-conversation work.

Required output:

- unsafe-action gate;
- license/auth/GUI/manual-review blocker protocol;
- dedupe and rate-limit design for future notifications;
- approval gates for gated runtime features;
- external path and secret-handling constraints.

Forbidden:

- do not implement email sender in this task;
- do not approve destructive or external path actions implicitly.

### DevOpsReleaseAgent

Objective:

Design Git, worktree, large-change, integration, and release hygiene for many
conversations working under one canonical task.

Required output:

- one task one integration owner rule;
- worktree binding and merge plan;
- large import/rename containment;
- staged commit policy;
- conflict and rollback design.

Forbidden:

- do not run broad Git staging or commits from this design task;
- do not treat worktree identity as agent identity.

### ExternalIntelligenceAgent

Objective:

Design the self-evolution loop that continuously learns from model vendors,
agent frameworks, open-source projects, and large-company management practice
without drifting into broad summarization.

Required output:

- problem-led research intake;
- source credibility and relevance scoring;
- adoption proposal template;
- update cadence for vendor/open-source learning;
- how rejected ideas are recorded for future projects.

Forbidden:

- do not summarize all external projects without tying them to current
  CoAgent problems;
- do not recommend direct API/key integration into untrusted third-party
  projects.

## First Dispatch Sequence

Start with these four streams:

1. DispatchAgent: topology and task-team state.
2. ContextMemoryAgent: context pack and memory boundaries.
3. RuntimePlatformAgent: Codex conversation/worktree mapping.
4. VerificationAgent: acceptance and drift-control rubric.

Then integrate:

5. SafetyComplianceAgent and DevOpsReleaseAgent for gates and merge strategy.
6. ProductStrategyAgent for appetite and product-value filter.
7. ToolchainMCPAgent for tool/MCP capability boundary.
8. ExternalIntelligenceAgent for problem-led external learning.
9. KnowledgeSecretaryAgent for doc/index/skill promotion.

## Result Contract

Each department must return a result packet with:

- conclusion;
- changed or proposed artifact paths;
- decisions;
- risks;
- unresolved questions;
- required review owner;
- next action.
