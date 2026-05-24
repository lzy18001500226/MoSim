---
name: mosim-epic-fab-library
description: Use when selecting or inspecting Epic/Fab/Launcher scene assets for MoSim, checking owned vs cached assets, or using the mosim_epic_library MCP. This skill is only for Epic/Fab library inventory and scene-source selection; it does not edit Unreal projects or download assets.
---

# MoSim Epic/Fab Library

Use this skill when the task is to see what Epic/Fab assets are available for
MoSim scene work or decide whether the Fab route can produce editable,
truth-backed simulator scenes.

## Scope

Allowed:

- read sanitized local Epic Launcher/Fab inventory;
- list owned account-library entries, cached Fab assets, and old VaultCache
  `.uproject` projects;
- choose candidate scenes for manual review.
- reject Fab/cache assets that cannot be imported into editable UE content or
  cannot support planning-truth generation.

Not allowed:

- dump raw Launcher logs, webcache, OAuth URLs, tokens, or account cache blobs;
- launch downloads or write outside the project unless the user explicitly asks;
- treat account-owned assets as editable until they are locally created or cached.

## Commands

Health check:

```bash
uv run python Scripts/UE5/check_epic_library_inventory.py
```

Merged human-readable scene view:

```bash
uv run python Scripts/UE5/epic_library_view.py
uv run python Scripts/UE5/epic_library_view.py --query Factory
```

Scene-source audit:

```bash
uv run python Scripts/UE5/audit_scene_source.py
uv run python Scripts/UE5/plan_scene_truth_export.py --query Derelict
uv run python Scripts/UE5/run_scene_truth_export.py --query Derelict --map-package /Game/DerelictCorridor/Maps/DerelictCorridor
```

`run_scene_truth_export.py` defaults to dry-run command generation. Add `--run`
only after the target project, engine version, plugins, and map package have
been checked.

Validate exported scene truth:

```bash
uv run python Scripts/UE5/export_unreal_scene_truth.py validate <truth-json>
uv run python Scripts/UE5/audit_scene_source.py
```

Current validated local scene: `DerelictCorridorMegascans`. Its UE 5.5
commandlet export writes
`UE5/MworksUnrealRenderer/Content/MworksData/scene_truth/derelictcorridormegascans_collision_truth.json`
with 4753 collision proxies, and `audit_scene_source.py` marks it
`ready_for_truth_backed_planning`. This is AABB collision-proxy truth, not final
semantic or voxel occupancy truth.

Raw sanitized inventory:

```bash
uv run python Scripts/UE5/epic_library_index.py --compact
```

MCP wrapper:

```bash
Scripts/UE5/mosim_epic_library_mcp_wsl_wrapper.sh
```

## Interpreting States

| State | Meaning |
|---|---|
| `account_owned` | Visible in the account cache, may not be installed locally |
| `fab_cached` | Present in FabLibrary cache |
| `vault_cached_project` | Old VaultCache project with discovered `.uproject` |
| `vault_cached_asset` | Old VaultCache asset without discovered `.uproject` |

## Next Step Rule

If a promising scene is only `account_owned`, ask the user to create/add it from
Epic Launcher/Fab before trying UE Editor MCP operations. If a Fab cache only
contains a binary manifest and no editable `.uproject/.umap/.uasset`, it is not
enough for MoSim import.

A usable scene source must pass:

```text
editable Unreal content -> renderable map -> explicit/plannable truth
```

`audit_scene_source.py` only marks a scene as truth-ready when it finds explicit
truth artifacts such as occupancy/collision/semantic JSON/CSV/YAML or point
cloud files. Collision/navigation `.uasset/.umap` names are only proxy
candidates that still require export.

Use `Scripts/UE5/export_unreal_scene_truth.py export` from Unreal Editor Python
after the scene opens. The first accepted truth artifact is an AABB collision
proxy JSON under `UE5/MworksUnrealRenderer/Content/MworksData/scene_truth/`.

If Fab cannot satisfy this, switch to local editable projects under:

```text
References/UnrealScenes
```
