# MoSim Extension Snapshot Record

No extension source, CMake input, QML, map asset, or bridge file was changed
while copying this component into
`src/ground_station/qgc/mosim_extension`.

The snapshot deliberately includes the following pre-existing local worktree
changes from `apps/flight_console/mosim`:

1. `custom/src/CustomPlugin.cc`
2. `custom/src/FactoryPlanMapOverlay.qml`
3. `custom/src/FlyViewCustomLayer.qml`
4. `custom/src/MoSimOrchestratorBridge.cc`
5. `custom/src/MoSimOrchestratorBridge.h`
6. `custom/maps/factory_l2/v1/scene_map.json`
7. `custom/maps/factory_l2/v1/structure.geojson`
8. `custom/maps/factory_l2/v1/world_to_pixel.json`

They are project UI and Factory-map snapshot content, not migration edits. The
legacy materialized overlay remains untouched at
`apps/flight_console/vendor/qgroundcontrol/custom`.

Before this component can become `canonical_active`, the migration task must:

1. make `Scripts/ui/materialize_qgc_custom_overlay.py` consume the canonical
   extension path only after its inputs and generated-output boundary are
   audited;
2. keep generated QGroundControl overlay files out of the upstream QGC source
   snapshot;
3. update only audited QGC custom-build references and validate the Factory map
   resource paths; and
4. perform a controlled QGC build/preflight while retaining the legacy source
   as the rollback path.
