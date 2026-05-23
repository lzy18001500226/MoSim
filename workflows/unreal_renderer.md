# Unreal Renderer Workflow

Unreal is a render-only layer. MWORKS/Sysplorer remains the simulation source
of truth for dynamics, control, planning, collision checks, and metrics.

## Asset-First Rendering Policy

Do not build the final Unreal scene by hand from low-poly boxes unless the goal
is a short collision/debug smoke test. The renderer must be asset-first:

```text
existing scene/model assets
  -> asset registry
  -> Unreal placement/material/collision proxy
  -> MWORKS state playback
  -> video review
```

MWORKS remains the truth source. Unreal is allowed to improve scene quality,
materials, camera, radar visualization, trail rendering, and video export. It is
not allowed to change controller output, planner truth, collision metrics, or
event logs.

Current asset-source priority:

| Priority | Source | Use |
| --- | --- | --- |
| P0 | `references/Sunray/simulation/sunray_simulator/models` | Immediate reusable Gazebo/SDF assets: Sunray150/Mid360, houses, trees, windows, gates, targets, terrain, AWS RoboMaker residential/retail assets |
| P0 | `references/Sunray/simulation/sunray_simulator/worlds/*.world` and `references/Sunray/simulation/sysu_competition/worlds/*.world` | Existing scene layout references such as competition maps, planning tests, houses, airport, outdoor, sand island |
| P1 | RflySim3D / RflySimUE installer or asset package, if available locally | UE-style scenario、camera、UDP/shared-memory、Mid360 and scene-layout reference only. Treat packaged maps as black-box runtime references unless editable source project, license, and collision/object-truth export are explicitly provided |
| P1 | RflySim public GitHub repos | Interface/modeling reference, not primary visual assets. `CopterSim` is mainly Simulink multicopter/HIL model; `RflyExpCode` is experiment code |
| P1 | `references/AirSim/Cosys-AirSim/Unreal/Environments/Blocks/Blocks.uproject` | Modern UE Blocks scene candidate with AirSim/Cosys assets; first smoke target for UE scene reuse |
| P2 | `references/AirSim/AirSim/Unreal/Environments/Blocks/Blocks.uproject` | Legacy UE4.27 AirSim Blocks scene and quadrotor visual/API reference |
| P2 | `references/AirSim/PegasusSimulator` | Isaac/Omniverse USD UAV scene reference; not direct UE asset source |
| P2 | UE Marketplace / open UE environment assets | Optional visual upgrade after license and file-size checks |

Important finding: the public RflySim GitHub repositories inspected so far do
not contain a complete UE scene asset project. They are still useful for MBD,
MAVLink/HIL, fault-injection, and UDP/display interface ideas. `CopterSim` is a
Simulink multicopter model with MAVLink/PX4/HIL/fault-injection ports; it is not
a render scene repository. `RflyExpCode` is course/experiment code and also is
not a UE environment asset repository. For final visual quality, use the local
Sunray/AWS assets first, or inspect the user's local RflySim3D/RflySimUE install
as a runtime/reference source. Do not make the final renderer depend on running
RflySim3D, and do not describe RflySim packaged maps as directly reusable
editable assets unless vendor/source evidence changes that status.

Open-source simulator scene audit update:

| Source | Local scene evidence | Decision |
| --- | --- | --- |
| Cosys-AirSim | `Unreal/Environments/Blocks/Blocks.uproject`, `Content/FlyingCPP/Maps/FlyingExampleMap.umap`, AirSim plugin asset map | First UE smoke candidate. Project says UE 5.4 while docs mention UE 5.5 support; test in UE 5.x before migration. |
| AirSim | `Unreal/Environments/Blocks/Blocks.uproject`, `Content/FlyingCPP/Maps/FlyingExampleMap.umap`, Unity demo scenes | Backup/reference candidate. Requires UE 4.27 for lowest-risk open; useful for vehicle/API concepts. |
| PegasusSimulator | USD worlds such as `Box`, `BoxWithCylinders`, `Lisbon`, plus `Iris`/`Pegasus` UAV USD assets | Strong UAV sim reference for Isaac/Omniverse branch, not direct UE renderer asset source. |
| IsaacSim | Full Isaac Sim source/test tree, not a focused UAV map pack | Do not start here for maps. Use only if the project opens a dedicated Isaac Sim route. |

2026-05-22 manual-open audit:

| Candidate | Open result | Practical conclusion |
| --- | --- | --- |
| `references/AirSim/AirSim/Unreal/Environments/Blocks/Blocks.uproject` | Opens in UE 4.27 standalone/game mode after root `build.cmd --no-full-poly-car` and project plugin rebuild. `Drone1` appears in `FlyingExampleMap`. | Directly runnable baseline. Visually simple, but useful for AirSim vehicle/API/camera smoke testing. Use `settings_quadrotor_manual.json` to force `Multirotor` and avoid the missing SUV/car path. |
| `references/AirSim/Cosys-AirSim/Unreal/Environments/Blocks/Blocks.uproject` | UE 5.5 standalone/game mode now opens `FlyingExampleMap` after generating the missing dependency libraries and forcing `SimMode=Multirotor` through `settings_quadrotor_manual.json`. Log shows `Game class is 'AirSimGameMode'` and `Drone1`. | Directly reviewable as the maintained AirSim/Cosys smoke scene. Keep generated `.lib/.dll/.obj/.pdb` local and ignored. Use the checked-in settings file to avoid the Car/SUV selection path. |
| `references/AirSim/spear/cpp/unreal_projects/SpearSim/SpearSim.uproject` | UE 5.5 exits with `Plugin 'SpCore' failed to load because module 'SpCore' could not be found`. Maps present under `Content/SPEAR/Scenes/`: `apartment_0000`, `debug_0000`, `debug_0001`. | Promising indoor-scene/reference project, but blocked by the full SPEAR build/install chain. Not a UAV simulator by itself. |
| `references/AirSim/spear/cpp/unreal_projects/DefaultProject/DefaultProject.uproject` | Opens in UE 5.5 standalone/game mode, but loads the default UE `OpenWorld` template. | Confirms UE 5.5 works; no target UAV or rich SPEAR scene value by itself. |
| `references/AirSim/carla-ue5-dev/Unreal/CarlaUnreal/CarlaUnreal.uproject` | UE 5.5 stops at `Missing CarlaUnreal Modules`; logs show `CarlaUnreal`, `CarlaDeviceProfileSelector`, `Carla`, `CarlaTools`, and `CarlaExporter` incompatible/missing. The rebuild attempt also cannot resolve `dotnet`. Four `.umap` map-generator assets exist. | Useful city/map architecture reference only until the full CARLA build route is completed in a configured UE5 build shell. It is not a quadrotor runtime. |

Do not say a map source is usable as a runtime until its matching project opens
without module errors. For manual visual review, prefer standalone/game windows
over the UE editor viewport. Editor-only opening is useful only for asset
inspection.

2026-05-22 AirSim / Cosys local build diagnosis:

| Item | Finding | Action |
| --- | --- | --- |
| Original AirSim Blocks plugin | `update_from_git.bat` successfully copied `Plugins/AirSim` into `references/AirSim/AirSim/Unreal/Environments/Blocks` | The missing-plugin issue is fixed locally. Do not rerun `update_from_git.bat` through its registry-based `GenerateProjectFiles.bat` unless the Unreal project-file association is repaired. |
| Original AirSim project files | `GenerateProjectFiles.bat` failed because `HKEY_CLASSES_ROOT\Unreal.ProjectFile\shell\rungenproj` is missing | Bypass the registry association and call UE directly: `D:\Program Files\Epic Games\UE_4.27\Engine\Binaries\DotNET\UnrealBuildTool.exe -projectfiles -project=C:\Users\HP\Desktop\Quadrotor\references\AirSim\AirSim\Unreal\Environments\Blocks\Blocks.uproject -game -rocket -progress`. |
| Original AirSim compile | UE4.27 finds VS2022 and Windows SDK. After AirSim root dependency build, `UE4Editor-AirSim.dll` rebuilds successfully under `Unreal/Environments/Blocks/Plugins/AirSim/Binaries/Win64`. | Use this as the first local standalone AirSim smoke scene. If the DLL is deleted or stale, run direct UBT against `Blocks.uproject`. |
| AirSim manual camera patch | Project-local patch adds right-mouse manual look and reduces keyboard rotation step to 0.1x in both root plugin source and Blocks' copied plugin source. `DefaultInput.ini` captures mouse during mouse-down. | In the running window, use `M` for manual view, hold right mouse to look around, arrow keys/PageUp/PageDown for translation, and W/A/S/D/Q/E for fine rotation. |
| Dotnet availability | UE5.5 has bundled `.NET 8`, but the GUI-spawned Build.bat sessions for Cosys/CARLA can still log `dotnet` as not resolvable. Direct `dotnet.exe UnrealBuildTool.dll ...` bypasses that PATH issue. | Rebuild UE5 C++ projects from a configured VS Developer shell or call UBT with UE's bundled dotnet explicitly. Do not assume a normal GUI rebuild prompt is using the same PATH as the user's shell. |
| VS2022 toolchain | UE4.27 UBT detects `D:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207` and Windows SDK `10.0.26100.0` | VS/C++ toolchain exists. If Cosys-AirSim still fails after dotnet PATH repair, treat the next error as source/API compatibility rather than missing VS. |
| Cosys-AirSim Blocks | Project has `Plugins/AirSim`. Direct UBT first failed on missing `MavLinkCom.lib`, then `AirLib.lib`, then `rpc.lib`; all were generated locally and synced into the Blocks plugin copy. UE5.5 direct UBT now produces `UnrealEditor-Blocks.dll` and `UnrealEditor-AirSim.dll`. | Use explicit dependency build commands instead of the GUI rebuild dialog. Keep generated libraries and Unreal binaries ignored; commit only small settings/docs/source changes. |
| SPEAR `SpCore` | `SpCore` source is present under `references/AirSim/spear/cpp/unreal_plugins/SpCore`; it is not a separate module to download | Build SPEAR with its documented Python/CMake/UE5.5 flow before opening `SpearSim.uproject`. |
| CARLA UE5 | Map-generator `.umap` files exist, but the project stops at missing/incompatible CARLA modules in UE5.5, with the same GUI Build.bat `dotnet` PATH failure. | Use as city/map architecture reference until a full CARLA build is justified in a configured shell. |

SPEAR build caveat:

The local SPEAR tree is partially prepared but not ready to open `SpearSim` as
a game window. The official `docs/getting_started.md` flow requires:

```text
pip install -e python
python tools/build_third_party_libs.py
python tools/install_python_extension.py
python tools/copy_engine_content.py --unreal-engine-dir D:\Program Files\Epic Games\UE_5.5
python tools/run_uat.py --unreal-engine-dir D:\Program Files\Epic Games\UE_5.5 -build
```

Current local state:

- `third_party/BUILD/build_third_party_worker.log` shows an earlier build
  attempt failed before third-party compilation because `yacs` was not installed
  in the active Python environment.
- `python_ext/BUILD/cp311-cp311-win_amd64/Release/spear_ext.cp311-win_amd64.pyd`
  exists, so part of the Python extension build has already run.
- The root `tools/` directory is currently empty even though the documentation
  references `tools/build_third_party_libs.py`, `tools/install_python_extension.py`,
  `tools/copy_engine_content.py`, and `tools/run_uat.py`. Do not keep pressing
  Unreal's rebuild dialog until the matching SPEAR tool scripts or a known-good
  upstream checkout are restored.

Recommended lowest-risk sequence:

```text
1. Keep original AirSim Blocks as the current runnable AirSim baseline.
2. Use AirSim/Cosys/ProjectAirSim for vehicle, camera, sensor, API, and frame
   schema ideas; do not expect their bundled Blocks maps to be final visuals.
3. Build SPEAR `SpCore` only if indoor scene review becomes a priority.
4. Build CARLA only if city/road assets become a priority.
5. Keep Pegasus/IsaacSim on the Omniverse branch; do not try to open them as
   UE projects.
```

### Cosys-AirSim Blocks Local Open Procedure

Cosys-AirSim Blocks is now a runnable UE5.5 review scene on this machine.
Do not use the Unreal GUI rebuild dialog as the primary repair path; it can hide
the real linker error and may use a different `PATH` than the shell.

Dependency build sequence used successfully:

