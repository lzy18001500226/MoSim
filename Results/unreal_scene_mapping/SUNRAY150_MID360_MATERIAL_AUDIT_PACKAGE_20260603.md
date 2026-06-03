# Sunray150 + MID-360 Material Audit Package

Status: manual Blender material audit pending. Do not export or import this material candidate into UE until manual acceptance.

## Geometry Invariants

- MID-360 four-hole uniform scale: `0.833527`
- Propeller source: `C:\Users\HP\Desktop\MoSim\References\Sunray\simulation\sunray_simulator\models\drone_models\sunray150_with_mid360\meshes\sunray_cw.stl`
- Propeller orientation: `flipped_around_screw_axis`
- Propeller Z rule: `Final propeller transform translation.z is computed from user-audited planes and fine tune: base -0.0161m + ((-0.0193m + 0.0001m) - -0.021098m) + 0.00015m = -0.014052m.`

## Component-Material-Texture Plan

### carbon frame plates / top panel / main structure

- Source names: `MAIN_STRUCTURE, TOP_PANNEL, BOT_PANNEL, Fill`
- Material: dark graphite woven carbon fiber
- Texture maps: `sunray150_carbon_fiber_base.png, sunray150_carbon_fiber_roughness.png, sunray150_carbon_fiber_bump.png`
- Evidence: Local DAE part names and Sunray/CUAV visual references show dark carbon composite frame plates, not white plastic.

### MID-360 protection structure

- Source names: `PROTECTIVE_RING, MID360_PROTECT_ARC*, MID360_PROTECT_ARC_CONNECTOR*`
- Material: matte black / dark grey low-reflection plastic or composite
- Texture maps: `sunray150_black_rubber_base.png, sunray150_black_rubber_roughness.png, sunray150_black_rubber_bump.png`
- Evidence: YunDrone MID-360 protection cover references and local DAE names indicate a dark protective structure; previous white/blue broad coloring was rejected.

### Livox MID-360 visual sensor

- Source names: `AUDIT_STANDALONE_MID360_013/014/015/016/017`
- Material: satin silver-grey housing, blue optical window, black M12 connector/base
- Texture maps: `mid360_silver_grey_aluminum_base.png, mid360_silver_grey_aluminum_roughness.png, mid360_silver_grey_aluminum_bump.png`
- Evidence: Livox MID-360 product references show blue optical dome/window with grey housing and black connector/base.

### propellers

- Source names: `sunray_cw.stl fitted to DAE M2 screw pairs`
- Material: dark smoked composite propeller
- Texture maps: `sunray150_smoked_translucent_guard_base.png, sunray150_smoked_translucent_guard_roughness.png`
- Evidence: User accepted three-blade geometry from local Sunray source; material remains dark composite until physical photo audit refines it.

### motors and screws

- Source names: `MOTOR, STATOR WIRE, SCREW, NUT, WASHER`
- Material: black motor bell, copper winding hints, brushed/dark steel screws
- Texture maps: `sunray150_dark_anodized_metal_base.png, sunray150_dark_anodized_metal_roughness.png`
- Evidence: DAE object names expose motor, stator wire, and screw families; material assignment separates metal, copper, and plastic roles.

### electronics, cameras, connectors, cables

- Source names: `N150, PCBModel, FRONT_CAMERA, BOTTOM_CAMERA, USB, HDMI, CABLE`
- Material: black PCB/camera bodies, nickel connector shells, colored cable hints
- Texture maps: `sunray150_pcb_black_base.png, sunray150_black_rubber_base.png`
- Evidence: Local DAE object hierarchy exposes N150/USB/HDMI/camera/cable groups; overlays mark cable and camera-lens intent without changing geometry.

## Audit Outputs

- Audit blend: `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend`
- mid360_housing_window_connector: `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/material_closeups/mid360_housing_window_connector.png`
- front_usb_camera_battery: `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/material_closeups/front_usb_camera_battery.png`
- pcb_connectors_cables: `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/material_closeups/pcb_connectors_cables.png`
- carbon_frame_gold_standoffs: `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/material_closeups/carbon_frame_gold_standoffs.png`
- motor_prop_guard: `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/material_closeups/motor_prop_guard.png`

## Next Gate

Manual review must accept MID-360 housing/window/connector, carbon frame, USB camera/electronics, motor/propeller, and overall material realism before any UE export.
