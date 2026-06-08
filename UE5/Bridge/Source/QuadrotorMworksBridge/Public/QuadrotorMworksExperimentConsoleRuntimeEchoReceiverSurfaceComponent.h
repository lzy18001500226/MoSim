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
};
