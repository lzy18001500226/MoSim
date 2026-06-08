# CoAgentOps Patrol And Recovery Workflow

> Executable workflow for `MoSim｜CoAgent运维平台` 10-minute patrol, bounded
> dispatch, visible-thread recovery, MWORKS window classification, and PMO
> escalation. This file replaces scattered dated hotfix prose in startup entry
> docs; keep `AGENTS.md` and `new_conversation_context.md` as hard-boundary
> pointers.

## 1. Scope And Owners

| Item | Current Rule |
|---|---|
| Patrol owner | `MoSim｜CoAgent运维平台` (`019e9bc1-ea9f-7102-b41a-4ef9b2308992`) |
| PMO owner | `MoSim｜主线 PMO` (`019e9868-83ea-70f0-92c5-a3a408bd78c6`) |
| Documentation secretary | `MoSim｜文档秘书部` (`019e9be0-f6ac-7762-b80c-b1dd18b0d013`) |
| Registry source | `CoAgent/dispatch/department_threads.json` |
| Return channel | `Results/agent_packets/returns/<request_id>.json` |
| Blocker channel | `Results/agent_packets/blockers/<request_id>.json` |

Former names such as `MoSim｜Codex 上下文维护部`,
`MoSim｜Codex 上下文维护部-R2`, and `MoSim｜知识秘书` are alias/history only.
Future context-memory, documentation consistency, startup recovery, and
cache-first migration tasks route to `MoSim｜文档秘书部`. The internal key
`CodexContextMaintenanceAgent` may remain in compatibility metadata.

CoAgentOps does not own product priority, engineering acceptance, visible
thread lifecycle changes, automation lifecycle changes, destructive Git,
private auth material, foreground approval clicks, or final integration. PMO
owns those decisions.

## 2. Patrol Workflow

Each patrol run must execute the steps below in order:

1. Read `AGENTS.md`, `Docs/Workflows/new_conversation_context.md`, this file,
   `CoAgent/dispatch/communication_contract.md`,
   `CoAgent/dispatch/department_threads.json`,
   `Docs/Workflows/mainline_operations_board.md`, and the newest active
   entries in `PROGRESS.md`. Read `Docs/Workflows/agent_task_ledger.md` only
   when the board or a packet names a row that must be traced for recovery.
2. Scan `MainPMO`, `CoAgentOps`, and only current `status=active_visible`
   engineering departments. Deleted or archived WeChat routes are not targets.
3. Classify approval/review/provider surfaces before dead-thread recovery.
4. Classify latest turn and expected packet state.
5. Classify MWORKS/Sysplorer/Syslab window state when relevant.
6. Report `dispatch_readiness` for every active engineering department.
7. Handle abnormal/recovery-pending threads first.
8. Then handle routable idle P0 engineering threads with ready gates.
9. Then handle PMO/user-resolvable open dependencies.
10. Then route review/audit work.
11. Only then do support-lane probe, learning, or meta checks.

An active engineering thread that is routable and idle while a P0 next gate
exists is not healthy closeout. If the bounded-dispatch preconditions in
section 6 are satisfied, CoAgentOps must dispatch the task to the visible
department in the same patrol run and notify PMO with the dispatch metadata.
Use `dispatch_needed` as a PMO-facing state only when a ready gate exists but
one or more bounded-dispatch preconditions are missing. In that case, notify
PMO through the native thread surface in the same run, or write a blocker
naming the missing PMO/thread tool, packet field, dependency, or explicit
deferral.

## 3. Semantic Boundary

Every patrol, recovery, dispatch, checkpoint, or review packet that uses words
such as `healthy`, `normal`, `blocked`, `review`, `审核`, `window`, `live`,
`done`, or `continue` must include:

```yaml
semantic_boundary:
  decision_scope: visible_thread | mworks_window_patrol | mworks_live_task | ros2_runtime | ue_runtime | asset_review | other
  state_class: <one concrete value>
  evidence_minimum:
    - <minimum evidence inspected before this state was claimed>
  allowed_actions:
    - <actions allowed while in this state>
  forbidden_actions:
    - <actions forbidden while in this state>
  stop_triggers:
    - <observations that force blocker/checkpoint>
  next_owner: PMO | CoAgentOps | MWORKS_R1 | MWORKS_R2 | ROS2_R1 | UE | user | current_department
```

Accepted visible-thread `state_class` values:

```text
routable
approval_pending_or_ui_blocked
provider_gateway_or_pending_review
dispatch_surface_or_agent_loop_failure
context_compression_surface
unknown_blocked
```

`state_class` is the visible-thread control-plane classification. It must not
carry queue state such as busy, idle, or dispatch-needed. Report queue state in
`dispatch_readiness` separately:

```text
busy_in_progress
idle_needs_dispatch
idle_blocked_by_open_dependency
idle_no_ready_task
idle_waiting_review_or_approval
```

Accepted MWORKS window/session `state_class` values:

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

Free-text-only states such as `ok`, `normal`, `healthy`, `looks fine`,
`still running`, and `probably blocked` are invalid.

## 4. Approval, Review, And Provider Surfaces

