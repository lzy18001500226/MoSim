---
name: unreal-actor-editing
description: Manage actors in UE levels via UCP. Use when the user asks to spawn, delete, move, duplicate, select, or otherwise manipulate actors in the Unreal Engine editor.
---

# Unreal Actor Editing

Manage actors in Unreal Engine levels through UCP's `call` command. This skill guides you to use engine-provided actor subsystems and libraries.

**Prerequisite**: The `unreal-client-protocol` skill must be available and the UE editor must be running with the UCP plugin enabled.

## Engine Built-in Actor Libraries

### UEditorActorSubsystem

**CDO Path**: `/Script/UnrealEd.Default__EditorActorSubsystem`

This is the primary API for actor manipulation in the editor:

| Function | Description |
|----------|-------------|
| `GetAllLevelActors()` | Get all actors in the current level |
| `GetAllLevelActorsOfClass(ActorClass)` | Get all actors of a specific class |
| `GetSelectedLevelActors()` | Get currently selected actors |
| `SetSelectedLevelActors(ActorsToSelect)` | Set actor selection |
| `SelectNothing()` | Deselect all actors |
| `SpawnActorFromClass(ActorClass, Location, Rotation)` | Spawn a new actor |
| `SpawnActorFromObject(ObjectToUse, Location, Rotation)` | Spawn from an existing asset |
| `DuplicateActor(ActorToDuplicate, ToWorld, Offset)` | Duplicate an actor |
| `DuplicateActors(ActorsToDuplicate, ToWorld, Offset)` | Duplicate multiple actors |
| `DestroyActor(ActorToDestroy)` | Delete an actor |
| `DestroyActors(ActorsToDestroy)` | Delete multiple actors |
| `SetActorTransform(Actor, WorldTransform)` | Set actor transform |
| `ConvertActors(Actors, ActorClass)` | Convert actors to a different class |

#### Examples

**Get all actors in level:**
```json
{"object":"/Script/UnrealEd.Default__EditorActorSubsystem","function":"GetAllLevelActors"}
```

**Get all static mesh actors:**
```json
{"object":"/Script/UnrealEd.Default__EditorActorSubsystem","function":"GetAllLevelActorsOfClass","params":{"ActorClass":"/Script/Engine.StaticMeshActor"}}
```

**Spawn a point light:**
```json
{"object":"/Script/UnrealEd.Default__EditorActorSubsystem","function":"SpawnActorFromClass","params":{"ActorClass":"/Script/Engine.PointLight","Location":{"X":0,"Y":0,"Z":200}}}
```

**Destroy an actor:**
```json
{"object":"/Script/UnrealEd.Default__EditorActorSubsystem","function":"DestroyActor","params":{"ActorToDestroy":"/Game/Maps/Main.Main:PersistentLevel.PointLight_0"}}
```

### UGameplayStatics

**CDO Path**: `/Script/Engine.Default__GameplayStatics`

Useful for runtime/game queries:

| Function | Description |
|----------|-------------|
| `GetAllActorsOfClass(WorldContextObject, ActorClass)` | Find actors by class |
| `GetAllActorsWithTag(WorldContextObject, Tag)` | Find actors by tag |
| `GetAllActorsOfClassWithTag(WorldContextObject, ActorClass, Tag)` | Combined class + tag filter |
| `GetAllActorsWithInterface(WorldContextObject, Interface)` | Find actors implementing an interface |
| `GetActorOfClass(WorldContextObject, ActorClass)` | Get first actor of class |
| `FindNearestActor(WorldContextObject, Origin, ActorClass)` | Find nearest actor of class to a location |
| `GetActorArrayAverageLocation(Actors)` | Get average location of an array of actors |
| `GetActorArrayBounds(Actors, bOnlyCollidingComponents)` | Get combined bounds of an array of actors |
| `GetPlayerPawn(WorldContextObject, PlayerIndex)` | Get player pawn |
| `GetPlayerController(WorldContextObject, PlayerIndex)` | Get player controller |
| `GetPlayerCameraManager(WorldContextObject, PlayerIndex)` | Get camera manager |

