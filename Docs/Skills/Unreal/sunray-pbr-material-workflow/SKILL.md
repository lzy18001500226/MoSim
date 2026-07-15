---
name: sunray-pbr-material-workflow
description: Use when creating, reviewing, or repairing Sunray150 / YunZong UAV Blender, Unreal, or DAE/FBX/glTF visual materials. This skill enforces component-first PBR texturing, material-library use, UV/atlas decisions, and realistic audit gates before UE import.
---

# Sunray PBR Material Workflow

Use this skill before changing Sunray150, MID-360, propeller, camera, PCB,
connector, cable, motor, battery, or frame materials.

## Hard Rules

1. Do not treat a `Base Color` edit as final texturing.
2. Do not tune whole-aircraft appearance before the relevant component family
   passes close-up review.
3. Do not change accepted geometry while doing material work:
   - MID-360 mount/scale accepted by four-hole fit;
   - tri-blade propeller source `sunray_cw.stl`;
   - propeller orientation `flipped_around_screw_axis`;
   - propeller final `translation_z=-0.014052 m`.
4. If part identity is unclear, ask the user through the normal project
   channel before applying a final material.
5. UE export/import is gated until Blender component material audits pass.
6. Current accepted Sunray150 visual baseline: the user has manually accepted
   the DAE-derived Blender material route from task 005. Do not run additional
   whole-aircraft grey-CAD/PBR repaint passes or add new material overlays
   unless the user explicitly reopens material work. The 006 whole-aircraft
   pass is a rejected regression/rollback incident; `pbr006_*` objects,
   materials, overlays, and manifests are not accepted visual baseline
   evidence.

## Current Acceptance Boundary

- Accepted for now: the 005 DAE-derived Blender asset/material route as the
  Sunray150 visual asset baseline.
- Rejected/superseded: 006 whole-aircraft material optimization and any
  `pbr006_*` visual overlays/materials unless a later user review explicitly
  accepts them.
- Required rollback evidence for the 006 incident: verify the restored Blender
  audit asset contains zero `pbr006_*` objects and zero `pbr006_*` materials,
  then write a concise return packet that says rollback complete. Do not use
  the 006 contact sheet, manifest, or rendered images as accepted material
  evidence.
- Next allowed Sunray work without another user material request: bounded
  packaging, review-display, UE import/export preparation, or route hygiene
  around the accepted asset. Do not keep tuning appearance.

## Department Planning Gate

When the Sunray150 asset/PBR department receives a PMO task, it must plan the
work before editing assets and must return these fields:

```text
department_local_goal
critical_path_steps
parallelizable_slices
subagent_plan
subagent_plan_reason
subagents_used
verification_gates
manual_review_or_blocker_triggers
expected_engineering_outputs
actual_engineering_outputs
claim_boundary
```

This is not a requirement to use at least one sub-agent. Use disposable
sub-agents only for safe independent slices such as read-only material-source
classification, component identity checks, or post-render image review. If no
sub-agent is used, record `available_but_not_useful`, `unavailable`, or
`unsafe` with a concrete reason.

Completed Sunray/PBR work must produce real visual evidence: Blender/UE asset
edits, material manifests, texture/PBR maps, rendered component close-ups,
contact sheets, or explicit failed-review images. JSON packets, ledger rows,
and progress notes are control-plane evidence only. If the output needs human
review, ask PMO to open/display the image or Blender scene instead of returning
only a path.

## Required Loop

```text
identify component objects
  -> confirm physical part and source evidence
  -> classify material family
  -> choose PBR route
  -> verify UV/scale suitability
  -> assign texture-node material
  -> render isolated close-up
  -> record pass/fail and evidence
```

## PBR Minimum

A final material should normally include:

- albedo/base color;
- roughness;
- normal or bump detail;
- metallic for metal parts;
- optional AO/height/displacement when the mesh and target engine support it.

Color maps use sRGB. Roughness, metallic, AO, normal, height, and packed ARM
maps use Non-Color data. Normal maps must go through a normal-map node, not
directly into color.

## Toolchain Roles

Use existing material/tool libraries before hand-making fake colors.

| Tool/source | Role |
|---|---|
| `Docs/Skills/Blender-MCP` | Poly Haven search/download/apply path for CC0 PBR textures and HDRI lighting. Its node path handles albedo, roughness, metallic, normal, displacement, AO, and ARM maps. |
| `References/Blender/material` | Material Maker: procedural graph source for repeatable carbon, plastic, rubber, PCB, cable, metal, glass, lens, and heat-shrink materials. |
| `References/Blender/armorpaint` | ArmorPaint: hand retouching and component-specific 3D PBR painting after UV unwrap when generic/procedural textures still look wrong. |
| `References/Blender/xatlas` | UV atlas generation for STL/DAE pieces without usable UVs before painting or baking. |
| `References/Blender/blender` | Assembly, material slots, node hookup, preview rendering, export staging. |

## External Sources To Prefer

Use official/high-quality PBR references before ad-hoc parameter guesses:

- Blender Principled BSDF manual:
  `https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html`
- Unreal Engine physically based materials:
  `https://dev.epicgames.com/documentation/unreal-engine/physically-based-materials-in-unreal-engine`
- Poly Haven CC0 texture/HDRI/model library:
  `https://polyhaven.com/`, `https://polyhaven.com/license`