```text
1. Build rpclib with explicit CMake/MSBuild:
   D:\Program Files\Dev\CMake\bin\cmake.exe -G "Visual Studio 17 2022" ..
   MSBuild build\rpc.vcxproj /p:Platform=x64 /p:Configuration=Release

2. Copy `rpc.lib` to:
   AirLib/deps/rpclib/lib/x64/Release/rpc.lib
   Unreal/Plugins/AirSim/Source/AirLib/deps/rpclib/lib/x64/Release/rpc.lib
   Unreal/Environments/Blocks/Plugins/AirSim/Source/AirLib/deps/rpclib/lib/x64/Release/rpc.lib

3. Build MavLinkCom:
   MSBuild MavLinkCom/MavLinkCom.sln /p:Platform=x64 /p:Configuration=Release

4. Copy `MavLinkCom.lib` to the same three dependency layers under
   `deps/MavLinkCom/lib/x64/Release/`.

5. Build AirLib:
   MSBuild AirSim.sln /p:Platform=x64 /p:Configuration=Release

6. Copy `AirLib.lib` to:
   Unreal/Plugins/AirSim/Source/AirLib/lib/x64/Release/AirLib.lib
   Unreal/Environments/Blocks/Plugins/AirSim/Source/AirLib/lib/x64/Release/AirLib.lib

7. Build the UE project with UE5.5 bundled dotnet/UBT:
   D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\ThirdParty\DotNet\8.0.300\win-x64\dotnet.exe
   D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll
   BlocksEditor Win64 Development
   -Project=C:\Users\HP\Desktop\Quadrotor\references\AirSim\Cosys-AirSim\Unreal\Environments\Blocks\Blocks.uproject
```

Manual review launch:

```text
D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe
C:\Users\HP\Desktop\Quadrotor\references\AirSim\Cosys-AirSim\Unreal\Environments\Blocks\Blocks.uproject
/Game/FlyingCPP/Maps/FlyingExampleMap
-game -windowed -ResX=1280 -ResY=720
-settings=C:\Users\HP\Desktop\Quadrotor\references\AirSim\Cosys-AirSim\Unreal\Environments\Blocks\settings_quadrotor_manual.json
-log
```

`settings_quadrotor_manual.json` is intentionally small and checked in. It
forces:

```json
{
  "SettingsVersion": 2.0,
  "SimMode": "Multirotor",
  "ViewMode": "Manual",
  "Vehicles": {
    "Drone1": {
      "VehicleType": "SimpleFlight",
      "DefaultVehicleState": "Armed",
      "AutoCreate": true,
      "EnableTrace": true
    }
  }
}
```

If this file is not passed with `-settings=...`, the project may enter the
interactive Car/SUV selection flow and then fail because the optional SUV assets
were intentionally skipped.

When the user installs RflySim locally, do not immediately copy files into this
project. First audit the install directory for:

```text
RflySim3D / RflySimUE / RflySimUE5 executable or project
Content / Paks / Maps / Plugins / Source / Config directories
RflySimAPIs / Python / MATLAB / Simulink communication examples
UDP / shared-memory / JSON / binary protocol examples
license / third-party notices / redistribution restrictions
single files larger than 100 MB
```

Classify the result before importing:

| Finding | Action |
| --- | --- |
| UE project with `.uproject`, `Content/`, `.umap`, meshes, materials, plus editable `Source/` or matching plugin `Binaries/` | Candidate for direct scene reuse after license and size check |
| Cooked packaged executable only, no editable assets | Use as visual/reference target only; do not depend on direct asset import |
| API examples only | Port the UDP/shared-memory protocol ideas into `QuadrotorMworksBridge` |
| Large `.pak`, video, installer, or binary assets | Keep outside Git; document external dependency and local path |
| No license or unclear redistribution terms | Do not commit assets; use only as implementation reference |

### Local RflySim Audit: `D:\PX4PSP`

The user-installed RflySim tree at `D:\PX4PSP` is useful, but it must stay an
external dependency. Do not copy the tree into this repository and do not commit
RflySim `Content/` assets directly. Several RflySim3D files are larger than
100 MB, including built-data and texture payloads, so wholesale import is not
Git-safe.

Current decision: do not keep porting the old Sysplorer/MWORKS blocky visual
map into Unreal as the primary video route. That map was a workaround for
MWORKS GUI limits. The installed RflySim3D tree is now classified as a
runtime/reference source, not an editable UE source project and not the final
renderer runtime. Before implementing more Unreal scene work, identify which
RflySim mechanisms, layouts, model references, protocols, or authorized assets
should be recreated in the project-owned UE5 renderer:

```text
RflySim docs/API audit
  -> run native RflySim3D/CopterSim examples
  -> inspect scene/map/sensor parameter availability
  -> migrate useful assets/protocol ideas into project-owned UE5 renderer
```

The first milestone is not "copy assets". It is to answer whether RflySim can
provide stable renderer behavior, scene parameters, vehicle visual models,
Mid360/lidar data, terrain service, and path-planning examples that are better
than the current project-owned renderer. Selected assets must be re-imported or
referenced through our UE5 asset registry, collision proxies, material system,
naming rules, and scenario profiles.

Direct-use definition:

| Meaning of "direct use" | Decision | Reason |
| --- | --- | --- |
| Run or view scenes in the native RflySim3D/RflySimUE runtime | Allowed as reference/demo only | The local install contains runnable map entries and the official UDP/API surface |
| Use RflySim maps as editable UE source scenes for our own simulator | Not supported now | The available maps/assets are packaged UE binary content plus missing/incompatible project/plugin modules, not a clean editable source project |
| Use RflySim maps as planner truth or obstacle truth | Not supported now | No verified object/bounding-box/collision export contract is available for our planner |
| Use RflySim protocols and examples as design references | Allowed | UDP pose, sensor, terrain, camera, lidar, and timing ideas can inform a project-owned bridge |

Therefore the simulator architecture is:

```text
MWORKS/Syslab/Sysplorer solver and evidence
  -> project-owned bridge/API
  -> project-owned UE5 renderer and editable scene assets
  -> optional RflySim/AirSim/Cosys reference observation, not final dependency
```

RflySim is not the editable base for the new simulator unless the vendor or a
licensed source package provides all of the following:

```text
editable `.uproject`
matching source or editor binaries for required plugins/modules
redistribution/migration permission
object pose / collision / terrain export or rebuild workflow
```

`D:\PX4PSP\HowToUse.pdf` establishes the official learning route:

1. Start with chapters `1.RflySimIntro` and `2.RflySimUsage` only as platform
   orientation.
2. For this project, jump directly to:
   - `3.RflySim3DUE` for scene/model loading, RflySim3D commands, terrain
     service, collision, camera/view, and UE-style rendering behavior;
   - `6.RflySimExtCtrl` for external control, trajectory, and MAVLink/UDP
     command interfaces;
   - `8.RflySimVision` for camera, depth, lidar, Mid360, point cloud, and
     perception-control loops;
   - `10.RflySimSwarm` for multi-UAV display, networking, and formation
     references.
3. Use each chapter in the official order `Intro.pdf -> PPT.pdf -> API.pdf ->
   Index.pdf -> selected Readme.pdf`. Do not start by editing our Unreal scene.
4. `HowToUse.pdf` also confirms RflySim3D accepts UDP commands from
   CopterSim/Python/Simulink and can return collision, terrain, and visual data.
   This is the key reason to test RflySim as a native renderer/runtime before
   building more custom UE logic.

Useful local entry points:

| Local path | Use |
| --- | --- |
| `D:\PX4PSP\RflySim3D\RflySim3D.exe` | Existing RflySim3D renderer executable |
| `D:\PX4PSP\RflySim3D\RflySim3D\RflySim3D.uproject` | UE4.27 project descriptor for audit only; do not treat it as an editable source project unless matching source/binaries are present |
| `D:\PX4PSP\RflySim3D\RflySim3D\Content\*.umap` | Existing maps such as `MapData`, `MapSmall`, `MatchScene`, `MatchScene2025`, `MountainTerrain`, `OldFactory`, `CameraRoom`, `ExhibitionHall` |
| `D:\PX4PSP\RflySim3D\RflySim3D\Content\FSJ150\XML` | Small quadrotor visual model references |
| `D:\PX4PSP\RflySim3D\RflySim3D\Content\obstacle` | Box obstacle XML/PNG references |
| `D:\PX4PSP\RflySim3D\RflySim3D\Content\ExhibitionHall\XML` | Trees, stones, city, factory, solar panel, windmill, and power-tower visual references |
| `D:\PX4PSP\RflySimAPIs\RflySimSDK\ue\UE4CtrlAPI.py` | UDP command and pose-update API for RflySim3D |
| `D:\PX4PSP\RflySimAPIs\RflySimSDK\vision\VisionCaptureApi.py` | Camera, lidar, point-cloud, and Mid360-style sensor request API |
| `D:\PX4PSP\RflySimAPIs\3.RflySim3DUE` | RflySim3D command, map, model-load, viewport, collision, weather, and trajectory examples |
| `D:\PX4PSP\RflySimAPIs\8.RflySimVision` | Vision, lidar, Livox/Mid360, direct UDP, ROS bridge, SLAM, and ESDF/path-planning examples |
| `D:\PX4PSP\RflySimAPIs\10.RflySimSwarm` | Multi-UAV and swarm display/control references |
| `D:\PX4PSP\CopterSim\ModelData.db` | Vehicle/component parameter database: motor, propeller, ESC, battery, frame presets |
| `D:\PX4PSP\CopterSim\external\XML\F450.xml` | Example quadrotor physical parameters: mass, inertia, arm radius, thrust/moment coefficients, hover RPM |

### RflySim Map Direct-Use Test

Static audit on the local install shows that RflySim maps are useful as a
reference source, but not as one-file drop-in assets for the UE5 renderer.
The local install is a packaged/runtime tree: it contains `RflySim3D.exe`, maps,
content, and plugins, but it does not expose complete project/plugin source or
matching plugin binaries for editor recompilation.

Findings:

| Item | Result |
| --- | --- |
| Project type | `D:\PX4PSP\RflySim3D\RflySim3D\RflySim3D.uproject`, `EngineAssociation=4.27` |
| Our renderer type | `unreal/MworksUnrealRenderer/MworksUnrealRenderer.uproject`, `EngineAssociation=5.7` |
| Available map files | `28` `.umap` files under `RflySim3D/RflySim3D/Content` |
| Source mesh formats | No loose `.fbx/.obj/.dae/.stl/.glb` found under the checked RflySim `Content`; most reusable geometry is inside `.uasset/.umap` |
| Required plugins | `Rfly3DSimPlugin`, `CesiumForUnreal_4.27`, `TwinmotionToUnreal`, `LidarPointCloud`, `RuntimeTransformer`, `DTRedis`, `PhysXVehicles` |
| Editor-open status | Not a reliable editor source project: UE4.27 can load engine plugins such as `PhysXVehicles`, but RflySim modules need missing/incompatible source or binaries |
| Direct copy risk | High: `.umap` references `/Game/...` assets and UE4.27/plugin packages that are not present in our UE5.7 project |

Hard blocker evidence now lives in the generated audit and registry:

```text
results/rflysim/rflysim_map_audit.md
unreal/MworksUnrealRenderer/Content/MworksData/rflysim_scene_registry.json
```

The current local tree has no usable `Source/RflySim3D/*.Build.cs`, no
`Binaries/Win64/RflySim3D*.dll`, and no source/editor binaries for critical
plugin modules such as `Rfly3DSimPlugin`, `CesiumRuntime`, `DTRedis`,
`RuntimeTransformer`, and `TwinmotionToUnreal`. Installing UE4.27 alone does not
solve this. A temporary UE editor pass is only diagnostic unless the missing
source or matching editor plugin binaries are obtained.

### Manual Archive / Extraction Gate

Do not leave archive requirements implicit. If an archive must be unpacked by
the user, report the exact archive, destination, purpose, and expected proof
before continuing.

Current archive decisions:

| Archive family | Extract now? | Destination | Purpose | Reuse status |
| --- | --- | --- | --- | --- |
| `references/RflySim/RflySimAdv3Full/4.HILApps/scenes427/*.zip` | Only if a native RflySim runtime map is missing | External RflySim install tree such as `D:\PX4PSP`, not this repo | View/record RflySim reference scenes like `OldFactory`, `NeighborhoodPark`, `RobotMissionChallenge`, `ExhibitionHall`, `MatchScene2025` | Runtime/reference only; not editable UE5 source |
| `references/RflySim/RflySimAdv3Full/4.HILApps/scenesUE5/Quarry.zip` | Only if testing the RflySim UE5 runtime scene | External RflySimUE5 tree, not this repo | View `Quarry` in the RflySim UE5 runtime | Runtime/reference only |
| `references/RflySim/RflySimAdv3Full/4.HILApps/UE5/RflySim3DUE5.zip` and `RflySim3DExUE5.zip` | Only if the installed RflySimUE5 runtime is absent or corrupted | External installation/review location | Native UE5 RflySim runtime review | Do not import as our simulator base |
| `references/RflySim/RflySimAdv3Full/4.HILApps/UE4/RflySim3D427.zip` and `RflySim3DEx427.zip` | Only if the installed UE4.27 RflySim runtime is absent or corrupted | External installation/review location | Native UE4.27 RflySim runtime review | Do not import as our simulator base |
| AirSim/Cosys release environments | No, unless explicitly reviewing a packaged runtime demo | External temporary review directory | Visual reference only | Usually not editable scene source |
| `references/Sunray/**` Gazebo/SDF/world assets | Already unpacked | Existing project reference tree | Convert or recreate scene layouts, objects, sensors, and planner truth in project-owned UE5 | Best current fallback source for editable/rebuildable scenes |

