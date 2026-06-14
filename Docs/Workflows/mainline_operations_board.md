# Mainline Operations Board

> PMO-facing short board for current MoSim operations. Keep this file concise:
> it is not a history ledger, not a packet archive, and not a replacement for
> `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`.

Status: temporary single-thread execution mode is active while the CoAgent
visible-thread architecture is being optimized. Do not dispatch to visible
department threads from this mode. Use
`Docs/Workflows/single_thread_longrun_execution_queue_20260610.md` as the
local 12h+ queue. Current 2026-06-12 execution has completed MWORKS formal
Dynamics smoke acceptance, single-UAV closeout, UE source-static replay input
bundle generation, local UDP loopback smoke, UE build-only gate, and a bounded
UE runtime replay ingest probe with log-level Sunray150 visibility/bounds
evidence. This still does not prove authoritative command echo acknowledgement,
final/manual visual acceptance, ROS2/FAST-LIO success, planner readiness,
controller performance from UE, multi-UAV readiness, or final material
acceptance.

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
| Current single-thread executor | Temporary local-only PMO/docs/static/checker execution while visible dispatch is paused by user direction. It may complete explicitly authorized local simulation/UE evidence slices and must record goal/sub-agent planning locally. | Visible-thread dispatch, product acceptance, final integration claims, or durable role-policy changes |

`CoAgent/docs/operating/coagent_ops_patrol_workflow.md` is the primary
CoAgentOps patrol/recovery source. The MoSim compatibility adapter at
`Docs/Workflows/coagent_ops_patrol_workflow.md` remains valid for host-specific
board paths, thread ids, MWORKS/ROS2/UE details, and no-loss migration review.

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
| 2026-06-09T21:38:17+08:00 | 2026-06-09T21:38:47+08:00 | 2026-06-09T22:38:17+08:00 | 019eac9a-f76d-7390-bb38-20b56bb723e1 status=inProgress agent_output_seen; no 032 return/blocker found in 2026-06-10 local sweep | breached_stale_no_terminal_packet | PMO / single-thread executor |

## 5. P0 Partition Board

| Partition | Current State | Waiting Returns | Blockers | Human Decisions | Integrable Results | Next PMO Action | Forbidden Actions |
|---|---|---|---|---|---|---|---|
| MWORKS | ready_to_integrate | none for current single-thread MWORKS smoke/closeout slice | 032 remains historical visible-thread terminal-packet debt, but it no longer blocks the current UE source-static/loopback path | User/PMO still decides any new live MWORKS GUI/layout/result-window review or report-final wording | 7/7 formal Dynamics smoke scenarios accepted as `dynamics_smoke_only`; single-UAV gate is `single_uav_gate_ready_for_ue_prep`; LinearMPC online fault-allocation rotor1-loss candidate remains the accepted current MWORKS_MCP run; its raw/metrics/replay artifacts now feed a passed UE replay input bundle and local UDP loopback smoke | Treat current MWORKS slice as closed for UE prep; do not start formation yet | No duplicate 031/032, no login click, no activation/license overclaim, no controller-performance claim from diagnostics smoke, no final report acceptance by implication |
| ROS2 | ready_to_integrate | `Results/agent_packets/returns/PMO-ROS2-R3-CAMERA-INIT-MAP-WORLD-GROUNDING-SOURCE-REPAIR-20260609-080.json` completed | 079 remains the latest same-run live evidence and still has no non-fake `camera_init` to `map/world/ue_world` chain; controller handoff remains blocked_no_map_world_grounding | PMO/user decision needed before any second probe, foreground RViz/manual review, planner/controller handoff, or setpoint publication | 080 adds source/static repair surface, route matrix, focused checker/test, and future single-probe gate only | Integrate 080 into design/evidence docs as future-gate readiness; keep current runtime grounding blocked until a separately authorized live probe proves it | No duplicate 079/080, no second 076/079 probe, no foreground RViz/manual GUI, no fake pointcloud/map/TF/odom, no keyboard pose, no UE truth shortcut, no planner_ready/closed_loop/runtime success/controller-performance claim |
| UE | running | none for current UE replay and command-echo hardening slices | 034 remains latest historical live preflight; no live seven-artifact command-echo capture bundle exists yet; current opened review screenshots do not show Sunray150 clearly by eye | PMO/user product acceptance is still needed for final/manual visual acceptance and material acceptance, but opening existing review materials no longer waits for separate authorization | 037 classifies the 036 runtime-echo implementation surface as `build_only_gate_ready`; accepted MWORKS run has `ue_replay_input_bundle.json` plus passed local `ue_state_stream_loopback.json`; build-only gate passed at `Results/ue_build/20260612_102452_mosim_scene_library_editor_build/build_manifest.json`; bounded runtime replay ingest probe passed at `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/ue_runtime_replay_probe_summary.json`; current command-echo hardening evidence is under `Results/unreal_experiment_console/command_echo_evidence_hardening_20260612_001/`; current visual-review planning packet is `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_review_path_20260612_001/current_review_packet.json` | Continue with the next executable UE path: either produce close/zoomed after-stream Sunray150 visual-review evidence, or run one bounded command-echo live probe that produces the seven required artifacts and then validate it | No duplicate 036/037, no authoritative UE command echo ack from static/checker/build/sender/UDP/state-frame evidence, no final/manual visual acceptance from far scene screenshots, no MWORKS downlink, ROS2 runtime echo, planner_ready, controller-performance-from-UE, material acceptance, multi-UAV readiness, or closed_loop claim |
| Git | running | DevOps closeout remains active by ledger | Large-tree ignore/drain queue still active; broad Git porcelain can be slow/noisy | PMO decides specific next path-limited batch when Git work becomes priority | Prior pushed slices are historical evidence; current staged runtime outputs are not this board's completion evidence | Keep Git work path-limited and do not let support work mask P0 engineering blockers | No `git add -A`, no force push/reset/clean, no broad cleanup, no hidden `.gitignore` backlog |
| Ops | recovery_pending | Post-PC-restart sweep blocker is available at `PMO-POST-PC-RESTART-P0-DISPATCH-SURFACE-SWEEP-20260609-001`; CoAgentOps is currently ACK-capable | MWORKS R1, ROS2 R1, and UE failed current post-PC-restart send attempts; 文档秘书部 also remains support-lane recovery debt | No restart now. User-facing notice was sent by sparse email at 2026-06-09T15:17:03+08:00 | CoAgentOps and MWORKS R2 returned exact post-PC-restart ACKs; CoAgentOps 029/079/036 blocker is validated; R2 030 delivery completed and return passed validation | Keep recovery evidence current; use R2 only for bounded static MWORKS work until primary P0 threads are superseded restored | No WeChat health checks, no archived gateway no-op, no replacement thread without explicit approval, no Codex restart from this sweep, no treating probe ACK as business/runtime success |

### Current UE Execution Pointer

Current UE next-slice plan:

```text
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_review_path_20260612_001/next_execution_plan.json
```

The preferred next executable slice is UE visual-review hardening with the
Factory follow-camera route, because the existing screenshot proves a nonblank
Factory scene but not a human-visible Sunray150 body. Command-echo live probe
remains the second slice unless PMO/user explicitly prioritizes it first; it
must produce the seven required artifacts and pass the existing validator.

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
