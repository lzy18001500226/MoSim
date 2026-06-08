# Round 2 ROS2 Runtime Setup Memory Audit

Date: 2026-06-04 CST

Scope: verify long-session memory about WSL2 Ubuntu 22.04 ROS2 Humble,
ROS-MCP/rosbridge, RViz2 review, replay topics, and FAST-LIO claim boundaries
against current project files. This is cache-only. It does not promote current
host, apt, rosbridge, or FAST-LIO state into formal truth.

## Status

```text
round: 2
topic: ROS2 runtime setup and FAST-LIO runtime boundary
status: mixed_round2_verified_and_needs_round3
risk: high
formal_docs_patched_this_round: none
cache_only: true
external_system_checks_run: none
```

No `/etc/apt`, `/opt/ros`, `/home/linux/.ros`, or external MCP wrapper file was
read or modified in this round. Any future host repair still requires a fresh
explicit infrastructure request.

## Sources Re-Read

| Source | Finding |
|---|---|
| `Docs/Workflows/ros2_runtime_setup.md` | Formal workflow says Ubuntu 22.04 uses ROS2 Humble/RViz2, records apt/key resolution as a prior validated host state, sets `ROS_LOG_DIR` to project-local `Results/tmp/ros_logs`, describes ROS-MCP through rosbridge on port `9090`, and records FAST-LIO candidate/runtime boundaries. |
| `Results/unreal_scene_mapping/ROS_MAPPING_RUNTIME_ENV.md` | Older environment preflight: `ready_for_native_mapping_runtime=true`, `ros_generation=ros2`, `ros2_replay_ready=true`, but `fastlio_ros2_runtime_claimable=false`. It is explicitly an environment preflight, not runtime evidence. |
| `Results/unreal_scene_mapping/FASTLIO_FAMILY_COMPATIBILITY.md` | Older source metadata scan: local FAST-LIO-family references were ROS1/Catkin-only and no local ROS2 candidate was claimable at that scan. It did not build, launch, record, or evaluate FAST-LIO. |
| `Results/unreal_scene_mapping/SPARK_FASTLIO_ROS2_CANDIDATE.md` | Snapshot says `spark-fast-lio` candidate was in `building` phase and `runtime_claimable=false` at that time. Later workflow text records a successful build/runtime route, so this is stage-specific history. |
| `Results/unreal_scene_mapping/FASTLIO_RUNTIME_STATUS.md` | Older 2026-06-01 runtime status: `spark-fast-lio` built and produced `/cloud_registered`, `/odometry`, and `/path`; Factory scan099 failed thresholds while Derelict passed with warnings. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE_CURRENT.md` | Latest Factory Gate B file read in this round: `ready_for_manual_rviz_ue_review`, counts `odometry=80`, `path=8`, `registered_cloud=80`, evaluation pass. This opens manual review only. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/runtime_review_bundle.md` | Execution contract for manual UE/RViz review. It says the bundle is not proof that runtime already ran and does not claim final controller/planner integration. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_INPUT_CONTRACT.md` | Dense Mid360 input is `claimable_input_ready`, but `spark-fast-lio` PointCloud2 Livox support is false and CustomMsg route is guarded. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_MID360_RUNTIME_BLOCKER.md` | Older/parallel blocker: dense Factory Mid360 PointCloud2 path produced zero outputs with `Error LiDAR Type`. Useful failure history for that route. |
| `Scripts/UE5/check_fastlio_ros2_topics.sh` | Current default FAST-LIO output topics include `/cloud_registered`, `/odometry`, and `/path`; it can check replay inputs only with `REQUIRE_FASTLIO_OUTPUTS=0`. |
| `Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh` | `START_FASTLIO=1` requires `FASTLIO_ROS2_LAUNCH_CMD`; defaults publish MoSim replay topics and set ROS logs under project-local `Results/tmp/ros_logs`. |
| `Docs/Workflows/debug_mcp.md` | ROS-MCP section records rosbridge route, wrapper auto-start behavior, config snippet, and control-tool approval cautions. |

## Round 2 Findings

### ROS2-MEM-001 - ROS2 Humble Is The Primary Ubuntu 22.04 Route

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  On this WSL2 Ubuntu 22.04 project host, the documented primary robotics
  runtime for UE mapping/review is ROS2 Humble plus RViz2, not direct ROS1
  Noetic installation.
