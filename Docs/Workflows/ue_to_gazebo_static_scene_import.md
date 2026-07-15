# UE To Gazebo Static Scene Import Workflow

> Repeatable workflow for importing an accepted Unreal scene into Gazebo
> Classic as a static physical scene base. This is a Scene Base workflow, not
> a runtime/control/localization/planner success workflow.

Status: active workflow, 2026-07-01 CST.

## 1. Use This Workflow When

Use this workflow when the task asks to:

```text
export a UE map or level for Gazebo
convert UE scene geometry into Gazebo Classic SDF/model assets
prepare Factory or another UE map as a static physical world
produce Gazebo-only visual review evidence for a static map
add a reversible Sunray/Gazebo scene-base entry after user acceptance
```

Do not use it for:

```text
UE runtime display or Data Bridge work
ROS/PX4/MAVROS/RViz runtime acceptance
SLAM, localization, planner, or controller success
Gazebo hand-built replacement maps
```

For UE display or runtime stream work, use
`Docs/Design/架构/04_展示与实验平台/UE渲染镜像桥接方案.md` and
`Docs/Workflows/unreal_renderer.md`. For current ROS1/Sunray runtime evidence,
use `Docs/Workflows/sunray_ros1_current_runtime_lane.md` and
`Docs/Workflows/sunray_ros1_execution_checklist.md`.

## 2. Claim Boundary

The maximum claim from this workflow after the current artifact has passed
human review is:

```text
This UE-derived Gazebo Classic static scene base is accepted for later
Gazebo/Sunray/RViz runtime checks.
```

Before human visual acceptance, the maximum claim is only:

```text
This UE-derived Gazebo Classic static scene candidate is prepared for
source/static review and must remain review_required.
```

It must not claim:

```text
ROS/PX4/MAVROS/RViz runtime success
SLAM/localization/planner success
controller performance
UE Data Bridge completion
spawn/free-space/sensor acceptance unless those later checks are run
closed-loop or competition runtime acceptance
```

The Gazebo world is a simulator scene and validation oracle. Planner prior-map
access is forbidden unless a future task explicitly changes the architecture.

## 3. Required Inputs

Before exporting or converting, identify and record:

```text
source_project
source_scene_id
source_map_package or map path
renderer_project if applicable
reviewed user intent or accepted source scene evidence
target Gazebo version and SDF version
coordinate contract: UE cm -> ROS/Gazebo m, axes, origin, frame_id
```

For the current Factory route, the design source of truth is:

```text
Docs/Design/架构/04_展示与实验平台/Factory地图导入与全局态势视图.md
```

## 4. Tool Preference

Prefer mature export and conversion tools. Agent-written code may orchestrate
tools, filter assets, write manifests, and run validation, but it must not
invent scene geometry.

| Stage | Preferred Tooling | Purpose |
|---|---|---|
| UE scene export | Unreal glTF Exporter, Unreal Python or commandlet routes | Export accepted level/static mesh assets while preserving source chain. |
| Mesh conversion | Blender headless Python; Assimp or meshoptimizer only if justified | Convert UE-derived geometry to simulator-friendly mesh formats. |
| Gazebo assembly | Gazebo Classic model structure and SDFormat mesh/include rules | Build `model.config`, `model.sdf`, and review world. |
| Static validation | XML parse plus `gz sdf -k` | Catch malformed SDF/model paths before runtime launch. |
| Human review | Gazebo-only static map screenshot/video and manifest | Let the user judge physical layout, scale, passages, obstacles, and start free-space. |

If the toolchain cannot export a usable scene, return a blocker. Do not replace
the map with hand-built boxes or a simplified proxy and call it L2.

## 5. Output Layout

Use a scene-specific result root:

```text
Results/unreal_scene_mapping/<scene_or_task_id>/
```

For L2 static imports, prefer:

```text
Results/unreal_scene_mapping/<scene_id>_l2_static_import/
  assets/
  manifests/
  gazebo_review/
    MANIFEST.json
    VERIFICATION.json
    SUMMARY.md
    worlds/
    models/
    logs/
    screenshots/
```

If the scene becomes an accepted reusable scene base, add a profile under:

```text
Config/gazebo/scene_profiles/
```

Optional Sunray/Gazebo launch entries belong under:

```text
Scripts/sunray/
```

These optional entries must be reversible and must not replace frozen baseline
Sunray launch files.

## 6. Execution Steps

### Step A: Source Scene Confirmation

1. Confirm the scene path or UE map identity from project docs, local assets,
   or user review.
2. Record the source project, map package, and asset chain in the manifest.
3. If the source scene is ambiguous, stop and ask the user before exporting.

### Step B: Export UE Geometry

1. Use an official or mature UE export route where possible.
2. Preserve the exported source artifact under `assets/`.
3. Record export tool, command, timestamp, and input map in `manifests/`.
4. Reject exported artifacts that are empty, tiny placeholders, or unrelated to
   the reviewed scene.

