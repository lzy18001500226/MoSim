#include "QuadrotorMworksPlaybackActor.h"

#include "Components/SceneComponent.h"
#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/MeshComponent.h"
#include "Materials/MaterialInterface.h"
#include "Misc/Paths.h"
#include "ProceduralMeshComponent.h"
#include "QuadrotorMworksMapActor.h"
#include "QuadrotorMworksPlaybackComponent.h"
#include "QuadrotorMworksUdpReceiverComponent.h"
#include "UObject/UObjectGlobals.h"
#include "UObject/ConstructorHelpers.h"

AQuadrotorMworksPlaybackActor::AQuadrotorMworksPlaybackActor()
{
    PrimaryActorTick.bCanEverTick = true;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(SceneRoot);

    BodyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyMesh"));
    BodyMesh->SetupAttachment(SceneRoot);

    LocalPlanSpline = CreateDefaultSubobject<USplineComponent>(TEXT("LocalPlanSpline"));
    TrajectoryTrailSpline = CreateDefaultSubobject<USplineComponent>(TEXT("TrajectoryTrailSpline"));
    LocalPlanSpline->SetupAttachment(SceneRoot);
    TrajectoryTrailSpline->SetupAttachment(SceneRoot);
    LocalPlanSpline->SetRelativeTransform(FTransform::Identity);
    TrajectoryTrailSpline->SetRelativeTransform(FTransform::Identity);
    LocalPlanSpline->SetUsingAbsoluteLocation(true);
    LocalPlanSpline->SetUsingAbsoluteRotation(true);
    LocalPlanSpline->SetUsingAbsoluteScale(true);
    TrajectoryTrailSpline->SetUsingAbsoluteLocation(true);
    TrajectoryTrailSpline->SetUsingAbsoluteRotation(true);
    TrajectoryTrailSpline->SetUsingAbsoluteScale(true);
    LocalPlanSpline->SetDrawDebug(true);
    TrajectoryTrailSpline->SetDrawDebug(true);

    ReferenceMarker = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ReferenceMarker"));
    RadarDirectionMarker = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RadarDirectionMarker"));
    RadarNearSectorMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("RadarNearSectorMesh"));
    RadarFarSectorMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("RadarFarSectorMesh"));
    LocalKnownMapMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("LocalKnownMapMesh"));
    LidarPointMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("LidarPointMesh"));
    ReferenceMarker->SetupAttachment(SceneRoot);
    RadarDirectionMarker->SetupAttachment(SceneRoot);
    RadarNearSectorMesh->SetupAttachment(SceneRoot);
    RadarFarSectorMesh->SetupAttachment(SceneRoot);
    LocalKnownMapMesh->SetupAttachment(SceneRoot);
    LidarPointMesh->SetupAttachment(SceneRoot);
    ReferenceMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarDirectionMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarNearSectorMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarFarSectorMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    LocalKnownMapMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    LidarPointMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ReferenceMarker->SetUsingAbsoluteLocation(true);
    ReferenceMarker->SetUsingAbsoluteRotation(true);
    ReferenceMarker->SetUsingAbsoluteScale(true);
    RadarDirectionMarker->SetUsingAbsoluteLocation(true);
    RadarDirectionMarker->SetUsingAbsoluteRotation(true);
    RadarDirectionMarker->SetUsingAbsoluteScale(true);
    RadarNearSectorMesh->SetUsingAbsoluteLocation(true);
    RadarNearSectorMesh->SetUsingAbsoluteRotation(true);
    RadarNearSectorMesh->SetUsingAbsoluteScale(true);
    RadarFarSectorMesh->SetUsingAbsoluteLocation(true);
    RadarFarSectorMesh->SetUsingAbsoluteRotation(true);
    RadarFarSectorMesh->SetUsingAbsoluteScale(true);
    LocalKnownMapMesh->SetUsingAbsoluteLocation(true);
    LocalKnownMapMesh->SetUsingAbsoluteRotation(true);
    LocalKnownMapMesh->SetUsingAbsoluteScale(true);
    LidarPointMesh->SetUsingAbsoluteLocation(true);
    LidarPointMesh->SetUsingAbsoluteRotation(true);
    LidarPointMesh->SetUsingAbsoluteScale(true);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> BasicMaterial(TEXT("/Engine/BasicShapes/BasicShapeMaterial"));
    if (CubeMesh.Succeeded())
    {
        RadarDirectionMarker->SetStaticMesh(CubeMesh.Object);
        RadarDirectionMarker->SetRelativeScale3D(FVector(1.0f, 0.035f, 0.025f));
    }
    if (CylinderMesh.Succeeded())
    {
        ReferenceMarker->SetStaticMesh(CylinderMesh.Object);
        ReferenceMarker->SetRelativeScale3D(FVector(0.14f, 0.14f, 0.14f));
    }
    ReferenceMarker->SetVisibility(false);
    ReferenceMarker->SetHiddenInGame(true);
    RadarDirectionMarker->SetVisibility(false);
    RadarDirectionMarker->SetHiddenInGame(true);
    RadarNearSectorMesh->SetVisibility(false);
    RadarNearSectorMesh->SetHiddenInGame(true);
    RadarFarSectorMesh->SetVisibility(false);
    RadarFarSectorMesh->SetHiddenInGame(true);
    LocalKnownMapMesh->SetVisibility(false);
    LocalKnownMapMesh->SetHiddenInGame(true);
    LidarPointMesh->SetVisibility(false);
    LidarPointMesh->SetHiddenInGame(true);
    if (BasicMaterial.Succeeded())
    {
        BaseMaterial = BasicMaterial.Object;
    }
    ApplyDefaultMaterials();
    BodyMesh->SetVisibility(false);
    BodyMesh->SetHiddenInGame(true);
    ApplySunrayDaeDerivedVisualLayout();

    Receiver = CreateDefaultSubobject<UQuadrotorMworksUdpReceiverComponent>(TEXT("MworksUdpReceiver"));
    Playback = CreateDefaultSubobject<UQuadrotorMworksPlaybackComponent>(TEXT("MworksPlayback"));
}