Classify these before dead-thread recovery:

- Codex App `waitingOnApproval` or permission prompt.
- Visible `审核` / review / approval button.
- Pending generated-file review.
- Provider/API gateway banner such as `502 Bad Gateway` or reconnect UI.
- A completed turn with a visible review surface but no expected packet.

Use `approval_pending_or_ui_blocked` or
`provider_gateway_or_pending_review`. These states are not proof that the
department is dead and are not by themselves a reason for Codex++ restart,
replacement thread creation, or repeated no-op retries. Pause only the
affected business dispatch until the surface clears or PMO/user decides.

## 5. Dead-Thread Recovery

Treat native send/read success as transport evidence only. A thread is not
restored until the same visible thread can start a new turn and produce agent
output, an explicit requested ACK, an expected return/blocker packet, or a
successful recovery validation requested by the packet.

Recovery sequence for non-CoAgentOps departments:

1. PMO or patrol writes an initial blocker/recovery packet.
2. Stop business dispatch to the affected thread.
3. Route bounded diagnosis/recovery to CoAgentOps.
4. CoAgentOps checks list/read, latest turn, approval/provider surfaces, and
   at most one no-op or expected-packet probe when needed.
5. For confirmed start-turn or agent-loop failure, write a recovery packet.
6. Send one sparse Chinese email audit. Email is notification/audit only.
7. If the authorized Codex++ restart surface is available and no explicit
   deferral exists, continue restart in the same run.
8. After restart, validate the same visible thread before restoring routing.
9. Write a superseding packet with `thread_execution_surface_restored` and
   `business_task_or_patrol_completed` as separate claims.

If CoAgentOps itself cannot start turns, PMO must become the recovery owner
from a healthy user-triggered/current turn. PMO writes/reads the blocker,
sends sparse email, uses the authorized restart route when appropriate, and
then validates CoAgentOps after restart. A heartbeat attached to a dead
CoAgentOps conversation cannot self-rescue.

Default policy is restart recovery on the same thread, not replacement.
Replacement requires explicit PMO/user approval, repeated failed restart
recovery, or a critical path that cannot wait.

## 6. Bounded CoAgentOps Dispatch

CoAgentOps is allowed to dispatch a P0 task only when all conditions hold; when
all conditions hold, direct dispatch is required in that patrol run:

- Target is `status=active_visible`.
- Target thread is routable through the native visible-thread send/read
  surface.
- Task is already in the current P0 queue, `mainline_operations_board.md`,
  newest active `PROGRESS.md` entry, or explicitly recommended by the latest
  accepted return/blocker.
- Task is static/source-static, diagnostic-only, recovery validation,
  packet-contract fix, rule-sync/preflight drill, or another pre-authorized
  low-risk follow-up.
- Packet declares read scope, write scope, `native_surface_gate`,
  `semantic_boundary`, expected return path, blocker path, evidence minimum,
  allowed actions, forbidden actions, stop triggers, expected engineering
  outputs, and next owner.
- Native visible-thread send/read surface is available.
- PMO can be notified in the same run.
- No approval/review/provider UI surface, open dependency, unresolved
  dispatch-surface recovery, live GUI/license/manual-review risk, or PMO/user
  product-priority choice is required first.

When all conditions hold, dispatch is the required action, not a recommendation
for PMO to dispatch later. CoAgentOps must instantiate a task packet, send it
to the target visible department thread, and write or send the PMO sync record
in the same run. The dispatch packet must carry the expected engineering
output and stop before any live/manual/destructive action that is outside the
pre-authorized task class.

CoAgentOps must not dispatch when a task requires PMO/user product judgment,
thread or automation lifecycle change, foreground GUI action, approval click,
login/license/activation click, private auth material, destructive Git, live
MWORKS work without a current live gate, out-of-budget ROS2/RViz/FAST-LIO
probe, UE runtime mutation without producer/consumer gate, or any scope not
represented by the current P0 queue.

After dispatch, CoAgentOps notifies PMO with:

```text
request_id
target_department
target_thread_id
task_class
expected_return_path
blocker_return_path
why_dispatch_was_pre_authorized
task_packet_path
native_dispatch_result
```

## 7. MWORKS Window And Review Routing

Routine activation/window patrol belongs to CoAgentOps. MWORKS R1/R2 business
tasks should focus on engineering output and stop only when their current
MCP/API/GUI work observes demo, login, license, authorization, GUI-error, or
unknown blocking evidence.

Patrol must separate:

- Real reusable `mworks.exe` / Sysplorer / Syslab main windows.
- Helper/proxy windows such as `mw_browser_proxy.exe`, CEF, Qt glow/IME,
  docsearch, crash monitors, memory monitors, ACP server, and titlebar helper
  surfaces.
- Login/license/demo/authorization/error dialogs.
- Visible unknown MWORKS/Sysplorer/Syslab windows.

Ordinary graphical simulation, wiring/layout, Smart Layout, result-window, and
animation review is routed to MWORKS R2. Use the DPI-aware background capture
route for ordinary non-activation review and include observations, not only a
path. Activation/login/license/authorization and hidden-login-pane claims still
need foreground or maximized target-main-window evidence.

