#include "QuadrotorMworksMapActor.h"

#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Dom/JsonObject.h"
#include "Json.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "QuadrotorMworksTypes.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
bool ReadVectorArray(const TSharedPtr<FJsonObject>& Object, const TCHAR* Field, FVector& Out)
{
    if (!Object.IsValid())
    {
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Object->TryGetArrayField(Field, Values) || !Values || Values->Num() < 3)
    {
        return false;
    }

    Out = FVector(
        (*Values)[0]->AsNumber(),
        (*Values)[1]->AsNumber(),
        (*Values)[2]->AsNumber());
    return true;
}

FVector MworksPositionToUnreal(const FVector& PositionMeters, float MetersToCentimeters)
{
    return FVector(
        PositionMeters.X * MetersToCentimeters,
        -PositionMeters.Y * MetersToCentimeters,
        PositionMeters.Z * MetersToCentimeters);
}

FVector MworksExtentToUnrealScale(const FVector& ExtentMeters)
{
    return FVector(
        FMath::Max(ExtentMeters.X, 0.001),
        FMath::Max(ExtentMeters.Y, 0.001),
        FMath::Max(ExtentMeters.Z, 0.001));
}

void ReadStringArray(const TSharedPtr<FJsonObject>& Object, const TCHAR* Field, TArray<FString>& Out)
{
    Out.Reset();
    if (!Object.IsValid())
    {
        return;
    }

    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Object->TryGetArrayField(Field, Values) || !Values)
    {
        return;
    }

    for (const TSharedPtr<FJsonValue>& Value : *Values)
    {
        if (Value.IsValid())
        {
            Out.Add(Value->AsString());
        }
    }
}

void AddBoxInstance(
    UInstancedStaticMeshComponent* Component,
    const FVector& CenterMeters,
    const FVector& ExtentMeters,
    float MetersToCentimeters)
{
    if (!Component)
    {
        return;
    }

    const FVector Location = MworksPositionToUnreal(CenterMeters, MetersToCentimeters);
    const FVector Scale = MworksExtentToUnrealScale(ExtentMeters);
    Component->AddInstance(FTransform(FRotator::ZeroRotator, Location, Scale));
}

void ClearSceneSourceState(AQuadrotorMworksMapActor& Actor)
{
    Actor.CurrentSceneSourceId = TEXT("");
    Actor.CurrentSceneSourceStatus = TEXT("");
    Actor.CurrentSceneProjectRoot = TEXT("");
    Actor.CurrentSceneUProjectPath = TEXT("");
    Actor.CurrentSceneRendererContentRoot = TEXT("");
    Actor.CurrentSceneRendererMapAsset = TEXT("");
    Actor.CurrentSceneRendererMapPackage = TEXT("");
    Actor.CurrentSceneTruthArtifacts.Reset();
    Actor.bCurrentSceneEditableCandidate = false;
    Actor.bCurrentSceneRenderableCandidate = false;
    Actor.bCurrentScenePlanningTruthReady = false;
    Actor.bCurrentSceneImportedIntoRenderer = false;
}
}

AQuadrotorMworksMapActor::AQuadrotorMworksMapActor()
{
    PrimaryActorTick.bCanEverTick = false;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(SceneRoot);

    TerrainInstances = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("TerrainInstances"));
    RandomColumnInstances = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("RandomColumnInstances"));
    WallInstances = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("WallInstances"));
    TerrainInstances->SetupAttachment(SceneRoot);
    RandomColumnInstances->SetupAttachment(SceneRoot);
    WallInstances->SetupAttachment(SceneRoot);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> BasicMaterial(TEXT("/Engine/BasicShapes/BasicShapeMaterial"));
    if (CubeMesh.Succeeded())
    {
        TerrainInstances->SetStaticMesh(CubeMesh.Object);
        RandomColumnInstances->SetStaticMesh(CubeMesh.Object);
        WallInstances->SetStaticMesh(CubeMesh.Object);
    }
    if (BasicMaterial.Succeeded())
    {
        BaseMaterial = BasicMaterial.Object;
    }

    TerrainInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RandomColumnInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    WallInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ApplyPreviewMaterials();
}

void AQuadrotorMworksMapActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    ApplyPreviewMaterials();
}

void AQuadrotorMworksMapActor::BeginPlay()
{
    Super::BeginPlay();
    LoadRenderMapSummary();
}

