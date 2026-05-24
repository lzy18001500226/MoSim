# Project Progress

> Current project memory for agent recovery. Keep this file short. Durable
> rules stay in `AGENTS.md`; detailed procedures stay in `workflows/`.

## Current Focus

- Current active goal: complete the S0/S1 Unreal rendering loop to a state that
  can be manually reviewed. Goal records are total objectives, not single-step
  tasks; keep the immediate next action separately in the active queue or
  ledger.
- 2026-05-24 Unreal map reset: stop improving all old generated blockout,
  grid, STL, semantic-box, RflySim direct-mount, factory-review, and
  YunZong/Sunray primitive-reconstruction maps. The old routes have been
  cleaned from `unreal/` except for the reusable renderer/bridge shell.
  Current map work must start from real editable Unreal/Fab/Epic/open-source
  scene assets with physical-world visual language, then connect the existing
  MWORKS playback bridge after the map itself passes manual review.
- Current map-source priority: use downloaded Fab/Epic/free UE assets such as
  factory/warehouse, forest/park, indoor corridor/cave, city/building, and open
  outdoor scene packs. Do not reconnect quadrotor, radar, trajectory, UDP, or
  MWORKS simulation until the selected map source is visually acceptable.
- Keep a `TaskSecretary` intake record for new user corrections, sub-agent
  terminal results, Git blockers, and manual-review decisions before promoting
  stable items to this file or the ledger.
- Current task/status review draft for user confirmation:
  `results/tmp/session_audit_20260521/task_status_review_20260521.md`.
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
| Agent organization model | main agent + `TaskSecretary` | done | Modern-company department model added in `workflows/org_operating_model.md`; future multi-agent work must record user directives and work checkpoints before relying on chat memory. |
| External docs learning | `ExternalDocsLearningOwner` | recurring-loop-defined | Use `docs/index/external_learning_index.md` and `workflows/agent_orchestration.md#71-recurring-learning-owner` when failures, new tools, new repos, or milestones trigger another learn-and-patch cycle. |
| Vehicle parameter identification | `VehicleParamIdentificationResearcher` | local-code-audit-complete-awaiting-sunray-ulog | `references/Data` code audit is promoted to `workflows/identify_quadrotor_parameters.md`; first useful data package is RC-collected PX4 `.ulg` logs plus `.params`, exact takeoff mass, motor order, and motor/prop/ESC info. RPM or thrust-stand data remains optional but improves confidence. |
| AirSim batch migration | `AirSimMigrationCoordinator` + `AirSimGitBatchOwner` | done | Git-safe migration is complete and pushed. Tracked scopes now include Cosys tutorial/content assets under 100 MB, SPEAR source/reference subset, CARLA UE5 source/reference subset, and IsaacSim text/source subset. Remaining local ignored content is intentional: CARLA image/content packs, IsaacSim LFS-managed assets/cache/data, and SPEAR `third_party`/Content/generated assets. |
| UE S0/S1 renderer next round | `TaskSecretary` + `UEMCPProbe(Ptolemy)` + `SceneProfileAuditor(Maxwell)` + `RendererContractAuditor(Carson)` + `Erdos` | source-ready-editor-mcp-currently-unreachable | S0/S1 source-level and standalone UDP runtime paths are ready: S0/S1 metadata gaps are fixed, packet contracts include mission/local-map/status/overlay fields, the UE C++ receiver parses them, S1 render-map instances carry `source.collision_proxy_id`, and `scripts/check_unreal_s0_s1_readiness.py --build` passes. Current 2026-05-23 listener probe fails, so Editor MCP/viewport automation remains unavailable until the UE editor plugin is reachable on TCP `55557` and one read-only actor probe passes. |
| UE S0/S1 runtime autos-pawn review | main agent | done | Runtime autos-pawn, S1 blockout map, and review-camera input fixes are pushed through `dbf03cdcd`. `scripts/check_unreal_s0_s1_readiness.py` and `scripts/build_unreal_renderer.sh` passed. `scripts/review_unreal_s0_s1_renderer.sh` streamed 1604 frames to the standalone game UDP receiver at `172.17.48.1:5005`. UE log confirms `MworksUnrealRendererGameMode`, map/playback actor spawn, UDP listen, first received MWORKS frame, and review-camera movement/rotation input accepted. |
| S1 competition industrial hybrid blockout | main agent | runtime-reviewable-blockout | Added project-owned S1 blockout render map `map_competition_industrial_hybrid_render_map.json` and bound it from the S1 profile. `SCENE_ID=competition_industrial_hybrid_manual_review MAP_ID=competition_industrial_hybrid bash scripts/review_unreal_s0_s1_renderer.sh` streamed 1604 frames; UE log confirms map selection and load: terrain `308`, random/inspection columns `11`, wall/gate/pad boxes `11`. This is visual blockout evidence only, not final art or proof of formal local-avoidance behavior. |
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
  `workflows/agent_task_ledger.md` and `results/agent_runs/*/events.jsonl`.
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
  work checkpoints stay only in chat. The secretary/PMO route must capture them
  in intake, ledger, PROGRESS, or WAL before they are treated as recoverable.
