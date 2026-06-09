# Mainline Operations Board

> PMO-facing short board for current MoSim operations. Keep this file concise:
> it is not a history ledger, not a packet archive, and not a replacement for
> `Docs/Workflows/coagent_ops_patrol_workflow.md`.

Status: MWORKS/Sysplorer main window restored and maximized by PMO after the
user challenged the missing live window; no login/license dialog was observed
by sentinel or foreground screenshot. UE 036, ROS2 079, and MWORKS R2 031 remain
integrated as source/static or bounded evidence only, 2026-06-09 17:25 CST.

## 1. PMO Startup Loop

Every PMO turn starts here after `AGENTS.md` and
`Docs/Workflows/new_conversation_context.md`:

1. Read this board first.
2. Check only the return/blocker packets named in this board.
3. If a state is unclear, trace back through
   `Docs/Workflows/agent_task_ledger.md` and the referenced packets.
4. Decide one next PMO action per P0 partition before support-lane work.
5. Update this board when a return/blocker changes PMO dispatch decisions.

Routine startup does not ingest the full ledger. The ledger is recovery and
audit context.

## 2. Ownership Boundaries

| Owner | Owns | Does Not Own |
|---|---|---|
| PMO | Mainline operating architecture, P0 priority, dispatch, acceptance, integration, thread lifecycle decisions, manual/GUI decisions, restart/recovery decisions | Long worker execution when a visible department owns the task |
| CoAgentOps | 10-minute patrol, recovery execution, bounded dispatch under `coagent_ops_patrol_workflow.md`, state reporting, thread-registry hygiene | Product priority, engineering acceptance, broad automation/thread lifecycle changes, final integration |
| 文档秘书部 | Context maintenance, documentation consistency review, cache-first migration, periodic cleanup, compact recovery notes | Defining PMO runtime rules, choosing P0 priority, accepting engineering results, recovering dead threads |

`Docs/Workflows/coagent_ops_patrol_workflow.md` is the only executable source
for CoAgentOps patrol, bounded dispatch, dead-thread recovery,
approval/review/provider surfaces, MWORKS window classification, and
email/restart order.

## 3. State Enums

Use these board states only:

```text
running
waiting_return
dispatch_needed
blocked_open_dependency
manual_decision_needed
recovery_pending
ready_to_integrate
frozen_by_user
support_only
done_no_action
```

Do not write vague states such as `healthy`, `normal`, `looks fine`, or
`probably blocked`.

## 4. Dispatch SLO Watchlist

Active dispatch monitoring rows use exactly these columns. The detailed
dispatch ticket JSON stores target thread, task type, expected paths,
checkpoint due, observations, and validation evidence.

| sent_at | first_readback_due | expected_packet_due | last_observed_turn | breach_action | owner |
|---|---|---|---|---|---|

## 5. P0 Partition Board

