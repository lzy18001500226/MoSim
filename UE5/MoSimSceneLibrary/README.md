# MoSimSceneLibrary

This Unreal project is the local scene library and runtime renderer shell for
MoSim.

Purpose:

- Receive maps from Epic Launcher / Fab through manual **Create Project** or
  **Add To Project** actions.
- Keep imported Marketplace content out of Git by default.
- Host the project-owned runtime renderer that consumes MWORKS playback through
  the `UE5/Bridge` plugin.
- Provide a stable project path for later MoSim scripts to inspect `.uproject`,
  `.umap`, `.uasset`, collision data, and scene truth.

Recommended manual import order:

1. `Factory Environment Collection`
2. `City Park Environment Collection`
3. `Electric Dreams Env`
4. `Derelict Corridor Megascans Sample`
5. `Dark Ruins Megascans Sample`
6. `Old Mine`
7. `Rain Forest`
8. `Landscape Mountains`

Repository policy:

- Track this project shell, config, and documentation.
- Do not commit imported `Content/` or project-local `Plugins/` assets unless a
  reviewed asset-batch task explicitly changes `.gitignore`.
- After importing a scene, run the MoSim UE audit scripts from the repository
  root to rank maps and export planning truth.

Expected path:

```text
C:\Users\HP\Desktop\MoSim\UE5\MoSimSceneLibrary\MoSimSceneLibrary.uproject
```
