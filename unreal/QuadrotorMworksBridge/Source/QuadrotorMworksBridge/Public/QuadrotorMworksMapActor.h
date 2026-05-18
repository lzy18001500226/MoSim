#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "QuadrotorMworksMapActor.generated.h"

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

protected:
    virtual void BeginPlay() override;
    virtual void OnConstruction(const FTransform& Transform) override;
};
