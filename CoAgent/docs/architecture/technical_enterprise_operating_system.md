# Technical Enterprise Operating System

Date: 2026-05-28

Status: enterprise-management baseline source. Closure is recorded in
`CoAgent/docs/architecture/technical_enterprise_operating_system_closure.md`. This is
not implementation approval for new runtime, transport, automation, or
department expansion.

## Purpose

CoAgent should learn from multi-agent systems, but the deeper target is a
technical enterprise operating model: a way to move complex work forward
quickly without losing direction, evidence, safety, or institutional memory.

The system should optimize for task completion, not department purity.
Departments exist to provide accountability and capability. They should not
become barriers that prevent the user's objective from being completed.

## Core Principle

```text
Goal before task.
Accountability before division of labor.
Acceptance before execution.
Evidence before conclusion.
Short feedback loops before long unattended runs.
Escalation before blind persistence.
Durable state before chat memory.
Retrospective before forgetting.
```

## Task-First Operating Model

A user request should first become an explicit outcome, not an immediate
department assignment.

Every non-trivial task should define:

- objective,
- reason for doing the work,
- definition of done,
- non-goals,
- constraints,
- risks,
- required evidence,
- escalation conditions,
- accountable owner.

Departments may collaborate dynamically, but accountability must stay explicit.
At any moment, one owner is accountable for returning an integrated result to
the user or escalating with evidence.

## Dynamic Boundaries

High-performing technical organizations have stable functions but dynamic work
boundaries.

Stable functions:

- product/PMO owns goal alignment and final user-facing integration,
- engineering owns technical implementation and investigation,
- verification owns independent evidence and reproducibility,
- security/compliance owns hard risk gates,
- documentation owns durable knowledge and decision records,
- DevOps owns Git/release/repository hygiene.

Dynamic task boundaries:

- engineering may request DevOps support for a large rename or staged commit,
- PMO may request verification before accepting an uncertain result,
- security may veto or pause a task that crosses path, credential, license, or
  destructive-action boundaries,
- documentation may request clarification before recording a decision,
- a long task may create a dedicated task conversation when context continuity
  matters.

Dynamic boundaries are allowed at the execution layer, not at the
accountability layer.

## Standard Task Lifecycle

```text
1. User states a need.
2. PMO clarifies objective, definition of done, non-goals, risk, and escalation.
3. Dispatch records a task ticket and assigns one accountable owner.
4. A bounded context pack is prepared for the owner.
5. The owner decomposes work and requests support from departments as needed.
6. Supporting departments return result packets with evidence and blockers.
7. The owner integrates the result and requests verification/security/docs/Git
   gates when relevant.
8. PMO reports the integrated result, residual risk, and next step to the user.
9. Documentation records durable decisions and lessons.
10. DevOps handles staged Git/release work when appropriate.
11. Retrospective updates process, skills, hooks, or checklists when the task
    reveals a repeatable failure mode.
```

## Management Patterns To Adopt

### Mission Command

Each task should capture intent, success criteria, boundaries, and escalation
conditions. The owner may choose tactics inside that boundary.

### OODA Loop

Long or uncertain work needs short feedback loops:

```text
observe -> orient -> decide -> act -> report checkpoint
```

The more uncertainty or risk, the shorter the checkpoint interval.

### RACI

Each significant task should distinguish:

- Responsible: doing the work,
- Accountable: final owner,
- Consulted: domain reviewers,
- Informed: parties that need status.

Only one party should be accountable for the integrated task outcome.

### Definition Of Done

No significant task should start without a clear completion standard.

Completion should include required artifacts, tests or checks, evidence paths,
review state, and known exclusions.

### Escalation Policy

A task should pause and escalate when:

- the objective appears ambiguous,
- execution crosses a write/path/secret/account/destructive boundary,
- required credentials or login state are missing,
- evidence contradicts the original plan,
- a time budget is exceeded without meaningful progress,
- implementation reveals a higher-impact architecture decision,
- verification cannot reproduce the claimed result.

### Design Review And ADR

