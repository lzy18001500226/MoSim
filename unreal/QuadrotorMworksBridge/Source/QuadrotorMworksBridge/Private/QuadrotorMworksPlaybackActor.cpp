#include "QuadrotorMworksPlaybackActor.h"

#include "Components/SceneComponent.h"
#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
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
    ReferenceMarker->SetupAttachment(SceneRoot);
    RadarDirectionMarker->SetupAttachment(SceneRoot);
    ReferenceMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RadarDirectionMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ReferenceMarker->SetUsingAbsoluteLocation(true);
    ReferenceMarker->SetUsingAbsoluteRotation(true);
    ReferenceMarker->SetUsingAbsoluteScale(true);
    RadarDirectionMarker->SetUsingAbsoluteLocation(true);
    RadarDirectionMarker->SetUsingAbsoluteRotation(true);
    RadarDirectionMarker->SetUsingAbsoluteScale(true);

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
    auto ApplyColor = [this](UStaticMeshComponent* Component, const FLinearColor& Color)
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
}

void AQuadrotorMworksPlaybackActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    ApplyPropellerVisuals();
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
}
