#pragma once

#include "Components/ActorComponent.h"
#include "CoreMinimal.h"
#include "QuadrotorMworksExperimentConsoleStateComponent.generated.h"

USTRUCT(BlueprintType)
struct FQuadrotorMworksExperimentConsoleCommandState
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    FString RunId;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    FString RequestId;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    int32 Seq = 0;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    FString CommandKind;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    FString UiState = TEXT("pending");

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    FString AckAuthority;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    FString Reason = TEXT("awaiting_matching_echo");

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    FString Source = TEXT("ue_command_request");

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    FString QualityStatus = TEXT("pending_no_runtime_echo");

    UPROPERTY(BlueprintReadOnly, meta = (DisplayName = "accepted_as_runtime_ack"), Category = "MWORKS Experiment Console")
    bool bAcceptedAsRuntimeAck = false;

    UPROPERTY(BlueprintReadOnly, Category = "MWORKS Experiment Console")
    FString NoPoseOverwriteStatus = TEXT("pass");
};

UCLASS(ClassGroup = (Quadrotor), meta = (BlueprintSpawnableComponent))
class QUADROTORMWORKSBRIDGE_API UQuadrotorMworksExperimentConsoleStateComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UQuadrotorMworksExperimentConsoleStateComponent();

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool RecordPendingCommandFromPacketJson(
        const FString& PacketJson,
        FQuadrotorMworksExperimentConsoleCommandState& OutState,
        FString& RejectReason);

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    bool ApplyCommandEchoJson(
        const FString& EchoJson,
        FQuadrotorMworksExperimentConsoleCommandState& OutState,
        FString& RejectReason);

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    TArray<FQuadrotorMworksExperimentConsoleCommandState> GetCommandStates() const;

    UFUNCTION(BlueprintCallable, Category = "MWORKS Experiment Console")
    void ClearCommandStates();

private:
    TMap<FString, FQuadrotorMworksExperimentConsoleCommandState> CommandStatesByKey;

    FString MakeStateKey(const FString& RunId, const FString& RequestId) const;
};
