# CoAgentOps Patrol And Recovery Workflow

> Legacy after 2026-06-24 single-thread reset. CoAgentOps patrol, bounded
> dispatch, visible-thread recovery, and dispatch SLOs are not active MoSim
> workflow unless the user explicitly reopens that architecture.

> MoSim compatibility entrypoint. The portable CoAgent OS source of truth is
> `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`; keep reusable
> patrol/recovery/dispatch SLO rules there first, then mirror only MoSim PMO,
> board, MWORKS, ROS2, UE, and thread-id adapter notes here.

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
| Documentation secretary | `MoSim｜Codex 上下文维护部` (`019eab73-c5bc-7740-a6d1-5e0541bdb0c5`) |
| Registry source | `CoAgent/dispatch/department_threads.json` |
| Return channel | `Results/agent_packets/returns/<request_id>.json` |
| Blocker channel | `Results/agent_packets/blockers/<request_id>.json` |

Former names such as `MoSim｜文档秘书部`, R-suffixed context-maintenance titles,
and `MoSim｜知识秘书` are alias/history only.
Future context-memory, documentation consistency, startup recovery, and
cache-first migration tasks route to `MoSim｜Codex 上下文维护部`. The internal
key `CodexContextMaintenanceAgent` may remain in compatibility metadata.

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

When a patrol observes `login_or_license_blocked`,
`authorization_blocked`, `gui_error_blocked`, `visible_unknown_blocked`,
`live_attach_blocked`, or any ambiguous MWORKS/Sysplorer/Syslab main-window
state, CoAgentOps must load
`Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` before sending the final
blocker, email, or attempting bounded recovery. Use that skill's rules 12-21
as the recovery SOP:

- Engineering departments stop live MCP/model/GUI work and return a blocker;
  they do not click login, activation, license, save, close, restart, or
  error-report controls.
- CoAgentOps/PMO may perform bounded official login/license recovery only when
  the user/PMO has explicitly authorized it for the current incident.
- Background screenshots do not prove activation, license, login, or
  authorization success. Acceptance requires foreground or maximized evidence
  of the target reusable MWORKS/Sysplorer/Syslab main window.
- Use only the approved secure credential source named by the user/PMO. Never
  write account names, passwords, tokens, or credential hints into project
  docs, packets, logs, screenshot manifests, terminal output, emails, or
  cross-thread chat.
- If the approved secure credential source is missing, inaccessible, or
  ambiguous, stop recovery and ask PMO/user to provide a safe credential route;
  do not guess or search personal credential locations.
- Stop without action on MFA/captcha, account/password error, abnormal
  authorization, unknown modal/window, crash/error-report, save/overwrite
  prompt, or any non-MWORKS credential surface.
- After successful bounded recovery, keep the reusable target main window open
  unless the current task explicitly authorizes closing a specific dialog.

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

### 5.1 Post-Restart Probe Sweep

When the user restarts Codex App or the computer after widespread visible-thread
failure, start a fresh incident clock from the confirmed app restart time:

```text
app_restart_completed_at=<ISO timestamp from the first healthy PMO turn>
```

Before dispatching business work, PMO or CoAgentOps must run a bounded probe
sweep over every current `status=active_visible` route in
`CoAgent/dispatch/department_threads.json`:

1. Read the current registry and list/read each active visible thread.
2. Send exactly one short no-op probe per active department thread, unless the
   thread is the current PMO thread or the user explicitly excludes it.
3. Immediately `read_thread` after each send and record whether a new visible
   turn appears.
4. Recheck any thread without a visible turn within 2 minutes.
5. At 5 minutes after that thread's probe `sent_at`, classify it as
   `dispatch_surface_failure_suspected` if there is still no visible turn,
   agent output, expected ACK, return/blocker packet, approval/provider
   surface, or context-compression surface.
