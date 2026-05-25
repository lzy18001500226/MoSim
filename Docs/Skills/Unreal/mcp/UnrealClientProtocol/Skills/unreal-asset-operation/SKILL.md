---
name: unreal-asset-operation
description: Query and manage UE assets via UCP. Use when the user asks about asset search, dependencies, referencers, asset CRUD, asset management, getting selected/current assets, opening/closing asset editors, or any editor asset operation in Unreal Engine.
---

# Unreal Asset Operations

Operate on Unreal Engine assets through UCP's `call` command. The core approach is to obtain the `IAssetRegistry` instance and call its rich API directly, combined with engine asset libraries for CRUD operations.

**Prerequisite**: The `unreal-client-protocol` skill must be available and the UE editor must be running with the UCP plugin enabled.

## Custom Function Library

### UAssetEditorOperationLibrary (Editor)

**CDO Path**: `/Script/UnrealClientProtocolEditor.Default__AssetEditorOperationLibrary`

| Function | Params | Returns | Description |
|----------|--------|---------|-------------|
| `GetAssetRegistry` | (none) | `IAssetRegistry` object | Returns the AssetRegistry instance. Call its functions directly via UCP `call`. |
| `ForceDeleteAssets` | `AssetPaths` (array of string) | `int32` — number deleted | Force-deletes assets ignoring references. Wraps `ObjectTools::ForceDeleteObjects`. |
| `FixupReferencers` | `AssetPaths` (array of string) | `bool` | Cleans up redirectors left after rename/consolidate. Wraps `IAssetTools::FixupReferencers`. |

#### Getting the AssetRegistry

```json
{"object":"/Script/UnrealClientProtocolEditor.Default__AssetEditorOperationLibrary","function":"GetAssetRegistry"}
```

The returned object path can then be used as the `object` parameter for subsequent calls to IAssetRegistry functions.

Alternatively, you can use the engine helper directly:

```json
{"object":"/Script/AssetRegistry.Default__AssetRegistryHelpers","function":"GetAssetRegistry"}
```

#### Force-deleting assets

```json
{"object":"/Script/UnrealClientProtocolEditor.Default__AssetEditorOperationLibrary","function":"ForceDeleteAssets","params":{"AssetPaths":["/Game/OldAssets/M_Unused","/Game/OldAssets/T_Unused"]}}
```

#### Fixing up redirectors

After renaming or consolidating assets, redirectors may be left behind. Use `FixupReferencers` to resolve them:

```json
{"object":"/Script/UnrealClientProtocolEditor.Default__AssetEditorOperationLibrary","function":"FixupReferencers","params":{"AssetPaths":["/Game/Materials/M_OldName"]}}
```

## Engine Built-in Asset Libraries

### IAssetRegistry (via GetAssetRegistry)

Once you have the AssetRegistry instance, you can call these BlueprintCallable functions on it:

#### Asset Queries

| Function | Key Params | Description |
|----------|------------|-------------|
| `GetAssetsByPackageName` | `PackageName`, `OutAssetData`, `bIncludeOnlyOnDiskAssets` | Get assets in a specific package |
| `GetAssetsByPath` | `PackagePath`, `OutAssetData`, `bRecursive` | Get assets under a content path |
| `GetAssetsByPaths` | `PackagePaths`, `OutAssetData`, `bRecursive` | Get assets under multiple paths |
| `GetAssetsByClass` | `ClassPathName`, `OutAssetData`, `bSearchSubClasses` | Get all assets of a specific class |
| `GetAssets` | `Filter`, `OutAssetData` | Query with an `FARFilter` (powerful filtered search) |
| `GetAllAssets` | `OutAssetData`, `bIncludeOnlyOnDiskAssets` | Get ALL registered assets |
| `GetAssetByObjectPath` | `ObjectPath` | Get single asset data by path |
| `HasAssets` | `PackagePath`, `bRecursive` | Check if any assets exist under a path |
| `GetInMemoryAssets` | `Filter`, `OutAssetData` | Query only currently loaded assets |

#### Dependency & Reference Queries

| Function | Key Params | Description |
|----------|------------|-------------|
| `GetDependencies` | `PackageName`, `DependencyOptions`, `OutDependencies` | Get packages this asset depends on |
| `GetReferencers` | `PackageName`, `ReferenceOptions`, `OutReferencers` | Get packages that reference this asset |

#### Class Hierarchy

| Function | Key Params | Description |
|----------|------------|-------------|
| `GetAncestorClassNames` | `ClassPathName`, `OutAncestorClassNames` | Get parent classes |
| `GetDerivedClassNames` | `ClassNames`, `DerivedClassNames` | Get child classes |