| Partition | Current State | Waiting Returns | Blockers | Human Decisions | Integrable Results | Next PMO Action | Forbidden Actions |
|---|---|---|---|---|---|---|---|
| MWORKS | dispatch_needed | No active MWORKS return is waiting; R2 031 completed and passed PMO validation | R1 failed current post-PC-restart send with `no active turn to steer`; 029 remains blocked/superseded by validated R2 backup evidence. PMO restored a reusable MWORKS/Sysplorer main window at 2026-06-09 17:20 CST, but live work still needs task-local no-start attach, GUI/license sufficiency, and engineering evidence | No user decision needed to keep the restored main window open; PMO/user decision is still needed before any live `check_model`, `SimulateModel`, package-browser, Smart Layout, or graphical/layout acceptance task | R1 static Batch A, R1 027 actuator mapper, R2 026 `OptionalDampingGyroLayer`, R2 030 `ActuatorMappedWrapperSurface`, R2 031 `PhysicalWrenchAdapter`, and PMO main-window recovery evidence are integrable only within their declared scopes | Next MWORKS action must start from the restored `Sysplorer [教育版]` window: either run a narrow no-start attach/live-gate validation task, or continue bounded static R2 work while R1 recovery remains pending | No duplicate 031, no R1 029 duplicate, no new MWORKS window unless the restored window fails, no login click, no activation/license claim from title alone, no live simulation/layout claim without current task-local evidence, and no retry loop from routing-surface recovery alone |
| ROS2 | blocked_open_dependency | No active ROS2 return is waiting; 079 post-reboot redispatch completed and the expected return packet passed PMO validation | 079 consumed its single live attempt, so no second probe is allowed; same-run raw TF/static TF still has no non-fake `camera_init` to `map/world/ue_world` chain; controller handoff remains blocked_no_map_world_grounding | PMO/user decision needed before any second probe, foreground RViz/manual review, planner/controller handoff, or setpoint publication | 074 headless live evidence bundle; 075 static gate; 076 same-run probe; 077 source route design; 078 same-run TF-chain capture contract; 079 single same-run TF-chain evidence probe and PMO integration, accepted only as `blocked_absent` grounding evidence | Decide the next low-risk source/static route task for real grounding or keep ROS2 blocked until PMO/user authorizes a new live probe/review path | No duplicate 079, no second 076/079 probe, no foreground RViz/manual GUI, no fake pointcloud/map/TF/odom, no keyboard pose, no UE truth shortcut, no planner_ready/closed_loop/runtime success/controller-performance claim |
| UE | ready_to_integrate | No active UE return is waiting; 036 post-reboot redispatch completed and the expected return packet passed PMO validation | Old 15:03 dispatch-surface failure remains historical evidence but is superseded for UE by the completed post-reboot 036 turn; 034 remains latest live preflight and did not consume the live attempt; 035/036 are source/static only | No restart now; any UE runtime/editor/build/live probe remains a separate PMO/user decision | 032 capture-bundle wiring; 033 bounded probe plan; 034 live-probe blocker integration; 035 producer/capture/cleanup route contract; 036 producer/capture/cleanup implementation surface and PMO integration | Treat 036 as source/static integrable evidence; decide a separate build-only gate or bounded live probe only through a new task packet | No UE runtime/editor/build/live probe by implication, no duplicate 036/035, no rerun 034, no UE runtime ack, final UI acceptance, MWORKS downlink, ROS2 runtime echo, planner_ready, or closed_loop claim |
| Git | running | DevOps closeout remains active by ledger | Large-tree ignore/drain queue still active; broad Git porcelain can be slow/noisy | PMO decides specific next path-limited batch when Git work becomes priority | Prior pushed slices are historical evidence; current staged runtime outputs are not this board's completion evidence | Keep Git work path-limited and do not let support work mask P0 engineering blockers | No `git add -A`, no force push/reset/clean, no broad cleanup, no hidden `.gitignore` backlog |
| Ops | recovery_pending | Post-PC-restart sweep blocker is available at `PMO-POST-PC-RESTART-P0-DISPATCH-SURFACE-SWEEP-20260609-001`; CoAgentOps is currently ACK-capable | MWORKS R1, ROS2 R1, and UE failed current post-PC-restart send attempts; 文档秘书部 also remains support-lane recovery debt | No restart now. User-facing notice was sent by sparse email at 2026-06-09T15:17:03+08:00 | CoAgentOps and MWORKS R2 returned exact post-PC-restart ACKs; CoAgentOps 029/079/036 blocker is validated; R2 030 delivery completed and return passed validation | Keep recovery evidence current; use R2 only for bounded static MWORKS work until primary P0 threads are superseded restored | No WeChat health checks, no archived gateway no-op, no replacement thread without explicit approval, no Codex restart from this sweep, no treating probe ACK as business/runtime success |

## 6. Support Lanes

| Lane | State | Rule |
|---|---|---|
| Sunray/PBR | frozen_by_user | Do not dispatch material/PBR/DAE visual changes unless the user explicitly reopens the lane. |
| Open-source probe/learning | support_only | Use only for a concrete source-first question; it cannot substitute for idle P0 engineering dispatch. |
| 文档秘书部 | support_only | Use for consistency review, context maintenance, and cleanup; it does not define PMO runtime rules. |
| DH TDMS goal thread | support_only | Refresh-only watch target `019de24d-e993-72c0-a0b2-caf2ac8ac85e` after Codex App/PC restart so its active goal can resume; not a MoSim dispatchable department. |

## 7. Current Board Maintenance Rules

- PMO updates this board when accepting a return, recording a blocker, changing
  the next dispatch, or after a CoAgentOps patrol changes a P0 state.
- CoAgentOps must directly dispatch routable idle P0 work when every
  bounded-dispatch gate in `coagent_ops_patrol_workflow.md` is satisfied. If
  any gate is missing, it reports `dispatch_needed` with the missing
  precondition. PMO decides acceptance, priority changes, narrowing,
  supersede, and any dispatch that needs product/user judgment.
- CoAgentOps may update only the fixed operating areas needed for patrol:
  P0 partition state, Dispatch SLO watchlist, Ops/recovery state, and Support
  lane state. It must not change product priority, accept/reject conclusions,
  or final integration judgments.
- Historical detail belongs in `Docs/Workflows/agent_task_ledger.md` and
  `Results/agent_packets/`, not in this board.
- Packet paths remain the durable evidence; this board is the short operating
  index that points to them.
- Dispatch SLO details belong in
  `Results/agent_packets/dispatch_tickets/<request_id>.json`. This board only
  displays `sent_at`, `first_readback_due`, `expected_packet_due`,
  `last_observed_turn`, `breach_action`, and `owner` for active dispatch
  monitoring.
- The dispatcher that sends a visible-thread task owns the dispatch ticket
  until terminal closure. A row with a visible turn stuck in progress/thinking
  but no agent output, checkpoint, final response, expected packet, blocker,
  approval/provider surface, or context-compression surface is not healthy
  progress and must breach through the ticket workflow.
- This board and the return packet
  `Results/agent_packets/returns/PMO-MAINLINE-OPERATIONS-BOARD-ARCHITECTURE-20260608-001.json`
  are the durable evidence for the PMO operating-architecture update.
- Current Git lock or staged `References/` warnings are unrelated Git/reference
  intake blockers. They do not block this control-plane board/packet delivery
  unless the exact board or packet paths are locked, staged-conflicted, or fail
  their targeted checks.
