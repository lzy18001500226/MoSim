# RflySim Map Audit

- Project: `/mnt/d/PX4PSP/RflySim3D/RflySim3D`
- EngineAssociation: `4.27`
- Map count: `28`
- Loose mesh scan: `scanned`
- Loose mesh count: `0`
- Conclusion: Not drop-in for UE5.7: RflySim maps are UE4.27 .umap/.uasset assets with project/plugin dependencies. Use as migration source only.
- Editor source conclusion: Packaged/runtime install: RflySim3D.exe exists, but editable project/plugin source and plugin binaries are not present. Do not open this .uproject as a UE Editor source project; use the runtime as reference and rebuild scenes in the project-owned UE5 renderer.
- Project source dir: `False`
- Runtime executable: `True`
- Plugin source files: `0`
- Plugin binary files: `0`
- Reference scan MB per map: `0`

## Project Modules

| Module | Source Build.cs | Win64 DLL |
| --- | --- | --- |
| `RflySim3D` | `False` | `False` |

## Plugin Module Availability

| Plugin | Engine | Content | Modules | Missing Source/DLL? |
| --- | --- | --- | --- | --- |
| `Cesium for Unreal` | `4.27.0` | `True` | `CesiumRuntime`, `CesiumEditor` | `CesiumRuntime`, `CesiumEditor` |
| `Color Wheel` | `4.27.0` | `False` | `ColorWheelPlugin` | `ColorWheelPlugin` |
| `HZFRedis` | `None` | `True` | `DTRedisLib`, `DTRedis`, `DTRedisEditor` | `DTRedisLib`, `DTRedis`, `DTRedisEditor` |
| `Rfly3DSimPlugin` | `None` | `True` | `Rfly3DSimPlugin` | `Rfly3DSimPlugin` |
| `RuntimeTransformer` | `4.27.0` | `True` | `RuntimeTransformer` | `RuntimeTransformer` |
| `Datasmith Twinmotion Importer` | `4.27.0` | `True` | `TwinmotionBase`, `TwinmotionStorageLite`, `TwinmotionToUnreal` | `TwinmotionBase`, `TwinmotionStorageLite`, `TwinmotionToUnreal` |

## Enabled Plugins

- `ModelingToolsEditorMode`
- `PhysXVehicles`
- `DatasmithImporter`
- `TwinmotionToUnrealContent`
- `CesiumForUnreal`
- `DTRedis`
- `TwinmotionToUnreal`
- `LidarPointCloud`
- `ColorWheelPlugin`
- `RuntimeTransformer`

## Map Candidates

