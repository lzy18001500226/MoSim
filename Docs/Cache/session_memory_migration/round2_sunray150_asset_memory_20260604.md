# Round 2 Sunray150 Asset Memory Audit

Date: 2026-06-04 CST

Scope: verify the long-session memory around Sunray150 geometry, MID-360
placement, propeller assembly, and material/texture work against current
project files. This is a cache-only round 2 audit. It does not promote any
numeric assembly parameter, material appearance, or UE runtime asset as final
project truth.

## Status

```text
round: 2
topic: Sunray150 asset and assembly memory
status: mixed_round2_verified_and_needs_round3
risk: high
formal_docs_patched_this_round: none
cache_only: true
```

## Sources Re-Read

| Source | Finding |
|---|---|
| `Results/unreal_scene_mapping/SUNRAY150_MID360_MATERIAL_AUDIT_PACKAGE_20260603.md` | Material candidate is explicitly rejected on 2026-06-04. It records geometry invariants but says not to export or import this material candidate into UE. |
| `Results/unreal_scene_mapping/SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md` | Current material direction is an evidence matrix and next-pass requirement set, not UE runtime evidence. It requires manual Blender acceptance before UE export/import. |
| `Results/unreal_scene_mapping/sunray150_mid360_material_audit_package_20260603.json` | JSON status is `manual_blender_material_audit_pending`, `do_not_export_to_ue_until_manual_acceptance=true`, and `ue_export_allowed=false`. |
| `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_full_assembly_audit_manifest.json` | Current assembly audit uses `150.dae` plus standalone `livox_mid360/test2.dae`; it records MID-360 hole-fit, propeller source, propeller hole/screw fit, and manual review requirements. |
| `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit_manifest.json` | Material audit scene is a manual review scene, not a final runtime asset. It repeats the same assembly constraints and marks review decals/cable hints as non-physical intent markers. |
| `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_with_mid360_propeller_assembly_audit_manifest.json` | Earlier propeller audit is explicitly `audit_only_not_runtime_parameter_commit`. |
| `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured_manifest.json` | Earlier generated textured asset is DAE-derived review output and includes supplemental/proxy MID-360 geometry, so it is historical diagnostic output rather than final source-faithful geometry. |
| `PROGRESS.md` current Sunray entries | Records several rejected manual tuning attempts and later source-derived corrections. It is useful for contradiction history, but not sufficient as final numeric proof. |

## Round 2 Findings

### SUNRAY-MEM-001 - Source Chain

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  The current source-faithful Sunray150 visual audit chain is based on
  the Sunray `150.dae` aircraft source plus the standalone Livox MID-360
  `test2.dae` scanner source. The old proxy MID-360 base/dome route is
  historical diagnostic output and must not be resumed as final geometry.
current_evidence:
  - `SUNRAY150_MID360_MATERIAL_AUDIT_PACKAGE_20260603.md` says the previous
    material candidate is rejected and lists the source files.
  - `sunray150_dae_mid360_full_assembly_audit_manifest.json` imports
    `150.dae` and `sensor_models/livox_mid360/meshes/test2.dae`.
  - `PROGRESS.md` records that `150.dae` alone is not the complete vehicle
    plus MID-360 source.
contradictions_or_history:
  Earlier generated `sunray150_with_mid360_textured.*` assets added
  supplemental grey base/blue dome geometry. Treat those as diagnostic
  outputs only.
formal_target_if_promoted:
  `Docs/Workflows/unreal_renderer.md` or a dedicated Sunray visual asset
  evidence workflow section.
next_round_action:
  Round 3 may promote the source-chain rule only after re-reading the current
  source manifests once more and writing narrow wording that excludes final
  material/runtime acceptance.
```

### SUNRAY-MEM-002 - MID-360 Placement

```text
round: 2
status: round2_verified_for_cache_but_not_final_parameter
risk: high
candidate_statement:
  Current audit manifests record MID-360 yaw `270 deg`, four-hole direct fit,
  uniform scale `0.833527`, and placement by fitting XY to the four named
  mount-hole centers while snapping visual bottom to the selected top-panel
  plane.
current_evidence:
  - `sunray150_dae_mid360_full_assembly_audit_manifest.json` records
    `yaw_deg: 270.0`, `uniform_scale: 0.833527`, frame hole centers, and
    `placement_rule`.
  - `sunray150_dae_mid360_realistic_material_audit_manifest.json` repeats the
    same placement rule and scale.
  - `SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md` says to preserve
    accepted radar placement in the next material pass.
contradictions_or_history:
  User rejected earlier proxy/source-incomplete MID-360 visuals. Old
  `150.dae`-only or proxy dome/base conclusions are superseded.
formal_target_if_promoted:
  Sunray visual asset workflow or a result manifest index, not a dynamics
  parameter document.
