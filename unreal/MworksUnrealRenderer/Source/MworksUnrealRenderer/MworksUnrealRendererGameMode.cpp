#include "MworksUnrealRendererGameMode.h"

#include "Engine/World.h"
#include "QuadrotorMworksMapActor.h"
#include "QuadrotorMworksPlaybackActor.h"

AMworksUnrealRendererGameMode::AMworksUnrealRendererGameMode()
{
    DefaultPawnClass = nullptr;
}

void AMworksUnrealRendererGameMode::BeginPlay()
{
    Super::BeginPlay();

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