- ambientCG CC0 PBR material library and API:
  `https://ambientcg.com/`, `https://docs.ambientcg.com/api/`

If more local references are needed, ask the user to crawl repositories or
asset libraries that provide source maps/material graphs, not screenshot-only
showcases.

## External Source Adoption Rule

For Sunray150 material realism work, do not crawl broad open-source code
repositories just because a component looks grey. Use this order instead:

1. Reuse local project assets and tools first:
   `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/`,
   `References/Blender/material`, `References/Blender/armorpaint`,
   `References/Blender/xatlas`, and `Docs/Skills/Blender-MCP`.
2. Use CC0 PBR libraries for generic material families only: carbon weave,
   rubber, black plastic, brushed/nickel metal, rough metal, glass/lens,
   heat-shrink, cable insulation, and PCB-like soldermask. Preferred sources
   are Poly Haven and ambientCG.
3. Use YunDrone/Sunray/N150/Livox official or vendor images as visual
   references only. They can justify component identity, port layout, and
   material targets, but they are not texture files unless an explicit license
   permits reuse.
4. Use Material Maker-style procedural generation for repeated materials that
   need project-specific scale or pattern, especially carbon fiber, cable
   rubber, black polymer, heat-shrink, PCB soldermask, pads/traces, and subtle
   molded plastic noise.
5. Use xatlas plus ArmorPaint/Blender texture paint only when a component needs
   part-specific detail: labels, port faces, pins, M.2 label cues, IC packages,
   connector cores, scratches, or board markings.

Reject these sources by default:

- screenshot-only showcase projects without source textures/material graphs or
  clear license;
- marketplace or Sketchfab-style models/assets with unclear reuse rights;
- large Unreal/game sample repositories that do not provide component-level
  PBR maps useful to this aircraft;
- another mirror of Blender/Material Maker/ArmorPaint/xatlas when the local
  copy is already present;
- tutorials that only tune Base Color without roughness/normal/material-slot
  evidence.

## Route Selection

Use this decision rule:

```text
standard material exists in library
  -> use Poly Haven / ambientCG / existing local PBR maps
material is repeated but needs product-like procedural structure
  -> generate Material Maker-style procedural PBR maps
component needs labels, ports, board features, wear, or part-specific detail
  -> xatlas/UV unwrap, then ArmorPaint or Blender texture paint/bake
mesh has no separable material slots
  -> split/classify object groups first, or record limitation before coloring
```

Examples:

- propeller: material class first; use smoked translucent plastic PBR with
  subtle molded streaks, not opaque black carbon/composite and not manual
  white/grey color tuning;
- carbon plate: use carbon-fiber weave map/procedural weave with physical
  scale; if the weave swims or stretches, fix UVs before tuning colors;
- connector shell: use nickel/brushed metal material for shell and black
  plastic for core; if one mesh contains both, split/assign material slots or
  record limitation;
- PCB/electronics: generic green/black rectangles are insufficient; use board
  soldermask, copper/pad/trace, IC package, connector, fan/heatsink materials
  as separate slots where geometry allows.

## Sunray150 Material Targets

| Component | Target material route |
|---|---|
| Carbon plates/frame | woven carbon-fiber PBR with clear-coat/satin roughness and visible weave scale. |
| Propellers | smoked translucent plastic PBR; semi-transparent grey material with subtle molded streaks; never opaque black or white audit color. |
| MID-360 dome/window | glossy dark blue/teal coated optical surface, with edge darkening and controlled reflections. |
| MID-360 housing | light silver-grey sealed industrial coated-metal/satin-metal housing with groove shadows. |
| MID-360 bracket/frame | dark matte/satin plastic/composite/metal, not blue glass. |
| Aluminum standoffs | gold anodized aluminum, metallic, satin/brushed; not yellow plastic. |
| Screws/nuts/washers | dark steel/chromoly metal with small highlights and visible recesses. |
| Motors | black/dark anodized bell, copper winding hints, steel fasteners. |
| N150/electronics | exposed board/interface/cooling stack; PCB soldermask, IC packages, connector shells/cores, fan/heatsink, M.2 module. |
| USB cameras | black polymer housing, glass lens, connector/cable details. |
| Cables | black rubber/silicone with colored leads only where physically visible. |
| Battery | black heat-shrink, label/edge wrinkle detail if visible. |

## Audit Output

Every component pass must update:

```text
Results/unreal_scene_mapping/SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md
```

Record:

- source objects;
- physical evidence;
- chosen PBR route;
- maps/material slots used;
- render path;
- pass/fail and remaining risks.

If the result still reads as flat CAD, overexposed white, pure black blocks, or
generic colored plastic, mark it failed and return to component material
classification or UV/PBR source selection.

## Minimum-Loop Check

For the current carbon-frame and accepted tri-blade-propeller PBR gate, run:

```bash
python3 Scripts/UE5/check_sunray150_pbr_miniloop.py
```

The check is file-level and does not launch Blender or UE. It verifies:

- `carbon_fiber` and `smoked_propeller` texture-manifest entries;
- base color, roughness, and bump map files, modes, sizes, and variation;
- component review manifest entries for `carbon_frame` and
  `tri_blade_propeller`;
- connected override texture targets: `Base Color`, `Roughness`, and `Bump`;
- review image existence and non-flat pixels;
- documentation guard tokens for accepted geometry and no UE export.
