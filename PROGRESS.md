# Project Progress

> Current project memory for agent recovery. Keep this file short. Durable
> rules stay in `AGENTS.md`; detailed procedures stay in `Docs/Workflows/`.

## Current Focus

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
  This first ID set was later superseded by the real visible department threads
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
- 2026-05-26 visible department communication correction: internal
  `spawn_agent` calls are not department communication. The visible department
  threads currently used by the UI are:
  `019e6335-a2e2-7b92-b9f8-396400f4429e` (`MoSim｜总经办 PMO`),
  `019e6318-4516-72c1-a50a-a36dc2aed215` (`MoSim｜调度中台`),
  `019e6319-fecd-7bd1-a4d5-7a5207e0ddba` (`MoSim｜研发工程部`),
  `019e631b-c6b2-73e3-9ad9-551b12687fe0` (`MoSim｜文档秘书部`),
  `019e631d-8164-72e3-aac5-4ee3d91e462e` (`MoSim｜验证测试部`),
  `019e631f-406e-7401-af17-8f17e09a50e3` (`MoSim｜安全合规部`), and
  `019e6321-1940-7bc0-8a97-f2720aa8af1b` (`MoSim｜DevOps 发布部`). Dispatch to a
  visible department by `codex exec resume <thread_id>` plus
  `--output-last-message`; do not represent an internal subagent as that
  department. Communication probe `comm-probe-20260526-01` to DevOps returned
  `DEVOPS_COMM_OK｜received_from_main｜task_id=comm-probe-20260526-01`.
- 2026-05-26 visible department metadata fix: `codex exec resume` failed when
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
- Do not reduce "continue tasks" to only the latest user-visible thread.
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

## Recovery Pointers

- Agent orchestration workflow: `Docs/Workflows/agent_orchestration.md`
- Long-running task ledger: `Docs/Workflows/agent_task_ledger.md`
- External repo audit workflow: `Docs/Workflows/audit_external_repo.md`
- Unreal renderer workflow: `Docs/Workflows/unreal_renderer.md`
- Git/quality rule source: `AGENTS.md#331-parallel-agent-rule`
- Clean Docs/workflow recovery branch:
  `git/recovery-docs-workflows-clean-20260521` at
  `c279bf4add5a4efb0cf5699e93172047ad148a20`

## Current Unreal Renderer Checkpoints

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
