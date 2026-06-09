#pragma once

#include "Components/ActorComponent.h"
#include "CoreMinimal.h"
#include "QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h"
#include "QuadrotorMworksExperimentConsoleStateComponent.h"
#include "QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.generated.h"

UCLASS(ClassGroup = (Quadrotor), meta = (BlueprintSpawnableComponent))
class QUADROTORMWORKSBRIDGE_API UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent();

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool ValidateAuthoritativeRuntimeCommandEchoDownlinkJson(
        const FString& EchoJson,
        UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent* CommandEchoReceiver,
        FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool IngestAuthoritativeRuntimeCommandEchoDownlinkJson(
        const FString& EchoJson,
        UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent* CommandEchoReceiver,
        UQuadrotorMworksExperimentConsoleStateComponent* StateComponent,
        FQuadrotorMworksExperimentConsoleCommandState& OutState,
        FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    FString GetSourceStaticReceiverBoundary() const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool BuildRuntimeProbeManifestJson(
        const FString& ProbeId,
        const FString& RunId,
        const FString& RequestId,
        const FString& ProducerSource,
        const FString& AckAuthority,
        const FString& ProducerSurface,
        const FString& ProducerInstanceId,
        const FString& CaptureSessionId,
        const FString& TransportCaptureId,
        FString& RuntimeProbeManifestJson,
        FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool BuildAuthoritativeEchoCaptureJson(
        const FString& EchoJson,
        const FString& ProducerSource,
        const FString& AckAuthority,
        const FString& CaptureSessionId,
        const FString& TransportCaptureId,
        UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent* CommandEchoReceiver,
        FString& AuthoritativeEchoCaptureJson,
        FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool BuildRequestEchoMatchReportJson(
        const FString& PendingRequestCaptureJson,
        const FString& AuthoritativeEchoCaptureJson,
        FString& RequestEchoMatchReportJson,
        FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool BuildNoPoseOverwriteReportJson(
        const FString& EchoJson,
        FString& NoPoseOverwriteReportJson,
        FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool BuildFalseAckNegativeReportJson(
        const TArray<FString>& CheckedSources,
        FString& FalseAckNegativeReportJson,
        FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool BuildTimeoutCleanupManifestJson(
        float TimeoutSeconds,
        int32 ProbeAttemptCount,
        int32 RetryCount,
        bool bCleanupCompleted,
        FString& TimeoutCleanupManifestJson,
        FString& RejectReason) const;
};
