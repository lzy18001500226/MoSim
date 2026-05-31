#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MoSimSceneLibraryGameMode.generated.h"

class AMworksReviewCameraPawn;
class AQuadrotorMworksMapActor;
class AQuadrotorMworksPlaybackActor;
class ADirectionalLight;
class APawn;
class APlayerController;
class ASkyLight;
class APostProcessVolume;

UCLASS()
class MOSIMSCENELIBRARY_API AMoSimSceneLibraryGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AMoSimSceneLibraryGameMode();

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
    float ReviewSunIntensity = 12.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer|Review")
    float ReviewSkyLightIntensity = 3.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer|Review")
    FRotator ReviewSunRotation = FRotator(-45.0f, -35.0f, 0.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer|Review")
    bool bForceDaylightReviewExposure = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer|Review")
    float ReviewExposureBias = 0.0f;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Renderer")
    AQuadrotorMworksMapActor* SpawnedMapActor = nullptr;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Renderer")
    AQuadrotorMworksPlaybackActor* SpawnedPlaybackActor = nullptr;

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

private:
    void SpawnDefaultReviewLighting(UWorld* World, const FActorSpawnParameters& SpawnParameters);
    void EnforceSceneReviewCamera(UWorld* World);
    AMworksReviewCameraPawn* FindOrSpawnReviewCamera(UWorld* World, const FActorSpawnParameters& SpawnParameters);
    void DisableImportedPawnInput(APawn* Pawn, APlayerController* PlayerController) const;

    UPROPERTY()
    ADirectionalLight* SpawnedReviewSunLight = nullptr;

    UPROPERTY()
    ASkyLight* SpawnedReviewSkyLight = nullptr;

    UPROPERTY()
    APostProcessVolume* SpawnedReviewPostProcessVolume = nullptr;

    UPROPERTY()
    AMworksReviewCameraPawn* ActiveReviewCameraPawn = nullptr;

    bool bSceneReviewModeActive = false;
    double LastReviewCameraPossessLogTimeSeconds = -1000.0;
};
