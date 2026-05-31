# CoAgent Problem-to-Solution Synthesis

Date: 2026-05-29

Status: design baseline for task-oriented multi-conversation CoAgent work.
This document does not approve app-server transport, unattended automation,
automatic conversation creation, automatic email sending, or new permanent
departments.

## Purpose

The current CoAgent problem is not "how many departments exist". The primary
unit is the user task. A task may need one conversation, many scoped
conversations, or short-lived subagents inside a conversation. Departments are
governance and capability lenses; they are not fixed execution boundaries.

This document maps the open architecture issues to concrete design decisions
using three reference families:

- large technical-organization management: DRI, shaped work, incident command,
  review gates, integration ownership, and measurable delivery health;
- large-model agent architecture: manager/tool calls, handoffs, graph
  orchestration, human interrupts, durable execution, memory, and traces;
- GitHub agent projects already mirrored under `References/Agent`: Codex,
  Hermes, OpenClaw, LangGraph, OpenAI Agents SDK, agent-teams-ai, Autogen/AG2,
  CrewAI, Temporal, security/guardrail projects, and context-engineering
  projects.

## Adopted Operating Principle

```text
user task
  -> canonical task charter
  -> topology selection
  -> context pack
  -> one or more scoped conversations
  -> optional short-lived subagents inside a scoped conversation
  -> evidence packets
  -> review and integration
  -> knowledge promotion
```

The canonical task state is durable. Chat history is not the source of truth.

## External Patterns Mapped Into CoAgent

| Source pattern | CoAgent decision | Reason |
|---|---|---|
| OpenAI Agents SDK separates agents, handoffs, guardrails, sessions, tracing, and human-in-the-loop. | Distinguish manager-style subagent calls from conversation handoffs. Keep packet contracts and review gates separate from execution prompts. | Avoid treating every helper as a durable department. |
| Anthropic recommends simple composable workflows before autonomous agents and emphasizes context engineering. | Default to shaped task graphs and small context packs; escalate to multi-conversation only when coordination value exceeds overhead. | Prevent over-orchestration and context bloat. |
| Google ADK and Microsoft Semantic Kernel expose sequential, parallel, group-chat, handoff, and custom orchestration forms. | Add a topology selector instead of hard-coding seven departments as the execution model. | A PX4 identification task and a UE truth-export task need different shapes. |
| A2A, LangGraph, and Temporal model task state, interrupts, persistence, and resumability. | Use durable task states, blocker packets, resume packets, WAL/event evidence, and explicit human intervention states. | Long tasks must survive context loss, crashes, and login/license interruptions. |
| CrewAI-style process models use sequential/hierarchical patterns. | Allow hierarchical planning but require one accountable owner and explicit acceptance. | Management hierarchy is useful only when ownership stays clear. |
| GitLab DRI and incident practices. | Every durable task has one accountable owner and one integration owner; incidents get a temporary incident commander. | Prevent responsibility diffusion across conversations. |
| Shape Up shaped work and appetite. | Every long task needs appetite, non-goals, circuit breaker, and stop conditions before worker conversations start. | Avoid spending hours after an initial misunderstanding. |
| Hermes/OpenClaw local projects emphasize operator experience, notifications, skills/hooks, and memory boundaries. | Human-intervention UX, task packets, and memory promotion are first-class artifacts. Hooks are hard constraints, not optional context. | Operator experience is part of system correctness. |
| Agent-team and arena projects show peer communication and comparative execution are useful but fragile. | Use direct peer communication only with copied packets and a coordinator-visible transcript. Use arena worktrees only for bounded design/code alternatives. | Peer chat without durable evidence is not recoverable. |

## Issue Register Resolution Map

