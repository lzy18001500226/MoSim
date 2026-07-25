# MoSim Agent Protocol Communication Contract V1

Date: 2026-05-28

Status: legacy visible-thread communication contract. It was active before the
2026-06-24 single-thread reset and is retained for historical packet review,
checker maintenance, and explicitly reopened protocol work only.

Current MoSim execution must start from:

```text
Docs/Workflows/single_thread_operating_model.md
Docs/Workflows/mainline_operations_board.md
Docs/Index/capability_index.md
task-specific Docs/Workflows or Docs/Skills entries
```

Do not use this contract to dispatch current engineering work, create/reopen
visible departments, run CoAgentOps patrols, or restore R1/R2/R3 routing unless
the user explicitly authorizes that legacy route.

## Purpose

This contract defines how work used to move between visible Codex department
conversations and workers. It is no longer the current MoSim operating model.
Use it only to understand or validate historical visible-thread packets, or as
design input if the protocol layer is deliberately reopened later.

The rule is:

```text
conversation is UI and working surface
packet is durable communication
event log is recovery truth
```

## Durable Communication Units

| Unit | Created By | Consumed By | Purpose |
|---|---|---|---|
| task packet | PMO or project helper | owner conversation | start or update durable work |
| context pack | PMO / runtime helper | dedicated task conversation | compact startup state |
| checkpoint packet | owner conversation | PMO / owner department | recoverable progress, risk, blocker |
| result packet | owner conversation | result router / reviewer | terminal or reviewable output |
| review note | Verification/Security/Docs/DevOps/PMO | PMO / owner | accept, reject, or request changes |
| event log entry | runtime/helper | all recovery flows | state transition evidence |

Plain chat may explain work, but it is not sufficient for handoff or
acceptance.

## Legacy Standard Task Dispatch

```text
PMO/main:
  frames user objective
  creates task_id
  records canonical_task_goal
  records native Codex surface gate before choosing the delivery route
  assigns accountable_owner
  records worktree binding when file isolation is required
  writes task packet
  sends packet to an existing visible department thread or creates a new
  visible department thread when no reusable one exists

Owner conversation:
  receives task packet
  works within read/write scope
  emits checkpoint or result packet

Result router/reviewer:
  imports packet
  marks review metadata

PMO/main:
  reports accepted result or escalation
```

## Legacy Ops Patrol Bounded Dispatch

legacy ops patrol is allowed to dispatch during patrol only when every precondition
below is true; when they are all true, dispatch is required in that patrol run:

```text
target thread status is active_visible in Config/legacy/department_threads.json
target thread is routable through the native visible-thread send/read surface
task is already inside the current P0 queue, mainline_operations_board.md,
  latest active PROGRESS entry, or latest accepted return/blocker
task class is static/source-static, diagnostic_only, recovery_validation,
  packet_contract_fix, rule_sync_only, preflight_drill_only, or another
  explicitly pre-authorized low-risk follow-up
task packet declares read scope, write scope, expected return path, blocker
  path, native_surface_gate, semantic_boundary, evidence minimum, allowed
  actions, forbidden actions, stop triggers, expected engineering outputs, and
  next owner
native visible-thread send/read surface is available
MainPMO can be notified in the same run
no approval/review/provider UI surface, open dependency, live GUI/license gate,
  manual-review risk, or PMO/user product-priority choice is required first
```

When every precondition is true, legacy ops patrol dispatches directly in that patrol
run; it does not merely report `dispatch_needed` and wait for PMO to send the
same pre-authorized packet later. `dispatch_needed` is reserved for cases where
a ready P0 gate exists but a bounded-dispatch precondition is missing, ambiguous,
or explicitly deferred.

legacy ops patrol must not dispatch or execute when any condition below is true:

```text
new user-facing priority or product scope decision is needed
the target thread is not active_visible or is a deleted/archived/historical id
visible-thread lifecycle changes are needed, including create/fork/rename/archive
automation lifecycle changes are needed
foreground desktop interaction, click/login/license/activation, private auth
  material, or approval buttons are needed
destructive Git, force push, history rewrite, broad staging, or cleanup outside
  the declared project scope is needed
live MWORKS load/check/simulation/layout/package-browser work is required
  without the current approved live gate
live ROS2/RViz/FAST-LIO probing would exceed the declared probe budget or skip
  required cleanup/source-window gates
UE runtime mutation or live command-echo claims are required without the
  accepted producer/consumer gate
the packet cannot satisfy the semantic boundary and native surface gate
```

