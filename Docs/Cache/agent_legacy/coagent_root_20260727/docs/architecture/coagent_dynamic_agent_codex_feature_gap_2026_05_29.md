# CoAgent Dynamic Agent And Codex Feature Gap Review

Date: 2026-05-29

Status: design review only. This document does not approve app-server
transport, automatic conversation creation, automatic worktree creation,
unattended automation, plugin installation, hook rewrites, email sending, or
new permanent conversations.

## Purpose

This pass rechecks the current CoAgent design against:

- Claude Code subagents, agent teams, and worktrees;
- Kimi Agent Swarm / Agent Team patterns;
- Codex App / app-server / CLI features that are already present in the local
  Codex source tree and visible documentation.

The question is not whether CoAgent should copy one vendor product. The
question is:

```text
which external patterns reduce task drift, context overload, coordination
failure, unsafe automation, and slow integration in our own task-first
multi-conversation architecture?
```

## Sources Rechecked

Previously consolidated local docs:

- `CoAgent/docs/architecture/coagent_vendor_pattern_mapping.md`
- `CoAgent/docs/architecture/coagent_vendor_gap_review_2026_05_29.md`
- `CoAgent/docs/architecture/coagent_department_capability_model.md`
- `CoAgent/docs/architecture/coagent_task_team_architecture.md`
- `CoAgent/learning/audits/2026-05-27_official_multi_agent_principles_round8.md`
- `CoAgent/learning/audits/2026-05-27_official_protocol_convergence_round11.md`

Current first-party/vendor docs spot-checked:

- Anthropic multi-agent research system:
  `https://www.anthropic.com/engineering/multi-agent-research-system`
- Claude Code subagents:
  `https://docs.anthropic.com/en/docs/claude-code/sub-agents`
- Claude Code agent teams:
  `https://code.claude.com/docs/en/agent-teams`
- Claude Code worktrees:
  `https://docs.anthropic.com/en/docs/claude-code/worktrees`
- Kimi Agent Swarm:
  `https://www.kimi.com/help/agent/agent-swarm`
- Kimi Agent Swarm blog:
  `https://www.kimi.com/blog/agent-swarm`
- OpenAI Codex documentation entry point:
  `https://developers.openai.com/codex/`
- Local Codex app-server source doc:
  `References/Agent/codex/codex-rs/app-server/README.md`
- Local Codex protocol source doc:
  `References/Agent/codex/codex-rs/docs/protocol_v1.md`

## Bottom Line

The 11 permanent CoAgent conversations remain the right startup target.

The current gap is not "more permanent departments". The gap is that dynamic
task teams are not yet protocol-complete. Claude and Kimi both confirm the
same architecture pressure:

```text
stable lead / orchestrator
  -> dynamic teammates or subagents
  -> explicit context partitioning
  -> shared task board / mailbox
  -> independent work surfaces
  -> synthesis, review, and closeout gates
```

Codex already exposes enough primitives to support this shape later, but
CoAgent is not fully using them yet. The missing design objects are:

1. `team_mailbox` / `shared_task_board`
2. `dynamic_team_policy`
3. `conversation_fork_policy`
4. `codex_feature_use_matrix`
5. stricter `worktree_binding` and `runtimeWorkspaceRoots` policy
6. `hook_policy` as hard deterministic gates
7. plugin capability packaging rules
8. critical-path and true-parallelism metrics

## Claude Agent Team Pattern

Claude's useful distinction is:

```text
subagent = bounded helper inside one session
agent team = multiple durable sessions with their own context and coordination
```

The important lessons for CoAgent are:

- Use teams for work where independent parallel exploration adds real value:
  research, review, competing hypotheses, cross-layer slices, or separable
  implementation modules.
- Do not use teams for mostly sequential work, same-file edits, or unclear
  ownership; coordination overhead will dominate.
- Give teammates enough context, but not raw transcript dumps.
- Choose team size deliberately.
- Avoid file conflicts explicitly.
- The lead must monitor and synthesize; teammates do not replace integration.

### CoAgent Mapping

| Claude pattern | CoAgent object | Current state | Gap |
|---|---|---|---|
| lead session | `MoSim｜调度中台` plus PMO acceptance | exists | Dispatch needs a formal team board, not just prose routing |
| teammate session | task-scoped conversation | designed | spawn/decommission rules are incomplete |
| subagent | one bounded call inside a scoped conversation | designed | acceptable only as local helper, not durable owner |
| shared task list | task charter / ledger | partial | needs `shared_task_board` template |
| inter-agent messaging | packet flow through Dispatch | partial | needs `team_mailbox` with dedupe and owner rules |
| worktree separation | worktree binding | partial | needs fork/worktree mode policy |

