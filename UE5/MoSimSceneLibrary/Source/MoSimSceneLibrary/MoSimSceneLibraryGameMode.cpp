#include "MoSimSceneLibraryGameMode.h"

#include "Components/LightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/SkyLight.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "MworksReviewCameraPawn.h"
#include "QuadrotorMworksMapActor.h"
#include "QuadrotorMworksPlaybackActor.h"

AMoSimSceneLibraryGameMode::AMoSimSceneLibraryGameMode()
{
    PrimaryActorTick.bCanEverTick = true;
    DefaultPawnClass = AMworksReviewCameraPawn::StaticClass();
}

void AMoSimSceneLibraryGameMode::BeginPlay()
{
    Super::BeginPlay();

    const bool bSceneReviewOnly = FParse::Param(FCommandLine::Get(), TEXT("MoSimSceneReview"));
    const bool bSimulationReview = FParse::Param(FCommandLine::Get(), TEXT("MoSimSimulationReview"));
    bSceneReviewModeActive = bSceneReviewOnly || bSimulationReview;
    const bool bDisablePreviewMap =
        bSceneReviewOnly || bSimulationReview || FParse::Param(FCommandLine::Get(), TEXT("MoSimNoPreviewMap"));
    const bool bDisablePlayback =
        bSceneReviewOnly || FParse::Param(FCommandLine::Get(), TEXT("MoSimNoPlayback"));

    if (!bSpawnDefaultRendererActors)
    {
        UE_LOG(LogTemp, Display, TEXT("MWORKS renderer auto-spawn disabled."));
        return;
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        UE_LOG(LogTemp, Error, TEXT("MWORKS renderer GameMode has no valid world."));
        return;
    }

    FActorSpawnParameters SpawnParameters;
    SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    if (bSpawnDefaultReviewLighting)
    {
        if (FParse::Param(FCommandLine::Get(), TEXT("MoSimDayReview")))
        {
            bForceDaylightReviewExposure = !FParse::Param(FCommandLine::Get(), TEXT("MoSimNoDayReviewExposure"));
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewSunIntensity="), ReviewSunIntensity);
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewSkyLightIntensity="), ReviewSkyLightIntensity);
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewExposureBias="), ReviewExposureBias);
        }
        else
        {
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewSunIntensity="), ReviewSunIntensity);
            FParse::Value(FCommandLine::Get(), TEXT("MoSimReviewSkyLightIntensity="), ReviewSkyLightIntensity);
        }
        SpawnDefaultReviewLighting(World, SpawnParameters);
    }

    if (bSceneReviewModeActive)
    {
        EnforceSceneReviewCamera(World);
    }

    if (bDisablePreviewMap)
    {
        UE_LOG(LogTemp, Display, TEXT("MWORKS preview map auto-spawn disabled by command line."));
    }
    else if (DefaultRenderMapJson.IsEmpty())
    {
        UE_LOG(LogTemp, Display, TEXT("MWORKS preview map auto-spawn skipped because DefaultRenderMapJson is empty."));
    }
    else
    {
        SpawnedMapActor = World->SpawnActor<AQuadrotorMworksMapActor>(
            AQuadrotorMworksMapActor::StaticClass(),
            MapActorLocation,
            FRotator::ZeroRotator,
            SpawnParameters);

        if (SpawnedMapActor)
        {
            SpawnedMapActor->SetActorLabel(TEXT("MWORKS_Render_Map"));
            SpawnedMapActor->RenderMapJson = DefaultRenderMapJson;
            SpawnedMapActor->LoadRenderMapSummary();
            UE_LOG(LogTemp, Display, TEXT("MWORKS renderer spawned map actor with map json: %s"), *DefaultRenderMapJson);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("MWORKS renderer failed to spawn map actor."));
        }
    }

    if (bDisablePlayback)
    {
        UE_LOG(LogTemp, Display, TEXT("MWORKS playback actor auto-spawn disabled by command line."));
    }
    else
    {
        SpawnedPlaybackActor = World->SpawnActor<AQuadrotorMworksPlaybackActor>(
            AQuadrotorMworksPlaybackActor::StaticClass(),
            PlaybackActorLocation,
            FRotator::ZeroRotator,
            SpawnParameters);

        if (SpawnedPlaybackActor)
        {
            SpawnedPlaybackActor->SetActorLabel(TEXT("MWORKS_Quadrotor_Playback"));
            SpawnedPlaybackActor->MapActor = SpawnedMapActor;
            UE_LOG(LogTemp, Display, TEXT("MWORKS renderer spawned playback actor and linked map actor."));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("MWORKS renderer failed to spawn playback actor."));
        }
    }
}

