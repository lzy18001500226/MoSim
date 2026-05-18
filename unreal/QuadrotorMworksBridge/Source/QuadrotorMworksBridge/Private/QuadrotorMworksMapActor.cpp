#include "QuadrotorMworksMapActor.h"

#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Dom/JsonObject.h"
#include "Json.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
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
}

bool AQuadrotorMworksMapActor::LoadRenderMapSummary()
{
    if (bBuildPreviewOnBeginPlay)
    {
        ClearPreviewInstances();
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
