# Round 1 ROS2 Runtime Setup Memory Cache

Date: 2026-06-04 CST

Scope: first cache pass for long-session memory about WSL2 Ubuntu 22.04 ROS2
Humble setup, ROS/RViz runtime boundaries, ROS-MCP/rosbridge behavior, apt
key/source repair, and FAST-LIO claim status. This is cache-only. It does not
promote any current host or FAST-LIO state as final without a later round-2
verification.

## Status

```text
round: 1
topic: ROS2 runtime setup and FAST-LIO runtime boundary
status: candidate_cache_created
risk: medium_high
formal_docs_patched_this_round: none
cache_only: true
source_pointers_re_read:
  - Docs/Workflows/ros2_runtime_setup.md
  - PROGRESS.md
  - Results/unreal_scene_mapping/ROS_MAPPING_RUNTIME_ENV.md
  - Results/unreal_scene_mapping/FASTLIO_RUNTIME_STATUS.md
  - Results/unreal_scene_mapping/FASTLIO_RUNTIME_CANDIDATES.md
  - Results/unreal_scene_mapping/FASTLIO_FAMILY_COMPATIBILITY.md
  - Results/unreal_scene_mapping/UE_SCENE_RUNTIME_READINESS.md
```

This cache records project-local documentation and result pointers only. It does
not read or modify `/etc/apt`, `/opt/ros`, `/home/linux/.ros`, or other external
system paths. Future infrastructure repair outside the repository still needs a
fresh explicit user request or approved project-infrastructure exception.

## Candidate Items

### ROS2-MEM-001 - Ubuntu 22.04 Uses ROS2 Humble, Not Direct ROS1 Noetic

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  On the current Ubuntu 22.04 WSL2 host, MoSim UE mapping/runtime work should
  use ROS2 Humble/RViz2 rather than trying to install ROS1 Noetic directly.
known_sources:
  - `Docs/Workflows/ros2_runtime_setup.md`.
  - `PROGRESS.md` 2026-06-01 ROS2 runtime setup entry.
  - `Results/unreal_scene_mapping/ROS_MAPPING_RUNTIME_ENV.md`.
contradictions_or_history:
  Earlier ROS1/FAST-LIO/Catkin assumptions remain useful as reference or bridge
  candidates, but direct ROS1 Noetic on Ubuntu 22.04 is no longer the primary
  route.
current_evidence_needed:
  Round 2 should re-run or re-read `check_ros_mapping_runtime_env.py --write`
  output before claiming the current host state.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/ros2_runtime_setup.md` and
  `Docs/Workflows/unreal_renderer.md`.
next_round_action:
  Mark as already formalized if current runtime-env JSON still reports
  `ros_generation=ros2`.
```

### ROS2-MEM-002 - ROS Apt Key/Source Issue Was Resolved

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  The recorded ROS2 apt key/source repair uses keyring
  `/usr/share/keyrings/ros-archive-keyring.gpg` and the Tsinghua ROS2 jammy
  source; project docs say apt update had no `NO_PUBKEY` or `EXPKEYSIG` error.
known_sources:
  - `Docs/Workflows/ros2_runtime_setup.md`.
  - `PROGRESS.md` 2026-06-01 ROS2 runtime setup entry.
  - `FASTLIO_RUNTIME_STATUS.md`.
contradictions_or_history:
  Old terminal errors about missing/expired ROS apt keys are superseded if the
  current host checks still pass.
current_evidence_needed:
  Round 2 should verify from current project preflight or a targeted user-
  approved infrastructure check before telling the user to avoid all apt repair.
formal_target_if_promoted:
  Existing ROS2 setup workflow.
next_round_action:
  Keep as infrastructure memory; do not run external apt commands during
  session-memory migration unless explicitly requested.