Every legacy ops patrol-dispatched task must use the same durable task packet and
result/blocker paths as PMO dispatch. After dispatch, legacy ops patrol must notify
MainPMO in the same run with:

```text
request_id
target_department
target_thread_id
task_class
expected_return_path
blocker_return_path
dispatch_ticket_path
why_dispatch_was_pre_authorized
task_packet_path
native_dispatch_result
```

If a dispatch precondition is missing, legacy ops patrol writes a blocker packet or
returns `dispatch_needed` with the missing precondition instead of dispatching.
PMO remains the acceptance owner and may reject, supersede, narrow, or pause
any legacy ops patrol-dispatched task after reviewing the return/blocker evidence.

## Legacy Dispatch Ticket And SLO

When the legacy visible-thread route is explicitly reopened, every
visible-thread dispatch must create a JSON dispatch ticket under
`Results/agent_packets/dispatch_tickets/<request_id>.json`. The task packet
describes the engineering work; the dispatch ticket describes whether the
native visible-thread delivery and readback surface actually worked.

Use `Config/protocol/templates/visible_thread_dispatch_ticket.json` as the
starting point and validate each ticket with:

```powershell
python Scripts\quality\check_dispatch_ticket_slo.py `
  Results\agent_packets\dispatch_tickets\<request_id>.json
```

New visible-thread tickets use `ticket_version=2`. The dispatcher must generate
a fresh `dispatch_nonce`, write the same value into the dispatch ticket and the
visible task packet, and require the target thread to echo it in the runtime
lease. `Scripts/quality/check_dispatch_ticket_slo.py` rejects v2 runtime-lease
tickets when the nonce is missing, mismatched, or the lease path is not the
canonical `Results/runtime_leases/<target_thread_id>/<request_id>.json` path.
Older v1 tickets remain readable recovery evidence and must not be bulk
rewritten only to satisfy the newer checker rules.

Dispatch monitoring sequence:

```text
1. Before send, create the dispatch ticket with ticket_version=2,
   dispatcher_owns_slo_closure=true, dispatch_nonce, durable_start_due, and
   durable_start_requirement.
2. Send the visible-thread task packet.
3. The target thread's first execution step, except for exact no-op probes,
   is to create or update one durable project-local artifact declared by the
   packet's durable_start_requirement, normally the runtime lease that echoes
   the dispatch_nonce.
4. Immediately read_thread once and record last_observed_turn.
5. If no visible turn is observed, set second_readback_due_if_no_visible_turn
   within 2 minutes of sent_at and read again before that due time.
6. If a visible turn is observed but it only remains in progress/thinking and
   has no durable-start artifact, agent output, final response, checkpoint,
   expected return packet, blocker packet, approval/provider surface, or
   context-compression surface by first_agent_output_due, set breach_action to
   dispatch_surface_failure_suspected and write a blocker/recovery packet.
7. If 5 minutes after sent_at there is still no meaningful progress, set
   breach_action to dispatch_surface_failure_suspected and write a
   blocker/recovery packet. A visible in-progress turn without agent output is
   not meaningful progress.
8. The dispatcher that sent the task owns this ticket until it reaches a
   terminal state: expected_return_packet_seen, blocker_packet_seen,
   completed_without_expected_packet with escalation, approval/provider surface,
   context-compression surface, or dispatch_surface_failure_suspected.
9. Do not duplicate-dispatch the same request while delivery/readback remains
   ambiguous.
