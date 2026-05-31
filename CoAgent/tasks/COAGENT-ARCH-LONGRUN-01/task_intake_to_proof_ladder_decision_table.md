# COAGENT-ARCH-LONGRUN-01 Task Intake To Proof Ladder Decision Table

Date: 2026-05-30
Status: design decision table

## Purpose

Define how one user task chooses the first proof path, task team, context pack,
and blocker policy. This prevents CoAgent from routing by a fixed department
chart or by whichever conversation happens to be open.

This is design-only. It does not authorize automatic conversation creation,
worktree creation, live dispatch, tool/MCP execution, email, or unattended
automation.

## Core Rule

```text
The task selects the proof path. The proof path selects the first team.
Departments provide capabilities; they do not define the task boundary.
```

## Intake Classifier

Dispatch should classify each serious user task into one primary class and any
secondary risks.

| Class | Trigger | First Proof Path | First Gate |
|---|---|---|---|
| `architecture_mechanics` | task is about CoAgent communication, context, review, runtime, packets, or operating model | Candidate A | proof-package preflight |
| `data_parameter_identification` | task asks to infer simulation/model parameters from logs, experiments, papers, or datasets | Candidate B | data sufficiency and identifiability |
| `scene_truth_productization` | task asks to import/use UE/Fab/local scenes, generate map truth, or support planning/navigation | Candidate C | scene-source and tool capability |
| `git_heavy_change` | task involves many renames, imports, deletes, generated outputs, large assets, or risky staging | Candidate D | change inventory and Git safety |
| `auth_license_interruption` | task is blocked by login, license, GUI activation, manual review, or tool unavailable state | Candidate E | blocker packet and resume condition |
| `ordinary_small_task` | task is bounded, low-risk, and fits one conversation | no proof package | main-thread completion plus targeted checks |
| `mixed_product_task` | task spans multiple classes, such as PX4 plus MWORKS tuning plus Git plus docs | start with highest-risk gate | Dispatch chooses ladder order |

## Secondary Risk Ordering

When a task has multiple classes, choose the first gate by this order:

1. `auth_license_interruption` if a tool/session/license is already blocking
   execution;
2. `git_heavy_change` if repository safety or large assets could corrupt the
   worktree;
3. `architecture_mechanics` if packet/context/review mechanics are not yet
   stable enough to run the product task;
4. `scene_truth_productization` if UE/Fab/source truth is the product
   bottleneck;
5. `data_parameter_identification` if data sufficiency is the product
   bottleneck;
6. `ordinary_small_task` only when none of the above applies.

Rationale:

```text
Safety, recoverability, and communication mechanics come before product
automation. Product work should not run on an unsafe worktree, blocked license,
or unvalidated packet chain.
```

## Team Selection By Proof Path

### Candidate A: Architecture Packet Chain

Required minimum team:

- MainAgent: PMO and final synthesis;
- DispatchAgent: task charter, workflow graph, mailbox, closeout;
- ContextMemoryAgent: context pack and context delta;
- VerificationAgent: review and trace eval;
- KnowledgeSecretaryAgent: promotion/rejection result.

First context pack must include:

- canonical task goal;
- Candidate A non-goals;
- proof package root;
- flat result packet contract;
- expected context delta;
- forbidden tools and automation.

Do not include:

- UE/MWORKS/Fab work;
- Git staging;
- worktree creation;
- automatic conversation creation;
- raw transcript.

### Candidate B: PX4 Parameter Identification

Required first team:

- MainAgent: user ask and manual data expectations;
- DispatchAgent: task charter and gate ordering;
- ProductStrategyAgent: what parameter claims matter for MoSim;
- ContextMemoryAgent: log/spec context pack;
- VerificationAgent: identifiability and evidence label review.

Conditional later team:

- RuntimePlatformAgent when estimator execution/runtime matters;
- ToolchainMCPAgent when MWORKS/Sysplorer health is required;
- DevOpsReleaseAgent when code/results need staged integration;
- KnowledgeSecretaryAgent when methods or templates are promoted.

First gate:

```text
log audit -> identifiability matrix -> method choice
```

Estimator or MWORKS tuning starts only after the matrix separates identifiable,
weakly identifiable, assumed, and non-identifiable parameters.

### Candidate C: UE Scene Truth

Required first team:

- MainAgent: product goal and manual-review expectations;
- DispatchAgent: scene truth task charter and proof path;
- ToolchainMCPAgent: UE/MCP/Fab/local scene capability;
- ProductStrategyAgent: RflySim-like product scope;
- VerificationAgent: truth versus rendering review.

Conditional later team:

- DevOpsReleaseAgent for large asset policy;
- SafetyComplianceAgent for license/manual-import blockers;
- ContextMemoryAgent for scene-source/context deltas;
- RuntimePlatformAgent if live UE dispatch or editor state becomes a runtime
  issue.

First gate:

```text
scene-source classification -> UE/MCP capability card -> truth manifest
```

Planning readiness remains false until truth artifacts exist or limitations
are explicitly accepted.

### Candidate D: Git Heavy Change

Required first team:

- MainAgent: scope and approval boundary;
- DispatchAgent: task state and integration request;
- DevOpsReleaseAgent: inventory, worktree binding, integration plan;
- SafetyComplianceAgent: destructive-action and external-path blockers;
- VerificationAgent: diff/check/review evidence.

First gate:

```text
change inventory -> path-family classification -> risk policy
```

No broad staging, commit, push, delete, move, or worktree creation occurs
inside proof validation.

### Candidate E: Auth/License/Manual Interruption

Required first team:

- MainAgent: user-facing ask;
- SafetyComplianceAgent: blocker type, redaction, dedupe, retry policy;
- DispatchAgent: last safe state and resume path;
- ToolchainMCPAgent or RuntimePlatformAgent: failing tool/session evidence;
- VerificationAgent: blocker completeness.

First gate:

```text
blocker packet -> exact PMO ask -> safe parallel work decision -> resume packet
```

Only MainAgent/PMO sends the user-facing ask. Other conversations may propose
it as a packet, not message the user directly.

## Decision Outputs

Every classified task should produce these outputs before execution:

| Output | Required For | Purpose |
|---|---|---|
| `task_charter` | all non-small tasks | canonical goal and non-goals |
| `proof_path` | all proof tasks | selected Candidate A-E or ordinary path |
| `first_gate` | all proof tasks | earliest falsifiable stop/check |
| `minimum_team` | all proof tasks | conversations that must exist first |
| `context_pack_path` | all delegated work | curated context, not transcript |
| `result_packet_contract` | all delegated work | durable return path |
| `blocker_policy` | all proof tasks | stop/resume behavior |
| `review_owner` | all proof tasks | independent acceptance |
| `integration_owner` | any file/Git work | merge and closeout authority |

## Example Routing

### PX4 Log Parameter Task

User asks:

```text
Use this PX4 log to derive simulation parameters and tune MoSim.
```

Classifier:

```text
primary: data_parameter_identification
secondary: auth_license_interruption if MWORKS activation is needed later
proof_path: Candidate B
first_gate: log audit and identifiability matrix
minimum_team: MainAgent, DispatchAgent, ProductStrategyAgent,
  ContextMemoryAgent, VerificationAgent
```

Do not start:

- estimator implementation;
- MWORKS simulation tuning;
- Git integration;
- docs promotion;

until the first gate states what can and cannot be identified.

### UE Scene Truth Task

User asks:

```text
Use Fab/local UE maps to build planning truth and integrate navigation.
```

Classifier:

```text
primary: scene_truth_productization
secondary: git_heavy_change if large imported assets are involved
proof_path: Candidate C, then Candidate D if assets enter Git scope
first_gate: scene-source classification and UE/MCP capability card
minimum_team: MainAgent, DispatchAgent, ToolchainMCPAgent,
  ProductStrategyAgent, VerificationAgent
```

Do not start:

- path planning claims;
- algorithm integration;
- map editing;
- broad asset staging;

until scene truth capability is established.

### CoAgent Communication Task

User asks:

```text
Prove multiple conversations can coordinate one task safely.
```

Classifier:

```text
primary: architecture_mechanics
proof_path: Candidate A
first_gate: proof-package preflight and fixture validation
minimum_team: MainAgent, DispatchAgent, ContextMemoryAgent,
  VerificationAgent, KnowledgeSecretaryAgent
```

Do not start product proofs B/C until Candidate A mechanics are stable or the
user explicitly accepts packet/transport risk.

## Anti-Drift Questions

At each checkpoint, Dispatch should answer:

1. Is the task still on the selected proof path?
2. Did any worker expand the canonical goal?
3. Has a secondary risk become primary?
4. Is the first gate passed, blocked, or still unknown?
5. Are we starting implementation before proof-package preflight?
6. Are we using a department because it is needed or because it exists?
7. Has a context delta changed another conversation's assumptions?
8. Is there a review owner who can reject the result?

If any answer is unclear, stop expansion and emit `decision_required` or a
blocker packet.

## Design Decision

This decision table becomes the routing bridge between user intake and the A-E
proof ladder. New task classes should be added here only when they cannot be
honestly represented as one of the existing classes plus secondary risks.
