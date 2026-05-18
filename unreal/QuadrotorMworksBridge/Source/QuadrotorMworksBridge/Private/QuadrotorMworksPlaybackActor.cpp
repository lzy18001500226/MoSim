#include "QuadrotorMworksPlaybackActor.h"

#include "Components/SceneComponent.h"
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
    }
    if (CylinderMesh.Succeeded())
    {
        UStaticMeshComponent* Props[4] = {PropellerMesh1, PropellerMesh2, PropellerMesh3, PropellerMesh4};
        for (UStaticMeshComponent* Prop : Props)
        {
            Prop->SetStaticMesh(CylinderMesh.Object);
            Prop->SetRelativeScale3D(FVector(0.24f, 0.24f, 0.015f));
        }
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
}

void AQuadrotorMworksPlaybackActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    ApplyPropellerVisuals();
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