If the goal is **our own simulator**, do not ask the user to unpack RflySim
scene zips as the next step. The next step is to build or import a project-owned
UE5 scene from editable/authorized sources. Use RflySim and YunZong/Sunray
scenes as visual and layout references, then rebuild the map, object registry,
collision proxies, and planner truth under our own UE5 project.

Open-source scene-source reality check:

1. AirSim/Cosys/Project AirSim are primarily **plugins / APIs / vehicle-sensor
   frameworks**. Their bundled `Blocks` map is intentionally small; for
   photorealistic scenes, official workflows expect users to create or provide
   their own Unreal environment and drop the plugin into it.
2. CARLA is a stronger open digital asset source for city/road scenes, but it
   is heavy, car-oriented, and not a drop-in quadrotor simulator.
3. UnrealROX/SPEAR-style projects are useful for indoor scene-control and
   sensor/ground-truth patterns, but local builds may require old or specific
   UE/plugin chains.
4. The practical route for this project is a project-owned UE5 simulator shell:
   MWORKS/Syslab/Sysplorer solver and evidence, project bridge, project-owned
   scene profiles, and imported/recreated assets with explicit collision truth.

External-source-backed summary:

| Source | What it confirms | Project decision |
| --- | --- | --- |
| AirSim Blocks docs | Built-in Blocks is deliberately lightweight/basic and meant as a fast sanity environment | Do not keep showing Blocks as proof of rich scene availability |
| AirSim custom-environment docs | High-quality AirSim usage is normally "bring your own Unreal environment, then copy/add the AirSim plugin" | Our simulator should own the UE scene and bridge, not wait for AirSim maps |
| AirSim release notes | Rich released environments such as AirSimNH/LandscapeMountains are packaged demos and many cannot distribute source/project files because of proprietary assets | Treat released AirSim maps like RflySim-style runtime references unless editable source is obtained |
| CARLA docs/repo | CARLA provides open digital assets and a map-import/content-authoring workflow, but it is automotive/road centered and heavy | Use as outdoor/city asset and import-pipeline reference, not as the UAV simulator core |
| UnrealROX/SPEAR-style projects | Better fit for indoor photorealistic scene-control and sensor/ground-truth ideas | Use as scene-control/ground-truth reference; test editable maps only if build chain is stable |

Questions for RflySim support:

1. Does the free/advanced install provide an editable Unreal project for
   `RflySim3D.uproject`, or is it intentionally runtime-only?
2. Where can we obtain the UE4.27 editor binaries or source for the project
   module `RflySim3D`?
3. Where can we obtain matching UE4.27 editor binaries or source for
   `Rfly3DSimPlugin`, `DTRedis`, `RuntimeTransformer`,
   `TwinmotionToUnreal`, `CesiumRuntime`, and `ColorWheelPlugin`?
4. Are the bundled `.umap/.uasset` scene assets allowed to be migrated into a
   separate UE project for non-commercial competition visualization?
5. If direct migration is not supported, is there an official export path for
   scene geometry, object poses, collision boxes, lidar-visible obstacles, or
   terrain height data?
6. Which examples expose object/bounding-box truth or map geometry through the
   Python/UDP API, beyond vehicle pose and point cloud output?

Representative candidate maps:

| Candidate | Path | Use | Migration priority |
| --- | --- | --- | --- |
| `OldFactory` | `Content/OldFactory/Maps/OldFactory.umap` | industrial patrol, wall/pipe/building occlusion | P0 |
| `NeighborhoodPark` | `Content/ModularNeighborhood/Maps/NeighborhoodPark.umap` | park patrol, trees/buildings | P0 |
| `Grasslands` / `3DDisplay` | `Content/Grasslands/Maps/Grasslands/*.umap` | open wind/motor-efficiency scenes | P0 |
| `VisionRing` | `Content/Vision/Maps/VisionRing.umap` | ring/gate attitude-control demo | P0 |
| `ChallengeMap` | `Content/RobotMissionChallenge/Map/ChallengeMap.umap` | indoor challenge / maze-like task | P1 |
| `MountainTerrain` | `Content/MountainTerrain/Maps/*.umap` | terrain-following and outdoor path planning | P1 |
| `ExhibitionHall` | `Content/ExhibitionHall/Maps/ExhibitionHall.umap` | asset source for trees, stones, factory props, towers | P1 |
| Cesium maps | `MapData`, `MapSmall`, `Changsha`, `Denver`, `EarthMap`, `MoutainRoad` | large geospatial background | P2 because Cesium token/plugin dependency is heavy |

Decision:

```text
Do not copy one .umap into MworksUnrealRenderer and expect it to work.
Do not make RflySim3D.exe the final runtime.
Do not spend more time trying to open the packaged RflySim `.uproject` as a
normal UE editor source project unless the user obtains a source-enabled project
or a matching editor plugin binary package.

Use RflySim maps as reference inputs:
  runtime scene observation
  -> map/object/vehicle/sensor behavior notes
  -> project-owned UE5 scene recreation
  -> project-owned asset registry
  -> collision proxy extraction
  -> MWORKS UDP playback
```

### RflySim + Sunray Scene Reconstruction Plan

This is the active planning gate before starting new UE5 scene work. Do not
implement the scene until this plan has been reviewed.

Goal:

```text
RflySim visual reference
  + Sunray/YunZong parseable truth reference
  -> project-owned editable UE5 scene
  -> project-owned object registry and collision proxies
  -> MWORKS-driven playback and later real-time bridge
```

Non-goals:

1. Do not use RflySim `.umap/.uasset` files as the final editable project base.
2. Do not make RflySim runtime maps the planner/collision truth.
3. Do not restart the old MWORKS blocky-map workaround as the primary visual
   route.
4. Do not wait for PX4 logs or final Sunray150 parameter identification before
   building the visual/sensor architecture.
5. Do not start UE implementation until the first scene profile and review
   gates below are accepted.

Source roles:

| Source | Role | Allowed Use | Forbidden Use |
| --- | --- | --- | --- |
| RflySim scenes | Visual and interaction reference | Observe scene style, object families, camera behavior, lidar/radar display, map scale, demo pacing | Planner truth, final runtime dependency, unlicensed asset import |
| Sunray/YunZong assets and Gazebo worlds | Parseable truth and rebuild reference | Extract SDF/world layout, primitive dimensions, sensor/drone model references, object categories, coordinate assumptions | Treat Gazebo rendering as final video quality |
| Project-owned UE5 renderer | Final editable visualization shell | Own scene profiles, object registry, collision proxies, materials, cameras, overlays, MWORKS playback | Change MWORKS controller/planner/metric truth |

First scene family:

```text
competition_industrial_hybrid
```

Reference inputs:

| Reference | Why it matters |
| --- | --- |
| `MatchScene2025` | competition-style objects, gates/boxes/pillars, challenge scale |
| `RobotMissionChallenge` | indoor/challenge obstacle vocabulary, ArUco-like target ideas |
| `OldFactory` | industrial patrol visual language: walls, pipes, crane, barrels, cabinets, debris |
| Sunray/YunZong `.world/.sdf` | object dimensions, drone/sensor layout, truth geometry fallback |

First UE5 scene modules:

| Module | Required Behavior |
| --- | --- |
| start/goal/takeoff/landing pads | deterministic start in lower-left region and goal in upper-right region; explicit coordinate frame |
| obstacle corridor | pillars, boxes, short walls, and local replanning blockers with collision proxies |
| gate/ring/frame area | attitude-control visual target for later tilted-frame or ring traversal |
| industrial inspection cluster | factory-style props for video context, with render-only tags unless they affect planning |
| Mid360 visualization | local FOV/range display, local known-map coloring, occlusion-aware display target |
| path/trail visualization | actual UAV trail, current local plan, reference trajectory, and controller mode/fault overlays |

Data model to create before UE implementation:

```text
scene_profile:
  scene_id
  source_references
  coordinate_frame
  bounds_m
  start_goal
  object_registry[]
  collision_proxy_registry[]
  render_only_assets[]
  local_perception_policy
  randomization_policy
  review_gates[]
```

Object registry rule:

```text
Every visible object that can affect planning must have:
  object_id
  semantic_tag
  visual_asset_ref
  transform_m
  dimensions_m
  collision_proxy_id
  truth_source
  license/source note

Visual-only context objects must be explicitly marked:
  render_only=true
```

Truth separation:

```text
render_world:
  complete scene loaded in UE for video

planner_truth:
  scenario/world_geometry used by MWORKS metrics and collision checks

planner_known_map:
  local sensor memory built only from current/past perception packets
```

The planner must not read the full `render_world` object list during local
unknown-map demonstrations.

Acceptance gates before implementation:

| Gate | Acceptance |
| --- | --- |
| `plan_review` | This section is reviewed and accepted by the user |
| `scene_profile_review` | First `competition_industrial_hybrid` profile lists bounds, objects, collision proxies, randomization policy, and source roles |
| `ue_mcp_probe` | `unreal_engine` MCP is available or a source-level fallback is explicitly recorded |
| `blockout_review` | UE scene opens with pads, major obstacles, drone, axes, and camera; no asset-quality work yet |
| `asset_style_review` | RflySim/Sunray-inspired visual styling is readable; no copied unlicensed runtime assets are required |
| `perception_review` | Mid360/local map visualization shows local perception, occlusion, and known/unknown regions without exposing global truth to planner |
| `playback_review` | MWORKS result playback drives UAV, propellers, trail, local plan, overlays, and camera smoothly enough for video |
| `planning_smoke` | local planner path begins at UAV center, avoids visible collision proxies, and no longer behaves as a hard-coded straight line |

Performance targets:

| Loop | Initial Target | Stretch Target | Rule |
| --- | --- | --- | --- |
| MWORKS control evidence | 20 Hz | 50 Hz | Solver truth remains MWORKS-side |
| Mid360/local map display | 20 Hz | 30 Hz | Drop stale render frames; do not block control evidence |
| UE playback/render | 30 FPS | 60 FPS | Use instancing/LOD/static geometry before lowering visual clarity |
| planner update | 5-20 Hz | 20 Hz | Reuse previous feasible trajectory on timeout |

Implementation sequence after approval:

1. Generate a small RflySim scene reference index from the unpacked scene
   folders. This is documentation/metadata only; do not import assets.
2. Extract or list Sunray/YunZong truth candidates from `.world/.sdf` files:
   model names, primitive dimensions, mesh references, start/goal examples, and
   coordinate assumptions.
3. Draft `competition_industrial_hybrid` scene profile and object registry.
4. Build a UE5 blockout using project-owned primitives/assets and collision
   proxies.
5. Add visual styling and imported/authorized assets only after collision truth
   is stable.
6. Add MWORKS playback, local perception coloring, path/trail, camera presets,
   and video export.
7. Only then expand to park/city, terrain/wind, indoor/gate, forest, maze, and
   multi-UAV scene families.

Risks and downgrade paths:

| Risk | Response |
| --- | --- |
| RflySim assets cannot be legally or technically imported | Recreate layout/style with project-owned UE5 primitives, Fab/free assets, or Sunray/Gazebo assets |
| Sunray/Gazebo dimensions are incomplete | Use them for coarse truth and mark uncertain dimensions; do not claim physical fidelity until parameters are identified |
| UE performance drops with rich assets | Convert repeated objects to instanced meshes, simplify collision proxies, add LODs, and keep MWORKS evidence independent |
| Local planner still cuts through obstacles | Fix planner/proxy/known-map interface before adding visual polish |
| Visual map and planner truth diverge | Stop scene expansion and repair registry/proxy bindings |

Scene expansion order after the first scene:

| Priority | Scene Family | Reference Inputs | Purpose |
| --- | --- | --- | --- |
| P0 | `competition_industrial_hybrid` | `MatchScene2025`, `RobotMissionChallenge`, `OldFactory`, Sunray truth | main single-UAV navigation/control video |
| P1 | `gate_ring_attitude` | `VisionRing`, challenge/gate references | tilted-frame and aggressive attitude demo |
| P1 | `park_city_patrol` | `NeighborhoodPark`, `ModernCityBundle`, Sunray/AWS assets | patrol/logistics context |
| P2 | `terrain_wind` | `DesertTown`, `MountainTerrain`, open grassland assets | wind and terrain-following videos |
| P2 | `maze_indoor` | `CameraRoom`, challenge maps, indoor open assets | occlusion/local-replanning stress test |
| P3 | `forest_dense` | licensed UE forest/open assets | dense obstacle and swarm extension |