### Step C: Convert For Gazebo Classic

1. Convert the UE-derived artifact into Gazebo-compatible mesh assets.
2. Split large meshes into chunks when needed for Gazebo load and review.
3. Keep the conversion manifest with object counts, chunk counts, units, and
   bounding boxes.
4. Preserve enough material/visual information for user orientation, but
   prioritize physical geometry and collision fidelity over beauty.
5. Filter nonphysical display/background assets before generating Gazebo
   physical meshes. Examples include sky spheres, editor-only backgrounds,
   distant atmospheric shells, preview cameras, lights, and other objects that
   are not intended to be collision/world geometry. Every filtered object must
   be recorded in the conversion manifest with the exact name/pattern and the
   reason.

For Factory L2, `SkySphereMesh` is a required filter. Keeping it in the STL
conversion expands the Gazebo world bounds to about +/-16384 m and makes the
global coordinate audit meaningless. Filtering `SkySphereMesh` does not remove
factory walls, doors, floors, outdoor space, machines, or other physical scene
geometry.

### Step D: Assemble Gazebo Review World

1. Create `model.config`, `model.sdf`, and one review world SDF.
2. Set mesh paths relative to the Gazebo model structure.
3. Use SDF 1.6 for Gazebo Classic 11 unless the current runtime lane changes.
4. Avoid adding runtime vehicles or controller claims in this review world.

### Step E: Validate Headlessly

At minimum:

```powershell
@'
import json, pathlib, xml.etree.ElementTree as ET
for p in [
    pathlib.Path("Results/unreal_scene_mapping/<scene>/gazebo_review/MANIFEST.json"),
    pathlib.Path("Results/unreal_scene_mapping/<scene>/gazebo_review/VERIFICATION.json"),
]:
    json.loads(p.read_text(encoding="utf-8"))
ET.parse("Results/unreal_scene_mapping/<scene>/gazebo_review/worlds/<world>.sdf")
'@ | python -
```

Then run Gazebo SDF validation from Ubuntu-20.04 when Gazebo Classic is needed:

```bash
wsl -d Ubuntu-20.04 --exec bash -lc \
  'cd /mnt/c/Users/HP/Desktop/MoSim &&
   GAZEBO_MODEL_PATH="$PWD/Results/unreal_scene_mapping/<scene>/gazebo_review/models:$GAZEBO_MODEL_PATH" \
   gz sdf -v 1.6 -k Results/unreal_scene_mapping/<scene>/gazebo_review/worlds/<world>.sdf'
```

Expected output includes:

```text
Check complete
```

For Factory L2 or any large UE-derived map, run the coordinate audit before
user visual acceptance or runtime gate promotion:

```powershell
python Scripts\gazebo\audit_factory_l2_coordinate_contract.py `
  --conversion-manifest Results\unreal_scene_mapping\factory_l2_static_import\manifests\blender_chunked_stl_conversion_clean.json
