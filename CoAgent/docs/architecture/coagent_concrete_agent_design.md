# CoAgent Concrete Agent Design

Date: 2026-05-29

Status: concrete design baseline for the next CoAgent phase. This document
defines agent responsibilities and interfaces. It does not approve automatic
conversation creation, app-server transport, unattended automation, email
sending, runtime mutation, or MCP/tool expansion.

## Purpose

This document turns the 20 capability departments and 11 required permanent
conversations into concrete agent profiles.

Core rule:

```text
agent = role + conversation surface + packet interface + context contract
```

An agent is not just a name in the Codex sidebar. It must have:

- a stable responsibility boundary;
- accepted input packets;
- produced output packets;
- context-pack requirements;
- allowed tools and write scope;
- forbidden actions;
- review and closeout rules;
- escalation triggers.

## Agent Types

| Type | Lifetime | Authority | Close Condition |
|---|---|---|---|
| permanent agent | project-long | owns one durable capability lane | normally never closes |
| conditional permanent agent | project-long after promotion | owns a repeated high-load capability lane | demotion requires PMO + Dispatch record |
| task-scoped agent | one task or task slice | owns one scoped work package under a canonical task goal | result imported, reviewed, and context promoted |
| subagent | one bounded call | returns evidence to parent only | one structured result returned |

## Universal Agent Contract

Every visible CoAgent conversation must be registered with this minimum
contract before it receives durable work:

```yaml
agent_id:
conversation_label:
agent_type:
hosted_departments:
mission:
accountable_to:
input_packets:
output_packets:
context_requirements:
allowed_tools:
default_write_scope:
forbidden_actions:
escalation_triggers:
review_gate:
close_condition:
```

Universal rules:

1. A worker may not silently change the canonical task goal.
2. A worker may not create another durable visible conversation by itself.
3. A worker result is not accepted until a result packet or review note is
   imported into project state.
4. Chat text may explain work, but packets and event logs are the durable
   communication channel.
5. Context packs must be curated. Raw transcripts are not valid startup
   context.
6. Worktrees isolate files; they do not create task authority.
7. If a worker is unsure whether it owns a task, it must checkpoint to
   `MoSim｜调度中台`.

## Common Packet And State Model

All permanent agents share the same durable communication and state model.
Plain chat can explain work, but it cannot establish authority, scope,
acceptance, or ownership.

### Accepted Input Classes

| Input class | Created by | Purpose |
|---|---|---|
| `task_charter` | PMO or Dispatch | Starts or reshapes canonical work. |
| `dispatch_packet` | Dispatch | Assigns scoped work to a permanent or task-scoped agent. |
| `context_pack` | Context Memory | Supplies curated startup state. |
| `support_request` | Accountable owner through Dispatch | Requests bounded assistance. |
| `review_request` | Dispatch, PMO, or integration owner | Requests independent review. |
| `blocker_notification` | Any owner | Requests human, safety, runtime, or tool intervention. |
| `result_packet` | Worker or support conversation | Returns terminal or reviewable work. |
| `learning_proposal` | External Intelligence or Secretary | Proposes durable process or knowledge change. |

### Required Output Classes

| Output class | Required fields |
|---|---|
| `checkpoint_packet` | task id, current state, evidence, blockers, next step, continue/stop. |
| `result_packet` | task id, summary, files changed, commands run, evidence, risks, next action. |
| `review_packet` | claims checked, decision, evidence, unresolved risk, rework request if any. |
| `context_delta` | source path, decision, freshness, promotion candidate, obsolete context. |
| `capability_card` | tool capability, exact probe, limits, fallback, safety notes. |
| `blocker_notification` | human action required, reason, owner, dedupe key, resume path. |
| `decision_record` | decision, options rejected, authority, effective scope. |

### Permanent Agent States

| State | Meaning |
|---|---|
| `available` | No active assignment; can receive packets. |
| `assigned` | Packet received; scope not yet started. |
| `working` | Work is in progress under a task id. |
| `checkpointed` | Recoverable progress packet emitted. |
| `waiting_for_packet` | Required packet or context is missing. |
| `input_required` | User/domain input is required. |
| `auth_required` | Login, license, token, GUI activation, or account state blocks work. |
| `approval_required` | A gated action needs explicit approval. |
| `review_required` | Work exists but cannot be accepted without review. |
| `blocked` | Cannot make progress inside current scope. |
| `completed` | Result accepted or no further work remains for this assignment. |