void AQuadrotorMworksPlaybackActor::BeginPlay()
{
    Super::BeginPlay();

    LoadSunrayDaeDerivedVisualAsset();
}

void AQuadrotorMworksPlaybackActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    ApplyDefaultMaterials();
    ApplySunrayDaeDerivedVisualLayout();
}

void AQuadrotorMworksPlaybackActor::ApplyDefaultMaterials()
{
    ApplyMaterialColor(ReferenceMarker, ReferenceColor);
    ApplyMaterialColor(RadarDirectionMarker, RadarColor);
    ApplyMaterialColor(RadarNearSectorMesh, RadarColor);
    ApplyMaterialColor(RadarFarSectorMesh, RadarFarColor);
    ApplyMaterialColor(LocalKnownMapMesh, LocalKnownFreeColor);
    ApplyMaterialColor(LocalKnownMapMesh, LocalKnownOccupiedColor, 1);
    ApplyMaterialColor(LidarPointMesh, LidarPointColor);
}

namespace
{
FString ResolveProjectRelativePath(const FString& RelativePath)
{
    if (FPaths::IsRelative(RelativePath))
    {
        return FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), RelativePath);
    }
    return FPaths::ConvertRelativePathToFull(RelativePath);
}

FString VectorToDiagnosticString(const FVector& Value)
{
    return FString::Printf(TEXT("(%.3f, %.3f, %.3f)"), Value.X, Value.Y, Value.Z);
}

}

void AQuadrotorMworksPlaybackActor::ApplyMaterialColor(UMeshComponent* Component, const FLinearColor& Color, int32 MaterialIndex) const
{
    if (!Component || !BaseMaterial)
    {
        return;
    }
    Component->SetMaterial(MaterialIndex, BaseMaterial);
}

