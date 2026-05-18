#pragma once

#include "Components/ActorComponent.h"
#include "CoreMinimal.h"
#include "QuadrotorMworksTypes.h"
#include "QuadrotorMworksPlaybackComponent.generated.h"

class UQuadrotorMworksUdpReceiverComponent;

UCLASS(ClassGroup = (Quadrotor), meta = (BlueprintSpawnableComponent))
class QUADROTORMWORKSBRIDGE_API UQuadrotorMworksPlaybackComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UQuadrotorMworksPlaybackComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Playback")
    UQuadrotorMworksUdpReceiverComponent* Receiver = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Playback")
    float MetersToCentimeters = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Playback")
    bool bAutoFindReceiverOnOwner = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Playback")
    bool bApplyActorTransform = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Playback")
    bool bConvertMworksYToUnrealNegativeY = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Playback")
    float PropellerVisualScale = 32.0f;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Playback")
    FQuadrotorMworksFrame LatestFrame;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Playback")
    FVector LatestUnrealLocation = FVector::ZeroVector;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Playback")
    FRotator LatestUnrealRotation = FRotator::ZeroRotator;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Playback")
    TArray<float> PropellerAnglesDegrees;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Playback")
    void ApplyFrame(const FQuadrotorMworksFrame& Frame, float DeltaSeconds);

    UFUNCTION(BlueprintCallable, Category = "MWORKS Playback")
    FVector MworksPositionToUnreal(const FVector& PositionMeters) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Playback")
    FRotator MworksRotationToUnreal(const FVector& RollPitchYawRadians) const;

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, enum ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
};
