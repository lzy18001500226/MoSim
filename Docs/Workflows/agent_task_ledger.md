# Agent Task Ledger

> Persistent coordination state for long-running or multi-agent work.
> This file prevents sub-agent task loss across chat turns, context refreshes,
> closed agents, and temporary tool failures.
>
> Machine-readable run events should be written under
> `Results/agent_runs/<run_id>/events.jsonl` when a task lasts more than one
> user turn, touches large reference trees, or delegates work to multiple
> sub-agents. Keep this Markdown ledger as the human recovery surface.

## Rules

1. Before starting a long-running sub-agent, add or update one row in this
   ledger.
2. Use stable role names, not arbitrary nicknames. Examples:
   `GitIntegrator`, `SpearSimSystemLauncher`, `MWORKSEvidenceRunner`.
3. A row must include objective, owner role, write scope, current state, last
   checkpoint, and recovery instruction.
4. When an agent returns `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or is closed,
   update the row before relying on another agent.
5. If an agent disappears after a user message or context refresh, recover from
   this ledger instead of guessing from memory.
6. Keep this ledger concise. Move detailed logs to the referenced workflow,
   result directory, or commit message.
7. The main agent remains the orchestrator: it owns the task graph, sub-agent
   instructions, integration, verification, and final report. A sub-agent may
   execute a stream, but it must not become the hidden owner of the whole plan.
8. If a sub-agent finishes and waits for instructions, either consume its
   result immediately, queue a concrete follow-up in this ledger, or close it
   after recording the checkpoint.

Status values:

```text
planned
running
paused
blocked
done
superseded
```

## Active Tasks

| ID | Role | Objective | Write Scope | State | Last Checkpoint | Recovery Instruction |
|---|---|---|---|---|---|---|
| GIT-20260521-UNDER100 | GitIntegrator | Submit all project files <=100 MB in safe batches and skip >100 MB/generated artifacts | Git index/branches, `.gitignore` only unless committing approved project files | done | Safe content from the clean aggregate was covered by pushed split branches; `uncovered_paths_final=0`. Do not push old polluted or aggregate branches. | For future Git work, start from current changed paths only. Keep >100 MB/generated artifacts excluded and avoid gitlinks/LFS pointers unless explicitly approved. |
| GIT-20260521-OKWINDS | GitIntegrator | Commit workflow/tooling updates, safely integrate `Docs/Skills/okwinds/**`, and rewrite unpublished integration branch to remove >100 MB ONNX blob | Git index/branches, `.gitignore` only if needed | done | Safe split branches pushed, including `git/skills-agent-awesome-codex-20260521` and workflow/docs branches. Unsafe aggregate branches remain intentionally unpushed. | Do not resume old polluted branches. Continue only from new current diffs. |
| GIT-20260521-PUSH-CLEAN | GitIntegratorPush | Push `git/finalize-safe-batches-clean-20260521` or split it into smaller clean branches if push keeps timing out | Git index/branches, `.gitignore` only if needed | done | Whole clean branch `git/finalize-safe-batches-clean-20260521` at `3abd6be6` validated with no >100 MB tree blobs and no gitlinks, but push remained too large for the transport window. Split branches pushed: `git/finalize-workflows-docs-clean-20260521` at `204b3169` and `git/finalize-okwinds-clean-20260521` at `3514d0a2`. | Continue remaining integration from `origin/main` in smaller clean scopes. Do not push old polluted branch `git/finalize-safe-batches-20260521`; avoid whole-branch push unless transport capacity changes. |
| OKWINDS-20260521-WORKFLOW-AUDIT | OkwindsWorkflowAuditor | Read-only audit of `Docs/Skills/okwinds/*` for reusable agent orchestration, WAL, skill packaging, evidence-chain, and doctor patterns | No writes | done | Audit completed. Borrow WAL/run events from `skills-runtime-sdk`, NodeReport evidence from `capability-runtime`, task graph and pause/resume semantics from `Agently`, skill validation from `agentskills`; reject unrelated UI/runtime adoption and `wkteam-api-sdk` as mostly irrelevant. | Use audit result to update workflow docs only; do not import full runtimes as project dependencies. |
| EXTDOCS-20260521-LEARN | ExternalDocsLearningOwner | Three-round learn/extract/update/review across Claude Code docs, Codex docs, open skills/workflow repos, and project-management/reviewer patterns | Assigned Docs/workflows only; no source/runtime dependency imports | done | Parent learning stream is accepted as historical completion together with `EXTDOCS-20260521-ROUND3`: external Docs/skills learning produced TaskSecretary, WAL, reviewer lanes, source-to-doc coverage, do-not-adopt lists, and fresh verification gates. | Superseded by recurring learning loop. Future work should start a fresh row when a new incident, tool, milestone, or user correction triggers another learn-and-patch cycle. |
| COSYS-20260521-BLOCKS-UE55 | UEBuildSmokeRunner | Build/smoke Cosys-AirSim Blocks UE 5.5 project from command line | `Results/tmp` logs; minimal project-local dependency sync if required | done | UBT passed with `exit_code=0`; log `Results/tmp/cosys_airsim_blocks_ue55_ubt_rerun_20260521_155920.log`; generated `UnrealEditor-Blocks.dll` and `UnrealEditor-AirSim.dll`. User visually checked scene. Blocks-local `AirLib.lib` is 154 MB and must not be committed. | Next route is AirSim API/settings/UE Blueprint or project UI integration; the Blocks scene alone has no project-specific function panel. |
| SPEAR-20260521-SYSTEM | SpearSimSystemLauncher | Verify SPEAR as a scene/RPC system, not as a UAV simulator | No source writes; runtime windows and temporary outputs only | done | SpearSim game window launched with `-game`; RPC port `30000`; `spear_ext` built; Python `spear.Instance` connected; minimal camera render/readback succeeded | For further SPEAR work, use it as map/RPC/vision reference only. Real UAV needs project-owned UE asset import/Blueprint. |
| SPEAR-20260521-MAPS | SpearMapReviewer | Review all local SPEAR maps | No source writes | done | Available main maps are `apartment_0000`, `debug_0000`, `debug_0001`; no larger complete UAV scene found | If user wants visual review, open maps one by one. Do not search for built-in drone simulation in SPEAR. |
| GIT-20260521-RECOVERY-DOCS | GitRecoveryIntegrator | Recover current Docs/workflow changes from polluted checkout into a clean branch and push without large/generated artifacts | Git index/branches only; no source model edits | done | Clean branch `git/recovery-docs-workflows-clean-20260521` pushed at `c279bf4add5a4efb0cf5699e93172047ad148a20`. Included only `AGENTS.md`, `PROGRESS.md`, `Docs/Index/workflow_index.md`, `Docs/Workflows/agent_orchestration.md`, `Docs/Workflows/agent_task_ledger.md`, and `Docs/Workflows/audit_external_repo.md`. No >100 MB blobs. | Use this branch as the safe Docs/workflow recovery point. Do not push old polluted branch `git/finalize-safe-batches-20260521`. |
| RFLYSIM-20260521-SCENE-REVIEW | RflySimSceneReviewer | Open locally available RflySim3D packaged scenes one by one for visual review without UE Editor | Runtime windows only; optional `Results/tmp` launch notes | superseded | User clarified this was an older line and RflySim maps are no longer the current priority. Do not continue scene opening until the reconstructed 2026-05-21 backlog says it is still active. | Stop RflySim scene review. Recover from session-derived backlog instead of memory. |
| EXTDOCS-20260521-ROUND3 | ExternalDocsLearningOwner | Complete third learn-and-update round for Codex/Claude docs, open skills/workflow repos, reviewer agents, and task-depth orchestration | Assigned Docs/workflows only | done | Round 3 completed from new source slices: `Docs/Skills/Agent/superpowers/skills/{verification-before-completion,requesting-code-review,receiving-code-review,dispatching-parallel-agents,subagent-driven-development,writing-skills,loopback-adjacent execution docs}`, `Docs/Skills/Agent/awesome-codex-subagents/categories/{04-quality-security,09-meta-orchestration,10-research-analysis}`, `Docs/Skills/Agent/awesome-codex-skills/{create-plan,gh-fix-ci,gh-address-comments,skill-creator,pr-review-ci-fix,datadog-logs,issue-triage}`, and OKWinds testing/coverage/review/pollution docs. Patched `Docs/Workflows/agent_orchestration.md`, `Docs/Workflows/audit_external_repo.md`, `Docs/Workflows/agent_task_ledger.md`, and `PROGRESS.md`. | Recovery: source-to-doc rules now require fresh verification evidence, two reviewer lanes, coverage matrices, WAL/log noise filtering, and explicit do-not-adopt lists. Remaining validation is docs-quality review plus `git diff --check`; do not import external runtimes or global agent configs. |
| PARAM-20260521-PX4-IDENT | VehicleParamIdentificationResearcher | Research practical methods and open-source projects for estimating quadrotor mass, inertia, motor/thrust, and drag parameters from PX4 logs or flight data | Read-only research; docs patch after review | done | Report saved to `Results/tmp/vehicle_param_identification_research_20260521.md`. Key conclusion: current `1.0 kg`, inertia, `motorConstant/lift_cofficient` values must be labeled `source=SDF_migration`, not Sunray150 identified truth. Recommended sources: PX4 ULog, `pyulog`, ETH ASL `data-driven-dynamics`, ARPL `data-driven-system-identification`, ESC/RPM or thrust stand data. Actionable route and risk-parameter table were promoted to `Docs/Workflows/identify_quadrotor_parameters.md`, `Docs/Design/02`, `Docs/Design/03`, and `Docs/Design/07`. | Next step is data collection and identification execution. Required user/vendor inputs: measured mass, `.ulg` logs with attitude/rate/actuator/IMU topics, motor order/rotor direction, ESC/RPM or thrust stand data. Do not upgrade parameters from `source=SDF_migration` to `identified` until held-out validation passes. |
| SESSION-20260521-BACKLOG | SessionBacklogAuditor | Reconstruct authoritative unfinished task backlog from 2026-05-21 session logs and the main 05/09 carry-over session | `Results/tmp/session_audit_20260521/`, then Docs/ledger after user review | running | Raw user-message extraction saved to `Results/tmp/session_audit_20260521/user_messages_20260521.md` with 92 messages. Keyword draft was too noisy and is not accepted as final. | Split session by time, have auditors classify tasks and decisions, merge into a user-reviewable backlog before executing old remembered tasks. |
| SESSION-20260520-BACKLOG | SessionBacklogAuditor | Reconstruct authoritative unfinished task backlog from 2026-05-20 session logs, because 05/21 tasks depend on prior-day context | `Results/tmp/session_audit_20260520/`, then Docs/ledger after user review | running | Raw user-message extraction saved to `Results/tmp/session_audit_20260520/user_messages_20260520.md` with 16422 lines. Needs segmented audit before execution. | Split by local time windows; classify tasks as done/running/blocked/superseded/unknown and identify user-review gates. |
| GIT-20260521-CONTINUITY | GitContinuityOwner | Keep Git progress alive while backlog/session audit continues; push stable Docs/workflow changes only from clean branch/index | Git index/branches only; no References/Results/generated artifacts | done | Clean branch `git/continuity-docs-backlog-clean-20260521` pushed at `2776f06e616b386aff0f29e9f8247d1eecd14733`. Included only `AGENTS.md`, `PROGRESS.md`, `Docs/Index/workflow_index.md`, `Docs/Workflows/agent_orchestration.md`, `Docs/Workflows/agent_task_ledger.md`, and `Docs/Workflows/audit_external_repo.md`. Push used `--no-verify` after confirming these six small files had no LFS filters because local pre-push hook could not find `git-lfs`. | Current checkout remains old polluted branch with local edits. Future Git work should continue from clean branches and avoid old polluted branch `git/finalize-safe-batches-20260521`. |
| SECRETARY-20260521-INSTRUCTION-LEDGER | TaskSecretary | Recover user directives from 2026-05-20/21, establish intake/goal rules, and promote reviewed coordination rules into durable docs | `Results/tmp/task_intake/`, `PROGRESS.md`, `Docs/Workflows/agent_orchestration.md`, `Docs/Workflows/agent_task_ledger.md`; `AGENTS.md` policy-level only | done | User reviewed `Results/tmp/session_audit_20260521/task_status_review_20260521.md` as broadly acceptable. Stable rules are promoted: TaskSecretary, goal split, Git owner stop condition, user-review gate, and parameter-identification next route. | Keep the accepted task/status table as recovery evidence. Future user corrections must go through TaskSecretary intake first, then durable docs only after review. |
| EXTDOCS-RECURRING-LEARNING | ExternalDocsLearningOwner | Recurring learn-and-patch loop for external docs, skills, agent orchestration, and workflow improvements triggered by project failures or milestones | Assigned Docs/workflows only; no global config or source-runtime imports | planned | Triggered by current issue: task plan existed but chat ended and sub-agent/task state risked disappearing; docs were updated, but index/structure and recurring review need a permanent loop. | On each trigger, perform source review, propose/patch target docs, run docs-quality review, and record accepted/rejected patterns. Do not import full external runtimes without explicit user approval. |
| GIT-20260521-FULL-CONVERGENCE-RESTART | GitFullConvergenceOwner | Converge current repository state by classifying every path group as pushed, ignored/excluded, needs-user-decision, or blocked | Git index/branches/commits/pushes, `.gitignore` only if needed | done | Owner `Helmholtz` returned `DONE_WITH_CONCERNS`. Pushed `git/full-convergence-docs-checkpoint-20260521` at `69bd26df44497153fd4eb731c5d03f811a9589e5`, containing only `PROGRESS.md` and `Docs/Workflows/agent_task_ledger.md`. It confirmed no final `.git/index.lock`; old aggregate branch `git/finalize-safe-batches-20260521` remains polluted and was not pushed. Path groups were classified as pushed via split refs, ignored/excluded, or unsafe old branches not to push. | Do not resume this owner. For future Git, start from clean branches or `origin/main`, avoid old polluted aggregate branches, and use path-limited status because full checkout/index refresh remains slow and `Docs/Skills/Agent` has stat noise. |
| AIRSIM-20260521-BATCH-MIGRATION | AirSimMigrationCoordinator | Migrate `C:\Users\HP\Desktop\AirSim` into `References/AirSim` in audited, small Git-safe batches using parent-child-grandchild agents | `References/AirSim/`, Git index/branches, `.gitignore` only if needed | running | Source exception approved by user. Nested subagent smoke passed. Low-risk stage completed and pushed: `PEDRA`/workflow docs `aadfb09bf`, management rules `bcd9cc5e`, `PegasusSimulator` `f3019f301`, `ProjectAirSim` `e70f1deb`, `UESVONavigation-develop` `6f357904`, `AirSim` `702cd898`, `unrealcv-5.2` subset `e5ea1ed3`. AirSim copied credential-like Unity and map fields were sanitized in the project copy before commit. `unrealcv-5.2` owner reformatted imported text for whitespace; record as a one-off deviation and do not repeat. | Remaining batches: decide `AirSim360/carla` 50-100 MB media handling; handle `IsaacSim` LFS pointers separately; handle `Cosys-AirSim/spear` with generated-artifact exclusions. Keep using child owners and secretary/reviewer checks; do not copy the remaining large repos whole. |
| ORG-20260522-OPERATING-MODEL | TaskSecretary / OrganizationDesigner | Define company-style multi-agent departments and make instruction/work-record capture mandatory | `Docs/Workflows/org_operating_model.md`, `Docs/Workflows/agent_orchestration.md`, `Docs/Index/workflow_index.md`, `PROGRESS.md`, `Docs/Workflows/agent_task_ledger.md` | done | Added organization model covering GeneralManager, TaskSecretary/PMO, project, test, security, DevOps, architecture, knowledge, and incident-review departments. Secretary hard rule now requires every directive, correction, manual-review result, sub-agent return, blocker, and checkpoint to be recorded before relying on chat memory. | For future multi-agent work, start with secretary intake, assign department owners, run test/security/docs review, then let GitIntegrator commit/push. |
| AIRSIM-20260522-COMPLETE-MIGRATION | AirSimMigrationCoordinator | Finish migrating `C:\Users\HP\Desktop\AirSim` into `References/AirSim` after ignore hardening, with main-agent routed sub-agent/reviewer handoffs | `.gitignore`, `References/AirSim/`, workflow docs, Git index/branches | done | Completed on clean `main`. Pushed additional batches after `f7dd12c922`: Cosys tutorial assets one file per commit, Cosys Unreal content assets, SPEAR source/reference subset, CARLA UE5 source/reference subset, and IsaacSim text/source subset. Final tracked counts: CARLA 1341, IsaacSim 3359, SPEAR 320, Cosys 2470. `main` and `origin/main` were synchronized after each pushed batch; no `>100MB` files were found under `References/AirSim` in final scan. | Treat migration as complete for Git-safe source/reference scope. Remaining ignored local content is policy-excluded: CARLA `Docs/img`/Content/generated assets, IsaacSim LFS-managed assets/cache/data, and SPEAR `third_party`/Content/generated assets. Reintroduce those only through a new explicit asset-batch task. |
| AIRSIM-20260523-RUNTIME-REVIEW | AirSimRuntimeReviewer | Review locally runnable AirSim-family runtime scenes in standalone/game windows and separate runnable scenes from blocked UE source projects | Runtime windows, `Docs/Workflows/unreal_renderer.md`, optional `Results/tmp` launch notes | done | Original AirSim Blocks and Cosys-AirSim Blocks are directly runnable smoke scenes only; they are not rich final scenes. SPEAR/CARLA remain blocked by module/build chains. RflySim packaged maps are directly viewable in native RflySim runtime, but not directly usable as editable UE5 scene assets, planner truth, or final simulator dependency. | Continue simulator work from project-owned UE5 renderer + editable/authorized assets. Use RflySim/AirSim/Cosys only as reference for scene style, protocols, sensors, timing, and API ideas unless a source-enabled asset package is obtained. |
| UE-MAP-RESET-20260524 | main agent | Retire failed generated Unreal visual routes and keep only the reusable UE renderer/bridge shell | `UE5/`, `Docs/Workflows/unreal_renderer.md`, `PROGRESS.md`, `.gitignore` | done | Removed OldFactory direct-open/review scripts, migration-staging packages, primitive FactoryReview actor, UE generated caches, and stale OldFactory ignore rules. `UE5/` now keeps only `MworksUnrealRenderer`, `QuadrotorMworksBridge`, and `README.md`. | Future map work must start from real editable UE/Fab/Epic/open-source assets and pass map-only manual review before reconnecting UAV/radar/trajectory/UDP playback. |
| UE-S0S1-20260523-NEXT | TaskSecretary / main agent; UEMCPProbe(Ptolemy); SceneProfileAuditor(Maxwell) | Advance the next S0/S1 Unreal renderer round: recoverable sub-agent split, diagnose `unreal_engine` MCP connection blockage, continue project-owned UE scene framework, then document, check, commit, and push through the normal owner route | TaskSecretary may edit only `Docs/Workflows/agent_task_ledger.md` and `PROGRESS.md`; UEMCPProbe is read-only diagnostics plus MCP/editor probes; SceneProfileAuditor is read-only audit of S0/S1 scene/profile/code contracts; main agent owns integration files and Git after results return | source-contract-updated | Ptolemy classified the MCP blocker: WSL cannot connect to UE Editor UnrealMCP TCP `55557`; no viewport evidence is available and repeated `get_actors_in_level` calls should stop until the plugin listener is confirmed. Maxwell found S0/S1 consistency gaps; main agent fixed S0 proxy registry metadata and S1 distinct takeoff/landing pad proxies, regenerated active packages/plans, and passed active package plus bridge checks. | Next: user or editor-side check must confirm the renderer project is open with UnrealMCP plugin listening on a WSL-reachable host/port. After MCP recovers, run the smallest read probe, then viewport review. Keep `stream_unreal_udp.py` local-plan preview labeled render-only until real planner/perception data is wired. |
| UE-S0S1-20260523-PACKET-CONTRACT | TaskSecretary(Jason); RendererContractAuditor(Carson); QualityGate(Bohr); main agent | Continue S0/S1 renderer after MCP inventory/tool distinction: if UE Editor MCP is unavailable, advance only file-level packet/data contracts and keep visual review blocked | Jason may edit `PROGRESS.md` and ledger only; Carson/Bohr are read-only; main agent owns `Scripts/UE5/stream_unreal_udp.py`, `Docs/Workflows/unreal_renderer.md`, docs, checks, and Git | done | Latest `unreal_engine.get_actors_in_level` still times out even though `/mcp` inventory lists the tool. Carson identified missing mission/local-known-map/status/overlay packet contracts. Main agent added those fields to the UDP dry-run packet with explicit `render_only`/`evidence_backed` flags and documented the contract. | Packet contract is source-level complete. Next dependency for viewport work is UE Editor MCP listener recovery; formal S1 local avoidance remains unclaimed until planner/perception evidence backs the packet fields. |
| UE-S0S1-20260523-CPP-UDP-PARSE | TaskSecretary / main agent | Implement source-level compatible parsing in the UE C++ UDP receiver for Python packet contract fields `mission`, `local_known_map`, `status`, and `overlays` | TaskSecretary may edit only `PROGRESS.md` and this ledger; main agent owns UE C++ receiver source, targeted checks, and later Git through normal owner route | done | User corrected goal usage: active goal is the total S0/S1 Unreal rendering loop to manual-review readiness, not this single parser step. Receiver source now exposes Blueprint-readable mission, local-known-map, local-plan provenance, status, and overlay fields. Checks passed: Python syntax, `check_unreal_bridge.py`, S0/S1 migration packages, UDP dry-run, `git diff --check`, and UE 5.7 UBT/UHT build through `Scripts/UE5/build_unreal_renderer.sh`. | Keep total S0/S1 goal active. Next safe action is UE MCP listener recovery and viewport/manual review, or additional source-level S0/S1 renderer work that does not require Editor tools. |
| UE-S0S1-20260523-RESUME | TaskSecretary / main agent; UEMCPProbe(Ptolemy); SceneContractOwner(Maxwell); GitIntegrator | Resume S0/S1 Unreal renderer under the user goal: recheck UE MCP, run the smallest viewport/read probe if available, otherwise advance no-viewport S0/S1 data contracts, checks, and docs, then verify, commit, and push | TaskSecretary: `PROGRESS.md`, this ledger only. UEMCPProbe: read-only UE MCP/editor probe. SceneContractOwner: S0/S1 profile/code/docs only. GitIntegrator: Git index/commit/push only after main-agent review. | superseded-by-later-rows | Later rows record the actual listener diagnosis, readiness gate, route audit, runtime review, completion audit, and current Editor MCP blocked state. | Do not resume this planned row. Use `UE-S0S1-20260523-EDITOR-MCP-RECHECK` plus `unreal-s0s1-completion-audit-20260523` as the current recovery points. |
| UE-S0S1-20260523-MCP-LISTENER-DIAG | main agent | Add a project-local preflight probe for the Unreal Editor-side MCP listener so tool inventory is not confused with viewport readiness | `Scripts/UE5/probe_unreal_mcp_listener.py`, `Docs/Workflows/debug_mcp.md`, `PROGRESS.md` | done | After commit `7a5efe17c`, `unreal_engine.get_actors_in_level` still returned `Connection timeout`; repeated actor-tool retries are wasteful until TCP `55557` reachability is confirmed. `Scripts/UE5/probe_unreal_mcp_listener.py` now gives a direct TCP check and currently reports `ConnectionRefusedError`. | Use this probe before any future interactive UE MCP work. |
| UE-S0S1-20260523-READINESS-GATE | main agent | Provide a single S0/S1 source-level readiness command plus optional listener gate before viewport review | `Scripts/UE5/check_unreal_s0_s1_readiness.py`, `Scripts/UE5/check_unreal_bridge.py`, `Docs/Workflows/unreal_renderer.md`, `PROGRESS.md` | done | Added `Scripts/UE5/check_unreal_s0_s1_readiness.py`. Source-level mode passes Python syntax, bridge contract, S0/S1 staging package, UDP packet dry-run checks, and `--build` passes UE 5.7 UBT/UHT. `--check-listener` correctly fails while UE Editor TCP `55557` is unreachable. | Source-level readiness is now one command. Next safe action after listener recovery is `python3 Scripts/UE5/check_unreal_s0_s1_readiness.py --build --check-listener`, then smallest UE MCP actor read probe and manual viewport review. |
| UE-S0S1-20260523-LISTENER-ROUTE-AUDIT | main agent | Align listener diagnostics with the WSL wrapper's actual `UNREAL_HOST` route | `Scripts/UE5/probe_unreal_mcp_listener.py`, `Docs/Workflows/debug_mcp.md`, `Docs/Workflows/unreal_renderer.md`, `PROGRESS.md` | done | Wrapper defaults `UNREAL_HOST` to WSL default gateway. After the project-owned UE editor was opened, `Scripts/UE5/probe_unreal_mcp_listener.py --timeout 1` reached `172.17.48.1:55557`, and `unreal_engine.get_actors_in_level` returned the editor world actor list. The remaining issue was not MCP availability; it was using the editor MCP listener as a gate for standalone `-game` UDP playback. | Future interactive editor work may use MCP after the listener probe. Future standalone game review must check the `MworksUnrealRenderer.uproject -game` process, UDP 5005, and runtime logs instead of `probe_unreal_mcp_listener.py`. |
| UE-S0S1-20260523-RUNTIME-AUTOSPAWN | main agent | Make the project-owned UE renderer open to a manually reviewable runtime scene without requiring manual placement of map/playback actors | `UE5/MworksUnrealRenderer/Source/MworksUnrealRenderer/`, `UE5/MworksUnrealRenderer/Config/DefaultEngine.ini`, `UE5/QuadrotorMworksBridge/Source/QuadrotorMworksBridge/`, `Scripts/UE5/open_unreal_renderer.sh`, `Scripts/UE5/review_unreal_s0_s1_renderer.sh`, `PROGRESS.md`, `Docs/Workflows/unreal_renderer.md`, `UE5/README.md` | done | Added a project GameMode route to spawn the map actor and playback actor at BeginPlay, set the playback actor's map pointer, and log runtime spawn status. Added first-frame UDP logging to the receiver. Corrected the manual review script so standalone `-game` mode waits for the Windows game process and UDP 5005 endpoint instead of the editor MCP listener. Evidence: `Scripts/UE5/check_unreal_s0_s1_readiness.py` passed, `Scripts/UE5/build_unreal_renderer.sh` passed, `Scripts/UE5/review_unreal_s0_s1_renderer.sh` streamed 1604 frames to `udp://172.17.48.1:5005`, and UE log shows GameMode load, map/playback actor spawn, UDP listen, and first frame `scene=renderer_framework_manual_review map=renderer_framework seq=0`. Later push through `dbf03cdcd` also fixed standalone review-camera input. | No pending Git action. Runtime window remains available for user manual review; future work is art quality, real local planning/perception evidence, and additional scenarios. |
| UE-S1-20260523-BLOCKOUT-RUNTIME-MAP | main agent | Promote S1 `competition_industrial_hybrid` from metadata-only profile to a project-owned runtime-reviewable blockout map | `Scripts/create_competition_industrial_hybrid_render_map.py`, `UE5/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json`, `UE5/MworksUnrealRenderer/Content/MworksData/map_competition_industrial_hybrid_render_map.json`, `Scripts/UE5/check_unreal_s0_s1_readiness.py`, `Scripts/UE5/review_unreal_s0_s1_renderer.sh`, `PROGRESS.md`, `Docs/Workflows/unreal_renderer.md` | done | Generated deterministic S1 blockout render map with terrain grid `23x15`, random/inspection columns `11`, wall/gate/pad boxes `11`, start `[-18,-10,1]`, goal `[18,10,1]`, and bound the S1 profile to `MworksData/map_competition_industrial_hybrid_render_map.json`. `Scripts/UE5/check_unreal_s0_s1_readiness.py --build` passed. Runtime review command `SCENE_ID=competition_industrial_hybrid_manual_review MAP_ID=competition_industrial_hybrid bash Scripts/UE5/review_unreal_s0_s1_renderer.sh` streamed 1604 frames; UE log confirms S1 profile selection and map load. Subsequent review-camera fix is pushed through `dbf03cdcd`. | No pending Git action. Keep claims scoped to blockout/runtime review; final art, real occlusion/local planning evidence, and formal S1 planner behavior remain future work. |
| UE-S0S1-20260523-EDITOR-MCP-RECHECK | main agent | Recheck current UE Editor MCP availability and keep the S0/S1 viewport evidence state accurate | `PROGRESS.md`, `Docs/Workflows/agent_task_ledger.md`, `Docs/Workflows/debug_mcp.md`, `Docs/Workflows/unreal_renderer.md`; read-only MCP probe | blocked-current-turn | Current read-only tool call `unreal_engine.get_actors_in_level` failed with `Connection timeout`. Project probe `python3 Scripts/UE5/probe_unreal_mcp_listener.py --timeout 1` also failed: WSL gateway `172.17.48.1:55557` timed out and `127.0.0.1:55557` refused. This contradicts any claim that editor/viewport MCP is currently ready. | Do not retry actor/Blueprint/viewport MCP tools until the renderer editor is open with `UnrealMCP` listening on a WSL-reachable TCP route. Continue only source-level checks or standalone `-game` UDP review. After recovery, rerun `python3 Scripts/UE5/check_unreal_s0_s1_readiness.py --build --check-listener`, then one read-only actor/scene probe. |
| UE-S1-20260523-BLACK-SCREEN | main agent; ReviewAuditor(Raman) | Fix S1 standalone renderer black viewport after user manual audit reported an all-black window | `UE5/MworksUnrealRenderer/Source/MworksUnrealRenderer/MworksUnrealRendererGameMode.*`, `Scripts/UE5/check_unreal_s0_s1_readiness.py`, `Docs/Workflows/unreal_renderer.md`, `PROGRESS.md`, this ledger | running | Latest S1 standalone log showed Entry map, review camera, UDP first frame, and S1 map JSON load were active, but no runtime lighting was spawned. Main agent added default sun/sky review lighting and a readiness token check. `Scripts/UE5/build_unreal_renderer.sh` passed. `SCENE_ID=competition_industrial_hybrid_manual_review MAP_ID=competition_industrial_hybrid bash Scripts/UE5/review_unreal_s0_s1_renderer.sh` streamed 1604 frames to game PID `68552`, and the log confirms `MWORKS renderer spawned default review lighting: sun=true sky=true`. Raman audited the diff as limited to runtime lighting/readiness, with no direct changes to drone model, UDP protocol, or map data. | Wait for user visual audit result. If visible, mark done and commit/push. If still black, inspect material/emissive path and camera target next; do not modify quadrotor mesh or UDP protocol without log evidence. |
| MOSIM-TOOLS-20260524-EPIC-LIBRARY | main agent; UnrealMCPAuditor(Laplace/Locke); EpicCacheAuditor(Kant) | Split MoSim tool capability boundaries and add a read-only Epic/Fab/Launcher library index for scene-source selection | `Scripts/UE5/epic_library_index.py`, `Scripts/UE5/mosim_epic_library_mcp.py`, `Scripts/UE5/mosim_epic_library_mcp_wsl_wrapper.sh`, `Scripts/UE5/check_epic_library_inventory.py`, `Scripts/tests/test_epic_library_index.py`, `Docs/Workflows/debug_mcp.md`, `Docs/Workflows/unreal_renderer.md`, `Docs/Index/workflow_index.md`, `PROGRESS.md`, this ledger | running | Audits found UE Editor automation is best as external MCP server plus C++ UE plugin bridge, while Epic/Fab library discovery is a separate cache/index boundary. Local index detects 11 Launcher items, 11 installs, 5 Fab assets, 3 old VaultCache projects, and 17 account-library items from allowlisted `OC_*.dat` parsing. Added the project-local WSL wrapper and health check so this can be registered as `mosim_epic_library` without touching UE Editor. | Finish tests and static checks, then report the exact MCP/tool split and config entry. |

## Completed Notes

- SPEAR is not equivalent to AirSim/RflySim for UAV dynamics. It provides UE
  maps, RPC, sensor/rendering, and scene control.
- For Unreal migration, prefer editable `.uproject`, `.umap`, `.uasset`,
  `Config/`, `Source/`, and `Plugins/*/Source/`. Runtime `.dll`, `.pak`,
  `Binaries/`, `Intermediate/`, `Saved/`, and `DerivedDataCache/` are not
  sufficient for editable migration.

## Run Event Format

Use JSON Lines for long-running agent or automation runs:

```json
{"event_id":"GIT-20260521-UNDER100-0001","ts":"2026-05-21T10:30:00+08:00","task_id":"GIT-20260521-UNDER100","agent_role":"GitIntegrator","event_type":"checkpoint","summary":"processed References/Lab","paths_read":["References/Lab"],"paths_written":[],"artifact_refs":[],"approval_state":"none","tool_state":"finished","error_kind":"","risk":"","next_action":"fix spear rpclib gitlink"}
```

Required fields:

| Field | Meaning |
|---|---|
| `event_id` | Stable event id, usually `<task_id>-NNNN`. |
| `ts` | Local timestamp with timezone. |
| `task_id` | Stable task id matching this ledger. |
| `agent_role` | Stable role name such as `GitIntegrator` or `SceneResearch`. |
| `event_type` | Use the canonical event type list in `Docs/Workflows/agent_orchestration.md`; common ledger rows usually use `task_started`, `checkpoint`, `blocked`, `completed`, or `superseded`. |
| `summary` | One-line factual update. |
| `paths_read` | Optional project-local paths inspected. |
| `paths_written` | Optional project-local paths changed. |
| `artifact_refs` | Optional evidence paths, commit hashes, logs, result files, hashes, and sizes. |
| `approval_state` | `none`, `requested`, `approved`, `denied`, or `pending`. |
| `tool_state` | `none`, `requested`, `finished`, `pending`, or `failed`. |
| `error_kind` | Shared taxonomy such as `timeout`, `mcp_unavailable`, `gui_blocked`, `license_or_login`, `git_push_rejected`, or `pack_too_large`. |
| `risk` | Known risk or empty string. |
| `next_action` | Concrete next action or recovery step. |

For explicit multi-round learn-and-update audits, add these optional fields to
each JSONL event or include them in `summary` when using the compact schema:

| Field | Meaning |
|---|---|
| `round` | `1`, `2`, or `3`; required for `round_started`, `round_learned`, and `round_doc_patched`. |
| `source_slice` | Local source paths read for that round, such as `Docs/Skills/okwinds/skills-runtime-sdk/docs_for_coding_agent/*`. |
| `patch_target` | Project docs expected to change in that round. |
| `do_not_adopt` | Runtime, UI, provider, API-client, or dependency patterns rejected for this project. |
| `contradictions` | Current project docs or rules that the round found incomplete or inconsistent. |

For queue-owning agents, include these optional fields in JSONL events or the
ledger checkpoint:

| Field | Meaning |
|---|---|
| `queue_source` | Path or source that owns the ready task list. |
| `claimed_item_ids` | Queue items claimed in the current checkpoint. |
| `tasks_completed` | Count or ids completed since last checkpoint. |
| `tasks_blocked` | Count or ids blocked since last checkpoint. |
| `review_status` | `not_started`, `passed`, `failed`, or `needs_followup`. |
| `elapsed_time` | Human-readable or machine-readable elapsed time. |
| `missing_evidence` | Required evidence that was not produced. |
| `source_to_doc_coverage` | Optional list or summary mapping external source paths to project doc rules, validation gates, and rejected patterns. |
| `fresh_verification` | Current-turn command or manual review gate used before claiming completion. |
| `reviewer_lanes` | `spec/compliance`, `quality/risk`, or both; used for docs and workflow review recovery. |

Store these logs under:

```text
Results/agent_runs/<run_id>/events.jsonl
Results/agent_runs/<run_id>/summary.md
```

Use `Docs/Workflows/agent_orchestration.md` for the full event schema and
NodeReport-style completion format.

Completed ledger rows are not proof for a new user-scoped audit unless the
task id, objective, read scope, and requested pass count match. If the user
requests a fresh three-pass audit, start a fresh audit row or explicitly mark
the previous row as prior evidence only.

For `学习+更新文档三遍` requests, the ledger must show three distinct completed
rounds. A row with only `PASS 1/PASS 2/PASS 3` notes but no per-round doc
patch checkpoints is stale evidence, not completion.

Ledger checkpoints should mention, when relevant:

```text
latest_terminal_event:
pending_approvals:
pending_tool_calls:
artifact_refs:
error_kind:
resume_command_or_next_safe_action:
```

## Stale Ledger Recovery Checklist

Use this checklist when a task was interrupted, a sub-agent disappeared, or a
fresh user request overlaps an older ledger row:

```text
1. Does the row objective match the current user request exactly?
2. Does the read scope/write scope still match the current permission boundary?
3. Is there a terminal event: completed, blocked, superseded, or run_terminal?
4. Are there pending approvals or pending tool calls?
5. Are artifact refs local paths with expected roles?
6. For three-round learn-and-update work, are rounds 1/2/3 each represented by
   round_started, round_learned, and round_doc_patched or an explicit blocker?
7. Is the next action safe without Git, network, credentials, GUI, or destructive
   cleanup?
```

If any answer is no, mark the row `paused` or `blocked`, record the missing
evidence, and resume only from the last checkpoint that has a matching
objective and safe write scope.

## Active / Recent Task Rows

| Task ID | Owner | Status | Objective | Latest checkpoint | Next action |
|---|---|---|---|---|---|
| unreal-review-camera-20260523 | Main + Aristotle(read-only review) | done | Restore manual view movement in the project-owned Unreal standalone review window and close the UE MCP/editor diagnostic loop. | 2026-05-23 21:14 CST: `Scripts/UE5/check_unreal_s0_s1_readiness.py` passed; UE log recorded `MWORKS review camera input accepted moved=1` and `moved=0 rotated=1`; `DefaultEngine.ini` has no local AndroidFileServer token section; pushed commit `dbf03cdcd fix: make Unreal review camera controllable` to `origin/main`. | If the user still cannot move the viewport, reopen via `RESTART_UNREAL_GAME=1 SCENE_ID=competition_industrial_hybrid_manual_review MAP_ID=competition_industrial_hybrid bash Scripts/UE5/review_unreal_s0_s1_renderer.sh`, click the game viewport once, then test W/A/S/D, Q/E, arrow keys, and RMB drag. Do not use the old `-log` game launch path. |
| unreal-s0s1-completion-audit-20260523 | Main + Erdos(read-only review) | source-ready-editor-mcp-blocked | Audit active goal completion without relying on chat memory. Requirements: stable S0/S1 scene/profile/proxy/packet/C++ contracts, MCP/Editor diagnostic path, targeted checks, documentation, and recoverable task records. | Erdos verified source/data contracts, docs, targeted checks, and task records. Main agent reran `python3 Scripts/UE5/check_unreal_s0_s1_readiness.py --build`: pass. Main agent reran `python3 Scripts/UE5/probe_unreal_mcp_listener.py --timeout 1`: fail, `172.17.48.1:55557` timeout and `127.0.0.1:55557` refused. `Scripts/UE5/check_unreal_s0_s1_readiness.py` now also requires every S1 visible render-map instance to carry `source.collision_proxy_id`. | Keep active goal open. Before claiming completion, open the project-owned UE editor with UnrealMCP listening, rerun `python3 Scripts/UE5/check_unreal_s0_s1_readiness.py --build --check-listener`, and run one read-only actor probe such as `unreal_engine.get_actors_in_level`. Standalone `-game` review may continue without the editor listener. |
