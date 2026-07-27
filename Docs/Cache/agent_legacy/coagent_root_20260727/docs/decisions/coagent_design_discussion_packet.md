# CoAgent Design Discussion Packet

## Status

This is a discussion packet, not an implementation approval.

The next step is to discuss and confirm the design philosophy before adding
more CoAgent runtime, transport, automation, department, or memory features.

## Core Position

CoAgent should be a MoSim-owned workflow control plane.

```text
Codex App / VSCode
  -> UI and review surfaces

CoAgent project files
  -> durable state, task packets, result packets, event logs, context packs,
     status boards, hooks, and recovery docs

Visible department conversations
  -> durable work surfaces for narrow responsibilities

Short-lived subagents
  -> disposable bounded workers that return evidence
```

The system should not be "many chats that happen to have names." It should be
a small workflow system where every conversation has a clear state contract.

## Task-First Operating Principle

CoAgent's purpose is task completion, not department purity.

Departments provide capability, accountability, review, and memory. They are
not rigid task boundaries. A task may require overlapping support from
engineering, verification, documentation, security, and DevOps, but it still
needs one accountable owner and an explicit state.

Use `CoAgent/docs/architecture/technical_enterprise_operating_system.md` for the
broader management model behind this principle.

Use `CoAgent/docs/architecture/task_intake_and_governance.md` for the concrete intake
rules that decide whether a request is a simple message, clear task,
complicated task, complex task, chaotic incident, disordered task, or
long-running task. It also defines appetite, circuit breaker, checkpoint,
escalation, and acceptance gates.

Use `CoAgent/docs/architecture/enterprise_to_agent_mapping.md` and
`CoAgent/docs/architecture/coagent_complexity_control.md` before turning the enterprise
model into runtime behavior. They define goal hierarchy, department-to-agent
mapping, context hierarchy, conversation creation limits, and the first-phase
ban on department-internal durable agent swarms.

## Agent Concepts

| Concept | Meaning | Durable? | Correct Use |
|---|---|---:|---|
| Main/PMO conversation | User alignment, goal tradeoffs, final integration | Yes | Clarify objective, make final decisions, report outcome |
| DispatchCenter | Task tickets, routing, state board, result intake | Yes | Own queue and communication protocol |
| Department conversation | Recurring responsibility lane | Yes | Git, verification, docs, security, engineering |
| Dedicated task conversation | One long high-context task | Yes, until closed | PX4 parameter identification, UE scene truth export |
| Short-lived subagent | Bounded one-shot worker | No | Read one source slice, inspect one risk, summarize one batch |
| Skill | Selectively loaded procedure | File-backed | How to perform a repeatable workflow |
| Hook/policy | Enforced lifecycle guard | Yes | Block unsafe actions, require review, enforce path/secrets/Git rules |
| MCP/tool | Callable capability | External | UE, MWORKS, Git, filesystem, search, model tools |
| Memory/search | Evidence retrieval | Indexed | Supply source-linked context, not instructions |

## Goal Hierarchy

Do not let every layer create an independent goal.

Use this hierarchy:

```text
Project Goal -> Canonical Task Goal -> Conversation Objective -> Subagent Objective
```

- Project Goal frames priority and strategic direction.
- Canonical Task Goal is the one official durable task goal owned by
  DispatchCenter.
- Conversation Objective is a scoped work order for a department or dedicated
  task conversation.
- Subagent Objective is a disposable local question that must return evidence.

Workers may detect goal drift and escalate. They must not silently rewrite the
canonical task goal.

## Department Model

Keep the permanent set small.

