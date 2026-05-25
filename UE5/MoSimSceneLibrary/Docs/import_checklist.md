# MoSimSceneLibrary Import Checklist

Use this checklist after manually adding Fab / Marketplace content.

## Before Import

- Open `MoSimSceneLibrary.uproject` with a compatible Unreal version.
- Prefer UE 5.5 assets first.
- Keep large imported assets local; they are ignored by Git.

## Per Scene

Record:

- Asset name
- Import action used: `Create Project` or `Add To Project`
- Unreal version
- Imported content root under `Content/`
- Primary `.umap` path
- Required plugins
- Whether the map opens in Editor
- Whether collision exists on major obstacles
- Whether the scene is suitable for drone navigation

## After Import

From repository root:

```bash
python3 Scripts/UE5/audit_scene_source.py --maps
python3 Scripts/UE5/plan_scene_truth_export.py --query <scene-name>
```

If the map is accepted, export scene truth and update the scene-source registry.
