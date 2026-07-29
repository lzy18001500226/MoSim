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

struct FMoSimFactoryCalibrationSegment
{
    FVector StartUnrealCm = FVector::ZeroVector;
    FVector EndUnrealCm = FVector::ZeroVector;
    FColor Color = FColor::White;
};

struct FMoSimFactoryCalibrationMarker
{
    FString Label;
    FVector UnrealCm = FVector::ZeroVector;
    FColor Color = FColor::White;
    float RadiusCm = 12.0f;
    FVector BoxExtentCm = FVector::ZeroVector;
    bool bDrawBox = false;
};

struct FMoSimFactoryOverlayPoint
{
    FVector UnrealCm = FVector::ZeroVector;
    FColor Color = FColor::Cyan;
    float Size = 6.0f;
};

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
    FVector PlaybackActorLocation = FVector(0.0, 0.0, 20.0);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer")
    int32 PlaybackActorCount = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer")
    int32 PlaybackBaseUdpPort = 5005;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MWORKS Renderer")
    FVector PlaybackActorSpacing = FVector(0.0, 180.0, 0.0);

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

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Renderer")
    TArray<AQuadrotorMworksPlaybackActor*> SpawnedPlaybackActors;

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

private:
    void SpawnDefaultReviewLighting(UWorld* World, const FActorSpawnParameters& SpawnParameters);
    void EnforceSceneReviewCamera(UWorld* World);
    AMworksReviewCameraPawn* FindOrSpawnReviewCamera(UWorld* World, const FActorSpawnParameters& SpawnParameters);
    void DisableImportedPawnInput(APawn* Pawn, APlayerController* PlayerController) const;
    void LoadFactoryCalibrationFrame();
    void LoadFactoryCalibrationMarkers();
    void DrawFactoryCalibrationFrame(UWorld* World) const;
    void LoadFactoryGazeboOverlay();
    void DrawFactoryGazeboOverlay(UWorld* World) const;
    void WriteFrameTimingMetrics(double WindowSeconds);

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
    bool bFactoryCalibrationFrameEnabled = false;
    FString FactoryCalibrationCsvPath;
    FString FactoryCalibrationMarkerCsvPath;
    float FactoryCalibrationLineThickness = 6.0f;
    float FactoryCalibrationDrawLifetimeSeconds = 0.5f;
    TArray<FMoSimFactoryCalibrationSegment> FactoryCalibrationSegments;
    TArray<FMoSimFactoryCalibrationMarker> FactoryCalibrationMarkers;
    bool bFactoryGazeboOverlayEnabled = false;
    FString FactoryGazeboOverlayCsvPath;
    float FactoryGazeboOverlayZOffsetCm = 20.0f;
    TArray<FMoSimFactoryOverlayPoint> FactoryGazeboOverlayPoints;
    FString ObservabilityRunId;
    FString UeReceiverMetricsOutputPath;
    FString UeFrameMetricsOutputPath;
    double FrameMetricsWindowStartSeconds = 0.0;
    double FrameMetricsTotalSeconds = 0.0;
    double FrameMetricsMaxSeconds = 0.0;
    int32 FrameMetricsCount = 0;
    int32 FrameMetricsHitchCount = 0;
};