#### Path & Scanning

| Function | Key Params | Description |
|----------|------------|-------------|
| `GetAllCachedPaths` | `OutPathList` | Get all known content paths |
| `GetSubPaths` | `InBasePath`, `OutPathList`, `bInRecurse` | Get sub-paths under a base path |
| `ScanPathsSynchronous` | `InPaths`, `bForceRescan` | Force scan specific paths |
| `ScanFilesSynchronous` | `InFilePaths`, `bForceRescan` | Force scan specific files |
| `SearchAllAssets` | `bSynchronousSearch` | Trigger full asset scan |
| `ScanModifiedAssetFiles` | `InFilePaths` | Scan modified files |
| `IsLoadingAssets` | (none) | Check if scan is in progress |
| `WaitForCompletion` | (none) | Block until scan finishes |

#### Filter & Sort

| Function | Key Params | Description |
|----------|------------|-------------|
| `RunAssetsThroughFilter` | `AssetDataList`, `Filter` | Filter asset list in-place (keep matching) |
| `UseFilterToExcludeAssets` | `AssetDataList`, `Filter` | Filter asset list in-place (remove matching) |

#### UAssetRegistryHelpers (Static Utilities)

**CDO Path**: `/Script/AssetRegistry.Default__AssetRegistryHelpers`

| Function | Description |
|----------|-------------|
| `GetAssetRegistry` | Get the IAssetRegistry instance |
| `GetDerivedClassAssetData` | Get asset data for derived classes |
| `SortByAssetName` | Sort FAssetData array by name |
| `SortByPredicate` | Sort FAssetData array by custom predicate |

### IAssetTools (via UAssetToolsHelpers::GetAssetTools())

Get the instance via static helper:

```json
{"object":"/Script/AssetTools.Default__AssetToolsHelpers","function":"GetAssetTools"}
```

Then call functions on the returned instance:

#### Create

| Function | Key Params | Description |
|----------|------------|-------------|
| `CreateAsset` | `AssetName`, `PackagePath`, `AssetClass`, `Factory` | Create a new asset (Factory can be null for simple types) |
| `CreateUniqueAssetName` | `InBasePackageName`, `InSuffix` | Generate a unique name to avoid conflicts |
| `DuplicateAsset` | `AssetName`, `PackagePath`, `OriginalObject` | Duplicate an existing asset |

##### Example: Create a new material

```json
{"object":"<asset_tools_instance>","function":"CreateAsset","params":{"AssetName":"M_NewMaterial","PackagePath":"/Game/Materials","AssetClass":"/Script/Engine.Material","Factory":null}}
```

#### Import & Export

| Function | Key Params | Description |
|----------|------------|-------------|
| `ImportAssetTasks` | `ImportTasks` (array of UAssetImportTask) | Import external files as assets |
| `ImportAssetsAutomated` | `ImportData` (UAutomatedAssetImportData) | Automated batch import |
| `ExportAssets` | `AssetsToExport`, `ExportPath` | Export assets to files |

#### Rename & Move

| Function | Key Params | Description |
|----------|------------|-------------|
| `RenameAssets` | `AssetsAndNames` (array of FAssetRenameData) | Batch rename/move assets |
| `FindSoftReferencesToObject` | `TargetObject` | Find soft references to an object |
| `RenameReferencingSoftObjectPaths` | `PackagesToCheck`, `AssetRedirectorMap` | Update soft references after rename |
| `MigratePackages` | `PackageNamesToMigrate`, `DestinationPath` | Migrate packages to another project |

##### Example: Batch rename assets

`RenameAssets` takes an array of `FAssetRenameData` structs. Each struct has `Asset` (the object to rename), `NewPackagePath` (destination directory), and `NewName` (new asset name):

```json
{"object":"<asset_tools_instance>","function":"RenameAssets","params":{"AssetsAndNames":[{"Asset":"/Game/Materials/M_OldName.M_OldName","NewPackagePath":"/Game/Materials","NewName":"M_NewName"}]}}
```

##### Example: Find soft references

```json
{"object":"<asset_tools_instance>","function":"FindSoftReferencesToObject","params":{"TargetObject":"/Game/Materials/M_Example.M_Example"}}
```

### UEditorAssetLibrary

**CDO Path**: `/Script/EditorScriptingUtilities.Default__EditorAssetLibrary`

#### Query & Check

