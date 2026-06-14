#pragma once

#include "Components/ActorComponent.h"
#include "CoreMinimal.h"
#include "QuadrotorRotorAudioComponent.generated.h"

class UAudioComponent;
class UQuadrotorMworksPlaybackComponent;
class USoundBase;

UCLASS(ClassGroup = (Quadrotor), meta = (BlueprintSpawnableComponent))
class QUADROTORMWORKSBRIDGE_API UQuadrotorRotorAudioComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UQuadrotorRotorAudioComponent();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio")
    UQuadrotorMworksPlaybackComponent* Playback = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio")
    bool bAutoFindPlaybackOnOwner = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio")
    bool bEnableRotorAudio = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio")
    TSoftObjectPtr<USoundBase> RotorHoverLoopSound;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio")
    TSoftObjectPtr<USoundBase> RotorLoadLoopSound;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio")
    TSoftObjectPtr<USoundBase> RotorSpoolUpSound;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio")
    TSoftObjectPtr<USoundBase> RotorSpoolDownSound;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float MotorCommandScale = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float MinimumVolume = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float HoverVolume = 0.42f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float MaximumVolume = 0.86f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.1"))
    float MinimumPitch = 0.82f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.1"))
    float HoverPitch = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.1"))
    float MaximumPitch = 1.38f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float LoadPitchBoost = 0.22f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float LoadVolumeBoost = 0.22f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float LoadLayerMaximumVolume = 0.48f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.1"))
    float LoadLayerMinimumPitch = 0.95f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.1"))
    float LoadLayerMaximumPitch = 1.26f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float SpoolOneShotVolume = 0.76f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float RotorActiveThrottleThreshold = 0.10f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float TakeoffVerticalSpeedThreshold = 0.10f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float LandingVerticalSpeedThreshold = 0.12f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float SpoolTriggerCooldownSeconds = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.1"))
    float ResponseHz = 6.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float StaleFrameFadeSeconds = 1.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float TiltLoadGain = 1.25f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float HorizontalSpeedLoadGain = 0.08f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float VerticalSpeedLoadGain = 0.18f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float MotorSpreadLoadGain = 0.45f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Rotor Audio", meta = (ClampMin = "0.0"))
    float AttitudeRateLoadGain = 0.05f;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Rotor Audio")
    float CurrentThrottleCue = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Rotor Audio")
    float CurrentLoadCue = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Rotor Audio")
    float CurrentLoadLayerVolume = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Rotor Audio")
    float CurrentVolume = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Rotor Audio")
    float CurrentPitch = 1.0f;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Rotor Audio")
    void UpdateRotorAudio(float DeltaSeconds);

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void TickComponent(float DeltaTime, enum ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
    bool EnsurePlayback();
    bool EnsureLoopAudioComponent(
        UAudioComponent*& AudioComponent,
        FName ComponentName,
        const TSoftObjectPtr<USoundBase>& SoundReference,
        bool& bLoggedMissing);
    bool EnsureOneShotAudioComponent();
    bool HasUsableFrame() const;
    float ComputeThrottleCue() const;
    float ComputeMotorSpreadCue(float NormalizationScale) const;
    float ComputeLoadCue(float DeltaSeconds, float MotorSpreadCue);
    void UpdateSpoolOneShot(float TargetThrottle, float TargetLoad, double WorldSeconds);
    void PlaySpoolSound(const TSoftObjectPtr<USoundBase>& SoundReference);
    void StopRotorAudio();

    UPROPERTY(Transient)
    UAudioComponent* HoverAudio = nullptr;

    UPROPERTY(Transient)
    UAudioComponent* LoadAudio = nullptr;

    UPROPERTY(Transient)
    UAudioComponent* SpoolAudio = nullptr;

    bool bLoggedMissingHoverSound = false;
    bool bLoggedMissingLoadSound = false;
    bool bLoggedMissingSpoolSound = false;
    bool bHasPreviousFrame = false;
    bool bHasObservedFrameSignature = false;
    bool bWasRotorActive = false;
    bool bWasLikelyAirborne = false;
    int32 LastObservedSequence = TNumericLimits<int32>::Min();
    double LastObservedFrameTimeSeconds = -1.0;
    double LastObservedWorldTimeSeconds = -1.0;
    double LastSpoolTriggerWorldSeconds = -1000.0;
    float MaxObservedMotorCommand = 1.0f;
    float LastHorizontalSpeedMetersPerSecond = 0.0f;
    float LastVerticalSpeedMetersPerSecond = 0.0f;
    float LastVerticalSpeedAbsMetersPerSecond = 0.0f;
    float LastAttitudeRateRadiansPerSecond = 0.0f;
    FVector PreviousPositionMeters = FVector::ZeroVector;
    FVector PreviousRotationRadians = FVector::ZeroVector;
    double PreviousFrameTimeSeconds = -1.0;
};
