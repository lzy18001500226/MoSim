#include "QuadrotorMworksPlaybackComponent.h"

#include "GameFramework/Actor.h"
#include "QuadrotorMworksUdpReceiverComponent.h"

UQuadrotorMworksPlaybackComponent::UQuadrotorMworksPlaybackComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PropellerAnglesDegrees.Init(0.0f, 4);
}

void UQuadrotorMworksPlaybackComponent::BeginPlay()
{
    Super::BeginPlay();

    if (!Receiver && bAutoFindReceiverOnOwner)
    {
        if (AActor* Owner = GetOwner())
        {
            Receiver = Owner->FindComponentByClass<UQuadrotorMworksUdpReceiverComponent>();
        }
    }
}

void UQuadrotorMworksPlaybackComponent::TickComponent(
    float DeltaTime,
    enum ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (Receiver && Receiver->HasFrame())
    {
        ApplyFrame(Receiver->GetLatestFrame(), DeltaTime);
    }
}

FVector UQuadrotorMworksPlaybackComponent::MworksPositionToUnreal(const FVector& PositionMeters) const
{
    const float X = static_cast<float>(PositionMeters.X) * MetersToCentimeters;
    const float YSign = bConvertMworksYToUnrealNegativeY ? -1.0f : 1.0f;
    const float Y = YSign * static_cast<float>(PositionMeters.Y) * MetersToCentimeters;
    const float Z = static_cast<float>(PositionMeters.Z) * MetersToCentimeters;
    return FVector(X, Y, Z);
}

namespace
{
bool UsesUnrealWorldMeters(const FQuadrotorMworksFrame& Frame)
{
    return Frame.CoordinatePolicy.Equals(TEXT("ue_world_m_z_up"), ESearchCase::IgnoreCase);
}
}

FRotator UQuadrotorMworksPlaybackComponent::MworksRotationToUnreal(const FVector& RollPitchYawRadians) const
{
    const float RollDeg = FMath::RadiansToDegrees(static_cast<float>(RollPitchYawRadians.X));
    const float PitchDeg = FMath::RadiansToDegrees(static_cast<float>(RollPitchYawRadians.Y));
    const float YawSign = bConvertMworksYToUnrealNegativeY ? -1.0f : 1.0f;
    const float YawDeg = YawSign * FMath::RadiansToDegrees(static_cast<float>(RollPitchYawRadians.Z));
    return FRotator(PitchDeg, YawDeg, RollDeg);
}

void UQuadrotorMworksPlaybackComponent::ResetTrail()
{
    TrajectoryTrailUnreal.Reset();
}