## Kimi Agent Swarm Pattern

Kimi's useful pattern is horizontal scaling:

```text
commander / orchestrator
  -> many specialist subagents
  -> context sharding
  -> final synthesis
```

The most relevant Kimi ideas are:

- The orchestrator sets strategy; specialists focus on local work.
- Avoid "serial collapse", where the orchestrator gives all work to one agent.
- Avoid "fake parallelism", where the system splits work only to look busy.
- Optimize for final-result quality, true parallelism, sub-task completion, and
  critical-path time.
- Use context sharding: each worker keeps a local notebook; only key findings
  flow back to the orchestrator.
- The product pattern is useful for wide retrieval, large reading, long
  writing, code review, refactoring, and broad parallel research.

### CoAgent Mapping

| Kimi pattern | CoAgent object | Current state | Gap |
|---|---|---|---|
| commander | Dispatch task team owner | exists | needs explicit critical-path owner and team-size cap |
| specialists | task-scoped conversations and subagents | exists | selection policy is still informal |
| local notebook | conversation state + context delta | partial | needs per-slice context shard rules |
| true parallelism reward | Flow Analytics | conditional department | metrics not yet defined in task packet |
| final-result quality | Verification + PMO acceptance | exists | needs trace/eval rubric attached to dynamic teams |
| anti-fake-parallelism | topology selector | partial | needs split-justification gate |

## Codex Feature Use Matrix

Codex should be treated as the execution substrate, not the architecture owner.
The architecture owner remains CoAgent's task/packet/worktree protocol.

| Codex feature | What it gives us | Current CoAgent use | Required decision |
|---|---|---|---|
| `thread/start` | create a clean conversation with cwd, permissions, runtime roots | manually used indirectly | use only after task charter and context pack exist |
| `thread/resume` | continue a durable conversation | manually used | require registered conversation id and owner |
| `thread/fork` | branch with copied history | not formalized | use for context-seeded task slices only when Dispatch records the edge |
| `ephemeral: true` fork | temporary in-memory experiment | not formalized | use only for bounded experiments that must not become durable state |
| `thread/name/set` | clean visible thread names | manually repaired | Runtime Platform should own naming policy |
| `thread/goal/set/get/clear` | persisted thread-local goal | partially understood | canonical task goal stays in Dispatch; thread goal is slice-local |
| `thread/compact/start` | reduce long context | not formalized | Context Memory decides compaction triggers |
| `thread/rollback` | remove drift or unaccepted turns from thread context | not formalized | use after result packet says which state is accepted |
| `review/start` | inline or detached automated review | not used as protocol | Verification should own detached review lanes for scoped diffs |
| `runtimeWorkspaceRoots` | materialize workspace roots for a thread/turn | not formalized | bind to WorktreeBinding, not ad-hoc paths |
| permission profiles / environments | isolate tool and execution capability | partial | Safety and Runtime must approve profiles per task class |
| `skills/list` and skill input items | discover/select procedural context | implicit | Context Memory must load minimal skills, not all skills |
| `hooks/list` and managed hooks | deterministic lifecycle gates | partial | hooks are hard gates, not optional skills |
| plugin list/read/install | package skills/hooks/MCP/apps | not adopted | treat plugins as capability packages; do not production-enable while under development |
| `mcpServerStatus/list` and `mcpServer/tool/call` | tool health and calls through app-server | not adopted | Toolchain MCP owns capability cards and probes |
| `fs/watch`, `skills/changed`, config reload | live capability refresh | not adopted | useful later for runtime, gated by stability tests |
| `command/exec` / `process/spawn` | app-server command execution | not adopted | keep behind Safety/Runtime policy; do not bypass current CLI/file route |
| thread list/read/archive | durable conversation inventory | manually inspected | Runtime Platform owns registry reconciliation |
| automations | scheduled or triggered work | concept exists | guarded dry-run only until automation approval |

## Thread Fork And Goal Policy

CoAgent should use three goal layers:

| Layer | Owner | Meaning |
|---|---|---|
| canonical task goal | Dispatch | the real user-facing objective and definition of done |
| team goal | task-team charter | the coordinated outcome for one dynamic task team |
| thread goal | one Codex conversation | the local slice objective for one conversation |

Rules:

1. PMO may accept or revise the user-facing goal.
2. Dispatch owns the canonical task goal and task-team charter.
3. A scoped conversation owns only its local slice goal.
4. `thread/goal/set` may not silently replace the canonical task goal.
5. `thread/fork` requires an edge record:

```text
source_thread_id
new_thread_id
fork_mode: durable_slice | detached_review | ephemeral_experiment
task_id
team_id
context_pack_path
slice_goal
close_condition
```

## Worktree And Runtime Workspace Policy