| Conversation | Role | Should Own | Should Not Own |
|---|---|---|---|
| `MoSim｜主线总控` | Main/PMO | user dialogue, priorities, final decisions, integrated reporting | long Git batches, full test queues, hidden implementation grind |
| `MoSim｜调度中台` | DispatchCenter | task tickets, status board, owner assignment, dependencies, result routing | feature implementation, Git execution, silent scope changes |
| `MoSim｜研发工程部` | Engineering | bounded implementation/research streams, UE/Fab/MCP/MWORKS technical work | global priority, final acceptance |
| `MoSim｜验证测试部` | Verification | independent tests, reproducibility, simulation evidence, result review | implementing the feature under test |
| `MoSim｜文档秘书部` | Documentation | user directives, decisions, work records, docs patches, docs consistency | owning the full task board |
| `MoSim｜安全合规部` | Security | path/secrets/license/large-file/destructive-action review | general product direction |
| `MoSim｜DevOps 发布部` | DevOps | Git staging/commit/push, branch hygiene, large-file/LFS gates | feature implementation or architecture approval |

Recommended default: do not add more permanent departments yet.

If Engineering becomes too broad, split by repeated queue pressure, not by
topic curiosity. For example, split only if UE scene work, parameter
identification, and MWORKS controller work are all active enough to collide.

## Communication Contract

Every non-trivial cross-conversation task should follow this lifecycle:

```text
1. PMO clarifies the user objective and constraints.
2. DispatchCenter creates or updates a task ticket.
3. A context pack is built for the target department or task conversation.
4. The owner conversation receives a task packet.
5. The owner returns a result packet with evidence, blockers, next action, and review status.
6. Verification/Security/Docs/DevOps gates run when relevant.
7. PMO reports the integrated result to the user.
```

Communication is successful only when a visible target conversation returns
or records a result packet. A hidden subagent result is not department
communication.

Not every interaction needs the same protocol weight:

| Interaction | Required Boundary |
|---|---|
| Simple reply | Can stay as a normal visible chat response when it has no durable task ownership, artifact, or follow-up state |
| Durable task | Requires task_id, owner, state, context pack, result packet, evidence/artifact paths, and review state |
| Long task / dedicated task conversation | Requires the durable task boundary plus checkpoints and recovery notes |

The protocol should avoid two errors:

- over-promoting every short reply into a heavy task packet;
- under-specifying long work so that evidence, auth, user input, or review
  state exists only in chat.

## State Vocabulary

Use explicit task states:

```text
planned
ready
working
input_required
auth_required
review_required
blocked
failed
completed
canceled
rejected
superseded
```

Human review should move a task between states. It should not be only a note in
chat.

## Task Intake Gate

Before creating a durable task, DispatchCenter should classify the request.

Minimum classification:

```text
simple message
clear task
complicated task
complex task
chaotic incident
disordered task
long-running task
```

The class controls the protocol weight:

- simple messages stay lightweight,
- clear tasks can execute with a small checklist,
- complicated tasks need owner and evidence,
- complex tasks need discovery before delivery,
- chaotic incidents need stabilization before analysis,
- disordered tasks need clarification before routing,
- long-running tasks need context pack, appetite, circuit breaker, checkpoint,
  and result packet.

The task-entry details live in
`CoAgent/docs/architecture/task_intake_and_governance.md`.

Minimum vocabulary after approval must distinguish:

- simple message versus durable task,
- artifact/evidence outputs versus prose-only replies,
- interrupted states such as `input_required` and `auth_required`,
- review states such as `review_required`,
- terminal states such as `completed`, `failed`, `canceled`, and `rejected`.

## Skill / Hook Boundary

Use a skill when the question is:

```text
How should the agent perform this repeatable workflow?
```

Examples:

- UE map import checklist.
- PX4 log parameter-identification workflow.
- MWORKS simulation evidence generation.
- Documentation consistency review procedure.

Use a hook or policy when the question is:

```text
What must be enforced regardless of what the model says?
```

Examples:

- Block writes outside project boundaries.
- Require human review before deletion or broad Git operations.
- Prevent secrets or account caches from entering tracked files.
- Stop large-file commits without LFS/ignore decision.
- Require result-packet schema before marking a task completed.

## When To Create A Dedicated Task Conversation

Create one when all conditions hold:

```text
multi-turn technical context is required
the task needs repeated human or verifier review
there is a parent department
there is a task_id
there is a read/write scope
there is a stop condition
there is an expected result packet
```

