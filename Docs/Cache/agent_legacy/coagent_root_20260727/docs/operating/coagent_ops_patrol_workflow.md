# CoAgentOps Patrol And Recovery Workflow

Status: portable core, split-audited 2026-06-10 CST.

This file defines reusable CoAgentOps patrol, dispatch-SLO, liveness, recovery,
and failover behavior. Host-project details such as concrete thread IDs,
current boards, domain windows, email wording, and tool paths belong in host
adapters.

MoSim host adapters:

```text
Docs/Workflows/coagent_ops_patrol_workflow.md
Docs/Workflows/mosim_visible_dispatch_adapter.md
Docs/Workflows/mainline_operations_board.md
CoAgent/dispatch/department_threads.json
```

The no-loss split is recorded in:

```text
CoAgent/docs/operating/audits/no_loss_split_audit_20260610.md
CoAgent/docs/operating/MIGRATION_MAP.md
```

## 1. Authority Boundary

CoAgentOps is a control-plane operator. It may patrol, classify visible-thread
state, maintain dispatch SLO records, recover dispatch surfaces, and perform
bounded pre-authorized dispatch when every gate in this workflow is satisfied.

CoAgentOps does not own product priority, acceptance/rejection, final
integration, visible-thread lifecycle decisions, automation lifecycle changes,
destructive Git, private authentication material, foreground approval clicks,
or host-specific GUI actions unless a host adapter and task packet explicitly
authorize that action.

The host project must define:

```text
PMO/product owner
CoAgentOps owner
current visible-route registry
current operating board
return/blocker/checkpoint packet roots
human notification channel
domain adapters and live-resource gates
```

## 2. Patrol Inputs

Each patrol reads only the minimum current control-plane context:

1. Compact project entry instructions.
2. CoAgent communication contract and packet templates.
3. Current visible-route registry.
4. Current PMO/operating board or queue.
5. Active dispatch tickets, return packets, blockers, checkpoints, recovery
   packets, and board-referenced ledger rows.
6. Host adapter documents only for domains touched in this patrol.

Patrol must ignore routes that the registry marks archived, deleted,
superseded, or not currently dispatchable. Absence of an archived/deleted route
is not a failure.

## 3. Semantic Boundary

Every patrol, recovery, dispatch, checkpoint, or review packet that makes a
state claim must include a semantic boundary:

```yaml
semantic_boundary:
  decision_scope: visible_thread | domain_window_patrol | live_task | runtime_task | asset_review | other
  state_class: <one concrete value>
  evidence_minimum:
    - <minimum evidence inspected before this state was claimed>
  allowed_actions:
    - <actions allowed while in this state>
  forbidden_actions:
    - <actions forbidden while in this state>
  stop_triggers:
    - <observations that force blocker/checkpoint>
  next_owner: <PMO | CoAgentOps | target_department | user | other>
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

`state_class` is not queue state. Report queue readiness separately as:

```text
busy_in_progress
idle_needs_dispatch
idle_blocked_by_open_dependency
idle_no_ready_task
idle_waiting_review_or_approval
```

Domain-specific state classes, such as simulator window or runtime resource
states, must be supplied by the host adapter and named in the task packet.
Free-text-only states such as `ok`, `normal`, `healthy`, `looks fine`,
`probably blocked`, and `still running` are invalid.

## 4. Approval, Review, And Provider Surfaces

Classify these before dead-thread recovery:

```text
permission or waiting-on-approval prompt
visible review/approval surface
pending generated-file review
provider/API gateway banner
reconnect surface
completed turn with pending review UI and no expected packet
```

Use `approval_pending_or_ui_blocked` or
`provider_gateway_or_pending_review`. These states are not proof that the
department is dead and are not by themselves a reason for app restart,
replacement thread creation, or repeated no-op retries. Pause only the
affected business dispatch until the surface clears or PMO/user decides.

## 5. Durable Start And Dispatch SLO

Default liveness evidence is durable project state, not transcript clicking.
Every non-trivial visible-department dispatch must include:

```text
dispatch ticket
fresh dispatch nonce
durable_start_requirement
expected return path
blocker path
expected packet due time
first readback due time
breach action
```

For visible-thread dispatch, the default durable-start artifact is a runtime
lease:

```text
Results/runtime_leases/<target_thread_id>/<request_id>.json
```

The dispatcher must create a `ticket_version=2` dispatch ticket with a fresh
`dispatch_nonce` and put the same nonce in the task packet's
`durable_start_requirement`. The target thread must echo the nonce in the
runtime lease. A lease with the wrong nonce is stale evidence and does not
count as progress.

Exact no-write probes are exempt from durable-start writes only when the probe
explicitly forbids file writes.

Meaningful progress means one of:

```text
matching durable-start artifact or runtime lease
agent output
expected return packet
blocker packet
checkpoint packet
approval/provider/review surface
context-compression surface
```

Native send success, old exact ACKs, stale leases, or a new visible turn stuck
in thinking/in-progress with no agent output are not meaningful progress.

Default SLO ladder:

```text
sent_at -> immediate readback
if no visible turn -> read again within 2 minutes
if 5 minutes passes without meaningful progress -> classify
  dispatch_surface_failure_suspected and write recovery/blocker evidence
