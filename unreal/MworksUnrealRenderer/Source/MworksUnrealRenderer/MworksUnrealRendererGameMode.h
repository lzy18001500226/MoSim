#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MworksUnrealRendererGameMode.generated.h"

class AQuadrotorMworksMapActor;
class AQuadrotorMworksPlaybackActor;

UCLASS()
class MWORKSUNREALRENDERER_API AMworksUnrealRendererGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AMworksUnrealRendererGameMode();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer")
    bool bSpawnDefaultRendererActors = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer")
    FString DefaultRenderMapJson = TEXT("MworksData/map_open_blocks_render_map.json");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer")
    FVector MapActorLocation = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer")
    FVector PlaybackActorLocation = FVector(0.0, 0.0, 150.0);

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Renderer")
    AQuadrotorMworksMapActor* SpawnedMapActor = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Renderer")
    AQuadrotorMworksPlaybackActor* SpawnedPlaybackActor = nullptr;

protected:
    virtual void BeginPlay() override;
};
