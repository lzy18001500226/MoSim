#include "QuadrotorRotorAudioComponent.h"

#include "Components/AudioComponent.h"
#include "GameFramework/Actor.h"
#include "QuadrotorMworksPlaybackComponent.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundWave.h"

UQuadrotorRotorAudioComponent::UQuadrotorRotorAudioComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    RotorHoverLoopSound = TSoftObjectPtr<USoundBase>(
        FSoftObjectPath(TEXT("/Game/Audio/MoSim/SunrayRotorHoverLoop.SunrayRotorHoverLoop")));
    RotorLoadLoopSound = TSoftObjectPtr<USoundBase>(
        FSoftObjectPath(TEXT("/Game/Audio/MoSim/SunrayRotorLoadLoop.SunrayRotorLoadLoop")));
    RotorSpoolUpSound = TSoftObjectPtr<USoundBase>(
        FSoftObjectPath(TEXT("/Game/Audio/MoSim/SunrayRotorSpoolUp.SunrayRotorSpoolUp")));
    RotorSpoolDownSound = TSoftObjectPtr<USoundBase>(
        FSoftObjectPath(TEXT("/Game/Audio/MoSim/SunrayRotorSpoolDown.SunrayRotorSpoolDown")));
}

void UQuadrotorRotorAudioComponent::BeginPlay()
{
    Super::BeginPlay();
    EnsurePlayback();
    EnsureLoopAudioComponent(HoverAudio, TEXT("MoSimRotorHoverAudioRuntime"), RotorHoverLoopSound, bLoggedMissingHoverSound);
    EnsureLoopAudioComponent(LoadAudio, TEXT("MoSimRotorLoadAudioRuntime"), RotorLoadLoopSound, bLoggedMissingLoadSound);
    EnsureOneShotAudioComponent();
}

void UQuadrotorRotorAudioComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopRotorAudio();
    Super::EndPlay(EndPlayReason);
}

void UQuadrotorRotorAudioComponent::TickComponent(
    float DeltaTime,
    enum ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    UpdateRotorAudio(DeltaTime);
}

bool UQuadrotorRotorAudioComponent::EnsurePlayback()
{
    if (Playback || !bAutoFindPlaybackOnOwner)
    {
        return Playback != nullptr;
    }

    if (AActor* Owner = GetOwner())
    {
        Playback = Owner->FindComponentByClass<UQuadrotorMworksPlaybackComponent>();
    }
    return Playback != nullptr;
}

bool UQuadrotorRotorAudioComponent::EnsureLoopAudioComponent(
    UAudioComponent*& AudioComponent,
    FName ComponentName,
    const TSoftObjectPtr<USoundBase>& SoundReference,
    bool& bLoggedMissing)
{
    AActor* Owner = GetOwner();
    if (!Owner)
    {
        return false;
    }

    if (!AudioComponent)
    {
        AudioComponent = NewObject<UAudioComponent>(Owner, ComponentName);
        if (!AudioComponent)
        {
            return false;
        }
        AudioComponent->bAutoActivate = false;
        AudioComponent->bAllowSpatialization = false;
        AudioComponent->bStopWhenOwnerDestroyed = true;
        AudioComponent->RegisterComponent();
        if (USceneComponent* Root = Owner->GetRootComponent())
        {
            AudioComponent->AttachToComponent(Root, FAttachmentTransformRules::KeepRelativeTransform);
        }
    }

    if (!AudioComponent->Sound)
    {
        USoundBase* Sound = SoundReference.LoadSynchronous();
        if (!Sound)
        {
            if (!bLoggedMissing)
            {
                bLoggedMissing = true;
                UE_LOG(
                    LogTemp,
                    Warning,
                    TEXT("MoSim rotor audio missing loop asset: %s"),
                    *SoundReference.ToSoftObjectPath().ToString());
            }
            return false;
        }
        if (USoundWave* SoundWave = Cast<USoundWave>(Sound))
        {
            SoundWave->bLooping = true;
        }
        AudioComponent->SetSound(Sound);
    }

    return AudioComponent != nullptr && AudioComponent->Sound != nullptr;
}