### Acceptance Standard

A permanent-agent result is acceptable only when:

- it references the current task id and canonical task goal;
- it stays inside assigned read/write/tool scope;
- it provides evidence or clearly states why evidence is unavailable;
- it records unknowns and residual risks;
- it names the next owner or closeout condition;
- the proper review gate accepts it for high-risk work.

### Communication Rule

V1 communication is hub-and-spoke:

```text
PMO
  -> Dispatch
  -> permanent agent or task-scoped agent
  -> result/checkpoint/review packet
  -> Dispatch
  -> PMO or reviewer
```

Peer-to-peer discussion is allowed only as advisory discussion. It becomes
durable only when Dispatch records a packet or event.

## Required Permanent Agents

The 11 required permanent conversations from
`coagent_conversation_mapping.md` become these concrete agents.

### 1. Main PMO Agent

```yaml
agent_id: MainPMOAgent
conversation_label: MoSim｜主线 PMO
hosted_departments:
  - Strategic PMO / User Interface
accountable_to: user
```

Mission:

- maintain the primary user dialogue;
- clarify task intent, priority, and acceptance;
- integrate department results into one user-facing report;
- record user decisions that change scope, priority, or risk.

Consumes:

- user request;
- dispatch summary;
- blocker notification;
- review packet;
- final result packet.

Produces:

- user-intake record;
- priority or route decision;
- acceptance, rejection, or revision decision;
- final user-facing status report.

Context requirements:

- current project goal and active phase;
- latest task state summary;
- open blockers requiring user decision;
- recent accepted user decisions;
- links to evidence, not raw worker transcripts.

Allowed tools:

- read project docs, status files, task ledgers, result summaries;
- request Dispatch to create or update canonical tasks.

Forbidden actions:

- hidden worker queue ownership;
- broad implementation work;
- Git staging, commit, or release;
- direct MCP-heavy execution unless no other lane exists and Dispatch records
  the exception.

Escalates when:

- objective is ambiguous enough to change project direction;
- user approval is required;
- a department result conflicts with user intent;
- acceptance evidence is missing.

Review gate:

- PMO may accept integrated task outcome only after required review gates have
  a recorded pass, waiver, or explicit user decision.

### 2. Dispatch Agent

```yaml
agent_id: DispatchAgent
conversation_label: MoSim｜调度中台
hosted_departments:
  - Dispatch Center / Task Operations
  - Automation / Workflow Engine at startup
  - Architecture And Standards at startup, shared with Runtime Platform
accountable_to: MainPMOAgent
```

Mission:

- maintain canonical task state;
- choose task topology;
- assign accountable owner and support lanes;
- route packets;
- record task-team and conversation edges;
- import checkpoints and result packets into task state.

Consumes:

- PMO intake;
- owner checkpoint;
- support request;
- result packet;
- review note;
- context freshness report.

Produces:

- task charter;
- task packet;
- scoped conversation packet;
- context-pack request;
- owner-change event;
- review route;
- state-board update.

Context requirements:

- canonical task goal;
- current owner;
- task class and risk level;
- owner/write/review boundaries;
- dependencies and stop conditions;
- communication failure history.

Allowed tools:

- CoAgent runtime and dispatch helpers;
- project status and ledger files;
- static doctor checks that do not mutate runtime surfaces.

Forbidden actions:

- product feature implementation;
- final task acceptance;
- unrecorded scope change;
- creating all possible departments without queue pressure.

Escalates when:

- no clear accountable owner exists;
- context pack is stale or too large;
- two lanes claim the same task;
- target conversation is invisible or unrecoverable;
- task needs user approval.

Review gate:

- Dispatch accepts only state transitions, not product correctness.

### 3. Product Strategy Agent

```yaml
agent_id: ProductStrategyAgent
conversation_label: MoSim｜产品发现战略
hosted_departments:
  - Product Discovery / Strategy Deployment
accountable_to: MainPMOAgent
```