The full staged route is fixed now, but implementation is intentionally
limited:

| Stage | Profile | Implementation Status | Purpose |
| --- | --- | --- | --- |
| S0 | `renderer_framework` | active | UE5/MWORKS playback framework, object registry, collision proxy registry, camera, UAV, trail, radar/local-plan overlays |
| S1 | `competition_industrial_hybrid` | active after S0 profile | first complete single-UAV navigation scene with industrial/challenge references |
| S2 | `gate_ring_attitude` | planned only | tilted-frame/ring traversal and aggressive attitude-control display |
| S3 | `park_city_patrol` | planned only | patrol/logistics style outdoor mission |
| S4 | `open_grass_robustness` | planned only | wind, motor-efficiency, mass/inertia, sensor-noise and pulse-disturbance display |
| S5 | `maze_indoor_occlusion` | planned only | wall occlusion, local map memory, no-through-wall radar, indoor replanning |
| S6 | `dense_forest_high_obstacle` | planned only | dense local perception and high obstacle-count stress test |
| S7 | `multi_uav_formation` | planned only | leader-follower, formation geometry, inter-UAV distance and formation avoidance |

Current execution boundary:

```text
allowed now:
  S0 renderer_framework
  S1 competition_industrial_hybrid

blocked pending later review:
  S2-S7 implementation
```

Profiles for all stages live in:

```text
unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json
```

The file defines stage ids, map ids, source roles, visual classes, proxy
classes, planner visibility rules, and acceptance checks. The Markdown plan is
descriptive; the JSON profile is the machine-readable source for scripts and UE
scene selection.

Manual review checkpoints:

```text
profile draft -> blockout viewport -> asset styling -> perception overlay
-> playback/video -> planner-quality result
```

Do not skip from a profile draft directly to a polished scene. The profile and
blockout must be accepted first so coordinates, object roles, and collision
truth do not drift later.

Repeatable audit command:

```bash
python3 scripts/audit_rflysim_maps.py
```

Outputs:

```text
results/rflysim/rflysim_map_audit.json
results/rflysim/rflysim_map_audit.md
unreal/MworksUnrealRenderer/Content/MworksData/rflysim_scene_registry.json
```

Keep these files small and tracked. They document candidate maps and dependency
samples, not the original RflySim binary assets.

Build the project-owned scene registry after the audit:

```bash
python3 scripts/build_rflysim_scene_registry.py
```

The registry is the handoff point between RflySim research and our UE5 renderer.
It marks every RflySim scene as `direct_use_supported=false` and
`direct_editor_open_supported=false` while required project/plugin source or
editor binaries are missing. It also keeps the direct-editor blocker list so the
workflow cannot silently return to the failed "open original `.uproject`"
route. `migration_status` stays `audit_only` until a temporary UE conversion
project proves the map, materials, dependencies, and collision proxies can be
migrated cleanly.
`stream_unreal_udp.py` already sends `map_id`; `QuadrotorMworksBridge` receives
it as `FQuadrotorMworksFrame.MapId` so the renderer can later select a migrated
scene profile without changing MWORKS simulation data.

Build the first concrete migration smoke plan from the registry:

```bash
python3 scripts/plan_rflysim_scene_migration.py --scene-id rflysim_vision_ring
```

Generate the current P0 scene-plan batch:

```bash
python3 scripts/plan_rflysim_scene_migration.py \
  --scene-ids rflysim_vision_ring,rflysim_old_factory,rflysim_grasslands_3d_display
```

Outputs:

```text
results/rflysim/rflysim_vision_ring_migration_plan.json
results/rflysim/rflysim_vision_ring_migration_plan.md
results/rflysim/rflysim_vision_ring_manual_review_checklist.md
```

`VisionRing` is the first P0 target because it is small, has direct relevance to
ring/gate and tilted-frame attitude-control video, and should expose asset
migration problems before larger scenes such as `OldFactory` or `Grasslands`.
This plan is a checklist for manual/Unreal-editor work; it does not copy assets
and does not change the RflySim installation.
The manual review checklist is the required handoff artifact for the first UE
editor pass. It records missing plugins/assets, scale, coordinates, material
quality, collision proxy readiness, playback readiness, and the import decision.

Scene assets must be bound through the project-owned schema:

```text
unreal/MworksUnrealRenderer/Content/MworksData/scene_asset_registry.schema.json
```

The key rule is strict: every visible obstacle, wall, gate, tree trunk, building,
terrain surface, or ring that matters to planning must have a `collision_proxy_id`
linked back to `world_geometry`. A visual-only asset may exist only if it is
marked `render_only=true`. This prevents the final UE5 scene from drifting away
from MWORKS collision truth.

Before importing any migrated UE content into the project, validate the staged
package:

```bash
python3 scripts/create_unreal_migration_package_stub.py
python3 scripts/check_unreal_migration_package.py \
  --package-dir unreal/migration_staging/rflysim_vision_ring
```

The stub is metadata-only and is allowed to pass the quality gate before real
assets exist. After the temporary UE migration pass, replace placeholder
`asset_path`, `source_path`, scale, material, and collision proxy bounds with
measured values. The package directory must be inside this project and must
contain exactly one `scene_asset_registry.json`. The checker rejects `.pak`,
installers, engine binaries, files over 100 MB, invalid licenses, and
obstacle-like visual assets without collision proxies.

Deprecated direct-editor migration test:

This path was tested and is not the current main route.

1. A scratch copy of `D:\PX4PSP\RflySim3D\RflySim3D\RflySim3D.uproject` was
   opened with UE4.27.2.
2. UE4.27 found the engine `PhysXVehicles` plugin, but RflySim modules such as
   `RflySim3D`, `Rfly3DSimPlugin`, `CesiumRuntime`, `DTRedis`, and
   `RuntimeTransformer` remained incompatible or missing.
3. The tree does not contain enough editable project/plugin source or matching
   editor plugin binaries for a clean rebuild.
4. Therefore this route is stopped. Continue with native RflySim runtime
   observation and project-owned UE5 scene reconstruction.

Allowed fallback route when direct editor migration is blocked:

```text
RflySim runtime/manual observation
  -> record map layout, scale, materials, sensors, and useful scene assets
  -> rebuild scene in project-owned UE5 renderer using project-owned assets
  -> bind every visible obstacle/gate/wall/terrain piece to collision proxies
  -> drive visualization from MWORKS UDP/replay packets
```

Do not spend engineering time repeatedly clicking through missing-plugin dialogs
unless the goal is to record a new blocker or verify newly obtained source or
plugin binaries.

Use the dry-run helper to print the exact Windows commands without copying
assets:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/prepare_rflysim_temp_migration.ps1
```

The helper intentionally does not run `robocopy`. Copying the RflySim UE project
to `D:\UE_MigrationScratch` is an external write operation and is now useful
only for diagnostics. It is not a required step for the main UE5 reconstruction
route.

Stop conditions:

1. missing proprietary Marketplace plugin that cannot be installed;
2. map opens only in the bundled RflySim runtime and not in editable Unreal;
3. UE conversion rewrites large binary assets that cannot be tracked or
   externalized cleanly;
4. collision/geometry truth cannot be extracted or approximated.

Official RflySim documentation entry points used for architecture reference:

| Topic | Source |
| --- | --- |
| RflySim3D / UE command and scene workflow | `https://rflysim.cn/doc/en/3/RflySim3DUE.html` |
| Vision sensor configuration, shared memory / UDP / stream modes | `https://rflysim.cn/doc/en/3.Soft/viscreate.html` |
| RflySim default UDP port allocation | `https://rflysim.com/doc/zh/RflySimAPIs/RflySimSDK/html/md_comm_2md_2port.html` |
| High-frame-rate image access concept | `https://rflysim.com/en/4_Pro/UAVVisionAIControl.html` |

Most relevant RflySim3D examples:

```text
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/1.UECtrlPy/PythonSendUE4Pos.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/1.UECtrlPy/PythonSendUE4ExtDemo.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/3.LoadModelsByTxt/LoadModelsByTxt.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/4.TrajDemo/UE4MapTerrainDemo.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/6.RflySim3DViewPortDemo/UE4ViewPortDemo.py
3.RflySim3DUE/0.ApiExps/e6_RflySim3DCtrlAPI/9.RflySim3DPosGet/GetUE4PosAPI.py
3.RflySim3DUE/0.ApiExps/e5_UEMapCtrl/2.TargetCreatePy/code/TargetCreateDemo.py
3.RflySim3DUE/0.ApiExps/e5_UEMapCtrl/3.TargetPlace/code/TargetPlace.py
3.RflySim3DUE/0.ApiExps/e9_RflySim3DCollision
```

Most relevant vision/lidar examples:

```text
8.RflySimVision/0.ApiExps/10.Mid360Demo
8.RflySimVision/0.ApiExps/1-UsageAPI/3.PointCloudAPI
8.RflySimVision/0.ApiExps/1-UsageAPI/4.SendProtocolAPI
8.RflySimVision/0.ApiExps/4.Point-CloudVisualize
8.RflySimVision/0.ApiExps/7.LidarLivoxDemo
8.RflySimVision/2.AdvExps/e16_ESDFPathPlan
```

Confirmed communication facts from the local SDK:

| Item | Finding |
| --- | --- |
| RflySim3D command channel | `sendUE4Cmd(...)` sends UDP commands to `20010 + windowID` |
| RflySim3D pose channel | `sendUE4Pos(...)`, `sendUE4PosNew(...)`, `sendUE4PosFull(...)` create or update a vehicle by `copterID` and `vehicleType` |
| Rotor visual input | `sendUE4Pos(...)` accepts `MotorRPMSMean`; `sendUE4PosFull(...)` accepts eight motor RPM values |
| Scene switch | `RflyChangeMapbyName <map>` |
| Model switch | `RflyChange3DModel <CopterID> <veTypes>` |
| Camera/view | `RflyChangeViewKeyCmd`, `RflyCameraPosAng`, `RflyCameraFovDegrees` |
| Text overlay | `RflyShowTextTime`, `RflyShowText` |
| Terrain query | `RflyScanTerrainH ...` |
| Sensor request channel | Vision sensor requests are sent to the RflySim3D window and can return shared-memory or UDP data |
| Mid360 example | `TypeID=23`, `DataWidth=64`, `DataHeight=272`, `DataCheckFreq=10`, UDP return port example `9999` |
| Object/camera query | `RflyReqObjData` can request camera, vehicle, and object pose plus bounding-box origin/extent for named objects |
| Terrain service | `RflyScanTerrainH x0 y0 x1 y1 h interval` exports terrain PNG/TXT data; examples convert it to height query and PLY point cloud |

Known parameter limits:

1. Vehicle physical parameters are available from CopterSim XML and
   `ModelData.db`. Example F450 data includes mass `1.4 kg`, inertia
   `Jxx=0.0211`, `Jyy=0.0219`, `Jzz=0.0366`, arm radius `0.225 m`,
   thrust coefficient `1.105e-05`, torque coefficient `1.779e-07`, motor
   response time `0.05 s`, and hover motor speed `5235.8 rpm`.
2. Terrain height can be sampled through RflySim3D terrain scan files. This is
   useful for visual alignment and local height maps, but it is not yet proof
   that every scene object/collision mesh can be exported as clean planning
   truth.
3. Scene object geometry may be available only for named/requested actors via
   `RflyReqObjData`, returning `PosUE`, `angEuler`, `boxOrigin`, and
   `BoxExtent`. Full static-scene collision truth is not guaranteed until the
   target scene is tested.
4. Cooked RflySim scenes and `.pak` files are not project-owned assets. If the
   installed tree does not expose editable `.uasset/.umap` source with usable
   license terms, treat it as a renderer/runtime reference rather than a source
   asset library.

RflySim native experience path:

```text
1. RflySim3D command and map test
   - Start RflySim3D.
   - Use RflyChangeMapbyName, r.setres, t.MaxFPS, camera commands.
   - If sending commands from WSL, do not assume 127.0.0.1 is the Windows
     RflySim3D host. Use the WSL default gateway IP or run the command script
     with Windows Python/PowerShell from the Windows side.

2. Terrain service test
   - Run 3.RflySim3DUE/1.BasicExps/e3_RflySim3DTerrainPcd.
   - Verify RflyScanTerrainH output and height-query consistency.

3. Vehicle visual/control test
   - Use UE4CtrlAPI.sendUE4PosFull or RflySim3D built-in SITL example.
   - Check pose, scale, propeller RPM display, and camera following.

4. Mid360/lidar test
   - Run 8.RflySimVision/0.ApiExps/10.Mid360Demo.
   - Verify TypeID=23 point cloud path and update frequency.

5. Path-planning reference test
   - Run 8.RflySimVision/2.AdvExps/e16_ESDFPathPlan.
   - Record whether its ESDF/Voronoi path planner is usable as an algorithm
     reference, not as final MWORKS evidence.
```

Only after these pass should the project port useful pieces into the
project-owned Unreal scene. Driving RflySim3D from MWORKS output is allowed only
as a temporary reference comparison, not as the final delivery path.

Manual review gates for the native RflySim experience:

| Gate | What to check | Pass condition |
| --- | --- | --- |
| `rflysim3d_map_view` | RflySim3D starts, changes map, camera/FPS commands work | User can see a stable scene and switch views without freezing |
| `rflysim_vehicle_visual` | Built-in or UDP-driven quadrotor model, propellers, scale, attitude | Vehicle model, propellers, and pose are visually credible |
| `rflysim_mid360` | Mid360/lidar example data path | Point cloud or ROS/RViz output appears at expected update rate |
| `rflysim_terrain_service` | Terrain scan and height lookup | Generated terrain files match selected scene region and can be queried |
| `rflysim_object_truth` | Object/camera query or scene metadata | Named object pose and bounding boxes can be obtained, or limitation is documented |
| `rflysim_esdf_path` | ESDF/Voronoi planning example | Path is not a hard-coded straight line and can be mapped to NED waypoints |

If `rflysim_object_truth` fails, RflySim can still be used for mechanism study,
but not as the source of obstacle/planning truth. In all cases MWORKS/scenario
files remain the truth source, and final rendering should run in the
project-owned UE5 scene.

### Project-Owned UE5 Scene Workflow

Use this workflow before any new UE5 navigation demo:

```text
1. Reference survey
   - Inspect RflySim/Gazebo/AirSim-style examples only to identify useful
     scene, sensor, protocol, and timing mechanisms.
   - Do not treat RflySim runtime maps as planner truth.

2. Editable scene construction
   - Pick project-owned or explicitly licensed editable maps, meshes,
     materials, XML/parameter files, or scene-layout data.
   - Recreate or import them into project-owned UE5 assets, scenario profiles,
     and collision proxies.
   - Save source path, license/approval note, scale, coordinate frame, and
     object IDs.

3. Truth/proxy binding
   - For every visible obstacle/tree/wall/gate, create a matching
     world_geometry primitive or occupancy/collision proxy.
   - Do not use visual meshes directly for planner truth until proxy extraction
     is verified.

4. Local planning smoke
   - Enable only local point-cloud/occupancy input.
   - The planner must not read the complete map object list.
   - A useful run must show nonzero local obstacles, no yaw spinning, no wall-through path, and no artificial box corridor.

5. Playback or real-time bridge
   - For video, drive project-owned UE5 from MWORKS raw/native result or a
     bounded real-time state stream.
   - Keep controller and metrics truth in MWORKS.
   - `stream_unreal_udp.py` sends `map_id`; `QuadrotorMworksPlaybackActor`
     forwards it to `QuadrotorMworksMapActor`, which resolves the id against
     `rflysim_scene_registry.json` and exposes/logs migration status and direct
     use blockers. This is scene-selection/status plumbing, not a promise that
     RflySim `.umap` files are loaded at runtime.
```

Scenario families:

| Family | Preferred map/source | Purpose |
|---|---|---|
| Dense forest | Project-owned or licensed editable UE forest scene; RflySim/open scenes only as visual reference | Unknown-map dense obstacle avoidance |
| Maze/building | Project-owned maze or licensed editable building/factory assets | Wall occlusion and local replanning |
| Old factory | Project-owned `OldFactory`-style scene or licensed editable UE factory scene | Mid360 point cloud and industrial inspection demo |
| Park/patrol | Project-owned or licensed editable park assets | Inspection/logistics scenario |
| Gate/ring indoor | Project-owned `VisionRing` / challenge-style indoor assets | Attitude tracking through tilted gates/rings |
| Open grass | Project-owned grassland scene | Wind and motor-efficiency robustness |

The project-owned profile source is:

```text
unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json
```

This file is the route away from direct RflySim editor migration. Each profile
defines the intended visual world, required collision proxies, planner
visibility rule, timing targets, and manual acceptance checks. Do not start a
new UE5 scene without either using one of these profiles or adding a reviewed
profile entry first.

Generate the current implementation plan from these profiles:

```bash
python3 scripts/plan_unreal_scene_profiles.py
```

Outputs:

```text
results/unreal/unreal_scene_profile_implementation_plan.json
results/unreal/unreal_scene_profile_implementation_plan.md
```

Recommended open asset candidates:

| Priority | Candidate | Best Use | Git Policy |
|---|---|---|---|
| P0 | Electric Dreams Env | Dense forest, PCG vegetation, forest-flight video | External asset only |
| P0 | Factory Environment Collection | Old factory, industrial patrol, indoor/outdoor obstacle avoidance | External asset only |
| P1 | Open World Demo Collection / A Boy and His Kite | Open forest, mountain, canyon, large outdoor flight | External asset only |
| P1 | Rural Australia | Open natural patrol and logistics-style scenes | External asset only |
| P2 | Poly Haven CC0 assets | HDRI, rocks, materials, small props | Small selected files may be committed if under limits |

Large scene assets stay outside Git by default. Commit only scripts, config, scenario profiles, derived small manifests, and documentation.

### AirSim / Cosys-AirSim Map Decision

AirSim is useful as an architecture and API reference, but it is not a good
primary source for finished high-quality maps.

Current finding:

| Source | Status | Project Use |
|---|---|---|
| Microsoft AirSim | Original repo is archived/no longer updated. The plugin and APIs are MIT and still useful as reference. | Study sensor/API/plugin architecture only |
| AirSim `Blocks` | Source project exists in the repo and is lightweight/fast, but visually basic. | Use only for build/interface smoke ideas |
| AirSim release environments | Downloadable maps such as `AirSimNH`, `LandscapeMountains`, `Africa`, `Coastline`, `ZhangJiajie`; official releases say many use proprietary assets and do not include source/project files. | Runtime visual reference only, not a direct asset migration source |
| Cosys-AirSim | Maintained fork direction for newer UE versions, including Unreal 5.5 branch/release. Same MIT base, but provided as-is. | Better modern plugin/sensor reference than original AirSim |
| Colosseum | AirSim successor fork targeting newer UE, MIT, useful for UE5 robotics architecture. | Reference for plugin architecture and SITL/HIL patterns |

Decision:

```text
Do not depend on AirSim release maps as final UE assets.
Do not expect AirSimNH/LandscapeMountains/etc. to provide editable scene source.
Use AirSim/Cosys/Colosseum for architecture, vehicle/sensor API ideas, and
runtime behavior references.
Use Fab/Marketplace/open licensed UE assets or project-owned generated geometry
for final maps.
```

If the user wants to test AirSim locally, download only source-controlled or
explicitly licensed content first:

1. Clone `Cosys-Lab/Cosys-AirSim` or `CodexLabsLLC/Colosseum` outside the repo
   for source inspection.
2. Use the original AirSim `Blocks` environment only as a small build sanity
   check.
3. Treat AirSim release environment zips as runtime demos unless their editable
   Unreal project/source assets are separately available and licensed.

Useful questions if contacting an AirSim/Fork maintainer:

1. Which UE5 branch is currently recommended for multirotor simulation?
2. Are any visually rich environments distributed as editable UE projects with
   redistributable assets?
3. Is there an official way to export map geometry, object pose, or collision
   proxies for a custom renderer/planner?
4. Which sensor modules provide lidar/point-cloud plus object-level truth?

### Open-Source Scene Candidate Survey

The goal is not to find another full simulator to replace MWORKS. The goal is
to find reusable scene assets or scene-generation ideas for the project-owned
UE5 renderer. Prefer sources that provide editable project files, clear
licenses, and extractable geometry/collision truth.

Current candidate ranking:

| Rank | Candidate | Scene Value | Reuse Mode | Risk |
|---|---|---|---|---|
| A+ | SPEAR / SpearSim | Photorealistic embodied-AI UE project/control layer; includes programmable UE access, camera modalities, and example UE app control | Use as primary reference for UE-side scene control, sensor rendering, Python/UE transaction design, and indoor/warehouse candidate inspection | Need local clone/open test; separate SPEAR-owned assets from Epic sample-project assets |
| A | Project AirSim | UE5 drone/robot simulator framework with physics, controllers, actuators, sensors, headless/off-screen operation | Use as primary drone-renderer/interface reference for UE5, sensor configuration, robot JSONC, and off-screen rendering | Visual scenes are simple; use as architecture reference more than final scene source |
| A | CARLA | Urban roads, buildings, layouts, vehicles; open digital assets with clear simulator workflow | Use as reference/source for city/building map assets and map-ingestion workflow | Heavy build; primarily autonomous-driving urban, not factory/indoor |
| A- | UnrealROX | Photorealistic indoor UE4 project with `Content/`, `Source/`, `robotrix.uproject`; MIT code | Clone outside repo and test whether rooms/objects can be migrated or used as indoor reference | UE4.18-era project; not drone-specific; asset license needs review beyond code license |
| B+ | PEDRA | Drone RL environments including many indoor and outdoor maps | Use as runtime/reference for drone navigation scenarios | Environments are packaged Windows binaries; not clearly editable source maps |
| B+ | UESVONavigation | UE sparse-voxel-octree 3D navigation plugin | Use as algorithmic reference for volumetric navigation in UE scenes | Plugin is old UE4; integrate ideas, not direct dependency unless ported |
| B | UnrealCV / UnrealZoo | Large set of UE virtual worlds and ground-truth APIs | Use API/ground-truth ideas; binaries may be useful for visual reference | Mostly compiled environments, not direct asset source |
| B | Colosseum / Cosys-AirSim | Modern AirSim-style drone/PX4/UE architecture | Use plugin/sensor/control architecture as reference | Maps still need separate UE assets |
| B | Cesium for Unreal Samples | Large-scale city/building/geospatial scenes and photogrammetry examples | Use for global/city visual reference and geospatial streaming patterns | Depends on Cesium plugin/ion data; not suitable as self-contained indoor map |
| C | Small UE industrial demo repos | Factory/industrial visuals may exist as `.uproject` | Only use after inspecting included assets and licenses | Many use Quixel/Megascans or Marketplace assets; repo license may not cover assets |
| C | StreetMap / OSM import plugins | Fast procedural buildings/roads from OSM | Use to generate simple city blocks if no better assets are available | Not factory/indoor; visual quality limited without material/asset work |

Specific notes:

1. SPEAR is the best architecture reference found so far for programmable UE
   rendering. Its key value is not only scene assets: it demonstrates a
   transaction-style Python/UE bridge, fast camera rendering into arrays, and
   ground-truth modalities. This matches our need to keep MWORKS as the
   controller/planner truth while UE handles visual state and perception views.
2. Project AirSim is the best UE5 drone-simulator reference found so far. Its
   immediate value is the UE5 sensor/robot/headless/off-screen architecture,
   not final scenery. Use it to design the MWORKS-to-UE frame schema and future
   lidar/camera playback modes.
3. CARLA is currently the best open-source asset candidate for outdoor
   building/city scenes because its project explicitly provides simulator code
   and open digital assets. It also documents `.fbx + .xodr` map ingestion and
   editor customization. For this project, use CARLA ideas/assets only as a
   scene-source layer; do not adopt CARLA as the control simulator.
4. UnrealROX is the best candidate for an editable indoor UE project. It is not
   a UAV simulator, but it has the right pattern: complete UE project,
   photorealistic indoor scenes, and exportable scene/robot/camera data.
5. PEDRA is drone-oriented and has many indoor/outdoor environments, but the
   documented environment distribution is packaged. Treat it like RflySim unless
   editable UE project files are found.
6. UESVONavigation is not a scene source, but it is relevant because ordinary
   ground navigation is not enough for quadrotor scenes. Keep it as a reference
   if we need UE-side 3D collision/navigation previews.
7. UnrealZoo is promising for visual reference and ground-truth interfaces, but
   current public distribution appears to focus on binaries/API rather than
   editable scenes.
8. Factory/warehouse GitHub demos should be treated as suspect until each asset
   is checked. A repo can be Apache/MIT while still containing Quixel or
   Marketplace assets whose license is not covered by the repo license.

Recommended next asset actions:

```text
1. Clone/inspect SPEAR outside the repo first and identify whether its warehouse
   or indoor examples can be opened locally and whether its UE control bridge
   design can inform our TCP/UDP renderer.
2. Clone/inspect Project AirSim outside the repo second and extract its UE5
   scene/sensor/headless architecture notes.
3. Clone UnrealROX outside the repo and check whether UE opens the project and
   whether Content maps are useful for indoor/gate/maze scenes.
4. Clone or inspect CARLA outside the repo only if we want outdoor city/building
   assets or a robust map-ingestion reference.
5. Search Fab/Marketplace for free factory/warehouse/industrial packs and keep
   them external; record only manifest/paths/licenses in this repo.
6. Keep project-owned generated geometry for gates, rings, and planner-truth
   objects even if final visuals come from imported assets.
```

### Local Reference Repository Triage

The local reference folders are inputs for design extraction, not dependencies
to vendor wholesale into the final project. Keep the names as broad buckets for
now:

```text
references/AirSim/   UE/Isaac/drone-rendering and visual-sensor references
references/Lab/      planning, mapping, trajectory optimization, racing, swarm references
references/MWORKS/   official/contest/platform reference materials
references/RflySim/  local RflySim installer/runtime/reference materials
```

Current local-priority split:

| Bucket | Highest-Value Local Repos | Extract First |
|---|---|---|
| UE/rendering bridge | `spear`, `unrealcv-5.2`, `AirSim`, `ProjectAirSim`, `UESVONavigation-develop` | UE scene/control bridge pattern, camera/depth/semantic capture, object truth, 3D navigation preview |
| Drone sim architecture | `AirSim`, `Cosys-AirSim`, `ProjectAirSim`, `PegasusSimulator` | vehicle/sensor/actuator schemas, client APIs, headless/off-screen modes, PX4/MAVLink integration patterns |
| Trajectory/planning | `GCOPTER`, `Fast-Racing`, `ego-planner`, `EGO-Planner-v2`, `SUPER` | MINCO/GCOPTER constraints, B-spline replanning, aggressive/racing trajectories, benchmark task organization |
| Swarm planning | `EGO-Planner-v2`, `ego-planner-swarm`, `SUPER` | multi-UAV formation, collision avoidance, swarm bridge, distributed replanning |
| Mapping/localization | `Point-LIO-point-lio-with-grid-map`, `FAST_LIO`, `FAST-LIVO2` | LIO/LIVO interfaces and future local-map evidence; keep as P2 unless needed for perception demos |
| Data-only or weak fit | `AirSim360`, packaged PEDRA/RflySim environments | reference only unless editable scenes or clear data conversion value is identified |

Do not try to integrate all repositories. The next implementation pass should
extract small, project-owned interfaces:

1. A `map_id` / scene-profile manifest that can name imported or generated UE
   scenes without hard-coding one simulator.
2. A MWORKS-to-UE frame schema carrying pose, planned path, local perception
   window, obstacle truth/proxies, controller mode, and fault/disturbance state.
3. A planning module adapter API that can host simplified versions of
   B-spline/EGO/GCOPTER/MINCO outputs while the official MWORKS model remains
   the source of simulation evidence.
4. A reference-audit note for each imported external repo before any asset or
   algorithm is promoted into `unreal/`, `planners/`, or `models/`.

Known local Git hygiene rule: files over GitHub's 100 MB hard limit are ignored
under `references/**` by extension (`.iso`, `.msi`, `.exe`, `.dll`, `.vis`,
`.resS`, `.pe`, `.peo`, `.onnx`, plus archives/videos already covered). If a
large reference file is actually required for reproduction, keep it external and
record only its path, checksum, and source in documentation.

Immediate adapter work queue:

| Queue | First Inputs | Output To Produce | Acceptance |
|---|---|---|---|
| UE frame schema | `spear/README.md`, `unrealcv-5.2/README.md`, `AirSim/README.md`, `ProjectAirSim/README.md` | Extend the existing MWORKS-to-UE frame schema with camera/depth/semantic/lidar visibility fields without binding to one simulator | `check_unreal_bridge.py` passes and old frame replay remains compatible |
| Scene manifest | `spear`, `unrealcv-5.2`, `carla-ue5-dev`, RflySim audit results | A project-owned scene profile manifest that records source, license risk, map_id aliases, coordinate convention, and whether geometry/collision is importable | No raw third-party assets required for the manifest |
| Planning adapter | `ego-planner`, `EGO-Planner-v2`, `GCOPTER`, `Fast-Racing`, `SUPER` | A small planner-adapter spec mapping external planner concepts to `path_bus`, `trajectory_bus`, and `planning_debug_bus` | `Design/02` and `Design/05` remain consistent; A* remains fallback only |
| Aggressive flight demo | `Fast-Racing`, `GCOPTER`, current gate/ring scene profile | A staged plan for tilted gate/ring traversal with velocity/acceleration/tilt constraints | Does not bypass controller tracking metrics |
| Swarm extension | `EGO-Planner-v2`, `ego-planner-swarm`, `SUPER` | Formation/swarm adapter notes for leader-follower, inter-UAV distance, and local collision avoidance | Plugs into `Design/06` without changing single-UAV closed-loop evidence |

UE/rendering adapter backlog extracted from local references:

| Adapter | Reference Pattern | Project-Owned Output |
|---|---|---|
| RenderBridge state protocol | ProjectAirSim `types.py`, `kinematics_message.hpp`; AirSim vehicle API | typed frame carrying time, vehicle id, NED pose, quaternion, velocity, angular velocity, motor speeds, controller mode, fault flags |
| Coordinate/time adapter | ProjectAirSim `clock.hpp`; AirSim pause/sync/image timestamp API | NED-to-UE, meters-to-centimeters, quaternion convention, interpolation, pause/single-step rules |
| UE actor sink | AirSim `PawnSimApi` / `MultirotorPawnSimApi` boundary | lightweight `QuadrotorRenderActor` / subsystem that updates body, rotors, trace, local plan, and fault highlights from MWORKS frames |
| Camera/sensor capture | AirSim `PIPCamera`, `RenderRequest`; UnrealCV camera sensors | capture RGB/depth/segmentation/normal with pose, timestamp, and intrinsics |
| Annotation layers | Cosys-AirSim annotation and proxy mesh design | semantic/fault-zone/safety-boundary/formation-role/obstacle-id visualization layers |
| Scenario object API | ProjectAirSim `World` concepts | list/get/set/spawn/destroy scene objects and debug lines for obstacles, no-fly zones, wind/fault markers |
| Replay adapter | Project result CSV/native exports | time-aligned UE playback that preserves `source=MWORKS_MCP`, `source=MWORKS_GUI`, or `source=offline_script` |
| Headless QA | UnrealCV workflow harness/build/launch/test/log-monitor | build/launch smoke, frame capture, log filter, screenshot/hash evidence |
| 3D path preview | UESVONavigation SVO/Theta* concepts | UE-side debug path/voxel markers only; not controller truth |
| Minimal UE MCP | SPEAR single-frame transaction and MCP idea | `load_scene`, `spawn_quadrotor`, `apply_state_frame`, `capture_camera`, `export_replay_clip`; do not expose full UE reflection to normal workflow |

### Long-Running UE5 Reconstruction Queue

This queue is the default continuation path. The agent should keep moving down
the queue without asking for "continue" after each small task. Stop only for
license/authorization decisions, external write access, Unreal editor manual
review, frozen GUI/MCP/editor state, or a change that risks data loss.

Before each UE/RflySim/MWORKS renderer round, run a short task-distribution
check instead of executing serially by habit. Split by both task type and task
scale: if a read-only investigation covers more than about 3 repositories or
more than one subsystem, divide it into multiple explorers instead of assigning
one broad "research" task.

```text
1. Critical path: what must the main agent do locally before anything else?
2. Research sidecar: docs, open-source reference, license, or asset audit that
   can run read-only in parallel.
3. Implementation sidecar: one disjoint UE/MWORKS/tooling write scope, only if
   the interface is already clear.
4. Evidence sidecar: one bounded smoke/regression check with explicit output
   paths.
5. Git/quality sidecar: size scan, diff review, tests, commit, and push for
   explicit paths only.
```

Every sidecar task must include `objective`, `read scope`, `write set`,
`stop condition`, `expected output`, and `forbidden actions`. If the task is
small enough that this overhead is larger than the work itself, do it locally
and record the reason in the progress update.

Recommended split for the current external-reference phase:

| Workstream | Scope | Expected Output |
|---|---|---|
| UE/rendering explorer | `spear`, `unrealcv-5.2`, `AirSim`, `ProjectAirSim`, `Cosys-AirSim`, `UESVONavigation` | MWORKS-to-UE frame/schema implications, reusable sensor/rendering APIs, direct-migration risks |
| Planning/trajectory explorer | `ego-planner`, `EGO-Planner-v2`, `ego-planner-swarm`, `GCOPTER`, `Fast-Racing`, `SUPER` | Adapter mapping to `path_bus`, `trajectory_bus`, `planning_debug_bus`, and priority order |
| Perception/mapping explorer | `Point-LIO`, `FAST_LIO`, `FAST-LIVO2`, `AirSim360`, `IsaacSim`, `PegasusSimulator` | P2/P3 value, Mid360/local-map interface implications, data/engine mismatch risks |
| Skills/subagent explorer | `Skills/awesome-codex-skills`, `Skills/awesome-codex-subagents` | Reusable task patterns for Git/quality, codebase research, long-running simulation, and workflow updates |
| Git/quality worker | Current repo status and staged paths | Large-file guard, diff check, commit, push, and remaining-change report |

Reusable subagent patterns extracted from local skill catalogs:

| Project Role | Borrowed Pattern | Project Adaptation |
|---|---|---|
| Git/quality agent | `reviewer`, `git-workflow-manager` | status, diff grouping, large-file guard, secret guard, `git diff --check`, targeted checks, commit, push, remaining-change report |
| Codebase mapper | `code-mapper`, `context-manager` | read-only path/interface/model/result inventory before touching unfamiliar repos or MWORKS models |
| Long-task coordinator | `multi-agent-coordinator`, `task-distributor`, `workflow-orchestrator` | split by scale and subsystem, define objective/read scope/write set/stop condition/forbidden actions for each agent |
| Docs/API researcher | `docs-researcher`, `research-analyst` | separate facts, inferences, and pending validation; prefer local docs/MCP before external sources |
| Simulation diagnostics | `debugger`, `qa-expert`, `performance-engineer` | distinguish slow simulation from frozen GUI, require logs/metrics, and preserve MWORKS evidence labels |
| UE runtime reviewer | `game-developer` | use frame-rate, asset lifecycle, runtime smoke, and visual verification ideas, but keep project-owned Unreal workflow as source of truth |

Do not install or copy the upstream skill catalogs wholesale. Promote only the
specific workflow rule into `AGENTS.md`, `workflows/`, or `Skills/Mworks/` after
it has been adapted to this project boundary.

| Phase | Task | Owner Pattern | Done When | Human Gate |
|---|---|---|---|---|
| U0 | Keep RflySim/UE audit and scene registry current | main + Git/quality agent | `audit_rflysim_maps.py`, `build_rflysim_scene_registry.py`, and `check_unreal_bridge.py` pass | none |
| U1 | Produce one-scene migration plan, starting with `rflysim_vision_ring` | main | `rflysim_vision_ring_migration_plan.json/.md` exists and passes bridge checks | none |
| U2 | Validate staged migration packages before import | main + Git/quality agent | `check_unreal_migration_package.py` accepts valid fixture and rejects missing collision proxy | none |
| U3 | Open temporary UE conversion copy and verify selected RflySim scene | user/UE editor + main guidance | map opens, missing plugin/asset warnings recorded, no repo files polluted | yes |
| U4 | Create project-owned `scene_asset_registry.json` for the migrated scene | main, possibly docs/scene agent | every visible obstacle-like asset has `collision_proxy_id`; package gate passes | only if license/status unknown |
| U5 | Import or recreate approved assets in `MworksUnrealRenderer` | UE MCP/Editor agent after MCP probe | assets appear in UE, scale/axis verified, no `.pak` or >100 MB tracked file | yes for visual audit |
| U6 | Build playback scene using `QuadrotorMworksBridge` | UE MCP/Editor agent | UAV, propellers, local plan, trail, radar sector, and selected scene are visible | yes |
| U7 | Run MWORKS raw/native replay into UE | main + MWORKS/UE tools | `stream_unreal_udp.py --dry-run` and a short real playback work | yes for video review |
| U8 | Add camera/video workflow | UE MCP/Editor agent | follow/overview camera preset and export path documented | yes |
| U9 | Expand scene family after first pass | research agent + main | next scene plan exists for `OldFactory` or `Grasslands` | none unless new license issue |