bool AQuadrotorMworksPlaybackActor::LoadSunrayDaeDerivedVisualAsset()
{
    ApplySunrayDaeDerivedVisualLayout();
    if (!bUseDaeDerivedVehicleVisual)
    {
        UE_LOG(LogTemp, Error, TEXT("MoSim Sunray visual rejected: bUseDaeDerivedVehicleVisual=false. MWORKS STL/runtime animation fallback is disabled."));
        return false;
    }

    UStaticMesh* DaeDerivedMesh = LoadObject<UStaticMesh>(nullptr, *SunrayDaeDerivedStaticMeshPath);
    if (!DaeDerivedMesh)
    {
        const FString SourceAssetFullPath = ResolveProjectRelativePath(SunrayDaeDerivedSourceAssetPath);
        UE_LOG(
            LogTemp,
            Error,
            TEXT("MoSim Sunray DAE-derived visual asset missing: static_mesh=%s source_fbx=%s. Import this reviewed FBX/GLB into UE Content; MWORKS STL and MWORKS animation fallback are disabled."),
            *SunrayDaeDerivedStaticMeshPath,
            *SourceAssetFullPath);
        if (BodyMesh)
        {
            BodyMesh->SetVisibility(false);
            BodyMesh->SetHiddenInGame(true);
        }
        return false;
    }

    if (BodyMesh)
    {
        BodyMesh->SetStaticMesh(DaeDerivedMesh);
        BodyMesh->SetVisibility(true);
        BodyMesh->SetHiddenInGame(false);
    }
    if (bLogSunrayVisualDiagnostics)
    {
        LogVisualComponentDiagnostics(TEXT("SunrayDaeDerivedVehicleMesh"), BodyMesh);
    }
    return true;
}

void AQuadrotorMworksPlaybackActor::ApplySunrayDaeDerivedVisualLayout() const
{
    if (!BodyMesh)
    {
        return;
    }
    BodyMesh->SetRelativeLocation(SunrayDaeDerivedVisualLocation);
    BodyMesh->SetRelativeRotation(SunrayDaeDerivedVisualRotation);
    BodyMesh->SetRelativeScale3D(SunrayDaeDerivedVisualScale);
}

void AQuadrotorMworksPlaybackActor::LogVisualComponentDiagnostics(const TCHAR* Label, const UMeshComponent* Component) const
{
    if (!Component)
    {
        UE_LOG(LogTemp, Warning, TEXT("MoSim Sunray component diagnostic: %s missing"), Label);
        return;
    }

    const FBoxSphereBounds Bounds = Component->Bounds;
    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Sunray component diagnostic: %s visible=%s hidden_in_game=%s relative_location=%s relative_rotation=%s relative_scale=%s world_origin=%s box_extent=%s sphere_radius=%.3f"),
        Label,
        Component->IsVisible() ? TEXT("true") : TEXT("false"),
        Component->bHiddenInGame ? TEXT("true") : TEXT("false"),
        *VectorToDiagnosticString(Component->GetRelativeLocation()),
        *Component->GetRelativeRotation().ToString(),
        *VectorToDiagnosticString(Component->GetRelativeScale3D()),
        *VectorToDiagnosticString(Bounds.Origin),
        *VectorToDiagnosticString(Bounds.BoxExtent),
        Bounds.SphereRadius);
}

void AQuadrotorMworksPlaybackActor::LogFirstAppliedFrameDiagnosticsIfNeeded()
{
    if (!bLogFirstAppliedFrameDiagnostics || bLoggedFirstAppliedFrameDiagnostics || !Receiver || !Receiver->HasFrame() || !Playback)
    {
        return;
    }

    bLoggedFirstAppliedFrameDiagnostics = true;
    const FQuadrotorMworksFrame Frame = Receiver->GetLatestFrame();
    UE_LOG(
        LogTemp,
        Display,
        TEXT("MoSim Sunray first applied frame: scene=%s map=%s seq=%d mworks_position_m=%s unreal_location_cm=%s actor_location_cm=%s actor_rotation=%s coordinate_policy=%s"),
        *Frame.SceneId,
        *Frame.MapId,
        Frame.Sequence,
        *VectorToDiagnosticString(Frame.PositionMeters),
        *VectorToDiagnosticString(Playback->LatestUnrealLocation),
        *VectorToDiagnosticString(GetActorLocation()),
        *GetActorRotation().ToString(),
        *Frame.CoordinatePolicy);
    if (bLogSunrayVisualDiagnostics)
    {
        LogVisualComponentDiagnostics(TEXT("SunrayDaeDerivedVehicleAfterFirstFrame"), BodyMesh);
        LogVisualComponentDiagnostics(TEXT("ReferenceMarkerAfterFirstFrame"), ReferenceMarker);
        LogVisualComponentDiagnostics(TEXT("RadarDirectionMarkerAfterFirstFrame"), RadarDirectionMarker);
    }
}

void AQuadrotorMworksPlaybackActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (Playback && Receiver && Receiver->HasFrame())
    {
        Playback->ApplyFrame(Receiver->GetLatestFrame(), DeltaSeconds);
    }
    UpdateMapSelection();
    UpdateVisualHelpers();
    LogFirstAppliedFrameDiagnosticsIfNeeded();
}