current_evidence:
  - `Docs/Workflows/ros2_runtime_setup.md` makes ROS2 Humble the decision.
  - `ROS_MAPPING_RUNTIME_ENV.md` reports `ros_generation=ros2`,
    `ROS_DISTRO=humble`, `rviz2=/opt/ros/humble/bin/rviz2`, and
    `colcon=/usr/bin/colcon`.
contradictions_or_history:
  ROS1/Catkin FAST-LIO references remain useful as source/reference material
  or an explicitly approved bridge/container route, but they are not the
  primary host route.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/ros2_runtime_setup.md`.
next_round_action:
  Round 3 can mark already formalized unless a new setup doc conflicts.
```

### ROS2-MEM-002 - Apt Key/Source State Is Prior Infrastructure Evidence Only

```text
round: 2
status: round2_verified_for_cache_infrastructure_history
risk: medium
candidate_statement:
  Project docs record a prior successful ROS apt key/source repair using
  `/usr/share/keyrings/ros-archive-keyring.gpg` and the Tsinghua ROS2 jammy
  source, with apt update passing without `NO_PUBKEY` or `EXPKEYSIG`.
current_evidence:
  - `Docs/Workflows/ros2_runtime_setup.md` records the key/source pair and
    says the 2026-06-01 host state was validated.
  - `Docs/Workflows/debug_mcp.md` repeats the same 2026-06-01 diagnosis.
contradictions_or_history:
  This round did not re-run `apt update` or inspect external apt files.
  Therefore it must not be stated as a live current host guarantee.
formal_target_if_promoted:
  Existing ROS2 setup and MCP debug workflows only.
next_round_action:
  Keep as infrastructure memory. Re-run host checks only when the user asks for
  ROS infrastructure repair or current host verification.
```

### ROS2-MEM-003 - ROS-MCP Uses Rosbridge And Wrapper Auto-Start Is Documented

```text
round: 2
status: round2_verified_for_cache_not_live_port_checked
risk: medium
candidate_statement:
  ROS-MCP talks to the active ROS/ROS2 runtime through rosbridge. Project docs
  say the WSL wrapper auto-starts `rosbridge_websocket` on port `9090` when
  absent, then reuses it for MCP calls.
current_evidence:
  - `Docs/Workflows/debug_mcp.md` section 5.3 describes the wrapper behavior,
    expected config, logs under `Results/logs/rosbridge_mcp/`, and read-first
    robot operation policy.
  - `Docs/Workflows/ros2_runtime_setup.md` records the same ROS-MCP note.
contradictions_or_history:
  The long-session launch warnings about rosbridge service timeout/threading
  were warnings, not startup failure proof. This round did not run `ss` or a
  live MCP tool call, so current port state is not verified.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/debug_mcp.md`.
next_round_action:
  Round 3 can mark already formalized; do not add a claim that rosbridge is
  currently listening unless a live check is run in that same round.
```

### ROS2-MEM-004 - Project-Local ROS Log Directory Is Required

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  ROS2 runtime logs should be directed to
  `/mnt/c/Users/HP/Desktop/MoSim/Results/tmp/ros_logs` for project scripts and
  agent-run ROS calls.
current_evidence:
  - `Docs/Workflows/ros2_runtime_setup.md` records the `ROS_LOG_DIR` rule.
  - `Scripts/UE5/check_fastlio_ros2_topics.sh` and
    `Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh` default `ROS_LOG_DIR`
    to `${PROJECT_ROOT}/Results/tmp/ros_logs` and create the directory.
contradictions_or_history:
  External `/home/linux/.ros/log` writes may fail in restricted agent contexts.
formal_target_if_promoted:
  Already represented in ROS2 setup workflow and scripts.
next_round_action:
  Round 3 can mark already formalized.
```

### ROS2-MEM-005 - Replay/RViz2 Readiness Is Not Runtime Localization Evidence

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  ROS2 replay input readiness and RViz2 review readiness are not completed
  FAST-LIO runtime or localization evidence by themselves.
current_evidence:
  - `ROS_MAPPING_RUNTIME_ENV.md` reports `ros2_replay_ready=true` and
    `fastlio_ros2_runtime_claimable=false` in the same preflight.
  - `UE_SCENE_RUNTIME_READINESS.md` says file loop ready but runtime ready
    false at that snapshot.
  - `runtime_review_bundle.md` says the bundle is an execution contract, not
    proof that runtime already ran.
contradictions_or_history:
  Old replay files, RViz launch packages, and topic smoke outputs can look like
  runtime evidence. They remain input/review readiness until real FAST-LIO
  output topics and evaluation are recorded.