bool UQuadrotorRotorAudioComponent::EnsureOneShotAudioComponent()
{
    AActor* Owner = GetOwner();
    if (!Owner)
    {
        return false;
    }

    if (!SpoolAudio)
    {
        SpoolAudio = NewObject<UAudioComponent>(Owner, TEXT("MoSimRotorSpoolAudioRuntime"));
        if (!SpoolAudio)
        {
            return false;
        }
        SpoolAudio->bAutoActivate = false;
        SpoolAudio->bAllowSpatialization = false;
        SpoolAudio->bStopWhenOwnerDestroyed = true;
        SpoolAudio->RegisterComponent();
        if (USceneComponent* Root = Owner->GetRootComponent())
        {
            SpoolAudio->AttachToComponent(Root, FAttachmentTransformRules::KeepRelativeTransform);
        }
    }
    return SpoolAudio != nullptr;
}

bool UQuadrotorRotorAudioComponent::HasUsableFrame() const
{
    if (!Playback)
    {
        return false;
    }

    const FQuadrotorMworksFrame& Frame = Playback->LatestFrame;
    return Frame.bIsValid
        || Frame.MotorCommand.Num() > 0
        || Frame.Sequence != 0
        || Frame.TimeSeconds > 0.0
        || !Frame.PositionMeters.IsNearlyZero()
        || !Frame.RotationRadians.IsNearlyZero();
}

float UQuadrotorRotorAudioComponent::ComputeThrottleCue() const
{
    if (!Playback || Playback->LatestFrame.MotorCommand.Num() == 0)
    {
        return 0.0f;
    }

    const TArray<double>& MotorCommand = Playback->LatestFrame.MotorCommand;
    double Sum = 0.0;
    double MaxAbs = 0.0;
    for (double Command : MotorCommand)
    {
        const double AbsCommand = FMath::Abs(Command);
        Sum += AbsCommand;
        MaxAbs = FMath::Max(MaxAbs, AbsCommand);
    }

    const float MeanCommand = static_cast<float>(Sum / FMath::Max(1, MotorCommand.Num()));
    const float Scale = MotorCommandScale > 0.0f
        ? MotorCommandScale
        : (MaxAbs <= 1.25 ? 1.0f : FMath::Max(MaxObservedMotorCommand, 1.0f));
    return FMath::Clamp(MeanCommand / FMath::Max(Scale, KINDA_SMALL_NUMBER), 0.0f, 1.0f);
}

float UQuadrotorRotorAudioComponent::ComputeMotorSpreadCue(float NormalizationScale) const
{
    if (!Playback || Playback->LatestFrame.MotorCommand.Num() < 2)
    {
        return 0.0f;
    }

    double MinCommand = TNumericLimits<double>::Max();
    double MaxCommand = TNumericLimits<double>::Lowest();
    for (double Command : Playback->LatestFrame.MotorCommand)
    {
        const double AbsCommand = FMath::Abs(Command);
        MinCommand = FMath::Min(MinCommand, AbsCommand);
        MaxCommand = FMath::Max(MaxCommand, AbsCommand);
    }

    return FMath::Clamp(
        static_cast<float>(MaxCommand - MinCommand) / FMath::Max(NormalizationScale, KINDA_SMALL_NUMBER),
        0.0f,
        1.0f);
}