```

The audit must show:

```text
axis_policy_ok: true
polluted_chunk_count: 0
Gazebo chunk bounds approximately match UE collision-truth bounds
anchor CSV written for origin, scene bounds, and spawn points
```

If the audit reports polluted chunks or mismatched bounds, do not promote the
scene profile and do not use old runtime results as proof of global coordinate
alignment.

For Factory L2, AABB and spawn anchors are not enough to prove the map is not
mirrored, shifted, or locally misaligned. The primary coordinate acceptance
surface is now a purpose-built calibration rig near the configured spawn frame.
It creates three non-symmetric rectangular line frames on the XY/XZ/YZ planes,
red X / green Y / blue Z directional ticks, and project-owned asymmetric blocks
that do not depend on Factory walls, doors, pillars, or machines. The UE
placement script, Gazebo overlay world, RViz MarkerArray publisher, CSV line
data, and marker CSV are derived from the same source contract:

```powershell
python Scripts\gazebo\build_factory_l2_calibration_frame_contract.py
```

The packet must contain:

```text
single JSON coordinate contract
UE Python visual-only placement script
Gazebo visual-only calibration-rig review world for backend/source isolation
RViz MarkerArray config and publisher command for backend/source isolation
CSV line segments in Gazebo meters and UE centimeters
CSV asymmetric calibration markers in Gazebo meters and UE centimeters
review_required status until backend checks pass and the user visually accepts
the UE display
```

The current calibration-rig review packet is:

```text
Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/FACTORY_L2_CALIBRATION_FRAME_CONTRACT.json
```

The user-facing review target is deliberately UE-only: the user checks the
calibration/audit frame, expected trajectory, and actual trajectory in the
Factory UE scene. Gazebo/RViz/logs remain backend evidence for the agent to
verify source trajectory, frame ids, units, and coordinate conversion. Do not
promote the clean Factory scene until backend source checks pass and the user
accepts the UE display.

Named UE landmarks are allowed only as an auxiliary context check after the
calibration frame exists. They are not the primary coordinate gate because
doors, pillars, walls, and machines have thickness and semantic boundaries:

```powershell
python Scripts\gazebo\build_factory_l2_landmark_review.py
```

The auxiliary landmark packet contains:

```text
UE-truth named landmark CSV
Gazebo visual-only landmark review world
RViz MarkerArray config and publisher command
review_required status until the user visually accepts the landmark placement
```

The current landmark review packet is:

```text
Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/FACTORY_L2_LANDMARK_REVIEW.json
```

The landmark set intentionally uses non-symmetric named UE objects such as
large gates, an office door, concrete pillars, columns, machines, stairs,
floor tiles, and an outdoor hangar. These landmarks are derived from UE
collision truth, not from Gazebo mesh inspection. A Y-axis sign error, origin
shift, or gross scale issue should be visible when these markers are overlaid
on the clean Gazebo/RViz review surfaces.

### Step F: Bounded Visual Review

Open UE for user visual acceptance. Do not require the user to visually compare
Gazebo or RViz during normal Factory coordinate acceptance. Gazebo/RViz are
opened only when the UE display is suspicious, the mismatch source must be
isolated, or the user explicitly asks to see them. Do not start PX4, MAVROS,
RViz, planners, or controller nodes as part of static scene review unless the
current task explicitly authorizes a bounded runtime gate.

For review evidence:

```text
capture or copy the accepted screenshot/video into gazebo_review/screenshots/
record screenshot sha256
write user review state into MANIFEST.json and VERIFICATION.json
summarize accepted/rejected/needs-fix in SUMMARY.md
```

If the user rejects the scene, keep the rejected evidence and record the exact
issue. Do not overwrite it with a silent replacement.

### Step G: Promote To Scene Profile

Only after user acceptance:

1. Create or update `Config/gazebo/scene_profiles/<scene>.json`.
2. Link the accepted manifest, verification, screenshot, and world path.
3. Add optional launch entries only if they are reversible and do not replace
   the baseline runtime lane.
4. Update the design document and board with the accepted boundary.

## 7. Verification Checklist

Before reporting completion, verify:

```text
JSON manifests parse
SDF/world XML parses
gz sdf -k passes for Gazebo Classic target
accepted screenshot/video exists when user review happened
sha256 recorded for accepted user-provided screenshot
scene profile points to existing paths
optional launch file parses as XML if created
claim boundary is explicit
board/design docs do not overclaim runtime success
git diff --check passes on touched text files
```

## 8. Factory L2 Current Reference

Factory L2 has two static-scene references after the 2026-07-02 coordinate
cleanup.

Historical user-accepted Gazebo-only visual reference:

```text
Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/
Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/screenshots/factory_l2_user_accepted_20260701.png
Config/gazebo/scene_profiles/factory_l2_static_sunray_scene.json
Scripts/sunray/factory_l2_sunray_px4_gazebo.launch
```

This reference remains useful as human visual evidence and as the source of the
previous Factory F1-F8 runtime runs, but it is not sufficient proof of full
global coordinate alignment because the original conversion included
`SkySphereMesh`.

Clean coordinate-audit candidate:

```text
Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/
Results/unreal_scene_mapping/factory_l2_static_import/manifests/blender_chunked_stl_conversion_clean.json
Results/unreal_scene_mapping/factory_l2_coordinate_audit_20260702_104942/FACTORY_L2_COORDINATE_AUDIT.json
Results/unreal_scene_mapping/factory_l2_coordinate_audit_20260702_104942/factory_l2_anchor_points.csv
Config/gazebo/scene_profiles/factory_l2_static_sunray_scene_clean_candidate.json
```

Current clean status:

```text
coordinate_audit_passed_visual_review_required
```

The clean candidate passed source/static coordinate audit and SDF validation,
with `SkySphereMesh` filtered as nonphysical background geometry. It must still
be visually accepted by the user before it replaces the primary Factory scene
profile. After promotion, rerun the smallest required runtime gates instead of
claiming old F1-F8 results as clean-map runtime proof.

Current primary calibration-rig review reference:

```text
Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/
Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/FACTORY_L2_CALIBRATION_FRAME_CONTRACT.json
Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/factory_l2_calibration_segments.csv
Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/factory_l2_calibration_markers.csv
Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/worlds/factoryenvironmentcollect_l2_static_calibration_review.sdf
Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/rviz/factory_l2_calibration_frames.rviz
Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/ue/place_factory_l2_calibration_frames.py
Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/ros/publish_factory_l2_calibration_frames.py
```

Status:

```text
calibration_frame_review_required
```

Current auxiliary landmark review reference:

```text
Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/
Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/factory_l2_landmark_anchors.csv
Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/worlds/factoryenvironmentcollect_l2_static_landmark_review.sdf
Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/rviz/factory_l2_coordinate_landmarks.rviz
```

Status:

```text
landmark_review_required
```

This proves only Gazebo Classic static physical scene-base acceptance. The next
engineering gate is a separately authorized bounded Factory/Sunray
spawn-free-space and MID360/RViz sensor check.