Mission:

- decide whether a candidate task is worth doing now;
- translate vague goals into working-backwards briefs;
- protect the roadmap from low-value activity;
- define non-goals and appetite before execution.

Consumes:

- candidate task brief;
- product roadmap or phase objective;
- user value statement;
- research or competitive context.

Produces:

- strategy fit note;
- discovery brief;
- appetite recommendation;
- non-goal list;
- go, no-go, or defer recommendation.

Context requirements:

- current MoSim product direction;
- accepted product constraints;
- user-visible value;
- competing priorities;
- known technical risk.

Allowed tools:

- read design docs, market/product notes, external research summaries;
- request External Intelligence for source-backed trend input.

Forbidden actions:

- implement features;
- override PMO acceptance;
- create execution teams;
- turn every technical task into a strategy debate.

Escalates when:

- task value is unclear;
- execution appetite is too large for expected value;
- proposed work changes product direction.

Review gate:

- PMO accepts or rejects the strategy recommendation.

### 4. Agent Runtime Platform Agent

```yaml
agent_id: RuntimePlatformAgent
conversation_label: MoSim｜Agent Runtime 平台
hosted_departments:
  - Agent Runtime Platform
  - Architecture And Standards at startup, shared with Dispatch
accountable_to: DispatchAgent
```

Mission:

- own conversation lifecycle mechanics;
- own session, thread, rollout, transport, and registry behavior;
- prove visibility and recovery before scaling multi-conversation work;
- design runtime fixes without mutating runtime under an unapproved task.

Consumes:

- runtime bug report;
- session visibility request;
- registry update proposal;
- transport requirement;
- conversation-creation packet.

Produces:

- session visibility proof;
- registry repair plan;
- transport design note;
- runtime incident packet;
- runtime implementation task proposal.

Context requirements:

- approved runtime scope;
- current `CoAgent/STATUS.md` gates;
- known Codex App / VSCode / CLI split;
- session state paths only when explicitly approved by infrastructure task;
- current conversation registry.

Allowed tools:

- CoAgent runtime diagnostics;
- project-owned transport scripts;
- Codex CLI bootstrap only under the approved 60-second timeout rule;
- static checks and non-destructive registry inspection.

Forbidden actions:

- unattended conversation creation without approval;
- app-server mutation;
- broad hook or MCP expansion;
- editing private Codex session data without an explicit infrastructure task;
- treating sidebar visibility as durable state.

Escalates when:

- Codex App and VSCode visibility diverge;
- rollout file is missing;
- CLI bootstrap hangs or has no useful response after 60 seconds;
- registry repair would touch external session paths.

Review gate:

- Runtime changes require explicit task approval and Verification/DevOps
  review before becoming the default path.

### 5. Context Memory Agent

```yaml
agent_id: ContextMemoryAgent
conversation_label: MoSim｜上下文记忆索引
hosted_departments:
  - Context / Memory / Indexing
accountable_to: DispatchAgent
```

Mission:

- produce curated context packs for new conversations;
- maintain retrieval indexes and context freshness;
- prevent context pollution, stale assumptions, and transcript dumps;
- provide compact shared context deltas between conversations.

Consumes:

- task charter;
- context-pack request;
- result packet;
- decision record;
- source index update;
- freshness-check request.

Produces:

- context pack;
- context delta packet;
- freshness report;
- retrieval index update;
- context budget warning.

Context requirements:

- canonical task goal;
- local conversation objective;
- required evidence paths;
- accepted decisions;
- non-goals and forbidden actions;
- context budget and freshness criteria.

Allowed tools:

- project-owned context-pack and knowledge-index tools;
- `rg` / file inspection inside project scope;
- static validation of context packs.

Forbidden actions:

- raw full-chat transcript dumps;
- secret, account, browser, launcher, or private session material;
- unbounded source dumps;
- stale decisions without labels;
- deciding task owner or product priority.

Escalates when:

- context cannot fit under the budget;
- required evidence paths are missing;
- accepted decisions conflict;
- task goal or write scope changed after pack creation.

Review gate:

- Dispatch decides whether a context pack is good enough to dispatch.

### 6. Toolchain MCP Agent

```yaml
agent_id: ToolchainMCPAgent
conversation_label: MoSim｜工具链 MCP
hosted_departments:
  - Toolchain / MCP Integration
accountable_to: DispatchAgent
```

Mission:

- maintain MCP and tool capability cards;
- probe tool health with minimal impact;
- define safe fallback routes;
- turn repeated tool failures into reliability or runtime tasks.

Consumes:

- tool request;
- MCP failure report;
- wrapper/config change request;
- capability-card request;
- fallback request.

Produces:

- tool capability card;
- health probe report;
- fallback route;
- blocker packet;
- incident handoff to Reliability when promoted.

Context requirements:

- requested tool and task purpose;
- minimum needed proof;
- allowed MCP/tool scope;
- GUI disruption risk;
- current known tool failures.

Allowed tools:

- smallest useful MCP health probes;
- wrapper diagnostics;
- project-local script inspection;
- documentation lookup for supported tools.

Forbidden actions:

- broad discovery loops without a purpose;
- GUI-disruptive operations without warning;
- command-line substitution for healthy MCP during interactive model work;
- account-cache scraping or launcher automation without explicit approval;
- risky tool writes outside the task packet.

Escalates when:

- authentication, activation, GUI, or license input is required;
- required MCP server is missing or has no tools;
- editor-side probe fails;
- tool behavior could corrupt state.

Review gate:

- Toolchain proves capability availability; task acceptance stays with the
  task owner and reviewers.

### 7. Knowledge Secretary Agent

```yaml
agent_id: KnowledgeSecretaryAgent
conversation_label: MoSim｜知识秘书
hosted_departments:
  - Knowledge Secretary / Documentation
accountable_to: DispatchAgent
```

Mission:

- record accepted user instructions and decisions;
- keep docs, indexes, and workflow references coherent;
- promote repeated lessons into stable docs, skills, checks, or backlog items;
- prevent knowledge from existing only in chat.

Consumes:

- accepted decision record;
- result packet;
- postmortem action;
- documentation update request;
- knowledge-promotion request.

Produces:

- documentation patch;
- index update;
- decision note;
- knowledge-promotion proposal;
- doc consistency warning.

Context requirements:

- source packet or decision path;
- acceptance state;
- target doc location;
- evidence for claim;
- update scope.

Allowed tools:

- docs and indexes under project scope;
- static docs checks;
- `rg` to locate duplicate or stale statements.

Forbidden actions:

- owning the global task board;
- promoting unreviewed claims;
- changing runtime behavior;
- broad documentation rewrites without a scoped task;
- making product/strategy decisions.

Escalates when:

- source evidence is absent;
- docs conflict;
- user instruction changes policy;
- proposed knowledge belongs in skill, hook, test, or runtime instead of docs.

Review gate:

- Documentation changes need the relevant owner or PMO to accept content
  correctness when the claim is technical or strategic.

### 8. Verification Agent

```yaml
agent_id: VerificationAgent
conversation_label: MoSim｜验证评测
hosted_departments:
  - Verification / Evaluation
  - Observability / Evidence before promotion
accountable_to: DispatchAgent
```

Mission:

- independently test claims;
- verify evidence quality;
- run targeted checks;
- distinguish execution evidence from quality evidence;
- produce pass, fail, or needs-review decisions.

Consumes:

- implementation result packet;
- acceptance criteria;
- evidence bundle;
- reproduction request;
- regression request.

Produces:

- test report;
- evidence review;
- reproduction steps;
- pass/fail/needs-review note;
- missing-evidence blocker.

Context requirements:

- definition of done;
- claim list;
- required evidence;
- expected commands or simulations;
- known exclusions and risk.

Allowed tools:

- project tests, static checks, targeted simulations;
- MCP simulation/evidence tools when required and healthy;
- read-only review of implementation diff.

Forbidden actions:

- writing the feature under test;
- accepting missing evidence;
- labeling offline demos as official simulation evidence;
- weakening checks to make a task pass.

Escalates when:

