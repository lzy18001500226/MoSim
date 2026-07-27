# CoAgent Architecture Issue Register

Date: 2026-05-29

Status: issue register plus current resolution pointers. Problems marked
`decided` have a design baseline, but this document still does not approve
runtime changes, transport changes, automatic conversation creation, automatic
worktree creation, unattended automation, or permanent department expansion.

## Purpose

The current CoAgent discussion corrected an important misunderstanding:

```text
task is the primary unit
conversation is an execution surface
department is a capability/governance lens
subagent is a short-lived bounded helper
```

CoAgent should not be designed as a fixed set of department conversations that
occasionally receive work. A serious task may create many Codex CLI/App
conversations under one canonical task goal. Those conversations must share
enough context to avoid semantic drift, but not so much context that the model
degrades or blindly inherits stale assumptions.

This register keeps the unresolved design problems visible so they can be
solved deliberately instead of being hidden inside prose architecture claims.

## Issue Status Vocabulary

| Status | Meaning |
|---|---|
| `open` | problem is known but not designed |
| `needs_discussion` | needs user/PMO design discussion before a decision |
| `needs_experiment` | needs a small proof or measurement before a decision |
| `blocked` | cannot progress without external tool, UI, or user action |
| `decided` | decision exists and should point to a durable design doc |

## Current Resolution Baseline

`COAGENT-DESIGN-12` adds the current problem-to-solution synthesis:

```text
CoAgent/docs/architecture/coagent_solution_synthesis.md
CoAgent/docs/architecture/coagent_user_intervention_ux.md
CoAgent/protocol/templates/
```

Resolved enough for V1 design:

```text
CAI-001 CAI-002 CAI-003 CAI-004 CAI-005 CAI-006 CAI-007 CAI-008
CAI-009 CAI-010 CAI-011 CAI-014 CAI-015 CAI-016 CAI-017 CAI-018
CAI-019 CAI-020 CAI-021 CAI-022 CAI-023 CAI-024 CAI-025
```

Still requiring experiments or separate approval:

```text
CAI-012 Codex App / VSCode / CLI state split
CAI-013 repeatable communication test coverage
automatic conversation creation
automatic email sending
app-server transport
automatic worktree provisioning
new permanent departments
broad hook/tool expansion
```

## Core Issues

### CAI-001: Canonical Task Versus Conversation State

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#canonical-task-lifecycle`

Problem:

Codex App, VSCode Codex, and Codex CLI conversations are visible work
surfaces, but they are not reliable project truth by themselves. A task may
span many conversations, and one conversation may be only a slice of the task.

Open questions:

- What exact object is the canonical task record?
- Which fields must be task-owned instead of conversation-owned?
- How does a conversation attach to, detach from, or close under a task?
- When a conversation disappears or is deleted in the UI, what task state
  remains authoritative?

Decision needed:

Define the task record as the source of truth for objective, owner, scope,
context pack references, child conversations, worktree bindings, evidence,
review status, blockers, and closeout state.

### CAI-002: Dynamic Task Teams, Not Fixed Department Execution

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#task-topology-selector`

Problem:

The prior design still drifts toward fixed department lanes. The user clarified
that execution must be task-oriented. A task such as Sunray150 parameter
identification may need multiple conversations: log audit, estimator design,
parameter mapping, simulation validation, documentation, and Git integration.

Open questions:

- When is a task large enough to create a task team?
- Who decides the number of scoped conversations?
- Can task-team conversations cross capability domains without becoming
  permanent departments?
- How does a task team terminate cleanly without leaving orphan conversations?

Decision needed:

Design task-team creation and closure rules around task complexity, risk,
context budget, write-scope isolation, and acceptance evidence.

### CAI-003: Conversation Creation Criteria

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#task-topology-selector`

Problem:

Creating too many conversations increases coordination cost and failure
probability. Creating too few conversations overloads context and mixes
unrelated reasoning.

Open questions:

- What thresholds trigger a new Codex CLI/App conversation?
- Which factors matter most: context length, write scope, risk, duration,
  tool requirements, review independence, or human visibility?
- When should a task use a short-lived subagent instead of a durable
  conversation?
- When should a task stay in the main conversation?

Decision needed:

Define a topology selector for:

```text
main-thread execution
single scoped task conversation
multiple scoped task conversations under one task team
short-lived subagents inside one conversation
review board / verification conversation
DevOps integration conversation
```

### CAI-004: Context Pack Granularity

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#context-pack-quality-model`

Problem:

New conversations need prior knowledge, but raw transcript copying creates
large context, stale assumptions, and hidden contradictions. Too little context
causes semantic drift.

Open questions:

- What belongs in the team-level context pack?
- What belongs only in a slice-level context pack?
- What must be excluded from context packs?
- How often should context packs refresh?
- How are new decisions propagated to already-running conversations?

Decision needed:

Split context into:

```text
task charter
shared context
slice context
decision log
evidence index
forbidden assumptions
accepted interfaces
context delta
```

### CAI-005: Cross-Conversation Communication Protocol

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#communication-protocol`

Problem:

The current visible-conversation communication proof shows a route can work,
but the architecture still lacks a full protocol for many conversations working
on one task. Free-form chat-to-chat messages will drift.

Open questions:

- What packet types are mandatory?
- Who is allowed to send packets to another conversation?
- Can peer conversations communicate directly, or must messages pass through a
  task coordinator?
- How are contradictions resolved?
- How are result packets merged without losing concerns?

Decision needed:

Define packet flow for:

```text
Task Packet
Context Pack
Context Delta
Checkpoint Packet
Result Packet
Blocker Packet
Review Packet
Merge Packet
Closeout Packet
```

### CAI-006: Worktree Binding Strategy

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#worktree-strategy`

Problem:

Codex App worktrees appear highly relevant to multi-conversation execution,
but the binding rules are not yet settled. Worktree identity must not become
task authority, yet worktrees are essential for Git safety and isolated
experiments.

Open questions:

- One task one worktree, or one scoped conversation one worktree?
- When should DevOps own an integration worktree?
- Can a subagent use an ephemeral worktree?
- How are worktree diffs reviewed, merged, or discarded?
- What happens if two conversations need the same files?

Decision needed:

Define worktree binding by task risk and write scope, with explicit
`review_owner`, `merge_owner`, and `close_owner`.

### CAI-007: Goal Ownership Across Three Layers

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#issue-register-resolution-map`

Problem:

There are at least three goal layers:

```text
project goal
canonical task goal
conversation objective
```

Inside a conversation there may also be short-lived subagent objectives. If
every layer freely changes goals, the system will drift. If every layer is too
rigid, the system cannot adapt to discovered facts.

Open questions:

- Who owns the canonical task goal?
- Can a scoped conversation propose a goal change?
- Can a scoped conversation change its own objective without PMO or Dispatch?
- How does a subagent objective inherit limits from the parent conversation?
- What happens when execution reveals the original task framing is wrong?

Decision needed:

Define goal inheritance, proposal, approval, and rollback rules.

### CAI-008: Acceptance Evidence And Stop Conditions

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#canonical-task-lifecycle`

Problem:

Multi-conversation execution can produce large activity without proving the
task is done. Every task needs explicit acceptance and stop conditions before
execution starts.

Open questions:

- What evidence is required for each task class?
- Who can mark a task done?
- Who can mark a slice done with concerns?
- What evidence is enough to stop an unproductive route?
- How are human-review-only gates recorded?

Decision needed:

Make acceptance evidence mandatory at task, conversation, and review levels.

### CAI-009: PMO, Dispatch, And User Boundary

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_user_intervention_ux.md#user-ask-rules`

Problem:

The system needs a user-facing coordinator and an internal task coordinator,
but their authority must be clear. The user does not want arbitrary hidden
implementation or fake communication. The main line should report when human
action is needed, then resume after the user acts.

Open questions:

- Which decisions must return to the user?
- Which decisions can Dispatch make automatically?
- Which decisions can a task-team lead make?
- When does PMO become a bottleneck?
- How do we prevent "manager does all work" failure?

Decision needed:

Separate user-facing decision authority from internal scheduling mechanics.

### CAI-010: Capability Domains Versus Departments

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#adopted-operating-principle`

Problem:

Departments are useful for capability, review, and accountability, but they are
not the primary execution object. A task may need DevOps, verification,
security, documentation, and research capabilities without creating one
permanent conversation for every capability.

Open questions:

- Are departments persistent conversations, capability cards, or review gates?
- Which capabilities must be always available?
- Which capabilities should be instantiated only when triggered?
- How do task teams request capability help without exploding conversation
  count?

Decision needed:

Define departments as capability domains and governance/review functions, not
as the default shape of execution.

### CAI-011: Subagent Versus Conversation Boundary

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#task-topology-selector`

Problem:

Subagents are useful for bounded work but cannot own durable communication or
long-running task state. Durable work needs visible task conversations.

Open questions:

- What work is appropriate for short-lived subagents?
- What work must be promoted to a scoped conversation?
- How does a parent conversation consume and verify a subagent result?
- Can a subagent ever write files directly?
- How are failed subagent results recorded?

Decision needed:

Freeze subagents as bounded disposable slices with no durable authority.

### CAI-012: Codex App / VSCode / CLI State Split