next_round_action:
  Round 3 must verify whether a later accepted manual review exists. If no
  accepted review exists, preserve this only as an audit-scene constraint and
  keep it out of final UE runtime docs.
```

### SUNRAY-MEM-003 - Propeller Assembly

```text
round: 2
status: round2_verified_for_cache_but_not_final_runtime_commit
risk: high
candidate_statement:
  Current propeller assembly memory should preserve the source-chain rule:
  use `sunray150_with_mid360/meshes/sunray_cw.stl` as the required tri-blade
  propeller source, remove DAE propeller pattern objects, fit STL screw holes
  to DAE M2x8 screw pairs, and keep the flipped-around-screw-axis orientation
  as the current manually accepted audit orientation.
current_evidence:
  - `sunray150_dae_mid360_full_assembly_audit_manifest.json` records
    `source_rule`, `placement_rule`, `orientation_mode:
    flipped_around_screw_axis`, and `orientation_warning`.
  - The same manifest records the current propeller z rule ending at
    `-0.014052 m`.
  - `sunray150_with_mid360_propeller_assembly_audit_manifest.json` is
    `audit_only_not_runtime_parameter_commit`.
contradictions_or_history:
  PROGRESS records rejected manual propeller Z/yaw/XY attempts, including
  `+2.5 cm`, `-7.5 cm`, `-7.75 cm`, and `-7.0 cm` style procedural UE visual
  trials. Those are not current final assembly truth.
formal_target_if_promoted:
  Sunray visual asset workflow or UE asset review notes. Do not promote to
  Sunray physical dynamics/parameter identification docs.
next_round_action:
  Round 3 must re-check whether a newer runtime asset or manual review has
  superseded `-0.014052 m`. If not, document it only as the current audit-scene
  geometry constraint, with the `audit_only` caveat intact.
```

### SUNRAY-MEM-004 - Material/Texture Candidate

```text
round: 2
status: rejected_or_pending_not_promotable
risk: high
candidate_statement:
  The current material/texture memory is not an accepted UE asset. The
  2026-06-04 audit rejects the material candidate because it still reads as
  CAD grey/partial coloring. The next valid route is component classification,
  real material research, procedural/PBR texture work, close-up renders, and
  manual Blender acceptance before UE export.
current_evidence:
  - `SUNRAY150_MID360_MATERIAL_AUDIT_PACKAGE_20260603.md` status: rejected in
    material audit on 2026-06-04.
  - `SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md` says it is not UE
    runtime evidence and lists next material pass requirements.
  - `sunray150_mid360_material_audit_package_20260603.json` has
    `do_not_export_to_ue_until_manual_acceptance=true`.
contradictions_or_history:
  Earlier simple PBR recolor, proxy MID-360, and grey/dark stylized material
  candidates are rejected or superseded.
formal_target_if_promoted:
  No formal promotion until the manual material gate passes.
next_round_action:
  Round 3 should only promote a negative rule: do not reuse rejected material
  candidates or export to UE before manual acceptance.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| `150.dae` alone as complete Sunray150 + MID-360 final source | Superseded by `150.dae` plus standalone `livox_mid360/test2.dae` source chain. |
| Supplemental/proxy MID-360 grey base and blue dome as final geometry | Rejected/superseded; diagnostic output only. |
| Simple PBR recolor as final material realism proof | Rejected on 2026-06-04. |
| Manual propeller placement by ad hoc UE yaw/Z/XY trial values | Rejected as final source. Use screw/hole/face constraints instead. |
| Treating material close-up renders as UE runtime evidence | Rejected. The current files call them manual Blender audit material, not UE runtime evidence. |

## Round 3 Promotion Candidates

Only the following narrow items are candidates for round 3:

1. Source-chain rule: use local Sunray `150.dae` plus standalone Livox
   `test2.dae` for source-faithful visual audit, not proxy MID-360 geometry.
2. Negative material rule: do not export/import rejected Sunray material
   candidates to UE until manual Blender material acceptance.
3. Negative assembly rule: do not resume old ad hoc propeller offset tuning;
   use source-derived screw/hole/face constraints and keep audit/runtime caveats.

Numeric values such as `0.833527`, `270 deg`, and `-0.014052 m` are not ready
for formal promotion as final project parameters. At most, after round 3 they
may be documented as current audit-scene constraints with exact manifest paths
and the manual-review caveat.

## Verification Needed Before Round 3

```text
1. Re-read the same current manifests and check whether newer Sunray asset
   manifests exist.
2. Confirm whether the user has manually accepted a later Blender material
   pass. If not, keep material status rejected/pending.
3. Confirm whether a UE runtime import/export manifest exists after manual
   acceptance. If not, do not call any Sunray material asset UE-ready.
4. Check `git diff --check` for the cache and any narrow formal doc patch.
```