Do not close, restart, open fresh MWORKS windows, or click login/activation/
save/error-report controls from delegated MWORKS departments. PMO/CoAgentOps
may perform bounded recovery only after blocker evidence or explicit approval.

## 8. Packet Template

Task packets should be instantiated as JSON before dispatch. Use
`CoAgent/protocol/templates/visible_thread_dispatch_packet.json` as the
machine-checkable starting point for visible-thread dispatch. The sibling
`visible_thread_dispatch_packet.yaml` is a human-readable scaffold only and
must not be passed directly to the JSON checker.

The JSON task packet should include this control-plane envelope:

```yaml
request_id: <stable id>
origin_thread: MoSim｜主线 PMO
origin_thread_id: 019e9868-83ea-70f0-92c5-a3a408bd78c6
target_thread: <target visible thread title>
target_thread_id: <target visible thread id>
responsible_department: <owner>
task_id: <task id>
native_surface_gate:
  selected_native_surface: [visible_thread, coagent_packet_glue]
  surface_selection_reason: <why this route is the narrowest safe route>
  rejected_surfaces:
    subagent: <why disposable context is insufficient, or empty if not applicable>
  worktree_required: false
  worktree_decision: <why no isolated worktree is required, or binding if required>
semantic_boundary:
  decision_scope: <scope enum>
  state_class: <state enum>
  evidence_minimum:
    - <required evidence>
  allowed_actions:
    - <allowed action>
  forbidden_actions:
    - <forbidden action>
  stop_triggers:
    - <stop trigger>
  next_owner: <owner enum>
read_scope: []
write_scope: []
expected_return_path: Results/agent_packets/returns/<request_id>.json
blocker_return_path: Results/agent_packets/blockers/<request_id>.json
definition_of_done: <observable completion condition>
```

Run these checks for new packeted dispatch/recovery work:

```powershell
python Scripts\quality\check_agent_task_native_surface_gate.py `
  Results\agent_packets\<request_id>.json --strict
python Scripts\quality\check_agent_task_native_surface_gate.py `
  CoAgent\protocol\templates\visible_thread_dispatch_packet.json --strict
python Scripts\quality\check_department_packet_contract.py `
  Results\agent_packets\returns\<request_id>.json
```

MWORKS department packets must also pass `check_mworks_live_gate.py` with the
right `--expect` mode.

## 9. Board And Ledger Responsibility

`Docs/Workflows/mainline_operations_board.md` is the PMO current operating
surface. It records current P0 partition state, waiting returns, blockers,
manual decisions, integrable results, next PMO actions, and forbidden actions.
CoAgentOps patrol must report idle/blocked/recovery findings back into PMO's
dispatch queue through that board or a directly referenced packet.

`Docs/Workflows/agent_task_ledger.md` is a historical/recovery ledger. It keeps
durable delegated-task history, restart/recovery context, and trace-back rows.
It is not the normal PMO real-time board and should not be loaded as a full
routine context entry.

When the ledger becomes too large, split older completed rows into archive
files without changing current packet paths:

```text
Docs/Workflows/mainline_operations_board.md      current PMO operating board
Docs/Workflows/agent_task_ledger.md              historical/recovery rows
Docs/Archive/agent_task_ledger_2026_H1.md        archived completed rows
```

Fresh conversations should read the PMO board, newest `PROGRESS.md` entries,
and packets named by the board. Ledger rows are consulted only when a current
board item, packet, or recovery question references them.

## 10. Constraint Ownership Review Table

| Constraint | AGENTS hard boundary | Workflow | Packet template | JSON schema | Quality checker |
|---|---|---|---|---|---|
| Workspace, secrets, destructive operations, live GUI safety | yes | pointer only | no | no | preflight hooks |
| PMO final authority and CoAgentOps bounded authority | yes | yes | yes | no | semantic/native gate |
| Dead-thread recovery and restart order | pointer | yes | yes | optional fields | semantic/native gate |
| Approval/review/provider classification | pointer | yes | yes | `semantic_boundary` | semantic checker |
| MWORKS window/session classification | pointer | yes | yes | `semantic_boundary`, `mworks_live_gate` | native gate plus MWORKS gate |
| `native_surface_gate` and return/blocker paths | pointer | yes | yes | explicit fields | native gate |
| `semantic_boundary` fields | pointer | yes | yes | explicit fields | native gate and packet contract |
| Documentation secretary routing | pointer | yes | no | no | stale-name search |
| PMO board and historical ledger boundary | pointer | yes | no | no | stale-entry search plus PMO review |

## 11. Still Needs Human Review

- Whether to make `semantic_boundary` mandatory for every historical packet, or
  only for newly dispatched packets and current returns.
- When to physically archive old completed rows out of
  `Docs/Workflows/agent_task_ledger.md`.
- Whether the Codex++ restart surface remains acceptable for all persistent
  dead-thread incidents.
- Whether CoAgentOps bounded dispatch should stay limited to one task per
  patrol run or use a stricter active-capacity budget.