6. Record per-thread timing as:
   `last_known_alive_at`, `probe_sent_at`, `first_missing_at`,
   `failure_suspected_at`, and `dead_thread_duration_minutes`.
7. Do not restart Codex again during the sweep unless the user explicitly
   authorizes it for the active incident.

The probe text must be minimal and must not include business work. Example:

```text
PMO post-restart health probe only. If you can start a new turn, reply exactly:
<department_key>_post_restart_probe_ok_<YYYYMMDD_HHMM>
Do not read/write project files, do not run commands, do not dispatch work.
```

The sweep result belongs in
`Results/agent_packets/returns/PMO-POST-RESTART-PROBE-SWEEP-<date>-001.json`
or, if the sweep itself is blocked,
`Results/agent_packets/blockers/PMO-POST-RESTART-PROBE-SWEEP-<date>-001.json`.
It must include one row per active visible thread and the measured timing
fields above. This sweep is control-plane recovery evidence only; it does not
prove MWORKS/ROS2/UE business progress.

### 5.2 Durable Start And Main-Shell Observation

Default liveness evidence is durable project state, not transcript clicking.
For every non-trivial visible-department dispatch, the task packet must include
`durable_start_requirement`. The target thread's first execution step is to
create or update that small artifact inside the declared write scope, then
continue with the actual work. Acceptable durable-start artifacts include a
checkpoint, return packet, blocker packet, task-local notes file, declared
output scaffold, or another project-local file named by the packet.

For new visible-thread dispatches, the default artifact is a runtime lease at
`Results/runtime_leases/<target_thread_id>/<request_id>.json`. The dispatcher
must create a `ticket_version=2` dispatch ticket with a fresh `dispatch_nonce`
and must put the same nonce in the task packet's
`durable_start_requirement`. The target thread must echo that value as `nonce`
in the runtime lease. A lease with the wrong nonce is stale evidence and does
not count as dispatch progress.

The durable-start artifact proves that the execution surface has started and
can write recoverable state. It does not prove engineering completion.
Exact no-op probes that explicitly forbid file writes are exempt.

For `source_static`, `control_plane`, `packet_contract_fix`,
`dispatch_surface_diagnostic`, and `recovery_validation`, durable-start is a
first-start proof, not a continuing heartbeat. Once patrol sees a fresh
matching durable-start artifact, agent output, return/blocker packet,
approval/provider surface, or context-compression surface for the dispatched
request, it must stop treating missing later checkpoints as a dead-thread
signal and wait for the declared expected packet due time. Continuing
checkpoint freshness is required only for task types that declare
`checkpoint_due`, normally `live_runtime`, `mworks_gui`, and `manual_review`.

Dispatch-surface classification after send:

1. Check native read/send state and latest visible turn.
2. Check the expected return, blocker, checkpoint, and durable-start paths;
   for runtime leases, require the same request id, target thread id, and
   nonce from the current dispatch ticket.
3. Check approval/review/provider/context-compression surfaces.
4. Check the Codex App main shell/list area only for global indicators such as
   green `待批准`/approval, pending review, reconnect, or provider banners.
5. If 5 minutes after `sent_at` there is no durable-start artifact, no agent
   output, no expected packet/checkpoint/blocker, and no known UI/provider
   surface, classify as `dispatch_surface_failure_suspected` and write a
   recovery/blocker packet.

If several unrelated active visible threads stop producing new turns after they
had already started, classify the situation as a global Codex/App/network
incident first. Do not convert source/static tasks into per-thread
stale-worker incidents merely because no later checkpoint was written.

Routine heartbeat patrol must not click through every thread row to refresh
transcripts. Slow or blank transcript views are `view_refresh_required`
observations, not dead-thread evidence. Record them in the ticket or recovery
notes, then rely on native read/send checks, expected-packet checks,
durable-start artifact checks, and main-shell observation.