### UEditorLevelLibrary

**CDO Path**: `/Script/EditorScriptingUtilities.Default__EditorLevelLibrary`

Unique level editing functions not covered by UEditorActorSubsystem:

| Function | Description |
|----------|-------------|
| `JoinStaticMeshActors(ActorsToJoin, JoinOptions)` | Merge static meshes into one |
| `ReplaceSelectedActors(InAssetPath)` | Replace selected actors with given asset |
| `GetPIEWorlds()` | Get worlds from Play-In-Editor sessions |

## Layer Management (ULayersSubsystem)

Get the instance via `FindObjectInstances` with `ClassName` set to `/Script/UnrealEd.LayersSubsystem`.

| Function | Description |
|----------|-------------|
| `CreateLayer(LayerName)` | Create a new layer |
| `DeleteLayer(LayerToDelete)` | Delete a layer |
| `RenameLayer(OriginalLayerName, NewLayerName)` | Rename a layer |
| `AddActorToLayer(Actor, LayerName)` | Add a single actor to a layer |
| `RemoveActorFromLayer(Actor, LayerName)` | Remove a single actor from a layer |
| `AddActorsToLayer(Actors, LayerName)` | Add multiple actors to a layer |
| `GetActorsFromLayer(LayerName)` | Get all actors in a layer |
| `SetLayerVisibility(LayerName, bIsVisible)` | Show/hide a layer |
| `SelectActorsInLayer(LayerName)` | Select all actors in a layer |
| `AddAllLayerNamesTo(OutLayers)` | Get all layer names |

#### Examples

**Find the LayersSubsystem instance:**
```json
{"object":"/Script/UnrealClientProtocol.Default__ObjectOperationLibrary","function":"FindObjectInstances","params":{"ClassName":"/Script/UnrealEd.LayersSubsystem"}}
```

**Create a layer (use the instance path returned above):**
```json
{"object":"<layers_subsystem_instance_path>","function":"CreateLayer","params":{"LayerName":"Lighting"}}
```

**Add an actor to a layer:**
```json
{"object":"<layers_subsystem_instance_path>","function":"AddActorToLayer","params":{"Actor":"/Game/Maps/Main.Main:PersistentLevel.PointLight_0","LayerName":"Lighting"}}
```

## Actor Grouping (UActorGroupingUtils)

Get the CDO at `/Script/UnrealEd.Default__ActorGroupingUtils`, then call `Get()` on it to obtain the singleton instance.

| Function | Description |
|----------|-------------|
| `GroupActors(Actors)` | Group specified actors |
| `UngroupActors(Actors)` | Ungroup specified actors |
| `GroupSelected()` | Group currently selected actors |
| `UngroupSelected()` | Ungroup currently selected actors |
| `LockSelectedGroups()` | Lock selected groups |
| `UnlockSelectedGroups()` | Unlock selected groups |
| `CanGroupActors()` | Check if current selection can be grouped |

#### Examples

**Get the grouping utils instance:**
```json
{"object":"/Script/UnrealEd.Default__ActorGroupingUtils","function":"Get"}
```

**Group selected actors (use the instance returned by Get):**
```json
{"object":"<actor_grouping_utils_instance_path>","function":"GroupSelected"}
```

## Actor Folders (on Actor instances)

Functions called directly on actor instance paths:

| Function | Description |
|----------|-------------|
| `GetFolderPath()` | Get the actor's folder path in the outliner |
| `SetFolderPath(NewFolderPath)` | Set the actor's folder path in the outliner |

#### Examples

**Get an actor's folder:**
```json
{"object":"/Game/Maps/Main.Main:PersistentLevel.PointLight_0","function":"GetFolderPath"}
```

