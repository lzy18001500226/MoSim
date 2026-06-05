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
| Propellers | accepted `sunray_cw.stl` tri-blade source | smoked translucent plastic with subtle molded/edge streaks; semi-transparent grey, not opaque black and not white audit-color faces | current component render no longer washes out to white; needs manual acceptance and later photo-real surface refinement |
| Battery / payload block | `YUNDRONE_4S1P`, battery-like block names | black heat-shrink pack with mild wrinkle/label strip, not flat grey | currently too grey/black depending on view |
| Landing gear / guards | `LAND_GEAR`, guard/ring parts | dark smoked plastic/carbon-composite or black protective structure depending component | some large guard surfaces read as grey CAD |

## Toolchain Interpretation

2026-06-04 workflow correction after local open-source study:

- `Docs/Skills/Unreal/sunray-pbr-material-workflow/SKILL.md` is now the
  required entry point before further Sunray150 material edits.
- Blender-MCP already contains a Poly Haven PBR path:
  `get_polyhaven_categories`, `search_polyhaven_assets`,
  `download_polyhaven_asset`, and `set_texture`. Its addon code builds node
  materials from texture maps and wires albedo/base color, roughness,
  metallic, normal, displacement, AO, and packed ARM maps. This is the
  preferred route for standard library materials and HDRI lighting.
- Material Maker is the procedural graph route for repeatable carbon fiber,
  rubber, plastic/composite, metal, PCB, cable, lens, and battery heat-shrink
  maps when a suitable library material is not specific enough.
- ArmorPaint is the escalation path when procedural/library maps still look
  generic or need labels, connector faces, scratches, port details, and
  component-specific painting. UV unwrap first, then paint/bake.
- xatlas is the UV-atlas route for STL/DAE pieces without usable UVs before
  per-object painting or baking. Do not treat UV-less object-wide colors as
  final texture work.
- Blender remains the assembly/material-slot/node/render/export staging tool.
  It is not the justification for inventing fake material appearance without
  physical part evidence.

Rejected route:

- Simple `Base Color` edits, broad material overrides, or lighting tricks are
  not accepted final texturing. They may be temporary audit markers only.
- Whole-aircraft renders are final consistency checks, not the optimization
  surface for component material work.

## Next Material Pass Requirements

1. Preserve accepted assembly geometry:
   MID-360 scale `0.833527`, accepted radar placement, tri-blade propeller
   source/orientation, and propeller final `translation_z=-0.014052 m`.
2. Start from material identity and PBR source selection, not manual color
   tuning. A valid material route should identify library/procedural/painted
   maps and include at least albedo/base color, roughness, and normal/bump
   detail when the component surface needs texture.
3. Remove light-grey fallback from visible primary components. Any remaining
   neutral grey object must be listed in the manifest with a reason.
4. Re-light close-ups so black components keep edge detail and metal/glass
   highlights without turning frame plates grey.
5. Generate audit views for:
   whole aircraft, MID-360, front camera/electronics, PCB/connectors/cables,
   carbon/standoffs, and motor/propeller.
6. Do not export/import into UE until the user manually accepts Blender
   material appearance.

## 2026-06-04 PBR Minimum Loop Start

Scope:

- This pass is limited to two component families: carbon frame plates and the
  accepted tri-blade propellers.
- It does not change accepted geometry: MID-360 four-hole fit, propeller source
  `sunray_cw.stl`, propeller orientation `flipped_around_screw_axis`, and
  propeller final `translation_z=-0.014052 m` remain untouched.
- It does not export to UE.

Implemented file-chain correction:

- `Scripts/UE5/assets/generate_sunray150_pbr_texture_set.py` generates
  deterministic map sets under
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/`.
- `Scripts/UE5/assets/render_sunray150_component_material_reviews.py` now uses
  explicit image texture nodes for the carbon-frame component pass and the
  smoked-propeller component pass instead of relying on emission-only carbon
  review or a pure procedural-noise propeller override.

Verified generated maps:

| Component | Map set | Verification |
|---|---|---|
| Carbon frame | `sunray150_carbon_fiber_base.png`, `sunray150_carbon_fiber_roughness.png`, `sunray150_carbon_fiber_bump.png` | 1024x1024 maps generated; base color mean approximately `[20.35, 21.73, 20.97]`, roughness range `86..207`, bump range `38..231`. |
| Tri-blade propeller | `sunray150_smoked_propeller_base.png`, `sunray150_smoked_propeller_roughness.png`, `sunray150_smoked_propeller_bump.png` | 1024x1024 maps generated; base color mean approximately `[22.08, 23.08, 22.46]`, roughness range `133..191`, bump range `98..149`. |

Current status:

- `python3 -m py_compile` passes for the texture generator and component-review
  renderer.
- File-level minimum-loop check passes:
  `python3 Scripts/UE5/check_sunray150_pbr_miniloop.py`.
- Blender 5.0 background render passes for `carbon_frame` and
  `tri_blade_propeller`.
- Latest component close-ups:
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/carbon_frame.png`
  and
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/tri_blade_propeller.png`.
- The project WeChat adapter attempted to notify task start but cc-connect
  failed with `internal_api_unavailable` / Unix socket `connection refused`
  even after bounded restart. Recovery evidence:
  `Results/coagent_gateway/recovery/weixin_recovery_required_20260604_141017.json`.
  The latest manual-review packet retry also failed with Unix socket
  `connection refused`; recovery evidence:
  `Results/coagent_gateway/recovery/weixin_recovery_required_20260604_150646.json`.

User material correction:

- The accepted propeller should be treated as smoked/transparent plastic, not
  opaque black composite. Update future renders toward grey translucent plastic
  with visible thickness/edge shading and subtle molded texture.
- 2026-06-04 follow-up: the first transparent-plastic attempt still rendered
  nearly white under Cycles. The review material was changed away from
  glass-like transmission and toward smoked injection-molded plastic: explicit
  dark grey plastic shader, low transparent mix, no transmission, lower
  component exposure, and reduced component light energy. The final minimum
  loop pass keeps all three generated PBR audit maps connected for the
  propeller: base color, roughness, and bump. Latest close-up:
  `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/tri_blade_propeller.png`;
  image mean approximately `[33.07, 33.18, 33.09]`, extrema `0..104`.
  This is acceptable as a material-class correction candidate for manual
  review, but still not final photo-real texture approval.

## 2026-06-04 Component-First Pass Notes

Workflow correction has been applied: material work is now component-family
first. Whole-aircraft renders are no longer the primary optimization target.
Unknown part identity must be clarified through WeChat before applying a final
material.

### MID-360 Sensor

Current review image:

```text
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/mid360_sensor.png
```

Internal status: ready for manual visual audit.

Observed improvements:

- Optical dome/window is now dark blue/teal with glossy reflection instead of
  pale cyan/white.
- Housing is rendered from an angled view so the side heat-sink grooves,
  front connector, screws, and `LIVOX` marking are visible.
- The image is a Blender component material audit, not UE runtime evidence and
  not a final exported asset.

Remaining risks:

- The `LIVOX` marking is currently a review decal, not a manufacturer-authored
  UV texture baked into a final asset.
- Final UE import/export remains gated until the full component material pass
  is manually accepted.

2026-06-04 user review correction:

- The MID-360 radar window and base must be researched as a single product
  before further tuning. Do not tune the whole UAV first.
- Official Livox MID-360 product imagery and local `References/CUAV/MId360.png`
  show a dark blue/teal coated optical dome/window with small glossy highlights
  and darker edges, not a milky/pale glass cap.
- The top cap/label area should read as dark/black with `LIVOX`, not as a large
  white disk.
- The lower housing/base should read as light silver-grey sealed industrial
  housing with satin metallic or coated-metal sheen, visible front connector,
  screws, and strong side heat-sink groove shadows.
- Official product data confirms MID-360 is a compact sealed outdoor LiDAR
  (`65 x 65 x 60 mm`, about `265 g`, `IP67`), supporting an industrial
  metal/coated housing interpretation rather than flat white plastic.

### MID-360 Protection Frame

Current review image:

```text
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/mid360_protection_frame.png
```

Internal status: stage evidence only, not final texture approval.

Observed improvements:

- The target object set is verified as `MID360_PROTECT_ARC*`,
  `MID360_PROTECT_ARC_CONNECTOR*`, and `MID-360_4_ASM*`.
- The close-up no longer shows the protection frame as white CAD in the
  controlled audit view.

Remaining risks:

- This render uses a stable dark-grey component-review material to avoid
  Blender 5 color-management/light washout. It proves component identity and
  dark protective-frame intent, but it still needs a more physical satin
  plastic/composite material pass before final approval.

### Carbon Frame / Plates

Current review image:

```text
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/carbon_frame.png
```

Internal status: ready for manual style audit, not final material approval.

Observed progress:

- `carbon_frame` selection has been corrected. It now matches only four
  carbon-plate objects:
  `DAE_FULL_MAIN_STRUCTURE.1_MAIN_STRUCTURE`,
  `DAE_FULL_TOP_PANNEL.1_TOP`,
  `DAE_FULL_Fill.1`, and `DAE_FULL_Fill.1_ncl1_1`.
- The previous white render was not caused by aluminum standoffs or other
  objects being mixed into the carbon component pass.

Resolved issue:

- The source carbon texture-node route still rendered as white under this
  Blender audit path, so the component review now uses a controlled procedural
  carbon material based on generated coordinates. This is an audit material,
  not a final baked UE material.

Remaining risks:

- The current carbon surface reads as dark carbon with visible fine diagonal
  texture, but it is still procedural and slightly regular. If the user rejects
  the style, the next step is xatlas/UV unwrap plus photo/painted texture
  baking rather than more broad color tuning.

### Aluminum Standoffs / Columns

Current review image:

```text
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/aluminum_standoffs.png
```

Internal status: ready for manual component audit.

Observed progress:

- Component isolation now hides non-mesh review decals by default. The previous
  `LAVA YUN DRONE` text leakage into the aluminum-only render is fixed.
- Target selection matches 32 aluminum-column objects from the
  `AL_COLUMNS`, `AL_COLUMS`, and `YUNDRONE_AL_COLUMNS` families.
- The material review override was darkened and re-lit to reduce washout. The
  standoffs now read as satin gold anodized aluminum rather than white/yellow
  overexposed plastic.

Remaining risks:

- This is still a Blender audit material, not a final baked UE material.
- Steel screws, nuts, washers, and other fasteners are intentionally excluded
  and must be reviewed as a separate component family.

### Steel Fasteners / Nuts / Inserts

Current review image:

```text
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/steel_fasteners.png
```

Internal status: ready for manual component audit.

Observed progress:

- Target selection is material-name driven, not broad keyword driven. It
  matches 99 objects with material
  `Sunray150_Texture_Dark_Chromoly_Steel_Screws`.
- This avoids false positives such as tri-blade objects whose names contain
  `screw_axis`.
- The audit material was darkened and re-lit after the first render washed out
  to bright silver. The current pass keeps screw/nut shapes, hex/socket
  details, and controlled metal edge highlights.

Remaining risks:

- This is still a Blender audit material, not a final baked UE material.
- Some long insert/lead-screw-like objects are in the same source steel
  material family. If the user wants only visible external screws/nuts, this
  component family should be split again into external fasteners and internal
  inserts.

### Front Monocular / USB Camera

Current review image:

```text
UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/front_camera.png
```

Internal status: not ready for manual audit.

Observed progress:

- Object identity was narrowed to the local front-camera region:
  `front_usb_camera_lens_glass_overlay`,
  `DAE_FULL_FRONT_CAMERA_PartBody`, and
  `DAE_FULL_FRONT_CAMERA_CONNECTOR.1`.
- Broad `FRONT_CAMERA` matching was rejected because it also pulls in
  `CABLE_FRONT_CAMERA...` USB cable/connector geometry.
- `CAMERA_SHIM` was removed from this pass because its bounding box center is
  near `y=0.027 m`, while the front camera is near `y=0.094 m`; it should be
  reviewed separately or with a broader camera-mount assembly view.

Blocking issue:

- The first front-camera close-ups rendered black/empty because the review
  camera was too close and Blender's default camera near clipping plane removed
  the target geometry. The component-review camera now uses
  `clip_start=0.001`.
- After the near-clip fix, the debug render shows the target at both left and
  right image edges, so the current component camera framing is still wrong.
  Do not request manual review for this component until the close-up framing is
  repaired.

### N150 / PCB / Electronics Correction

2026-06-04 user correction:

- Do not treat N150 as a closed external shell for material review. The visible
  assembly should be interpreted as a disassembled/exposed onboard-computer
  and electronics stack.
- The current `n150_stack_boards.png` and `esc_board.png` are not accepted
  review evidence. They show simplified pale/grey board plates rather than
  believable exposed PCB, heat-sink, connector, component, soldermask, and
  small-package detail.
- Next pass must research each concrete visible electronics part before
  material work: N150 board/heat-sink/interface stack, ESC board, USB/HDMI/NGFF
  connector shells/cores, cable harnesses, and camera module. If the exact part
  identity is unclear, ask the user instead of guessing from the object name.
- YunDrone official `机载电脑` page confirms the N150 is used on Sunray-150,
  and that its shell is removed during assembly to reduce aircraft weight. It
  also lists the visible/functional interface set: PD power, HDMI, USB-C,
  RJ45, and three USB 3.2 ports. This supports treating the model as an exposed
  board/interface/heat-sink stack instead of a closed mini-PC shell.
- Additional user correction: the N150 outer shell should be treated as
  removed. The visible part materials must be derived from the actual N150
  components, local model objects, and online references rather than a generic
  grey box.
- Object inspection of the accepted DAE audit scene shows that the N150 area is
  not a single shell object. It contains `N150_AllCATPart.1_Part1/Part2` board
  plates, `A_USB_9P`, `A_USB_24P`, `HDMI connector`, `PJ311D`, `A_NGFF`,
  `C-3-1734795-2`, `TN_MTS400_29-3462_M2_2242`, and `TURBO_FAN` geometry.
  This supports splitting material review into visible cooling/interface
  stack, connector-core close-up, and internal/exposed PCB material checks.
- Current DAE visibility caveat: the visible top of the N150 stack is dominated
  by a blower/fan and heat-sink-like fin assembly, while the lower PCB layers
  are partly hidden by aircraft plates and the N150 cooling structure. Do not
  claim that one close-up proves all exposed-board details. Use separate review
  passes: `n150_cooling_storage` for the visible cooling/storage layer,
  `n150_ports` for interface shells/cores, and a dedicated PCB/board pass with
  the top cooling geometry hidden if board-surface material must be audited.
- Generated `decal_n150_*` overlays are review aids for PCB/IC/M.2/connector
  material intent. They are not accepted mechanical geometry, and obvious
  floating or overlong marks must be removed before manual review.