void AQuadrotorMworksPlaybackActor::UpdateMapSelection() const
{
    if (!MapActor || !Receiver || !Receiver->HasFrame())
    {
        return;
    }

    MapActor->ApplyFrameMapSelection(Receiver->GetLatestFrame());
}

void AQuadrotorMworksPlaybackActor::UpdateSplineFromPoints(USplineComponent* Spline, const TArray<FVector>& Points) const
{
    if (!Spline)
    {
        return;
    }

    Spline->ClearSplinePoints(false);
    const int32 Count = MaxSplinePoints > 0 ? FMath::Min(MaxSplinePoints, Points.Num()) : Points.Num();
    const int32 StartIndex = Points.Num() - Count;
    for (int32 Index = FMath::Max(0, StartIndex); Index < Points.Num(); ++Index)
    {
        Spline->AddSplinePoint(Points[Index], ESplineCoordinateSpace::World, false);
    }
    Spline->UpdateSpline();
}

void AQuadrotorMworksPlaybackActor::UpdateVisualHelpers() const
{
    if (!bUpdateVisualHelpers || !Playback)
    {
        if (ReferenceMarker)
        {
            ReferenceMarker->SetVisibility(false);
            ReferenceMarker->SetHiddenInGame(true);
        }
        if (RadarDirectionMarker)
        {
            RadarDirectionMarker->SetVisibility(false);
            RadarDirectionMarker->SetHiddenInGame(true);
        }
        if (RadarNearSectorMesh)
        {
            RadarNearSectorMesh->ClearAllMeshSections();
            RadarNearSectorMesh->SetVisibility(false);
            RadarNearSectorMesh->SetHiddenInGame(true);
        }
        if (RadarFarSectorMesh)
        {
            RadarFarSectorMesh->ClearAllMeshSections();
            RadarFarSectorMesh->SetVisibility(false);
            RadarFarSectorMesh->SetHiddenInGame(true);
        }
        if (LocalKnownMapMesh)
        {
            LocalKnownMapMesh->ClearAllMeshSections();
            LocalKnownMapMesh->SetVisibility(false);
            LocalKnownMapMesh->SetHiddenInGame(true);
        }
        if (LidarPointMesh)
        {
            LidarPointMesh->ClearAllMeshSections();
            LidarPointMesh->SetVisibility(false);
            LidarPointMesh->SetHiddenInGame(true);
        }
        return;
    }

    UpdateSplineFromPoints(LocalPlanSpline, Playback->LocalPlanPointsUnreal);
    UpdateSplineFromPoints(TrajectoryTrailSpline, Playback->TrajectoryTrailUnreal);

    if (ReferenceMarker)
    {
        ReferenceMarker->SetVisibility(true);
        ReferenceMarker->SetHiddenInGame(false);
        ReferenceMarker->SetWorldLocation(Playback->ReferenceUnrealLocation);
        ReferenceMarker->SetWorldRotation(FRotator::ZeroRotator);
    }

    if (RadarDirectionMarker)
    {
        RadarDirectionMarker->SetVisibility(true);
        RadarDirectionMarker->SetHiddenInGame(false);
        const float Length = FMath::Max(Playback->RadarNearRadiusCentimeters, 50.0f);
        const float YawRadians = FMath::DegreesToRadians(Playback->RadarYawDegrees);
        const FVector Forward(FMath::Cos(YawRadians), FMath::Sin(YawRadians), 0.0f);
        RadarDirectionMarker->SetWorldLocation(Playback->LatestUnrealLocation + Forward * (0.5f * Length));
        RadarDirectionMarker->SetWorldRotation(FRotator(0.0f, Playback->RadarYawDegrees, 0.0f));
        RadarDirectionMarker->SetWorldScale3D(FVector(Length / 100.0f, 0.035f, 0.025f));
    }

    UpdateRadarSectorMesh();
    UpdateLocalKnownMapMesh();
    UpdateLidarPointMesh();
}