```

SLO profiles:

| Task type | Expected packet due | Extra requirement |
|---|---:|---|
| `source_static` | 10-20 minutes after `sent_at` | first-start artifact, agent output, packet, or explicit surface must appear inside the 5-minute surface window |
| `control_plane` / `packet_contract_fix` | 10-20 minutes after `sent_at` | same 5-minute meaningful-progress window |
| `dispatch_surface_diagnostic` / `recovery_validation` | 2-10 minutes after `sent_at` | same 5-minute meaningful-progress window |
| `live_runtime` / `mworks_gui` | may run longer, normally up to the declared ticket due time | `checkpoint_due` is required and must be within 10 minutes of `sent_at` |
| `manual_review` | may run longer, normally up to the declared ticket due time | `checkpoint_due` is required and must be within 15 minutes of `sent_at` |

The 5-minute rule is not a completion timeout. It detects an unhealthy
delivery/readback surface. A long live/runtime task may continue past 5 minutes
only if PMO or legacy ops patrol can see a durable-start artifact, agent output,
checkpoint, approval/provider surface, expected return packet, blocker packet,
or context-compression surface. A visible turn stuck in "thinking"/in-progress
with no durable artifact or agent output is not enough to continue waiting.

`durable_start_requirement` is required for non-trivial visible-department
dispatches. It should name the first artifact path or artifact class, the due
time, and the minimum content. Acceptable first artifacts include a checkpoint,
return packet, blocker packet, task-local notes file, declared output scaffold,
or another small project-local file inside the packet write scope. The artifact
does not prove completion; it proves that the target execution surface started
and can write recoverable state. Exact no-op probes that explicitly forbid file
writes are exempt.

For `source_static`, `control_plane`, `packet_contract_fix`,
`dispatch_surface_diagnostic`, and `recovery_validation`, this is a first-start
proof, not a continuing heartbeat contract. Once a fresh matching first-start
artifact, agent output, return/blocker packet, approval/provider surface, or
context-compression surface is observed, the dispatcher waits for the declared
expected packet due time instead of repeatedly probing the worker. Continuing
checkpoint freshness is required only when the task type declares
`checkpoint_due`, normally live/runtime/MWORKS GUI/manual review work.

The preferred first artifact is a runtime lease:

```text
Results/runtime_leases/<target_thread_id>/<request_id>.json
```

Minimum runtime lease content:

```json
{
  "request_id": "<request_id>",
  "target_thread_id": "<target_thread_id>",
  "nonce": "<unique dispatch nonce from the ticket/task packet>",
  "started_at": "<ISO timestamp>",
  "last_checkpoint_at": "<ISO timestamp>",
  "current_phase": "started|reading|planning|editing|verifying|blocked|returning",
  "next_checkpoint_due_at": "<ISO timestamp>"
}
```

For first-start-only task types, `last_checkpoint_at` may equal `started_at`
and `next_checkpoint_due_at` may be the same as `expected_packet_due`; patrol
must not treat that as a stale-worker heartbeat violation. The dispatcher must
put a fresh `dispatch_nonce` in the v2 ticket and task packet. The target
thread must echo the same value as `nonce` in the runtime lease so patrol can
reject stale lease files from older attempts. If the target thread shows a
visible in-progress turn but no matching runtime lease, agent output,
checkpoint, packet, approval/provider surface, or context-compression surface
by the 5-minute surface window, classify it as
`dispatch_surface_failure_suspected`.

If multiple unrelated visible threads stop producing new turns at the same
time after they had already started, classify the incident as a global
Codex/App/network surface until evidence proves a single department failure.
Do not use a per-thread stale-worker model for ordinary source/static work.

Codex App transcript clicking is not the default liveness mechanism. Slow or
blank transcript views should be recorded as `view_refresh_required`, then
classified through native read/send checks, expected packet checks, durable
artifact checks, approval/provider/context inspection, and main-shell
observation. Do not click through every thread as a routine heartbeat. A
host-project adapter may authorize a bounded UI refresh exception only for a
specific incident; the exception must forbid approval/review/send/restart/
login/save/archive/delete/pin/overflow/composer controls and must not be used
as ordinary progress evidence.

The 10-minute patrol may capture or inspect the Codex App main shell/list area
when the native desktop surface is available. Its default UI purpose is only to
detect global pending-approval/review/provider indicators, such as a green
`待批准`/approval badge in the left thread list, and send a sparse Chinese email
or PMO notice. It must not click the badge or treat the badge as a dead-thread
failure.

PMO board entries for active dispatch monitoring must stay short. The board
shows only these columns:

```text
sent_at
first_readback_due
expected_packet_due
last_observed_turn
breach_action
owner
```

Detailed target thread, task class, expected paths, checkpoint due, and SLO
evidence belong in the dispatch ticket JSON, not in the board or ledger.

## Legacy Native Surface Gate

Before a non-trivial legacy task is dispatched, PMO or bounded legacy ops
patrol records why the work belongs to a native Codex surface, a visible
department thread, a bounded sub-agent, or agent packet/evidence glue. This is
a routing decision, not a task result.

Task packets should include:

```yaml
native_surface_gate:
  selected_native_surface: [visible_thread, agent_packet_glue]
  surface_selection_reason: durable department context plus packet return is required
  capability_index_consulted: Docs/Index/capability_index.md
  selected_capabilities:
    - Codex visible thread dispatch
    - Review / evidence gate
  rejected_capabilities:
    Disposable subagent: disposable context is insufficient
  rejected_surfaces:
    subagent: disposable context is insufficient
    codex_exec: hidden formal dispatch is not accepted without visible delivery
  worktree_required: false
  worktree_decision: read-only planning task; no isolated worktree needed