float UQuadrotorRotorAudioComponent::ComputeLoadCue(float DeltaSeconds, float MotorSpreadCue)
{
    if (!Playback)
    {
        return 0.0f;
    }

    const FQuadrotorMworksFrame& Frame = Playback->LatestFrame;
    const float TiltRadians = FMath::Sqrt(
        FMath::Square(static_cast<float>(Frame.RotationRadians.X))
        + FMath::Square(static_cast<float>(Frame.RotationRadians.Y)));

    float HorizontalSpeed = 0.0f;
    float VerticalSpeed = 0.0f;
    float AttitudeRate = 0.0f;
    if (bHasPreviousFrame)
    {
        float Dt = DeltaSeconds;
        if (Frame.TimeSeconds > PreviousFrameTimeSeconds)
        {
            Dt = static_cast<float>(Frame.TimeSeconds - PreviousFrameTimeSeconds);
        }
        Dt = FMath::Max(Dt, 1.0e-3f);

        const FVector VelocityMetersPerSecond = (Frame.PositionMeters - PreviousPositionMeters) / Dt;
        HorizontalSpeed = FVector(VelocityMetersPerSecond.X, VelocityMetersPerSecond.Y, 0.0f).Size();
        LastVerticalSpeedMetersPerSecond = VelocityMetersPerSecond.Z;
        VerticalSpeed = FMath::Abs(LastVerticalSpeedMetersPerSecond);

        const float RollRate = FMath::Abs(FMath::FindDeltaAngleRadians(
            static_cast<float>(PreviousRotationRadians.X),
            static_cast<float>(Frame.RotationRadians.X))) / Dt;
        const float PitchRate = FMath::Abs(FMath::FindDeltaAngleRadians(
            static_cast<float>(PreviousRotationRadians.Y),
            static_cast<float>(Frame.RotationRadians.Y))) / Dt;
        const float YawRate = FMath::Abs(FMath::FindDeltaAngleRadians(
            static_cast<float>(PreviousRotationRadians.Z),
            static_cast<float>(Frame.RotationRadians.Z))) / Dt;
        AttitudeRate = FMath::Max3(RollRate, PitchRate, YawRate);
    }
    else
    {
        LastVerticalSpeedMetersPerSecond = 0.0f;
    }

    LastHorizontalSpeedMetersPerSecond = HorizontalSpeed;
    LastVerticalSpeedAbsMetersPerSecond = VerticalSpeed;
    LastAttitudeRateRadiansPerSecond = AttitudeRate;

    PreviousPositionMeters = Frame.PositionMeters;
    PreviousRotationRadians = Frame.RotationRadians;
    PreviousFrameTimeSeconds = Frame.TimeSeconds;
    bHasPreviousFrame = true;

    return FMath::Clamp(
        TiltRadians * TiltLoadGain
        + HorizontalSpeed * HorizontalSpeedLoadGain
        + VerticalSpeed * VerticalSpeedLoadGain
        + MotorSpreadCue * MotorSpreadLoadGain
        + AttitudeRate * AttitudeRateLoadGain,
        0.0f,
        1.0f);
}

void UQuadrotorRotorAudioComponent::StopRotorAudio()
{
    if (HoverAudio && HoverAudio->IsPlaying())
    {
        HoverAudio->Stop();
    }
    if (LoadAudio && LoadAudio->IsPlaying())
    {
        LoadAudio->Stop();
    }
    if (SpoolAudio && SpoolAudio->IsPlaying())
    {
        SpoolAudio->Stop();
    }
}

void UQuadrotorRotorAudioComponent::PlaySpoolSound(const TSoftObjectPtr<USoundBase>& SoundReference)
{
    if (!EnsureOneShotAudioComponent())
    {
        return;
    }

    USoundBase* Sound = SoundReference.LoadSynchronous();
    if (!Sound)
    {
        if (!bLoggedMissingSpoolSound)
        {
            bLoggedMissingSpoolSound = true;
            UE_LOG(
                LogTemp,
                Warning,
                TEXT("MoSim rotor audio missing spool asset: %s"),
                *SoundReference.ToSoftObjectPath().ToString());
        }
        return;
    }

    SpoolAudio->SetSound(Sound);
    SpoolAudio->SetVolumeMultiplier(SpoolOneShotVolume);
    SpoolAudio->SetPitchMultiplier(1.0f);
    SpoolAudio->Play(0.0f);
}