| Issue group | V1 resolution | Still unresolved |
|---|---|---|
| CAI-001 canonical task vs conversation state | Canonical task charter is the durable object. Conversations are execution surfaces linked to the task. | Automatic App/VSCode thread reconciliation remains experimental. |
| CAI-002/003/016 dynamic task teams and conversation criteria | Use topology selector below. Create scoped conversations only when evidence, risk, or parallelism justifies the overhead. | Automatic conversation creation is not approved. |
| CAI-004/017 context packs | Use layered context packs with relevance, freshness, and token-budget checks. | Need empirical context-size quality thresholds. |
| CAI-005/018 communication and contradiction handling | Packet-first communication. Peer direct messages must be copied to the coordinator-visible task log. Contradictions become review packets. | App-native cross-thread communication is not reliable enough yet. |
| CAI-006/022 worktrees and review economy | One integration surface per task team. Optional scoped worktrees for large or risky branches. Arena worktrees are bounded experiments only. | Automatic worktree provisioning is not approved. |
| CAI-007/024 goal ownership and task reshaping | Only PMO/Dispatch may change canonical task goal. Workers can propose reshaping through `review_required`. | Need runtime support for goal-change proposal records. |
| CAI-008/023 evidence and capability proof | Every result packet needs evidence paths, unknowns, risks, and next validation. Capability claims need proof-of-capability tasks. | Some tool/MCP capability proofs remain pending. |
| CAI-009/015/019 PMO/user boundary and human intervention | PMO owns user-facing asks. Blocker notifications compress the ask to one action, one reason, one resume path. | Email transport is design-only until separately approved. |
| CAI-010/011/021/025 capability domains, subagents, skills/hooks, knowledge promotion | Capability templates define what a worker needs. Subagents are disposable. Skills are selective context. Hooks are mandatory policy. Knowledge promotion requires review. | Need a knowledge-promotion queue implementation. |
| CAI-012/013 Codex App/VSCode state split and communication tests | Treat live sync as UI convenience only. Durable records live in project files. | Need repeatable App/VSCode/CLI state tests after runtime approval. |
| CAI-014/020 learning drift and anti-loop controls | Use problem-led research, appetite, circuit breakers, and "three repeated blocker" escalation. | Need metrics for semantic drift and repeated bad assumptions. |

## Task Topology Selector

The coordinator chooses the smallest topology that can meet acceptance.

| Topology | Use when | Avoid when |
|---|---|---|
| `direct_main` | One small change, low risk, acceptance obvious. | Work must be recoverable or reviewed by another conversation. |
| `single_scoped_conversation` | One bounded long-running task needs its own history and checkpoints. | Task has independent research, code, test, or Git tracks. |
| `task_team_parallel_slices` | Independent slices can progress with disjoint read/write scopes. | Slices need constant peer negotiation. |
| `manager_calls_subagents` | Fast read-only research, review, or bounded code inspection can return one structured result. | The helper needs memory, follow-up, Git, or long-running state. |
| `handoff_to_scoped_conversation` | A department or task worker should own execution until a result packet returns. | The parent still lacks task charter, acceptance, or context pack. |
| `review_board` | High-impact architecture, safety, security, or report claims need multiple lenses. | The question is already settled by tests or small evidence. |
| `arena_comparison` | Two or more bounded solution variants need side-by-side evidence. | Broad implementation would create expensive merge debt. |
| `incident_response` | Tool crash, Git explosion, activation loss, context corruption, or repeated failed attempts. | The issue is just slow but still making measurable progress. |

## Canonical Task Lifecycle

1. Intake: PMO records the user request as either a simple message or a
   candidate durable task.
2. Shape: Dispatch writes a task charter with goal, non-goals, appetite,
   acceptance, evidence, blockers, and stop conditions.
3. Gate: Security/DevOps/Verification declare required capability, data,
   tool, MCP, license, and worktree gates.
4. Topology: Dispatch selects the smallest topology that can satisfy the
   charter.
5. Context: A context pack is built for each scoped conversation. It contains
   only the task-relevant summary, source paths, decisions, constraints,
   unresolved questions, and output contract.
6. Execution: Workers produce checkpoints and result packets. Subagents can be
   used inside a worker only as short-lived helpers.
7. Interrupt: If a task hits auth, license, missing data, unsafe action, or
   review dependency, the worker emits a blocker notification and stops retrying
   past its circuit breaker.
8. Review: Verification, Security, domain reviewer, or PMO accepts, rejects, or
   requests rework based on evidence.
9. Integration: DevOps merges code/worktree output only after review gates.
10. Knowledge: Secretary promotes stable lessons into docs, skills, hooks, or
    indexes after review. Raw chat is not promoted directly.

## Context Pack Quality Model

Each scoped conversation receives a context pack, not the full project memory.

| Layer | Required content | Exclude |
|---|---|---|
| Task charter | canonical goal, non-goals, owner, state, acceptance, stop conditions | raw brainstorming not accepted by PMO |
| Project constraints | AGENTS boundary, safety rules, current approval gates, tool/MCP limits | secrets, personal paths outside approved boundary |
| Prior decisions | relevant accepted decisions and rejected alternatives | stale proposals superseded by later decisions |
| Evidence map | source paths, test logs, result files, external references, uncertainty | uncited claims |
| Working contract | write scope, worktree binding, result packet path, reviewer | broad "fix everything" instructions |
| Refresh trigger | what changed since the pack was built | entire chat transcript |

Quality gates:

- relevance: every included section must explain why the worker needs it;
- freshness: known superseded decisions must be marked or omitted;
- sufficiency: the worker can explain the task without asking for hidden chat;
- boundedness: if the pack is too large, split by task slice instead of
  dumping more context.