expected_return_path: Results/agent_packets/returns/<request_id>.json
blocker_return_path: Results/agent_packets/blockers/<request_id>.json
dispatch_ticket_path: Results/agent_packets/dispatch_tickets/<request_id>.json
```

Use `Config/protocol/templates/visible_thread_dispatch_packet.json` as the
machine-checkable scaffold for new visible-thread dispatches, then replace the
placeholder values before sending. The sibling YAML file is a human-readable
draft scaffold only; instantiate or edit the JSON packet before running the
checker. The schema keeps `semantic_boundary`, return paths, and the optional
`dispatch_ticket_path` explicit, while
the checker enforces the current routing fields before dispatch:

```powershell
python Scripts\quality\check_agent_task_native_surface_gate.py `
  Config\protocol\templates\visible_thread_dispatch_packet.json --strict
```

Capability fields are advisory routing evidence, not permission. A selected
capability means PMO or the dispatcher considered that surface. Actual
authority still comes from `read_scope`, `write_scope`, `allowed_actions`,
`forbidden_actions`, `semantic_boundary`, domain gates, hooks/checkers, and
PMO/user approval when required. If a rule is mechanically enforceable, prefer
a checker, schema, or hook over prose-only workflow text.

## Capability Resolution

For current single-thread work, capability resolution remains useful when a
task involves selecting or creating a skill, workflow, MCP/plugin
surface, script, checker, desktop-window capability, or other reusable tool
asset. Use `Config/protocol/templates/capability_resolution.json` as a small
standalone planning/checker artifact. Legacy visible-thread dispatch packets
may include the same block beside `native_surface_gate`.

This block prevents context drift where an existing capability is planned as
new because the responding thread did not resolve current assets first.

Use `Config/protocol/templates/capability_resolution.json` as the minimal
scaffold.

Minimum fields:

```json
{
  "capability_resolution": {
    "required": true,
    "capability_index_consulted": true,
    "consulted_index_path": "Docs/Index/capability_index.md",
    "matched_capability_ids": [],
    "matched_capabilities": [],
    "existing_assets_to_reuse": [],
    "searched_existing_assets": [
      "Docs/Index/capability_index.md",
      "Docs/Skills/",
      "Docs/Skills/",
      "Scripts/"
    ],
    "create_new_assets": [],
    "reason_existing_assets_insufficient": "",
    "do_not_recreate": [],
    "unresolved_capabilities": []
  }
}
```

Rules:

1. Prefer existing indexed capabilities over new files.
2. If `create_new_assets` includes a skill, workflow, script, checker, or MCP
   adapter, the packet must name `searched_existing_assets` and explain why
   the existing assets are insufficient.
3. If a capability is already present and reusable, list it in
   `existing_assets_to_reuse` and add the duplicate concept to
   `do_not_recreate`.
4. `capability_resolution` is routing evidence, not permission. It does not
   authorize clicking, login, save, restart, live MWORKS/ROS2/UE work, Git
   mutation, or visible-thread lifecycle actions.
5. Validate reusable-capability decisions with:

```powershell
python Scripts\quality\check_capability_resolution.py `
  Results\agent_packets\<request_id>.json --strict
