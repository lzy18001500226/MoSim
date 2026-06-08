#pragma once

#include "Components/ActorComponent.h"
#include "CoreMinimal.h"
#include "QuadrotorMworksExperimentConsoleStateComponent.h"
#include "QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.generated.h"

UCLASS(ClassGroup = (Quadrotor), meta = (BlueprintSpawnableComponent))
class QUADROTORMWORKSBRIDGE_API UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent();

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool IsCommandEchoPacketJson(const FString& EchoJson, FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool IsAuthoritativeRuntimeCommandEchoPacketJson(const FString& EchoJson, FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool ApplyCommandEchoJsonToState(
        const FString& EchoJson,
        UQuadrotorMworksExperimentConsoleStateComponent* StateComponent,
        FQuadrotorMworksExperimentConsoleCommandState& OutState,
        FString& RejectReason) const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState(
        const FString& EchoJson,
        UQuadrotorMworksExperimentConsoleStateComponent* StateComponent,
        FQuadrotorMworksExperimentConsoleCommandState& OutState,
        FString& RejectReason) const;
};