void AQuadrotorMworksMapActor::ApplyPreviewMaterials()
{
    auto ApplyColor = [this](UInstancedStaticMeshComponent* Component, const FLinearColor& Color)
    {
        if (!Component || !BaseMaterial)
        {
            return;
        }
        UMaterialInstanceDynamic* DynamicMaterial = Component->CreateDynamicMaterialInstance(0, BaseMaterial);
        if (DynamicMaterial)
        {
            DynamicMaterial->SetVectorParameterValue(TEXT("Color"), Color);
            DynamicMaterial->SetVectorParameterValue(TEXT("BaseColor"), Color);
            Component->SetMaterial(0, DynamicMaterial);
        }
    };

    ApplyColor(TerrainInstances, TerrainColor);
    ApplyColor(RandomColumnInstances, RandomColumnColor);
    ApplyColor(WallInstances, WallColor);
}

void AQuadrotorMworksMapActor::ClearPreviewInstances()
{
    if (TerrainInstances)
    {
        TerrainInstances->ClearInstances();
    }
    if (RandomColumnInstances)
    {
        RandomColumnInstances->ClearInstances();
    }
    if (WallInstances)
    {
        WallInstances->ClearInstances();
    }
    TerrainInstanceCount = 0;
    RandomColumnCount = 0;
    WallBoxCount = 0;
    BoundsMeters = FBox2D();
}

