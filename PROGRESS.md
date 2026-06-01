# Project Progress

> Current project memory for agent recovery. Keep this file short. Durable
> rules stay in `AGENTS.md`; detailed procedures stay in `Docs/Workflows/`.

## Current Focus

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
  `ros2_replay_ready=true`, and no ROS2 blockers. The local
  `References/Lab/FAST_LIO` package remains ROS1/Catkin-only, so FAST-LIO
  localization is still unclaimed until a ROS2 FAST-LIO-family package or an
  approved ROS1 bridge publishes `/cloud_registered` and `/Odometry`. Headless
  ROS2 runtime smoke passed for Factory input topics using
  `run_fastlio_rviz_replay_ros2.sh` with `START_RVIZ=0 START_FASTLIO=0` and
  `check_fastlio_ros2_topics.sh` with `REQUIRE_FASTLIO_OUTPUTS=0`.

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
