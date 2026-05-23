# Project Progress

> Current project memory for agent recovery. Keep this file short. Durable
> rules stay in `AGENTS.md`; detailed procedures stay in `workflows/`.

## Current Focus

- Current active goal: complete the S0/S1 Unreal rendering loop to a state that
  can be manually reviewed. Goal records are total objectives, not single-step
  tasks; keep the immediate next action separately in the active queue or
  ledger.
- Current architecture boundary: keep the simulator architecture on the correct
  branch: MWORKS/Syslab/Sysplorer solver evidence plus project-owned UE5
  renderer and editable scene assets. RflySim maps are native-runtime visual
  references only, not an editable base for the new simulator.
- Current UE scene gate: `workflows/unreal_renderer.md#rflysim--sunray-scene-reconstruction-plan`
  is the active plan. Do not start new UE5 scene implementation until the user
  reviews the scene source roles, first-scene family, data model, and acceptance
  gates.
- UE scene roadmap now defines S0-S7 in
  `unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json`.
  Active implementation is limited to S0 `renderer_framework` and S1
  `competition_industrial_hybrid`; S2-S7 are planning contracts only until
  later review unlocks them.
- S0 source-level preparation is complete: `renderer_framework` packets can be
  dry-run streamed with `map_id=renderer_framework`, and the UE map actor clears
  stale static map previews when a profile has no `render_map_json`.
  2026-05-23 correction: editor MCP and standalone game review are separate
  routes. Editor MCP read probes now work when the editor is open; standalone
  game review must be validated through the `-game` process and UDP port 5005,
  not through the editor MCP listener.
- 2026-05-23 S0/S1 metadata hardening: S0 now has explicit
  `scene_bounds_box`, `optional_ground_plane`, and `debug_collision_proxy`
  registry entries; S1 now has distinct takeoff and landing pad proxies. This is
  a scene-contract fix only. It is not UE viewport evidence.
- 2026-05-23 UE MCP status distinction: `/mcp` may list the `unreal_engine`
  tools, but the actual tool call still times out if Unreal Editor's plugin is
  not reachable on TCP `55557`. Treat inventory success as wrapper availability
  only, not viewport readiness.
- 2026-05-23 S0/S1 packet contract extension: `stream_unreal_udp.py` now emits
  `mission`, `local_known_map`, `status`, and `overlays` fields. These are
  display contracts until `evidence_backed=true`; do not use preview packets as
  proof of S1 local avoidance or occlusion behavior.
- 2026-05-23 TaskSecretary correction: do not set the thread goal to a single
  engineering step. The active total goal is S0/S1 Unreal rendering loop to
  manual-review readiness; the current small step is making the UE C++ UDP
  receiver compatibly parse the Python packet contract fields `mission`,
  `local_known_map`, `status`, and `overlays`.
- 2026-05-23 UE C++ packet receiver: source-level receiver compatibility now
  includes mission, local-known-map, local-plan provenance, status, and overlay
  fields. This is still a packet/data-contract step only; viewport/manual
  visual evidence remains blocked until the Unreal Editor MCP listener is
  reachable.
- 2026-05-23 UE MCP listener probe: after opening the project-owned UE editor,
  `scripts/probe_unreal_mcp_listener.py --timeout 1` reached
  `172.17.48.1:55557`, and `unreal_engine.get_actors_in_level` returned the
  editor world actor list. This proves editor-side MCP availability only.
  Standalone `-game` windows are validated through UDP 5005 and log output.
- 2026-05-23 UE renderer build: `scripts/build_unreal_renderer.sh` passed after
  the packet receiver extension, including UHT and `QuadrotorMworksBridge`
  compile/link. Generated `Binaries/` and `Intermediate/` outputs are ignored.
- 2026-05-23 S0/S1 readiness gate: `scripts/check_unreal_s0_s1_readiness.py`
  now bundles source-level checks for Python syntax, bridge contract, S0/S1
  staging packages, and UDP packet fields. It passes without
  `--check-listener`; `--build` also passes UE 5.7 UBT/UHT. With
  `--check-listener` it correctly fails while UE Editor TCP `55557` is
  unreachable.
- 2026-05-23 UE MCP listener route audit: the WSL wrapper defaults
  `UNREAL_HOST` to the WSL default gateway. The listener probe now tests
  `UNREAL_HOST`, WSL gateway, and `127.0.0.1`. The editor route is healthy when
  the editor plugin is running; do not use that probe as a gate for standalone
  game UDP playback.
- 2026-05-23 TaskSecretary intake: current goal is to resume S0/S1 Unreal
  renderer work with a recoverable split. Main agent owns the critical path and
  integration; `UEMCPProbe(Ptolemy)` owns the smallest UE MCP connection/read
  probe; `SceneContractOwner(Maxwell)` owns no-viewport S0/S1 data-contract,
  checks, and docs if MCP remains unavailable; `GitIntegrator` owns commit/push
  only after checks pass. Acceptance: UE read probe plus viewport note when MCP
  recovers, or no-viewport contract/check/doc update plus targeted verification
  and pushed commit. Blocker: UE Editor UnrealMCP listener still unreachable
  from WSL on `55557`, credentials, destructive cleanup, or unsafe Git state.
- Active recovery goal for this turn: advance the next S0/S1 Unreal renderer
  round with recoverable sub-agent split. `UEMCPProbe(Ptolemy)` owns the
  smallest `unreal_engine` MCP blocker diagnosis; `SceneProfileAuditor(Maxwell)`
  owns the read-only S0/S1 profile/workflow/code-contract audit. Main agent
  integrates only after those reports identify safe next writes and checks.
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
| UE S0/S1 renderer next round | `TaskSecretary` + `UEMCPProbe(Ptolemy)` + `SceneProfileAuditor(Maxwell)` + `RendererContractAuditor(Carson)` | editor-mcp-ok-standalone-review-in-progress | Editor MCP route is healthy when the project editor is open: listener probe reached `172.17.48.1:55557` and `get_actors_in_level` returned actors. Maxwell fixed S0/S1 metadata gaps. Carson identified missing S1 packet contracts; `stream_unreal_udp.py` now emits mission/local-map/status/overlay fields while keeping render-only flags explicit, and the UE C++ receiver now parses them. `scripts/check_unreal_s0_s1_readiness.py` passes source-level checks. Current fix is standalone `-game` review: spawn runtime actors through GameMode, check UDP 5005, stream review packets, then inspect logs/manual viewport. |
| UE S0/S1 runtime autos-pawn review | main agent | verified-awaiting-git | `scripts/check_unreal_s0_s1_readiness.py` and `scripts/build_unreal_renderer.sh` passed. `scripts/review_unreal_s0_s1_renderer.sh` streamed 1604 frames to the standalone game UDP receiver at `172.17.48.1:5005`. UE log confirms `MworksUnrealRendererGameMode`, map/playback actor spawn, UDP listen, and first received MWORKS frame. |
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
