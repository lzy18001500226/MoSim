# COAGENT-ARCH-LONGRUN-01 Context Pack

Date: 2026-05-30
Built by: MainAgent / DispatchAgent
Target: all active permanent CoAgent departments and future task-scoped
architecture conversations

## Purpose

Give every CoAgent architecture worker enough shared context to continue the
10-hour design task without relying on hidden chat memory or copying the full
conversation transcript.

## Canonical Task Goal

Sustain at least 10 hours of CoAgent architecture design work and produce
reviewable architecture artifacts for a task-first, multi-conversation
multi-agent operating system.

## Current Operating Rules

- Project boundary: operate inside `/mnt/c/Users/HP/Desktop/MoSim`.
- The durable source of task truth is project files plus
  `Results/agent_runtime/`, not Codex App sidebar state.
- Live Codex App / VSCode visibility is useful for review, but not sufficient
  as durable task state.
- Permanent departments are governance and capability lanes, not the unit of
  execution.
- A user task may create a temporary task team with multiple scoped
  conversations when justified by context, risk, review, or parallelism.
- Short-lived subagents are disposable helpers inside one conversation. They
  cannot own Git, review, safety, testing, documentation, or long-running
  state.
- Hooks and safety rules are hard constraints, not optional context.

## Active Department Conversations

The user confirmed the recreated 10 department conversations are visible.
Registry state is now `active_visible` for:

- DispatchAgent
- ProductStrategyAgent
- RuntimePlatformAgent
- ContextMemoryAgent
- ToolchainMCPAgent
- KnowledgeSecretaryAgent
- VerificationAgent
- SafetyComplianceAgent
- DevOpsReleaseAgent
- ExternalIntelligenceAgent

MainAgent was already `active_visible`.

## Key Source Documents

Read only the parts needed for the local slice:

- `CoAgent/STATUS.md`
- `CoAgent/docs/architecture/coagent_architecture_issue_register.md`
- `CoAgent/docs/architecture/coagent_problem_driven_operating_model.md`
- `CoAgent/docs/architecture/coagent_department_capability_model.md`
- `CoAgent/docs/architecture/coagent_conversation_mapping.md`
- `CoAgent/docs/architecture/coagent_concrete_agent_design.md`
- `CoAgent/docs/architecture/coagent_agent_design_protocol.md`
- `CoAgent/docs/architecture/coagent_dynamic_task_team_v2_design.md`
- `CoAgent/docs/architecture/coagent_solution_synthesis.md`
- `CoAgent/docs/architecture/coagent_user_intervention_ux.md`
- `CoAgent/docs/status/codex_visible_thread_sop.md`

## Accepted Design Baseline

The current architecture direction is:

```text
user task
  -> canonical task charter
  -> topology selection
  -> context pack
  -> one or more scoped conversations
  -> optional short-lived subagents inside scoped conversations
  -> evidence/result packets
  -> review and integration
  -> knowledge promotion
```

Important distinction:

```text
department = long-lived capability / governance boundary
conversation = execution and review surface
task team = temporary organization around one durable task
subagent = short-lived bounded helper
worktree = file isolation surface
packet/event log = durable communication and authority
```

## Stress Tests

### PX4 Log Parameter Identification

The task is complete only if the system can distinguish:

- directly observed parameters;
- estimated parameters;
- simulation-calibrated parameters;
- assumed vehicle/spec parameters;
- not identifiable parameters;
- parameters requiring additional experiment or human input.

It must also define how conversations split across log audit, methods research,
identifiability, estimator implementation, simulator mapping, simulation
tuning, verification, DevOps, and knowledge promotion.

### UE Scene Truth / RflySim-Like Productization

Rendering is not enough. Acceptance depends on:

- map/source availability;
- UE/Fab/MCP capability proof;
- collision/planning/navigation truth export;
- occupancy or navmesh artifacts;
- FastLIO/planning/navigation integration;
- wind and motor-degradation experiment control;
- reproducible scenario configuration;
- verification evidence and manual review gates.

## Forbidden Assumptions

- Do not assume all desired simulator parameters can be identified from one
  PX4 log.
- Do not assume Fab/UE rendering proves planning truth.
- Do not assume a visible conversation is durable task state.
- Do not assume a subagent can replace a durable department conversation.
- Do not assume more departments or more conversations means better work.
- Do not implement gated runtime features during this design task.

## Context Refresh Rules

Refresh this pack when:

- the canonical task goal changes;
- a design decision supersedes a prior document;
- a new department is promoted or demoted;
- a task-scoped conversation is approved;
- a blocker changes the architecture assumptions;
- a review rejects a design decision.

Do not refresh by appending raw chat. Write a context delta that states:

- what changed;
- why it matters;
- which documents are superseded;
- which departments or task slices must update behavior.

## Output Contract For Department Work

Each department result should include:

- one-sentence conclusion;
- evidence paths;
- decisions proposed;
- risks and unknowns;
- required user decision, if any;
- next action and owner;
- whether the result changes the canonical architecture or only local guidance.
