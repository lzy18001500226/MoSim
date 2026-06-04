# Sunray150 Component Material Evidence

Status: working evidence matrix for the next material pass. This file is not
UE runtime evidence.

## Source Set

- YunDrone wiki, `单目相机`: confirms the Sunray-150 stack uses a monocular
  camera module and documents the camera as a separate hardware component.
- YunDrone wiki, `Sunray150 硬件整体介绍`: confirms the basic version uses
  the model `Sunray-150`, carbon-fiber material, overall dimensions
  `150 mm x 150 mm`, wheelbase `150 mm`, takeoff weight below `250 g`, and
  `N150` as the onboard computer.
- YunDrone wiki, `Sunray150 硬件整体介绍`: confirms the 3D-LiDAR version adds
  Livox MID-360 and an N150 onboard computer, uses carbon-fiber material, has
  overall dimensions `180 mm x 180 mm`, and has takeoff weight below `500 g`.
- YunDrone wiki, `动力系统`: confirms the frame material direction as
  carbon fiber for the main structure, 7-series aviation aluminum alloy for
  support parts, and chromium-molybdenum steel for connections/fasteners. It
  also confirms the propulsion-system component set as battery, ESC, motor,
  and propeller.
- Local reference images:
  `References/CUAV/Sunray150-正.png`,
  `References/CUAV/Sunray150-侧.png`,
  `References/CUAV/MId360.png`,
  `References/CUAV/motor.png`,
  `References/CUAV/电池.png`,
  `References/CUAV/电调.png`,
  `References/CUAV/V6X.png`,
  `References/CUAV/ORIN NX.png`.
- Local CAD/DAE/SDF source:
  `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/150.dae`,
  `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/sunray_cw.stl`,
  `References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/sunray150_with_mid360.sdf.jinja`.
- User-supplied Taobao item URL:
  `https://item.taobao.com/item.htm?id=901786241859...`.
  Browser/tool access is unreliable from this environment, so do not cite it as
  confirmed evidence unless the user supplies screenshots or local saved media.

## Component To Material Targets

| Component family | DAE/source names | Target appearance | Current risk |
|---|---|---|---|
| Main structural plates | `MAIN_STRUCTURE`, `TOP_PANNEL`, `BOT_PANNEL`, flat arm/frame plates | dark woven carbon fiber, satin/semigloss clear coat, visible diagonal weave at close range | many objects still fall through as light grey CAD; carbon texture not visible enough |
| Aluminum standoffs/columns | `AL_COLUMNS*`, `SPACER`, `STAND`, `COLUMN` | gold/yellow anodized 7-series aluminum, metallic, brushed/satin, not plastic yellow | early classifier allowed `AL_COLUMNS*\\MAIN_STRUCTURE` to be treated as carbon/neutral in some views |
| Steel screws/nuts/washers | `SCREW*`, `HEX_SOCKET*`, `HEX_NUT*`, `WASHER*`, `BOLT*` | dark chromoly/alloy steel, visible metal highlights and hex/socket recesses | acceptable direction, but close-up lighting can crush detail |
| MID-360 scanner | standalone `AUDIT_STANDALONE_MID360_*` plus Livox visual | blue glossy optical dome/window, off-white/silver-grey housing, black connector/base, small screw details | housing too white; connector close-up has black artifact/occlusion |
| MID-360 protection frame | `MID360_PROTECT_ARC*`, `MID360_PROTECT_ARC_CONNECTOR*`, `PROTECTIVE_RING` | matte/satin black or dark grey protective plastic/composite/metal, not blue glass | acceptable direction, but large grey arcs still look like CAD if fallback material leaks in |
| Monocular/USB cameras | `FRONT_CAMERA`, `BOTTOM_CAMERA`, `CAMERA_SHIM`, `FRONT_CAMERA_CONNECTOR` | small black polymer camera body, dark lens glass, subtle bevel/edge highlights; brackets dark carbon/plastic | front camera close-up currently too dark/grey to audit |
| N150 / PCB / electronics | `N150_AllCATPart*`, `PCBModel`, `ESC_SPEEDYBEE`, `MAIN_BOARD` | black or dark green soldermask, copper traces/pads, small black IC packages, nickel connector shells | many boards/connectors still grey; need stronger PCB/connector distinction |
| USB/HDMI/RJ45/connectors | `A_USB_*`, `HDMI connector`, `CONNECTOR`, `MANIFOLD_SOLID_BREP` near cables | nickel/silver shells, black plastic cores, tiny metal pins; readable without pure black blocks | current material mapping collapses several connectors into grey or black holes |
| Cables/wires | `CABLE_*`, `WIRE*` | black rubber/silicone cable with red/blue/yellow signal leads where exposed | colored hints are readable, but routing is still overlay-like |
| Motors | `MOTOR_2104_3000KV*`, `MOTOR_STATOR`, `Stator Wire` | black/dark anodized motor bell, copper windings, steel screws, subtle brand/decal cues | motor/prop close-up underexposed; motor reads as black block |
| Propellers | accepted `sunray_cw.stl` tri-blade source | dark smoked composite/plastic with subtle fiber/edge streaks; no white audit-color faces | rendered blades show grey/white patches; material/lighting needs correction |
| Battery / payload block | `YUNDRONE_4S1P`, battery-like block names | black heat-shrink pack with mild wrinkle/label strip, not flat grey | currently too grey/black depending on view |
| Landing gear / guards | `LAND_GEAR`, guard/ring parts | dark smoked plastic/carbon-composite or black protective structure depending component | some large guard surfaces read as grey CAD |

## Toolchain Interpretation

- Material Maker is useful as a procedural graph model for repeatable carbon,
  rubber, plastic, metal, PCB, and lens texture maps.
- ArmorPaint is the next escalation when procedural maps still look generic:
  UV unwrap first, then hand-paint/bake component-specific maps.
- xatlas is the UV-atlas route for unique per-object painting/baking when DAE
  source UVs or material slots are insufficient.
- Blender remains the assembly/material-node/render staging tool. In this
  environment, use background Blender commands only until GUI launch is
  explicitly repaired.

## Next Material Pass Requirements

1. Preserve accepted assembly geometry:
   MID-360 scale `0.833527`, accepted radar placement, tri-blade propeller
   source/orientation, and propeller final `translation_z=-0.014052 m`.
2. Remove light-grey fallback from visible primary components. Any remaining
   neutral grey object must be listed in the manifest with a reason.
3. Re-light close-ups so black components keep edge detail and metal/glass
   highlights without turning frame plates grey.
4. Generate audit views for:
   whole aircraft, MID-360, front camera/electronics, PCB/connectors/cables,
   carbon/standoffs, and motor/propeller.
5. Do not export/import into UE until the user manually accepts Blender
   material appearance.