void AMoSimSceneLibraryGameMode::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (bSceneReviewModeActive)
    {
        EnforceSceneReviewCamera(GetWorld());
    }
}

void AMoSimSceneLibraryGameMode::SpawnDefaultReviewLighting(UWorld* World, const FActorSpawnParameters& SpawnParameters)
{
    if (!World)
    {
        return;
    }

    SpawnedReviewSunLight = World->SpawnActor<ADirectionalLight>(
        ADirectionalLight::StaticClass(),
        FVector(0.0f, 0.0f, 3000.0f),
        ReviewSunRotation,
        SpawnParameters);

    if (SpawnedReviewSunLight)
    {
        SpawnedReviewSunLight->SetActorLabel(TEXT("MWORKS_Review_SunLight"));
        if (ULightComponent* LightComponent = SpawnedReviewSunLight->GetLightComponent())
        {
            LightComponent->SetMobility(EComponentMobility::Movable);
            LightComponent->SetIntensity(ReviewSunIntensity);
            LightComponent->SetLightColor(FLinearColor(1.0f, 0.96f, 0.86f));
            LightComponent->SetCastShadows(false);
        }
    }

    SpawnedReviewSkyLight = World->SpawnActor<ASkyLight>(
        ASkyLight::StaticClass(),
        FVector(0.0f, 0.0f, 1000.0f),
        FRotator::ZeroRotator,
        SpawnParameters);

    if (SpawnedReviewSkyLight)
    {
        SpawnedReviewSkyLight->SetActorLabel(TEXT("MWORKS_Review_SkyLight"));
        if (USkyLightComponent* SkyComponent = SpawnedReviewSkyLight->GetLightComponent())
        {
            SkyComponent->SetMobility(EComponentMobility::Movable);
            SkyComponent->SetIntensity(ReviewSkyLightIntensity);
            SkyComponent->RecaptureSky();
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("MWORKS renderer spawned default review lighting: sun=%s sky=%s"),
        SpawnedReviewSunLight ? TEXT("true") : TEXT("false"),
        SpawnedReviewSkyLight ? TEXT("true") : TEXT("false"));

    if (bForceDaylightReviewExposure)
    {
        SpawnedReviewPostProcessVolume = World->SpawnActor<APostProcessVolume>(
            APostProcessVolume::StaticClass(),
            FVector::ZeroVector,
            FRotator::ZeroRotator,
            SpawnParameters);

        if (SpawnedReviewPostProcessVolume)
        {
            SpawnedReviewPostProcessVolume->SetActorLabel(TEXT("MWORKS_Review_Daylight_PostProcess"));
            SpawnedReviewPostProcessVolume->bUnbound = true;
            SpawnedReviewPostProcessVolume->BlendWeight = 1.0f;
            SpawnedReviewPostProcessVolume->Priority = 10000.0f;
            FPostProcessSettings& Settings = SpawnedReviewPostProcessVolume->Settings;
            Settings.bOverride_AutoExposureMinBrightness = true;
            Settings.bOverride_AutoExposureMaxBrightness = true;
            Settings.bOverride_AutoExposureBias = true;
            Settings.AutoExposureMinBrightness = 2.0f;
            Settings.AutoExposureMaxBrightness = 2.0f;
            Settings.AutoExposureBias = ReviewExposureBias;
            Settings.bOverride_MotionBlurAmount = true;
            Settings.MotionBlurAmount = 0.0f;

            UE_LOG(
                LogTemp,
                Display,
                TEXT("MWORKS renderer forced daylight review exposure: bias=%.2f"),
                ReviewExposureBias);
        }
    }
}

AMworksReviewCameraPawn* AMoSimSceneLibraryGameMode::FindOrSpawnReviewCamera(
    UWorld* World,
    const FActorSpawnParameters& SpawnParameters)
{
    if (!World)
    {
        return nullptr;
    }

    if (IsValid(ActiveReviewCameraPawn))
    {
        return ActiveReviewCameraPawn;
    }

    TArray<AActor*> ExistingReviewPawns;
    UGameplayStatics::GetAllActorsOfClass(World, AMworksReviewCameraPawn::StaticClass(), ExistingReviewPawns);
    for (AActor* Actor : ExistingReviewPawns)
    {
        if (AMworksReviewCameraPawn* ReviewPawn = Cast<AMworksReviewCameraPawn>(Actor))
        {
            ActiveReviewCameraPawn = ReviewPawn;
            return ActiveReviewCameraPawn;
        }
    }

    ActiveReviewCameraPawn = World->SpawnActor<AMworksReviewCameraPawn>(
        AMworksReviewCameraPawn::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        SpawnParameters);

    if (ActiveReviewCameraPawn)
    {
        ActiveReviewCameraPawn->SetActorLabel(TEXT("MWORKS_Review_Camera"));
        UE_LOG(LogTemp, Display, TEXT("MWORKS scene-review spawned missing review camera pawn."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("MWORKS scene-review failed to spawn review camera pawn."));
    }

    return ActiveReviewCameraPawn;
}

void AMoSimSceneLibraryGameMode::DisableImportedPawnInput(APawn* Pawn, APlayerController* PlayerController) const
{
    if (!Pawn || Pawn == ActiveReviewCameraPawn)
    {
        return;
    }

    Pawn->AutoPossessPlayer = EAutoReceiveInput::Disabled;
    Pawn->AutoReceiveInput = EAutoReceiveInput::Disabled;
    if (PlayerController && Pawn->GetController() == PlayerController)
    {
        Pawn->DisableInput(PlayerController);
    }
}

void AMoSimSceneLibraryGameMode::EnforceSceneReviewCamera(UWorld* World)
{
    if (!World)
    {
        return;
    }

    FActorSpawnParameters SpawnParameters;
    SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    AMworksReviewCameraPawn* ReviewPawn = FindOrSpawnReviewCamera(World, SpawnParameters);
    APlayerController* PlayerController = UGameplayStatics::GetPlayerController(World, 0);

    if (!ReviewPawn || !PlayerController)
    {
        return;
    }

    TArray<AActor*> Pawns;
    UGameplayStatics::GetAllActorsOfClass(World, APawn::StaticClass(), Pawns);
    int32 DisabledPawnCount = 0;
    for (AActor* Actor : Pawns)
    {
        APawn* Pawn = Cast<APawn>(Actor);
        if (Pawn && Pawn != ReviewPawn)
        {
            DisableImportedPawnInput(Pawn, PlayerController);
            ++DisabledPawnCount;
        }
    }

    const bool bNeedsPossess = PlayerController->GetPawn() != ReviewPawn;
    if (bNeedsPossess)
    {
        PlayerController->Possess(ReviewPawn);
    }
    ReviewPawn->ApplyReviewInputMode(PlayerController);

    const double NowSeconds = World->GetTimeSeconds();
    if (bNeedsPossess || NowSeconds - LastReviewCameraPossessLogTimeSeconds > 5.0)
    {
        LastReviewCameraPossessLogTimeSeconds = NowSeconds;
        const APawn* CurrentPawn = PlayerController->GetPawn();
        const FString PawnName = CurrentPawn ? CurrentPawn->GetName() : TEXT("<none>");
        UE_LOG(
            LogTemp,
            Display,
            TEXT("MWORKS scene-review control enforced: pawn=%s review_pawn=%s disabled_imported_pawns=%d"),
            *PawnName,
            *ReviewPawn->GetName(),
            DisabledPawnCount);
    }
}