**Move an actor into a folder:**
```json
{"object":"/Game/Maps/Main.Main:PersistentLevel.PointLight_0","function":"SetFolderPath","params":{"NewFolderPath":"Lighting/Dynamic"}}
```

## Actor Attachment (on Actor instances)

Functions called directly on actor instance paths:

| Function | Description |
|----------|-------------|
| `K2_AttachToActor(ParentActor, SocketName, LocationRule, RotationRule, ScaleRule, bWeldSimulatedBodies)` | Attach this actor to a parent actor |
| `K2_DetachFromActor(LocationRule, RotationRule, ScaleRule)` | Detach this actor from its parent |

Rules are `EAttachmentRule` values: `KeepRelative`, `KeepWorld`, `SnapToTarget`.

#### Examples

**Attach an actor to another:**
```json
{"object":"/Game/Maps/Main.Main:PersistentLevel.Cube_0","function":"K2_AttachToActor","params":{"ParentActor":"/Game/Maps/Main.Main:PersistentLevel.Sphere_0","SocketName":"None","LocationRule":"KeepWorld","RotationRule":"KeepWorld","ScaleRule":"KeepWorld","bWeldSimulatedBodies":false}}
```

**Detach an actor:**
```json
{"object":"/Game/Maps/Main.Main:PersistentLevel.Cube_0","function":"K2_DetachFromActor","params":{"LocationRule":"KeepWorld","RotationRule":"KeepWorld","ScaleRule":"KeepWorld"}}
```

## Level Management (ULevelEditorSubsystem + UEditorLevelUtils)

### ULevelEditorSubsystem

Get the instance via `FindObjectInstances` with `ClassName` set to `/Script/LevelEditor.LevelEditorSubsystem`.

| Function | Description |
|----------|-------------|
| `NewLevel(AssetPath)` | Create a new level |
| `NewLevelFromTemplate(AssetPath, TemplatePath)` | Create a new level from template |
| `LoadLevel(AssetPath)` | Load a level |
| `SaveCurrentLevel()` | Save the current level |
| `SaveAllDirtyLevels()` | Save all modified levels |
| `SetCurrentLevelByName(LevelName)` | Switch current level |
| `GetCurrentLevel()` | Get the current level |
| `PilotLevelActor(ActorToPilot)` | Pilot an actor in the viewport |
| `EjectPilotLevelActor()` | Stop piloting an actor |

#### Examples

**Find the LevelEditorSubsystem instance:**
```json
{"object":"/Script/UnrealClientProtocol.Default__ObjectOperationLibrary","function":"FindObjectInstances","params":{"ClassName":"/Script/LevelEditor.LevelEditorSubsystem"}}
```

**Save the current level:**
```json
{"object":"<level_editor_subsystem_instance_path>","function":"SaveCurrentLevel"}
```

### UEditorLevelUtils

**CDO Path**: `/Script/UnrealEd.Default__EditorLevelUtils`

| Function | Description |
|----------|-------------|
| `CreateNewStreamingLevel(LevelStreamingClass, NewLevelPath, bMoveSelectedActors)` | Create a new streaming level |
| `MoveActorsToLevel(ActorsToMove, DestLevel, bWarnAboutReferences, bWarnAboutRenaming)` | Move actors to another level |
| `K2_AddLevelToWorld(World, LevelPath, LevelStreamingClass)` | Add a sub-level to the world |
| `K2_RemoveLevelFromWorld(Level)` | Remove a sub-level from the world |
| `SetLevelVisibility(Level, bShouldBeVisible, bForceLayersVisible)` | Show/hide a level |
| `GetLevels(World)` | Get all levels in a world |

## Viewport & Camera (UUnrealEditorSubsystem)

Get the instance via `FindObjectInstances` with `ClassName` set to `/Script/UnrealEd.UnrealEditorSubsystem`.