Status: `needs_experiment`

Problem:

Current practical evidence shows Codex App, VSCode Codex, and WSL/CLI session
state do not behave as one simple store. Some App-created conversations are not
visible in VSCode, and some migrated sessions needed path/source metadata
repair. The UI can also hang.

Open questions:

- Which runtime is authoritative for creating new conversations?
- Which session metadata fields are required for App visibility?
- Which metadata fields are required for VSCode visibility?
- What is the safe way to delete, migrate, or repair a conversation?
- Can the App worktree UI be reliably controlled through project-owned state,
  or is it only a manual frontend?

Decision needed:

Keep Codex App as UI/frontend until a stronger, repeatable session-state model
is proven.

### CAI-013: Communication Test Coverage

Status: `needs_experiment`

Problem:

There has been at least one visible DevOps communication proof, but the user
correctly challenged that broad communication is not proven just because a
thread exists.

Open questions:

- What is the minimal communication smoke test for one task team?
- What is the minimal cross-conversation result merge test?
- How do we prove a message went to the visible target conversation rather
  than an internal hidden subagent?
- How do we prove the App and VSCode both see the same result?

Decision needed:

Design explicit communication acceptance tests before relying on multi-dialogue
task execution.

### CAI-014: Learning And Architecture Drift Control

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#unresolved-questions-to-carry-forward`

Problem:

The project has many local and online sources: Hermes, Codex, OpenClaw,
Anthropic, OpenAI, ADK, LangGraph, AutoGen, CrewAI, and others. The value is
not copying them wholesale, but extracting design philosophy and mapping it to
CoAgent. Without a drift-control process, repeated research can become a loop
instead of implementation guidance.

Open questions:

- Which source families are already sufficiently audited?
- Which source families are only seed-level?
- What source evidence is required before adopting an idea?
- How are rejected ideas kept visible so they are not reintroduced later?
- How does a task request targeted research without reopening broad study?

Decision needed:

Keep vendor/framework lessons tied to concrete CoAgent architecture objects,
with evidence level and adoption status.

### CAI-015: Human Review And Intervention Model

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_user_intervention_ux.md`

Problem:

The user expects the system to proceed autonomously where safe, but surface
clear human intervention points for login, GUI, manual review, direction
changes, and high-risk actions.

Open questions:

- What events require human review?
- How should a task pause while waiting for user action?
- How is "user completed manual action" represented?
- How does the task resume without losing context?
- How do we prevent agents from wasting hours after an early wrong assumption?

Decision needed:

Define human-interrupt packets and circuit breakers as first-class task state.

### CAI-016: Dynamic Task Topology Revision

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#task-topology-selector`

Problem:

The number of conversations for one task is not known at task start. A task
may begin as one analysis thread and later split into research,
implementation, verification, incident, DevOps, and documentation
conversations.

Open questions:

- Who can propose a new scoped conversation?
- Who approves conversation split/merge/close events?
- When should a slice be collapsed back into the main task team?
- How are orphaned conversations detected and closed?

Decision needed:

Define topology revision events:

```text
propose_new_conversation
approve_new_conversation
close_conversation
merge_conversation_result
collapse_back_to_main
```

### CAI-017: Context Quality Metrics

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#context-pack-quality-model`

Problem:

A context pack can be too short, too long, stale, biased, or missing critical
negative lessons. Context quality cannot be assumed from the fact that a pack
exists.

Open questions:

- What minimum fields prove the context is adequate?
- How should stale context be detected?
- How should forbidden assumptions and prior failures be surfaced?
- What context size should trigger summary or retrieval instead of paste?

Decision needed:

Context packs need measurable quality fields such as source coverage,
freshness, token estimate, decision references, evidence references, known
risks, and forbidden assumptions.

### CAI-018: Contradiction Resolution

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#communication-protocol`

Problem:

Two conversations may return conflicting conclusions. If Dispatch merely
summarizes both, the final task state becomes incoherent.

Open questions:

- What counts as a contradiction versus a harmless difference in scope?
- Who owns contradiction resolution?
- Can work continue while a contradiction is unresolved?
- How is the final decision recorded?

Decision needed:

Introduce a `Contradiction Packet` with claims, evidence, impact, resolver,
deadline, and decision record.

### CAI-019: Human Notification Policy

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_user_intervention_ux.md#notification-levels`

Problem:

Some blockers require user action: MWORKS activation, Epic/Fab login, UE GUI
selection, manual visual review, or high-risk approval. Email or desktop
notification may be useful but is security-sensitive.

Open questions:

- Which blockers justify notification outside the main chat?
- Which notification channels are allowed?
- How are credentials and notification secrets isolated?
- What acknowledgement is required before resume?

Decision needed:

Define a notification policy with allowed channels, owner, rate limit, message
template, ack requirement, and resume command/link.

### CAI-020: Anti-Loop Controls

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_user_intervention_ux.md#retry-and-circuit-breaker-rules`

Problem:

Agents can repeatedly try the same failing MCP probe, retune parameters
without improvement, reread the same sources, or keep testing a blocked GUI
route.

Open questions:

- What repeated-failure signature trips a circuit breaker?
- How many retries are allowed per failure class?
- What counts as a novel attempt?
- When does an incident or postmortem become mandatory?

Decision needed:

Add attempt counters, novelty requirements, failure signatures,
same-failure retry limits, circuit breakers, escalation, and postmortem
triggers.

### CAI-021: Skill / Hook / Checklist Promotion Rules

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#issue-register-resolution-map`

Problem:

Failed tasks should improve the system, but not every lesson belongs in a
skill, and not every skill should become a hook. Hooks enforce policy; skills
guide optional procedure.

Open questions:

- Which lessons become skills?
- Which failures deserve hard hooks?
- Which lessons belong only in docs or checklists?
- Who reviews promoted knowledge before future tasks consume it?

Decision needed:

Create a postmortem classification path:

```text
skill_update
hook_update
checklist_update
doctor_check
test_case
documentation_note
do_not_repeat_rule
```

### CAI-022: Worktree Review Economy

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#worktree-strategy`

Problem:

A task team may produce many worktrees. Reviewing all diffs can become slower
than the work itself, and blindly merging all worktrees can destabilize the
project.

Open questions:

- How are worktree diffs triaged?
- When should a worktree be discarded instead of merged?
- Can two candidate worktrees compete for the same solution?
- Who owns manual rewrite when neither worktree is directly mergeable?

Decision needed:

Define merge dispositions:

```text
discard
cherry_pick
merge_whole
manual_rewrite
compare_two_candidates
request_rework
```

### CAI-023: Capability Proof

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#decisions-ready-for-implementation`

Problem:

A conversation may claim it can use UE, MWORKS, Git, email, MCP, or tests, but
the tool, login, listener, dependency, or environment may be unavailable.

Open questions:

- What proof is required before assigning a tool-dependent task?
- How often should capabilities be reprobed?
- What fallback applies when a capability disappears mid-task?
- Can a conversation continue with degraded capability?

Decision needed:

Define capability cards with declared capability, last verified time, probe
command, probe result, scope limit, and fallback.

### CAI-024: Task Reshaping

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#issue-register-resolution-map`

Problem:

A route may become less valuable after discovery. For example, manual Fab
import may be cheaper and safer than full Launcher automation. Without an
explicit reshaping event, agents may keep executing the old plan.

Open questions:

- Who can propose a route change?
- Which changes require user approval?
- How is saved cost versus lost capability recorded?
- How are already-open conversations affected?

Decision needed:

Define a task reshaping event with original route, new route, reason, saved
cost, lost capability, affected conversations, and approval state.

### CAI-025: Knowledge Promotion Safety

Status: `decided`

Resolution pointer:

`CoAgent/docs/architecture/coagent_solution_synthesis.md#canonical-task-lifecycle`

Problem:

Bad conclusions can be promoted into docs, skills, context packs, or memory
and poison future tasks.

Open questions:

- What evidence is required before promoting a lesson?
- How is scope of validity recorded?
- How are conflicting lessons handled?
- When should a promoted lesson expire or require review?

Decision needed:

Knowledge promotion needs source evidence, reviewer, scope of validity,
revisit condition, and conflicting-evidence tracking.

## Remaining Highest-Priority Discussion Order

After `COAGENT-DESIGN-12`, the remaining problems should be solved in this
order:

1. `CAI-012` Codex App / VSCode / CLI state split.
2. `CAI-013` repeatable communication test coverage.
3. Email adapter proof without leaking secrets or spamming.
4. Automatic worktree lifecycle proof.
5. Automatic conversation creation proof.
6. Context-pack quality experiments.
7. Semantic drift and anti-loop metrics.

The Codex App/VSCode/CLI state split and communication test coverage must be
solved before treating multi-conversation execution as reliable infrastructure.

Use `CoAgent/docs/architecture/coagent_problem_driven_operating_model.md` for
the task-pressure examples behind `CAI-016` through `CAI-025`.

## Non-Decisions

This register does not decide:

- how many permanent conversations should exist,
- whether to implement automatic conversation creation,
- whether to use app-server transport,
- whether to create automatic worktrees,
- whether to run unattended scheduled automation,
- whether to import Hermes, Codex, OpenClaw, or any other project wholesale.

Those decisions require separate design closure and explicit approval.
