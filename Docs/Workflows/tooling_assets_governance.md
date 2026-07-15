# Tooling Assets Governance

> Current MoSim workflow for tools, skills, hooks, MCP wrappers, plugins,
> reference indexes, and capability routing. The legacy long body was
> archived at `Docs/Cache/agent_legacy/tooling_assets_governance_legacy_20260624.md`.

Status: single-thread project workflow, 2026-06-24 CST.

## 1. Scope

Use this workflow when a task changes or relies on:

| Asset | Current Location |
|---|---|
| Native hooks | `Scripts/hooks/`, configured by `C:\Users\HP\.codex\hooks.json` |
| Capability index | `Docs/Index/capability_index.md`, `Config/capabilities/capability_index.json` |
| Experiment profiles and run contracts | `Config/profiles/` |
| Legacy/design protocol and templates | `Config/protocol/` |
| Legacy thread registry snapshot | `Config/legacy/department_threads.json` |
| Project skills | `Docs/Skills/` |
| MCP/tool docs | `Docs/Index/api_index.md`, task-specific skill/workflow |
| External reference index | `Docs/Index/reference_project_index.md`, `Docs/Index/external_learning_index.md` |
| Deterministic checks | `Scripts/quality/`, `Scripts/tests/` |

Do not put active tool rules back into retired agent-OS internals. If old
material is needed, copy the useful current rule into a MoSim-owned path and
leave the old file as cache/reference.

## 2. Placement Rules

| Content | Put It In |
|---|---|
| executable guardrail | `Scripts/hooks/` or `Scripts/quality/` with tests |
| repeatable human/agent procedure | `Docs/Workflows/` |
| task-family procedural knowledge | `Docs/Skills/<family>/` |
| current machine-readable route/config/template | `Config/profiles/`, `Config/capabilities/`, or task-specific `Config/` paths |
| legacy/design protocol template | `Config/protocol/` |
| one-off migration note or old long body | `Docs/Cache/` |
| generated evidence, manifests, logs, packets | `Results/` |

Indexes point to owners. They do not grant permission by themselves.

Skill indexing must prefer project-owned skill entry points. Do not raw-scan
vendored or generated trees such as `.venv`, `node_modules`, plugin caches, or
external tool catalogs under `Docs/Skills/` as if every nested `SKILL.md` were a
MoSim-owned skill. If a vendored skill is useful, promote only a short
project-owned wrapper or index row that names the exact upstream path and
current use boundary.

## 3. Native Hook Workflow

1. Edit `Scripts/hooks/preflight.py` or `Scripts/hooks/codex_native_hook.py`.
2. Update `Scripts/hooks/README.md` when behavior or smoke commands change.
3. Run:

```powershell
python Scripts\tests\test_preflight_policy.py
python Scripts\hooks\preflight.py --json --write-path Results/tmp/hook_probe.txt --command "Write-Output ok"
```

4. Only after the new path passes, update `C:\Users\HP\.codex\hooks.json`.
5. Re-run the smoke test.

Hook policy must remain mechanical: block outside-project writes, destructive
commands, broad Git, real sensitive paths, oversized file candidates, and
known Git/runtime-output hazards. Do not use hooks to load large context or
auto-continue turns.

## 4. Capability Workflow

When adding or changing a capability:

1. Update the human row in `Docs/Index/capability_index.md`.
2. Update the machine row in `Config/capabilities/capability_index.json`.
3. If explicitly reopened legacy/design task packets use the capability,
   update `Config/protocol/` templates. Do not update legacy packet templates
   for ordinary single-thread work.
4. Run:

```powershell
python Scripts\quality\check_capability_index.py
python Scripts\quality\check_capability_resolution.py Config\protocol\templates\capability_resolution.json
```

Legacy visible-thread packet checks are only for historical packet repair or an
explicitly reopened visible-thread route:

```powershell
python Scripts\quality\check_capability_resolution.py Config\protocol\templates\visible_thread_dispatch_packet.json --strict
python Scripts\quality\check_agent_task_native_surface_gate.py Config\protocol\templates\visible_thread_dispatch_packet.json --strict
```

## 5. MCP And Plugin Rule

Use native/plugin/MCP surfaces when they already exist. Do not hand-roll a
local substitute before checking:

```text
Docs/Index/api_index.md
Docs/Index/capability_index.md
task-specific Docs/Skills/*/SKILL.md
```

If an API/tool behavior is unclear, inspect official/local docs or run a small
read-only probe before writing workflow rules.

## 6. External Reference Rule

Before broad web research or raw tree scanning, check:

```text
Docs/Index/reference_project_index.md
Docs/Index/external_learning_index.md
Docs/Index/agent_project_classification.md
```

External projects are reference material. Do not import runtime frameworks,
provider configs, credentials, or large tool products into active MoSim
without explicit user approval.

## 7. Completion Check

A tooling/governance edit is complete only when:

- the active entry docs still stay compact;
- owner paths point to `Docs/`, `Config/`, `Scripts/`, or `Results/`;
- old legacy paths are either cache/reference or removed from active indexes;
- relevant tests/checkers pass;
- no runtime engineering success is claimed from documentation or hook changes.