Codex `runtimeWorkspaceRoots` is not the same as a Git worktree.

CoAgent should treat them separately:

| Surface | Purpose | Owner |
|---|---|---|
| Git worktree | isolate file edits and merge/discard decisions | DevOps Release |
| `runtimeWorkspaceRoots` | expose allowed roots to a Codex thread/turn | Runtime Platform + Safety |
| task write scope | define what a conversation may change | Dispatch |
| artifact path | record accepted outputs | Observability / Evidence or Verification |

Default:

- read-only research conversation: no new worktree;
- scoped implementation conversation: one task worktree;
- detached review conversation: review worktree or read-only view;
- integration: one integration worktree;
- subagent experiment: ephemeral worktree only when parent owns cleanup.

## Shared Task Board And Team Mailbox

The missing coordination object is not another chat. It is a compact task-team
state board plus mailbox.

Minimum `shared_task_board` fields:

```yaml
team_id:
task_id:
canonical_task_goal:
current_phase:
members:
  - conversation_id:
    owner:
    slice_goal:
    state:
    worktree_binding:
    dependencies:
    next_checkpoint_due:
critical_path:
open_blockers:
review_gates:
integration_queue:
close_condition:
```

Minimum `team_mailbox` fields:

```yaml
team_id:
messages:
  - message_id:
    from_owner:
    to_owner:
    message_type:
    task_id:
    requires_response:
    dedupe_key:
    payload_path:
    expiry_or_close_condition:
```

Rules:

1. Peer chat is advisory only.
2. Durable cross-conversation state must pass through Dispatch or a recorded
   mailbox item.
3. Mailbox messages must reference packet paths, not raw long chat.
4. A conversation cannot create another durable conversation by itself.

## Hooks Are Hard Gates

Skills are optional context. Hooks are enforcement.

CoAgent must not model hooks as "things an agent may remember to use". Hooks
should enforce:

- project filesystem boundary;
- secret and credential path denial;
- destructive command approval;
- broad Git action gate;
- large-file and generated-output policy;
- result-packet requirement before closeout.

Hook changes remain gated because a bad hook can block all useful work.

## Plugins Are Capability Packages

Codex plugins are useful as packaging units because they can bundle skills,
hooks, MCP servers, apps, and capability metadata.

CoAgent should not depend on plugins as the first implementation layer. The
Codex app-server docs mark several plugin APIs as under development. Treat
plugins as a later distribution format:

```text
CoAgent protocol and tests first
  -> stable skill/hook/MCP capability cards
  -> plugin packaging after stability proof
```

## Design Extensions Required

P0 design extensions before runtime expansion:

1. `team_mailbox.yaml`
2. `shared_task_board.yaml`
3. `dynamic_team_policy.yaml`
4. `conversation_fork_policy.yaml`
5. `codex_feature_use_matrix.md`
6. worktree/runtime-workspace binding fields in task-team charter
7. hook policy separating hard gates from optional skills

P1 design extensions after one closed-loop proof:

1. Flow Analytics metrics for critical-path time, fake parallelism, handoff
   failure, blocked time, and context freshness.
2. Observability/Evidence promotion if task evidence becomes too heavy for
   Verification.
3. Plugin capability packaging.
4. Guarded automation for daily learning, daily open-source reference refresh,
   and recurring Git hygiene.

## Impact On Current Permanent Conversations

No new permanent conversations should be created immediately.

The current 11-conversation plan remains the startup baseline. However, this
review strengthens two conditional promotion rules:

- `MoSim｜组织运行指标` should be promoted after the first real multi-agent
  proof if we cannot measure critical-path time, blocked time, and handoff
  failures from the current logs.
- `MoSim｜观测证据` should be promoted if Verification becomes overloaded with
  both correctness judgment and evidence/trace packaging.

## Remaining Open Questions

These are not solved by vendor patterns:

1. Can Codex App expose the app-server methods we need without UI instability?
2. Can threads created from WSL be made consistently visible in both VSCode
   and Codex App without stale-path failures?
3. Which operations should use app-server directly versus the current
   CLI/file-packet transport?
4. How much context should be forked into a scoped conversation before model
   quality starts to decline?
5. What is the minimum useful closed-loop proof that exercises:
   task charter -> context pack -> thread/fork or start -> result packet ->
   review -> context delta -> Git disposition?

## Final Design Position

CoAgent should combine:

```text
Claude-style durable agent teams
  + Kimi-style context-sharded parallel specialists
  + Codex thread/worktree/goal/review primitives
  + our own packet-first governance, safety, and evidence protocol
```

Do not copy the vendor UX blindly. The durable source of truth remains CoAgent
task packets, context packs, result packets, review packets, worktree bindings,
and decision records.