| Priority | Map | Size KB | Reason | Reference sample |
| --- | --- | ---: | --- | --- |
| P1 | `CameraRoom/Maps/CameraRoom.umap` | 320.6 | challenge/indoor candidate | `/Game/CameraRoom/EpicContent/Geometry/Meshes/1M_Cube`<br>`/Game/CameraRoom/Fence_Chainlink/Meshes/BP_Fence`<br>`/Game/CameraRoom/Fence_Chainlink/Meshes/SM_Fence_Chain_Door`<br>`/Game/CameraRoom/Maps/CameraRoom` |
| P2 | `Changsha.umap` | 6.5 | Cesium/geospatial dependency | `/CesiumForUnreal/CesiumCreditSystemBP`<br>`/Game/Changsha`<br>`/Game/Changsha_BuiltData`<br>`/Script/CesiumRuntime` |
| P2 | `Denver.umap` | 6.2 | Cesium/geospatial dependency | `/CesiumForUnreal/CesiumCreditSystemBP`<br>`/Game/Denver`<br>`/Game/Denver_BuiltData`<br>`/Script/CesiumRuntime` |
| P2 | `EarthMap.umap` | 6.6 | Cesium/geospatial dependency | `/CesiumForUnreal/CesiumCreditSystemBP`<br>`/Game/EarthMap`<br>`/Game/EarthMap_BuiltData`<br>`/Script/CesiumRuntime` |
| P1 | `ExhibitionHall/Maps/ExhibitionHall.umap` | 56.6 | useful scene family | `/Game/ExhibitionHall/BP/BP_Scene`<br>`/Game/ExhibitionHall/Maps/ExhibitionHall`<br>`/Game/ExhibitionHall/Maps/ExhibitionHall_BuiltData`<br>`/Game/ExhibitionHall/Maps/LayerInfo/Layer_01_LayerInfo` |
| P0 | `Grasslands/Maps/Grasslands/3DDisplay.umap` | 229.8 | matches target demo scenes | `/Game/Grasslands/DistanceMeshes/Generic_Erosion_01/S_Generic_Erosion_01`<br>`/Game/Grasslands/DistanceMeshes/Generic_Erosion_02/MI_Generic_Erosion_02_Grasslands`<br>`/Game/Grasslands/DistanceMeshes/Generic_Erosion_02/S_Generic_Erosion_02`<br>`/Game/Grasslands/DistanceMeshes/Generic_Erosion_03/S_Generic_Erosion_03` |
| P0 | `Grasslands/Maps/Grasslands/Grasslands.umap` | 230.0 | matches target demo scenes | `/Game/Grasslands/DistanceMeshes/Generic_Erosion_01/S_Generic_Erosion_01`<br>`/Game/Grasslands/DistanceMeshes/Generic_Erosion_02/MI_Generic_Erosion_02_Grasslands`<br>`/Game/Grasslands/DistanceMeshes/Generic_Erosion_02/S_Generic_Erosion_02`<br>`/Game/Grasslands/DistanceMeshes/Generic_Erosion_03/S_Generic_Erosion_03` |
| P2 | `LightShow/LightShow.umap` | 4.2 | needs manual review | `/Game/LightShow/LightShow`<br>`/Game/LightShow/LightShow_BuiltData`<br>`/Script/CoreUObject`<br>`/Script/Engine` |
| P2 | `MapData.umap` | 9.7 | Cesium/geospatial dependency | `/CesiumForUnreal/CesiumCreditSystemBP`<br>`/Game/MapData`<br>`/Game/MapData_BuiltData`<br>`/Script/CesiumRuntime` |
| P2 | `MapSmall.umap` | 9.6 | Cesium/geospatial dependency | `/CesiumForUnreal/CesiumCreditSystemBP`<br>`/Game/MapSmall`<br>`/Script/CesiumRuntime`<br>`/Script/CoreUObject` |
| P1 | `MatchScene/MatchScene.umap` | 92.4 | challenge/indoor candidate | `/Game/MatchScene/Geometries/0021_DarkRed`<br>`/Game/MatchScene/Geometries/0038_Orange`<br>`/Game/MatchScene/Geometries/0045_Goldenrod`<br>`/Game/MatchScene/Geometries/0064_Chartreuse` |
| P1 | `MatchScene2/MatchScene2.umap` | 18.3 | challenge/indoor candidate | `/Game/MatchScene2/Geometries/Checkerboard_Black`<br>`/Game/MatchScene2/Geometries/Color_A01`<br>`/Game/MatchScene2/Geometries/Color_J05`<br>`/Game/MatchScene2/Geometries/Default` |
| P1 | `MatchScene2025/-Demo.umap` | 14.9 | challenge/indoor candidate | `/Game/MatchScene2025/-Demo`<br>`/Game/MatchScene2025/-Demo_BuiltData`<br>`/Game/MatchScene2025/StaticMesh/Materials/M_DB`<br>`/Game/MatchScene2025/StaticMesh/SM_Door0` |
| P1 | `MatchScene2025/MatchScene2025.umap` | 17.8 | challenge/indoor candidate | `/Game/MatchScene2025/MatchScene2025`<br>`/Game/MatchScene2025/MatchScene2025_BuiltData`<br>`/Game/MatchScene2025/StaticMesh/1`<br>`/Game/MatchScene2025/StaticMesh/Materials/M_Flooring_Mat` |
| P1 | `MatchScene2025/MatchScene2025_Height.umap` | 17.3 | challenge/indoor candidate | `/Game/MatchScene2025/MatchScene2025_Height`<br>`/Game/MatchScene2025/StaticMesh/Materials/M_Flooring_Mat`<br>`/Game/MatchScene2025/StaticMesh/Materials/M_Walnut_Hrrngbn_01_Mat_Inst`<br>`/Game/MatchScene2025/StaticMesh/SM_Door0` |
| P0 | `ModularNeighborhood/Maps/NeighborhoodPark.umap` | 1342.3 | matches target demo scenes | `/Game/ModularNeighborhood/Audio/Cues/SC_Outdoor_Ambience_01`<br>`/Game/ModularNeighborhood/Blueprints/Doors/BP_Door_Inside_01`<br>`/Game/ModularNeighborhood/Blueprints/Doors/BP_Door_Outside_01`<br>`/Game/ModularNeighborhood/Blueprints/Fan/BP_Fan_01` |
| P1 | `MountainTerrain/Maps/MountainTerrain.umap` | 799.6 | useful scene family | `/Game/MountainTerrain/Blueprints/BP_Birds`<br>`/Game/MountainTerrain/Landscape/LayerInfoObject_Grass01`<br>`/Game/MountainTerrain/Landscape/LayerInfoObject_Snow01`<br>`/Game/MountainTerrain/Landscape/MI_Landscape_Inst` |
| P1 | `MountainTerrain/Maps/MountainTerrain_Water.umap` | 751.6 | useful scene family | `/Game/MountainTerrain/Blueprints/BP_Birds`<br>`/Game/MountainTerrain/Landscape/LayerInfoObject_Grass01`<br>`/Game/MountainTerrain/Landscape/LayerInfoObject_Snow01`<br>`/Game/MountainTerrain/Landscape/MI_Landscape_Inst` |
| P2 | `MoutainRoad.umap` | 6.5 | Cesium/geospatial dependency | `/CesiumForUnreal/CesiumCreditSystemBP`<br>`/Game/MoutainRoad`<br>`/Game/MoutainRoad_BuiltData`<br>`/Script/CesiumRuntime` |
| P0 | `OldFactory/Maps/OldFactory.umap` | 1459.3 | matches target demo scenes | `/Game/ModularNeighborhood/Models/Building/Prefab_Houses/SM_House_Prefab_01`<br>`/Game/ModularNeighborhood/Models/Foliage/Trees/SM_Birch_01`<br>`/Game/ModularNeighborhood/Models/Foliage/Trees/SM_Fir_01`<br>`/Game/ModularNeighborhood/Models/Foliage/Trees/SM_Oak_03` |
| P1 | `RobotMissionChallenge/Map/ChallengeMap.umap` | 15.6 | useful scene family | `/Game/RobotMissionChallenge/Blueprint/BP_Floor`<br>`/Game/RobotMissionChallenge/Blueprint/BP_Wall1`<br>`/Game/RobotMissionChallenge/Blueprint/BP_Wall2`<br>`/Game/RobotMissionChallenge/Map/ChallengeMap` |
| P1 | `SimulationScenario/SLAMScene.umap` | 13.2 | challenge/indoor candidate | `/Game/SimulationScenario/Geometries/Carpet_Berber_Pattern_Gray`<br>`/Game/SimulationScenario/Geometries/Formica_Laminate_Light`<br>`/Game/SimulationScenario/Geometries/Translucent_Glass_Safety`<br>`/Game/SimulationScenario/Materials/Clear_glass` |
| P2 | `UltraDynamicSky/Maps/UDS_LogicMap.umap` | 23.6 | needs manual review | `/Game/UltraDynamicSky/Blueprints/Ultra_Dynamic_Sky`<br>`/Game/UltraDynamicSky/Blueprints/Ultra_Dynamic_Weather`<br>`/Game/UltraDynamicSky/Blueprints/Weather_Effects/System/Random_Weather_Variation`<br>`/Game/UltraDynamicSky/Maps/UDS_LogicMap` |
| P0 | `Vision/Maps/LowGPU.umap` | 13.1 | matches target demo scenes | `/Game/Vision/Architecture/Floor_400x400`<br>`/Game/Vision/Maps/LowGPU`<br>`/Game/Vision/Maps/LowGPU_BuiltData`<br>`/Game/Vision/Materials/AlignedGrass` |
| P0 | `Vision/Maps/VisionRing.umap` | 14.9 | matches target demo scenes | `/Game/Vision/Architecture/Floor_400x400`<br>`/Game/Vision/Maps/VisionRing`<br>`/Game/Vision/Maps/VisionRing_BuiltData`<br>`/Game/Vision/Materials/AlignedGrass` |
| P0 | `Vision/Maps/VisionRingBlank.umap` | 13.2 | matches target demo scenes | `/Game/Vision/Architecture/Floor_400x400`<br>`/Game/Vision/Maps/VisionRingBlank`<br>`/Game/Vision/Maps/VisionRingBlank_BuiltData`<br>`/Game/Vision/Materials/AlignedGrass` |
| P2 | `WhiteMap/WhiteMap.umap` | 7.3 | needs manual review | `/Game/WhiteMap/WhiteMap`<br>`/Game/WhiteMap/WhiteMap_BuiltData`<br>`/Game/WhiteMap/white_Mat`<br>`/Script/CoreUObject` |
| P2 | `anti_terror/TerrorTest.umap` | 313.1 | needs manual review | `/Game/anti_terror/TerrorTest`<br>`/Game/anti_terror/TerrorTest.TerrorTest`<br>`/Game/anti_terror/TerrorTest_BuiltData`<br>`/Game/anti_terror/terror2022/Geometries/Default_material` |