- Do not conclude parameter identification with "parameters are wrong"; produce
  the data, log fields, estimator route, MWORKS mapping, and validation plan.
  For Sunray150, ordinary RC operation is acceptable if PX4 logs include the
  required actuator, attitude/rate, acceleration, position, battery/status, and
  parameter-export data.
- Do not treat external docs/skills learning as a one-time task. Make it a
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
  project-owned docs/workflows or record third-party whitespace as accepted
  upstream state. If a third-party subset was reformatted during initial import,
  record it explicitly and do not repeat the pattern.
- Do not spend main-thread time on Git when local LFS hooks, stale
  `index.lock`, polluted branches, or broad external-reference trees make even
  small commits slow. Delegate Git to `GitIntegrator`; the main agent only sets
  scope, reviews evidence, and keeps the engineering critical path moving.

## Recovery Pointers

- Agent orchestration workflow: `workflows/agent_orchestration.md`
- Long-running task ledger: `workflows/agent_task_ledger.md`
- External repo audit workflow: `workflows/audit_external_repo.md`
- Unreal renderer workflow: `workflows/unreal_renderer.md`
- Git/quality rule source: `AGENTS.md#331-parallel-agent-rule`
- Clean docs/workflow recovery branch:
  `git/recovery-docs-workflows-clean-20260521` at
  `c279bf4add5a4efb0cf5699e93172047ad148a20`

## Current Unreal Renderer Checkpoints

- 2026-05-23 19:56 CST: User reported the standalone S1 Unreal review window
  could not move its view. Root cause was `MworksUnrealRendererGameMode`
  setting `DefaultPawnClass = nullptr`, leaving the game viewport without a
  controllable review pawn. Added a project-owned review camera pawn with
  WASD/QE movement, arrow/RMB mouse look, and Shift/Ctrl speed scaling; the
  readiness check now verifies this contract.
- 2026-05-23 20:01 CST: First rebuild attempt failed because the project-owned
  Unreal Editor process held `UnrealEditor-MworksUnrealRenderer.dll`; after
  stopping only the `MworksUnrealRenderer.uproject` process, the build passed.
  The next standalone launch exited inside `UnrealEditor-Landscape.dll` while
  loading `/Engine/Maps/Templates/OpenWorld`; default maps are now set to
  `/Engine/Maps/Entry` because renderer geometry is spawned at runtime.
- 2026-05-23 20:18 CST: `--check-listener` still failed while only the
  standalone `-game` process was running. `open_unreal_renderer.sh editor`
  incorrectly treated that `-game` process as an Editor session; editor-mode
  reuse now excludes command lines containing `-game`.
- 2026-05-23 20:26 CST: Actual Editor process was launched alongside the
  standalone game process. `scripts/probe_unreal_mcp_listener.py --timeout 1`
  reached `172.17.48.1:55557`; `scripts/check_unreal_s0_s1_readiness.py
  --check-listener` passed; Unreal MCP read-only `get_actors_in_level` returned
  actors from the Editor scene.
- 2026-05-23 20:36 CST: UE Editor rewrote `DefaultEngine.ini` with
  `AndroidFileServerRuntimeSettings/SecurityToken`. This is local generated
  config, not project state. The readiness check now fails if this section is
  present, so it must be removed before commit.
- 2026-05-23 20:48 CST: Added runtime input evidence for the standalone review
  camera. When keyboard/mouse input actually changes the camera, the game log
  prints `MWORKS review camera input accepted` with location and rotation.
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