void AQuadrotorMworksPlaybackActor::UpdateRadarSectorMesh() const
{
    if (!Playback)
    {
        return;
    }

    if (!bShowRadarSectorMesh)
    {
        if (RadarNearSectorMesh)
        {
            RadarNearSectorMesh->ClearAllMeshSections();
        }
        if (RadarFarSectorMesh)
        {
            RadarFarSectorMesh->ClearAllMeshSections();
        }
        return;
    }

    BuildSectorMesh(RadarNearSectorMesh, 0.0f, Playback->RadarNearRadiusCentimeters, RadarColor);
    BuildSectorMesh(
        RadarFarSectorMesh,
        Playback->RadarNearRadiusCentimeters,
        Playback->RadarFarRadiusCentimeters,
        RadarFarColor);
}

void AQuadrotorMworksPlaybackActor::UpdateLocalKnownMapMesh() const
{
    if (!LocalKnownMapMesh || !Playback)
    {
        return;
    }

    if (!bShowLocalKnownMapMesh)
    {
        LocalKnownMapMesh->ClearAllMeshSections();
        return;
    }

    auto BuildCells = [this](const TArray<FVector>& Cells, const FLinearColor& Color, int32 SectionIndex)
    {
        TArray<FVector> Vertices;
        TArray<int32> Triangles;
        TArray<FVector> Normals;
        TArray<FVector2D> UVs;
        TArray<FLinearColor> VertexColors;
        TArray<FProcMeshTangent> Tangents;

        Vertices.Reserve(Cells.Num() * 4);
        Triangles.Reserve(Cells.Num() * 6);
        Normals.Reserve(Cells.Num() * 4);
        UVs.Reserve(Cells.Num() * 4);
        VertexColors.Reserve(Cells.Num() * 4);
        Tangents.Reserve(Cells.Num() * 4);

        for (const FVector& Center : Cells)
        {
            AppendCellQuad(
                Vertices,
                Triangles,
                Normals,
                UVs,
                VertexColors,
                Tangents,
                Center,
                Color,
                LocalKnownMapCellSizeCentimeters,
                LocalKnownMapHeightOffsetCentimeters);
        }

        if (Vertices.Num() == 0)
        {
            LocalKnownMapMesh->ClearMeshSection(SectionIndex);
            return;
        }

        LocalKnownMapMesh->CreateMeshSection_LinearColor(
            SectionIndex,
            Vertices,
            Triangles,
            Normals,
            UVs,
            VertexColors,
            Tangents,
            false);
    };

    if (Playback->LocalKnownFreeCellsUnreal.Num() == 0 && Playback->LocalKnownOccupiedCellsUnreal.Num() == 0)
    {
        LocalKnownMapMesh->ClearAllMeshSections();
        return;
    }

    BuildCells(Playback->LocalKnownFreeCellsUnreal, LocalKnownFreeColor, 0);
    BuildCells(Playback->LocalKnownOccupiedCellsUnreal, LocalKnownOccupiedColor, 1);
}

void AQuadrotorMworksPlaybackActor::UpdateLidarPointMesh() const
{
    if (!LidarPointMesh || !Playback)
    {
        return;
    }

    if (!bShowLidarPointMesh)
    {
        LidarPointMesh->ClearAllMeshSections();
        return;
    }

    if (Playback->LidarPointsUnreal.Num() == 0)
    {
        LidarPointMesh->ClearAllMeshSections();
        return;
    }

    TArray<FVector> Vertices;
    TArray<int32> Triangles;
    TArray<FVector> Normals;
    TArray<FVector2D> UVs;
    TArray<FLinearColor> VertexColors;
    TArray<FProcMeshTangent> Tangents;

    Vertices.Reserve(Playback->LidarPointsUnreal.Num() * 4);
    Triangles.Reserve(Playback->LidarPointsUnreal.Num() * 6);
    Normals.Reserve(Playback->LidarPointsUnreal.Num() * 4);
    UVs.Reserve(Playback->LidarPointsUnreal.Num() * 4);
    VertexColors.Reserve(Playback->LidarPointsUnreal.Num() * 4);
    Tangents.Reserve(Playback->LidarPointsUnreal.Num() * 4);

    for (const FVector& Point : Playback->LidarPointsUnreal)
    {
        AppendCellQuad(
            Vertices,
            Triangles,
            Normals,
            UVs,
            VertexColors,
            Tangents,
            Point,
            LidarPointColor,
            LidarPointSizeCentimeters,
            LidarPointHeightOffsetCentimeters);
    }

    LidarPointMesh->CreateMeshSection_LinearColor(
        0,
        Vertices,
        Triangles,
        Normals,
        UVs,
        VertexColors,
        Tangents,
        false);
}

