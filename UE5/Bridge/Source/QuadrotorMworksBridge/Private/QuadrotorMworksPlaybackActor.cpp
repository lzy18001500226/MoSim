#include "QuadrotorMworksPlaybackActor.h"

#include "Components/SceneComponent.h"
#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/MeshComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/StaticMesh.h"
#include "HAL/PlatformTime.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "Misc/Paths.h"
#include "ProceduralMeshComponent.h"
#include "QuadrotorMworksMapActor.h"
#include "QuadrotorMworksPlaybackComponent.h"
#include "QuadrotorRotorAudioComponent.h"
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

    AcceptedPropellerRoot = CreateDefaultSubobject<USceneComponent>(TEXT("AcceptedPropellerRoot"));
    AcceptedPropellerRoot->SetupAttachment(SceneRoot);
    const TCHAR* PropellerComponentNames[] = {
        TEXT("AcceptedPropellerRotor0FrontRight"),
        TEXT("AcceptedPropellerRotor1BackLeft"),
        TEXT("AcceptedPropellerRotor2FrontLeft"),
        TEXT("AcceptedPropellerRotor3BackRight"),
    };
    // Accepted audit coordinates are Blender Z-up; UE import mirrors Blender Y.
    const FVector PropellerPivotsCm[] = {
        FVector(5.3745f, 5.3740f, -1.4052f),
        FVector(-5.3761f, -5.3760f, -1.4052f),
        FVector(5.3746f, -5.3759f, -1.4052f),
        FVector(-5.3761f, 5.3739f, -1.4052f),
    };
    for (int32 Index = 0; Index < 4; ++Index)
    {
        const FName PivotName(*FString::Printf(TEXT("%sPivot"), PropellerComponentNames[Index]));
        const FName MeshName(*FString::Printf(TEXT("%sMesh"), PropellerComponentNames[Index]));
        USceneComponent* Pivot = CreateDefaultSubobject<USceneComponent>(PivotName);
        UStaticMeshComponent* Mesh = CreateDefaultSubobject<UStaticMeshComponent>(MeshName);
        Pivot->SetupAttachment(AcceptedPropellerRoot);
        Mesh->SetupAttachment(Pivot);
        Pivot->SetRelativeLocation(PropellerPivotsCm[Index]);
        Mesh->SetRelativeLocation(-PropellerPivotsCm[Index]);
        Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Mesh->SetVisibility(false);
        Mesh->SetHiddenInGame(true);
        AcceptedPropellerPivots.Add(Pivot);
        AcceptedPropellerMeshes.Add(Mesh);
        AcceptedPropellerAnglesDegrees.Add(0.0f);
    }

    LocalPlanSpline = CreateDefaultSubobject<USplineComponent>(TEXT("LocalPlanSpline"));
    TrajectoryTrailSpline = CreateDefaultSubobject<USplineComponent>(TEXT("TrajectoryTrailSpline"));
    LocalPlanLineMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("LocalPlanLineMesh"));
    TrajectoryTrailLineMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("TrajectoryTrailLineMesh"));
    LocalPlanSpline->SetupAttachment(SceneRoot);
    TrajectoryTrailSpline->SetupAttachment(SceneRoot);
    LocalPlanLineMesh->SetupAttachment(SceneRoot);
    TrajectoryTrailLineMesh->SetupAttachment(SceneRoot);
    LocalPlanSpline->SetRelativeTransform(FTransform::Identity);
    TrajectoryTrailSpline->SetRelativeTransform(FTransform::Identity);
    LocalPlanSpline->SetUsingAbsoluteLocation(true);
    LocalPlanSpline->SetUsingAbsoluteRotation(true);
    LocalPlanSpline->SetUsingAbsoluteScale(true);
    TrajectoryTrailSpline->SetUsingAbsoluteLocation(true);
    TrajectoryTrailSpline->SetUsingAbsoluteRotation(true);
    TrajectoryTrailSpline->SetUsingAbsoluteScale(true);
    LocalPlanLineMesh->SetUsingAbsoluteLocation(true);
    LocalPlanLineMesh->SetUsingAbsoluteRotation(true);
    LocalPlanLineMesh->SetUsingAbsoluteScale(true);
    TrajectoryTrailLineMesh->SetUsingAbsoluteLocation(true);
    TrajectoryTrailLineMesh->SetUsingAbsoluteRotation(true);
    TrajectoryTrailLineMesh->SetUsingAbsoluteScale(true);
    LocalPlanSpline->SetDrawDebug(false);
    TrajectoryTrailSpline->SetDrawDebug(false);

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
    LocalPlanLineMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    TrajectoryTrailLineMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
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
    LocalPlanLineMesh->SetVisibility(false);
    LocalPlanLineMesh->SetHiddenInGame(true);
    TrajectoryTrailLineMesh->SetVisibility(false);
    TrajectoryTrailLineMesh->SetHiddenInGame(true);

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
    RotorAudio = CreateDefaultSubobject<UQuadrotorRotorAudioComponent>(TEXT("RotorAudio"));
}

