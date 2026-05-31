#include "MoSimSceneLibraryGameMode.h"

#include "Components/LightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/World.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "MworksReviewCameraPawn.h"
#include "QuadrotorMworksMapActor.h"
#include "QuadrotorMworksPlaybackActor.h"

AMoSimSceneLibraryGameMode::AMoSimSceneLibraryGameMode()
{
    DefaultPawnClass = AMworksReviewCameraPawn::StaticClass();
}

void AMoSimSceneLibraryGameMode::BeginPlay()
{
    Super::BeginPlay();

    const bool bSceneReviewOnly = FParse::Param(FCommandLine::Get(), TEXT("MoSimSceneReview"));
    const bool bDisablePreviewMap =
        bSceneReviewOnly || FParse::Param(FCommandLine::Get(), TEXT("MoSimNoPreviewMap"));
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
        SpawnDefaultReviewLighting(World, SpawnParameters);
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
}