```

### ROS2-MEM-003 - ROS-MCP Uses Active ROS Runtime Through Rosbridge

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  ROS-MCP talks to the active ROS runtime through rosbridge. On this host the
  intended route is ROS2 Humble plus `ros-humble-rosbridge-suite`; the WSL
  wrapper can auto-start `rosbridge_websocket` on port `9090` in the
  background when needed.
known_sources:
  - `Docs/Workflows/ros2_runtime_setup.md` ROS-MCP note.
  - User-visible launch output in the long session showed `rosbridge_websocket`
    and `rosapi_node` starting, with rosbridge listening on port `9090`.
contradictions_or_history:
  The rosbridge warnings about default service timeout and threading were
  warnings, not necessarily startup failures. A separate terminal should not be
  required if the wrapper auto-start works.
current_evidence_needed:
  Round 2 should re-read current MCP config/wrapper docs and, only if needed,
  inspect project-local wrapper references. Do not assume rosbridge is running
  without a current port/process check.
formal_target_if_promoted:
  `Docs/Workflows/ros2_runtime_setup.md` or `Docs/Workflows/debug_mcp.md`.
next_round_action:
  Verify wrapper path/config from project docs before adding any new formal
  command.
```

### ROS2-MEM-004 - ROS2 Replay/RViz2 Input Review Is Ready, But Runtime
Evidence Is Separate

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Current project reports say ROS2/RViz2 replay input review is ready, but
  environment preflight and replay inputs are not completed mapping/runtime or
  FAST-LIO localization evidence.
known_sources:
  - `ROS_MAPPING_RUNTIME_ENV.md`: `ready_for_native_mapping_runtime=true`,
    `ros_generation=ros2`, `ros2_replay_ready=true`, and
    `fastlio_ros2_runtime_claimable=false`.
  - `UE_SCENE_RUNTIME_READINESS.md`: file loop ready but runtime ready false.
  - `Docs/Workflows/ros2_runtime_setup.md` runtime boundary.
contradictions_or_history:
  Older generated replay files and topic-smoke outputs can look like runtime
  evidence. They are input/review readiness unless FAST-LIO output topics are
  recorded and evaluated.
current_evidence_needed:
  Round 2 should re-read latest `ROS_MAPPING_RUNTIME_ENV.md/json` and scene
  runtime readiness JSON before any runtime claim.
formal_target_if_promoted:
  Already represented in ROS2/renderer workflows.
next_round_action:
  Put in round-3 already-formalized or narrow cross-reference bucket.
```

### ROS2-MEM-005 - HTML Is Not An Active Point-Cloud/Map Review Window

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  Active point-cloud, occupancy/grid-map, TF, odometry, FAST-LIO, and planner
  review must use RViz2 or equivalent native robotics tooling. Browser HTML is
  only an offline report preview.
known_sources:
  - `AGENTS.md` Unreal Mapping Window Rule.
  - `Docs/Workflows/ros2_runtime_setup.md`.
  - `Docs/Workflows/unreal_renderer.md`.
  - `ROS_MAPPING_RUNTIME_ENV.md` claim boundary.
contradictions_or_history:
  Old HTML point-cloud previews and UE overlays were rejected as active review
  evidence.
current_evidence_needed:
  Round 2 can mark this as already formalized unless a new workflow conflicts.
formal_target_if_promoted:
  Already represented in `AGENTS.md` and renderer/ROS workflows.
next_round_action:
  Keep as anti-regression memory.
```

### ROS2-MEM-006 - `/mosim/replay_odometry` Is Reference Pose, Not FAST-LIO
Odometry

```text
round: 1
status: candidate
risk: high
candidate_statement:
  `/mosim/replay_odometry` is replay/reference pose for operator review and
  must not be counted as FAST-LIO `/Odometry` or `/odometry`.
known_sources:
  - `PROGRESS.md` ROS2 runtime setup entry.
  - `Docs/Workflows/ros2_runtime_setup.md` FAST-LIO note.
  - `ROS_MAPPING_RUNTIME_ENV.md` claim boundary.
contradictions_or_history:
  Topic names in ROS1 and ROS2 differ (`/Odometry` versus `/odometry`), and
  replay odometry can be confused with estimator output.
current_evidence_needed:
  Round 2 should re-read current launch/topic checker scripts before stating
  expected topic names.
formal_target_if_promoted:
  Existing ROS2 setup workflow and runtime topic check docs.
next_round_action:
  Verify topic checker defaults and candidate-specific odometry topic.
```

### ROS2-MEM-007 - FAST-LIO Claim Status Has Superseded Intermediate States