void AQuadrotorMworksPlaybackActor::AppendCellQuad(
    TArray<FVector>& Vertices,
    TArray<int32>& Triangles,
    TArray<FVector>& Normals,
    TArray<FVector2D>& UVs,
    TArray<FLinearColor>& VertexColors,
    TArray<FProcMeshTangent>& Tangents,
    const FVector& Center,
    const FLinearColor& Color,
    float SizeCentimeters,
    float HeightOffsetCentimeters) const
{
    const int32 BaseIndex = Vertices.Num();
    const float HalfSize = FMath::Max(SizeCentimeters, 2.0f) * 0.5f;
    const FVector C = Center + FVector(0.0f, 0.0f, HeightOffsetCentimeters);
    Vertices.Append({
        C + FVector(-HalfSize, -HalfSize, 0.0f),
        C + FVector(HalfSize, -HalfSize, 0.0f),
        C + FVector(HalfSize, HalfSize, 0.0f),
        C + FVector(-HalfSize, HalfSize, 0.0f),
    });
    Triangles.Append({BaseIndex, BaseIndex + 1, BaseIndex + 2, BaseIndex, BaseIndex + 2, BaseIndex + 3});
    Normals.Append({FVector::UpVector, FVector::UpVector, FVector::UpVector, FVector::UpVector});
    UVs.Append({FVector2D(0.0f, 0.0f), FVector2D(1.0f, 0.0f), FVector2D(1.0f, 1.0f), FVector2D(0.0f, 1.0f)});
    VertexColors.Append({Color, Color, Color, Color});
    Tangents.Append({
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
        FProcMeshTangent(1.0f, 0.0f, 0.0f),
    });
}

void AQuadrotorMworksPlaybackActor::BuildSectorMesh(
    UProceduralMeshComponent* Mesh,
    float InnerRadiusCm,
    float OuterRadiusCm,
    const FLinearColor& Color) const
{
    if (!Mesh || !Playback || OuterRadiusCm <= 0.0f || Playback->RadarFovDegrees <= 0.0f)
    {
        return;
    }

    const int32 Segments = FMath::Max(RadarSectorSegments, 3);
    const float HalfFovRadians = FMath::DegreesToRadians(0.5f * Playback->RadarFovDegrees);
    const float YawRadians = FMath::DegreesToRadians(Playback->RadarYawDegrees);
    const FVector Origin = Playback->LatestUnrealLocation + FVector(0.0f, 0.0f, RadarSectorHeightOffsetCentimeters);

    TArray<FVector> Vertices;
    TArray<int32> Triangles;
    TArray<FVector> Normals;
    TArray<FVector2D> UVs;
    TArray<FLinearColor> VertexColors;
    TArray<FProcMeshTangent> Tangents;

    Vertices.Reserve((Segments + 1) * 2);
    for (int32 Index = 0; Index <= Segments; ++Index)
    {
        const float Alpha = static_cast<float>(Index) / static_cast<float>(Segments);
        const float Angle = YawRadians - HalfFovRadians + Alpha * 2.0f * HalfFovRadians;
        const FVector Direction(FMath::Cos(Angle), FMath::Sin(Angle), 0.0f);
        Vertices.Add(Origin + Direction * FMath::Max(InnerRadiusCm, 0.0f));
        Vertices.Add(Origin + Direction * OuterRadiusCm);
        Normals.Add(FVector::UpVector);
        Normals.Add(FVector::UpVector);
        UVs.Add(FVector2D(Alpha, 0.0f));
        UVs.Add(FVector2D(Alpha, 1.0f));
        VertexColors.Add(Color);
        VertexColors.Add(Color);
        Tangents.Add(FProcMeshTangent(1.0f, 0.0f, 0.0f));
        Tangents.Add(FProcMeshTangent(1.0f, 0.0f, 0.0f));
    }

    for (int32 Index = 0; Index < Segments; ++Index)
    {
        const int32 A = 2 * Index;
        const int32 B = A + 1;
        const int32 C = A + 2;
        const int32 D = A + 3;
        Triangles.Append({A, B, D, A, D, C});
    }

    Mesh->CreateMeshSection_LinearColor(
        0,
        Vertices,
        Triangles,
        Normals,
        UVs,
        VertexColors,
        Tangents,
        false);
}
