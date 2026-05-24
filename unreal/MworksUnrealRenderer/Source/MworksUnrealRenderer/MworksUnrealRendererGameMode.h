#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MworksUnrealRendererGameMode.generated.h"

class AQuadrotorMworksMapActor;
class AQuadrotorMworksPlaybackActor;
class ADirectionalLight;
class ASkyLight;

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

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer|Review")
    bool bSpawnDefaultReviewLighting = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer|Review")
    float ReviewSunIntensity = 10.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer|Review")
    float ReviewSkyLightIntensity = 1.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer|Review")
    FRotator ReviewSunRotation = FRotator(-45.0f, -35.0f, 0.0f);

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Renderer")
    AQuadrotorMworksMapActor* SpawnedMapActor = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Renderer")
    AQuadrotorMworksPlaybackActor* SpawnedPlaybackActor = nullptr;

protected:
    virtual void BeginPlay() override;

private:
    void SpawnDefaultReviewLighting(UWorld* World, const FActorSpawnParameters& SpawnParameters);

    UPROPERTY()
    ADirectionalLight* SpawnedReviewSunLight = nullptr;

    UPROPERTY()
    ASkyLight* SpawnedReviewSkyLight = nullptr;
};