The 10-minute patrol may capture or inspect the Codex App main shell/list area
when the native desktop surface is available. Its default UI purpose is only to
notice pending approval/review/provider indicators and send a sparse Chinese
email or PMO notice. It must not click approval/review/send/restart/login/save/
archive/delete/pin/overflow/composer controls.

A bounded thread-row refresh exception is allowed only when a specific recovery
incident explicitly authorizes it. That exception must be observation-only,
must prefer stable UI Automation/OCR/title matching over raw coordinates, must
avoid all controls listed above, and must not become the default heartbeat
mechanism. If the thread list is collapsed and the incident explicitly requires
view recovery, the only allowed list-control action is restoring list visibility
through the documented expand control; record drift risk and stop if the target
cannot be identified safely.

### 5.3 Incident-Scoped Thread-Row Refresh Appendix

This appendix preserves the user-approved refresh details as a recovery-only
tool. It is not part of the routine 10-minute patrol and does not override the
durable-start evidence ladder.

Allowed only when a named recovery incident or PMO packet explicitly requests
visible-thread refresh:

1. Use background/native UI automation when available; do not maximize Codex
   App solely for this action.
2. Click only the stable title region for rows whose title begins with
   `MoSim｜`. Do not click pin controls, project/folder headers, overflow
   menus, composer/send areas, approval/review controls, restart controls, or
   unknown UI chrome.
3. If the project/thread list is collapsed, expand only through the documented
   list expand control, wait `0.5s`, then re-identify the target rows. If the
   target cannot be identified after expansion, stop and report a blocker.
4. Dwell time on each selected row is `0.5s`. Capture/observe after the dwell,
   then move to the next scoped target.
5. If a transcript pane is blank, loading, or visually ambiguous, record
   `view_refresh_required`, skip business classification for that row, and
   continue to the next scoped target. Recheck on the next authorized refresh
   pass; do not wait on the blank pane inside the sweep.
6. If two passes still show blank/loading content while native read/send,
   durable-start, expected-packet, and main-shell checks show no progress or UI
   blocker, write a recovery/blocker packet and send the sparse Chinese alert.
7. Include the refresh-only non-MoSim watch target
   `019de24d-e993-72c0-a0b2-caf2ac8ac85e` only after Codex App/PC restart, and
   only to refresh its goal-bearing window. It is not dispatchable MoSim work.

Forbidden actions remain absolute: do not click approval, review, send,
restart, login, authorization, save, archive, delete, pin, overflow, unknown
controls, or any MWORKS/Sysplorer/Syslab UI from this refresh procedure.

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
dispatch_ticket_path
why_dispatch_was_pre_authorized
task_packet_path
native_dispatch_result
```

Before the visible-thread send call, the dispatcher must create/update the
dispatch ticket at `Results/agent_packets/dispatch_tickets/<request_id>.json`
with `dispatcher_owns_slo_closure=true`, then validate it with
`Scripts/quality/check_dispatch_ticket_slo.py`. The dispatcher is the PMO or
CoAgentOps turn that actually sends the task; a 10-minute patrol may audit or
catch a missed ticket, but it is not the primary timer owner. The delivery SLO
is:

```text
sent_at -> immediate read_thread once
if no visible turn -> read again within 2 minutes
if visible turn is only inProgress/thinking with no agent output/final/packet
  by first_agent_output_due -> classify dispatch_surface_failure_suspected
if 5 minutes passes with no meaningful progress -> classify
  dispatch_surface_failure_suspected and write a recovery/blocker