```

Task-type SLO is layered:

```text
source_static / control_plane / packet_contract_fix: return or blocker in 10-20 minutes
dispatch_surface_diagnostic / recovery_validation: return or blocker in 2-10 minutes
live_runtime / GUI / manual_review: checkpoint_due must be declared
```

Continuing checkpoint freshness is required only for task types that declare
`checkpoint_due`. For static/control-plane work, once a matching durable-start
artifact, return/blocker, approval/provider surface, or context-compression
surface appears, missing later checkpoints must not be reclassified as a
dead-thread signal before the expected packet due time.

## 6. Main-Shell Observation And Transcript Refresh

Routine heartbeat patrol must not click through every visible thread row as
the default liveness mechanism. Slow or blank transcript views are
`view_refresh_required` observations, not dead-thread evidence.

The default liveness ladder is:

```text
dispatch ticket
  -> native read/send state
  -> durable-start / packet / checkpoint checks
  -> approval/review/provider/context-compression classification
  -> main-shell pending indicator observation
  -> recovery/blocker if no meaningful progress exists
```

The patrol may observe or capture the application main shell/list area when the
native desktop surface is available. The default UI purpose is only to notice
global pending approval/review/provider indicators and trigger the host
notification route. It must not click approval, review, send, restart, login,
save, archive, delete, pin, overflow, composer controls, or unknown UI chrome.

A bounded thread-row refresh exception is allowed only when a named recovery
incident or PMO packet explicitly requests it. That exception must be
observation-only, must prefer stable UI Automation/OCR/title matching over raw
coordinates, must avoid forbidden controls, and must not become a routine
heartbeat mechanism. Host adapters may define title prefixes, dwell time, and
blank-pane handling for a specific desktop application.

## 7. Bounded Dispatch

CoAgentOps may dispatch a task only when all conditions hold:

```text
target route is current and dispatchable
target native send/read surface is available
task is already in the current queue/board or latest accepted packet
task class is pre-authorized low risk
packet declares complete read/write/evidence/stop boundaries
dispatch ticket and durable-start requirement are valid
PMO can be notified in the same run
no approval/review/provider surface blocks the target
no open dependency or product-priority decision is needed first
no host live-resource, GUI, auth, destructive, or manual-review risk is present
```

When all conditions hold, direct dispatch is the required action, not merely a
recommendation for PMO to dispatch later. CoAgentOps must instantiate the task
packet, create/update the dispatch ticket, send the task to the target route,
and write or send the PMO sync record in the same run.

CoAgentOps must not dispatch when the next step requires PMO/user product
judgment, route/automation lifecycle change, foreground GUI action, approval
click, login/license/activation click, private auth material, destructive Git,
unapproved live runtime work, or any scope outside the current queue.

The PMO sync record includes:

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

## 8. Recovery

Treat native send/read success as transport evidence only. A thread is not
restored until the same visible route can start a new turn and produce agent
output, an explicit requested ACK, an expected return/blocker packet, or a
successful recovery validation requested by the packet.

Recovery sequence for a department route:

1. Write an initial blocker or recovery packet.
2. Stop business dispatch to the affected route.
3. Check native list/read state, latest turn, approval/review/provider
   surfaces, durable-start artifacts, expected packets, and active tickets.
4. Use at most one no-op or expected-packet probe when the packet authorizes
   it.
5. For confirmed start-turn or agent-loop failure, write a recovery packet.
6. Notify through the host human-notification channel.
7. If an authorized restart surface is available and no explicit deferral
   exists, continue restart recovery in the same run.
8. After restart, validate the same visible route before restoring business
   dispatch.
9. Write a superseding packet that separates
   `thread_execution_surface_restored` from
   `business_task_or_patrol_completed`.

If CoAgentOps itself cannot start turns, a healthy PMO/current user-triggered
turn becomes recovery owner. A dead CoAgentOps heartbeat cannot self-rescue.

Default policy is restart recovery on the same route, not replacement.
Replacement requires explicit PMO/user approval, repeated failed restart
recovery, or a critical path that cannot wait.

## 9. Post-Restart Probe Sweep

After an application or machine restart that may affect multiple visible
routes, start a fresh incident clock from the confirmed restart completion time:

```text
app_restart_completed_at=<ISO timestamp from first healthy PMO/current turn>
```

Before dispatching business work, run a bounded probe sweep over current
dispatchable routes:

1. Read the current registry and each active visible route.
2. Send exactly one short no-op probe per scoped route unless excluded by the
   incident packet.
3. Immediately read back after each send.
4. Recheck missing visible turns within 2 minutes.
5. At 5 minutes after that route's `probe_sent_at`, classify suspected
   dispatch-surface failure only if there is still no visible turn, output,
   expected ACK, return/blocker packet, approval/provider surface, or
   context-compression surface.
6. Record `last_known_alive_at`, `probe_sent_at`, `first_missing_at`,
   `failure_suspected_at`, and `dead_thread_duration_minutes`.
7. Do not restart again during the sweep unless explicitly authorized for the
   active incident.

The probe text must be minimal and must not include business work.

## 10. Failover

The portable failover model is:

```text
R1: primary execution lane
R2: first safe failover lane for static/diagnostic/contract/review work
R3: reserve capacity proposed or approved only after R2 failover still leaves
    important work idle or blocked
