# COAGENT-ARCH-LONGRUN-01 Product Appetite And Non-Goals

Date: 2026-05-30
Status: phase 2 draft

## Purpose

Keep CoAgent architecture tied to useful MoSim delivery and portable reuse,
instead of becoming an oversized agent bureaucracy.

## CoAgent V1 Product Promise

CoAgent V1 should make long-running technical tasks more reliable by providing:

- task-first canonical goals;
- visible multi-conversation work surfaces when useful;
- recoverable context and state;
- packet-based communication;
- reviewable evidence;
- safer Git/tool/human-intervention flows;
- repeatable knowledge promotion.

CoAgent V1 does not need to fully automate every action.

## Appetite Rules

### Small Task Appetite

Use main thread and finish quickly. Do not create task teams.

### Medium Task Appetite

Use one scoped conversation or main thread plus bounded subagents.

### Long Task Appetite

Use a dynamic task team only when it reduces risk or context load.

### Architecture Task Appetite

Design work must produce:

- decisions;
- experiments;
- protocols;
- backlog items;
- review artifacts.

Design work that only summarizes sources is not enough.

## P0 For CoAgent V1

- canonical task charter;
- shared task board;
- context pack;
- result/review/blocker packet flow;
- active department registry;
- visible conversation proof and recovery notes;
- worktree/Git integration policy;
- safety and human intervention protocol;
- verification/evaluation rubric;
- problem-led external learning loop.

## P1 After User Review

- one bounded real multi-conversation proof using active department threads;
- context-delta implementation;
- mailbox schema and validator;
- task-scoped conversation bootstrap helper;
- result packet import improvements;
- minimal worktree binding record.

## P2 Later

- app-server transport;
- automatic conversation creation;
- automatic worktree provisioning;
- email or desktop notification sender;
- scheduled external learning automation;
- dashboards for operating metrics.

## Non-Goals

- Replace PMO/user judgment.
- Hide all work in subagents.
- Create a permanent department for every topic.
- Copy third-party agent runtimes wholesale.
- Connect private API keys to untrusted open-source projects.
- Treat Codex App UI state as durable truth.
- Treat conversation count as productivity.

## Stress-Test Done Criteria

### PX4 Parameter Identification

Done means:

- parameters are classified by identifiability;
- estimates include uncertainty;
- simulation mapping exists;
- non-identifiable parameters are explicit;
- additional experiment/manual data needs are clear;
- verification evidence exists or the task is explicitly blocked.

### UE Scene Truth / Simulation Product

Done means:

- scene source and capability route are known;
- truth export is defined and validated;
- planning/navigation inputs are explicit;
- wind/degradation experiment controls are scoped;
- manual review points are clear;
- large asset and Git strategy are safe.