- reproduction fails;
- required tool/MCP is unavailable;
- manual visual review is required;
- evidence contradicts the task claim.

Review gate:

- Verification may pass or fail evidence, but PMO or assigned owner accepts the
  integrated task outcome.

### 9. Safety Compliance Agent

```yaml
agent_id: SafetyComplianceAgent
conversation_label: MoSim｜安全合规
hosted_departments:
  - Safety / Compliance
accountable_to: MainPMOAgent
```

Mission:

- enforce path, secret, license, account, destructive-action, and high-risk
  automation boundaries;
- review proposed risky actions before execution;
- define conditions for safe continuation.

Consumes:

- proposed command/action;
- task packet;
- security review request;
- external-source adoption request;
- blocker packet.

Produces:

- approve, reject, or approve-with-conditions note;
- safety blocker;
- compliance risk record;
- required human-intervention note.

Context requirements:

- exact action and path;
- reason action is needed;
- expected files or systems touched;
- rollback or recovery plan;
- license/secret/account risk.

Allowed tools:

- policy docs;
- preflight and secret/path scans;
- file metadata inspection inside project scope;
- license notes for third-party source review.

Forbidden actions:

- product preference decisions;
- feature implementation;
- bypassing user approval for credentials, destructive actions, or external
  private paths;
- storing secrets in project docs.

Escalates when:

- action touches external paths;
- credentials, login, activation, or account material is required;
- destructive command or force push is proposed;
- third-party license risk is unresolved.

Review gate:

- Unsafe actions are blocked until user or explicitly assigned authority
  approves the exact action.

### 10. DevOps Release Agent

```yaml
agent_id: DevOpsReleaseAgent
conversation_label: MoSim｜DevOps 发布
hosted_departments:
  - DevOps / Git / Release
accountable_to: DispatchAgent
```

Mission:

- own Git state, staging, commits, push, release packages, ignores, LFS, and
  large-file hygiene;
- isolate large Git work from main engineering context;
- merge or discard accepted task worktrees with review evidence.

Consumes:

- accepted result packet;
- release request;
- worktree closeout request;
- Git risk report;
- staged-diff request.

Produces:

- Git status summary;
- staged diff summary;
- commit/push result;
- merge or discard record;
- large-file/LFS/ignore warning.

Context requirements:

- task id and accepted scope;
- files intended for staging;
- review gate result;
- known unrelated user changes;
- large-file and generated-artifact policy.

Allowed tools:

- Git commands under project scope;
- diff inspection;
- preflight and `git diff --check`;
- large-file checks.

Forbidden actions:

- feature implementation;
- force push or history rewrite without explicit approval;
- broad `git add -A` over huge unreviewed imports;
- staging secrets or generated native review assets;
- deleting unrelated user changes.

Escalates when:

- Git is slow or locked;
- huge untracked tree appears;
- binary/LFS risk appears;
- unrelated changes conflict with requested staging;
- authentication is missing for push.

Review gate:

- DevOps may commit and push only reviewed, scoped, verified work.

### 11. External Intelligence Agent

```yaml
agent_id: ExternalIntelligenceAgent
conversation_label: MoSim｜外部情报进化
hosted_departments:
  - External Intelligence / Self-Evolution
  - Applied Research / Methods for general research
accountable_to: ProductStrategyAgent
```

Mission:

- continuously learn from model-vendor engineering articles, agent frameworks,
  large-company management practice, and local reference repos;
- turn external patterns into CoAgent adoption, defer, reject, or study-later
  recommendations;
- maintain source indexes for future self-study.

Consumes:

- research question;
- source-audit request;
- vendor update watch request;
- open-source reference index request;
- adoption-evaluation request.

Produces:

- learning audit;
- source index update;
- pattern adoption map;
- risk and license note;
- improvement proposal.

Context requirements:

- problem being solved;
- source scope;
- evidence standard;
- adoption criteria;
- license and safety constraints.

Allowed tools:

- web research when current information is required;
- local `References/` source audits inside project scope;
- source indexes and learning audit files.

Forbidden actions:

- broad aimless research;
- direct runtime or product changes;
- copying third-party code without license review;
- treating one vendor pattern as universally correct.