```

R2 failover is appropriate when R1 has a confirmed dispatch/start-turn failure,
is blocked by dispatch-surface recovery, or has an overdue declared checkpoint
for a live/manual task and a safe failover task exists.

Default R2/R3 failover task classes:

```text
source_static
diagnostic_only
packet_contract_fix
rule_sync_only
checker/review
```

Default failover must not perform live runtime work, GUI clicks, login,
authorization, save, restart, destructive mutation, or host-specific live
resource actions. A host adapter may narrow this further. It may broaden it
only with explicit PMO/user approval and a task packet that names the live
resource and stop conditions.

Do not use a generic "R1/R2 died multiple times in 24 hours" rule as an R3
trigger. The trigger is current critical-path idle/blockage after R2 failover
is insufficient.

## 11. Desktop Window And Host Live-Resource Adapters

Desktop observation and desktop action are separate capabilities:

```text
screenshot/capture evidence does not imply click/action authority
background capture does not prove login/license/authorization success
foreground/maximized evidence may be required by host adapters
```

Host adapters define domain-specific window/session state classes, live
resource ownership, screenshot requirements, and allowed/forbidden UI actions.
The portable default is stop-and-block on unknown, login/license/auth,
crash/error-report, destructive, or manually ambiguous UI surfaces.

## 12. Packet And Checker Requirements

Task packets should start from:

```text
CoAgent/protocol/templates/visible_thread_dispatch_packet.json
```

Dispatch tickets should start from:

```text
CoAgent/protocol/templates/visible_thread_dispatch_ticket.json
```

New visible-thread dispatch/recovery work must pass the host's relevant
checkers. At minimum, use the native-surface and dispatch-ticket validators
when present:

```powershell
python Scripts\quality\check_agent_task_native_surface_gate.py <packet.json> --strict
python Scripts\quality\check_dispatch_ticket_slo.py <ticket.json>
```

Host domains may add stricter checkers, such as live-resource gates or
department-specific return contracts.

## 13. Board And Ledger Responsibility

The current operating board records current queue state, waiting returns,
blockers, manual decisions, integrable results, next actions, and forbidden
actions. CoAgentOps may update only host-authorized control-plane areas. It
must not change product priority, accept/reject conclusions, or final
integration judgments.

Detailed dispatch timing, ticket paths, checkpoint due times, and observations
belong in JSON tickets or recovery packets. A board should show only a compact
watchlist view.

Historical/recovery ledgers are not routine startup context. Read them only
when a current board item, packet, or recovery question references them.

## 14. Human Review Triggers

Escalate rather than acting when:

```text
semantic evidence is missing
packet fields are incomplete
route status or native surface is uncertain
host adapter is absent or contradictory
PMO/user priority decision is needed
approval/review/provider surface is present
live GUI/runtime/manual-review risk is present
restart/replacement/automation lifecycle change is required
```

The correct output in those cases is a blocker, recovery packet, or PMO/user
question with the missing gate named explicitly.