void UQuadrotorRotorAudioComponent::UpdateSpoolOneShot(float TargetThrottle, float TargetLoad, double WorldSeconds)
{
    if (WorldSeconds - LastSpoolTriggerWorldSeconds < SpoolTriggerCooldownSeconds)
    {
        bWasRotorActive = TargetThrottle > RotorActiveThrottleThreshold;
        bWasLikelyAirborne = TargetThrottle > RotorActiveThrottleThreshold
            || FMath::Abs(LastVerticalSpeedMetersPerSecond) > LandingVerticalSpeedThreshold
            || LastHorizontalSpeedMetersPerSecond > 0.25f;
        return;
    }

    const bool bRotorActive = TargetThrottle > RotorActiveThrottleThreshold || TargetLoad > 0.18f;
    const bool bTakeoffMotion = LastVerticalSpeedMetersPerSecond > TakeoffVerticalSpeedThreshold;
    const bool bLandingMotion = LastVerticalSpeedMetersPerSecond < -LandingVerticalSpeedThreshold;
    const bool bLikelyAirborne = bRotorActive
        || FMath::Abs(LastVerticalSpeedMetersPerSecond) > LandingVerticalSpeedThreshold
        || LastHorizontalSpeedMetersPerSecond > 0.25f;

    if (!bWasRotorActive && bRotorActive)
    {
        PlaySpoolSound(RotorSpoolUpSound);
        LastSpoolTriggerWorldSeconds = WorldSeconds;
    }
    else if (!bWasLikelyAirborne && bTakeoffMotion)
    {
        PlaySpoolSound(RotorSpoolUpSound);
        LastSpoolTriggerWorldSeconds = WorldSeconds;
    }
    else if (bWasLikelyAirborne && (bLandingMotion || !bRotorActive))
    {
        PlaySpoolSound(RotorSpoolDownSound);
        LastSpoolTriggerWorldSeconds = WorldSeconds;
    }

    bWasRotorActive = bRotorActive;
    bWasLikelyAirborne = bLikelyAirborne;
}