formal_target_if_promoted:
  Already broadly represented in ROS2 and UE renderer workflows.
next_round_action:
  Round 3 should keep this as an anti-regression boundary.
```

### ROS2-MEM-006 - HTML Is Not Active Point-Cloud/Map Review

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  Active point-cloud, map, TF, odometry, FAST-LIO, and planner review must use
  RViz2 or equivalent native robotics tooling. Browser HTML is only offline
  preview/report material unless explicitly requested.
current_evidence:
  - `AGENTS.md` Unreal Mapping Window Rule states browser HTML is not accepted
    as active point-cloud/map review.
  - `ROS_MAPPING_RUNTIME_ENV.md`, `UE_SCENE_RUNTIME_READINESS.md`, and
    `runtime_review_bundle.md` all reject HTML as the active point-cloud
    window.
contradictions_or_history:
  Old browser previews and static point clouds were useful for debugging, but
  must not be resumed as product evidence.
formal_target_if_promoted:
  Already represented in `AGENTS.md` and workflows.
next_round_action:
  Round 3 can mark already formalized or include this in a rejected-route map.
```

### ROS2-MEM-007 - `/mosim/replay_odometry` Is Reference Pose Only

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  `/mosim/replay_odometry` is replay/reference pose for RViz2 review. It must
  not be counted as FAST-LIO odometry output.
current_evidence:
  - `Docs/Workflows/ros2_runtime_setup.md` explicitly says
    `/mosim/replay_odometry` is only replay reference pose and not FAST-LIO
    localization output.
  - `Scripts/UE5/check_fastlio_ros2_topics.sh` checks FAST-LIO odometry through
    `FASTLIO_ODOMETRY_TOPIC`, defaulting to `/odometry`, not
    `/mosim/replay_odometry`.
  - Current workflow text notes `spark_fast_lio` uses relative `odometry`,
    appearing as `/odometry`, while older ROS1 examples often use `/Odometry`.
contradictions_or_history:
  Topic spelling varies by candidate (`/odometry` versus `/Odometry`), and a
  reference replay pose can be mistaken for estimator output.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/ros2_runtime_setup.md`.
next_round_action:
  Round 3 should avoid hard-coding one odometry spelling globally; use
  candidate-specific topic checks.
```

### ROS2-MEM-008 - FAST-LIO Status Is Route-Specific And Date-Specific

```text
round: 2
status: round2_verified_for_cache_needs_round3_disambiguation
risk: high
candidate_statement:
  FAST-LIO status is not a single global yes/no answer. Current project files
  contain older source scans and failure histories, older scan099 runtime
  status, and a later Factory `*_CURRENT` Gate B manual-review entry.
current_evidence:
  - `FASTLIO_FAMILY_COMPATIBILITY.md` is a source metadata scan only and says
    local FAST-LIO-family sources were ROS1/Catkin-only at that time.
  - `SPARK_FASTLIO_ROS2_CANDIDATE.md` was a build-phase snapshot with
    `runtime_claimable=false`.
  - `FASTLIO_RUNTIME_STATUS.md` is dated 2026-06-01 and says Factory scan099
    failed thresholds while Derelict passed with warnings.
  - `FASTLIO_MID360_RUNTIME_BLOCKER.md` records a dense Factory Mid360
    spark-fast-lio PointCloud2 blocker with zero output messages.
  - `REALSTACK_MINILOOP_GATE_CURRENT.md` records later Factory Gate B status
    `ready_for_manual_rviz_ue_review`, counts `odometry=80`, `path=8`,
    `registered_cloud=80`, `position_rmse_m=0.39454`,
    `max_position_error_m=0.611542`, and `yaw_rmse_rad=0.017802`.
  - `runtime_review_bundle.md` says Gate B opens manual UE/RViz review only.
contradictions_or_history:
  Old "cannot claim" files and later "ready for manual review" files refer to
  different scans/routes/gates. New sessions must read latest matching
  `*_CURRENT` gates and runtime review bundles first, then use older blocker
  and scan files as failure/compatibility history.
formal_target_if_promoted:
  A narrow source-priority note in `Docs/Workflows/ros2_runtime_setup.md` or
  `Docs/Workflows/unreal_renderer.md`, if round 3 confirms current formal docs
  are still easy to misread.
next_round_action:
  Round 3 must re-read current `*_CURRENT` files before quoting any metric.
```