bool AQuadrotorMworksMapActor::LoadRenderMapSummary()
{
    if (bBuildPreviewOnBeginPlay)
    {
        ClearPreviewInstances();
    }

    if (RenderMapJson.IsEmpty())
    {
        CurrentSourceMap = TEXT("");
        UE_LOG(LogTemp, Display, TEXT("Selected scene profile has no static render map; preview instances cleared."));
        return true;
    }

    const FString FullPath = FPaths::ProjectContentDir() / RenderMapJson;
    FString Text;
    if (!FFileHelper::LoadFileToString(Text, *FullPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to read MWORKS render map: %s"), *FullPath);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to parse MWORKS render map JSON: %s"), *FullPath);
        return false;
    }

    const TSharedPtr<FJsonObject>* Obstacles = nullptr;
    if (Root->TryGetObjectField(TEXT("obstacles"), Obstacles) && Obstacles && Obstacles->IsValid())
    {
        RandomColumnCount = static_cast<int32>((*Obstacles)->GetIntegerField(TEXT("random_column_count")));
        WallBoxCount = static_cast<int32>((*Obstacles)->GetIntegerField(TEXT("wall_box_count")));
    }

    const TSharedPtr<FJsonObject>* Bounds = nullptr;
    if (Root->TryGetObjectField(TEXT("bounds_m"), Bounds) && Bounds && Bounds->IsValid())
    {
        const TArray<TSharedPtr<FJsonValue>>* X = nullptr;
        const TArray<TSharedPtr<FJsonValue>>* Y = nullptr;
        if ((*Bounds)->TryGetArrayField(TEXT("x"), X) && (*Bounds)->TryGetArrayField(TEXT("y"), Y) && X && Y && X->Num() >= 2 && Y->Num() >= 2)
        {
            BoundsMeters = FBox2D(
                FVector2D((*X)[0]->AsNumber(), (*Y)[0]->AsNumber()),
                FVector2D((*X)[1]->AsNumber(), (*Y)[1]->AsNumber()));
        }
    }

    if (bBuildPreviewOnBeginPlay)
    {
        const TSharedPtr<FJsonObject>* Terrain = nullptr;
        if (Root->TryGetObjectField(TEXT("terrain"), Terrain) && Terrain && Terrain->IsValid())
        {
            const TArray<TSharedPtr<FJsonValue>>* Origin = nullptr;
            const TArray<TSharedPtr<FJsonValue>>* Count = nullptr;
            const TArray<TSharedPtr<FJsonValue>>* HeightRows = nullptr;
            double CellMeters = 1.0;
            if ((*Terrain)->TryGetArrayField(TEXT("origin_m"), Origin)
                && (*Terrain)->TryGetArrayField(TEXT("count"), Count)
                && (*Terrain)->TryGetArrayField(TEXT("height_m"), HeightRows)
                && (*Terrain)->TryGetNumberField(TEXT("cell_m"), CellMeters)
                && Origin && Count && HeightRows && Origin->Num() >= 2 && Count->Num() >= 2)
            {
                const double OriginX = (*Origin)[0]->AsNumber();
                const double OriginY = (*Origin)[1]->AsNumber();
                const int32 Nx = static_cast<int32>((*Count)[0]->AsNumber());
                const int32 Ny = static_cast<int32>((*Count)[1]->AsNumber());
                const int32 Stride = FMath::Max(TerrainStride, 1);
                for (int32 Iy = 0; Iy < Ny - 1; Iy += Stride)
                {
                    if (!HeightRows->IsValidIndex(Iy) || !(*HeightRows)[Iy].IsValid())
                    {
                        continue;
                    }
                    const TArray<TSharedPtr<FJsonValue>>& Row = (*HeightRows)[Iy]->AsArray();
                    for (int32 Ix = 0; Ix < Nx - 1; Ix += Stride)
                    {
                        if (!Row.IsValidIndex(Ix) || !Row[Ix].IsValid())
                        {
                            continue;
                        }
                        const double HeightMeters = FMath::Max(Row[Ix]->AsNumber(), 0.02);
                        const FVector CenterMeters(
                            OriginX + (Ix + 0.5 * Stride) * CellMeters,
                            OriginY + (Iy + 0.5 * Stride) * CellMeters,
                            0.5 * HeightMeters);
                        const FVector ExtentMeters(CellMeters * Stride, CellMeters * Stride, HeightMeters);
                        AddBoxInstance(TerrainInstances, CenterMeters, ExtentMeters, MetersToCentimeters);
                        ++TerrainInstanceCount;
                    }
                }
            }
        }

        const TSharedPtr<FJsonObject>* PreviewObstacles = nullptr;
        if (Root->TryGetObjectField(TEXT("obstacles"), PreviewObstacles) && PreviewObstacles && PreviewObstacles->IsValid())
        {
            const TArray<TSharedPtr<FJsonValue>>* RandomColumns = nullptr;
            if ((*PreviewObstacles)->TryGetArrayField(TEXT("random_columns"), RandomColumns) && RandomColumns)
            {
                const int32 Limit = MaxRandomColumnInstances > 0 ? FMath::Min(MaxRandomColumnInstances, RandomColumns->Num()) : RandomColumns->Num();
                for (int32 Index = 0; Index < Limit; ++Index)
                {
                    const TSharedPtr<FJsonObject> Box = (*RandomColumns)[Index]->AsObject();
                    FVector CenterMeters;
                    FVector ExtentMeters;
                    if (ReadVectorArray(Box, TEXT("center_m"), CenterMeters) && ReadVectorArray(Box, TEXT("extent_m"), ExtentMeters))
                    {
                        AddBoxInstance(RandomColumnInstances, CenterMeters, ExtentMeters, MetersToCentimeters);
                    }
                }
            }

            const TArray<TSharedPtr<FJsonValue>>* Walls = nullptr;
            if ((*PreviewObstacles)->TryGetArrayField(TEXT("wall_boxes"), Walls) && Walls)
            {
                const int32 Limit = MaxWallInstances > 0 ? FMath::Min(MaxWallInstances, Walls->Num()) : Walls->Num();
                for (int32 Index = 0; Index < Limit; ++Index)
                {
                    const TSharedPtr<FJsonObject> Box = (*Walls)[Index]->AsObject();
                    FVector CenterMeters;
                    FVector ExtentMeters;
                    if (ReadVectorArray(Box, TEXT("center_m"), CenterMeters) && ReadVectorArray(Box, TEXT("extent_m"), ExtentMeters))
                    {
                        AddBoxInstance(WallInstances, CenterMeters, ExtentMeters, MetersToCentimeters);
                    }
                }
            }
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("Loaded MWORKS render map %s: terrain_instances=%d random_columns=%d wall_boxes=%d"),
        *FullPath,
        TerrainInstanceCount,
        RandomColumnCount,
        WallBoxCount);
    return true;
}

