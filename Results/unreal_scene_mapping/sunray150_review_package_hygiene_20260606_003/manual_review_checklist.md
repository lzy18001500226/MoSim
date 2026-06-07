# Sunray150 Component Material Review Package

Status: file-level review package ready; manual visual review required.

This package is path-neutral for manual routing: use the project-relative paths
below, not the legacy absolute `path` fields in the source manifest.

## Boundary

- This is not final material acceptance.
- This is not UE import/export final acceptance.
- This is not MWORKS, ROS2, FAST-LIO, planner, controller, or closed-loop evidence.
- Do not change geometry, dynamics, FAST-LIO extrinsics, controller, or planner
  settings based on these images.

## Review Batches

### 1. MID-360

Images:

- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/mid360_sensor.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/mid360_protection_frame.png`

Question: MID-360 optical window, housing, connector/base, and protection frame
look credible?

Return: `pass` or `fail`, plus the most visible defect.

### 2. Carbon Frame / Standoffs / Fasteners

Images:

- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/carbon_frame.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/aluminum_standoffs.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/steel_fasteners.png`

Question: carbon weave, anodized aluminum, and dark steel fasteners look like
separate real materials?

Return: `pass` or `fail`, plus the most visible defect.

### 3. Camera / Electronics / Connectors / Cables

Images:

- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/front_camera.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/electronics_connectors.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/pcb_boards.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/n150_stack_boards.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/n150_internal_pcb_audit.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/n150_ports.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/n150_cooling_storage.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/esc_board.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/connector_shells.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/cables_wires.png`

Question: camera, PCB, ports, connectors, and cables are visually separable and
not just grey/black placeholders?

Return: `pass` or `fail`, plus the most visible defect.

### 4. Motors / Propellers

Images:

- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/motor_only.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/motor_propeller.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/tri_blade_propeller.png`

Question: motor bell, windings, screws, and the accepted tri-blade propeller are
readable; propeller looks like smoked translucent plastic?

Return: `pass` or `fail`, plus the most visible defect.

### 5. Battery / Guard Landing Gear

Images:

- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/battery.png`
- `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/component_material_reviews/guard_landing_gear.png`

Question: `battery.png` looks like black heat-shrink battery/clip with surface
detail, and `guard_landing_gear.png` looks like dark/smoked protective ring and
landing gear rather than white CAD or a temporary placeholder?

Return: `pass` or `fail`, plus the most visible defect.
