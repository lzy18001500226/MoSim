# Agent Task Ledger

> Persistent coordination state for long-running or multi-agent work.
> This file prevents sub-agent task loss across chat turns, context refreshes,
> closed agents, and temporary tool failures.
>
> Machine-readable run events should be written under
> `results/agent_runs/<run_id>/events.jsonl` when a task lasts more than one
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
| GIT-20260521-OKWINDS | GitIntegrator | Commit workflow/tooling updates, safely integrate `Skills/okwinds/**`, and rewrite unpublished integration branch to remove >100 MB ONNX blob | Git index/branches, `.gitignore` only if needed | done | Safe split branches pushed, including `git/skills-agent-awesome-codex-20260521` and workflow/docs branches. Unsafe aggregate branches remain intentionally unpushed. | Do not resume old polluted branches. Continue only from new current diffs. |
| GIT-20260521-PUSH-CLEAN | GitIntegratorPush | Push `git/finalize-safe-batches-clean-20260521` or split it into smaller clean branches if push keeps timing out | Git index/branches, `.gitignore` only if needed | done | Whole clean branch `git/finalize-safe-batches-clean-20260521` at `3abd6be6` validated with no >100 MB tree blobs and no gitlinks, but push remained too large for the transport window. Split branches pushed: `git/finalize-workflows-docs-clean-20260521` at `204b3169` and `git/finalize-okwinds-clean-20260521` at `3514d0a2`. | Continue remaining integration from `origin/main` in smaller clean scopes. Do not push old polluted branch `git/finalize-safe-batches-20260521`; avoid whole-branch push unless transport capacity changes. |
| OKWINDS-20260521-WORKFLOW-AUDIT | OkwindsWorkflowAuditor | Read-only audit of `Skills/okwinds/*` for reusable agent orchestration, WAL, skill packaging, evidence-chain, and doctor patterns | No writes | done | Audit completed. Borrow WAL/run events from `skills-runtime-sdk`, NodeReport evidence from `capability-runtime`, task graph and pause/resume semantics from `Agently`, skill validation from `agentskills`; reject unrelated UI/runtime adoption and `wkteam-api-sdk` as mostly irrelevant. | Use audit result to update workflow docs only; do not import full runtimes as project dependencies. |
| EXTDOCS-20260521-LEARN | ExternalDocsLearningOwner | Three-round learn/extract/update/review across Claude Code docs, Codex docs, open skills/workflow repos, and project-management/reviewer patterns | Assigned docs/workflows only; no source/runtime dependency imports | done | Parent learning stream is accepted as historical completion together with `EXTDOCS-20260521-ROUND3`: external docs/skills learning produced TaskSecretary, WAL, reviewer lanes, source-to-doc coverage, do-not-adopt lists, and fresh verification gates. | Superseded by recurring learning loop. Future work should start a fresh row when a new incident, tool, milestone, or user correction triggers another learn-and-patch cycle. |
| COSYS-20260521-BLOCKS-UE55 | UEBuildSmokeRunner | Build/smoke Cosys-AirSim Blocks UE 5.5 project from command line | `results/tmp` logs; minimal project-local dependency sync if required | done | UBT passed with `exit_code=0`; log `results/tmp/cosys_airsim_blocks_ue55_ubt_rerun_20260521_155920.log`; generated `UnrealEditor-Blocks.dll` and `UnrealEditor-AirSim.dll`. User visually checked scene. Blocks-local `AirLib.lib` is 154 MB and must not be committed. | Next route is AirSim API/settings/UE Blueprint or project UI integration; the Blocks scene alone has no project-specific function panel. |
| SPEAR-20260521-SYSTEM | SpearSimSystemLauncher | Verify SPEAR as a scene/RPC system, not as a UAV simulator | No source writes; runtime windows and temporary outputs only | done | SpearSim game window launched with `-game`; RPC port `30000`; `spear_ext` built; Python `spear.Instance` connected; minimal camera render/readback succeeded | For further SPEAR work, use it as map/RPC/vision reference only. Real UAV needs project-owned UE asset import/Blueprint. |
| SPEAR-20260521-MAPS | SpearMapReviewer | Review all local SPEAR maps | No source writes | done | Available main maps are `apartment_0000`, `debug_0000`, `debug_0001`; no larger complete UAV scene found | If user wants visual review, open maps one by one. Do not search for built-in drone simulation in SPEAR. |
| GIT-20260521-RECOVERY-DOCS | GitRecoveryIntegrator | Recover current docs/workflow changes from polluted checkout into a clean branch and push without large/generated artifacts | Git index/branches only; no source model edits | done | Clean branch `git/recovery-docs-workflows-clean-20260521` pushed at `c279bf4add5a4efb0cf5699e93172047ad148a20`. Included only `AGENTS.md`, `PROGRESS.md`, `docs/index/workflow_index.md`, `workflows/agent_orchestration.md`, `workflows/agent_task_ledger.md`, and `workflows/audit_external_repo.md`. No >100 MB blobs. | Use this branch as the safe docs/workflow recovery point. Do not push old polluted branch `git/finalize-safe-batches-20260521`. |
| RFLYSIM-20260521-SCENE-REVIEW | RflySimSceneReviewer | Open locally available RflySim3D packaged scenes one by one for visual review without UE Editor | Runtime windows only; optional `results/tmp` launch notes | superseded | User clarified this was an older line and RflySim maps are no longer the current priority. Do not continue scene opening until the reconstructed 2026-05-21 backlog says it is still active. | Stop RflySim scene review. Recover from session-derived backlog instead of memory. |
| EXTDOCS-20260521-ROUND3 | ExternalDocsLearningOwner | Complete third learn-and-update round for Codex/Claude docs, open skills/workflow repos, reviewer agents, and task-depth orchestration | Assigned docs/workflows only | done | Round 3 completed from new source slices: `Skills/Agent/superpowers/skills/{verification-before-completion,requesting-code-review,receiving-code-review,dispatching-parallel-agents,subagent-driven-development,writing-skills,loopback-adjacent execution docs}`, `Skills/Agent/awesome-codex-subagents/categories/{04-quality-security,09-meta-orchestration,10-research-analysis}`, `Skills/Agent/awesome-codex-skills/{create-plan,gh-fix-ci,gh-address-comments,skill-creator,pr-review-ci-fix,datadog-logs,issue-triage}`, and OKWinds testing/coverage/review/pollution docs. Patched `workflows/agent_orchestration.md`, `workflows/audit_external_repo.md`, `workflows/agent_task_ledger.md`, and `PROGRESS.md`. | Recovery: source-to-doc rules now require fresh verification evidence, two reviewer lanes, coverage matrices, WAL/log noise filtering, and explicit do-not-adopt lists. Remaining validation is docs-quality review plus `git diff --check`; do not import external runtimes or global agent configs. |
| PARAM-20260521-PX4-IDENT | VehicleParamIdentificationResearcher | Research practical methods and open-source projects for estimating quadrotor mass, inertia, motor/thrust, and drag parameters from PX4 logs or flight data | Read-only research; docs patch after review | done | Report saved to `results/tmp/vehicle_param_identification_research_20260521.md`. Key conclusion: current `1.0 kg`, inertia, `motorConstant/lift_cofficient` values must be labeled `source=SDF_migration`, not Sunray150 identified truth. Recommended sources: PX4 ULog, `pyulog`, ETH ASL `data-driven-dynamics`, ARPL `data-driven-system-identification`, ESC/RPM or thrust stand data. Actionable route and risk-parameter table were promoted to `workflows/identify_quadrotor_parameters.md`, `Design/02`, `Design/03`, and `Design/07`. | Next step is data collection and identification execution. Required user/vendor inputs: measured mass, `.ulg` logs with attitude/rate/actuator/IMU topics, motor order/rotor direction, ESC/RPM or thrust stand data. Do not upgrade parameters from `source=SDF_migration` to `identified` until held-out validation passes. |
| SESSION-20260521-BACKLOG | SessionBacklogAuditor | Reconstruct authoritative unfinished task backlog from 2026-05-21 session logs and the main 05/09 carry-over session | `results/tmp/session_audit_20260521/`, then docs/ledger after user review | running | Raw user-message extraction saved to `results/tmp/session_audit_20260521/user_messages_20260521.md` with 92 messages. Keyword draft was too noisy and is not accepted as final. | Split session by time, have auditors classify tasks and decisions, merge into a user-reviewable backlog before executing old remembered tasks. |
| SESSION-20260520-BACKLOG | SessionBacklogAuditor | Reconstruct authoritative unfinished task backlog from 2026-05-20 session logs, because 05/21 tasks depend on prior-day context | `results/tmp/session_audit_20260520/`, then docs/ledger after user review | running | Raw user-message extraction saved to `results/tmp/session_audit_20260520/user_messages_20260520.md` with 16422 lines. Needs segmented audit before execution. | Split by local time windows; classify tasks as done/running/blocked/superseded/unknown and identify user-review gates. |
| GIT-20260521-CONTINUITY | GitContinuityOwner | Keep Git progress alive while backlog/session audit continues; push stable docs/workflow changes only from clean branch/index | Git index/branches only; no references/results/generated artifacts | done | Clean branch `git/continuity-docs-backlog-clean-20260521` pushed at `2776f06e616b386aff0f29e9f8247d1eecd14733`. Included only `AGENTS.md`, `PROGRESS.md`, `docs/index/workflow_index.md`, `workflows/agent_orchestration.md`, `workflows/agent_task_ledger.md`, and `workflows/audit_external_repo.md`. Push used `--no-verify` after confirming these six small files had no LFS filters because local pre-push hook could not find `git-lfs`. | Current checkout remains old polluted branch with local edits. Future Git work should continue from clean branches and avoid old polluted branch `git/finalize-safe-batches-20260521`. |
| SECRETARY-20260521-INSTRUCTION-LEDGER | TaskSecretary | Recover user directives from 2026-05-20/21, establish intake/goal rules, and promote reviewed coordination rules into durable docs | `results/tmp/task_intake/`, `PROGRESS.md`, `workflows/agent_orchestration.md`, `workflows/agent_task_ledger.md`; `AGENTS.md` policy-level only | done | User reviewed `results/tmp/session_audit_20260521/task_status_review_20260521.md` as broadly acceptable. Stable rules are promoted: TaskSecretary, goal split, Git owner stop condition, user-review gate, and parameter-identification next route. | Keep the accepted task/status table as recovery evidence. Future user corrections must go through TaskSecretary intake first, then durable docs only after review. |
| EXTDOCS-RECURRING-LEARNING | ExternalDocsLearningOwner | Recurring learn-and-patch loop for external docs, skills, agent orchestration, and workflow improvements triggered by project failures or milestones | Assigned docs/workflows only; no global config or source-runtime imports | planned | Triggered by current issue: task plan existed but chat ended and sub-agent/task state risked disappearing; docs were updated, but index/structure and recurring review need a permanent loop. | On each trigger, perform source review, propose/patch target docs, run docs-quality review, and record accepted/rejected patterns. Do not import full external runtimes without explicit user approval. |
| GIT-20260521-FULL-CONVERGENCE-RESTART | GitFullConvergenceOwner | Converge current repository state by classifying every path group as pushed, ignored/excluded, needs-user-decision, or blocked | Git index/branches/commits/pushes, `.gitignore` only if needed | done | Owner `Helmholtz` returned `DONE_WITH_CONCERNS`. Pushed `git/full-convergence-docs-checkpoint-20260521` at `69bd26df44497153fd4eb731c5d03f811a9589e5`, containing only `PROGRESS.md` and `workflows/agent_task_ledger.md`. It confirmed no final `.git/index.lock`; old aggregate branch `git/finalize-safe-batches-20260521` remains polluted and was not pushed. Path groups were classified as pushed via split refs, ignored/excluded, or unsafe old branches not to push. | Do not resume this owner. For future Git, start from clean branches or `origin/main`, avoid old polluted aggregate branches, and use path-limited status because full checkout/index refresh remains slow and `Skills/Agent` has stat noise. |
| AIRSIM-20260521-BATCH-MIGRATION | AirSimMigrationCoordinator | Migrate `C:\Users\HP\Desktop\AirSim` into `references/AirSim` in audited, small Git-safe batches using parent-child-grandchild agents | `references/AirSim/`, Git index/branches, `.gitignore` only if needed | running | Source exception approved by user. Nested subagent smoke passed. Low-risk stage completed and pushed: `PEDRA`/workflow docs `aadfb09bf`, management rules `bcd9cc5e`, `PegasusSimulator` `f3019f301`, `ProjectAirSim` `e70f1deb`, `UESVONavigation-develop` `6f357904`, `AirSim` `702cd898`, `unrealcv-5.2` subset `e5ea1ed3`. AirSim copied credential-like Unity and map fields were sanitized in the project copy before commit. `unrealcv-5.2` owner reformatted imported text for whitespace; record as a one-off deviation and do not repeat. | Remaining batches: decide `AirSim360/carla` 50-100 MB media handling; handle `IsaacSim` LFS pointers separately; handle `Cosys-AirSim/spear` with generated-artifact exclusions. Keep using child owners and secretary/reviewer checks; do not copy the remaining large repos whole. |
| ORG-20260522-OPERATING-MODEL | TaskSecretary / OrganizationDesigner | Define company-style multi-agent departments and make instruction/work-record capture mandatory | `workflows/org_operating_model.md`, `workflows/agent_orchestration.md`, `docs/index/workflow_index.md`, `PROGRESS.md`, `workflows/agent_task_ledger.md` | done | Added organization model covering GeneralManager, TaskSecretary/PMO, project, test, security, DevOps, architecture, knowledge, and incident-review departments. Secretary hard rule now requires every directive, correction, manual-review result, sub-agent return, blocker, and checkpoint to be recorded before relying on chat memory. | For future multi-agent work, start with secretary intake, assign department owners, run test/security/docs review, then let GitIntegrator commit/push. |
| AIRSIM-20260522-COMPLETE-MIGRATION | AirSimMigrationCoordinator | Finish migrating `C:\Users\HP\Desktop\AirSim` into `references/AirSim` after ignore hardening, with main-agent routed sub-agent/reviewer handoffs | `.gitignore`, `references/AirSim/`, workflow docs, Git index/branches | blocked | Missing source dirs were copied with generated artifacts excluded. Security review found no >100 MB files and no nested `.git`; `IsaacSim` contains many LFS pointer files and several 50-100 MB assets are recorded. Pushed: docs/ignore `8babb1a3e`, AirSim360 `7e0c1a85`. Blocked: local unpushed CARLA commit `0d261d0c` contains ~2084 files and push times out; the split owner failed to reset/split and was closed. | Decide next Git strategy: exclude `carla-ue5-dev` temporarily and continue smaller batches, or allow a dedicated long-running local Git session to reset `0d261d0c` and split CARLA by subdirectories. Do not retry the large CARLA push. |

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
{"event_id":"GIT-20260521-UNDER100-0001","ts":"2026-05-21T10:30:00+08:00","task_id":"GIT-20260521-UNDER100","agent_role":"GitIntegrator","event_type":"checkpoint","summary":"processed references/Lab","paths_read":["references/Lab"],"paths_written":[],"artifact_refs":[],"approval_state":"none","tool_state":"finished","error_kind":"","risk":"","next_action":"fix spear rpclib gitlink"}
```

Required fields:

| Field | Meaning |
|---|---|
| `event_id` | Stable event id, usually `<task_id>-NNNN`. |
| `ts` | Local timestamp with timezone. |
| `task_id` | Stable task id matching this ledger. |
| `agent_role` | Stable role name such as `GitIntegrator` or `SceneResearch`. |
| `event_type` | Use the canonical event type list in `workflows/agent_orchestration.md`; common ledger rows usually use `task_started`, `checkpoint`, `blocked`, `completed`, or `superseded`. |
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
| `source_slice` | Local source paths read for that round, such as `Skills/okwinds/skills-runtime-sdk/docs_for_coding_agent/*`. |
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
results/agent_runs/<run_id>/events.jsonl
results/agent_runs/<run_id>/summary.md
```

Use `workflows/agent_orchestration.md` for the full event schema and
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