| Function | Description |
|----------|-------------|
| `DoesAssetExist(AssetPath)` | Check if an asset exists |
| `DoAssetsExist(AssetPaths)` | Batch existence check |
| `ListAssets(DirectoryPath, bRecursive, bIncludeFolder)` | List assets in directory |
| `ListAssetByTagValue(AssetTagName, TagValue)` | List assets matching a specific tag value |
| `LoadAsset(AssetPath)` | Load an asset into memory |
| `LoadBlueprintClass(AssetPath)` | Load a Blueprint and return its generated class |
| `GetTagValues(AssetPath, AssetTagName)` | Get tag values for a specific asset |
| `FindPackageReferencersForAsset(AssetPath, bLoadAssetsToConfirm)` | Find all packages that reference this asset |

##### Example: Find references to an asset

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"FindPackageReferencersForAsset","params":{"AssetPath":"/Game/Materials/M_Example","bLoadAssetsToConfirm":false}}
```

##### Example: List assets by tag

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"ListAssetByTagValue","params":{"AssetTagName":"MyCustomTag","TagValue":"SomeValue"}}
```

##### Example: Load a Blueprint class

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"LoadBlueprintClass","params":{"AssetPath":"/Game/Blueprints/BP_MyActor"}}
```

#### Create & Modify

| Function | Description |
|----------|-------------|
| `DuplicateAsset(SourceAssetPath, DestinationAssetPath)` | Duplicate an asset by path |
| `DuplicateDirectory(SourceDirectoryPath, DestinationDirectoryPath)` | Duplicate an entire directory of assets |
| `RenameAsset(SourceAssetPath, DestinationAssetPath)` | Rename/move an asset by path |
| `RenameDirectory(SourceDirectoryPath, DestinationDirectoryPath)` | Rename/move an entire directory |
| `SaveAsset(AssetToSave, bOnlyIfIsDirty)` | Save an asset to disk |
| `SaveDirectory(DirectoryPath, bOnlyIfIsDirty, bRecursive)` | Save all assets in directory |

##### Example: Duplicate a directory

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"DuplicateDirectory","params":{"SourceDirectoryPath":"/Game/Materials","DestinationDirectoryPath":"/Game/Materials_Backup"}}
```

##### Example: Rename a directory

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"RenameDirectory","params":{"SourceDirectoryPath":"/Game/OldFolder","DestinationDirectoryPath":"/Game/NewFolder"}}
```

#### Delete & Reference Replace

| Function | Description |
|----------|-------------|
| `DeleteAsset(AssetPathToDelete)` | Delete an asset by path |
| `ConsolidateAssets(AssetToConsolidateTo, AssetsToConsolidate)` | Replace all references to `AssetsToConsolidate` with `AssetToConsolidateTo`, then delete the consolidated assets |

##### Example: Consolidate assets

Replace all references to `M_OldMaterial` with `M_NewMaterial`, effectively merging them:

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"ConsolidateAssets","params":{"AssetToConsolidateTo":"/Game/Materials/M_NewMaterial.M_NewMaterial","AssetsToConsolidate":["/Game/Materials/M_OldMaterial.M_OldMaterial"]}}
```

After consolidation, run `FixupReferencers` to clean up any leftover redirectors:

```json
{"object":"/Script/UnrealClientProtocolEditor.Default__AssetEditorOperationLibrary","function":"FixupReferencers","params":{"AssetPaths":["/Game/Materials/M_OldMaterial"]}}
```

#### Directory Management

| Function | Description |
|----------|-------------|
| `MakeDirectory(DirectoryPath)` | Create a content directory |
| `DeleteDirectory(DirectoryPath)` | Delete a content directory |
| `DoesDirectoryExist(DirectoryPath)` | Check if directory exists |
| `DoesDirectoryHaveAssets(DirectoryPath, bRecursive)` | Check if directory contains assets |

#### Metadata Tags

| Function | Description |
|----------|-------------|
| `SetMetadataTag(Object, Tag, Value)` | Set asset metadata tag |
| `GetMetadataTag(Object, Tag)` | Get asset metadata tag |
| `RemoveMetadataTag(Object, Tag)` | Remove asset metadata tag |
| `GetMetadataTagValues(Object)` | Get all metadata tag key-value pairs for an asset |

##### Example: Get all metadata tags

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"GetMetadataTagValues","params":{"Object":"/Game/Materials/M_Example.M_Example"}}
```

#### Browser Sync

| Function | Description |
|----------|-------------|
| `SyncBrowserToObjects(AssetPaths)` | Sync the Content Browser to show the specified assets |

##### Example: Sync browser to an asset

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"SyncBrowserToObjects","params":{"AssetPaths":["/Game/Materials/M_Example"]}}
```

#### Checkout (Source Control)