void AQuadrotorMworksPlaybackActor::BeginPlay()
{
    Super::BeginPlay();

    LoadSunrayDaeDerivedVisualAsset();
    LoadAcceptedPropellerAssets();
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
    ApplyMaterialColor(LocalPlanLineMesh, LocalPlanColor);
    ApplyMaterialColor(TrajectoryTrailLineMesh, TrajectoryTrailColor);
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
    UMaterialInstanceDynamic* DynamicMaterial = UMaterialInstanceDynamic::Create(BaseMaterial, Component);
    if (DynamicMaterial)
    {
        DynamicMaterial->SetVectorParameterValue(TEXT("Color"), Color);
        DynamicMaterial->SetVectorParameterValue(TEXT("BaseColor"), Color);
        DynamicMaterial->SetVectorParameterValue(TEXT("TintColor"), Color);
        DynamicMaterial->SetScalarParameterValue(TEXT("Opacity"), Color.A);
        Component->SetMaterial(MaterialIndex, DynamicMaterial);
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

bool AQuadrotorMworksPlaybackActor::LoadAcceptedPropellerAssets()
{
    const TCHAR* AcceptedPropellerAssetPaths[] = {
        TEXT("/Game/Sunray150/TriBlade_flipped_around_screw_axis_rotor_0_front_right_sunray_cw_stl.TriBlade_flipped_around_screw_axis_rotor_0_front_right_sunray_cw_stl"),
        TEXT("/Game/Sunray150/TriBlade_flipped_around_screw_axis_rotor_1_back_left_sunray_cw_stl.TriBlade_flipped_around_screw_axis_rotor_1_back_left_sunray_cw_stl"),
        TEXT("/Game/Sunray150/TriBlade_flipped_around_screw_axis_rotor_2_front_left_sunray_cw_stl.TriBlade_flipped_around_screw_axis_rotor_2_front_left_sunray_cw_stl"),
        TEXT("/Game/Sunray150/TriBlade_flipped_around_screw_axis_rotor_3_back_right_sunray_cw_stl.TriBlade_flipped_around_screw_axis_rotor_3_back_right_sunray_cw_stl"),
    };

    bool bLoadedAll = AcceptedPropellerMeshes.Num() == 4;
    for (int32 Index = 0; Index < AcceptedPropellerMeshes.Num(); ++Index)
    {
        UStaticMeshComponent* PropellerMesh = AcceptedPropellerMeshes[Index];
        UStaticMesh* MeshAsset = Index < 4
            ? LoadObject<UStaticMesh>(nullptr, AcceptedPropellerAssetPaths[Index])
            : nullptr;
        if (!PropellerMesh || !MeshAsset)
        {
            bLoadedAll = false;
            if (PropellerMesh)
            {
                PropellerMesh->SetVisibility(false);
                PropellerMesh->SetHiddenInGame(true);
            }
            UE_LOG(
                LogTemp,
                Error,
                TEXT("MoSim accepted Sunray propeller missing: index=%d asset=%s"),
                Index,
                Index < 4 ? AcceptedPropellerAssetPaths[Index] : TEXT("invalid"));
            continue;
        }

        PropellerMesh->SetStaticMesh(MeshAsset);
        PropellerMesh->SetVisibility(true);
        PropellerMesh->SetHiddenInGame(false);
        if (bLogSunrayVisualDiagnostics)
        {
            LogVisualComponentDiagnostics(TEXT("AcceptedSunrayPropeller"), PropellerMesh);
        }
    }
    return bLoadedAll;
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
    if (AcceptedPropellerRoot)
    {
        AcceptedPropellerRoot->SetRelativeLocation(SunrayDaeDerivedVisualLocation);
        AcceptedPropellerRoot->SetRelativeRotation(SunrayDaeDerivedVisualRotation);
        AcceptedPropellerRoot->SetRelativeScale3D(SunrayDaeDerivedVisualScale);
    }
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
        const FQuadrotorMworksFrame Frame = Receiver->GetLatestFrame();
        Playback->ApplyFrame(Frame, DeltaSeconds);
        ++AppliedTicksInWindow;
        if (Frame.Sequence != LastAppliedSequence)
        {
            LastAppliedSequence = Frame.Sequence;
            ++UniqueFramesAppliedInWindow;
        }

        const double NowSeconds = FPlatformTime::Seconds();
        if (ApplyRateWindowStartSeconds <= 0.0)
        {
            ApplyRateWindowStartSeconds = NowSeconds;
        }
        const double ElapsedSeconds = NowSeconds - ApplyRateWindowStartSeconds;
        if (ElapsedSeconds >= 5.0)
        {
            UE_LOG(
                LogTemp,
                Display,
                TEXT("MoSim UE playback rates: game_apply=%.1fHz unique_udp_frames=%.1fHz last_seq=%d"),
                AppliedTicksInWindow / ElapsedSeconds,
                UniqueFramesAppliedInWindow / ElapsedSeconds,
                LastAppliedSequence);
            ApplyRateWindowStartSeconds = NowSeconds;
            AppliedTicksInWindow = 0;
            UniqueFramesAppliedInWindow = 0;
        }
    }
    UpdateAcceptedPropellers(DeltaSeconds);
    UpdateMapSelection();
    if (bUpdateVisualHelpers)
    {
        UpdateVisualHelpers();
    }
    LogFirstAppliedFrameDiagnosticsIfNeeded();
}

void AQuadrotorMworksPlaybackActor::UpdateAcceptedPropellers(float DeltaSeconds)
{
    if (!bAnimateAcceptedPropellers || !Playback || AcceptedPropellerPivots.Num() != 4 || AcceptedPropellerAnglesDegrees.Num() != 4)
    {
        return;
    }

    const TArray<double>& MotorCommand = Playback->LatestFrame.MotorCommand;
    double MaxAbsCommand = 0.0;
    for (double Command : MotorCommand)
    {
        MaxAbsCommand = FMath::Max(MaxAbsCommand, FMath::Abs(Command));
    }
    const bool bNormalizedInput = MaxAbsCommand <= 1.25;
    const float SpinDirections[] = {1.0f, 1.0f, -1.0f, -1.0f};
    for (int32 Index = 0; Index < AcceptedPropellerPivots.Num(); ++Index)
    {
        USceneComponent* Pivot = AcceptedPropellerPivots[Index];
        if (!Pivot)
        {
            continue;
        }

        const double RawCommand = MotorCommand.IsValidIndex(Index) ? FMath::Abs(MotorCommand[Index]) : 0.0;
        const float NormalizedCommand = bNormalizedInput
            ? FMath::Clamp(static_cast<float>(RawCommand), 0.0f, 1.0f)
            : FMath::Clamp(static_cast<float>(RawCommand) / FMath::Max(PropellerRawCommandScale, 1.0f), 0.0f, 1.0f);
        if (NormalizedCommand <= KINDA_SMALL_NUMBER)
        {
            continue;
        }

        const float DegreesPerSecond = FMath::Lerp(
            PropellerIdleVisualDegreesPerSecond,
            PropellerMaxVisualDegreesPerSecond,
            NormalizedCommand);
        AcceptedPropellerAnglesDegrees[Index] = FMath::Fmod(
            AcceptedPropellerAnglesDegrees[Index] + SpinDirections[Index] * DegreesPerSecond * DeltaSeconds,
            360.0f);
        Pivot->SetRelativeRotation(FRotator(0.0f, AcceptedPropellerAnglesDegrees[Index], 0.0f));
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
        if (LocalPlanLineMesh)
        {
            LocalPlanLineMesh->ClearAllMeshSections();
            LocalPlanLineMesh->SetVisibility(false);
            LocalPlanLineMesh->SetHiddenInGame(true);
        }
        if (TrajectoryTrailLineMesh)
        {
            TrajectoryTrailLineMesh->ClearAllMeshSections();
            TrajectoryTrailLineMesh->SetVisibility(false);
            TrajectoryTrailLineMesh->SetHiddenInGame(true);
        }
        return;
    }

    if (bShowLocalPlan)
    {
        UpdateSplineFromPoints(LocalPlanSpline, Playback->LocalPlanPointsUnreal);
    }
    else if (LocalPlanSpline)
    {
        LocalPlanSpline->ClearSplinePoints(true);
    }
    if (bShowTrajectoryTrail)
    {
        UpdateSplineFromPoints(TrajectoryTrailSpline, Playback->TrajectoryTrailUnreal);
    }
    else if (TrajectoryTrailSpline)
    {
        TrajectoryTrailSpline->ClearSplinePoints(true);
    }
    if (LocalPlanLineMesh)
    {
        LocalPlanLineMesh->ClearAllMeshSections();
        LocalPlanLineMesh->SetVisibility(false);
        LocalPlanLineMesh->SetHiddenInGame(true);
    }
    if (TrajectoryTrailLineMesh)
    {
        TrajectoryTrailLineMesh->ClearAllMeshSections();
        TrajectoryTrailLineMesh->SetVisibility(false);
        TrajectoryTrailLineMesh->SetHiddenInGame(true);
    }
    if (bShowLocalPlan)
    {
        DrawDebugLineStrip(Playback->LocalPlanPointsUnreal, LocalPlanColor, LocalPlanLineThicknessPixels);
    }
    if (bShowTrajectoryTrail)
    {
        DrawDebugLineStrip(Playback->TrajectoryTrailUnreal, TrajectoryTrailColor, TrajectoryTrailLineThicknessPixels);
    }

    if (ReferenceMarker)
    {
        ReferenceMarker->SetVisibility(bShowReferenceMarker);
        ReferenceMarker->SetHiddenInGame(!bShowReferenceMarker);
        if (bShowReferenceMarker)
        {
            ReferenceMarker->SetWorldLocation(Playback->ReferenceUnrealLocation);
            ReferenceMarker->SetWorldRotation(FRotator::ZeroRotator);
        }
    }

    if (RadarDirectionMarker)
    {
        RadarDirectionMarker->SetVisibility(bShowRadarSectorMesh);
        RadarDirectionMarker->SetHiddenInGame(!bShowRadarSectorMesh);
        if (bShowRadarSectorMesh)
        {
            const float Length = FMath::Max(Playback->RadarNearRadiusCentimeters, 50.0f);
            const float YawRadians = FMath::DegreesToRadians(Playback->RadarYawDegrees);
            const FVector Forward(FMath::Cos(YawRadians), FMath::Sin(YawRadians), 0.0f);
            RadarDirectionMarker->SetWorldLocation(Playback->LatestUnrealLocation + Forward * (0.5f * Length));
            RadarDirectionMarker->SetWorldRotation(FRotator(0.0f, Playback->RadarYawDegrees, 0.0f));
            RadarDirectionMarker->SetWorldScale3D(FVector(Length / 100.0f, 0.035f, 0.025f));
        }
    }

    UpdateRadarSectorMesh();
    UpdateLocalKnownMapMesh();
    UpdateLidarPointMesh();
}

void AQuadrotorMworksPlaybackActor::DrawDebugLineStrip(
    const TArray<FVector>& Points,
    const FLinearColor& Color,
    float ThicknessPixels) const
{
    UWorld* World = GetWorld();
    if (!World || Points.Num() < 2)
    {
        return;
    }

    const int32 Count = MaxSplinePoints > 0 ? FMath::Min(MaxSplinePoints, Points.Num()) : Points.Num();
    const int32 StartIndex = FMath::Max(0, Points.Num() - Count);
    const FColor DrawColor = Color.ToFColor(true);
    const float Thickness = FMath::Max(0.0f, ThicknessPixels);
    for (int32 Index = StartIndex; Index < Points.Num() - 1; ++Index)
    {
        const FVector A = Points[Index] + FVector(0.0f, 0.0f, TrajectoryLineHeightOffsetCentimeters);
        const FVector B = Points[Index + 1] + FVector(0.0f, 0.0f, TrajectoryLineHeightOffsetCentimeters);
        if (FVector::DistSquared(A, B) <= KINDA_SMALL_NUMBER)
        {
            continue;
        }
        DrawDebugLine(World, A, B, DrawColor, false, 0.0f, 0, Thickness);
    }
}

void AQuadrotorMworksPlaybackActor::UpdateLineStripMesh(
    UProceduralMeshComponent* Mesh,
    const TArray<FVector>& Points,
    const FLinearColor& Color,
    float WidthCentimeters) const
{
    if (!Mesh)
    {
        return;
    }

    if (Points.Num() < 2)
    {
        Mesh->ClearAllMeshSections();
        Mesh->SetVisibility(false);
        Mesh->SetHiddenInGame(true);
        return;
    }

    const int32 Count = MaxSplinePoints > 0 ? FMath::Min(MaxSplinePoints, Points.Num()) : Points.Num();
    const int32 StartIndex = FMath::Max(0, Points.Num() - Count);
    const float HalfWidth = FMath::Max(WidthCentimeters, 1.0f) * 0.5f;

    TArray<FVector> Vertices;
    TArray<int32> Triangles;
    TArray<FVector> Normals;
    TArray<FVector2D> UVs;
    TArray<FLinearColor> VertexColors;
    TArray<FProcMeshTangent> Tangents;

    Vertices.Reserve((Count - 1) * 4);
    Triangles.Reserve((Count - 1) * 6);
    Normals.Reserve((Count - 1) * 4);
    UVs.Reserve((Count - 1) * 4);
    VertexColors.Reserve((Count - 1) * 4);
    Tangents.Reserve((Count - 1) * 4);

    for (int32 Index = StartIndex; Index < Points.Num() - 1; ++Index)
    {
        const FVector A = Points[Index] + FVector(0.0f, 0.0f, TrajectoryLineHeightOffsetCentimeters);
        const FVector B = Points[Index + 1] + FVector(0.0f, 0.0f, TrajectoryLineHeightOffsetCentimeters);
        const FVector Segment = B - A;
        if (Segment.SizeSquared() < KINDA_SMALL_NUMBER)
        {
            continue;
        }

        FVector Side = FVector::CrossProduct(Segment.GetSafeNormal(), FVector::UpVector);
        if (Side.SizeSquared() < KINDA_SMALL_NUMBER)
        {
            Side = FVector::RightVector;
        }
        Side = Side.GetSafeNormal() * HalfWidth;

        const int32 BaseIndex = Vertices.Num();
        Vertices.Append({A - Side, A + Side, B + Side, B - Side});
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

    if (Vertices.Num() == 0)
    {
        Mesh->ClearAllMeshSections();
        Mesh->SetVisibility(false);
        Mesh->SetHiddenInGame(true);
        return;
    }

    Mesh->CreateMeshSection_LinearColor(0, Vertices, Triangles, Normals, UVs, VertexColors, Tangents, false);
    Mesh->SetVisibility(true);
    Mesh->SetHiddenInGame(false);
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