void UQuadrotorMworksPlaybackComponent::ApplyFrame(const FQuadrotorMworksFrame& Frame, float DeltaSeconds)
{
    LatestFrame = Frame;
    const bool bUseUnrealWorldMeters = UsesUnrealWorldMeters(Frame);
    const auto ToUnrealPosition = [this, bUseUnrealWorldMeters](const FVector& PositionMeters)
    {
        if (bUseUnrealWorldMeters)
        {
            return FVector(
                static_cast<float>(PositionMeters.X) * MetersToCentimeters,
                static_cast<float>(PositionMeters.Y) * MetersToCentimeters,
                static_cast<float>(PositionMeters.Z) * MetersToCentimeters);
        }
        return MworksPositionToUnreal(PositionMeters);
    };

    LatestUnrealLocation = ToUnrealPosition(Frame.PositionMeters);
    LatestUnrealRotation = bUseUnrealWorldMeters
        ? FRotator(
            FMath::RadiansToDegrees(static_cast<float>(Frame.RotationRadians.Y)),
            FMath::RadiansToDegrees(static_cast<float>(Frame.RotationRadians.Z)),
            FMath::RadiansToDegrees(static_cast<float>(Frame.RotationRadians.X)))
        : MworksRotationToUnreal(Frame.RotationRadians);
    ReferenceUnrealLocation = ToUnrealPosition(Frame.ReferencePositionMeters);

    LocalPlanPointsUnreal.Reset(Frame.LocalPlanPointsMeters.Num());
    for (const FVector& PointMeters : Frame.LocalPlanPointsMeters)
    {
        LocalPlanPointsUnreal.Add(ToUnrealPosition(PointMeters));
    }

    LocalKnownFreeCellsUnreal.Reset();
    LocalKnownOccupiedCellsUnreal.Reset();
    const FVector LocalMapOriginUnreal = ToUnrealPosition(Frame.LocalKnownMap.OriginMeters);
    const float LocalMapGridCentimeters = static_cast<float>(Frame.LocalKnownMap.GridMeters) * MetersToCentimeters;
    for (const FQuadrotorMworksLocalKnownMapCell& Cell : Frame.LocalKnownMap.Cells)
    {
        const FVector CellLocationUnreal = LocalMapOriginUnreal + FVector(
            static_cast<float>(Cell.Offset.X) * LocalMapGridCentimeters,
            static_cast<float>(Cell.Offset.Y) * LocalMapGridCentimeters,
            static_cast<float>(Cell.Offset.Z) * LocalMapGridCentimeters);
        if (Cell.State.Contains(TEXT("occupied"), ESearchCase::IgnoreCase))
        {
            LocalKnownOccupiedCellsUnreal.Add(CellLocationUnreal);
        }
        else
        {
            LocalKnownFreeCellsUnreal.Add(CellLocationUnreal);
        }
    }

    LidarPointsUnreal.Reset(Frame.LidarPoints.PointsMeters.Num());
    const bool bLidarUsesUnrealWorldMeters = Frame.LidarPoints.CoordinateFrame.Equals(TEXT("ue_world_m_z_up"), ESearchCase::IgnoreCase);
    for (const FVector& PointMeters : Frame.LidarPoints.PointsMeters)
    {
        LidarPointsUnreal.Add(bLidarUsesUnrealWorldMeters ? FVector(
            static_cast<float>(PointMeters.X) * MetersToCentimeters,
            static_cast<float>(PointMeters.Y) * MetersToCentimeters,
            static_cast<float>(PointMeters.Z) * MetersToCentimeters) : ToUnrealPosition(PointMeters));
    }

    RadarNearRadiusCentimeters = static_cast<float>(Frame.RadarNearRadiusMeters) * MetersToCentimeters;
    RadarFarRadiusCentimeters = static_cast<float>(Frame.RadarFarRadiusMeters) * MetersToCentimeters;
    RadarFovDegrees = static_cast<float>(Frame.RadarFovDegrees);
    const float YawSign = bUseUnrealWorldMeters ? 1.0f : (bConvertMworksYToUnrealNegativeY ? -1.0f : 1.0f);
    RadarYawDegrees = YawSign * FMath::RadiansToDegrees(static_cast<float>(Frame.RadarYawRadians));

    const float TrailMinDistanceCentimeters = TrailMinDistanceMeters * MetersToCentimeters;
    if (TrajectoryTrailUnreal.Num() == 0
        || FVector::DistSquared(TrajectoryTrailUnreal.Last(), LatestUnrealLocation)
            >= TrailMinDistanceCentimeters * TrailMinDistanceCentimeters)
    {
        TrajectoryTrailUnreal.Add(LatestUnrealLocation);
        while (MaxTrailPoints > 0 && TrajectoryTrailUnreal.Num() > MaxTrailPoints)
        {
            TrajectoryTrailUnreal.RemoveAt(0, 1, EAllowShrinking::No);
        }
    }

    if (PropellerAnglesDegrees.Num() != 4)
    {
        PropellerAnglesDegrees.Init(0.0f, 4);
    }

    for (int32 Index = 0; Index < PropellerAnglesDegrees.Num() && Index < Frame.MotorCommand.Num(); ++Index)
    {
        const float Direction = (Index % 2 == 0) ? 1.0f : -1.0f;
        const float Command = static_cast<float>(Frame.MotorCommand[Index]);
        PropellerAnglesDegrees[Index] = FMath::Fmod(
            PropellerAnglesDegrees[Index] + Direction * Command * PropellerVisualScale * DeltaSeconds,
            360.0f);
    }

    if (bApplyActorTransform)
    {
        if (AActor* Owner = GetOwner())
        {
            Owner->SetActorLocationAndRotation(LatestUnrealLocation, LatestUnrealRotation);
        }
    }
}
