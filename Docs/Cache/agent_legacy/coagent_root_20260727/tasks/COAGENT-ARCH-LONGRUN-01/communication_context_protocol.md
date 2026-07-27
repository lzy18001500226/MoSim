# COAGENT-ARCH-LONGRUN-01 Communication And Context Protocol

Date: 2026-05-30
Status: phase 2 draft

## Purpose

Define how multiple Codex conversations cooperate without relying on hidden
chat memory, raw transcript copying, or untracked peer instructions.

## Authority Model

| Object | Authority |
|---|---|
| canonical task charter | source of task goal and definition of done |
| shared task board | source of team state |
| mailbox | source of cross-conversation communication |
| context pack | source of worker starting context |
| result packet | source of worker output |
| review packet | source of acceptance or rework decision |
| raw chat | evidence only after summarized into a packet |

## Packet Types

### Task Packet

Owner: DispatchAgent

Contains:

- task id;
- canonical goal;
- local conversation objective;
- read/write scope;
- context pack path;
- result path;
- acceptance;
- stop condition;
- review owner.

### Context Pack

Owner: ContextMemoryAgent

Contains:

- shared task context;
- slice context;
- source paths;
- accepted decisions;
- excluded stale assumptions;
- forbidden assumptions;
- output contract.

### Context Delta

Owner: ContextMemoryAgent or KnowledgeSecretaryAgent

Contains:

- changed fact or decision;
- affected conversations;
- superseded documents;
- refresh requirement;
- whether acknowledgement is needed.

### Checkpoint Packet

Owner: worker conversation

Contains:

- current progress;
- evidence paths;
- assumptions;
- risks;
- next planned step;
- whether canonical goal still looks valid.

### Blocker Packet

Owner: worker conversation; routed by DispatchAgent

Contains:

- blocker class;
- last safe state;
- failed command/tool if any;
- human action required if any;
- resume packet path;
- circuit breaker state.

### Result Packet

Owner: worker conversation

Contains:

- conclusion;
- artifacts changed or produced;
- evidence;
- unknowns;
- risks;
- next action;
- requested review owner;
- context delta proposal.

### Review Packet

Owner: VerificationAgent, SafetyComplianceAgent, ProductStrategyAgent,
DevOpsReleaseAgent, or MainAgent depending on risk.

Contains:

- accepted/rejected/rework/blocker disposition;
- evidence checked;
- concerns;
- required rework;
- integration permission.

### Integration Packet

Owner: DevOpsReleaseAgent

Contains:

- accepted slices;
- merge order;
- diff scope;
- checks;
- rollback plan;
- final Git/release status.

## Mailbox Rules

1. Every cross-conversation message must have a `message_type`.
2. Every message must name `task_id`, sender, receiver, and expected response.
3. Peer-to-peer messages are allowed only when copied into the shared mailbox.
4. No mailbox message may change the canonical task goal directly.
5. Contradictions create `review_request`, not silent overwrite.
6. Closed conversations cannot receive new work; create a new scoped
   conversation or reopen through Dispatch.

Durable storage, acknowledgement records, replay, timeout/retry, contradiction
resolution, and closeout recovery are defined in
`mailbox_ledger_and_replay_design.md`. This protocol defines the vocabulary;
the ledger design defines recoverability.

## Allowed Message Types

- `task_packet`
- `context_refresh`
- `checkpoint`
- `blocker`
- `decision_required`
- `review_request`
- `integration_request`
- `result_packet`
- `closeout`

## Forbidden Message Types

- `raw_chat_forward`
- `unscoped_instruction`
- `silent_goal_change`
- `unreviewed_merge_request`
- `credential_request_without_policy`
- `retry_forever`

## Context Layers

### Project Baseline

Stable rules:

- AGENTS boundary;
- current CoAgent status;
- active gates;
- safety rules;
- document map.

### Task Shared Context

Task-specific:

- canonical goal;
- non-goals;
- accepted facts;
- current blockers;
- shared definitions;
- current topology.

### Slice Context

Conversation-specific:

- local objective;
- read/write scope;
- relevant source files;
- prior outputs this slice depends on;
- output contract.

### Subagent Context

One-shot:

- bounded question;
- source scope;
- expected answer shape;
- forbidden actions;
- parent result path.

## Context Quality Gates

Before dispatching a context pack:

- `relevance_ok`: every section has a reason to be included;
- `freshness_ok`: superseded decisions are excluded or marked;
- `sufficiency_ok`: the worker can explain the task without hidden chat;
- `boundedness_ok`: pack is compact enough for the worker to reason well.

If `boundedness_ok` fails:

```text
split the task by slice
```

Do not solve it by pasting more transcript.

## Contradiction Handling

If two conversations disagree:

1. Dispatch records contradiction on task board.
2. Each side submits evidence paths and local assumptions.
3. Verification or relevant reviewer writes a review packet.
4. Dispatch records accepted resolution.
5. ContextMemoryAgent publishes context delta.
6. Affected conversations acknowledge refresh before continuing.

## Stale Context Handling

A context pack becomes stale when:

- canonical task goal changes;
- a review rejects an assumption;
- a tool capability is disproved;
- a source path moves;
- a blocker changes what work is safe;
- a newer decision supersedes the pack.

Stale context response:

- pause affected slice if it may continue in wrong direction;
- issue `context_refresh`;
- require acknowledgement before high-risk work resumes.

## Human-Facing Compression

Only MainAgent/PMO should ask the user for action.

User asks must contain:

- one requested action;
- one reason;
- last safe state;
- exact resume condition;
- whether the task can continue elsewhere meanwhile.

Multiple departments must not independently ask the user for the same login,
license, GUI, or approval action.