```text
round: 1
status: candidate_with_contradiction
risk: high
candidate_statement:
  FAST-LIO runtime status is route- and date-specific. Current docs/results
  include both older "no local ROS2 FAST-LIO-family source / cannot claim"
  metadata scans and later `spark-fast-lio` runtime status showing real output
  topics with scene-specific evaluation results.
known_sources:
  - `FASTLIO_FAMILY_COMPATIBILITY.md` says local FAST-LIO family sources are
    ROS1/Catkin-only and `can_claim_fastlio_ros2_runtime=false`.
  - `FASTLIO_RUNTIME_CANDIDATES.md` says `spark-fast-lio` is a patchable ROS2
    candidate and the external `Ericsii/FAST_LIO_ROS2` import was not local
    evidence at that point.
  - `Docs/Workflows/ros2_runtime_setup.md` later says `spark_lio_mapping`
    records exist for `/cloud_registered`, `/odometry`, and `/path`.
  - `FASTLIO_RUNTIME_STATUS.md` says Factory fails threshold, Derelict passes
    with warnings.
contradictions_or_history:
  These files reflect different stages. Do not answer from only the older
  compatibility scan or only the later summary without checking latest result
  directories.
current_evidence_needed:
  Round 2 must read the latest `fastlio_runtime_scan099` artifacts, status
  reports, logs, and evaluation JSONs before saying FAST-LIO is claimable for a
  scene.
formal_target_if_promoted:
  A later narrow update may be needed if workflow docs contain stale
  `START_FASTLIO=0` or claimability wording.
next_round_action:
  Verify latest result folders and classify Factory, Derelict, and any other
  scene separately.
```

### ROS2-MEM-008 - Current FAST-LIO Scene Outcomes Are Not Global Acceptance

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Latest cached status says `spark-fast-lio` produced real output topics;
  Derelict passes current numeric thresholds with warnings, while Factory fails
  error thresholds and cannot be claimed. This is scene-specific and not final
  production-grade localization.
known_sources:
  - `Results/unreal_scene_mapping/FASTLIO_RUNTIME_STATUS.md`.
  - `Docs/Workflows/ros2_runtime_setup.md`.
  - `PROGRESS.md`.
contradictions_or_history:
  Earlier zero-output, crash, and no-candidate states were superseded for some
  runs but remain useful failure history. Factory remains degraded despite
  output topics existing.
current_evidence_needed:
  Round 2 should re-read latest runtime evaluation JSON/logs, including
  timestamp monotonicity and IMU warning status.
formal_target_if_promoted:
  Possibly `Docs/Workflows/unreal_renderer.md` or a result manifest, but only
  after round 2.
next_round_action:
  Do not promote numeric RMSE/max-error values until latest artifacts are
  re-read in round 2.
```

## Rejected Or Superseded Historical Items

```text
REJ-ROS2-001:
  Installing ROS1 Noetic directly on Ubuntu 22.04 as the primary route is
  rejected for this host.

REJ-ROS2-002:
  Treating ROS2 replay input topics as FAST-LIO localization output is
  rejected.

REJ-ROS2-003:
  Treating `/mosim/replay_odometry` as FAST-LIO odometry is rejected.

REJ-ROS2-004:
  Treating HTML/browser point-cloud preview as active mapping runtime evidence
  is rejected.

REJ-ROS2-005:
  Treating old zero-output/crash/no-candidate findings as the latest answer
  without re-reading current runtime results is rejected.

REJ-ROS2-006:
  Treating Derelict's current pass-with-warnings as final production-grade
  localization, or applying it to Factory, is rejected.
```

## Round 2 Backlog

1. Re-read `ROS_MAPPING_RUNTIME_ENV.md/json` and rerun or inspect current
   preflight only if the task explicitly allows runtime checks.
2. Re-read `FASTLIO_RUNTIME_STATUS.md` plus latest scene-specific runtime
   result folders before classifying scene outcomes.
3. Reconcile older `FASTLIO_FAMILY_COMPATIBILITY` and candidate-decision
   reports with newer `spark-fast-lio` runtime evidence.
4. Check current ROS-MCP/rosbridge wrapper docs before recording auto-start
   behavior as current.
5. Update `round3_promotion_rejection_map_20260604.md` only after the round-2
   evidence pass.

## Do Not Promote Yet

- Any current host apt/key status without a current preflight or explicit
  infrastructure check.
- Any scene-level FAST-LIO claim without latest runtime logs/evaluation files.
- Any global "FAST-LIO works" statement that does not separate Factory,
  Derelict, input replay, runtime output topics, and quality warnings.
- Any command that edits external apt/ROS/system paths as part of session memory
  migration.
