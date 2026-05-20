#include "QuadrotorMworksPlaybackActor.h"

#include "Components/SceneComponent.h"
#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/MeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "ProceduralMeshComponent.h"
#include "QuadrotorMworksMapActor.h"
#include "QuadrotorMworksPlaybackComponent.h"
#include "QuadrotorMworksUdpReceiverComponent.h"
#include "UObject/ConstructorHelpers.h"

AQuadrotorMworksPlaybackActor::AQuadrotorMworksPlaybackActor()
{
    PrimaryActorTick.bCanEverTick = true;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(SceneRoot);

    BodyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyMesh"));
    BodyMesh->SetupAttachment(SceneRoot);

    PropellerMesh1 = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Propeller1"));
    PropellerMesh2 = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Propeller2"));
    PropellerMesh3 = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Propeller3"));
    PropellerMesh4 = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Propeller4"));
    PropellerMesh1->SetupAttachment(SceneRoot);
    PropellerMesh2->SetupAttachment(SceneRoot);
    PropellerMesh3->SetupAttachment(SceneRoot);
    PropellerMesh4->SetupAttachment(SceneRoot);

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
    ReferenceMarker->SetupAttachment(SceneRoot);
    RadarDirectionMarker->SetupAttachment(SceneRoot);
    RadarNearSectorMesh->SetupAttachment(SceneRoot);
    RadarFarSectorMesh->SetupAttachment(SceneRoot);
    ReferenceMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarDirectionMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarNearSectorMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarFarSectorMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
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

    PropellerMesh1->SetRelativeLocation(FVector(32.0, 32.0, 0.0));
    PropellerMesh2->SetRelativeLocation(FVector(32.0, -32.0, 0.0));
    PropellerMesh3->SetRelativeLocation(FVector(-32.0, -32.0, 0.0));
    PropellerMesh4->SetRelativeLocation(FVector(-32.0, 32.0, 0.0));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> BasicMaterial(TEXT("/Engine/BasicShapes/BasicShapeMaterial"));
    if (CubeMesh.Succeeded())
    {
        BodyMesh->SetStaticMesh(CubeMesh.Object);
        BodyMesh->SetRelativeScale3D(FVector(0.75f, 0.42f, 0.12f));
        RadarDirectionMarker->SetStaticMesh(CubeMesh.Object);
        RadarDirectionMarker->SetRelativeScale3D(FVector(1.0f, 0.035f, 0.025f));
    }
    if (CylinderMesh.Succeeded())
    {
        UStaticMeshComponent* Props[4] = {PropellerMesh1, PropellerMesh2, PropellerMesh3, PropellerMesh4};
        for (UStaticMeshComponent* Prop : Props)
        {
            Prop->SetStaticMesh(CylinderMesh.Object);
            Prop->SetRelativeScale3D(FVector(0.24f, 0.24f, 0.015f));
        }
        ReferenceMarker->SetStaticMesh(CylinderMesh.Object);
        ReferenceMarker->SetRelativeScale3D(FVector(0.14f, 0.14f, 0.14f));
    }
    if (BasicMaterial.Succeeded())
    {
        BaseMaterial = BasicMaterial.Object;
    }
    ApplyDefaultMaterials();

    Receiver = CreateDefaultSubobject<UQuadrotorMworksUdpReceiverComponent>(TEXT("MworksUdpReceiver"));
    Playback = CreateDefaultSubobject<UQuadrotorMworksPlaybackComponent>(TEXT("MworksPlayback"));
}

void AQuadrotorMworksPlaybackActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    ApplyDefaultMaterials();
}

void AQuadrotorMworksPlaybackActor::ApplyDefaultMaterials()
{
    auto ApplyColor = [this](UMeshComponent* Component, const FLinearColor& Color)
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

    ApplyColor(BodyMesh, BodyColor);
    ApplyColor(PropellerMesh1, PropellerColor);
    ApplyColor(PropellerMesh2, PropellerColor);
    ApplyColor(PropellerMesh3, PropellerColor);
    ApplyColor(PropellerMesh4, PropellerColor);
    ApplyColor(ReferenceMarker, ReferenceColor);
    ApplyColor(RadarDirectionMarker, RadarColor);
    ApplyColor(RadarNearSectorMesh, RadarColor);
    ApplyColor(RadarFarSectorMesh, RadarFarColor);
}

void AQuadrotorMworksPlaybackActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    ApplyPropellerVisuals();
    UpdateMapSelection();
    UpdateVisualHelpers();
}

void AQuadrotorMworksPlaybackActor::ApplyPropellerVisuals() const
{
    if (!Playback || Playback->PropellerAnglesDegrees.Num() < 4)
    {
        return;
    }

    UStaticMeshComponent* Props[4] = {PropellerMesh1, PropellerMesh2, PropellerMesh3, PropellerMesh4};
    for (int32 Index = 0; Index < 4; ++Index)
    {
        if (Props[Index])
        {
            Props[Index]->SetRelativeRotation(FRotator(0.0f, Playback->PropellerAnglesDegrees[Index], 0.0f));
        }
    }
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
        return;
    }

    UpdateSplineFromPoints(LocalPlanSpline, Playback->LocalPlanPointsUnreal);
    UpdateSplineFromPoints(TrajectoryTrailSpline, Playback->TrajectoryTrailUnreal);

    if (ReferenceMarker)
    {
        ReferenceMarker->SetWorldLocation(Playback->ReferenceUnrealLocation);
        ReferenceMarker->SetWorldRotation(FRotator::ZeroRotator);
    }

    if (RadarDirectionMarker)
    {
        const float Length = FMath::Max(Playback->RadarNearRadiusCentimeters, 50.0f);
        const float YawRadians = FMath::DegreesToRadians(Playback->RadarYawDegrees);
        const FVector Forward(FMath::Cos(YawRadians), FMath::Sin(YawRadians), 0.0f);
        RadarDirectionMarker->SetWorldLocation(Playback->LatestUnrealLocation + Forward * (0.5f * Length));
        RadarDirectionMarker->SetWorldRotation(FRotator(0.0f, Playback->RadarYawDegrees, 0.0f));
        RadarDirectionMarker->SetWorldScale3D(FVector(Length / 100.0f, 0.035f, 0.025f));
    }

    UpdateRadarSectorMesh();
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