void UQuadrotorRotorAudioComponent::UpdateRotorAudio(float DeltaSeconds)
{
    DeltaSeconds = FMath::Max(DeltaSeconds, 0.0f);
    EnsurePlayback();

    const bool bHoverReady = EnsureLoopAudioComponent(
        HoverAudio,
        TEXT("MoSimRotorHoverAudioRuntime"),
        RotorHoverLoopSound,
        bLoggedMissingHoverSound);
    const bool bLoadReady = EnsureLoopAudioComponent(
        LoadAudio,
        TEXT("MoSimRotorLoadAudioRuntime"),
        RotorLoadLoopSound,
        bLoggedMissingLoadSound);
    EnsureOneShotAudioComponent();

    if (!bEnableRotorAudio || !bHoverReady)
    {
        StopRotorAudio();
        return;
    }

    const bool bFrameUsable = HasUsableFrame();
    const double WorldSeconds = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
    if (bFrameUsable && Playback)
    {
        const FQuadrotorMworksFrame& Frame = Playback->LatestFrame;
        bool bNewFrameSignature = !bHasObservedFrameSignature
            || LastObservedSequence != Frame.Sequence
            || !FMath::IsNearlyEqual(LastObservedFrameTimeSeconds, Frame.TimeSeconds, 1.0e-6);
        if (bNewFrameSignature)
        {
            bHasObservedFrameSignature = true;
            LastObservedSequence = Frame.Sequence;
            LastObservedFrameTimeSeconds = Frame.TimeSeconds;
            LastObservedWorldTimeSeconds = WorldSeconds;

            for (double Command : Frame.MotorCommand)
            {
                MaxObservedMotorCommand = FMath::Max(MaxObservedMotorCommand, static_cast<float>(FMath::Abs(Command)));
            }
        }
    }

    float TargetThrottle = 0.0f;
    float TargetLoad = 0.0f;
    float TargetVolume = 0.0f;
    float TargetPitch = HoverPitch;
    float TargetLoadLayerVolume = 0.0f;
    float TargetLoadLayerPitch = LoadLayerMinimumPitch;

    const bool bFrameFresh = bFrameUsable
        && (!bHasObservedFrameSignature
            || StaleFrameFadeSeconds <= 0.0f
            || LastObservedWorldTimeSeconds < 0.0
            || WorldSeconds - LastObservedWorldTimeSeconds <= StaleFrameFadeSeconds);
    if (bFrameFresh)
    {
        const float NormalizationScale = MotorCommandScale > 0.0f
            ? MotorCommandScale
            : FMath::Max(MaxObservedMotorCommand, 1.0f);
        TargetThrottle = ComputeThrottleCue();
        const float MotorSpreadCue = ComputeMotorSpreadCue(NormalizationScale);
        TargetLoad = ComputeLoadCue(DeltaSeconds, MotorSpreadCue);
        if (TargetThrottle <= KINDA_SMALL_NUMBER && TargetLoad > 0.0f)
        {
            TargetThrottle = FMath::Clamp(0.25f + TargetLoad * 0.45f, 0.0f, 1.0f);
        }

        TargetVolume = FMath::Clamp(
            FMath::Lerp(MinimumVolume, HoverVolume, TargetThrottle) + TargetLoad * LoadVolumeBoost,
            MinimumVolume,
            MaximumVolume);
        TargetPitch = FMath::Clamp(
            FMath::Lerp(MinimumPitch, HoverPitch, TargetThrottle) + TargetLoad * LoadPitchBoost,
            MinimumPitch,
            MaximumPitch);
        TargetLoadLayerVolume = FMath::Clamp(TargetLoad * LoadLayerMaximumVolume, 0.0f, LoadLayerMaximumVolume);
        TargetLoadLayerPitch = FMath::Clamp(
            FMath::Lerp(LoadLayerMinimumPitch, LoadLayerMaximumPitch, TargetLoad),
            LoadLayerMinimumPitch,
            LoadLayerMaximumPitch);
        UpdateSpoolOneShot(TargetThrottle, TargetLoad, WorldSeconds);
    }

    const float Alpha = ResponseHz <= 0.0f ? 1.0f : 1.0f - FMath::Exp(-ResponseHz * DeltaSeconds);
    CurrentThrottleCue = FMath::Lerp(CurrentThrottleCue, TargetThrottle, Alpha);
    CurrentLoadCue = FMath::Lerp(CurrentLoadCue, TargetLoad, Alpha);
    CurrentLoadLayerVolume = FMath::Lerp(CurrentLoadLayerVolume, TargetLoadLayerVolume, Alpha);
    CurrentVolume = FMath::Lerp(CurrentVolume, TargetVolume, Alpha);
    CurrentPitch = FMath::Lerp(CurrentPitch, TargetPitch, Alpha);

    HoverAudio->SetVolumeMultiplier(CurrentVolume);
    HoverAudio->SetPitchMultiplier(CurrentPitch);
    if (CurrentVolume > 0.01f)
    {
        if (!HoverAudio->IsPlaying())
        {
            HoverAudio->Play();
        }
    }
    else if (HoverAudio->IsPlaying())
    {
        HoverAudio->FadeOut(0.15f, 0.0f);
    }

    if (bLoadReady && LoadAudio)
    {
        LoadAudio->SetVolumeMultiplier(CurrentLoadLayerVolume);
        LoadAudio->SetPitchMultiplier(TargetLoadLayerPitch);
        if (CurrentLoadLayerVolume > 0.01f)
        {
            if (!LoadAudio->IsPlaying())
            {
                LoadAudio->Play();
            }
        }
        else if (LoadAudio->IsPlaying())
        {
            LoadAudio->FadeOut(0.15f, 0.0f);
        }
    }
}