| Function | Description |
|----------|-------------|
| `GetLevelViewportCameraInfo(OutCameraLocation, OutCameraRotation)` | Get the viewport camera position and rotation |
| `SetLevelViewportCameraInfo(CameraLocation, CameraRotation)` | Set the viewport camera position and rotation |
| `GetEditorWorld()` | Get the current editor world |
| `ScreenToWorld(ScreenPosition)` | Convert screen coordinates to world coordinates |
| `WorldToScreen(WorldPosition)` | Convert world coordinates to screen coordinates |

Also available via `UEditorUtilityLibrary`:

**CDO Path**: `/Script/Blutility.Default__EditorUtilityLibrary`

| Function | Description |
|----------|-------------|
| `GetSelectionBounds(Origin, BoxExtent, SphereRadius)` | Get bounding info of the current selection |

#### Examples

**Find the UnrealEditorSubsystem instance:**
```json
{"object":"/Script/UnrealClientProtocol.Default__ObjectOperationLibrary","function":"FindObjectInstances","params":{"ClassName":"/Script/UnrealEd.UnrealEditorSubsystem"}}
```

**Get viewport camera info:**
```json
{"object":"<unreal_editor_subsystem_instance_path>","function":"GetLevelViewportCameraInfo"}
```

**Set viewport camera position:**
```json
{"object":"<unreal_editor_subsystem_instance_path>","function":"SetLevelViewportCameraInfo","params":{"CameraLocation":{"X":0,"Y":0,"Z":500},"CameraRotation":{"Pitch":-45,"Yaw":0,"Roll":0}}}
```

**Get selection bounds:**
```json
{"object":"/Script/Blutility.Default__EditorUtilityLibrary","function":"GetSelectionBounds"}
```

## Common Patterns

### Discover and inspect actors

First get all actors, then inspect a specific actor (run as separate calls):

```json
{"object":"/Script/UnrealEd.Default__EditorActorSubsystem","function":"GetAllLevelActors"}
```

```json
{"object":"/Script/UnrealClientProtocol.Default__ObjectOperationLibrary","function":"GetObjectProperty","params":{"ObjectPath":"<actor_path>","PropertyName":"RelativeLocation"}}
```

### Move an actor

Use the `unreal-object-operation` skill to set properties on the actor's root component:

```json
{"object":"/Script/UnrealClientProtocol.Default__ObjectOperationLibrary","function":"SetObjectProperty","params":{"ObjectPath":"<actor_root_component_path>","PropertyName":"RelativeLocation","JsonValue":"{\"X\":100,\"Y\":200,\"Z\":0}"}}
```

### Spawn, position, and select

Spawn an actor, then get selection (run as separate calls):

```json
{"object":"/Script/UnrealEd.Default__EditorActorSubsystem","function":"SpawnActorFromClass","params":{"ActorClass":"/Script/Engine.PointLight","Location":{"X":0,"Y":0,"Z":300}}}
```

```json
{"object":"/Script/UnrealEd.Default__EditorActorSubsystem","function":"GetSelectedLevelActors"}
```

### Organize actors into folders

```json
{"object":"/Script/UnrealEd.Default__EditorActorSubsystem","function":"GetAllLevelActorsOfClass","params":{"ActorClass":"/Script/Engine.PointLight"}}
```

Then set folder paths on each returned actor:

```json
{"object":"/Game/Maps/Main.Main:PersistentLevel.PointLight_0","function":"SetFolderPath","params":{"NewFolderPath":"Lighting"}}
```

### Attach actors together

```json
{"object":"/Game/Maps/Main.Main:PersistentLevel.ChildActor_0","function":"K2_AttachToActor","params":{"ParentActor":"/Game/Maps/Main.Main:PersistentLevel.ParentActor_0","SocketName":"None","LocationRule":"KeepWorld","RotationRule":"KeepWorld","ScaleRule":"KeepWorld","bWeldSimulatedBodies":false}}
```