```

The checker fails packets that skip the capability index, create duplicate
assets without a clear insufficiency reason, or treat capability resolution as
permission to click, login, save, restart, dispatch, or perform another
authority-gated action.

`check_agent_task_native_surface_gate.py --strict` also invokes this
capability-resolution gate for legacy visible-thread dispatch packets, so
strict legacy preflight runs catch both native-surface routing errors and
duplicate-capability planning errors.

## Legacy Department Local Planning Template

For every non-trivial visible-department assignment, PMO should include the
same local-planning block, and the target department must derive and report it
before deep business work. This is a planning and scheduling decision
requirement, not a requirement to use at least one sub-agent:

```text
department_local_goal
critical_path_steps
parallelizable_slices
subagent_plan
subagent_plan_reason
subagents_used
verification_gates
manual_review_or_blocker_triggers
```

The `department_local_goal` should be short and bounded to the current task
packet. Prefer the next concrete engineering gate over broad research,
large-scale cleanup, or workflow redesign. If a workflow, skill, MCP, or
documentation issue is discovered, record it as a parallel/follow-up action
unless the current engineering gate cannot safely proceed without that fix.

`subagent_plan` must be one of `used`, `available_but_not_useful`,
`unavailable`, or `unsafe`. `subagents_used=[]` is acceptable when the
department runtime has no sub-agent surface, no independent slice exists, or
serial execution is safer. If a department uses disposable sub-agents, they
must be bounded, task-local, evidence-returning helpers; they must not become
hidden durable departments or create/fork/rename/archive visible threads.

Dispatch packets for non-trivial department work must explicitly tell the
target to plan before deep execution. The packet should require the department
to state a local goal, split critical-path and parallelizable work, decide
whether a disposable sub-agent is useful, and record that decision in its
return or blocker. This is a scheduling requirement, not a requirement to spawn
a sub-agent. Use `available_but_not_useful`, `unavailable`, or `unsafe` when no
safe independent slice exists.

## Legacy R2/R3 Failover Scope

For MWORKS, ROS2, and UE, R2 is the default failover lane when R1 is blocked by
a confirmed or suspected dispatch-surface failure and a safe task is available.
R2 task packets may use only these task classes unless PMO explicitly creates a
new exception:

```text
source_static
diagnostic_only
packet_contract_fix
rule_sync_only
checker/review
```

R2 failover packets must forbid:

```text
MWORKS live work
ROS2 live work
UE runtime/build/editor work
GUI clicks
login/authorization/save/restart actions
setpoint publication
```

R2 returns still need real engineering or review evidence for the declared task
class. JSON packets, ledger rows, and board updates are only control-plane
evidence unless the task class is explicitly diagnostic/control-plane.

R3 is reserve capacity, not an automatic second backup. PMO proposes or
approves R3 only after R2 failover still leaves a P0 partition idle or blocked
long enough that another static/diagnostic/checker/review lane is useful. Do
not trigger R3 merely because the same department's R1/R2 had repeated
dead-thread incidents in a 24-hour window.

## Legacy Semantic Boundary Template

Every dispatch, checkpoint, patrol, recovery, and review packet must avoid
standalone vague status words. If a task says `health`, `healthy`, `normal`,
`blocked`, `review`, `审核`, `window`, `live`, or `done`, it must also declare
the classification boundary that makes those words executable:

```yaml
semantic_boundary:
  decision_scope: visible_thread | mworks_window_patrol | mworks_live_task | ros2_runtime | ue_runtime | asset_review | other
  state_class: <one concrete enum value>
  evidence_minimum:
    - <minimum evidence that must exist before this state can be claimed>
  allowed_actions:
    - <actions allowed in this state>
  forbidden_actions:
    - <actions forbidden in this state>
  stop_triggers:
    - <observations that force blocker/checkpoint instead of continued work>
  next_owner: PMO | legacy ops patrol | MWORKS_R1 | MWORKS_R2 | ROS2_R1 | UE | user | current_department