High-impact changes require a design note before implementation. Architecture
decisions should be recorded with context, options, decision, tradeoffs, risks,
and revisit triggers.

### WIP Limit

Limit concurrent long-running tasks. More active work increases context drift,
coordination failure, and unreviewed state.

### Single Source Of Truth

Use project-owned durable files as truth:

- task state in task tickets/status boards,
- architecture decisions in ADRs,
- user directives in PMO summaries,
- implementation truth in the repository,
- verification truth in test outputs and evidence,
- chat as discussion evidence, not canonical state.

### Pre-Mortem

Before risky work, list likely failure modes and define stop conditions.

### After-Action Review

After significant work, ask:

- What was intended?
- What happened?
- Why was there a gap?
- What process, skill, hook, test, or document should change?

The goal is system improvement, not blame.

## Failure Modes This Model Should Prevent

- The task spends hours executing a misunderstood objective.
- Multiple departments assume another department owns the outcome.
- Chat claims completion without artifacts or verification.
- A worker performs broad Git or destructive edits without review.
- A long task cannot resume because context existed only in a conversation.
- Documentation diverges from implementation.
- Automation continues after it should have escalated to the user.

## Follow-Up Research Queue

Research should continue beyond agent frameworks and study how durable
technical organizations operate:

- engineering management systems for high-uncertainty R&D,
- incident command and postmortem practice,
- product/engineering alignment and scope control,
- design review and ADR practice,
- DevOps release management and change control,
- quality systems and independent verification,
- knowledge management and organizational memory,
- OpenMOSS, MetaGPT, CrewAI, AG2/AutoGen, AutoGroq, Squad, Kimi/Qwen agent
  ecosystems, and other agent-team systems as organization-design references.

Each future study should answer:

1. How does the organization preserve intent during handoff?
2. How does it prevent work from continuing after the objective is wrong?
3. How does it assign one accountable owner while allowing collaboration?
4. How does it make evidence and review mandatory without killing velocity?
5. How does it convert failures into process improvement?

## First Source Leads

The first follow-up audit is
`CoAgent/learning/audits/2026-05-28_technical_enterprise_operating_system_round1.md`.

It starts from these management patterns:

- DRI/DACI for single accountable ownership and decision roles,
- SRE incident response and blameless postmortems for recovery and learning,
- DORA metrics for balancing delivery speed and stability,
- Team Topologies for reducing cognitive load through team boundaries,
- ADRs for durable architecture memory,
- Working Backwards for user-outcome-first task framing.

## Gap-Analysis Additions

The second follow-up audit is
`CoAgent/learning/audits/2026-05-28_technical_enterprise_operating_system_round2_gap_analysis.md`.

It adds management mechanisms that were under-emphasized in the first pass:

- scope appetite, betting, cooldown, and circuit breakers from Shape Up,
- complexity classification from Cynefin,
- strategy deployment from Hoshin Kanri,
- product discovery and project-poster style problem framing,
- psychological safety plus structure/clarity from Google re:Work,
- multidimensional productivity measurement from SPACE,
- secure-by-design lifecycle practice from NIST SSDF,
- cognitive-load reduction and team-boundary design from Team Topologies.

These additions reinforce one rule: long tasks need a clear appetite and stop
condition before execution, and ambiguous tasks need problem discovery before
delivery work begins.

## Task Intake Governance

The concrete task-entry mechanism is documented in
`CoAgent/docs/architecture/task_intake_and_governance.md`.

That document translates the management model into operational design:

- classify the request before execution,
- decide whether the work is a simple message, clear task, complicated task,
  complex task, chaotic incident, disordered task, or long-running task,
- assign one accountable owner,
- set appetite and circuit breaker before long or uncertain work,
- define checkpoint and escalation rules,
- accept results only through evidence and review state.

This is the missing bridge between enterprise management philosophy and the
future CoAgent task/result protocol.

## Closure

Enterprise-management discussion is closed as a baseline in
`CoAgent/docs/architecture/technical_enterprise_operating_system_closure.md`.

Open implementation questions now belong to the Agent design layer:
conversation creation, context packing, transport, scheduling, runtime state,
and worker lifecycle.