Do not create one for:

- a small edit,
- a one-file review,
- a short source lookup,
- a task that can return one bounded result packet immediately.

For the first runtime phase, do not create department-internal durable agent
swarms. The maximum supported nesting is:

```text
PMO/main -> DispatchCenter -> department or dedicated task conversation -> short-lived subagent
```

Canonical examples that deserve dedicated task conversations:

- PX4/Sunray log-based parameter identification.
- UE/Fab scene truth export and path-planning acceptance.
- Large Git migration with many path groups.

## Design Decisions To Confirm

| Decision | Recommended Default | Reason |
|---|---|---|
| PMO and DispatchCenter | Logically separate; visible split only if communication is reliable | Keeps user dialogue clean without overcomplicating early workflow |
| Permanent departments | Keep current seven; do not add more now | Minimizes synchronization failure |
| Engineering | One default execution lane for now | Split only after repeated queue pressure |
| DevOps | Permanent | Git is high-risk and can become huge |
| Documentation Secretary | Records decisions and docs; does not own full status board | Prevents secretary overload |
| Security | Hook/policy owner | Safety must be enforced, not merely suggested |
| Verification | Independent gate | Avoids workers self-certifying |
| Task/event vocabulary | Distinguish simple messages, durable tasks, artifact/evidence, interrupted states, review states, and terminal states | Prevents long work from collapsing into ambiguous `done/blocked` chat notes |
| Transport | File/CLI first; app-server later | Avoids private Codex App state dependency |
| Automation | Dry-run and guarded task creation first | Real unattended mutation needs more proof |

## User Confirmation Checklist

Implementation stays frozen until these items are explicitly accepted or
changed:

```text
[ ] CoAgent is MoSim-local first, portable later by clean boundaries.
[ ] Codex App / VSCode are UI and review surfaces, not durable state.
[ ] Current seven visible conversations are enough for now.
[ ] Engineering stays one general execution department for now.
[ ] DevOps remains a permanent department.
[ ] Documentation Secretary records decisions and docs, but DispatchCenter owns task state.
[ ] Skills are procedural packages, not policy enforcement.
[ ] Hooks/policies enforce path, secrets, Git, destructive operations, and review gates.
[ ] Dedicated task conversations require task_id, parent department, scope, stop condition, and result packet.
[ ] Task/event vocabulary distinguishes simple messages, durable tasks, artifact/evidence, input-required/auth-required states, review states, and terminal states.
[ ] Transport stays file/CLI first until app-server stability is verified.
[ ] Automation stays dry-run/guarded until hooks and review gates are proven.
```

If any item is rejected, update this packet and the operating docs before
writing runtime code.

## Implementation Freeze Gate

Do not implement or expand these until the checklist above is resolved:

- new permanent department conversations,
- app-server transport,
- unattended automation,
- workflow replay,
- task-state schema migration,
- scheduled repository-update jobs,
- memory promotion beyond source-linked evidence,
- broad hook rewrites,
- task/result packet schema changes.

Allowed before confirmation:

- read-only source study,
- documentation clarification,
- validation of existing learning indexes,
- small corrections that make the discussion packet more accurate.

## Implementation Sequence After Approval

1. Freeze the task-state vocabulary and event schema, including simple message,
   durable task, artifact/evidence, input-required/auth-required, review, and
   terminal states.
2. Update task packet and result packet schemas to match the vocabulary.
3. Strengthen hooks for path, secrets, destructive operations, Git, and result
   packet validation.
4. Run one real communication lifecycle with DevOps or Verification using a
   small task packet.
5. Run one dedicated long-task conversation with a context pack and result
   packet.
6. Only then expand transport or scheduled automation.

## Non-Goals For The Next Phase

- No new custom frontend.
- No wholesale Hermes/OpenClaw/LangGraph import.
- No broad app-server dependency before stability is verified.
- No all-skills/all-references context loading.
- No uncontrolled permanent department expansion.
- No unattended file mutation without hooks and review gates.
