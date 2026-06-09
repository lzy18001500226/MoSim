# Project Progress

## 2026-06-09 CST - PMO Created MWORKS/ROS2/UE R3 Reserve Threads

- User explicitly approved creating R3 reserve routes for the three main
  departments. PMO created and titled the visible Codex threads:
  MWORKS R3 `019eac00-55d6-7443-b986-1b501503195a`, ROS2 R3
  `019eac00-70be-7172-b158-b585079c7d67`, and UE R3
  `019eac00-8645-7da3-b43e-d9169b2713e7`.
- All three R3 threads completed their initialization ACK turns and were
  registered in `CoAgent/dispatch/department_threads.json` as
  `active_visible` `permanent_reserve` routes. Each R3 is restricted to
  explicit PMO/CoAgentOps packets for static, diagnostic, packet-contract,
  rule-sync, checker, or review work when R1/R2 dead-thread surfaces block
  progress.
- No MWORKS, ROS2, or UE business work was dispatched. R3 reserve routes do
  not run live MWORKS GUI/MCP/check_model/SimulateModel, ROS2/RViz/FAST-LIO/
  planner/controller runtime, or UE editor/build/runtime work by default.

## 2026-06-09 CST - CoAgentOps Superseded MWORKS R1 028 Routing Recovery

- CoAgentOps closed the MWORKS R1 028 dispatch-surface recovery loop at the
  thread-execution layer. The pre-restart sparse email audit
  `Results/coagent_gateway/email/email_alert_20260609_052402.json` succeeded,
  Codex++ watchdog evidence
  `Results/codex_watchdog/codex_outer_watchdog_check_20260609_052425.json`
  reports `restart_requested=true` and `restart_result.ok=true`, and the same
  visible R1 thread completed validation turn
  `019ea92c-5746-7681-9e0a-55c7b340b6fa` with exact ACK
  `mworks_r1_028_post_restart_validation_ack_20260609_0525`.
- Supersede return:
  `Results/agent_packets/returns/COAGENTOPS-MWORKS-R1-028-DISPATCH-SURFACE-RECOVERY-SUPERSEDE-20260609-001.json`.
  This restores `thread_execution_surface_restored=true` for bounded R1
  control-plane routing only. `business_task_or_patrol_completed=false`: task
  028 was not re-dispatched and still has no expected return/blocker packet.
- The same patrol read
  `Results/coagent_gui/mworks_gui_sentinel_20260609_0510.json`, which reports
  `status=clean`, a visible `Sysplorer [教育版]` main window, helper/proxy
  windows, and no demo/login/authorization/license/crash matches. This is
  window-patrol context only, not permanent activation, live attach,
  `check_model`, `SimulateModel`, graphical/layout review, or controller
  evidence.
- PMO sync packet:
  `Results/agent_packets/returns/COAGENTOPS-PATROL-PMO-SYNC-20260609-0535-001.json`.
  It reports dispatch_needed scopes rather than direct business dispatch:
  ROS2 needs PMO route selection after 077, UE needs producer/capture/cleanup
  route materialization after 034, and MWORKS needs PMO scope/live-gate
  decision before 028 can be redispatched. No MWORKS/ROS2/UE live runtime,
  planner_ready, controller performance, mission success, final material
  acceptance, or closed_loop claim is made.

## 2026-06-09 CST - PMO Integrated ROS2 076 And Dispatched 077 Source Route Design

- PMO validated the formal ROS2 R1 076 return
  `RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-GROUNDING-SAME-RUN-PROBE-20260609-076`:
  JSON parsing passed and `check_department_packet_contract.py` returned
  `ok=true`. ROS2 R1 readback shows the 076 turn completed and returned the
  expected packet path, superseding the earlier PMO waiting-return observation.
- 076 is accepted only as one bounded headless/no-goal same-run output evidence
  probe. It consumed exactly one live probe, observed FAST-LIO output topics in
  `camera_init`, kept forbidden planner/controller topics absent, and cleaned
  up task-owned processes. Real `camera_init` to `map/world` grounding remains
  `blocked_absent`, so controller handoff remains blocked.
- PMO wrote integration packet
  `PMO-ROS2-076-SAME-RUN-GROUNDING-PROBE-INTEGRATION-20260609-001`, then
  created and validated strict source/static task packet
  `RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-GROUNDING-SOURCE-ROUTE-DESIGN-20260609-077`.
  JSON parsing, `check_agent_task_native_surface_gate.py --strict`, and
  `check_department_packet_contract.py` all passed before dispatch.
- PMO dispatched 077 to ROS2 R1 `019e9c72-ee74-79d1-b9fe-621d3c6fc99e` with
  `gpt-5.5`/`xhigh`; readback shows the 077 turn is `inProgress`. The board
  now marks ROS2 as `waiting_return` for 077. No planner_ready, controller
  handoff, runtime success, controller performance, mission success, UE runtime
  ack, MWORKS simulation success, or closed_loop claim is made.

## 2026-06-09 CST - PMO Observed ROS2 076 Evidence But Still Awaits Formal Packet

- PMO rechecked ROS2 R1 task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-GROUNDING-SAME-RUN-PROBE-20260609-076`.
  The target turn is still `inProgress` and has reached return-writing
  commentary; the expected 076 return and blocker packet paths are both still
  absent at this PMO observation point.
- The 076 evidence directory already contains preliminary artifacts from one
  consumed headless/no-goal probe: FAST-LIO outputs are still in `camera_init`,
  forbidden planner/controller topics are absent, cleanup is clean, and real
  `camera_init` to map/world grounding remains `blocked_absent`. PMO has not
  integrated this as a ROS2 department result because the formal return/blocker
  packet is still pending.
- Board state remains `waiting_return` for ROS2. PMO must not duplicate-dispatch
  076 and must not claim planner_ready, controller handoff, runtime success,
  controller performance, mission success, or closed_loop from these
  preliminary artifacts. Durable PMO control-plane observation packet:
  `PMO-ROS2-076-EVIDENCE-OBSERVED-AWAITING-RETURN-20260609-001`.

## 2026-06-09 CST - PMO Dispatched ROS2 076 Same-Run Grounding Probe

- PMO created and validated task packet
  `RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-GROUNDING-SAME-RUN-PROBE-20260609-076`
  for ROS2 R1. JSON parsing, `check_agent_task_native_surface_gate.py
  --strict`, and `check_department_packet_contract.py` passed before dispatch.
  The task authorizes at most one bounded headless no-goal ROS2/FAST-LIO
  same-run grounding evidence probe after the 075 static contract; it forbids
  foreground RViz/manual GUI, planner/controller/setpoint publication, UE,
  MWORKS, fake TF/map/pointcloud, frame/extrinsic/source edits, and Git.
- PMO dispatched 076 to current ROS2 R1
  `019e9c72-ee74-79d1-b9fe-621d3c6fc99e` with `gpt-5.5`/`xhigh`; readback
  shows the new turn is `inProgress`. The board now marks ROS2 as
  `waiting_return`. No planner_ready, controller handoff, runtime success,
  controller performance, mission success, or closed_loop claim is made.

## 2026-06-09 CST - PMO Integrated ROS2 074 And Current Static Returns

- PMO validated ROS2 R1 return
  `RFLY-MOSIM-ROS2-RUNTIME-B1-HEADLESS-LIVE-EVIDENCE-BUNDLE-20260608-074`:
  JSON parse passed and `check_department_packet_contract.py` returned
  `ok=true`. The result is accepted only as one bounded headless no-goal
  FAST-LIO output evidence bundle. It reports LiDAR/IMU source observations,
  FAST-LIO `/Odometry`, `/cloud_registered`, `/path` output evidence,
  forbidden planner/controller topic absence, cleanup evidence, and a validator
  summary. It does not prove planner readiness, controller handoff, runtime
  success, mission success, foreground RViz acceptance, localization quality,
  or closed loop. Controller handoff remains blocked by absent real same-run
  `camera_init` to map/world grounding.
- PMO rechecked the current static-only returns for MWORKS R1 027 and UE 032
  with `check_department_packet_contract.py`; both returned `ok=true` after
  semantic-boundary repair. MWORKS R1 027 remains static Modelica
  source-surface materialization only. UE 032 remains source-static wiring
  evidence only, not UE runtime ack.
- Current MWORKS routing is still recovery-pending: R1 028 and the reopened
  R2 025 recovery blockers have no current supersede return. Do not redispatch
  those live/review business tasks until same-thread validation restores the
  latest incidents.
## 2026-06-08 CST - PMO Integrated CoAgentOps R1 027 Dispatch And R2 025 Recovery

- CoAgentOps performed one bounded P0 static-only dispatch after idle-thread
  recovery:
  `PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-COMMAND-MAPPER-FORMAL-SOURCE-SURFACE-20260608-027`
  to MWORKS R1 `019e9be5-334b-76b1-93f9-8b02caebf376`. PMO readback shows the
  R1 027 turn is `inProgress` with agent commentary, so it must not be
  duplicate-dispatched or treated as dead.
- CoAgentOps also superseded the stale MWORKS R2 025 dispatch-surface failure:
  `Results/agent_packets/returns/COAGENTOPS-MWORKS-R2-025-DISPATCH-SURFACE-RECOVERY-SUPERSEDE-20260608-001.json`.
  This restores the same R2 visible thread execution surface only
  (`thread_execution_surface_restored=true`); it does not start or complete the
  R2 025 static review (`business_task_or_patrol_completed=false`).
- Ledger state was already aligned: R1 Batch A 025 is completed static
  aggregation, R2 025 is recovered-but-business-unstarted, and R1 027 is
  dispatched/in progress. Live MWORKS GUI/MCP/check_model/SimulateModel,
  graphical acceptance, controller performance, runtime ack, planner_ready,
  mission success, and closed_loop remain unclaimed.

## 2026-06-08 CST - PMO Integrated UE 030, MWORKS R1 025, And ROS2 071

- UE completed 030:
  `Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SOURCE-GATE-20260608-030.json`.
  The output is a source-static UE receiver surface for future authoritative
  `mosim.ue_command_echo.v1` ingestion plus checker/test evidence. It does not
  prove live UE runtime ack, MWORKS downlink, ROS2 runtime echo, final UI
  acceptance, planner readiness, controller performance, mission success, or
  closed loop.
- MWORKS R1 completed 025:
  `Results/agent_packets/returns/PMO-MWORKS-R1-MOSIMQUAD-ROTOR-ACTUATOR-CORE-FORMAL-SOURCE-SURFACE-20260608-025.json`.
  The output is static Modelica source-surface materialization for
  `MoSimQuadrotorModel.Dynamics.RotorActuatorCore`; it added the independent
  `.mo` surface, preserved legacy `QuadrotorExperiments` behavior, and updated
  static checkers/tests. It does not prove live MWORKS `check_model`,
  `SimulateModel`, graphical acceptance, parameter truth, controller
  performance, planner readiness, or closed loop.
- ROS2 R1 completed 071:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-LIDAR-IMU-ODOM-20HZ-SYNC-CONTRACT-STATIC-GATE-20260608-071.json`.
  The output is a source/static synchronization contract: LiDAR 20 Hz remains
  replay-time adaptation, IMU timing is 200 Hz, FAST-LIO output facts are
  inherited in `camera_init`, and the controller 20 Hz handoff remains
  static-only pending frame-policy and bounded runtime validation.
- PMO next actions: dispatch UE 031 build-only compile gate for the new 030 C++
  source, dispatch MWORKS R1 026 static wrapper-source surface formalization,
  and keep live MWORKS/R2 graphical review blocked until a true main
  MWORKS/Sysplorer window plus no-start attach route is validated.

## 2026-06-08 CST - CoAgentOps Notified MainPMO Of Idle And Blocked P0 Queue

- User corrected the patrol failure mode: detecting idle, blocked, review-needed,
  or recovery-needed active-visible threads is not useful unless CoAgentOps
  notifies MainPMO so PMO can dispatch, request manual review, or decide a
  dependency recovery path. CoAgentOps sent a native thread sync to MainPMO with
  the current priority queue.
- Current queue integration: MWORKS R1 024 has completed a static-only runner
  hardening return, but future live MWORKS validation still waits for the
  MWORKS main-window/no-start attach dependency; MWORKS R2 023 completed
  static-only organization audit but live graphical/layout review remains under
  the same dependency; ROS2 070 remains a foreground RViz review/approval
  surface; UE 029 is source-static validator evidence only and needs PMO
  choice of live runtime gate versus further source-static hardening.
- Blocker/control packet:
  `Results/agent_packets/blockers/COAGENTOPS-HEARTBEAT-P0-DISPATCH-QUEUE-NOTIFIED-20260608-1716.json`.
  This is control-plane notification evidence only; it does not claim MWORKS
  live load/check/simulation, ROS2 RViz acceptance, UE runtime ack, controller
  performance, planner_ready, mission success, final material acceptance, or
  closed_loop.

## 2026-06-08 CST - CoAgentOps 15:46 Patrol Reconfirmed MWORKS Main Window Missing

- CoAgentOps closed the 15:46 heartbeat with fresh read-only evidence. PMO and
  CoAgentOps execution surfaces are active; no new start-turn or agent-loop
  failure was found, so no Codex++ restart was triggered.
- Current MWORKS evidence still shows no true MWORKS/Sysplorer/Syslab main
  window: sentinel `target_window_count=0`,
  `license_state_hint=no_mworks_window_observed`, window-management
  `window_count=0`, and no `mworks.exe`/true Sysplorer main-window handle in
  the process inventory. This is not a visible login/license/authorization or
  GUI-error incident, but it keeps MWORKS R1/R2 live and graphical review work
  blocked by the open main-window/no-start-attach dependency.
- Dispatch readiness remains material: UE is routable and idle after 028, so
  PMO should decide whether to dispatch the next bounded command-echo runtime
  probe or a source-static hardening follow-up. No duplicate email was sent for
  the unchanged MWORKS missing-window condition.
- Blocker:
  `Results/agent_packets/blockers/COAGENTOPS-HEARTBEAT-P0-MWORKS-MAIN-WINDOW-MISSING-20260608-0746.json`.
  No MWORKS/ROS2/UE live runtime, restart, WeChat notification, `check_model`,
  simulation, graphical acceptance, controller performance, planner_ready,
  runtime ack, mission success, final material acceptance, or closed-loop
  claim is made.

## 2026-06-08 CST - CoAgentOps 15:34 Patrol Confirmed MWORKS Main Window Still Missing

- CoAgentOps closed the 15:34 heartbeat with current read-only window
  evidence. PMO and CoAgentOps execution surfaces are active, so the stale
  CoAgentOps restart-pending blocker remains superseded at the thread layer.
- Current MWORKS patrol evidence still shows no true MWORKS/Sysplorer/Syslab
  main window: sentinel `target_window_count=0`,
  `license_state_hint=no_mworks_window_observed`, window-management
  `window_count=0`, and only `syslab-mcp-server-win64` processes without main
  window handles. This is not a visible login/license/authorization/GUI-error
  incident, but it keeps MWORKS R1/R2 live work and graphical review
  `idle_blocked_by_open_dependency`.
- Dispatch readiness note: UE is routable and idle after 028, so PMO should
  decide whether to dispatch the next bounded command-echo runtime probe or a
  source-static hardening follow-up. ROS2 R1 remains
  `idle_waiting_review_or_approval`. No duplicate user notification was sent
  for the unchanged MWORKS missing-window condition.
- Blocker:
  `Results/agent_packets/blockers/COAGENTOPS-HEARTBEAT-P0-MWORKS-MAIN-WINDOW-MISSING-20260608-0734.json`.
  No MWORKS/ROS2/UE live runtime, restart, WeChat notification, `check_model`,
  simulation, graphical acceptance, controller performance, planner_ready,
  runtime ack, mission success, final material acceptance, or closed-loop
  claim is made.

## 2026-06-08 CST - PMO Re-activated CoAgentOps Patrol And Pinned Two Workflow Boundaries

- PMO found the single CoAgentOps 10-minute automation was `PAUSED`, which is a
  patrol outage under current rules. PMO restored the same automation id to
  `ACTIVE` instead of creating a duplicate.
- User clarified that the durable fix is a clear workflow, not repeated
  constraint prose. PMO pinned two hard boundaries in canonical docs: routable
  idle active engineering threads with ready P0 work must become
  `dispatch_needed`, and sparse email in dead-thread recovery is not a finish
  state. If authorized restart can run, the recovery owner continues restart in
  the same run; otherwise it writes a blocker naming the missing surface.
- Packet:
  `Results/agent_packets/returns/PMO-COAGENTOPS-WORKFLOW-BOUNDARY-ACTIVE-PATROL-20260608-003.json`.
  This is control-plane workflow and automation-state correction only; it does
  not claim MWORKS, ROS2, UE, controller, planner, runtime, graphical, or
  closed-loop evidence.

## 2026-06-08 CST - PMO Simplified CoAgentOps Patrol Into Executable Workflow

- User corrected that the automation should not grow through repeated
  constraint prose. PMO updated the same CoAgentOps 10-minute automation in
  place as a seven-step workflow: scan active threads, classify control-plane
  surfaces, execute recovery, report dispatch readiness, patrol MWORKS windows,
  integrate engineering packets, and output NOTIFY/DONT_NOTIFY.
- The workflow keeps the two required hard actions: routable idle engineering
  departments with ready P0 work must be returned as `dispatch_needed`, and a
  restart-pending dead-thread recovery must continue after sparse email when
  the authorized restart surface is available. If the next step cannot run,
  CoAgentOps must write a blocker naming the missing tool, permission, or
  evidence.
- Return packet:
  `Results/agent_packets/returns/PMO-COAGENTOPS-PATROL-WORKFLOW-PROMPT-SIMPLIFICATION-20260608-002.json`.
  This is control-plane workflow cleanup only; it does not claim any MWORKS,
  ROS2, UE, controller, planner, runtime, graphical, or closed-loop evidence.

## 2026-06-08 CST - PMO Fixed CoAgentOps Idle Dispatch And Restart Closure Semantics

- User identified that CoAgentOps patrol still treated idle active departments
  as quiet health and did not reliably turn them into PMO scheduling actions.
  PMO updated the existing automation `mosim-wechat-gateway-hourly-health` in
  place, preserving the automation id, target thread, ACTIVE status, and
  10-minute cadence.
- The automation now requires every active-visible engineering thread to report
  `dispatch_readiness` separately from control-plane `state_class`:
  `busy_in_progress`, `idle_needs_dispatch`,
  `idle_blocked_by_open_dependency`, `idle_no_ready_task`, or
  `idle_waiting_review_or_approval`. Routable idle MWORKS R1 and R2, ROS2 R1,
  UE, or Sunray tasks with a ready next P0 gate must be returned as
  `dispatch_needed` for PMO with suggested task scope and expected engineering
  output.
- The same update clarifies P0 restart fail-close: a sparse email is only the
  pre-restart notification and audit step, not recovery completion. If a PMO or
  CoAgentOps recovery packet remains restart-pending and there is no explicit
  deferral, the healthy owner must continue the authorized Codex++ restart route
  and leave post-restart validation for the next healthy turn.
- Return packet:
  `Results/agent_packets/returns/PMO-COAGENTOPS-IDLE-DISPATCH-RESTART-CLOSURE-PROMPT-FIX-20260608-001.json`.
  This is automation semantics correction only. No MWORKS, ROS2, UE,
  controller, planner, graphical acceptance, runtime ack, mission success, or
  closed-loop evidence is claimed.

## 2026-06-08 CST - CoAgentOps Closed PMO Start-Turn Failure Recovery And Hardened Patrol

- The PMO start-turn incident is now classified as a CoAgentOps patrol
  fail-close miss, not a special user-authorization event. During the
  10-minute patrol, PMO was readable but its latest turn was `interrupted`;
  the patrol should have classified/probed that state before the user reminded
  CoAgentOps. A minimal start-turn probe then failed before turn start with
  `agent loop died unexpectedly`.
- This is not primarily a CoAgentOps automation cadence failure: the
  `mosim-wechat-gateway-hourly-health` heartbeat did enter CoAgentOps and
  execute native checks. The miss was the patrol's initial classification: a
  readable PMO thread with an interrupted latest turn should have been probed
  or classified as a P0 control-plane risk, not treated as routable because it
  was readable and had older closeout evidence.
- CoAgentOps wrote blocker
  `Results/agent_packets/blockers/COAGENTOPS-PMO-START-TURN-FAILURE-INCIDENT-20260608-001.json`
  and sent sparse Chinese email audit
  `Results/coagent_gateway/email/email_alert_20260608_131310.json`.
- Per existing fail-close policy, email was only the pre-restart audit; it was
  not recovery completion. The restart helper evidence
  `Results/codex_watchdog/codex_outer_watchdog_check_20260608_132117.json`
  reports `restart_requested=true` and `restart_result.ok=true` through UI
  Automation. A later PMO turn `019ea5ae-d064-7753-8f41-5ef76d40ea44` started
  and produced agent output, so the same PMO thread execution surface is
  supersedingly restored. Business-task completion for that PMO turn remains
  separate and must be judged from its final packet/output.
- Current routing decision: PMO is no longer quarantined solely by the old
  start-turn blocker. Future CoAgentOps patrols must treat latest
  `interrupted`/`systemError`/completed-without-agent-output mainline turns as
  P0 control-plane risks and must continue from email audit to the
  policy-mandated Codex++ restart route unless there is an explicit deferral.
- Same patrol side evidence: read-only MWORKS window scripts saw no
  MWORKS-like target window and no login/license/authorization/error markers.
  This is not `window_patrol_clean` because a true main MWORKS/Sysplorer
  window was not proven.

## 2026-06-08 CST - PMO Superseded CoAgentOps Self-Dead Blocker After Start-Turn Recovery

- PMO rechecked the single CoAgentOps automation after the user asked whether
  prior incidents are covered. The automation is configured as ACTIVE at a
  10-minute cadence and its prompt now explicitly covers the historical failure
  classes: MWORKS activation/login/license/authorization loss, extra or blank
  MWORKS/Sysplorer windows from bad live attach, provider/network/review or
  approval surfaces, visible-thread dead/half-dead dispatch surfaces, and
  idle/no-progress turns that lack expected packet/no-op evidence.
- The coverage is configuration-level only at this moment. A current PMO
  minimal no-op probe to CoAgentOps failed before turn start with
  `agent loop died unexpectedly`, while `read_thread` still works. PMO wrote
  blocker
  `Results/agent_packets/blockers/PMO-COAGENTOPS-SELF-DEAD-START-TURN-FAILURE-20260608-001.json`.
- PMO sent the required sparse Chinese email alert and recorded audit
  `Results/coagent_gateway/email/email_alert_20260608_122533.json`. CoAgentOps
  was initially quarantined for production routing.
- User corrected the recovery criterion: if the target subthread can start a
  turn and produce agent output, that proves restart/thread execution-surface
  recovery; exact no-op text is not the only valid proof unless the narrow
  probe specifically asks for it. PMO re-read CoAgentOps and found turn
  `019ea583-efd4-7343-877b-0aeb916a03d3` completed with agent output and the
  explicit ACK `coagentops_post_blocker_reprobe_received_20260608_1235`.
  Superseding return:
  `Results/agent_packets/returns/PMO-COAGENTOPS-SELF-DEAD-START-TURN-RECOVERY-SUPERSEDE-20260608-001.json`.
- Current routing decision: CoAgentOps execution surface is restored for bounded
  control-plane routing. Patrol completion and MWORKS/ROS2/UE engineering
  claims still require their own packets/evidence.
- No replacement thread was created. No MWORKS/ROS2/UE runtime, model,
  controller, planner, graphical acceptance, runtime ack, mission success, or
  closed-loop evidence is claimed from this control-plane audit.

## 2026-06-08 CST - PMO Deleted Self-Blocking Heartbeat And Folded Patrol Into CoAgentOps

- User identified that a thread-attached PMO automation cannot enter while the
  current PMO turn is still running, so it cannot be a reliable P0 patrol during
  long PMO work. PMO deleted `mosim-pmo-p0-long-run-followup`.
- PMO folded the deleted heartbeat's duties into the CoAgentOps automation:
  active-visible scan, UE/Sunray/MWORKS/ROS2/CoAgentOps return/blocker
  integration, ledger/PROGRESS updates, MWORKS activation/window patrol,
  graphical-review routing to MWORKS R2, explicit semantic-boundary state
  classes, and sparse-email incident handling.
- Current observed CoAgentOps automation is `MoSim CoAgentOps 状态与主线巡检`
  on `mosim-wechat-gateway-hourly-health`, ACTIVE, targeting CoAgentOps. Its
  cadence is now 10 minutes after the user-side cadence adjustment; PMO did not
  overwrite that cadence.
- PMO remains the interactive escalation owner if CoAgentOps itself cannot
  start/complete turns. Recovery then happens from a live PMO/user-triggered
  turn, not from a deleted PMO heartbeat. This is control-plane cleanup only; no
  MWORKS/ROS2/UE runtime or model evidence is claimed.

## 2026-06-08 CST - PMO Tightened CoAgentOps Automation Prompt Boundaries

- User corrected that automation prompts must be compact but not ambiguous.
  PMO updated the existing single CoAgentOps automation prompt in place:
  the id, 10-minute cadence, target thread, and ACTIVE state are confirmed, and
  the prompt now explicitly defines healthy versus blocked thread states,
  approval/review/provider surfaces, MWORKS main-window versus helper-window
  health, allowed helper/error cleanup, forbidden main/login/license/auth
  closures, and email-only notification.
- PMO added the reusable rule to `AGENTS.md`,
  `Docs/Workflows/new_conversation_context.md`, and
  `Docs/Workflows/coagent_meta_maintenance.md`: automations should not become
  policy manuals, but they must include enough decision boundary to survive
  context compression.
- This is control-plane cleanup only. No MWORKS/Sysplorer/Syslab operation,
  WeChat, thread creation, cadence change, MWORKS model edit, ROS2/UE runtime,
  or simulation/controller evidence is claimed.

## 2026-06-08 CST - PMO Integrated 021/070/027 And Closed Current P0 Heartbeat

- Active visible department check found no current dead-thread recovery that
  needs user action: CoAgentOps is readable/idle after its MWORKS review
  automation sync; MWORKS R1/R2, ROS2 R1, and UE are idle after their latest
  return/blocker packets; Sunray/PBR remains frozen after the user-accepted
  DAE-derived 005 baseline.
- MWORKS R2 021 is accepted as a corrected static closeout: the previous R2
  017 unresolved `DynamicsUpgrade` rows were a static parser/index false
  positive around hidden sibling `.mo` implementation classes. 021 made no
  model-source changes and does not prove live MWORKS package-browser,
  graphical layout, `check_model`, `SimulateModel`, controller performance,
  runtime ack, or closed loop.
- ROS2 R1 070 returned a precise blocker before foreground RViz review. It
  inherits 068 headless TF/output-topic facts and 069 static output-only RViz
  route repair, but it did not start ROS2/RViz2/FAST-LIO and did not consume a
  live probe. A future foreground review needs a cleared GUI/approval route.
- UE 027 is accepted as a source-static runtime-readiness gate: checker/tests
  classify 024/025/026 as source/build-prep evidence and preserve that live
  authoritative command echo ack is still not claimable without a future live
  producer/transport/capture gate.
- PMO updated the task ledger rows for 021, 070, and 027 and wrote closeout
  packet `Results/agent_packets/returns/PMO-P0-LONG-RUN-FOLLOWUP-INTEGRATION-20260608-001.json`.
  No WeChat route, Sunray/PBR work, live MWORKS operation, ROS2 foreground GUI
  launch, UE runtime/editor launch, or new department dispatch was performed.

## 2026-06-08 CST - PMO Routed MWORKS Graphical Review To R2 And Updated CoAgentOps Automation

- User clarified that MWORKS graphical simulation/result, wiring/layout, Smart
  Layout, and animation review is a review responsibility rather than repeated
  activation patrol work. Ordinary review should use the now DPI-aware
  full-window background screenshot route plus concrete observations; activation,
  login, authorization, license, hidden-login-pane, and GUI-error acceptance
  still require foreground or maximized target main-window evidence.
- PMO updated the historical automation id `mosim-wechat-gateway-hourly-health`
  through Codex App native `automation_update`: the user-facing name is now
  `MoSim CoAgentOps 状态与主线巡检`. The old id remains only as a stable internal
  automation id, not as a WeChat gateway task.
- The later PMO heartbeat was deleted after the user identified same-thread
  automation insertion blocking. Future MWORKS graphical/layout/result-review
  routing semantics now live in the single CoAgentOps 10-minute automation and
  canonical docs, not in a PMO heartbeat.
- Durable rules were updated in `AGENTS.md`,
  `Docs/Workflows/new_conversation_context.md`,
  `Docs/Workflows/agent_orchestration.md`,
  `Docs/Workflows/coagent_meta_maintenance.md`, and this ledger/progress pair.
  CoAgentOps was sent a short sync packet. No MWORKS model, runtime, controller,
  ROS2, UE, Blender, or CoAgent runtime/schema/transport work was changed by
  this rule sync.

## 2026-06-08 CST - PMO Closed Hidden MWORKS Warning Window And Resumed Dispatch

- PMO closed one hidden `mworks.exe` window titled `内存警告` with a targeted
  `WM_CLOSE`. The reusable MWORKS/Sysplorer main window was not closed,
  killed, restarted, or logged in again.
- A fresh sentinel recheck is `clean`: no visible demo, login, activation,
  authorization, license, crash-report, or memory-warning window is currently
  detected. The remaining MWORKS-like windows are the education-edition main
  window plus helper/proxy surfaces.
- This is window cleanup only. It is not activation acceptance, no-start MCP
  attach proof, `check_model`, `SimulateModel`, package-browser/layout
  acceptance, controller performance, planner readiness, runtime ack, mission
  success, or closed-loop evidence.
- PMO is resuming non-conflicting dispatch: MWORKS R2 static corrected
  closeout, ROS2 R1 bounded no-goal RViz output gate, UE source/static runtime
  readiness gate, and CoAgentOps patrol/DPI screenshot sync. Live MWORKS model
  work remains blocked until the no-start attach route is validated.
- 2026-06-08 10:40 CST update: PMO re-ran the MWORKS GUI sentinel after
  dispatch; it stayed clean with no matched demo/login/activation/
  authorization/license/crash/memory-warning blocker. The three prepared
  visible-thread tasks were accepted by native dispatch transport. Engineering
  completion still requires each target department's return/blocker packet.

## 2026-06-08 CST - PMO Closed MWORKS Multi-Window Source Audit

- PMO inspected the current MWORKS/Sysplorer process/window state after the
  user asked where the many windows came from. Current live evidence shows one
  real `mworks.exe` root process, started on 2026-06-07 21:39 CST, plus normal
  helper/proxy/docsearch/acp/CEF subprocesses and helper windows.
- The current maximized main-window screenshot shows the Sysplorer start page
  in education edition with no visible login, activation, authorization, demo,
  or crash-report dialog. This is only visual window-state evidence; education
  edition text is still not activation proof.
- Root-cause split: current window count is mostly helper/proxy surfaces;
  historical extra main-window drift came from `session_manager(action=health)`
  starting new MWORKS/Sysplorer sessions instead of proving reuse; the old
  background screenshot script could also restore/maximize helper/proxy
  windows and make the desktop look polluted.
- PMO wrote closeout packet
  `Results/agent_packets/returns/PMO-MWORKS-MULTI-WINDOW-SOURCE-AUDIT-20260608-001.json`
  and hardened the sentinel/capture scripts so helper windows are classified
  separately and `capture_window_background.ps1 -Maximize` only maximizes the
  target main window by default.
- Live MWORKS R1/R2 work remains blocked until the no-start attach route is
  explicitly approved, implemented, and validated. Static file-only MWORKS
  tasks may continue with `live_mworks_touched=false`. No `check_model`,
  `SimulateModel`, package-browser, layout acceptance, controller performance,
  planner readiness, runtime ack, mission success, or closed-loop evidence is
  claimed from this audit.

## 2026-06-08 CST - PMO Corrected MWORKS R2 Provider/Review-Surface Misclassification

- User confirmed all current subthreads are normal and clarified that the
  MWORKS R2 017 incident had visible provider/API `502 Bad Gateway` plus a
  review/approval UI, not a durable dead-thread or MWORKS business-domain
  failure.
- PMO wrote a superseding correction packet and updated the durable rules:
  provider 502, reconnect banners, generated-file review, `审核`/review
  buttons, and approval buttons must be classified as
  `provider_gateway_or_pending_review` or `approval_pending_or_ui_blocked`
  before dead-thread recovery.
- MWORKS R2 may receive bounded static model-organization dispatches again.
  The malformed R2 017 return is still not accepted as completed engineering
  evidence; it needs corrected static closeout or PMO takeover.
- Live MWORKS package-browser, layout, `check_model`, and `SimulateModel`
  remain blocked until the no-start attach route is approved and validated.
  This correction does not prove live MWORKS activation, graphical acceptance,
  simulation, controller performance, planner readiness, runtime ack, or
  closed_loop.

## 2026-06-08 CST - PMO Restored ROS2 R1 Routing After Approval-Surface Correction

- User clarified that the ROS2 R1 post-069 issue was a Codex App permission or
  manual approval surface, not a simple long no-packet stall.
- PMO re-read ROS2 R1 and found the post-069 routing-health no-op turn
  completed with the exact expected reply string. The older CoAgentOps blocker
  is now superseded by a PMO restore packet.
- ROS2 R1 may resume bounded production dispatches with explicit packets and
  evidence gates. 069 remains PMO-takeover static repair only and must not be
  re-dispatched.
- Future `waitingOnApproval` incidents should use Windows MCP foreground or
  screenshot confirmation when practical before no-packet/dead-thread
  classification.

## 2026-06-08 CST - PMO Integrated MWORKS R1 020 Static Integrity Gate

- MWORKS R1 020 returned completed and PMO verified JSON parsing, department
  packet contract, MWORKS static live gate, evidence JSON files, and scoped
  diff check.
- 020 confirms the current `MoSimQuadrotorModel.Dynamics` formal surface is
  statically coherent after 017/018/019: all 12 formal Dynamics entries resolve
  through `QuadrotorExperiments.DynamicsUpgrade` aliases to project-owned
  implementation files, and the Parameters provenance package remains
  package/order consistent.
- 020 made no `.mo` or `package.order` source repair. It wrote static evidence
  for alias resolution, package/order integrity, default-behavior preservation,
  parameter-provenance consistency, changed files, and the future live
  validation queue.
- This is static source/package/order/provenance evidence only. It is not live
  MWORKS `check_model`, `SimulateModel`, result viewer, package-browser,
  graphical/layout acceptance, identified Sunray150 parameter truth,
  controller performance, runtime ack, mission success, or closed_loop.
- Current P0 routing status: MWORKS live validation still waits for approved
  reusable no-start attach; MWORKS R2 remains quarantined; ROS2 R1 is restored
  for bounded packeted dispatch after approval-surface correction; Sunray/PBR
  remains frozen on the user-accepted 005 baseline.

## 2026-06-08 CST - PMO Corrected ROS2 R1 Approval-State Classification

- User clarified that the ROS2 R1 post-069 problem was a Codex App permission
  or manual approval surface, not simply a long no-packet stall.
- PMO updated the current coordination rule: `waitingOnApproval` must be
  treated as `approval_pending_or_ui_blocked` first, with bounded Windows MCP
  foreground/screenshot confirmation when practical.
- ROS2 R1 production routing stays paused until the approval surface is cleared
  and a fresh expected packet/no-op validates the thread, but it must not be
  restarted or replaced solely because the approval prompt blocked the closeout.
- This correction does not change ROS2 069 engineering evidence: it remains a
  static RViz output launch-route repair only, with no TF/RViz readiness,
  planner_ready, runtime success, mission success, or closed_loop claim.

## 2026-06-08 CST - PMO Integrated UE 026 And Tracking MWORKS R1 020

- UE 026 returned completed and PMO verified JSON parsing, department packet
  contract, and scoped diff check. The refreshed UE boundary checker/tests now
  reflect UE 024 source-level future authoritative downlink handoff plus UE
  025 compile-only evidence while preserving zero runtime-ack leaks.
- UE 026 remains source-static checker/test/evidence refresh only. It is not a
  live UE runtime ack, MWORKS downlink, ROS2 runtime echo, final UI
  acceptance, planner/controller success, mission success, or closed_loop.
- MWORKS R1 020 has since returned completed and is integrated in the latest
  entry above.
- MWORKS R2 remains quarantined after the R2 017 systemError/control-plane
  blocker. ROS2 R1 routing is paused after the post-069 approval-state issue;
  do not dispatch production work until the permission surface is cleared and
  a fresh expected packet/no-op validates the thread.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline. The department reported the 006 repaint/overlay regression has
  been removed and the user requested no further Sunray150 texture/PBR edits.

## 2026-06-08 CST - PMO Integrated R2 017 Blocker And Prepared UE 026

- CoAgentOps returned a valid MWORKS R2 017 control-plane blocker. R2 remains
  quarantined because the visible thread reports `systemError`, the 017 turn
  did not provide a final expected packet-path reply, and the existing 017
  return-path JSON is contract-invalid (`status=blocked` without
  `blocker_summary`).
- PMO does not integrate R2 017 as completed engineering evidence. Static
  review indicates the 12 unresolved `DynamicsUpgrade` targets were a sibling
  `.mo` indexing false positive, but fixing that now belongs to PMO takeover or
  a future recovered R2 static-only redrive.
- ROS2 R1 is not treated as a simple no-packet stall after the user's
  correction: post-069 `waitingOnApproval` should be handled as a possible
  Codex App permission/manual approval surface before any dead-thread or
  restart classification. Do not dispatch ROS2 production work until the
  approval state is resolved and a fresh validation succeeds.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline. Do not continue material/PBR retuning unless the user explicitly
  reopens visual work.
- PMO prepared UE 026 as the safe parallel next step: refresh the older UE live
  echo receiver boundary checker/tests so they reflect the UE 024 source-level
  handoff and UE 025 compile-only evidence, without opening UE runtime or
  claiming runtime ack.
- UE 026 task packet passed JSON/native-surface/scoped-diff gates, was
  dispatched to UE with `gpt-5.5` / `xhigh`, and the target turn is
  `inProgress`. PMO sent one sparse Chinese progress email.

## 2026-06-08 CST - PMO Integrated UE 025 And Queued MWORKS R2 017

- UE 025 returned completed and PMO verified the department packet contract
  and scoped diff check. The project UE build script completed with exit code
  0 and was classified as `compile_pass_warning_only`; this is compile-only
  evidence for the UE 024 runtime echo downlink handoff, not a live runtime ack.
- CoAgentOps returned the ROS2 R1 post-069 routing-health blocker, but this
  older wording is superseded by the user's later correction: the observed
  `waitingOnApproval` state should be treated first as a Codex App
  permission/manual approval surface, not as a simple long no-packet stall.
  ROS2 R1 production routing remains paused until that approval state is
  cleared and a fresh validation succeeds.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline. The later 006 material pass is rejected rollback history and must
  not be used as a new visual-material baseline.
- MWORKS live tasks remain blocked by the attach-only/no-start approval
  boundary. Static MWORKS source/model organization may continue with
  `live_mworks_touched=false`; the next auxiliary task is an R2 static
  integrity gate over `MoSimQuadrotorModel` aliases and `package.order`
  surfaces after R1 017/018/019.
- PMO dispatched the R2 static integrity gate with `gpt-5.5` / `xhigh`,
  verified the target turn started, and sent one sparse Chinese progress email.

## 2026-06-08 CST - PMO Integrated UE 024 And ROS2 069 Static Prep

- UE 024 returned completed and PMO verified JSON parsing, department packet
  contract, and scoped diff check. The result is source/static build-prep for a
  future authoritative `mosim.ue_command_echo.v1` downlink handoff; it is not a
  UE runtime ack.
- ROS2 069 required PMO takeover: ROS2 R1 generated static script/test/evidence
  changes but did not write the expected return/blocker packet while its turn
  stayed `inProgress` with `waitingOnApproval`. PMO validated the static repair
  and wrote the 069 return packet.
- 069 now has an explicit `RVIZ_CONFIG` route so a future authorized live task
  can open the output-only `camera_init` RViz config for `/tf`,
  `/cloud_registered`, `/Odometry`, and `/path` without falling back to the old
  pointcloud profile. No live ROS2/RViz2/FAST-LIO probe was consumed.
- PMO wrote a separate CoAgentOps blocker/request for the ROS2 R1
  approval-stuck closeout behavior. The later user correction makes this an
  approval-surface/control issue first, not a ROS2 technical failure and not a
  dead-thread conclusion by itself.
- Sunray/PBR remains frozen on the accepted 005 DAE-derived Blender baseline.
  MWORKS live work remains blocked until the no-start attach route is approved,
  implemented, and validated; static MWORKS source work may continue.

## 2026-06-08 CST - PMO Integrated MWORKS 019 Parameter Provenance Layer

- MWORKS R1 019 returned completed and PMO verified JSON parsing, department
  packet contract, MWORKS department live-gate fields, scoped diff check, and
  static evidence files.
- 019 added a static `MoSimQuadrotorModel.Parameters` package and the
  `Sunray150ParameterProvenance` record-only layer. It separates accepted
  DAE/Blender rotor-center geometry from non-geometry YunZong/Gazebo/
  SDF-migration seed parameters.
- No dynamics behavior changed. Mass, inertia, motor constants, thrust/yaw
  coefficients, motor lag, drag, damping, and gyro values remain source-labeled
  seeds, not identified Sunray150 truth.
- This is not live MWORKS `check_model`, `SimulateModel`, result viewer,
  graphical/layout acceptance, parameter identification, controller
  performance, runtime ack, mission success, or closed_loop evidence.
- UE 024 and ROS2 069 have since been integrated above; Sunray/PBR remains
  frozen on the accepted 005 DAE-derived Blender baseline.

## 2026-06-08 CST - PMO Dispatched Next P0 Static/Prep Batch

- PMO dispatched UE 024, ROS2 069, and MWORKS R1 019 with `gpt-5.5` /
  `xhigh`, then verified with `read_thread` that all three target turns
  started and are `inProgress`.
- UE 024 is source/static/build-prep for the authoritative runtime command
  echo producer/downlink; it is not runtime ack.
- ROS2 069 is static RViz output launch-route repair; it does not consume
  another live probe and does not prove TF/RViz readiness.
- MWORKS R1 019 is static parameter-provenance organization for
  `MoSimQuadrotorModel`; it keeps `live_mworks_touched=false` and does not
  prove parameter identification, `check_model`, or simulation.
- Sunray/PBR remains frozen on the accepted 005 DAE-derived Blender baseline;
  no further visual material work should be dispatched unless the user
  explicitly reopens it.

## 2026-06-08 CST - PMO Integrated ROS2 068 Passive TF Observation

- ROS2 R1 068 returned completed and PMO verified JSON parsing, department
  packet contract, evidence summary JSON parsing, and scoped diff check.
- The single authorized passive/no-goal probe was consumed exactly once. It
  recorded dynamic TF edge `camera_init->body`, zero `/tf_static` transforms in
  the window, nonzero monotonic `/Odometry` and `/cloud_registered` in
  `camera_init`, nonzero `/path`, zero FAST-LIO loop-back, forbidden
  planner/setpoint topics absent, and clean cleanup.
- This is narrow passive TF/output-topic observation evidence only. It is not
  final TF/RViz readiness, localization quality, local-map quality,
  planner_ready, controller performance, runtime ack, mission success, true
  sensor capture, or closed_loop.
- The 067 launch-profile gap remains: output-only RViz config compatibility
  was checked headlessly, but RViz GUI was not started or accepted.
- Current P0 status: live MWORKS remains blocked pending explicit approval and
  validation of no-start attach implementation; UE runtime echo remains blocked
  pending an authoritative runtime echo producer/downlink; Sunray/PBR remains
  frozen on the accepted 005 DAE-derived Blender baseline and should not be
  retuned unless the user explicitly reopens visual material work.

## 2026-06-08 CST - PMO Integrated MWORKS 018 Optional Dynamics Layer

- MWORKS R1 018 returned completed and PMO verified JSON parsing,
  department packet contract, static MWORKS live gate, evidence JSON parsing,
  scoped diff check, and source review.
- 018 added a project-owned optional dynamics boundary layer for
  `MoSimQuadrotorModel.Dynamics`: rotor gyroscopic moment, body-frame
  translational drag, and angular damping are now represented as a separate
  wrapper layer over the 017 actuator-mapped dynamics surface.
- The new layer defaults to disabled and/or zero source-labeled coefficients,
  so the existing motor lag, `Ct*omega^2` thrust, yaw reaction torque,
  rotor-center `r x F` moment, actuator mapper, and mapped wrapper chain remain
  the default path.
- This is static Modelica source integration only. It is not live MWORKS
  `check_model`, `SimulateModel`, result viewer, graphical/layout acceptance,
  identified rotor inertia/drag/damping truth, controller performance,
  runtime ack, mission success, or closed_loop.
- Remaining P0 status: CoAgentOps 004 keeps live MWORKS routing blocked until
  no-start attach implementation is explicitly approved and validated; UE 023
  is blocked pending authoritative runtime echo producer/downlink; ROS2 R1 068
  is still in progress.

## 2026-06-08 CST - PMO Integrated UE 023 Runtime Echo Blocker

- UE 023 returned blocked and PMO verified JSON parsing, department packet
  contract, scoped diff check, and source/evidence boundaries.
- The one permitted UE runtime/editor command-echo probe was not consumed.
  Current UE code/scripts provide sender-only uplink plus source-static
  receiver/sink guards, but no authoritative runtime
  `mosim.ue_command_echo.v1` producer/downlink that can match a pending
  `mosim.ue_command.v1` request.
- UE 022 compile success remains valid as build-only evidence, but it is not
  runtime command ack. Future UE work needs a separately scoped live
  producer/receiver/evidence-capture gate before retrying the runtime probe.
- PMO must not accept build success, sender loopback, fixture/static rows,
  hand-written JSON, or frame/status receiver output as runtime ack.
- MWORKS R1 018 and ROS2 R1 068 are still in progress and are not yet PMO
  integrated. Sunray/PBR remains frozen on the accepted 005 baseline.

## 2026-06-08 CST - PMO Integrated CoAgentOps 004 Boundary Blocker

- CoAgentOps 004 returned blocked and PMO integrated the blocker into the
  active task ledger.
- The no-start MWORKS/Sysplorer attach route remains a technical design, not
  an implemented capability. Implementing `attach_existing` / `health_no_start`
  would expand the Sysplorer MCP/session-manager tool surface, and current
  `CoAgent/STATUS.md` still gates that expansion pending explicit approval.
- Live MWORKS R1/R2 routing remains blocked for `load_file`, `check_model`,
  `SimulateModel`, package-browser work, graphical layout review, and live
  validation until a separately approved implementation and no-start validation
  prove no new process/window/port drift.
- Static file-only MWORKS source work may continue with
  `live_mworks_touched=false`. Current P0 tasks MWORKS R1 018, ROS2 R1 068,
  and UE 023 remain in progress and are not yet integrated by PMO.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline; the user confirmed the latest rollback result and requested no
  further material edits.

## 2026-06-08 CST - PMO Dispatched And Confirmed Current P0 Batch Started

- PMO dispatched four current P0 tasks with `gpt-5.5` / `xhigh` and verified
  with `read_thread` that each target turn started and is `inProgress`:
  CoAgentOps 004 attach-only implementation-boundary decision, MWORKS R1 018
  optional gyro/drag/damping static Modelica layer, ROS2 R1 068 passive
  TF/RViz observation probe, and UE 023 runtime command-echo probe gate.
- This is dispatch/start evidence only. PMO has not yet integrated any 004,
  018, 068, or 023 return/blocker packet.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline after the department reported the 006 extra overlays/materials
  removed and the user requested no further material changes.
- Live MWORKS model gates remain blocked until the no-start reusable attach
  route is implemented or precisely blocked by CoAgentOps. Static MWORKS source
  work may continue with `live_mworks_touched=false`.
- No planner_ready, TF/RViz readiness, UE runtime ack, controller performance,
  mission success, final material acceptance change, or closed_loop claim is
  made from this dispatch batch.

## 2026-06-08 CST - PMO Integrated MWORKS 017 Static Actuator Mapper

- MWORKS R1 017 returned completed and PMO verified JSON parsing, department
  packet contract, static MWORKS live gate, static validation JSON parsing,
  scoped diff check, and source review.
- 017 added a project-owned `MoSimQuadrotorModel.Dynamics` actuator-command
  boundary: normalized actuator/throttle command saturation, signed visual
  rotor-speed mapping, and a mapped wrapper surface that feeds the existing
  rotor dynamics wrapper.
- The existing motor lag, `Ct*omega^2` thrust, yaw reaction torque, and
  rotor-center `r x F` moment core were preserved. The official
  `QuadrotorModel` baseline was not edited, and no live MWORKS/Sysplorer/
  Syslab GUI, MCP, `check_model`, or `SimulateModel` work was performed.
- Parameter boundary remains unchanged: hover command, max visual rotor speed,
  mass, lift coefficient, spin signs, motor lag, and related coefficients are
  source-labeled seeds, not identified Sunray150 PWM/RPM/ESC or physical
  truth.
- Remaining dynamics gaps are now rotor gyro moment, body drag, angular
  damping, fault/dynamic parameter layers, and later live validation once the
  no-start reusable MWORKS attach route is implemented and proven.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline; no further texture/PBR retuning is being routed.

## 2026-06-08 CST - PMO Integrated ROS2 067 Static TF/RViz Repair

- ROS2 R1 067 returned completed and PMO verified JSON parsing, department
  packet contract, static checker execution, evidence summary parsing, and
  scoped diff check.
- 067 added a default dry-run future operator runner, an output-only
  `camera_init` RViz config for `/tf`, `/cloud_registered`, `/Odometry`, and
  `/path`, plus a static regression checker for the contract.
- This consumed no live probe and did not run ROS2, RViz2, FAST-LIO, UE,
  MWORKS, planner, PositionCommand, 20 Hz adapter, goal, setpoint, fake point
  cloud/map/odom/TF, or UE truth shortcut.
- Remaining gaps are explicit: actual TF edge/tree content is still unproven,
  existing launch profiles are not yet mapped to the new output-only RViz
  config, and raw LiDAR RViz display still needs a real PointCloud2 source or
  conversion path.
- MWORKS R1 017 was later returned and integrated in the newest PMO entry
  above.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline; the 006 material pass remains rejected rollback evidence.

## 2026-06-08 CST - PMO Integrated CoAgentOps 003 Attach-Only Design

- CoAgentOps 003 returned completed and PMO verified JSON parsing,
  department packet contract, and scoped diff check.
- Static design conclusion: a safe reusable Sysplorer bind route should use
  `FindSysplorer()` plus explicit `ConnectSysplorer(port)` behind a future
  no-start action such as `attach_existing` or `health_no_start`, with
  before/after process, window, and port inventory.
- Current routing conclusion is still blocked for live MWORKS: the project
  tool surface does not yet expose the no-start bind action, and implementation
  is gated by CoAgent/MCP approval. MWORKS R1/R2 live MCP, package browser,
  graphical layout, `check_model`, and `SimulateModel` work remain paused.
- Static file-only MWORKS work may continue with `live_mworks_touched=false`.
  This is not live MWORKS readiness, graphical acceptance, controller
  performance, planner_ready, runtime ack, mission success, or closed loop.

## 2026-06-08 CST - PMO Dispatched Next Static P0 Batch

- PMO machine-validated and dispatched three next P0 tasks with `gpt-5.5` /
  `xhigh`: MWORKS R1 017 static actuator-command mapper implementation, ROS2
  R1 067 static TF/RViz observation repair, and CoAgentOps 003 static
  attach-only bind-route design/blocker.
- MWORKS 017 is static `.mo/package.mo` work only. It may add a project-owned
  normalized actuator/throttle mapper boundary but must not touch live
  MWORKS/Sysplorer/Syslab, `check_model`, `SimulateModel`, or official
  `QuadrotorModel` baseline.
- ROS2 067 is static script/config/test prep only. It must not run ROS2,
  RViz2, FAST-LIO, UE, planner, PositionCommand, 20 Hz adapter, publish fake
  data, or claim TF/RViz readiness.
- CoAgentOps 003 is static infrastructure design only. It must not run live
  MWORKS or edit CoAgent runtime; live MWORKS remains paused until a no-start
  attach/bind route is proven or precisely blocked.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline; no texture/PBR retuning is being dispatched.

## 2026-06-08 CST - PMO Integrated MWORKS 016 Audit And CoAgentOps 002 Blocker

- MWORKS R1 016 returned completed and PMO verified JSON parsing, department
  packet contract, static MWORKS live gate, gap/source-anchor JSON parsing, and
  scoped diff check.
- Current `MoSimQuadrotorModel.Dynamics` is a formal alias surface over
  `QuadrotorExperiments.DynamicsUpgrade`. The existing project-owned dynamics
  chain already covers motor lag, `Ct*omega^2` thrust, yaw reaction torque,
  rotor-center `r x F` moment, wrapper total force/torque, and an explicit
  physical wrench adapter.
- Remaining dynamics gaps are normalized actuator/PWM-to-speed mapping and
  saturation, rotor gyro moment, body drag, angular damping, and separate
  fault/dynamic parameter layers. Current mass, inertia, Ct/Cm, lag, drag,
  damping, and gyro values remain source-labeled seeds, not identified
  Sunray150 truth.
- CoAgentOps 002 returned blocked: `session_manager(action='probe')` can safely
  inspect an existing Sysplorer port without starting a process, but no
  bind-capable attach-only route was proven for live `load_file`,
  `check_model`, or simulation. Live MWORKS package-browser, graphical layout,
  `check_model`, and `SimulateModel` work remain paused; static file-only
  MWORKS work may continue with `live_mworks_touched=false`.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline. The rejected 006 material pass must not be resumed unless the user
  explicitly reopens visual material work.
- This is not live MWORKS simulation evidence, graphical/layout acceptance,
  identified parameter truth, controller performance, planner_ready, runtime
  ack, mission success, or closed_loop.

## 2026-06-08 CST - PMO Integrated ROS2 066 TF/RViz Prep Classification

- ROS2 066 returned completed and PMO verified JSON parsing, department packet
  contract, evidence summary parsing, and scoped diff check.
- 066 did not run a live probe. It used 065 evidence plus local launch/RViz
  files to classify the next observation-prep state: FAST-LIO outputs are
  monotonic and nonzero in `camera_init`, `/tf` topic presence was observed,
  but TF edge/tree content was not recorded.
- Main RViz config uses `camera_init`, which is consistent for output-only
  FAST-LIO observation. Review/manual configs still need a proven
  `ue_world <-> camera_init` transform and raw LiDAR display topic consistency;
  the task-required RViz replay script is currently missing.
- This is not TF/RViz readiness, localization quality, local-map quality,
  planner_ready, controller performance, runtime ack, mission success, or
  closed_loop.

## 2026-06-08 CST - PMO Integrated UE 022 Build-Only Compile Gate

- UE 022 returned completed and PMO verified JSON parsing, department packet
  contract, evidence summary parsing, and scoped diff check.
- The build-only command exited 0: no running UnrealEditor process was found
  before the build, UBT compiled the current experiment-console state component
  and linked the bridge editor DLL. The only classification caveat is a
  non-fatal Visual Studio compiler-version preference warning.
- This is compile evidence only. It does not prove live UE runtime ack,
  accepted UI, MWORKS/ROS2 live ack, planner_ready, controller performance,
  mission success, final UI acceptance, or closed_loop.
- MWORKS R1 016 and CoAgentOps 002 were integrated in the newest PMO entry
  above.

## 2026-06-08 CST - PMO Dispatched Next P0 Parallel Batch

- PMO created, machine-validated, and dispatched four next P0 tasks with
  `gpt-5.5` / `xhigh`: ROS2 066 TF/RViz observation-prep gate, UE 022
  build-only compile gate, MWORKS R1 016 static RflySim-like dynamics-gap
  audit, and CoAgentOps 002 MWORKS attach-only reusable-session route.
- Live MWORKS package-browser, `check_model`, `SimulateModel`, and layout
  review remain paused until CoAgentOps proves or precisely blocks the
  attach-only/no-start reusable session path. Static MWORKS file/model audit
  may continue with `live_mworks_touched=false`.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline. The rejected 006 whole-aircraft material pass must not be used as a
  new visual baseline or a reason to keep retuning materials.
- PMO is now waiting for department return/blocker packets from ROS2 R1, UE,
  MWORKS R1, and CoAgentOps; no planner_ready, TF/RViz readiness, runtime ack,
  controller performance, or closed_loop claim is made from dispatch alone.

## 2026-06-08 CST - PMO Integrated ROS2 065, UE 021, And MWORKS R2 015

- PMO verified all three previously running P0 department returns with JSON
  parsing, department packet contracts, scoped diff checks, and task-specific
  evidence gates.
- ROS2 065 completed the fixed-LiDAR-runtime FAST-LIO-only precondition gate.
  ROS2 R1 used a 065 evidence-local fixed LiDAR publisher/runner, proved it
  did not reuse the old 062/047 instrumented runner, passed the fixed-runtime
  binding and safety gates, consumed exactly one no-goal live probe, recorded
  monotonic Livox/IMU source topics, zero FAST-LIO callback/full-log loop-back,
  nonzero monotonic FAST-LIO outputs, forbidden planner/setpoint topics absent,
  and clean cleanup. This is still only fixed LiDAR runtime binding plus
  FAST-LIO-only precondition evidence, not true sensor capture, TF/RViz
  readiness, localization quality, planner_ready, controller performance,
  runtime ack, mission success, or closed_loop.
- UE 021 completed the command-echo runtime-prep source-static/build-prep gate.
  The state component now rejects non-authoritative or non-live echo rows as
  runtime ack and requires matching pending command identity, authoritative
  source/authority, timestamp, status, and no-pose-overwrite guards for future
  live accepted state. The 021 checker, focused pytest, regression checkers,
  and regression pytest passed. This is not live UE runtime ack, accepted UI,
  MWORKS/ROS2 live ack, planner readiness, or closed-loop evidence.
- MWORKS R2 015 completed the static MoSimQuadrotorModel classification and
  live-audit queue. It separates official `QuadrotorModel`, formal
  `MoSimQuadrotorModel`, legacy `QuadrotorExperiments`, and
  `QuadrotorControllerBlocks`, and records a 20-target future live
  package-browser/layout/wiring/check queue. This is static-only evidence with
  `live_mworks_touched=false`, not live package-browser, wiring,
  `check_model`, simulation, graphical acceptance, or controller evidence.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline. Do not restart broad texture/PBR tuning unless the user explicitly
  reopens visual material work.

## 2026-06-08 CST - PMO Integrated Sunray Final Freeze And Monitoring P0 Batch

- Sunray/PBR final closeout is integrated. The current Sunray150 visual
  baseline remains the user-reviewed 005 DAE-derived Blender route; the 006
  whole-aircraft repaint is rejected rollback evidence and must not be
  reintroduced.
- Sunray/PBR reported that the extra generated overlays/materials from the 006
  pass were removed and the user accepted the current Blender review effect.
  PMO recorded closeout packet
  `PMO-SUNRAY150-PBR005-FINAL-FREEZE-CLOSEOUT-20260608-002`. Do not dispatch
  more Sunray150 texture/PBR retuning unless the user explicitly reopens visual
  material work.
- ROS2 065, UE 021, and MWORKS R2 015 were later returned and integrated in
  the newest 2026-06-08 PMO progress entry above.

## 2026-06-08 CST - PMO Dispatched Next ROS2/UE/MWORKS R2 P0 Batch

- PMO created and validated three next-step task packets, then dispatched them
  with `gpt-5.5` / `xhigh`: ROS2 065 fixed-LiDAR-runtime FAST-LIO-only probe,
  UE 021 command-echo runtime-prep gate, and MWORKS R2 015 static
  MoSimQuadrotorModel classification/live-audit queue.
- ROS2 065 is the direct follow-up to 064: R1 must prove the live LiDAR
  publisher uses the 064 monotonic replay-clock fix before spending exactly one
  no-goal FAST-LIO-only probe. It must not reuse the old 062/047 runner unless
  rebuilt/replaced to prove the fixed path.
- UE 021 is source-static/build-prep only. It may prepare hooks/checkers/tests
  for a later authoritative `mosim.ue_command_echo.v1` runtime probe, but it
  must not open UE runtime, bind live sockets, implement final UI, or treat
  build/checker/sender success as runtime ack.
- MWORKS R2 015 is static-only with `live_mworks_touched=false`; it should
  classify the now-formal `MoSimQuadrotorModel` tree against the official
  baseline, legacy compatibility package, controller packages, and future
  live-audit batches. It must not touch MWORKS GUI/MCP, package-browser,
  `check_model`, or simulation.
- Sunray/PBR remains frozen on the user-accepted 005 DAE-derived Blender
  baseline. The 006 whole-aircraft material pass stays rejected rollback
  evidence; no further texture/PBR retuning is being dispatched.

## 2026-06-08 CST - PMO Integrated MWORKS 014 And UE 020

- PMO verified the Sunray/PBR freeze packet and CoAgentOps automation-update
  packet. Sunray visual material work remains frozen on the user-accepted 005
  DAE-derived Blender baseline; the 006 whole-aircraft pass remains rejected
  rollback evidence.
- CoAgentOps completed the 30-minute patrol automation tweak: after a
  MWORKS/Sysplorer/Syslab screenshot patrol, the target main window should be
  minimized when safe. Cadence/target/status were preserved.
- MWORKS R2 014 returned and PMO validated it with JSON parsing, department
  contract, static MWORKS gate, package/order evidence, and scoped diff check.
  `MoSimQuadrotorModel` Missions, Robustness, Planning, Formation, Support,
  and LegacyCompatibility now have explicit static wrapper/package surfaces
  and package.order files that preserve legacy `QuadrotorExperiments` load
  paths. This is static organization only, not live package-browser, wiring,
  `check_model`, simulation, controller performance, or closed-loop evidence.
- UE 020 returned and PMO validated JSON, department contract, source-static
  checker, focused pytest, and scoped diff check. It adds a seven-control,
  49-row reducer fixture matrix for future RflySim-like operator UI state
  handling, with no runtime-ack leaks. This is source-static fixture evidence
  only, not live UE runtime ack, accepted UI, planner_ready, or closed loop.
- ROS2 064 returned a formal blocker and PMO validated JSON parsing,
  department contract, the dense LiDAR contract pytest, the 064 static audit
  script, and scoped diff check. The static timestamp repair is complete:
  dense LiDAR replay now uses a run-local monotonic replay clock, the contract
  test rejects per-message `now()` header stamping, and an evidence-local
  monotonic IMU helper exists. No live FAST-LIO probe ran because the available
  062/047 runner could not prove it uses the fixed LiDAR runtime inside 064
  scope. This is static timestamp-discipline repair plus live-verification
  blocker only, not FAST-LIO success, TF/RViz readiness, planner_ready, runtime
  ack, controller performance, mission success, or closed-loop evidence.

## 2026-06-08 CST - PMO Integrated Latest Gates And Prepared Next Dispatch Batch

- Sunray/PBR is frozen at the user-accepted 005 DAE-derived Blender material
  baseline. The 006 whole-aircraft material pass is closed as rejected
  rollback evidence; PMO added
  `PMO-SUNRAY150-PBR005-FREEZE-006-ROLLBACK-INTEGRATION-20260608-001`
  as the control-plane freeze record. Do not dispatch more Sunray material/PBR
  retuning unless the user explicitly reopens it.
- ROS2 062 is blocked, not running: the one allowed no-goal FAST-LIO-only probe
  proved the IMU lifecycle coverage fix, but publisher/source stamps still
  regressed and FAST-LIO callback loop-back reproduced. ROS2 063 completed the
  static diagnosis and localized the next repair to publisher-side timestamp
  generation: replace per-message wall-clock stamps with one monotonic
  run-local replay clock.
- MWORKS R2 completed 013 static package-surface hygiene: four category
  `package.order` files were added where local visible entries already existed,
  while alias-only categories were left as planned migration work. This is
  static package-surface evidence only, not live package-browser, wiring,
  `check_model`, or simulation acceptance.
- PMO validated the next three P0 task packets and is dispatching them in
  parallel where resources do not conflict: ROS2 064 monotonic replay-clock
  repair/verification, UE 020 source-static control-state reducer fixture gate,
  and MWORKS R2 014 static alias-category migration planning. MWORKS 014 is
  explicitly `live_mworks_touched=false` and must not operate MWORKS GUI/MCP.

## 2026-06-08 CST - Sunray150 PBR 006 Reclassified As Regression Rollback

- User clarified the Sunray/PBR 005 DAE-derived Blender material route was
  already manually reviewed and acceptable as the current Sunray150 visual
  asset baseline.
- The later Sunray/PBR 006 whole-aircraft grey-CAD material pass is not an
  accepted optimization route. Treat it as a regression/rollback incident and
  do not continue broad texture/PBR tuning unless the user explicitly reopens
  material work.
- PMO verified rollback evidence:
  `Results/unreal_scene_mapping/sunray150_pbr_whole_aircraft_grey_cad_realism_20260607_006/verify_006_revert_no_pbr006.json`
  reports `pbr006_object_count=0`, `pbr006_material_count=0`, and `ok=true`.
  The older 006 contact sheet, material manifest, and completion packet remain
  rejected experiment/control-plane history, not accepted visual evidence.
- Current Sunray route is closed/frozen: preserve the 005-approved DAE-derived
  Blender asset. Future asset tasks should focus only on explicitly requested
  bounded packaging/review display/UE export preparation around the accepted
  asset, not unsolicited appearance retuning.

## 2026-06-07 CST - PMO Queued Next Parallel P0 Tasks After ROS2 R1 Recovery

- CoAgentOps superseded the earlier ROS2 R1 partial-recovery blocker with a
  completed post-restart no-op validation. ROS2 R1 is restored for business
  dispatch, so PMO can re-dispatch the next ROS2 gate.
- ROS2 060 returned blocked: LiDAR/IMU source topics stayed monotonic and the
  FAST-LIO loop-back counts stayed zero, but `/Odometry` and
  `/cloud_registered` also stayed zero. The current suspected gap is source
  timing/lifecycle alignment: the IMU window ends before later LiDAR stamps.
- PMO prepared, validated, and dispatched four next task packets: UE 019
  source-static control-binding preflight, Sunray/PBR 006 whole-aircraft
  grey-CAD material refinement, MWORKS R2 012 static live-audit queue
  refinement, and ROS2 061 FAST-LIO timing/source-lifecycle diagnosis. JSON
  parsing, native-surface checks, scoped diff checks, and the static MWORKS
  task gate passed. PMO also sent a sparse Chinese email progress update.
- MWORKS live GUI/MCP work remains blocked until the reusable existing-window
  attach/no-start route is proven. Static MWORKS planning may continue with
  `live_mworks_touched=false`.
- MWORKS R2 completed 012. PMO verified JSON parsing, department packet
  contract, static MWORKS live gate, and scoped diff check. The result refines
  the 011 large queue into a 20-candidate future live-audit first batch, plus
  R1/R2 single-session serialization and pre-live blocker guidance. This is
  static planning only, not live package-browser evidence, `check_model`,
  simulation, graphical/layout acceptance, or wiring acceptance.
- ROS2 R1 completed 061. PMO verified JSON parsing, department packet
  contract, and scoped diff check. The diagnosis explains the 060 FAST-LIO
  output gap from existing evidence and FAST-LIO source: the 060 IMU publisher
  finished before the later LiDAR replay window, so FAST-LIO's sync gate kept
  waiting for IMU coverage of LiDAR end time. 061 did not run a new live probe
  and does not prove FAST-LIO success, TF/RViz readiness, planner readiness, or
  closed loop.
- UE completed 019. PMO verified JSON parsing, department packet contract, and
  scoped diff check. The task added source-static checker/test/evidence for
  catalog-to-control UI binding descriptors. This is only future UI/control
  preflight evidence: no Unreal Editor/runtime, accepted-state UI, live UE
  ack, MWORKS/ROS2 ack, planner readiness, mission success, or closed loop is
  claimed.
- PMO is preparing the next ROS2 062 gate as a separate bounded
  FAST-LIO-only source-lifecycle alignment retest. The intended scope is
  evidence-local runner/helper work plus at most one no-goal probe after a
  current safety gate; no TF/RViz, planner/EGO, PositionCommand, 20 Hz adapter,
  UE, MWORKS, or production config/source/extrinsic edits are authorized.

## 2026-06-07 CST - PMO Integrated UE 018 And Kept ROS2 060 Running

- UE completed
  `RFLY-MOSIM-UE-CONSOLE-OPERATOR-COMMAND-CATALOG-SOURCE-STATIC-GATE-20260607-018`.
  PMO verified JSON parsing, department packet contract, and scoped diff check.
  The task added source-static checker/test/evidence for the RflySim-like UE
  operator command catalog: motor fault, wind disturbance, controller switch,
  planner switch, scene/map switch, experiment run control, and manual-review
  request. Each entry records owner, payload contract, ack/evidence fields,
  forbidden shortcut, accepted-state precondition, and claim boundary. This is
  not UE runtime transport, not UMG/Blueprint/Slate/Web UI, not accepted-state
  UI, not live MWORKS/ROS2 ack, not planner readiness, not controller
  performance, not mission success, and not closed loop.
- ROS2 R1 completed
  `RFLY-MOSIM-ROS2-RUNTIME-B1-20HZ-SOURCE-ONLY-NORMAL-EXIT-GATE-20260607-059`.
  PMO verified JSON parsing, department packet contract, and scoped diff check.
  The single allowed no-goal source-only probe exited normally: LiDAR, IMU, and
  recorder all returned 0; LiDAR produced 120 monotonic replay-time frames at
  about 20.15 Hz; IMU produced 1500 monotonic messages at about 200 Hz;
  forbidden planner/setpoint topics were absent; cleanup was clean. This is
  source-only replay-time normal-exit/timing evidence, not true 20 Hz sensor
  capture, FAST-LIO success, TF/RViz readiness, planner readiness, controller
  performance, mission success, or closed loop.
- PMO created and dispatched
  `RFLY-MOSIM-ROS2-RUNTIME-B1-20HZ-FASTLIO-ONLY-PRECONDITION-GATE-20260607-060`
  to ROS2 R1 with `gpt-5.5 + xhigh`. The task may run at most one no-goal
  FAST-LIO-only precondition probe using the 059 replay-time source discipline,
  and may write only 060 evidence-local artifacts plus return/blocker. It may
  not start RViz2, UE, MWORKS, planner/EGO, PositionCommand, 20 Hz adapter, TF
  bridge, active `/tf` recorder, goals, setpoints, or fake-data routes. Even a
  successful 060 return can only support FAST-LIO-only precondition evidence
  for a later separate TF/RViz observation gate; it cannot claim true 20 Hz
  sensor capture, TF/RViz readiness, localization/local-map quality,
  planner_ready, controller performance, mission success, or closed loop.
- CoAgentOps returned
  `PMO-COAGENTOPS-MWORKS-REUSABLE-SESSION-REBIND-20260607-001` as blocked.
  `session_manager(action=probe)` is safe no-start inspection only; a bounded
  `session_manager(action=health)` still started a new Sysplorer/MWORKS process
  and a new dedicated port instead of proving reuse of the existing logged-in
  window. MWORKS R1/R2 live `load_file`, `check_model`, `SimulateModel`, live
  graphical/package-browser audit, and GUI acceptance stay blocked until an
  attach-only/no-start route is fixed and validated.
- Static MWORKS work may continue only when the task declares
  `live_mworks_touched=false` and does not require MCP/GUI/check/simulation.
  ROS2 060 is still running in ROS2 R1; PMO has not received a 060 return or
  blocker yet and should not duplicate-dispatch it while that turn remains in
  progress.

## 2026-06-07 CST - PMO Integrated R2 010 And Dispatched Next P0 Engineering Gates

- MWORKS R2 completed
  `PMO-MWORKS-R2-MOSIMQUAD-CONTROLLERS-CONTROLLERBLOCKS-STATIC-INTEGRATION-20260607-010`.
  PMO verified JSON parsing, department packet contract, static MWORKS live
  gate, and scoped diff check. `MoSimQuadrotorModel.Controllers` now exposes
  the seven `QuadrotorControllerBlocks` formal controller categories while
  preserving `QuadrotorExperiments.ControllerBaselines` compatibility. This is
  static package/category integration only, not live package-browser,
  `check_model`, simulation, graphical/layout acceptance, controller
  performance, planner readiness, runtime ack, mission success, or closed loop.
- PMO created and dispatched three next P0 tasks with `gpt-5.5 + xhigh`:
  MWORKS R1 006 for live `MoSimQuadrotorModel.Dynamics` wrapper/chassis
  `check_model` first and minimal smoke only if eligible; MWORKS R2 011 for
  static graphical/package-browser audit preparation; and UE 017 for the
  authoritative live command-echo producer/consumer gate definition.
- PMO created ROS2 059 for the source-only normal-exit and 20 Hz timing-gap
  gate after 058, but dispatch to ROS2 R1 failed with an agent-loop error
  before the engineering task started. PMO wrote the initial blocker and handed
  recovery to CoAgentOps. No ROS2 059 runtime, FAST-LIO, TF/RViz, planner,
  UE, MWORKS, planner_ready, or closed-loop evidence exists.

## 2026-06-07 CST - PMO Retired WeChat Progress Route And Dispatched MWORKS R2 Controller Static Integration

- PMO sent a sparse Chinese email progress update successfully. Project
  notifications now stay email-only; the stale WeChat `ret=-2` progress
  diagnosis row is superseded and the archived WeChat gateway is not polled or
  dispatched for ordinary MoSim work.
- PMO integrated UE 016 as completed: the command-echo runtime-preflight task
  remains source-static only, and the static checker/test matrix now rejects
  build/UBT/CLI success as live command-ack evidence. This does not prove live
  UE runtime ack, accepted-state UI, planner readiness, controller performance,
  mission success, or closed loop.
- After R2 completed the real `QuadrotorExperiments` folder/category migration,
  PMO created MWORKS R2 task
  `PMO-MWORKS-R2-MOSIMQUAD-CONTROLLERS-CONTROLLERBLOCKS-STATIC-INTEGRATION-20260607-010`.
  The packet passed JSON parsing, strict native-surface gate,
  `check_mworks_live_gate.py --kind task --expect department`, and scoped diff
  check. Scope is static-only: no MWORKS/Sysplorer window, screenshot, MCP,
  `check_model`, simulation, Smart Layout, or live graphical/layout claim.

## 2026-06-07 CST - PMO Synced P0 Mainline State And Kept Automations Compact

- User confirmed not to keep growing automation prompts. PMO updated the
  durable rule surfaces so native automations stay as short triggers that read
  canonical docs/templates/checkers at runtime; existing working automations
  were not changed.
- MWORKS R2 has completed a static-only real folder/category migration for
  `QuadrotorExperiments`: root package/order now exposes 11 category packages,
  137 real model files moved under categories, 137 hidden root compatibility
  aliases remain, and static validation passed. This is not graphical/layout
  acceptance, `check_model`, or simulation evidence.
- ROS2 R1 completed 056 as a static source/rate/sync audit: no true validated
  20 Hz LiDAR source was found; the accepted current LiDAR source is about
  10 Hz, and the non-fake route is replay-time adaptation that still requires
  later validation.
- ROS2 R1 completed 057 as a blocker: the first source-only live probe budget
  was consumed but aborted through the runner first-message gate after only
  three LiDAR trace rows, with no full-window 20 Hz source evidence.
- ROS2 R1 completed 058 closeout from existing evidence only, and PMO verified
  the department packet contract. 058 proves only replay-time source-only
  validation: 120 LiDAR frames were replayed at about 18.46 Hz observed, bounded
  IMU evidence is about 200 Hz, forbidden planner/control topics were absent,
  and cleanup ended clean. Recorder exit status 137 remains a caveat from the
  interrupted outer turn. This is not true 20 Hz sensor capture, FAST-LIO
  success, TF/RViz readiness, planner readiness, controller performance,
  mission success, or closed loop.

## 2026-06-07 CST - MWORKS R2 006 Closed As Live-Surface Blocker

- R2 wrote blocker
  `Results/agent_packets/blockers/PMO-MWORKS-R2-MOSIMQUAD-LIVE-PACKAGE-BROWSER-GRAPHICAL-AUDIT-20260607-006.json`
  and both `check_mworks_live_gate.py --kind return --expect department` and
  `check_department_packet_contract.py` pass.
- Current closeout sentinel was `incident_detected/license_or_login` with
  `license_state=unknown_blocked_visible_unknown_and_session_reuse_blocked`.
  Interrupted evidence also showed a separate `Sysplorer [教育版]` start page
  after MCP health, so the 006 live package/browser and graphical audit cannot
  be completed under the reuse-existing-session/no-new-window boundary.
- Treat 006 as blocker evidence only: partial package-browser screenshots are
  not graphical/layout acceptance, and no check_model, simulation, controller
  performance, planner readiness, UE/ROS2 runtime ack, mission success, or
  closed-loop claim is made. Next MWORKS live audit requires PMO/CoAgentOps to
  resolve or classify the reusable Sysplorer session and rerun a fresh
  current-turn gate.

## 2026-06-07 CST - MWORKS Activation Patrol Moved To CoAgentOps Automation

- PMO updated the current MWORKS operating boundary: routine activation/window
  patrol now belongs to `MoSim｜CoAgent运维平台` through the 30-minute native
  automation, not to every MWORKS R1/R2 engineering dispatch.
- MWORKS R1/R2 should reference the latest patrol and focus on engineering
  outputs: `.mo`/`package.mo`, `check_model`, `SimulateModel`, metrics,
  layout/wiring observations, and phase screenshots when GUI evidence is
  claimed. JSON packets or sentinel-only outputs do not count as model progress.
- CoAgentOps patrol must use maximized-window evidence when hidden authorization
  panes are possible. If official recovery on the existing window does not
  return, PMO/CoAgentOps may restart MWORKS and recover through the official UI
  as a bounded exception.
- Updated durable docs, MWORKS skills, dispatch templates, the MWORKS live-gate
  checker, `capture_window_background.ps1`, and automation
  `mosim-wechat-gateway-hourly-health`.

## 2026-06-07 CST - CoAgentOps/ROS2 R1 Dispatch Surface Restored; 056 Redispatched

- CoAgentOps returned
  `COAGENTOPS-ROS2-R1-056-DISPATCH-SURFACE-RECOVERY-20260607-001`; PMO
  verified JSON parsing and `check_department_packet_contract.py` with
  `ok=true`. ROS2 R1 `019e9c72-ee74-79d1-b9fe-621d3c6fc99e` accepted the
  recovery no-op and replied exactly `ros2_r1_noop_received_20260607_1848`.
- This supersedes the earlier PMO-side `still_quarantined` conclusion for the
  CoAgentOps/R1-056 recovery path after the user manually fixed the Codex App
  context-compression surface. Production dispatch to ROS2 R1 is restored for
  bounded tasks.
- PMO revalidated the 056 task packet with
  `check_agent_task_native_surface_gate.py --strict`, confirmed no existing
  056 return/blocker packet, and redispatched
  `RFLY-MOSIM-ROS2-RUNTIME-B1-LIDAR-IMU-20HZ-SOURCE-SYNC-AUDIT-20260607-056`
  to ROS2 R1 with `gpt-5.5 + xhigh`.
- Current 056 scope remains audit-only: no live ROS2/FAST-LIO/RViz/planner/UE/
  MWORKS, no fake point clouds/maps, and no planner_ready/closed_loop/runtime
  success claims until later evidence exists.

## 2026-06-07 CST - PMO Took Over CoAgentOps Self-Dead Recovery

- User flagged that `MoSim｜CoAgent运维平台` was not replying while PMO kept
  waiting. PMO reclassified this as a P0 control-plane incident: native
  list/read/send success is not enough when the target thread produces no
  agent final reply, exact no-op reply, or expected return/blocker packet.
- PMO wrote recovery packet
  `PMO-COAGENTOPS-SELF-DEAD-RESTART-RECOVERY-20260607-001`, attempted sparse
  WeChat and mail notification, then triggered the authorized Codex++ restart
  route. WeChat was attempted but still failed at the Weixin layer with
  `ret=-2`; the sparse mail alert succeeded.
- Restart evidence was written under `Results/codex_watchdog/`, with the
  Codex++ restart button invoked through UI Automation. Post-restart no-op
  validation to CoAgentOps did not return the expected text within the bounded
  window and the ROS2 056 recovery return/blocker packet still does not exist,
  so CoAgentOps remains `still_quarantined`.
- PMO updated the durable rules in `AGENTS.md`,
  `Docs/Workflows/new_conversation_context.md`, and
  `Docs/Workflows/coagent_meta_maintenance.md`: a visible thread marked
  completed without an agent response or expected packet is not routable.
  PMO must not wait for repeated automation prompts to accumulate.
- Consequence: do not rely on CoAgentOps for ROS2 R1 056 recovery or other P0
  recovery actions until a later no-op proves restoration or the user approves
  replacement/escalation. PMO may continue non-conflicting mainline work.

## 2026-06-07 CST - PMO Patrol Updated; MWORKS 005 Integrated; ROS2 055 Running

- PMO updated the current thread heartbeat automation
  `mosim-pmo-p0-long-run-followup` to a 15 minute visible-department patrol.
  The prompt now explicitly covers child-thread status checks and the
  CoAgentOps-dead failover path: if CoAgentOps cannot receive recovery work,
  PMO writes a recovery/blocker packet, sends sparse Chinese WeChat plus email
  alerts, triggers the authorized Codex++ restart route, and post-restart
  no-op validates CoAgentOps. The rare automation-update/heartbeat collision
  reported by the user is treated as an exceptional incident, not a default
  policy branch.
- PMO attempted sparse WeChat progress notifications for the patrol/054/005
  update and again after 005 was integrated plus R2 006/ROS2 055 were in
  flight. Both sends were not delivered: WeChat returned `ret=-2`. A follow-up
  local gateway health check for the earlier failure returned `ok=true`, so the
  current evidence still points to stale WeChat outbound context rather than
  local API/socket failure. PMO did not loop retry; the next retry requires a
  fresh inbound WeChat message or a gateway-owned recovery turn. The latest
  failed-send audit is recorded under `Results/coagent_gateway/progress/`.
  PMO dispatched a separate P1 gateway diagnosis task to `MoSim｜微信网关运维部`
  so the engineering mainline can continue without treating notification
  delivery as MWORKS/ROS2 progress evidence.
- PMO integrated MWORKS R1 blocker
  `PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-SMOKE-CHECK-20260607-004`.
  Both `check_mworks_live_gate.py --kind return --expect department` and
  `check_department_packet_contract.py` pass. R1 ran the required current-turn
  MWORKS GUI sentinel/background screenshot, recorded current-turn license API
  evidence, loaded the official baseline, `QuadrotorExperiments`, and
  `MoSimQuadrotorModel`, then ran the five `MoSimQuadrotorModel.Dynamics`
  formal-entry `check_model` gates. Four entries passed; only
  `PhysicalWrenchAdapter` failed with a MultiBody `world.*` conditional
  component error around `enableAnimation and animateWorld`. Hover/Yaw smoke
  simulations were not run because the pre-simulation check gate failed.
- MWORKS R1 returned 005 as completed, and PMO verified JSON parsing,
  `check_mworks_live_gate.py --kind return --expect department`,
  `check_department_packet_contract.py`, and scoped `git diff --check` over
  the 005 evidence/model files. R1 made two narrow project-owned `.mo` changes:
  `Sunray150PhysicalWrenchFrameAdapter` now explicitly final-disables
  MultiBody World animation switches, and `MoSimQuadrotorModel.Dynamics`
  removed the package-level legacy inheritance while keeping explicit formal
  entries and retargeting `PhysicalWrenchAdapter` to the checked project-owned
  adapter. Five `MoSimQuadrotorModel.Dynamics` formal entries passed
  `check_model`; `HoverSmoke` and `YawStepSmoke` each completed a 0.25 s
  `SimulateModel` smoke run. Result probes recorded hover thrust error at end
  near zero and yaw body moment z at end about `0.061538`. Current-turn
  sentinel, background screenshots, license API, and phase screenshots were
  included. This is a narrow Dynamics adapter check/smoke repair only; it does
  not prove identified Sunray150 parameters, controller performance,
  planner/runtime readiness, graphical/layout acceptance, mission success, or
  closed loop.
- PMO created and dispatched MWORKS R2 task
  `PMO-MWORKS-R2-MOSIMQUAD-LIVE-PACKAGE-BROWSER-GRAPHICAL-AUDIT-20260607-006`.
  The task packet passed JSON parsing, `check_mworks_live_gate.py --kind task
  --expect department`, strict native-surface gate, and scoped diff checks.
  Scope is a non-destructive live package/browser and graphical-interface
  audit after the first cleanup and Dynamics smoke repair. R2 must run its own
  current-turn sentinel/background screenshot and same-turn license/window
  classification, then produce package/browser or equivalent graphical
  screenshots/observations, representative wiring/layout observations, an
  issue list, and next cleanup recommendations or a precise blocker. It may
  not edit `.mo`/`package.mo`/`package.order`, run Smart Layout writeback,
  simulate, open/close/restart windows, or claim final graphical acceptance,
  controller performance, planner/runtime readiness, mission success, or
  closed loop.
- PMO integrated UE return
  `RFLY-MOSIM-UE-CONSOLE-SOURCE-STATIC-COMMAND-ECHO-RECEIVER-SHELL-IMPLEMENTATION-20260607-014`.
  `check_department_packet_contract.py` passes. UE added the project-owned
  source-static command-echo receiver shell C++ header/source, updated the
  static checker/tests, and produced 014 source-boundary evidence. This is not
  Unreal compile evidence, not runtime transport, not live ack, and not
  accepted-state UI proof.
- PMO integrated UE return
  `RFLY-MOSIM-UE-CONSOLE-COMMAND-ECHO-RECEIVER-SHELL-BUILD-GATE-20260607-015`.
  `check_department_packet_contract.py` passes. UE ran the Windows-native CLI
  build wrapper for `MoSimSceneLibraryEditor Win64 Development`; UBT compiled
  the new command-echo receiver shell source and linked
  `UnrealEditor-QuadrotorMworksBridge.dll` on the first attempt. No C++ fix was
  needed. This is build-only evidence, not UE runtime, live command ack,
  accepted-state UI, MWORKS/ROS2 ack, planner readiness, controller
  performance, mission success, or closed-loop proof.
- ROS2 R1 returned blocker
  `RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-LIFECYCLE-SAFE-RUNNER-PROBE-20260607-053`,
  and PMO integrated it after a one-turn contract correction.
  `check_department_packet_contract.py` now passes. The blocker records that
  053 only produced partial evidence-local runner/script drafts; required
  safety artifacts and helper scripts were missing, no preflight-only safety
  gate ran, and no live no-goal FAST-LIO probe ran. No TF/RViz/planner/
  PositionCommand/20Hz follow-up is accepted from 053; the next ROS2 step must
  be a fresh bounded helper/artifact completion task before any live probe.
- PMO created and dispatched ROS2 R1 task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-LIFECYCLE-SAFE-RUNNER-ARTIFACTS-20260607-054`.
  The packet passed JSON parsing, strict native-surface gate, and diff
  whitespace checks before dispatch. Scope is artifact/preflight-only:
  complete the missing evidence-local helper scripts and dry-run safety
  artifacts from 053, with live probe budget set to zero.
- ROS2 R1 returned 054 as completed, and PMO verified
  `check_department_packet_contract.py`, JSON parsing, and scoped
  `git diff --check`. The result created the evidence-local dry-run wrapper,
  helper scripts, cleanup-scope audit, LiDAR invocation audit, preflight
  process-match report, probe-budget manifest, source-window check, probe
  metadata, and artifact validation summary under the 054 evidence directory.
  No ROS2, FAST-LIO, RViz2, planner, UE, MWORKS, TF bridge,
  PositionCommand, or 20 Hz adapter was started. Treat 054 as a pre-live
  safety artifact closeout only; any IMU lifecycle runtime classification
  still needs a separately authorized no-goal live probe task.
- PMO created ROS2 R1 task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-LIFECYCLE-SAFE-RUNNER-LIVE-PROBE-20260607-055`.
  The task packet passed JSON parsing, strict native-surface gate, and diff
  whitespace checks. 055 is the separately authorized live follow-up to 054:
  it must first create current 055 safety artifacts, then run exactly one
  no-goal FAST-LIO-only bounded probe only if the gate passes. It still
  forbids TF/RViz2/planner/EGO/PositionCommand/20 Hz/UE/MWORKS work, goal or
  setpoint publication, fake data, repeated probes, and planner/controller/
  closed-loop claims.
- ROS2 R1 returned 055 as completed, and PMO verified JSON parsing,
  `check_department_packet_contract.py`, and scoped `git diff --check`. R1
  created fresh 055 evidence-local runner/helper artifacts, passed the current
  safety gate, and consumed exactly one no-goal FAST-LIO-only live probe.
  Evidence records monotonic source-topic windows, zero callback loop-back in
  the FAST-LIO trace, scoped `/Odometry` and `/cloud_registered` output counts,
  forbidden planner/position topics absent, no TF/RViz/planner/EGO/
  PositionCommand/20 Hz/UE/MWORKS processes started, and clean final cleanup.
  This is bounded IMU lifecycle/start-stop diagnostic evidence only: it says
  the previous loop-back did not reproduce under this no-goal FAST-LIO-only
  probe. It is not FAST-LIO success, TF/RViz readiness, localization/local-map
  quality, planner_ready, controller performance, mission success, or closed
  loop.
- PMO created ROS2 R1 task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-LIDAR-IMU-20HZ-SOURCE-SYNC-AUDIT-20260607-056`
  to convert the user-requested LiDAR/IMU/control 20 Hz synchronization into a
  non-fake source/rate audit and next implementation plan. The packet passed
  JSON parsing, strict native-surface gate, and scoped diff checks, but native
  dispatch to ROS2 R1 failed with `failed to start turn: internal error; agent
  loop died unexpectedly`. PMO wrote initial blocker
  `PMO-ROS2-R1-056-DISPATCH-SURFACE-20260607-001`, did not retry business
  routing, did not create a replacement thread, and handed the incident to
  CoAgentOps for bounded diagnosis/recovery. 056 has not started; this is a
  Codex App dispatch-surface incident, not ROS2 source/rate evidence.

## 2026-06-07 CST - ROS2 052 Blocked; UE 014 Prepared

- PMO integrated ROS2 blocker
  `RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-LIFECYCLE-RUNNER-FIX-20260607-052`.
  `check_department_packet_contract.py` passes. The first 052 turn was
  interrupted before it produced a corrected evidence-local runner, cleanup
  audit, or probe artifact; the收口 turn correctly did not launch ROS2/
  FAST-LIO and wrote a precise blocker. There is still no proven `trace_path`
  runner repair, no proof that cleanup excludes MWORKS/Sysplorer/Syslab/MCP
  wrapper/Codex/browser/general desktop processes, and no new 052 runtime
  evidence.
- PMO created UE task
  `RFLY-MOSIM-UE-CONSOLE-SOURCE-STATIC-COMMAND-ECHO-RECEIVER-SHELL-IMPLEMENTATION-20260607-014`
  from 013 build-preflight evidence. Scope is source-static only: implement
  the minimal project-owned command-echo receiver shell component and update
  static checker/tests. It must not open UE, run Unreal build/runtime, bind
  sockets/listeners, edit Blueprint/UMG/assets, enable accepted-state UI, or
  claim live UE runtime ack, planner readiness, controller performance,
  mission success, or closed loop.
- PMO created ROS2 task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-LIFECYCLE-SAFE-RUNNER-PROBE-20260607-053`.
  It is a stricter follow-up to 052: ROS2 R1 must first write a corrected
  evidence-local runner and cleanup-scope audit, prove the cleanup cannot
  match MWORKS/Sysplorer/Syslab/MCP wrapper/Codex/browser/general desktop
  processes, and prove the LiDAR invocation supplies `trace_path` if the
  instrumented binary is used. Only after that safety gate may it run one
  no-goal FAST-LIO-only probe; otherwise it must return a blocker without live
  ROS2 work.

## 2026-06-07 CST - UE 013 And MWORKS R2 002 Integrated; ROS2 051 Blocked

- PMO integrated UE return
  `RFLY-MOSIM-UE-CONSOLE-RECEIVER-SHELL-BUILD-PREFLIGHT-20260607-013`.
  `check_department_packet_contract.py` passes. The result is only a
  source-static/build-preflight closeout for a future command-echo receiver
  shell: it identifies the minimal C++ receiver component slice, build
  surface, build command, and acceptance gates. It does not implement or build
  UE code, does not prove live runtime ack, and does not enable accepted-state
  UI binding.
- PMO integrated MWORKS R2 return
  `PMO-MWORKS-R2-MOSIMQUAD-PACKAGE-CLASSIFICATION-RENAME-PLAN-20260607-002`.
  Both `check_mworks_live_gate.py --kind return --expect department` and
  `check_department_packet_contract.py` pass. R2 produced the static
  `MoSimQuadrotorModel` classification/migration map: 11 formal categories,
  11 legacy compatibility categories, and 94 retained flat
  `QuadrotorExperiments` sibling `.mo` files. This is static package
  organization evidence only; it is not `check_model`, simulation,
  graphical/layout acceptance, controller performance, parameter
  identification, planner readiness, runtime ack, or closed-loop evidence.
- PMO integrated ROS2 blocker
  `RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-LIFECYCLE-BOUNDED-PROBE-20260607-051`.
  `check_department_packet_contract.py` passes. R1 produced evidence-local
  runner/recorder/summarizer/publisher artifacts and consumed the one live
  probe budget, but the probe failed before first Livox delivery because the
  runner did not pass the required LiDAR trace parameter. The blocker also
  records a cleanup-scope risk: ROS2 runner preflight matched
  MWORKS/Sysplorer/Syslab MCP wrapper processes, so future ROS2 cleanup must be
  narrowed to ROS/FAST-LIO/replay processes only.
- Updated `Docs/Workflows/ros2_runtime_setup.md`: ROS2 runtime cleanup must not
  include MWORKS, Sysplorer, Syslab, MCP wrapper, Codex, browser, or general
  desktop process names in kill/preflight patterns. Next ROS2 step is a narrow
  052 runner-fix task; still no TF/RViz/planner/PositionCommand/20 Hz claims.

## 2026-06-07 CST - PMO 15-Minute Patrol Verified And P0 Dispatch Continued

- PMO verified the real Codex App automation configuration for
  `mosim-pmo-p0-long-run-followup`: it is active, runs every 15 minutes, and
  explicitly checks `MoSim｜CoAgent运维平台`
  (`019e9bc1-ea9f-7102-b41a-4ef9b2308992`) before ordinary department patrol.
  If CoAgentOps itself cannot start turns, the automation prompt now requires
  PMO to write the recovery packet, send sparse WeChat plus email alerts,
  trigger the authorized Codex++ restart route, and perform next-heartbeat
  no-op validation. This is present in the actual `automation.toml`, not only
  in chat text.
- PMO rechecked current return packets without touching live runtimes:
  `PMO-MWORKS-R1-MOSIMQUAD-BASELINE-ADAPTER-CHECK-20260607-003` passes both
  the MWORKS live gate and department packet contract; ROS2 050 and UE 012
  pass the department packet contract. R1 003 proves only current-turn
  `MoSimQuadrotorModel.Baseline` adapter load/check evidence for four baseline
  aliases; it is not dynamics optimization, simulation, controller performance,
  planner readiness, runtime ack, or closed-loop evidence.
- PMO dispatched three follow-ups with `gpt-5.5 + xhigh`: ROS2 051 bounded
  IMU lifecycle probe to ROS2 R1, UE 013 existing-evidence build-preflight
  closeout to the UE console department, and MWORKS R2 002 static
  package-classification closeout to R2. MWORKS R2 002 must rerun its own
  current-turn sentinel/background screenshot before static package audit
  because the previous 002 turn was interrupted.
- Updated `Docs/Workflows/coagent_meta_maintenance.md` so the created native
  automation table includes the PMO 15-minute heartbeat and its CoAgentOps
  self-dead fail-close responsibility.

## 2026-06-07 CST - CoAgentOps Heartbeat P0 Fail-Close Rule Added

- User caught a CoAgentOps patrol failure: the 13:48 heartbeat saw an open
  MWORKS R2 dead-thread recovery packet but treated it as ordinary pending work
  and returned `DONT_NOTIFY`. That patrol packet is now superseded, not a valid
  healthy-heartbeat example.
- Durable rule landed: any PMO/CoAgentOps heartbeat that sees P0 dead-thread
  recovery still waiting for notifications, Codex++ restart, post-restart
  validation, or `still_quarantined` must fail closed. It must continue the
  authorized recovery step, or write a blocker/request packet and `NOTIFY`; it
  must not mark healthy, return `DONT_NOTIFY`, or run P1 optimization while the
  P0 recovery remains open.
- Updated `AGENTS.md`, `Docs/Workflows/new_conversation_context.md`,
  `Docs/Workflows/coagent_meta_maintenance.md`,
  `Docs/Workflows/agent_orchestration.md`, and the native heartbeat automation
  `mosim-wechat-gateway-hourly-health`. Correction packet:
  `Results/agent_packets/returns/COAGENTOPS-HEARTBEAT-P0-FAILCLOSE-CORRECTION-20260607-001.json`.
- Boundary: this correction prevents recurrence of the巡检误判. It did not
  trigger Codex++ restart, create R3, modify CoAgent runtime/schema/transport,
  or touch MWORKS/ROS2/UE/Blender runtime surfaces.

## 2026-06-07 CST - MoSimQuadrotorModel Formal Package Started

- User approved naming the project-owned formal quadrotor package
  `MoSimQuadrotorModel` and asked to classify the old experiment pool there.
  PMO created the first package skeleton under `Models/MoSimQuadrotorModel/`.
  The current structure classifies entry points as `Baseline`, `Dynamics`,
  `Missions`, `Controllers`, `Robustness`, `Planning`, `SceneTrace`,
  `System`, `Formation`, `Support`, and `LegacyCompatibility`, each with
  Chinese descriptions for Sysplorer/model-browser review.
- Boundary: this is a low-risk alias/extends migration layer, not a destructive
  rename of all old files. `QuadrotorModel` remains the official/upstream
  baseline and dependency. `QuadrotorExperiments` remains the legacy
  experiment pool and compatibility source until each old class is mapped,
  references are updated, and targeted `check_model`/simulation/layout
  evidence proves the new entry.
- Next PMO split: dispatch MWORKS R1 to connect/verify the `QuadrotorModel`
  baseline adapter into `MoSimQuadrotorModel`, and dispatch MWORKS R2 to audit
  the package tree, migration classification, naming plan, and graphical/model
  organization. Both tasks must repeat the department-owned MWORKS activation
  sentinel/background screenshot preflight and must return engineering outputs,
  not JSON-only progress.
- PMO generated and validated two MWORKS department task packets:
  `PMO-MWORKS-R1-MOSIMQUAD-BASELINE-ADAPTER-CHECK-20260607-001` for live
  baseline adapter `check_model` evidence, and
  `PMO-MWORKS-R2-MOSIMQUAD-PACKAGE-CLASSIFICATION-RENAME-PLAN-20260607-001`
  for static old-to-new class mapping and rename batch planning. Both passed
  `check_mworks_live_gate.py --kind task --expect department` and were
  dispatched to the current MWORKS R1/R2 visible threads. Return/blocker
  packets are pending.
- Follow-up correction: R1 and R2 returned 001 blockers because the target
  departments could not observe/capture a reusable MWORKS/Sysplorer window in
  that turn. PMO then corrected a bad acceptance assumption: `Sysplorer
  [教育版]` is only an edition/window marker and is not proof of account
  activation, because activated and unactivated states may both show it. New
  packets must use `license_state=education_window_observed_activation_unverified`
  for title-only observations, and live MWORKS work must record
  `license_api_before` when available. A successful `check_model` or simulation
  without authorization errors is only task-local license sufficiency evidence,
  not a standing activation claim.
- PMO updated the machine gate and tests accordingly, then generated validated
  retry task packets `PMO-MWORKS-R1-MOSIMQUAD-BASELINE-ADAPTER-CHECK-20260607-002`
  and `PMO-MWORKS-R2-MOSIMQUAD-PACKAGE-CLASSIFICATION-RENAME-PLAN-20260607-002`.
  Both pass `check_mworks_live_gate.py --kind task --expect department` and
  `check_agent_task_native_surface_gate.py --strict`. No MWORKS R3 is needed
  yet; the current bottleneck is corrected gate semantics plus R1/R2 execution,
  not staffing.

## 2026-06-07 CST - Department Subagent Planning Template Unified And Model State Rechecked

- PMO corrected the visible-department dispatch wording after the user pointed
  out that departments should plan sub-agent scheduling, not be told to use at
  least one sub-agent. The standard dispatch helper now injects a
  `Department Local Planning And Subagent Decision Contract` into every
  department task text. Required fields are `department_local_goal`,
  `critical_path_steps`, `parallelizable_slices`, `subagent_plan`,
  `subagent_plan_reason`, `subagents_used`, `verification_gates`, and
  `manual_review_or_blocker_triggers`; `subagent_plan` is a decision among
  `used`, `available_but_not_useful`, `unavailable`, and `unsafe`.
- The same wording was synchronized into `AGENTS.md`,
  `Docs/Workflows/agent_orchestration.md`,
  `CoAgent/dispatch/communication_contract.md`,
  `Docs/Workflows/rfly_mosim_p0_10h_execution_plan.md`, and
  `Docs/Workflows/agent_task_ledger.md`. Focused validation passed:
  `python -m pytest Scripts/tests/test_dispatch_helper_mworks_gate.py
  CoAgent/tests/test_lifecycle_smoke.py -q` and
  `python -m py_compile CoAgent/dispatch/dispatch_helper.py`.
- Static model-state recheck: `Models/QuadrotorExperiments/package.mo` already
  contains category packages such as `OfficialScenarios`,
  `ControllerBaselines`, `RobustFaultScenarios`, `PlanningScenarios`,
  `SceneTraceScenarios`, `TraceIsolation`, `DynamicsUpgrade`,
  `SystemArchitecture`, `SystemModules`, `SupportModels`, and
  `FormationScenarios`, and it contains the project-owned
  `Sunray150RflyStyleRotorDynamics`, wrapper, and physical-wrench adapter
  slices. However, the directory still has many legacy flat `.mo` files and
  the official `References/MWORKS/QuadrotorModel/Mechanics/QuadChassis`
  remains the baseline plant. The Rfly-style dynamics slice is experimental
  wrapper evidence, not a full replacement of `QuadChassis` or a closed-loop
  Sunray150 model acceptance.
- Current GUI preflight for this static audit saw no MWORKS/Sysplorer window
  (`license_state_hint=no_mworks_window_observed`), so no live MWORKS
  readiness, package-browser acceptance, `check_model`, simulation,
  graphical/layout acceptance, controller performance, planner_ready, runtime
  ack, or closed_loop claim is made in this entry.

## 2026-06-07 CST - MWORKS 021 Screenshot Classification Drill Closed

- PMO received the CoAgentOps recovery-rule sync and verified the canonical
  docs already contain the new boundary: every planned Codex++ restart for a
  dead-thread incident must first attempt one sparse Chinese email, even if
  WeChat was attempted or appears healthy; if CoAgentOps itself is the dead
  thread, PMO or another healthy mainline surface must own email, restart, and
  post-restart no-op validation. No engineering dispatch or runtime change was
  needed for this sync.
- PMO closed the MWORKS R1/R2 021 screenshot classification drill. Both target
  departments ran their own read-only GUI sentinel and existing-window
  background screenshot, then read the sentinel/capture evidence in the same
  turn and classified the observed education-edition window state under the
  then-current rule.
  `python Scripts/quality/check_mworks_live_gate.py <packet> --kind return
  --expect department` passed with `fail_count=0` for both return packets.
- Boundary: 021 proves the department-owned screenshot/sentinel
  same-turn-classification habit is executable. After the later user
  correction, its old `education_clean_preflight` wording is not activation
  proof and must not be reused as a live-work acceptance condition. It is not
  MWORKS package acceptance, model readiness, `check_model`, simulation,
  graphical/layout acceptance, controller performance, planner readiness, live
  runtime ack, or closed-loop evidence. Every later MWORKS business dispatch
  must repeat this preflight in that task's own packet, classify title-only
  education observations as activation-unverified unless stronger API/result
  evidence exists, and any demo/login/authorization/mixed/unknown/unavailable
  state remains a blocker.

## 2026-06-07 CST - MWORKS Screenshot Gate Hardened To Require Same-Turn Classification

- User corrected the PMO again: MWORKS departments must not merely run a
  background screenshot or return an evidence path. They must read the sentinel
  JSON/capture manifest or inspect screenshot/window-title evidence in the same
  task turn, classify activation state, and return a blocker if they cannot
  inspect/classify the evidence.
- PMO hardened the machine gate in `Scripts/quality/check_mworks_live_gate.py`:
  `activation_state_observation` must explicitly reference observed evidence
  such as sentinel, window title, screenshot, capture, or manifest; vague
  status prose is rejected. A blocking `license_state` such as demo, login,
  activation, authorization, mixed, unknown, unavailable, or blocked must be
  returned with `status=blocked`, not as a completed MWORKS task.
- PMO synchronized the same rule into the PMO dispatch helper, communication
  contract, orchestration workflow, `AGENTS.md`, and MWORKS skills for MCP
  operations, runtime diagnostics, model context, simulation evidence,
  Sysblock graphical modeling, report visualization, and test quality.
- Focused validation passed:
  `python -m pytest Scripts/tests/test_mworks_live_gate.py
  Scripts/tests/test_agent_task_native_surface_gate.py
  Scripts/tests/test_dispatch_helper_mworks_gate.py -q`.
  The strict 019 R1/R2 task packets still pass
  `check_mworks_live_gate.py --kind task --expect department`, and the latest
  clean 016 R1/R2 current-activation return packets still pass
  `check_mworks_live_gate.py --kind return --expect department`.
- Boundary: this is PMO-side dispatch/machine-gate hardening. It does not mean
  the blocked 019 R1/R2 drills have executed; those remain blocked by the
  Codex App visible-thread dispatch-surface issue until R1/R2 can start turns
  again. Historical 010 mixed/demo blocker packets predate
  `activation_state_observation` and should be treated as incident/training
  evidence, not current-format acceptance packets.
- Follow-up: native visible-thread delivery to both MWORKS R1 and R2 succeeded
  for static 020 rule-sync ACK tasks. R1 wrote
  `PMO-MWORKS-R1-SCREENSHOT-CLASSIFICATION-GATE-HARDENING-ACK-20260607-020`
  and R2 wrote
  `PMO-MWORKS-R2-SCREENSHOT-CLASSIFICATION-GATE-HARDENING-ACK-20260607-020`.
  Both ACK packets are valid JSON, include department planning fields, and
  explicitly set `live_mworks_touched=false` and
  `mworks_window_evidence_touched=false`; they are rule acknowledgements only,
  not current activation/readiness evidence. This shows the R1/R2 thread
  dispatch surface can start turns again for static work, but the original 019
  per-task screenshot drill still needs to be retried before resuming MWORKS
  business work.

## 2026-06-07 CST - ROS2 048 And UE 012 Integrated; CoAgentOps Still Cannot Start Turns

- PMO integrated ROS2 R1 return
  `RFLY-MOSIM-ROS2-RUNTIME-B1-FASTLIO-IMU-CALLBACK-STARTUP-BOUNDARY-DIAG-20260607-048`.
  048 ran as static diagnosis only: it did not start a new ROS2 live graph or
  FAST-LIO probe. It classifies the 047 blocker as monotonic publisher/Livox/IMU
  source-topic stamps with a FAST-LIO callback-local `imu_cbk` loop-back, not
  publisher-side Livox stamp regression or source-topic IMU header-stamp
  regression in that run.
- PMO integrated UE return
  `RFLY-MOSIM-UE-CONSOLE-SOURCE-STATIC-RECEIVER-SHELL-IMPLEMENTATION-CHECKER-20260607-012`.
  012 added a source/static receiver-shell contract checker for future
  `mosim.ue_command_echo.v1`. PMO reran the checker and combined UE static
  tests: 39 static tests passed. The checker keeps runtime receiver
  implementation, accepted-state UI enablement, and live ack claims blocked
  until an authoritative live echo producer exists.
- Boundary: 048/012 do not prove FAST-LIO success, TF/RViz readiness, live UE
  runtime ack, live MWORKS downlink, ROS2 runtime ack, planner readiness,
  controller performance, final UI acceptance, mission success, or closed loop.
  Next ROS2 work should be a separately scoped evidence-local FAST-LIO callback
  first-N instrumentation gate before any planner or TF/RViz readiness work.
- PMO ran one CoAgentOps no-op recovery probe at 08:08 CST after the earlier
  MWORKS 019 dispatch-surface incident. It still failed with `failed to start
  turn: internal error; agent loop died unexpectedly`. Treat CoAgentOps/MWORKS
  visible-thread recovery as still blocked; continue with ROS2/UE threads only
  when they are independently reachable and their task scopes do not require
  MWORKS.

## 2026-06-07 CST - MWORKS 019 Screenshot Drill Blocked By Visible-Thread Dispatch Surface

- User corrected the PMO again: every MWORKS assignment must force the target
  department to run its own background screenshot and activation-state check
  before model, solver, MCP, layout, or graphical-review work. PMO created two
  019 drill packets for MWORKS R1/R2 that require department-owned
  `check_mworks_gui_sentinel.py` plus `capture_window_background.ps1`, concrete
  `activation_state_observation`, concrete `license_state`, no-click pledge,
  `mworks_window_evidence_touched=true`, and `live_mworks_touched=false`.
- Both 019 task packets passed JSON parse,
  `Scripts/quality/check_mworks_live_gate.py --kind task --expect department`,
  and `Scripts/quality/check_agent_task_native_surface_gate.py --strict`.
  PMO also patched two wording risks found by a read-only subagent: AGENTS now
  says GUI sentinel and background screenshot are both required, and
  `agent_orchestration.md` distinguishes blocker category `license_or_login`
  from concrete `license_state` values.
- Native visible-thread delivery failed for MWORKS R1 and R2. With a settings
  override, both failed on `failed to update thread settings`; without override,
  both failed on `failed to start turn`; all failures ended with `agent loop
  died unexpectedly`. CoAgentOps also failed to start a diagnostic turn through
  the same native route. PMO wrote blocker packets for R1, R2, and CoAgentOps
  dispatch-surface failure.
- Boundary: this is Codex App visible-thread dispatch-surface evidence, not
  MWORKS activation/license/GUI/MCP/model/solver evidence. The 019 drills are
  not executed by R1/R2 yet. Do not route production MWORKS business work until
  the visible-thread surface is restored and the target department completes a
  current-turn screenshot/activation preflight packet that passes
  `check_mworks_live_gate.py --kind return --expect department`.
- PMO attempted a sparse WeChat alert with an obvious manual-intervention
  header, but the send reached the Weixin layer and returned `ret=-2`. No loop
  retry was attempted. The main conversation remains the active notification
  surface until the user sends one ordinary WeChat message to refresh the send
  context, after which PMO may retry once if the incident still needs WeChat.

## 2026-06-07 CST - UE 011 Static UI Binding Return Integrated

- PMO integrated UE Experiment Console return
  `RFLY-MOSIM-UE-CONSOLE-STATIC-UI-BINDING-PREFLIGHT-20260607-011`.
  The department completed a source/static UI-binding preflight checker for
  controller, planner, wind, fault, scene, reset, and recording controls. The
  checker keeps all controls pending or disabled until a future authoritative
  `mosim.ue_command_echo.v1` live echo row exists, and distinguishes future
  eligibility from actual UI enablement.
- PMO rechecked the return packet, reran the checker, ran the focused and
  existing UE console static tests, and diff whitespace checks passed. There is
  no 011 blocker packet.
- Boundary: 011 does not prove live UE runtime ack, live MWORKS downlink, ROS2
  runtime ack, Blueprint/UMG accepted-state implementation, planner readiness,
  controller performance, FAST-LIO success, final UI acceptance, mission
  success, or closed loop. Accepted-state controls remain disabled until an
  authoritative live echo producer exists.
- PMO also integrated ROS2 R1 blocker
  `RFLY-MOSIM-ROS2-RUNTIME-B1-INSTRUMENTED-PUBLISHER-RUNTIME-GATE-20260607-047`.
  The single allowed no-goal FAST-LIO-only live probe used an evidence-local
  instrumented publisher. Publisher trace was complete and monotonic, Livox and
  IMU source topics were monotonic, FAST-LIO outputs were nonzero and
  monotonic, forbidden planner/setpoint topics were absent, and cleanup was
  clean. The gate blocked because FAST-LIO still logged one callback-labeled
  `imu_cbk` loop-back.
- Boundary: 047 shifts suspicion away from publisher-side Livox timestamp
  assignment and toward FAST-LIO IMU callback/startup-buffer discipline, but it
  is not FAST-LIO success, TF/RViz readiness, localization/local-map quality,
  planner readiness, controller performance, mission success, or closed loop.
  Next ROS2 work must stay on the IMU callback/startup boundary before planner
  or TF/RViz readiness gates.

## 2026-06-07 CST - MWORKS Per-Task Screenshot Gate Rechecked After User Correction

- User corrected the PMO again: every MWORKS department assignment must require
  the target department to screenshot/check activation state itself before
  business work, because activation drift can appear as solver, GUI, or MCP
  errors and departments were not reliably reporting it.
- PMO ran a fresh read-only background recheck at 07:24 CST. The GUI sentinel
  was `clean`, and background capture showed one existing Sysplorer window in
  `[教育版]` with no visible login, activation, demo, authorization, mixed-state,
  or error-report dialog. PMO did not click, open, close, restart, call MWORKS
  MCP, or run model operations. This remains context only, not reusable
  readiness evidence.
- PMO revalidated the latest R1/R2 current activation preflight return packets:
  both pass `Scripts/quality/check_mworks_live_gate.py --kind return --expect
  department`. Future MWORKS business returns/blockers that omit current-turn
  sentinel/background screenshot evidence, `activation_state_observation`,
  concrete `license_state`, `will_not_click_activation_login=true`,
  `mworks_window_evidence_touched=true`, or `live_mworks_touched` must be
  rejected or returned for correction before integration.
- The dispatch contract, helper, MWORKS skills, and orchestration docs already
  contain this rule. The operational acceptance rule is now stricter than a
  static ACK: the actual business packet must contain the evidence from that
  same task turn.
- PMO also hardened the general pre-dispatch native surface checker:
  MWORKS/Sysplorer/Syslab target task packets are now required to pass the
  MWORKS activation/screenshot task gate before dispatch. Focused tests pass,
  and current MWORKS 016 plus ROS2 047/UE 011 task packets still validate.

## 2026-06-07 CST - ROS2 047 And UE 011 Dispatched While MWORKS Business Remains Gated

- PMO validated and dispatched ROS2 047 to
  `MoSim｜ROS2感知定位与规划运行部-R1`. 047 is a bounded no-goal
  FAST-LIO-only instrumented publisher runtime gate after 046, with
  evidence-local instrumentation only. It forbids RViz2, UE, planner/EGO,
  PositionCommand, 20 Hz adapter, TF bridge, active `/tf`, production
  source/config/extrinsic/frame/source-data edits, fake inputs, and repeated
  live probes.
- PMO validated and dispatched UE 011 to
  `MoSim｜UE实验控制台与场景交互部`. 011 is a source/static UI binding
  preflight task after UE 010, keeping experiment-console accepted-state
  controls disabled/pending until future authoritative
  `mosim.ue_command_echo.v1` live echo rows exist. It forbids UE GUI, Unreal
  build, runtime receiver implementation, Blueprint/UMG/assets edits,
  MWORKS/ROS2/FAST-LIO/planner/UE runtime calls, and accepted-state enablement.
- Both packets passed JSON parse and
  `Scripts/quality/check_agent_task_native_surface_gate.py --strict` before
  dispatch. Their ledger rows are now `dispatched-running`.
- Boundary: 047/011 do not prove FAST-LIO success, TF/RViz readiness, live UE
  runtime ack, live MWORKS downlink, ROS2 runtime ack, planner readiness,
  controller performance, mission success, final UI acceptance, or closed loop.
  MWORKS production business remains gated by per-task department-owned
  activation/screenshot preflight and current visible-thread recovery state.

## 2026-06-07 CST - MWORKS Activation Screenshot Rule Reaffirmed And Current PMO Check

- User again reported that MWORKS activation can drift between assignments and
  that MWORKS departments must learn to notice activation/login/GUI incidents
  themselves instead of continuing solver, model, layout, Smart Layout, or MCP
  retries. PMO treated this as a mandatory dispatch acceptance rule.
- PMO ran a read-only current check at 07:11 CST using only
  `Scripts/agent/check_mworks_gui_sentinel.py` and
  `Scripts/tools/capture_window_background.ps1`. The sentinel was `clean`, and
  the background screenshot captured one existing Sysplorer window titled with
  `[教育版]`; no visible demo, login, activation, authorization, mixed-state, or
  GUI error-report dialog was observed. PMO did not click, open, close,
  restart, recover login, call MWORKS MCP, or run model operations.
- This PMO check is context only. It is not reusable readiness evidence and
  does not prove package acceptance, graphical/layout acceptance,
  `check_model`, simulation, controller performance, live runtime ack,
  `planner_ready`, or `closed_loop`.
- Future MWORKS R1/R2 business dispatches, including static model
  organization and graphical-review preparation, must still start with the
  target department's own current-turn GUI sentinel plus background screenshot.
  Return/blocker packets must include `activation_state_observation`,
  `license_state`, sentinel and screenshot evidence, the no-click pledge,
  `mworks_window_evidence_touched=true`, and `live_mworks_touched`, then pass
  `Scripts/quality/check_mworks_live_gate.py --kind return --expect
  department`.
- R1 and R2 have both received the hard-gate reminder in visible threads. New
  production MWORKS business work remains gated by the current visible-thread
  start-turn recovery state and by the per-task department-owned screenshot
  preflight; PMO must reject any MWORKS return/blocker that omits this evidence
  or uses vague activation/license labels such as `ok`, `normal`, or
  `looks_fine`.

## 2026-06-07 CST - ROS2 046 And UE 010 Static Returns Integrated

- PMO integrated ROS2 R1 return
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PUBLISHER-TIMESTAMP-INSTRUMENTATION-STATIC-OR-BOUNDED-PROBE-20260607-046`.
  046 completed as a static publisher-side timestamp instrumentation design:
  it did not run a ROS2 live graph, did not start FAST-LIO/RViz2/UE/planner,
  did not publish planner/setpoint topics, and did not edit production ROS2
  packages, source data, config, extrinsics, frame adapters, MWORKS, UE,
  controller, or planner files. The return uses one disposable read-only
  subagent and recommends the next runtime diagnostic only as a separate
  evidence-local instrumented publisher build/run gate, because the current
  production publisher lacks publisher-side per-frame trace.
- PMO integrated UE Experiment Console return
  `RFLY-MOSIM-UE-CONSOLE-SOURCE-STATIC-RECEIVER-SHELL-CONTRACT-DESIGN-20260607-010`.
  010 completed as source-static receiver-shell contract design only. The
  future receiver must be a separate project-owned command echo receiver or
  adapter for `mosim.ue_command_echo.v1`, must sink into
  `UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson`, and
  must reject smoke/source/preflight rows, UDP send success, and
  `quadrotor.unreal_state` frame/status downlink as live command ack. Static
  checkers passed, while live runtime receiver implementation and accepted-state
  UI binding remain explicitly unsafe.
- Boundary: neither 046 nor 010 proves FAST-LIO success, TF/RViz readiness,
  localization/local-map quality, live UE runtime ack, live MWORKS downlink,
  ROS2 runtime ack, planner readiness, controller performance, mission success,
  final UI acceptance, or closed loop. Next ROS2 work must be a separately
  scoped evidence-local instrumented publisher runtime gate; next UE work may
  be static UI binding contract preflight or later source-static receiver-shell
  implementation, not runtime receiver acceptance.

## 2026-06-07 CST - ROS2 045 And UE 009 Static Returns Integrated

- PMO integrated ROS2 R1 return
  `RFLY-MOSIM-ROS2-RUNTIME-B1-LIVOX-FASTLIO-STARTUP-DDS-STATIC-DIAG-20260607-045`.
  045 is static-only: it ran no new ROS2 live graph/probe, made no production
  source/config/extrinsic/frame edits, and used one disposable read-only
  subagent for a static QoS/startup/source timestamp audit. Classification is
  startup/subscriber-load-sensitive Livox node-`now()` stamp regression with
  FAST-LIO present; source JSONL ordering, `/clock`, `use_sim_time`, multiple
  Livox publishers, and IMU source-topic regression are not supported as root
  causes. Next safe ROS2 gate is a separately scoped evidence-local publisher
  timestamp instrumentation task, not planner/RViz/TF/UE/PositionCommand work.
- PMO integrated UE Experiment Console return
  `RFLY-MOSIM-UE-CONSOLE-STATIC-NEXT-GATE-AUDIT-20260607-009`. 009 is a static
  next-gate audit only: existing static checkers passed, a disposable read-only
  subagent confirmed the 004-008 evidence boundary, and no UE GUI/build/source
  edit/assets/runtime receiver/UI accepted-state/MWORKS/ROS2 runtime action
  occurred. Recommended next UE gate is source-static receiver-shell contract
  design before any runtime receiver implementation; UI binding contract
  preflight remains second and static-only.
- Boundary: neither 045 nor 009 proves FAST-LIO success, TF/RViz readiness,
  localization/local-map quality, planner readiness, live UE runtime ack, live
  MWORKS downlink, ROS2 runtime ack, controller performance, mission success,
  final UI acceptance, or closed loop.

## 2026-06-07 CST - ROS2 044 FAST-LIO-Only Retest Blocked By Livox Stamp Regression

- PMO integrated ROS2 R1 blocker
  `RFLY-MOSIM-ROS2-RUNTIME-B1-FASTLIO-ONLY-FULL-WINDOW-RETEST-20260607-044`.
  The target thread completed the task and wrote a blocker, not a return.
- 044 ran exactly one no-goal FAST-LIO-only full-window probe after 043. The
  accepted source window still had 120 `body_lidar_m_z_up` frames and source
  JSONL time monotonicity. Runtime captured Livox `120/120` and IMU `2433`
  samples; IMU stamps were monotonic.
- The gate blocked because Livox source-topic header stamps regressed once at
  runtime by about `-2.84 s` between the first two captured topic samples, and
  the FAST-LIO full log contained one `livox_pcl_cbk` loop-back. FAST-LIO did
  publish nonzero monotonic `/Odometry` and `/cloud_registered`, but that does
  not clear the blocker.
- Boundary: 044 proves only that adding FAST-LIO reproduced an early Livox
  stamp regression plus one FAST-LIO Livox callback loop-back in the single
  allowed full-window probe. It does not prove FAST-LIO success, TF/RViz
  readiness, localization/local-map quality, planner readiness, controller
  performance, mission success, or closed loop. Next ROS2 work must stay at
  evidence-local source publisher / DDS subscriber-load / FAST-LIO callback
  timing diagnosis; do not dispatch planner, RViz2, UE, PositionCommand, 20 Hz
   adapter, TF bridge, source/config/extrinsic/frame edits, or fake inputs from
   this evidence.

## 2026-06-07 CST - MWORKS Department Activation Gate Hardened After Drift Report

- User reported that MWORKS activation had drifted again and that specialist
  threads still were not reliably returning screenshots or activation blockers.
  PMO treated this as a dispatch/acceptance loophole, not as a model, solver, or
  controller problem.
- Updated the MWORKS dispatch helper, communication contract, orchestration
  workflow, and AGENTS rule so every MWORKS R1/R2 business task treats the
  department-owned GUI sentinel plus background screenshot as the first business
  gate in that same turn. PMO-side screenshots, old 014/015/016 drills, and
  static ACK packets are context only; they cannot satisfy a later business
  assignment.
- Tightened `Scripts/quality/check_mworks_live_gate.py`: return/blocker packets
  are now rejected when sentinel or screenshot fields are empty placeholders,
  `activation_state_observation` is a vague short ACK, or `license_state` is not
  a concrete classification such as education-clean, mixed/demo blocked,
  login/activation required, authorization failed, GUI error-report blocked,
  sentinel unavailable, or unknown blocked.
- Added regression tests for vague observations, empty evidence placeholders,
  and unclassified license states. Boundary: this is enforcement/training
  infrastructure only. It does not prove current MWORKS readiness, package
  acceptance, check_model, simulation, graphical/layout acceptance, controller
  performance, planner readiness, runtime ack, or closed loop.
- PMO ran one read-only current context check at 06:19 CST using the project
  GUI sentinel and background screenshot scripts only. It observed one matching
  Sysplorer window in `[教育版]` and no sentinel incident. This is PMO context
  only, not reusable readiness evidence; every future R1/R2 business task still
  needs fresh department-owned preflight evidence in that task.
- R2 received the hardened rule sync and wrote
  `MWORKS-R2-ACTIVATION-SCREENSHOT-GATE-HARDENING-ACK-20260607-018`. The ACK is
  static rule synchronization only; R2 did not run GUI/MCP/model/screenshot work
  in that turn. R1 production routing remains paused because CoAgentOps 017
  classified the R1 visible-thread surface as `partial_recovery`: readable, but
  a fresh no-op start-turn still fails with an agent-loop error. Do not dispatch
  new R1 business work until Codex++ restart recovery plus one no-op validation
  restores the thread, or PMO/user explicitly authorizes a temporary route.
- PMO also fixed the background screenshot helper so
  `capture_manifest.json` is written as UTF-8 without BOM. The old PowerShell
  default could make strict Python JSON parsing fail before a department even
  classified activation state. A fresh PMO context capture parsed with
  `python -m json.tool`, and the MWORKS live-gate tests still pass.

## 2026-06-07 CST - ROS2 044 FAST-LIO-Only Full-Window Retest Dispatched

- PMO validated task packet
  `RFLY-MOSIM-ROS2-RUNTIME-B1-FASTLIO-ONLY-FULL-WINDOW-RETEST-20260607-044`
  after 043 proved the complete source-only Livox/IMU window is monotonic.
  JSON parse, `check_agent_task_native_surface_gate.py --strict`, and scoped
  `git diff --check` passed. No 044 return/blocker existed at dispatch time.
- PMO added 044 to the task ledger and dispatched it to
  `MoSim｜ROS2感知定位与规划运行部-R1` through the native visible-thread surface.
  The target thread is active and has started reading the 044 packet plus
  043/041/042 evidence.
- 044 is intentionally narrow: at most one no-goal FAST-LIO-only live probe,
  using 043 as the source-clean precondition. RViz2, UE, planner/EGO,
  PositionCommand, 20 Hz adapter, TF bridge, active `/tf` recorder, production
  edits, fake data, and repeated retries remain forbidden. A successful return
  may only classify the FAST-LIO-only callback/source-output boundary, not
  TF/RViz readiness, localization/local-map quality, planner readiness,
  controller performance, mission success, or closed loop.

## 2026-06-07 CST - MWORKS Activation Screenshot Gate Reaffirmed After User Report

- After the user reported that MWORKS activation state had drifted again, PMO
  reran only the read-only existing-window evidence route at 05:26 CST. The
  Win32 GUI sentinel was `clean`, and the background capture matched one
  existing Sysplorer window titled with `[教育版]`. PMO did not click
  login/activation/close/restart/send-report, did not open or close MWORKS,
  and did not call MWORKS MCP/model operations.
- This PMO-side observation does not replace department evidence. Future MWORKS
  R1/R2 assignments, including static model organization and graphical/layout
  review prep, must still start with the target department personally running
  `check_mworks_gui_sentinel.py` plus `capture_window_background.ps1`, writing
  `activation_state_observation`, and passing
  `check_mworks_live_gate.py --kind return --expect department`.
- If a department sees `[演示版]`, login/activation/authorization symptoms,
  mixed state, unknown sentinel state, or unavailable screenshot/sentinel
  tooling, it must return a blocker instead of trying solver, model, layout, or
  MCP retries. Live MWORKS acceptance remains task-local; no later dispatch may
  reuse this PMO check or 016 as readiness evidence.
- 05:38 CST follow-up: PMO repeated the same read-only route after the user
  reported another activation drift. The matched existing Sysplorer window was
  still `[教育版]`, but PMO treated this only as context. PMO sent explicit
  hard-gate ACK prompts to both MWORKS R1 and R2; both confirmed that every
  later MWORKS business task must begin with department-owned GUI sentinel plus
  background screenshot evidence, and that demo/login/authorization/mixed/
  unknown or unavailable evidence must become a blocker before solver, model,
  layout, MCP, or GUI retries. PMO will reject or return-for-fix any future
  MWORKS department return/blocker that lacks `activation_state_observation`,
  screenshot/sentinel evidence, the no-click pledge, and
  `check_mworks_live_gate.py --expect department` validation.
- 05:58 CST follow-up: PMO repeated the same read-only existing-window route
  and manually inspected the captured background screenshot. The sentinel was
  `clean`, and the captured Sysplorer window title was still `[教育版]`, with no
  visible login, activation, authorization, demo, or error-report dialog in
  that screenshot. PMO also revalidated the latest R1/R2 016 task and return
  packets with `check_mworks_live_gate.py --kind task|return --expect
  department`; all four checks returned `ok=true`. This remains only a
  point-in-time PMO observation and department-training verification. It is not
  reusable MWORKS readiness evidence for later assignments; each future MWORKS
  business dispatch must repeat the department-owned sentinel and background
  screenshot preflight in that task.
- 06:05 CST dispatch-surface follow-up: PMO attempted to send a fresh hard-gate
  synchronization prompt to MWORKS R1. The first native visible-thread send
  failed while updating thread settings, and a second send without model/
  thinking overrides failed while starting the turn; both reported an internal
  agent-loop failure. PMO wrote blocker
  `PMO-MWORKS-R1-DISPATCH-SURFACE-20260607-017` and routed bounded diagnosis to
  `MoSim｜CoAgent运维平台`. This is a Codex App visible-thread dispatch-surface
  incident, not MWORKS license, GUI, MCP, model, or solver evidence. R1's
  earlier 014/015/016 department-owned screenshot/sentinel preflights remain
  valid training evidence, but new live MWORKS R1 work should wait for
  dispatch-surface diagnosis or an explicit temporary route.

## 2026-06-07 CST - ROS2 043 Source Full-Window Timestamp Discipline Passed

- PMO integrated ROS2 R1 return
  `RFLY-MOSIM-ROS2-RUNTIME-B1-SOURCE-FULL-WINDOW-TIMESTAMP-DISCIPLINE-20260607-043`
  and inspected its evidence. 043 used exactly one source-only full-window live
  probe after static review showed 040/041 only covered active prefixes.
- Evidence: the accepted finite source file has 120 `body_lidar_m_z_up`
  frames, and the source-only run delivered Livox `120/120` with zero header
  stamp regressions plus IMU `2413` samples with zero header stamp regressions.
  `/clock` was absent, both source nodes reported `use_sim_time=false`, and
  forbidden planner/setpoint topics were absent. Cleanup reported no matching
  leftover processes.
- Boundary: 043 proves only source/full-window Livox and IMU timestamp
  discipline under source-only load. It does not prove FAST-LIO success,
  TF/RViz readiness, localization/local-map quality, planner readiness,
  controller performance, mission success, or closed loop. It also does not
  authorize source/config/extrinsic/frame edits.
- Next safe ROS2 step is a separately scoped FAST-LIO-only retest or
  subscriber-boundary diagnostic using 043 as the source-clean precondition.
  Keep RViz2, UE, planner/EGO, PositionCommand, 20 Hz adapter, TF bridge, active
  `/tf` recorder, and production edits out of that next task unless separately
  authorized.

## 2026-06-07 CST - ROS2 042 Static Boundary Diagnosis Integrated And 043 Prepared

- PMO integrated ROS2 R1 return
  `RFLY-MOSIM-ROS2-RUNTIME-B1-FASTLIO-CALLBACK-DDS-BOUNDARY-DIAG-20260607-042`
  and recorded a disposable read-only subagent audit. 042 completed as a
  static-first diagnosis; no live probe was run.
- Classification: 041 is not a contradiction. The active recorder observed a
  monotonic Livox/IMU prefix, while FAST-LIO remained subscribed across more of
  the finite replay and compared delivered header stamps against persistent
  callback-local `last_timestamp_*` state. Source publishers stamp with node
  `now()`, so the next proof point is full-window source timestamp discipline,
  not TF/RViz or planner work.
- Boundary: 042 does not prove FAST-LIO success, TF/RViz readiness,
  localization quality, local-map quality, planner readiness, controller
  performance, mission success, or closed loop. It also does not prove DDS as
  the sole root cause or justify source/config/extrinsic/frame edits.
- PMO prepared
  `RFLY-MOSIM-ROS2-RUNTIME-B1-SOURCE-FULL-WINDOW-TIMESTAMP-DISCIPLINE-20260607-043`
  for ROS2 R1. 043 is source-only/full-window by default: static-first, at most
  one source-only full-window live probe, no FAST-LIO/RViz2/UE/planner/EGO/
  PositionCommand/20Hz adapter/TF bridge/active `/tf` recorder, no production
  edits, and no planner/setpoint topics.

## 2026-06-07 CST - MWORKS Current Activation Preflight 016 Completed

- PMO repeated a read-only current-window activation check at 04:47 CST after
  the user pointed out that MWORKS departments must learn to screenshot/check
  activation state on every assignment. The sentinel was `clean`, and the
  background capture matched one existing Sysplorer window titled with
  `[教育版]`; PMO did not click login/activation/close/restart/send-report, did
  not call MWORKS MCP/model operations, and did not open a new MWORKS window.
- This PMO check is context only. PMO created and validated
  `PMO-MWORKS-R1-CURRENT-ACTIVATION-PREFLIGHT-20260607-016` and
  `PMO-MWORKS-R2-CURRENT-ACTIVATION-PREFLIGHT-20260607-016`, then dispatched
  both through native visible-thread messaging. R1 and R2 both completed the
  task: each department ran the sentinel/background screenshot itself, wrote
  `activation_state_observation` from the actual observed `[教育版]` Sysplorer
  window, did not call MWORKS MCP/model/GUI operations, and passed
  `Scripts/quality/check_mworks_live_gate.py --kind return --expect department`.
- PMO inspected both target visible-thread turns and both are completed, not
  half-running. PMO also repeated a read-only current check at 04:58 CST; it was
  still `clean` and captured only one existing `[教育版]` Sysplorer window.
- 2026-06-07 05:12 CST follow-up: after the user again questioned activation
  drift and department reporting habits, PMO repeated the same read-only route
  without touching MWORKS/MCP/model/GUI actions. The sentinel was still
  `clean`, the background screenshot showed the existing Sysplorer window in
  `[教育版]`, and PMO visually inspected the captured PNG for this check. PMO
  did not reproduce a visible `[演示版]`, login, activation, authorization, or
  error-report dialog in this check.
- Boundary: 016 is department preflight habit enforcement only. It is not
  MWORKS model evidence, package acceptance, graphical/layout acceptance,
  simulation, controller performance, planner readiness, live runtime ack, or
  closed-loop evidence. Every future MWORKS R1/R2 business dispatch must repeat
  the same department-owned preflight for that specific task; 016 cannot be
  reused as readiness evidence for later model, solver, layout, or GUI work.
  PMO must reject or return-for-fix any future MWORKS department return/blocker
  packet that omits `activation_state_observation`, background screenshot/
  sentinel evidence, `mworks_window_evidence_touched=true`, the no-click pledge,
  or the `check_mworks_live_gate.py --expect department` result. If either
  department reports demo/login/authorization/mixed/unknown/unavailable state,
  PMO must keep live MWORKS work blocked and must not let the department
  continue solver, model, or layout retries.

## 2026-06-07 CST - PMO Rechecked MWORKS Window State Without Replacing Department Preflight

- After the user reported that MWORKS activation had dropped again, PMO ran
  only the read-only existing-window GUI sentinel and background capture route.
  No login, activation, close, restart, save, report, MCP model operation, or
  new MWORKS window was touched.
- The PMO-side sentinel at 04:35 CST was `clean`, and the background capture
  matched one visible Sysplorer window titled with `[教育版]`. PMO did not see a
  matching `[演示版]` window in this check.
- Boundary: this PMO observation is not MWORKS model evidence and does not
  replace department-owned preflight. Every future MWORKS R1/R2 business
  dispatch still requires the target department itself to run
  `check_mworks_gui_sentinel.py` plus `capture_window_background.ps1`, report
  `activation_state_observation`, and pass
  `Scripts/quality/check_mworks_live_gate.py --kind return --expect department`.
  If the department sees demo/login/activation/authorization/mixed/unknown
  state, it must return a blocker instead of trying solver/model/layout fixes.

## 2026-06-07 CST - ROS2 041 Blocked By FAST-LIO Callback Loopback And 042 Prepared

- PMO integrated the ROS2 041 blocker and the disposable read-only subagent
  audit. The single allowed FAST-LIO-only no-goal probe kept RViz2, UE,
  planner/EGO, PositionCommand, 20 Hz adapter, TF bridge, active `/tf`
  recorder, source/config/extrinsic/frame edits, and repeated retries out of
  scope.
- Recorder-observed source-topic stamps stayed nonzero and monotonic
  (`Livox=40`, `IMU=80`), and FAST-LIO outputs were nonzero/monotonic
  (`/Odometry=29`, `/cloud_registered=29`). However, the FAST-LIO full log
  still reported two callback-labeled loop-back events: `imu_cbk=1` and
  `livox_pcl_cbk=1`.
- Classification: 041 proves that adding FAST-LIO back as the only material
  variable can reproduce internal callback loop-back while the recorder sees
  source-topic stamps as monotonic. It does not prove source-topic stamp
  rollback, does not prove an algorithm-body root cause, and is only medium
  confidence from one isolated probe.
- PMO prepared
  `RFLY-MOSIM-ROS2-RUNTIME-B1-FASTLIO-CALLBACK-DDS-BOUNDARY-DIAG-20260607-042`
  as the next static-first ROS2 R1 diagnostic. The task is constrained to
  FAST-LIO callback-local timestamp state, DDS queue/stale delivery, and finite
  replay startup/end boundary analysis, with at most one no-goal FAST-LIO-only
  probe only if static evidence cannot answer the boundary question.
- Boundary: do not advance to planner, RViz, PositionCommand, 20 Hz adapter,
  UE, TF/RViz readiness, localization/local-map quality, planner readiness,
  controller performance, mission success, or closed loop from 041.

## 2026-06-07 CST - MWORKS Activation Observation Gate Added And R1/R2 Refresh Dispatched

- User corrected that MWORKS departments must not only run activation
  screenshot/sentinel checks, but must also report what the screenshot or
  window title actually showed before doing any MWORKS business work.
- PMO added the required return/blocker field
  `activation_state_observation` to the MWORKS live gate. A packet can no
  longer pass by only filling a summarized `license_state`; it must record the
  observed activation evidence such as education marker, demo marker, login or
  activation prompt, mixed state, unknown state, or unavailable evidence.
- Updated the machine checker, dispatch helper, communication contract,
  orchestration workflow, and MWORKS skills. Targeted live-gate tests passed.
- PMO wrote and validated single-target refresh packets for MWORKS R1 and R2,
  then dispatched them by native visible-thread messaging. They are instructed
  to run only the GUI sentinel and background screenshot, write
  `activation_state_observation`, and return a blocker instead of solver,
  layout, or model retries if activation is unsafe.
- MWORKS R1 returned a valid packet: it ran the sentinel and background
  screenshot itself, observed the existing Sysplorer window title with
  `[教育版]`, wrote `activation_state_observation`, did not touch MWORKS MCP or
  model work, and passed the department return gate.
- MWORKS R2 also returned a valid packet with the same bounded behavior: it ran
  sentinel/background capture itself, observed one existing education-mode
  Sysplorer window, wrote `activation_state_observation`, did not touch MWORKS
  MCP/model/GUI operations, and passed the department return gate.
- PMO also ran a read-only background evidence check and the currently matched
  Sysplorer window title showed `[教育版]`. This is PMO-side evidence only; it
  is not a replacement for R1/R2 department-owned return packets.
- Historical 014 return packets predate `activation_state_observation`, so they
  intentionally fail the new stricter checker and must not be treated as the
  new acceptance baseline.

## 2026-06-07 CST - ROS2 040 Source-Only Stamp Origin Passed And 041 Prepared

- ROS2 R1 completed
  `RFLY-MOSIM-ROS2-RUNTIME-B1-SOURCE-ONLY-CLOCK-DDS-STAMP-ORIGIN-20260607-040`
  as a source-only stamp-origin classification gate.
- The single source-only probe did not reproduce the 039 Livox/IMU timestamp
  rollback. FAST-LIO, RViz2, UE, planner/EGO, PositionCommand recorder, 20 Hz
  adapter, TF bridge, and active `/tf` recorder were absent.
- Livox and IMU source samples were nonzero and monotonic
  (`Livox=40`, `IMU=80`, no regressions). `/clock` was absent, source nodes
  reported `use_sim_time=false`, each source topic had one publisher with GID
  evidence, forbidden planner/setpoint topics were absent, and cleanup was
  clean.
- PMO also ran a disposable read-only audit of the 040 packet/evidence. The
  audit agrees that 040 is enough to add FAST-LIO back as the only material
  variable; it does not justify direct publisher/source edits yet.
- PMO prepared
  `RFLY-MOSIM-ROS2-RUNTIME-B1-FASTLIO-ONLY-STAMP-LOOPBACK-ISOLATION-20260607-041`
  for ROS2 R1. 041 is a bounded no-goal probe that adds FAST-LIO only and still
  forbids RViz2, UE, planner/EGO, PositionCommand, 20 Hz adapter, TF bridge,
  active `/tf` recorder, source/config/extrinsic edits, and repeated retries.
- Boundary: 040 is not FAST-LIO success, TF/RViz readiness, localization
  quality, local-map quality, planner readiness, controller performance,
  mission success, or closed-loop evidence.

## 2026-06-07 CST - MWORKS Department-Owned Activation Screenshot Drill Superseded

- PMO closed the latest MWORKS coordination gap after the user pointed out that
  departments must learn to detect activation loss themselves instead of relying
  on PMO noticing a GUI state change.
- The MWORKS R1/R2 dispatch template now embeds the exact existing-window
  sentinel and background screenshot commands and requires the target
  department to run them before any MWORKS business work. If a department cannot
  run the tools, it must return a blocker with
  `license_state=sentinel_unavailable_blocked` and must not continue model/MCP
  retries.
- PMO dispatched
  `PMO-MWORKS-R1R2-BACKGROUND-SCREENSHOT-ACTIVATION-DRILL-20260607-014` to
  MWORKS R1 and R2. Both departments ran the Win32 GUI sentinel plus background
  screenshot route themselves, returned required planning/subagent fields,
  confirmed the no-click pledge, and did not call MWORKS MCP, load/check/
  translate/simulate, Smart Layout, GUI edit, click, open, close, or restart.
- Historical correction: the 014 return packets predate the later
  `activation_state_observation` hard field and fail the current
  `Scripts/quality/check_mworks_live_gate.py --kind return --expect department`
  check. They prove the departments attempted the screenshot/sentinel route,
  but they are not current-format acceptance packets and must not be reused as
  the template for future MWORKS business dispatches.
- Current accepted examples are the later 015/016 MWORKS preflight packets,
  which include `activation_state_observation`, classify what the screenshot or
  window title actually showed, and pass the department live-gate checker.
- This is only MWORKS dispatch-safety evidence. It is not model/package
  acceptance, graphical/layout acceptance, simulation success, controller
  performance, planner readiness, live runtime ack, or closed loop.
- PMO attempted the required sparse completion WeChat notification for this
  gate, but outbound WeChat returned `ret=-2`; the failure was recorded in the
  gateway audit/recovery records and dispatched to WeChat Gateway Ops R3 through
  native Codex thread messaging. Do not assume the completion notice reached
  WeChat. This gateway incident does not block the MWORKS dispatch gate itself.

## 2026-06-07 CST - MWORKS Window Evidence Gate Tightened

- User corrected that every MWORKS dispatch must force the department to check
  activation state with background screenshot/sentinel evidence; departments
  must learn this route and return blockers instead of continuing solver/model
  trial-and-error when activation drops.
- PMO reran read-only evidence and confirmed the current reusable MWORKS state
  is still mixed: one Sysplorer window is `[教育版]` and another relevant
  `QuadrotorControllerBlocks` Sysplorer window is `[演示版]`.
- The MWORKS live gate now has three explicit cases: pure static file-only
  (`live_mworks_touched=false` and no window evidence), window-evidence tasks
  (`live_mworks_touched=false`, `mworks_window_evidence_touched=true`, full
  sentinel/screenshot/license/no-click fields), and real live MCP/model/GUI
  work (`live_mworks_touched=true`, full gate).
- `Scripts/quality/check_mworks_live_gate.py` now rejects packets that include
  activation/screenshot sentinel evidence but omit
  `mworks_window_evidence_touched=true`. Targeted tests passed, and the current
  R1/R2 activation-practice blocker packets pass the tightened gate.
- PMO synced the refinement to MWORKS R1 and R2 as static ACK tasks. Both wrote
  ACK packets and both pass the static machine gate. These ACKs prove the
  department contract was received, but they are not MWORKS activation recovery
  evidence because no MWORKS/MCP/GUI/screenshot/model command was run.
- Until a clean activation sentinel identifies a valid reusable MWORKS session,
  do not dispatch live MWORKS MCP/model/GUI work. Static MWORKS file
  organization may continue only when it explicitly avoids window/MCP work.

## 2026-06-07 CST - MWORKS 008 Blocked By Alias Check And Demo Edition

- MWORKS R2 completed
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-PACKAGE-LIVE-VALIDATION-20260607-008`
  as a blocker, not a package acceptance.
- The pre-MCP GUI sentinel was clean and the existing Sysplorer session was
  reused. The new `QuadrotorControllerBlocks` package shell loaded, and
  `GetClasses(QuadrotorControllerBlocks)` showed seven category entries plus
  19 flat sibling entries.
- The representative category aliases did not pass: all six `check_model`
  probes failed with compiler error 3001 because the leading-dot global
  flat-class `extends` bases were not found in the observed Sysplorer context.
- The post-MCP GUI sentinel then detected a license/login incident: the
  Sysplorer window title matched `演示版`. PMO instructed R2 to stop live
  MWORKS/Sysplorer automation and write the blocker instead of continuing
  trial-and-error.
- PMO attempted one sparse WeChat intervention notice, but the gateway send
  failed with `ret=-2`. The failed send is recorded, a recovery packet was
  written, and the incident was forwarded to WeChat Gateway Ops R3. Do not
  assume the WeChat notification reached the user.
- WeChat Gateway Ops R3 classified the send failure as stale outbound WeChat
  context, not `no active session`. The required recovery is one fresh ordinary
  inbound user message in the WeChat gateway chat, then exactly one adapter
  retry for the original notification; if that still returns `ret=-2`, stop
  retries and run the documented QR setup route.
- Next: resolve or classify the Sysplorer demo-edition/license state before
  more live MWORKS validation. A separate static-only task may prepare a
  package-shell alias fix, but it must not claim live package acceptance until
  a clean sentinel + live rerun passes.

## 2026-06-07 CST - Sunray150 DAE Blender Visual Route Confirmed

- User confirmed the current DAE-derived Blender model is the Sunray150 visual
  asset route going forward. The active review model is
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend`.
- Sunray Asset/PBR Department removed the incorrect USB camera lens/barrel
  overlay after user review; camera bodies remain black PartBody material and
  the lens/barrel overlay should not be regenerated without a later reviewed
  geometry placement route.
- MID-360 is now on the deep-blue mirror-coated dome visual route with white
  strip reflection overlays for manual visual review. Guard/landing gear and
  propeller remain on the prior transparent glass/liuli review route.
- This confirms the visual asset route only. It is not final material
  acceptance, UE import/export final acceptance, geometry/extrinsic approval,
  MWORKS/ROS2/UE runtime evidence, controller performance, planner readiness,
  or closed loop.

## 2026-06-07 CST - ROS2 037 Clean TF Readiness Blocked

- ROS2 R1 completed the single allowed
  `RFLY-MOSIM-ROS2-RUNTIME-B1-CLEAN-TF-READINESS-NOGOAL-20260607-037`
  no-goal probe and wrote a blocker.
- Useful TF classification was captured: `camera_init -> body` and
  `ue_world -> base_link` were observed, while `ue_world <-> camera_init`
  remained absent.
- The run cannot be treated as clean TF/RViz readiness: Livox active stamps
  were nonmonotonic, and the FAST-LIO full log contained two callback-labeled
  loop-back events, `livox_pcl_cbk=1` and `imu_cbk=1`.
- FAST-LIO outputs were still nonzero/monotonic for this blocked run
  (`/Odometry=20`, `/cloud_registered=20`), forbidden planner/setpoint topics
  were absent, and cleanup was clean. This is blocker evidence, not a
  readiness pass.
- Do not advance to RViz manual quality acceptance, EGO/planner,
  PositionCommand, 20 Hz adapter, localization/local-map quality,
  planner_ready, controller performance, mission success, or closed loop from
  037. The next ROS2 task should diagnose the Livox timestamp regression and
  `livox_pcl_cbk` loop-back without creating the missing frame bridge.

## 2026-06-07 CST - QuadrotorControllerBlocks 008 Live Package Validation Dispatched

- PMO dispatched
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-PACKAGE-LIVE-VALIDATION-20260607-008`
  to MWORKS R2 after integrating the 007 static package-shell return and the
  037 ROS2 blocker.
- Scope remains live validation only: reuse the existing MWORKS/Sysplorer
  session, run GUI sentinel, run minimal MCP/session health, then load/check
  the new `QuadrotorControllerBlocks` package shell or representative aliases
  if the tool surface supports it.
- It still forbids opening/closing/restarting MWORKS, simulation, Smart Layout,
  model edits, diagram writeback, and graphical/layout/controller performance
  claims.

## 2026-06-07 CST - QuadrotorControllerBlocks 008 Live Package Validation Prepared

- PMO prepared
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-PACKAGE-LIVE-VALIDATION-20260607-008`
  as the next MWORKS R2 follow-up after 007.
- Scope is live validation only: reuse the existing MWORKS/Sysplorer session,
  run GUI sentinel, run minimal MCP/session health, then load/check the new
  `QuadrotorControllerBlocks` package shell or representative aliases if the
  tool surface supports it.
- It explicitly forbids opening/closing/restarting MWORKS, simulation, Smart
  Layout, model edits, diagram writeback, and graphical/layout acceptance
  claims. It is prepared but not dispatched yet.

## 2026-06-07 CST - QuadrotorControllerBlocks 007 Static Package Shell Completed

- MWORKS R2 completed
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-PACKAGE-SHELL-20260607-007`.
- It created only `Models/QuadrotorControllerBlocks/package.mo` and
  `package.order`: seven category packages with Chinese descriptions, and 19
  wrapper aliases that extend the current flat controller classes through
  leading-dot global references. The 19 existing controller `.mo` files and
  backup/upgrade histories were not edited.
- Static evidence passed: `package.order` has the seven approved categories,
  all 19 active controller classes are represented, alias targets come from the
  006 inventory, backup/upgrade directories are excluded, controller/backup
  hashes are unchanged, and scoped diff check passed.
- Evidence is under
  `Results/mworks_model_hygiene/20260607_007_quadrotor_controller_blocks_package_shell/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-PACKAGE-SHELL-20260607-007.json`.
- This is static package-shell organization only. It is not true namespace
  migration, not live Sysplorer package-browser acceptance, not `check_model`,
  not simulation, not graphical acceptance, not controller performance, and not
  closed loop. The next MWORKS R2 follow-up should live-validate package
  browser/load behavior through the existing MWORKS/Sysplorer session, with GUI
  sentinel and no simulation initially.

## 2026-06-07 CST - ROS2 037 Clean TF Readiness No-Goal Task Prepared

- PMO prepared
  `RFLY-MOSIM-ROS2-RUNTIME-B1-CLEAN-TF-READINESS-NOGOAL-20260607-037`
  for ROS2 R1.
- The task permits at most one no-goal runtime probe. It must preserve the 034
  active source/output acceptance discipline, minimize additional TF capture
  load, and require zero FAST-LIO loop-back before any clean TF readiness
  return.
- The task may observe `camera_init -> body`, `ue_world -> base_link`, and
  whether `ue_world <-> camera_init` already exists, but it must not create a
  frame bridge or enter planner/setpoint paths.
- Disposable read-only PMO subagent
  `019e9de4-7340-7413-af42-42b603788106` confirmed the boundary and one-live
  probe limit. PMO dispatched 037 to ROS2 R1 at 01:07 CST.
- This remains preflight evidence only. It cannot claim localization quality,
  local-map quality, planner readiness, mission success, controller
  performance, or closed loop.

## 2026-06-07 CST - ROS2 036 IMU Loop-Back Static Diagnosis Completed

- ROS2 R1 completed
  `RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-LOOPBACK-STARTUP-DIAG-20260607-036`
  as a static 034/035 runner/log diagnosis. It did not run a new live ROS2
  probe.
- Key finding: the 035 loop-back was callback-labeled `imu_cbk`, while LiDAR
  callback loop-back counts were zero. Active Livox/IMU recorder stamps were
  monotonic, `is_first_lidar=0`, active `/Odometry` and `/cloud_registered`
  were nonzero, and the event occurred after first LiDAR and after FAST-LIO
  outputs had started. This narrows the likely issue to an IMU callback
  stale/ordering race or sensitivity from the 035 active TF recorder/longer
  active window, not LiDAR source regression and not the earlier pre-first-LiDAR
  startup boundary.
- Evidence is under
  `Results/ros2_runtime/b1_imu_loopback_startup_diag_20260607_036/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-LOOPBACK-STARTUP-DIAG-20260607-036.json`.
- This is diagnostic evidence only. It does not claim FAST-LIO success,
  localization quality, local-map quality, TF/RViz readiness, planner readiness,
  controller performance, mission success, or closed loop. The next ROS2 gate
  should rerun a clean no-goal TF readiness probe with 034-style source/output
  acceptance preserved and minimum added TF recorder load.

## 2026-06-07 CST - QuadrotorControllerBlocks 007 Package Shell Prepared

- PMO prepared
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-PACKAGE-SHELL-20260607-007`
  for `MoSim｜MWORKS动力学与控制验证部-R2`.
- Scope is intentionally narrow: create only
  `Models/QuadrotorControllerBlocks/package.mo` and `package.order` as a
  categorized, Chinese-described package shell for the 19 active controller
  files already inventoried by 006. Existing controller `.mo` files,
  backup/upgrade directories, `QuadrotorExperiments`, `References`, UE/ROS2,
  controller configs, and planner configs are out of scope.
- If alias resolution cannot be made static-compatible because the existing
  controller files lack package-level `within` clauses, R2 must write a blocker
  instead of editing the controller files.
- This task is package organization only. It must not open/close/restart
  MWORKS, call MCP, run Smart Layout, run `check_model`, run simulation, or
  claim graphical acceptance/controller performance/planner readiness/live
  runtime ack/closed loop.

## 2026-06-07 CST - QuadrotorControllerBlocks 006 Read-Only Organization Plan Completed

- MWORKS R2 completed
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-ORGANIZATION-20260607-006`
  as a read-only package-shell/category-entry plan for
  `Models/QuadrotorControllerBlocks`. It inventoried 19 active top-level
  controller `.mo` files, confirmed there is currently no
  `package.mo/package.order`, separated five `*_backup/upgrade` history
  directories from the future public package surface, and proposed categories
  for AWFF PID blocks, innovation controllers, fault/allocation controllers,
  LinearMPC, safety controllers, demos/SIL, and future compatibility aliases.
- Evidence is under
  `Results/mworks_model_hygiene/20260607_006_quadrotor_controller_blocks_organization/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-ORGANIZATION-20260607-006.json`.
- This is planning evidence only. It did not create package files, edit `.mo`
  models, move/delete backups, open GUI/MCP, run Smart Layout, run
  `check_model`, run simulation, or prove graphical acceptance/controller
  performance/planner readiness/live runtime ack/closed loop.
- Next allowed MWORKS R2 follow-up is a separately scoped write gate to create
  only the package shell and static aliases, followed by a later serialized
  GUI/MCP load/check review using the existing MWORKS/Sysplorer session.

## 2026-06-07 CST - MWORKS Model Classification Split Updated

- PMO and disposable read-only subagent `019e9db5-4b60-7363-9c69-217384475756`
  rechecked the current `Models/` organization after the user repeated that
  the models are still not properly categorized.
- Current classification boundary:
  `Models/QuadrotorExperiments` is the only formal package with
  `package.mo/package.order`; its 11 category entries are a reasonable visible
  browser surface, but the old flat `.mo` classes remain compatibility load
  paths and must not be moved or deleted without a later migration gate.
  `Models/QuadrotorControllerBlocks` is now the clearest remaining
  organization problem: it is an important AWFF/INDI/L1/LinearMPC/QP-NMPC
  controller library, but it is still a loose folder without `package.mo`,
  `package.order`, or formal category entries.
- PMO prepared the next task packet
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-ORGANIZATION-20260607-006`
  as a read-only controller-library package plan for MWORKS R2. This was later
  completed; see the 006 completion entry above for the current state.
- The user directly assigned the Sunray/PBR follow-up to
  `MoSim｜Sunray150资产与PBR审核部`; PMO will not duplicate-dispatch that task.

## 2026-06-07 CST - QuadrotorExperiments 005 Visible Cleanup Completed

- MWORKS R2 completed
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-EXPERIMENTS-VISIBLE-CLEANUP-20260607-005`.
  Static validation passed: `package.order` now has exactly the 11 category
  entries, the four missing `TraceIsolation` aliases for Iso22/Iso28/Iso29/Iso30
  exist and extend the expected flat smoke models, 104 old flat entries remain
  statically resolvable, and all category alias targets resolved statically.
- Evidence is under
  `Results/mworks_model_hygiene/20260607_005_quadrotor_experiments_visible_cleanup/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-QUADROTOR-EXPERIMENTS-VISIBLE-CLEANUP-20260607-005.json`.
- This is visible package/display organization only. It is not live Sysplorer
  browser acceptance, not `check_model`, not simulation, not graphical
  acceptance, not Factory trace consumption, not controller performance, not
  planner readiness, and not closed loop.
- PMO is now dispatching
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-CONTROLLER-BLOCKS-ORGANIZATION-20260607-006`
  to R2 as the next read-only model classification task for
  `Models/QuadrotorControllerBlocks`.

## 2026-06-07 CST - QuadrotorExperiments 005 Visible Cleanup Prepared

- MWORKS R2 completed
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-EXPERIMENTS-ORGANIZATION-20260606-004`
  as a read-only organization plan. It confirmed the user-visible problem:
  the top-level `QuadrotorExperiments` browser still lists 104 flat legacy
  entries after the 11 category packages. It also confirmed the compatibility
  boundary: those flat classes still back current aliases, scripts, and
  evidence chains, so they must not be deleted or physically migrated in the
  first write slice.
- PMO prepared
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-EXPERIMENTS-VISIBLE-CLEANUP-20260607-005`
  for `MoSim｜MWORKS动力学与控制验证部-R2`. The narrow write scope is:
  add four missing `TraceIsolation` aliases for Iso22/Iso28/Iso29/Iso30, then
  reduce top-level `package.order` display to the 11 category packages while
  preserving old flat class definitions as compatibility load paths.
- This planned cleanup is package display/model hygiene only. It must not
  move/delete `.mo` files, open/close/restart MWORKS, call MCP, run Smart
  Layout, or claim check_model, simulation, graphical acceptance, controller
  performance, planner readiness, or closed loop.

## 2026-06-07 CST - Sunray150 PBR 005 Review Sheet Opened

- Sunray150 Asset/PBR Department completed
  `RFLY-MOSIM-SUNRAY150-PBR-ELECTRONICS-CAMERA-REALISM-20260606-005`
  as a review-ready component material pass, not final material acceptance.
  Evidence:
  `Results/unreal_scene_mapping/sunray150_pbr_electronics_camera_realism_20260606_005/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-SUNRAY150-PBR-ELECTRONICS-CAMERA-REALISM-20260606-005.json`.
- PMO opened the generated contact sheet for user review in the Codex app.
  The return packet was later updated after direct user correction: front and
  bottom camera PartBody objects were routed to black camera-body material, TF
  Mini was separated as a black laser rangefinder body, MID-360 was moved
  toward a glass/optical-dome material, motor gold-ring decal generation was
  removed, and propeller/guard review targets were moved toward transparent
  glass/liuli material. The correction contact sheet was generated for manual
  pass/fail review.
- This does not claim final material acceptance, UE import/export acceptance,
  runtime success, planner readiness, controller performance, or closed loop.

## 2026-06-07 CST - ROS2 035 Blocked On FAST-LIO IMU Loopback

- ROS2 R1 completed the single allowed no-goal TF/RViz gap diagnostic and wrote
  blocker
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-TF-RVIZ-READINESS-GAP-DIAG-20260606-035.json`.
  Active-window TF classification was useful: `camera_init -> body` and
  `ue_world -> base_link` were observed, while `ue_world <-> camera_init`
  bridge was absent.
- The task is still blocked because the same probe logged one FAST-LIO
  `imu_cbk` loop-back event. Therefore 035 cannot be promoted to TF/RViz
  readiness, localization quality, local-map quality, planner readiness, or
  closed-loop evidence. Do not enter RViz manual quality, EGO/planner,
  PositionCommand, 20 Hz adapter, extrinsic/frame edits, fake data, or
  planner/closed-loop claims from 035.
- PMO opened 036 as the next bounded ROS2 task:
  `RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-LOOPBACK-STARTUP-DIAG-20260607-036`.
  It may only compare 034/035 startup/logs and, if needed, run one no-goal
  diagnostic probe. It must not create a frame bridge, enter planner/setpoint
  paths, edit extrinsics/frame adapters/production ROS2 packages, or claim
  readiness.

## 2026-06-06 CST - PMO Dispatched QuadrotorExperiments Organization 004

- User confirmed `QuadrotorExperiments` is still not truly categorized in the
  model browser. PMO static scan and disposable read-only subagent
  `019e9d97-2540-70c1-a0d3-3ff48363b450` both found the same issue:
  `Models/QuadrotorExperiments/package.order` has 115 entries, where the first
  11 are category packages but 104 old flat legacy entries still remain at the
  top-level display surface.
- This corrects the boundary of the earlier 013 classification cleanup:
  013 added categorized compatibility entry points with Chinese descriptions,
  but it did not complete physical subpackage migration, hide/deprecate the
  flat compatibility surface, or remove old public class paths. Direct deletion
  is unsafe because current category aliases still extend many old flat classes
  and historical scripts/results may reference those paths.
- PMO created and dispatched
  `RFLY-MOSIM-MWORKS-R2-QUADROTOR-EXPERIMENTS-ORGANIZATION-20260606-004` to
  `MoSim｜MWORKS动力学与控制验证部-R2`
  (`019e9999-b0d3-7682-bccd-faef08fcf1df`). The task is read-only in this
  first pass: classify all 104 flat entries, propose keep/migrate/deprecate/
  delete-later actions, define compatibility strategy, and specify later write
  and verification gates. It must not edit `.mo`, `package.mo`,
  `package.order`, run GUI/MCP, or claim graphical/model/simulation evidence.

## 2026-06-06 CST - MWORKS R1 017 Completed Yaw Transient Observability Gate

- MWORKS R1 completed
  `RFLY-MOSIM-MWORKS-DYNAMICS-YAW-TRANSIENT-EVIDENCE-GATE-20260606-017`
  without model edits. P0 GUI sentinels were clean, Sysplorer MCP health/load
  worked under `mworks_window_policy=reuse_existing_do_not_close`, and
  `check_model` passed for the existing wrapper yaw-step, physical-wrench
  yaw-step, and Iso30 external-body state smokes.
- 0-0.25 s MWORKS_MCP smokes returned `data=true` and `GetVarTimes=251`.
  Evidence now classifies command-side yaw moment, lagged wrapper yaw moment,
  applied physical-wrench yaw torque, and external body yaw-rate response as
  observable. Representative samples: `wrapper.yaw_moment_gate@end =
  0.06153801695664962 N.m`, `adapter.applied_yaw_torque_body@end =
  0.061540561756854906 N.m`, and `external_body_yaw_rate@end =
  -0.4531353758463619 rad/s`.
- Evidence:
  `Results/mworks_dynamics_upgrade/20260606_017_yaw_transient_evidence_gate/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-YAW-TRANSIENT-EVIDENCE-GATE-20260606-017.json`.
  This is yaw transient observability only, not Factory trace consumption,
  full plant closure, controller performance, parameter identification,
  planner readiness, live runtime ack, mission success, or closed loop.

## 2026-06-06 CST - PMO Corrected MWORKS Window Reuse Policy

- PMO corrected the active MWORKS R1/R2 tasks after user review: Sysplorer /
  Syslab / MWORKS windows must not be closed as a default cleanup step.
  The current operating rule is to reuse the existing logged-in, license-active
  session and avoid new windows/restarts unless there is a proven freeze,
  login/license blocker, unrecoverable MCP/session failure, duplicate-window
  runaway, or explicit PMO/user approval.
- PMO pushed the correction to `MoSim｜MWORKS动力学与控制验证部-R1`
  (`019e9be5-334b-76b1-93f9-8b02caebf376`) and
  `MoSim｜MWORKS动力学与控制验证部-R2`
  (`019e9999-b0d3-7682-bccd-faef08fcf1df`). Active and future MWORKS
  return/blocker packets should record
  `mworks_window_policy=reuse_existing_do_not_close` when relevant.
- This is a workflow correction only. It is not MWORKS simulation evidence and
  does not change any dynamics/control/planner readiness claim.

## 2026-06-06 CST - MWORKS R1 016 Completed External Body State Boundary

- MWORKS R1 completed
  `RFLY-MOSIM-MWORKS-POST-ISO29-ONE-BOUNDARY-20260606-016`.
  It added `FactoryTraceIso30ExternalBodyStateBoundarySmoke` on the current
  project-owned `QuadrotorExperiments` package surface, extending Iso29 and
  adding only read-only external test-body state/motion response aliases/gates.
- P0 GUI sentinels were clean before and after; Sysplorer MCP health reused
  the existing session; targeted `model_manager(load_file, force_reload=true)`
  avoided `reload_mo_path`; Iso29/Iso30 `check_model` passed; 0-0.25 s
  `SimulateModel data=true`; `GetVarTimes=251`; sampled external body state
  response aliases were readable with
  `external_body_state_boundary_gate_error@end=0.0`.
- Evidence:
  `Results/mworks_dynamics_upgrade/20260606_016_post_iso29_one_boundary/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-POST-ISO29-ONE-BOUNDARY-20260606-016.json`.
  This is only minimal external body state response evidence, not Factory
  trace consumption, QuadChassis/full plant closure, controller performance,
  parameter identification, planner readiness, live runtime ack, mission
  success, or closed loop.

## 2026-06-06 CST - PMO Updated R1/R2 Routing And Opened Next P0 Tasks

- User renamed the MWORKS and ROS2 visible department threads. Current routing
  is now explicit: `MoSim｜MWORKS动力学与控制验证部-R1`
  (`019e9be5-334b-76b1-93f9-8b02caebf376`) owns MWORKS mainline
  dynamics/control/model-integration evidence, while
  `MoSim｜MWORKS动力学与控制验证部-R2`
  (`019e9999-b0d3-7682-bccd-faef08fcf1df`) is an auxiliary model
  organization / graphical interface / connection-layout / diagram hygiene
  reviewer. R2 is not business-ready until it passes a bounded sync-validation
  packet because it previously had dispatch/UI-submit instability.
- Current ROS2 mainline route is `MoSim｜ROS2感知定位与规划运行部-R1`
  (`019e9c72-ee74-79d1-b9fe-621d3c6fc99e`). Historical records may still use
  old R2/R3 labels; do not rewrite evidence history, but new dispatch follows
  `CoAgent/dispatch/department_threads.json`.
- PMO generated and displayed a Sunray150 component material contact sheet for
  manual review. This only surfaces the pending review images; it is not final
  material acceptance.
- User corrected PMO delivery behavior: human-review artifacts must be opened
  or displayed directly when available, not only reported as paths. PMO opened
  the Sunray150 component contact sheet in the Windows image viewer and
  selected it in Explorer; future review prompts should keep paths in packets
  and present the artifact itself to the user.
- PMO created the next three task packets: ROS2 033 to diagnose the 032
  loop-back/zero-output regression, MWORKS R1 016 to advance exactly one
  post-Iso29 physical/model boundary, and MWORKS R2 sync validation 001 before
  any auxiliary graphical-model audit work.
- PMO dispatched all three packets through native visible-thread delivery at
  22:29 CST. Delivery succeeded for ROS2 R1, MWORKS R1, and MWORKS R2
  sync-validation.
- MWORKS R2 sync validation returned `sync_validation_passed` at 22:32 CST.
  It proves only PMO dispatch receipt, turn start, context read, and return
  packet write. R2 can now receive explicitly scoped auxiliary model
  organization / graphical-layout audit tasks, but this is not MWORKS GUI/MCP
  or model-quality evidence.
- ROS2 R1 returned 033 as diagnostic-only at 22:56 CST. It found that 032 had
  early Livox and FAST-LIO output, then a real in-run Livox timestamp
  regression triggered callback-labeled FAST-LIO loop-back, and the later
  Livox/FAST-LIO acceptance windows sampled after the finite non-looping source
  was already consumed. This explains the zero-output window but does not
  restore no-goal preflight, planner readiness, RViz quality, or closed loop.
- PMO created the first real auxiliary MWORKS R2 task,
  `RFLY-MOSIM-MWORKS-R2-GRAPHICAL-MODEL-AUDIT-INVENTORY-20260606-002`.
  It is read-only static inventory/prioritization for graphical model/interface
  hygiene only; it forbids GUI/MCP, Smart Layout writeback, model edits, and
  simulation claims. Native visible-thread delivery to R2 succeeded.
- Dispatch packets now must explicitly require department-local planning and
  `subagent_plan` / `subagents_used`. When a safe independent slice exists, the
  target department should use disposable sub-agents; otherwise it must record
  why sub-agents are unavailable, unsafe, or not useful.

## 2026-06-06 CST - PMO Integrated MWORKS 015, ROS2 032 Blocker, And MWORKS Window Reuse

- MWORKS R2 completed
  `RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015`.
  It added the Iso29 external-frame smoke and proved only that wrapper
  force/torque can enter an explicit minimal external MultiBody test body.
  This is not full plant closure, Factory trace consumption, controller
  performance, parameter identification, planner readiness, live runtime ack,
  or closed loop.
- ROS2 032 returned a real technical blocker after the no-op recovery retry:
  FAST-LIO loop-back reappeared, `/Odometry` and `/cloud_registered` recorder
  counts were zero, Livox probe count was zero, and TF/RViz CLI evidence cannot
  override the failed source gates. PMO updated the ledger and P0 manifest
  integration to keep `planner_ready=false` and `closed_loop_ready=false`.
- PMO fixed the P0 bundle audit so ROS2 032 zero counts are preserved as
  blocker evidence instead of being treated as missing values. The refreshed
  bundle audit and closed-loop gap matrix both pass with smoke-only status.
- CoAgentOps returned the validated MWORKS background evidence/click capability.
  PMO verified the two project-local scripts and return packet exist, then
  updated orchestration rules: delegated departments may collect background
  screenshots for MWORKS GUI incidents and must stop retries with a blocker;
  PMO or CoAgentOps owns any approved background recovery/click-through.
- User clarified that MWORKS/Sysplorer startup/loading windows disrupt normal
  desktop use and make manual review messy. PMO tightened the project rules:
  MWORKS/Sysplorer/Syslab must reuse the existing logged-in window/session by
  default; new windows or full restarts are last-resort blocker recovery actions
  requiring PMO/user approval except for a clearly frozen or duplicating
  process.
- WeChat notification policy remains sparse Chinese only. Routine "task is
  running" updates are kept in the ledger unless a valid notification packet
  class applies; blockers, manual review, auth/license, GUI incidents, and
  completion packets use the short Chinese WeChat format.

## 2026-06-06 CST - PMO Recovered ROS2 R3 Dispatch Surface And Retried 032

- PMO found a stale P0 matrix drift and regenerated the current
  `RUN_MANIFEST` validation, bundle audit, and closed-loop gap matrix. The
  evidence bundle gate is now `pass_smoke_only` with zero audit issues, while
  planner, MWORKS trace consumption, local-map quality, PositionCommand,
  controller performance, and closed loop remain blocked.
- PMO ran one native no-op recovery probe against ROS2 R3 after the earlier
  032 dispatch-surface blocker. The thread replied
  `ros2_r3_noop_recovered_20260606_214x`, so PMO retried 032 exactly once on
  the same ROS2 R3 thread. This is dispatch-surface recovery only; 032 has not
  returned no-goal odom/TF/RViz evidence yet.
- Sunray150 manual material review notification for 004 was delivered through
  WeChat at 20:35 CST. Manual pass/fail review remains pending and no final
  material acceptance is claimed.

## 2026-06-06 CST - WeChat And Dead-Thread Rules Tightened

- User clarified that WeChat notifications must be short Chinese human-facing
  updates. Routine progress should look like a quiet status message; manual
  intervention, auth/license, GUI incident, and dead-thread cases must use an
  obvious alert header.
- Updated gateway notification behavior and tests so WeChat bodies redact
  concrete filenames, long paths, JSON/log names, and raw evidence lists. Those
  details stay in project packets and evidence files.
- Reconfirmed the dead visible-thread recovery rule in top-level project
  policy and CoAgent UX docs: bounded CoAgentOps diagnosis first, then blocker
  plus sparse notification, then Codex++ restart recovery if needed. Do not
  create replacement threads by default.

## 2026-06-06 CST - Foreground Screenshot Boundary Corrected

- User caught that CoAgentOps used Windows MCP screenshot/snapshot while the
  user was typing. This is not background screenshot capability.
- Updated project rules: Windows MCP `Snapshot` / `Screenshot` observe the
  foreground desktop and must not be used as background capture. For Codex++
  restart or similar GUI maintenance, prefer UI Automation/PowerShell/app APIs;
  only use visible desktop screenshots after warning the user or when
  explicitly authorized.

## 2026-06-06 CST - Codex++ Controlled Restart Rule Added

- User authorized `D:\Program Files\Codex++\codex-plus-plus-manager.exe` as the
  controlled restart surface for persistent visible-thread dead-thread
  incidents.
- Updated CoAgentOps and orchestration rules: after bounded diagnosis writes a
  blocker, CoAgentOps should attempt one sparse user notification; if
  notification is unavailable or the user cannot intervene and maintenance
  would stall, CoAgentOps may trigger Codex++ restart through the manager.
- Because restart terminates the current conversation, recovery validation must
  be picked up by the existing 30-minute PMO/CoAgentOps heartbeat automations:
  read latest blocker, run no-op validation, and classify the thread as
  `partial_recovery`, `restored`, or `still_quarantined`.

## 2026-06-06 CST - Dead Thread Restart Notification Rule Added

- User clarified the preferred recovery path for future visible-thread
  start-turn/agent-loop failures: after CoAgentOps confirms a persistent dead
  thread through the bounded ladder, notify the user directly so the user can
  restart Codex App.
- Updated `Docs/Workflows/coagent_meta_maintenance.md` and
  `Docs/Workflows/agent_orchestration.md`: do not keep retrying the same dead
  thread and do not create a replacement before restart notification unless
  PMO/user explicitly authorizes replacement or the critical path cannot wait.
- Post-restart recovery still requires one no-op validation and classification
  as `partial_recovery`, `restored`, or quarantined before production routing.

## 2026-06-06 CST - PMO Integrated UE 008, Sunray 004, And ROS2 032 Dispatch Diagnosis

- UE Experiment Console department completed
  `RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-ACCEPTANCE-FIXTURE-CONTRACT-20260606-008`.
  It added the source/static future live-echo accepted-state fixture checker
  and focused tests. Valid accepted rows require `mosim.ue_command_echo.v1`
  plus authoritative source, command/run/request/seq identity, timestamp,
  accepted status, ack authority, and no-pose-overwrite pass. Smoke/source/
  preflight, rejected, malformed, and non-authoritative rows remain disabled
  or non-runtime. This is not live UE runtime ack.
- Sunray/PBR department completed
  `RFLY-MOSIM-SUNRAY150-REVIEW-MANIFEST-PATH-HYGIENE-20260606-004`.
  It added a headless path-hygiene checker/tests and updated the future render
  script manifest writer so new outputs use project-relative routing and drop
  legacy row `path` fields. Current source manifest was not rewritten; legacy
  absolute fields remain quarantined as existing-manifest risk. Manual visual
  review remains pending and no final material acceptance is claimed.
- CoAgentOps completed ROS2 R3 dispatch-surface diagnosis for 032. R3 is
  visible/readable and title-writable, but no-op start-turn still fails in the
  current App session. PMO sent a sparse WeChat notification asking for Codex
  App restart plus recheck, or explicit authorization for exactly one ROS2
  replacement if the P0 path cannot wait.
- MWORKS 014 has returned completed minimal bridge evidence: Iso28 proves only
  the actuator-input alias to physical-wrench adapter smoke. PMO still does not
  claim Factory trace consumption, full plant closure, controller performance,
  planner readiness, live runtime ack, or closed loop from this packet.

## 2026-06-06 CST - PMO Routed Gateway R3 And Dispatched Next P0 Slices

- PMO corrected operation-facing Gateway routing docs after a read-only subagent
  found R2/R3 drift. Production gateway maintenance now points to
  `MoSim｜微信网关运维部-R3`
  (`019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c`); R2 remains
  quarantine/diagnostic-only unless PMO restores it through a bounded ladder.
- Corrected MWORKS department title drift back to
  `MoSim｜MWORKS动力学与控制验证部-R2`.
- Created and queued four narrow continuation packets:
  MWORKS 014 actuator-to-wrench bridge resume, ROS2 032 no-goal odom/TF/RViz
  preflight, UE 008 live-echo accepted-state fixture contract, and Sunray 004
  manifest path hygiene.
- Dispatch results: MWORKS 014, UE 008, and Sunray 004 native thread dispatch
  started successfully. ROS2 032 failed before target turn start with
  `failed to start turn: internal error; agent loop died unexpectedly`; PMO
  wrote dispatch blocker
  `Results/agent_packets/blockers/PMO-ROS2-R3-DISPATCH-SURFACE-20260606-032.json`
  and will route bounded diagnosis to CoAgentOps before creating another
  ROS2 replacement.
- CoAgentOps completed the bounded ROS2 R3 diagnosis and confirmed this is a
  persistent visible-thread start-turn surface failure in the current App
  session: R3 is listable/readable and title-writable, but two no-op
  `send_message_to_thread` probes still fail with `agent loop died
  unexpectedly`. Do not retry ROS2 032 on R3 now. Next step is a Codex App
  restart plus CoAgentOps no-op recheck, or explicit PMO/user authorization for
  exactly one replacement ROS2 department if the P0 path cannot wait.
  Evidence:
  `Results/agent_packets/blockers/COAGENTOPS-ROS2-R3-DISPATCH-SURFACE-DIAG-20260606-032.json`.
- Prepared Sunray150 manual visual review WeChat packet:
  `Results/agent_packets/notifications/RFLY-MOSIM-SUNRAY150-MANUAL-REVIEW-20260606-004.weixin.json`.
  This asks for human pass/fail review of the 5 component material batches and
  does not claim final material acceptance.

## 2026-06-06 CST - MWORKS 012 Paused For QuadrotorExperiments Package Restructure

- PMO paused `RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-012`
  before any model edits because `Models/QuadrotorExperiments` needs
  package-level classification/merge/cleanup design and concurrent writes would
  be unsafe.
- MWORKS R2 had only read required rules and parent packets (`010`, `011`,
  `021`) plus local MWORKS skill instructions. No 012 model file was edited, no
  new bridge model was created, and no 012 MCP/check_model/simulation/sentinel
  evidence was generated.
- Paused blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-012.json`.
- Resume condition: PMO must publish or complete the package restructuring plan
  and explicitly lift the `Models/QuadrotorExperiments` write lock. A resumed
  bridge task must start with P0 GUI sentinel, force-load current disk package,
  check recovered wrapper/physical adapter models, and only then add the minimal
  actuator-to-wrench bridge smoke.

## 2026-06-06 CST - MWORKS 011 Restored Wrapper Source Reproducibility

- PMO completed `RFLY-MOSIM-MWORKS-WRAPPER-SOURCE-RECOVERY-20260606-011` as a
  narrow source-recovery task after 010 found the parent wrapper/physical
  adapter models missing from current disk source.
- Restored six project-owned model definitions in
  `Models/QuadrotorExperiments/package.mo`:
  `Sunray150DynamicsWrapperSurface`, `Sunray150DynamicsWrapperHoverSmoke`,
  `Sunray150DynamicsWrapperYawStepSmoke`,
  `Sunray150PhysicalWrenchFrameAdapter`,
  `Sunray150PhysicalWrenchHoverSmoke`, and
  `Sunray150PhysicalWrenchYawStepSmoke`. `package.order` already listed these
  models and was not changed.
- Verification: P0 GUI sentinel was clean before/after; Sysplorer MCP
  `session_manager health` passed on dedicated port `49153`;
  `model_manager load_file force_reload=true` loaded current
  `Models/QuadrotorExperiments/package.mo`; `check_model` passed for all six
  restored models. Evidence:
  `Results/mworks_dynamics_upgrade/20260606_011_wrapper_source_recovery/` and
  return packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-WRAPPER-SOURCE-RECOVERY-20260606-011.json`.
- During validation, an initial `check_model` call with `reload_mo_path` caused
  unwanted Sysplorer Smart Layout writeback churn. PMO reverted that broad diff
  and reran the gate with `model_manager(load_file)` followed by `check_model`
  without `reload_mo_path`; the retained diff is limited to six recovered model
  definitions.
- Claim boundary: 011 only restores source reproducibility and `check_model`
  readiness. It does not implement actuator-to-wrench bridge, Factory trace
  consumption, controller performance, dynamic yaw transient acceptance,
  parameter identification, allocation/fault-isolation readiness, planner
  readiness, live UE/ROS2 ack, or closed loop. Next MWORKS task can re-dispatch
  the actuator-to-wrench bridge as a new bounded 012 task.

## 2026-06-06 CST - MWORKS 010 Blocked On Missing Parent Physical Wrapper Source

- MWORKS R2 stopped `RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010`
  before implementation and wrote blocker packet
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`.
- P0 GUI sentinel before and after the MCP gate was clean. Sysplorer MCP
  `session_manager health` was good on dedicated port `49154`, and
  `model_manager load_file` force-loaded current
  `Models/QuadrotorExperiments/package.mo` from disk.
- Reproducibility gate: `check_model` passed for
  `QuadrotorExperiments.Sunray150RflyStyleRotorDynamics`, but failed for
  `QuadrotorExperiments.Sunray150PhysicalWrenchFrameAdapter` because the model
  does not exist after disk reload. Current `package.order` lists the 006/007
  wrapper/physical models, but current `package.mo` no longer defines them.
- No bridge model was added and no simulation was run. 010 does not claim
  Factory trace consumption, closed loop, controller performance, plant
  tracking, planner readiness, live runtime ack, parameter identification, or
  allocation/fault-isolation readiness.
- Next PMO action: restore or intentionally supersede the missing 006/007
  wrapper/physical adapter definitions under `Models/QuadrotorExperiments`,
  then re-run a bounded actuator-to-wrench bridge task with sentinel before/after
  and `check_model` before smoke.

## 2026-06-06 CST - MWORKS 010 Actuator-To-Wrench Bridge Dispatched

- PMO verified current MWORKS dynamics state before dispatch: 005 already proved
  the minimal Rfly-style core, 006 added a wrapper surface, 007 added a
  project-owned physical wrench frame adapter, 008 completed wrapper-level yaw
  sign/motor-order audit, 009 restored the post-GUI sentinel health gate, and
  021 proved the Iso27 actuator-input alias surface.
- Created and dispatched
  `RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010` to MWORKS R2
  (`019e9be5-334b-76b1-93f9-8b02caebf376`).
- Scope: bridge Iso27 actuator input aliases into the project-owned
  RflySim-style Sunray150 physical-wrench wrapper, or precisely block at the
  first command-domain/sign/unit/connector boundary. This must stay in
  `Models/QuadrotorExperiments` and `Results/mworks_dynamics_upgrade/`.
- Claim boundary: 010 must not replace the official `QuadChassis`, retune
  controllers, change mass/inertia/motor/thrust/source labels, consume Factory
  traces, or claim controller performance, parameter identification,
  planner readiness, live runtime ack, or `closed_loop`.

## 2026-06-06 CST - ROS2 030 IMU Startup Discipline Gate Passed

- ROS2 R3 completed
  `RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-STARTUP-DISCIPLINE-GATE-20260606-030`
  with return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-IMU-STARTUP-DISCIPLINE-GATE-20260606-030.json`.
- Candidate order was evidence-local: start FAST-LIO, start LiDAR replay, wait
  for the first Livox frame, then start IMU/state replay. This directly
  targets 029's finding that the prior loop-back came from `imu_cbk` before
  first accepted LiDAR.
- Gate result: zero callback-labeled loop-back events, no `No Effective
  Points`, nonzero `/Odometry=14`, `/cloud_registered=14`, `/path=2`,
  Livox/IMU input timestamps monotonic, forbidden planner/setpoint topics
  absent, and final cleanup `no_matching_processes`.
- Claim boundary: this is only a no-goal FAST-LIO startup discipline
  precondition pass. It is not localization quality, local-map quality,
  planner readiness, PositionCommand, 20 Hz adapter runtime, controller
  performance, mission success, or `closed_loop`.
- Next ROS2 step should rerun the 028 long-source gate using this ordering
  before any EGO/planner acceptance.
- PMO created and dispatched
  `RFLY-MOSIM-ROS2-RUNTIME-B1-LONG-SOURCE-STARTUP-DISCIPLINE-RERUN-20260606-031`
  to ROS2 R3. It may run exactly one no-goal long-source rerun using the 030
  order and must stop before planner/EGO/PositionCommand/20Hz adapter work.

## 2026-06-06 CST - Dead Visible Threads Recovered After Codex App Restart

- User reported that Codex App crashed/restarted and previously "dead"
  visible threads became usable again. CoAgentOps treated this as a Codex App
  visible-thread dispatch-surface diagnosis, not a business-domain incident.
- Post-restart native no-op probes succeeded:
  Gateway Ops R2 `019e9be0-534e-7c22-97ff-98fa7c2af39b` replied
  `dead_thread_restart_probe_received_gateway_r2_20260606`, and ROS2 R2
  `019e9b85-d4d8-7bf3-8afd-a65697cd3889` replied
  `dead_thread_restart_probe_received_ros2_r2_20260606`. The old MWORKS
  thread `019e9999-b0d3-7682-bccd-faef08fcf1df` had already passed no-op and
  settings-override probes after earlier start-turn failures.
- Working conclusion: the observed pattern strongly points to transient Codex
  App or agent-loop lifecycle state affecting forwarding/start-turn surfaces.
  Root cause is not proven because Codex App private DB/session files were not
  inspected and should not be inspected.
- Policy updated: restart recovery is only `partial_recovery` unless
  cross-thread no-op, settings override, user UI composer, and required
  automation/wakeup surfaces are all revalidated. Production routing stays on
  current canonical replacements until PMO/CoAgentOps explicitly restores a
  thread through the bounded validation ladder.
- Result packet:
  `Results/agent_packets/returns/COAGENTOPS-DEAD-THREAD-RESTART-RECOVERY-DIAG-20260606-001.json`.

## 2026-06-06 CST - MWORKS Post-GUI Sentinel Health Gate Passed With Writeback Concern

- MWORKS R2 completed `RFLY-MOSIM-MWORKS-POST-GUI-SENTINEL-HEALTH-GATE-20260606-009`.
  Evidence:
  `Results/mworks_gui_incidents/post_gui_sentinel_health_gate_20260606_009/`.
- Gate sequence: pre-sentinel clean, Sysplorer MCP `session_manager health`
  ok on dedicated port `49152`, narrow `check_model` ok for
  `QuadrotorExperiments.Sunray150PhysicalWrenchHoverSmoke`, post-sentinel
  clean, model diff restored, post-restore sentinel clean.
- Concern recorded: the `check_model` call with `reload_mo_path` triggered MCP
  Smart Layout writeback on `Models/QuadrotorExperiments/package.mo`. R2
  detected the unintended diff and restored the file to clean before return.
  Future read-only health gates should use a no-write check path when exposed,
  or avoid arguments that trigger Smart Layout writeback.
- This restores only the minimal post-GUI session/check_model gate for later
  scoped MWORKS tasks. It is not dynamics performance, controller performance,
  Factory trace consumption, live runtime ack, planner readiness, or
  closed_loop evidence.

## 2026-06-06 CST - PMO P0 Mainline Dispatch Continued After Gateway Detach

- User clarified that WeChat gateway maintenance should stay with the gateway
  owner thread and should not block PMO technical mainline work.
- PMO created and dispatched
  `RFLY-MOSIM-MWORKS-CONTROL-DOWNSTREAM-OUTPUT-GROUP-20260606-020` to
  `MoSim｜MWORKS动力学与控制验证部` (`019e9be5-334b-76b1-93f9-8b02caebf376`).
  The task fixes the baseline to passing Iso25, requires before/after MWORKS
  GUI sentinel, allows exactly one downstream control-output or
  actuator-preflight reconnect group, and still forbids full Factory retry or
  closed_loop/controller-performance claims.
- PMO found ROS2 R3 task 028 was `interrupted` with no return/blocker packet,
  despite partial evidence showing a generated 120-frame body-frame source,
  nonzero `/Odometry` and `/cloud_registered`, and remaining FAST-LIO
  `lidar loop back, clear buffer` log events. PMO sent a resume/correction
  packet to active ROS2 R3
  (`019e9c72-ee74-79d1-b9fe-621d3c6fc99e`): either rerun one no-goal
  source/FAST-LIO correction that removes loop-back, or write a blocker. It
  remains forbidden to run planner goal, `/planning/bspline` acceptance,
  PositionCommand recorder, `/position_cmd`, 20Hz adapter, or extrinsic/frame
  edits in 028.

## 2026-06-06 CST - MWORKS GUI Sentinel P0 Completed

- MWORKS R2 implemented the read-only P0 GUI sentinel
  `Scripts/agent/check_mworks_gui_sentinel.py`. It enumerates Win32
  top-level/child window title and control text, classifies MWORKS/Sysplorer
  crash/error-report and login/license patterns, and writes machine-readable
  JSON without clicking, closing, focusing, restarting, sending reports, or
  reading external `Documents/MWORKS/log` files.
- Focused tests pass:
  `python -m pytest Scripts/tests/test_mworks_gui_sentinel.py -q`.
  A live dry probe wrote
  `Results/mworks_gui_incidents/sentinel_probe_20260606_001/sentinel_probe.json`
  with `status=clean`, `window_count=374`, and no matched MWORKS crash/license
  windows after tightening a generic `授权` false-positive boundary.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-GUI-SENTINEL-P0-20260606-001.json`.
  This is a P0 title/text sentinel only, not hidden-window screenshot evidence
  and not Computer Use Windows.Graphics.Capture.

## 2026-06-06 CST - CoAgentOps Learned Codex Goal Usage Guidance

- User provided the Feishu page
  `https://xiangyangqiaomu.feishu.cn/wiki/YQn6wZ1hzijlRvkU1E6cEL5mnic`
  about Codex `/goal` usage. CoAgentOps used background `windows_mcp.Scrape`
  and Chrome headless capture; no foreground browser or user desktop takeover
  was needed. Evidence screenshot:
  `Results/browser_captures/feishu_goal_20260606/feishu_goal_viewport_1280x2000.png`.
- Reusable lesson: `/goal` is a durable completion contract for multi-turn
  work with a clear, testable stop condition, not a generic way to make Codex
  run longer. Good goals specify outcome, verification surface, constraints,
  boundaries, iteration policy, blocker stop condition, and evidence to record
  after each round.
- Updated `Docs/Workflows/agent_orchestration.md#24-goal-assignment` with a
  Goal Contract Gate. Short explanations, one-line edits, simple suggestions,
  routine code-review comments, and vague aims should stay as ordinary prompts
  or ledger tasks unless rewritten into auditable completion criteria.

## 2026-06-06 CST - ROS2 027 No-Loopback Source Window Blocked Before Goal

## 2026-06-06 CST - PMO Corrects Sunray Notification And Opens MWORKS GUI Sentinel P0

- User correctly challenged two PMO/process gaps:
  1. the newly generated Sunray150 component review images `battery.png` and
     `guard_landing_gear.png` were not separately notified for manual review;
  2. MWORKS/Sysplorer GUI error-report handling cannot rely on a department
     visually noticing a foreground dialog, because the user may be using other
     applications and background screenshot is not currently proven.
- PMO created the missing WeChat review packet:
  `Results/coagent_gateway/packets/sunray150_component_review_gap_fill_20260606.json`.
  It asks the user to review only the two new component images:
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/battery.png`
  and
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/guard_landing_gear.png`.
  The packet is manual-review only and does not claim final material
  acceptance.
- PMO attempted to send the packet through
  `CoAgent/gateway/cc_connect_weixin.py`; the adapter accepted the packet and
  reached the Weixin send layer, but failed with
  `weixin: sendMessage: ret=-2 errcode=0`. The notification has not been
  delivered.
- User instructed PMO to hand this to WeChat gateway maintenance thread
  `019e9be0-534e-7c22-97ff-98fa7c2af39b`. Native
  `send_message_to_thread` to that visible thread failed with
  `failed to update thread settings: internal error; agent loop died unexpectedly`.
  PMO recorded:
  `Results/agent_packets/blockers/PMO-WEIXIN-GATEWAY-R2-DISPATCH-SURFACE-20260606-001.json`.
  PMO then routed the combined ret=-2 recovery and gateway-thread dispatch
  diagnosis to `MoSim｜CoAgent运维平台`
  (`019e9bc1-ea9f-7102-b41a-4ef9b2308992`). Await its return/blocker.
- PMO used one read-only disposable sub-agent
  `019e9c5a-4b69-7142-aa8f-1daa2fbe178e` to audit screenshot options. Result:
  current Computer Use would be the preferred occluded-window screenshot route
  because its skill documents Windows.Graphics.Capture, but it is not currently
  callable in this session (`native pipe path is unavailable`). Current
  Windows MCP can enumerate windows and capture visible desktop state, but is
  not a reliable hidden Sysplorer HWND screenshot path.
- PMO updated `AGENTS.md` and `Docs/Workflows/agent_orchestration.md`:
  non-trivial tasks must now record an explicit `subagent_plan` decision, and
  MWORKS GUI-affecting tasks must use a GUI sentinel before/after risky MCP
  steps when available. Preferred P0 sentinel is read-only UIA/EnumWindows
  title/text detection for `MWORKS错误报告`, `Sysplorer 遇到错误，需要关闭`, and
  login/license prompts. Background screenshots remain P1 until Computer Use is
  repaired.
- PMO created and dispatched P0 sentinel task:
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-GUI-SENTINEL-P0-20260606-001.json`
  to MWORKS R2 (`019e9be5-334b-76b1-93f9-8b02caebf376`). Scope is read-only:
  detector/tests/evidence/return-or-blocker only; no Sysplorer operation,
  no click/close/restart/send-report, no virtual desktop.

- ROS2 R2 completed the narrow 027 code correction: `dense_lidar_replay_node`
  now supports explicit `loop` and `exit_after_last_frame` parameters. Default
  behavior remains `loop=true`, while `loop=false` publishes finite frames
  without modulo wrap and logs completion.
- Verification: `python Scripts/tests/test_dense_lidar_cpp_contract.py` passed,
  and WSL ROS2 `colcon` built `mosim_dense_lidar_cpp` successfully. The older
  headless dry-run regression is currently blocked on Windows Python
  subprocess encoding/path handling before producing dry-run JSON; this was
  recorded as a verification limitation, not a C++ build failure.
- 027 runtime gate remains blocked before any planner goal. With `loop=false`,
  the accepted Factory body-frame source has only 40 frames at 10Hz, so the
  non-wrapping window lasts about 4 seconds. Evidence shows first Livox and
  first IMU messages were captured, and dense replay completed `40/40` frames,
  but the Livox+IMU probe later observed `livox_count=0`. FAST-LIO advertised
  `/Odometry` and `/cloud_registered` publishers but recorded zero samples.
- No EGO map-readiness, planner goal, `/planning/bspline` acceptance,
  PositionCommand recorder, `/position_cmd`, 20Hz adapter, fake map/cloud, UE
  truth planner input, keyboard pose, FAST-LIO `/path` trajectory conversion,
  or MID-360 extrinsic/frame adapter change was performed. This is not
  planner_ready, FAST-LIO success, local-map quality, closed_loop, controller
  performance, or mission success.
- Blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-NO-LOOPBACK-SOURCE-WINDOW-20260606-027.json`.
  Evidence:
  `Results/ros2_runtime/b1_no_loopback_source_window_20260606_027/`.
  Next minimum correction gate should use a longer accepted
  `body_lidar_m_z_up` non-wrapping source window or a startup order that leaves
  enough live non-wrapping Livox for FAST-LIO, then require source probe pass,
  no loop-back log, nonzero `/Odometry` and `/cloud_registered`, and cleanup
  before any goal.

## 2026-06-06 CST - PMO Corrects Sunray Component Review Dispatch Gap

- User correctly pointed out that the YunZong/Sunray150 asset thread
  `019e9b25-066e-7372-8152-209c2b1322a4` was not being advanced enough after
  the close-up review-prep return.
- PMO re-read the Sunray return packet and current component-review outputs.
  The existing task only prepared grouped manual review inputs; it did not
  generate dedicated `battery.png` or `guard_landing_gear.png` component review
  images, and the manifest has no dedicated rows for those two components.
  The script `Scripts/UE5/assets/render_sunray150_component_material_reviews.py`
  already defines both components, so this is a concrete review-output gap, not
  a reason to claim final material acceptance.
- PMO opened the corrective Sunray task packet
  `Results/agent_packets/tasks/sunray_pbr/RFLY-MOSIM-SUNRAY150-COMPONENT-REVIEW-GAP-FILL-20260606-002.json`.
  Scope is narrow: generate or precisely block the two missing dedicated
  component review outputs, update the component-review manifest, save evidence
  under `Results/unreal_scene_mapping/sunray150_component_review_gap_fill_20260606_002/`,
  and return a packet. It must not edit geometry, dynamics, FAST-LIO
  extrinsics, controller/planner parameters, or claim final material
  acceptance.
- Sunray department returned completed:
  `Results/agent_packets/returns/RFLY-MOSIM-SUNRAY150-COMPONENT-REVIEW-GAP-FILL-20260606-002.json`.
  Headless Blender 5.0 rendered only `battery` and `guard_landing_gear`;
  generated `battery.png` (`1018043` bytes) and `guard_landing_gear.png`
  (`1200097` bytes); both are RGBA `1400x1050`, non-flat by file-level pixel
  extrema, and the manifest now has project-relative rows for both components.
  Evidence summary:
  `Results/unreal_scene_mapping/sunray150_component_review_gap_fill_20260606_002/evidence_summary.json`.
  `python Scripts/UE5/check_sunray150_pbr_miniloop.py` passed after the
  manifest update. This is still file-level review-output readiness only;
  manual visual review is required before final material acceptance.

## 2026-06-06 CST - Sysplorer GUI Error Dialog Must Become Blocker Evidence

- User reported that a department encountered a Sysplorer/MWORKS GUI error
  dialog but did not screenshot or return it to PMO. PMO captured the current
  desktop evidence at
  `Results/mworks_gui_incidents/20260606_sysplorer_error_dialog/sysplorer_error_dialog_20260606_1737.png`
  and recorded incident metadata at
  `Results/mworks_gui_incidents/20260606_sysplorer_error_dialog/incident.json`.
- Visible dialog text: `MWORKS错误报告`; `Sysplorer 遇到错误，需要关闭`;
  the dialog shows a MWORKS error report path under
  `C:/Users/HP/Documents/MWORKS/log/2026-06-06/...`, offers restart and send
  report options, and should not be clicked through silently by an agent.
- Reusable rule landed in `AGENTS.md` and
  `Docs/Workflows/agent_orchestration.md`: if a Sysplorer/Syslab/MWORKS GUI
  crash/error-report dialog appears, the department must stop the active
  MCP/model sequence, capture or reference a screenshot under `Results/`, write
  a blocker with visible dialog text, triggering command/action, report path or
  visible prefix, and next recovery step, and must not continue hidden solver
  retries or click restart/send/confirm without PMO/user approval.

## 2026-06-06 CST - CoAgentOps Diagnosed Old MWORKS Thread As Partial-Recovery UI Failure

- ROS2 026 returned blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-PRECONDITION-CORRECTION-20260606-026.json`.
  The corrected 019-style source discipline made useful progress: real dense
  LiDAR replay, MWORKS IMU/state replay, and FAST-LIO started; `/Odometry`
  stayed meter-scale rather than the 024 kilometer-scale failure; and
  `/cloud_registered` was non-empty (`width=15859`). The gate is still blocked
  before any planner goal because FAST-LIO logged `lidar loop back, clear
  buffer` twice, the Livox/IMU short probe reported non-monotonic stamps, the
  latest odometry `(12.454, 23.061, -1.304)m` left the configured EGO static
  envelope, and EGO map-readiness was not accepted before the 60 s window
  ended. This is not FAST-LIO success, planner readiness, local-map quality, or
  `closed_loop`.
- PMO opened the next ROS2 task packet
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-NO-LOOPBACK-SOURCE-WINDOW-20260606-027.json`.
  Scope is deliberately narrow: make the dense LiDAR replay source support a
  bounded/non-wrapping source window, rerun the precondition-only gate, and
  stop before any planner goal unless timestamp monotonicity, no-loop-back
  FAST-LIO logs, odometry/envelope checks, and non-empty map-readiness all
  pass. No MID-360 extrinsic edits, `/planning/bspline`, `/position_cmd`, 20 Hz
  adapter, fake map/cloud, or planner-ready claim is allowed.
- MWORKS 007 returned completed:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-PHYSICAL-WRENCH-WRAPPER-20260606-007.json`.
  R2 added project-owned `Sunray150PhysicalWrenchFrameAdapter`,
  `Sunray150PhysicalWrenchHoverSmoke`, and
  `Sunray150PhysicalWrenchYawStepSmoke` under
  `Models/QuadrotorExperiments`. Sysplorer MCP session health was good, all
  new models passed `check_model` before simulation, hover smoke applied
  `9.810000000000002 N` at `body.frame_a.f[3]` with zero force/torque
  application error, and yaw smoke applied
  `0.05418494199832341 N.m` at `body.frame_a.t[3]` with zero torque
  application error. Official baseline remained unmodified. This is a
  physical-wrench wrapper smoke only, not parameter identification, controller
  performance, dynamic yaw transient acceptance, Factory trace consumption,
  ROS2/UE runtime, planner readiness, live runtime ack, or `closed_loop`.
- PMO opened MWORKS 008:
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-YAW-SIGN-MOTOR-ORDER-AUDIT-20260606-008.json`.
  Scope is a narrow source/evidence audit for yaw sign and motor order against
  local PX4/Sunray/YunZong allocation conventions before any fault-isolation or
  allocation claim. It must not edit the official baseline, retune controllers,
  consume Factory traces, or promote current parameters to identified truth.
- PMO heartbeat follow-up opened MWORKS 007:
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-PHYSICAL-WRENCH-WRAPPER-20260606-007.json`.
  The task goes only to MWORKS R2
  (`019e9be5-334b-76b1-93f9-8b02caebf376`), not the old quarantined MWORKS
  thread. Scope is the smallest project-owned physical wrench wrapper that
  applies the 006 wrapper outputs to a body/frame interface. It must reuse the
  current logged-in Sysplorer window/MCP where healthy, stop on license/auth
  symptoms, and must not edit the official baseline, retune controllers,
  consume Factory traces, or claim parameter identification, controller
  performance, dynamic yaw transient acceptance, planner readiness, live
  runtime ack, or `closed_loop`.
- User asked to keep old MWORKS thread
  `019e9999-b0d3-7682-bccd-faef08fcf1df` for diagnosis instead of deleting it.
  The thread remains visible as `MoSim｜MWORKS动力学与控制验证部`; replacement R2
  remains visible as `MoSim｜MWORKS动力学与控制验证部`
  (`019e9be5-334b-76b1-93f9-8b02caebf376` in the App list, documented as
  `-R2` in project routing).
- Earlier blocker evidence still stands: two MWORKS 004 business dispatch
  attempts to the old thread failed through `codex_app.send_message_to_thread`,
  first with `failed to update thread settings: internal error; agent loop died
  unexpectedly`, then with `failed to start turn: internal error; agent loop
  died unexpectedly`.
- New controlled diagnosis found the old thread is not permanently unreadable:
  a no-op cross-thread healthcheck without settings override completed with
  `healthcheck_received_old_mworks_thread_20260606`, and a no-op cross-thread
  healthcheck with `model=gpt-5.5` / `thinking=high` completed with
  `settings_healthcheck_received_old_mworks_thread_20260606`.
- User then showed that manual sending from inside the old thread UI still
  fails with `Error submitting message`. Updated classification: partial
  recovery only. Cross-thread native no-op dispatch works, but the in-thread UI
  composer/manual-submit path is still broken. This is not a
  MWORKS/Sysplorer/Syslab technical blocker and not a fully rescued thread.
  Production MWORKS task dispatch still stays on R2 unless PMO explicitly
  approves a bounded CoAgentOps R2 validation ladder for the old thread.
- User instructed PMO not to rush into creating replacement conversations for
  future dead-thread incidents. CoAgentOps R2 now owns the first-pass rescue and
  diagnosis task; create a replacement only after bounded diagnosis or when the
  critical path cannot wait.
- Diagnostic packet:
  `Results/agent_packets/returns/MOSIM-COAGENT-OPS-R2-DEAD-THREAD-DIAG-MWORKS-20260606-001.json`.
  Updated routing/workflow records:
  `CoAgent/dispatch/department_threads.json`,
  `Docs/Workflows/agent_orchestration.md`,
  `Docs/Workflows/agent_task_ledger.md`, and
  `Docs/Index/codex_app_session_research.md`.

## 2026-06-06 CST - PMO Recovered Sysplorer License Login State

- User identified that recent odd MWORKS solver/check behavior was likely a
  dropped Sysplorer login/activation state, not necessarily a code or solver
  problem. PMO paused further MWORKS trial-and-error and performed one
  controlled foreground login recovery. User-provided credentials were used
  only in the official Sysplorer login dialog and were not written to project
  docs, packets, logs, or scripts.
- Before recovery, Sysplorer showed demo/unactivated license symptoms and the
  output contained `L5104-B0` / software-not-activated style messaging. After
  login, Sysplorer title showed education edition and the license dialog showed
  account-license status with remaining days and authorized modules.
- MCP verification after login passed:
  `session_manager health` returned `driver_ready=true` and `api_ready=true`;
  a minimal `check_model` for
  `QuadrotorExperiments.Sunray150DynamicsWrapperHoverSmoke` returned
  `ok=true`. Evidence summary:
  `Results/mworks_license_recovery/20260606_pmo_sysplorer_login_recovery.json`.
- Reusable rule landed in `AGENTS.md`: `L5104-B0`, "软件尚未激活",
  "当前授权不允许变量方程数大于 300", unexpected demo-edition mode, login
  prompts, and authorization failures are auth/license incidents first.
  Department threads must stop solver/model trial-and-error and return an
  auth/license blocker or ask PMO to recover login state.
- User confirmed window operation is acceptable and requested avoiding repeated
  MWORKS window restarts. `AGENTS.md` now strengthens the reuse rule: after
  license health is restored, keep the current logged-in Sysplorer window open
  for related MWORKS checks/review and prefer MCP reconnect/reuse over full
  restarts. Credentials still are not persisted in project files.

## 2026-06-06 CST - PMO Integrated ROS2 025 And Opened B1 Precondition Correction

- ROS2 025 returned a diagnostic completion packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-FRAME-SCALE-Z-DIAG-20260606-025.json`.
  It did not run a new live probe, publish a planner goal, rerun
  `/planning/bspline`, run a PositionCommand recorder, publish `/position_cmd`,
  or start the 20 Hz adapter.
- Diagnosis: 019 and 024 used the same FAST-LIO topic/config basis
  (`/mosim/livox/lidar`, `/mosim/forward/imu`, `timestamp_unit=2`,
  `scan_rate=10`, identity extrinsic), but 019 produced meter-scale odometry
  in `camera_init` while 024 produced kilometer-scale odometry. The supported
  primary cause is source replay/runtime sequencing causing FAST-LIO
  initialization drift; EGO empty map-readiness is downstream. A static
  extrinsic/frame edit is not justified from current evidence.
- PMO created the next ROS2 task packet
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-PRECONDITION-CORRECTION-20260606-026.json`.
  This is a precondition-only correction gate using the 019-style bounded
  source startup discipline. It must stop before any goal if odometry remains
  kilometer-scale/out-of-envelope, map samples are empty, or FAST-LIO logs
  loop-back buffer clearing / persistent `No Effective Points`.
- UE 006 compile-only evidence is present and already reflected in the ledger:
  UnrealBuildTool exit code 0, `QuadrotorMworksExperimentConsoleStateComponent.cpp`
  compiled, and `UnrealEditor-QuadrotorMworksBridge.dll` linked. This remains
  compile evidence only, not live UE runtime ack.
- MWORKS 006 wrapper integration returned completed evidence:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-WRAPPER-INTEGRATION-20260606-006.json`.
  R2 added project-owned `Sunray150DynamicsWrapperSurface`,
  `Sunray150DynamicsWrapperHoverSmoke`, and
  `Sunray150DynamicsWrapperYawStepSmoke`; all three passed Sysplorer MCP
  `check_model` before simulation. Hover smoke read zero thrust error and
  command-side yaw sign/motor-order gate read
  `commanded_yaw_moment_gate@end = 0.061549776 N.m`, with
  `motor_order_gate_error=0.0` and `yaw_direction_gate_error=0.0`.
  Dynamic lagged yaw transient remains unclaimed from this slice. Official
  baseline file stayed clean; full baseline `QuadChassis` check was degraded
  by license limit `当前授权不允许变量方程数大于 300`. Evidence:
  `Results/mworks_dynamics_upgrade/20260606_006_wrapper_integration/`.

## 2026-06-06 CST - PMO Dispatches Next P0 Parallel Gates

- PMO integrated the CoAgentOps R2 replacement packet, MWORKS 004 return, and
  ROS2 023 diagnostic return into the active P0 task graph.
- MWORKS 004 is no longer pending. It passed a fresh
  `MWORKS_MCP_runtime_adapter_preflight` but precisely blocked live
  `mosim.ue_command_echo.v1` downlink because no project-owned MWORKS-to-UE or
  MWORKS-to-ROS2 echo transport/receiver surface exists yet.
- PMO created three non-conflicting next task packets:
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-DYNAMICS-MIN-UPGRADE-20260606-005.json`
  for the project-owned MWORKS dynamics minimal upgrade,
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-CORRECTED-BSPLINE-GATE-20260606-024.json`
  for the corrected ROS2 frame/scale/z and `/planning/bspline` gate, and
  `Results/agent_packets/tasks/ue/RFLY-MOSIM-UE-LIVE-ECHO-RECEIVER-BOUNDARY-20260606-004.json`
  for UE live echo receiver boundary design/static audit.
- MWORKS 005 completed as a minimal project-owned MWORKS_MCP dynamics smoke:
  `QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke` and
  `QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke` passed
  `check_model` before simulation. Hover smoke verified
  `dynamics.hover_thrust_error@end = 1.7763568394002505e-15 N`; yaw-step smoke
  verified `dynamics.total_moment_body[3]@end = 0.06153801695664962 N.m`.
  The existing `Sunray150RflyStyleRotorDynamics` slice contains command-to-
  speed mapping, first-order motor lag, `Ct*omega^2` thrust, yaw reaction
  torque, and rotor-center moment. Official baseline
  `References/MWORKS/QuadrotorModel/package.mo` was not edited. Evidence:
  `Results/mworks_dynamics_upgrade/20260606_005_minimal_upgrade/`; return:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-MIN-UPGRADE-20260606-005.json`.
- PMO created the next MWORKS follow-up task
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-DYNAMICS-WRAPPER-INTEGRATION-20260606-006.json`
  for `MoSim｜MWORKS动力学与控制验证部-R2`. The task is limited to
  project-owned wrapper/chassis integration of the checked rotor dynamics core,
  plus yaw sign/motor-order validation or a precise blocker. It must not edit
  the official baseline, retune controllers, consume Factory traces, or claim
  parameter identification, controller performance, planner readiness, live
  runtime ack, or `closed_loop`.
- ROS2 024 returned a corrected precondition blocker before any goal was
  published. Real `/Odometry` and `/cloud_registered` were present, but current
  odometry in `camera_init` was about
  `(-2865.728, -228.497, -12849.773)m`; EGO would force the effective goal z
  to `1.0`, yielding about `12850.77m` start-goal distance outside the static
  EGO envelope `x/y=[-20,20]`, `z=[-0.01,2.99]`. Occupancy/inflated occupancy
  samples had `width=0`. No goal was published and `/planning/bspline` was not
  accepted. Blocker:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-CORRECTED-BSPLINE-GATE-20260606-024.json`.
- PMO created follow-up ROS2 diagnosis task
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-FRAME-SCALE-Z-DIAG-20260606-025.json`
  to compare 024 against the last bounded good odom/cloud restore and classify
  the frame/scale/z plus empty-map-readiness failure. It may run only
  source-graph/odom/cloud/tf diagnostics, not planner goals, Bspline
  acceptance, PositionCommand recorder, `/position_cmd`, or the 20 Hz adapter.
- UE 005 completed the source-label safety patch. The state component now
  treats `offline_adapter_smoke`, `source_level_smoke`,
  `MWORKS_MCP_result_adapter_smoke`, and
  `MWORKS_MCP_runtime_adapter_preflight` as non-live smoke/preflight sources:
  `quality_status=smoke_only` and `accepted_as_runtime_ack=false`. Evidence:
  `Results/unreal_experiment_console/echo_source_label_safety_20260606_005/`;
  return:
  `Results/agent_packets/returns/RFLY-MOSIM-UE-ECHO-SOURCE-LABEL-SAFETY-20260606-005.json`.
  Runtime echo receiver remains blocked because MWORKS 004 still has no live
  transport surface.
- PMO created UE compile-only follow-up
  `Results/agent_packets/tasks/ue/RFLY-MOSIM-UE-SOURCE-LABEL-COMPILE-GATE-20260606-006.json`.
  `mosim-unreal.project_context` confirmed the renderer project and bridge
  plugin exist, but did not expose a local Unreal Engine install path, so the
  UE department must either produce compile-only evidence or a precise
  UnrealBuildTool/toolchain blocker. No UE GUI, assets, runtime receiver, UI
  accepted-state controls, MWORKS/ROS2 runtime, or live ack claim is allowed.
- UE 004 returned a precise static-boundary blocker: the existing
  `UQuadrotorMworksUdpReceiverComponent` is frame/status-only, and the source
  state component does not yet downgrade `MWORKS_MCP_result_adapter_smoke` or
  `MWORKS_MCP_runtime_adapter_preflight` to `smoke_only`. Do not implement a
  live echo receiver until that source-label gap is fixed and rechecked.
- PMO created the follow-up source-label safety task
  `Results/agent_packets/tasks/ue/RFLY-MOSIM-UE-ECHO-SOURCE-LABEL-SAFETY-20260606-005.json`
  for `MoSim｜UE实验控制台与场景交互部`. The task is narrow: patch/check the
  C++ state component so known offline/source/preflight echo rows remain
  `quality_status=smoke_only` and `accepted_as_runtime_ack=false`; it must not
  implement a runtime receiver or claim live ack.
- Current claim boundary remains strict: no `planner_ready`, no
  `PositionCommand`, no `/position_cmd`, no 20 Hz adapter runtime, no live UE
  runtime ack, no final material acceptance, and no `closed_loop` claim until
  the corresponding MWORKS/ROS2/UE/RViz/MCP evidence exists.
- Sparse WeChat milestone packet
  `Results/coagent_gateway/packets/pmo_p0_parallel_gates_dispatched_20260606.json`
  was attempted once through `CoAgent/gateway/cc_connect_weixin.py` and reached
  Weixin but failed with `weixin: sendMessage: ret=-2 errcode=0`. Do not retry
  in a loop. Minimal recovery remains one ordinary user message in the
  WeChat-side Codex conversation `MoSim｜WechatCodex`
  (`019e8358-86b4-7070-8fd6-a2b4f4d2af97`), then retry once if a new
  notification is still needed.

## 2026-06-06 CST - CoAgent Meta Departments Rebuilt As App-Native R2

- Created and titled four App-native replacement department threads:
  `MoSim｜微信网关运维部-R2`
  (`019e9be0-534e-7c22-97ff-98fa7c2af39b`),
  `MoSim｜Codex 上下文维护部-R2`
  (`019e9be0-f6ac-7762-b80c-b1dd18b0d013`),
  `MoSim｜开源项目探针-R2`
  (`019e9be3-94de-7dc3-b067-92a78b678287`), and
  `MoSim｜开源项目学习部-R2`
  (`019e9be4-56d0-7981-b71c-a5ded1c7ec76`).
- Created and verified four Codex App heartbeat automations:
  `mosim-r2` for gateway health every 4 hours,
  `mosim-codex-r2` for context maintenance every 6 hours,
  `mosim-r2-2` for open-source probe inventory daily, and
  `mosim-r2-3` for open-source learning evaluation weekly.
- Old thread deletion is gated by content landing, not backup. Reusable content
  must be recoverable from canonical docs and packets. The replacement result
  packet with the landing matrix is:
  `Results/agent_packets/returns/MOSIM-COAGENT-OPS-R2-DEPARTMENT-REPLACEMENT-AUTOMATION-20260606-001.json`.
- Updated active routing in `CoAgent/dispatch/department_threads.json`,
  `Docs/Index/codex_app_session_research.md`,
  `Docs/Workflows/coagent_meta_maintenance.md`,
  `Docs/Workflows/org_operating_model.md`,
  `Docs/Workflows/agent_orchestration.md`, `AGENTS.md`, and
  `Docs/Index/external_learning_index.md`.
- Dead-thread handling rule is now documented: if a visible department can be
  read but cannot reliably receive work, expose native tools, run automations,
  or keep a healthy loop, record the observed failure, treat root cause as
  unknown unless proven, extract useful history into canonical docs, create an
  App-native replacement, update the allowlist, and leave deletion to the user.

## 2026-06-06 CST - MWORKS R2 Created And 004 Dispatched

- PMO attempted to dispatch
  `RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004` to the old
  `MoSim｜MWORKS动力学与控制验证部`
  (`019e9999-b0d3-7682-bccd-faef08fcf1df`) twice through native
  `send_message_to_thread`.
- Both attempts failed at the Codex App visible-thread dispatch surface:
  first `failed to update thread settings: internal error; agent loop died
  unexpectedly`, then `failed to start turn: internal error; agent loop died
  unexpectedly`.
- PMO recorded the dispatch blocker:
  `Results/agent_packets/blockers/PMO-MWORKS-VISIBLE-THREAD-DISPATCH-SURFACE-20260606-001.json`.
- PMO created and titled replacement thread
  `MoSim｜MWORKS动力学与控制验证部-R2`
  (`019e9be5-334b-76b1-93f9-8b02caebf376`), updated
  `CoAgent/dispatch/department_threads.json`,
  `Docs/Index/codex_app_session_research.md`, the 004 task packet, and the
  ledger. Future MWORKS dispatch should use R2 unless PMO later proves the old
  thread healthy.
- 004 is now assigned to R2 through the initialization prompt. Await either
  return packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004.json`
  or blocker packet
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004.json`.
- This is a thread-dispatch recovery only. It does not change any MWORKS model,
  runtime transport, UE runtime, ROS2 runtime, or control evidence state.

## 2026-06-06 CST - MWORKS 004 Runtime-Adapter Preflight Passed, Live Downlink Blocked

- R2 completed
  `RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004` with return
  packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004.json`.
- Sysplorer MCP evidence was refreshed in this task: `session_manager probe`
  passed, `ensure` started dedicated port `49152`, `check_model` passed for
  `QuadrotorExperiments.EchoMcpStateSmoke`, `simulate_model` passed for
  `0.0..1.0s`, `GetVarTimes` returned `101` samples, and 12 echo-state
  variables were read at end time.
- Added `Scripts/mworks/smoke_mworks_echo_live_downlink_preflight.py` and
  `Scripts/tests/test_mworks_echo_live_downlink_preflight.py`. The script
  consumes only fresh `source=MWORKS_MCP` preflight input and rejects task-003
  style result-adapter fixture input.
- Evidence directory:
  `Results/mworks_echo_producer_smoke/20260606_004_live_downlink_preflight/`.
  Generated rows use
  `source=MWORKS_MCP_runtime_adapter_preflight`,
  `evidence_level=fresh_result_context_runtime_adapter_preflight`, and
  `live_downlink_status=blocked_no_transport_surface`.
- Output summary: 6 `mosim.ue_command_echo.v1` rows, 5 accepted MWORKS-owned
  commands, 1 forbidden pose rejection, `no_pose_overwrite_status=pass`,
  `stronger_than_task_003_fixture=true`, and
  `uses_task_003_fixture_rows=false`.
- Validation passed:
  `python Scripts\UE5\check_ue_command_echo_contract.py ... --require-runtime-ack`,
  `python Scripts\UE5\smoke_ue_command_echo_state_reducer.py ...`, and
  `python -m pytest Scripts\tests\test_mworks_echo_live_downlink_preflight.py Scripts\tests\test_mworks_mcp_echo_result_adapter.py Scripts\tests\test_ue_command_echo_state_reducer.py -q`.
  The UE reducer keeps `accepted_as_runtime_ack=false` for this preflight
  source.
- Precise blocker remains: no project-owned MWORKS-to-UE/ROS2
  `mosim.ue_command_echo.v1` live downlink or receiver transport surface is
  implemented/proven in this task scope. Do not enable UE accepted-state
  controls or claim live UE runtime ack, live MWORKS downlink, closed_loop,
  controller performance, planner_ready, FAST-LIO success, Factory trace
  consumption, plant tracking, mission success, or parameter identification.
- WeChat sparse completion packet:
  `Results/coagent_gateway/packets/mworks_echo_live_downlink_preflight_004_completed_20260606.json`.
  First local notify attempt used unsupported `template_type=status_update` and
  was blocked before external send; packet was corrected to
  `template_type=completion_notification` before retry. Second local attempt
  showed completion packets require `canonical_status=completed`; packet was
  corrected while preserving the fine-grained status in `status/details`.
  Final bounded send reached the Weixin layer but failed with
  `weixin: sendMessage: ret=-2 errcode=0`; do not retry until the user sends
  one normal text message in the WeChat gateway conversation, then retry once.
  dynamics parameter, simulation evidence, live UE runtime ack, planner_ready,
  closed_loop, or controller-performance claim.
- Sparse WeChat notification for this routing change was attempted through
  `CoAgent/gateway/cc_connect_weixin.py`. The first packet shape was rejected
  locally as `unsupported packet type`; PMO corrected the packet to
  `template_type=blocker_notification`. The single real send then reached
  Weixin and failed with `weixin: sendMessage: ret=-2 errcode=0`. Per gateway
  rules, do not retry in a loop or restart cc-connect for this. Minimal user
  action before any retry is one ordinary message in the WeChat-side Codex
  conversation `MoSim｜WechatCodex` (`019e8358-86b4-7070-8fd6-a2b4f4d2af97`).

## 2026-06-06 CST - ROS2 023 Bspline No-Sample Diagnosis Integrated

- ROS2 R2 returned diagnostic packet
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-BSPLINE-NO-SAMPLE-DIAG-20260606-023.json`.
- The diagnosis confirms `/planning/bspline` topic presence in 022 only proved
  EGO's init-time publisher existed. A non-empty Bspline message is published
  only after successful `reboundReplan()`, and 022 produced no accepted sample.
- Strongest current cause: invalid planner-frame geometry. The 022 odometry
  was approximately `(2456.218, -404.699, -7241.161) m` in `camera_init`, while
  EGO waypoint handling forced goal z to `1.0`, producing a kilometers-scale
  vertical planning problem outside the configured local map envelope.
- Next ROS2 gate must first prove odometry, goal, and local map envelope are in
  the same bounded frame/scale/z and capture map-readiness evidence, then rerun
  only the real-goal `/planning/bspline` acceptance.
- Do not run PositionCommand recorder, publish `/position_cmd`, start the
  20 Hz adapter, or claim planner_ready/closed_loop from 023.

## 2026-06-06 CST - MWORKS 004 Live/Downlink Echo Preflight Prepared

- PMO created task packet
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004.json`
  for `MoSim｜MWORKS动力学与控制验证部`
  (`019e9999-b0d3-7682-bccd-faef08fcf1df`).
- Current MWORKS echo evidence boundary:
  001 is offline/schema smoke, 002 is project-owned MWORKS_MCP result-context
  state smoke, and 003 adapts 002 result-context evidence into
  `mosim.ue_command_echo.v1` fixture rows. None of these prove live UE runtime
  ack or live MWORKS downlink.
- 004 must either implement the smallest project-owned MWORKS/model/adapter
  preflight with source labels stronger than task-003 fixture rows, or return a
  precise blocker if current project surfaces have no MWORKS-to-UE/ROS2
  downlink/transport path in scope.
- Do not enable UE accepted-state controls, expand CoAgent transport/schema,
  edit official `References/MWORKS` baseline, start ROS2/UE runtime, or claim
  live runtime ack, closed_loop, controller performance, planner_ready,
  FAST-LIO success, Factory trace consumption, plant tracking, mission success,
  or parameter identification from 004 preparation alone.

## 2026-06-06 CST - ROS2 022 Bspline Sample Blocker Integrated

- ROS2 R2 returned blocker
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-GOAL-BSPLINE-ACCEPTANCE-20260606-022.json`.
- Real `/Odometry` and `/cloud_registered` inputs were present from
  `/laser_mapping` before and during planner startup, a real waypoint trigger
  was published, planner log reached `Triggered!`, and `/planning/bspline`
  existed with publisher `ego_planner_node_preflight`.
- Acceptance is still blocked: no non-empty
  `ego_planner_msgs/msg/Bspline` echo sample was captured, and
  `Results/ros2_runtime/b1_real_goal_bspline_acceptance_20260606_022/bspline_acceptance_status.txt`
  records `bspline_accepted=false`.
- Key diagnostic clue: the goal was generated from `/Odometry` in
  `camera_init` where source position was approximately
  `(2456.218, -404.699, -7241.161) m`, while the goal z was set to `0.2`.
  This frame/scale/z drift and EGO waypoint-z handling must be diagnosed
  before another acceptance run.
- PMO dispatched ROS2 023 as a diagnostic-only task to
  `MoSim｜ROS2感知定位与规划运行部-R2`
  (`019e9b85-d4d8-7bf3-8afd-a65697cd3889`):
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-BSPLINE-NO-SAMPLE-DIAG-20260606-023.json`.
  `read_thread` shows the target thread is in progress.
- Sparse WeChat blocker notification was sent successfully with dedupe key
  `pmo_ros2_022_bspline_blocker_20260606`; audit log:
  `Results/coagent_gateway/weixin_notifications.jsonl`.
- Do not run
  PositionCommand recorder, enable a 20 Hz adapter, publish or claim
  `/position_cmd`, accept `/planning/bspline` from topic presence alone, or
  claim planner_ready/closed_loop/FAST-LIO quality/local-map quality/controller
  performance/mission success.

## 2026-06-06 CST - Current CoAgent Ops Native Capability Re-Adoption Audit

- `MoSim｜CoAgent运维平台`
  (`019e9bc1-ea9f-7102-b41a-4ef9b2308992`) is the current baseline thread for
  Codex App native thread/automation capability adoption.
- The old `MoSim｜CoAgent运维平台`
  (`019e74d1-72fa-7d33-8783-90584035ae92`) was deleted by the user. Do not
  read, restore, dispatch to, or rely on that thread; old capability research
  from it is historical/incomplete only.
- Current surface exposes `automation_update` and native thread tools.
  Read-only checks found `MoSim｜微信网关运维部` by title, found
  `MoSim｜开源项目探针` by title, and read `MoSim｜Codex 上下文维护部` by ID.
  The context-maintenance thread shows `cwd=C:\mnt\c\Users\HP\Desktop\MoSim`,
  so heartbeat/automation delivery there needs a target-thread cwd/visibility
  validation before use.
- No Codex App automation was created in this audit. The task forbids reading
  Codex private automation state, so duplicate detection could not be completed;
  the CoAgent ops thread must return candidate definitions and missing dedupe
  evidence rather than create a possible duplicate.

## 2026-06-06 CST - MWORKS Echo Result Adapter Smoke Passed

- MWORKS Dynamics And Control Verification completed
  `RFLY-MOSIM-MWORKS-ECHO-RESULT-ADAPTER-SMOKE-20260606-003` with return
  packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-RESULT-ADAPTER-SMOKE-20260606-003.json`.
- Evidence is under
  `Results/mworks_echo_producer_smoke/20260606_003_result_adapter/`. It reads
  task-002 `source=MWORKS_MCP` result-context samples and emits
  `source=MWORKS_MCP_result_adapter_smoke` echo rows only.
- Adapter output: 6 `mosim.ue_command_echo.v1` rows, 5 accepted MWORKS-owned
  command rows, 1 rejected forbidden pose row, `no_pose_overwrite_status=pass`.
  Existing contract checker and UE offline reducer fixture passed; reducer
  states remain `quality_status=smoke_only` and
  `accepted_as_runtime_ack=false`.
- This is not live UE runtime ack, live MWORKS ack/downlink, closed_loop,
  controller performance, planner_ready, FAST-LIO success, Factory trace
  consumption, plant tracking, or parameter identification.

## 2026-06-06 CST - WeChat Gateway Email Alert And Background Health Verified

- User's first QQ email alert command failed because it was run from
  `C:\Users\HP`, so Python searched for
  `C:\Users\HP\Scripts\agent\send_gateway_email_alert.py`. Correct working
  directory is `C:\Users\HP\Desktop\MoSim`.
- The current Codex process did not inherit the user-level SMTP environment
  variables set by `setx`; verification used the same runtime environment
  injection style now configured in Windows Task Scheduler. No authorization
  code was printed or stored in project files.
- A real sparse email alert to `1062771286@qq.com` succeeded:
  `Results/coagent_gateway/email/email_alert_20260606_144121.json`
  reports `ok=true`.
- Local health is currently healthy:
  `python Scripts\agent\check_weixin_gateway_health.py` wrote
  `Results/coagent_gateway/health/weixin_gateway_health_20260606_144142.json`
  with `ok=true`, `ok_local=true`, and no real WeChat canary.
- `python -m py_compile Scripts\agent\check_weixin_gateway_health.py
  Scripts\agent\send_gateway_email_alert.py CoAgent\gateway\cc_connect_weixin.py`
  passed.
- `MoSim Weixin Gateway Local Health` is enabled with `Interval=PT15M`; manual
  scheduled-task trigger at `2026-06-06T14:42:17+08:00` returned
  `LastTaskResult=0` and wrote
  `Results/coagent_gateway/health/weixin_gateway_health_20260606_144217.json`.
- `MoSim Weixin Gateway Canary` remains enabled with `Interval=PT4H`; it was
  not manually triggered in this round to avoid an extra real WeChat canary.
  Its previous `LastTaskResult=3221225786` is historical and should be judged
  again after the next scheduled low-frequency canary.

## 2026-06-06 CST - MWORKS Echo Result-Adapter Task Prepared

- Historical note: at the time this entry was written, UE003 and ROS2 022 were
  still `inProgress`. Later UE003 completed as source-level static smoke and
  ROS2 022 returned `blocked_bspline_sample_missing`; use the newer entries and
  packets above as current state.
- Sunray close-up visual review is already notified through WeChat. Evidence:
  `Results/coagent_gateway/weixin_notifications.jsonl` records successful send
  at `2026-06-06T13:44:41+08:00` for dedupe key
  `sunray150_closeup_material_review_20260606`. Do not resend unless the user
  asks or dedupe state is intentionally reset.
- Prepared MWORKS follow-up task packet
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-ECHO-RESULT-ADAPTER-SMOKE-20260606-003.json`.
  Scope: convert proven MWORKS_MCP result-context echo-status evidence from
  task 002 into `mosim.ue_command_echo.v1` rows and validate existing
  contract/reducer consumption. This is still result-adapter smoke only, not
  live UE runtime ack, live MWORKS downlink, closed_loop, controller
  performance, planner_ready, FAST-LIO success, Factory trace consumption,
  plant tracking, or parameter identification.
- PMO dispatched MWORKS 003 to `MoSim｜MWORKS动力学与控制验证部`
  (`019e9999-b0d3-7682-bccd-faef08fcf1df`) via visible `send_message_to_thread`.
  No WeChat notification was sent because this is neither manual review nor a
  blocker.

## 2026-06-06 CST - UE Console State Component Source Smoke Returned

- UE003 completed in `MoSim｜UE实验控制台与场景交互部` with return packet
  `Results/agent_packets/returns/RFLY-MOSIM-UE-EXPERIMENT-CONSOLE-STATE-COMPONENT-SOURCE-SMOKE-20260606-003.json`.
  Quality is `source_level_component_static_smoke_passed`.
- Added source-level state component:
  `UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleStateComponent.h`
  and
  `UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp`.
  It records pending rows from `mosim.ue_command.v1` request JSON and upgrades
  accepted/rejected only from matching `mosim.ue_command_echo.v1` rows.
- Evidence under
  `Results/unreal_experiment_console/console_state_component_smoke_20260606_003/`
  reports static checker `ok=true`, `sender_remains_sender_only=true`,
  `runtime_echo_receiver_implemented=false`, `planner_ready=false`, and
  `closed_loop_ready=false`. Targeted pytest output shows 16 passing tests.
- PMO spot-check found no Actor pose overwrite or socket receive APIs in the
  new component. This is not Unreal build evidence, live UE runtime ack,
  runtime echo receiver, Blueprint/UMG binding, MWORKS runtime ack, ROS2 runtime
  ack, planner_ready, closed_loop, controller performance, FAST-LIO success, or
  mission success.

## 2026-06-06 CST - Dead ROS2 Thread Deleted And Recovery Rule Updated

- User reviewed PMO's recovery evidence for dead ROS2 thread
  `019e9917-6181-7ec2-b3d6-4b624d6d3348` and deleted it manually. Future ROS2
  work must use `MoSim｜ROS2感知定位与规划运行部-R2`
  (`019e9b85-d4d8-7bf3-8afd-a65697cd3889`) only.
- Reusable rule added to `Docs/Workflows/agent_orchestration.md`: if a visible
  department remains readable but dispatch fails with `agent loop died
  unexpectedly`, PMO records a blocker, notifies human intervention when
  WeChat is available, preserves recovery through packets/ledger, and creates
  or selects a replacement department in parallel instead of waiting on the
  dead thread.
- `Docs/Workflows/agent_task_ledger.md` now marks the old ROS2 thread as
  `active-r2-old-user-deleted` and adds ready-dispatch rows for UE003 source
  component smoke and ROS2 022 real-goal `/planning/bspline` acceptance.
- PMO dispatched UE003 to `MoSim｜UE实验控制台与场景交互部`
  (`019e9b24-50aa-7cd3-9e7c-4c43b224d993`) and ROS2 022 to
  `MoSim｜ROS2感知定位与规划运行部-R2`
  (`019e9b85-d4d8-7bf3-8afd-a65697cd3889`). Both target threads are currently
  `inProgress`; no repeat `continue` tick has been sent.

## 2026-06-06 CST - MWORKS MCP Echo State Smoke Returned

- MWORKS MCP echo state smoke completed in
  `MoSim｜MWORKS动力学与控制验证部` with return packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-MCP-STATE-SMOKE-20260606-002.json`.
  Quality is `mworks_mcp_state_smoke_passed`.
- The department added project-owned model
  `Models/QuadrotorExperiments/EchoMcpStateSmoke.mo` and package-order entry,
  then used Sysplorer MCP to load `Models/QuadrotorExperiments/package.mo`,
  pass `check_model`, simulate 0-1 s with `data=true`, read non-empty
  `GetVarTimes` (`101` samples), and read representative echo-status variables
  at `t=0.0/0.5/1.0`.
- Evidence is under
  `Results/mworks_echo_producer_smoke/20260606_002_mcp_state/`.
  This is MWORKS_MCP state-smoke evidence only. It is not live UE runtime ack,
  closed_loop, controller performance, planner_ready, FAST-LIO success, Factory
  trace consumption, plant tracking, or parameter identification.

## 2026-06-06 CST - UE Reducer Integration Audit Returned

- UE reducer integration audit completed in
  `MoSim｜UE实验控制台与场景交互部` with return packet
  `Results/agent_packets/returns/RFLY-MOSIM-UE-EXPERIMENT-CONSOLE-REDUCER-INTEGRATION-AUDIT-20260606-002.json`.
  Quality is `source_level_integration_audit_only`.
- The audit rejects overloading `UQuadrotorMworksUdpCommandSenderComponent`
  or `UQuadrotorMworksUdpReceiverComponent` with command lifecycle reducer
  state. The next UE source-level slice should add a project-owned
  `UQuadrotorMworksExperimentConsoleStateComponent` that records pending
  command rows and upgrades them only from matching `mosim.ue_command_echo.v1`
  rows.
- No UE GUI, Blueprint, UMG, asset, texture/material, or runtime C++ edit was
  performed by the audit. No live UE/MWORKS/ROS2 runtime ack, planner_ready,
  closed_loop, controller performance, FAST-LIO success, or mission success is
  claimed.

## 2026-06-06 CST - Echo Producer And Department Returns Integrated

- MWORKS echo producer smoke completed in
  `MoSim｜MWORKS动力学与控制验证部` with return packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-PRODUCER-SMOKE-20260606-001.json`.
  It added an offline/schema helper and test for MWORKS-owned command echo rows.
  Quality is `mworks_echo_producer_schema_smoke_passed`, not live MWORKS ack.
- UE echo-state smoke completed in
  `MoSim｜UE实验控制台与场景交互部` with return packet
  `Results/agent_packets/returns/RFLY-MOSIM-UE-EXPERIMENT-CONSOLE-ECHO-STATE-SMOKE-20260606-001.json`.
  Quality is `offline_reducer_smoke_passed`; pending can come from UE command
  intent, but accepted/rejected state requires matching echo rows.
- Sunray close-up review prep completed in
  `MoSim｜Sunray150资产与PBR审核部` with return packet
  `Results/agent_packets/returns/RFLY-MOSIM-SUNRAY150-CLOSEUP-REVIEW-PREP-20260606-001.json`.
  Manual material/texture review remains required; final material acceptance is
  not claimed.
- ROS2 021R is now running in the replacement R2 department. Its result is still
  completed at the narrow input-consumption gate. Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-STABLE-SOURCE-PLANNER-INPUT-20260606-021R.json`.
  Evidence under
  `Results/ros2_runtime/b1_stable_source_planner_input_20260606_021R/`
  proves real `/Odometry` and `/cloud_registered` publishers from
  `/laser_mapping` plus `echo --once` immediately before and during bounded
  planner startup, with planner subscriptions visible during the startup
  window. This only clears the input surface. `/planning/bspline`,
  PositionCommand recorder, planner_ready, closed_loop, FAST-LIO quality, local
  map quality, controller performance, and mission success remain unclaimed.

## 2026-06-06 CST - ROS2 Dispatch Surface Recovered With R2 Thread

- PMO diagnosed the user-reported `Error submitting message` on the ROS2
  department dispatch. The old thread
  `MoSim｜ROS2感知定位与规划运行部`
  (`019e9917-6181-7ec2-b3d6-4b624d6d3348`) remains readable, but a short
  `send_message_to_thread` health check failed with
  `failed to update thread settings: internal error; agent loop died unexpectedly`.
  This is a Codex App visible-thread dispatch surface blocker, not a ROS2
  business blocker.
- Blocker evidence:
  `Results/agent_packets/blockers/PMO-ROS2-VISIBLE-THREAD-DISPATCH-SURFACE-20260606-001.json`.
- PMO created and renamed the replacement visible department
  `MoSim｜ROS2感知定位与规划运行部-R2`
  (`019e9b85-d4d8-7bf3-8afd-a65697cd3889`), initialized it successfully, and
  rerouted pending task packet
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-STABLE-SOURCE-PLANNER-INPUT-20260606-021R.json`
  to R2.
- 2026-06-06 follow-up: PMO rechecked the old thread's latest useful turns and
  project references. The old thread is no longer a recovery dependency; the
  current canonical ROS2 department is R2, and historical recovery should use
  `Results/agent_packets/`, `Results/ros2_runtime/`,
  `Docs/Workflows/agent_task_ledger.md`, and this file. The user may delete or
  archive old thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`.
- 021R is now dispatched to R2. The task still may only prove stable real
  `/Odometry` and `/cloud_registered` publishers with topic info plus
  `echo --once` before/during planner startup, then decide whether planner input
  consumption is blocked. It must not run PositionCommand recorder, accept
  `/planning/bspline`, publish or claim `/position_cmd`, or claim
  planner/closed-loop readiness.

## 2026-06-06 CST - UE And Sunray Departments Dispatched In Parallel

- User requested coordinating other departments in parallel when tasks do not
  conflict.
- PMO verified both visible department threads are idle:
  `MoSim｜UE实验控制台与场景交互部`
  (`019e9b24-50aa-7cd3-9e7c-4c43b224d993`) and
  `MoSim｜Sunray150资产与PBR审核部`
  (`019e9b25-066e-7372-8152-209c2b1322a4`).
- Dispatched UE echo-state smoke task:
  `Results/agent_packets/tasks/ue/RFLY-MOSIM-UE-EXPERIMENT-CONSOLE-ECHO-STATE-SMOKE-20260606-001.json`.
  Scope: offline command pending/accepted/rejected state reducer or fixture
  smoke based on MWORKS/ROS2 echo contracts. No UE GUI, no Blueprint/UMG runtime
  asset edit, no live runtime ack claim.
- Dispatched Sunray close-up review-prep task:
  `Results/agent_packets/tasks/sunray_pbr/RFLY-MOSIM-SUNRAY150-CLOSEUP-REVIEW-PREP-20260606-001.json`.
  Scope: review checklist/image grouping/next bounded PBR rework plan after the
  path fix. No Blender/UE GUI, no texture/material/geometry/dynamics/extrinsic
  edits, no final material acceptance claim.
- The two tasks have disjoint write scopes and can run in parallel with the
  MWORKS/ROS2 echo contract work already integrated.

## 2026-06-06 CST - PMO PBR Path Fix And UE Echo Boundary

- PMO continued active goal
  `推进 MoSim P0 后续最小闭环的下一批可落地任务` with two disposable
  read-only sub-agents:
  `019e9b68-df76-7dd3-a451-b28e547d4485` audited the Sunray150 PBR path
  normalization blocker, and `019e9b69-2439-7913-952b-455a0d056547` audited the
  UE command/echo smoke boundary.
- Fixed the Windows-native Sunray150 PBR miniloop blocker. The checker now
  accepts WSL-equivalent `/mnt/<drive>/...` paths only after converting them
  back through the normal project-boundary guard. The texture generator now
  writes project-relative manifest paths with stable LF line endings.
- Regenerated
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/sunray150_texture_manifest.json`;
  it no longer contains `/mnt/c`, `C:\mnt\c`, or `C:\Users` absolute paths.
- Added regression test
  `Scripts/tests/test_sunray150_pbr_miniloop_paths.py` so future compatibility
  fixes do not weaken the project path guard.
- Validation passed:
  `python Scripts/UE5/check_sunray150_pbr_miniloop.py`;
  `python -m pytest Scripts/tests/test_sunray150_pbr_miniloop_paths.py -q`;
  `python -m py_compile Scripts/UE5/check_sunray150_pbr_miniloop.py Scripts/UE5/assets/generate_sunray150_pbr_texture_set.py Scripts/tests/test_sunray150_pbr_miniloop_paths.py`;
  `git diff --check` on the touched Sunray files.
- UE command/echo audit boundary was reaffirmed with
  `python Scripts/UE5/check_ue_command_sender_contract.py` and
  `python -m pytest Scripts/tests/test_ue_command_sender_contract.py Scripts/tests/test_ue_command_echo_contract.py Scripts/tests/test_ue_command_adapter_smoke.py Scripts/tests/test_ue_command_schema_docs.py -q`.
  Current evidence is still `source_level_static_check` plus
  `offline_adapter_smoke`/loopback only. Do not claim live UE console runtime,
  MWORKS/ROS2 accepted command ack, controller/planner readiness, FAST-LIO
  success, or closed loop from this smoke.
- Next PMO task candidate:
  `RFLY-MOSIM-MWORKS-ROS2-ECHO-ADAPTER-CONTRACT-20260606-001`, owned jointly
  by `MoSim｜MWORKS动力学与控制验证部` and
  `MoSim｜ROS2感知定位与规划运行部`, to freeze or implement the authoritative
  `mosim.ue_command_echo.v1` producer/consumer contract before enabling UE
  controls as accepted runtime state.
- WeChat completion notification was verified after two adapter-usage mistakes:
  `cc_connect_weixin.py notify` requires `--packet <json>` and does not support
  `--stdin`; custom `mosim.wechat_notification.v1` packets are rejected as
  `unsupported packet type`. The working sparse completion packet used
  `template_type=completion_notification`, `canonical_status=completed`, and
  task fields in
  `Results/coagent_gateway/packets/pmo_pbr_path_ue_echo_boundary_completed_20260606.json`;
  the adapter returned `Message sent successfully.`.
- PMO dispatched follow-up visible-thread contract tasks:
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-ECHO-ADAPTER-CONTRACT-20260606-001.json`
  to `MoSim｜MWORKS动力学与控制验证部`
  (`019e9999-b0d3-7682-bccd-faef08fcf1df`) and
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-ECHO-ADAPTER-CONTRACT-20260606-001.json`
  to `MoSim｜ROS2感知定位与规划运行部`
  (`019e9917-6181-7ec2-b3d6-4b624d6d3348`). Both departments completed
  read-only contract return packets:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-ADAPTER-CONTRACT-20260606-001.json`
  and
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-ECHO-ADAPTER-CONTRACT-20260606-001.json`.
  These packets define command echo authority and rejection semantics only;
  they do not prove runtime echo producers, live UE console acceptance,
  planner readiness, PositionCommand, or closed loop.
- Sunray close-up material manual review was sent through WeChat after fixing
  the review packet status from unsupported `review_required` to allowed
  `needs_review`. Packet:
  `Results/coagent_gateway/packets/sunray150_closeup_material_review_20260606.json`;
  adapter returned `Message sent successfully.`.

## 2026-06-06 CST - WeChat Thread Route Clarified

- User corrected the WeChat recovery route: for `ret=-2`, the ordinary inbound
  message such as "你好" should be sent in `MoSim｜WechatCodex`
  (`019e8358-86b4-7070-8fd6-a2b4f4d2af97`). That conversation is not the
  gateway operations owner.
- Gateway incidents, health failures, QR/login/context-token diagnostics, and
  recovery requests should go to `MoSim｜微信网关运维`
  (`019e9855-aa43-7fe2-807e-be7d4095877b`).
- Updated `AGENTS.md`, `Docs/Index/codex_app_session_research.md`,
  `Docs/Workflows/new_conversation_context.md`, and
  `Docs/Workflows/debug_mcp.md` with this distinction.
- PMO reran the gateway health check:
  `python Scripts/agent/check_weixin_gateway_health.py` returned `ok=true`,
  `ok_local=true`, with health record
  `Results/coagent_gateway/health/weixin_gateway_health_20260606_132629.json`.
- After the inbound refresh, PMO retried the sparse completion packet
  `Results/coagent_gateway/packets/codex_native_surface_gate_pmo_completed_20260606.json`
  once through `CoAgent/gateway/cc_connect_weixin.py notify --send`; it returned
  `Message sent successfully.` No gateway-ops incident dispatch was needed.
- Current working rule: for future `ret=-2`, request one ordinary inbound
  message in `MoSim｜WechatCodex`, retry once, and only send an incident to
  `MoSim｜微信网关运维` if the bounded retry still fails or health diagnostics
  show a gateway/runtime problem.

## 2026-06-06 CST - PMO Native Surface Gate Checker Added

- PMO created an active Codex goal for landing native Codex surface selection
  into daily MoSim dispatch practice.
- Used two read-only disposable sub-agents:
  `019e9b55-899f-7670-beeb-0d2151c1e521` audited task packet/schema/template/
  dispatch-helper gaps, and `019e9b55-ca70-7291-baf6-f36a74bb278d` audited P1
  automation/notify/goal validation entry points. Both confirmed that broad
  CoAgent schema/runtime/transport expansion should remain gated.
- Added read-only checker
  `Scripts/quality/check_agent_task_native_surface_gate.py` and regression test
  `Scripts/tests/test_agent_task_native_surface_gate.py`. New non-trivial JSON
  task packets should pass this checker before PMO dispatch.
- Documented the compatibility rule in
  `Docs/Workflows/agent_orchestration.md`,
  `Docs/Workflows/tooling_assets_governance.md`, and
  `CoAgent/dispatch/communication_contract.md`: `native_surface_gate` may live
  at top level or under `metadata.native_surface_gate`; required fields include
  selected surface, selection reason, worktree decision, and delegated
  return/blocker paths.
- The checker intentionally rejects existing historical packets such as
  `Results/agent_packets/tasks/ue/RFLY-MOSIM-UE-EXPERIMENT-CONSOLE-P0-SLICE-20260606-001.json`
  because they predate the new gate. This is expected; do not rewrite history
  unless the packet is being reused for a new dispatch.
- Result packet:
  `Results/agent_packets/returns/CODEX-NATIVE-SURFACE-GATE-PMO-20260606-001.json`.
- Validation passed:
  `python -m pytest Scripts/tests/test_agent_task_native_surface_gate.py -q`;
  `python -m py_compile Scripts/quality/check_agent_task_native_surface_gate.py Scripts/tests/test_agent_task_native_surface_gate.py`;
  `git diff --check` on the touched docs/scripts.
- Sparse WeChat completion packet
  `Results/coagent_gateway/packets/codex_native_surface_gate_pmo_completed_20260606.json`
  reached the Weixin layer but failed once with
  `weixin: sendMessage: ret=-2 errcode=0`. Per gateway policy, PMO did not
  retry in a loop. Next retry should happen only after the user sends one
  ordinary message in the WeChat gateway chat.
- Later correction: the ordinary refresh message belongs in
  `MoSim｜WechatCodex` (`019e8358-86b4-7070-8fd6-a2b4f4d2af97`), not the
  gateway ops thread. After the user-side refresh, PMO retried this same packet
  once and the adapter returned `Message sent successfully.`

## 2026-06-06 CST - Visible Department Dispatch Succeeded For UE And Sunray

- PMO corrected the UE and Sunray task packets before dispatch so their
  `target_thread` and `target_thread_id` point to the new canonical department
  threads:
  `MoSim｜UE实验控制台与场景交互部`
  `019e9b24-50aa-7cd3-9e7c-4c43b224d993`, and
  `MoSim｜Sunray150资产与PBR审核部`
  `019e9b25-066e-7372-8152-209c2b1322a4`.
- `send_message_to_thread` succeeded for both departments. Both visible
  threads ran to completion and became idle again. No background CLI dispatch
  or hidden thread workaround was used.
- UE return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-UE-EXPERIMENT-CONSOLE-P0-SLICE-20260606-001.json`.
  Result: completed. It defines the P0 operator console shell/contract slice
  and confirms current evidence is source-level command intent only. No live
  UE console, runtime MWORKS/ROS2 ack, planner readiness, or closed-loop
  readiness is claimed.
- Sunray/PBR return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-SUNRAY150-DAE-PBR-AUDIT-20260606-001.json`.
  Result: completed with manual review required. Component close-up review
  targets are carbon/standoffs/fasteners, MID-360 housing/window/connector,
  motor/prop/guard, and front-camera/PCB/connectors/cables/battery.
- Sunray/PBR found a real Windows-native portability issue: the texture
  manifest stores `/mnt/c/...` absolute paths, which Windows Python resolves as
  `C:\mnt\c\...` and triggers the project path guard in
  `Scripts/UE5/check_sunray150_pbr_miniloop.py`. This is a path-normalization
  blocker for the miniloop check, not proof that texture PNGs are missing.
- Follow-up candidates: one UE schema/fixture smoke implementation task; one
  MWORKS/ROS2 authoritative command-echo contract task; one Sunray texture
  manifest path-normalization task; and one user manual review packet for the
  four Sunray close-up batches.

## 2026-06-06 CST - Renamed ROS2 And MWORKS Department Threads

- User pointed out that the old department names ending in "集成" were awkward
  as long-term department names.
- PMO renamed ROS2 department thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`
  from `MoSim｜ROS2 Runtime 集成` to:
  `MoSim｜ROS2感知定位与规划运行部`.
- PMO renamed MWORKS department thread `019e9999-b0d3-7682-bccd-faef08fcf1df`
  from `MoSim｜MWORKS-Control 集成` to:
  `MoSim｜MWORKS动力学与控制验证部`.
- These are now the canonical visible department names. Existing historical
  task packets may still contain old target labels, but future PMO dispatch
  prompts and recovery docs should use the new names.

## 2026-06-06 CST - Recreated UE And Sunray Department Threads With Correct Names

- User requested recreating the two previously deleted/problematic department
  threads and emphasized correct naming.
- PMO created and verified the new canonical UE department:
  `MoSim｜UE实验控制台与场景交互部`
  `019e9b24-50aa-7cd3-9e7c-4c43b224d993`.
- PMO created and verified the new canonical Sunray/PBR department:
  `MoSim｜Sunray150资产与PBR审核部`
  `019e9b25-066e-7372-8152-209c2b1322a4`.
- Both prompts addressed the target thread as the department itself with
  "你就是该部门线程，请初始化自己"; neither prompt asked the target to create
  another thread.
- Both new departments replied with the expected one-line initialization
  message and are idle, waiting for PMO task packets.
- ROS2 department thread `019e9917-6181-7ec2-b3d6-4b624d6d3348` was read-only
  verified and not modified. Its later canonical title is
  `MoSim｜ROS2感知定位与规划运行部`.
- Old problematic UE/Sunray threads remain archived/superseded and must not be
  used for future dispatch.

## 2026-06-06 CST - Archived Old UE And Sunray Department Threads

- User requested deleting the two problematic visible department threads and
  explicitly said not to touch the ROS2 thread.
- PMO archived old Sunray DAE/PBR thread
  `019e9af4-6ffc-7db0-a037-187dd3787f2e`.
- PMO archived old UE Experiment Console thread
  `019e9af5-3768-77b0-aa9d-3c21ea20d99d`.
- PMO did not archive or modify ROS2 department thread
  `019e9917-6181-7ec2-b3d6-4b624d6d3348`.
- Updated `Docs/Workflows/agent_task_ledger.md` and
  `Docs/Workflows/rfly_mosim_p0_10h_execution_plan.md`: UE and Sunray
  departments now have no active canonical visible thread. Their old task
  packets remain PMO-local references only and must not be treated as valid
  department returns.
- If UE or Sunray departments are recreated later, the initial prompt must say
  "你就是该部门线程，请初始化自己"; never say "请创建线程".

## 2026-06-06 CST - Visible Department Dispatch Aborted By User

- PMO prepared two scoped department task packets without creating any new
  thread:
  `Results/agent_packets/tasks/sunray_pbr/RFLY-MOSIM-SUNRAY150-DAE-PBR-AUDIT-20260606-001.json`
  for Sunray thread `019e9af4-6ffc-7db0-a037-187dd3787f2e`, and
  `Results/agent_packets/tasks/ue/RFLY-MOSIM-UE-EXPERIMENT-CONSOLE-P0-SLICE-20260606-001.json`
  for UE thread `019e9af5-3768-77b0-aa9d-3c21ea20d99d`.
- Both direct `send_message_to_thread` attempts failed once with Codex App
  internal error `agent loop died unexpectedly`; `read_thread` still worked.
  A short CLI `codex exec resume` probe to Sunray returned `SUNRAY_COMM_OK`,
  but the formal foreground task exceeded PMO's 60s outer timeout and produced
  an interrupted visible turn. PMO then tried hidden background CLI dispatch for
  Sunray/UE, which proved unsafe for visible coordination: user reported the
  Sunray thread did not show the new thread-authority constraint and the UE
  thread was stuck, then manually terminated the attempts.
- PMO stopped the residual `sunray_dispatch_resume` and `ue_dispatch`
  powershell/codex processes. The ledger rows are now
  `dispatch-aborted-by-user`. No return/blocker packet exists for either task,
  so neither department result is accepted.
- Updated `Docs/Workflows/agent_orchestration.md`: App forwarding failures may
  be probed with CLI resume, but formal tasks must not be launched through
  unattended background `codex exec resume` until a visible-delivery and
  controlled-stop workflow is verified. If App forwarding and safe CLI dispatch
  are unavailable, mark `dispatch-blocked-tool`/manual fallback or keep the work
  PMO-local.
- Updated `Docs/Workflows/rfly_mosim_p0_10h_execution_plan.md` with the
  department communication contract: durable returns must be packet files under
  `Results/agent_packets/returns/` or `Results/agent_packets/blockers/`; chat
  and WeChat are notifications only.
- Sparse WeChat blocker packet
  `Results/coagent_gateway/packets/rfly_mosim_department_dispatch_blocked_thread_send_20260606.json`
  reached the Weixin send layer but failed with
  `weixin: sendMessage: ret=-2 errcode=0`. Per gateway rules, PMO did not retry
  in a loop. If WeChat notification is needed again, the next minimal action is
  one ordinary user message in the WeChat gateway chat, then one bounded retry.
- Manual fallback if the user wants immediate department start: open Sunray
  thread `019e9af4-6ffc-7db0-a037-187dd3787f2e` and paste the Sunray packet
  path; open UE thread `019e9af5-3768-77b0-aa9d-3c21ea20d99d` and paste the UE
  packet path. Otherwise PMO should continue the file-level audit locally in
  the main thread instead of trying more automatic dispatch. PMO-only thread
  creation remains in force.

## 2026-06-06 CST - PMO Corrected Duplicate Department Thread Creation

- PMO incorrectly initialized new visible department threads with prompts that
  said "请创建并初始化一个线程", causing recursive department creation instead
  of direct self-initialization.
- Archived duplicate/intermediate threads:
  `019e9af2-de9e-7093-ac4f-8126b2ce1272`,
  `019e9af3-6c57-7f21-b6b9-532391b6e08b`, and
  `019e9af4-3fb5-7b41-9b11-2195c3d4d6b1`.
- Canonical visible reusable department thread
  `MoSim｜UE Experiment Console 集成` is now:
  `019e9af5-3768-77b0-aa9d-3c21ea20d99d`.
- Canonical visible reusable department thread
  `MoSim｜Sunray150 DAE/PBR 资产优化` is now:
  `019e9af4-6ffc-7db0-a037-187dd3787f2e`.
- Current thread-creation authority is PMO-only: only main PMO thread
  `019e9868-83ea-70f0-92c5-a3a408bd78c6` may create, fork, rename, or archive
  visible department threads unless the user explicitly changes this rule.
  Other departments may return a charter suggestion or blocker, but must not
  create or delegate visible-thread creation.
- Future `create_thread` prompts must say "你就是该部门线程，请初始化自己";
  they must not say "请创建线程" or wrap another creation request.
- UE department received this thread-authority correction packet. Sending the
  same correction to the Sunray department failed once with Codex App internal
  error; the durable file-level rule above applies before the next task packet.
- Existing `MoSim｜MWORKS动力学与控制验证部`
  (`019e9999-b0d3-7682-bccd-faef08fcf1df`) remains the dedicated MWORKS
  thread; no new MWORKS thread is needed now.
- Historical note: `MoSim｜ROS2感知定位与规划运行部`
  (`019e9917-6181-7ec2-b3d6-4b624d6d3348`) was the owner at this point in the
  run, but it was later superseded by R2 after its send surface failed. Current
  ROS2 work must use `MoSim｜ROS2感知定位与规划运行部-R2`
  (`019e9b85-d4d8-7bf3-8afd-a65697cd3889`).
- Thread creation must be done from the PMO thread using Codex App thread
  management capability. The senior architecture thread
  `019e0198-a041-77f1-84d0-c5524bfd4b81` can advise prompts and routing, but
  must not create or relay thread creation.
- Sparse WeChat notification packet
  `Results/coagent_gateway/packets/rfly_mosim_departments_created_ue_console_sunray_pbr_20260606.json`
  reached the Weixin send layer but failed once with
  `weixin: sendMessage: ret=-2 errcode=0`. Do not retry in a loop; the next
  valid action is one ordinary user message in the WeChat gateway chat, then
  one bounded retry if notification is still needed.

## 2026-06-06 CST - MWORKS 019 Attitude Feedback Bridge Passed And ROS2 021 Dispatched

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019`
  returned completed in thread `019e9999-b0d3-7682-bccd-faef08fcf1df`.
- Added `FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke`; it extends Iso23,
  preserves the sampled/held display-position bridge, and changes only the
  controller roll/pitch/yaw measurement source to sampled/held
  `sensors1_1.AngleMea[1..3]` through `attitude_sampler/attitude_hold`.
- Sysplorer MCP `check_model` passed, 0-2 s `SimulateModel` returned
  `data=true`, `GetVarTimes=1001`, and reference/display/attitude bridge
  aliases were readable at 0/1/2 s. No 6140 text appeared.
- This is one incremental result-context bridge pass only. It is not Factory
  trace consumption, closed_loop, controller performance, plant tracking, or
  parameter identification evidence.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/attitude_feedback_bridge_20260606_019/`.
- PMO dispatched ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-STABLE-SOURCE-PLANNER-INPUT-20260606-021`
  to thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`.
- 021 is a narrow retry after 020: it must keep real `/Odometry` and
  `/cloud_registered` publishers alive and prove publisher counts plus
  `ros2 topic echo --once` immediately before and during planner startup.
- If either topic lacks a live publisher or echo sample before planner launch,
  021 must write a blocker without launching planner.
- Recorder, `/position_cmd`, `/mosim/planner/position_cmd`,
  `/planning/bspline` acceptance, FAST-LIO `/path` conversion, fake
  pointcloud/map, planner readiness, and closed-loop claims remain forbidden.
- P0 remains `quality_status=smoke_only`, `planner_ready=false`, and
  `closed_loop_ready=false`.
- WeChat notification packet must use the adapter-whitelisted
  `blocker_notification/manual_review_required` shape even for sparse
  non-blocking milestones. A first 021 notification attempt with
  `class=progress_update` was locally rejected by the adapter before Weixin
  send; PMO corrected the packet shape and retried once.
- Corrected sparse WeChat checkpoint packet
  `Results/coagent_gateway/packets/rfly_mosim_p0_dispatched_ros2_021_20260606.json`
  sent successfully through `CoAgent/gateway/cc_connect_weixin.py`.
- PMO integrated 019 into
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`,
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json`, and
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_CLOSED_LOOP_GAP_MATRIX.json`.
  The new `mworks_attitude_feedback_bridge` gate records the Iso25 local pass
  while keeping P0 `smoke_only`.
- Sent sparse WeChat checkpoint packet
  `Results/coagent_gateway/packets/rfly_mosim_p0_integrated_mworks_019_waiting_ros2_021_20260606.json`
  successfully through the project WeChat adapter.

## 2026-06-06 CST - PMO Integrated MWORKS 018 And Dispatched MWORKS 019

- PMO integrated MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-FIRST-CONTROL-FEEDBACK-GROUP-20260606-018`
  into the P0 quality chain. P0 remains `quality_status=smoke_only`,
  `planner_ready=false`, and `closed_loop_ready=false`.
- 018 is accepted only as blocker evidence: direct
  `sensors1_1.AngleMea[1..3]` controller attitude feedback on top of Iso23
  passed `check_model` but failed 0-2 s `SimulateModel data=false`, with
  `GetVarTimes=[]` and aliases unavailable. No 6140 text was reported.
- PMO dispatched MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019`
  to thread `019e9999-b0d3-7682-bccd-faef08fcf1df`. It may test exactly one
  sampled/held or first-order attitude-feedback bridge variant, must preserve
  the Iso23 sampled/held display-position bridge, and must not retry the full
  Factory wrapper or add actuator/motor/speedSensor/control-output reconnects.
- Evidence/gates regenerated:
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`,
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json`, and
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_CLOSED_LOOP_GAP_MATRIX.json`.

## 2026-06-06 CST - MWORKS 018 Direct Attitude Feedback Boundary Found

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-FIRST-CONTROL-FEEDBACK-GROUP-20260606-018`
  returned blocked after one allowed controller/control-feedback group.
- Added `FactoryTraceIso24DirectAttitudeFeedbackSmoke`; it preserves the Iso23
  sampled/held display-position bridge and changes only the controller
  measurement path to direct `sensors1_1.AngleMea[1..3]` roll/pitch/yaw
  feedback via inherited `RealExpression` source overrides.
- Sysplorer MCP `check_model` passed, but 0-2 s `SimulateModel` returned
  `data=false`; `GetVarTimes=[]` and alias probes returned `[]`. No 6140 text
  was reported in this run.
- First new boundary: direct `AngleMea` attitude feedback on top of Iso23
  clears the result context. Next validation should test sampled/held or
  first-order attitude-feedback bridge variants while preserving Iso23.
- No full Factory retry, actuator/motor/speedSensor/control-output reconnect,
  direct display `PosMea` reconnect, or closed-loop/Factory trace-consumption
  claim was made.
- Blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-FIRST-CONTROL-FEEDBACK-GROUP-20260606-018.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/first_control_feedback_group_20260606_018/`.

## 2026-06-06 CST - PMO Integrated 017/020 Gates And Dispatched MWORKS 018

- PMO integrated MWORKS 017 and ROS2 020 into the P0 quality chain:
  `RUN_MANIFEST.json`, `P0_BUNDLE_AUDIT.json`, and
  `P0_CLOSED_LOOP_GAP_MATRIX.json` now keep both gates blocking while
  preserving `quality_status=smoke_only`, `planner_ready=false`, and
  `closed_loop_ready=false`.
- MWORKS 017 is recorded as topology/scope evidence only:
  sensor/display-only reconnect scope is exhausted after Iso23, so the next
  MWORKS task must explicitly permit one controller/control-feedback reconnect
  group. It is not new MWORKS simulation evidence.
- ROS2 020 is recorded as a startup-surface blocker: fresh odom/cloud restore
  passed, but planner input consumption was not accepted because the planner
  window showed `no odom` and zero `/Odometry` and `/cloud_registered`
  publishers.
- PMO dispatched MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-FIRST-CONTROL-FEEDBACK-GROUP-20260606-018`
  to thread `019e9999-b0d3-7682-bccd-faef08fcf1df`. It may add exactly one
  controller/control-feedback reconnect group from Iso23, must preserve the
  sampled/held display-position bridge, and must not retry the full Factory
  wrapper or add actuator/motor reconnects.
- WeChat notification channel is restored per user confirmation. PMO sparse
  status packets should include origin/self thread id
  `019e9868-83ea-70f0-92c5-a3a408bd78c6`.

## 2026-06-06 CST - ROS2 020 Planner Startup Probe Blocked

- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-STARTUP-PROBE-20260606-020`
  ran one bounded `runtime_disabled=false` startup-surface probe after a fresh
  019-style restore.
- Fresh restore succeeded and recorded current real local sensed inputs:
  `/Odometry` 149 samples, `/cloud_registered` 148 samples over 16 s, with
  FAST-LIO truth evaluation `status=pass`, RMSE `0.716944 m`, max error
  `1.084927 m`, yaw RMSE `0.015175 rad`. Truth remains validation oracle only,
  not planner input.
- The isolated EGO planner node started and created graph endpoints, but the
  probe is blocked: planner log stayed in FSM `INIT` and repeatedly printed
  `no odom.` / `wait for goal.`, while during-window topic info showed planner
  subscriptions for `/Odometry` and `/cloud_registered` but publisher count
  `0` for both topics.
- `/planning/bspline` appeared only as an unaccepted startup-surface topic-list
  observation; it is not trajectory/planner evidence. `/position_cmd` and
  `/mosim/planner/position_cmd` remained absent. No PositionCommand recorder
  was run.
- Final cleanup evidence shows only rosbridge/rosapi graph entries and no
  matching planner/FAST-LIO/replay processes. Blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-STARTUP-PROBE-20260606-020.json`.
  Evidence directory:
  `Results/ros2_runtime/b1_planner_startup_probe_20260606_020/`.

## 2026-06-06 CST - MWORKS 017 Sensor/Display Scope Exhausted

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-NEXT-SENSOR-DISPLAY-GROUP-20260606-017`
  returned blocked without creating a new model.
- Topology comparison from Iso23 to the target Factory trace wrapper shows the
  only `navigationDisplay` sensor/display connections are already represented:
  inherited `planningReference.position_command -> reference_position`, and
  Iso23 sampled/held `sensors1_1.PosMea -> actual_position`.
- The remaining differences are controller/control-feedback or actuator paths,
  which 017 explicitly forbids. Creating an artificial sensor/display group
  would not correspond to the target wrapper, and full Factory retry remains
  forbidden.
- No new MWORKS simulation evidence is claimed for 017. Iso23 remains the last
  passing MCP simulation baseline from 016.
- Blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-NEXT-SENSOR-DISPLAY-GROUP-20260606-017.json`.
  Topology artifact:
  `Results/mworks_trace_consumption/next_sensor_display_group_20260606_017/`.

## 2026-06-06 CST - PMO Dispatched ROS2 020 And MWORKS 017

- PMO dispatched two follow-up P0 gates after integrating ROS2 019 and MWORKS
  016. P0 remains `quality_status=smoke_only`, `planner_ready=false`, and
  `closed_loop_ready=false`.
- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-STARTUP-PROBE-20260606-020`
  historically went to thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`.
  That thread is now superseded by R2. The task itself remained bounded:
  `runtime_disabled=false` startup-surface probe after a fresh 019-style
  `/Odometry` and `/cloud_registered` restore. PositionCommand recorder,
  `/position_cmd` claims, `/planning/bspline` acceptance, fake pointcloud/map,
  and planner/closed-loop claims remain forbidden.
- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-NEXT-SENSOR-DISPLAY-GROUP-20260606-017`
  goes to thread `019e9999-b0d3-7682-bccd-faef08fcf1df`. It must use Iso23 as
  the passing baseline and add exactly one remaining sensor/display reconnect
  group before any full Factory retry.
- WeChat local API was repaired by ops, but the last business notification
  reached Weixin and returned `ret=-2`; PMO will not retry until the user sends
  one normal gateway-chat message, then retry once with origin thread id
  `019e9868-83ea-70f0-92c5-a3a408bd78c6`.

## 2026-06-06 CST - PMO Integrated MWORKS 016 And ROS2 019 Into P0 Gates

- PMO integrated MWORKS 016 and ROS2 019 into the P0 generation chain:
  `RUN_MANIFEST.json`, `P0_BUNDLE_AUDIT.json`,
  `P0_CLOSED_LOOP_GAP_MATRIX.json`, and sparse status packet
  `Results/coagent_gateway/packets/rfly_mosim_p0_sparse_status_20260606.json`.
- Current P0 remains `quality_status=smoke_only`, `planner_ready=false`, and
  `closed_loop_ready=false`.
- MWORKS 016 is accepted only as narrow Iso23 display-position bridge evidence:
  sampled/held `PosMea` restores result context and removes 6140 for
  `navigationDisplay.actual_position`; it is not Factory trace consumption.
- ROS2 019 is accepted only as odom/cloud input-source readiness:
  `/Odometry=93` and `/cloud_registered=92` over 10 s with primary truth
  evaluation pass. It permits a later separate bounded
  `runtime_disabled=false` planner startup probe after a fresh restore, but it
  is not planner runtime, PositionCommand, recorder, or closed-loop evidence.
- Regenerated artifacts and checks:
  `python Scripts\quality\build_p0_slice_run_manifest.py --validate`,
  `python Scripts\quality\check_p0_run_bundle.py ...`,
  `python Scripts\quality\summarize_p0_closed_loop_gap_matrix.py`,
  `python Scripts\quality\build_p0_sparse_status_packet.py`,
  `python -m py_compile ...`, focused P0 pytest, JSON parse, and
  `git diff --check` all passed.
- WeChat ops restored the local API socket, but the last business send reached
  Weixin and returned `ret=-2`; do not retry P0 notification until the user
  sends one normal message in the gateway chat, then retry once with PMO thread
  id `019e9868-83ea-70f0-92c5-a3a408bd78c6`.

## 2026-06-06 CST - ROS2 019 Odom/Cloud Restore Completed

- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-ODOM-CLOUD-RESTORE-20260606-019`
  completed the odom/cloud input restore gate for later planner startup.
- Bounded Gate B restore via
  `Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh` produced current
  FAST-LIO runtime outputs under
  `Results/ros2_runtime/b1_odom_cloud_restore_20260606_019/current_restore_live/`.
- Primary current recording: `/Odometry=93`, `/cloud_registered=92`,
  `/path=9` over 10 s; estimated odom/cloud rates are about 9 Hz. Livox/IMU
  input probe passed with Livox CustomMsg at 9.14666 Hz and IMU at 184.332 Hz.
- Truth evaluation for the primary 10 s restore passed with position RMSE
  `0.305369 m`, max position error `0.519524 m`, and yaw RMSE
  `0.013956 rad`. Truth remains a validation oracle only, not planner input.
- This proves only that real local sensed `/Odometry` and `/cloud_registered`
  can be restored for a later separate `runtime_disabled=false` planner
  startup probe. It is not planner runtime, `/planning/bspline`,
  PositionCommand, recorder, or closed-loop evidence.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-ODOM-CLOUD-RESTORE-20260606-019.json`.
  Evidence artifacts:
  `Results/ros2_runtime/b1_odom_cloud_restore_20260606_019/`.

## 2026-06-06 CST - MWORKS 016 Position Bridge Probe Passed

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016`
  completed as a display-position bridge/result-context probe only.
- Added `FactoryTraceIso23PositionSampleHoldBridgeSmoke` under
  `Models/QuadrotorExperiments/`; it extends the passing Iso21 baseline and
  changes only the inherited `actual_position` source to sampled/held
  `sensors1_1.PosMea[1..3]` before `navigationDisplay.actual_position`.
- Sysplorer MCP load/check passed, 0-2 s `SimulateModel` returned
  `data=true`, `GetVarTimes=1001`, and display actual/reference/bridge aliases
  were readable at t=0, t=1, and t=2. Error 6140 was removed for this narrow
  bridge.
- The 015 direct vector reconnect remains rejected; it likely overconstrained
  the inherited Factory-lite `actual_position` input by adding a second source.
- This is not closed-loop, Factory trace consumption, controller performance,
  plant tracking, or parameter identification evidence. No full Factory wrapper
  retry was attempted and no official baseline was edited.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/position_bridge_20260606_016/`.

## 2026-06-06 CST - PMO Dispatched MWORKS 016 And ROS2 019

- PMO dispatched the next two P0 gates after integrating ROS2 018 and MWORKS
  015 blockers.
- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016`
  goes to thread `019e9999-b0d3-7682-bccd-faef08fcf1df`. It may only test an
  Iso23 sampled/held or RealExpression bridge between `sensors1_1.PosMea` and
  `navigationDisplay.actual_position`.
- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-ODOM-CLOUD-RESTORE-20260606-019`
  historically went to thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`.
  That thread is now superseded by R2. The task itself only restored and proved
  live real `/Odometry` plus `/cloud_registered` input readiness.
- Both tasks preserve the current P0 boundary: no full Factory retry first, no
  PositionCommand recorder, no `runtime_disabled=false` planner startup in 019,
  no planner/closed_loop/Factory trace-consumption claim.
- WeChat business notification is still not retried because the last business
  send reached Weixin and returned `ret=-2`; wait for one normal user message in
  the gateway chat before a single bounded retry.

## 2026-06-06 CST - PMO Integrated ROS2 018 And MWORKS 015 Blockers

- PMO integrated ROS2 018 and MWORKS 015 into the P0 generation chain:
  `RUN_MANIFEST.json`, `P0_BUNDLE_AUDIT.json`,
  `P0_CLOSED_LOOP_GAP_MATRIX.json`, and sparse status packet
  `Results/coagent_gateway/packets/rfly_mosim_p0_sparse_status_20260606.json`.
- P0 remains `quality_status=smoke_only`, `planner_ready=false`, and
  `closed_loop_ready=false`.
- Current ROS2 blocker: live graph lacks real `/Odometry` and
  `/cloud_registered`, so `runtime_disabled=false` planner startup is not
  cleared.
- Current MWORKS blocker: direct `sensors1_1.PosMea` to
  `navigationDisplay.actual_position` reconnect passes `check_model` but fails
  simulation with error 6140 and empty result context.
- WeChat notification remains degraded after prior `ret=-2`; do not retry
  until the user sends one normal message in the gateway chat.

## 2026-06-06 CST - MWORKS 015 Sensor-Bus Reconnect Blocked

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015`
  returned a blocker after one narrow reconnect probe from Iso21.
- Added `FactoryTraceIso22SensorDisplayReconnectSmoke` under
  `Models/QuadrotorExperiments/`; it extends the passing Iso21 baseline and
  adds only `sensors1_1.PosMea -> navigationDisplay.actual_position` plus
  display actual/reference aliases.
- Sysplorer MCP dependency load and `check_model` passed, but 0-2 s
  `SimulateModel` returned `data=false` with error 6140 redundant Real
  equations. `GetVarTimes` returned 0 samples and alias probes returned no
  values.
- First new boundary is direct plant sensor position reconnect into
  `navigationDisplay.actual_position`. Recommended next validation is an Iso23
  RealExpression or sampled/held bridge for that display actual-position path.
- This is not closed-loop, Factory trace consumption, controller performance,
  plant tracking, or parameter identification evidence. No full Factory wrapper
  retry was attempted and no official baseline was edited.
- Blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/sensor_bus_reconnect_20260606_015/`.

## 2026-06-06 CST - ROS2 018 Real Planner Input Gate Blocked

- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-INPUT-GATE-20260606-018`
  returned blocked after a bounded WSL ROS2 live-graph probe.
- Current live topics are only `/client_count`, `/connected_clients`,
  `/parameter_events`, and `/rosout`; visible nodes are rosbridge/rosapi
  surfaces.
- Required real planner inputs are absent now: `/Odometry` is unknown and
  `/cloud_registered` is unknown, so no type/rate evidence can be recorded for
  the needed odom/cloud pair.
- The isolated `ego_planner` launch/config/executable surface exists, but
  `runtime_disabled=false` would initialize `EGOReplanFSM`, create timers,
  subscribe to `/odom_world`, and create `/planning/bspline` publishers. It is
  not safe to attempt until real local sensed `/Odometry` plus
  `/cloud_registered` are restored and measured.
- No PositionCommand recorder ran, no `/position_cmd` or
  `/mosim/planner/position_cmd` was published, no `/planning/bspline` evidence
  is claimed, and P0 remains `smoke_only` with `planner_ready=false` and
  `closed_loop_ready=false`.
- Blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-INPUT-GATE-20260606-018.json`.
  Probe artifacts:
  `Results/ros2_runtime/b1_real_planner_input_gate_20260606_018/`.

## 2026-06-06 CST - PMO Dispatched ROS2 018 And MWORKS 015

- PMO dispatched two next-gate tasks after ROS2 017:
  - ROS2 Runtime task
    `RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-INPUT-GATE-20260606-018`
    to thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`.
  - MWORKS-Control task
    `RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015`
    to thread `019e9999-b0d3-7682-bccd-faef08fcf1df`.
- Task packets are:
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-INPUT-GATE-20260606-018.json`
  and
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015.json`.
- 018 may only check real planner runtime input readiness from current ROS2
  topics such as `/Odometry` and `/cloud_registered`; it must not run the
  PositionCommand recorder or claim `/planning/bspline`, planner, or
  closed-loop evidence.
- 015 may only continue from the passing Iso21 rate-alias baseline with one
  minimal sensor-bus/component reconnect probe; it must not retry the full
  Factory wrapper first, edit official baseline, change parameters, or claim
  Factory trace consumption/controller performance.
- P0 remains `quality_status=smoke_only`, `planner_ready=false`, and
  `closed_loop_ready=false` until both real planner runtime and MWORKS
  same-trace consumption pass their own gates.

## 2026-06-06 CST - ROS2 017 Runtime-Disabled Smoke Integrated

- PMO directly ran the bounded B1 runtime-disabled smoke for the guarded
  `ego_planner runtime_disabled_preflight.launch.py` artifact from 016.
- Evidence:
  `Results/ros2_runtime/b1_runtime_disabled_smoke_20260606_017/`.
  Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-SMOKE-20260606-017.json`.
- The launch exited with code 0 and logged
  `runtime_disabled=true; skipping EGOReplanFSM init and exiting without creating planner publishers/timers.`
  Topic lists before and after contained only `/client_count`,
  `/connected_clients`, `/parameter_events`, and `/rosout`.
- No planner runtime was accepted, no recorder was run, no `/position_cmd` or
  `/planning/bspline` evidence was produced, and no closed-loop claim is made.
- Regenerated `RUN_MANIFEST.json`, `P0_BUNDLE_AUDIT.json`,
  `P0_CLOSED_LOOP_GAP_MATRIX.json`, and sparse status packet. P0 remains
  `quality_status=smoke_only`; `planner_ready=false`; `closed_loop_ready=false`.
- Next gate is a separate real planner runtime input gate only after real local
  sensed `/Odometry` plus `/cloud_registered` are present. Recorder,
  PositionCommand evidence, and MWORKS same-trace consumption remain blocked.
- WeChat still must not be retried until the user sends one normal text message
  in `MoSim｜微信通知网关`; prior outbound send reached Weixin and returned
  `ret=-2`.

## 2026-06-06 CST - PMO Integrated MWORKS 014

- PMO consumed
  `RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014`
  into the P0 manifest/audit/gap/status flow after its return packet landed.
- 014 is `quality_status=rate_feedback_isolation_probe_passed`, but it is only
  rate-alias/result-context evidence. The current AWFF controller has no
  external `roll_rate/pitch_rate/yaw_rate` inports, so this is not an external
  gyro/rate-feedback controller claim and not controller performance evidence.
- Regenerated `RUN_MANIFEST.json`, `P0_BUNDLE_AUDIT.json`,
  `P0_CLOSED_LOOP_GAP_MATRIX.json`, and sparse status packet. P0 remains
  `quality_status=smoke_only`; `planner_ready=false`; `closed_loop_ready=false`.
- Current next packet to consume is only ROS2 016 runtime-disabled
  launch/config return or blocker:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-CONFIG-20260606-016.json`.
- WeChat still must not be retried until the user sends one normal text message
  in `MoSim｜微信通知网关`.

## 2026-06-06 CST - Rate Feedback Isolation Probe Passed

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014`
  completed as a rate alias/result-context isolation probe only.
- Added `FactoryTraceIso21ControllerRateAliasSmoke` under
  `Models/QuadrotorExperiments/`; it extends the passing Iso20 baseline and
  exposes project-owned attitude-derived rate aliases plus controller internal
  `roll_rate/pitch_rate/yaw_rate` and acceleration probes.
- The current AWFF controller surface has no external
  `roll_rate/pitch_rate/yaw_rate` inports, so this did not wire a true
  external gyro/rate signal.
- Iso21 passed `check_model`, simulated 0-2 s through Sysplorer MCP with
  `data=true`, returned `GetVarTimes=1001`, preserved nonzero reference
  aliases, and exposed nonzero rate aliases. 6140 remained absent.
- This is not closed-loop, Factory trace consumption, external rate-feedback
  controller evidence, controller performance, plant tracking, or parameter
  identification evidence.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/rate_feedback_isolation_20260606_014/`.

## 2026-06-06 CST - ROS2 016 Runtime-Disabled Launch Config Completed

- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-CONFIG-20260606-016`
  completed as a guarded runtime-disabled launch/config artifact only.
- Added isolated `runtime_disabled_preflight.launch.py` and
  `runtime_disabled_preflight.yaml` under the actual isolated
  `plan_manage` package, whose CMake project installs as `ego_planner`.
- Added a `runtime_disabled` guard to `ego_planner_node_preflight`; when true,
  it exits before initializing `EGOReplanFSM`, so planner publishers, timers,
  and subscriptions are not created.
- Static validation passed: launch `py_compile`, YAML text gate, guard/remap
  scans, and bounded colcon build/install. Installed artifacts are listed in
  `Results/ros2_runtime/b1_runtime_disabled_launch_config_20260606_016/artifact_inventory_final.json`.
- No planner runtime was launched, no recorder was run, no `/position_cmd` was
  published, and no `/planning/bspline` runtime evidence or closed-loop claim
  is made.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-CONFIG-20260606-016.json`.
  Config artifacts:
  `Results/ros2_runtime/b1_runtime_disabled_launch_config_20260606_016/`.
- WeChat remains gated by the prior `weixin: sendMessage: ret=-2` result. Do
  not retry until the user sends one normal text message in
  `MoSim｜微信通知网关`.

## 2026-06-06 CST - Yaw Attitude Decoupling Probe Passed

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-YAW-RATE-DECOUPLING-20260606-013`
  completed as a yaw attitude decoupling/result-context probe only.
- Added `FactoryTraceIso20RollPitchYawEstimatorSmoke` under
  `Models/QuadrotorExperiments/`; it keeps Iso19 roll+pitch extraction and
  adds only yaw `sensors1_1.AngleMea[3]` through a project-owned first-order
  `yaw_est_state` before `controller3_2.yaw_mea`.
- Iso20 passed `check_model`, simulated 0-2 s through Sysplorer MCP with
  `data=true`, returned `GetVarTimes=1001`, preserved nonzero
  `x_ref/y_ref/z_ref/yaw_ref` aliases, and exposed yaw estimator/controller
  input aliases. 6140 remained absent.
- Rate fallback was not run because yaw attitude extraction passed first.
  Unknowns remain rate feedback, full sensor bus, full Factory wrapper,
  yaw wrapping/frame semantics, and long-horizon behavior.
- This is not closed-loop, Factory trace consumption, controller performance,
  plant tracking, or parameter identification evidence.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-YAW-RATE-DECOUPLING-20260606-013.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/yaw_rate_decoupling_20260606_013/`.

## 2026-06-06 CST - ROS2 015 Runtime-Disabled Launch Audit Completed

- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-AUDIT-20260606-015`
  completed as a static launch/parameter/remap audit only.
- No planner runtime was launched, no recorder was run, no `/position_cmd` was
  published, and no `/planning/bspline` runtime evidence is claimed.
- The audit confirms 014 exposed buildable `ego_planner_node_preflight`,
  `EGOReplanFSM`, and `EGOPlannerManager` surfaces, but there is still no
  direct ROS2 `.launch.py`; the legacy EGO launch XML uses ROS1 slash-style
  parameter names and must be translated to ROS2 dotted parameter names.
- Reserved real input contract remains `/odom_world:=/Odometry`,
  `/grid_map/odom:=/Odometry`, and `/grid_map/cloud:=/cloud_registered`.
  This is a local sensed input contract only; no fake map/cloud or UE global
  truth planner input is allowed.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-AUDIT-20260606-015.json`.
  Audit artifacts:
  `Results/ros2_runtime/b1_runtime_disabled_launch_audit_20260606_015/`.

## 2026-06-06 CST - WeChat Gateway Maintenance Gap Fixed

- User reported WeChat was broken again. Diagnosis showed two separate
  failures. First, the 07:21 scheduled canary reached Weixin but failed with
  `weixin: sendMessage: ret=-2 errcode=0`; this is a Weixin/iLink outbound
  context problem and should not trigger a cc-connect runtime restart. Second,
  the adapter then restarted cc-connect for `ret=-2`, hit a stale instance lock,
  and left `api.sock` present but not connectable.
- Windows Task Scheduler evidence at 09:01 CST:
  `MoSim Weixin Gateway Local Health` last ran at 08:51 with
  `LastTaskResult=2`; `MoSim Weixin Gateway Canary` last ran at 07:21 with
  `LastTaskResult=0` even though the canary send failed and wrote recovery
  packets. This exposed the maintenance gap: local health detected failure but
  did not self-recover the cc-connect API socket.
- Fixed `CoAgent/gateway/cc_connect_weixin.py` so only
  `internal_api_unavailable` and `timeout` trigger a bounded cc-connect
  restart/retry. `weixin_ret_minus_2`, `missing_context_token`, and
  `no_active_session` no longer restart the runtime; they require the documented
  WeChat context/session recovery path instead.
- Fixed `Scripts/agent/check_weixin_gateway_health.py` so local `api_socket`
  failure performs one bounded local recovery: clear stale lock/socket when no
  live process owns the lock, start cc-connect with
  `config-wsl-runtime.toml`, and wait for a real Unix socket connect. The same
  Task Scheduler local-health command can now restore stale API socket state
  without relying on an open Codex conversation.
- Validation after repair:
  `python Scripts\agent\check_weixin_gateway_health.py` wrote
  `Results/coagent_gateway/health/weixin_gateway_health_20260606_090820.json`
  with local `ok=true`; `python -m py_compile
  Scripts\agent\check_weixin_gateway_health.py CoAgent\gateway\cc_connect_weixin.py`
  passed; WSL shows cc-connect PID `51293` listening on
  `/home/linux/.cache/mosim/coagent/cc-connect-weixin/data/run/api.sock`.
- A single explicit canary at 09:07 still failed at Weixin with `ret=-2`:
  `Results/coagent_gateway/health/weixin_gateway_health_20260606_090718.json`.
  Minimal user action is to send one ordinary text message in the
  `MoSim｜微信通知网关` WeChat chat, then retry one canary. Do not restart
  cc-connect or loop sends for `ret=-2`.
- After the user sent one ordinary WeChat message, exactly one retry canary
  passed at 09:37 CST:
  `Results/coagent_gateway/health/weixin_gateway_health_20260606_093706.json`.
  The adapter returned `Message sent successfully.` This confirms the shared
  outbound WeChat notification path was restored after the Weixin/iLink context
  refresh.
- Follow-up hardening for offline operators: `Scripts/agent/check_weixin_gateway_health.py`
  now writes a separate end-to-end canary status file
  `Results/coagent_gateway/health/gateway_outbound_latest.json`, and writes
  `gateway_outbound_unhealthy_latest.json` when a real canary fails. Local
  health snapshots no longer erase the last outbound-canary state. When
  `--send-canary` fails, the script exits nonzero so the
  `MoSim Weixin Gateway Canary` scheduled task can surface the failure via
  `LastTaskResult` while keeping the routine frequency at 4 hours.
- Validation:
  `python Scripts\agent\check_weixin_gateway_health.py --send-canary --timeout 30`
  wrote `Results/coagent_gateway/health/weixin_gateway_health_20260606_093932.json`
  and `gateway_outbound_latest.json` with `status=healthy` and
  `Message sent successfully.` Local health remained healthy with cc-connect
  PID `51293` listening on `api.sock`.
- Added QQ email fallback scaffolding. SMTP network probes to `smtp.qq.com`
  passed on ports `465` and `587`; Python `smtplib` EHLO/STARTTLS smoke also
  passed. New script:
  `Scripts/agent/send_gateway_email_alert.py`. It sends sparse gateway alerts
  to `1062771286@qq.com` by default and reads SMTP credentials only from
  environment variables, never from project files or chat:
  `MOSIM_ALERT_EMAIL_FROM`, `MOSIM_ALERT_EMAIL_PASSWORD`, optional
  `MOSIM_ALERT_EMAIL_TO`, `MOSIM_ALERT_SMTP_HOST`, and
  `MOSIM_ALERT_SMTP_PORT`.
- `Scripts/agent/check_weixin_gateway_health.py` now attempts this email
  fallback on local or outbound gateway failure. Without SMTP credentials it
  records `missing_config` under `Results/coagent_gateway/email/` instead of
  failing silently. Validation:
  `python Scripts\agent\send_gateway_email_alert.py --status-json
  Results\coagent_gateway\health\gateway_outbound_latest.json --cooldown-minutes 0`
  wrote `Results/coagent_gateway/email/email_alert_20260606_094620.json` with
  missing `MOSIM_ALERT_EMAIL_FROM` and `MOSIM_ALERT_EMAIL_PASSWORD`;
  `python -m py_compile Scripts\agent\check_weixin_gateway_health.py
  Scripts\agent\send_gateway_email_alert.py CoAgent\gateway\cc_connect_weixin.py`
  passed. Real email send remains blocked until the user configures a QQ SMTP
  authorization code locally.

## 2026-06-06 CST - PMO Integrated MWORKS 012 And ROS2 014

- PMO consumed MWORKS 012 pitch-decoupling return and ROS2 014
  plan_manage link-preflight return into the P0 manifest/audit/gap/status
  flow.
- P0 remains `quality_status=smoke_only`; 012 is only a roll+pitch
  result-context probe and 014 is only compile/link preflight. Neither is
  planner runtime, `/position_cmd`, `/planning/bspline` runtime evidence,
  Factory trace consumption, controller performance, or closed-loop evidence.
- Dispatched next bounded department tasks:
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-CONTROL-YAW-RATE-DECOUPLING-20260606-013.json`
  and
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-AUDIT-20260606-015.json`.
- Current next packets to consume are MWORKS 013 yaw/rate decoupling and ROS2
  015 runtime-disabled launch/static audit. No WeChat retry was attempted.
- WeChat adapter send attempt for
  `Results/coagent_gateway/packets/rfly_mosim_p0_sparse_status_20260606.json`
  was rejected before transport with `unsupported packet type`; no direct
  `cc-connect send` fallback was used.
- Follow-up repair changed the sparse status packet to the whitelisted
  `blocker_notification/manual_review_required` shape. Dry-run passed. A first
  live attempt with the wrong project argument failed as `project "MoSim" not
  found`; retrying with the adapter default project reached Weixin and returned
  `weixin: sendMessage: ret=-2`. Per gateway rule, do not retry again until the
  user sends one normal text message in the `MoSim｜微信通知网关` WeChat chat.

## 2026-06-06 CST - Pitch Decoupling Probe Passed

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-PITCH-DECOUPLING-20260606-012`
  completed as a pitch decoupling/result-context probe only.
- Added `FactoryTraceIso19RollPitchEstimatorSmoke` under
  `Models/QuadrotorExperiments/`; it keeps Iso18 roll extraction and adds only
  pitch `sensors1_1.AngleMea[2]` through a project-owned first-order
  `pitch_est_state` before `controller3_2.pitch_mea`.
- Iso19 passed `check_model`, simulated 0-2 s through Sysplorer MCP with
  `data=true`, returned `GetVarTimes=1001`, preserved nonzero
  `x_ref/y_ref/z_ref/yaw_ref` aliases, and exposed roll/pitch estimator and
  controller input aliases. 6140 remained absent.
- This confirms the Iso18 project-owned extraction pattern scales from
  roll-only to roll+pitch result-context stability. It is not closed-loop,
  Factory trace consumption, controller performance, plant tracking, or
  parameter identification evidence.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-PITCH-DECOUPLING-20260606-012.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/pitch_decoupling_20260606_012/`.

## 2026-06-06 CST - PMO Integrated MWORKS 011 And Dispatched 012

- PMO consumed
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json`
  into the P0 manifest/audit/gap-matrix flow.
- Current P0 state remains `quality_status=smoke_only`; 011 is a
  result-context decoupling probe, not Factory trace consumption or
  closed-loop evidence.
- Dispatched next MWORKS-Control task packet:
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-CONTROL-PITCH-DECOUPLING-20260606-012.json`.
  Objective: add only pitch extraction using the Iso18 project-owned
  first-order extraction pattern before any full Factory retry.

## 2026-06-06 CST - Attitude Decoupling Probe Restored Result Context

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011`
  completed as an attitude dependency decoupling probe only.
- Added `FactoryTraceIso17SampleHoldAngleSmoke` and
  `FactoryTraceIso18ProjectAttitudeEstimatorSmoke` under
  `Models/QuadrotorExperiments/`.
- Iso17 sampled/held `sensors1_1.AngleMea[1]` before
  `controller3_2.roll_mea`; Iso18 used a project-owned first-order
  `roll_est_state` extraction before `roll_mea`.
- Both probes passed `check_model`, simulated 0-2 s through Sysplorer MCP with
  `data=true`, returned `GetVarTimes=1001`, preserved nonzero
  `x_ref/y_ref/z_ref/yaw_ref` aliases, and kept 6140 absent.
- This confirms the `AbsoluteAngles/AngleMea` dependency path can be decoupled
  to restore result context. It is not a closed-loop, Factory trace
  consumption, controller performance, plant tracking, or parameter
  identification claim.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/attitude_decoupling_20260606_011/`.

## 2026-06-06 CST - Sparse PMO Status Packet Added

- Added `Scripts/quality/build_p0_sparse_status_packet.py` and
  `Scripts/tests/test_p0_sparse_status_packet.py`.
- Generated
  `Results/coagent_gateway/packets/rfly_mosim_p0_sparse_status_20260606.json`.
- The packet records the current P0 state as waiting for MWORKS 011 and ROS2
  014 department returns, with `closed_loop_ready=false`,
  `planner_ready=false`, and no WeChat send attempt.
- WeChat retry remains gated by a normal user message if outbound send later
  reaches `weixin: sendMessage: ret=-2`; do not retry in a loop.

## 2026-06-06 CST - P0 Closed Loop Gap Matrix Added

- Added `Scripts/quality/summarize_p0_closed_loop_gap_matrix.py` and
  `Scripts/tests/test_p0_closed_loop_gap_matrix.py`.
- Generated
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_CLOSED_LOOP_GAP_MATRIX.json`
  from the current `RUN_MANIFEST.json` and `P0_BUNDLE_AUDIT.json`.
- The gap matrix explicitly records `closed_loop_ready=false`,
  `planner_ready=false`, `quality_status=smoke_only`, active blocking gates for
  MWORKS same-trace consumption, MWORKS attitude decoupling, ROS2 real planner
  runtime, ROS2 planner dependency surfaces, and UE runtime command ack.
- Next packets to consume are MWORKS 011 attitude decoupling and ROS2 014
  plan_manage link preflight. This is an anti-overclaim artifact, not a new
  simulation run.

## 2026-06-06 CST - PMO Integrated ROS2 013 Into P0 Bundle

- PMO consumed
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-TRAJ-QUADMSGS-PORT-20260606-013.json`
  into `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`
  and `P0_BUNDLE_AUDIT.json`.
- 013 is `build_surface_only`: isolated `quadrotor_msgs` and `traj_utils`
  now build/install in the ROS2 Humble preflight workspace, but no planner
  runtime, `/planning/bspline`, `/position_cmd`, runtime recorder, fake map, or
  UE truth shortcut is claimed.
- Current P0 bundle still passes audit with `quality_status=smoke_only` and no
  `planner` / `closed_loop` claim.
- Dispatched next ROS2 Runtime task packet:
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-PLANMANAGE-LINK-PREFLIGHT-20260606-014.json`.
  Objective: full `plan_manage` / `EGOPlannerManager` / `EGOReplanFSM` link
  preflight only, still no runtime planner or recorder.

## 2026-06-06 CST - PMO Integrated MWORKS 010 Into P0 Bundle

- PMO consumed
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010.json`
  into `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`
  and `P0_BUNDLE_AUDIT.json`.
- The P0 bundle audit now checks the 010 return packet and artifacts:
  constant/table attitude inputs pass, while `AngleMea`-dependent
  `RealExpression` reproduces the empty result context.
- Current bundle status remains `quality_status=smoke_only`; `planner` and
  `closed_loop` remain excluded from `claim_scope`.
- Dispatched next MWORKS-Control task packet:
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json`.
  Objective: test sampled/held or project-owned attitude extraction decoupling
  before any full Factory retry.

## 2026-06-06 CST - Attitude Intermediary Classified AbsoluteAngles Coupling

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010`
  completed as an intermediary-signal diagnostic only, not as Factory
  closed-loop, controller performance, or trace-consumption evidence.
- Added `FactoryTraceIso14ConstantAttitudeInputSmoke`,
  `FactoryTraceIso15TableAttitudeInputSmoke`, and
  `FactoryTraceIso16RealExpressionAngleSmoke` under
  `Models/QuadrotorExperiments/`.
- Iso14 constant roll attitude input and Iso15 inline table roll attitude input
  both passed `check_model`, simulated 0-2 s with `data=true`, returned
  `GetVarTimes=1001`, and preserved nonzero `x_ref/y_ref/z_ref/yaw_ref`
  aliases.
- Iso16 `RealExpression(y=sensors1_1.AngleMea[1]) -> roll_mea` passed
  `check_model` but reproduced `SimulateModel data=false`, `GetVarTimes=[]`,
  and empty alias values. `6140` stayed absent in all three probes.
- Classification: the current blocker follows the
  `AbsoluteAngles/AngleMea` dependency path into controller attitude feedback;
  it is not supported as generic controller inport sensitivity and not just
  direct-connector syntax. Next bounded step is sampled/held decoupling or a
  project-owned attitude extraction wrapper before any full Factory retry.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/attitude_intermediary_20260606_010/`.

## 2026-06-06 CST - Attitude Feedback Isolation Found Single-Channel Boundary

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009`
  completed as an attitude-feedback isolation diagnostic only, not as Factory
  closed-loop, controller performance, or trace-consumption evidence.
- Added four project-owned probe models under `Models/QuadrotorExperiments/`:
  `FactoryTraceIso10RollFeedbackSmoke`,
  `FactoryTraceIso11PitchFeedbackSmoke`,
  `FactoryTraceIso12RollFeedbackNegatedSmoke`, and
  `FactoryTraceIso13PitchFeedbackNegatedSmoke`.
- All four probes passed `check_model`, but 0-2 s `SimulateModel` returned
  `data=false`; explicit result reads returned `GetVarTimes=[]` and no
  nonzero `x_ref/y_ref/z_ref/yaw_ref` aliases. `6140` stayed absent.
- Direct roll-only and pitch-only feedback each reproduce the empty result
  context. Negating the single angle channel did not restore result binding, so
  a simple sign inversion is not sufficient.
- Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009.json`.
  Probe artifacts:
  `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/`.

## 2026-06-06 CST - UE Command Sender Source Contract Added, P0 Still Smoke-Only

- Added a narrow UE Bridge command uplink component:
  `UQuadrotorMworksUdpCommandSenderComponent` in
  `UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpCommandSenderComponent.h`
  and
  `UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpCommandSenderComponent.cpp`.
- The component builds `mosim.ue_command.v1` packets for controller/planner,
  wind, motor fault, sensor mode, scenario reset, start/goal, recording, and
  scene switching, with MWORKS/ROS2 acknowledgement guards. It does not expose
  pose overwrite APIs.
- Added `Scripts/UE5/check_ue_command_sender_contract.py` and
  `Scripts/tests/test_ue_command_sender_contract.py`. The source-level check
  requires the sender to reject `pose_override`, `teleport`, `set_uav_pose`,
  `actor_transform`, and `keyboard_pose`, and to avoid direct Actor pose APIs.
- Regenerated
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` and
  `P0_BUNDLE_AUDIT.json`. The bundle now records the source-level UE sender
  contract but remains `quality_status=smoke_only`,
  `claim_scope=["fast_lio","ue_visual"]`, and `not_runtime_ue_console=true`.
- Added `Scripts/UE5/smoke_ue_command_sender_loopback.py` and integrated its
  result into the P0 bundle. It sends four `mosim.ue_command.v1` packets over
  local UDP loopback, receives all four, and preserves
  `no_pose_overwrite_status=pass`. This only proves packet/transport shape; it
  is not a runtime UE console, MWORKS ack, or ROS2 ack.
- Boundary: this is not a live UE Experiment Console, not runtime MWORKS/ROS2
  command acknowledgement, and not planner or closed-loop evidence. Runtime
  acceptance still requires `mosim.ue_command_echo.v1` rows from the MWORKS/ROS2
  authority path.
- WeChat notification remains degraded at the Weixin send layer after `ret=-2`;
  do not retry until the user sends one normal message in the gateway chat, then
  retry once through `CoAgent/gateway/cc_connect_weixin.py`.

## 2026-06-06 CST - ROS2 012 Path/BSpline Build Surfaces Integrated

- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PATH-BSPLINE-PORT-20260606-012` returned
  `completed_preflight` / `quality_status=build_surface_only`.
- The isolated `path_searching` and `bspline_opt` packages in
  `Results/tmp/ego_planner_ros2_port_ws/` are now ROS2 `ament_cmake`
  build/API surfaces. Installed artifacts include
  `install/path_searching/lib/libpath_searching.a` and
  `install/bspline_opt/lib/libbspline_opt.a`.
- PMO integrated 012 into
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` and
  `P0_BUNDLE_AUDIT.json`. P0 remains `smoke_only`; no planner runtime,
  `/planning/bspline`, `/position_cmd`, runtime recorder, fake map/cloud, UE
  truth shortcut, FAST-LIO `/path` trajectory conversion, keyboard pose, or
  replacement planner was used.
- Remaining ROS2 B1 blocker moved to `traj_utils`, `quadrotor_msgs`, and full
  `plan_manage/EGOPlannerManager/EGOReplanFSM` linkage/runtime reachability.

## 2026-06-06 CST - MWORKS 009 AngleMea Single-Channel Boundary Integrated

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009`
  returned `completed` /
  `quality_status=attitude_feedback_sub_boundary_found`.
- Starting from the passing Iso08 position-feedback wrapper, direct roll-only
  `AngleMea[1] -> roll_mea`, direct pitch-only `AngleMea[2] -> pitch_mea`,
  negated roll-only, and negated pitch-only probes all passed `check_model` but
  failed 0-2 s `SimulateModel` with `data=false`, `GetVarTimes=0`, and zero
  aliases. Compiler error 6140 stayed absent.
- The current boundary is not actuator wiring and not a simple sign issue:
  direct single-channel `AbsoluteAngles` / `AngleMea` coupling into Sysblock
  controller inports is sufficient to trigger the empty result context.
- PMO integrated 009 into the P0 manifest/audit. Next MWORKS slice should test
  constant/time-table/sampled-held or RealExpression intermediary attitude
  signals before reconnecting plant sensor angles or retrying the full Factory
  wrapper.

## 2026-06-06 CST - Sensor Feedback Isolation Found Roll/Pitch Boundary

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-SENSOR-FEEDBACK-ISOLATION-20260606-008`
  completed as a sensor-feedback isolation diagnostic only, not as Factory
  closed-loop or controller trace-consumption evidence.
- Added `FactoryTraceIso08PositionFeedbackSmoke` and
  `FactoryTraceIso09PositionAttitudeFeedbackSmoke` under
  `Models/QuadrotorExperiments/`.
- Iso08 position feedback only passed: `check_model` passed,
  `SimulateModel data=true`, `GetVarTimes=1001`, and
  `x_ref@1s=0.31861753694312633` with nonzero aliases.
- Iso09 is the first sensor-feedback failure boundary. After adding roll/pitch
  attitude feedback from `sensors1_1.AngleMea[1..2]` while keeping yaw open,
  `check_model` still passed but `SimulateModel data=false`, `GetVarTimes=0`,
  and aliases were zero. Compiler error 6140 remained absent.
- Next repair/isolation should test roll-only versus pitch-only feedback and
  compare `AngleMea` frame/sign/range against controller input expectations
  before retrying any full Factory wrapper.
- PMO dispatched the follow-up task
  `RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009` to
  thread `019e9999-b0d3-7682-bccd-faef08fcf1df` for roll-only, pitch-only, and
  `AngleMea` frame/sign/range isolation. It remains forbidden to change
  parameters/gains or claim closed loop.
- Artifacts:
  `Results/mworks_trace_consumption/sensor_feedback_isolation_20260606_008/sensor_feedback_isolation_probe.json`,
  `Results/mworks_trace_consumption/sensor_feedback_isolation_20260606_008/sensor_feedback_isolation_summary.csv`,
  and return packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-FEEDBACK-ISOLATION-20260606-008.json`.

## 2026-06-06 CST - P0 Bundle Integrates 007, Adds UE Command Schemas, Dispatches 008

- PMO integrated MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007`
  into the P0 smoke-only bundle. The manifest now records that Iso04's
  compiler error 6140 was caused by duplicate actuator input sources, while
  clean sensor-feedback closure remains blocked.
- Added documented UE Experiment Console packet schemas:
  `Config/schemas/mosim_ue_command_v1.schema.json` and
  `Config/schemas/mosim_ue_command_echo_v1.schema.json`. These document the
  current `controller_select` / `planner_select` / fault / wind / sensor /
  scene-switch command boundary and explicitly forbid `teleport`,
  `pose_override`, `set_uav_pose`, `actor_transform`, and `keyboard_pose`.
- `check_p0_run_bundle.py` now checks the 007 return packet and artifacts and
  requires the UE command/echo schema docs to exist. The bundle still remains
  `quality_status=smoke_only`; `claim_scope` still excludes `planner` and
  `closed_loop`.
- PMO dispatched the next MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-SENSOR-FEEDBACK-ISOLATION-20260606-008` to thread
  `019e9999-b0d3-7682-bccd-faef08fcf1df`. It must start from Iso07 and add
  position/velocity feedback, attitude/rate feedback, yaw feedback, and
  remaining sensor bus coupling one group at a time. Full Factory wrapper
  retry and closed-loop claims remain forbidden.
- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PLANENV-GRIDMAP-PORT-20260606-011` returned
  `completed_preflight` / `quality_status=build_surface_only`. The isolated
  `plan_env` package is now ROS2 `ament_cmake` buildable and installs
  `libplan_env.a`, headers, and package metadata. This is not planner runtime:
  no `/planning/bspline`, `/position_cmd`, runtime recorder, fake map/cloud, UE
  global truth, FAST-LIO `/path` shortcut, or keyboard pose was used.
- PMO integrated 011 into the P0 manifest/audit and dispatched the next ROS2
  Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PATH-BSPLINE-PORT-20260606-012` to thread
  `019e9917-6181-7ec2-b3d6-4b624d6d3348`. The next slice is isolated
  `path_searching` and `bspline_opt` build/API surface only; planner runtime
  and B1 recorder remain forbidden.
- WeChat ops returned that the local cc-connect API socket health check was
  repaired to use a real Unix socket connect. If a future outbound notification
  reaches Weixin and returns `ret=-2`, the next valid action remains: user sends
  one normal message in the WeChat gateway chat, then PMO retries once. PMO
  notification packets include self/origin thread id
  `019e9868-83ea-70f0-92c5-a3a408bd78c6`.

## 2026-06-06 CST - Actuator Wiring Isolation Refined 6140 Boundary

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007`
  completed as an actuator/topology isolation diagnostic only, not as Factory
  closed-loop or controller trace-consumption evidence.
- Compared the 006 Iso04 failure model against the known project-owned
  `Example1LinearMPCSysblockClosedLoop` actuator input pattern. The passing
  pattern has `hover_u*.y -> motor*_hover_sum.u2` and only
  `motor*_hover_sum.y -> actuator*.u`; Iso04 inherited direct
  `hover_u*.y -> actuator*.u` and also added `motor*_hover_sum.y ->
  actuator*.u`.
- Added derivative probes
  `FactoryTraceIso05CleanHoverSumSmoke`,
  `FactoryTraceIso06CleanControllerPlantWiringSmoke`, and
  `FactoryTraceIso07CleanControllerOpenFeedbackSmoke`.
- Iso05 clean hover-sum topology passed and removed compiler error 6140.
  Iso07 clean controller-to-actuator motor-sum topology also passed when
  controller feedback was trace-derived/open. Therefore Iso04's 6140 was caused
  by duplicate actuator input sources, not by the motor-sum topology itself.
- Remaining boundary: Iso06 with clean actuator input topology but sensor
  feedback closed into the controller still returned `SimulateModel data=false`,
  `GetVarTimes=0`, and zero aliases, without 6140 text. Next step is
  sensor-feedback isolation from Iso07.
- Artifacts:
  `Results/mworks_trace_consumption/actuator_wiring_isolation_20260606_007/actuator_wiring_isolation_probe.json`,
  `Results/mworks_trace_consumption/actuator_wiring_isolation_20260606_007/actuator_wiring_isolation_summary.csv`,
  and return packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007.json`.

## 2026-06-06 CST - P0 Audit Integrates 006 And UE Echo Gate

- PMO advanced the UE Experiment Console path from placeholder-only to an
  executable offline command adapter smoke. Added
  `Scripts/UE5/smoke_ue_command_adapter.py` and
  `Scripts/tests/test_ue_command_adapter_smoke.py`.
- `build_p0_slice_run_manifest.py` now writes
  `ue_command_input_smoke.jsonl`, runs the adapter smoke, and records
  `ue_command_echo_smoke.jsonl` plus `ue_command_adapter_smoke.json` in the P0
  manifest. The smoke accepts `controller_select` and `planner_select`, rejects
  `teleport`, preserves `no_pose_overwrite_status=pass`, and is explicitly
  marked `source=offline_adapter_smoke` / `not_runtime_ue_console=true`.
- The UE echo checker now accepts a forbidden pose command only when it is
  explicitly rejected by the adapter with a pose-forbidden reason; accepted
  pose override/teleport evidence still fails the gate.
- Boundary: this is still not a live UE command sender and not a MWORKS/ROS2
  runtime acknowledgement. `P0_BUNDLE_AUDIT.json` warns:
  `UE command adapter smoke has accepted/rejected echo rows, but it is offline-only and not runtime UE console evidence`.
- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-UPSTREAM-PLANNER-DEPS-20260606-010` returned
  `blocked_after_classification`. It identified the preferred upstream
  `/planning/bspline` producer as EGO `plan_manage/EGOReplanFSM`, but real
  runtime remains blocked because `plan_env` / GridMap and related
  `path_searching`, `bspline_opt`, and `traj_utils` surfaces are still
  ROS1/catkin-only in the isolated ROS2 workspace.
- PMO integrated 010 into `RUN_MANIFEST.json` and `P0_BUNDLE_AUDIT.json`. The
  audit now checks the 010 blocker packet and logs for producer scan,
  dependency scan, `colcon list`, and the failed expected `plan_env` build
  probe. It also confirms no `/position_cmd`, recorder, fake map/cloud, UE
  global truth, keyboard pose, or new hand-written planner was used.
- PMO dispatched the next ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PLANENV-GRIDMAP-PORT-20260606-011` to thread
  `019e9917-6181-7ec2-b3d6-4b624d6d3348`. It must port/preflight only the
  isolated `plan_env` GridMap build/API surface for the intended
  `/grid_map/odom:=/Odometry` and `/grid_map/cloud:=/cloud_registered` route.
- PMO integrated MWORKS-Control 006 into
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` and
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json`.
  The bundle remains `quality_status=smoke_only`; `claim_scope` still excludes
  `planner` and `closed_loop`.
- Added `Scripts/UE5/check_ue_command_echo_contract.py` and tests in
  `Scripts/tests/test_ue_command_echo_contract.py`. The checker allows the
  current UE command echo placeholder only as smoke evidence, requires runtime
  echo rows to be acknowledged by `MWORKS`, `ROS2`, or `MWORKS_ROS2`, and
  rejects `teleport`, `pose_override`, `set_uav_pose`, `actor_transform`, and
  `keyboard_pose` command kinds.
- `Scripts/quality/check_p0_run_bundle.py` now runs the UE echo checker and
  warns when the current log is placeholder-only. This prevents
  `ue_command_echo_placeholder.jsonl` from being promoted to a runtime UE
  Experiment Console command/ack implementation.
- PMO dispatched the next MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007` to thread
  `019e9999-b0d3-7682-bccd-faef08fcf1df`. It must continue from Iso04 and
  isolate controller-to-actuator wiring/topology without touching official
  baseline parameters or claiming closed loop.
- Focused checks passed:
  `python Scripts\quality\build_p0_slice_run_manifest.py --validate`;
  `python Scripts\quality\check_p0_run_bundle.py`;
  `python -m pytest Scripts\tests\test_ue_command_adapter_smoke.py Scripts\tests\test_ue_command_echo_contract.py Scripts\tests\test_p0_run_bundle_audit.py Scripts\tests\test_p0_slice_run_manifest.py Scripts\tests\test_run_manifest_gate.py -q`.

## 2026-06-06 CST - Incremental Factory Trace Isolation Found First Failure Boundary

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006`
  completed as an incremental isolation diagnostic only, not as Factory
  closed-loop or controller trace-consumption evidence.
- Added four project-owned probes under `Models/QuadrotorExperiments/`:
  `FactoryTraceIso01FullDisplaySmoke`,
  `FactoryTraceIso02ControllerOnlySmoke`,
  `FactoryTraceIso03PlantHoverStackSmoke`, and
  `FactoryTraceIso04ControllerPlantWiringSmoke`.
- Iso01 full display, Iso02 controller-only math, and Iso03 open-loop hover
  plant/actuator/sensor stack all passed MCP `check_model`, 0-2 s simulation,
  `GetVarTimes=1001`, and nonzero aliases with `x_ref@1s=0.31861753694312633`.
- Iso04 is the first failure boundary: after adding controller feedback plus
  motor-command scaling/summing/wiring into actuator inputs, `check_model`
  passed but `SimulateModel` returned `data=false` with compiler error 6140
  redundant Real equations in the QuadChassis frame rotation system.
- This narrows but does not exactly reproduce the 004 full-wrapper empty
  result context: after Iso04 failed simulate, `GetVarTimes` and wrapper
  aliases were still readable/nonzero. Next work should isolate
  controller-to-actuator wiring/topology before retrying the full Factory
  wrapper.
- Artifacts:
  `Results/mworks_trace_consumption/incremental_trace_isolation_20260606_006/incremental_trace_isolation_probe.json`,
  `Results/mworks_trace_consumption/incremental_trace_isolation_20260606_006/incremental_trace_isolation_summary.csv`,
  and return packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006.json`.

## 2026-06-06 CST - ROS2 009 Planner-Node Stub Integrated

- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-NODE-PORT-PREFLIGHT-20260606-009`
  returned `completed_preflight` / `quality_status=build_surface_only`.
  It compiled an isolated ROS2 `plan_manage/traj_server` surface/stub in
  `Results/tmp/ego_planner_ros2_port_ws`, but did not launch planner runtime,
  did not publish `/position_cmd`, and did not run the runtime recorder.
- PMO regenerated
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` and
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json`.
  The audit now checks the 009 return packet, three build logs, and installed
  `traj_server_ros2_node` executable path, while keeping the P0 bundle
  `quality_status=smoke_only` and excluding `planner` / `closed_loop`.
- Focused checks passed:
  `python Scripts\quality\build_p0_slice_run_manifest.py --validate`;
  `python Scripts\quality\check_p0_run_bundle.py`;
  `python -m pytest Scripts\tests\test_p0_run_bundle_audit.py Scripts\tests\test_p0_slice_run_manifest.py Scripts\tests\test_run_manifest_gate.py -q`.
- Current blockers remain real: there is still no upstream EGO/Sunray/FUEL
  planner runtime producing `ego_planner_msgs/msg/Bspline` from `/Odometry`
  plus `/cloud_registered`, and no sustained real `/position_cmd` recorder
  evidence. The next ROS2 task is
  `RFLY-MOSIM-ROS2-RUNTIME-B1-UPSTREAM-PLANNER-DEPS-20260606-010`, not a
  runtime recorder attempt.
- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006` later
  returned the Iso04 first-failure boundary recorded above; P0 still lacks full
  Factory/controller trace consumption.
- WeChat ops reported the gateway root cause and local socket fix: previous
  health used session-file reads as a false-positive; the repaired health path
  now performs a real Unix socket connect to `api.sock`. If outbound reaches
  Weixin and fails with `ret=-2`, the next valid action is still one normal
  user message in the WeChat gateway chat followed by one bounded retry. PMO
  notification packets include self/origin thread id
  `019e9868-83ea-70f0-92c5-a3a408bd78c6`.

## 2026-06-06 CST - Factory-Lite Trace Result Binding Passed

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-FACTORY-LITE-TRACE-20260606-005` completed as a
  Factory-lite diagnostic only, not as Factory closed-loop or controller
  consumption evidence.
- Added `QuadrotorExperiments.FactoryLiteTraceSmoke`, containing only
  `TraceInlineReference`, `PlanningNavigationDisplay`, wrapper aliases
  `x_ref/y_ref/z_ref/yaw_ref/z_ref_rate`, and `trace_probe_state`. It excludes
  QuadChassis, actuators, sensors, and controller components.
- Sysplorer MCP package load/check passed, the 0-2 s simulation passed, and
  result binding was nonzero: `GetVarTimes` returned 41 samples and
  `x_ref@1s=0.31861753694312633`, `y_ref@1s=0.49481767718910424`,
  `z_ref@1s=1.242037957383867`, `yaw_ref@1s=1.9974016333898024`.
- Artifacts:
  `Results/mworks_trace_consumption/factory_lite_trace_20260606_005/factory_lite_trace_probe.json`,
  `Results/mworks_trace_consumption/factory_lite_trace_20260606_005/factory_lite_trace_raw.csv`,
  and return packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-LITE-TRACE-20260606-005.json`.
- This narrows the 004 blocker: `TraceInlineReference` plus
  `PlanningNavigationDisplay` does not cause the empty result context. Next
  reconnect should add full-wrapper component groups incrementally and must
  still avoid any `closed_loop`, real planner, or controller-performance claim.

## 2026-06-06 CST - ROS2 008 Message Slice Integrated

- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-MSG-PORT-SLICE-20260606-008` completed a
  message/build-surface slice in the isolated workspace only. It did not port
  planner node logic and did not publish `/position_cmd`.
- Decision: reuse project-owned `mosim_msgs/msg/PositionCommand` as the
  external B1 command surface; do not port the full ROS1 `quadrotor_msgs`
  package for the command interface now.
- Added isolated `ego_planner_msgs` under
  `Results/tmp/ego_planner_ros2_port_ws/src/ego_planner_msgs/` with
  `Bspline.msg` and `DataDisp.msg`. Focused `colcon build --packages-select
  ego_planner_msgs` passes with clock-skew warnings only, and `ros2 interface
  show` passes.
- PMO integrated 008 into
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` under
  `ros2.position_command_b1_msg_port_slice`; the run remains
  `quality_status=smoke_only` and still excludes `planner` and `closed_loop`.
- Next ROS2 step is planner/traj_server node port preflight in the same
  isolated workspace. Runtime recorder is still forbidden until a real
  local-map/planner chain publishes `/position_cmd` from `/Odometry` plus
  `/cloud_registered`.

## 2026-06-06 CST - P0 Manifest/Audit Now Integrates 007 and 004

- PMO regenerated
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` and
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json` after
  consuming ROS2 Runtime 007 and MWORKS-Control 004. The run is still
  `quality_status=smoke_only`; `claim_scope` still excludes `planner` and
  `closed_loop`.
- ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PORT-PREFLIGHT-20260606-007` completed
  preflight classification only. EGO candidate packages copied to the isolated
  `Results/tmp/ego_planner_ros2_port_ws/src` are discovered by `colcon` as
  `ros.catkin`, and the bounded build fails first on missing
  `catkinConfig.cmake` for `quadrotor_msgs`. Port effort is
  `medium_to_large_port`; real `/position_cmd` recorder cannot run yet.
- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-FACTORY-TRACE-RECONNECT-20260606-004` is
  represented under `mworks.factory_trace_reconnect`: alias repair plus
  `check_model` passed, but 0-2 s smoke still produced empty times and zero
  alias refs. Next minimal probe is Factory-lite, not another full-wrapper
  retry.
- Current bundle audit passes with explicit warnings for the real blockers:
  standalone trace lookup passed but Factory consumption remains blocked;
  Factory reconnect aliases still zero; FAST-LIO is restored but planner
  PositionCommand is absent; EGO/Sunray/FUEL planner route needs porting;
  WeChat still needs one normal user message before one bounded retry.
- Focused checks passed:
  `python Scripts\quality\build_p0_slice_run_manifest.py --validate`;
  `python Scripts\quality\check_p0_run_bundle.py`;
  `python -m pytest Scripts\tests\test_p0_run_bundle_audit.py Scripts\tests\test_p0_slice_run_manifest.py Scripts\tests\test_run_manifest_gate.py -q`.

## 2026-06-06 CST - Factory Trace Reconnect Still Blocked

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-FACTORY-TRACE-RECONNECT-20260606-004` is
  blocked. This preserves the 003 standalone pass but does not create Factory
  trace-consumption evidence.
- Added wrapper-level aliases `x_ref/y_ref/z_ref/yaw_ref/z_ref_rate` and
  `trace_probe_state` to
  `QuadrotorExperiments.Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke`.
  No official baseline, controller gain, or dynamics parameter was edited.
- Sysplorer MCP probe and `check_model` passed. The required 0-2 s smoke still
  returned `SimulateModel data=false`; `GetVarTimes` returned `[]`; wrapper
  aliases and nested `planningReference` probes remained zero.
- Blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-TRACE-RECONNECT-20260606-004.json`.
  Next minimal probe is a Factory-lite model containing `TraceInlineReference`
  plus only `PlanningNavigationDisplay` and aliases, before adding plant or
  controller components incrementally.

## 2026-06-06 CST - P0 Manifest/Audit Integrated 006 and 003

- PMO regenerated
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` and
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json`.
  The manifest remains `quality_status=smoke_only`; `claim_scope` remains only
  `fast_lio` and `ue_visual`, with no `planner` or `closed_loop`.
- ROS2 Runtime blocker
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-WRAPPER-20260606-006.json`
  is now represented under `ros2.position_command_b1_planner_wrapper`. The
  selected EGO/Sunray/FUEL route is a valid semantic planner candidate, but it
  is ROS1/catkin while the current lane is ROS2 Humble and has no executable
  planner package. Converting FAST-LIO `/path` or scripted waypoints into
  PositionCommand remains rejected.
- MWORKS-Control return
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-TRACELOOKUP-DIAG-20260606-003.json`
  is now represented under `mworks.trace_lookup_diagnostic`. It is
  `diagnostic_pass` only: standalone trace lookup and Sysplorer result binding
  work, but Factory wrapper trace consumption is still blocked.
- Updated quality gate:
  `Scripts/quality/check_p0_run_bundle.py` now checks the 006 blocker packet
  and the 003 return/probe/raw paths. Current audit passes with warnings:
  standalone trace lookup passed but Factory consumption remains blocked;
  FAST-LIO runtime is restored but planner PositionCommand is absent; B1
  planner wrapper is blocked; WeChat still needs one normal user message before
  a bounded retry.
- Focused checks passed:
  `python Scripts\quality\build_p0_slice_run_manifest.py --validate`;
  `python Scripts\quality\check_p0_run_bundle.py`;
  `python -m pytest Scripts\tests\test_p0_run_bundle_audit.py Scripts\tests\test_p0_slice_run_manifest.py Scripts\tests\test_run_manifest_gate.py -q`.
- PMO created follow-up task packets:
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-PORT-PREFLIGHT-20260606-007.json`
  for isolated EGO/Sunray/FUEL ROS2 port preflight, and
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-TRACE-RECONNECT-20260606-004.json`
  for Factory wrapper alias/reconnect smoke.

## 2026-06-06 CST - MWORKS Standalone Trace Lookup Diagnostic Passed

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-TRACELOOKUP-DIAG-20260606-003` completed as a
  standalone diagnostic only, not as Factory/controller or closed-loop
  evidence.
- Added `QuadrotorExperiments.TraceLookupStandaloneSmoke`, which uses the
  existing exact-trace `TraceInlineReference` and exposes `x_ref`, `y_ref`,
  `z_ref`, `yaw_ref`, `z_ref_rate`, and a simple `probe_state`.
- Sysplorer MCP probe passed, package load passed, `check_model` passed, and
  `simulate_model` passed for 0-2 s. Result binding is usable at standalone
  level: `GetVarTimes` returned 41 samples and `x_ref@1s` was
  `0.31861753694312633`.
- Diagnostic artifacts:
  `Results/mworks_trace_consumption/trace_lookup_diag_20260606_003/trace_lookup_standalone_probe.json`,
  `Results/mworks_trace_consumption/trace_lookup_diag_20260606_003/trace_lookup_standalone_raw.csv`,
  and return packet
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-TRACELOOKUP-DIAG-20260606-003.json`.
- This narrows the previous 002 blocker: pure trace lookup and standalone
  Sysplorer result binding work. The next issue is Factory wrapper integration
  or result context binding, and B0 must remain `smoke_only`.

## 2026-06-06 CST - P0 Bundle Audit Added

- Added `Scripts/quality/check_p0_run_bundle.py` and
  `Scripts/tests/test_p0_run_bundle_audit.py` so the current P0 slice has a
  recoverability and overclaim audit beyond schema-level manifest validation.
- Current audit output:
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json`.
  It passes with `quality_status=smoke_only`, verifies required evidence and
  blocker packet paths, and preserves the warnings that FAST-LIO runtime is
  restored but planner PositionCommand is absent, and WeChat needs one normal
  user message before one bounded retry.
- Evidence-Logging task
  `RFLY-MOSIM-AUDIT-EVIDENCE-LOGGING-20260606-001` is complete with return
  packet
  `Results/agent_packets/returns/RFLY-MOSIM-AUDIT-EVIDENCE-LOGGING-20260606-001.json`.
  The audit proves bundle recoverability and honest smoke-only status; it does
  not prove planner closure or MWORKS closed_loop.

## 2026-06-06 CST - P0 Follow-Up Department Tasks Dispatched

- PMO dispatched ROS2 Runtime task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-WRAPPER-20260606-006` to persistent
  thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`. The task starts from the
  005-restored inputs `/Odometry` plus `/cloud_registered` and asks for a real
  existing EGO/Sunray/FUEL-style planner wrapper/port that emits sustained
  `/position_cmd`. It explicitly forbids fake maps, fake PositionCommand,
  UE global truth planner input, and hand-written planner algorithms.
- PMO dispatched MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-TRACELOOKUP-DIAG-20260606-003` to persistent
  thread `019e9999-b0d3-7682-bccd-faef08fcf1df`. The task reduces the prior
  trace-consumption blocker to a standalone pure Modelica trace lookup smoke
  model before reconnecting the Factory/controller wrapper.
- Expected packets:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-PLANNER-WRAPPER-20260606-006.json`
  or matching blocker, and
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-TRACELOOKUP-DIAG-20260606-003.json`
  or matching blocker. Until those return, P0 remains `smoke_only`; no
  `planner` or `closed_loop` claim is allowed.

## 2026-06-06 CST - P0 Manifest Integrated Current Blockers

- PMO integrated two durable department returns into
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`.
  The manifest remains `quality_status=smoke_only` and `claim_scope` still
  excludes `planner` and `closed_loop`.
- ROS2 Runtime blocker
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-UNBLOCK-20260606-005.json`
  is a partial restore: Gate B can currently regenerate `/Odometry`,
  `/cloud_registered`, and `/path` under
  `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_b1_unblock_20260606_005/`.
  B1 remains blocked because no planner/local-map runtime consumes `/Odometry`
  plus `/cloud_registered` and emits sustained real `/position_cmd`.
- MWORKS-Control blocker
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002.json`
  is also integrated. The trace wrapper/check_model pass is recorded only as a
  blocked attempt; `mworks.setpoint_trace_consumption_status=blocked`, with no
  consumed trace or trace-consumption evidence claimed.
- Focused checks passed:
  `python Scripts\quality\build_p0_slice_run_manifest.py --validate` and
  `python -m pytest Scripts\tests\test_p0_slice_run_manifest.py Scripts\tests\test_run_manifest_gate.py Scripts\tests\test_position_command_runtime_recorder.py Scripts\tests\test_ros_setpoint_adapter_contract.py -q`.
- WeChat sparse blocker notification packet
  `Results/coagent_gateway/packets/rfly_mosim_p0_current_blockers_integrated_20260606.json`
  reached the Weixin send layer but failed once with
  `weixin: sendMessage: ret=-2 errcode=0`. Do not retry in a loop. Per
  gateway ops, the user should send one normal text message in the
  `MoSim｜微信通知网关` chat before one bounded retry.

## 2026-06-06 CST - MWORKS Trace Consumption Blocked

- MWORKS-Control task
  `RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002` is blocked, not
  completed.
- Created project-owned trace wrapper/table artifacts under
  `Models/QuadrotorExperiments/`, `Config/scenarios/planning/`, and
  `Results/mworks_trace_consumption/` from the exact B0 `setpoint_trace.csv`.
  The source trace has 227 rows and its SHA is recorded in
  `Results/mworks_trace_consumption/trace_consumption_manifest_20260606.json`.
- Sysplorer MCP availability, package load, and `check_model` passed for
  `QuadrotorExperiments.Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke`.
  `SimulateModel` then returned false; `GetVarTimes` returned `[]`, and probed
  `planningReference` outputs stayed zero.
- No MWORKS trace-consumption raw CSV or metrics are claimed. Recovery should
  start from blocker packet
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002.json`.

## 2026-06-06 CST - P0 Slice RUN_MANIFEST Created

- Added `Scripts/quality/build_p0_slice_run_manifest.py` and
  `Scripts/tests/test_p0_slice_run_manifest.py`.
- Generated the first source-linked P0 slice manifest at
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` and checked
  it with `Scripts/quality/check_run_manifest.py`.
- The manifest deliberately stays `quality_status=smoke_only` and
  `evidence_level=p0_slice_smoke_manifest`. It links existing source-labeled
  evidence only:
  - MWORKS/MCP Factory scene smoke metrics and raw CSV;
  - Factory FAST-LIO Gate B current-pass evidence;
  - ROS2 planner setpoint adapter no-RViz smoke evidence.
- The manifest does not claim a full P0 closed loop. `claim_scope` excludes
  `planner` and `closed_loop`, and blockers remain:
  real local 3D map planner output is not bound to
  `/mosim/planner/position_cmd`; no same-run MWORKS/controller simulation has
  consumed the ROS2 adapter trace; UE Experiment Console command echo is still
  placeholder/design-only.
- Validation passed:
  `python Scripts/quality/build_p0_slice_run_manifest.py --validate`;
  `python -m pytest Scripts/tests/test_p0_slice_run_manifest.py Scripts/tests/test_run_manifest_gate.py Scripts/tests/test_ros_setpoint_adapter_contract.py Scripts/tests/test_planner_setpoint_adapter.py -q`;
  `python -m py_compile Scripts/quality/build_p0_slice_run_manifest.py Scripts/quality/check_run_manifest.py Scripts/ros/smoke_setpoint_adapter.py`;
  JSON syntax checks for the generated manifest and validation report; and
  `git diff --check` on the new manifest artifacts.
- Integrated the ROS2 Runtime department return packet
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-ADAPTER-BINDING-PLAN-20260606-001.json`.
  The department recommended an EGO/Sunray-style `PositionCommand` stream as
  the first real planner-output candidate because it directly maps to
  p/v/a/yaw setpoints and matches local EGO/Sunray reference contracts.
- Added project-owned ROS2 `PositionCommand` message and converter:
  `Scripts/ros/mosim_msgs/msg/PositionCommand.msg` and
  `Scripts/ros/mosim_setpoint_adapter/src/position_command_to_planner_setpoint_node.cpp`.
  The converter maps `/position_cmd` into `/mosim/planner/position_cmd`
  without implementing or replacing a planner. It normalizes the local EGO
  `world` frame alias to adapter `map`, maps position/velocity/acceleration,
  yaw/yaw_dot, trajectory id/status, and uses planner id `ego_position_cmd`.
- Added no-RViz chain smoke
  `Scripts/ros/smoke_position_command_adapter.py`. WSL validation passed:
  `colcon build --base-paths Scripts/ros/mosim_msgs Scripts/ros/mosim_setpoint_adapter --packages-select mosim_msgs mosim_setpoint_adapter --event-handlers console_direct+ --executor sequential`;
  `python3 Scripts/ros/smoke_position_command_adapter.py --timeout-s 8`.
  Result: `converted_count=1`, `setpoint_count=1`, status reached
  `accepted=true`, `mode=track`, `planner_id=ego_position_cmd`, and no ROS2
  adapter/converter process remained afterward.
- Regenerated the P0 slice manifest so it records the PositionCommand converter
  smoke evidence in addition to the existing setpoint adapter smoke. The
  manifest remains `smoke_only`; the next blocker is still a real planner/local
  map runtime stream and a same-run MWORKS/controller consumption of the adapter
  trace.
- Sent sparse WeChat completion notification through
  `CoAgent/gateway/cc_connect_weixin.py notify --packet ... --send` using
  packet
  `Results/coagent_gateway/packets/rfly_mosim_position_command_adapter_20260606.json`.
  The adapter returned `Message sent successfully.` The packet includes origin
  thread id `019e9868-83ea-70f0-92c5-a3a408bd78c6`.
- Confirmed the experienced architecture/coordination thread rule is now
  current project behavior: `019e0198-a041-77f1-84d0-c5524bfd4b81` can be asked
  directly when PMO is unsure how to create or dispatch a visible department,
  or when delegating department creation is faster. A matching Codex memory
  update note was written outside the repo at the user's explicit request.
- Dispatched the next durable ROS2 Runtime department planning task
  `RFLY-MOSIM-ROS2-RUNTIME-POSITIONCMD-SOURCE-20260606-002` to
  `019e9917-6181-7ec2-b3d6-4b624d6d3348`. Latest observed thread state is
  `inProgress`; no return/blocker packet had landed yet when checked. The
  target thread had already identified the likely Sunray/EGO ROS1-style route:
  `sunray_ego_single_mid360.launch` / `sunray_sim_ego.launch` ->
  `traj_server` -> `/uav1/pos_cmd`, with a ROS1-to-ROS2 routing/porting blocker
  still to resolve.
- Integrated the completed ROS2 Runtime return packet
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-POSITIONCMD-SOURCE-20260606-002.json`.
  Decision: the preferred real runtime source is the local Sunray/EGO chain
  `ego_planner_node -> traj_server -> /uav1/pos_cmd`. It is not directly
  claimable in MoSim yet because those launch files are ROS1-style while the
  current MoSim adapter lane is ROS2 Humble. The next execution route must
  explicitly choose either a bounded ROS1-to-ROS2 bridge or a narrow native
  ROS2 port/wrapper of the same runtime output contract.
- Added passive no-RViz recorder
  `Scripts/ros/record_position_command_adapter_runtime.py` plus static test
  `Scripts/tests/test_position_command_runtime_recorder.py`. The recorder does
  not publish `PositionCommand` and therefore cannot create fake planner
  evidence. It records an existing runtime source, converter output, adapter
  setpoint/status, topic rates, timestamp/frame gate, and planner-input gate
  into `Results/ros2_runtime/...`.
- Checks passed for this slice:
  `python -m pytest Scripts/tests/test_position_command_runtime_recorder.py Scripts/tests/test_ros_setpoint_adapter_contract.py -q`;
  `python -m py_compile Scripts/ros/record_position_command_adapter_runtime.py Scripts/tests/test_position_command_runtime_recorder.py`;
  Windows `python Scripts/ros/record_position_command_adapter_runtime.py --help`;
  WSL `source /opt/ros/humble/setup.bash && python3 Scripts/ros/record_position_command_adapter_runtime.py --help`.
- Quick WSL environment probe after fixing PowerShell-to-Bash `$PATH`
  expansion confirmed ROS2 Humble and `rclpy` are available, while
  `roscore`/`catkin_make` were not found. This makes Route A
  (ROS1 Sunray/EGO source plus ROS1-to-ROS2 bridge) a separate setup task, not
  the shortest immediate implementation route.
- PMO dispatched the next read-only Route B planning packet to the ROS2 Runtime
  department thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`:
  `RFLY-MOSIM-ROS2-RUNTIME-ROUTEB-PACKET-20260606-003`. Expected return:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-ROUTEB-PACKET-20260606-003.json`;
  blocker path:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-ROUTEB-PACKET-20260606-003.json`.
  The requested plan must separate B0 contract replay (`smoke_only`) from B1
  real planner/runtime port with real local-map/odom inputs.
- Hardened `Scripts/ros/record_position_command_adapter_runtime.py` so a missing
  real planner source records `source_available=false`,
  `runtime_source_required=true`, and a concrete blocker rather than looking
  like a silent tool failure. Verified in WSL with project ROS2 overlay:
  `source /opt/ros/humble/setup.bash && source install/setup.bash &&
  python3 Scripts/ros/record_position_command_adapter_runtime.py --duration-s 1
  --output-dir Results/tmp/positioncmd_recorder_no_source_smoke`. Expected exit
  was non-pass; generated summary reports `quality_status=needs_iteration` and
  blocker `No real planner runtime source was recorded on source_topic.`
- Copied this negative smoke evidence to
  `Results/ros2_runtime/positioncmd_recorder_no_source_smoke_20260606/`. This
  is not planner evidence; it proves the recorder fails closed until a real
  `/position_cmd` source is available.
- Integrated Route B planning packet
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-ROUTEB-PACKET-20260606-003.json`.
  It separates B0 contract replay (`smoke_only`) from B1 real planner/runtime
  port, where B1 still needs real local-map/odom input and must preserve
  Sunray/EGO behavior semantics rather than introducing a hand-written planner.
- Added B0 smoke-only source/orchestrator:
  `Scripts/ros/publish_position_command_contract_replay.py` and
  `Scripts/ros/run_b0_position_command_contract_replay.py`. The source
  publishes a smooth `mosim_msgs/PositionCommand` contract stream for adapter
  testing only; it is not a planner and does not consume local map or odometry.
  The orchestrator uses unique topic prefixes and the passive recorder to avoid
  shell PID and stale-topic contamination.
- B0 recorder run passed:
  `Results/ros2_runtime/positioncmd_b0_contract_replay_orchestrated_20260606_pass/run_summary.json`.
  Result: `quality_status=pass`, `source_available=true`, `accepted_ratio=1.0`,
  `stale_samples=0`, `rates_ok=true`, `timestamp_ok=true`, `frame_ok=true`,
  and `b0_contract_replay.smoke_only=true`. Topic rates were about
  `/position_cmd=19.99Hz`, converted setpoint `19.99Hz`, adapter setpoint
  `22.73Hz`, and status `22.73Hz`.
- Boundary: this B0 pass is only ROS2 adapter/recorder contract evidence. It
  cannot add `planner` or `closed_loop` to `RUN_MANIFEST.claim_scope` because
  `planner_input_gate.json` still records no real local-map/odom planner input
  and MWORKS has not consumed this trace in a same-run controller simulation.
- Integrated the B0 recorder evidence into
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` under
  `ros2.position_command_b0_contract_replay`. The manifest now points
  `planner.setpoint_trace` at the B0 recorder CSV
  `Results/ros2_runtime/positioncmd_b0_contract_replay_orchestrated_20260606_pass/setpoint_trace.csv`,
  while staying `quality_status=smoke_only` and
  `claim_scope=[fast_lio, ue_visual]`. Validation passed:
  `python Scripts/quality/build_p0_slice_run_manifest.py --validate`,
  `python -m py_compile Scripts/quality/build_p0_slice_run_manifest.py Scripts/tests/test_p0_slice_run_manifest.py`,
  and `python -m pytest Scripts/tests/test_p0_slice_run_manifest.py Scripts/tests/test_run_manifest_gate.py Scripts/tests/test_position_command_runtime_recorder.py Scripts/tests/test_ros_setpoint_adapter_contract.py -q`.
- Tried to send the required sparse WeChat completion notification with packet
  `Results/coagent_gateway/packets/rfly_mosim_b0_manifest_integrated_20260606.json`.
  The gateway failed with `connect: connection refused` on
  `/home/linux/.cache/mosim/coagent/cc-connect-weixin/data/run/api.sock` even
  after the adapter's bounded restart/retry. Recovery record:
  `Results/coagent_gateway/recovery/weixin_recovery_required_20260606_045903.json`.
  PMO sent the exact incident report, including origin thread id
  `019e9868-83ea-70f0-92c5-a3a408bd78c6`, to the WeChat ops thread
  `019e9855-aa43-7fe2-807e-be7d4095877b`.
- WeChat ops diagnosis found a local health false-positive: the previous
  health/recovery probe used `cc-connect sessions list --data-dir`, which can
  read session history from disk and return success without touching the
  internal API socket. The actual socket probe returned
  `ConnectionRefusedError: [Errno 111] Connection refused`, and no live
  `cc-connect` process owned `api.sock`.
- Fixed `Scripts/agent/check_weixin_gateway_health.py` and
  `CoAgent/gateway/cc_connect_weixin.py` to verify local API health by a real
  Unix socket `connect()` to
  `/home/linux/.cache/mosim/coagent/cc-connect-weixin/data/run/api.sock`.
  During diagnosis the script correctly wrote
  `Results/coagent_gateway/health/gateway_unhealthy_latest.json` with
  `failure_kind=api_socket`, then the stale lock/socket were cleared and the
  configured runtime was restarted once.
- Current gateway local state is recovered without a real WeChat canary:
  `Results/coagent_gateway/health/weixin_gateway_health_20260606_050621.json`
  and `gateway_healthy_latest.json` report `ok_local=true`,
  `api_socket_connectable=true`, `active_session_key_type=platform`, and
  `context_token_files=1`. WSL process evidence showed PID `40786` listening on
  the cc-connect `api.sock`.
- PMO retried the original B0 manifest completion packet after the local socket
  fix. It reached the Weixin layer but failed with
  `weixin: sendMessage: ret=-2 errcode=0`. Recovery record:
  `Results/coagent_gateway/recovery/weixin_recovery_required_20260606_050850.json`.
  Per WeChat ops guidance, do not retry in a loop; the next retry should happen
  only after the user sends one plain text message in the
  `MoSim｜微信通知网关` WeChat chat.
- Dispatched the next B1 ROS2 real-planner/runtime task to the existing
  ROS2 Runtime department thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`.
  Task packet:
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-20260606-004.json`.
  Expected return:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-20260606-004.json`;
  blocker:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-20260606-004.json`.
  The packet requires real runtime odom plus local sensed map/cloud/voxel input
  and explicitly forbids B0 replay, offline UE handoff, fake point cloud/map,
  keyboard pose overwrite, UE global-truth planner input, and hand-written
  planner/FAST-LIO replacements.
- Integrated the ROS2 Runtime B1 blocker packet:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-20260606-004.json`.
  Current live ROS2 graph only showed rosbridge/rosapi topics and nodes; it did
  not provide `/position_cmd`, FAST-LIO odometry, `/cloud_registered`, local
  occupancy/map/voxel topics, or a real planner runtime package. PMO regenerated
  `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json` so the
  blocker is visible under `ros2.position_command_b1_real_planner` and in the
  manifest `blockers`/warnings. The manifest still validates and remains
  `quality_status=smoke_only` with no `planner` or `closed_loop` claim.
- Dispatched follow-up unblock packet
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-UNBLOCK-20260606-005.json`
  to ROS2 Runtime thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`. The packet
  uses Factory Gate B historical FAST-LIO evidence only as a locator for the
  runnable route; it requires current live topics or a newly recorded current
  run before any B1 claim. Expected return:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-UNBLOCK-20260606-005.json`;
  blocker:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-UNBLOCK-20260606-005.json`.
- Created persistent visible department thread `MoSim｜MWORKS-Control 集成` with
  id `019e9999-b0d3-7682-bccd-faef08fcf1df` and assigned trace-consumption
  task packet
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002.json`.
  Expected return:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002.json`;
  blocker:
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002.json`.
  PMO static check confirms the B0 `setpoint_trace.csv` has 227 rows and
  `x_ref/y_ref/z_ref/v*_ref/a*_ref/yaw_ref/yaw_rate_ref` fields suitable for a
  reference mapping, but this is not MWORKS consumption evidence until a
  project-owned wrapper is checked/simulated through MCP.
- Tightened `Scripts/quality/check_run_manifest.py` and documented
  `Config/schemas/mosim_run_manifest_v1.schema.json` so any future
  `closed_loop` claim requires MWORKS to consume the same setpoint trace named
  by `planner.setpoint_trace`. Required fields are now
  `mworks.setpoint_trace_consumption_status=pass`,
  `mworks.consumed_setpoint_trace`, and `mworks.trace_consumption_evidence`.
  Regression test added in `Scripts/tests/test_run_manifest_gate.py` rejects a
  closed-loop manifest where MWORKS consumed a different trace file.

## 2026-06-06 CST - PMO Thread Dispatch Rule And ROS2 Adapter Smoke

- User clarified the operating model for visible threads versus sub-agents:
  Codex sub-agents are disposable one-task workers, while visible Codex
  threads are reusable department-style conversations with durable context.
  PMO may dispatch existing visible departments or create new ones when a task
  needs sustained ownership. If the user is online, PMO should use WeChat for
  sparse coordination; if not, PMO may create/dispatch directly when the next
  action is clear.
- Updated `AGENTS.md` and `Docs/Workflows/agent_orchestration.md` with the new
  rule. The DevOps/Git long-running department
  `019e74de-a452-7a50-99e7-ca9a247b32f1` must not be repurposed while it owns
  its current long task. Other suitable visible threads may be dispatched, and
  missing departments may be created with a full role prompt, origin thread id,
  request id, return/blocker packet paths, scope, forbidden actions, and
  checkpoint cadence.
- User also designated `019e0198-a041-77f1-84d0-c5524bfd4b81`
  (`MoSim｜四旋翼控制系统设计`) as the experienced architecture/coordination
  thread. Current corrected rule: if PMO is unsure how to create/dispatch a
  visible department, it may ask that thread for a charter or blocker only.
  Actual visible-thread creation, fork, rename, archive, or delegation remains
  PMO-only unless the user explicitly changes the rule.
- Cleaned stale WSL ROS2 adapter processes left by the previous timed-out
  smoke attempt. Root cause of the repeated timeout was PowerShell-to-WSL long
  inline Bash variable expansion: `$!`, `${SEC}`, and similar Bash variables
  were consumed before reaching Bash, leaving empty PIDs/timestamps.
- Added `Scripts/ros/smoke_setpoint_adapter.py` as a reusable no-RViz ROS2
  smoke harness. It launches the C++ `planner_setpoint_adapter_node`, publishes
  streamed 20Hz-style `PlannerSetpoint` messages with monotonic stamps and
  sequence numbers, subscribes to `/mosim/planner/setpoint` and
  `/mosim/planner/setpoint_adapter_status`, writes
  `Results/tmp/mosim_setpoint_adapter_smoke.json`, and cleans up the node.
- WSL ROS2 validation passed:
  `colcon build --base-paths Scripts/ros/mosim_msgs Scripts/ros/mosim_setpoint_adapter --packages-select mosim_msgs mosim_setpoint_adapter --event-handlers console_direct+ --executor sequential`.
  No-RViz smoke passed:
  `python3 Scripts/ros/smoke_setpoint_adapter.py --timeout-s 8`.
  Result summary: `published=true`, `setpoint_count=1`, `status_count=1`,
  `accepted=true`, `mode=track`, `planner_id=smoke`, and no adapter process
  remained afterward.
- PMO sent a visible-thread task to the experienced architecture/coordination
  thread `019e0198-a041-77f1-84d0-c5524bfd4b81` to create or locate a reusable
  `MoSim｜ROS2 Runtime 集成` department thread. Request id:
  `RFLY-MOSIM-CREATE-ROS2-RUNTIME-DEPT-20260606-001`; expected return path:
  `Results/agent_packets/returns/RFLY-MOSIM-CREATE-ROS2-RUNTIME-DEPT-20260606-001.json`.
  The architecture thread returned a blocker packet because its tool surface
  could not create visible threads:
  `Results/agent_packets/blockers/RFLY-MOSIM-CREATE-ROS2-RUNTIME-DEPT-20260606-001.json`.
  PMO then used its own visible thread-management tool to create
  `MoSim｜ROS2 Runtime 集成` with thread id
  `019e9917-6181-7ec2-b3d6-4b624d6d3348`, set the title, and dispatched the
  first read-only planning task:
  `RFLY-MOSIM-ROS2-RUNTIME-ADAPTER-BINDING-PLAN-20260606-001`.
- Sent sparse WeChat completion notification through
  `CoAgent/gateway/cc_connect_weixin.py notify --packet ... --send` using
  packet
  `Results/coagent_gateway/packets/rfly_mosim_ros2_adapter_smoke_20260606.json`.
  The adapter returned `Message sent successfully.`

## 2026-06-06 CST - P0 10h Execution Started

- User approved starting the RflySim-like MoSim architecture execution and asked
  for an at-least-10h goal, sub-agent planning, timely notifications, and
  continued progress when manual review is not immediately available.
- Created active execution plan:
  `Docs/Workflows/rfly_mosim_p0_10h_execution_plan.md`.
- Active PMO goal:
  `Factory scene -> UE sensor oracle / ROS2 sensor topics -> FAST-LIO/local map
  -> planner/setpoint stream -> 20Hz MWORKS controller -> MWORKS dynamics
  -> UE/RViz/evidence feedback`.
- Integrated the architecture design thread return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-AUDIT-UE-FRONTEND-MAP-20260606-001.json`.
  Status is `completed`; it defines UE Experiment Console, QGC/GCS-style
  surface placement, map-switching state machine, command/echo schema, and
  P0 smoke path. It is design evidence only, not UI/runtime implementation.
- Spawned three sidecar agents:
  ROS2-FASTLIO sidecar for topic/timing/FAST-LIO/local-map/planner gate;
  Evidence-Report sidecar for `RUN_MANIFEST` and source/quality gates; and
  MWORKS-Control sidecar for current wrapper feature matrix and safe model
  check/edit plan.
- Manual review policy for this 10h run: if a review packet is needed, send a
  sparse WeChat message with origin thread id
  `019e9868-83ea-70f0-92c5-a3a408bd78c6`; if the user does not respond in
  time, record `review_pending` and continue headless work that does not depend
  on that review decision.
- Current worktree has unrelated or concurrent Git/reference changes
  (`.gitignore`, `References/Agent/...`, `Results/codex_app_debug/`). The PMO
  thread must not revert or stage those as part of P0 architecture work.
- First checkpoint:
  - Sysplorer MCP health passed with `driver_ready=true`.
  - `QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke` and
    `QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke` both passed
    `check_model`.
  - `HoverSmoke` simulation verified `dynamics.hover_thrust_error@end =
    1.7763568394002505e-15`.
  - `YawStepSmoke` simulation verified `dynamics.total_moment_body[3]@end =
    0.06147367992970332`.
  - Updated
    `Results/identification/sunray150/SUNRAY150_DYNAMICS_UPGRADE_20260605.md`
    with this `source=MWORKS_MCP` refresh.
- Sidecar checkpoint:
  - Evidence sidecar says P0 needs a strict `RUN_MANIFEST.json` and cross-layer
    gate before any full-loop claim.
  - MWORKS-Control sidecar confirms motor lag/yaw torque/rotor-center moment
    exist in the project-owned experimental dynamics, not in the official
    baseline.
  - ROS2-FASTLIO sidecar confirms Factory FAST-LIO Gate B is current-pass for
    manual UE/RViz review readiness, but P0 still lacks a real 3D local
    map/planner gate and 20Hz planner-to-MWORKS setpoint adapter.
- WeChat checkpoint packet:
  `Results/coagent_gateway/packets/rfly_mosim_p0_10h_start_checkpoint_20260606.json`.
  The first send attempts were blocked by packet schema issues
  (`unsupported packet type`, then missing review `decision`). After adding
  `template_type=review_packet` and `decision=needs_review`, the adapter sent
  successfully. Do not treat earlier blocked attempts as user notification.
- Implemented the first P0 evidence gate:
  `Config/schemas/mosim_run_manifest_v1.schema.json`,
  `Scripts/quality/check_run_manifest.py`, and
  `Scripts/tests/test_run_manifest_gate.py`.
  The checker prevents slice evidence from being overclaimed as full P0 by
  requiring formal MWORKS source labels, ROS2 timing/FAST-LIO metrics, no
  global-truth planner input, 20Hz setpoint trace for planner/closed-loop
  claims, and `ue.no_pose_overwrite_status=pass`.
  Checks passed:
  `python -m pytest Scripts/tests/test_run_manifest_gate.py -q`,
  `python -m json.tool Config/schemas/mosim_run_manifest_v1.schema.json`, and
  `python Scripts/quality/check_run_manifest.py --help`.

## 2026-06-06 CST - P0 Planner Setpoint Adapter Contract

- Tightened the P0 planner/closed-loop gate so an offline UE
  navigation/control handoff cannot be claimed as the runtime
  planner-to-MWORKS adapter. `Scripts/quality/check_run_manifest.py` now
  requires `planner.setpoint_trace_source=RUNTIME_20HZ_ADAPTER`,
  `planner.setpoint_adapter_status=pass`, a positive
  `planner.stale_command_timeout_s`, and an existing 20Hz trace for
  planner/closed-loop claims.
- Added regression coverage in `Scripts/tests/test_run_manifest_gate.py` and
  kept `Scripts/tests/test_navigation_handoff.py` asserting the generated
  scenario remains inactive/offline.
- Added the headless planner setpoint adapter contract at
  `Scripts/ros/planner_setpoint_adapter.py` with tests in
  `Scripts/tests/test_planner_setpoint_adapter.py`. It generates a 20Hz
  setpoint trace and accepted/rejected echo log from runtime-style p/v/a/yaw
  planner commands, rejects wrong frames/non-finite values, and records stale
  commands as `mode=hold`.
- Boundary: this is an executable contract only. It does not publish ROS2
  messages and does not prove live closed-loop integration until a real ROS2
  node and MWORKS run bind it under one `RUN_MANIFEST`.
- Checks passed: `python -m pytest Scripts/tests/test_planner_setpoint_adapter.py -q`;
  `python Scripts/tests/test_planner_setpoint_adapter.py`;
  `python -m pytest Scripts/tests/test_run_manifest_gate.py Scripts/tests/test_navigation_handoff.py Scripts/tests/test_mworks_uav_state_ros2.py -q`;
  `python -m json.tool Config/schemas/mosim_run_manifest_v1.schema.json`;
  `python Scripts/quality/check_run_manifest.py --help`.
- Sent sparse WeChat completion notification through
  `CoAgent/gateway/cc_connect_weixin.py` using packet
  `Results/coagent_gateway/packets/rfly_mosim_p0_setpoint_adapter_contract_20260606.json`;
  adapter returned `Message sent successfully.` Origin thread id included:
  `019e9868-83ea-70f0-92c5-a3a408bd78c6`.
- Added ROS2 skeleton packages for the same contract:
  `Scripts/ros/mosim_msgs/` and `Scripts/ros/mosim_setpoint_adapter/`.
  Static test `Scripts/tests/test_ros_setpoint_adapter_contract.py` checks
  `PlannerSetpoint`, `SetpointAdapterStatus`, default topics
  `/mosim/planner/position_cmd`, `/mosim/planner/setpoint`,
  `/mosim/planner/setpoint_adapter_status`, and reject/stale status strings.
  This is still not a live ROS2 runtime pass; WSL `colcon build` and a
  no-RViz topic smoke remain next.

## 2026-06-06 CST - RflySim-like Architecture Audit And Dispatch Plan

- User provided `C:\Users\HP\Downloads\Mosim审核.md` as an external audit
  checklist and asked to optimize the architecture, plan goals, and dispatch
  sub-agent work around an RflySim-like MoSim platform. The external read is
  limited to that user-named file; project state is recorded inside MoSim.
- Added `Docs/Design/11_RflySim式MoSim最小闭环架构审核.md`. Conclusion:
  MoSim has the correct RflySim-like boundary and credible implementation
  slices, but it is not yet a complete minimum closed-loop platform. The
  missing single run is still:
  `UE/env sensor -> ROS2 FAST-LIO/local map -> planner -> 20Hz MWORKS
  controller -> MWORKS plant -> UE/ROS2 feedback`.
- The audit records a nine-module completion table, breakpoint analysis,
  P0/P1/P2 roadmap, and 10 tasks for the minimum usable version. Current
  completion is partial: architecture boundary, accepted rotor geometry,
  SDF/YunZong parameter seed provenance, Factory Gate B manual-review
  readiness, and PID-demo codegen/SIL are useful; PX4 integration, live
  planner-to-MWORKS setpoint flow, UE command/uplink, unified run bundle, and
  final dynamics upgrade remain open.
- Generated five scoped dispatch packets:
  `Results/agent_packets/tasks/audit/RFLY-MOSIM-AUDIT-ROS-FASTLIO-20260606-001.json`,
  `Results/agent_packets/tasks/audit/RFLY-MOSIM-AUDIT-MWORKS-CONTROL-20260606-001.json`,
  `Results/agent_packets/tasks/audit/RFLY-MOSIM-AUDIT-PX4-SILHIL-20260606-001.json`,
  `Results/agent_packets/tasks/audit/RFLY-MOSIM-AUDIT-UE-FRONTEND-MAP-20260606-001.json`,
  and `Results/agent_packets/tasks/audit/RFLY-MOSIM-AUDIT-EVIDENCE-LOGGING-20260606-001.json`.
- Updated `Docs/Workflows/agent_task_ledger.md` with the PMO audit task and
  five child streams. The UE/frontend/map packet is ready to dispatch to the
  visible architecture design thread `019e0198-a041-77f1-84d0-c5524bfd4b81`.
- Guardrails reiterated: no fake point cloud, no fake 2D grid map, no keyboard
  pose overwrite, no browser active point-cloud review, no hand-rolled
  FAST-LIO/planning/formation, no direct official QuadChassis baseline damage,
  and no RflySim/Gazebo sample parameters as identified Sunray150 truth.

## 2026-06-06 CST - UAV Architecture Sync Dispatched

- User requested a focused design pass to align Gazebo/Sunray and RflySim UAV
  simulation flows with MoSim's MWORKS-first architecture.
- Main PMO thread id is `019e9868-83ea-70f0-92c5-a3a408bd78c6`; the request was
  sent to architecture design thread `019e0198-a041-77f1-84d0-c5524bfd4b81`
  with an explicit return contract.
- Dispatch packet:
  `Results/agent_packets/tasks/architecture_sync/UAV-ARCH-SYNC-20260606-001.json`.
- Expected return:
  `Results/agent_packets/returns/UAV-ARCH-SYNC-20260606-001.json`; blocker:
  `Results/agent_packets/blockers/UAV-ARCH-SYNC-20260606-001.json`.
- Required design focus: MWORKS as dynamics/control/truth/metrics, UE as
  renderer/sensor oracle, ROS2/RViz2/FAST-LIO/planner/formation as reusable
  algorithm and review windows; 20Hz controller/setpoint, 20Hz enhanced LiDAR
  target, high-rate IMU, one clock domain, and synchronized FAST-LIO odometry
  evaluation against truth.
- Forbidden routes remain: fake point cloud, fake grid map, keyboard pose
  overwrite, browser HTML active map/point-cloud review, and hand-rolled
  FAST-LIO/planning/formation algorithms.
- Follow-up integration: the architecture design thread returned
  `status=completed` with `needs_user_action=false` in
  `Results/agent_packets/returns/UAV-ARCH-SYNC-20260606-001.json`.
  The result is now integrated into `Docs/Design/10_架构边界与当前状态ADR.md`
  and `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md`.
- Active open blockers from the return: exact local PX4 Iris model source still
  needs a later parameter audit; no PX4 ULog/bench bundle exists, so
  non-geometry Sunray150 parameters remain `source=SDF_migration` seeds; and
  FAST-LIO current gates do not yet close final production localization,
  planner performance, or controller integration.
- The user-requested 20Hz loop is now documented as: controller/setpoint 20Hz
  streamed contract, enhanced LiDAR 20Hz target only with throughput,
  monotonic timestamp, per-point offset, explicit extrinsic, FAST-LIO output,
  and truth-error gates; `/mosim/truth/odometry` is evaluation truth, not a
  substitute for FAST-LIO odometry.
- User added that the simulator should also design a recommended RflySim-like
  UE front-end/operator console. Updated `Docs/Design/10_架构边界与当前状态ADR.md`
  and `Docs/Workflows/unreal_renderer.md`: UE can expose scenario,
  controller, planner, motor fault, wind disturbance, sensor mode, evidence,
  and recording controls, but only as operator intent. MWORKS/ROS2 adapters
  must validate and echo accepted state before the UI shows it as active. UE
  must not directly teleport pose, inject hidden global map truth, or judge
  controller/planner success.
- Follow-up frontend architecture expansion: updated `Docs/Design/00_系统总体设计.md`,
  the ADR, and `Docs/Workflows/unreal_renderer.md` so MoSim has a multi-window
  product interface plan, not only a UE panel. MoSim Studio owns batch
  experiments/results; UE Experiment Console owns live rendered operation and
  requests; QGC/GCS-style windows are future PX4/V6X/offboard supervision only;
  RViz2 owns point-cloud/FAST-LIO/local-map/planner review; Sysplorer/Syslab
  remain model/result authority. Map switching must synchronize
  `scene_source_id`, `scene_id`, `map_id`, MWORKS scenario binding, ROS2 topic
  contract, truth artifacts, and evidence paths before the UI enables
  review/run controls.

## 2026-06-06 CST - MoSim Architecture Boundary ADR Added

- Added `Docs/Design/10_架构边界与当前状态ADR.md` as the compact current
  architecture entry for new conversations and parallel task streams.
- The ADR fixes the active boundary: MWORKS/Sysplorer/Sysblock/Syslab own
  dynamics, controller, truth, metrics, and generated controller runtime; UE5
  owns high-quality rendering, accepted UAV visual, camera, collision and
  sensor oracle; ROS2/RViz2/FAST-LIO own native robotics transport,
  localization/map/planner review; CoAgent/WeChat remains sparse progress and
  human intervention only.
- Recorded the Gazebo/Sunray plugin translation rule: Gazebo plugins are not
  copied as runtime plugins. Motor, base, MAVLink, groundtruth, IMU, Livox ray,
  camera/GPS/barometer/magnetometer semantics must become explicit MoSim
  modules with separate evidence gates.
- Current Sunray/Gazebo parameters remain baseline seeds:
  `mass=1.0 kg`, `Ixx/Iyy/Izz=0.0085/0.0085/0.012`,
  `motorConstant=8.54858e-06`, `momentConstant=0.06`,
  `timeConstantUp=0.0125`, `timeConstantDown=0.025`, and
  `rotorVelocitySlowdownSim=10`. MWORKS `lift_cofficient=0.000854858` is the
  SDF motor constant scaled by `rotorVelocitySlowdownSim^2`; it remains
  `source=SDF_migration`, not Sunray150 identified truth.
- RflySim is now explicitly recorded as a role-split and actuator-structure
  reference, not a parameter truth or direct `.mo` translation source. Useful
  ideas are streamed state/command transport, actuator lag/thrust/moment
  structure, parameter injection, and multi-rate execution.
- Updated `Docs/Index/project_work_memory_index.md`,
  `Docs/Workflows/new_conversation_context.md`,
  `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md`,
  `Docs/Workflows/unreal_renderer.md`,
  `Docs/Workflows/mworks_codegen_controller_runtime.md`, and
  `Docs/Workflows/identify_quadrotor_parameters.md` to point to or align with
  the ADR.
- Read-only sub-agent results supported the split: one agent confirmed current
  docs mainly lacked a compact ADR/Gate matrix; another confirmed RflySim's
  CopterSim/RflySim3D/ROS role split and warned not to reuse RflySim numeric
  parameters as Sunray150 truth. The Sunray/Gazebo plugin conclusion was
  verified directly from local SDF files in this thread.

## 2026-06-06 CST - Cross-Thread Department Return Protocol Documented

- Documented that Codex App cross-thread send is one-way task delivery, not
  request/response RPC. A forwarded message is not task completion.
- Updated `Docs/Workflows/agent_orchestration.md` so every department-to-
  department request must expose `origin_thread`, `origin_thread_id`,
  `target_thread`, `target_thread_id`, `request_id`, expected return path, and
  blocker path.
- Target departments must first resolve issues inside their own scope. If they
  cannot solve the issue, they return a blocker packet to the origin thread id.
  PMO may audit or integrate, but PMO is not the only return owner.
- Durable returns now use
  `Results/agent_packets/returns/<request_id>.json`; durable blockers use
  `Results/agent_packets/blockers/<request_id>.json`. WeChat remains a sparse
  alert channel only.
- Updated `Docs/Index/codex_app_session_research.md` with the same Codex App
  transport boundary.

## 2026-06-06 CST - WeChat Gateway Background Health Monitoring Hardened

- Upgraded WeChat gateway maintenance from conversation memory to background
  Task Scheduler + project script evidence. This does not rely on any Codex
  conversation staying open.
- Verified Windows Task Scheduler:
  `MoSim Weixin Gateway Local Health` is enabled, runs
  `python Scripts\agent\check_weixin_gateway_health.py` every 15 minutes, and
  latest scheduler state showed `LastRunTime=2026/6/6 0:06:01`,
  `LastTaskResult=0`, `NextRunTime=2026/6/6 0:21:00`.
  `MoSim Weixin Gateway Canary` is enabled and remains every 4 hours; frequency
  was not increased. It had not yet reached its first scheduled run
  (`NextRunTime=2026/6/6 3:21:00`).
- `Scripts/agent/check_weixin_gateway_health.py` now writes durable latest
  status files on every run:
  `Results/coagent_gateway/health/gateway_healthy_latest.json` when local
  health is OK, and
  `Results/coagent_gateway/health/gateway_unhealthy_latest.json` when local
  health fails. Failure reporting is file/local-notification based and does not
  depend on WeChat.
- The script now classifies local failures as `data_dir`, `api_socket`,
  `session`, `active_session`, `context_token`, or `unknown`, and records a
  minimal user action in the latest failure file. Optional Windows toast is
  attempted only on local health failure; if unavailable, the file remains the
  authoritative alert surface.
- Fixed `CoAgent/gateway/cc_connect_weixin.py` so its default data-dir is
  platform-aware. Windows defaults to the WSL UNC path, so other Codex
  conversations can call the narrow adapter without explicitly passing
  `--data-dir` and still resolve the platform `active_session`.
- Validation passed:
  `python Scripts\agent\check_weixin_gateway_health.py` wrote
  `Results/coagent_gateway/health/weixin_gateway_health_20260606_000614.json`
  and refreshed `gateway_healthy_latest.json`; `python -m py_compile
  Scripts\agent\check_weixin_gateway_health.py CoAgent\gateway\cc_connect_weixin.py`
  passed. No real WeChat canary was sent in this round.

## 2026-06-05 CST - WeChat Cross-Thread Notification Policy Clarified

- User reports WeChat communication is now normal. Durable rule: all other
  Codex conversations send sparse completion/blocker/review packets through
  `CoAgent/gateway/cc_connect_weixin.py`; none of them owns cc-connect runtime
  maintenance.
- `MoSim｜微信网关运维`
  (`019e9855-aa43-7fe2-807e-be7d4095877b`) owns scheduled health checks,
  low-frequency outbound canary, QR/context-token/active-session recovery, and
  failure classification.
- Updated `Docs/Workflows/debug_mcp.md` with the cross-thread notification
  guarantee and no-tight-loop retry boundary.

## 2026-06-05 CST - Codex Thread Registry Refreshed

- Read-only scan of Windows Codex state DB produced
  `Results/codex_history_audit/current_codex_threads_title_scan_20260605.csv`.
- Current active MoSim operating threads:
  `019e9868-83ea-70f0-92c5-a3a408bd78c6` = `MoSim｜主线 PMO`;
  `019e74de-a452-7a50-99e7-ca9a247b32f1` = `MoSim｜DevOps 发布`;
  `019e9855-aa43-7fe2-807e-be7d4095877b` = `MoSim｜微信网关运维`;
  `019e8358-86b4-7070-8fd6-a2b4f4d2af97` = `MoSim｜WechatCodex`.
- Older CoAgent bootstrap conversations are still active in the DB but should
  be treated as inactive/legacy unless the user explicitly resumes CoAgent
  runtime work.

## 2026-06-05 CST - WeChat Gateway Canary Failed At Weixin Send Context

- User explicitly authorized a real outbound canary after the earlier local-only
  check. The first send attempt exposed a Windows launcher bug:
  `CoAgent/gateway/cc_connect_weixin.py` tried to execute the Linux ELF
  `Results/tmp/cc-connect-node/node_modules/cc-connect/bin/cc-connect`
  directly from Windows and failed with `WinError 193`.
- Fixed the narrow adapter path so Windows runs cc-connect through
  `wsl.exe -d Ubuntu-22.04 -- /mnt/c/.../cc-connect`, and fixed
  `Scripts/agent/check_weixin_gateway_health.py` so canary sends pass the
  WSL-backed data dir explicitly.
- A real canary then reached the cc-connect/Weixin send layer. The runtime log
  `Results/tmp/cc-connect-weixin-smoke/recover-20260605_233952.log` shows
  Weixin declined outbound `sendMessage` with `ret=-2 errcode=0` after three
  fresh-context retries.
- Current local-only health is good after the script correction:
  `Results/coagent_gateway/health/weixin_gateway_health_20260605_234230.json`
  has `ok_local=true`, `api_socket_connectable=true`,
  `active_session_present=true`, `active_session_key_type=platform`, and
  `context_token_files=1`.
- Conclusion: local cc-connect runtime/session state is reachable, but
  end-to-end Weixin outbound communication is not currently normal. Minimal
  user action: send one ordinary plain-text message in the
  `MoSim｜微信通知网关` WeChat chat, then retry one canary. If it still returns
  `ret=-2`, rerun QR login for cc-connect Weixin.
- Follow-up after user sent an ordinary WeChat message: fixed the adapter
  recovery wait so it verifies `api_socket_connectable` instead of only socket
  file existence. Final canary
  `Results/coagent_gateway/health/weixin_gateway_health_20260605_235034.json`
  succeeded with `send_result.ok=true` and `stdout="Message sent successfully."`
  End-to-end Weixin outbound communication is recovered.
- User then reported the delivered WeChat message was garbled. Fixed
  `CoAgent/gateway/cc_connect_weixin.py` to pass UTF-8 text explicitly to the
  Windows `wsl.exe ... cc-connect send --stdin` subprocess. Verification
  canary `Results/coagent_gateway/health/weixin_gateway_health_20260605_235128.json`
  also succeeded with `send_result.ok=true`; visual confirmation of readable
  Chinese is pending user review.

## 2026-06-05 CST - WeChat Gateway Scheduled Health Check Verified

- Scope: this was handled in the dedicated WeChat gateway operations thread
  `MoSim｜微信网关运维`. No MoSim technical implementation, Git work, simulation
  code, or outbound WeChat canary was run.
- Windows Task Scheduler entries exist and are enabled:
  `MoSim Weixin Gateway Local Health` runs
  `python Scripts\agent\check_weixin_gateway_health.py` every 15 minutes; next
  run was `2026/6/5 23:36:00`.
  `MoSim Weixin Gateway Canary` runs
  `python Scripts\agent\check_weixin_gateway_health.py --send-canary` every 4
  hours; next run was `2026/6/6 3:21:00`.
- Both tasks still showed the Task Scheduler sentinel `LastRunTime =
  1999/11/30 0:00:00` and `LastTaskResult = 267011`, so the scheduled entries
  were present but had not yet produced a scheduler-run result at the time of
  inspection.
- Manual local-only health check passed:
  `python Scripts\agent\check_weixin_gateway_health.py` wrote
  `Results/coagent_gateway/health/weixin_gateway_health_20260605_232655.json`
  with `ok_local=true`, `api_socket_exists=true`,
  `active_session_present=true`, `active_session_key_type=platform`, and
  `context_token_files=1`.
- No manual action is required from the user now. If a future local health JSON
  reports failure, classify the failing field first as `api_socket`,
  `session/active_session`, or `context_token`, then request only the minimal
  matching user action.

## 2026-06-05 CST - WeChat Intervention Thread Reclassified

- User correction: thread `019e8358-86b4-7070-8fd6-a2b4f4d2af97` is a
  conversation created after WeChat human intervention, not the dedicated
  WeChat gateway operations thread. Do not route gateway maintenance,
  cc-connect QR recovery, or notification-runtime ownership to that thread.
- Dedicated Codex thread for WeChat gateway operations was manually created by
  the user:
  `019e9855-aa43-7fe2-807e-be7d4095877b` = `MoSim｜微信网关运维`.
- Clarification: `019e8358-86b4-7070-8fd6-a2b4f4d2af97` is the Codex
  conversation used by the WeChat-side message path. It is not a task-intake
  owner and should not be asked to maintain gateway runtime. Send cc-connect,
  QR, context-token, active-session, scheduled health-check, and recovery
  instructions to `019e9855-aa43-7fe2-807e-be7d4095877b`.
- Current manual multi-thread plan should keep only a small always-on set:
  main PMO/task thread, DevOps/Git thread, and a separate WeChat gateway
  operations thread. Other CoAgent departments remain out of scope unless the
  user explicitly resumes CoAgent runtime work.

## 2026-06-05 CST - Codex App History Titles And Project Roots Fixed

- After the Codex App history became visible again, the user reported that the
  App showed only MoSim and that most titles were wrong. Verified the backend
  with `codex app-server --stdio`: global active history already contained 28
  records, but many `thread/list` items returned `name=null`, so the App UI
  fell back to the first user message / long preview.
- Stopped Codex App/app-server/plugin helper processes, then backed up the
  Windows Codex state to
  `C:\Users\HP\.codex\backups\app-history-title-project-fix-20260605-221723`.
  The backup includes `state_5.sqlite*`, `session_index.jsonl`,
  `.codex-global-state.json`, and all 28 active rollout files.
- Synchronized the 28 active records across SQLite `threads.title`,
  `session_index.jsonl.thread_name`, and each rollout first-line
  `session_meta.payload.title/name/thread_name`. Also updated the App global
  project roots to include `C:\Users\HP\Desktop\MoSim`,
  `C:\Users\HP\Desktop\DH`, and `C:\Users\HP\Desktop\JIT-Fine`.
  Manifest:
  `Results/codex_history_audit/app_history_title_project_fix_20260605-2217_manifest.json`.
- Verification passed through the Windows app-server protocol: global active
  list returns 28 records with `missing_name=0`; project queries return
  `MoSim=14`, `DH=12`, and `JIT-Fine=2`, all with non-empty titles.
  If the App window still shows only MoSim after relaunch, that is now a
  frontend/project-view cache or workspace selection issue, not missing backend
  history data.

## 2026-06-05 CST - Windows Native Codex TUI Input Bug Recorded

- Windows native Codex CLI remains unsuitable for interactive TUI use on this
  machine. The symptom is not a normal keyboard or PowerShell input failure:
  a project key probe using `[Console]::ReadKey($true)` correctly reads
  `A`, `Backspace`, `Delete`, `Enter`, pasted characters, and `Escape` in
  Windows Terminal / PowerShell.
- The failure is specific to Codex TUI raw input/rendering: in interactive
  `codex`, `Backspace` behaves as if it moves in the wrong direction, and
  `Enter`, paste, and deletion remain unusable. The issue reproduces after
  bypassing the user profile (`powershell.exe -NoProfile`) and running
  `C:\nvm4w\nodejs\codex.cmd` directly, so the root cause is not the user
  PowerShell profile, input method, Windows key events, or the patched
  `codex.ps1` launcher.
- Routes tried without fixing the TUI: Windows Terminal + classic PowerShell
  5.1, PowerShell 7.6.2 install/test, `--no-alt-screen`, disabling
  `features.terminal_resize_reflow`, setting
  `CODEX_TUI_DISABLE_KEYBOARD_ENHANCEMENT=1`, bypassing npm's PowerShell shim,
  running the native `codex.exe` directly, and a temporary downgrade to
  `@openai/codex@0.130.0`.
- Current state after stopping CLI troubleshooting: npm global Codex is back
  at `@openai/codex@0.137.0`; `C:\Users\HP\.codex\config.toml` has
  `features.terminal_resize_reflow = false`; PowerShell 7.6.2 is installed;
  `Scripts/tools/windows_key_probe.ps1` is available for future key-event
  checks. Prefer Codex App / VSCode Codex or WSL Codex TUI until upstream
  Windows native TUI behavior is fixed.

## 2026-06-05 CST - Codex App History Visible After Reinstall

- After reinstalling Codex App, the App initially showed no chat history even
  though `C:\Users\HP\.codex` still contained 28 active rollout files and a
  healthy `state_5.sqlite`. The durable root cause was not only SQLite:
  `thread/list` also reads each rollout file's first-line
  `session_meta.payload`. Those metadata rows still used WSL paths such as
  `/mnt/c/Users/HP/Desktop/MoSim`, so the App/backend exposed them as
  `C:\mnt\c\Users\HP\Desktop\MoSim`; a project query for
  `C:\Users\HP\Desktop\MoSim` returned an empty list.
- Stopped Codex App/app-server/plugin helper processes, backed up state/index
  files to
  `C:\Users\HP\.codex\backups\app-empty-history-fix-20260605-215735`, then
  normalized the Windows history DB to 28 active rows:
  `source=cli`, `thread_source=user`, `archived=0`, and cwd groups
  `MoSim=14`, `DH=12`, `JIT-Fine=2`. Rebuilt `session_index.jsonl` with 28
  entries and verified all rollout paths exist.
- Rewrote only the first `session_meta` JSONL line of the 28 rollout files so
  `payload.cwd`, `payload.source`, and `payload.thread_source` match Windows
  App-compatible values. Full per-file before/after manifest:
  `Results/codex_history_audit/app_empty_history_rollout_meta_fix_20260605-220250.jsonl`.
- Protocol check using `codex app-server --stdio` passed after the metadata
  fix: `thread/list` returned `MoSim=14`, `DH=12`, and global active `28`.
  Cleared Codex App frontend cache after backing it up to
  `C:\Users\HP\.codex\backups\app-frontend-cache-before-history-visible-20260605-220442`,
  then relaunched Codex App. Windows screenshot showed the App left sidebar
  populated with the 14 MoSim histories again.

## 2026-06-05 CST - Windows Codex Home Quarantined For Clean Rebuild

- Per user request, cleaned the Windows Codex home as an external
  infrastructure operation outside the project tree. The old
  `C:\Users\HP\.codex` was not permanently deleted; it was quarantined under
  `C:\Users\HP\.codex.quarantine-2026060`.
- The first `Move-Item` attempt partially moved the directory and was blocked
  by a live Chrome extension host under
  `C:\Users\HP\.codex\plugins\cache\openai-bundled\chrome\latest\extension-host\windows\x64`.
  Stopped only the locked `cmd.exe` / `extension-host.exe` pair, then moved the
  remaining old `.codex` contents into
  `C:\Users\HP\.codex.quarantine-2026060\remaining_from_failed_move_20260605-145907`.
- Recreated `C:\Users\HP\.codex` as an empty clean directory. Do not restore
  files from `C:\Users\HP\.codex.quarantine-2026060`, nested `backups*`
  directories, or `remaining_from_failed_move_*` unless they are explicitly
  reviewed and selected. Next intended route is to clean WSL history/config
  first, then migrate only the reviewed clean source into this fresh Windows
  Codex home with Windows paths.
- After the user uninstalled Codex App, removed the remaining Windows Codex CLI
  npm artifacts without deleting Node/nvm: deleted
  `C:\nvm4w\nodejs\codex`, `codex.cmd`, `codex.ps1`, and
  `C:\nvm4w\nodejs\node_modules\@openai\codex`; removed the empty
  `C:\nvm4w\nodejs\node_modules\@openai` directory. Verification:
  `where.exe codex` returns no command, those Codex files no longer exist, and
  `C:\Users\HP\.codex` remains empty.
- Started WSL history cleanup from `/home/linux/.codex` after Windows Codex
  was reset. Generated read-only review reports under
  `Results/codex_history_audit/`. Per user decision, deleted three archived
  `HP/Desktop` scratch records from WSL history:
  `019ddf78-e5f7-7b02-bcd9-35ddd016512e`,
  `019e39b0-979b-7940-8b1d-570f60202cd6`, and
  `019e39f9-7c27-7051-9958-131aa116b547`; unarchived dog image record
  `019e1aa8-5855-7c83-9db9-a97f1e1050e5` by moving its rollout back to
  `/home/linux/.codex/sessions/2026/05/12/`. Backups and manifest:
  `/home/linux/.codex/backups/wsl-clean-other-project-20260605-1530/` and
  `Results/codex_history_audit/wsl_clean_other_project_20260605-1530_manifest.json`.
  Post-check: SQLite `integrity_check=ok`, `quick_check=ok`, 305 DB rows,
  113 active, 192 archived, 0 missing rollout rows, 1 file-only rollout id.
- Per user review, deleted another 13 WSL history records: the scoped
  `COAGENT-MINILOOP-02-WORKER` record, five old archived CoAgent department
  bootstrap records, and seven MoSim greeting/visibility/empty test records.
  Backups and manifest:
  `/home/linux/.codex/backups/wsl-delete-coagent-old-and-scratch-20260605-1545/`
  and
  `Results/codex_history_audit/wsl_delete_coagent_old_and_scratch_20260605-1545_manifest.json`.
  Post-check: SQLite `integrity_check=ok`, `quick_check=ok`, 292 DB rows,
  107 active, 185 archived, all 13 requested IDs absent from DB, 13 rollout
  files deleted, 0 remaining rollout files for those IDs. Latest WSL cleanup
  buckets now show 261 subagent/delegated candidates, 10 CoAgent records still
  under review, 8 DH records, 6 other-project records, 4 MoSim user-work
  records, 2 MoSim scratch records, and 1 MoSim main long-context record.
- Reclassified the two remaining MoSim scratch records as active visible
  CoAgent-style maintenance windows by changing only WSL DB display metadata:
  `019e8358-86b4-7070-8fd6-a2b4f4d2af97` is now titled
  `MoSim｜微信网关接口`, and
  `019e3dac-de0e-7180-98ad-d7137e8a6275` is now titled
  `MoSim｜Codex 环境维护`. Rollout contents were not modified, so `codex
  resume <id>` still resumes the original histories. Backup and manifest:
  `/home/linux/.codex/backups/wsl-retitle-two-visible-departments-20260605-1555/`
  and
  `Results/codex_history_audit/wsl_retitle_two_visible_departments_20260605-1555_manifest.json`.
  Latest buckets now show 12 CoAgent visible records and 0 MoSim scratch
  records. Superseded by the 2026-06-05 user correction above: the
  `019e8358-86b4-7070-8fd6-a2b4f4d2af97` record is a WeChat
  intervention/event conversation, not the dedicated gateway operations owner.
- Per user review, deleted archived DH scratch record
  `019e0589-1fef-7d92-9b56-09e238ad8840` (`你好`, interrupted, no project
  content). Backup and manifest:
  `/home/linux/.codex/backups/wsl-delete-dh-scratch-20260605-1605/` and
  `Results/codex_history_audit/wsl_delete_dh_scratch_20260605-1605_manifest.json`.
  Post-check: SQLite `integrity_check=ok`, `quick_check=ok`, 291 DB rows,
  107 active, 184 archived, target ID absent, and no rollout file remains for
  that ID. DH review bucket now has 7 records.
- Per user review, reclassified archived GPU_Test/CUDA record
  `019e1156-f22f-7823-9e83-96f1506152e0` into DH by unarchiving it, moving its
  rollout to active `sessions/2026/05/10/`, setting cwd to
  `/mnt/c/Users/HP/Desktop/DH`, and retitling it
  `DH｜GPU_Test CUDA/cuFFT 初始化错误码 5 排查`. Deleted low-value MoSim records
  `019e631d-8164-72e3-aac5-4ee3d91e462e` and
  `019e7373-37f4-75e1-9780-e1519a489715`. Backup and manifest:
  `/home/linux/.codex/backups/wsl-reclass-dh-delete-two-mosim-20260605-1615/`
  and
  `Results/codex_history_audit/wsl_reclass_dh_delete_two_mosim_20260605-1615_manifest.json`.
  Post-check: SQLite `integrity_check=ok`, `quick_check=ok`, 289 DB rows,
  107 active, 182 archived, deleted IDs absent, and no rollout files remain for
  deleted IDs. Latest keep buckets now show 1 MoSim user-work record, 1 MoSim
  main long-context record, and 8 DH records.
- Normalized final WSL cleanup grouping by cwd metadata only: moved the two
  non-GPU other-project records (`dog` image and `JIT-Fine` conda setup) into
  `JIT-Fine`, moved the four `gpu_test` records into `DH`, and normalized all
  MoSim/CoAgent visible records to `/mnt/c/Users/HP/Desktop/MoSim`. Rollout
  contents were not modified. Backup and manifest:
  `/home/linux/.codex/backups/wsl-final-group-cwd-normalize-20260605-1625/`
  and
  `Results/codex_history_audit/wsl_final_group_cwd_normalize_20260605-1625_manifest.json`.
  Latest final buckets: 261 subagent/delegated delete candidates, 14 MoSim
  records, 12 DH records, and 2 JIT-Fine records.
- Per user request, deleted all WSL Codex subagent/delegated history records
  from `/home/linux/.codex`: 261 thread rows removed, 256 spawn-edge rows
  removed, 184 matching `session_index.jsonl` lines removed, and 261 rollout
  files removed from active/archived session folders. Full backup and manifest:
  `/home/linux/.codex/backups/wsl-delete-all-subagents-20260605-175855/` and
  `Results/codex_history_audit/wsl_delete_all_subagents_20260605-175855_manifest.json`.
  Post-check: SQLite `integrity_check=ok`, `quick_check=ok`, 28 DB rows, 28
  active, 0 archived, 0 subagent rows, 0 spawn edges, 0 DB rows missing rollout,
  and 0 remaining rollout files for the deleted target IDs. Corrected four
  remaining `dh-deploy`/`dh-master` DH histories to the DH bucket with backup
  `/home/linux/.codex/backups/wsl-normalize-dh-four-after-subagent-delete-20260605-180114/`.
  Latest WSL buckets are now 14 MoSim, 12 DH, and 2 JIT-Fine records. One
  known file-only rollout orphan remains:
  `019e01a6-3930-73e3-a692-066cf92071d2`.
- Per user review, deleted the remaining WSL file-only rollout orphan
  `019e01a6-3930-73e3-a692-066cf92071d2`, which was a
  `codex-auto-review` guardian/subagent approval log rather than a normal
  user-visible conversation. Backup and manifest:
  `/home/linux/.codex/backups/wsl-delete-file-only-guardian-orphan-20260605-181434/`
  and
  `Results/codex_history_audit/wsl_delete_file_only_guardian_orphan_20260605-181434_manifest.json`.
  Final WSL post-check: SQLite `integrity_check=ok`, `quick_check=ok`, 28 DB
  rows, 28 active, 0 archived, 0 subagent rows, 0 spawn edges, 0 DB rows
  missing rollout, 0 file-only rollout IDs, and buckets remain 14 MoSim, 12
  DH, and 2 JIT-Fine.
- Deleted the old Windows Codex quarantine directory
  `C:\Users\HP\.codex.quarantine-2026060` after confirming the active
  `C:\Users\HP\.codex` directory was empty and the quarantine lived outside
  the active Codex home. Reinstalled Windows Codex CLI through nvm/npm:
  `C:\nvm4w\nodejs\npm.cmd install -g @openai/codex@0.137.0`. Verification:
  `where codex` resolves to `C:\nvm4w\nodejs\codex` and
  `C:\nvm4w\nodejs\codex.cmd`, `codex --version` reports
  `codex-cli 0.137.0`, and npm global list shows `@openai/codex@0.137.0`.
- Migrated the cleaned WSL Codex source into the fresh Windows Codex home.
  Backed up the pre-migration Windows home to
  `C:\Users\HP\.codex.pre-wsl-migration-20260605-183845`, then copied
  `auth.json`, `config.toml`, `state_5.sqlite`, `session_index.jsonl`,
  `history.jsonl`, `skills/`, and the cleaned `sessions/` tree from
  `/home/linux/.codex` into `C:\Users\HP\.codex`. Converted project cwd and
  rollout paths from WSL paths to Windows paths and converted WSL MCP wrapper
  commands to `wsl.exe -d Ubuntu -- ...` form. Migration manifest:
  `Results/codex_history_audit/windows_codex_migration_from_wsl_20260605-183937_manifest.json`.
  Verification: Windows `codex doctor --summary --ascii --no-color` now has
  0 failures, auth is configured, config loads, 9 MCP servers are configured,
  thread DB and rollout inventory agree, and the Windows history DB contains
  28 active rows, 0 archived rows, and 0 subagent rows. Buckets are 14
  `C:\Users\HP\Desktop\MoSim`, 12 `C:\Users\HP\Desktop\DH`, and 2
  `C:\Users\HP\Desktop\JIT-Fine`. Latest audit summary:
  `Results/codex_history_audit/windows_codex_migration_latest.md`.
- Corrected the Windows history migration after an interactive `codex` launch
  reported local database damage: `migration 1 was previously applied but has
  been modified`. Root cause was copying the WSL `state_5.sqlite` file
  wholesale into Windows, which preserved WSL `_sqlx_migrations` checksums that
  do not match the Windows CLI migration bundle. Do not repair this by letting
  Codex wipe/rebuild history automatically. Fixed by restoring the
  Windows-native empty `state_5.sqlite` from
  `C:\Users\HP\.codex.pre-wsl-migration-20260605-183845` and importing only
  the 28 cleaned `threads` rows with Windows cwd/rollout paths. The bad DB
  family was backed up to
  `C:\Users\HP\.codex.bad-wsl-db-before-native-rebuild-20260605-191614`; fix
  manifest:
  `Results/codex_history_audit/windows_codex_native_db_rebuild_20260605-191614_manifest.json`.
  Recheck: `codex doctor --summary --ascii --no-color` has 0 failures,
  `codex --help` runs normally, DB/rollout parity is 28 files, 0 file-only,
  0 missing, and buckets remain 14 MoSim, 12 DH, 2 JIT-Fine.
- User clarified the operating boundary: from this point forward the active
  Codex environment is Windows-native `C:\Users\HP\.codex`. WSL is not a
  second Codex home or sync peer; it is only a runtime subsystem invoked from
  Windows, for example via `wsl.exe -d Ubuntu-22.04 -- ...`, when Linux-native
  tools are required. Do not continue treating `/home/linux/.codex` as an
  active environment after migration; use it only as a reviewed source archive
  if the user explicitly asks.
- Repaired Windows-native MCP/skills/plugins after the first Windows Codex
  launch reported MCP startup failures. Root cause for the WSL-backed MCPs was
  the wrong WSL distribution name; this machine's active distro is
  `Ubuntu-22.04`, not `Ubuntu`. Rewrote Windows `config.toml` MCP commands to
  use `wsl.exe -d Ubuntu-22.04 -- ...`. Verified initialize handshakes for the
  8 startup MCP servers: `filesystem`, `git`, `mosim-epic`, `mosim-unreal`,
  `ros-mcp`, `syslab`, `sysplorer`, and `windows-mcp`. Removed startup
  `blender` MCP because it requires a running Blender addon/socket and did not
  complete initialize in the startup probe; keep Blender MCP on-demand rather
  than default startup. Cleaned stale plugin config by removing
  `[marketplaces.local]` and `[plugins."codex-session-tools@local"]`, because
  no supported Windows marketplace manifest existed. Verification:
  `codex doctor --summary --ascii --no-color` has 0 failures, `codex mcp list`
  shows 8 enabled MCP servers, `codex plugin list` returns "No marketplace
  plugins found" without error, and Windows `.codex/skills` has 51 skill files
  including 5 `.system` skills and 46 non-system skills. Audit summary:
  `Results/codex_history_audit/windows_codex_mcp_skills_plugins_latest.md`.
- Added Windows terminal usability fixes for Codex TUI after the user reported
  Backspace rendering as spaces / cursor drift in the classic Windows
  PowerShell 5.1 console. Current host was PowerShell 5.1 with `gb2312`
  console encoding and no `WT_SESSION`, so raw-mode TUI behavior is unreliable
  in that existing console window. Set Windows default terminal registry values
  under `HKCU\Console\%%Startup` to Windows Terminal, added a UTF-8 profile
  block to
  `C:\Users\HP\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`,
  and created two user PATH launchers:
  `C:\Users\HP\.local\bin\codex-wt.cmd` opens Codex inside Windows Terminal
  with UTF-8 setup, while `C:\Users\HP\.local\bin\codex-inline.cmd` runs
  `codex --no-alt-screen` as a fallback for old consoles. Existing already-open
  PowerShell windows keep their old console host; open a new terminal or run
  the launcher to use the fix.
- Per user request, re-added the `blender` MCP server to the Windows-native
  `C:\Users\HP\.codex\config.toml` even though Blender may fail unless the
  Blender addon/socket is running. The server uses `wsl.exe -d Ubuntu -- bash
  -lc "cd /mnt/c/Users/HP/Desktop/MoSim && exec
  /mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/Blender-MCP/wrappers/blender-mcp.sh"`
  with `BLENDER_HOST=172.17.48.1` and `BLENDER_PORT=9876`. Backed up the
  previous config as
  `C:\Users\HP\.codex\config.toml.bak-before-blender-mcp-20260605-192526`,
  then corrected the WSL distribution name to this machine's
  `Ubuntu-22.04` with backup
  `C:\Users\HP\.codex\config.toml.bak-blender-distro-fix-20260605-192848`.
  Verification: `codex doctor --summary --ascii --no-color` still loads config
  successfully, reports auth configured, 10 MCP servers configured, 28 active
  rollout files / thread DB inventory aligned, and 0 failures. The remaining
  warnings are expected local notes: 2.80 GB rollouts, unrestricted
  filesystem/network, and update configuration warning.
- Re-audited the Windows-native Codex configuration for WSL bridge residue
  after the user confirmed future use should be through the Windows-native
  Codex App. Current `C:\Users\HP\.codex\config.toml` has no `wsl.exe`,
  `/mnt/c`, `/home/linux`, `\\wsl`, or `wsl.localhost` launcher/path entries.
  `codex mcp list` shows Windows-native commands for the active MCP set:
  MWORKS Sysplorer/Syslab native Windows executables, project `.cmd` wrappers
  for Windows/ROS/Unreal/Epic/Blender MCPs, `uvx.exe` for git, and the bundled
  Codex `node_repl.exe`. The project wrapper `.cmd` files also have no WSL
  bridge calls. `codex doctor --summary --ascii --no-color` reports 0 failures,
  auth configured, DB/rollout inventory aligned, and 9 enabled MCP servers at
  startup. The only WSL mentions found under copied skills are documentation
  text describing WSL as a runtime lane, not active Codex launcher config.
  `codex-wt` from the old window.
- Refined the PowerShell-only Codex launcher after the user clarified they
  only want to type `codex` in PowerShell. PowerShell resolves `codex` to
  `C:\nvm4w\nodejs\codex.ps1` before `codex.cmd`, and that npm-generated
  PowerShell shim is the problematic path for Codex TUI in classic conhost.
  Backed up the shim to
  `C:\nvm4w\nodejs\codex.ps1.bak-before-wt-autolaunch-20260605` and patched
  `codex.ps1` so plain `codex` from a non-Windows-Terminal PowerShell opens a
  Windows Terminal tab running Codex with UTF-8/TERM setup; argument commands
  such as `codex --version`, `codex doctor`, and `codex mcp list` still pass
  through normally. Also updated the user PowerShell profile function with the
  same behavior, so new PowerShell sessions resolve `codex` to the compatible
  launcher first. If an already-open PowerShell session still has the old
  function cached, run `. $PROFILE` once or open a new PowerShell window.

## 2026-06-05 CST - Codex History Cleanup Baseline

- Current cleanup baseline is Windows `C:\Users\HP\.codex`, not WSL. Latest
  read-only audit: Windows state DB has 264 rows, all active, 231 active
  subagent rows, 32 active user rows, 1 null `thread_source` row, SQLite
  `integrity_check=ok`, `quick_check=ok`, and one DB row pointing to a missing
  rollout file (`019e3dac-de0e-7180-98ad-d7137e8a6275`). Windows
  `archived_session_files=0`.
- WSL `/home/linux/.codex` is now a legacy/reference store for this cleanup
  round: 308 DB rows, 112 active, 196 archived, 6 legacy
  `thread_source=vscode` rows, 14 null-source rows, and 309 rollout file IDs.
  Do not automatically resync WSL into Windows while the user is cleaning
  Codex App/VSCode history, or deleted/hidden records will reappear.
- The previous Codex++ script location under AppData/Roaming is no longer
  present in the current Windows AppData scan. Treat App/VSCode visible
  history as the Windows Codex state plus their own frontend caches; if the UI
  disagrees with the DB, diagnose that frontend separately instead of editing
  WSL history.

## 2026-06-05 CST - Windows Codex CLI Runtime Consolidated

- Consolidated the Windows command-line Codex environment to one canonical
  CLI: npm global `@openai/codex@0.137.0` under nvm-managed Node
  `C:\nvm4w\nodejs`. `where codex` now resolves first to
  `C:\nvm4w\nodejs\codex` and `C:\nvm4w\nodejs\codex.cmd`; `codex --version`
  reports `codex-cli 0.137.0`.
- Removed `C:\Users\HP\.codex\bin` from the Windows user `Path` and moved its
  legacy CLI files to
  `C:\Users\HP\.codex\bin\disabled-legacy-cli-20260605`. This prevents the
  older/manual `.codex\bin` launcher from becoming a second active CLI
  environment.
- Codex App and VSCode Codex may still ship and launch their own private
  `codex.exe` binaries internally. Treat those as App/plugin runtimes only,
  not as the user's shell CLI. The shared state/config home remains
  `C:\Users\HP\.codex`.

## 2026-06-05 CST - Windows Codex CLI Node Toolchain Installed

- Installed `nvm-windows` 1.2.2 with `winget` and installed/activated Node LTS
  through nvm. Current verified toolchain:
  `C:\Users\HP\AppData\Local\nvm\nvm.exe`, `C:\nvm4w\nodejs\node.exe`
  `v24.16.0`, `npm`/`npx` `11.13.0`.
- Reordered the Windows user `Path` so `%NVM_HOME%` and `%NVM_SYMLINK%` take
  precedence over `C:\Users\HP\AppData\Local\Microsoft\WindowsApps`; this
  prevents `node` from resolving to the Codex App packaged WindowsApps
  `node.exe`, which failed with `Access is denied`.
- Synchronized the local `codex` CLI under `C:\Users\HP\.codex\bin` from the
  current App cache
  `C:\Users\HP\AppData\Local\OpenAI\Codex\bin\fb2111b91430cb17`, updating
  `codex --version` from `0.136.0-alpha.2` to `0.137.0-alpha.4`. Old CLI
  binaries were backed up to
  `C:\Users\HP\.codex\backups\codex-cli-bin-before-20260605-1245`.
- Verification passed: `node --version`, `npm --version`, `npx --version`,
  `nvm version`, `codex --version`, and `codex doctor --summary --ascii
  --no-color`. `doctor` reports healthy config/auth/MCP and only the known 3
  residual thread/rollout issues.

## 2026-06-05 CST - Current Codex App Thread Visibility Rechecked

- Rechecked the active Windows Codex App conversation after the user reported
  that App replies did not appear under MoSim or chat history. The current
  thread is present and healthy in `C:\Users\HP\.codex\state_5.sqlite`:
  `019e8181-6653-73b3-9685-f5bc9a24b947`, `archived=0`,
  `has_user_event=1`, and rollout file exists under
  `C:\Users\HP\.codex\sessions\2026\06\01\...`.
- Current MoSim history index state: 266 total rows, 210 MoSim rows, all 210
  using the extended Windows cwd `\\?\C:\Users\HP\Desktop\MoSim`, and 0 using
  the plain `C:\Users\HP\Desktop\MoSim` cwd. Do not normalize back to the
  plain path for the current App/VSCode runtime.
- Important UI interpretation: the active App conversation remains one thread
  whose sidebar title/preview is the first 2026-06-01 prompt
  `把windows环境下也安装好codex cli...`. New replies append to that rollout
  and may not create a new history row or update the visible title to the
  latest message.
- `codex doctor` still reports 3 residual thread/rollout issues: one missing
  active row, two stale rows, and one duplicate rollout thread id sample. These
  do not include the current App thread. Per user instruction, do not restore
  from `C:\Users\HP\.codex\backups` or reintroduce manually deleted histories.
- Reusable route documented in
  `Docs/Workflows/debug_mcp.md#45-vscode-codex-shows-dh-histories-but-mosim-is-missing`.

## 2026-06-05 CST - Windows Primary Runtime Documentation Alignment

- Updated current project operating rules to reflect the completed Windows-side
  Codex migration: the primary project conversation/config/history is now the
  Windows-native VSCode/Codex route under `C:\Users\HP\.codex`, not the older
  WSL-backed VSCode session.
- Preserved the robotics runtime boundary: ROS2, RViz2, FAST-LIO-family,
  rosbridge, and Linux-native robotics tools remain WSL2 Ubuntu 22.04 runtime
  work. Do not move those runtime claims to Windows PowerShell unless a future
  workflow explicitly approves a Windows ROS route.
- Files updated: `AGENTS.md`,
  `Docs/Workflows/debug_mcp.md`, and
  `Docs/Workflows/new_conversation_context.md`. Historical PROGRESS entries
  describing the earlier WSL-primary policy remain as history only.
- Added a `Historical Context Coverage` section to
  `Docs/Workflows/new_conversation_context.md` so fresh conversations see the
  session-memory migration status immediately: the currently identified
  important topic set is recoverable through the cache/round-3/completion audit
  files, but any newly surfaced old claim must still go through
  `Docs/Workflows/session_memory_migration.md` before becoming project truth.

## 2026-06-05 CST - VSCode Codex MoSim History Visibility Repair

- Repaired the Windows-native VSCode Codex history index under
  `C:\Users\HP\.codex` after the plugin showed about 50 DH histories and hid
  most MoSim histories. Stopped only the VSCode Codex app-server, backed up the
  current DB family to
  `C:\Users\HP\.codex\backups\pre-mosim-visibility-repair-20260605-104256`,
  and merged only MoSim thread rows from
  `C:\Users\HP\.codex\backups\latest-wsl-sync-20260604-225318`.
- Post-check: SQLite `integrity_check=ok`, 271 total threads,
  215 active MoSim rows at `C:\Users\HP\Desktop\MoSim`, 0 archived MoSim rows,
  and 52 DH-like rows preserved. Copied 186 missing MoSim rollout files, kept
  22 existing rollouts, and recorded 7 MoSim rows whose rollout files were also
  missing from the available backup.
- Reusable recovery route is documented in
  `Docs/Workflows/debug_mcp.md#45-vscode-codex-shows-dh-histories-but-mosim-is-missing`.

## 2026-06-05 CST - Windows Codex Startup Warning Repair

- Fixed Windows Codex startup warnings in `C:\Users\HP\.codex` after backing up
  config and affected files to
  `C:\Users\HP\.codex\backups\startup-warning-fix-20260605-100846`.
- Root causes and fixes:
  - `syslab-code-style`, `syslab-digital-filter-design`, and `syslab-testing`
    skill frontmatter was valid text but had a UTF-8 BOM before `---`; rewrote
    those `SKILL.md` files as UTF-8 without BOM.
  - `openai-api-key-local-confirmation` came from the OpenAI Developers plugin
    `.mcp.json` and used bare `node`; Windows Codex startup did not have
    `node.exe` on PATH. Replaced it in all observed OpenAI Developers plugin
    copies with
    `C:\Users\HP\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`.
  - `git` MCP had no explicit timeout. Added `startup_timeout_sec = 120` and
    `tool_timeout_sec = 300` under `[mcp_servers.git]`.
  - The `local` marketplace source pointed at `C:\Users\HP\.codex`, which is
    not a marketplace root. Added
    `C:\Users\HP\.codex\local-marketplace\.agents\plugins\marketplace.json`
    for `codex-session-tools@local` and repointed `[marketplaces.local]`.
  - Windows-mode Blender MCP now uses the project Windows wrapper
    `Docs\Skills\Blender-MCP\wrappers\blender-mcp.cmd` instead of the WSL
    wrapper to avoid slow `wsl.exe` startup in Windows-native Codex sessions.
- Verification: `codex plugin marketplace list`, `codex plugin list`,
  `codex mcp get blender`, and `codex doctor --summary --ascii --no-color`
  all load successfully. `doctor` still reports the known Windows Codex
  thread/rollout mismatch; that is the separate chat-history visibility repair
  task, not an MCP/skill startup failure.
- Follow-up MCP inventory audit: Windows config had an unintended duplicate
  `[mcp_servers.sysplorer_mcp]` entry pointing at the same Sysplorer MCP
  executable as `[mcp_servers.sysplorer]`. This was not present in the WSL
  source config. Removed the duplicate after backing up to
  `C:\Users\HP\.codex\backups\mcp-dedupe-20260605-102326`; `codex doctor`
  now reports `mcp 9 server (9 stdio)`.
- `node_repl` is not a project MCP entry in current `config.toml`; it is an
  internal OpenAI bundled browser/native-host JavaScript channel referenced by
  Browser/Chrome/Computer Use plugin files. The currently configured project
  MCP servers do not include `[mcp_servers.node_repl]`.
- CC Switch keeps a separate MCP registry in
  `C:\Users\HP\.cc-switch\cc-switch.db`, so it can still show stale entries
  after `C:\Users\HP\.codex\config.toml` is fixed. Stopped the running
  `cc-switch.exe`, backed up the database to
  `C:\Users\HP\.cc-switch\backups\cc-switch-mcp-cleanup-20260605-103427.db`,
  removed non-project `node_repl`, and synced the CC Switch `blender` row to
  the Windows `.cmd` wrapper. Follow-up correction: `sysplorer_mcp` is not a
  separate downloaded Sysplorer MCP; it is another client registration for the
  same MWORKS-installed Sysplorer MCP under
  `D:\Program Files\MWORKS\Sysplorer 2026a\Tools\sysplorer_mcp`. Restored that
  row in CC Switch with `enabled_codex=0` and `enabled_opencode=1`, while
  keeping Codex on the canonical `sysplorer` row. Codex CLI still shows 10 MCP
  entries because the OpenAI Developers plugin contributes
  `openai-api-key-local-confirmation` outside CC Switch's project MCP table.
- WSL-vs-Windows MCP route audit: WSL `syslab_mcp.sh` and
  `sysplorer_mcp.sh` are wrappers that still launch Windows MWORKS binaries
  through `/init ... cmd.exe`; they are not separate Linux MCP server builds.
  Windows Codex can use the same installed MWORKS MCPs directly. Synced Windows
  `syslab` args to WSL behavior by adding
  `--julia-root C:\Users\Public\TongYuan\julia-1.10.10` and
  `--syslab-display-mode nodesktop` in both `C:\Users\HP\.codex\config.toml`
  and the CC Switch `syslab` row. No new Syslab/Sysplorer MCP server download
  is needed.
- Codex 0.136 uses deferred tool discovery in this environment. The visible
  conversation may initially show only `tool_search`; project MCP tools are
  exposed after a targeted `tool_search` query. Verified discovery exposes
  `mcp__mosim_epic`, `mcp__mosim_unreal`, `mcp__windows_mcp`, `mcp__sysplorer`,
  and `mcp__syslab`. Any stale `mcp__sysplorer_mcp` namespace visible in the
  current already-started conversation is a pre-repair tool-surface cache and
  should disappear after restarting VSCode Codex/app-server.

## 2026-06-05 CST - Windows Codex History Unarchived For Manual Review

- After user approval, cleaned the Windows Codex App history surface under
  `C:\Users\HP\.codex`. Stopped Codex App/app-server processes first, backed
  up the DB family and affected rollout files, and then modified only the
  Codex history store.
- Deleted the one pre-existing archived user thread
  `019ddf78-e5f7-7b02-bcd9-35ddd016512e` (`你好`). Archived all 262 DB-marked
  `thread_source=subagent` threads. A later user correction clarified that
  CoAgent-related records must remain visible, so the 20 CoAgent department,
  scoped task packet, candidate worker/test, and visibility-test threads that
  had been temporarily archived were restored to active history.
- Backups and manifests:
  `C:\Users\HP\.codex\backups\archive-subagents-delete-archived-20260605-003122\manifest.json`,
  `C:\Users\HP\.codex\backups\archive-agentlike-user-threads-20260605-003515\manifest.json`,
  and
  `C:\Users\HP\.codex\backups\restore-coagent-visible-threads-20260605-004050\manifest.json`.
  Post-check: SQLite `integrity_check=ok`, `quick_check=ok`, 304 total rows,
  42 active rows/files, 262 archived rows/files, 20 active CoAgent-like rows,
  0 archived CoAgent-like rows, and 0 active subagent rows.
- Known residual not changed by this request: active non-subagent dog-image
  thread `019e1aa8-5855-7c83-9db9-a97f1e1050e5` still points to a missing
  rollout file. Leave it for a separate cleanup decision.
- Because Codex App does not expose archived conversations for manual review,
  generated project-local review sheets for the 262 archived subagent records:
  `Results/codex_history_audit/archived_subagent_fine_group_review_latest.md`
  groups them into 11 review groups, and
  `Results/codex_history_audit/archived_subagent_group_review_latest.md`
  keeps the broader 34-group view. This grouping pass was read-only against
  Windows `.codex`; it did not delete, restore, or move any Codex history.
- User then chose to cancel all archive state and review one by one in Codex
  App. Stopped Codex App/app-server again, backed up to
  `C:\Users\HP\.codex\backups\unarchive-all-for-manual-review-20260605-005827`,
  and unarchived all 262 currently archived subagent records. Post-check:
  SQLite `integrity_check=ok`, `quick_check=ok`, 304 active DB rows, 0 archived
  DB rows, 262 active subagent rows, 0 archived rollout files. File-level
  residual: seven active rows point to missing rollout files
  (`019e0589-1fef-7d92-9b56-09e238ad8840`,
  `019e1aa8-5855-7c83-9db9-a97f1e1050e5`,
  `019e1156-f22f-7823-9e83-96f1506152e0`,
  `019e078b-9fcf-7650-9d05-205ac11d2b41`,
  `019e02b8-5613-74b1-8edb-1b01b8943b7e`,
  `019df629-ebd2-78d2-a031-b32e79d0ebbf`,
  `019de2ae-24e0-7d93-b2f7-bc85d3cafc85`).
- When the user still could not see restored records in Codex App, verified the
  Windows DB already had 304 active rows and 262 active subagent rows. The
  remaining visibility blocker was Codex++ frontend cache/filtering:
  `market-codex-list-pagebuster.js` still used localStorage archived/hidden
  snapshots and internal-thread filtering. Backed up the script as
  `market-codex-list-pagebuster.js.bak-20260605-011944-unarchived-subagents-visible`
  and
  `market-codex-list-pagebuster.js.bak-20260605-012023-fix-keep-subagents`,
  bumped its storage version to
  `2026-06-05-unarchived-subagents-visible-v2`, and confirmed Node syntax
  check passes. Reloading/restarting Codex App should clear stale
  `__codexListPagebusterArchivedIds` / hidden snapshots and let active
  subagent rows appear.
- Later environment audit showed the Codex history state is still not clean
  enough for blind deletion. Current Windows `C:\Users\HP\.codex` DB has 264
  active rows, 0 archived rows, 231 active subagent rows, 32 user rows, and 1
  null-source row; WSL `/home/linux/.codex` DB has 308 rows with 112 active and
  196 archived. The ID sets differ: 45 WSL IDs are missing from Windows and 1
  Windows ID is missing from WSL. The previously observed 304-row Windows
  state was later changed by additional repair/cleanup batches such as
  `remove-stale-thread-indexes-20260605-1300` and
  `restore-mosim-visible-history-20260605-103856`. Also, the Codex++ user
  script path `C:\Users\HP\AppData\Roaming\Codex++\user_scripts` is not
  currently present via `$env:APPDATA`, so the earlier frontend patch may no
  longer be active. Do not perform bulk history deletion until the authority
  source is explicitly chosen: Windows App DB, WSL/VSCode DB, or a merged
  reviewed manifest.

## 2026-06-04 CST - Windows Codex History Cleanup Audit Prepared

- After the user pointed out that restoring all Windows Codex history had also
  surfaced subagent conversations in the visible App history, generated an
  audit-only cleanup package under `Results/codex_history_audit/`. No Codex
  history was deleted or modified in this pass.
- Current Windows `C:\Users\HP\.codex` audit counts from `state_5.sqlite`:
  310 total threads, 263 likely subagent/delegated records, 30 MoSim user main
  records, 15 Codex infrastructure user records, 15 DH/DHPA records, and 5
  scratch/greeting records. The proposed post-review cleanup set is
  `Results/codex_history_audit/proposed_delete_after_user_review_ids.txt`
  with 270 de-duplicated candidates; the proposed keep set is
  `Results/codex_history_audit/proposed_keep_after_user_review_ids.txt` with
  40 candidates.
- Reusable correction: future Windows Codex App history migration must not
  treat `thread_source=subagent` rollout records as normal foreground chat
  history. Keep them backed up and auditable, but hide/archive/delete them only
  after an explicit reviewed ID list.

## 2026-06-04 CST - Windows Codex Latest WSL History Increment Synced

- Rechecked WSL `/home/linux/.codex` against Windows
  `C:\Users\HP\.codex` after the user asked whether the newest chats had all
  migrated. They had not: WSL had 309 rollout IDs versus Windows 308, Windows
  was missing two WSL archived sessions, and the current MoSim infrastructure
  conversation `019e8181-6653-73b3-9685-f5bc9a24b947` plus the large original
  MoSim conversation `019e0198-a041-77f1-84d0-c5524bfd4b81` were stale on the
  Windows side.
- Stopped Windows Codex App/app-server, backed up Windows state and replaced
  rollout files under
  `C:\Users\HP\.codex\backups\latest-wsl-sync-20260604-225318`. Copied the two
  missing WSL archived rollouts, replaced 288 same-ID Windows rollouts whose
  contents differed from WSL, preserved the Windows-only thread
  `019e7c99-e807-7cc1-b1b4-2a88d012a68e`, and normalized copied rollout
  first-line metadata to Windows `cwd`, `source=cli`, and
  `thread_source=user/subagent`.
- Added the two missing archived thread rows to Windows `state_5.sqlite` from
  WSL metadata. Verification passed: `codex doctor --json` reports
  `state.rollout_db_parity=ok`, 308 active rollout files/rows, 2 archived
  rollout files/rows, 310 total rows, 0 missing rows, 0 stale rows, and
  `rollout DB sources=cli=310`. A final app-server `thread/list` for MoSim
  shows `019e8181-6653-73b3-9685-f5bc9a24b947` as the latest MoSim thread, and
  the latest active file body hash matches WSL after Windows metadata
  normalization.

## 2026-06-04 CST - Windows Codex App DH-Only History View Fixed

- User later reported the App showed about 90 conversations and all were
  DH-related. Direct app-server protocol checks still showed the backend had
  global active history: 307 unique active rows, including 212 MoSim rows and
  81 DH/DH-variant rows; explicit MoSim pagination returned 100 + 100 + 11
  rows. Evidence:
  `Results/codex_app_debug/after_exact_cwd_fix_protocol.json`.
- Fixed remaining frontend-layer risk in
  `C:\Users\HP\AppData\Roaming\Codex++\user_scripts\market-codex-list-pagebuster.js`
  after backing it up under
  `C:\Users\HP\.codex\backups\app-ui-dh-only-fix-20260604-221525`: storage
  version is now `2026-06-04-global-history-v7-explicit-mosim`, the script
  explicitly supplements `C:\Users\HP\Desktop\MoSim` even when the native App
  is scoped to another project such as DH, and subagent project history is kept
  instead of being classified as internal hidden history.
- Verification passed: bundled Node `--check` passed for the Codex++ script;
  `codex doctor --json` reports state DB/log DB integrity `ok`,
  `state.rollout_db_parity=ok`, 308 active rollout files/rows, 0 archived
  files/rows, 0 stale rows, and `rollout DB sources=cli=308`. Remaining doctor
  warnings are Windows PATH missing Git and update probe timeout, not chat
  migration problems.

## 2026-06-04 CST - Windows Codex App Full MoSim History Restored

- User still saw only 12 conversations after DB/source normalization and the
  first Codex++ script patch. Direct app-server `thread/list` proved the
  backend could see more than 12: MoSim active CLI returned 25 rows, while the
  remaining MoSim history was still under `archived_sessions` and therefore
  hidden from the normal project list.
- Fixed the durable cause by moving all 186 MoSim archived rollout files back
  to active `C:\Users\HP\.codex\sessions\YYYY\MM\DD\...` paths and updating
  `state_5.sqlite` (`archived=0`, `archived_at=NULL`, Windows-local
  `rollout_path`). Backup and move manifest:
  `C:\Users\HP\.codex\backups\unarchive-mosim-history-20260604-2242`.
- Protocol verification after the move: paged `thread/list` for
  `cwd=C:\Users\HP\Desktop\MoSim`, `archived=false`, `limit=100`,
  `sortKey=updated_at` returned 100 + 100 + 11 rows, 211 unique total; the
  archived MoSim query returned 0.
- `codex doctor --json` now reports `state DB integrity=ok`,
  `rollout DB rows=308`, `rollout DB active rows=305`,
  `rollout DB archived rows=3`, `rollout DB archive mismatches=0`, and
  `rollout DB stale rows=0`. `state.rollout_db_parity=ok`.
- Updated Codex++ `market-codex-list-pagebuster.js` again after backing it up
  as `market-codex-list-pagebuster.js.bak-20260604-2248`: storage version is
  now `2026-06-04-global-history-v6-unarchived-mosim`, and version migration
  plus manual reset clear `__codexListPagebusterArchivedIds` so the script does
  not keep hiding the 186 conversations that were just restored to active.
  Node syntax check passed.

## 2026-06-04 CST - Windows Codex App Partial 12-Thread List Earlier Fix

- User manually verified that the Windows Codex App showed only 12
  conversations after the empty-list repair. The Windows state DB was not
  missing MoSim history: `state_5.sqlite` integrity was `ok`, WSL and Windows
  both had 308 thread rows, and Windows had all 213 MoSim rows
  (27 active user, 4 archived user, 182 archived subagent).
- Fixed the Windows thread index again after backing up to
  `C:\Users\HP\.codex\backups\app-full-list-fix-20260604-211911`: every
  `threads.source` is now `cli`, every `thread_source` is `user` or
  `subagent`, and every MoSim `cwd` variant is normalized to
  `C:\Users\HP\Desktop\MoSim`.
- `codex doctor --json` now reports `state DB integrity=ok`,
  `rollout DB rows=308`, `rollout DB active rows=119`,
  `rollout DB archived rows=189`, `rollout DB sources=cli=308`, and
  `rollout DB stale rows=0`. The remaining provider route timeout is network
  reachability, not chat migration.
- The remaining 12-item symptom was a UI/list enhancement issue, not DB loss.
  Patched
  `C:\Users\HP\AppData\Roaming\Codex++\user_scripts\market-codex-list-pagebuster.js`
  after backing it up as
  `market-codex-list-pagebuster.js.bak-20260604-2129`: unresolved native
  metadata checks now keep snapshot rows instead of pruning them, project
  supplements can render even while native project lists are collapsed, and the
  localStorage version was bumped to force a fresh snapshot.

## 2026-06-04 CST - Windows Codex App Empty Chat List Fixed

- User manually verified that the Windows Codex App still showed no MoSim
  conversations after the WSL chat-history migration. The issue was not a
  missing rollout copy or only a `cwd` mismatch. Windows `logs_2.sqlite`
  showed direct App evidence:
  `state db list_threads failed: unknown thread source: vscode` for
  `thread/list` requests from `Codex Desktop`.
- Fixed the Windows-native `C:\Users\HP\.codex\state_5.sqlite` thread index
  after backing up the DB family to
  `C:\Users\HP\.codex\backups\app-list-fix-20260604-205142`: normalized all
  `threads.source` values to `cli`, preserved user/subagent semantics in
  `thread_source`, and normalized MoSim rows to
  `C:\Users\HP\Desktop\MoSim`.
- Verification: SQLite `integrity_check` and `quick_check` are `ok`; thread
  inventory is 310 rows; `rollout DB sources` is now `cli=310`; MoSim rows are
  27 active and 186 archived. `codex doctor` still has a provider route timeout
  and 2 stale non-MoSim archived rows, but no `vscode` thread source remains.
- Do not diagnose this class by repeatedly changing `cwd`. Check
  `logs_2.sqlite` for `state db list_threads failed` first, then normalize
  unsupported `threads.source` values if needed.

## 2026-06-04 CST - Windows Codex Chat History Migration Completed

- Migrated WSL Codex chat history from `/home/linux/.codex` into the
  Windows-native Codex home `C:\Users\HP\.codex` after checking the existing
  Windows history. Backup:
  `C:\Users\HP\.codex\backups\wsl-chat-migration-20260604-200448`.
- Conflict policy: WSL wins for duplicate rollout IDs, but Windows-only
  sessions are preserved. Results: 106 new active WSL rollouts copied, 9
  identical active rollouts skipped, 3 shorter Windows conflicting rollouts
  backed up and replaced, 191 archived WSL rollouts copied, and the
  Windows-only thread `019e7c99-e807-7cc1-b1b4-2a88d012a68e` preserved.
- Merged `session_index.jsonl` now has 215 unique entries. Windows
  `state_5.sqlite` was repointed to Windows-local rollout paths and then
  repaired for rollout/DB parity: 310 thread rows, 119 active files, 191
  archived rows, no Linux-style paths, and SQLite integrity `ok`.
- Verification passed for config and MCP parsing: Windows `codex doctor`
  reports `config.load=ok`, `mcp.config=ok`, `state DB integrity=ok`, and
  `rollout DB sources=cli=310` after the later App-list fix; `codex mcp list`
  shows the expected Windows/WSL MCP server set. Remaining warnings/failures
  are the provider route probe timeout and two stale old archived rows outside
  MoSim, not the MoSim chat-list migration issue.

## 2026-06-04 CST - Windows Codex MCP Mirror Completed

- Windows-native Codex config now mirrors all WSL MCP server and tool-level
  entries. Added the missing `blender` MCP through
  `C:\Windows\System32\wsl.exe -d Ubuntu-22.04 --exec
  /mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/Blender-MCP/wrappers/blender-mcp.sh`
  with the WSL `BLENDER_HOST`, `BLENDER_PORT`, and `DISABLE_TELEMETRY` values.
- Added the missing Windows-side `windows-mcp.tools.PowerShell`
  `approval_mode = "approve"` entry so the Windows MCP approval boundary
  matches WSL.
- Verification passed: Windows `codex mcp list` shows `blender`, `filesystem`,
  `git`, `mosim-epic`, `mosim-unreal`, `ros-mcp`, `syslab`, `sysplorer`,
  `windows-mcp`, plus Codex App's extra `node_repl`; table comparison reports
  no WSL MCP table paths missing from Windows.

## 2026-06-04 CST - CoAgent WeChat Completion Notification Boundary

- Current multi-dialog scheduling boundary is now explicit: visible Codex
  conversations are manually created, opened, switched, and tasked by the user
  until a later approved task proves reliable visible-thread dispatch again.
  CoAgent/main-agent responsibility is packet preparation, result import,
  ledger/status updates, integration, and notification.
- Added automatic WeChat completion notification support for accepted
  `canonical_status=completed` result packets. `CoAgent/result_router` now
  generates `completion_notification` packets under
  `Results/agent_packets/notifications/` when `--notify-weixin` is used, and
  routes them through `CoAgent/gateway/cc_connect_weixin.py`.
- Human-review/blocker notifications remain supported through
  `blocker_notification`. Completion notification is required even when no
  human review is needed, because WeChat is the unified out-of-band task
  completion signal.
- Verification passed:
  `python3 CoAgent/tests/test_gateway_weixin.py`,
  `python3 CoAgent/tests/test_result_router.py`, and
  `python3 -m py_compile CoAgent/gateway/cc_connect_weixin.py CoAgent/result_router/result_router.py`.
- A real completion notification packet was generated through the result
  router:
  `Results/agent_packets/notifications/COAGENT-WEIXIN-COMPLETION-RULE-20260604.weixin_notification.json`.
  Actual WeChat sending failed after the bounded restart/retry with
  `read unix ... api.sock: read: connection reset by peer`; recovery evidence:
  `Results/coagent_gateway/recovery/weixin_recovery_required_20260604_195248.json`.
  Treat this as cc-connect runtime/session degradation, not as a completion
  packet contract failure. Do not retry in a tight loop.
- Git commit for this patch is still pending because another Git owner/process
  is holding `.git/index.lock` while running
  `git -c core.hooksPath=/dev/null commit -m docs: cache cli app session details`.
  Do not kill or overwrite that process from the main thread.

## 2026-06-04 CST - Long Conversation Memory Migration Supplemental Routing

- Added `Docs/Cache/session_memory_migration/02_round2_review/round2_core_competition_report_docs_memory_20260604.md` as a cache-only recovery entry for historical core competition work that was already represented in formal docs/results but needed clearer fresh-conversation routing.
- Updated `Docs/Index/project_work_memory_index.md` with explicit entries for simulation report/evidence audit, official MWORKS docs conversion, and test/quality gates.
- Corrected stale documentation-entry paths from `Docs/Mworks/` to the current `Docs/MworksDocs/` tree in `Docs/Index/doc_index.md`, `Docs/Index/api_index.md`, `Docs/Index/mathworks_to_mworks_migration.md`, `Docs/Workflows/translate_mathworks_to_mworks.md`, and `Docs/Workflows/pre_submit_check.md`. `Docs/MinerU/mineru_precise_api.md` remains the current MinerU API path.
- This is a routing/memory patch only. It does not promote new controller, scene, FAST-LIO, parameter, codegen, or CoAgent runtime claims.

> Current project memory for agent recovery. Keep this file short. Durable
> rules stay in `AGENTS.md`; detailed procedures stay in `Docs/Workflows/`.

## Current Focus

- 2026-06-04 CST new conversation recovery context: created
  `Docs/Workflows/new_conversation_context.md` as the short startup document
  for new Codex conversations. Use it before reading the long `PROGRESS.md` or
  any raw session transcript. It records only current effective decisions,
  current Sunray150 geometry/dynamics boundaries, RflySim local source entry,
  UE/ROS/FAST-LIO authority split, and rejected historical routes. The old
  large chat transcript remains non-authoritative; newly surfaced historical
  claims must still go through `Docs/Workflows/session_memory_migration.md`
  before formal promotion.

- 2026-06-04 CST full project work-memory index: added
  `Docs/Index/project_work_memory_index.md` so a new conversation can recover
  the broader history without reading the 2 GB session file. The index routes
  CoAgent, Codex/App infrastructure, WeChat, Git/DevOps, external-reference
  learning, Unreal MCP/Fab scene tooling, S0/S1 renderer history, Factory and
  Derelict scene gates, UE/ROS/FAST-LIO, MWORKS evidence/codegen/SIL,
  Sunray150 geometry/materials, RflySim dynamics reference, and PX4/Sunray
  behavior contracts to their current source docs and evidence. It also
  records rejected/superseded routes so old failed iterations are not revived
  as current truth.

- 2026-06-04 CST Sunray150 geometry parameter migration: user-reviewed
  DAE/Blender assembly geometry has been extracted to
  `Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json`
  and applied only to high-confidence geometry fields. MWORKS
  `Dronefixed1..4`, Sunray `sunray150_with_mid360.sdf/.sdf.jinja` rotor poses,
  front/down camera candidates, conservative collision box, and the UE Blender
  asset rotor-center script now use the DAE-derived rotor centers:
  rotor 0 `(0.053745,-0.05374,-0.014052)`, rotor 1
  `(-0.053761,0.05376,-0.014052)`, rotor 2
  `(0.053746,0.053759,-0.014052)`, rotor 3
  `(-0.053761,-0.053739,-0.014052)` m. Mass, inertia, thrust/motor constants,
  controller gains, and timing were not changed. MID-360 remains held for
  review as separate concepts: mechanical mount pose, point-cloud origin,
  built-in IMU position, FAST-LIO extrinsic, and Sunray/Gazebo ray-sensor pose.
  Official Livox Mid-360 manual evidence gives the IMU position as
  `(11.0,23.29,-44.12) mm` in the point-cloud coordinate system, which matches
  the local FAST-LIO convention `extrinsic_T=[-0.011,-0.02329,0.04412]` for
  LiDAR pose in IMU body frame when axes are aligned. Do not replace SDF
  MID-360 pose or FAST-LIO extrinsics from DAE mount geometry without a
  separate coordinate-frame review.

- 2026-06-04 CST long-session memory migration for
  `MoSim|四旋翼无人机仿真系统` is recoverable and remains cache-first. Durable
  workflow: `Docs/Workflows/session_memory_migration.md`; ledger row:
  `SESSION-MEMORY-MIGRATION-20260604`; coverage matrix:
  `Docs/Cache/session_memory_migration/00_index/coverage_matrix_20260604.md`; round-3
  gate: `Docs/Cache/session_memory_migration/03_round3_disposition/round3_promotion_rejection_map_20260604.md`.
  The currently identified topic set now has round-1 capture and topic-specific
  round-2 evidence review, including infrastructure/session policy, Sunray150
  asset history, UE/ROS/FAST-LIO, MWORKS controller evidence, MWORKS codegen/SIL,
  ROS2 runtime setup, scene-source/renderer state, parameter identification,
  CoAgent operating boundaries, and external-reference lessons. Round 3 has
  started with one narrow parameter-provenance clarification in
  `Docs/Workflows/identify_quadrotor_parameters.md`: accepted takeoff mass is
  only a provenance-labeled input for the exact flight configuration, not a
  promotion of inertia, rotor geometry, motor coefficients, drag, controller
  evidence, or the full parameter set to `identified`. No numeric parameter was
  promoted, and no project-local identification bundle was found in that round.
  MWORKS codegen/SIL has also completed round-3 migration review with no
  formal patch: `Docs/Workflows/mworks_codegen_controller_runtime.md` and
  `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md` already record the
  `GenerateModelCode` route, PID-demo-only compile/runtime/SIL smoke evidence,
  timestamp-shift limitation, and the still-open per-controller/time-varying
  SIL gate. No newer target-controller SIL artifact was found under
  `Results/codegen_probe` in that pass.
  UE scene-source/renderer state has a round-3 disambiguation patch in
  `Docs/Workflows/unreal_renderer.md`: current answers must separate registry
  policy primary, active renderer content links, manual-review packet target,
  Gate-B/runtime readiness, smoke evidence, and final scene acceptance. The
  2026-06-04 pass found registry policy primary
  `local_derelictcorridormegascans` while active content links point to
  `local_factoryenvironmentcollect`; no scene was promoted to final product
  acceptance.
  ROS2/FAST-LIO runtime setup has a round-3 source-priority patch in
  `Docs/Workflows/ros2_runtime_setup.md`: 2026-06-01 apt/key and rosbridge
  notes are prior infrastructure evidence unless live-checked; current
  FAST-LIO answers must read the latest route-specific `*_CURRENT` gate and
  linked runtime directory first; old `PROGRESS.md` mentions of
  `open_mapping_rviz_ros2.sh` or `run_fastlio_rviz_replay_ros2.sh` are
  historical and should not override the current command list in the workflow.
  Factory Gate B currently opens manual UE/RViz review only and does not prove
  final controller integration, planner performance, or product acceptance.
  CoAgent operating history has a round-3 no-formal-patch disposition: existing
  CoAgent docs and orchestration workflow already carry the gate. This
  migration records guardrails only and does not authorize CoAgent
  implementation, live visibility-health claims, app-server transport,
  unattended automation, department expansion, schema changes, routine real
  notifications, or tool/MCP expansion.
  External-reference learning has a round-3 no-formal-patch disposition:
  existing indexes/workflows already require reference-index-first routing,
  patch-or-no-patch audit outcomes, and explicit approval plus local evidence
  before direct runtime adoption. RflySim/AirSim/Gazebo/PX4/Sunray/FAST-LIO and
  agent/skill/MCP references remain contracts, patterns, source material, or
  candidates unless a separate approved integration proves them locally.
  The currently identified round-2 topic set now has round-3 dispositions and
  a cache-only completion audit:
  `Docs/Cache/session_memory_migration/00_index/completion_audit_20260604.md`. A new
  conversation can recover this migration from project-local docs/cache without
  reading the old chat transcript. This does not certify unknown external
  session lines; any newly surfaced historical claim must enter round 1 before
  formal promotion. Do not compress this `PROGRESS.md` in the migration itself;
  compaction should be a separate cleanup after confirming equivalent cache,
  workflow, result-manifest, or ledger coverage.

- 2026-06-03 CST Codex shared Windows state repair: user prefers not to isolate
  Windows CLI into `C:\Users\HP\.codex-cli`. Restored the shared-home route by
  changing `C:\Users\HP\.codex\bin\codex.cmd` to set
  `CODEX_HOME=C:\Users\HP\.codex`, replacing the stale `0.135.0-alpha.1`
  Windows CLI runtime in `C:\Users\HP\.codex\bin` with the `0.136.0-alpha.2`
  runtime from the VSCode extension, and backing up old files under
  `C:\Users\HP\.codex\backups\shared_cli_runtime_before_0136_20260603_221540`.
  `app-server` still failed because `state_5.sqlite` SQLx checksums used LF
  migration text while the current Windows runtime expected CRLF checksums.
  After closing Codex App, backed up `state_5.sqlite*` under
  `C:\Users\HP\.codex\backups\shared_state_sqlx_checksum_fix_20260603_221742`
  and updated only `_sqlx_migrations.checksum` from a clean current-runtime
  probe DB, preserving 308 `threads` rows and all session JSONL files.
  Verification: `codex --version` now reports `codex-cli 0.136.0-alpha.2`,
  `codex doctor --summary` reports `15 ok`, `0 fail`, and a direct
  `codex app-server --analytics-default-enabled` smoke no longer prints the
  SQLite migration error. Remaining warnings are thread index/path drift, not a
  startup blocker. Workflow updated in `Docs/Workflows/debug_mcp.md`.

- 2026-06-03 CST Codex App hang diagnosis: Windows event log shows repeated
  `Application Hang` events for `OpenAI.Codex` / `Codex.exe`, including App
  version `26.601.2237.0` and Chromium `149.0.7827.54`. Latest desktop log
  after the SQLite repair shows app-server connects successfully, then startup
  work can stall on plugin/skills/MCP/Computer Use probes:
  `IpcClient Initialize failed timeout`, `computer-use native pipe startup
  failed`, `bundled_plugins_reconcile_failed ... 拒绝访问`, and
  `mcpServerStatus/list` taking about 16-17 seconds. Local Windows proxy is
  enabled at `127.0.0.1:7897` with no Codex AppContainer loopback exemption;
  adding the exemption requires elevated Windows terminal:
  `CheckNetIsolation.exe LoopbackExempt -a -n=openai.codex_2p2nqsd0c76g0`.
  `Get-AppxPackage` reports `OpenAI.Codex_2p2nqsd0c76g0`, but
  `CheckNetIsolation -n=` must use the AppContainer moniker registered under
  HKCU mappings on this machine.
  Major independent risk: the active MoSim Windows App session JSONL is about
  `1.96 GB` and the state row records nearly `1e9` tokens, so Windows App
  resume/thread rendering may hang even when `codex doctor` is healthy. Updated
  `Docs/Workflows/debug_mcp.md#42-windows-codex-app-not-responding`.

- 2026-06-03 CST Sunray150 realistic material review candidate generated:
  WeChat notification is working again after the user refreshed the context
  with a normal message. `sunray150_dae_mid360_realistic_material_audit.blend`
  was generated from the accepted DAE + standalone MID-360 assembly without
  changing `MID-360 uniform_scale=0.833527` or propeller
  `translation_z=-0.014052 m`. The candidate replaces the rejected dark/stylized
  palette with role-based PBR materials: graphite carbon plates, black composite
  propellers, metal screws/motors, and per-submesh MID-360 materials
  (`015` blue optical window, `013/014` dark housing, `016` black base,
  connector details black). Status: pending user Blender visual audit; do not
  export to UE until accepted.

- 2026-06-03 CST Sunray150 realistic material review candidate rejected by
  user. Root issue: it was simple PBR coloring, not a real texture/material
  workflow, and it did not first identify all physical components. Do not reuse
  that candidate as final appearance evidence. Correct route is: study local
  Blender/ArmorPaint/Material Maker/xatlas workflows, classify DAE/SDF
  components, research actual component appearances, then build a review asset
  with component-specific PBR materials/procedural textures/UV-ready texture
  slots. Initial DAE probe shows the source contains front/bottom cameras, USB
  9P/24P connectors, HDMI connector, FCU cable, ESC board, TF Mini PLUS,
  screws, standoffs, motors/windings, carbon frame, landing gear, and MID-360
  protection arcs; these must be handled explicitly or marked as unresolved.
  Follow-up: local Blender/ArmorPaint/Material Maker/xatlas projects were
  reviewed. Current route now generates deterministic PBR texture maps under
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/` and attaches them
  to Blender node materials. The whole-aircraft preview is still not accepted:
  distant rendering remains dominated by light DAE/MID-360 geometry and does
  not yet prove real material quality. Next valid review must use close-up
  material views for carbon fiber, MID-360 housing/window, USB camera/PCB,
  motors/windings, propellers, and smoked guards before any UE export.
  Safety correction: do not open `.blend` via Windows file association,
  Windows MCP `App`, or `blender-launcher.exe`; those routes triggered
  unrelated Visual Studio Blend/Ansys installer or uninstall dialogs. Ansys is
  not part of MoSim; if any non-Blender installer/uninstaller appears during
  asset work, stop immediately and report it instead of clicking through. Use
  only verified Blender command-line/background paths until GUI launch is
  repaired.
  Material update: fixed residual WSL/Windows path bugs in Blender asset
  scripts, regenerated darker carbon-fiber and MID-360 silver-grey PBR maps,
  corrected `PROTECTIVE_RING` / `MID360_PROTECT_ARC*` material assignment to
  dark protection structure, and rendered close-up audit images for MID-360,
  front USB camera/battery, PCB/connectors/cables, carbon/gold standoffs, and
  motor/prop/guard. Geometry invariants are preserved: MID-360 scale
  `0.833527`, propeller source `sunray_cw.stl`, orientation
  `flipped_around_screw_axis`, and propeller Z rule ending at `-0.014052 m`.
  Status remains pending manual Blender material audit; no UE export/import is
  allowed yet.
  Follow-up material audit package:
  `Results/unreal_scene_mapping/SUNRAY150_MID360_MATERIAL_AUDIT_PACKAGE_20260603.md`.
  The latest preview has stable exposure and clearer MID-360/connector
  materials, but remains an audit candidate. Known visual risks before
  acceptance: the front camera/module shell may still read too light grey, and
  propeller blades/guards can show white reflection patches. Resolve by
  component-specific material correction or UV/ArmorPaint paint pass after
  manual review, not by broad geometry or placement changes.
  2026-06-04 audit update: rejected the current material candidate. Whole
  preview remains dominated by light-grey CAD surfaces; MID-360 housing is too
  white and has a connector black artifact; front electronics/camera and
  motor/prop close-ups are underexposed; carbon frame weave is not visible on
  the main frame; gold standoffs look too plastic. Geometry remains accepted
  and must stay locked. Next pass is material-only: reclassify grey fallback
  objects, fix MID-360 connector material/occlusion, improve lighting, and
  produce readable component close-ups before any UE export.
  Added evidence matrix
  `Results/unreal_scene_mapping/SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md`
  so component identity, target material, source names, and known visual risks
  are not chat-only. The Taobao reference URL is useful for user-side visual
  checking, but browser/tool access is unreliable here, so it is not treated as
  confirmed evidence without local screenshots or saved media.

- 2026-06-03 CST Sunray150 propeller assembly correction: user rejected manual
  propeller tuning and clarified that this is an assembly constraint problem:
  propeller holes must align with motor screw positions / mating faces. Added
  `Scripts/UE5/assets/build_sunray_propeller_assembly_audit_scene.py` and
  generated
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/Sunray_Propeller_Assembly_Audit.blend`
  plus manifest. The DAE source preserves 8 `SCREW_BUTTON_HEAD_M2_8MM`
  propeller screw candidates and 4 `PROPELLER_*` semantic parts; the audit scene
  marks DAE screws in gold, DAE semantic propellers in blue, DAE `CircPattern*`
  possible full propeller patterns in red, MWORKS runtime propeller hole centers
  in magenta, and candidate hole-to-screw constraints in green. Current status:
  audit-only, not runtime parameter commit. Do not fix remaining propeller error
  by manual yaw/Z/XY offsets; choose the final asset source chain after visual
  audit, then regenerate UE runtime geometry from that source.

- 2026-06-02 CST Sunray150 DAE source audit: user rejected the previous
  textured/proxy MID-360 result because the radar base was not source-faithful.
  Source files for audit are
  `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/150.dae`
  and
  `References/Sunray/simulation/sunray_simulator/models/sensor_models/livox_mid360/meshes/test2.dae`.
  Critical correction: `sunray150_with_mid360.sdf` includes
  `model://livox_mid360` at pose `0.036 -0.0155 0.075 0 0 0`; therefore
  `150.dae` alone is not the complete vehicle + MID-360 source. Created and
  opened
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/Sunray_DAE_Source_Audit.blend`
  with left = raw `150.dae`, right = raw standalone `livox_mid360/test2.dae`,
  and no supplemental proxy geometry. Do not use the earlier proxy base/dome
  asset as final geometry.

- 2026-06-02 23:20 CST Blender/Sunray asset route: Blender MCP is confirmed
  working. Blender 5.0 has no Collada/DAE import operator in this environment,
  so `bpy.ops.wm.collada_import` is not a valid route. Added
  `Scripts/UE5/assets/build_sunray150_blender_asset.py` to parse local Sunray
  `150.dae` directly, group 701 named geometries by physical role, assign
  Blender materials through `node.type == "BSDF_PRINCIPLED"`, and export
  `Sunray150_Mid360_Textured.blend/.fbx/.glb` plus manifest and preview under
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/`. This generated review asset
  is now historical diagnostic output only, because it adds supplemental grey
  base + blue dome geometry instead of composing the actual standalone
  `livox_mid360/test2.dae` scanner from the Sunray SDF.

- 2026-06-02 CST Factory/Sunray visual gate user review update: user confirms
  propellers remain wrong and the UAV nose is yawed 90 deg. Specific visual:
  camera looks forward while UAV nose points right. Correction: the UE
  procedural visual must reproduce the MWORKS animation frame, not only the
  Sunray SDF rotor link order. MWORKS body uses
  `lengthDirection={0,-1,0}`, so the UE visual subtree needs a shared
  `-90 deg` yaw offset. Apply that same visual yaw to body mesh, rotor
  positions, and per-frame propeller spin; otherwise the upside-down motor /
  propeller layout separates from the already verified MWORKS visual result.

- 2026-06-02 CST Factory/Sunray visual gate follow-up: rotating rotor
  translations with the body visual yaw is still wrong. Updated correction:
  `lengthDirection={0,-1,0}` is a body STL visual orientation rule, while
  `Dronefixed1..4` are physical rotor translations already correct in MWORKS.
  Keep the body mesh yaw offset, but keep propeller component relative
  locations at the raw MWORKS fixed translations. Only propeller mesh
  orientation/spin carries the visual yaw offset.

- 2026-06-02 CST Factory/Sunray visual gate follow-up: user identifies the
  remaining propeller error as the vertical coordinate. The motors are
  inverted and should appear on the aircraft underside in the UE review. For
  the current procedural visual, preserve MWORKS rotor XY translations but use
  UE visual Z `+2.5 cm` for all four propeller components instead of `-2.5 cm`.

- 2026-06-02 CST Factory/Sunray visual gate follow-up: user reviewed the
  `+2.5 cm` propeller Z attempt and reported it is worse. Current manual test
  value is UE visual Z `-7.5 cm` for all four propeller components, preserving
  the same XY coordinates.

- 2026-06-02 CST Factory/Sunray visual gate source-derived correction: local
  MWORKS and Sunray SDF agree on body visual offset `r_shape/body visual
  z=+0.0525 m` and rotor center `z=-0.025 m`. Because the UE actor root is at
  the UAV state origin while the body mesh visual is offset relative to that
  origin, the propeller visual Z relative to the body visual center should be
  `(-0.025 - 0.0525) m = -0.0775 m = -7.75 cm`. Current UE review value is
  therefore `Z=-7.75 cm`, not the earlier trial values `-2.5`, `+2.5`, or
  `-7.5`.

- 2026-06-02 CST Factory/Sunray visual gate manual override: user reviewed the
  `-7.5 cm` / `-7.75 cm` range and reported the propeller underside fit should
  be closer to `-7.0 cm`. The UE procedural STL component origin does not
  visually match the simple source-derived rotor-center calculation tightly
  enough for final placement. Current review value is therefore `Z=-7.0 cm`
  for all four propellers, while preserving MWORKS rotor XY translations and
  visual yaw offset.

- 2026-06-02 CST Factory/Sunray visual gate root-cause correction: user pointed
  out that approximate manual ranges are not a substitute for the parameters
  already working in MWORKS. Investigation found the UE bridge had mixed the
  MWORKS body STL with the compact Gazebo/Sunray `sunray_cw.stl` propeller and
  SDF roll/yaw visual offsets. That invalidated the MWORKS coordinate chain.
  Corrected rule: use MWORKS `sunray150_mid360_body.stl` at scale `3.0`,
  MWORKS body `r_shape={0,0,0.0525}` -> UE body component `Z=+5.25 cm`, MWORKS
  `sunray150_mid360_propeller.stl` at scale `0.125`, and MWORKS
  `Dronefixed*.r.z=-0.025` -> UE propeller component `Z=-2.5 cm`. Do not mix
  Gazebo compact propeller meshes or SDF propeller roll offsets into the
  MWORKS-parity UE visual gate.

- 2026-06-02 CST Factory/Sunray movement follow gate: after user accepted the
  static UAV visual as basically correct, added a separate `FOLLOW_UAV_CAMERA=1`
  review mode. It keeps the static first-frame gate unchanged, but can replay
  the short Factory path once and enables `-MoSimFollowPlaybackCamera`. The
  review camera follows the spawned playback actor at a closer offset
  `(-180,0,85) cm` by default, rotating the offset with UAV yaw so translation
  and heading changes remain inspectable.

- 2026-06-02 CST Factory/Sunray movement follow camera tuning: user requested
  the moving review camera be much closer for inspection. Accepted default
  follow offset is now `(-50,0,30) cm`: 50 cm behind and 30 cm above the UAV,
  still rotated with UAV yaw during movement review.

- 2026-06-02 CST Factory/Sunray movement follow camera tuning: user refined the
  close follow offset to `(-60,0,30) cm`: 60 cm behind and 30 cm above the UAV.

- 2026-06-02 CST Factory/Sunray movement smoothness correction: user requested
  `60/40` follow camera and rejected stepwise UAV motion. Updated the movement
  gate to `(-60,0,40) cm`, resample sparse Factory review CSV poses to the
  20 Hz controller-frame contract, and interpolate UE actor transforms at the
  60 fps display contract. This fixes render-side teleporting; the current
  Factory review replay remains display-only and is not a Sysplorer solver
  evidence source.

- 2026-06-02 CST Factory/Sunray movement smoothness correction follow-up:
  user still observed stepwise motion and requested `60/60`. Root cause is the
  Factory visual gate CSV itself: 34 rows over 8.25 s, i.e. 0.25 s / 4 Hz path
  points, not a 20 Hz MWORKS controller/state output. RflySim's pattern is
  continuous CopterSim/PX4 state over UDP into RflySim3D/UE, not direct path
  point playback. Updated this visual gate to stream 60 Hz resampled render
  pose frames and lock the follow camera to the render pose without an extra
  chase interpolation layer. Formal controller smoothness still requires a real
  MWORKS/Sysplorer 20 Hz or higher state source, not this display CSV.

- 2026-06-02 CST Factory/Sunray movement follow camera tuning: user reviewed
  `60/60` and requested returning to `60/40`. Kept the 60 Hz render-frame replay
  route, but restored the close follow camera to `(-60,0,40) cm`.

- 2026-06-02 CST Factory/Sunray movement follow camera tuning: user requested
  `80/40` as the better close-inspection distance. Kept the 60 Hz render-frame
  replay route and changed the default follow camera to `(-80,0,40) cm`.

- 2026-06-02 CST Factory/Sunray movement follow camera tuning: user requested
  a left-rear inspection view. Kept the 80 cm rear distance and 40 cm height,
  and changed the default follow camera to `(-80,-40,40) cm`.

- 2026-06-02 CST Factory/Sunray movement follow camera tuning: user refined the
  left-rear offset from `y=-40 cm` to `y=-20 cm`. Kept the default follow
  camera at `(-80,-20,40) cm`.

- 2026-06-02 CST Factory/Sunray movement gate correction: user rejected the
  previous movement review because it was pure path-point translation with no
  visible attitude dynamics. Root cause: `FOLLOW_UAV_CAMERA=1` still used sparse
  `render_replay.csv` by default. Corrected the movement gate to default to the
  MWORKS/Sysplorer smoke state CSV
  `Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv`,
  which has 628 rows over 31.3 s and includes `roll/pitch/yaw` and `u1..u4`.

- 2026-06-02 CST Factory/Sunray visual gate user review update: user reports
  propeller placement is still wrong and the UAV initial heading is wrong.
  Current correction route is constrained to the already accepted body render:
  keep the full Sunray/MWORKS body STL source, scale, and body relative
  transform unchanged; use `sunray150_with_mid360.sdf` visual order for
  propeller components (`rotor_0` front-right, `rotor_1` back-left,
  `rotor_2` front-left, `rotor_3` back-right); and force the Factory visual
  gate first-frame yaw to neutral `0 rad` before any path replay/planner
  review. Do not proceed to point cloud, grid map, FAST-LIO, or planning until
  this visual gate is accepted.

- 2026-06-02 CST Factory/Sunray visual gate user review update: UAV task start
  is accepted, but the review camera was also spawned at the same UE point and
  became trapped by the collision-constrained review setup. Correct rule: keep
  the UAV first frame at accepted task start `(-55.33,-24.23,1.90) m`, but keep
  the review camera offset from the UAV center. Updated defaults use camera UE
  `(-5733,2423,280) cm` with pitch `-12 deg` while UAV remains at
  `(-5533,2423,190) cm`.

- 2026-06-02 CST Factory/Sunray visual gate user review update: body rendering
  is accepted, but the review behavior and propeller layout are not. User
  observed the UAV starts near the camera, then replays the old path several
  times and finally stops far away; propeller positions are wrong. Fix route:
  keep the accepted body transform/source unchanged, stop default path replay
  for the vehicle visual gate, and use local Sunray/MWORKS rotor layout before
  asking for the next review. Reusable rule reinforced: when the user gives a
  manual visual result, accept it as authoritative and fix that result; do not
  spend more time checking whether the window is still open. For UAV/UE
  behavior problems, inspect local RflySim/Sunray/YunZong/MWORKS references
  first, then go online only if local sources are insufficient.

- 2026-06-02 CST Factory/Sunray visual gate propeller recheck opened. Fixes:
  `review_factory_uav_platform.sh` now defaults to first-frame-only
  (`STREAM_MAX_FRAMES=1`) and requires explicit `STREAM_PATH_REPLAY=1` before
  replaying the old path; `QuadrotorMworksPlaybackActor` keeps the
  user-accepted body transform unchanged and applies the MWORKS/Sunray rotor
  layout `(6.5,-6.5,-2.5)`, `(6.5,6.5,-2.5)`, `(-6.5,6.5,-2.5)`,
  `(-6.5,-6.5,-2.5)` cm to the four propeller components. Checks passed:
  `python3 Scripts/tests/test_factory_uav_platform_review.py`,
  `python3 -m py_compile ...`, `bash -n ...`, targeted `git diff --check`,
  and `timeout 60s bash Scripts/UE5/build_unreal_renderer.sh`. The Factory
  review command streamed exactly 1 frame; UE log confirms first frame
  `mworks_position_m=(-55.330,-24.230,1.900)` maps to
  `actor_location_cm=(-5533,2423,190)`, primitive fallback is hidden, and
  propeller component diagnostics match the source rotor layout. WeChat manual
  review notification sent successfully using
  `Results/coagent_gateway/progress/factory_sunray_propeller_gate_review_20260602.json`.
  Current state: stop and wait for user visual audit of propeller placement and
  no old-path movement before continuing.

- 2026-06-02 14:56 CST Factory/Sunray visual gate reopened after user
  rejection. Fixes applied: `QuadrotorMworksPlaybackActor` now loads the full
  Sunray body STL (`source_triangles=530874`, `loaded_triangles=530874`) and
  refuses destructive triangle-limit downsampling; propellers now use compact
  binary Sunray `sunray150/meshes/sunray_cw.stl` instead of the huge-extent
  ASCII propeller STL; primitive cube/cylinder fallback and render-only helper
  cylinders/markers are hidden for the vehicle-visual gate; the Factory review
  first frame is aligned to the review camera start
  `position_m=(-55.330,-24.230,1.900)` -> UE `(-5533,2423,190)` cm. UE log
  confirms fallback hidden, full body load, compact propeller bounds, review
  camera at `(-5533,2423,190)`, UDP first frame, and actor first-applied frame
  at the same location. `Scripts/UE5/review_factory_uav_platform.sh` reopened
  the Factory window and streamed 34 frames. WeChat manual review packet sent:
  `Results/coagent_gateway/progress/factory_sunray_visual_gate_review_20260602.json`.
  Current state is waiting for user visual acceptance of the opened UE window.

- 2026-06-02 14:56 CST reusable UE build recovery: if
  `build_unreal_renderer.sh` fails with `LNK1104` or UBA says
  `UnrealEditor-QuadrotorMworksBridge.dll` is locked by `UnrealEditor.exe`,
  inspect and stop only the `UnrealEditor.exe` processes whose command line
  contains `MoSimSceneLibrary.uproject`, then rebuild. Use escaped PowerShell
  `$_` from bash; an unescaped `$_` is expanded by bash and the process will
  not be stopped.

- 2026-06-02 14:23 CST long-run goal checkpoint: current active goal is the
  Factory-first MoSim UAV platform minimum loop. Execution order is fixed:
  first keep WeChat notification recoverable; then use the YunZong/Sunray150
  body in UE; then prove Factory scene + visible Sunray UAV + MWORKS/Bridge
  pose drive; only after manual acceptance may the task return to
  LiDAR/FAST-LIO/RViz evidence. Primitive cube/cylinder UAV visuals are not
  accepted review evidence. They may appear only as an explicit diagnostic
  fallback when Sunray STL/UE asset loading fails, and that condition must be
  reported as a blocker instead of being treated as success.

- 2026-06-02 14:23 CST WeChat gateway hardening checkpoint:
  `CoAgent/gateway/cc_connect_weixin.py` now resolves empty session, `s1`,
  project name, session JSON path, and platform session keys to the active
  `weixin:dm:...` key. It classifies `ret=-2`, missing context token, missing
  active session, internal API/socket failure, and timeout; for these failures
  it performs one bounded cc-connect restart/retry and writes a recovery packet
  under `Results/coagent_gateway/recovery/` if still blocked. This can recover
  stale process/socket state, but cannot synthesize a Weixin ilink context
  token when the platform requires a fresh inbound message or QR relogin.

- 2026-06-02 14:27 CST Factory/Sunray manual gate opened. Checks passed:
  `python3 CoAgent/tests/test_gateway_weixin.py`,
  `python3 -m py_compile CoAgent/gateway/cc_connect_weixin.py
  CoAgent/tests/test_gateway_weixin.py`,
  `python3 Scripts/UE5/check_unreal_bridge.py`,
  targeted `git diff --check`, `bash -n` for UE review/build scripts, and
  `timeout 60s bash Scripts/UE5/build_unreal_renderer.sh`. UE build completed
  in about 12s and rebuilt `UnrealEditor-QuadrotorMworksBridge.dll`. Runtime
  Factory review evidence: `Scripts/UE5/review_factory_uav_platform.sh`
  activated `local_factoryenvironmentcollect`, opened
  `/Game/Maps/Demonstration`, found UDP 5005, and streamed the Factory replay.
  UE log confirms `MoSim Sunray STL loaded` for
  `sunray150_mid360_body.stl` with `88479` triangles and four
  `sunray150_mid360_propeller.stl` meshes with `848` triangles each; it also
  confirms `MWORKS renderer spawned playback actor and linked map actor` and
  `Quadrotor MWORKS UDP first frame`. WeChat review packet
  `Results/coagent_gateway/progress/mosim_factory_sunray_manual_review_20260602.json`
  sent successfully. Manual decision needed before continuing to RViz,
  FAST-LIO, or point-cloud work.

- 2026-06-02 CST Factory/Sunray manual review failed. User confirmed the UAV is
  connected, but the visible model is not acceptable: there is a huge cylinder,
  the STL body renders broken/fragmented, and the UAV initial position is not
  aligned with the camera initial position. Treat this as a failed UE vehicle
  body gate, not as an accepted platform loop. Next work must inspect the
  Sunray/SDF/STL asset dimensions and UE runtime mesh logs, switch to a
  complete/valid STL or proper UE asset import path, fix scale/rotor
  placement, and set the review initial UAV position to the camera initial
  position before asking for review again. Reusable rule: for UE manual gates,
  write more diagnostic logs and inspect those logs before requesting user
  review; visual evidence without model-load/scale/position logs is too weak.

- 2026-06-02 14:27 CST script note: `OPEN_UE=0
  Scripts/UE5/review_factory_uav_platform.sh` intentionally routes to dry-run
  and does not send live UDP frames, preserving the regression-test route.
  Reusable command for an already-open UE review window is now
  `STREAM_ONLY=1 STREAM_LOOP_COUNT=10 STREAM_FPS=6
  Scripts/UE5/review_factory_uav_platform.sh`; it does not restart UE and does
  send live UDP frames with the Factory `mworks_world_m_z_up` coordinate
  policy. Regression `python3 Scripts/tests/test_factory_uav_platform_review.py`
  now covers both dry-run review and live `STREAM_ONLY=1` replay. Live smoke
  `STREAM_ONLY=1 STREAM_LOOP_COUNT=2 STREAM_FPS=12
  bash Scripts/UE5/review_factory_uav_platform.sh` streamed 34 frames to the
  open UE UDP receiver.

- 2026-06-02 CST Factory-first UAV platform gate: added
  `Scripts/UE5/review_factory_uav_platform.sh` as the narrow UE-only manual
  review entry. It activates `local_factoryenvironmentcollect`, opens
  `/Game/Maps/Demonstration` in `simulation-review`, waits for UDP 5005, and
  streams `render_replay.csv` to the visible UAV body only. It deliberately
  does not open RViz or continue the rejected point-cloud/grid-map route. The
  stream uses `--coordinate-policy mworks_world_m_z_up`; Factory collision
  truth states `mworks_y=-unreal_y`, so replaying Factory MWORKS/truth
  coordinates as `ue_world_m_z_up` places the UAV on the wrong Y side of the
  scene. WeChat start packet
  `Results/coagent_gateway/progress/mosim_factory_first_uav_platform_start_20260602.json`
  was attempted once and failed with
  `weixin: sendMessage: ret=-2 errcode=0`; keep progress in project records
  until the gateway runtime is refreshed. UE Factory UAV body review was
  launched; manual gate is visible blue UAV body moving in Factory, with
  keyboard/mouse controlling only the view.

- 2026-06-02 CST WeChat gateway failure diagnosis: latest failure is not a
  CoAgent packet-format error and not a missing cc-connect session file. The
  cc-connect process is still running and
  `/home/linux/.cache/mosim/coagent/cc-connect-weixin/data/sessions/MoSim｜微信通知网关_b075d247.json`
  still has an active `weixin:dm:...` session. The send failed because the
  Weixin platform API declined outbound `sendMessage` with `ret=-2 errcode=0
  errmsg=` after cc-connect retried three times with a fresh `context_token`.
  Treat this as Weixin/ilink send-context degradation or login/send-window
  staleness, not as a project-message construction failure. Recovery path:
  first have the user send a short message in the WeChat gateway conversation
  to refresh the active context, then retry one tiny send; if `ret=-2` remains,
  restart/relogin cc-connect Weixin via QR and do not loop notifications.

- 2026-06-02 CST WeChat gateway recovered after user context refresh. User sent
  a short WeChat message, then bounded retry packet
  `Results/coagent_gateway/progress/weixin_context_refresh_retry_20260602.json`
  sent successfully with `Message sent successfully.` Reusable rule: after
  Weixin outbound `ret=-2`, request one user inbound ping to refresh context,
  then retry exactly one tiny packet before escalating to QR/relogin.

- 2026-06-02 13:27 CST process correction: the previous UE/ROS route-hardening
  task did not send the required WeChat milestone report. For future UE/ROS,
  FAST-LIO, MWORKS, MCP, Git split, or manual-review tasks, send WeChat at
  task start, phase completion, blocker, and manual-review request. If WeChat
  is unavailable, report the failure immediately in the main conversation and
  continue with file-based progress records only after making that explicit.

- 2026-06-02 13:30 CST platform-order correction: do not ask for point-cloud
  or FAST-LIO window manual audit as "basic platform" evidence before the UAV
  actor/body is connected in UE and its pose is driven by the MWORKS/bridge
  state path. FAST-LIO headless/RViz evidence is sensor/localization evidence
  only. The next platform gate must first prove Factory UE scene + visible UAV
  body + MWORKS/bridge-driven pose update, then review LiDAR/FAST-LIO in RViz.

- 2026-06-02 13:21 CST current route hardening: keyboard mappings are retained
  only for UE/RViz view/camera control, not UAV motion. `AGENTS.md` and
  `Docs/Workflows/unreal_renderer.md` now state that keyboard/mouse input must
  not drive UAV pose, overwrite MWORKS truth, or substitute for controller
  setpoints. Current executable ROS2 path is narrowed to Factory
  MWORKS/Livox/FAST-LIO: `publish_mworks_uav_state_ros2.py`,
  `run_factory_fastlio_mid360_headless_ros2.sh`,
  `mosim_scene_replay.launch.py`, `check_fastlio_ros2_topics.sh`, and
  `Config/rviz2/mosim_uav_fastlio_pointcloud.rviz`. Removed live dependencies
  on deleted mapping/grid wrappers from runtime checks/tests. Targeted tests
  passed: `test_mworks_uav_state_ros2.py`, `test_ros_mapping_runtime_env.py`,
  `test_fastlio_rviz_runtime_scripts.py`,
  `test_unreal_scene_runtime_readiness.py`, and
  `test_scene_runtime_bundle.py`. With ROS2 sourced, runtime preflight reports
  ROS2/RViz2 packages ready; local ROS1 FAST_LIO references remain degraded
  compatibility references. Current Gate B output remains
  `ready_for_manual_rviz_ue_review` with `/Odometry=80`, `/path=8`,
  `/cloud_registered=80`, RMSE `0.39454m`.

- 2026-06-02 CST route correction from user manual audit: stop continuing the
  hand-built RViz point-cloud / local grid-map display route. The current
  review chain (`publish_mosim_mapping_replay_ros2.py`,
  project-authored RViz configs, local voxel/grid replay, and display-side
  fixes for `/Odometry`, `/mosim/local_occupancy_voxels`, wall-time replay, or
  RViz fixed-frame tuning) is no longer a product direction and must not be
  treated as accepted evidence. The user reports that the point cloud/grid map
  are fundamentally wrong compared with real FAST-LIO/RflySim behavior, and
  suspects the missing real UAV integration is the root cause. Next work must
  pivot to studying local RflySim/source patterns and connecting the UAV stack
  first: MWORKS dynamics/control -> UAV body/vehicle interface -> UE render and
  sensor source -> native FAST-LIO/RViz outputs from reused upstream code. Do
  not spend more time polishing hand-written point-cloud/grid visualization.

- 2026-06-02 CST Factory Gate B correction checkpoint: the main FAST-LIO
  failure has been narrowed from "runtime cannot publish" to a data-consistency
  and quality gate. Fixed ROS2 MWORKS IMU replay so `linear_acceleration`
  uses second finite differences of position and adds the explicit gravity
  convention on `z`, instead of publishing velocity as acceleration; regression
  `python3 Scripts/tests/test_dense_lidar_cpp_contract.py` covers this. Fixed
  the headless ROS2 setup route in
  `Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh` to source
  package-level local setup files for `livox_ros_driver2`, `fast_lio`, and
  `mosim_dense_lidar_cpp`, avoiding the old overlay package masking the rebuilt
  dense publisher. Added first-message waits for `/mosim/livox/lidar` and
  `/mosim/forward/imu`, because the dense replay node can spend about 20s
  parsing large JSONL before publishing. Extended
  `Scripts/UE5/generate_livox_like_lidar_replay.py` with `--pose-stride`,
  `--points-frame world|body`, and `--truth-dataset-name`; regression
  `python3 Scripts/tests/test_livox_like_lidar_replay.py` covers body-frame
  LiDAR and matching truth output. Critical contract: Gate B LiDAR, IMU/state,
  and truth evaluation must come from the same MWORKS raw trajectory, and
  FAST-LIO input points must be body/lidar-frame points when published as
  `base/mid360_link`. The old mixed-source/world-frame route produced large
  errors and must not be used for acceptance. Latest same-source body-frame
  smoke run
  `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_factory_mworks_body_smoke_20260602_120335`
  produced nonzero FAST-LIO output counts `/Odometry=41`, `/path=4`,
  `/cloud_registered=40`, but still failed the formal threshold with
  RMSE `1.019363m` and max error `1.437659m`. Gate B remains
  `blocked_before_manual_review`; next step is a formal same-source
  body-frame dataset at >=15k points/frame and enough duration, then rerun the
  headless gate before opening UE/RViz2 windows.

- 2026-06-02 CST Factory Gate B formal headless pass. Generated formal
  same-source body-frame Factory Mid360 dataset from MWORKS raw:
  `Results/unreal_scene_mapping/factoryenvironmentcollect/livox_like_lidar_frames_mworks_body.jsonl`
  and
  `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_mworks_truth_dataset.jsonl`.
  Manifest reports 40 frames, pose stride 2, body-frame points, min/avg/max
  points per frame `15607/16094.55/16515`, 10Hz LiDAR, 200k pts/s target.
  Removed the previous 29-line partial formal file from the official path by
  renaming it to
  `livox_like_lidar_frames_mworks_body.invalid_partial_20260602.jsonl`; the
  replay generator now uses atomic output files and supports
  `--pose-start-index` so timeouts do not leave half-written evidence. Fixed
  `mworks_state_imu_replay_node` finite-row behavior so it holds the final
  MWORKS row instead of looping and creating IMU/trajectory discontinuities.
  Rebuilt `mosim_dense_lidar_cpp` with direct CMake build/install. Formal run:
  `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_factory_mworks_body_formal_20260602_122033`.
  Input probe passed with Livox count `80`, IMU count `1600`, Livox `9.887Hz`,
  IMU `198.857Hz`, monotonic LiDAR/IMU stamps, min/max points
  `15607/16515`, lines `0..3`, tag `16`. FAST-LIO runtime recorded
  `/Odometry=80`, `/path=8`, `/cloud_registered=80`. Truth evaluation passed:
  RMSE `0.39454m`, max error `0.611542m`, yaw RMSE `0.017802rad`. Current
  `REALSTACK_MINILOOP_GATE.md/json` status is
  `ready_for_manual_rviz_ue_review`. This is a headless Gate B pass only; it
  does not yet prove final controller integration, planner performance, or
  manual visual acceptance. Next step is UE + RViz2 FAST-LIO + RViz2 3D map
  window review.

- 2026-06-02 CST Factory manual-review launch prep. Updated Gate B review
  defaults so `run_factory_fastlio_mid360_headless_ros2.sh`,
  `run_fastlio_rviz_replay_ros2.sh`, and
  `check_realstack_miniloop_gate.py` prefer the formal body-frame artifacts
  `livox_like_lidar_frames_mworks_body.jsonl` and
  `fastlio_mworks_truth_dataset.jsonl`, falling back to legacy files only when
  the formal files are absent. Updated
  `Results/unreal_scene_mapping/factoryenvironmentcollect/run_native_runtime_review.sh`
  so the manual review wrapper starts the ROS2 `fast_lio mapping.launch.py`
  runtime by default and opens split RViz2 review windows. Direct calls to
  `run_fastlio_rviz_replay_ros2.sh` still require an explicit
  `FASTLIO_ROS2_LAUNCH_CMD`; otherwise they only publish replay inputs and are
  degraded for FAST-LIO visual review. Checks passed:
  `test_factory_fastlio_mid360_headless.py`,
  `test_fastlio_input_contract.py`, and `test_realstack_miniloop_gate.py`.
  First manual-review launch exposed a ROS2 overlay bug: without sourcing the
  Livox underlay, `fastlio_mapping` could not load
  `liblivox_ros_driver2__rosidl_typesupport_cpp.so`, and Python replay could
  not import `livox_ros_driver2.msg.CustomMsg`. Fixed
  `run_fastlio_rviz_replay_ros2.sh` to source Livox, FAST-LIO, and MoSim dense
  bridge overlays in the same order as the passing headless gate; regression
  `test_fastlio_rviz_runtime_scripts.py` now checks these markers. Also fixed
  `run_native_runtime_review.sh` so `START_FASTLIO=1` owns RViz split and
  mapping publisher startup, avoiding duplicate mapping publishers and
  repeated `TF_OLD_DATA` warnings from two TF sources.
  Follow-up manual-review probe showed the selected ROS2 FAST-LIO runtime
  publishes odometry on `/Odometry`, while RViz had subscribed to `/odometry`;
  updated `Config/rviz2/mosim_uav_fastlio_pointcloud.rviz` to match the actual
  runtime topic. The planning RViz config also subscribed to
  `/mosim/local_occupancy_voxels` before the replay publisher emitted that
  topic; `publish_mosim_mapping_replay_ros2.py` now publishes occupied local
  cells as the 3D voxel review topic. These are review-surface fixes only and
  do not claim final planner/map integration.

- 2026-06-02 CST architecture validation/design closure checkpoint:
  `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md` now has a compact
  closure section for Gates A/B/C. Gate A is
  `passed_for_pid_demo_runtime_path`: generated MWORKS/Sysblock C runtime
  compiles and the PID demo nonzero constant-input SIL check passes under
  `1e-5` tolerance. Gate B is still `blocked_before_manual_review`: current
  Factory headless FAST-LIO evidence either has zero odometry/path/cloud output
  on the selected run, or older nonzero-output runs fail truth evaluation with
  about 9-10m RMSE and about 18m max error. Gate C is
  `design_closed_for_next_implementation`: MWORKS owns solver/controller/truth
  and generated C runtime; UE owns rendering and scene/sensor oracle; ROS2/RViz2
  owns LiDAR/IMU/TF, FAST-LIO, 3D local map, planner state, and native review;
  V6X/PX4/companion adapter remains the deployment/control-stream boundary.
  Before any UE/RViz2 manual review, the next implementation must pass a
  headless Factory FAST-LIO gate with nonzero `/cloud_registered`, odometry,
  path, monotonic timestamps, explicit extrinsics, and truth-error metrics.
  WeChat progress/manual-review reporting is now a hard rule in `AGENTS.md` and
  repeated in the architecture closure: use sparse milestone/blocker packets by
  default; if sending fails, diagnose cc-connect session/context immediately
  and report in the main conversation if it cannot be restored quickly. Closure
  packet
  `Results/coagent_gateway/progress/mosim_arch_validation_closure_20260602.json`
  was sent successfully through `MoSim｜微信通知网关`.

- 2026-06-02 CST Factory-first implementation started. WeChat start packet
  `Results/coagent_gateway/progress/mosim_factory_first_miniloop_start_20260602.json`
  sent successfully. Rechecked current FAST-LIO state: Factory dense
  Mid360/Livox input contract remains `claimable_input_ready`; local
  `spark-fast-lio` static Livox patch-readiness is now `ready=true`, but the
  current headless script runs the imported ROS2 `fast_lio` package route. The
  first short headless run used 10Hz LiDAR baseline and failed in the
  Livox/IMU probe because IMU stamps were nonmonotonic. Inspection found
  explicit leftover `dense_lidar_replay_node` and `mworks_state_imu_replay_node`
  processes from the failed script still publishing on the same topics, which
  can corrupt monotonicity checks. Reusable constraint: after a failed ROS2
  headless run, check and clean only matching MoSim publisher/FAST-LIO
  processes before retrying:
  `ps -eo pid,ppid,cmd | rg 'dense_lidar_replay_node|mworks_state_imu_replay_node|livox_imu_probe_node|fastlio|fast_lio|spark_lio|record_fastlio'`.

- 2026-06-02 CST MoSim architecture validation goal recreated. Scope is
  architecture validation and design closure, not display tuning. Gate A:
  MWORKS generated C/C++ controller nonzero-input SIL equivalence. Gate B: UE
  truth + ROS2 Mid360/FAST-LIO localization quality diagnosis. Gate C:
  closed-loop system contract for MWORKS, UE, ROS2/RViz2, V6X/PX4/companion
  computer, frequencies, time sync, coordinates, reuse/adapt/replace matrix,
  and manual-review points. Added WeChat Progress and Intervention Rule to
  `AGENTS.md`; updated `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md`
  with Gates A/B/C; recorded task in `Docs/Workflows/agent_task_ledger.md`.
  WeChat start packet
  `Results/coagent_gateway/progress/mosim_arch_validation_start_20260602.json`
  sent successfully through `MoSim｜微信通知网关`.
  Gate A progress: added MWORKS/Sysblock reference model
  `Models/QuadrotorControllerBlocks/AWFF_PID_Sysblock_Demo_SIL_Constant.mo`,
  checked and simulated it through Sysplorer MCP, and read `cmd_sum.y` values
  for constant `z_error=0.1`. Added reference evidence
  `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json`.
  Generated C runtime with input sequence `0.1,0.1,0.1,0.1` matches the MWORKS
  reference by output order with `max_abs_error=8.934736470678217e-07` under
  `1e-5` tolerance; evidence:
  `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json`.
  This validates the codegen/SIL architecture path for the PID demo. Stronger
  time-varying input SIL remains open before claiming all generated
  controllers are runtime-authoritative.

- 2026-06-02 CST WeChat gateway diagnosis completed. There were two distinct
  failure modes. `no active session found (key="MoSim｜微信通知网关")` was a
  CoAgent adapter bug: the project name was passed as `--session`, but
  cc-connect expects the `active_session` platform key (`weixin:dm:...`).
  Fixed `CoAgent/gateway/cc_connect_weixin.py` so empty session, `s1`, project
  name, session JSON path, and already-resolved platform key all resolve
  correctly; `result_router.py` and `review_queue.py` now default to
  `MoSim｜微信通知网关`. Test passed:
  `python3 CoAgent/tests/test_gateway_weixin.py`. Live send smoke passed using
  `Results/coagent_gateway/progress/weixin_gateway_diagnosis_20260602.json`
  with `Message sent successfully.` The other failure mode,
  `weixin: sendMessage: ret=-2`, is a Weixin/iLink send-context problem; first
  recovery is user sends one normal message to the gateway conversation, then
  retry once. If that fails, redo 10 minute QR setup and send one normal
  message to bind/refresh `context_token`. Keep WeChat sparse; do not mirror
  high-volume Codex/tool output through the gateway.

- 2026-06-02 CST MWORKS code-generation checkpoint: MWORKS/Sysplorer/Sysblock
  direct controller C generation is verified. The correct official Python API
  route is `GetModelCodeGenerationOptions` ->
  `SetModelCodeGenerationOptions` -> `GenerateModelCode`, not the current MCP
  `translate_model` wrapper. Probe model
  `Models/QuadrotorControllerBlocks/AWFF_PID_Sysblock_Demo.mo` generated C/H
  sources under
  `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo/`.
  Generated interface currently exposes `Init()`, `Step()`,
  `awff_pid_sysblock_demoGbIn`, `awff_pid_sysblock_demoGbOut`, and 0.01s step
  time. The generated C files compiled with `gcc -std=c99 -Wall -Wextra
  -pedantic -c`; temporary `.o` files were removed. Workflow is recorded in
  `Docs/Workflows/mworks_codegen_controller_runtime.md`. Next architecture
  step: make generated C/C++ controller runtime pass SIL equivalence against
  MWORKS/Sysblock, then adapt it to ROS2/PX4/V6X; do not resume hand-built
  point-cloud/grid demos as product work.
  2026-06-02 follow-up: external source check supports copying the RflySim
  layering pattern but replacing its solver/control authority with MWORKS.
  RflySim-style role split maps to MWORKS/Sysblock/Syslab for solver,
  controller, truth, metrics, and code generation; UE for rendering and
  scene/sensor oracle; ROS2/RViz2 for FAST-LIO, 3D map, planner state, and
  native review. The current Sysplorer MCP remains missing a dedicated
  `GenerateModelCode` wrapper; `translate_model` is not code-export evidence.
  Re-ran the generated C compile probe successfully on 2026-06-02 and removed
  temporary object files.
  Added reusable pre-SIL gate `Scripts/mworks/check_codegen_runtime.py` and
  regression test `Scripts/tests/test_mworks_codegen_runtime.py`. The gate
  summarizes generated files, confirms `Init`/`Step`, input/output globals,
  `sample_time_s=0.01`, and compiles generated C in a temporary directory so
  generated evidence folders are not polluted. Latest runtime-check evidence:
  `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_check.json`.
  Follow-up gate now includes a temporary C harness smoke run: write
  `awff_pid_sysblock_demoGbIn.z_error` values `0.1, 0.2, -0.1`, call
  `Init()`/`Step()`, and verify generated runtime time advances to
  `0.01, 0.02, 0.03` with `thrust_cmd` outputs recorded in
  `runtime_check.json`. This proves the generated code can be driven as a
  minimal runtime candidate before SIL equivalence. WeChat progress packet
  `Results/coagent_gateway/progress/mworks_codegen_runtime_gate_20260602.json`
  was attempted once through `MoSim｜微信通知网关`; cc-connect failed with
  `Error: no active session found (key="MoSim｜微信通知网关")`. Do not retry in a
  loop; refresh the gateway session before relying on progress notifications.
  Added first SIL smoke gate
  `Scripts/mworks/check_codegen_sil_equivalence.py` plus
  `Scripts/tests/test_mworks_codegen_sil_equivalence.py`. MCP simulation of
  `AWFF_PID_Sysblock_Demo` succeeds, but `AWFF_PID_Sysblock_Demo.thrust_cmd`
  is not a readable result variable; `result_manager` model-scoped discovery
  exposes internal variables including `cmd_sum.y`. The current evidence
  `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_zero_input_check.json`
  passes only `zero_input_sil_smoke` with max error `0.0`. This is not complete
  SIL: the next gate must inject the same nonzero input sequence into
  MWORKS/Sysblock and generated C runtime and compare outputs sample-by-sample.
  WeChat SIL smoke progress packet
  `Results/coagent_gateway/progress/mworks_codegen_sil_smoke_20260602.json`
  was attempted once through `MoSim｜微信通知网关`; cc-connect again failed with
  `Error: no active session found (key="MoSim｜微信通知网关")`.

- 2026-06-02 CST real FAST-LIO headless gate update: the route has moved past
  zero-output/runtime-startup blocking for Factory, but it is still not
  acceptable for manual RViz/UE review. Added C++ ROS2
  `livox_imu_probe_node` under `Scripts/ros/mosim_dense_lidar_cpp` because the
  Python double-subscriber probe could not reliably measure 200Hz IMU while
  deserializing 25k-point Livox frames. Latest successful headless run:
  `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_cpp_livox_headless_20260602_090500`.
  Input gate passed: `/mosim/livox/lidar` about `18.68Hz`, `/mosim/forward/imu`
  about `187.89Hz`, 24.5k-25.9k points/frame, Livox lines `0..3`, per-point
  offsets `0..49998us`, and latest LiDAR/IMU stamp delta about `-0.020s`.
  FAST-LIO runtime produced nonzero `/Odometry`, `/path`, and
  `/cloud_registered` counts `172/17/172`, but truth evaluation failed:
  position RMSE `9.576m`, max error `17.900m`. Updated
  `Scripts/UE5/check_realstack_miniloop_gate.py` so nonzero FAST-LIO topics are
  not enough; the gate now also requires a passing truth-evaluation file before
  opening review windows. Current gate report:
  `Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE.md`
  remains `blocked_before_manual_review`. Next work is extrinsic/timestamp/
  scan-pattern/initialization diagnosis, not RViz visual tuning. WeChat packet
  `Results/coagent_gateway/progress/ue_uav_fastlio_headless_gate_20260602_0905.json`
  was attempted once through project `MoSim｜微信通知网关`; the adapter accepted
  the blocker packet but cc-connect still failed with
  `weixin: sendMessage: ret=-2 errcode=0`. Treat WeChat as degraded and do not
  loop retries until the gateway session/runtime is refreshed. Recovery
  checkpoint: after the user sent `你好` in the Weixin gateway conversation,
  the exact same packet resent successfully with `Message sent successfully`.
  Record `ret=-2` as a stale Weixin/iLink send-context symptom first; ask the
  user to send one normal message and retry once before forcing QR relogin.

- 2026-06-02 CST handoff checkpoint: current ROS graph check through
  `ros_mcp` shows only rosbridge/static TF topics and no active
  `/mosim/*`, `/odometry`, `/path`, or `/cloud_registered` runtime. The latest
  Factory headless `spark-fast-lio` Livox CustomMsg attempt reached the real
  subscriber path but `spark_lio_mapping` crashed with exit code `-11`
  immediately after `Livox avia_handler entry` on a 21k-point frame. Evidence:
  `Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime_livox_custommsg_headless_20260602_062834/fastlio_launch.log`.
  Keep UE/RViz manual review closed until the headless gate has nonzero
  FAST-LIO odometry/path/registered-cloud output. The next technical decision
  is either finish a bounded `spark-fast-lio` Livox preprocess/runtime patch
  and rebuild, or switch to a native ROS2 Mid360/`livox_ros_driver2`
  FAST-LIO implementation. Sunray remains the local behavior reference:
  `external_fusion_node` runs at 200Hz, Mid360 uses `/livox/lidar` and
  `/livox/imu`, EGO consumes world-frame point cloud plus odometry, then
  `traj_server`/`positionCmd2sunray` converts planner output to UAV control.
  Do not optimize grid-cell movement, static point-cloud display, or 2D
  occupancy as product work.
  WeChat handoff task-list send was attempted once through
  `Results/coagent_gateway/progress/ue_uav_realstack_handoff_tasklist_20260602.json`
  using project `MoSim｜微信通知网关` and adapter session resolution. It still
  failed at the cc-connect/Weixin send layer with
  `weixin: sendMessage: ret=-2 errcode=0`. Treat WeChat as degraded for this
  run and keep progress in project files until the gateway is manually
  refreshed.
  Implementation checkpoint: removed repeated startup-log/filter-check blocks
  that had polluted the temporary `spark-fast-lio` candidate source under
  `Results/tmp/fastlio_ros2_candidates/.../spark_fast_lio.cpp`. Python gates
  now pass: `test_fastlio_input_contract.py`,
  `test_realstack_miniloop_gate.py`, and `test_fastlio_runtime_candidates.py`.
  `check_realstack_miniloop_gate.py` still correctly blocks manual review
  because runtime counts are zero. C++ rebuild on `/mnt/c` still exceeds the
  60s command rule while compiling/linking `spark_lio_component` and reports
  clock-skew warnings; treat this candidate as slow/fragile. A fresh
  `git clone --depth 1 https://github.com/Ericsii/FAST_LIO_ROS2.git` into
  `Results/tmp/fastlio_ros2_candidates_import/` also timed out at 60s and the
  partial directory was removed. Next preferred route is to import a native
  ROS2 Mid360/`livox_ros_driver2` FAST-LIO candidate via a faster download
  path or manual download, then run the same Factory headless gate.
  Build hygiene correction: direct `cmake --build` / `colcon` attempts must
  first source ROS2 in the same shell with `set +u; source
  /opt/ros/humble/setup.bash; source
  Results/tmp/spark_fast_lio_ros2_ws/install/setup.bash; set -u`. A later
  direct build without sourcing ROS2 failed at CMake with
  `ModuleNotFoundError: No module named 'ament_package'`; that is an
  environment error, not a FAST-LIO source diagnosis.

- 2026-06-02 CST real-stack correction update: do not tune the current
  point-cloud marker size, grid-cell step, or 2D map as product work. The
  correct next task is still a real UAV stack study/reuse pass before more
  implementation. Online and local checks confirm the hard contracts:
  PX4-style external control is streamed and faulted on stale proof-of-life,
  not a one-shot pose write; PX4 ROS2 uses uXRCE-DDS and matching `px4_msgs`
  definitions; Mid360 hardware-faithful baseline is 10Hz and about
  200k points/s with 200Hz IMU; FAST-LIO Livox evidence requires synchronized
  LiDAR/IMU plus per-point timing and explicit extrinsics/time offset. The
  FAST-LIO candidate gate is updated: current local `spark-fast-lio` remains
  patchable but not accepted for Mid360 because its standard PointCloud2 path
  rejects Livox `lidar_type=1`; before spending more time patching it, evaluate
  the external `Ericsii/FAST_LIO_ROS2` `ros2` branch, which declares
  `ament_cmake`, `livox_ros_driver2`, `mapping.launch.py`, default
  `mid360.yaml`, `/livox/lidar`, `/livox/imu`, `lidar_type=1`,
  `scan_line=4`, and `scan_rate=10`. Network clone/zip import timed out within
  the 60s gate, so it is not local runtime evidence yet. WeChat startup
  notification for `UE-UAV-REALSTACK-RESEARCH-20260602-LONGRUN` was attempted
  once and failed with `weixin: sendMessage: ret=-2 errcode=0`; continue
  file-based progress until the gateway runtime is repaired.

- 2026-06-02 CST user correction checkpoint: the current visible mapping
  prototype still has the wrong abstraction. Moving the UAV by grid-cell-sized
  steps, showing a 2D-only occupancy grid, or lowering point-cloud density to
  make a static/toy display reach frame rate cannot support controller
  optimization. The accepted direction is a real UAV stack: MWORKS produces
  continuous dynamics, controller state, truth, and 200Hz IMU; ROS2 carries
  synchronized IMU/LiDAR/TF/odometry, FAST-LIO, 3D local map, and planner
  topics; UE renders the accepted scene and provides sensor/collision oracle;
  RViz2 windows show live FAST-LIO point cloud and live 3D local map. Use PX4
  offboard-style continuous command semantics as the control-contract model:
  commands and heartbeat/setpoints are streamed, not one-shot pose overwrites.
  Use Mid360 hardware-faithful baseline first: 10Hz LiDAR, about 200k pts/s,
  per-point timing, 200Hz IMU, explicit extrinsic/time sync. The user's 20Hz
  LiDAR target is an enhanced simulation target after the baseline gates pass.
  Local Sunray is the primary source-code pattern to reuse:
  `external_fusion`, `sunray_control_node`, Mid360/FAST-LIO launch,
  EGO-planner 3D local map, `traj_server`, and `positionCmd2sunray`. RflySim
  confirms the same role split: CopterSim/PX4 computes motion/control,
  RflySim3D/UE renders and generates perception data, ROS/RViz consumes
  sensors and algorithm outputs. WeChat remains default for milestones, but
  latest sends still fail with `weixin: sendMessage: ret=-2 errcode=0`;
  2026-06-02 04:xx checkpoint packet
  `Results/coagent_gateway/progress/ue_uav_realstack_replan_checkpoint_20260602.json`
  was attempted once with the correct `MoSim｜微信通知网关` project and project
  session key, then failed with the same ret=-2. Do one bounded send per
  checkpoint and record the failure.

- 2026-06-02 CST long-run architecture correction is active under
  `UE-UAV-ARCH-REPLAN-20260602-LONGRUN`. The current keyboard/grid-step,
  fake/static point-cloud, and 2D occupancy-grid route is stopped as product
  work. It remains smoke-only for checking ROS/RViz plumbing. The new
  execution rule is to study and reuse real UAV-stack patterns before coding:
  PX4/Gazebo/RFlySim/AirSim/Sunray/Mid360/FAST-LIO first, then MoSim
  integration. Immediate hard contracts: MWORKS owns continuous dynamics,
  controller, truth, IMU, wind/fault/motor-efficiency effects; UE owns
  rendering plus scene/sensor/collision oracle; ROS2 owns LiDAR/IMU/TF,
  FAST-LIO, local 3D map, planner, and RViz2 native review windows. Control
  and setpoints are continuous streams, not grid-cell steps. Baseline sensor
  contract is IMU 200Hz, controller/setpoint 20Hz, Mid360 hardware-faithful
  LiDAR 10Hz at about 200k pts/s, with 20Hz as an explicit enhanced-sim target
  that must pass throughput and localization quality gates. WeChat startup
  notification was attempted with both default and corrected project names;
  the corrected command still failed with
  `weixin: sendMessage: ret=-2 errcode=0`. Do not tight-loop retry; treat
  WeChat as degraded until the gateway runtime is refreshed.

- 2026-06-04 CST Sunray150 PBR minimum loop checkpoint:
  `SUNRAY-PBR-MINILOOP-20260604` now has component-first evidence for the
  carbon frame and accepted tri-blade propeller only. Geometry gates remain
  unchanged: MID-360 scale `0.833527`, propeller source `sunray_cw.stl`,
  orientation `flipped_around_screw_axis`, final translation Z `-0.014052 m`,
  and no UE export. `generate_sunray150_pbr_texture_set.py` generated
  base-color, roughness, and bump maps for both `carbon_fiber` and
  `smoked_propeller`. `render_sunray150_component_material_reviews.py` now
  records the override material's connected texture maps into
  `sunray150_component_material_reviews_manifest.json`; verified targets for
  both `carbon_frame` and `tri_blade_propeller` include `Base Color`,
  `Roughness`, and `Bump`. Latest review images are
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/carbon_frame.png`
  and
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/tri_blade_propeller.png`.
  User correction is recorded: propellers are smoked/transparent plastic, not
  opaque black composite. The WeChat review packet
  `Results/coagent_gateway/packets/sunray_pbr_propeller_review_20260604.json`
  was attempted once through `MoSim｜微信通知网关`, but cc-connect still failed
  with Unix socket `connection refused`; recovery packet:
  `Results/coagent_gateway/recovery/weixin_recovery_required_20260604_150646.json`.
  Await manual review in the main conversation or after WeChat recovery; do
  not mark the PBR loop complete until the human review gate is accepted.

- 2026-06-02 architecture reset: user rejected the current grid-cell keyboard
  movement, static/synthetic point cloud, 2D-only grid, and hand-polished
  mapping route as unsuitable for controller optimization. Product work on
  that route is stopped. The active task is now
  `UE-UAV-ARCH-REPLAN-20260602`: spend the next long run studying upstream UAV
  simulation practice and local source before implementation. Required study
  surfaces are PX4/Gazebo/RFlySim/AirSim/Sunray/Mid360/FAST-LIO. Required
  contracts to settle are continuous MWORKS dynamics/controller authority,
  200Hz IMU, 10Hz hardware-faithful Mid360 LiDAR with 20Hz enhanced-sim target,
  20Hz controller/setpoint path, timestamp/extrinsic synchronization,
  truth-vs-estimate boundaries, RViz2 native point-cloud and 3D map windows,
  and UE as rendering/sensor/collision oracle only. WeChat remains the default
  milestone/blocker notification path; failed sends must be recorded and not
  retried in a tight loop.
  Start-packet WeChat send failed once with
  `weixin: sendMessage: ret=-2 errcode=0`; no tight-loop retry was attempted.
  The design-gate completion packet failed with the same `ret=-2`; record this
  as a WeChat gateway runtime issue, not a reason to retry repeatedly.
- 2026-06-02 FAST-LIO/Mid360 blocker update: dense Factory and Derelict
  Livox-like replay inputs are available, but the selected ROS2
  `spark-fast-lio` runtime cannot consume MoSim's current Mid360 `PointCloud2`
  route with `lidar_type=1`. Source inspection shows its
  `sensor_msgs::msg::PointCloud2` preprocessing path accepts only `OUST64`,
  `KMOUST64`, and `VELO16`; Livox handling is guarded by
  `LIVOX_ROS_DRIVER_FOUND` and expects `livox_ros_driver::CustomMsg`. Factory
  dense runtime smoke recorded zero `/odometry`, `/path`, and
  `/cloud_registered`, with `[FATAL] [Preprocess]: Error LiDAR Type`,
  `No point, skip this scan`, and `TF_OLD_DATA`. Evidence:
  `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_MID360_RUNTIME_BLOCKER.md`.
  Do not tune RViz/grid visuals on this path; choose a Livox CustomMsg-capable
  runtime, a different Mid360-capable FAST-LIO variant, or an explicitly
  degraded non-Mid360 smoke path.
  WeChat notification for this blocker failed once with the same
  `weixin: sendMessage: ret=-2 errcode=0`; no tight-loop retry was attempted.

- 2026-06-02 CST user review correction: current grid-cell movement,
  static/toy point-cloud, and 2D-grid display route is stopped. The next work
  is not RViz point-size tuning or fake frame-rate optimization; it is a
  real UAV stack pass using MWORKS dynamics/controller as authority, UE as
  scene/sensor oracle, ROS2 as LiDAR/IMU/TF/FAST-LIO/local-map middleware, and
  RViz2 native windows for point cloud and 3D map review. Rechecked upstream
  architecture constraints: PX4/ROS2 is a streamed companion-computer contract,
  Livox Mid360 is a Livox serial sensor requiring per-point timing semantics,
  FAST-LIO localization requires synchronized LiDAR/IMU rather than display
  points, and Sunray provides the closest local implementation pattern
  (`external_fusion`, `sunray_control_node`, Mid360/FAST-LIO, EGO 3D local map,
  `positionCmd2sunray`). Added
  `Scripts/UE5/check_spark_fastlio_livox_patch_readiness.py`,
  `Scripts/tests/test_spark_fastlio_livox_patch_readiness.py`, and reports
  `Results/unreal_scene_mapping/SPARK_FASTLIO_LIVOX_PATCH_READINESS.md/json`.
  Current result is `ready=false`: `spark-fast-lio` must patch ROS2
  `livox_ros_driver2` package/header/signature use, Livox macro/callback
  consistency, `imu_buffer_`, and `nanoseconds()` before any Mid360 runtime
  claim. Checks passed:
  `test_spark_fastlio_livox_patch_readiness.py`,
  `test_fastlio_runtime_candidates.py`, and `test_fastlio_input_contract.py`.
  WeChat checkpoint notification was attempted once through
  `CoAgent/gateway/cc_connect_weixin.py` and failed with
  `weixin: sendMessage: ret=-2 errcode=0`; no tight-loop retry was attempted.

- 2026-06-02 UE/ROS2/MWORKS UAV mainline correction: the manual keyboard/grid
  mapping path is smoke-only and must not be polished as the product path. User
  rejected grid-cell movement, synthetic/static point clouds, oversized RViz
  points, and 2D-only grid review as unsuitable for controller optimization and
  real UAV simulation. Current goal is a continuous multi-rate UAV loop:
  MWORKS owns dynamics/controller/IMU/truth, UE owns rendering and scene/sensor
  oracle, ROS2 owns LiDAR/IMU/TF/FAST-LIO/local 3D map/planner topics, and
  RViz2 owns point-cloud/map/planner review. Sunray local source is the primary
  contract reference: `external_fusion` + `sunray_control_node` +
  Mid360/FAST-LIO + EGO planner + `positionCmd2sunray` +
  `/uav1/sunray/uav_control_cmd`. First implementation target is Factory only,
  MWORKS-first continuous state/IMU bridge, Mid360-shaped LiDAR at 10Hz
  baseline then 20Hz target, IMU 200Hz, controller/setpoint 20Hz, and 3D local
  map review. Design source: `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md`.

- 2026-06-01 Windows-native Codex CLI is installed for explicit Windows shell
  use. The installed launcher is `C:\Users\HP\.codex\bin\codex.cmd` pointing to
  `C:\Users\HP\.codex\bin\codex.exe`, copied from the VSCode extension
  `windows-x86_64` binary, and the Windows user PATH includes that bin
  directory. Windows config was generated from `/home/linux/.codex/config.toml`
  with path conversion: MoSim project paths are `C:\...`, Sysplorer/Syslab MCP
  use Windows-native MWORKS executables, and WSL-only MCP wrappers are launched
  through `C:\Windows\System32\wsl.exe -d Ubuntu-22.04 --exec ...`. Verification
  passed with `codex --version` (`codex-cli 0.135.0-alpha.1`), `codex mcp list`
  showing 8 servers, and `codex doctor` loading config/auth/provider/MCP
  successfully. Remaining doctor warnings are non-fatal: missing Windows
  `rg.exe`, stale historical rollout index rows, unrestricted sandbox, and an
  update probe timeout. Detailed route:
  `Docs/Workflows/debug_mcp.md#51-install-windows-native-codex-cli-from-wsl-config`.

- 2026-06-01 ROS-MCP diagnosis: the installed project checkout is
  version-agnostic and supports ROS1/ROS2 through rosbridge, but this WSL host
  should use ROS2 Humble. Current checks show `ROS_VERSION=2`,
  `ROS_DISTRO=humble`, `rviz2` and `turtlesim` installed, ROS apt source
  `/etc/apt/sources.list.d/ros2.list` using the TUNA ROS2 jammy mirror, keyring
  `/usr/share/keyrings/ros-archive-keyring.gpg` fingerprint
  `C1CF 6E31 E6BA DE88 68B1 72B4 F42E D6FB AB17 C654`, and a temporary
  `apt-get update` probe passed without `NO_PUBKEY` or `EXPKEYSIG`.
  `rosbridge_server` / `ros-humble-rosbridge-suite` is now installed and port
  `9090` is listening after manual launch. `/home/linux/mcp-wrappers/ros_mcp.sh`
  now auto-starts `rosbridge_websocket` in the background when Codex starts
  ROS-MCP and port `9090` is absent, so a separate rosbridge terminal should not
  be required for normal MCP use.

- 2026-06-01 VSCode Codex plugin load failure root cause: the extension was
  launching the Windows Codex runtime against `C:\Users\HP\.codex`, whose
  `state_5.sqlite` migration checksums were written by the WSL/Linux Codex
  runtime. The fatal log was `migration 1 was previously applied but has been
  modified`, so the webview could not load. The minimal fix was to back up VS
  Code `settings.json` and set
  `chatgpt.runCodexInWindowsSubsystemForLinux=true`, matching the project
  policy that VSCode Codex runs WSL-backed. After reload, logs showed
  `Spawning codex process inside WSL` and `app routes mounted`; remaining
  warnings are non-fatal auth/plugin-sync, old-workspace watcher, or MCP
  resource-list compatibility messages. Do not delete Codex `state_5.sqlite`
  for this issue without a backup; it contains visible thread metadata and
  token counters. Detailed recovery is in
  `Docs/Workflows/debug_mcp.md#41-vscode-codex-fails-on-sqlite-migration-checksum`.
  Later the standalone Windows Codex App showed the same
  `Codex cannot access its local database` / `migration 1 was previously
  applied but has been modified` dialog. Final root cause was mixed SQLite
  migration checksums across the Windows App runtime and Windows CLI/state
  helpers sharing `C:\Users\HP\.codex`: `state_5.sqlite` was eventually
  compatible, but `logs_2.sqlite`, `goals_1.sqlite`, and `memories_1.sqlite`
  still had incompatible migration-1 checksums. Windows CLI was isolated to
  `C:\Users\HP\.codex-cli` by setting `CODEX_HOME` in
  `C:\Users\HP\.codex\bin\codex.cmd`; the App keeps `C:\Users\HP\.codex`.
  Backed up and moved the incompatible split DB families to
  `C:\Users\HP\.codex\backups\windows_app_split_sqlite_reset_20260601_183309`.
  Direct `app-server` smoke no longer exits with SQLite migration errors,
  `doctor` reports all four DBs healthy and rollout/state inventory agrees,
  and the Windows Codex App opens to the normal chat UI. WSL primary state at
  `/home/linux/.codex/state_5.sqlite` was not touched.

- 2026-06-01 ROS2 runtime setup: current host is Ubuntu 22.04.5 WSL2, so the
  UE mapping/runtime branch must use ROS2 Humble/RViz2 rather than trying to
  install ROS1 Noetic directly. FishROS was inspected and its public bootstrap
  delegates to an interactive installer; project automation will use the
  official ROS2 Humble apt route, with FishROS kept as a manual fallback. The
  setup and evidence boundary are recorded in
  `Docs/Workflows/ros2_runtime_setup.md`. Installation touches external system
  paths such as `/etc/apt`, `/opt/ros/humble`, and apt caches as an explicit
  project-infrastructure exception. Current ROS2 status: Humble/RViz2/colcon
  are installed and project preflight reports `ros_generation=ros2`,
  `ros2_replay_ready=true`, and no ROS2 blockers. The ROS apt key and source
  issue is resolved: keyring is
  `/usr/share/keyrings/ros-archive-keyring.gpg`, source is
  `https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu jammy main`, and apt update
  has no `NO_PUBKEY` or `EXPKEYSIG` error. The local `References/Lab/FAST_LIO`
  package remains ROS1/Catkin-only, but the native ROS2 `spark-fast-lio`
  candidate builds and has produced real runtime topics
  `/cloud_registered`, `/odometry`, and `/path`. FAST-LIO runtime is therefore
  no longer blocked by ROS2 installation or key state. Derelict now has a real
  ROS2 FAST-LIO numeric pass with warnings; Factory remains degraded and cannot
  be claimed. Headless ROS2 runtime smoke passed for Factory input topics using
  `run_fastlio_rviz_replay_ros2.sh` with `START_RVIZ=0 START_FASTLIO=0` and
  `check_fastlio_ros2_topics.sh` with `REQUIRE_FASTLIO_OUTPUTS=0`.
  Follow-up topic-boundary update added `/mosim/replay_odometry` to the ROS2
  replay publisher, planning RViz2 window, overview RViz2 window, and input-side
  topic smoke check. This topic is only replay/reference pose for operator
  review; it must not be counted as FAST-LIO `/Odometry`.
  Added `Scripts/UE5/check_fastlio_family_compatibility.py` and
  `Scripts/tests/test_fastlio_family_compatibility.py`; latest evidence
  `Results/unreal_scene_mapping/FASTLIO_FAMILY_COMPATIBILITY.md/json` reports
  `FAST_LIO`, `FAST-LIVO2`, and `Point-LIO-point-lio-with-grid-map` are all
  `ros1_catkin_only`, `ros2_candidate_count=0`, and
  `fastlio_ros2_runtime_claimable=false`. Keep `START_FASTLIO=0` on the ROS2
  wrapper until a ROS2 FAST-LIO-family package or approved bridge route exists.
  Added project-local ROS2 launch package `Scripts/ros/mosim_scene_replay` and
  wrapper `Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh`. The wrapper
  builds the launch package under ignored
  scene-specific `Results/tmp/mosim_scene_replay_ros2_ws_<scene>` workspaces
  and runs `ros2 launch` for both accepted scenes. Scene-specific workspaces
  avoid concurrent Factory/Derelict smoke tests deleting each other's build
  outputs. Verified short launch smoke with `START_RVIZ=0`,
  `START_FASTLIO=0`, `MAX_FRAMES=3`, `LOOP=0`, plus topic smoke with
  `REQUIRE_FASTLIO_OUTPUTS=0`.
  Added `Scripts/UE5/prepare_spark_fastlio_ros2_candidate.sh` for a ROS2
  FAST-LIO2-family candidate based on MIT SPARK `spark-fast-lio`, staged only
  under ignored `Results/tmp`. Current host state is native ROS2 Humble with
  `/opt/ros/humble/bin/ros2`, `/opt/ros/humble/bin/rviz2`, `/usr/bin/colcon`,
  ROS apt key `/usr/share/keyrings/ros-archive-keyring.gpg`, and ROS2 jammy
  apt source `https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu`. The
  `spark-fast-lio` candidate builds successfully under
  `Results/tmp/spark_fast_lio_ros2_ws`, and executable
  `install/spark_fast_lio/lib/spark_fast_lio/spark_lio_mapping` exists.
  Runtime probe starts `spark_lio_mapping` with MoSim remapped topics
  `/mosim/lidar_points` and `/mosim/forward/imu`; ROS graph and recordings show
  `/cloud_registered`, `/odometry`, and `/path`. Fixed
  `publish_fastlio_replay_ros2.py` so `--wall-time --loop` uses a monotonic
  global sequence across replay cycles instead of resetting timestamps and
  triggering FAST-LIO IMU/LiDAR loopback clearing. Added project-local
  `ROS_LOG_DIR=Results/tmp/ros_logs` handling so ROS2 launch/rclpy logs do not
  fail when `/home/linux/.ros/log` is read-only. Added a MoSim-specific
  `spark_fast_lio_mosim.launch.py` with identity LiDAR/IMU extrinsics instead
  of the upstream MIT campus transform. Current runtime evaluation:
  Factory fails with RMSE `9.761 m` and max error `18.547 m`;
  Derelict passes with RMSE `0.814 m` and max error `1.938 m`, but runtime logs
  still include IMU sufficiency warnings and odometry timestamps are partly
  nonmonotonic. Treat Derelict as a numeric runtime pass with quality warnings,
  and Factory as degraded.

- 2026-06-01 mapping-window correction: user rejected HTML point-cloud review.
  The project policy is now explicit in `Docs/Workflows/unreal_renderer.md`:
  UE/MoSimSceneLibrary is the rendered-scene window; RViz/RViz2 or equivalent
  native robotics tooling is the point-cloud, occupancy/grid-map, TF, odometry,
  FAST-LIO, and planner-state window. HTML may only be an optional offline
  report preview, never the active map/point-cloud review surface. This matches
  the checked RflySim, AirSim, PX4/Gazebo, Gazebo ROS, FAST-LIO, and FAST-LIVO2
  patterns. The mapping surface may be one RViz/RViz2 window with multiple
  displays or separate native windows for 2D grid/local-plan and 3D
  point-cloud/FAST-LIO review; the operator-facing default is now
  `RVIZ_PROFILE=split`, which opens `Config/rviz2/mosim_uav_planning_grid.rviz`
  and `Config/rviz2/mosim_uav_fastlio_pointcloud.rviz` as separate native RViz2
  windows. It is still not browser HTML. ROS2 replay inputs are available, but
  FAST-LIO output evidence still requires a real FAST-LIO-family runtime.
  Supporting research and local-source evidence are now separated into
  `Docs/Workflows/unreal_mapping_window_research.md`.

- 2026-06-01 UE scene truth/mapping minimal loop: added
  `Scripts/UE5/scene_truth_pipeline.py` and
  `Scripts/tests/test_scene_truth_pipeline.py`. The pipeline consumes the
  accepted Factory and Derelict collision-truth JSON files, builds flight-height
  occupancy grids, runs an unknown-global-map receding A* planner, simulates
  LiDAR frames, writes merged point clouds, writes
  `fastlio_handoff.json`, writes `render_replay.csv`, and now writes
  per-frame `local_known_map_frames.jsonl`, `local_plan_frames.jsonl`, and
  `lidar_point_frames.jsonl` for UE runtime replay. Point-cloud review is no
  longer routed through HTML: the accepted architecture is UE for the rendered
  scene window and ROS/RViz or equivalent native tooling for PointCloud2,
  occupancy/grid-map, TF, odometry, and planner-path windows. Added
  `Config/rviz2/mosim_uav_mapping.rviz`,
  `Config/rviz2/mosim_uav_planning_grid.rviz`,
  `Config/rviz2/mosim_uav_fastlio_pointcloud.rviz`,
  `Scripts/ros/publish_mosim_mapping_replay_ros2.py`, and
  `Scripts/UE5/open_mapping_rviz_ros2.sh`. Current outputs:
  `Results/unreal_scene_mapping/RUN_SUMMARY.md`,
  `Results/unreal_scene_mapping/factoryenvironmentcollect/*`, and
  `Results/unreal_scene_mapping/derelictcorridormegascans/*`. Latest verified
  output after the controller-tracking clearance pass: Factory
  `path_cells=34`, `lidar_points=1934`,
  `global_truth_available_to_planner=false`,
  `collision_free_against_truth=true`,
  `buffered_collision_free_against_truth=true`; Derelict `path_cells=45`,
  `lidar_points=2068`, `global_truth_available_to_planner=false`,
  `collision_free_against_truth=true`,
  `buffered_collision_free_against_truth=true`. `stream_unreal_udp.py` now sends
  evidence-backed local-known-map cells, local planner frames, and LiDAR point
  frames to UE for optional rendered debug overlays. The primary
  point-cloud/grid-map review window remains RViz or equivalent native
  robotics tooling, not UE-internal mesh rendering or browser HTML. Checks
  passed: `python3 Scripts/tests/test_scene_truth_pipeline.py`,
  `python3 Scripts/tests/test_fastlio_replay_adapter.py`,
  `Scripts/UE5/build_unreal_renderer.sh`, and short live review loops for both
  accepted scenes. UE log evidence: Factory first frame has
  `local_map_cells=137`, `lidar_points=176`, `local_map_evidence=true`,
  `lidar_evidence=true`; Derelict first frame has `local_map_cells=320`,
  `lidar_points=166`, `local_map_evidence=true`, `lidar_evidence=true`.
  FAST-LIO adapter outputs are generated and current status is
  `ready_for_ros2_replay`; do not claim completed FAST-LIO localization because
  the runtime output topics still require a real FAST-LIO-family package.
  Runtime readiness is now checked by
  `Scripts/UE5/check_unreal_scene_runtime_readiness.py --write`, which writes
  `Results/unreal_scene_mapping/UE_SCENE_RUNTIME_READINESS.md/json`. Latest
  preflight reports `file_loop_ready=true` for both accepted scenes and
  `runtime_ready=false` only because `unreal_editor_listener_unavailable`.
  ROS1/Catkin/FAST_LIO is now a degraded compatibility warning, not a ROS2
  replay blocker. Treat that report as the current guard
  against confusing offline/file artifacts with native RViz/FAST-LIO runtime
  evidence.
  Added `Scripts/UE5/run_fastlio_rviz_replay_ros1.sh` and
  `Scripts/UE5/check_fastlio_ros1_topics.sh` so the next machine/session with a
  sourced ROS1/Catkin/FAST-LIO environment can start the native RViz/FAST-LIO
  replay and verify runtime topics (`/velodyne_points`, `/imu/data`,
  `/mosim/local_occupancy_grid`, `/mosim/local_plan`, `/cloud_registered`,
  `/Odometry`). Current session can only pass their `DRY_RUN=1` contracts.
  Added `Scripts/UE5/bootstrap_fastlio_ros1_workspace.sh` as the standard
  project-local bootstrap route for an already installed/sourced ROS1 Catkin
  environment; it wires `References/Lab/FAST_LIO` into ignored
  `Results/tmp/fastlio_ros1_ws`, builds with `catkin_make`, then reruns the ROS
  mapping preflight. Added `Scripts/UE5/open_unreal_editor_mcp_listener.sh` as
  the standard UE Editor MCP listener entrypoint; it opens
  `MoSimSceneLibrary.uproject` in Editor mode and polls port 55557 for up to 60
  seconds. Use their `DRY_RUN=1` contracts before real GUI/runtime attempts.
  Do not run `prepare_fastlio_replay.py` concurrently with publisher dry-runs
  for the same scene; it rewrites JSONL/manifest files and concurrent readers
  can hit partial-line decode errors.
  Added `Scripts/UE5/build_scene_runtime_bundle.py` and
  `Scripts/tests/test_scene_runtime_bundle.py`; each accepted scene now has
  `runtime_review_bundle.json`, `runtime_review_bundle.md`, and
  `run_native_runtime_review.sh`. The generated wrapper now starts the UE
  rendered-scene review and RViz/FAST-LIO native review as background processes
  so the intended two-window runtime layout is not serialized behind the UE
  review loop. The bundle is an execution contract that gathers UE
  rendered-scene review, RViz mapping-window review, FAST-LIO runtime launch,
  FAST-LIO recording/evaluation, truth-policy flags, and manual acceptance
  gates. Current bundle status is
  `blocked_runtime_dependencies` for both accepted scenes only because the UE
  editor listener is unreachable; the ROS2/RViz2 replay path is ready. Added
  `Scripts/UE5/check_ros_mapping_runtime_env.py` and
  `Scripts/tests/test_ros_mapping_runtime_env.py`; latest report
  `Results/unreal_scene_mapping/ROS_MAPPING_RUNTIME_ENV.md/json` reports
  `ready_for_native_mapping_runtime=true`, `ros_generation=ros2`, and
  `ros2_replay_ready=true`. Missing ROS1/RViz/Catkin tools and local
  `fast_lio` package visibility are now degraded compatibility warnings, not
  blockers for ROS2 replay input review. This is deliberate: it prevents
  treating file artifacts, UE overlays, or HTML as completed FAST-LIO/RViz
  runtime evidence while allowing RViz2 input/map review to proceed.
  Follow-up control-interface packaging is now generated by
  `Scripts/UE5/build_navigation_handoff.py` and guarded by
  `Scripts/tests/test_navigation_handoff.py`. Each accepted scene now has
  `navigation_control_handoff.json`, `control_reference.csv`,
  `planned_quintic_reference_params.json`,
  `planned_quintic_reference_constructor.mo.txt`,
  `control_interface_package.json`, and an inactive `scenario_draft.yaml`.
  The generated reference speed is now capped at `0.8 m/s` with
  `min_segment_duration_s=0.9` so the MWORKS smoke controller can track the
  path without early termination. Factory produces `n_segments=33`,
  `stop_time_s=31.3258252147`; Derelict produces `n_segments=44`,
  `stop_time_s=39.6`. Concrete Sysplorer smoke models now consume these
  references: `QuadrotorExperiments.Sunray150UEFactoryLinearMPCSysblockSmoke`
  and `QuadrotorExperiments.Sunray150UEDerelictLinearMPCSysblockSmoke`. MCP
  evidence passed for both (`check_model ok`, `simulate_model ok`), with
  metrics `quality_status=smoke_only`, Factory `rows=628`, Derelict
  `rows=793`. Strict UE-truth collision gate passed for both scenes:
  actual/reference occupied samples are `0/0`, with minimum actual clearance
  about `0.95 m` for Factory and `0.79 m` for Derelict. These results validate
  the scene-truth -> unknown-map planner -> controller-interface smoke chain;
  they are still not final autonomous navigation, final FAST-LIO localization,
  or full performance evidence. `Scripts/UE5/summarize_scene_closed_loop.py`
  now aggregates this state into
  `Results/unreal_scene_mapping/UE_SCENE_CLOSED_LOOP_STATUS.md/json`; latest
  aggregate status is `ready_smoke_validated`; current per-scene warning is
  `fastlio_ros1_compat_unavailable`, while ROS2 replay status is
  `ready_for_ros2_replay`.
  Latest live-editor automation probe: `mosim-unreal` can read project context and finds `UE_5.5` plus
  `UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject`, but editor listener
  `127.0.0.1:55557` is still refused and no callable WindowsMCP namespace is
  exposed in this Codex tool surface. Continue file-level/standalone review
  work until a reversible editor probe passes.

- 2026-06-01 Factory review point correction: user confirmed the review camera
  no longer passes through walls, but the old Factory start point prevented
  entry into the real map area. Diagnosis found the previous
  `(-4750, 3850, 180) cm` point intersected a CargoCar collision proxy.
  Factory `review-scene` now forces
  `/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode` and starts near the
  map-authored `PlayerStart` at `(-5533, 2423, 190) cm`, with camera collision
  enabled. Follow-up fix also forces PlayerController possession to
  `MworksReviewCameraPawn` during `-MoSimSceneReview` and disables imported
  Pawn input, because Factory can otherwise hand control to its robot/forklift
  actors. Latest log confirms `/Game/Maps/Demonstration`, MoSim GameMode,
  `MWORKS scene-review control enforced`, `pawn=MworksReviewCameraPawn_0`,
  `disabled_imported_pawns=3`, preview/playback disabled, and the new start
  point. Manual review passed: Factory now moves with the review camera instead
  of the imported robot.

- 2026-06-01 Derelict initial-position correction: `DerelictCorridor` review
  no longer relies on the generic MoSim default camera or the previous high
  exterior overview point. Its default review camera is now placed inside the
  exported truth bounds on a terrain/floor patch at approximately
  `(8704, -2240, 220) cm` with yaw `90 deg`; this corresponds to truth-space
  `(~87.04, 22.40, 2.20) m` before final UAV/path planning validation.
  `review-scene` now appends the MoSim GameMode override to any `/Game/...` map
  argument, not only Factory, so imported maps cannot bypass the review camera
  contract through map-local GameMode settings.
  Manual review passed: Derelict is now visible and controllable with the
  review camera.

- 2026-06-01 ElectricDreams first renderer review is deferred. The source has
  an explicit collision-truth artifact, but both
  `/Game/Levels/PCG/ElectricDreams_PCGCloseRange` and
  `/Game/Levels/ElectricDreams_Env` produced black/non-reviewable windows in
  the current `MoSimSceneLibrary` runtime. Logs show long first-time
  static-mesh/Nanite builds plus Blueprint/PCG compile errors involving stale
  functions such as `Generate`, `Cleanup`, `NotifyPropertiesChangedFromBlueprint`,
  `SkipBlends`, and missing drone/player blueprint pins. Do not spend further
  one-map review time on ElectricDreams until there is a dedicated
  compatibility fix or manual editor-assisted repair.

- 2026-05-31/2026-06-01 UE scene integration current state:
  `FactoryEnvironmentCollect` and `DerelictCorridorMegascans` are the only
  current main rendered-map candidates that passed manual visual review and have
  valid explicit collision-truth artifacts. All other tested local scene sources
  are rejected/deferred for the immediate linked-content route and need
  dedicated conversion, plugin/source integration, relighting, or asset-cache
  warm-up before they can return to the main map set.
  `Scripts/UE5/activate_renderer_scene_source.py --scene-source-id
  <scene_source_id>` switches renderer Content links to the
  selected source; do not mount all scene projects at once because `/Game/Maps`,
  `/Game/Meshes`, `/Game/Blueprints`, etc. conflict across samples. Factory
  truth artifact
  `UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json`
  validates with 8658 collision proxies; renderer load proof
  `Results/tmp/renderer_map_load_probe_factory_active_20260531.json` loaded
  `/Game/Maps/Demonstration` with 11872 actors inside the MoSim renderer.
  Derelict truth artifact
  `UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/derelictcorridormegascans_collision_truth.json`
  validates with 4753 collision proxies and launches with
  `/Game/DerelictCorridor/Maps/DerelictCorridor` when that source is active.
  `AMoSimSceneLibraryGameMode` previously auto-spawned the old generated
  `MworksData/map_open_blocks_render_map.json` preview map on top of every real
  scene; use `Scripts/UE5/open_unreal_renderer.sh review-scene` or pass
  `-MoSimSceneReview` for manual map review so the old preview/STL/blockout map
  and playback actor are disabled. Visual review policy has also tightened:
  current product maps should be white/daytime visible by default. If a scene
  only works as a dark/exploration map even after balanced scene-review
  fill light and corrected camera placement, mark it as a
  special indoor/radar candidate rather than a main rendered map.
  `ElectricDreamsEnv` also has a truth artifact, but it has not passed rendered
  manual review. `CityParkEnvironmentCollec`, `CitySample`,
  `DarkRuinsMegascansSample`, `MedievalVillageMegascansS`, and
  `ABoyandHisKite` are not current main rendered-map candidates.
  `check_ue_fab_goal_acceptance.py` and `check_unreal_bridge.py` must validate
  the currently activated source/content link, not hard-coded Derelict.
  Manual visual review: user confirmed Factory and Derelict are visible and
  controllable with the review camera after start-position and possession fixes.
  A too-aggressive forced-exposure retry on Derelict previously produced a
  pure-white viewport, so forced exposure is not the default review path.
  Review-camera collision is now required: manual map review must not use a
  camera that can pass through walls or exterior boundaries. The review pawn
  uses a collision sphere and swept movement so blocked walls are visible during
  inspection. This is only a runtime review guard; final UAV motion and path
  planning still need exported collision/occupancy truth checks so planned
  trajectories cannot collide with walls.

- 2026-05-31 CoAgent DevOps Git delegation: user manually deleted the old
  DevOps goal; MainAgent sent one complete visible charter to
  `MoSim｜DevOps 发布` thread `019e74de-a452-7a50-99e7-ca9a247b32f1` for
  `COAGENT-DEVOPS-GIT-DIVIDE-20260531`, but the first foreground
  `timeout 60s codex exec resume ...` delivery killed the worker process after
  message delivery. Corrected route: start the visible DevOps resume as a
  background process without an outer 60s kill and record PID/logs under
  `Results/coagent_transport/runs/`. Current corrected DevOps run started as
  PID `11167` from
  `Results/coagent_transport/COAGENT-DEVOPS-GIT-DIVIDE-20260531_visible_background_prompt_20260531_124300.txt`.
  Do not repeatedly tick the DevOps thread; recover from
  `Docs/Workflows/agent_task_ledger.md` and collect a flat result packet when a
  phase ends. The old npm/node16 Codex shim fails with
  `SyntaxError: Unexpected reserved word`; visible dispatch should use the
  VSCode extension Codex binary resolved by `command -v codex`.

- 2026-05-30 CoAgent open-source adoption design pass: added
  `References/Agent/Gateway/cc-connect` as the first Gateway candidate after the
  user moved the desktop copy into the project. Current design direction:
  CoAgent should not be built fully from scratch and no mirrored upstream is a
  complete replacement. Keep CoAgent-owned task ledger, packet contracts,
  context packs, safety gates, and MoSim evidence rules; selectively reuse or
  port CodexMonitor for Codex UI/control-plane ideas, OpenMOSS for
  task/review/patrol model, ClawTeam for inbox/worktree communication,
  cc-connect for human-intervention Gateway, and Hermes/OpenClaw for
  memory/skills/hooks/operator patterns. Broad `git status --short` became slow
  with the large untracked reference tree and was stopped; use path-scoped Git
  status/diff or the reference index validator for reference-tree checks.

- 2026-05-30 CoAgent implementation miniloop reached human review:
  `COAGENT-IMPL-MINILOOP-01`. The previous architecture long-run runtime task
  `COAGENT-ARCH-LONGRUN-01` was cancelled because the user redirected the work
  from design-only artifacts to approved implementation. Current implemented
  scope: goal-alignment doctor, runtime `update-metadata`, active-department
  automation mapping, reference index repair, and doctor health wiring. Latest
  doctor result: `Results/coagent_doctor/latest.json` reports
  `overallStatus=ok` with 23 ok checks, 0 warnings, and 0 failures. Still gated:
  app-server transport, unattended automation, new permanent departments,
  broad hook rewrites, MCP/tool expansion, external credentials/config, and
  destructive reference cleanup. Current state: stop for user review before
  expanding scope.

- Current active goal: design and advance MoSim as an RflySim-like UAV
  simulation product. MWORKS/Sysplorer/Syslab remain the authoritative solver,
  controller, planner, disturbance, metric, and event-log source; UE5 provides
  high-quality scene rendering, camera, radar/point-cloud overlays, trajectory
  display, and video recording. MCP automation should cover scene inventory,
  scene import/reuse, UE editing, truth export, simulation streaming, evidence
  generation, and pre-review checks where practical.
- Current UE/Fab decision boundary: first attempt automation through
  `mosim-epic` and `mosim-unreal`; if Fab/Launcher/UE automation
  cannot reliably produce local editable content, renderer load proof, and
  planning truth, stop that route and use
  `References/UnrealScenes` as the scene source. Login/authorization/download
  prompts and final visual review remain manual-intervention points.
- 2026-05-24 Unreal map reset: stop improving all old generated blockout,
  grid, STL, semantic-box, RflySim direct-mount, factory-review, and
  YunZong/Sunray primitive-reconstruction maps. The old routes have been
  cleaned from `UE5/` except for the reusable renderer/bridge shell.
  Current map work must start from real editable Unreal/Fab/Epic/open-source
  scene assets with physical-world visual language, then connect the existing
  MWORKS playback bridge after the map itself passes manual review.
- Current map-source priority: use downloaded Fab/Epic/free UE assets such as
  factory/warehouse, forest/park, indoor corridor/cave, city/building, and open
  outdoor scene packs. Do not reconnect quadrotor, radar, trajectory, UDP, or
  MWORKS simulation until the selected map source is visually acceptable.
- Current tool-capability scope is intentionally narrow: implement and operate
  only `mosim-unreal` for live UE Editor authoring through the
  `Docs/Skills/Unreal/mosim-unreal` implementation, and
  `mosim-epic` for Epic/Fab/Launcher inventory, scene-source registry, and
  Fab/import feasibility. Do not expand this phase into
  MWORKS, external renderer bridges, downloader automation, or a full simulator
  MCP unless explicitly requested.
  Use `Scripts/UE5/check_epic_library_inventory.py` for a cheap health check
  and `Scripts/UE5/epic_library_view.py` for the merged human-readable library
  view. The project-owned MCP wrapper for this boundary is
  `Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh`.
- 2026-05-25 MCP route update: the live UE Editor implementation is now
  `Docs/Skills/Unreal/mosim-unreal/`. The intended configured MCP server
  key is `mosim-unreal`, and it should point to
  `Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh`; the legacy
  Flopperam wrapper remains in the same project for rollback. Current
  MoSim-native UE tools are `ue_health`, `project_context`,
  `editor_listener_health`, `asset_search`, `list_maps`,
  `current_level_summary`, `find_level_actors`, `reversible_actor_probe`,
  `scene_source_status`, `scene_truth_export_plan`, `editor_log_summary`, and
  `tool_boundary`.
  `current_level_summary` and `find_level_actors` are live-editor read-only
  tools and may return `ok=false` when UE is closed; this is a diagnostic state,
  not an MCP startup failure. `reversible_actor_probe` is plan-only by default;
  execute it only after loading a real review map. `scene_source_status` is
  compact by default; use detailed output only for targeted review. Epic/Fab
  inventory, scene-source registry, scene-source acceptance gates, and
  Launcher/Fab readiness belong to `mosim-epic`, not `mosim-unreal`.
- 2026-05-25 MCP wrapper fix: `/home/linux/mcp-wrappers/sysplorer_mcp.sh`
  previously pointed at `C:\Users\HP\Desktop\Quadrotor\scripts\...` and caused
  `sysplorer` handshake failures after the MoSim restructure. It should point to
  `C:\Users\HP\Desktop\MoSim\Scripts\mworks\sysplorer_mcp_wsl_entry.py`.
- 2026-05-26 Codex App config fix: Codex App was unreliable when the
  Windows-side config was absent. Keep `/home/linux/.codex/config.toml` as the
  canonical source, but copy it to `C:\Users\HP\.codex\config.toml` when the
  Windows App requires a local config. Do not hand-edit the Windows copy. The
  Windows default WSL distro should remain `Ubuntu-22.04`. Verification
  command: `/mnt/c/Users/HP/.codex/bin/wsl/codex mcp list`, which should show
  `mosim-epic` and `mosim-unreal` plus filesystem/git/syslab/sysplorer.
- 2026-05-26 Codex App session policy: keep this WSL-backed conversation as the
  primary project conversation. Codex App is currently used as a Windows desktop
  review/front-end surface and for opening other project conversations. Even if
  the App appears to receive live updates, durable state must still be written
  to repo docs, not trusted to chat sync. Manual one-way session handoff from
  WSL to App requires copying the selected JSONL, fixing stale `cwd` values, and
  updating `C:\Users\HP\.codex\state_5.sqlite`; do not attempt live
  bidirectional session writes.
- 2026-05-26 Codex App manual-thread test: manually writing App-local
  `state_5.sqlite` rows and short `rollout-*.jsonl` files made conversations
  visible only in Codex App and produced stale-path resume errors. This route is
  rejected. Do not directly create department/task conversations in the Windows
  App database. Create them from the WSL/VSCode Codex environment first, then let
  Codex App display the synced conversation.
- 2026-05-26 Codex App department threads: removed over-split role threads and
  replaced the old "secretary owns everything" model with a clearer operating
  model:
  `MoSim｜主线总控` for user dialogue and integration,
  `MoSim｜调度中台` for task tickets/status board/routing,
  `MoSim｜文档秘书部` for decisions and docs,
  `MoSim｜研发工程部` for implementation/research,
  `MoSim｜验证测试部` for evidence gates,
  `MoSim｜安全合规部` for boundary/secret/license/large-file safety, and
  `MoSim｜DevOps 发布部` for Git. Do not create persistent App threads for every
  narrow role; create dedicated task conversations only for long-running
  high-context tasks with a parent department, task_id, stop condition, and
  result-packet contract.
- 2026-05-26 Codex App conversation rollback: after App resume failures, backed
  up the broken local department-thread state to
  `C:\Users\HP\.codex\backups\revert-app-local-department-threads-20260526-123853`,
  removed the manually seeded App-only department/test conversations, cleaned the
  short 2026-05-26 rollout files, and restored the App sidebar index to the
  original main project thread `四旋翼无人机图形化仿真系统`. Future department or
  dedicated-task conversations must be created from WSL/VSCode Codex, not by
  direct SQLite/JSONL injection into the App.
- 2026-05-26 Codex App department-thread sync: created six real WSL-origin
  department conversations with `codex exec`, normalized their WSL thread titles
  and `cwd`, copied the existing WSL rollout files into the Windows Codex App
  session store, and upserted matching App thread rows. Backup before sync:
  `C:\Users\HP\.codex\backups\wsl-department-thread-sync-20260526-130607`.
  This first ID set was later superseded by the real deleted-UI rollout threads
  listed below.
- 2026-05-26 Codex App/VSCode visibility correction: the first WSL-origin
  department sync still did not appear in either UI because `codex exec`
  generated background-style rows (`source=exec`, `has_user_event=0`) and the
  WSL `session_index.jsonl` did not include the six department IDs. Backed up
  both WSL and Windows state/index files to
  `C:\Users\HP\.codex\backups\visibility-fix-20260526-142902`, then normalized
  both sides: added the six department rows to WSL and Windows
  `session_index.jsonl`, set `source=vscode`, `thread_source=vscode`,
  `has_user_event=1`, `archived=0`, and verified every `rollout_path` exists.
  If the UI still does not show these threads after a refresh/restart, treat
  `codex exec` bootstrap as insufficient for durable department conversations
  and create future department/task threads through a real interactive
  WSL/VSCode Codex conversation before handoff to Codex App.
- 2026-05-26 deleted-UI rollout communication correction: internal
  `spawn_agent` calls are not department communication. The deleted-UI rollout
  threads currently used by the UI are:
  `019e6335-a2e2-7b92-b9f8-396400f4429e` (`MoSim｜总经办 PMO`),
  `019e6318-4516-72c1-a50a-a36dc2aed215` (`MoSim｜调度中台`),
  `019e6319-fecd-7bd1-a4d5-7a5207e0ddba` (`MoSim｜研发工程部`),
  `019e631b-c6b2-73e3-9ad9-551b12687fe0` (`MoSim｜文档秘书部`),
  `019e631d-8164-72e3-aac5-4ee3d91e462e` (`MoSim｜验证测试部`),
  `019e631f-406e-7401-af17-8f17e09a50e3` (`MoSim｜安全合规部`), and
  `019e6321-1940-7bc0-8a97-f2720aa8af1b` (`MoSim｜DevOps 发布部`). Dispatch to a
  deleted-UI rollout by `codex exec resume <thread_id>` plus
  `--output-last-message`; do not represent an internal subagent as that
  department. Communication probe `comm-probe-20260526-01` to DevOps returned
  `DEVOPS_COMM_OK｜received_from_main｜task_id=comm-probe-20260526-01`.
- 2026-05-26 deleted-UI rollout metadata fix: `codex exec resume` failed when
  WSL-side DevOps thread metadata was normalized to `source=vscode` /
  `thread_source=vscode`, reporting `unknown thread source: vscode`. The
  working split is WSL-side `source=cli`, `thread_source=user` for resume
  communication, and Windows App-side `source=vscode`, `thread_source=vscode`
  for task-list visibility. Regression probe
  `DEVOPS-VISIBLE-PROBE-20260526-03` returned
  `DEVOPS_VISIBLE_ACK｜task_id=DEVOPS-VISIBLE-PROBE-20260526-03` and was then
  copied to the Windows rollout/index/state for UI inspection.
- 2026-05-26 long-running task conversation policy: tasks like PX4-log-based
  Sunray150 parameter identification should not be delegated to disposable
  Codex subagents. They should run as dedicated Codex App/VSCode conversations
  under the Project Department, while this primary conversation continues to
  integrate results and report to the user. Subagents remain useful only for
  bounded read/review/execution slices that return one structured result.
- 2026-05-26 recurring automation policy: Codex App automations may be used for
  daily workflow/skills improvement, external-repo update checks,
  documentation drift checks, and safety scans after their behavior is verified
  for the installed App version. Automation notifications are triggers, not
  durable project state; convert outputs into task tickets or evidence files.
- 2026-05-25 UE/MCP chain verification: `MoSimSceneLibrary.uproject` is bound
  to UE `5.5`; `Scripts/UE5/build_unreal_renderer.sh` passes with target up to
  date; `Scripts/UE5/open_unreal_renderer.sh editor` finds the running editor;
  `Scripts/UE5/probe_unreal_mcp_listener.py --wrapper-route-only --timeout 1`
  reaches `172.17.48.1:55557`; and
  `Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-level --timeout 2`
  returns live actor data. Local UE installs detected are UE 4.27
  (`UE4Editor.exe`) plus UE 5.4/5.5/5.7 (`UnrealEditor.exe`). This is the
  current baseline before adding more UE MCP write tools.
- Updated scene-source requirement: rendering is insufficient. A scene must be
  importable/editable, renderable, and able to provide or generate
  collision/semantic/occupancy truth for mapping and path planning. If Fab
  cannot provide editable content plus truth route, fall back to local editable
  projects under `References/UnrealScenes`.
- Current `References/UnrealScenes` audit result: editable visual scene
  candidates exist. `DerelictCorridorMegascans` now has explicit exported
  AABB collision truth; the other local candidates still need truth extraction
  before planner validation. UE collision/navigation assets are proxy
  candidates only until exported into explicit occupancy/collision/semantic
  artifacts.
- Local scene map selection is now config-first, not path-order-first:
  `audit_scene_source.py --maps` reads `Config/DefaultEngine.ini` and ranks
  `GameDefaultMap` / `EditorStartupMap` ahead of guessed `.umap` paths.
  Current main-map candidates are `DerelictCorridorMegascans` ->
  `/Game/DerelictCorridor/Maps/DerelictCorridor`,
  `DarkRuinsMegascansSample` -> `/Game/Main`, `ElectricDreamsEnv` ->
  `/Game/Levels/PCG/ElectricDreams_PCGCloseRange`, and
  `FPS-Shooter-Unreal` -> `/Game/FirstPerson/Maps/FirstPersonMap`. Do not
  load `PackedLevels`, `PLBPs`, `Asmbly`, `Previewer`, or `AssetZoo` maps as
  first-review scenes.
- First truth-export route is now defined as
  `Scripts/UE5/export_unreal_scene_truth.py`: run `export` inside Unreal Editor
  Python to write AABB collision proxy JSON under
  `UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/`, then run
  `validate` from normal Python and rerun `audit_scene_source.py`.
- `Scripts/UE5/run_scene_truth_export.py` generates the matching
  `UnrealEditor-Cmd.exe -run=pythonscript` command and temporary Editor Python
  batch script for a selected local scene. It defaults to dry-run; add `--run`
  only after the selected scene opens with the matching UE version/plugins.
- Derelict corridor scene truth is now verified: UE 5.5 commandlet loaded
  `/Game/DerelictCorridor/Maps/DerelictCorridor` and wrote
  `derelictcorridormegascans_collision_truth.json` with 4753 assets and 4753
  AABB collision proxies. `audit_scene_source.py` marks
  `DerelictCorridorMegascans` as `ready_for_truth_backed_planning`; this is
  not yet final semantic or voxel occupancy truth.
- Current scene-source contract:
  `UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json`.
  It records `fab_route.status=inventory_visible_not_scene_accepted`,
  `local_editable_fallback.status=active`, and
  `primary_scene_source_id=local_derelictcorridormegascans`. This means
  Launcher/Fab inventory is visible but not accepted as an imported/editable
  truth-backed MoSim scene yet; Derelict is the active local fallback.
- `AQuadrotorMworksMapActor` now exposes `SceneSourceRegistryJson` and
  `ResolveSceneSourceId`. It can resolve
  `local_derelictcorridormegascans` from the registry, record editable project
  and truth-artifact metadata, and record renderer-local content root, renderer
  map asset, and renderer map package. The Derelict fallback now uses
  `imported_into_renderer=true` through an ignored Windows directory junction,
  not a committed asset copy.
- `Scripts/UE5/check_scene_source_udp_contract.py` verifies the matching UDP
  packet-level contract: dry-run streaming with
  `map_id=local_derelictcorridormegascans` selects the registry primary scene
  source and keeps preview local-map / local-plan data explicitly render-only.
  This proves the frame contract for `ResolveSceneSourceId`; it is still not
  visual import evidence.
- `Scripts/UE5/check_ue_fab_goal_acceptance.py` is now the gate-level audit
  for the current UE/Fab tool objective. Latest status is `7/8` gates passed:
  Fab inventory, local fallback readiness, Derelict truth validation, UDP
  scene-source contract, live `mosim-unreal` edit authority, minimal
  Skills/workflow docs, and local Derelict renderer reuse/load proof pass.
  Remaining gap: Fab route acceptance. Fab is still only inventory-visible, so
  the active route remains `References/UnrealScenes` fallback.
- `Scripts/UE5/link_renderer_scene_source.py` creates/verifies the local
  content link
  `UE5/MoSimSceneLibrary/Content/DerelictCorridor -> References/UnrealScenes/DerelictCorridorMegascans/Content/DerelictCorridor`.
  On WSL/Windows this must be a Windows directory junction, not a Linux symlink,
  otherwise Unreal may fail to find the `.umap` even when Python sees the path.
  The link is ignored and not committed; `scene_source_registry.json` records
  `imported_into_renderer=true`, `renderer_reuse_kind=content_link`, and
  `/Game/DerelictCorridor/Maps/DerelictCorridor`.
- `Scripts/UE5/probe_renderer_map_load.py` is the hard visual-reuse proof for
  this fallback route. Latest evidence in
  `Results/tmp/renderer_map_load_probe_latest.json` reports `ok=true`,
  `loaded_expected_map=true`, `actor_count=1`, and level
  `/Game/DerelictCorridor/Maps/DerelictCorridor.DerelictCorridor` loaded by
  the project-owned `MoSimSceneLibrary` UE 5.5 commandlet.
- `Scripts/UE5/probe_linked_scene_source_mcp.py` produced live editor evidence
  at `Results/tmp/linked_scene_source_mcp_probe_latest.json`: the
  `mosim-unreal` listener was reachable, the Derelict scene source was linked
  into renderer Content, and a temporary `MoSimSceneSourceProbe_*` actor was
  created, transformed, deleted, and cleaned up without saving the map.
- Latest goal audit now reports `ok=True`, `route=local_editable_fallback`,
  `7/8` gates passed. The remaining non-passing gate is Fab route acceptance,
  which is intentionally bypassed by the objective's fallback branch until a
  Fab asset is actually created/imported with edit access and planning truth.
- Current Codex MCP config should use MoSim paths and split the Unreal-related
  servers into `mosim-unreal` and `mosim-epic`. The project-owned
  `MoSimSceneLibrary.uproject` resolves `UnrealMCP` from
  `Docs/Skills/Unreal/mcp/unreal-engine-mcp/FlopperamUnrealMCP/Plugins`; UE 5.5
  build/open/listener/read probes now pass. Persistent map edits still require a
  loaded real review map and an explicit reversible probe; do not execute write
  probes on `/Engine/Maps/Entry`.
- Keep a `TaskSecretary` intake record for new user corrections, sub-agent
  terminal results, Git blockers, and manual-review decisions before promoting
  stable items to this file or the ledger.
- Current task/status review draft for user confirmation:
  `Results/tmp/session_audit_20260521/task_status_review_20260521.md`.
  User reviewed it as broadly acceptable on 2026-05-21; promote stable items
  and keep it as the accepted task-state snapshot for this recovery round.
- Latest Git owner returned `DONE_WITH_CONCERNS`: docs checkpoint branch
  `git/full-convergence-docs-checkpoint-20260521` was pushed at
  `69bd26df44497153fd4eb731c5d03f811a9589e5`; the current local checkout is
  still an old polluted aggregate branch and must not be pushed as-is.
- Parameter identification next step is actionable workflow design: PX4 ULog,
  measured mass, motor order, ESC/RPM or thrust-stand data, and MWORKS parameter
  mapping. Do not stop at "current parameters are unreliable."

## Active Queues

| Queue | Owner Role | State | Next Safe Action |
|---|---|---|---|
| CoAgent implementation miniloop | `MainAgent` | needs-human-review | Doctor/tests are green; user should review before expanding transport or automation. |
| Current instruction recovery | `TaskSecretary` / main agent | accepted | User reviewed the task/status table as broadly acceptable; keep future corrections in TaskSecretary intake. |
| Git integration | `GitFullConvergenceOwner` | done-with-concerns | Use clean branches or `origin/main` for future Git work; do not push old polluted aggregate branches. |
| Cosys-AirSim smoke | `UEBuildSmokeRunner` | visually-reviewed | UE 5.5 Blocks UBT build passed and user confirmed the opened scene is okay; next task is deciding the control/API/UI integration route. |
| Agent workflow improvement | main agent + reviewers | awaiting-user-review | TaskSecretary/goal/Git-owner rules are promoted and `git diff --check` passed; next change should follow user review. |
| Agent organization model | main agent + `DispatchCenter` + `TaskSecretary` | updating | Department model now separates Dispatch Center from Documentation Secretary and defines long-running task conversations. Next safe action: run docs checks, then use this model for future task packets. |
| External docs learning | `ExternalDocsLearningOwner` | recurring-loop-defined | Use `Docs/Index/external_learning_index.md` and `Docs/Workflows/agent_orchestration.md#71-recurring-learning-owner` when failures, new tools, new repos, or milestones trigger another learn-and-patch cycle. |
| Vehicle parameter identification | `VehicleParamIdentificationResearcher` | local-code-audit-complete-awaiting-sunray-ulog | `References/Data` code audit is promoted to `Docs/Workflows/identify_quadrotor_parameters.md`; first useful data package is RC-collected PX4 `.ulg` logs plus `.params`, exact takeoff mass, motor order, and motor/prop/ESC info. RPM or thrust-stand data remains optional but improves confidence. |
| AirSim batch migration | `AirSimMigrationCoordinator` + `AirSimGitBatchOwner` | done | Git-safe migration is complete and pushed. Tracked scopes now include Cosys tutorial/content assets under 100 MB, SPEAR source/reference subset, CARLA UE5 source/reference subset, and IsaacSim text/source subset. Remaining local ignored content is intentional: CARLA image/content packs, IsaacSim LFS-managed assets/cache/data, and SPEAR `third_party`/Content/generated assets. |
| UE S0/S1 renderer next round | `TaskSecretary` + `UEMCPProbe(Ptolemy)` + `SceneProfileAuditor(Maxwell)` + `RendererContractAuditor(Carson)` + `Erdos` | superseded-by-real-scene-source-route | S0/S1 source-level and standalone UDP runtime paths are available, but old generated/blockout maps are no longer the active map route. Current UE 5.5 editor listener and read probes pass; new map work must start from real editable scene sources with truth export. |
| UE S0/S1 runtime autos-pawn review | main agent | done | Runtime autos-pawn, S1 blockout map, and review-camera input fixes are pushed through `dbf03cdcd`. `Scripts/UE5/check_unreal_s0_s1_readiness.py` and `Scripts/UE5/build_unreal_renderer.sh` passed. `Scripts/UE5/review_unreal_s0_s1_renderer.sh` streamed 1604 frames to the standalone game UDP receiver at `172.17.48.1:5005`. UE log confirms `MoSimSceneLibraryGameMode`, map/playback actor spawn, UDP listen, first received MWORKS frame, and review-camera movement/rotation input accepted. |
| S1 competition industrial hybrid blockout | main agent | runtime-reviewable-blockout | Added project-owned S1 blockout render map `map_competition_industrial_hybrid_render_map.json` and bound it from the S1 profile. `SCENE_ID=competition_industrial_hybrid_manual_review MAP_ID=competition_industrial_hybrid bash Scripts/UE5/review_unreal_s0_s1_renderer.sh` streamed 1604 frames; UE log confirms map selection and load: terrain `308`, random/inspection columns `11`, wall/gate/pad boxes `11`. This is visual blockout evidence only, not final art or proof of formal local-avoidance behavior. |
| UE C++ UDP packet receiver | main agent | done | Source-level compatible parsing for Python packet fields `mission`, `local_known_map`, `status`, and `overlays` is implemented, static checks passed, and UE 5.7 UBT/UHT build passed. |

## Superseded Queues

| Queue | Previous Owner Role | State | Reason |
|---|---|---|---|
| CoAgent architecture long-run | `DispatchAgent` | cancelled | User redirected away from design-only long-run work to approved implementation miniloop. Do not resume unless explicitly requested. |
| RflySim scene review | `RflySimSceneReviewer` | superseded | User clarified RflySim maps are no longer the current priority. Do not resume unless explicitly requested. |

## Mistakes To Avoid

- Do not execute first and plan later. Every non-trivial task starts by
  recovering or writing a task graph with objective, current state, critical
  path, owners, verification gates, Git strategy, and stop conditions.
- Do not put live task state, long trigger phrases, or detailed mechanics into
  `AGENTS.md`.
- Do not mark a sub-agent task done just because one checkpoint succeeded.
- Do not close Git owner agents before the full push/integration stop condition.
- Do not batch-close agents. Record each agent's terminal checkpoint in the
  ledger/PROGRESS/WAL first, then close only that specific completed agent.
- Do not accept documentation updates without a docs-quality review pass.
- Do not claim agent/documentation tasks complete without fresh verification
  evidence from this turn or a recorded WAL terminal event.
- Do not accept external reviewer feedback blindly; evaluate it against project
  scope, permission boundaries, YAGNI, and source evidence first.
- Do not paste raw SSE/UI/PTY streams, provider configs, full prompts, secrets,
  or huge logs into durable docs. Record locators, hashes, sizes, and summaries.
- Do not trust chat memory for long tasks; recover from
  `Docs/Workflows/agent_task_ledger.md` and `Results/agent_runs/*/events.jsonl`.
- Do not treat UE/RflySim/SPEAR/Cosys repositories as equivalent; record exact
  simulator role and evidence before adopting assets.
- Do not leave stale runtime tasks active after user redirects the goal. Cancel
  them through `CoAgent/runtime/mosim_agent_runtime.py cancel` and record the
  replacement task immediately.
- Do not hand-edit `Results/agent_runtime/tasks.sqlite3` for result packet
  metadata. Use `mosim_agent_runtime.py update-metadata` so evidence changes
  have an event trail.
- Do not say RflySim maps are "directly usable" without the qualifier. They are
  directly viewable in the native RflySim runtime, but not currently directly
  usable as editable UE5 scenes, planner truth, or the base of our simulator.
- Do not accept a passing core library build as proof that a local Unreal
  environment builds; environment-local plugin copies can have missing
  dependencies.
- Do not commit local UE build libraries such as Blocks-local `AirLib.lib`
  when they exceed 100 MB; keep them as local build artifacts only.
- Do not chase `git/finalize-safe-batches-clean-20260521` as a single aggregate
  push; its content is covered by split branches and GitHub rejected the
  aggregate pack for exceeding 2 GiB.
- Do not reduce "continue tasks" to only the latest user-resumable rollout thread.
  Maintain a ledger-backed queue for Git, external learning, simulator bring-up,
  parameter identification, docs review, and mainline implementation.
- Do not use goal tracking for one-off implementation steps. The goal should
  stay at the durable total objective level; record immediate actions as
  ledger/queue tasks.
- Do not let a stale or malformed goal block execution. If a goal cannot be
  updated, corrected, or safely reused, delete/reset it and recreate it at the
  durable total-objective level; do not keep working against a wrong
  single-step goal.
- Do not conflate UE Editor MCP with Epic/Fab/Launcher library access. UE MCP
  edits a running editor project; Epic/Fab library discovery is a separate
  read-only cache/index problem and must redact account/cache secrets.
- Do not write external Epic Launcher/Fab cache absolute paths into committed
  scene-source contracts. Use inventory commands for live inspection and keep
  committed contracts limited to sanitized state, counts, and MoSim-local paths.
- Do not create broad Skills for every possible simulator task in this phase.
  Current Skills should support only the `mosim-unreal` and `mosim-epic`
  boundaries.
- Do not open UE Editor when the requested review is a packaged simulator
  interface such as RflySim3D or CopterSim.
- Do not adopt Loopback/self-repeating driver loops, Composio credentialed
  workflows, global Codex agent installs, or OKWinds runtime services as project
  requirements unless the user explicitly asks for that integration.
- Do not treat a sub-agent checkpoint as completion when the assigned goal was
  broader than that checkpoint.
- Do not let user corrections stay only in chat. Add them to the current
  `TaskSecretary` intake and promote stable rules to durable docs after review.
- Do not let user directives, manual review decisions, sub-agent returns, or
  work checkpoints stay only in chat. The Dispatch Center and Documentation
  Secretary routes must capture them in task tickets, intake, ledger, PROGRESS,
  or WAL before they are treated as recoverable.
- Do not overload the Documentation Secretary with global dispatch. Dispatch
  Center owns task tickets, owner routing, status board, blocked-task checks,
  and result-packet routing; Documentation Secretary owns durable decisions,
  doc patches, and docs-quality review.
- Do not assign long-running high-context tasks such as Sunray150 parameter
  identification, UE scene integration, or broad simulator bring-up to a
  disposable subagent. Open a dedicated task conversation with a task packet,
  parent department, stop condition, and result-packet contract.
- Do not conclude parameter identification with "parameters are wrong"; produce
  the data, log fields, estimator route, MWORKS mapping, and validation plan.
  For Sunray150, ordinary RC operation is acceptable if PX4 logs include the
  required actuator, attitude/rate, acceleration, position, battery/status, and
  parameter-export data.
- Do not treat external Docs/skills learning as a one-time task. Make it a
  recurring loop after repeated failures, new tool installs, major milestones,
  and sub-agent management incidents.
- Do not treat a temporary task/status table as final project truth until the
  user has reviewed it; promote only stable decisions to `PROGRESS.md`, ledger,
  or workflows.
- Do not migrate AirSim-scale external repositories as one aggregate Git
  operation. Use per-subproject batches, record exclusions, and verify
  >100 MB files, gitlinks, LFS pointers, generated artifacts, and secrets
  before every commit.
- Do not let the main agent become the long-running worker for large migration
  or Git streams. Main agent is the director: keep ledger/PROGRESS current,
  assign child-owner queues, review returned evidence, and integrate/push only
  after batch gates pass.
- Do not let Git batch owners rewrite third-party source formatting merely to
  satisfy whitespace checks. For external imports, scope `git diff --check` to
  project-owned Docs/workflows or record third-party whitespace as accepted
  upstream state. If a third-party subset was reformatted during initial import,
  record it explicitly and do not repeat the pattern.
- Do not spend main-thread time on Git when local LFS hooks, stale
  `index.lock`, polluted branches, or broad external-reference trees make even
  small commits slow. Delegate Git to `GitIntegrator`; the main agent only sets
  scope, reviews evidence, and keeps the engineering critical path moving.
- Do not treat repeated failures, user corrections, review escapes, or
  incidents as handled just because they are mentioned in chat or a status
  paragraph. Route them through a retrospective closure action with owner,
  evidence, promotion/rejection/deferral decision, and closeout criteria.

## Recovery Pointers

- Agent orchestration workflow: `Docs/Workflows/agent_orchestration.md`
- Long-running task ledger: `Docs/Workflows/agent_task_ledger.md`
- External repo audit workflow: `Docs/Workflows/audit_external_repo.md`
- Unreal renderer workflow: `Docs/Workflows/unreal_renderer.md`
- Git/quality rule source: `AGENTS.md#331-parallel-agent-rule`
- Clean Docs/workflow recovery branch:
  `git/recovery-docs-workflows-clean-20260521` at
  `c279bf4add5a4efb0cf5699e93172047ad148a20`

## Current CoAgent Design Checkpoints

- 2026-05-29 CST: Added `COAGENT-DESIGN-12` as the current problem-to-solution
  design landing task. The new baseline is task-oriented rather than
  department-count oriented: durable user task -> topology selector -> context
  pack -> scoped conversations/subagents -> evidence packets -> review and
  knowledge promotion.
- 2026-05-29 CST: Added the design source files
  `CoAgent/docs/architecture/coagent_solution_synthesis.md` and
  `CoAgent/docs/architecture/coagent_user_intervention_ux.md`. These define
  issue-to-decision mapping, dynamic task-team topology, context quality,
  packet-first communication, worktree strategy, blocker notification, and
  email-ready-but-not-sending intervention UX.
- 2026-05-29 CST: Added design-time templates under
  `CoAgent/protocol/templates/` for task charters, context packs, scoped
  conversation packets, blocker notifications, and review packets. These are
  not runtime schemas yet. App-server transport, automatic conversation
  creation, automatic email sending, automatic worktree provisioning, new
  permanent departments, and broad hook/tool expansion remain gated.
- 2026-05-29 CST: Verified the WSL Codex CLI bootstrap route. The Node 16
  `codex` wrapper fails on current syntax, but launching the same JS entrypoint
  with Node 20 works. Recorded the exact command and successful session id in
  `CoAgent/docs/status/codex_cli_entrypoint.md`.
- 2026-05-29 CST: Reframed CoAgent departments as portable capability
  boundaries rather than the old seven-conversation startup set. Added
  `CoAgent/docs/architecture/coagent_department_capability_model.md`; after
  rechecking the enterprise-management audits, expanded the model to 20
  capability departments by adding Product Discovery / Strategy Deployment,
  Flow Analytics / Operating Metrics, and Continuous Improvement /
  Retrospective Closure. The old seven-lane model is now marked as a historical
  startup baseline in
  `CoAgent/docs/architecture/technical_enterprise_operating_system_closure.md`.
- 2026-05-29 CST: Added
  `CoAgent/docs/architecture/coagent_conversation_mapping.md` to map the 20
  capability departments to concrete UI-deleted rollout conversations. Recommended next
  deployment is 11 required permanent conversations, 6 conditional permanent
  conversations, hosted startup capabilities, and task-scoped conversations for
  high-context temporary work. The first proof should use a smaller 6-7
  conversation closed loop before scaling.
- 2026-05-30 CST: During `COAGENT-ARCH-LONGRUN-01`, added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/retrospective_and_improvement_closure_protocol.md`
  and synchronized P59/B40/ADR-014/NEXT-26. Repeated failures such as goal
  weakening, Codex visibility drift, transport timeout, invalid packets, or
  broad external-learning drift now require owned retrospective actions with
  evidence, closeout, promotion, rejection, or explicit deferral. This is
  design-only; no automation, notification, dispatch, Git, MCP, skill, or hook
  mutation is approved by it.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/retrospective_closure_checker_design.md`
  and synchronized P59/B53/NEXT-26. Retrospective closure is now specified as
  a read-only checker contract covering trigger discovery, record presence,
  ownership, evidence, action targets, close conditions,
  promotion/rejection/deferral, stale actions, dependency reporting,
  `RETRO_*` fixtures, and shared validator envelope output. This is
  design-only; it does not create issues, edit docs or skills, send
  notifications, dispatch conversations, call MCP/tools, mutate runtime state,
  stage Git, repair Codex state, inspect account caches, or emit private DB
  dumps/raw transcripts.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/worktree_git_recovery_validator_design.md`
  and synchronized P08/P09/P37/P62/B54/NEXT-04/NEXT-18. Worktree and Git-heavy
  recovery are now specified as a read-only validator family covering worktree
  binding, workspace mode, change inventory, path-family classification,
  integration plans, blockers, role separation, rollback, cleanup, safe
  decisions, evidence labels, and `GIT_*` fixtures. This is design-only; it
  does not run Git, create worktrees, stage, commit, push, delete, move, repair
  locks, edit Git config, call tools, or dispatch DevOps work.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/human_review_package_checker_design.md`
  and synchronized P64/B55/NEXT-29. Human review and intervention are now
  specified as a read-only checker contract covering one-action asks,
  blocker-specific resume mapping, allowed decisions, dedupe, redaction, last
  safe state, safe parallel work, manual evidence boundaries, notification
  readiness, `HREV_*` fixtures, and shared validator envelope output. This is
  design-only; it does not ask the user automatically, send notifications,
  open GUIs, call MCP/tools, retry blocked tools, inspect credentials/account
  caches/private Codex DBs, or mutate runtime/Git/conversation state.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/tool_capability_health_and_fallback_protocol.md`
  and synchronized P13/B41/ADR-015/NEXT-27. MWORKS, UE, Fab/manual import,
  Codex transport, Git, and external-reference routes now require capability
  cards with health levels, evidence labels, stop/fallback decisions, blocker
  policies, stale-card criteria, and future `TOOL_*` checker codes before
  product or dispatch claims can depend on them. This is design-only; no
  MCP/tool execution, UE map mutation, Fab automation, MWORKS simulation,
  Codex dispatch, Git staging, automatic repair, or broad tool expansion is
  approved by it.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/tool_capability_health_gate_checker_design.md`
  and synchronized P13/B56/NEXT-27. The future read-only tool capability
  health checker now has concrete discovery rules, required fields,
  route/health/evidence vocabulary checks, stale-card policy, health-level
  claim ceilings, blocker/fallback validation, unsafe probe rejection,
  route-specific UE/Fab/MWORKS/Codex/Git/external-reference rules,
  dependency handling, and `TOOL_*` fixtures. This is design-only; it does not
  open or repair tools, inspect account caches, run simulations, mutate maps,
  download assets, dispatch Codex conversations, stage Git, or rewrite cards.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/real_task_execution_walkthroughs.md`
  and synchronized P21/P22/P63/B57. The abstract CoAgent operating model is
  now mapped onto two concrete MoSim task families: PX4/Sunray150 parameter
  identification and UE/Fab/local scene truth. The walkthroughs define
  canonical goals, invalid weakened goals, initial departments, task-scoped
  conversations, context pack contents, workflow graphs, mailbox/result packet
  boundaries, contradiction handling, PMO asks, Git disposition, evidence
  boundaries, and completion criteria. This is design-only; it does not parse
  logs, call UE/MWORKS/Fab/MCP, create conversations, mutate maps, create
  worktrees, stage Git, or run product proofs.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/implementation_sequence_and_release_plan.md`
  and synchronized P23/B42/ADR-016. The post-design backlog now has an R0-R8
  phase ladder: review baseline, validator foundation, packet/blocker atoms,
  Candidate A preflight, supervised Candidate A proof, communication recovery,
  product-adjacent proofs, tool-backed product execution, and operating
  evolution. Each phase has entry evidence, exit evidence, skip rules,
  approval-packet fields, release milestones, and forbidden claims. This is
  design-only and does not approve implementation by itself.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/human_review_intervention_ux_design.md`
  and synchronized P64/B48/ADR-021/NEXT-29. Human intervention is now designed
  as a PMO-facing review packet flow with one-action asks, allowed decision
  values, severity, dedupe/rate-limit, redaction, blocker-specific resume
  mapping, required MWORKS/UE/Fab/visual/Git/transport cases, audit log, and
  future checker scope. This remains design-only and does not approve email,
  desktop notification, GUI automation, credential handling, MCP/tool calls,
  conversation creation, Git operations, or live dispatch.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/validator_shared_envelope_design.md`
  and synchronized P65/B49/ADR-022/NEXT-00. Future validators now have one
  shared report contract for schema version, target, allowed modes, decisions,
  dependency reports, findings, evidence paths, side-effect declarations,
  claim boundaries, report storage, fixtures, and integration rules. This is
  design-only; it does not implement domain validators or approve live
  dispatch, MCP/tool calls, GUI automation, credential handling, Git/worktree
  mutation, notification sending, external fetch, or runtime transport changes.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_alignment_checker_design.md`
  and synchronized P66/B50/ADR-023/NEXT-25. Goal alignment is now specified as
  an L0 checker contract covering user objective, canonical task goal, scoped
  objective alignment, result goal mutation, checkpoint evidence delta,
  completion overclaim, recreated-goal scope loss, recovery records, `GOAL_*`
  fixtures, and shared validator envelope output. This is design-only; it does
  not create, mutate, complete, or block goals; dispatch conversations; call
  MCP/tools; create worktrees; stage Git; send notifications; edit Codex state;
  or rewrite task documents automatically.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/runbook_readiness_checker_design.md`
  and synchronized P67/B51/ADR-024/NEXT-30. End-to-end runbook readiness is
  now specified as a read-only checker contract covering readiness levels,
  charter, proof path, context, workflow, mailbox, packets, evidence labels,
  Git disposition, knowledge decision, retrospective triggers, closeout,
  dependency reports, `RUNBOOK_*` fixtures, and shared validator envelope
  output. This is design-only; it does not dispatch conversations, create
  conversations or worktrees, call MCP/tools, stage Git, send notifications,
  mutate goals, edit Codex state, inspect credentials/account caches, or
  rewrite task documents automatically.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/implementation_approval_gate_design.md`
  and synchronized P68/B52/ADR-025/NEXT-31. Implementation approval is now
  specified as a read-only gate contract covering explicit slice approval,
  phase entry evidence, scope, forbidden actions, dependency reports, exit
  evidence, claim boundaries, `APPROVAL_*` fixtures, and shared validator
  envelope output. The validator dependency graph now includes runbook
  readiness and implementation approval as composition gates. This is
  design-only; it does not approve implementation, mutate runtime state,
  dispatch conversations, create worktrees, call MCP/tools, stage Git, send
  notifications, edit Codex state, inspect credentials/account caches, or
  rewrite task documents automatically.
- 2026-05-30 CST: Added
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_health_monitoring_and_intervention_design.md`
  and synchronized P10/P25/P29/P60/P63/P67/B58/NEXT-32. Long-running task
  health now has a runtime intervention playbook: health states,
  trigger-to-action table, critical-path owner rule, topology shrink rules,
  one-action PMO blocker asks, PX4/UE health applications, close-ready
  criteria, and future read-only task-health checker scope. This is
  design-only; it does not implement a scheduler, dashboard, live dispatch,
  automatic task mutation, conversation creation, worktree creation, MCP/tool
  calls, notification, Git operation, or automatic document edits.
- 2026-05-30 CST: During verification, `check_department_visibility.py`
  exposed recurring Codex visible-thread metadata drift across active
  department rows. The approved `codex_session_repair.py sync-visible --apply`
  path was rerun for registered active_visible department threads in WSL and
  Windows Codex homes. Final verification passed with 11 active visible
  conversations and valid WSL main DB, WSL alternate DB, Windows DB, and index
  rows. This reinforces P47 as an active reliability risk until the future
  visibility drift gate/checker exists.
- 2026-05-30 CST: Clarified CoAgent task cancellation boundary after the current
  Codex goal could not be edited by available goal tools. Durable task
  cancellation must use CoAgent runtime lifecycle state, especially
  `python3 CoAgent/runtime/mosim_agent_runtime.py cancel`, and keep a tombstone
  audit trail. Codex `/goal clear` or UI goal deletion is only a visible-thread
  recovery step and must not become the internal task-control plane. Added
  `CoAgent/docs/decisions/coagent_task_cancellation_policy.md` and linked the
  rule from protocol and orchestration docs.
- 2026-05-30 CST: Corrected the above cancellation policy after user challenge:
  CoAgent runtime cancellation does not imply Codex goal deletion is automated.
  Current available goal tools cannot clear or edit this paused goal, the
  documented VSCode Codex binary path is currently missing, and the old Node 16
  npm entrypoint fails with a syntax error. Automatic Codex goal clearing must
  remain an explicit future proof requirement, not an assumed dispatch feature.

## Current Unreal Renderer Checkpoints

- 2026-06-02 Weixin notification recovery: the QR login was not the immediate
  cause of the failed UE/RViz review notification. The adapter passed
  `--session s1` to `cc-connect send`, but `s1` is cc-connect's internal
  conversation id; the send API expects the platform session key stored in the
  session file's `active_session` map. Direct send with the platform key
  returned `Message sent successfully`. Updated
  `CoAgent/gateway/cc_connect_weixin.py` so internal ids such as `s1` are
  resolved to the platform key before sending. Adapter verification with
  `--session s1` now returns `ok=true` and `Message sent successfully`; evidence
  is in `Results/tmp/keyboard_mapping/weixin_adapter_send_resolved_session_20260602.json`.
- 2026-06-01 23:45 CST: user correctly rejected the previous 170-point
  `/velodyne_points` and coarse local occupancy grid as not representative of a
  FAST-LIO/RViz review input. Updated
  `Scripts/ros/publish_mosim_keyboard_mapping_ros2.py` so the manual review
  publisher samples local collision-proxy surfaces near the vehicle, caps the
  LiDAR review cloud at 220000 points/frame by default, and publishes
  `/mosim/local_occupancy_grid` at 0.05 m/cell over an 8 m local radius instead
  of reusing the internal 0.75 m/0.35 m scene grid. Dry-run evidence:
  `Results/tmp/keyboard_mapping/factory_high_density_lidar_grid_dryrun_20260601.json`
  reports 620875 total points over 6 frames and 0.05 m grid cells; Derelict
  reports 1158285 total points over 6 frames. ROS2 runtime probe
  `Results/tmp/keyboard_mapping/derelict_high_density_ros2_runtime_probe_20260601.json`
  confirms `sensor_msgs/msg/PointCloud2`, width 195992, and
  `nav_msgs/msg/OccupancyGrid` resolution 0.05 with 321x321 cells. This remains
  sensor/review oracle evidence only; final FAST-LIO and MWORKS solver claims
  still require real runtime FAST-LIO registered cloud/odometry and MWORKS-side
  dynamics/control evidence.
- 2026-06-01 23:55 CST / 2026-06-02 follow-up: user reported the RViz point
  cloud looked like large balls and clarified that point cloud and grid/map
  review should still be separate RViz2 windows, but each window should be
  simplified to only the useful view, like the UE rendered map window. Root
  cause: the review RViz configs had
  `Style=Spheres`, `Size (Pixels)=9`, and large meter size for
  `/velodyne_points`. Changed FAST-LIO point-cloud review configs back to
  `Style=Points`, `Size (Pixels)=1`, `Size (m)=0.01`. Added
  `/mosim/local_occupancy_voxels` as a 3D occupied voxel PointCloud2 topic while
  keeping `/mosim/local_occupancy_grid` as the ROS `nav_msgs/OccupancyGrid` 2D
  map. Changed `Scripts/UE5/open_keyboard_mapping_rviz_ros2.sh` default to open
  exactly two simplified RViz2 windows: point-cloud and grid/map. Use
  `OPEN_RVIZ=0` to run only the publisher when the windows are already open.
- 2026-06-01 22:55 CST: ROS2/RViz2 manual keyboard mapping point-cloud
  visibility issue was resolved as an RViz display/audit-layout issue, not a
  ROS2 topic failure. ROS2 MCP confirmed `/velodyne_points` publishes
  `sensor_msgs/msg/PointCloud2` in `ue_world` with about 170 points per frame,
  `/mosim/local_known_map_cloud` is non-empty, and `/mosim/manual_odometry`
  reports Derelict pose near `(87.54, 23.74, 2.2)`. Added review configs
  `Config/rviz2/mosim_uav_fastlio_pointcloud_review.rviz` and
  `Config/rviz2/mosim_uav_planning_grid_review.rviz` that hide the RViz
  Displays panel and use a close audit view; desktop screenshot confirmed the
  cyan point cloud is visible. When this repeats, verify ROS topics first, then
  adjust RViz camera/panel layout before changing the publisher. WeChat notify
  retry must use `CoAgent/gateway/cc_connect_weixin.py notify --packet ...`;
  the current send attempt was blocked by `no active session found`, so the
  WeChat gateway session must be reactivated before relying on milestone
  delivery again.
- 2026-06-01 23:15 CST: Factory ROS2/RViz2/UE manual keyboard mapping loop is
  running. First launch failed because `MoSimSceneLibrary/Content` was still
  activated for Derelict, causing UE to report `/Game/Maps/Demonstration` not
  found. Reactivating `local_factoryenvironmentcollect` fixed the map load and
  UE exposed UDP 5005. UE log confirms first Factory keyboard frame:
  `scene=factoryenvironmentcollect_manual_keyboard`,
  `map=local_factoryenvironmentcollect`, `local_map_cells=137`,
  `lidar_points=171`, `local_plan_points=7`. ROS2 MCP confirmed
  `/velodyne_points` has `PointCloud2` width 171, `/mosim/local_occupancy_grid`
  is non-empty, and `/mosim/manual_odometry` moved from about
  `(-55.58, -24.48, 1.9)` to `(-55.58, -23.73, 1.9)` after publishing
  `/mosim/keyboard_command` `w/w/a/d/s`. Added scene-independent manual-review
  RViz2 configs targeting `base_link` so Factory and Derelict do not need
  separate absolute RViz camera coordinates. The keyboard launcher now defaults
  to review configs and keeps RViz windows open for manual audit.
- 2026-06-01 01:35 CST: `DarkRuinsMegascansSample` first-pass manual review is
  rejected for the main daytime rendered scene list. `/Game/Main` can start
  under the forced MoSim review GameMode after the root-level `Content/Main.umap`
  link fix, but the user reported the rendered view was still fully black even
  with forced daylight, skylight, exposure, and headlight review parameters.
  Treat this as a special dark/indoor/radar reference only; do not spend more
  one-map review time trying to relight it for the primary rendered map set.
- 2026-06-01 01:17/01:45 CST: `CitySample` first-pass manual review is
  rejected for the immediate linked-content route. After activating
  `local_citysample`, both `/Game/Map/Big_City_LVL` and
  `/Game/Map/Small_City_LVL` opened through the forced MoSim review GameMode but
  remained black for the user. Logs show the route is missing CitySample
  project-specific runtime classes such as
  `/Script/CitySample.CitySampleCharacter`,
  `/Script/CitySample.CitySamplePlayerController`,
  `/Script/CitySample.CitySampleGameMode`, and
  `/Script/CitySampleMassCrowd.MassPlayerAnimInstance`, plus very large
  texture/UDIM builds. Do not treat CitySample as a simple Content-link scene
  source; it needs a dedicated plugin/source integration or standalone
  CitySample-project review pass before it can become a MoSim main city map.
- 2026-06-01 01:04/01:55 CST: `ABoyandHisKite` first-pass manual review is
  rejected for the immediate linked-content route. The large
  `/Game/Maps/GoldenPath/GDC_Landscape_01` map did not reach `Load map complete`
  in the short review window and showed UE 4.27-origin Blueprint compatibility
  errors. A lightweight `/Game/Maps/TutorialMap` retry loaded with the MoSim
  review camera, but the user reported a mostly black view with only a row of
  3D text visible. Logs also show missing KiteDemo C++ parent classes such as
  `/Script/KiteDemo.GDC_DemoGameMode`. Do not use ABoy/Kite through simple
  Content linking; schedule a dedicated KiteDemo source/project conversion only
  if the large outdoor Kite scene becomes necessary.
- 2026-06-01 00:50 CST: `FPS-Shooter-Unreal` was manually rejected as a formal
  MoSim map candidate. `/Game/FirstPerson/Maps/FirstPersonMap` loaded correctly
  with `MworksReviewCameraPawn` and daylight review controls, so it remains a
  useful lightweight Unreal launch/control smoke test, but the user judged the
  scene visually unsuitable ("too ugly") and it must not be used for the
  simulation scene library.
- 2026-06-01 00:57/01:40 CST: `MedievalVillageMegascansS` first-pass manual
  review is rejected for the immediate main rendered scene list. A second
  `/Game/Maps/MedievalVillage_P` review start under UE 5.5 again used the
  forced MoSim review GameMode, but the user reported the visible window was
  fully black. Logs also show UE 4.27-origin Blueprint/input compatibility
  warnings, stale navmesh data, and long first-time static mesh builds including
  `SM_WindmillWings` and roof meshes. Do not use it in immediate one-map manual
  review; schedule a dedicated conversion/cache warm-up/lighting pass only if a
  village scene becomes necessary.
- 2026-06-01 00:46/01:50 CST: CityPark first-pass manual review is deferred.
  After activating `local_cityparkenvironmentcollec`,
  `/Game/CityPark/Maps/Overview` reached `Load map complete` with
  `MworksReviewCameraPawn`, but the game window immediately reported
  `All Windows Closed`. Retries on `/Game/CityPark/Maps/Showcase` and
  `/Game/CityPark/Maps/Showcase_NotOptimized` with explicit daylight/camera
  coordinates stayed black for the user while logs waited on or built merged
  park/fence/foliage static meshes such as `SM_MergedFence01_1` and
  `SM_MergedParkFence03_1`. Do not spend more one-map review time on CityPark
  until a dedicated compatibility/build pass fixes or prebuilds the asset cache.
- 2026-05-23 19:56 CST: User reported the standalone S1 Unreal review window
  could not move its view. Root cause was `MoSimSceneLibraryGameMode`
  setting `DefaultPawnClass = nullptr`, leaving the game viewport without a
  controllable review pawn. Added a project-owned review camera pawn with
  WASD/QE movement, arrow/RMB mouse look, and Shift/Ctrl speed scaling; the
  readiness check now verifies this contract.
- 2026-05-23 20:01 CST: First rebuild attempt failed because the project-owned
  Unreal Editor process held `UnrealEditor-MoSimSceneLibrary.dll`; after
  stopping only the `MoSimSceneLibrary.uproject` process, the build passed.
  The next standalone launch exited inside `UnrealEditor-Landscape.dll` while
  loading `/Engine/Maps/Templates/OpenWorld`; default maps are now set to
  `/Engine/Maps/Entry` because renderer geometry is spawned at runtime.
- 2026-05-23 20:18 CST: `--check-listener` still failed while only the
  standalone `-game` process was running. `open_unreal_renderer.sh editor`
  incorrectly treated that `-game` process as an Editor session; editor-mode
  reuse now excludes command lines containing `-game`.
- 2026-05-23 20:26 CST: Actual Editor process was launched alongside the
  standalone game process. `Scripts/UE5/probe_unreal_mcp_listener.py --timeout 1`
  reached `172.17.48.1:55557`; `Scripts/UE5/check_unreal_s0_s1_readiness.py
  --check-listener` passed; Unreal MCP read-only `get_actors_in_level` returned
  actors from the Editor scene.
- 2026-05-23 20:36 CST: UE Editor rewrote `DefaultEngine.ini` with
  `AndroidFileServerRuntimeSettings/SecurityToken`. This is local generated
  config, not project state. The readiness check now fails if this section is
  present, so it must be removed before commit.
- 2026-05-23 20:48 CST: Added runtime input evidence for the standalone review
  camera. When keyboard/mouse input actually changes the camera, the game log
  prints `MWORKS review camera input accepted` with location and rotation.
- 2026-05-25 CST: UE crashed after an Unreal MCP write probe tried to create a
  probe actor while the editor was on `/Engine/Maps/Entry`. The probe scripts now
  treat CLI actor names as prefixes, append a UUID suffix unconditionally, and
  refuse write probes on Entry or unidentified maps unless an explicit smoke-test
  override is passed. If an Entry recovery package appears, skip recovery rather
  than restoring the temporary editor state.
- 2026-05-25 CST: The old `UE5/MworksUnrealRenderer` project has been directly
  replaced by `UE5/MoSimSceneLibrary`; do not keep a separate deprecated
  renderer shell. `UE5/MoSimSceneLibrary` is now both the Fab/Marketplace scene
  staging project and the runtime renderer project. The bridge plugin lives at
  `UE5/Bridge` while retaining the module name `QuadrotorMworksBridge`.
  `Scripts/UE5/check_unreal_bridge.py` passes against the new layout. Scene
  source UDP/truth checks may still fail until the local, ignored scene asset
  link such as `UE5/MoSimSceneLibrary/Content/DerelictCorridor` is recreated.
- 2026-05-23 21:02 CST: Strengthened the Unreal review camera after a manual
  report that the viewport could not move. The camera now uses UE axis bindings
  plus key-poll fallback, reapplies GameOnly input after possession/restart, and
  the standalone launcher no longer opens the extra `-log` window that can steal
  focus from the game viewport.
- 2026-05-23 21:14 CST: Confirmed the standalone S1 renderer window accepted
  camera input during `competition_industrial_hybrid_manual_review`. Runtime log
  evidence:
  `MWORKS review camera input accepted moved=1` and
  `MWORKS review camera input accepted moved=0 rotated=1`.
- 2026-06-02 CST: Fixed the Factory ROS2/RViz keyboard mapping review loop after
  user reported that the point cloud did not update and the grid map was still
  2D. Root causes: the Python publisher recomputed and republished very large
  clouds every frame, so the claimed 20Hz path collapsed under rclpy/WSLg load;
  and the review launcher could set both `--interactive` and
  `/mosim/keyboard_command`, but the publisher consumed only the ROS command
  topic in that mode. `publish_mosim_keyboard_mapping_ros2.py` now caches
  pose-dependent LiDAR/voxel data, refreshes headers at 20Hz while stationary,
  accepts both terminal keyboard input and `/mosim/keyboard_command`, publishes
  `/mosim/local_occupancy_voxels` as the primary 3D map surface, and keeps
  `nav_msgs/OccupancyGrid` as 2D reference only. Runtime probe showed
  `/velodyne_points` at about 20Hz with `lidar=20000`, odometry changed after
  `w w w d d`, and the 3D voxel topic published `width=30000`.
- 2026-06-02 CST: Rejected the keyboard/grid-step route as mainline after user
  review. Added `Scripts/ros/publish_mworks_uav_state_ros2.py` as the first
  MWORKS-derived ROS2 replay bridge and verified topic rates without opening
  RViz: `/mosim/truth/odometry` about 20.0Hz, `/mosim/imu` about 200.0Hz after
  fixing uniform 5ms IMU scheduling, and `/mosim/lidar_points` about 10.0Hz.
  This is still replay evidence, not live closed-loop co-simulation. The
  current Factory LiDAR JSONL contains only about 156-176 points/frame, so it
  is smoke-only and cannot support a credible FAST-LIO/Mid360 claim. Next
  mainline step is dense LiDAR/Livox-like scan generation or live UE sensor
  export tied to MWORKS state, then FAST-LIO runtime output validation.
- 2026-06-02 CST: CoAgent Weixin gateway progress packets must use the existing
  whitelisted packet shapes. A generic JSON with `type=progress_update` is
  rejected as `unsupported packet type`; use `template_type=blocker_notification`
  with `class=manual_review_required` for non-blocking milestone updates, or a
  review/result packet when actual human action is needed.
- 2026-06-02 CST: Added `Scripts/UE5/generate_livox_like_lidar_replay.py` to
  reuse Sunray's `mid360-real-centr.csv` scan pattern with UE collision truth.
  Factory dense replay probe generated about 24.5k-25.9k points/frame with
  `offset_time_ns`, `line`, `reflectivity`, and `tag` attributes. The current
  Python/rclpy MWORKS bridge can show the dense point cloud, but LiDAR topic
  rate collapses to about 0.3-0.5Hz for 25k-point frames. Do not optimize this
  Python route as the final dense LiDAR transport; move dense real-time LiDAR
  to C++ ROS2, UE C++ sensor bridge, or a Livox-plugin-derived path.
- 2026-06-02 CST: Added `Scripts/ros/mosim_dense_lidar_cpp` as a minimal C++
  ROS2 dense LiDAR publisher. Clean `colcon build` passed in
  `Results/tmp/mosim_dense_lidar_cpp_ws`. A naive C++ timer publisher still
  measured only about 0.5-0.8Hz for 25k-point frames; after prepacking
  `PointCloud2` messages and updating only the header timestamp, measured rate
  improved to about 7-8Hz as seen by `ros2 topic hz`. Added internal publisher
  stats because the `topic hz` subscriber can become the bottleneck for large
  `PointCloud2`; with about 21k points/frame, the C++ node reported about
  9.73Hz and mean publish call time around 100-130 microseconds. This is still a
  transport prototype, not final FAST-LIO input; next step is actual FAST-LIO
  subscriber or dedicated C++ subscriber validation plus QoS/DDS/zero-copy or
  point-density tradeoff.
- 2026-06-02 CST: Weixin milestone packet
  `ue_uav_cpp_lidar_transport_status_20260602.json` was accepted by the gateway
  formatter but cc-connect send failed once with `weixin: sendMessage: ret=-2`.
  Do not retry in a tight loop; treat it as a transient Weixin/session send
  failure and continue local work unless a later manual-review notification
  also fails.
- 2026-06-02 CST: Continued the UE/ROS2/MWORKS architecture correction instead
  of polishing the rejected keyboard/grid route. `publish_mosim_keyboard_mapping_ros2.py`
  and `open_keyboard_mapping_rviz_ros2.sh` now explicitly report
  `quality_status=smoke_only` and block controller/FAST-LIO/3D-map/autonomous
  planning claims. `publish_mworks_uav_state_ros2.py --dry-run` now emits
  source-rate, resampling, timestamp, odometry-continuity, LiDAR-density, and
  TF-contract diagnostics; current IMU remains marked as resampled from 20Hz
  MWORKS replay data. ROS2 LiDAR publishers were corrected to Livox-compatible
  `PointCloud2` fields (`offset_time`, `x`, `y`, `z`, `intensity`, `tag`,
  `line`) in the MWORKS bridge, FAST-LIO replay publisher, and C++ dense
  publisher. RViz2 planning configs now default to a 3D Orbit view with
  `/mosim/local_occupancy_voxels` as the active map surface and the 2D
  `OccupancyGrid` disabled as reference. Targeted checks passed:
  `test_mworks_uav_state_ros2.py`, `test_livox_like_lidar_replay.py`,
  `test_keyboard_mapping_ros2.py`, `test_fastlio_replay_adapter.py`, and
  `colcon build --packages-select mosim_dense_lidar_cpp` with only WSL clock
  skew warnings.
- 2026-06-02 CST: Added subscriber-side dense LiDAR transport gate in
  `Scripts/ros/mosim_dense_lidar_cpp`: `dense_lidar_subscriber_probe_node`
  subscribes to `PointCloud2`, verifies Livox-compatible fields, stamp
  monotonicity, point counts, `point_step=22`, and measured receive rate before
  exiting with pass/fail status. A short Factory Livox-like replay probe passed:
  8 received frames, about `9.69Hz`, about `19.9k-21.0k` points/frame,
  `livox_fields_ok=true`, `stamps_monotonic=true`. This is stronger than
  publisher-only evidence but remains a transport gate, not FAST-LIO
  localization evidence. New check `Scripts/tests/test_dense_lidar_cpp_contract.py`
  and `colcon build --packages-select mosim_dense_lidar_cpp` passed.
- 2026-06-02 CST: Rechecked existing Factory FAST-LIO runtime evidence instead
  of rerunning blindly. Runtime topic recording exists and is nonzero:
  `fastlio_runtime` recorded odometry/path/cloud counts `339/32/328`, while
  `fastlio_runtime_scan099` recorded `2998/29/297`. Both Factory evaluations
  fail quality thresholds: RMSE about `10.20m` and `9.76m`, max error about
  `17.71m` and `18.55m`, with nonmonotonic odometry timestamp pairs. Therefore
  the immediate blocker is not just starting FAST-LIO; it is Factory FAST-LIO
  quality diagnosis across timestamp policy, scan pattern, extrinsics, motion
  excitation, initialization, and scene geometry.
- 2026-06-02 CST: Added reusable Factory FAST-LIO failure diagnosis:
  `Scripts/UE5/diagnose_fastlio_factory_failure.py`, regression
  `Scripts/tests/test_fastlio_factory_failure_diagnosis.py`, and reports
  `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md`
  plus `fastlio_failure_diagnosis.json`. Diagnosis result is
  `status=not_claimable`: Factory runtime topics exist but both quality gates
  fail; current config is Velodyne-like (`lidar_type=2`, `scan_line=16`) while
  target is Mid360/Livox-like; evaluated input is only about 509 points/frame;
  IMU is synthetic finite-difference; evaluated frames lack per-point
  attributes; yaw is fixed; odometry timestamps are nonmonotonic. Next action is
  to promote dense Livox-like input plus synchronized high-rate IMU and a
  Mid360 config before any planner/controller claim.
- 2026-06-02 CST: Added the first executable Mid360 input gate instead of
  continuing the rejected toy mapping route. New files:
  `Config/ros2/mosim_spark_fast_lio_mid360.yaml`,
  `Scripts/UE5/check_fastlio_input_contract.py`, and
  `Scripts/tests/test_fastlio_input_contract.py`. ROS2 FAST-LIO launch/wrapper
  defaults now use `/mosim/lidar_points`, `/mosim/forward/imu`,
  `base/mid360_link`, and the Mid360 config. Factory contract output:
  `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_INPUT_CONTRACT.md`
  and `fastlio_input_contract.json`; status is
  `dense_lidar_ready_but_fastlio_input_blocked`. Dense Livox-like replay is
  ready at about 20.5k points/frame with line ids 0-3 and Livox attributes, but
  the legacy FAST-LIO dataset is blocked because it has only 512 points/frame,
  lacks point attributes, and still uses synthetic finite-difference IMU.
  Targeted checks passed: `test_fastlio_input_contract.py`,
  `test_fastlio_factory_failure_diagnosis.py`, and
  `test_fastlio_rviz_runtime_scripts.py`.
- 2026-06-02 CST: Updated the ROS2 Factory FAST-LIO replay entry so it no
  longer defaults to the old 512-point `fastlio_replay_dataset.jsonl` when
  dense artifacts are present. `Scripts/UE5/run_fastlio_rviz_replay_ros2.sh`
  and `Scripts/ros/mosim_scene_replay/launch/mosim_scene_replay.launch.py`
  now prefer `publish_mworks_uav_state_ros2.py` with Factory
  `mworks_smoke/raw/...linear_mpc_smoke.csv` plus
  `livox_like_lidar_frames.jsonl`, publishing `/mosim/lidar_points` and
  `/mosim/forward/imu`. Dry-run status for Factory is
  `USE_DENSE_MWORKS_FASTLIO_INPUT=1`, about 21k dense points/frame, and
  `mid360_density_claimable=true`. Derelict was brought to the same dense
  route after its Mid360 replay was generated. This remains replay plumbing,
  not FAST-LIO localization evidence until runtime output metrics pass.
- 2026-06-02 CST: Generated Derelict dense Mid360/Livox-like replay using the
  same Sunray `mid360-real-centr.csv` pattern and UE collision truth:
  `Results/unreal_scene_mapping/derelictcorridormegascans/livox_like_lidar_frames.jsonl`.
  The manifest reports 5 frames, about 24.3k points/frame, 10Hz LiDAR, and
  200k points/s. Derelict `FASTLIO_INPUT_CONTRACT.md` now exists and reports
  `dense_lidar_ready_but_fastlio_input_blocked`, matching Factory: dense sensor
  input is ready, but localization remains blocked until the runtime uses
  synchronized high-rate IMU and passes truth-error metrics. Re-ran and passed:
  `test_fastlio_input_contract.py`, `test_fastlio_rviz_runtime_scripts.py`, and
  `test_mworks_uav_state_ros2.py`.
- 2026-06-02 CST: Split ROS2 LiDAR topic semantics to avoid another
  FAST-LIO/mapping-smoke confusion. Dense Mid360/FAST-LIO input stays on
  `/mosim/lidar_points`; sparse RViz mapping smoke now defaults to
  `/mosim/mapping_smoke/lidar_points` in
  `publish_mosim_mapping_replay_ros2.py`, `open_mapping_rviz_ros2.sh`,
  `run_fastlio_rviz_replay_ros2.sh`, and `mosim_scene_replay.launch.py`.
  Checks passed: `test_ros_mapping_replay_publisher.py`,
  `test_fastlio_rviz_runtime_scripts.py`, `test_fastlio_input_contract.py`,
  and `test_mworks_uav_state_ros2.py`.
- 2026-06-02 CST: Added executable FAST-LIO runtime candidate selection gate:
  `Scripts/UE5/check_fastlio_runtime_candidates.py` and regression
  `Scripts/tests/test_fastlio_runtime_candidates.py`. The report
  `Results/unreal_scene_mapping/FASTLIO_RUNTIME_CANDIDATES.md/json` says
  `decision=patch_ros2_livox_custommsg_candidate_first`. `spark-fast-lio` is
  the only local native ROS2 FAST-LIO-family candidate, but it is not claimable
  for Mid360 yet: its standard `PointCloud2` path rejects Livox `lidar_type=1`,
  the CustomMsg path is guarded, ROS1/ROS2 Livox driver naming is mixed, and a
  Livox callback macro is inconsistent. ROS1 `FAST_LIO` and the Sunray Livox
  Gazebo plugin are strong semantic/bridge references only. Check passed:
  `python3 Scripts/tests/test_fastlio_runtime_candidates.py`.
- 2026-06-02 CST: User rejected the current mapping demo as structurally
  wrong for real UAV simulation: grid-cell motion is too coarse for controller
  optimization, point cloud and grid map must move continuously with UAV state,
  grid review must be 3D, and FAST-LIO-like point cloud quality cannot be
  replaced by RViz display tuning. Active work stays on the real stack:
  MWORKS continuous dynamics/controller/truth/IMU, UE rendering/sensor oracle,
  ROS2 Mid360/Livox + synchronized IMU + TF, FAST-LIO, RViz2 point-cloud and
  3D local-map windows. A task-list notification packet was written to
  `Results/coagent_gateway/progress/ue_uav_realstack_tasklist_20260602.json`,
  but the bounded WeChat send again failed with
  `weixin: sendMessage: ret=-2 errcode=0`; do not retry in a loop. Treat
  WeChat as degraded until cc-connect/Weixin session is repaired.
- 2026-06-02 CST: Current active goal is the long-run real UAV stack catch-up
  and minimum closed-loop redesign, not more RViz/point-cloud display tuning.
  Added the explicit task checklist to
  `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md`: PX4-style streamed
  control, Sunray/YunZong source audit, Mid360/FAST-LIO runtime route, RflySim
  / AirSim / Gazebo role-boundary comparison, Factory/Derelict headless gates,
  and WeChat notification fallback. Next implementation must prove continuous
  MWORKS state, 200Hz IMU, 10Hz Mid360-like dense LiDAR, coherent TF/timestamps,
  real FAST-LIO output, truth error, and 3D local map before opening UE/RViz2
  for manual review.
- 2026-06-02 CST: Added the concrete reuse/adapt/replace matrix at
  `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md`.
  Main decisions: PX4 Offboard/ROS2 is an architecture contract, not the first
  runtime dependency; Sunray control/Mid360/EGO are behavior and data-contract
  sources to adapt; RflySim/AirSim/Gazebo are role-boundary references; local
  `spark-fast-lio` is patch-only until Livox CustomMsg runtime passes; external
  `Ericsii/FAST_LIO_ROS2` branch `ros2` remains the preferred candidate to
  import/build/evaluate first. Current keyboard/grid mapping is smoke-only.
- 2026-06-02 CST: Probed the FAST-LIO ROS2 route. External
  `Ericsii/FAST_LIO_ROS2` branch `ros2` import still timed out at the 60s
  network gate, so it remains a preferred but unverified candidate. Local
  `spark-fast-lio` build probe showed ROS2 Humble and `livox_ros_driver2` are
  available; `livox_ros_driver2` built successfully in the temp workspace, and
  `spark_fast_lio` started configuration without an immediate error before the
  60s timeout. Evidence:
  `Results/unreal_scene_mapping/FASTLIO_ROS2_IMPORT_BUILD_PROBE_20260602.md`.
  Shell correction recorded: source ROS2 setup under `set +u`, then restore
  `set -u`.
- 2026-06-02 CST: Re-ran the Factory real-stack headless gate with the correct
  command syntax, because `check_realstack_miniloop_gate.py` has no `--scene`
  option and defaults to Factory paths. Result remains
  `blocked_before_manual_review`: MWORKS state is continuous at 20Hz with max
  step about 0.0033m; dense Mid360-like LiDAR has about 19.9k-21.0k
  points/frame, Livox fields, four lines, and monotonic frame times; RViz2
  point-cloud and 3D voxel-map configs are aligned. The only hard blockers are
  FAST-LIO input contract `dense_lidar_ready_but_fastlio_input_blocked` and
  zero `/odometry`, `/path`, `/cloud_registered` runtime samples.
- 2026-06-02 CST: User accepted the Factory UAV placement/movement review
  enough to proceed with visual coloring. Current Sunray150 runtime STL route
  has no original material/texture data, so UE now uses a documented procedural
  reference palette from `References/CUAV/Sunray150-正.png`,
  `References/CUAV/Sunray150-侧.png`, MWORKS `package.mo`, and local Sunray DAE
  material cues: black graphite body/frame, light grey duct/propeller cue,
  grey MID-360 base, and blue MID-360 dome. This is explicitly a review
  approximation until an approved textured UE/DAE asset is imported.
- 2026-06-02 CST: Updated the Factory follow-camera review control contract:
  default offset stays `FVector(-80.0f, -20.0f, 40.0f)`, while arrow keys now
  orbit the camera around the UAV on a fixed spherical radius instead of
  free-rotating the view. Left/right adjust azimuth, up/down adjust elevation,
  and the camera continuously looks back at the UAV.
- 2026-06-02 CST: User rejected the first Sunray recolor because it did not
  respect physical component identity: the blue MID-360 dome cue was acceptable,
  but the MID-360 protective bracket was incorrectly colored by a broad STL
  position heuristic. Local Sunray `150.dae` confirms named material groups:
  `MID360_PROTECT_ARC*` is dark grey, `MID360_PROTECT_ARC_CONNECTOR*` is dark
  graphite, `PROTECTIVE_RING` is dark grey, and only the MID-360 optical/dome
  cue should be blue. The UE review route now defaults to follow/orbit camera
  and uses DAE-informed material sections; exact manufacturer appearance still
  requires importing a proper textured DAE/UE asset.
- 2026-06-02 CST: Reworked the short-term MID-360 color route after inspecting
  local DAE geometry/materials and CUAV reference images. The MWORKS body STL
  is a single-material binary mesh, so the accepted blue MID-360 optical cue is
  isolated as a small independent UE dome component while the STL
  `MID360_PROTECT_ARC*` region remains dark grey/black. This avoids coloring
  the physical protective bracket as blue glass; the durable fix remains DAE or
  UE asset import with named material sections.
- 2026-06-02 CST: Corrected the Factory follow/orbit camera left/right arrow
  mapping after manual review. Only the UAV follow/orbit azimuth input was
  inverted; the separate free-look camera mapping was left unchanged.
- 2026-06-02 CST: Refined the left/right correction after the user clarified
  that the actual `←/→` orbit movement direction, not only the fallback key
  mapping, was reversed. The UE input axis remains right-positive, while the
  follow/orbit azimuth delta is now applied with the opposite sign.
- 2026-06-06 CST: UE Experiment Console source-level command state component
  smoke added. Use `python Scripts/UE5/check_ue_experiment_console_state_contract.py`
  plus `python -m pytest Scripts/tests/test_ue_experiment_console_state_contract.py
  Scripts/tests/test_ue_command_sender_contract.py Scripts/tests/test_ue_command_echo_contract.py
  Scripts/tests/test_ue_command_adapter_smoke.py Scripts/tests/test_ue_command_echo_state_reducer.py -q`
  to verify that pending originates only from `mosim.ue_command.v1`, accepted/
  rejected originates only from matching `mosim.ue_command_echo.v1`, the sender
  remains sender-only, no runtime echo receiver exists, and no Actor/input pose
  control API is exposed. Evidence:
  `Results/unreal_experiment_console/console_state_component_smoke_20260606_003/`.
- 2026-06-06 CST: UE Experiment Console source-label safety patch completed
  for task 005. `UQuadrotorMworksExperimentConsoleStateComponent::IsSmokeSource`
  now also downgrades `MWORKS_MCP_result_adapter_smoke` and
  `MWORKS_MCP_runtime_adapter_preflight`, in addition to
  `offline_adapter_smoke` and `source_level_smoke`, so these known
  offline/source/preflight rows remain `quality_status=smoke_only` and
  `accepted_as_runtime_ack=false`. Static evidence:
  `Results/unreal_experiment_console/echo_source_label_safety_20260606_005/`.
  This does not implement a runtime echo receiver and does not prove live UE,
  MWORKS, or ROS2 ack.
- 2026-06-06 CST: UE Experiment Console source-label compile-only gate
  completed for task 006. `Scripts/UE5/build_unreal_renderer.ps1` called
  UnrealBuildTool from `D:\Program Files\Epic Games\UE_5.5` for
  `MoSimSceneLibraryEditor Win64 Development` against
  `UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject`; exit code was 0.
  UBT compiled `QuadrotorMworksExperimentConsoleStateComponent.cpp` and linked
  `UnrealEditor-QuadrotorMworksBridge.dll`. Post-compile static checkers and
  focused pytest still pass. Evidence:
  `Results/unreal_experiment_console/source_label_compile_gate_20260606_006/`.
  This is compile evidence only, not live UE runtime ack or runtime receiver
  evidence.
- 2026-06-06 CST: Replaced the old `MoSim｜CoAgent运维平台`
  thread `019e74d1-72fa-7d33-8783-90584035ae92` for native Codex
  thread/automation work because it was created through an older WSL/non-App
  native conversation path. New active CoAgent ops thread:
  `MoSim｜CoAgent运维平台` / `019e9bc1-ea9f-7102-b41a-4ef9b2308992`.
  R2 capability smoke confirms `automation_update` and native thread-management
  tools are visible; no mutation automation was created in that smoke. Updated
  active routing docs and `CoAgent/dispatch/department_threads.json`; also
  corrected the deleted ROS2 old thread route to R2
  `019e9b85-d4d8-7bf3-8afd-a65697cd3889`. Evidence:
  `Results/agent_packets/returns/MOSIM-COAGENT-OPS-R2-NATIVE-CAPABILITY-SMOKE-20260606-001.json`
  and
  `Results/agent_packets/returns/PMO-COAGENT-OPS-R2-THREAD-REPLACEMENT-20260606-001.json`.
- 2026-06-06 CST: User clarified that existing departments needing recurring
  checks should not be duplicated as new visible threads now that
  `MoSim｜CoAgent运维平台` has native thread and automation capability.
  Updated orchestration/meta-maintenance rules: configure native Codex App
  automations or thread wakeups against existing threads for
  `MoSim｜微信网关运维部` (`019e9855-aa43-7fe2-807e-be7d4095877b`),
  `MoSim｜Codex 上下文维护部` (`019e3dac-de0e-7180-98ad-d7137e8a6275`), and
  `MoSim｜开源项目探针` (`019e74cf-fb50-7d71-912c-f586b4dd5f06`) instead of
  creating duplicate departments.
- 2026-06-06 CST: User confirmed the old CoAgent ops thread
  `019e74d1-72fa-7d33-8783-90584035ae92` can be deleted from the current
  operating set. Its earlier Codex App capability research is incomplete for
  current planning because the thread itself did not have reliable native
  thread/automation tools. PMO created a redo task packet for
  `MoSim｜CoAgent运维平台`:
  `Results/agent_packets/tasks/ops_codex/MOSIM-CODEX-NATIVE-CAPABILITY-READOPT-R2-20260606-001.json`.
- 2026-06-06 CST: User deleted the old CoAgent ops thread
  `019e74d1-72fa-7d33-8783-90584035ae92`. Updated current routing records so it
  is no longer described as a recoverable App thread. Future CoAgent ops,
  native Codex App capability audits, thread-management tasks, and automation
  setup go to `MoSim｜CoAgent运维平台`
  (`019e9bc1-ea9f-7102-b41a-4ef9b2308992`). Recover old work only from project
  docs and `Results/agent_packets/`.
- 2026-06-06 CST: User reported Codex App list still showed the deleted old
  `MoSim｜CoAgent运维平台` row even though the history was deleted. PMO
  `list_threads query=CoAgent运维平台` only returned R2
  `019e9bc1-ea9f-7102-b41a-4ef9b2308992`; old id archive attempt returned
  `Inactive thread archive did not persist`, indicating an inactive/App-cache
  residue rather than a dispatchable thread. PMO renamed the stale id to
  `MoSim｜CoAgent运维平台-已删除勿用` as a visual guard. If the list row remains,
  refresh/restart Codex App; do not restore or dispatch to the old id.
- 2026-06-06 CST: User renamed the new App-native CoAgent ops thread
  `019e9bc1-ea9f-7102-b41a-4ef9b2308992` back to
  `MoSim｜CoAgent运维平台` without the temporary `R2` suffix. PMO confirmed the
  App title through `list_threads query=CoAgent` and updated the current
  dispatch registry and active routing docs. The durable distinction is now the
  thread id: current `019e9bc1-ea9f-7102-b41a-4ef9b2308992`; deleted old
  `019e74d1-72fa-7d33-8783-90584035ae92`.
- 2026-06-06 CST: MWORKS Dynamics And Control Verification R2 completed task
  `RFLY-MOSIM-MWORKS-YAW-SIGN-MOTOR-ORDER-AUDIT-20260606-008`. Local source
  audit found PX4/Sunray quad order `0 front-right ccw`, `1 back-left ccw`,
  `2 front-left cw`, `3 back-right cw`; current MWORKS wrapper order is
  front-right, front-left, back-left, back-right, so the documented mapping is
  PX4/Sunray `0,2,1,3` -> MWORKS `1,2,3,4`. MCP health and check_model passed
  for existing physical yaw smoke; simulation result binding was degraded and
  only the internal `torque_application_error@end=0.0` probe was usable.
  Evidence:
  `Results/mworks_dynamics_upgrade/20260606_008_yaw_sign_motor_order_audit/`.
  This is not parameter identification, fault-isolation readiness, allocation
  reconstruction readiness, controller performance, planner_ready, live runtime
  ack, Factory trace consumption, or closed_loop.
- User then reported that the MWORKS/Sysplorer GUI error dialog had not been
  returned properly by the department. PMO dispatched an immediate correction
  to MWORKS R2. R2 wrote GUI blocker
  `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-YAW-SIGN-MOTOR-ORDER-AUDIT-20260606-008-GUI-CRASH-REPORT.json`,
  referencing PMO screenshot
  `Results/mworks_gui_incidents/20260606_sysplorer_error_dialog/sysplorer_error_dialog_20260606_1737.png`
  and incident metadata
  `Results/mworks_gui_incidents/20260606_sysplorer_error_dialog/incident.json`.
  The 008 source-audit evidence remains bounded to pre-dialog saved evidence;
  after the GUI crash dialog, no new MWORKS GUI/MCP evidence may be claimed
  until PMO/user authorizes recovery and the smallest relevant
  `session_manager health` plus `check_model` passes.
- 2026-06-06 CST: User clarified that the `ret=-2` recovery prompt should be
  handed to `MoSim｜微信网关运维部` (`019e9be0-534e-7c22-97ff-98fa7c2af39b`),
  which owns WeChat gateway maintenance and sparse fallback handling. PMO
  verified the thread is visible through `list_threads query=微信网关运维部`,
  but two native `send_message_to_thread` attempts failed before the task could
  start: first `failed to update thread settings: internal error; agent loop
  died unexpectedly`, then a minimal default-settings retry `failed to start
  turn: internal error; agent loop died unexpectedly`. New blocker:
  `Results/agent_packets/blockers/PMO-WEIXIN-GATEWAY-R2-DISPATCH-SURFACE-20260606-002.json`.
  The Sunray150 `battery.png` / `guard_landing_gear.png` review packet remains
  undelivered. Route the combined Gateway Ops thread-dispatch recovery plus
  WeChat `ret=-2` / email fallback handling to `MoSim｜CoAgent运维平台`
  (`019e9bc1-ea9f-7102-b41a-4ef9b2308992`); do not retry WeChat or the
  Gateway Ops visible thread in a loop.
- 2026-06-06 CST: CoAgentOps diagnosed `MoSim｜微信网关运维部-R2`
  (`019e9be0-534e-7c22-97ff-98fa7c2af39b`) as a visible-thread dispatch
  surface failure, not a WeChat `ret=-2` business failure. Evidence: R2 is
  listable/readable and title-writable, and its initialization turn completed,
  but PMO production dispatch and CoAgentOps no-op start-turn probes failed
  with `agent loop died unexpectedly`. User corrected the operating rule:
  next time, complete the bounded recovery ladder before creating a replacement.
  Because the user then explicitly said "新建吧", CoAgentOps created exactly
  one replacement, `MoSim｜微信网关运维部-R3`
  (`019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c`). Its first initialization turn was
  interrupted by the user, then a minimal initialization follow-up completed
  successfully. Production gateway dispatch should use R3; R2 remains
  quarantined unless PMO explicitly restores it through a later no-op recovery
  ladder. The earlier WeChat `ret=-2` Sunray packet retry had already
  succeeded in
  `Results/agent_packets/returns/COAGENTOPS-WEIXIN-GATEWAY-R2-DISPATCH-RET2-RECOVERY-20260606-003.json`.
- 2026-06-06 CST: ROS2 Runtime R3 completed 028 as a blocker, not a pass.
  It generated a longer accepted body-frame source under
  `Results/ros2_runtime/b1_long_noloop_source_gate_20260606_028/`: 120 frames,
  `body_lidar_m_z_up`, 0.0..11.9 s, about 15.6k-17.2k points/frame. The no-goal
  runner used `loop=false`, replay completed 120/120 frames, Livox/IMU probe
  passed (`/mosim/livox/lidar` 38 samples around 9.3 Hz, IMU 770 samples around
  191 Hz, both monotonic), and FAST-LIO output topics were nonzero
  (`/Odometry=47`, `/cloud_registered=46`). The hard gate still failed because
  `fast_lio.launch.log` contains one `lidar loop back, clear buffer`. Blocker:
  `Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-LONG-NOLOOP-SOURCE-GATE-20260606-028.json`.
  This restores source/output plumbing only; it is not FAST-LIO success,
  planner_ready, local-map quality, controller performance, mission success, or
  closed_loop. Next task is a narrow FAST-LIO timestamp/startup-reset diagnosis
  before any planner/EGO goal, PositionCommand recorder, or 20 Hz adapter.
- 2026-06-06 CST: PMO created and dispatched 029,
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-FASTLIO-TIMESTAMP-DIAG-20260606-029.json`,
  to ROS2 Runtime R3 (`019e9c72-ee74-79d1-b9fe-621d3c6fc99e`). Read-only
  source audit found the same FAST-LIO ROS2 candidate log string can be printed
  by PointCloud2 callback, Livox CustomMsg callback, or IMU callback; 028's
  first visible IMU stamp was about 14.07 s earlier than the first visible
  Livox stamp. 029 is limited to callback-labeled temporary diagnostics in the
  imported candidate under `Results/tmp/`, first-N Livox/IMU timestamp tracing,
  and at most one no-goal micro-probe. It must not enter EGO/planner acceptance,
  publish goals, run PositionCommand recorder, start the 20 Hz adapter, edit
  `References/`, or change extrinsics/frame adapters.
- 2026-06-06 CST: MWORKS Dynamics And Control Verification R2 completed task
  `RFLY-MOSIM-MWORKS-CONTROL-DOWNSTREAM-OUTPUT-GROUP-20260606-020`.
  `FactoryTraceIso26ControllerOutputAliasSmoke` extends the passing Iso25
  bridge and adds exactly one downstream controller/pre-actuator alias
  observation group. P0 GUI sentinel was clean before and after, Sysplorer MCP
  health passed, `check_model` passed, 0-2 s `simulate_model data=true`,
  `GetVarTimes=1001`, and selected aliases were readable. No new `connect()`,
  actuator/motor/speedSensor reconnect, direct PosMea/AngleMea reconnect, or
  full Factory wrapper retry occurred. Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-DOWNSTREAM-OUTPUT-GROUP-20260606-020.json`.
  This is only incremental result-context evidence, not Factory trace
  consumption, closed_loop, controller performance, plant tracking, mission
  success, or parameter identification.
- 2026-06-06 CST: PMO created and dispatched MWORKS 021,
  `Results/agent_packets/tasks/mworks/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-PREFLIGHT-GROUP-20260606-021.json`,
  to MWORKS R2 (`019e9be5-334b-76b1-93f9-8b02caebf376`). The next gate fixes
  the baseline to Iso26 and permits only one actuator-input/preflight group, or
  a precise blocker at the first actuator boundary. It still forbids full
  Factory wrapper retry, actuator flange/chassis/speedSensor/full plant paths
  together, parameter changes, and any Factory trace/closed-loop/performance
  claim.
- 2026-06-06 CST: Codex App crashed/restarted during visible-thread recovery.
  User confirmed CoAgentOps also needs an hourly self-maintenance automation,
  with Gateway Ops checked first but CoAgentOps acting as fallback when a
  specialist thread is half-dead. Initial implementation mistakenly created a
  detached workspace cron `mosim-coagentops`; user corrected that PMO-style
  self-maintenance must land in the CoAgentOps conversation itself. Fixed by
  updating existing automation `mosim-wechat-gateway-hourly-health` into a
  single hourly heartbeat named `MoSim｜CoAgentOps 小时巡检`, targeting
  CoAgentOps thread `019e9bc1-ea9f-7102-b41a-4ef9b2308992`, with no explicit
  model/reasoning override. Deleted the redundant detached cron
  `mosim-coagentops`. Updated `Docs/Workflows/coagent_meta_maintenance.md` with
  the priority plus fallback policy: one CoAgentOps-thread heartbeat checks
  Gateway Ops R3 first, then writes blocker/takes urgent recovery ownership if
  the specialist cannot start turns.
- 2026-06-06 CST: ROS2 Runtime R3 completed 029 as diagnostic return, not as a
  FAST-LIO success gate. Callback-labeled temporary logs in the imported
  `Results/tmp` FAST-LIO candidate showed the remaining 028 loop-back came from
  `imu_cbk` / `imu_stamp_regression_at_startup_boundary`, not LiDAR callback
  timestamp regression and not no-repro clean. The event occurred before first
  accepted LiDAR (`last_timestamp_lidar=0`, `is_first_lidar=1`,
  `lidar_buffer_size=0`) while the IMU buffer was already large. This no-goal
  micro-probe did not restore FAST-LIO output counts, so it is not planner_ready
  or local-map quality evidence. Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-FASTLIO-TIMESTAMP-DIAG-20260606-029.json`.
  Next ROS2 work must be a bounded IMU startup discipline no-goal gate before
  returning to 028, with zero callback-labeled loop-back and nonzero FAST-LIO
  outputs required before any planner/EGO/20 Hz adapter work.
- 2026-06-06 CST: MWORKS Dynamics And Control Verification R2 completed task
  `RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-PREFLIGHT-GROUP-20260606-021`.
  `FactoryTraceIso27ActuatorInputAliasSmoke` extends passing Iso26 and adds
  exactly one read-only actuator-input alias consistency group:
  `actuator1_1.u` through `actuator1_4.u`, per-motor error against
  `pre_actuator_command_1..4`, and `actuator_input_abs_error_sum`. The previous
  interrupted turn had no return/blocker packet; on resume the existing result
  context was empty, so R2 performed the one allowed 0-2 s smoke rerun after
  clean GUI sentinel and MCP health. `check_model` passed, `simulate_model
  data=true`, `GetVarTimes=1001`, aliases were readable, and actuator input
  error sum was `0.0`. Evidence:
  `Results/mworks_trace_consumption/actuator_preflight_group_20260606_021/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-PREFLIGHT-GROUP-20260606-021.json`.
  This is only actuator-input/preflight result-context evidence, not Factory
  trace consumption, full actuator/plant closure, closed_loop, controller
  performance, plant tracking, mission success, parameter identification,
  planner readiness, or live UE/ROS2 ack.
- 2026-06-06 CST: PMO completed `QuadrotorExperiments` package classification
  cleanup after the user reported the package tree was chaotic. Added
  categorized compatibility entries with Chinese descriptions:
  `OfficialScenarios`, `ControllerBaselines`, `RobustFaultScenarios`,
  `PlanningScenarios`, `SceneTraceScenarios`, `TraceIsolation`,
  `DynamicsUpgrade`, `SystemArchitecture`, `SystemModules`, `SupportModels`,
  and `FormationScenarios`. Updated `package.order`, registered the real
  formation model `FormationTriangleFigure8LinearMPCSysblockClosedLoop`, and
  deleted only `Sunray150DynamicsUpgradeSmoke.mo` after proving it was an
  exact duplicate of three classes already embedded in `package.mo`. Static
  checks passed: no missing `.mo` entries in `package.order`, no invalid
  package.order entries, no duplicate order entries, all terminal `extends`
  targets found, and `git diff --check` clean. Sysplorer MCP representative
  checks passed on dedicated port `49153`: dynamics, physical wrench, trace
  isolation Iso27, echo support, formation, controller baseline, system module,
  and complete-system aliases all checked after loading `QuadrotorModel` plus
  the needed independent Sysblock controller files. Evidence:
  `Results/mworks_package_cleanup/20260606_quadrotor_experiments_classification/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-QUADROTOR-EXPERIMENTS-CLASSIFICATION-20260606-013.json`.
  This is package organization evidence only, not final physical subpackage
  migration, controller performance, parameter identification, live runtime
  ack, planner readiness, or closed_loop. MWORKS 012 package-restructure lock
  is lifted; resume it only after reloading current package plus needed
  controller dependencies and running the GUI sentinel.
- 2026-06-06 CST: CoAgentOps hourly maintenance reported a real dispatch
  registry drift: production Gateway Ops should use `MoSim｜微信网关运维部-R3`
  (`019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c`), while
  `CoAgent/dispatch/department_threads.json` still pointed WeChatGatewayOps to
  quarantined R2 `019e9be0-534e-7c22-97ff-98fa7c2af39b`. PMO corrected the
  registry row to R3 and preserved the R2 quarantine note. Evidence blocker:
  `Results/agent_packets/blockers/COAGENTOPS-HOURLY-MAINTENANCE-20260606-2003.json`.
- 2026-06-06 CST: PMO verified the UE console and Sunray/PBR department
  threads are visible and dispatched the next two narrow P0 continuation tasks:
  `RFLY-MOSIM-UE-CONSOLE-DISABLED-STATE-CONTRACT-SMOKE-20260606-007` to
  `MoSim｜UE实验控制台与场景交互部`
  (`019e9b24-50aa-7cd3-9e7c-4c43b224d993`) and
  `RFLY-MOSIM-SUNRAY150-REVIEW-PACKAGE-HYGIENE-20260606-003` to
  `MoSim｜Sunray150资产与PBR审核部`
  (`019e9b25-066e-7372-8152-209c2b1322a4`). Both packets require
  department-local planning fields and `subagent_plan`. UE 007 is source/static
  disabled-state contract work only, not live receiver/UI/Blueprint/runtime
  evidence. Sunray 003 is review-package/path-neutral hygiene only, not
  material rework or final material acceptance.
- 2026-06-06 CST: UE Experiment Console department completed
  `RFLY-MOSIM-UE-CONSOLE-DISABLED-STATE-CONTRACT-SMOKE-20260606-007`.
  Added `Scripts/UE5/check_ue_console_disabled_state_contract.py` and
  `Scripts/tests/test_ue_console_disabled_state_contract.py` as a source/static
  fixture contract. The matrix covers controller switch, planner switch, wind
  disturbance, fault injection, and map/scene switch controls: pending rows
  remain `disabled_pending_echo`; `offline_adapter_smoke`,
  `source_level_smoke`, `MWORKS_MCP_result_adapter_smoke`, and
  `MWORKS_MCP_runtime_adapter_preflight` remain `quality_status=smoke_only`
  with `accepted_as_runtime_ack=false`; rejected rows remain disabled; and only
  a future live `mosim.ue_command_echo.v1` fixture can represent enabled
  accepted state. Evidence:
  `Results/unreal_experiment_console/console_disabled_state_contract_20260606_007/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-DISABLED-STATE-CONTRACT-SMOKE-20260606-007.json`.
  No UE GUI, Blueprint/UMG/assets, runtime receiver, MWORKS/Sysplorer/Syslab
  runtime, ROS2/RViz2/FAST-LIO/planner runtime, or live ack claim occurred.
- 2026-06-06 CST: UE Experiment Console department completed
  `RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-ACCEPTANCE-FIXTURE-CONTRACT-20260606-008`.
  Added `Scripts/UE5/check_ue_live_echo_acceptance_fixture_contract.py` and
  `Scripts/tests/test_ue_live_echo_acceptance_fixture_contract.py` as a
  source/static accepted-state fixture contract. Future enabled accepted state
  requires `mosim.ue_command_echo.v1` plus authoritative source
  (`MWORKS_live_downlink`, `ROS2_runtime_echo`, or
  `MWORKS_ROS2_live_downlink`), command id (`run_id`, `request_id`, `seq`,
  `command.kind`), timestamp (`time_s`), status, ack authority, and
  `no_pose_overwrite_status=pass`. Valid future accepted fixtures cover
  controller, planner, wind, fault, and scene switch controls. Smoke/source/
  preflight rows, rejected rows, authority mismatch rows, and missing
  command-id/timestamp/status rows remain disabled or invalid fixture, not
  runtime accepted. Evidence:
  `Results/unreal_experiment_console/live_echo_acceptance_fixture_contract_20260606_008/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-ACCEPTANCE-FIXTURE-CONTRACT-20260606-008.json`.
  No UE GUI, Blueprint/UMG/assets, runtime receiver/socket/UDP implementation,
  MWORKS/Sysplorer/Syslab runtime, ROS2/RViz2/FAST-LIO/planner runtime, or
  live ack/planner_ready/closed_loop/controller-performance claim occurred.
- 2026-06-06 CST: Sunray150 Asset/PBR department completed
  `RFLY-MOSIM-SUNRAY150-REVIEW-PACKAGE-HYGIENE-20260606-003`. It generated a
  path-neutral review package index and Markdown manual-review checklist under
  `Results/unreal_scene_mapping/sunray150_review_package_hygiene_20260606_003/`,
  covering 20 component PNGs across 5 review batches, including `battery.png`
  and `guard_landing_gear.png`. All 20 PNGs are present, non-empty, RGBA
  1400x1050, and non-flat. The source manifest remains recoverable via
  `project_relative_path` but still contains legacy absolute `path` fields and
  an absolute top-level `source_blend`; the new review package uses
  project-relative paths only. Return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-SUNRAY150-REVIEW-PACKAGE-HYGIENE-20260606-003.json`.
  This is file/package readiness only: manual visual review remains required,
  and there is no final material acceptance, UE import/export final acceptance,
  runtime success, planner_ready, closed_loop, or controller-performance claim.
- 2026-06-06 CST: MWORKS Dynamics/Control R2 completed
  `RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-RESUME-20260606-014`. It added
  project-owned `FactoryTraceIso28ActuatorToWrenchBridgeSmoke`, extending Iso27
  and feeding `actuator_input_1..4` into an independent
  `Sunray150PhysicalWrenchFrameAdapter` command surface. P0 GUI sentinels were
  clean, Sysplorer health passed, baseline/controller/package force-loads
  passed, parent checks passed, `check_model` passed, 0-0.25 s
  `SimulateModel data=true`, `GetVarTimes=251`, and sampled bridge command,
  force/torque application, motor-order, and yaw-direction errors were all
  zero. Evidence:
  `Results/mworks_dynamics_upgrade/20260606_014_actuator_to_wrench_bridge_resume/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-RESUME-20260606-014.json`.
  This is a minimal sidecar actuator-input alias to physical-wrench adapter
  smoke only, not Factory trace consumption, full Factory wrapper retry,
  actuator flange/chassis/speedSensor/full plant closure, controller
  performance, parameter identification, planner_ready, live runtime ack, or
  closed_loop.
- 2026-06-06 CST: MWORKS Dynamics/Control R2 completed
  `RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015`. It added
  project-owned `FactoryTraceIso29ExternalFrameWrenchBoundarySmoke`, extending
  Iso28 and applying wrapper force/torque to a new explicit
  `external_test_body` through a new `external_force_and_torque` component.
  P0 GUI sentinels were clean, Sysplorer health passed,
  baseline/controller/package force-loads passed, Iso28/Iso29 `check_model`
  passed, 0-0.25 s `SimulateModel data=true`, `GetVarTimes=251`, and sampled
  external force/torque application and adapter-match errors were all zero.
  Evidence:
  `Results/mworks_dynamics_upgrade/20260606_015_wrench_to_external_frame_boundary/`;
  return packet:
  `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015.json`.
  This is minimal external MultiBody frame/test-body boundary evidence only,
  not Factory trace consumption, QuadChassis/full plant closure, actuator
  flange/speedSensor chain, controller performance, parameter identification,
  planner_ready, live runtime ack, mission success, or closed_loop.
- 2026-06-06 CST: PMO changed Sunray150 PBR work back to department execution
  after user correction that the main thread should not spend time
  implementing the texture pass. PMO updated the Sunray PBR workflow with the
  external-source adoption rule, added a Sunray PBR/material source row to the
  external learning index, created
  `RFLY-MOSIM-SUNRAY150-PBR-ELECTRONICS-CAMERA-REALISM-20260606-005`, and
  dispatched it to `MoSim｜Sunray150资产与PBR审核部`
  (`019e9b25-066e-7372-8152-209c2b1322a4`). The task is bounded to component
  PBR realism for the grey/flat camera, PCB/N150, ports/connectors, cables,
  battery, and guard/landing-gear review outputs, requires local planning
  fields and a disposable subagent slice if available, and forbids geometry,
  dynamics, extrinsics, controller, planner, ROS2/MWORKS runtime, and
  `References/` changes. PMO also dispatched
  `RFLY-MOSIM-SUNRAY150-PBR-SOURCE-WHITELIST-LEARNING-20260606-001` to
  `MoSim｜开源项目学习部-R2` for source whitelist/adopt-adapt-reference-reject
  advice only. Main-thread role is now coordination, return integration, and
  opening/showing the resulting contact sheet for manual review; no final
  material acceptance is claimed.
- 2026-06-06 CST: PMO integrated three department returns while keeping the
  Sunray150 PBR implementation delegated to `MoSim｜Sunray150资产与PBR审核部`.
  Open Source Learning R2 completed the PBR source whitelist: no broad crawl is
  needed now; use named CC0 Poly Haven/ambientCG assets and local procedural/UV
  tooling, while YunDrone/N150/Livox images remain visual reference-only.
  MWORKS R2 completed static graphical-model inventory only; P0 GUI review
  candidates are FormationTriangle, Sunray150UEFactoryTraceTable smoke, and the
  FactoryTrace Iso chain, but static inventory is not graphical acceptance.
  ROS2 R1 completed 034 active-window recovery: Livox/IMU and FAST-LIO outputs
  were nonzero/monotonic in the active window, `/Odometry=20`,
  `/cloud_registered=20`, loop-back total was zero, and forbidden planner/
  setpoint topics were absent. The remaining ROS2 risk is TF/RViz readiness:
  late diagnostics did not capture `camera_init -> body` and did not observe a
  `ue_world <-> camera_init` bridge. PMO created and queued 035 for a bounded
  no-goal TF/RViz diagnostic and 017 for a bounded MWORKS yaw-transient evidence
  gate. MWORKS R2 GUI review is intentionally not run concurrently with R1,
  because both contend for the same existing Sysplorer/MWORKS session.
- 2026-06-07 CST: PMO integrated MWORKS R2 009. R2 completed the static-only
  `QuadrotorControllerBlocks` package alias repair by replacing all 19
  leading-dot wrapper aliases with explicit package-local alias targets in
  `package.mo`. It did not touch the 19 controller `.mo` files, backup/upgrade
  history, package.order, GUI, MCP, `check_model`, simulation, or Smart Layout;
  `live_mworks_touched=false`. This clears the static alias spelling issue
  found in 008 but does not clear live Sysplorer/package-browser acceptance,
  because the reusable Sysplorer window was still classified as demo/license
  blocked by 008.
- 2026-06-07 CST: PMO integrated ROS2 R1 038. R1 completed a read-only/static
  diagnosis of the 037 Livox regression and used one disposable read-only
  subagent. 034 and 037 used the same source, rates, loop flags, and declared
  startup order; the key 037 difference was active `/tf` capture plus TF edge
  wait conditions. 037 also showed dense LiDAR publish-cost anomaly and Livox
  active timestamp regression matching the FAST-LIO `livox_pcl_cbk` loop-back
  timebase. Classification is diagnostic-tooling/load-sensitive runtime Livox
  publication regression, not source ordering. This is not TF/RViz readiness,
  FAST-LIO success, localization/local-map quality, planner_ready, controller
  performance, mission success, or closed_loop evidence.
- 2026-06-07 CST: PMO strengthened the MWORKS dispatch rule after user
  correction. Every future live MWORKS/Sysplorer/Syslab task must run a
  preflight activation sentinel/background screenshot before any MCP/model/GUI
  operation and must return `activation_sentinel_before`, optional
  `background_screenshot_before`, `license_state`,
  `will_not_click_activation_login=true`, and `live_mworks_touched`. Demo
  edition, unactivated/login/authorization state, GUI error report, or unknown
  sentinel state is a blocker, not a model or solver tuning task. PMO synced
  this rule to MWORKS R1 and R2 through native visible-thread dispatch.
- 2026-06-07 CST follow-up: MWORKS R1 and R2 both acknowledged the live
  activation-sentinel dispatch contract without touching MWORKS GUI/MCP. R1
  wrote `MWORKS-R1-LIVE-ACTIVATION-SENTINEL-CONTRACT-ACK-20260607-001`; R2
  wrote `RFLY-MOSIM-MWORKS-R2-LIVE-ACTIVATION-SENTINEL-CONTRACT-ACK-20260607`.
  Treat future live MWORKS return/blocker packets as incomplete if they omit
  the activation sentinel, license state, no-click pledge, and
  `live_mworks_touched` fields. Static-only MWORKS tasks must explicitly state
  `live_mworks_touched=false`.
- 2026-06-07 CST: PMO prepared ROS2 R1 task
  `RFLY-MOSIM-ROS2-RUNTIME-B1-LOW-LOAD-SOURCE-OUTPUT-RECOVERY-20260607-039`
  after 038. 039 is the next real runtime gate that does not depend on MWORKS
  license recovery: restore 034-style low-load active Livox/IMU and
  `/Odometry`/`/cloud_registered` source/output acceptance, keep `/tf` out of
  the active recorder, move TF observation to post-active/gap evidence, and
  require zero FAST-LIO loop-back before any planner, PositionCommand, 20 Hz
  adapter, TF/RViz readiness, localization-quality, local-map-quality, mission,
  controller-performance, or closed-loop claim.
- 2026-06-07 CST: PMO confirmed the user's report that MWORKS activation state
  had drifted again, using only read-only local evidence. The Win32 sentinel
  detected `license_or_login` with matched pattern `演示版`, and background
  screenshots showed mixed Sysplorer state: one window in `[教育版]` and the
  `QuadrotorControllerBlocks` window in `[演示版]`. PMO wrote blocker
  `PMO-MWORKS-ACTIVATION-DRIFT-20260607-001`, updated the dispatch contract so
  every live MWORKS task packet must include `mworks_live_gate`, and prepared
  `PMO-MWORKS-ACTIVATION-SENTINEL-PRACTICE-20260607-010` for R1/R2. Until a
  later clean preflight identifies a valid reusable session, live MWORKS MCP,
  package acceptance, graphical review, check_model, translate, simulate, plot,
  and animation work remain blocked; static-only work may continue only with
  `live_mworks_touched=false`.
- 2026-06-07 CST: PMO integrated ROS2 R1 039 as a blocker. R1 ran the single
  allowed no-goal low-load source/output probe with active `/tf` capture
  removed. The run still failed before any planner/goal work: active Livox and
  IMU stamps were nonmonotonic, and FAST-LIO reported three callback-labeled
  loop-back events (`livox_pcl_cbk=1`, `imu_cbk=2`). `/Odometry` and
  `/cloud_registered` remained nonzero/monotonic, dense LiDAR publish stats
  were normal, forbidden planner/setpoint topics were absent, and cleanup was
  clean. This blocks source/output recovery even without active `/tf` recorder
  load; it is not TF/RViz readiness, FAST-LIO success, localization/local-map
  quality, planner_ready, controller performance, mission success, or
  closed_loop evidence.
- 2026-06-07 CST: PMO completed the MWORKS activation-sentinel practice gate
  for both MWORKS departments after the user pointed out that live MWORKS
  tasks must check activation before model work. R1 and R2 each ran only the
  read-only Win32 sentinel plus background screenshot path, detected the same
  mixed license state (`[教育版]` window plus `[演示版]` window), and returned
  `license_or_login` blockers with `will_not_click_activation_login=true` and
  `live_mworks_touched=false`. This proves the department rule is now
  executable: future live MWORKS dispatches must include `mworks_live_gate`, and
  missing/unknown/demo activation state is a blocker, not a solver/model
  tuning task. Live MWORKS acceptance remains blocked until a later clean
  sentinel verifies a valid reusable session; static file-only work can
  continue with `live_mworks_touched=false`.
- 2026-06-07 CST: PMO strengthened the MWORKS activation rule from prose to a
  machine-checkable gate. `Scripts/quality/check_mworks_live_gate.py` now
  validates live MWORKS task packets and return/blocker packets for
  `mworks_live_gate`, preflight sentinel, background screenshot, license state,
  no-click pledge, and `live_mworks_touched`; tests passed with
  `python -m pytest Scripts/tests/test_mworks_live_gate.py
  Scripts/tests/test_agent_task_native_surface_gate.py -q`. PMO also updated
  MWORKS skills/workflows and `CoAgent/dispatch/dispatch_helper.py` so R1/R2
  dispatch text explicitly reminds departments to screenshot/check activation
  before any live MCP/model/GUI work. A fresh read-only PMO sentinel still
  shows mixed `[教育版]`/`[演示版]` Sysplorer state, so live MWORKS remains
  blocked; PMO sent R1/R2 synchronization prompts and is waiting for brief
  acknowledgement packets.
- 2026-06-07 CST: MWORKS live-gate synchronization completed. R1 returned
  `MWORKS-R1-LIVE-GATE-MACHINE-CHECK-CONTRACT-ACK-20260607-002`; R2 returned
  `PMO-MWORKS-R2-LIVE-GATE-HARD-CONSTRAINT-SYNC-20260607-011`. Both static
  ack packets passed `check_mworks_live_gate.py --kind return --expect static`.
  Future live MWORKS dispatches must include the gate and future live
  return/blocker packets can be rejected by PMO if they omit activation
  sentinel evidence, background screenshot evidence, license state, the
  no-click pledge, or `live_mworks_touched`.
- 2026-06-07 CST: PMO closed the remaining MWORKS department loophole after
  the user clarified that every MWORKS assignment must first screenshot/check
  activation state. The rule is now stricter than "live only": any future
  MWORKS R1/R2 business dispatch, including static model organization and R2
  graphical/layout audit preparation, must start with existing-window
  activation sentinel plus background screenshot and must return
  `mworks_window_evidence_touched=true`. Static business work after that
  preflight uses `live_mworks_touched=false`; MCP/load/check/translate/
  simulate/plot/animation/GUI review uses `live_mworks_touched=true`.
  `Scripts/quality/check_mworks_live_gate.py --expect department` now enforces
  this. R1 and R2 wrote 013 static rule-sync ACK packets; they intentionally
  pass `--expect static` only because PMO forbade screenshot/GUI in the ACK
  turn, so they are not activation/window-readiness evidence. Live MWORKS work
  remains blocked until a later clean sentinel resolves the current mixed
  `[教育版]`/`[演示版]` state.
- 2026-06-07 CST: PMO converted the MWORKS screenshot/activation rule from a
  remembered instruction into the department dispatch template. MWORKS R1/R2
  dispatch text now includes the exact sentinel and background capture
  commands, states that the target department must run them itself, and
  requires a blocker with `license_state=sentinel_unavailable_blocked` if the
  department cannot run the tools. Added a regression test for the dispatch
  helper text and reran `python -m pytest
  Scripts/tests/test_dispatch_helper_mworks_gate.py
  Scripts/tests/test_mworks_live_gate.py -q` successfully. PMO wrote task
  packet
  `PMO-MWORKS-R1R2-BACKGROUND-SCREENSHOT-ACTIVATION-DRILL-20260607-014`,
  verified it with `check_mworks_live_gate.py --kind task --expect department`,
  and dispatched it to MWORKS R1 and R2. The drill requires each department to
  run its own existing-window sentinel/background screenshot and return a
  machine-checkable department blocker/return packet; no MWORKS model,
  Sysplorer MCP, GUI click, check_model, simulation, graphical acceptance,
  controller-performance, planner_ready, live ack, or closed_loop claim is
  permitted.
- 2026-06-07 CST: PMO closed the P0 MWORKS authorization infrastructure
  incident. After `session_manager(action="ensure")`, the reusable Sysplorer
  window was in `[演示版]` and `License(ltype="info")` reported demo state;
  maximizing/focusing the existing window exposed the official login/license
  pane that background screenshot alone did not reveal. With user-authorized
  foreground recovery on the existing window, PMO restored the account license:
  final title is `Sysplorer [教育版]`, API reports `教育版`, 149 days remaining,
  78 licensed modules, and `activate_account=true`; final sentinel is clean and
  final background screenshot shows the education-mode main window with no
  blocking license dialog. Return packet:
  `Results/agent_packets/returns/PMO-MWORKS-INFRA-RECOVERY-20260607-001.json`.
  The main MWORKS/Sysplorer window remains open for reuse. Rule update: a
  clean-looking background screenshot is not sufficient if title/sentinel/API
  indicates demo/login/authorization risk; departments must block and PMO owns
  any user-authorized foreground recovery. This is authorization recovery only,
  not model check, simulation, graphical/layout acceptance, controller
  performance, planner_ready, runtime ack, or closed_loop evidence.
- 2026-06-07 CST: PMO completed the postmortem hardening for the MWORKS
  activation/license outage after the user escalated the 6-hour wasted-progress
  failure. Root cause is classified as a combined PMO/department/probe/
  acceptance failure, not a single subthread mistake: PMO kept accepting
  JSON-only control-plane packets while the real critical path required `.mo`,
  `check_model`, simulation, or graphical/layout evidence; MWORKS departments
  did not consistently stop on license/login blockers; the previous sentinel
  could be fooled by one clean `[教育版]` window while another relevant window
  was `[演示版]` or login-required; and Computer Use was still present in older
  docs despite the project moving to Windows MCP/Win32 routes. The fix is now
  executable: `Scripts/agent/check_mworks_gui_sentinel.py` reports all
  MWORKS/Sysplorer/Syslab windows, mixed/unknown/license state, window counts,
  and an all-window license gate; `Scripts/quality/check_mworks_live_gate.py`
  rejects MWORKS department task packets without `expected_engineering_outputs`
  and rejects completed MWORKS returns that only provide JSON/ledger/progress
  metadata unless explicitly diagnostic/rule-sync/preflight-only. Updated
  AGENTS, orchestration/communication/tooling docs, Codex capability index, and
  MWORKS skills to state that Computer Use is deprecated for MWORKS and that
  one relevant bad window blocks the whole task. Tests passed:
  `python -m pytest Scripts/tests/test_mworks_gui_sentinel.py
  Scripts/tests/test_mworks_live_gate.py
  Scripts/tests/test_dispatch_helper_mworks_gate.py -q`, plus py_compile for
  the changed scripts. This is infrastructure hardening only, not MWORKS model
  optimization or simulation evidence.
- 2026-06-07 CST: PMO found and fixed one remaining MWORKS sentinel ambiguity
  during the postmortem recheck. The first live Win32 sentinel recheck saw one
  `[教育版]` Sysplorer window and five unknown MWORKS/Sysplorer-like windows;
  this exposed both a misleading clean hint risk and an over-broad
  `unknown_blocked` risk. PMO repaired
  `Scripts/tools/capture_window_background.ps1` so it captures all matching
  top-level windows with Win32 `EnumWindows` instead of only
  `Get-Process.MainWindowTitle`. The all-window screenshot manifest showed the
  five unknown windows are hidden Qt/browser-proxy/helper windows, not visible
  login/demo/authorization windows. `check_mworks_gui_sentinel.py` now
  separates visible unknown windows from hidden unknown helper windows:
  explicit demo/login/activation/authorization/error-report and visible
  unknown windows block; hidden unknown helper windows are counted as risk
  evidence but do not alone block a clean education window. The current live
  sentinel now returns `status=clean`,
  `license_state_hint=education_clean_preflight`,
  `hidden_unknown_mworks_window_count=5`, and
  `visible_unknown_mworks_window_count=0`. Targeted tests and py_compile
  passed. PMO also updated the native capability docs so Computer Use is
  deprecated for MoSim desktop GUI work generally, not only MWORKS. This is
  infrastructure evidence only; no MWORKS model optimization, graphical/layout
  acceptance, `check_model`, simulation, controller evidence, planner_ready,
  runtime ack, or closed_loop claim is made.
- 2026-06-07 CST: PMO integrated the latest P0 department returns after the
  MWORKS activation hardening. MWORKS R1 006 returned a valid blocker:
  `session_manager(action=health)` appeared to start a new Sysplorer/MWORKS
  process instead of proving reuse of the existing logged-in session, so R1
  stopped before `load_file`, `check_model`, and `SimulateModel`. The source
  alias patch in `Models/MoSimQuadrotorModel/Dynamics/package.mo` remains
  source-level and unverified by live MWORKS checks. MWORKS R2 011 completed
  static graphical/package-browser audit preparation for `MoSimQuadrotorModel`
  with a 126-candidate inventory, diagram/layout risk matrix, serialized
  live-audit queue, and no true missing project-source blocker. UE 017
  completed the source-static command-echo producer/consumer gate definition
  and false-ack rejection coverage; it is not live UE runtime ack. CoAgentOps
  restored ROS2 R1 dispatch surface with exact no-op
  `ros2_r1_post_restart_noop_received_20260607_2128`, and PMO re-dispatched
  ROS2 059; the ROS2 059 turn is still in progress and has not returned an
  engineering packet yet.
- 2026-06-07 CST: PMO prepared CoAgentOps task
  `PMO-COAGENTOPS-MWORKS-REUSABLE-SESSION-REBIND-20260607-001` to diagnose
  and fix or precisely block the MWORKS/Sysplorer MCP reusable-session route.
  This is now the next MWORKS infrastructure action before re-running R1 006
  or any live R2 graphical audit. The task explicitly forbids treating
  "MCP health started a new window" as success. No model optimization,
  `check_model`, simulation, graphical acceptance, controller performance,
  planner_ready, runtime ack, mission success, or closed_loop evidence is
  claimed from this infrastructure handoff.
- 2026-06-07 CST: PMO integrated ROS2 R1 059 and CoAgentOps MWORKS
  reusable-session diagnosis. ROS2 R1 059 returned completed source-only
  normal-exit evidence: the single authorized no-goal replay-time probe exited
  cleanly, LiDAR produced 120 monotonic frames at about 20.15 Hz, IMU produced
  1500 monotonic messages at about 200 Hz, forbidden planner/setpoint topics
  were absent, and cleanup was clean. This is not true 20 Hz sensor capture,
  FAST-LIO success, TF/RViz readiness, planner_ready, controller performance,
  mission success, or closed_loop. CoAgentOps returned the MWORKS
  reusable-session task as blocked: no-start `probe` can inspect an existing
  port, but `session_manager(action=health)` still starts a new Sysplorer/
  MWORKS process and new dedicated port, so MWORKS live model gates and live
  graphical audits remain paused until an attach-only/no-start route is fixed
  and validated. UE 018 is still in progress and has not returned a packet yet.
- 2026-06-07 CST: PMO continued the ROS2 FAST-LIO P0 path after 061. The new
  062 task packet was validated and dispatched to ROS2 R1 with `gpt-5.5` /
  `xhigh`; `read_thread` confirms the 062 turn is in progress with agent
  commentary, but no return/blocker packet exists yet. 062 remains bounded to
  evidence-local helper/runner artifacts and at most one no-goal FAST-LIO-only
  source-lifecycle retest. No TF/RViz, planner/EGO, PositionCommand, 20 Hz
  adapter, UE, MWORKS, production config/source/extrinsic edits, fake data,
  planner_ready, controller performance, mission success, or closed_loop claim
  is made.
- 2026-06-08 CST: CoAgentOps 13:54 patrol found no observable true
  MWORKS/Sysplorer/Syslab main window: the GUI sentinel reported
  `target_window_count=0` and `license_state_hint=no_mworks_window_observed`,
  while `manage_mworks_windows.ps1 -Mode List` reported `window_count=0`.
  This is not a visible login/license/authorization/GUI-error incident, but it
  blocks MWORKS graphical review and live MWORKS R1/R2 handoff. The patrol
  classified MWORKS window/session state as `unknown_blocked`, and MWORKS
  R1/R2 dispatch readiness as `idle_blocked_by_open_dependency` rather than
  quiet idle/healthy. Sparse Chinese email audit:
  `Results/coagent_gateway/email/email_alert_20260608_140010.json`. Blocker:
  `Results/agent_packets/blockers/COAGENTOPS-HEARTBEAT-P0-MWORKS-MAIN-WINDOW-MISSING-20260608-0554.json`.
  The finding was also synchronized to the PMO thread for dispatch/recovery
  decision. No MWORKS GUI recovery, MCP live action, `check_model`,
  simulation, graphical acceptance, controller-performance, planner_ready,
  runtime ack, or closed_loop claim was made.
- 2026-06-08 CST: PMO repaired a Codex App visible-thread title/routing drift
  after a history synchronization attempt changed display names. The canonical
  routing source remains `CoAgent/dispatch/department_threads.json`; PMO
  corrected the visible titles for PMO, CoAgentOps, open-source probe/learning,
  context maintenance, and historical WechatCodex, and the user confirmed the
  Codex environment migration thread is archived/not dispatchable. Route-sync
  packet:
  `Results/agent_packets/returns/PMO-CODEX-THREAD-TITLE-ROUTE-SYNC-20260608-001.json`.
  After validating the prepared task packets, PMO resumed safe P0 dispatch:
  MWORKS R1 023 is now running as a static-only MoSimQuadrotorModel
  smoke/check surface task, and UE 028 is running as a source-static runtime
  probe harness prep task. Both target turns have started and shown agent
  commentary. ROS2 070 and live MWORKS/R2 graphical review remain blocked on
  their existing GUI/review/window surfaces; no planner_ready, closed_loop,
  runtime ack, MWORKS live check, or controller-performance claim is made.
- 2026-06-08 CST: PMO completed a supplemental Codex App title hygiene pass
  after the user restored archived threads whose display names were also
  corrupted by the history sync. Historical MoSim routes were renamed with
  explicit display-only suffixes (`-历史` / `-旧`) for environment migration,
  WeChat gateway R2/R3, and WechatCodex; ROS2 R2 was corrected back to the
  non-historical title `MoSim｜ROS2感知定位与规划运行部-R2`; recent DH history
  threads were shortened to clear project titles. The registry and routing docs
  now state that restored archived threads were renamed only for UI hygiene,
  while ROS2 R2 is not historical and production dispatch still follows
  registry/user confirmation. Supplement packet:
  `Results/agent_packets/returns/PMO-CODEX-THREAD-TITLE-ROUTE-SYNC-SUPPLEMENT-20260608-002.json`.
  No MoSim engineering, MWORKS, ROS2, UE, Git, or notification route claim is
  made from this title repair.
- 2026-06-08 CST: PMO rechecked the user-reported 14:40-era missing reply by
  current thread state and packet evidence, not elapsed time alone. MWORKS R1
  023 completed with a valid return packet at 14:57, and UE 028 completed with
  a valid return packet at 14:48; both packet contracts passed. The 15:12
  CoAgentOps readable-but-not-startable incident was initially recorded in
  `Results/agent_packets/blockers/PMO-COAGENTOPS-SELF-DEAD-START-TURN-FAILURE-20260608-002.json`
  with sparse email audit, but later same-thread evidence superseded the
  restart-pending state: CoAgentOps turn `019ea617-3571-7233-ae1c-d991673fbfb4`
  started and produced agent output. PMO wrote
  `Results/agent_packets/returns/PMO-COAGENTOPS-SELF-DEAD-START-TURN-RECOVERY-SUPERSEDE-20260608-002.json`;
  no Codex++ restart is required for that stale incident now. This
  control-plane correction does not claim MWORKS live check, ROS2/RViz runtime
  success, UE runtime ack, planner_ready, controller performance, mission
  success, or closed_loop.
- 2026-06-08 CST: CoAgentOps 15:16 patrol executed on the same visible
  CoAgentOps thread, superseding the earlier CoAgentOps self-dead
  restart-pending state at the `thread_execution_surface_restored` layer. The
  business patrol itself still found a P0 open dependency: read-only MWORKS
  evidence again reported no true main MWORKS/Sysplorer/Syslab window
  (`target_window_count=0`, `window_count=0`, only `syslab-mcp-server-win64`
  in process inventory). MWORKS R1/R2 dispatch readiness remains
  `idle_blocked_by_open_dependency`; ROS2 R1 remains
  `idle_waiting_review_or_approval`; no duplicate email was sent because the
  14:00 sparse email audit already covers this missing-window condition. New
  blocker:
  `Results/agent_packets/blockers/COAGENTOPS-HEARTBEAT-P0-MWORKS-MAIN-WINDOW-MISSING-20260608-0716.json`.
  No MWORKS/ROS2/UE live runtime, Codex++ restart, WeChat notification,
  `check_model`, simulation, graphical acceptance, controller performance,
  planner_ready, mission success, or closed_loop claim was made.
- 2026-06-08 CST: CoAgentOps 15:56 patrol repeated the control-plane and
  MWORKS window evidence after UE 029 had already been dispatched. PMO and
  CoAgentOps execution surfaces remain usable, UE 029 is `busy_in_progress`,
  and no new Codex++ restart is justified. Read-only MWORKS evidence still
  shows no true MWORKS/Sysplorer/Syslab main window
  (`target_window_count=0`, `window_count=0`, no `mworks.exe` main GUI
  process), so MWORKS R1/R2 live work and graphical review remain
  `idle_blocked_by_open_dependency`. No duplicate email was sent because the
  earlier sparse email already covers the unchanged missing-window condition.
  Blocker:
  `Results/agent_packets/blockers/COAGENTOPS-HEARTBEAT-P0-MWORKS-MAIN-WINDOW-MISSING-20260608-0756.json`.
  No MWORKS/ROS2/UE live runtime, Codex++ restart, WeChat notification,
  `check_model`, simulation, graphical acceptance, controller performance,
  planner_ready, mission success, or closed_loop claim was made.
- 2026-06-08 CST: CoAgentOps 16:08 patrol integrated the completed UE 029
  source-static capture-bundle validator return and refreshed MWORKS window
  evidence. PMO and CoAgentOps execution surfaces remain usable, UE 029 is
  completed as source-static only, and no new Codex++ restart is justified.
  Read-only MWORKS evidence still shows no true MWORKS/Sysplorer/Syslab main
  window (`target_window_count=0`, `window_count=0`), so MWORKS R1/R2 live
  work and graphical review remain `idle_blocked_by_open_dependency`. No
  duplicate email was sent because the earlier sparse email already covers the
  unchanged missing-window condition. Blocker:
  `Results/agent_packets/blockers/COAGENTOPS-HEARTBEAT-P0-MWORKS-MAIN-WINDOW-MISSING-20260608-0808.json`.
  No MWORKS/ROS2/UE live runtime, Codex++ restart, WeChat notification,
  `check_model`, simulation, graphical acceptance, UE runtime ack, controller
  performance, planner_ready, mission success, or closed_loop claim was made.
- 2026-06-08 CST: CoAgentOps 16:18 patrol refreshed the same P0 control-plane
  and MWORKS window dependency after MWORKS R2 started 023. PMO and CoAgentOps
  execution surfaces remain usable, UE 029 remains source-static-only
  completed evidence, and MWORKS R2 023 is now `busy_in_progress` rather than
  idle. Read-only MWORKS evidence still shows no true MWORKS/Sysplorer/Syslab
  main window (`target_window_count=0`, `window_count=0`; process inventory
  only shows wrapper/no-desktop server processes and self-matching inventory
  commands), so MWORKS R1 live work and R2 graphical review remain blocked by
  the open main-window/no-start-attach dependency. No duplicate email was sent
  because the earlier sparse email already covers the unchanged
  missing-window condition. Blocker:
  `Results/agent_packets/blockers/COAGENTOPS-HEARTBEAT-P0-MWORKS-MAIN-WINDOW-MISSING-20260608-0818.json`.
  No MWORKS/ROS2/UE live runtime, Codex++ restart, WeChat notification,
  `check_model`, simulation, graphical acceptance, UE runtime ack, controller
  performance, planner_ready, mission success, or closed_loop claim was made.
- 2026-06-08 CST: CoAgentOps classified MWORKS R1 task 024 as a confirmed
  visible-thread dispatch-surface failure, not a MWORKS business failure. PMO's
  initial 024 dispatch failed with `failed to start turn: internal error; agent
  loop died unexpectedly`; CoAgentOps read the same R1 thread, observed latest
  completed business turn 023 and no 024 return/blocker, then ran one minimal
  no-op validation against R1. The no-op failed with the same start-turn error.
  CoAgentOps wrote
  `Results/agent_packets/blockers/COAGENTOPS-MWORKS-R1-024-DISPATCH-SURFACE-RECOVERY-20260608-001.json`
  before restart action. `thread_execution_surface_restored=false` and
  `business_task_or_patrol_completed=false`; task 024 remains unstarted until
  Codex++ restart evidence and same-thread post-restart validation exist. This
  turn also recorded the workflow correction that open-source probe/learning is
  a source-first support lane only; it cannot substitute for MWORKS/ROS2/UE P0
  mainline dispatch or hide routable idle engineering threads.
- 2026-06-08 CST: CoAgentOps completed the MWORKS R1 024 dispatch-surface
  recovery loop. Sparse email audit
  `Results/coagent_gateway/email/email_alert_20260608_165533.json` succeeded,
  Codex++ watchdog evidence
  `Results/codex_watchdog/codex_outer_watchdog_check_20260608_165558.json`
  reports `restart_requested=true` and `restart_result.ok=true`, and same
  visible R1 thread validation turn `019ea676-db46-7d53-81e6-a3b98850f606`
  completed with exact ACK
  `mworks_r1_024_post_restart_validation_ack_20260608_1656`. Supersede return:
  `Results/agent_packets/returns/COAGENTOPS-MWORKS-R1-024-DISPATCH-SURFACE-RECOVERY-SUPERSEDE-20260608-001.json`.
  This restores `thread_execution_surface_restored=true` for bounded R1
  control-plane routing only. `business_task_or_patrol_completed=false`: task
  024 was not re-dispatched and still has no expected return/blocker packet.
  Live MWORKS work remains gated by the separate true main-window/no-start
  attach dependency; no MWORKS GUI/MCP/check_model/SimulateModel/layout/result
  viewer, ROS2, UE runtime, planner_ready, controller performance, runtime ack,
  mission success, or closed_loop claim was made.
- 2026-06-08 CST: User clarified CoAgentOps patrol scheduling priority for
  review work: abnormal/recovery-pending visible threads and routable idle P0
  engineering threads must be surfaced before review/audit queues. Updated
  `AGENTS.md` and `Docs/Workflows/coagent_meta_maintenance.md` so future patrol
  triage order is: abnormal/recovery pending, idle P0 dispatch, idle
  open-dependency blockers, review/audit tasks, then support-lane
  probe/learning/meta checks. This is a control-plane scheduling correction
  only and does not claim any MWORKS/ROS2/UE runtime result.
- 2026-06-08 CST: User confirmed deletion of the historical WeChat-side message
  path `019e8358-86b4-7070-8fd6-a2b4f4d2af97` and historical WeChat Gateway Ops
  thread `019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c`. PMO updated current route
  registry and canonical docs to mark both as `deleted_by_user_not_visible`.
  CoAgentOps/PMO must not scan, no-op, dispatch, recover, or treat absence of
  either deleted thread as an outage. The active CoAgentOps patrol automation
  was also updated without changing its 10-minute cadence or target thread so
  archived/deleted WeChat routes are explicitly skipped and absence is not a
  fault. Return packet:
  `Results/agent_packets/returns/PMO-WECHAT-DELETED-THREAD-ROUTE-SYNC-20260608-001.json`.
- 2026-06-08 CST: PMO resumed mainline dispatch after the user restarted
  Codex and confirmed child threads are healthy. PMO created four
  contract-valid P0 task packets and successfully dispatched them with
  `gpt-5.5`/`xhigh`: UE 032 source-static runtime echo receiver capture-bundle
  wiring to `019e9b24-50aa-7cd3-9e7c-4c43b224d993`; ROS2 074 one bounded
  headless no-goal FAST-LIO output evidence bundle to
  `019e9c72-ee74-79d1-b9fe-621d3c6fc99e`; MWORKS R1 025 narrow static
  MoSimQuadrotorModel Dynamics Batch A source migration to
  `019e9be5-334b-76b1-93f9-8b02caebf376`; and MWORKS R2 025 static review of
  R1 Batch A to `019e9999-b0d3-7682-bccd-faef08fcf1df`. These are dispatched
  tasks, not completed results. MWORKS live GUI/check_model/SimulateModel and
  graphical/package-browser acceptance remain blocked by the separate true
  main-window/no-start attach dependency; UE runtime ack, ROS2 planner_ready,
  controller performance, mission success, and closed_loop are not claimed.
- 2026-06-08 CST: CoAgentOps closed the MWORKS R2 025 control-plane recovery
  loop but did not complete the business review. The pre-restart sparse email
  audit `Results/coagent_gateway/email/email_alert_20260608_204744.json`
  succeeded, Codex++ watchdog evidence
  `Results/codex_watchdog/codex_outer_watchdog_check_20260608_204758.json`
  reports `restart_requested=true` and `restart_result.ok=true`, and the same
  visible R2 thread completed validation turn `019ea74f-68bc-70a2-a089-906f069a6bfc`
  with exact ACK `mworks_r2_025_post_restart_validation_ack_20260608_2050`.
  Supersede return:
  `Results/agent_packets/returns/COAGENTOPS-MWORKS-R2-025-DISPATCH-SURFACE-RECOVERY-SUPERSEDE-20260608-001.json`.
  This restores `thread_execution_surface_restored=true` for bounded R2
  control-plane routing only. `business_task_or_patrol_completed=false`: R2
  025 was not re-dispatched and still has no expected return/blocker packet.
  No MWORKS GUI/MCP/check_model/SimulateModel/layout/result viewer, UE/ROS2
  runtime, planner_ready, controller performance, mission success, or
  closed_loop claim was made.
- 2026-06-08 CST: CoAgentOps superseded the stale MWORKS R1 027 dispatch
  blocker and used the bounded dispatch authority to keep the idle P0
  engineering thread moving. The old blocker
  `Results/agent_packets/blockers/PMO-MWORKS-R1-027-DISPATCH-SURFACE-FAILURE-20260608-001.json`
  is superseded by
  `Results/agent_packets/returns/COAGENTOPS-MWORKS-R1-027-DISPATCH-SURFACE-RECOVERY-SUPERSEDE-20260608-001.json`
  because the same R1 visible thread later completed task 025 with expected
  return `Results/agent_packets/returns/PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-BATCH-A-SOURCE-MIGRATION-20260608-025.json`.
  CoAgentOps validated the existing static-only 027 task packet with
  `check_department_packet_contract.py`, dispatched exactly one task to R1
  thread `019e9be5-334b-76b1-93f9-8b02caebf376`, and notified MainPMO in the
  same run. R1 readback shows turn `019ea75a-abc0-7ee2-87ff-79da13ed5c94`
  is `inProgress` with agent commentary. Expected 027 return/blocker:
  `Results/agent_packets/returns/PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-COMMAND-MAPPER-FORMAL-SOURCE-SURFACE-20260608-027.json`
  or
  `Results/agent_packets/blockers/PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-COMMAND-MAPPER-FORMAL-SOURCE-SURFACE-20260608-027.json`.
  This is static Modelica source-surface work only; no live MWORKS, GUI/MCP,
  `check_model`, simulation, graphical acceptance, UE/ROS2 runtime,
  controller performance, planner_ready, mission success, or closed_loop claim
  was made.
- 2026-06-08 CST: User explicitly allowed CoAgentOps to dispatch MWORKS GUI/MCP/live
  simulation tasks when the task packet and safety gates permit it. CoAgentOps
  validated R1 028 live-gate and R2 025 static-review task packets, but the
  native visible-thread dispatch surface failed before either business turn
  started: settings-update dispatch returned `agent loop died unexpectedly`,
  and the bounded no-settings retry returned `no active turn to steer` for both
  R1 and R2. CoAgentOps wrote recovery blockers
  `Results/agent_packets/blockers/COAGENTOPS-MWORKS-R1-028-DISPATCH-SURFACE-RECOVERY-20260608-001.json`
  and
  `Results/agent_packets/blockers/COAGENTOPS-MWORKS-R2-025-DISPATCH-SURFACE-RECOVERY-REOPEN-20260608-002.json`.
  `thread_execution_surface_restored=false` and
  `business_task_or_patrol_completed=false` for both incidents. Next step is
  sparse Chinese email audit, authorized Codex++ restart, then same-thread
  post-restart validation before any PMO redispatch. No MWORKS GUI/MCP,
  `check_model`, simulation, package browser, Smart Layout, result viewer,
  UE/ROS2 runtime, controller performance, planner_ready, mission success, or
  closed_loop claim was made.
- 2026-06-09 CST: PMO corrected the stale CoAgentOps 00:59 patrol state for
  ROS2 074 by validating the actual 074 return packet and current ROS2 thread
  closeout. ROS2 074 is accepted only as one bounded headless no-goal
  FAST-LIO output evidence bundle; it does not prove map/world grounding,
  planner handoff, controller performance, mission success, or closed loop.
  PMO then created strict-gate task packet
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-GROUNDING-STATIC-GATE-20260609-075.json`
  and dispatched it to ROS2 R1 with `gpt-5.5`/`xhigh` for source/static
  grounding-contract work only.
- 2026-06-09 CST: PMO accepted UE 032 only as source-static runtime echo
  receiver/capture-bundle wiring evidence and did not claim live UE runtime
  ack. PMO created strict-gate task packet
  `Results/agent_packets/tasks/ue/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SINGLE-BOUNDED-PROBE-PLAN-20260609-033.json`
  and dispatched it to the UE department with `gpt-5.5`/`xhigh` for a
  source/static single-bounded-probe plan/readiness contract. No Unreal
  Editor/PIE/runtime/build, MWORKS/ROS2 live producer, planner/controller, or
  closed-loop claim was made.
- 2026-06-09 CST: PMO integrated CoAgentOps bounded-dispatch automation
  semantics repair return
  `Results/agent_packets/returns/COAGENTOPS-BOUNDED-DISPATCH-AUTOMATION-SEMANTICS-REPAIR-20260609-001.json`.
  The packet passed JSON parsing and `check_department_packet_contract.py
  --allow-control-plane-only`, and board wording now says CoAgentOps must
  directly dispatch only when every bounded-dispatch precondition is satisfied;
  otherwise it reports the missing gate to PMO. This is a control-plane repair
  only: it does not complete ROS2 075, UE 033, MWORKS R1 028, or MWORKS R2
  025, and it makes no MWORKS/ROS2/UE runtime, planner, controller, or
  closed-loop claim.
- 2026-06-09 CST: PMO validated ROS2 075 return
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-GROUNDING-STATIC-GATE-20260609-075.json`.
  JSON parsing, department packet contract, and
  `Scripts/tests/test_ros2_camera_init_map_world_grounding_static_gate.py`
  passed. The accepted engineering output is a source/static `camera_init` to
  map/world grounding contract, matrix, same-run checklist, and fake-transform
  rejection rules. This does not prove live ROS2/RViz/FAST-LIO success,
  planner/controller handoff, runtime ack, controller performance, mission
  success, or closed loop; a future authorized same-run bundle is still needed
  before controller handoff.
- 2026-06-09 CST: PMO validated UE 033 return
  `Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SINGLE-BOUNDED-PROBE-PLAN-20260609-033.json`.
  JSON parsing, department packet contract, and
  `Scripts/tests/test_ue_runtime_echo_receiver_single_bounded_probe_plan.py`
  passed. The accepted output is a source/static plan/readiness contract for
  exactly one future bounded UE runtime command-echo probe, including capture
  bundle preconditions, timeout/cleanup, false-ack negative checks, and
  no-pose-overwrite checks. This does not prove live UE runtime ack, MWORKS
  downlink, ROS2 runtime echo, final UI acceptance, planner_ready, controller
  performance, mission success, or closed loop.
- 2026-06-09 CST: PMO validated ROS2 077 return after CoAgentOps bounded
  closeout recovered the missing expected packet:
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-GROUNDING-SOURCE-ROUTE-DESIGN-20260609-077.json`.
  JSON parsing, department packet contract, and
  `Scripts/tests/test_ros2_camera_init_map_world_grounding_source_route_design.py`
  passed. PMO integration packet:
  `Results/agent_packets/returns/PMO-ROS2-077-SOURCE-ROUTE-DESIGN-INTEGRATION-20260609-001.json`.
  Accepted scope is source/static route design only: route counts are
  adopt=1, adapt=2, reference_only=2, reject=2, with future same-run TF chain
  first in the recommended route order. 076 camera_init-to-map/world grounding
  remains `blocked_absent`; controller handoff and any new live probe remain
  blocked until a separate PMO task materializes real evidence gates.
- 2026-06-09 CST: PMO validated UE 034 blocker
  `Results/agent_packets/blockers/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SINGLE-BOUNDED-LIVE-PROBE-20260609-034.json`.
  JSON parsing, department packet contract, and preflight JSON parsing passed.
  PMO integration packet:
  `Results/agent_packets/returns/PMO-UE-034-LIVE-PROBE-BLOCKER-INTEGRATION-20260609-001.json`.
  The single live UE probe attempt was not consumed: preflight found missing
  authoritative live producer identity, pending request capture route,
  authoritative echo capture route, seven-artifact generation route, and
  timeout cleanup route. This is an engineering dependency blocker, not UE
  runtime ack or final UI acceptance; the UE thread surface also read
  `systemError` after producing the expected blocker and needs later
  patrol/recovery validation before more UE business dispatch.
- 2026-06-09 CST: PMO created, validated, and dispatched ROS2 078 to ROS2 R1
  with `gpt-5.5`/`xhigh`:
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-SAME-RUN-TF-CHAIN-CAPTURE-CONTRACT-20260609-078.json`.
  The packet passed JSON parsing,
  `Scripts/quality/check_agent_task_native_surface_gate.py --strict`, and
  `Scripts/quality/check_department_packet_contract.py --allow-control-plane-only`.
  Native readback shows turn `019ea9f3-430d-7821-bf91-96e4abf88042` is
  `inProgress`; PMO dispatch packet:
  `Results/agent_packets/returns/PMO-ROS2-078-SAME-RUN-TF-CHAIN-CAPTURE-CONTRACT-DISPATCH-20260609-001.json`.
  This is route-specific source/static capture-contract work for the 077
  first-priority same-run TF-chain route. It does not run ROS2/RViz/FAST-LIO,
  consume a live probe, authorize controller handoff, or claim planner_ready,
  controller performance, runtime success, mission success, or closed loop.
- 2026-06-09 CST: PMO created, validated, and dispatched UE 035 to the UE
  department with `gpt-5.5`/`xhigh`:
  `Results/agent_packets/tasks/ue/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-CAPTURE-CLEANUP-ROUTE-CONTRACT-20260609-035.json`.
  The packet passed JSON parsing,
  `Scripts/quality/check_agent_task_native_surface_gate.py --strict`, and
  `Scripts/quality/check_department_packet_contract.py --allow-control-plane-only`.
  Native readback shows turn `019ea9fd-4210-7630-8770-62c3af724beb` is
  `inProgress`; PMO dispatch packet:
  `Results/agent_packets/returns/PMO-UE-035-PRODUCER-CAPTURE-CLEANUP-ROUTE-CONTRACT-DISPATCH-20260609-001.json`.
  This is source/static producer/capture/cleanup route-contract work after the
  UE 034 blocker. It does not open UE runtime/editor, run UE build, consume a
  live probe, or claim live UE runtime ack, MWORKS downlink, ROS2 runtime echo,
  final UI acceptance, planner_ready, controller performance, mission success,
  or closed loop.
- 2026-06-09 CST: PMO validated and integrated ROS2 078 return
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-SAME-RUN-TF-CHAIN-CAPTURE-CONTRACT-20260609-078.json`.
  JSON parsing, department packet contract,
  `Scripts/tests/test_ros2_camera_init_map_world_same_run_tf_chain_capture_contract.py`,
  and scoped `git diff --check` passed. PMO integration packet:
  `Results/agent_packets/returns/PMO-ROS2-078-SAME-RUN-TF-CHAIN-CAPTURE-CONTRACT-INTEGRATION-20260609-001.json`.
  Accepted scope is source/static capture-contract evidence for the 077
  first-priority future same-run TF-chain route. It requires future raw `/tf`
  and `/tf_static` event paths, dynamic/static edge lists, same-run scope,
  non-fake grounding basis, and base plus route-specific validators. It does
  not prove current `camera_init` to `map/world` grounding; 076 remains
  `blocked_absent`. It does not authorize or consume a live ROS2/RViz/FAST-LIO
  probe, controller handoff, planner_ready, controller performance, runtime
  success, mission success, or closed loop.
- 2026-06-09 CST: PMO validated and integrated UE 035 return
  `Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-CAPTURE-CLEANUP-ROUTE-CONTRACT-20260609-035.json`.
  JSON parsing, department packet contract,
  `Scripts/tests/test_ue_runtime_echo_producer_capture_cleanup_route_contract.py`,
  and PMO checker re-run passed. PMO integration packet:
  `Results/agent_packets/returns/PMO-UE-035-PRODUCER-CAPTURE-CLEANUP-ROUTE-CONTRACT-INTEGRATION-20260609-001.json`.
  Accepted scope is source/static producer/capture/cleanup route-contract
  evidence only. It defines the future seven-artifact contract for runtime
  probe manifest, pending request capture, authoritative echo capture,
  request/echo match, no-pose proof, false-ack negative report, and timeout
  cleanup manifest. It explicitly reports `runtime_route_ready_now=false`,
  `live_attempt_consumed=false`, `runtime_probe_executed=false`, and
  `runtime_ack_leaks_now=0`. It does not prove live UE runtime ack, MWORKS
  downlink, ROS2 runtime echo, final UI acceptance, planner_ready, controller
  performance, mission success, or closed loop.
- 2026-06-09 CST: PMO prepared and locally validated ROS2 079 live evidence
  probe task packet
  `Results/agent_packets/tasks/ros2/RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-SAME-RUN-TF-CHAIN-EVIDENCE-PROBE-20260609-079.json`,
  then attempted dispatch to ROS2 R1 with `gpt-5.5`/`high`. Native send
  returned the target thread id, but bounded readback did not show a 079 turn,
  the visible thread status was `notLoaded`, and the expected 079 return or
  blocker packet was absent. PMO wrote and validated dispatch-surface blocker
  `Results/agent_packets/blockers/PMO-ROS2-079-DISPATCH-SURFACE-NOTLOADED-20260609-001.json`,
  changed the ROS2 board state to `recovery_pending`, and stopped before any
  duplicate 079 dispatch. This is control-plane recovery evidence only; it
  does not prove 079 started, ran, or produced ROS2/RViz/FAST-LIO runtime
  evidence, and it does not claim planner_ready, controller handoff,
  controller performance, mission success, runtime success, or closed loop.
- 2026-06-09 CST: PMO created and validated UE 036 source/static
  implementation-surface task packet
  `Results/agent_packets/tasks/ue/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-CAPTURE-CLEANUP-IMPLEMENTATION-SURFACE-20260609-036.json`.
  The packet passed JSON parsing,
  `Scripts/quality/check_agent_task_native_surface_gate.py --strict`,
  `Scripts/quality/check_department_packet_contract.py --allow-control-plane-only`,
  and scoped diff checks. PMO attempted dispatch to the UE department with
  `gpt-5.5`/`high`; native send returned the target thread id, but bounded
  readback did not show a 036 turn, the visible thread status was `notLoaded`,
  and the expected 036 return or blocker packet was absent. PMO wrote and
  validated dispatch-surface blocker
  `Results/agent_packets/blockers/PMO-UE-036-DISPATCH-SURFACE-NOTLOADED-20260609-001.json`,
  changed the UE board state to `recovery_pending`, and stopped before any
  duplicate 036 dispatch. This is control-plane recovery evidence only; it
  does not prove 036 started, ran, changed UE source, or produced UE runtime,
  build, live probe, runtime ack, MWORKS downlink, ROS2 runtime echo,
  planner_ready, controller performance, mission success, or closed loop.
- 2026-06-09 CST: PMO attempted to sync UE 036 dispatch-surface recovery to
  CoAgentOps after earlier syncing ROS2 079. The UE 036 sync failed with
  `failed to update thread settings: internal error; agent loop died unexpectedly`.
  PMO sent a sparse Chinese email alert with audit
  `Results/coagent_gateway/email/email_alert_20260609_095937.json`, wrote and
  validated blocker
  `Results/agent_packets/blockers/PMO-COAGENTOPS-AGENT-LOOP-DIED-DURING-DISPATCH-SURFACE-SYNC-20260609-001.json`,
  and changed Ops board state to `recovery_pending`. Email is not a recovery
  endpoint. Codex++ restart is intentionally deferred in this turn because the
  current user instruction in this incident sequence was to dispatch other
  tasks first and not restart yet. This control-plane blocker does not prove
  CoAgentOps is permanently dead or restored, and it does not prove ROS2 079,
  UE 036, MWORKS/ROS2/UE runtime, planner_ready, controller performance,
  mission success, or closed loop.
- 2026-06-09 CST: PMO prepared and locally validated MWORKS R1 static task 029
  `Results/agent_packets/tasks/mworks/PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-MAPPED-WRAPPER-FORMAL-SOURCE-SURFACE-20260609-029.json`
  for `MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface` source-surface
  materialization. The task packet passed JSON parsing,
  `Scripts/quality/check_agent_task_native_surface_gate.py --strict`,
  `Scripts/quality/check_department_packet_contract.py --allow-control-plane-only`,
  `Scripts/quality/check_mworks_live_gate.py --kind task --expect department`,
  and scoped diff checks. PMO attempted dispatch to MWORKS R1 with
  `gpt-5.5`/`high`; native send returned the target thread id, but bounded
  readback did not show a 029 turn, the visible thread status was `notLoaded`,
  and the expected 029 return or blocker packet was absent. PMO wrote and
  validated dispatch-surface blocker
  `Results/agent_packets/blockers/PMO-MWORKS-R1-029-DISPATCH-SURFACE-NOTLOADED-20260609-001.json`,
  changed the MWORKS board state to `recovery_pending`, and stopped before any
  duplicate 029 dispatch. This is control-plane recovery evidence only; it does
  not prove 029 started, changed `.mo` files, produced checker/test evidence,
  or completed, and it does not claim live MWORKS, `check_model`,
  `SimulateModel`, GUI acceptance, controller performance, planner_ready,
  runtime ack, mission success, or closed loop.
- 2026-06-09 CST: PMO selected a non-overlapping MWORKS R2 static task while
  R1 029, ROS2 079, and UE 036 remain dispatch-surface ambiguous. PMO created
  and validated task packet
  `Results/agent_packets/tasks/mworks/PMO-MWORKS-R2-MOSIMQUAD-OPTIONAL-DAMPING-GYRO-FORMAL-SOURCE-SURFACE-20260609-026.json`
  for `MoSimQuadrotorModel.Dynamics.OptionalDampingGyroLayer` formal
  source-surface materialization. The packet passed JSON parsing,
  `Scripts/quality/check_agent_task_native_surface_gate.py --strict`,
  `Scripts/quality/check_department_packet_contract.py --allow-control-plane-only`,
  `Scripts/quality/check_mworks_live_gate.py --kind task --expect department`,
  and scoped diff checks. PMO dispatched it to MWORKS R2 with
  `gpt-5.5`/`high`; native readback shows turn
  `019eaa31-b81e-7bd3-8406-697176e854fe` is `inProgress`. PMO dispatch packet:
  `Results/agent_packets/returns/PMO-MWORKS-R2-026-OPTIONAL-DAMPING-GYRO-DISPATCH-20260609-001.json`.
  This is a static Modelica source/package task only. It does not supersede
  R1 029, does not touch live MWORKS/Sysplorer/Syslab, and does not claim
  `check_model`, `SimulateModel`, graphical/layout acceptance, controller
  performance, planner_ready, runtime success, mission success, or closed loop.
- 2026-06-09 CST: After the user's full PC restart, PMO ran a fresh
  post-PC-restart dispatch-surface sweep. CoAgentOps and MWORKS R2 completed
  exact no-op ACK probes, but MWORKS R1, ROS2 R1, and UE all failed current
  sends with `no active turn to steer`. PMO wrote blocker
  `Results/agent_packets/blockers/PMO-POST-PC-RESTART-P0-DISPATCH-SURFACE-SWEEP-20260609-001.json`,
  sent a sparse Chinese email alert, and did not restart Codex. MWORKS R2 was
  therefore used as the only bounded backup lane for a strict static MWORKS
  task; no live MWORKS/ROS2/UE runtime was touched.
- 2026-06-09 CST: MWORKS R2 completed backup static task 030 for
  `MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface`. PMO verified the
  return packet
  `Results/agent_packets/returns/PMO-MWORKS-R2-MOSIMQUAD-ACTUATOR-MAPPED-WRAPPER-FORMAL-SOURCE-SURFACE-BACKUP-20260609-030.json`
  with `check_department_packet_contract.py` and
  `check_mworks_live_gate.py --kind return --expect department`, closed dispatch
  ticket
  `Results/agent_packets/dispatch_tickets/PMO-MWORKS-R2-MOSIMQUAD-ACTUATOR-MAPPED-WRAPPER-FORMAL-SOURCE-SURFACE-BACKUP-20260609-030.json`
  with `check_dispatch_ticket_slo.py`, updated the PMO board, and wrote PMO
  integration packet
  `Results/agent_packets/returns/PMO-MWORKS-R2-030-ACTUATOR-MAPPED-WRAPPER-SOURCE-SURFACE-INTEGRATION-20260609-001.json`.
  Accepted scope is static-only `.mo` source-surface and checker/evidence. It
  does not prove live MWORKS load, `check_model`, `SimulateModel`, graphical
  layout, controller performance, planner_ready, runtime success, mission
  success, or closed loop.
- 2026-06-09 CST: PMO re-probed MWORKS R1, ROS2 R1, and UE after R2 030
  completed. All three still failed before visible turn creation with
  `no active turn to steer`. PMO wrote blocker
  `Results/agent_packets/blockers/PMO-POST-PC-RESTART-P0-DISPATCH-SURFACE-REPROBE-20260609-002.json`.
  MWORKS R1/ROS2 R1/UE remain `recovery_pending`; do not redispatch 029, 079,
  or 036 there until a later same-thread validation or approved recovery
  supersedes the blocker. This re-probe did not send another user notification
  and did not restart Codex.
- 2026-06-09 CST: After the later user PC/app restart, PMO redispatched UE 036
  with dispatch ticket
  `Results/agent_packets/dispatch_tickets/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-CAPTURE-CLEANUP-IMPLEMENTATION-SURFACE-20260609-036-REDISPATCH-AFTER-REBOOT-20260609-001.json`.
  The target UE thread completed turn `019eab85-f191-7d00-92f6-d0f23e8b6fbc`
  and wrote expected return
  `Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-CAPTURE-CLEANUP-IMPLEMENTATION-SURFACE-20260609-036.json`.
  PMO verified the return with `check_department_packet_contract.py`, closed
  the dispatch ticket with `check_dispatch_ticket_slo.py`, updated
  `Docs/Workflows/mainline_operations_board.md`, and wrote integration packet
  `Results/agent_packets/returns/PMO-UE-036-PRODUCER-CAPTURE-CLEANUP-IMPLEMENTATION-SURFACE-INTEGRATION-20260609-001.json`.
  Accepted scope is UE source/static producer/capture/cleanup implementation
  surface only. It does not prove UE runtime ack, live MWORKS downlink, ROS2
  runtime echo, final UI acceptance, planner_ready, controller performance,
  runtime success, mission success, or closed loop.
- 2026-06-09 CST: PMO closed ROS2 079 post-reboot redispatch. ROS2 R1 turn
  `019eab8b-6010-75e2-9de7-5bb2944ce4d2` completed and wrote expected return
  `Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-SAME-RUN-TF-CHAIN-EVIDENCE-PROBE-20260609-079.json`.
  PMO verified the return with `check_department_packet_contract.py`, closed
  dispatch ticket
  `Results/agent_packets/dispatch_tickets/RFLY-MOSIM-ROS2-RUNTIME-B1-CAMERA-INIT-MAP-WORLD-SAME-RUN-TF-CHAIN-EVIDENCE-PROBE-20260609-079-POST-REBOOT-REDISPATCH-20260609-001.json`
  with `check_dispatch_ticket_slo.py`, updated
  `Docs/Workflows/mainline_operations_board.md`, and wrote integration packet
  `Results/agent_packets/returns/PMO-ROS2-079-SAME-RUN-TF-CHAIN-EVIDENCE-PROBE-INTEGRATION-20260609-001.json`.
  Accepted scope is one bounded headless no-goal same-run ROS2/FAST-LIO raw
  TF/static TF-chain probe. The outcome remains `blocked_absent`: dynamic TF
  shows `camera_init->body`, static edges are absent, and no non-fake
  `camera_init` to `map/world/ue_world` chain was found. 079 consumed its
  single live attempt; no second probe, foreground RViz/manual review,
  planner/controller handoff, UE/MWORKS integration, planner_ready, controller
  performance, runtime success, mission success, or closed loop is claimed.
- 2026-06-09 CST: MWORKS R2 completed static task 031 for
  `MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter`. PMO verified the return
  packet
  `Results/agent_packets/returns/PMO-MWORKS-R2-MOSIMQUAD-PHYSICAL-WRENCH-ADAPTER-FORMAL-SOURCE-SURFACE-20260609-031.json`
  with `check_department_packet_contract.py` and
  `check_mworks_live_gate.py --kind return --expect department`, closed
  dispatch ticket
  `Results/agent_packets/dispatch_tickets/PMO-MWORKS-R2-MOSIMQUAD-PHYSICAL-WRENCH-ADAPTER-FORMAL-SOURCE-SURFACE-20260609-031.json`
  with `check_dispatch_ticket_slo.py`, updated
  `Docs/Workflows/mainline_operations_board.md`, and wrote PMO integration
  packet
  `Results/agent_packets/returns/PMO-MWORKS-R2-031-PHYSICAL-WRENCH-ADAPTER-SOURCE-SURFACE-INTEGRATION-20260609-001.json`.
  Accepted scope is static-only `.mo` source-surface and checker/evidence:
  `PhysicalWrenchAdapter.mo` now exists as an extends-only formal source
  surface and the duplicate inline `Dynamics/package.mo` alias was removed.
  This does not prove live MWORKS load, `check_model`, `SimulateModel`,
  graphical layout, package-browser acceptance, controller performance,
  planner_ready, runtime success, mission success, or closed loop; MWORKS R1
  remains blocked until same-thread validation supersedes the post-restart
  dispatch-surface blocker.
- 2026-06-09 17:20 CST: User challenged PMO because MWORKS had not been opened
  all day. PMO stopped further static dispatch, inspected current desktop and
  process state, confirmed no reusable MWORKS/Sysplorer main window was open,
  then launched MWORKS and maximized the main `Sysplorer [教育版]` window.
  `check_mworks_gui_sentinel.py` reported `status=clean`, and
  `manage_mworks_windows.ps1` recorded one visible main window with hidden
  helper windows only. A DPI-aware background capture was also saved under
  `Results/mworks_background_capture/pmo_mworks_open_recovery_20260609_1720/`.
  This restores the live GUI precondition for future MWORKS work, but it does
  not prove activation, `check_model`, `SimulateModel`, package-browser
  acceptance, graphical layout, controller performance, runtime success, or
  closed loop.