| Function | Description |
|----------|-------------|
| `CheckoutAsset(AssetToCheckout)` | Check out asset for editing |
| `CheckoutLoadedAsset(AssetToCheckout)` | Check out a loaded asset |
| `CheckoutDirectory(DirectoryPath, bRecursive)` | Check out all assets in directory |

### UEditorUtilityLibrary — Content Browser & Selection

**CDO Path**: `/Script/Blutility.Default__EditorUtilityLibrary`

| Function | Description |
|----------|-------------|
| `GetSelectedAssets()` | Get currently selected assets in Content Browser |
| `GetSelectedAssetData()` | Get selected asset metadata |
| `GetSelectedAssetsOfClass(AssetClass)` | Get selected assets filtered by class |
| `GetCurrentContentBrowserPath()` | Get the current path shown in Content Browser |
| `GetSelectedFolderPaths()` | Get the folder paths selected in Content Browser |
| `SyncBrowserToFolders(FolderList)` | Navigate Content Browser to specified folders |

##### Example: Get selected assets of a specific class

```json
{"object":"/Script/Blutility.Default__EditorUtilityLibrary","function":"GetSelectedAssetsOfClass","params":{"AssetClass":"/Script/Engine.Material"}}
```

##### Example: Navigate Content Browser to a folder

```json
{"object":"/Script/Blutility.Default__EditorUtilityLibrary","function":"SyncBrowserToFolders","params":{"FolderList":["/Game/Materials"]}}
```

##### Example: Get current Content Browser path

```json
{"object":"/Script/Blutility.Default__EditorUtilityLibrary","function":"GetCurrentContentBrowserPath"}
```

### UAssetEditorSubsystem

**CDO Path**: Use via `call` on the subsystem (get instance via `FindObjectInstances`)

| Function | Description |
|----------|-------------|
| `OpenEditorForAsset(Asset)` | Open asset editor |
| `CloseAllEditorsForAsset(Asset)` | Close all editors for asset |

## Common Patterns

### Browse content directory

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"ListAssets","params":{"DirectoryPath":"/Game/Materials","bRecursive":true,"bIncludeFolder":false}}
```

### Duplicate and rename an asset

First duplicate, then rename (run as separate calls):

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"DuplicateAsset","params":{"SourceAssetPath":"/Game/Materials/M_Base","DestinationAssetPath":"/Game/Materials/M_BaseCopy"}}
```

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"RenameAsset","params":{"SourceAssetPath":"/Game/Materials/M_BaseCopy","DestinationAssetPath":"/Game/Materials/M_NewName"}}
```

### Delete an asset

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"DeleteAsset","params":{"AssetPathToDelete":"/Game/Materials/M_Unused"}}
```

### Force-delete assets ignoring references

```json
{"object":"/Script/UnrealClientProtocolEditor.Default__AssetEditorOperationLibrary","function":"ForceDeleteAssets","params":{"AssetPaths":["/Game/OldAssets/M_Deprecated"]}}
```

### Query dependencies via AssetRegistry

First get the registry, then call GetDependencies on it (run as separate calls):

```json
{"object":"/Script/AssetRegistry.Default__AssetRegistryHelpers","function":"GetAssetRegistry"}
```

Then on the returned registry path:

```json
{"object":"<returned_registry_path>","function":"GetDependencies","params":{"PackageName":"/Game/Materials/M_Example","DependencyOptions":{},"OutDependencies":[]}}
```

### Find all materials in project

```json
{"object":"/Script/AssetRegistry.Default__AssetRegistryHelpers","function":"GetAssetRegistry"}
```

Then on the returned registry:

```json
{"object":"<registry_path>","function":"GetAssetsByClass","params":{"ClassPathName":"/Script/Engine.Material","OutAssetData":[],"bSearchSubClasses":false}}
```

### Save all dirty assets in a directory

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"SaveDirectory","params":{"DirectoryPath":"/Game/Materials","bOnlyIfIsDirty":true,"bRecursive":true}}
```

### Consolidate and clean up

Replace references to old assets with a canonical asset, then fix redirectors:

```json
{"object":"/Script/EditorScriptingUtilities.Default__EditorAssetLibrary","function":"ConsolidateAssets","params":{"AssetToConsolidateTo":"/Game/Materials/M_Master.M_Master","AssetsToConsolidate":["/Game/Materials/M_Duplicate1.M_Duplicate1","/Game/Materials/M_Duplicate2.M_Duplicate2"]}}
```

```json
{"object":"/Script/UnrealClientProtocolEditor.Default__AssetEditorOperationLibrary","function":"FixupReferencers","params":{"AssetPaths":["/Game/Materials/M_Duplicate1","/Game/Materials/M_Duplicate2"]}}
```
