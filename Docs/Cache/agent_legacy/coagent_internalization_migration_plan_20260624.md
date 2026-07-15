# CoAgent Internalization Migration Plan 2026-06-24

> Cache/review plan for retiring the `CoAgent/` top-level tree after useful
> MoSim-specific material has been moved into project-owned locations. This is
> not a runtime workflow.

## Goal

Move useful CoAgent material into normal MoSim project paths so future agents
can work from `AGENTS.md`, `Docs/`, `Scripts/`, `Config/`, `Results/`, and
`References/` without loading `CoAgent/` as a parallel architecture.

Do not delete `CoAgent/` until:

1. all active project references point to MoSim-owned paths;
2. native hook configuration no longer depends on `CoAgent/hooks`;
3. checker/tests/protocol references are migrated or retired;
4. a path-limited dependency scan is clean;
5. the user approves final deletion/archive.

## Target Layout

| Source Class | New MoSim Location | Status |
|---|---|---|
| Current project workflows | `Docs/Workflows/` | active only; no legacy dispatch bodies |
| Review/cache/migration plans | `Docs/Cache/` | active cache area |
| Archived legacy workflow bodies | `Docs/Cache/agent_legacy/legacy_workflows_20260624/` | migrated |
| Desktop window skills | `Docs/Skills/Desktop/` | migrated first pass |
| MWORKS/UE/Sunray domain skills | `Docs/Skills/` | already project-owned |
| External-agent research summaries | `Docs/Cache/research/` or `Docs/Index/external_learning_index.md` | selective extraction started |
| Hook implementation | `Scripts/hooks/` | migrated; global hook config updated |
| Hook tests | `Scripts/tests/` | migrated for preflight smoke |
| Protocol schemas/templates still useful for MoSim packets | `Config/protocol/` plus `Scripts/quality/` | migrated first pass |
| Capability cards/index | `Config/capabilities/` and `Docs/Index/capability_index.md` | migrated first pass |
| Legacy visible-thread registry snapshot | `Config/legacy/department_threads.json` | migrated as historical snapshot |
| Runtime/transport/visible-thread code | archive or delete | likely obsolete unless a current dependency exists |
| Historical CoAgent tasks/status/decisions | `Docs/Cache/coagent_history/` | pending archive, not startup context |

## Already Completed

- Moved large legacy workflow bodies from `Docs/Workflows/` to
  `Docs/Cache/agent_legacy/legacy_workflows_20260624/`.
- Left short redirect stubs in `Docs/Workflows/` for old references.
- Moved desktop window skills into:
  - `Docs/Skills/Desktop/window-capture-evidence/SKILL.md`
  - `Docs/Skills/Desktop/window-ui-action-control/SKILL.md`
- Updated current project indexes/entry docs to use the new desktop skill
  paths.
- Copied protocol schemas/templates and the old packet communication contract
  into `Config/protocol/`.
- Copied machine capability index into `Config/capabilities/`.
- Copied the old visible-thread registry snapshot into
  `Config/legacy/department_threads.json` for historical reference only.
- Updated capability checkers/tests to use `Config/protocol` and
  `Config/capabilities` as their current paths.
- Copied the reference project index to `Docs/Index/reference_project_index.md`
  and updated `Scripts/reference/check_reference_index.py`.
- Copied/simplified external agent learning strategy to
  `Docs/Index/agent_learning_strategy.md`.
- Migrated native hook implementation to `Scripts/hooks/` and updated
  `C:\Users\HP\.codex\hooks.json` to call
  `Scripts\hooks\codex_native_hook.py`.
- Replaced the old long tooling governance body with a short current workflow
  at `Docs/Workflows/tooling_assets_governance.md`; archived the old body at
  `Docs/Cache/agent_legacy/tooling_assets_governance_legacy_20260624.md`.
- Validated:
  - `python Scripts\tests\test_capability_resolution.py`
  - `python Scripts\quality\check_capability_index.py`
  - `python Scripts\quality\check_capability_resolution.py Config\protocol\templates\visible_thread_dispatch_packet.json --strict`
  - `python Scripts\tests\test_preflight_policy.py`
  - `python Scripts\reference\check_reference_index.py --strict`
  - `python Scripts\hooks\preflight.py --json --write-path Results/tmp/hook_probe.txt --command "Write-Output ok"`

## Next Migration Batches

### Batch 1: Active Reference Cleanup

Update active project docs so they do not point at `CoAgent/docs/**` or
`CoAgent/dispatch/**` as current sources of truth. Keep old references only in
cache/history sections.

Status: mostly complete for startup docs, hook/protocol/capability/reference
indexes, and tooling governance. Remaining visible references are legacy or
require a separate runtime/gateway dependency decision.

Priority files:

```text
Docs/Workflows/tooling_assets_governance.md
Docs/Index/capability_index.md
Docs/Index/external_learning_index.md
Docs/Index/project_work_memory_index.md
Docs/Index/codex_app_session_research.md
Docs/Index/api_index.md
Scripts/quality/*.py
Scripts/tests/*.py
```

### Batch 2: Hooks And Guardrails

Status: completed for the active entrypoint.

Current active path:

```text
Scripts/hooks/codex_native_hook.py
Scripts/hooks/preflight.py
Scripts/tests/test_preflight_policy.py
C:\Users\HP\.codex\hooks.json
```

The old `CoAgent/hooks/*` copies are not deleted yet; they are legacy fallback
until a final deletion/archive pass.

### Batch 3: Protocol / Capability Material

Separate current MoSim needs from abandoned visible-thread dispatch:

- keep generic safety/evidence schemas only if they are still used by scripts;
- retire visible-thread dispatch tickets, R1/R2/R3, dispatch SLO, and
  department registry material unless a current checker imports them;
- move retained templates under project-owned config/template paths.

Status: first-pass copies now live in `Config/protocol/`,
`Config/capabilities/`, and `Config/legacy/`. Human docs now mark
visible-thread dispatch as legacy/reference in normal startup.

### Batch 4: Research And History

Do not bulk-promote CoAgent research into active docs. Extract only concise
lessons that improve current single-thread MoSim work:

- document placement and context hygiene;
- capability/tool selection;
- when to add logs/checkpoints;
- when to search official docs or ask the user;
- how to avoid substitute runtimes and unsupported evidence claims.

Everything else becomes cache/history.

## Final Deletion Gate

`CoAgent/` can be deleted or archived only after this command class is clean
for active paths:

```text
rg -n "CoAgent[/\\]" AGENTS.md Docs Scripts Config .codex .agents
```

Expected remaining matches before deletion should be limited to historical
cache files or explicit migration notes.