Parallelization rule for this queue:

```text
main agent:
  owns queue, integration, checks, and final user report

research agent:
  can investigate assets, docs, licenses, and reference architectures
  writes nothing unless assigned a doc section

UE/MCP agent:
  can edit only assigned Unreal project/scene files after MCP/editor probe passes

Git/quality agent:
  stages only explicit paths, checks file sizes, runs tests, commits, pushes
```

The main agent should not wait idly for Git when it can safely continue with a
non-overlapping file-level task. Conversely, it must not start UE editor scene
writes while a Git agent is committing the same Unreal files.

Recommended sub-agent contracts for this queue:

| Agent Type | Objective | Default Write Set | Required Return |
|---|---|---|---|
| Research | Verify RflySim/Gazebo/AirSim/UE reference behavior, licenses, map candidates, or API docs | none | facts with source paths/URLs, inferences, unknowns, license risk |
| UE implementation | Modify one assigned renderer, scene profile, bridge, or asset-registry slice | assigned `unreal/`, `scripts/`, or `results/unreal/` paths only | changed paths, manual review target, checks run |
| MWORKS evidence | Run/check one assigned scenario/controller evidence bundle | assigned `scenarios/`, `models/`, or `results/` subtree only | model, source label, result paths, quality status |
| Docs/workflow | Update the smallest relevant existing workflow/design/manual section | assigned `Design/`, `docs/`, `workflows/`, or `Skills/Mworks/` files only | sections changed, stale docs found, remaining gaps |
| Git/quality | Scan size/secrets, review diff, run checks, commit, push | no source edits except narrow ignore/quality notes when assigned | status, staged paths, checks, commit hash, push result |

Scene randomization rules:

1. Randomize scene layout only before the run starts.
2. Save the seed, selected scene profile, moved objects, bounding boxes,
   collision proxies, wind profile, and motor-efficiency profile.
3. Keep `render_world` and `planner_known_map` separate. The renderer may load
   the complete world, but the planner may only use local sensor updates and
   previously discovered map memory.
4. For validation, provide both views when possible: actual scene/map view and
   local point-cloud or known-map view.

Runtime latency rules:

| Loop | Target | Timeout Policy |
|---|---|---|
| Control | 20 Hz minimum, 50 Hz target | Hold last valid command or switch safe mode |
| Mid360/local map | 20 Hz minimum, 20-30 Hz target | Drop stale frames instead of blocking control |
| Planner/trajectory update | 5-20 Hz depending on solver cost | Reuse previous feasible trajectory |
| Renderer | 30-60 FPS target | Rendering must not block control or metrics |

Every RflySim/UE experiment should log solver time, dropped sensor frames,
planner timeout count, control-loop period, and bridge latency. A smooth replay
video is not enough to claim real-time feasibility.

### Verified RflySim Status

Current local verification status:

| Gate | Status | Evidence |
| --- | --- | --- |
| `rflysim3d_map_view` | Reference-only | RflySim3D launches from `D:\PX4PSP\RflySim3D\RflySim3D.exe`; use native maps for observation/demo only. Current evidence does not make the maps editable UE source assets or planner truth |
| `rflysim_vehicle_visual` | Passed | `tools/rflysim/rflysim_windows_smoke.py` creates and moves quadrotor actors through `UE4CtrlAPI` |
| `rflysim_lightweight_control` | Passed | Official `UAVCtrlNoPX4Demo.py` runs a point-mass control sequence without PX4/QGC |
| `rflysim_mid360` | Passed | `tools/rflysim/rflysim_mid360_smoke.py` receives direct UDP Mid360 point clouds: `80` frames, each `17408 x 4` |
| `rflysim_esdf_path` | Partly passed | `tools/rflysim/rflysim_esdf_path_smoke.py` validates official map-to-path logic: `15.86 m` path, `0.25 m` minimum clearance |
| `rflysim_esdf_playback` | Partly passed | `tools/rflysim/rflysim_esdf_path_playback.py` replays the generated `220`-point path into RflySim3D through `UE4CtrlAPI` |
| `rflysim_mid360_local_grid` | Prototype passed | `tools/rflysim/rflysim_mid360_reactive_avoidance.py` converts Mid360 world-coordinate point clouds into a local occupancy grid and runs local A*; latest smoke produced nonzero occupied cells and active front-blocked decisions |
| `rflysim_object_truth` | Not complete | Object/bounding-box truth still needs scene-specific verification before using RflySim as planning truth |

Use RflySim's bundled Python for local SDK smoke tests:

```text
D:\PX4PSP\Python38\python.exe
```

The project and Windows Anaconda environments may miss RflySim dependencies such
as `cv2`. Do not treat that as an RflySim API failure.

Radar and navigation scope:

```text
RflySim3D reference display
  -> Mid360 point cloud request/receive
  -> local point cloud / occupancy processing
  -> ESDF or Voronoi planner waypoint output
  -> project-owned UE5 bridge and renderer design
```

The display, sensor, and map-to-path layers are now verified separately.
Autonomous navigation is still not complete until the generated path is fed into
a flight/control loop and inspected in MWORKS plus the project-owned UE5 scene.

Mid360 local-planning integration rule:

1. Treat `TypeID=23` Mid360 output as world-coordinate point cloud data, per the
   local RflySim SDK documentation.
2. Convert world points into the current vehicle-local frame before occupancy
   generation. Do not assume `x-forward/y-left` body-frame points.
3. A useful smoke run must show `occupied > 0`, `path_len > 1`, and meaningful
   `front_blocked` transitions in the log.
4. The current local-grid script is a render/control-channel prototype. It is
   not yet a PX4/CopterSim or MWORKS dynamics proof. Promote it only after the
   same planner drives the real controller interface.

Validated local smoke commands:

```text
D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_windows_smoke.py
D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_mid360_smoke.py
D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_esdf_path_smoke.py --json-output results\rflysim\esdf_path_smoke.json --path-output results\rflysim\esdf_path_smoke.npy
D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_esdf_path_playback.py
D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_mid360_reactive_avoidance.py --udp-port 9999 --spawn-test-obstacles
```

WSL networking note:

RflySim3D runs on Windows and listens for UDP commands on `20010 + windowID`.
When Codex runs in WSL, `127.0.0.1` points to WSL itself, not necessarily the
Windows RflySim3D process. For WSL-driven smoke tests, resolve the Windows host
with:

```bash
ip route | awk '/default/ {print $3; exit}'
```

Prefer Windows-side Python/PowerShell for official RflySim examples when they
use RflySim's bundled Python environment or Windows-only dependencies. Use WSL
only for lightweight UDP packets, documentation extraction, and project file
updates.

Reference-only RflySim playback path after native examples and MWORKS evidence
are stable:

```text
MWORKS raw/native result
  -> project bridge reads time, position, attitude, motor commands, local plan
  -> RflySimSDK UE4CtrlAPI sends vehicle pose/RPM to RflySim3D
  -> optional VisionCaptureApi requests Mid360/camera data for render-side display
  -> compare mechanisms against project-owned UE5 renderer
```

This is a reference/debug route, not a replacement for the current UE bridge
and not the final simulator product. Use it to learn timing, sensor, camera,
and scene conventions. Final delivery should run through the project-owned
`QuadrotorMworksBridge` and UE5 scene.

Project-local prototype bridge:

```bash
python3 scripts/stream_rflysim3d.py \
  results/official/example3_figure8/official_example3_linear_mpc_sysblock/raw/official_example3_linear_mpc_sysblock.csv \
  --dry-run \
  --max-frames 2
```

Actual RflySim3D playback requires the installed RflySim3D window to be open:

```bash
python3 scripts/stream_rflysim3d.py \
  results/official/example3_figure8/official_example3_linear_mpc_sysblock/raw/official_example3_linear_mpc_sysblock.csv \
  --rflysim-root /mnt/d/PX4PSP \
  --transport direct \
  --host 127.0.0.1 \
  --window-id 0 \
  --vehicle-type 3 \
  --map-name MapData \
  --resolution 1280x720w \
  --max-fps 60 \
  --fps 30
```

Coordinate and rotor-display policy:

1. Project raw CSV uses `z` positive upward. RflySim3D examples use NED, so the
   bridge sends `PosE=[x, y, -z]`.
2. Project raw CSV `u1..u4` are controller/motor command channels, not verified
   physical RPM. The bridge defaults to a constant visual RPM. Use
   `--motor-mode command_magnitude` only for render-side rotor-speed variation,
   not for evidence claims.
3. If RflySim3D shows the vehicle underground, oversized, or mirrored, fix the
   bridge coordinate/scale arguments. Do not alter MWORKS raw evidence.
4. The bridge defaults to `--transport direct`, which sends the documented
   RflySim3D UDP structures without importing the RflySim Python SDK. Use
   `--transport sdk` only after the local Python environment has the SDK
   dependencies such as OpenCV available.

Do not rely on RflySim for controller truth unless a future task explicitly
builds and validates a bidirectional co-simulation. For the current competition
evidence chain, RflySim can only be:

1. a visual renderer driven by MWORKS results;
2. a protocol/API reference for our own Unreal bridge;
3. a source of scene and sensor design ideas, subject to license and file-size
   checks.

Repository crawl priority:

| Priority | Repository / source | Decision |
| --- | --- | --- |
| P0 | User-installed RflySim3D/RflySimUE/RflySimUE5 folder | Highest value if it contains editable scenes or protocol docs |
| P0 | Local `references/Sunray/simulation/sunray_simulator/models` and `worlds` | Already available; convert SDF/DAE/PNG assets into UE scene registry |
| P1 | Cosys-AirSim | Best AirSim-line candidate if we want a maintained Unreal plugin/API reference |
| P1 | Colosseum | AirSim-line open-source Unreal robotics simulator; inspect for reusable plugin/scene patterns |
| P1 | CARLA-Air | Strong UE urban-scene candidate for air-ground scenes, but likely heavy and Linux-oriented |
| P1 | `RflySim/CopterSim` | Clone only if we need model/HIL/fault-injection reference; not for scene visuals |
| P1 | `RflySim/RflyExpCode` | Clone only if we need RflySim workflow examples or course docs |
| P2 | Flightmare / FlightGoggles | Unity render/physics decoupling references; useful conceptually, less direct for UE5 |
| P2 | Pegasus Simulator | High-quality Isaac Sim/PX4 reference, but dependency stack is heavy and not aligned with UE5 |
| P3 | RotorS / XTDrone / Gazebo-only stacks | Use for multi-UAV, ROS/PX4, planning organization; not for final visual layer |

Open-source simulator reference notes:

| Platform | Engine | Useful for this project | Main risk |
| --- | --- | --- | --- |
| Cosys-AirSim | Unreal | Maintained AirSim-style Unreal plugin, drone/car APIs, PX4/HIL-style visual simulation ideas | Still a simulator stack; we should port only rendering/API patterns, not replace MWORKS |
| Colosseum | Unreal/Unity support | AirSim successor-style robotics simulator; useful for API, sensor, and UE integration patterns | Need inspect asset availability and license before reuse |
| CARLA-Air | Unreal | High-fidelity urban environments with drones in a CARLA world; useful if we want city/road scenes | Heavy; likely overkill for competition video unless prebuilt assets are easy to reuse |
| AirSim | Unreal/Unity | Mature API and UE plugin design; useful for camera/weather/segmentation/control examples | Upstream Microsoft repo is archived/no longer updated, so avoid making it the main dependency |
| Flightmare | Unity | Strong example of decoupling physics and rendering; good design reference for MWORKS + external renderer | Unity, not UE; less direct asset reuse |
| FlightGoggles | Unity/ROS | Photorealistic HIL agile-flight visualization reference | ROS/Unity stack, not aligned with current UE5 bridge |
| Pegasus Simulator | Isaac Sim | Modern multi-UAV/PX4/sensor simulation reference | Isaac/Omniverse is too heavy for the current workflow |
| XTDrone / RotorS | Gazebo | Multi-UAV organization, PX4/ROS interface, swarm examples | Gazebo visuals are not the desired final video layer |

For the current project, do not crawl all of these by default. Crawl only when
the target use is clear:

```text
need UE API/plugin reference       -> Cosys-AirSim or Colosseum
need high-quality urban UE scene   -> CARLA-Air / CARLA asset route
need render/physics decoupling     -> Flightmare
need agile-flight gate/drone logic -> Agilicious / FlightGoggles references
need ROS/PX4 multi-UAV organization -> XTDrone / RotorS
```

If RflySim download remains blocked, the recommended fallback is:

```text
Cosys-AirSim or Colosseum for Unreal API/sensor/rendering patterns
  + local Sunray/AWS Gazebo assets for actual scene meshes
  + project-owned QuadrotorMworksBridge for MWORKS state playback
```