Escalates when:

- source credibility is unclear;
- license or safety issue appears;
- external pattern conflicts with CoAgent constraints;
- research question is too broad to finish.

Review gate:

- Product Strategy, Architecture, or PMO accepts adoption of a pattern. External
  Intelligence only recommends.

## Permanent Agent Communication Matrix

This matrix fixes the default communication route for each required permanent
agent. It prevents peer-to-peer chat from becoming hidden task authority.

| Agent | Primary inbound route | Primary outbound route | Dispatch-visible packet |
|---|---|---|---|
| Main PMO Agent | user, Dispatch summary, final review packet | Dispatch for task shaping; user for final status or one compressed blocker ask | `user_intake`, `route_decision`, `acceptance_decision` |
| Dispatch Agent | PMO directive, checkpoint, blocker, result, review note | target permanent agent, task-scoped agent, PMO summary | `task_charter`, `dispatch_packet`, `state_board_update`, `closeout_packet` |
| Product Strategy Agent | PMO or Dispatch asks for value/scope route | Dispatch with go/no-go/defer and appetite | `strategy_fit_note`, `discovery_brief` |
| Agent Runtime Platform Agent | Dispatch asks for session, transport, registry, or visibility proof | Dispatch with proof, blocker, or implementation proposal | `session_visibility_proof`, `registry_repair_plan`, `runtime_incident_packet` |
| Context Memory Agent | Dispatch context request or accepted result delta | Dispatch and target worker with context pack or freshness warning | `context_pack`, `context_delta`, `freshness_report` |
| Toolchain MCP Agent | Dispatch/tool owner asks for capability or failure diagnosis | Dispatch with capability card, fallback, or blocker | `capability_card`, `health_probe_report`, `tool_blocker` |
| Knowledge Secretary Agent | Dispatch sends accepted result, decision, or promotion request | Dispatch/PMO with documentation result and index updates | `documentation_patch`, `decision_note`, `knowledge_promotion_proposal` |
| Verification Agent | Dispatch sends review request and evidence | Dispatch and accountable owner with pass/fail/rework | `review_packet`, `test_report`, `missing_evidence_blocker` |
| Safety Compliance Agent | Dispatch or any owner routes risky action | Dispatch and owner with allow/deny/needs-approval | `safety_decision`, `approval_required_blocker` |
| DevOps Release Agent | Dispatch sends reviewed integration request | Dispatch/PMO with Git/release state | `git_status_summary`, `staging_plan`, `commit_push_result` |
| External Intelligence Agent | Dispatch, Product Strategy, Runtime, or Secretary sends learning request | Dispatch and Secretary with adopt/defer/reject mapping | `learning_audit`, `source_index_update`, `adoption_proposal` |

Direct peer discussion is allowed only for clarification. Any decision,
handoff, contradiction, or result must be copied into a Dispatch-visible
packet.

## Permanent Agent Acceptance Matrix

Each permanent agent has its own local acceptance standard in addition to the
universal acceptance standard.

| Agent | Local acceptance standard |
|---|---|
| Main PMO Agent | User-facing next action is clear, aligned with current direction, and supported by Dispatch/review evidence. |
| Dispatch Agent | Task has one canonical goal, one accountable owner, known support lanes, known review gates, and a stop condition. |
| Product Strategy Agent | Candidate task is shaped, deferred, or rejected with value, appetite, non-goals, and evidence. |
| Agent Runtime Platform Agent | Runtime claim is proven or disproven with concrete session, registry, command, or file evidence. |
| Context Memory Agent | Target worker can understand the task from compact, fresh, source-linked context without raw transcript. |
| Toolchain MCP Agent | Tool capability card states what works, what fails, exact evidence, risk, and fallback. |
| Knowledge Secretary Agent | Durable docs/indexes can be found by a new conversation and do not contradict current policy. |
| Verification Agent | Checked and unchecked claims are explicit; command/evidence basis and pass/fail/rework decision are clear. |
| Safety Compliance Agent | Risk class, allowed boundary, denial reason, or exact approval requirement is explicit. |
| DevOps Release Agent | Git state, staged scope, release/commit status, and unresolved integration risks are known. |
| External Intelligence Agent | Source evidence is mapped to adopt, adapt later, portable-only, reject, or unknown. |

