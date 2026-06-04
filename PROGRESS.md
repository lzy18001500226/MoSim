# Project Progress

> Current project memory for agent recovery. Keep this file short. Durable
> rules stay in `AGENTS.md`; detailed procedures stay in `Docs/Workflows/`.

## Current Focus

- 2026-06-04 CST long-session memory migration for
  `MoSim|四旋翼无人机仿真系统` is recoverable and remains cache-first. Durable
  workflow: `Docs/Workflows/session_memory_migration.md`; ledger row:
  `SESSION-MEMORY-MIGRATION-20260604`; coverage matrix:
  `Docs/Cache/session_memory_migration/coverage_matrix_20260604.md`; round-3
  gate: `Docs/Cache/session_memory_migration/round3_promotion_rejection_map_20260604.md`.
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
  Continue round 3 one narrow item at a time: re-read current evidence and the
  formal target doc in the same round, then patch narrowly, reject/supersede,
  or record a user-review blocker. Do not compress this `PROGRESS.md` or mark
  the goal complete until high-risk items have round-3 promotion, rejection,
  supersession, or explicit user-review/current-evidence gates.

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
