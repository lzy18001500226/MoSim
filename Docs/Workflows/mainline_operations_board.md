# Mainline Operations Board

> PMO-facing short board for current MoSim operations. Keep this file concise:
> it is not a history ledger, not a packet archive, and not a replacement for
> `Docs/Workflows/coagent_ops_patrol_workflow.md`.

Status: current PMO snapshot, 2026-06-09 01:10 CST.

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

## 4. P0 Partition Board

| Partition | Current State | Waiting Returns | Blockers | Human Decisions | Integrable Results | Next PMO Action | Forbidden Actions |
|---|---|---|---|---|---|---|---|
| MWORKS | recovery_pending | None ready for live redispatch; `PMO-MWORKS-R1-MOSIMQUAD-ACTUATOR-COMMAND-MAPPER-FORMAL-SOURCE-SURFACE-20260608-027` return is available for static-only integration | `COAGENTOPS-MWORKS-R1-028-DISPATCH-SURFACE-RECOVERY-20260608-001`; `COAGENTOPS-MWORKS-R2-025-DISPATCH-SURFACE-RECOVERY-REOPEN-20260608-002`; the earlier R2 025 supersede is stale for the reopened incident; live work also waits for true reusable MWORKS/Sysplorer main-window and no-start attach evidence | PMO/user decides whether to authorize or wait for MWORKS main-window recovery before live checks | R1 static Batch A and R1 027 actuator mapper returns can be integrated as static-only source evidence | Integrate R1 027 static return; do not re-dispatch R1 028 or R2 025 until current supersede packets prove same-thread execution restored after the latest blockers | No live `check_model`, `SimulateModel`, package-browser, Smart Layout, graphical/layout review, new MWORKS window, login click, or retry loop without current patrol/recovery evidence |
| ROS2 | ready_to_integrate | None for 074 if return packet is accepted | 074 proves only bounded headless no-goal FAST-LIO output evidence; controller handoff remains blocked by absent same-run `camera_init` to map/world grounding; foreground RViz/review surfaces remain separate | PMO decides whether next ROS2 step is map/world grounding, foreground RViz review, or another bounded headless evidence gate | `RFLY-MOSIM-ROS2-RUNTIME-B1-HEADLESS-LIVE-EVIDENCE-BUNDLE-20260608-074` passed JSON and department packet checks as output evidence only | Integrate 074 as bounded headless FAST-LIO output evidence, then write the next bounded task only after choosing the missing grounding/review gate | No fake pointcloud/map, no keyboard pose, no UE truth shortcut, no planner_ready/closed_loop/runtime success/controller-performance claim from 074 |
| UE | ready_to_integrate | None for 032 if return packet is accepted | Live runtime ack still unproven; MWORKS/ROS2 authoritative producer/capture surfaces are not final | PMO decides whether next UE step is build/runtime probe or more source-static hardening | `RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-CAPTURE-BUNDLE-WIRING-20260608-032` is available as source-static wiring evidence | Validate/integrate 032, then choose one bounded next gate | No UE runtime ack, final UI acceptance, MWORKS downlink, ROS2 runtime echo, planner_ready, or closed_loop claim from source-static returns |
| Git | running | DevOps closeout remains active by ledger | Large-tree ignore/drain queue still active; broad Git porcelain can be slow/noisy | PMO decides specific next path-limited batch when Git work becomes priority | Prior pushed slices are historical evidence; current staged runtime outputs are not this board's completion evidence | Keep Git work path-limited and do not let support work mask P0 engineering blockers | No `git add -A`, no force push/reset/clean, no broad cleanup, no hidden `.gitignore` backlog |
| Ops | dispatch_needed | CoAgentOps should send patrol findings into PMO board/queue, not only heartbeat packets | Current open recovery blockers for MWORKS R1 028 and R2 025; old WeChat routes are deleted history | If CoAgentOps itself cannot start turns, PMO sends sparse email and handles restart recovery from the live PMO turn | PMO/CoAgentOps execution-surface supersede packets can restore routing only; they do not complete business tasks | Keep this board updated from CoAgentOps patrol; treat email as audit, not recovery endpoint | No WeChat health checks, no archived gateway no-op, no replacement thread without explicit approval, no quiet closeout when dispatch_needed exists |

## 5. Support Lanes

| Lane | State | Rule |
|---|---|---|
| Sunray/PBR | frozen_by_user | Do not dispatch material/PBR/DAE visual changes unless the user explicitly reopens the lane. |
| Open-source probe/learning | support_only | Use only for a concrete source-first question; it cannot substitute for idle P0 engineering dispatch. |
| 文档秘书部 | support_only | Use for consistency review, context maintenance, and cleanup; it does not define PMO runtime rules. |

## 6. Current Board Maintenance Rules

- PMO updates this board when accepting a return, recording a blocker, changing
  the next dispatch, or after a CoAgentOps patrol changes a P0 state.
- CoAgentOps may directly dispatch routable idle P0 work when the
  bounded-dispatch gate in `coagent_ops_patrol_workflow.md` is satisfied. If a
  gate is missing, it reports `dispatch_needed` with the missing precondition.
  PMO decides acceptance, priority changes, narrowing, supersede, and any
  dispatch that needs product/user judgment.
- Historical detail belongs in `Docs/Workflows/agent_task_ledger.md` and
  `Results/agent_packets/`, not in this board.
- Packet paths remain the durable evidence; this board is the short operating
  index that points to them.
- This board and the return packet
  `Results/agent_packets/returns/PMO-MAINLINE-OPERATIONS-BOARD-ARCHITECTURE-20260608-001.json`
  are the durable evidence for the PMO operating-architecture update.
- Current Git lock or staged `References/` warnings are unrelated Git/reference
  intake blockers. They do not block this control-plane board/packet delivery
  unless the exact board or packet paths are locked, staged-conflicted, or fail
  their targeted checks.