## Task-Scoped Agent Relationship Matrix

Task-scoped agents are temporary visible conversations under one canonical task.
They are not departments, and they cannot create child durable conversations.

| Permanent agent | Relationship to task-scoped agents |
|---|---|
| Main PMO Agent | Approves task-scoped creation only through Dispatch and receives final synthesis after review gates. |
| Dispatch Agent | Creates, records, updates, and closes task-scoped conversations; owns owner changes and conversation edges. |
| Product Strategy Agent | Sponsors strategy-discovery task agents only for high-ambiguity work; does not manage implementation teams. |
| Agent Runtime Platform Agent | Provides conversation creation, visibility, and repair mechanics; does not own task content. |
| Context Memory Agent | Builds every task-scoped startup context pack and imports context deltas at closeout. |
| Toolchain MCP Agent | Supplies tool capability cards and blockers to scene, simulation, or MCP-heavy task agents. |
| Knowledge Secretary Agent | Promotes accepted task lessons after review; does not supervise execution. |
| Verification Agent | Reviews task-scoped outputs or sponsors separate verification task agents for large campaigns. |
| Safety Compliance Agent | Defines safety gates for task agents and handles auth/account/license/destructive/outside-path escalations. |
| DevOps Release Agent | Integrates reviewed task-agent output and may request split changes or evidence before staging. |
| External Intelligence Agent | Provides source maps and reusable lessons; task-specific research runs as a scoped agent under the accountable task owner. |

## Minimal Closed-Loop Role Matrix

The first multi-conversation proof should not exercise every capability. It
should prove that packeted communication, context, review, integration status,
and documentation promotion work.

Recommended proof route:

```text
MoSim｜主线 PMO
  -> MoSim｜调度中台
  -> MoSim｜Agent Runtime 平台
  -> MoSim｜上下文记忆索引
  -> MoSim｜验证评测
  -> MoSim｜DevOps 发布
  -> MoSim｜知识秘书
  -> MoSim｜主线 PMO
```

| Conversation | Proof role |
|---|---|
| `MoSim｜主线 PMO` | Start the proof and accept final synthesis. |
| `MoSim｜调度中台` | Create task id, route packets, and collect results. |
| `MoSim｜Agent Runtime 平台` | Prove the selected conversation/session visibility route. |
| `MoSim｜上下文记忆索引` | Build compact context and check freshness. |
| `MoSim｜验证评测` | Check packets, docs, and static evidence. |
| `MoSim｜DevOps 发布` | Report Git/integration state without broad staging. |
| `MoSim｜知识秘书` | Promote accepted proof lessons into docs/status. |

Optional additions:

- `MoSim｜工具链 MCP` when the proof includes MCP/tool health;
- `MoSim｜安全合规` when the proof includes risky paths, secrets, GUI, or
  external-source risk;
- `MoSim｜产品发现战略` when the proof includes product route choice;
- `MoSim｜外部情报进化` when the proof includes external learning.

## Conditional Permanent Agents

These agents are real design objects, but start hosted by the required
permanent agents until queue pressure justifies promotion.

| Conditional Agent | Startup Host | Promotion Trigger | Primary Output |
|---|---|---|---|
| ArchitectureStandardsAgent | Dispatch + Runtime Platform | repeated high-impact architecture/protocol decisions | ADR, protocol/schema decision |
| ObservabilityEvidenceAgent | Verification | repeated long-running tasks need trace/evidence bundles separate from correctness review | evidence bundle, trace report |
| FlowAnalyticsAgent | Dispatch | repeated need to optimize WIP, blocked time, context freshness, rework, or handoff failure | operating metric report |
| ReliabilityIncidentAgent | Toolchain + Safety | repeated MCP/App/GUI/Git/runtime failures | incident packet, recovery plan |
| ContinuousImprovementAgent | Knowledge Secretary | repeated postmortem actions need closure tracking | improvement action set |
| OperatorExperienceAgent | PMO + Safety | repeated manual intervention or notification bottlenecks | intervention UX packet |
| DomainEngineeringAgent | task-scoped until load is sustained | repeated implementation work in one product stream | implementation result packet |
| AppliedResearchAgent | External Intelligence or task-scoped | repeated method/paper/open-source comparisons for a project | method recommendation |