bool AQuadrotorMworksMapActor::ResolveMapId(const FString& MapId)
{
    if (MapId.IsEmpty())
    {
        return false;
    }

    const FString ProfilesPath = FPaths::ProjectContentDir() / SceneProfilesJson;
    FString ProfilesText;
    if (FFileHelper::LoadFileToString(ProfilesText, *ProfilesPath))
    {
        TSharedPtr<FJsonObject> ProfilesRoot;
        const TSharedRef<TJsonReader<>> ProfilesReader = TJsonReaderFactory<>::Create(ProfilesText);
        if (FJsonSerializer::Deserialize(ProfilesReader, ProfilesRoot) && ProfilesRoot.IsValid())
        {
            const TArray<TSharedPtr<FJsonValue>>* Profiles = nullptr;
            if (ProfilesRoot->TryGetArrayField(TEXT("profiles"), Profiles) && Profiles)
            {
                for (const TSharedPtr<FJsonValue>& ProfileValue : *Profiles)
                {
                    const TSharedPtr<FJsonObject> Profile = ProfileValue.IsValid() ? ProfileValue->AsObject() : nullptr;
                    if (!Profile.IsValid())
                    {
                        continue;
                    }

                    const TArray<TSharedPtr<FJsonValue>>* MapIds = nullptr;
                    if (!Profile->TryGetArrayField(TEXT("map_ids"), MapIds) || !MapIds)
                    {
                        continue;
                    }
                    bool bMatches = false;
                    for (const TSharedPtr<FJsonValue>& Value : *MapIds)
                    {
                        if (Value.IsValid() && Value->AsString() == MapId)
                        {
                            bMatches = true;
                            break;
                        }
                    }
                    if (!bMatches)
                    {
                        continue;
                    }

                    CurrentMapId = MapId;
                    ClearSceneSourceState(*this);
                    Profile->TryGetStringField(TEXT("profile_id"), CurrentSceneProfileId);
                    Profile->TryGetStringField(TEXT("purpose"), CurrentScenePurpose);
                    Profile->TryGetStringField(TEXT("render_map_json"), RenderMapJson);
                    CurrentSourceMap = RenderMapJson;
                    CurrentMigrationStatus = TEXT("project_owned_profile");
                    bCurrentMapDirectUseSupported = true;
                    bCurrentMapEditorOpenSupported = true;
                    UE_LOG(
                        LogTemp,
                        Display,
                        TEXT("Selected project-owned map_id=%s profile=%s render_map=%s"),
                        *CurrentMapId,
                        *CurrentSceneProfileId,
                        *RenderMapJson);
                    LoadRenderMapSummary();
                    return true;
                }
            }
        }
    }

    const FString FullPath = FPaths::ProjectContentDir() / SceneRegistryJson;
    FString Text;
    if (!FFileHelper::LoadFileToString(Text, *FullPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to read RflySim scene registry: %s"), *FullPath);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to parse RflySim scene registry: %s"), *FullPath);
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Scenes = nullptr;
    if (!Root->TryGetArrayField(TEXT("scenes"), Scenes) || !Scenes)
    {
        UE_LOG(LogTemp, Warning, TEXT("RflySim scene registry has no scenes array: %s"), *FullPath);
        return false;
    }

    for (const TSharedPtr<FJsonValue>& SceneValue : *Scenes)
    {
        const TSharedPtr<FJsonObject> Scene = SceneValue.IsValid() ? SceneValue->AsObject() : nullptr;
        if (!Scene.IsValid())
        {
            continue;
        }

        FString SceneId;
        Scene->TryGetStringField(TEXT("scene_id"), SceneId);
        if (SceneId != MapId)
        {
            continue;
        }

        CurrentMapId = MapId;
        ClearSceneSourceState(*this);
        Scene->TryGetStringField(TEXT("purpose"), CurrentScenePurpose);
        Scene->TryGetStringField(TEXT("relative_path"), CurrentSourceMap);
        Scene->TryGetStringField(TEXT("migration_status"), CurrentMigrationStatus);
        Scene->TryGetBoolField(TEXT("direct_use_supported"), bCurrentMapDirectUseSupported);
        Scene->TryGetBoolField(TEXT("direct_editor_open_supported"), bCurrentMapEditorOpenSupported);
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Selected map_id=%s source=%s migration=%s direct_use=%s editor_open=%s"),
            *CurrentMapId,
            *CurrentSourceMap,
            *CurrentMigrationStatus,
            bCurrentMapDirectUseSupported ? TEXT("true") : TEXT("false"),
            bCurrentMapEditorOpenSupported ? TEXT("true") : TEXT("false"));
        return true;
    }

    UE_LOG(LogTemp, Warning, TEXT("Unknown map_id in scene registry: %s"), *MapId);
    return false;
}