```

Accepted visible-thread `state_class` values include:

```text
routable
approval_pending_or_ui_blocked
provider_gateway_or_pending_review
dispatch_surface_or_agent_loop_failure
context_compression_surface
unknown_blocked
```

Queue state is reported separately as `dispatch_readiness`:

```text
busy_in_progress
idle_needs_dispatch
idle_blocked_by_open_dependency
idle_no_ready_task
idle_waiting_review_or_approval
```

Accepted MWORKS patrol/task `state_class` values include:

```text
window_patrol_clean
helper_only_nonblocking
login_or_license_blocked
authorization_blocked
gui_error_blocked
visible_unknown_blocked
live_attach_blocked
unknown_blocked
```

If a different domain needs additional values, define them in the task packet
before dispatch. Free-text values such as `ok`, `normal`, `looks fine`,
`healthy`, `still running`, or `probably blocked` are not sufficient because
they do not tell the next thread what evidence was inspected or what it may
do next.

## Department Execution And Acceptance Contract

After local planning, the department owns execution inside the declared scope.
PMO should not have to decompose every internal step. The department must run
the task-specific infrastructure preflight before business work, then continue
through the critical path until it has either produced the declared engineering
output or hit a real blocker.

Task-specific preflights include, for example:

- MWORKS/Sysplorer/Syslab sentinel and background screenshots for MWORKS work;
- ROS2 stale-process, topic, source-window, and cleanup checks for ROS2 work;
- UE source/static/build-scope checks for UE work;
- Blender/source-asset availability and render-output checks for asset/PBR
  work.

If a preflight, GUI, license, runtime, build, tool-surface, source-data, or
permission issue blocks the task, the department must stop the domain work and
return a blocker promptly. It must not spend the turn producing unrelated JSON,
tuning parameters, retrying solver/runtime/model steps, or turning the symptom
into a completed metadata packet.

Completed work must include domain evidence that matches the task:

- model/simulation/layout/package work: `.mo` or `package.mo` edits,
  `check_model`, `SimulateModel`, native result/`.msr`, metrics,
  diagram/layout screenshots, or wiring observations;
- ROS2 runtime work: topic/process/source-window/log/cleanup evidence and
  bounded runtime artifacts when live probing is in scope;
- UE work: source/static/build/runtime evidence according to the task scope;
- asset/PBR work: Blender/UE asset files, rendered review images, material
  manifests, or visual-review artifacts.

JSON task/result/blocker packets, ledger rows, and progress notes are
control-plane evidence. They count as the engineering deliverable only when the
task is explicitly `diagnostic_only`, `rule_sync_only`,
`preflight_drill_only`, `dispatch_surface_diagnostic`, or
`static_inventory_only`.

For long or live tasks, the return/blocker packet must include phase
checkpoints: what phase ran, what evidence was inspected, what changed, and
what remains blocked. If a task produces a user-review artifact such as an
image, video, native result viewer, or model diagram, the department should
request PMO display/review instead of returning only a path.

PMO may reject completed packets that lack the declared engineering outputs,
omit the required local-planning/sub-agent decision fields, or report a real
infrastructure blocker as completed work.

PMO should run the generic visible-department packet gate before integrating
non-trivial return/blocker packets:

```powershell
python Scripts\quality\check_department_packet_contract.py `
  Results\agent_packets\returns\<request_id>.json
```

This gate is a shared backstop. It checks the local-planning fields,
`subagent_plan` decision, `actual_engineering_outputs`, and `claim_boundary`.
Domain-specific gates such as the MWORKS live gate still apply on top of it.

## Domain Dispatch Gates

Use the matching host-project domain gate in addition to the generic
local-planning block. These gates must be present in the dispatch prompt, not
only remembered by PMO.

Portable agent protocol does not own MWORKS, ROS2, UE, or asset-specific engineering
truth. Host projects must keep those rules in host adapters, workflows, skills,
or checkers and point task packets to them.

For legacy MoSim visible-department packet audits, the historical host adapter
is:

```text
Docs/Cache/agent_legacy/legacy_workflows_20260624/mosim_visible_dispatch_adapter.md
```

It preserves the previous MWORKS/Sysplorer/Syslab, ROS2/RViz2/FAST-LIO, UE,
Sunray150, R2/R3, and engineering-output gate wording for trace-back only. It
does not define the current MoSim runtime or task route. Current work follows
`AGENTS.md`, `Docs/Workflows/single_thread_operating_model.md`, and the
selected topic workflow. Other projects should provide their own current host
adapter when they use this legacy protocol.