## Gazebo Architecture Lessons

Gazebo is useful as an architecture reference even if it is not the final video
renderer. The important lesson is separation of concerns:

```text
backend server:
  physics system + sensor system + user command system + scene broadcaster

frontend client:
  GUI plugins + 3D view + visualization widgets

shared libraries:
  gz-physics + gz-rendering + gz-sensors + gz-transport + sdformat
```

This is why Gazebo can run efficiently with many visual objects:

1. Physics is a compiled native plugin, not a symbolic Modelica/Sysblock
   equation system containing all visual geometry.
2. Visual meshes and collision geometry are separate. A detailed `.dae` mesh can
   be rendered while physics uses a simpler collision proxy.
3. The GUI/client can be separated from the server/backend. Headless or reduced
   GUI runs avoid rendering overhead during batch simulation.
4. Rendering is handled by a rendering library and plugins such as OGRE /
   OGRE2 / OptiX, not by thousands of dynamic model components in the solver.
5. Sensors are plugin systems. Rendering sensors such as cameras and GPU lidar
   use the rendering pipeline, while physics/contact sensors can use physics
   state. Sensor update rates can be lower than the physics step.
6. Transport messages broadcast pose, scene, sensor, and command data across
   process boundaries instead of coupling every visual object into the dynamics
   equations.

For this project, copy the architecture pattern, not Gazebo itself:

```text
MWORKS/Sysplorer:
  closed-loop dynamics, controller, planner, fault/safety truth

external renderer:
  UE5 scene, materials, camera, radar visualization, video

transport:
  TCP/UDP state frames or raw/native result playback

asset registry:
  visual mesh + material + collision proxy + truth obstacle id
```

Do not push dense terrain blocks, thousands of obstacle visuals, local radar
overlays, or camera behavior into the Sysplorer solver layer. Keep Sysplorer
animation as a low-complexity audit view and move video-quality rendering to
the external renderer.

Official Gazebo documentation entry points for study:

| Topic | Official source |
| --- | --- |
| Gazebo Sim architecture | `https://gazebosim.org/docs/harmonic/architecture/` |
| Gazebo Sim library and server/client usage | `https://gazebosim.org/libs/sim/` |
| Gazebo Classic distributed architecture reference | `https://get.gazebosim.org/tutorials?cat=get_started&tut=architecture` |
| Gazebo documentation source repo | `https://github.com/gazebosim/docs` |
| Gazebo Rendering library | `https://gazebosim.org/libs/rendering/` |
| Gazebo Sensors library | `https://gazebosim.org/libs/sensors/` |
| Gazebo Physics plugin docs | `https://gazebosim.org/api/physics/9/physicsplugin.html` |
| Gazebo Sim physics engine selection | `https://gazebosim.org/api/sim/8/physics.html` |

There is no single authoritative PDF manual for current Gazebo Sim. The
official manual is the versioned website plus the `gazebosim/docs` repository.
If a local copy is needed for offline study, clone only the docs repository or
only the `harmonic/` and `common/` folders; do not commit built HTML, generated
Sphinx output, videos, or downloaded Gazebo Fuel assets.

Before importing any external scene asset, check:

1. license and attribution;
2. single-file size under GitHub limit;
3. mesh scale and coordinate axes;
4. material and texture dependencies;
5. collision proxy availability;
6. actor count, triangle count, texture memory, and LOD/performance risk.

Generated primitives remain useful for:

- collision truth debugging;
- planner occupancy visualization;
- radar sector and local-map overlays;
- fallback review scenes when asset conversion fails.

They are not the target visual quality for the final video.

## Project

Open:

```text
unreal/MworksUnrealRenderer/MworksUnrealRenderer.uproject
```

From WSL, use the project-local launcher:

```bash
scripts/build_unreal_renderer.sh
scripts/open_unreal_renderer.sh
```

Override `UE_EDITOR` only if Unreal is installed somewhere other than
`D:\Program Files\Epic Games\UE_5.7`.

When C++ files under `unreal/QuadrotorMworksBridge/Source` change, close the
running Unreal Editor before rebuilding. Otherwise Windows keeps
`UnrealEditor-QuadrotorMworksBridge.dll` locked and UBT will fail at the link
step.

The project enables:

```text
unreal/QuadrotorMworksBridge
Skills/unreal-engine-mcp/FlopperamUnrealMCP/Plugins/UnrealMCP
```

Do not copy engine binaries, `Binaries/`, `Intermediate/`, `Saved/`, packaged
builds, or Derived Data Cache into Git.

## Data Flow

```text
MWORKS raw CSV / native result
  -> scripts/stream_unreal_udp.py
  -> udp://127.0.0.1:5005
  -> QuadrotorMworksUdpReceiverComponent
  -> QuadrotorMworksPlaybackComponent
  -> UAV actor, propellers, radar material, local plan spline, trajectory trail, follow camera
```

The packet schema is `quadrotor.unreal_state.v1`.

Current S0/S1 runtime packet contract:

| Field | Purpose | Evidence status |
| --- | --- | --- |
| `uav.position_m`, `uav.rpy_rad` | UAV body pose and attitude | evidence-backed when sourced from MWORKS raw/native result |
| `uav.motor_command` | propeller visual speed/angle driver | evidence-backed when sourced from controller/motor output |
| `reference.position_m` | current reference marker | evidence-backed when sourced from MWORKS raw/native result |
| `mission.start_m`, `mission.goal_m`, `mission.current_goal_m` | S1 start/goal/current-goal overlay | contract-ready; start/goal must be scenario-backed before formal claims |
| `perception.radar_origin_m`, `yaw_rad`, `near_radius_m`, `far_radius_m`, `fov_deg` | radar sector display | contract-ready; occlusion truth still belongs to planner/perception evidence |
| `local_known_map` | local observed/free/occupied/occluded-map display | render-contract placeholder until `evidence_backed=true` |
| `local_plan.points_m` | local plan spline | render-only when `source=preview_from_reference`; formal S1 requires planner-backed points and clearance evidence |
| `status`, `overlays` | controller/planner/safety state and quality flags | display contract; formal evidence must trace to MWORKS metrics/logs |

Do not claim S1 local avoidance or occlusion behavior from a packet where
`local_plan.render_only=true` or `local_known_map.evidence_backed=false`.

The UE bridge C++ receiver must compatibly parse the same packet contract into
Blueprint-readable frame data before a UI/HUD or visualization blueprint can
depend on it. Current receiver fields include mission start/goal/current-goal,
local-known-map metadata and cells, local-plan provenance flags, controller /
planner / safety status, and display quality flags. This is a source-level data
contract only; it is not viewport evidence until an Unreal MCP/editor review or
packaged runtime review confirms the fields drive the intended visuals.

## Map Export

Generate the render-only map JSON before building or refreshing the UE scene:

```bash
python3 scripts/export_unreal_scene_map.py --terrain-cell-m 1.0
```

Output:

```text
unreal/MworksUnrealRenderer/Content/MworksData/map_open_blocks_render_map.json
```

This JSON uses the same `map_open_blocks.yaml` random obstacle and L/T wall
expansion as the planner. It contains map bounds, terrain height grid, random
obstacle columns, wall boxes, start/goal, and material tags. It is display
input only and must not feed back into MWORKS.

For high-quality Unreal scenes, generate a second registry instead of only a
primitive map:

```text
scene_asset_registry:
  source_world: existing .world / handcrafted scenario profile
  asset_refs: mesh/material/texture references
  placements: transform + semantic tag
  collision_proxies: simplified boxes/capsules/convex hulls
  mworks_truth_link: obstacle_id / wall_id / gate_id
```

This registry is the bridge between SDF/world assets and Unreal actors. The
planner uses truth geometry from MWORKS/scenario files; Unreal uses the registry
to show a better-looking equivalent scene.

Preferred asset conversion path:

```text
Gazebo .world / .sdf
  -> parse model:// references, pose, scale, mesh URI
  -> resolve .dae/.stl/.png under references/Sunray/...
  -> convert mesh/materials through Blender/Assimp or UE import
  -> write scene_asset_registry with original source path and license tag
  -> spawn UE actors from registry
  -> link each visual actor to MWORKS obstacle_id / gate_id / terrain_id
```

Do not let the imported scene become the planning source of truth. If a tree,
building, gate, wall, or frame is visible in UE, it must have a corresponding
`world_geometry` primitive or collision proxy in the scenario file before it is
used for planning/collision claims.

## Playback

Stream the current planning raw CSV:

```bash
python3 scripts/stream_unreal_udp.py \
  results/planning/single_obstacle_astar_awff/sunray150_planning_open_blocks_linear_mpc_sysblock/raw/sunray150_planning_open_blocks_linear_mpc_height_profile_0p2_sensor_20hz.csv \
  --host 127.0.0.1 \
  --port 5005 \
  --scene-id planning_open_blocks_ue_review \
  --map-id map_open_blocks \
  --fps 20 \
  --near-radius-m 6 \
  --far-radius-m 9 \
  --fov-deg 120
```

Use `--dry-run --max-frames 2` to validate packets without sending UDP.

## UE Actor Setup

Minimum scene actors:

1. `AQuadrotorMworksPlaybackActor`
   - owns `QuadrotorMworksUdpReceiverComponent`;
   - owns `QuadrotorMworksPlaybackComponent`;
   - applies position/attitude from latest frame;
   - exposes propeller visual angles, `LocalPlanPointsUnreal`,
     `TrajectoryTrailUnreal`, reference point, and radar sector parameters.
2. `AQuadrotorMworksMapActor`
   - reads `Content/MworksData/map_open_blocks_render_map.json`;
   - instantiates stepped terrain, random obstacle columns, and L/T wall box
     segments with instanced static meshes;
   - exposes map bounds and obstacle counts;
   - serves as the stable anchor for generated map visualization.

Blueprints/materials should read from these actors rather than parsing raw CSV
again inside Unreal.

## Manual Review Checklist

Before recording or comparing against Sysplorer animation, check these items in
the Unreal viewport:

| Item | Expected result |
| --- | --- |
| UAV body | visible, centered on the MWORKS state, no scale mismatch |
| Propellers | four propellers visible and rotating from motor commands |
| Static map | terrain, random columns, and L/T walls visible from `AQuadrotorMworksMapActor` |
| Coordinate direction | start is lower-left, goal is upper-right, no X/Y swap |
| Local plan | spline starts at UAV center and stays in front of the current pose |
| Trail | history line follows the UAV, no detached yellow marker behavior |
| Radar sector | yaw follows UAV heading, radius and FOV match packet metadata |
| Camera | one follow view and one overview view are usable without manual dragging |
| Performance | playback is smooth enough for video; if viewport interaction stutters, export video rather than lowering MWORKS evidence fidelity |

If any item fails, fix Unreal rendering first. Do not alter MWORKS controller,
planner, or metrics to hide a renderer issue.

## Verification

Run:

```bash
python3 scripts/check_unreal_s0_s1_readiness.py
python3 scripts/audit_rflysim_maps.py
python3 scripts/build_rflysim_scene_registry.py
python3 scripts/plan_rflysim_scene_migration.py --scene-id rflysim_vision_ring
python3 scripts/check_unreal_bridge.py
scripts/build_unreal_renderer.sh
python3 scripts/export_unreal_scene_map.py --terrain-cell-m 1.0
python3 scripts/stream_unreal_udp.py <raw.csv> --max-frames 2 --dry-run
```

If Unreal MCP is available, open the project first, then run a read-only probe
such as project context or scene brief. If the wrapper hangs or the editor is
not listening, do not modify the scene through MCP; continue with source-level
changes and report the MCP state.

Before requesting manual viewport review, run:

```bash
python3 scripts/check_unreal_s0_s1_readiness.py --build --check-listener
```

`--check-listener` is expected to fail while the Unreal Editor MCP plugin is not
reachable on TCP `55557` from `UNREAL_HOST`, the WSL default gateway, or
`127.0.0.1`. In that case, source-level S0/S1 readiness can still be valid, but
viewport readiness is not proven.

Current WSL note: the Unreal editor plugin starts its TCP server on Windows
`127.0.0.1:55557`. A Python MCP server running inside WSL may not reach that
Windows loopback address directly. If `get_actors_in_level` reports
`Connection refused` while the UE log says `Server started on 127.0.0.1:55557`,
the plugin is loaded and the remaining issue is the WSL-to-Windows loopback
path. Use source-level C++ work or run the Python MCP server from Windows until
the plugin host binding is changed.

## Boundaries

- Coordinate conversion happens in Unreal only.
- Unreal may improve colors, terrain material, radar sector, local plan spline,
  trails, camera, and video capture.
- Unreal must not modify planner truth, controller output, metrics, or event
  logs.