### ROS2-MEM-009 - Factory Gate B Is Not Final Product Acceptance

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Current Factory Gate B evidence opens manual UE/RViz review. It does not
  close final controller integration, planner performance, autonomous
  navigation, or product acceptance.
current_evidence:
  - `realstack_miniloop_gate_current.json` claim boundary says the gate allows
    opening RViz2/UE for human review only and does not claim final controller
    integration or planner performance.
  - `runtime_review_bundle.md` repeats the same boundary and separates
    MWORKS dynamics/control evidence from UE/RViz visual runtime evidence.
contradictions_or_history:
  Nonzero FAST-LIO counts and pass metrics can be overgeneralized. That is
  explicitly rejected.
formal_target_if_promoted:
  Already represented in result bundle and UE/ROS round-2 cache; possible
  narrow workflow pointer only.
next_round_action:
  Round 3 should map this with UE-ROS-MEM-003/004 instead of duplicating
  wording across many docs.
```

### ROS2-MEM-010 - Some ROS2 Workflow Commands Need Current File Check

```text
round: 2
status: round2_verified_gap
risk: medium
candidate_statement:
  Some workflow/result text still references ROS2 helper scripts that were not
  present in the current `Scripts/` file list during this migration pass.
current_evidence:
  - `Docs/Workflows/ros2_runtime_setup.md`,
    `Results/unreal_scene_mapping/UE_SCENE_RUNTIME_READINESS.md`, and
    `runtime_review_bundle.md` reference `Scripts/UE5/open_mapping_rviz_ros2.sh`
    and `Scripts/UE5/run_fastlio_rviz_replay_ros2.sh`.
  - `rg --files Scripts | rg 'open_mapping_rviz_ros2|run_fastlio_rviz_replay_ros2'`
    found no matching files in this round.
  - Existing current files include `Scripts/UE5/check_fastlio_ros2_topics.sh`
    and `Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh`.
contradictions_or_history:
  The missing script names may be stale, renamed, generated elsewhere, or
  intentionally absent. This round does not edit formal workflows.
formal_target_if_promoted:
  `Docs/Workflows/ros2_runtime_setup.md` or `Docs/Workflows/unreal_renderer.md`
  only after a round-3 current-file check.
next_round_action:
  Before promoting ROS2 command recipes, verify whether the missing helper
  scripts were renamed, should be restored, or should be removed from formal
  docs.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| Installing ROS1 Noetic directly on Ubuntu 22.04 as the main route | Rejected for this host; ROS1 can be a reference or approved bridge/container route only. |
| Treating ROS2 replay input topics as FAST-LIO localization output | Rejected. |
| Treating `/mosim/replay_odometry` as FAST-LIO odometry | Rejected. |
| Browser HTML point-cloud review as active mapping evidence | Rejected. |
| Treating old no-candidate, zero-output, or failed-threshold FAST-LIO files as the latest global answer | Rejected; use route/date/source priority. |
| Treating Factory Gate B manual-review readiness as final controller/planner/product acceptance | Rejected. |
| Claiming rosbridge is currently listening without a live port or MCP check | Rejected for this migration round. |

## Round 3 Promotion Candidates

Only these narrow items are candidates for round 3:

1. A source-priority note for ROS2/FAST-LIO status:
   latest route-specific `*_CURRENT` gates and runtime review bundles first;
   older preflight, blocker, candidate, and diagnosis files are historical
   context unless they match the current route.
2. A command-staleness check for ROS2 helper scripts:
   verify whether `open_mapping_rviz_ros2.sh` and
   `run_fastlio_rviz_replay_ros2.sh` are renamed/missing before repeating those
   commands in formal docs.
3. A compact anti-regression note:
   replay/RViz readiness and HTML previews are not FAST-LIO localization
   evidence.

No live host, apt, rosbridge, final FAST-LIO, final planner, or final
controller claim is ready for formal promotion from this cache.

## Verification Needed Before Round 3

```text
1. Re-read latest `*_CURRENT` gate files and check for newer runtime folders.
2. Re-check whether a user manual UE/RViz review result has been recorded.
3. Verify whether ROS2 helper script references are current, renamed, or stale.
4. If live ROS-MCP status matters, run a current port/MCP probe in an
   infrastructure task, not as chat-memory migration.
5. Keep MWORKS dynamics/control evidence, UE/RViz visual runtime evidence, and
   FAST-LIO localization evidence separated.
```