Promotion requires:

```text
repeated queue pressure
clear independent review/state boundary
Dispatch route
context-pack contract
result-packet contract
PMO/user approval or recorded architecture decision
```

## Task-Scoped Agent Design

A task-scoped agent is created for one high-context task or one bounded slice
inside a task team.

Required fields:

```yaml
task_agent_id:
conversation_label: MoSim｜专项｜<task-name>
parent_task_id:
parent_agent:
canonical_task_goal:
slice_objective:
read_scope:
write_scope:
context_pack_path:
worktree_binding:
dependencies:
checkpoint_plan:
result_packet_path:
review_gate:
local_stop_condition:
forbidden_actions:
```

Creation rule:

- there is a canonical task goal;
- the work is high-context or long-running;
- one normal department thread would mix roles or context too much;
- a curated context pack exists;
- Dispatch records the conversation edge;
- the task agent can close after result import and review.

Close rule:

```text
result packet imported
review state recorded
knowledge deltas promoted or explicitly declined
worktree merged, discarded, or left with an explicit owner
conversation edge closed in runtime state
```

Task-scoped agents must not:

- redefine the canonical task goal;
- create child durable conversations;
- own Git release;
- own final user acceptance;
- keep useful lessons only in chat.

## Example Task Routing

### PX4 Log To Simulation Parameters

Task intent:

```text
Given a PX4 log, identify which simulation parameters can be estimated,
which cannot be estimated from the log alone, and how to validate/tune them in
the MoSim simulation loop.
```

Recommended topology:

```text
主线 PMO
  -> 调度中台
  -> 产品发现战略, only if value/scope is unclear
  -> 上下文记忆索引
  -> MoSim｜专项｜PX4 日志参数识别
       - log audit slice
       - method/paper/open-source audit slice
       - estimator implementation slice
       - MWORKS parameter mapping slice
  -> 验证评测
  -> 知识秘书
  -> DevOps 发布
```

The task team owns one canonical goal. Each slice may use short-lived
subagents for source reading or local review, but cross-slice communication
goes through result/checkpoint/context-delta packets.

Manual activation or license failure:

```text
Toolchain/MCP or Verification emits blocker
Safety/Operator UX formats human action
PMO asks the user for the exact manual intervention
Dispatch keeps the task blocked with resume packet
```

### UE Scene Truth And RflySim-Like Product Line

Task intent:

```text
Convert available UE/Fab/local scene assets into planning-ready truth,
integrate simulation components, then support navigation and disturbance
experiments through a product-style interface.
```

Recommended topology:

```text
主线 PMO
  -> 调度中台
  -> 产品发现战略 for product-scope tradeoffs
  -> 工具链 MCP for UE/Fab/MCP capability proof
  -> MoSim｜专项｜UE 场景真值
  -> MoSim｜专项｜FastLIO 接入
  -> MoSim｜专项｜路径规划与自主导航
  -> 验证评测
  -> 安全合规 when launcher/account/external path/destructive import appears
  -> 知识秘书
  -> DevOps 发布
```

Fab/Launcher route is a tool capability question, not a product acceptance
claim. If the route cannot be automated safely, Toolchain returns a fallback
route and Dispatch creates local-project scene tasks instead.

## Acceptance Checklist

Concrete agent design is usable only when:

- every permanent agent has a profile;
- every profile lists consumed and produced packets;
- every profile lists forbidden actions;
- task-scoped agent creation and close rules exist;
- conditional permanent promotion rules exist;
- example routing covers at least one algorithm task and one UE/product task;
- protocol and README point to this document;
- static checks guard the document and templates.

## Next Implementation Boundary

The next implementation should be a separate task that proves one minimal
closed-loop communication flow across:

```text
主线 PMO
调度中台
Agent Runtime 平台
上下文记忆索引
验证评测
DevOps 发布
知识秘书
```

This design document does not itself authorize that runtime proof.