## Communication Protocol

Communication is packet-first:

```text
task_packet -> checkpoint_packet -> blocker_packet/result_packet -> review_packet
```

Rules:

1. The coordinator-visible task log is the source of truth.
2. Peer-to-peer worker communication is allowed only when both sides copy the
   request/result into coordinator-visible packets.
3. A worker cannot silently change another worker's acceptance criteria.
4. Contradictions become review packets with evidence and proposed resolution.
5. If a human decision is needed, the PMO emits one compressed user ask instead
   of letting multiple workers ask separately.

## Worktree Strategy

Default: one shared project workspace for small doc/design work.

Use a dedicated worktree when:

- the task changes many files or generated outputs;
- the task may conflict with another active worker;
- the task is a comparative arena experiment;
- Git status is already noisy and needs isolated staging;
- a long-running worker needs independent checkpoints.

Do not create a worktree just to appear parallel. Worktrees create merge and
review cost. The integration owner decides when a task team closes or squashes
worktree output.

## Human Intervention UX Baseline

Human intervention is a task state, not an informal chat complaint.

Trigger classes:

- `auth_required`: login, license, account, GUI activation, token, VPN;
- `input_required`: missing domain data, ambiguous task direction, manual file;
- `approval_required`: destructive, irreversible, high-risk, or policy-gated
  action;
- `manual_review_required`: simulation/video/report/hardware outcome needs
  human inspection;
- `incident_required`: repeated crash, corrupted state, unsafe path, runaway
  process, Git explosion.

Notification levels:

| Level | Channel | Use |
|---|---|---|
| `thread_only` | current conversation | Low urgency, main thread active. |
| `project_packet` | blocker notification file/result packet | Durable record required. |
| `email_requested` | future email adapter, not implemented in this task | User is absent and the task is blocked on human action. |
| `immediate_stop` | stop task and report | Continuing risks data loss, secrets, license churn, or destructive writes. |

Email is not implemented yet. The V1 design requires templates, dedupe keys,
and evidence paths before any sender is approved.

## Stress Test A: PX4 Log to Simulation Parameters

Suggested topology:

```text
PMO intake
  -> Dispatch shaping
  -> Data Sufficiency worker
  -> Method Research worker
  -> Identifiability worker
  -> Estimator Implementation worker
  -> Simulator Mapping worker
  -> Verification worker
  -> DevOps integration
  -> Secretary knowledge promotion
```

Key safeguards:

- first output is a parameter-identifiability matrix: observable, weakly
  observable, not observable from the log;
- papers/open-source references are evidence, not automatic implementation;
- estimator results are labeled provisional until validated in simulation;
- if MWORKS activation or license is lost, the simulation worker emits
  `auth_required` with one resume instruction and stops retrying;
- final integration requires code diff, metrics, scenario config, and a review
  packet that states what still needs manual tuning.

## Stress Test B: UE/Fab Scene Truth and RflySim-Like Product Line

Suggested topology:

```text
PMO product task
  -> Scene Source Gate
  -> Unreal MCP Capability Proof
  -> Truth Export worker
  -> Planning-Ready Occupancy worker
  -> Runtime Integration worker
  -> Algorithm Integration workers
  -> Verification and Manual Review
  -> DevOps integration
```

Key safeguards:

- Fab/Launcher automation remains a capability gate, not an assumption;
- local scene project is the fallback when Fab automation cannot complete;
- path-planning truth, collision, navmesh/occupancy, scale, and coordinate
  transforms are required evidence, not rendering screenshots;
- Unreal crash, Entry-map write probe risk, or missing editor listener triggers
  incident response and stops write probes;
- UI/product work starts only after truth/export/runtime gates are credible.

## Decisions Ready For Implementation

These are safe to implement without expanding runtime transport:

1. Task charter template.
2. Context pack template.
3. Scoped conversation packet template.
4. Blocker notification template.
5. Review packet template.
6. Static checks that verify required design files and templates exist.

These remain gated:

1. automatic conversation creation;
2. automatic email sending;
3. app-server transport;
4. automatic worktree provisioning;
5. new permanent departments;
6. broad hook rewrites;
7. tool/MCP expansion.

## Unresolved Questions To Carry Forward

- What exact context-pack size and structure maximizes model performance for
  this project?
- Which Codex App/VSCode/CLI session files can be treated as stable enough for
  repeatable cross-conversation tests?
- How should email notifications be sent without leaking sensitive data or
  creating notification spam?
- What is the minimal safe automatic worktree lifecycle?
- How should CoAgent detect semantic drift early enough to prevent hours of
  wrong execution?
- How should open-source project learning be scheduled so it remains
  problem-driven instead of drifting into broad summarization?
