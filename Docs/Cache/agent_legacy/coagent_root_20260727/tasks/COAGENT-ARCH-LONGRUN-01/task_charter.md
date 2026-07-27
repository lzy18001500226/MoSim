# COAGENT-ARCH-LONGRUN-01 Task Charter

Date: 2026-05-30
Status: active
Task class: long_running_task
Minimum appetite: 10 hours
Primary review point: user audit after at least 10 hours of sustained architecture work

## Canonical Goal

Sustain at least 10 hours of CoAgent architecture design work and produce
reviewable architecture artifacts for a task-first, multi-conversation
multi-agent operating system.

The work must advance the design itself. Merely creating this task, opening
department conversations, or writing a plan is not success.

## Scope

This task covers:

- dynamic task-team architecture for long-running technical tasks;
- permanent department responsibilities and conditional department promotion;
- scoped conversation creation, closure, and authority boundaries;
- task charter, shared board, mailbox, context pack, result packet, review
  packet, blocker packet, and integration plan flows;
- context and memory design for new conversations without raw transcript bloat;
- worktree and Git integration strategy for many active conversations;
- verification, evidence, trace, and process-quality evaluation;
- safety, compliance, destructive-action gates, and tool/MCP boundaries;
- human intervention UX, including future email-style notification design;
- external intelligence and self-evolution loop from model vendors, open-source
  agent projects, and large-company project-management practice;
- stress-test mappings for PX4 log parameter identification and UE scene truth /
  RflySim-like simulation productization.

## Non-Goals

- Do not implement app-server transport in this task.
- Do not implement automatic conversation creation in this task.
- Do not implement automatic worktree provisioning in this task.
- Do not implement unattended scheduled automation in this task.
- Do not add new permanent departments unless the design proves a concrete
  need and records a promotion proposal.
- Do not treat hidden Codex subagents as durable departments.
- Do not claim email notification is implemented; design only unless separately
  approved.

## Definition Of Done For The 10-Hour Review

The task is ready for user audit when these artifacts exist and are coherent:

1. an updated architecture issue matrix with each important problem classified
   as decided, needs experiment, needs user decision, or deferred;
2. a complete task-flow design for at least two stress tests:
   PX4 log parameter identification and UE scene truth/navigation simulation;
3. a dynamic task-team design that states when to create scoped conversations,
   when to use short-lived subagents, and when to avoid both;
4. a context/memory design that defines shared context, slice context, context
   delta, refresh, stale-context detection, and context budget control;
5. a cross-conversation communication design with packet types, ownership,
   mailbox rules, contradiction handling, and review handoff;
6. a worktree/Git integration design with branch/worktree ownership, merge
   gates, review gates, and large-change containment;
7. a verification/evaluation design covering both product correctness and
   organization/process quality;
8. a safety/human-intervention design covering auth/license/GUI blocks, unsafe
   actions, dedupe, escalation, and resume instructions;
9. a self-evolution design showing how external projects and vendor articles
   become reviewed improvements rather than unbounded research;
10. an implementation backlog that breaks the approved architecture into small,
    gated tasks;
11. real department review results are imported or explicitly recorded as
    blockers, including failed or partial communication tests;
12. stress-test templates exist for the PX4 and UE workflows so the design is
    anchored to real MoSim tasks, not only organization theory.

## Acceptance Evidence

Required evidence paths:

- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/shared_task_board.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_pack.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/architecture_problem_matrix.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/department_dispatch_plan.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/review_brief.md`
- architecture documents under `CoAgent/docs/architecture/`
- decision/backlog documents under `CoAgent/docs/decisions/`
- runtime task state under `Results/agent_runtime/`
- department result packets under `Results/agent_packets/`
- transport logs under `Results/coagent_transport/runs/`
- stress-test templates under `CoAgent/protocol/templates/`

## Circuit Breakers

Stop and ask the user only when:

- a required manual decision changes the project direction;
- a command requires credentials, account login, license activation, or GUI
  permission outside the project boundary;
- the next action would implement a gated runtime feature without approval;
- a destructive action, broad Git operation, or external path mutation is
  required;
- three consecutive cycles hit the same unresolved blocker.

Otherwise continue producing architecture artifacts, checks, and recoverable
state.

## Department Topology

Use the confirmed active 11 permanent conversations as governance and review
surfaces:

- MainAgent: user-facing PMO and final report.
- DispatchAgent: canonical task state, topology, board, mailbox.
- ProductStrategyAgent: product value, task appetite, non-goals.
- RuntimePlatformAgent: conversation/session/transport/worktree surface design.
- ContextMemoryAgent: context pack, memory, indexing, stale-context controls.
- ToolchainMCPAgent: MCP/tool boundary, capability cards, failure modes.
- KnowledgeSecretaryAgent: documentation, decisions, promotion of stable rules.
- VerificationAgent: evidence, tests, review gates, trace/evaluation.
- SafetyComplianceAgent: safety, secrets, license, destructive-action gates.
- DevOpsReleaseAgent: Git, worktree, merge, release hygiene.
- ExternalIntelligenceAgent: vendor/open-source learning and evolution loop.

Task-scoped conversations may be proposed in the design, but automatic creation
is not approved inside this task.

## First Execution Phase

Phase 1 must produce:

- active department registry;
- task board and context pack;
- initial architecture problem matrix;
- first-round department dispatch plan;
- runtime task entry and conversation links;
- review brief showing what the user should audit after 10 hours.
