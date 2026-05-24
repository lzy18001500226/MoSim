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
    LatestUnrealLocation = MworksPositionToUnreal(Frame.PositionMeters);
    LatestUnrealRotation = MworksRotationToUnreal(Frame.RotationRadians);
    ReferenceUnrealLocation = MworksPositionToUnreal(Frame.ReferencePositionMeters);

    LocalPlanPointsUnreal.Reset(Frame.LocalPlanPointsMeters.Num());
    for (const FVector& PointMeters : Frame.LocalPlanPointsMeters)
    {
        LocalPlanPointsUnreal.Add(MworksPositionToUnreal(PointMeters));
    }

    RadarNearRadiusCentimeters = static_cast<float>(Frame.RadarNearRadiusMeters) * MetersToCentimeters;
    RadarFarRadiusCentimeters = static_cast<float>(Frame.RadarFarRadiusMeters) * MetersToCentimeters;
    RadarFovDegrees = static_cast<float>(Frame.RadarFovDegrees);
    const float YawSign = bConvertMworksYToUnrealNegativeY ? -1.0f : 1.0f;
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
