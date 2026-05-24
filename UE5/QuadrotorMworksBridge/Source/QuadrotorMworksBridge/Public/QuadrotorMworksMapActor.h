#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "QuadrotorMworksMapActor.generated.h"

struct FQuadrotorMworksFrame;
class UInstancedStaticMeshComponent;
class UMaterialInterface;
class USceneComponent;

UCLASS()
class QUADROTORMWORKSBRIDGE_API AQuadrotorMworksMapActor : public AActor
{
    GENERATED_BODY()

public:
    AQuadrotorMworksMapActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS Map")
    USceneComponent* SceneRoot = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS Map")
    UInstancedStaticMeshComponent* TerrainInstances = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS Map")
    UInstancedStaticMeshComponent* RandomColumnInstances = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MWORKS Map")
    UInstancedStaticMeshComponent* WallInstances = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map")
    FString RenderMapJson = TEXT("MworksData/map_open_blocks_render_map.json");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map")
    FString SceneRegistryJson = TEXT("MworksData/rflysim_scene_registry.json");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map")
    FString SceneProfilesJson = TEXT("MworksData/unreal_scene_profiles.json");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map")
    FString SceneSourceRegistryJson = TEXT("MworksData/scene_source_registry.json");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map")
    float MetersToCentimeters = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map")
    bool bBuildPreviewOnBeginPlay = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map", meta = (ClampMin = "1"))
    int32 TerrainStride = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map", meta = (ClampMin = "0"))
    int32 MaxRandomColumnInstances = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map", meta = (ClampMin = "0"))
    int32 MaxWallInstances = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map|Material")
    UMaterialInterface* BaseMaterial = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map|Material")
    FLinearColor TerrainColor = FLinearColor(0.72f, 0.82f, 0.70f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map|Material")
    FLinearColor RandomColumnColor = FLinearColor(0.58f, 0.58f, 0.58f, 1.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Map|Material")
    FLinearColor WallColor = FLinearColor(0.72f, 0.72f, 0.70f, 1.0f);

    UFUNCTION(BlueprintCallable, Category = "MWORKS Map")
    bool LoadRenderMapSummary();

    UFUNCTION(BlueprintCallable, Category = "MWORKS Map")
    bool ResolveMapId(const FString& MapId);

    UFUNCTION(BlueprintCallable, Category = "MWORKS Map")
    bool ResolveSceneSourceId(const FString& SceneSourceId);

    UFUNCTION(BlueprintCallable, Category = "MWORKS Map")
    void ApplyFrameMapSelection(const FQuadrotorMworksFrame& Frame);

    UFUNCTION(BlueprintCallable, Category = "MWORKS Map")
    void ClearPreviewInstances();

    UFUNCTION(BlueprintCallable, Category = "MWORKS Map")
    void ApplyPreviewMaterials();

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    int32 RandomColumnCount = 0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    int32 WallBoxCount = 0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    int32 TerrainInstanceCount = 0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FBox2D BoundsMeters;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FString CurrentMapId;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FString CurrentScenePurpose;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FString CurrentSourceMap;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FString CurrentMigrationStatus;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FString CurrentSceneProfileId;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FString CurrentSceneSourceId;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FString CurrentSceneSourceStatus;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FString CurrentSceneProjectRoot;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    FString CurrentSceneUProjectPath;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    TArray<FString> CurrentSceneTruthArtifacts;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    bool bCurrentSceneEditableCandidate = false;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    bool bCurrentSceneRenderableCandidate = false;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    bool bCurrentScenePlanningTruthReady = false;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    bool bCurrentSceneImportedIntoRenderer = false;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    bool bCurrentMapDirectUseSupported = false;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Map")
    bool bCurrentMapEditorOpenSupported = false;

protected:
    virtual void BeginPlay() override;
    virtual void OnConstruction(const FTransform& Transform) override;
};
