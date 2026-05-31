# CoAgent Task Intake And Governance

Date: 2026-05-28

Status: approved vocabulary source for `COAGENT-IMPL-01`; runtime expansion
outside the protocol freeze remains gated.

## Purpose

This document defines how a user request becomes controlled work inside
CoAgent.

The goal is to prevent the most expensive failure mode:

```text
the system executes for a long time, but the task was framed wrong at the
start.
```

CoAgent should behave like a disciplined technical organization. It should
move quickly when the work is clear, slow down when the problem is ambiguous,
and stop early when evidence shows that the task is drifting.

## Intake Rule

Every request must first be classified before it becomes execution.

```text
request -> intake classification -> owner -> execution mode -> evidence gate
```

The classification determines how much process is required. Low-risk clear
work should stay lightweight. High-risk or ambiguous work must be shaped before
implementation.

## Task Classes

Canonical protocol names live in `CoAgent/protocol/README.md`. Human-facing
labels below map directly to these packet values: `simple_message`,
`clear_task`, `complicated_task`, `complex_task`, `chaotic_incident`,
`disordered_task`, and `long_running_task`.

| Class | Meaning | Default Mode | Example |
|---|---|---|---|
| `simple_message` | No durable artifact, state, or follow-up ownership | Reply directly | Explain a concept or answer a small question |
| `clear_task` | Known steps, low ambiguity, bounded change | Execute with minimal checklist | Fix one typo, inspect one file |
| `complicated_task` | Expert analysis needed, but problem is stable | Assign owner, require evidence | Design a schema, review a module |
| `complex_task` | Problem/solution uncertain; needs probes | Discovery first, short checkpoints | CoAgent architecture, UE/Fab truth pipeline |
| `chaotic_incident` | System is broken or unsafe now | Stabilize first, then analyze | Git explosion, broken config, crash loop |
| `disordered_task` | The class is unclear | Clarify before execution | Vague request with unclear outcome |
| `long_running_task` | Multi-turn work with durable context | Dedicated task boundary | PX4 parameter identification, large Git migration |

The same user objective may contain multiple classes. The accountable owner
must split the work only when that reduces risk or improves completion.

## Required Intake Fields

Every durable task should define:

```yaml
task_id:
user_objective:
why_now:
task_class:
project_goal:
canonical_task_goal:
conversation_objective:
accountable_owner:
supporting_departments:
definition_of_done:
non_goals:
read_scope:
write_scope:
required_evidence:
risk_level:
assumptions:
open_questions:
appetite:
circuit_breaker:
checkpoint_plan:
escalation_conditions:
review_gates:
```

For simple messages, these fields are not required. The boundary is:

```text
if the work creates state, changes files, delegates to another conversation,
requires review, or may continue after the current turn, it is not a simple
message.
```

## Complexity-Based Execution Modes

### Clear

Use a short checklist and execute directly.

Required:

- objective,
- write scope if editing,
- expected output,
- verification command or evidence.

### Complicated

Assign one accountable owner and gather evidence before conclusion.

Required:

- owner,
- approach,
- assumptions,
- evidence plan,
- reviewer if the result affects architecture, tests, safety, or Git.

### Complex

Do not start full delivery immediately. Start with discovery.

Required:

- problem framing,
- assumptions to test,
- smallest useful probe,
- checkpoint interval,
- stop condition,
- user review point.

Complex tasks should produce a framing note or design note before large
implementation.

### Chaotic

Do not route through normal delivery first. Stabilize.

Required:

- immediate safety boundary,
- what must stop,
- what evidence is needed to understand the incident,
- recovery action,
- after-action review trigger.

### Disordered

Clarify before assigning execution.

Required:

- restated objective,
- likely task class,
- missing information,
- proposed next step.

## Appetite And Circuit Breaker

Every long or uncertain task needs an appetite:

```text
how much time, risk, and complexity this task is worth before scope must
change.
```

It also needs a circuit breaker:

```text
the condition that stops blind continuation.
```

Examples:

- stop after 30 minutes without finding the relevant source boundary;
- stop if UE/Fab automation still needs account-sensitive UI state;
- stop if Git diff size exceeds the planned batch boundary;
- stop if verification cannot reproduce the claimed result;
- stop if the task reveals a higher-level architecture decision.

Circuit breakers are not failures. They protect the project from expensive
wrong execution.

## Owner And Department Boundary

One task has one accountable owner at a time.

Departments may contribute, but they do not split accountability unless the
task is explicitly decomposed into child tasks.

| Role | Owns |
|---|---|
| PMO / main | user alignment, priority, final integrated report |
| DispatchCenter | task ticket, state, owner assignment, routing |
| Engineering | technical execution and investigation |
| Verification | independent evidence and reproducibility |
| Documentation | durable decisions, records, and docs consistency |
| Security | hard safety, credential, license, path, and destructive-action gates |
| DevOps | Git, release, branch, large-file, and repository hygiene |

The owner can request support. Support returns evidence. The owner integrates.

## Checkpoints

Checkpoint frequency depends on uncertainty and risk.

| Condition | Checkpoint Rule |
|---|---|
| Clear, low-risk task | Report at completion |
| Complicated task | Report after evidence is gathered |
| Complex task | Report after each probe or time box |
| Chaotic incident | Report after stabilization or failed stabilization |
| Long-running task | Report at predefined intervals and before each irreversible step |

Checkpoint reports should include:

```yaml
current_state:
evidence_found:
decision_needed:
blocker_or_risk:
next_step:
continue_or_stop:
```

## Escalation

Escalate to the user or the relevant gate owner when:

- the objective is still ambiguous after clarification,
- the task crosses path, credential, license, account, or destructive boundary,
- the evidence contradicts the current plan,
- the appetite is exceeded,
- a circuit breaker fires,
- the owner cannot produce required evidence,
- the work needs a higher-level architecture decision,
- the result would be hard to reverse.

Escalation should include options, not only a problem statement.

## Acceptance Gate

A durable task can be accepted only when it has:

- the requested artifact or decision,
- evidence path or reproducible command,
- known exclusions,
- residual risk,
- review state,
- next action or terminal state.

No task should be accepted only because a chat message says it is done.

## Strategy Alignment

Every substantial task should connect to one of the current project directions:

- MoSim as an RflySim-like simulation platform,
- Unreal/Fab scene ingestion and truth-backed map/planning validation,
- MWORKS/Syslab/Sysplorer simulation and control integration,
- CoAgent as the durable multi-conversation work control plane,
- repository hygiene, reproducibility, and evidence-backed delivery.

If a task does not support a current direction, it should be paused or shaped
as exploratory research with a small appetite.

## Backlog Hygiene

The backlog is not a promise to do everything.

An item should stay active only if it has:

- current value,
- owner or next review date,
- clear trigger,
- enough context to restart,
- known stop condition.

Old ideas should be archived unless they return as a shaped task with renewed
value.

## Retrospective Trigger

Run an after-action review when:

- a task ran past its appetite,
- a task was accepted then reopened due to missing evidence,
- a handoff failed,
- a department conversation was not visible or recoverable,
- the same type of confusion appears twice,
- user review finds the original framing was wrong.

The output should update one of:

- task intake rules,
- hook or policy,
- skill,
- checklist,
- documentation,
- test or verification gate.

## Current Decision

This document is now part of the CoAgent design baseline for discussion.

It does not approve implementation. It clarifies what must be implemented
first after approval: task intake fields, execution mode, appetite, circuit
breaker, checkpoint, escalation, and acceptance gates.