```

Meaningful progress means one of: matching runtime lease/durable-start
artifact, agent output, expected return packet, blocker packet, checkpoint
packet, approval/provider surface, or context-compression surface. Native send
success, an old exact ACK, a stale lease with the wrong nonce, or a new visible
turn stuck in thinking/in-progress with no agent output is not meaningful
progress.

Task-type SLO is layered. `source_static`, `control_plane`, and
`packet_contract_fix` tasks normally expect a return/blocker packet within
10-20 minutes. `dispatch_surface_diagnostic` and `recovery_validation` expect
2-10 minutes. `live_runtime`, `mworks_gui`, and `manual_review` may run longer,
but their ticket must declare `checkpoint_due`; the first checkpoint is due
within 10 minutes for live/runtime/MWORKS GUI and within 15 minutes for manual
review.

The PMO board must show only the dispatch watch fields
`sent_at / first_readback_due / expected_packet_due / last_observed_turn /
breach_action / owner`. Detailed thread id, expected paths, checkpoint due,
and observations stay in the JSON ticket.

If CoAgentOps discovers an active ticket whose `dispatcher_next_check_due` has
passed and the dispatcher has not advanced it to a terminal state, CoAgentOps
reports the missed dispatcher closure to PMO and may write an audit blocker.
That is a fail-close catch for a broken dispatch loop, not the normal way a
task timer should close.

### 6.1 R2/R3 Failover Lane

For the three main engineering departments, R2 is the first failover lane when
R1 has a confirmed dispatch/start-turn failure, is blocked by dispatch-surface
recovery, or has a live/manual task with an overdue declared checkpoint and a
safe failover task is available. CoAgentOps must check this during each
10-minute patrol. For source/static/control-plane work, do not use missing
post-start checkpoints as the R2 trigger; use missing first-start proof,
missing expected return/blocker by the ticket due time, or an explicit blocker.

R2 failover packets are limited to:

```text
source_static
diagnostic_only
packet_contract_fix
rule_sync_only
checker/review
```

R2 failover must not run MWORKS live work, ROS2 live work, UE runtime/build/
editor work, GUI clicks, login/authorization/save/restart actions, or setpoint
publication. Default R2 work is still accountable department work: the packet
must include expected outputs, return/blocker paths, stop triggers, and the
department-local planning fields.

R3 is not an automatic response to any single R1 or R2 failure. PMO proposes or
approves R3 only when R2 failover still leaves a P0 partition idle/blocked long
enough that reserve capacity is useful. Do not use a generic "R1/R2 died
multiple times in 24 hours" rule as an R3 trigger.

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

Window action boundary:

- Activation/license/login/window-health audit uses the real reusable main
  MWORKS/Sysplorer/Syslab window, foreground or maximized evidence, because
  hidden login panes can be missed by background capture.
- If audit finds no reusable main window, CoAgentOps opens MWORKS directly,
  captures a first screenshot after 5 seconds, then continues a
  bounded stability check before classifying the state. Do not close the run by
  only reporting "window not open" when opening the window is the authorized
  recovery action.
- Ordinary non-activation screenshots do not need maximization. Prefer the
  background Win32 `PrintWindow` route
  `Scripts/tools/capture_window_background.ps1`; this is not a Windows MCP
  foreground desktop screenshot. If the target was minimized, use
  `-RestoreMinimized -MinimizeAfter`, verify manifest `dpi_awareness`,
  physical capture size, nonblank content, and leave the window minimized
  afterward. Use `-Maximize` only for activation/login/license/authorization
  evidence or an explicitly requested full-window wiring/layout review.
- If ordinary background capture shows blank, wrong, or ambiguous content,
  retry once after a short wait; only then escalate to foreground/maximized
  review or a blocker.

Do not close, restart, open fresh MWORKS windows, or click login/activation/
save/error-report controls from delegated MWORKS departments. PMO/CoAgentOps
may perform bounded official login recovery only when user-authorized, using a
secure credential source, foreground/maximized target-window evidence, and the
documented stop conditions.

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

CoAgentOps may update only these fixed board areas during patrol:

```text
P0 partition state
Dispatch SLO watchlist
Ops/recovery state
Support lane state
```

CoAgentOps must not change product priority, PMO accept/reject conclusions, or
final integration judgments. When such a decision is needed, write a packet or
board note that clearly assigns the next owner to PMO/user.

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