Host-specific gates may still have machine checks. For example, MoSim live
MWORKS packets are checked with:

```powershell
python Scripts\quality\check_mworks_live_gate.py `
  Results\agent_packets\<request_id>.json --kind task --expect department
python Scripts\quality\check_mworks_live_gate.py `
  Results\agent_packets\returns\<request_id>.json --kind return --expect department
```

For compatibility with existing runtime packets, the same object may be stored
under `metadata.native_surface_gate`. New JSON task packets should be checked
before dispatch with:

```powershell
python Scripts\quality\check_agent_task_native_surface_gate.py `
  Results\agent_packets\<request_id>.json --strict
```

## Worktree-Aware Dispatch

When a task uses a separate Codex App worktree or Git worktree, the dispatch
packet must carry:

```yaml
worktree_path:
branch_or_base:
write_scope:
merge_owner:
review_gate:
close_condition:
```

Worktree state is part of execution context, not acceptance. A result is still
accepted only through result packet evidence and review metadata.

Worktree closeout requires:

- result packet imported,
- review state known,
- Git state summarized,
- merge or discard decision recorded,
- no untracked broad artifacts left unexplained.

## Checkpoint Contract

Checkpoint content:

```yaml
task_id:
canonical_task_goal:
conversation_objective:
owner:
current_state:
evidence_found:
files_changed:
commands_run:
blockers:
risks:
decision_needed:
next_step:
continue_or_stop:
```

Checkpoint required when:

- a long task reaches its checkpoint interval,
- appetite or circuit breaker may be exceeded,
- evidence contradicts the plan,
- the worker needs user input,
- the worker wants to change owner, scope, or goal,
- an irreversible step is near.

## Result Packet Contract

A result packet must include:

- task id,
- task class,
- canonical status,
- summary,
- owner/role,
- files changed,
- commands run,
- evidence,
- acceptance state,
- review status,
- known exclusions,
- residual risks,
- next recommended action.

Terminal result without evidence should be imported as `needs_review` or
`rejected`, not accepted.

## Support Work

Supporting departments do not change the canonical task goal.

Support flow:

```text
accountable owner requests support
PMO or project helper records child/support task or review request when needed
support owner returns result packet or review note
accountable owner integrates
PMO accepts, rejects, or escalates
```

## Owner Change

Owner change requires:

- current owner checkpoint,
- reason for handoff,
- new accountable owner,
- updated task packet or context pack,
- event log entry,
- unresolved risks.

No worker may silently hand work to another durable conversation.

## Goal Change

Goal change requires:

- evidence that current goal is wrong or incomplete,
- proposed replacement canonical task goal,
- affected scope and acceptance changes,
- PMO/user decision record, optionally backed by agent runtime metadata,
- event log entry.

Until accepted, the task remains under the old canonical task goal and should
usually be `review_required` or `blocked`.

## Communication Failure

Treat communication as failed when:

- the target conversation is not visible or recoverable,
- no task packet was delivered,
- the packet was delivered only through a shadow/local Codex home while the
  user expected a front-end-visible department message,
- no result packet can be found,
- the worker result exists only in chat,
- the task id or canonical goal does not match,
- packet evidence paths are missing,
- review metadata is absent for high-risk work.

Recovery action:

```text
stop dispatch
record blocker
repair registry or context pack
retry only with a fresh packet or explicit recovery note
```

If the accountable owner falls back to local execution after department
transport fails, the fallback must be reported as a coordination failure, not
as successful department execution. A visible department status message should
be sent and synced before claiming that the department conversation has been
updated.

## V1 Constraint

V1 communication is PMO-led and packet-based. The durable authority is the
recorded task packet, return/blocker packet, ledger/runtime entry, and evidence
path, not a chat reply or a hidden helper process. Departments may request work
from each other only when they include origin thread id, request id, expected
return/blocker paths, and responsible owner. PMO does not have to be an
intermediate chat hop for every support request, but it remains accountable for
integration and may audit or override routing when the task affects the project
goal, Git state, evidence claims, user review, credentials, GUI/license state,
or safety boundary.