bool AQuadrotorMworksMapActor::ResolveSceneSourceId(const FString& SceneSourceId)
{
    if (SceneSourceId.IsEmpty())
    {
        return false;
    }

    const FString FullPath = FPaths::ProjectContentDir() / SceneSourceRegistryJson;
    FString Text;
    if (!FFileHelper::LoadFileToString(Text, *FullPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to read MoSim scene source registry: %s"), *FullPath);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to parse MoSim scene source registry: %s"), *FullPath);
        return false;
    }

    const TSharedPtr<FJsonObject>* Fallback = nullptr;
    if (!Root->TryGetObjectField(TEXT("local_editable_fallback"), Fallback) || !Fallback || !Fallback->IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("MoSim scene source registry has no local_editable_fallback object: %s"), *FullPath);
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Sources = nullptr;
    if (!(*Fallback)->TryGetArrayField(TEXT("scene_sources"), Sources) || !Sources)
    {
        UE_LOG(LogTemp, Warning, TEXT("MoSim scene source registry has no scene_sources array: %s"), *FullPath);
        return false;
    }

    for (const TSharedPtr<FJsonValue>& SourceValue : *Sources)
    {
        const TSharedPtr<FJsonObject> Source = SourceValue.IsValid() ? SourceValue->AsObject() : nullptr;
        if (!Source.IsValid())
        {
            continue;
        }

        FString SourceId;
        Source->TryGetStringField(TEXT("scene_source_id"), SourceId);
        if (SourceId != SceneSourceId)
        {
            continue;
        }

        CurrentSceneSourceId = SourceId;
        Source->TryGetStringField(TEXT("status"), CurrentSceneSourceStatus);
        Source->TryGetStringField(TEXT("project_root"), CurrentSceneProjectRoot);
        Source->TryGetStringField(TEXT("uproject_path"), CurrentSceneUProjectPath);
        Source->TryGetStringField(TEXT("renderer_content_root"), CurrentSceneRendererContentRoot);
        Source->TryGetStringField(TEXT("renderer_map_asset"), CurrentSceneRendererMapAsset);
        Source->TryGetStringField(TEXT("renderer_map_package"), CurrentSceneRendererMapPackage);
        Source->TryGetBoolField(TEXT("editable_candidate"), bCurrentSceneEditableCandidate);
        Source->TryGetBoolField(TEXT("renderable_candidate"), bCurrentSceneRenderableCandidate);
        Source->TryGetBoolField(TEXT("planning_truth_ready"), bCurrentScenePlanningTruthReady);
        ReadStringArray(Source, TEXT("truth_artifacts"), CurrentSceneTruthArtifacts);
        Source->TryGetBoolField(TEXT("imported_into_renderer"), bCurrentSceneImportedIntoRenderer);

        CurrentMapId = SourceId;
        CurrentScenePurpose = TEXT("local_editable_scene_source");
        CurrentSourceMap = bCurrentSceneImportedIntoRenderer ? CurrentSceneRendererMapPackage : CurrentSceneProjectRoot;
        CurrentMigrationStatus = CurrentSceneSourceStatus;
        bCurrentMapDirectUseSupported = bCurrentSceneImportedIntoRenderer;
        bCurrentMapEditorOpenSupported = bCurrentSceneEditableCandidate && bCurrentSceneRenderableCandidate;
        RenderMapJson = TEXT("");
        ClearPreviewInstances();

        UE_LOG(
            LogTemp,
            Display,
            TEXT("Selected MoSim scene_source_id=%s status=%s editable=%s renderable=%s truth_ready=%s truth_artifacts=%d project=%s renderer_map=%s imported_into_renderer=%s"),
            *CurrentSceneSourceId,
            *CurrentSceneSourceStatus,
            bCurrentSceneEditableCandidate ? TEXT("true") : TEXT("false"),
            bCurrentSceneRenderableCandidate ? TEXT("true") : TEXT("false"),
            bCurrentScenePlanningTruthReady ? TEXT("true") : TEXT("false"),
            CurrentSceneTruthArtifacts.Num(),
            *CurrentSceneProjectRoot,
            *CurrentSceneRendererMapPackage,
            bCurrentSceneImportedIntoRenderer ? TEXT("true") : TEXT("false"));
        return true;
    }

    UE_LOG(LogTemp, Warning, TEXT("Unknown scene_source_id in MoSim scene source registry: %s"), *SceneSourceId);
    return false;
}

void AQuadrotorMworksMapActor::ApplyFrameMapSelection(const FQuadrotorMworksFrame& Frame)
{
    if (Frame.MapId.IsEmpty() || Frame.MapId == CurrentMapId)
    {
        return;
    }
    if (Frame.MapId.StartsWith(TEXT("local_")) && ResolveSceneSourceId(Frame.MapId))
    {
        return;
    }
    if (!ResolveMapId(Frame.MapId))
    {
        ResolveSceneSourceId(Frame.MapId);
    }
}
